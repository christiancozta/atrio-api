"""Catálogo normativo de hard stops do RATIO.

O catálogo é derivado dos módulos canônicos do RATIO 7.0.0.

Convenção de códigos:
- HS-RI1.x / HS-ED3.x / HS-MS5.x: hard stop ligado a uma fase.
- HS-MS0.x (e qualquer futuro HS-<MOD>0.x): hard stop geral do módulo,
  sem criar uma fase operacional "00".
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from types import MappingProxyType
from typing import Mapping

from atrio_api.domain import RatioModule
from atrio_api.ratio.contract import RatioPhase


HARD_STOP_CATALOG_VERSION = "0.2.0"

_HARD_STOP_PATTERN = re.compile(
    r"^(HS-(RI|ED|MS)(\d+)\.(\d+))\s+(.+?)\s*$"
)

_MODULE_FILES: Mapping[RatioModule, str] = MappingProxyType(
    {
        RatioModule.RI: "modulo_ri.md",
        RatioModule.ED: "modulo_ed.md",
        RatioModule.MS: "modulo_ms.md",
    }
)


class HardStopCatalogError(ValueError):
    """Catálogo normativo inválido ou inconsistente."""


class UnknownHardStop(HardStopCatalogError):
    """Código não existe na fonte normativa carregada."""


class HardStopPhaseMismatch(HardStopCatalogError):
    """Código existe, mas não é aplicável à fase solicitada."""


@dataclass(frozen=True, slots=True)
class HardStopRule:
    code: str
    module: RatioModule
    phase: RatioPhase | None
    title: str
    source_path: str
    source_line: int

    @property
    def is_module_wide(self) -> bool:
        return self.phase is None


@dataclass(frozen=True, slots=True)
class HardStopCatalog:
    rules: Mapping[str, HardStopRule]
    source_sha256: Mapping[str, str]
    catalog_sha256: str

    def get(self, code: str) -> HardStopRule:
        try:
            return self.rules[code]
        except KeyError as exc:
            raise UnknownHardStop(
                f"Hard stop não existe no catálogo normativo: {code}."
            ) from exc

    def require_for_phase(
        self,
        code: str,
        phase: RatioPhase,
    ) -> HardStopRule:
        """Exige código aplicável à fase.

        Hard stop geral do módulo (número de fase 0) é aplicável a qualquer
        fase do mesmo módulo, sem ser convertido artificialmente em fase 00.
        """

        rule = self.get(code)
        phase_module = _module_for_phase(phase)

        if rule.module is not phase_module:
            raise HardStopPhaseMismatch(
                f"Hard stop {code} pertence ao módulo {rule.module.value}, "
                f"não ao módulo {phase_module.value} da fase {phase.value}."
            )

        if rule.phase is not None and rule.phase is not phase:
            raise HardStopPhaseMismatch(
                f"Hard stop {code} pertence a {rule.phase.value}, "
                f"não a {phase.value}."
            )

        return rule

    def for_phase(self, phase: RatioPhase) -> tuple[HardStopRule, ...]:
        """Retorna hard stops específicos + gerais aplicáveis à fase."""

        phase_module = _module_for_phase(phase)

        return tuple(
            rule
            for rule in self.rules.values()
            if rule.module is phase_module
            and (rule.phase is None or rule.phase is phase)
        )

    def for_module(self, module: RatioModule) -> tuple[HardStopRule, ...]:
        return tuple(
            rule
            for rule in self.rules.values()
            if rule.module is module
        )


def load_hard_stop_catalog(ratio_root: Path) -> HardStopCatalog:
    """Extrai todos os hard stops dos módulos canônicos."""

    modules_root = ratio_root.resolve() / "modulos"
    rules: dict[str, HardStopRule] = {}
    source_hashes: dict[str, str] = {}

    for expected_module, filename in _MODULE_FILES.items():
        path = modules_root / filename

        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise HardStopCatalogError(
                f"Fonte normativa indisponível: {path}."
            ) from exc

        source_hashes[path.as_posix()] = hashlib.sha256(raw).hexdigest()

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HardStopCatalogError(
                f"Fonte normativa não está em UTF-8: {path}."
            ) from exc

        for line_number, line in enumerate(text.splitlines(), start=1):
            match = _HARD_STOP_PATTERN.match(line.strip())
            if match is None:
                continue

            code, module_text, phase_number_text, _, raw_title = match.groups()
            module = RatioModule(module_text)

            if module is not expected_module:
                raise HardStopCatalogError(
                    f"{code} declara módulo {module.value} dentro de "
                    f"{filename}."
                )

            phase_number = int(phase_number_text)
            phase = _phase_for(module, phase_number)

            if code in rules:
                previous = rules[code]
                raise HardStopCatalogError(
                    f"Hard stop duplicado {code}: "
                    f"{previous.source_path}:{previous.source_line} e "
                    f"{path.as_posix()}:{line_number}."
                )

            title = raw_title.strip().lstrip("\u2014- ").rstrip(":").strip()

            rules[code] = HardStopRule(
                code=code,
                module=module,
                phase=phase,
                title=title,
                source_path=path.as_posix(),
                source_line=line_number,
            )

    if not rules:
        raise HardStopCatalogError(
            "Nenhum hard stop foi localizado nas fontes normativas."
        )

    ordered = dict(sorted(rules.items()))

    canonical = "\n".join(
        (
            f"{rule.code}|{rule.module.value}|"
            f"{rule.phase.value if rule.phase is not None else 'MODULE'}|"
            f"{rule.title}|{rule.source_path}|{rule.source_line}"
        )
        for rule in ordered.values()
    ).encode("utf-8")

    return HardStopCatalog(
        rules=MappingProxyType(ordered),
        source_sha256=MappingProxyType(dict(sorted(source_hashes.items()))),
        catalog_sha256=hashlib.sha256(canonical).hexdigest(),
    )


def _phase_for(
    module: RatioModule,
    phase_number: int,
) -> RatioPhase | None:
    """Resolve o número do código para fase operacional.

    Zero é reservado ao escopo geral do módulo. Não existe fase operacional
    RI_00, ED_00 ou MS_00.
    """

    if phase_number == 0:
        return None

    try:
        return RatioPhase[f"{module.value}_{phase_number:02d}"]
    except KeyError as exc:
        raise HardStopCatalogError(
            f"Hard stop referencia fase inexistente: "
            f"{module.value}_{phase_number:02d}."
        ) from exc


def _module_for_phase(phase: RatioPhase) -> RatioModule:
    prefix = phase.value.split("_", 1)[0]
    return RatioModule(prefix)
