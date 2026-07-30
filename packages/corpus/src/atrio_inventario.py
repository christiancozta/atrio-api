# -*- coding: utf-8 -*-
"""
atrio_inventario.py — o inventário do CORPUS.

Uma linha por documento que sai da pasta de entrada. CSV é a fonte da verdade
(escrita pela máquina; você não abre na mão). O Excel é gerado sob demanda pelo
exportar_inventario.py.

Não guarda dado pessoal cru: nome já virou código. Guarda hash, CNJ, classe,
situação, contagens e caminhos. Por isso o inventário pode circular — ao
contrário do cofre e dos originais.

Chave do arquivo: hash SHA-256 do conteúdo. O CNJ deduplica o PROCESSO; o hash
deduplica o ARQUIVO (impede reingestão do mesmo PDF).
"""

import csv
import hashlib
import re
from datetime import datetime
from pathlib import Path

CABECALHO = [
    "hash", "arquivo", "cnj", "classe", "situacao", "origem_texto",
    "dados_trocados", "txt_limpo", "original", "data_hora",
    "assunto", "localizador", "nucleo", "conferido",   # reservadas (taxonomia ECHO + revisão)
]

# situacao ∈ {na_base, revisar_segredo, segredo, aguardando_ocr, ocr_falhou}
#
# revisar_segredo: bateu em gatilho fraco de segredo de justiça. Continua na
# base e continua utilizável; só está marcado para leitura humana, com cópia
# pseudonimizada em corpus/_revisar_segredo/. Não é o mesmo que segredo, que
# sai da base.

_RE_CNJ = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")


def caminho(base):
    return Path(base) / "corpus" / "_inventario" / "inventario.csv"


def hash_arquivo(p, blocos=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(blocos), b""):
            h.update(bloco)
    return h.hexdigest()


def cnj_de(texto_ou_nome):
    m = _RE_CNJ.search(texto_ou_nome or "")
    return m.group() if m else ""


def classe_processual(texto):
    """Classe pela leitura do texto. Heurística simples por palavra-chave."""
    t = (texto or "").upper()
    if "MANDADO DE SEGURAN" in t:   return "MS"
    if "EMBARGOS DE DECLARA" in t:  return "ED"
    if "RECURSO INOMINADO" in t:    return "RI"
    if "AGRAVO" in t:               return "agravo"
    if "SENTEN" in t:               return "sentença"
    return "outro"


def _ler(base):
    p = caminho(base)
    if not p.exists():
        return []
    with p.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _gravar(base, linhas):
    p = caminho(base)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CABECALHO)
        w.writeheader()
        for ln in linhas:
            w.writerow({k: ln.get(k, "") for k in CABECALHO})


def hashes(base):
    return {ln["hash"] for ln in _ler(base) if ln.get("hash")}


def nova_linha(**campos):
    base_linha = {k: "" for k in CABECALHO}
    base_linha["data_hora"] = datetime.now().isoformat(timespec="seconds")
    base_linha["conferido"] = "nao"
    base_linha.update(campos)
    return base_linha


def registrar(base, linha):
    """Acrescenta uma linha (append). Usado quando o hash é novo."""
    p = caminho(base)
    novo = not p.exists()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CABECALHO)
        if novo:
            w.writeheader()
        w.writerow({k: linha.get(k, "") for k in CABECALHO})


def upsert(base, hash_, **campos):
    """Atualiza a linha daquele hash; se não existir, cria. Usado pelo OCR,
    que retoma uma linha antes marcada como aguardando_ocr."""
    linhas = _ler(base)
    for ln in linhas:
        if ln.get("hash") == hash_:
            ln.update({k: v for k, v in campos.items() if v is not None})
            _gravar(base, linhas)
            return
    nova = nova_linha(hash=hash_, **campos)
    registrar(base, nova)


def fmt_contagem(contagem):
    """Ex.: {'PESSOA':2,'CPF':1} -> 'PESSOA=2;CPF=1'."""
    return ";".join(f"{k}={v}" for k, v in sorted(contagem.items())) if contagem else ""
