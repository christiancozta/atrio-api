"""Homologação do CORPUS 1.5.0 contra PostgreSQL vivo.

Dirige o pipeline REAL (extração nativa + OCR + atrio_pii + cofre cifrado)
usando o adaptador PostgresExecutionRepository, exercitando exatamente o
caminho que os testes unitários só cobrem com o repositório in-memory:

    criar execução -> START_INGESTION -> intake -> process_pending
        -> (revisão humana, se exigida) -> finalize -> CORPUS_READY

Ao fim, relê estado, eventos e inventário direto do banco e confirma que
nenhum dado sensível vazou para a camada PostgreSQL.

Headless por desenho: a senha vem de PGPASSWORD (nunca de getpass), e o
cofre usa uma frase secreta descartável gerada em diretório temporário.
Rode contra um banco DESCARTÁVEL de homologação, não contra produção.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import secrets
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

SERVICE_ROOT = Path(__file__).resolve().parents[1]
PACKAGES_ROOT = SERVICE_ROOT.parents[1]
sys.path.insert(0, str(SERVICE_ROOT / "src"))

from atrio_api import __version__  # noqa: E402
from atrio_api.corpus_intake import (  # noqa: E402
    CorpusIntakeService,
    EncryptedCorpusStore,
)
from atrio_api.corpus_processing import ProcessingStatus  # noqa: E402
from atrio_api.corpus_service import (  # noqa: E402
    CorpusReviewDecision,
    default_corpus_workflow,
)
from atrio_api.domain import (  # noqa: E402
    Command,
    CommandKind,
    CreateExecutionRequest,
    Destination,
    ExecutionStage,
    RatioModule,
)
from atrio_api.postgres_repository import (  # noqa: E402
    PostgresExecutionRepository,
)
from atrio_api.release_catalog import ACTIVE_RELEASE  # noqa: E402
from atrio_api.service import ExecutionService  # noqa: E402


NAME = "Maria da Silva"
CPF = "123.456.789-09"


def _synthetic_pdf(text: str) -> bytes:
    """Gera um PDF de uma página com camada textual nativa."""
    stream = f"BT /F1 11 Tf 40 760 Td ({text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 1000 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii")
        + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii") + obj + b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return bytes(pdf)


async def _stream(value: bytes):
    yield value


def _fail(message: str) -> None:
    raise SystemExit(f"HOMOLOGAÇÃO FALHOU: {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=5432, type=int)
    parser.add_argument("--database", default="atrio_hml")
    parser.add_argument("--user", default="atrio_hml")
    args = parser.parse_args()

    password = os.environ.get("PGPASSWORD")
    if not password:
        _fail("defina PGPASSWORD no ambiente (execução headless, sem getpass).")

    repository = PostgresExecutionRepository.from_parameters(
        host=args.host,
        port=args.port,
        dbname=args.database,
        user=args.user,
        password=password,
        connect_timeout=5,
        application_name=f"atrio-api/{__version__}/homologacao",
    )
    repository.verify_schema()
    print(f"[1/8] Schema PostgreSQL verificado ({args.user}@{args.database}).")

    with tempfile.TemporaryDirectory(prefix="atrio-hml-") as temp:
        vault_root = Path(temp) / "vault"
        store = EncryptedCorpusStore.from_passphrase(
            vault_root,
            secrets.token_urlsafe(24),
        )
        service = ExecutionService(repository)
        intake = CorpusIntakeService(repository, store)
        workflow = default_corpus_workflow(
            repository,
            store,
            packages_root=PACKAGES_ROOT,
            scratch_root=vault_root / "scratch",
            expected_pii_version=ACTIVE_RELEASE.atrio_pii_version,
        )
        tools = workflow.verify_tools()
        print(f"[2/8] Ferramentas locais: {tools}")

        request = CreateExecutionRequest(
            tenant_id="_atrio_homologacao",
            actor_id="homologacao",
            idempotency_key=f"homologacao-corpus-{uuid4()}",
            ratio_module=RatioModule.RI,
            destination=Destination.INTERNO,
        )
        first = service.create(request, ACTIVE_RELEASE)
        second = service.create(request, ACTIVE_RELEASE)
        if first.state.execution_id != second.state.execution_id:
            _fail("idempotência retornou execuções diferentes.")
        execution_id = first.state.execution_id
        print(f"[3/8] Execução criada e idempotente: {execution_id}")

        state = service.command(
            execution_id,
            Command(
                kind=CommandKind.START_INGESTION,
                expected_version=first.state.state_version,
                actor_id="homologacao",
            ),
        ).state
        if state.stage is not ExecutionStage.CORPUS_INGESTING:
            _fail(f"esperava CORPUS_INGESTING, obtive {state.stage.value}.")
        print(f"[4/8] Ingestão iniciada (versão {state.state_version}).")

        documents = {
            "documento-nativo": (
                "application/pdf",
                _synthetic_pdf(
                    "Processo 1234567-89.2026.8.26.0001 SENTENCA requerente "
                    f"{NAME}, CPF {CPF}. Texto adicional suficiente para "
                    "validar a extracao nativa e a pseudonimizacao local."
                ),
            ),
            "documento-curto": (
                "text/plain",
                "Despacho breve.".encode("utf-8"),
            ),
        }
        for key, (media_type, content) in documents.items():
            result = asyncio.run(
                intake.ingest(
                    _stream(content),
                    execution_id=execution_id,
                    idempotency_key=key,
                    actor_id="homologacao",
                    expected_version=state.state_version,
                    media_type=media_type,
                )
            )
            state = result.state
        print(f"[5/8] {len(documents)} documentos ingeridos e cifrados.")

        # process_pending pode parar no primeiro que exigir revisão humana;
        # repete até não restar pendência (mesma lógica da console).
        while True:
            batch = workflow.process_pending(
                execution_id=execution_id,
                actor_id="homologacao",
                expected_version=state.state_version,
            )
            state = batch.state
            for document in batch.documents:
                inventory = document.inventory
                if inventory is None:
                    continue
                if (
                    inventory.status is ProcessingStatus.REVIEW_REQUIRED
                    and document.review_decision is None
                ):
                    reviewed = workflow.review(
                        execution_id=execution_id,
                        document_id=document.intake.document_id,
                        decision=CorpusReviewDecision.APPROVE,
                        actor_id="revisor-homologacao",
                        expected_version=state.state_version,
                    )
                    state = reviewed.state
            pending = [
                doc
                for doc in workflow.list_documents(execution_id)
                if doc.inventory is None
                or (
                    doc.inventory.status is ProcessingStatus.REVIEW_REQUIRED
                    and doc.review_decision is None
                )
            ]
            if not pending:
                break

        processed = workflow.list_documents(execution_id)
        for document in processed:
            inventory = document.inventory
            if inventory is None:
                _fail(f"documento {document.intake.document_id} sem inventário.")
            print(
                f"        - {inventory.extraction_method.value} "
                f"| {inventory.extracted_char_count} chars "
                f"| CNJ={inventory.cnj} "
                f"| PII={dict(inventory.pii_counts)} "
                f"| {document.effective_status}"
            )
        print(f"[6/8] Processamento e revisão concluídos ({len(processed)} docs).")

        finalized = workflow.finalize(
            execution_id=execution_id,
            actor_id="homologacao",
            expected_version=state.state_version,
        )
        if finalized.state.stage is not ExecutionStage.CORPUS_READY:
            _fail(f"esperava CORPUS_READY, obtive {finalized.state.stage.value}.")
        print(
            f"[7/8] Artefato {finalized.artifact.artifact_id} "
            f"({finalized.document_count} docs) -> CORPUS_READY."
        )

        # Releitura direto do banco: estado persistido, trilha e ausência de
        # dado sensível na camada PostgreSQL.
        persisted = service.get(execution_id)
        events = repository.events(execution_id)
        if persisted != finalized.state:
            _fail("estado relido do banco difere do estado finalizado.")
        if not events or events[-1].to_stage is not ExecutionStage.CORPUS_READY:
            _fail("trilha de eventos não termina em CORPUS_READY.")

        db_dump = json.dumps(
            [doc.safe_dict() for doc in processed],
            ensure_ascii=False,
        )
        for leak in (NAME, CPF, "pseudonymized_text", "storage_key"):
            if leak in db_dump:
                _fail(f"vazamento na camada segura: {leak!r} presente.")

        # O artefato cifrado no cofre não pode conter identidade em claro.
        artifact_key = (
            f"artifacts/{execution_id}/{finalized.artifact.artifact_id}.atrio"
        )
        envelope = store.read_private_record(artifact_key)
        if NAME.encode("utf-8") in envelope or CPF.encode("utf-8") in envelope:
            _fail("identidade em claro dentro do artefato pseudonimizado.")
        if hashlib.sha256(envelope).hexdigest() != finalized.artifact.sha256:
            _fail("hash do artefato diverge do registrado no banco.")
        print(
            f"[8/8] Releitura do banco OK | {len(events)} eventos "
            "| inventário sem PII | artefato íntegro e pseudonimizado."
        )

    print("\nHOMOLOGAÇÃO CORPUS 1.5.0 x PostgreSQL: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
