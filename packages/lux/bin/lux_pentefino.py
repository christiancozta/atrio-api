# -*- coding: utf-8 -*-
"""
lux_pentefino.py — ROBÔ DO LUX (saída).

Roda em cima do TEXTO QUE VAI SAIR (a minuta/parecer pronto), não na base.

O que faz:
  1. re-varre o texto (o RATIO pode ter remontado um dado ao escrever)
  2. CORTA DE VEZ: troca cada dado por marcador de tipo [pessoa], [cpf]...
     -> irreversível: NÃO escreve no cofre. O que sai não tem volta.
     -> em destino público ou externo, o número do processo vira [processo]
  3. SINALIZA para leitura humana o que é contextual (não dá pra cortar no
     automático): "ex-prefeito de X", cargo único + cidade, etc.
  4. salva o texto limpo e um relatório de sinalizações ao lado.

Rodar:
    python3 lux_pentefino.py minuta.txt
    python3 lux_pentefino.py minuta.txt --destino publico
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

import atrio_pii as pii

# corte irreversível: marca fixa por tipo (sem número, sem cofre)
#
# São marcadores DE TIPO, em minúscula, conforme shared/lexicon/tokens.yaml,
# modo "publico". Marcador de papel — [parte autora], [parte ré], [terceiro],
# [município], [instituição] — não entra aqui: um detector por expressão
# regular acha um nome próprio, não sabe de quem é o papel no processo. Papel é
# exclusivo do kernel, que lê contexto. Tipo pode virar papel; papel nunca vira
# tipo.
MARCA = {
    "PESSOA": "[pessoa]", "CPF": "[cpf]", "CNPJ": "[cnpj]", "OAB": "[oab]",
    "RG": "[rg]", "EMAIL": "[e-mail]", "CEP": "[endereço]",
    "TELEFONE": "[telefone]", "CNJ": "[processo]",
}

# pistas de risco contextual — o robô só APONTA; quem corta é você.
RE_CONTEXTO = re.compile(
    r"\b(ex-)?(prefeit[oa]|vereador[a]?|deputad[oa]|governador[a]?|"
    r"secretári[oa]|delegad[oa]|juiz[a]?|desembargador[a]?|"
    r"presidente|diretor[a]?|servidor[a]?)\b",
    re.IGNORECASE,
)


def cortar(texto, achados):
    contagem = {}
    for ini, fim, tipo, valor in sorted(achados, key=lambda x: x[0], reverse=True):
        # indexação direta de propósito: tipo sem marcador é erro de
        # vocabulário e tem de estourar, não virar marca genérica silenciosa
        texto = texto[:ini] + MARCA[tipo] + texto[fim:]
        contagem[tipo] = contagem.get(tipo, 0) + 1
    return texto, contagem


def sinalizar_contexto(texto):
    flags = []
    for i, linha in enumerate(texto.splitlines(), 1):
        if RE_CONTEXTO.search(linha):
            flags.append((i, linha.strip()[:160]))
    return flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo", help="texto de saída a revisar (.txt)")
    ap.add_argument("--destino", choices=["interno", "externo", "publico"],
                    default="publico", help="para onde o texto vai (default: publico)")
    args = ap.parse_args()

    entrada = Path(args.arquivo)
    texto = entrada.read_text(encoding="utf-8", errors="ignore")

    # destino público ou externo: o número do processo também sai, virando
    # [processo]. Só o destino interno preserva o CNJ, que é a chave do acervo.
    proteger_cnj = args.destino == "interno"
    achados = pii.detectar(texto, proteger_cnj=proteger_cnj)
    limpo, contagem = cortar(texto, achados)
    flags = sinalizar_contexto(limpo)

    saida = entrada.with_name(entrada.stem + "_LUX.txt")
    saida.write_text(limpo, encoding="utf-8")

    rel = entrada.with_name(entrada.stem + "_LUX_revisao.txt")
    linhas = [
        f"Pente fino LUX — {datetime.now().isoformat(timespec='seconds')}",
        f"atrio_pii {pii.VERSAO}",
        f"Destino declarado: {args.destino}",
        f"Número CNJ: {'preservado' if proteger_cnj else 'cortado para [processo]'}",
        "",
        "1) CORTADO NO AUTOMÁTICO (irreversível, sem cofre):",
        "   " + (", ".join(f"{k}={v}" for k, v in sorted(contagem.items())) or "nada"),
        "",
        "2) PARA SUA LEITURA — possível identificação por contexto.",
        "   O robô não corta isto. Você decide:",
    ]
    if flags:
        for num, trecho in flags:
            linhas.append(f"   linha {num}: {trecho}")
    else:
        linhas.append("   nada sinalizado.")
    if args.destino != "publico":
        linhas += ["", f"AVISO: destino '{args.destino}'. Se houver dúvida, trate como público."]
    rel.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    print("LUX pronto.")
    print(f"  texto limpo  -> {saida}")
    print(f"  revisão      -> {rel}")
    print(f"  cortado: " + (", ".join(f"{k}={v}" for k, v in sorted(contagem.items())) or "nada"))
    print(f"  sinalizado p/ leitura humana: {len(flags)} linha(s)")


if __name__ == "__main__":
    main()
