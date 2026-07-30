from __future__ import annotations

import re
from pathlib import Path

from atrio_api.cerne_core.domain import AxisCode


class KnowledgeError(RuntimeError):
    pass


AXIS_FILES = {
    AxisCode.EX001: "EX001_TOULMIN.md",
    AxisCode.EX002: "EX002_SOCRATES.md",
    AxisCode.EX003: "EX003_PEIRCE.md",
    AxisCode.EX004: "EX004_BION.md",
    AxisCode.EX005: "EX005_GADAMER.md",
    AxisCode.EX006: "EX006_MATTE_BLANCO.md",
    AxisCode.EX007: "EX007_LEVI.md",
    AxisCode.EX008: "EX008_MACCORMICK.md",
    AxisCode.EX009: "EX009_HART.md",
    AxisCode.EX010: "EX010_KELSEN.md",
    AxisCode.EX011: "EX011_RAZ.md",
}


class KnowledgeBase:
    def __init__(self, root: Path):
        self.root = root
        self.system = root / "00_sistema_cerne"
        self._cache: dict[str, str] = {}

    def read(self, name: str) -> str:
        if name in self._cache:
            return self._cache[name]
        path = self.system / name
        if not path.is_file():
            raise KnowledgeError(f"Arquivo de conhecimento ausente: {path}")
        value = path.read_text(encoding="utf-8")
        self._cache[name] = value
        return value

    def central(self) -> str:
        return self._join(
            "00_INSTRUCOES_GPT_CUSTOM.md",
            "01_WORKFLOW_PIPELINE.txt",
            "03_PROMPT_MESTRE.txt",
            "12_CAMADA_ANTIBANALIZACAO.txt",
            "20_DECISAO_PRODUTO_API_V0_2.md",
        )

    def triage_prompt(self) -> str:
        return self._join(
            "00_INSTRUCOES_GPT_CUSTOM.md",
            "01_WORKFLOW_PIPELINE.txt",
            "05_PROMPT_TRIAGEM.txt",
            "12_CAMADA_ANTIBANALIZACAO.txt",
            "18_ADENDO_POS_AUDITORIA_EXTERNA.txt",
            "20_DECISAO_PRODUTO_API_V0_2.md",
        )

    def lens_prompt(self, axis: AxisCode) -> str:
        return self._join(
            "00_INSTRUCOES_GPT_CUSTOM.md",
            "06_PROMPT_LENTE_ISOLADA.txt",
            AXIS_FILES[axis],
            "12_CAMADA_ANTIBANALIZACAO.txt",
            "20_DECISAO_PRODUTO_API_V0_2.md",
        )

    def confrontation_prompt(self, code: str) -> str:
        if code == "CF-013":
            card = self.read("CF-013_TOULMIN_SOCRATES.md")
        else:
            card = self._extract_confrontation_card(
                self.read("04_CARDS_CONFRONTOS.txt"),
                code,
            )
        return "\n\n".join(
            [
                self.read("00_INSTRUCOES_GPT_CUSTOM.md"),
                self.read("07_PROMPT_CONFRONTO_RODADA_C.txt"),
                f"# CARD APLICÁVEL\n\n{card}",
                self.read("12_CAMADA_ANTIBANALIZACAO.txt"),
                self.read("20_DECISAO_PRODUTO_API_V0_2.md"),
            ]
        )

    def gate_prompt(self) -> str:
        return self._join(
            "00_INSTRUCOES_GPT_CUSTOM.md",
            "08_PROMPT_GATE_TECNICO.txt",
            "12_CAMADA_ANTIBANALIZACAO.txt",
            "18_ADENDO_POS_AUDITORIA_EXTERNA.txt",
            "20_DECISAO_PRODUTO_API_V0_2.md",
        )

    def client_output_prompt(self) -> str:
        return self._join(
            "10_OUTPUT_CLIENTE.txt",
            "18_ADENDO_POS_AUDITORIA_EXTERNA.txt",
            "20_DECISAO_PRODUTO_API_V0_2.md",
        )

    def assert_ready(self) -> None:
        required = [
            "00_INSTRUCOES_GPT_CUSTOM.md",
            "01_WORKFLOW_PIPELINE.txt",
            "03_PROMPT_MESTRE.txt",
            "05_PROMPT_TRIAGEM.txt",
            "06_PROMPT_LENTE_ISOLADA.txt",
            "07_PROMPT_CONFRONTO_RODADA_C.txt",
            "08_PROMPT_GATE_TECNICO.txt",
            "10_OUTPUT_CLIENTE.txt",
            "12_CAMADA_ANTIBANALIZACAO.txt",
            "18_ADENDO_POS_AUDITORIA_EXTERNA.txt",
            "20_DECISAO_PRODUTO_API_V0_2.md",
            "04_CARDS_CONFRONTOS.txt",
            "CF-013_TOULMIN_SOCRATES.md",
            *AXIS_FILES.values(),
        ]
        for name in required:
            self.read(name)

    def _join(self, *names: str) -> str:
        return "\n\n".join(self.read(name) for name in names)

    @staticmethod
    def _extract_confrontation_card(text: str, code: str) -> str:
        start = re.search(
            rf"(?im)^#{{1,4}}\s+.*\b{re.escape(code)}\b.*$",
            text,
        )
        if not start:
            raise KnowledgeError(f"Card de confronto não localizado: {code}")
        tail = text[start.start() :]
        next_card = re.search(
            r"(?im)^#{1,4}\s+.*\bCF-\d{3}\b.*$",
            tail[start.end() - start.start() :],
        )
        if not next_card:
            return tail
        end = start.end() - start.start() + next_card.start()
        return tail[:end]
