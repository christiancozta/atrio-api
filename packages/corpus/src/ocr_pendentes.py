# -*- coding: utf-8 -*-
"""
ocr_pendentes.py — QUARTO ROBÔ (OCR dos escaneados).

Pega os PDFs que o robô do CORPUS mandou para  corpus/_ocr_pendente/
(decisões digitalizadas, sem camada de texto), lê por OCR e devolve à linha
normal: segredo -> pseudonimização -> pasta do processo -> mesmo cofre.

Reaproveita os motores existentes (atrio_pii, corpus_pseudonimizar): o
tratamento é o mesmo dos outros documentos, e o cofre é o mesmo — uma pessoa
num escaneado recebe o mesmo código que recebeu nos documentos de texto.

NÃO precisa de Poppler. Usa PyMuPDF para virar a página em imagem.
Instalar:
  pip install pymupdf pytesseract pillow
E o Tesseract (o motor de OCR), com o idioma português:
  - Windows: instalador da UB-Mannheim (marque o idioma 'Portuguese').
             Se o Tesseract não estiver no PATH, passe --tesseract "C:\\...\\tesseract.exe"
  - Mac:     brew install tesseract tesseract-lang
  - Linux:   apt install tesseract-ocr tesseract-ocr-por

Rodar:
    py ocr_pendentes.py --base ../
    py ocr_pendentes.py --base ../ --dpi 400 --tesseract "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
"""

import argparse
import shutil
from datetime import datetime
from pathlib import Path

import atrio_pii as pii
import corpus_pseudonimizar as corpus   # cofre, aplicar, achar_cnj, pasta_processo
import atrio_inventario as inv

try:
    import fitz                      # PyMuPDF (rasteriza sem Poppler)
    import pytesseract
    from PIL import Image
    _TEM_OCR = True
except ImportError:
    _TEM_OCR = False

# se mesmo após o OCR o texto vier curto demais, o reconhecimento falhou
_MIN_CHARS = 80


