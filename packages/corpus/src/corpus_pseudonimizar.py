# -*- coding: utf-8 -*-
"""
corpus_pseudonimizar.py — ROBÔ DO CORPUS (entrada).

O que faz, em cima da sua pasta:
  1. lê cada arquivo .pdf (ou .txt) de  corpus/00_entrada/
  2. PDF escaneado (imagem, sem texto) vai pra corpus/_ocr_pendente/ — não finge
     que limpou; fica esperando OCR
  3. manda pro corpus/_segredo/  o que for segredo de justiça
  4. acha os dados pessoais e troca por código consistente ([PESSOA_0001]...)
  5. salva o texto limpo em  corpus/01_pseudonimizado/  (o RATIO lê daqui), em .txt
  6. guarda o mapa código->dado real em  corpus/_cofre/cofre.json
  7. registra o que fez em  corpus/_log/corpus.log

É REVERSÍVEL: o cofre guarda o mapa. Por isso o cofre fica trancado e à parte.

Rodar:
    python3 corpus_pseudonimizar.py --base ./ATRIO
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

import atrio_pii as pii
import atrio_pdf
import atrio_inventario as inv

# Pasta-mãe resolvida a partir da localização do próprio script, para que
# `py corpus_pseudonimizar.py` funcione sem .bat e sem --base. Os .bat
# continuam passando --base ../ e continuam funcionando igual.
BASE_PADRAO = str(Path(__file__).resolve().parent.parent)

PREFIXO = {
    "PESSOA": "PESSOA", "CPF": "CPF", "CNPJ": "CNPJ", "OAB": "OAB",
    "RG": "RG", "EMAIL": "EMAIL", "CEP": "ENDERECO", "TELEFONE": "TELEFONE",
}


def carregar_cofre(caminho):
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return {"by_value": {}, "counters": {}}


def salvar_cofre(caminho, cofre):
    caminho.write_text(json.dumps(cofre, ensure_ascii=False, indent=2),
                       encoding="utf-8")


def token_para(cofre, tipo, valor, origem_cnj):
    """Mesmo valor -> mesmo token, em todo o acervo."""
    chave = f"{tipo}::{valor.strip().lower()}"
    if chave in cofre["by_value"]:
        return cofre["by_value"][chave]["token"]
    pref = PREFIXO.get(tipo, tipo)
    cofre["counters"][pref] = cofre["counters"].get(pref, 0) + 1
    token = f"[{pref}_{cofre['counters'][pref]:04d}]"
    cofre["by_value"][chave] = {
        "token": token,
        "tipo": tipo,
        "valor_real": valor.strip(),
        "origem_cnj": origem_cnj,
        "severidade": "normal",
        "visto_em": datetime.now().isoformat(timespec="seconds"),
    }
    return token


def aplicar(texto, achados, cofre, origem_cnj):
    """Troca cada achado pelo token.
    1ª passada (ordem de leitura): cria/recupera o token de cada achado.
    2ª passada (de trás pra frente): substitui sem quebrar os índices.
    """
    contagem = {}
    tokens = {}
    for ini, fim, tipo, valor in sorted(achados, key=lambda x: x[0]):
        tokens[(ini, fim)] = token_para(cofre, tipo, valor, origem_cnj)
        contagem[tipo] = contagem.get(tipo, 0) + 1
    for ini, fim, tipo, valor in sorted(achados, key=lambda x: x[0], reverse=True):
        texto = texto[:ini] + tokens[(ini, fim)] + texto[fim:]
    return texto, contagem


def achar_cnj(texto):
    m = pii.RE_CNJ.search(texto)
    return m.group() if m else "sem-cnj"


def pasta_processo(cnj, stem):
    """Nome da pasta do processo. Usa o número CNJ; sem ele, agrupa em _sem_cnj."""
    if cnj and cnj != "sem-cnj":
        return cnj           # ex.: 0001234-56.2020.8.16.0001 (seguro como pasta)
    return "_sem_cnj"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_PADRAO,
                    help=f"pasta-mãe do ATRIO (padrão: {BASE_PADRAO})")
    args = ap.parse_args()

    base = Path(args.base)
    p_entrada = base / "corpus" / "00_entrada"
    p_saida   = base / "corpus" / "01_pseudonimizado"
    p_orig    = base / "corpus" / "00_originais"
    p_segredo = base / "corpus" / "_segredo"
    p_cofre   = base / "corpus" / "_cofre" / "cofre.json"
    p_log     = base / "corpus" / "_log" / "corpus.log"
    p_ocr     = base / "corpus" / "_ocr_pendente"
    p_dup     = base / "corpus" / "_duplicados"
    p_revisar = base / "corpus" / "_revisar_segredo"

    for d in (p_saida, p_orig, p_segredo, p_ocr, p_dup, p_revisar,
              p_cofre.parent, p_log.parent):
        d.mkdir(parents=True, exist_ok=True)

    cofre = carregar_cofre(p_cofre)
    ja_vistos = inv.hashes(base)   # hashes já no inventário (deduplicação por arquivo)
    # lê PDF e TXT; PDF é o caso normal (decisão sai do TJPR em PDF)
    arquivos = sorted(p_entrada.glob("*.pdf")) + sorted(p_entrada.glob("*.txt"))

    n_ok = n_seg = n_ocr = n_dup = n_rev = 0
    tot = {}
    linhas_log = [
        f"=== execução {datetime.now().isoformat(timespec='seconds')} ===",
        f"atrio_pii {pii.VERSAO}",
    ]

    for arq in arquivos:
        # 0. deduplicação por arquivo: mesmo PDF já entrou antes?
        h = inv.hash_arquivo(arq)
        if h in ja_vistos:
            shutil.move(str(arq), str(p_dup / arq.name))
            n_dup += 1
            linhas_log.append(f"[DUPLICADO] {arq.name} :: hash já no inventário")
            continue
        ja_vistos.add(h)

        # 1. obter o texto, conforme o tipo de arquivo
        if arq.suffix.lower() == ".pdf":
            try:
                texto, n_pag, suspeita_ocr = atrio_pdf.extrai_texto(arq)
            except Exception as e:
                destino = p_ocr / arq.name
                shutil.move(str(arq), str(destino))
                n_ocr += 1
                inv.registrar(base, inv.nova_linha(
                    hash=h, arquivo=arq.name, cnj=inv.cnj_de(arq.name),
                    situacao="aguardando_ocr", original=str(destino)))
                linhas_log.append(f"[ERRO-PDF] {arq.name} :: {e}")
                continue
            if suspeita_ocr:
                destino = p_ocr / arq.name
                shutil.move(str(arq), str(destino))
                n_ocr += 1
                inv.registrar(base, inv.nova_linha(
                    hash=h, arquivo=arq.name, cnj=inv.cnj_de(arq.name),
                    situacao="aguardando_ocr", original=str(destino)))
                linhas_log.append(f"[OCR] {arq.name} :: PDF sem texto ({n_pag} pág.) — precisa de OCR")
                continue
        else:
            texto = arq.read_text(encoding="utf-8", errors="ignore")

        cnj = achar_cnj(texto)
        classe = inv.classe_processual(texto)

        # 2. segredo de justiça, em dois níveis
        # forte -> sai do reuso agora. fraco -> segue para a base e ganha uma
        # cópia pseudonimizada em _revisar_segredo/ para leitura humana.
        nivel, gatilho = pii.eh_segredo(texto)
        if nivel == "forte":
            destino = p_segredo / arq.name
            shutil.move(str(arq), str(destino))
            n_seg += 1
            inv.registrar(base, inv.nova_linha(
                hash=h, arquivo=arq.name, cnj=cnj, classe=classe,
                situacao="segredo", origem_texto="pdf-texto", original=str(destino)))
            linhas_log.append(f"[SEGREDO] {arq.name} :: gatilho='{gatilho}'")
            continue

        # 3. pseudonimiza e arquiva por processo
        achados = pii.detectar(texto)
        limpo, contagem = aplicar(texto, achados, cofre, cnj)

        pasta = pasta_processo(cnj, arq.stem)
        dir_limpo = p_saida / pasta            # base governada (texto limpo)
        dir_orig  = p_orig / pasta             # arquivo dos originais (dado bruto)
        dir_limpo.mkdir(parents=True, exist_ok=True)
        dir_orig.mkdir(parents=True, exist_ok=True)

        # texto limpo -> pasta do processo na base
        caminho_txt = dir_limpo / (arq.stem + ".txt")
        caminho_txt.write_text(limpo, encoding="utf-8")
        # original sai da entrada -> arquivo de originais (preservado, protegido)
        caminho_orig = dir_orig / arq.name
        shutil.move(str(arq), str(caminho_orig))

        # gatilho fraco: o documento fica na base, mas pede olho humano
        if nivel == "fraco":
            copia = p_revisar / (arq.stem + ".txt")
            copia.write_text(limpo, encoding="utf-8")
            n_rev += 1
            linhas_log.append(f"[REVISAR-SEGREDO] {arq.name} :: gatilho='{gatilho}' :: {copia}")

        inv.registrar(base, inv.nova_linha(
            hash=h, arquivo=arq.name, cnj=cnj, classe=classe,
            situacao="revisar_segredo" if nivel == "fraco" else "na_base",
            origem_texto="pdf-texto",
            dados_trocados=inv.fmt_contagem(contagem),
            txt_limpo=str(caminho_txt), original=str(caminho_orig)))

        n_ok += 1
        for k, v in contagem.items():
            tot[k] = tot.get(k, 0) + v
        resumo = ", ".join(f"{k}:{v}" for k, v in sorted(contagem.items())) or "nada"
        linhas_log.append(f"[OK] {arq.name} :: processo={pasta} :: {resumo}")

    salvar_cofre(p_cofre, cofre)

    linhas_log.append(
        f"--- fim: {n_ok} pseudonimizados, {n_seg} ao segredo, {n_rev} a revisar, "
        f"{n_ocr} p/ OCR, {n_dup} duplicados. "
        f"Totais: " + (", ".join(f"{k}={v}" for k, v in sorted(tot.items())) or "0")
    )
    with p_log.open("a", encoding="utf-8") as f:
        f.write("\n".join(linhas_log) + "\n\n")

    print(f"CORPUS pronto.")
    print(f"  {n_ok} documentos arquivados     -> {p_saida}/<processo>/")
    print(f"  originais preservados           -> {p_orig}/<processo>/")
    print(f"  {n_seg} arquivos ao segredo       -> {p_segredo}")
    print(f"  {n_rev} p/ revisão de segredo     -> {p_revisar}")
    print(f"  {n_ocr} PDFs escaneados p/ OCR    -> {p_ocr}")
    print(f"  {n_dup} duplicados ignorados      -> {p_dup}")
    print(f"  cofre atualizado                 -> {p_cofre}")
    print(f"  inventário atualizado            -> {inv.caminho(base)}")
    print(f"  totais por tipo: " + (", ".join(f"{k}={v}" for k, v in sorted(tot.items())) or "0"))
    print(f"  entrada esvaziada                -> {p_entrada}")
    print(f"  log                              -> {p_log}")


if __name__ == "__main__":
    main()
