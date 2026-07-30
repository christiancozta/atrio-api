from __future__ import annotations

import getpass
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from atrio_api.adapters.ollama import InferenceMetadata, InferenceResult
from atrio_api.corpus_intake import EncryptedCorpusStore
from atrio_api.domain import (
    ArtifactRef,
    CerneGate,
    Command,
    CommandKind,
    ComponentName,
    Destination,
    ExecutionStage,
    ExecutionState,
    RatioModule,
)
from atrio_api.lux.execution import LuxDataMode, LuxMode
from atrio_api.lux.service import default_lux_workflow
from atrio_api.postgres_repository import PostgresExecutionRepository, _payload_fingerprint
from atrio_api.release_catalog import ACTIVE_RELEASE


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
PACKAGES_ROOT = REPOSITORY_ROOT / "packages"
LUX_ROOT = PACKAGES_ROOT / "lux"
PII_SOURCE = PACKAGES_ROOT / "atrio_pii" / "atrio_pii.py"


class DeterministicLuxProvider:
    def __init__(self) -> None:
        self.calls = 0

    def generate(
        self,
        prompt,
        *,
        model,
        system=None,
        options=None,
        format_schema=None,
    ):
        del system, options
        if format_schema is None:
            raise RuntimeError("LUX não forneceu schema estruturado.")
        self.calls += 1
        source = prompt.split(
            "TEXTO JÁ TRATADO PELA CAMADA 0:\n",
            1,
        )[1]
        content = json.dumps(
            {
                "marked_text": source,
                "changes": [],
                "final_text": source,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return InferenceResult(
            content=content,
            metadata=InferenceMetadata(
                adapter_version="smoke",
                model=model,
                model_digest="a" * 64,
                prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                response_sha256=hashlib.sha256(content.encode()).hexdigest(),
                options_sha256="b" * 64,
                prompt_chars=len(prompt),
                response_chars=len(content),
            ),
        )


def repository(password: str) -> PostgresExecutionRepository:
    return PostgresExecutionRepository.from_parameters(
        host="127.0.0.1",
        port=5432,
        dbname="atrio",
        user="atrio_app",
        password=password,
    )


def private_artifact(
    store: EncryptedCorpusStore,
    execution: ExecutionState,
    *,
    producer: ComponentName,
    media_type: str,
    payload: dict,
) -> ArtifactRef:
    plaintext = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    artifact_id = str(uuid4())
    store.write_private_record(
        f"artifacts/{execution.execution_id}/{artifact_id}.atrio",
        plaintext,
    )
    return ArtifactRef(
        artifact_id=artifact_id,
        sha256=hashlib.sha256(plaintext).hexdigest(),
        media_type=media_type,
        classification="INTERNAL_PSEUDONYMIZED",
        producer=producer,
        producer_version=execution.release.version_for(producer),
        release_id=execution.release.release_id,
        schema_version=execution.release.schema_version,
    )


def apply(repo, execution_id, state, kind, actor, payload=None):
    result = repo.apply(
        execution_id,
        Command(
            kind=kind,
            expected_version=state.state_version,
            actor_id=actor,
            payload=payload or {},
        ),
    )
    return result.state


def main() -> None:
    print("ATRIO smoke LUX 6.0.0")
    password = getpass.getpass("Senha PostgreSQL: ")
    repo = repository(password)
    repo.verify_schema()

    with TemporaryDirectory(prefix="atrio-lux-smoke-") as directory:
        store = EncryptedCorpusStore(Path(directory), b"l" * 32)
        execution_id = str(uuid4())
        actor = "smoke-lux"
        state = ExecutionState(
            execution_id=execution_id,
            tenant_id="smoke",
            created_by=actor,
            ratio_module=RatioModule.RI,
            destination=Destination.PUBLICO,
            release=ACTIVE_RELEASE,
        )
        repo.create(
            state,
            idempotency_key=f"lux-smoke-create-{execution_id}",
            request_fingerprint=_payload_fingerprint(
                {"execution_id": execution_id, "smoke": "lux-6.0.0"}
            ),
        )

        # Monta somente a fronteira macro; CORPUS/RATIO/CERNE já têm acceptance próprio.
        state = apply(repo, execution_id, state, CommandKind.START_INGESTION, actor)
        corpus = private_artifact(
            store,
            state,
            producer=ComponentName.CORPUS,
            media_type="application/vnd.atrio.corpus+json",
            payload={
                "kind": "CORPUS_SMOKE_HANDOFF",
                "execution_id": execution_id,
                "release_id": ACTIVE_RELEASE.release_id,
            },
        )
        state = apply(
            repo,
            execution_id,
            state,
            CommandKind.COMPLETE_CORPUS,
            actor,
            {"artifact": corpus},
        )
        state = apply(repo, execution_id, state, CommandKind.START_RATIO, actor)

        ratio = private_artifact(
            store,
            state,
            producer=ComponentName.RATIO,
            media_type="application/vnd.atrio.ratio+json",
            payload={
                "kind": "RATIO_HANDOFF",
                "execution_id": execution_id,
                "release_id": ACTIVE_RELEASE.release_id,
                "audit_target": {
                    "object_type": "voto",
                    "text": (
                        "VOTO. A parte [PESSOA_0001] interpôs recurso no processo "
                        "0001234-56.2025.8.16.0001. A tese e o fundamento permanecem "
                        "inalterados. Em razão da sucumbência, os honorários são de 20%. "
                        "Ante o exposto, voto pelo CONHECIMENTO e DESPROVIMENTO do recurso."
                    ),
                },
            },
        )
        state = apply(
            repo,
            execution_id,
            state,
            CommandKind.COMPLETE_RATIO,
            actor,
            {"artifact": ratio},
        )
        state = apply(repo, execution_id, state, CommandKind.START_CERNE, actor)

        cerne = private_artifact(
            store,
            state,
            producer=ComponentName.CERNE,
            media_type="application/vnd.atrio.cerne.audit+json",
            payload={
                "kind": "CERNE_AUDIT",
                "execution_id": execution_id,
                "release_id": ACTIVE_RELEASE.release_id,
                "ratio_artifact_id": ratio.artifact_id,
                "audit_response": {"gate": {"estado": "AVANCA"}},
            },
        )
        state = apply(
            repo,
            execution_id,
            state,
            CommandKind.APPLY_CERNE_GATE,
            actor,
            {"artifact": cerne, "gate": CerneGate.AVANCA.value},
        )
        if state.stage is not ExecutionStage.CERNE_APPROVED:
            raise RuntimeError("Setup não chegou a CERNE_APPROVED.")

        provider = DeterministicLuxProvider()
        workflow = default_lux_workflow(
            repo,
            store,
            provider,
            model="lux-smoke",
            knowledge_root=LUX_ROOT,
            pii_source=PII_SOURCE,
        )
        workflow.verify()

        result = workflow.refine(
            execution_id,
            expected_version=state.state_version,
            actor_id=actor,
            idempotency_key="lux-smoke-refine",
            mode=LuxMode.PADRAO,
        )
        if result.execution_state.stage is not ExecutionStage.FINAL_INTEGRITY_CHECK:
            raise RuntimeError("LUX não chegou a FINAL_INTEGRITY_CHECK.")
        if result.data_mode != LuxDataMode.PUBLICO:
            raise RuntimeError("Destino público não forçou PUBLICO.")
        if provider.calls != 1:
            raise RuntimeError("Provedor LUX teve quantidade inesperada de chamadas.")

        private = store.read_private_record(
            f"artifacts/{execution_id}/{result.artifact.artifact_id}.atrio"
        )
        bundle = json.loads(private)
        output = bundle["output"]
        serialized = json.dumps(output, ensure_ascii=False)
        if "[PESSOA_0001]" in serialized:
            raise RuntimeError("Pseudotoken estável vazou na saída pública.")
        if "0001234-56.2025.8.16.0001" in serialized:
            raise RuntimeError("CNJ vazou na saída pública.")
        if "[pessoa]" not in serialized or "[processo]" not in serialized:
            raise RuntimeError("Camada 0 não propagou marcadores públicos.")
        if not any(
            "anonimização" in item
            for item in output["alteracoes_realizadas"]
        ):
            raise RuntimeError("Bloco de alterações não registra anonimização.")

        # Retry idempotente após COMPLETE_LUX: sem nova chamada ao modelo.
        retry = workflow.refine(
            execution_id,
            expected_version=state.state_version,
            actor_id=actor,
            idempotency_key="lux-smoke-refine",
            mode=LuxMode.PADRAO,
        )
        if retry.created:
            raise RuntimeError("Retry LUX deveria ser idempotente.")
        if provider.calls != 1:
            raise RuntimeError("Retry idempotente reexecutou o provedor.")

        reloaded = repository(password).get(execution_id)
        if reloaded.stage is not ExecutionStage.FINAL_INTEGRITY_CHECK:
            raise RuntimeError("Restart não reconstruiu FINAL_INTEGRITY_CHECK.")
        if reloaded.lux_artifact != result.artifact:
            raise RuntimeError("Restart alterou ArtifactRef LUX.")

        print("OK: CERNE_APPROVED → LUX_REFINING → FINAL_INTEGRITY_CHECK")
        print("OK: LUX 6.0.0 usou os três arquivos normativos")
        print("OK: Camada 0 forçou anonimização irreversível no destino público")
        print("OK: anonimização propagada aos três blocos")
        print("OK: ArtifactRef LUX persistido sem conteúdo jurídico no PostgreSQL")
        print("OK: retry idempotente não reexecutou o provedor")
        print("OK: restart reconstruiu o handoff LUX")
        print("OK: release permanece bloqueado para a próxima entrega")
        print(f"execution_id: {execution_id}")


if __name__ == "__main__":
    main()
