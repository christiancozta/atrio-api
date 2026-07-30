# -*- coding: utf-8 -*-
"""
atrio_pii.py — motor de detecção compartilhado.

Acha dados pessoais num texto e devolve uma lista de "achados" (spans).
Os dois robôs (CORPUS e LUX) usam este mesmo motor.

Sem dependência externa: roda só com Python 3.
Detecção de NOME é heurística (por pista textual). Para nome de verdade,
dá pra plugar spaCy depois — ver função detectar_nomes().
"""

import re

VERSAO = "1.0.0"
# Quem importa esta biblioteca grava VERSAO no cabeçalho do log de execução.
# É o que impede o motor compartilhado de mudar o comportamento do CORPUS e do
# LUX ao mesmo tempo sem deixar rastro.

# ----------------------------------------------------------------------
# 1. PADRÕES DE FORMATO FIXO (regex)
# ----------------------------------------------------------------------
# Ordem importa: o que é mais específico/longo vem antes (CNPJ antes de CPF).

# Número CNJ do processo — NÃO é dado pessoal. É a chave do acervo.
# Detectamos só para PROTEGER (nunca mascarar).
RE_CNJ = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")

PADROES = [
    # (tipo, regex)
    ("CNPJ",     re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")),
    ("CPF",      re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
    ("OAB",      re.compile(r"\bOAB\s*[/-]?\s*[A-Z]{2}\s*[-:nº.\s]*\d{1,6}\b", re.IGNORECASE)),
    ("RG",       re.compile(r"\bRG\b[\s:nº.]*\d{1,2}\.?\d{3}\.?\d{3}-?[\dXx]\b", re.IGNORECASE)),
    ("EMAIL",    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("CEP",      re.compile(r"\bCEP[\s:]*\d{5}-?\d{3}\b|\b\d{5}-\d{3}\b", re.IGNORECASE)),
    ("TELEFONE", re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}-\d{4}\b")),
]

# ----------------------------------------------------------------------
# 2. NOME — heurística por pista textual
# ----------------------------------------------------------------------
# Pega "requerente João da Silva", "Sr. Carlos Pereira" etc.
# Não é NER de verdade: erra. Mas funciona sem instalar nada.
# Para melhorar, troque esta função por spaCy (ver GUIA.md).

_PISTAS = (
    r"autor|autora|r[ée]u|r[ée]|requerente|requerido|requerida|"
    r"exequente|executado|executada|embargante|embargado|embargada|"
    r"recorrente|recorrido|recorrida|agravante|agravado|agravada|"
    r"impetrante|impetrado|paciente|interessado|interessada|"
    r"interposto por|interposta por|em face de|em desfavor de|"
    r"ajuizad[ao]s? por|promovid[ao]s? por|movid[ao]s? por|propost[ao]s? por|"
    r"opost[ao]s? por|oferecid[ao]s? por|impetrad[ao]s? por|deduzid[ao]s? por|"
    r"Sr\.|Sra\.|Dr\.|Dra\.|nome(?:ado|ada)?"
)
# Nome próprio: 2 a 6 palavras capitalizadas, com conectores (da, de, do...).
_NOME = (
    r"[A-ZÀ-Ý][a-zà-ÿ]+"
    r"(?:\s+(?:da|de|do|dos|das|e|del|van|von)\s+|\s+)"
    r"(?:[A-ZÀ-Ý][a-zà-ÿ]+(?:\s+(?:da|de|do|dos|das|e)\s+|\s+)?){1,5}"
)
# A PISTA é insensível a maiúscula (pega "Recorrente" no início da frase);
# o NOME continua sensível a maiúscula (exige inicial maiúscula de verdade).
RE_NOME = re.compile(r"(?i:" + _PISTAS + r")[\s:,]*?(" + _NOME + r")")


def _detectar_nomes_heuristica(texto):
    """Nomes por pista textual. Reserva: usada quando o spaCy não está instalado."""
    achados = []
    for m in RE_NOME.finditer(texto):
        ini, fim = m.span(1)              # só o nome, sem a pista
        valor = m.group(1).strip()
        valor = re.sub(r"\s+(da|de|do|dos|das|e)\s*$", "", valor).strip()
        fim = ini + len(valor)
        if len(valor) >= 4:
            achados.append((ini, fim, "PESSOA", valor))
    return achados


# --- spaCy (reconhecedor de nome de verdade) -------------------------
# Carregado uma vez. Tenta o modelo grande, depois médio, depois pequeno.
# Se nada estiver instalado, cai na heurística acima.
_NLP = None


def _carrega_spacy():
    global _NLP
    if _NLP is not None:
        return _NLP
    try:
        import spacy
        for modelo in ("pt_core_news_lg", "pt_core_news_md", "pt_core_news_sm"):
            try:
                _NLP = spacy.load(modelo)
                return _NLP
            except OSError:
                continue
    except ImportError:
        pass
    _NLP = False   # marca "não disponível" para não tentar de novo
    return _NLP


def usando_spacy():
    return bool(_carrega_spacy())


def detectar_nomes(texto):
    """Spans (inicio, fim, 'PESSOA', valor) de nomes de pessoa.
    Usa spaCy quando instalado; senão, a heurística por pista."""
    nlp = _carrega_spacy()
    if not nlp:
        return _detectar_nomes_heuristica(texto)
    achados = []
    for ent in nlp(texto).ents:
        if ent.label_ in ("PER", "PESSOA") and len(ent.text.strip()) >= 4:
            achados.append((ent.start_char, ent.end_char, "PESSOA", ent.text.strip()))
    return achados


# ----------------------------------------------------------------------
# 3. SEGREDO DE JUSTIÇA — triagem por palavra-chave, em dois níveis
# ----------------------------------------------------------------------
# Conservadora de propósito: na dúvida, não usa no reuso.
#
# Dois níveis porque um só produzia falso positivo caro. Termo como "menor"
# aparece legitimamente em causa de consumo ("de menor valor", "de menor
# monta") e, no teste por substring que existia antes, mandava documento comum
# para a pasta de segredo — tirando-o da base sem alarme nenhum.
#
# FORTE segrega automaticamente. FRACO vai para revisão humana, em pasta
# própria, sem sair da base e sem ser arquivado como segredo.
#
# A comparação é por fronteira de palavra, não por substring.

_SEGREDO_FORTE = [
    "segredo de justiça", "tramita em segredo", "sob sigilo",
    "violência doméstica", "lei maria da penha", "maria da penha",
    "estatuto da criança", "eca", "adoção", "curatela", "interdição",
    "investigação de paternidade", "reconhecimento de paternidade",
]

_SEGREDO_FRACO = [
    "menor", "adolescente", "guarda", "alimentos", "divórcio",
    "união estável", "incapaz",
]


def _compilar(termos):
    return [(t, re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE))
            for t in termos]


_RE_FORTE = _compilar(_SEGREDO_FORTE)
_RE_FRACO = _compilar(_SEGREDO_FRACO)


def eh_segredo(texto):
    """Devolve (nivel, termo).

    nivel == "forte"  -> segregar: sai da base, vai para corpus/_segredo/
    nivel == "fraco"  -> revisar:  fica na base, cópia em corpus/_revisar_segredo/
    nivel is None     -> nada encontrado; termo também é None
    """
    for termo, rgx in _RE_FORTE:
        if rgx.search(texto):
            return "forte", termo
    for termo, rgx in _RE_FRACO:
        if rgx.search(texto):
            return "fraco", termo
    return None, None


# ----------------------------------------------------------------------
# 4. MOTOR — junta tudo e resolve sobreposição
# ----------------------------------------------------------------------
def _intervalos_cnj(texto):
    return [m.span() for m in RE_CNJ.finditer(texto)]


def _sobrepoe(a_ini, a_fim, intervalos):
    for (b_ini, b_fim) in intervalos:
        if a_ini < b_fim and b_ini < a_fim:
            return True
    return False


def detectar(texto, proteger_cnj=True):
    """
    Devolve lista de achados ordenada, sem sobreposição:
    [(inicio, fim, tipo, valor), ...]

    proteger_cnj=True  (CORPUS, entrada): o número CNJ é preservado e nada que
        encoste nele entra na lista. É a chave do acervo.
    proteger_cnj=False (LUX, saída pública ou externa): o CNJ deixa de ser
        território protegido. Cabe a quem chamou trocá-lo pelo marcador de
        saída, como manda o kernel do LUX.
    """
    proteger = _intervalos_cnj(texto) if proteger_cnj else []
    brutos = []

    for tipo, rgx in PADROES:
        for m in rgx.finditer(texto):
            brutos.append((m.start(), m.end(), tipo, m.group()))

    if not proteger_cnj:
        for m in RE_CNJ.finditer(texto):
            brutos.append((m.start(), m.end(), "CNJ", m.group()))

    brutos.extend(detectar_nomes(texto))

    # tira o que encosta no número CNJ
    brutos = [a for a in brutos if not _sobrepoe(a[0], a[1], proteger)]

    # ordena e remove sobreposição (fica o que começa antes; em empate, o mais longo)
    brutos.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    limpos = []
    ocupado_ate = -1
    for ini, fim, tipo, valor in brutos:
        if ini >= ocupado_ate:
            limpos.append((ini, fim, tipo, valor))
            ocupado_ate = fim
    return limpos
