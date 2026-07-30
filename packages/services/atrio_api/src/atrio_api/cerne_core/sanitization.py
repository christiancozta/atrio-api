from __future__ import annotations

import re

from atrio_api.cerne_core.domain import ClientOutput

_REPLACEMENTS = (
    (
        r"\bBLOQUEIO TOTAL\b",
        "o documento não deve ser usado na forma atual",
    ),
    (
        r"\bBLOQUEIO PARCIAL\b",
        "o trecho afetado não deve ser usado sem correção",
    ),
    (
        r"\bREVISÃO HUMANA\b",
        "revisão técnica antes de uso",
    ),
    (
        r"\bAVANÇA COM AJUSTE\b",
        "pode avançar após ajuste pontual",
    ),
    (r"\bAVANÇA\b", "pode avançar"),
    (r"\bCERNE\b", "auditoria"),
    (r"\bo sistema\b", "a auditoria"),
    (r"\bEX\s*-?\s*\d{1,3}\b", "verificação técnica"),
    (r"\bCF\s*-?\s*\d{1,3}\b", "análise combinada"),
    (r"\bgate técnico\b", "avaliação técnica"),
    (r"\bachado emergente\b", "risco combinado"),
    (r"\blentes?\b", "verificação técnica"),
    (r"\bconfrontos?\b", "análise combinada"),
    (r"\bToulmin\b", "análise estrutural"),
    (r"\bSócrates\b", "análise adversarial"),
    (r"\bPeirce\b", "análise inferencial"),
    (r"\bBion\b", "análise de incerteza"),
    (r"\bGadamer\b", "análise interpretativa"),
    (r"\bMatte-?Blanco\b", "análise de distinções"),
    (r"\bLevi\b", "análise precedental"),
    (r"\bMacCormick\b", "análise sistêmica"),
    (r"\bHart\b", "análise de conceitos abertos"),
    (r"\bKelsen\b", "análise de validade"),
    (r"\bRaz\b", "análise de autoridade"),
)


def sanitize_text(value: str) -> str:
    sanitized = value
    for pattern, replacement in _REPLACEMENTS:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r"\s{2,}", " ", sanitized).strip()
    return sanitized


def sanitize_client_output(output: ClientOutput) -> ClientOutput:
    data = output.model_dump()
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = sanitize_text(value)
        elif isinstance(value, list):
            data[key] = [sanitize_text(item) for item in value]
    return ClientOutput.model_validate(data)


def contains_internal_terms(output: ClientOutput) -> bool:
    serialized = output.model_dump_json()
    return any(re.search(pattern, serialized, flags=re.IGNORECASE) for pattern, _ in _REPLACEMENTS)