def ocr_pdf(caminho, idioma="por", dpi=300):
    """Vira cada página em imagem (PyMuPDF) e lê o texto (Tesseract)."""
    doc = fitz.open(str(caminho))
    zoom = dpi / 72.0
    matriz = fitz.Matrix(zoom, zoom)
    partes = []
    for pagina in doc:
        pix = pagina.get_pixmap(matrix=matriz)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        partes.append(pytesseract.image_to_string(img, lang=idioma))
    doc.close()
    return "\n".join(partes).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=corpus.BASE_PADRAO,
                    help=f"pasta-mãe do ATRIO (padrão: {corpus.BASE_PADRAO})")
    ap.add_argument("--idioma", default="por", help="idioma do OCR (default: por)")
    ap.add_argument("--dpi", type=int, default=300, help="resolução do OCR (default: 300)")
    ap.add_argument("--tesseract", default=None,
                    help='caminho do tesseract.exe, se não estiver no PATH (Windows)')
    args = ap.parse_args()

    if not _TEM_OCR:
        raise RuntimeError(
            "Faltam dependências de OCR. Rode:  pip install pymupdf pytesseract pillow\n"
            "e instale o Tesseract (idioma 'por')."
        )
    if args.tesseract:
        pytesseract.pytesseract.tesseract_cmd = args.tesseract

    base = Path(args.base)
    p_ocr     = base / "corpus" / "_ocr_pendente"
    p_saida   = base / "corpus" / "01_pseudonimizado"
    p_orig    = base / "corpus" / "00_originais"
    p_segredo = base / "corpus" / "_segredo"
    p_falhou  = base / "corpus" / "_ocr_falhou"
    p_cofre   = base / "corpus" / "_cofre" / "cofre.json"
    p_log     = base / "corpus" / "_log" / "corpus.log"
    p_revisar = base / "corpus" / "_revisar_segredo"

    for d in (p_saida, p_orig, p_segredo, p_falhou, p_revisar,
              p_cofre.parent, p_log.parent):
        d.mkdir(parents=True, exist_ok=True)

    cofre = corpus.carregar_cofre(p_cofre)
    arquivos = sorted(p_ocr.glob("*.pdf"))

    n_ok = n_seg = n_falhou = n_rev = 0
    tot = {}
    linhas_log = [
        f"=== OCR {datetime.now().isoformat(timespec='seconds')} ===",
        f"atrio_pii {pii.VERSAO}",
    ]

    for arq in arquivos:
        h = inv.hash_arquivo(arq)   # mesmo hash da linha criada pelo CORPUS
        try:
            texto = ocr_pdf(arq, idioma=args.idioma, dpi=args.dpi)
        except Exception as e:
            destino = p_falhou / arq.name
            shutil.move(str(arq), str(destino))
            n_falhou += 1
            inv.upsert(base, h, situacao="ocr_falhou", original=str(destino))
            linhas_log.append(f"[OCR-ERRO] {arq.name} :: {e}")
            continue

        if len(texto) < _MIN_CHARS:
            destino = p_falhou / arq.name
            shutil.move(str(arq), str(destino))
            n_falhou += 1
            inv.upsert(base, h, situacao="ocr_falhou", original=str(destino))
            linhas_log.append(f"[OCR-FRACO] {arq.name} :: OCR rendeu pouco texto ({len(texto)} chars) — revisar à mão")
            continue

        cnj = corpus.achar_cnj(texto)
        classe = inv.classe_processual(texto)

        nivel, gatilho = pii.eh_segredo(texto)
        if nivel == "forte":
            destino = p_segredo / arq.name
            shutil.move(str(arq), str(destino))
            n_seg += 1
            inv.upsert(base, h, situacao="segredo", cnj=cnj, classe=classe,
                       origem_texto="ocr", original=str(destino))
            linhas_log.append(f"[SEGREDO/OCR] {arq.name} :: gatilho='{gatilho}'")
            continue

        achados = pii.detectar(texto)
        limpo, contagem = corpus.aplicar(texto, achados, cofre, cnj)

        pasta = corpus.pasta_processo(cnj, arq.stem)
        dir_limpo = p_saida / pasta
        dir_orig  = p_orig / pasta
        dir_limpo.mkdir(parents=True, exist_ok=True)
        dir_orig.mkdir(parents=True, exist_ok=True)

        caminho_txt = dir_limpo / (arq.stem + "_ocr.txt")
        caminho_txt.write_text(limpo, encoding="utf-8")
        caminho_orig = dir_orig / arq.name
        shutil.move(str(arq), str(caminho_orig))

        # gatilho fraco: fica na base e ganha cópia pseudonimizada para revisão
        if nivel == "fraco":
            copia = p_revisar / (arq.stem + "_ocr.txt")
            copia.write_text(limpo, encoding="utf-8")
            n_rev += 1
            linhas_log.append(f"[REVISAR-SEGREDO/OCR] {arq.name} :: gatilho='{gatilho}' :: {copia}")

        inv.upsert(base, h,
                   situacao="revisar_segredo" if nivel == "fraco" else "na_base",
                   cnj=cnj, classe=classe,
                   origem_texto="ocr", dados_trocados=inv.fmt_contagem(contagem),
                   txt_limpo=str(caminho_txt), original=str(caminho_orig))

        n_ok += 1
        for k, v in contagem.items():
            tot[k] = tot.get(k, 0) + v
        resumo = ", ".join(f"{k}:{v}" for k, v in sorted(contagem.items())) or "nada"
        linhas_log.append(f"[OK/OCR] {arq.name} :: processo={pasta} :: {resumo}")

    corpus.salvar_cofre(p_cofre, cofre)

    linhas_log.append(
        f"--- fim OCR: {n_ok} arquivados, {n_seg} ao segredo, {n_rev} a revisar, "
        f"{n_falhou} falharam. "
        f"Totais: " + (", ".join(f"{k}={v}" for k, v in sorted(tot.items())) or "0")
    )
    with p_log.open("a", encoding="utf-8") as f:
        f.write("\n".join(linhas_log) + "\n\n")

    print("OCR pronto.")
    print(f"  {n_ok} arquivados              -> {p_saida}\\<processo>\\ (com sufixo _ocr)")
    print(f"  {n_seg} ao segredo")
    print(f"  {n_rev} p/ revisão de segredo   -> {p_revisar}")
    print(f"  {n_falhou} falharam              -> {p_falhou}  (veja o motivo no log)")
    print(f"  totais por tipo: " + (", ".join(f"{k}={v}" for k, v in sorted(tot.items())) or "0"))
    print()
    print("Atenção: texto de OCR erra mais que texto nativo. Os arquivos com")
    print("sufixo _ocr merecem uma conferida humana antes de virar base definitiva.")


if __name__ == "__main__":
    main()
