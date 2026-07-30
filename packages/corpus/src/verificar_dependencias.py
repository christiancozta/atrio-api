# -*- coding: utf-8 -*-
"""
verificar_dependencias.py — ATRIO · CORPUS

Confere o que está instalado e imprime exatamente a linha de instalação do que
faltar. É o script que evita a falha mais provável em uso real: rodar o OCR
sem o Tesseract, ou sem o idioma português.

Não instala nada. Só olha e diz.

Rodar:
    py verificar_dependencias.py
"""

import importlib.util
import shutil
import subprocess
import sys

OBRIGATORIOS = [
    ("pdfplumber", "pdfplumber", "ler o texto dos PDFs"),
    ("openpyxl", "openpyxl", "exportar o inventário para Excel"),
]

OCR = [
    ("fitz", "pymupdf", "renderizar a página do PDF em imagem"),
    ("pytesseract", "pytesseract", "conversar com o Tesseract"),
    ("PIL", "pillow", "tratar a imagem antes do OCR"),
]

OPCIONAIS = [
    ("spacy", "spacy", "detecção de nome de pessoa melhor que a heurística"),
]


def tem(modulo):
    return importlib.util.find_spec(modulo) is not None


def checar(grupo, titulo):
    faltando = []
    print(f"\n{titulo}")
    for modulo, pacote, para_que in grupo:
        marca = "ok  " if tem(modulo) else "FALTA"
        print(f"  [{marca}] {pacote:14s} — {para_que}")
        if not tem(modulo):
            faltando.append(pacote)
    return faltando


def checar_tesseract():
    print("\nTesseract (programa do sistema, não é pacote Python)")
    exe = shutil.which("tesseract")
    if not exe:
        print("  [FALTA] tesseract não está no PATH")
        print("          Baixe em https://github.com/UB-Mannheim/tesseract/wiki")
        print("          e marque o idioma 'Portuguese' na instalação.")
        return False
    print(f"  [ok  ] {exe}")
    try:
        saida = subprocess.run([exe, "--list-langs"], capture_output=True,
                               text=True, timeout=30).stdout
    except Exception as e:
        print(f"  [aviso] não deu para listar os idiomas: {e}")
        return True
    if "por" in saida.split():
        print("  [ok  ] idioma 'por' (português) instalado")
        return True
    print("  [FALTA] idioma 'por' (português) NÃO está instalado")
    print("          Reinstale o Tesseract marcando Portuguese, ou copie")
    print("          por.traineddata para a pasta tessdata.")
    return False


def checar_modelo_spacy():
    if not tem("spacy"):
        return
    import spacy
    for modelo in ("pt_core_news_lg", "pt_core_news_md", "pt_core_news_sm"):
        try:
            spacy.load(modelo)
            print(f"  [ok  ] modelo {modelo} carregado")
            return
        except OSError:
            continue
    print("  [FALTA] spacy instalado, mas sem modelo em português")
    print("          py -m spacy download pt_core_news_lg")


def main():
    print("=" * 62)
    print("  ATRIO · CORPUS — verificação de dependências")
    print("=" * 62)
    print(f"\nPython {sys.version.split()[0]} em {sys.executable}")

    falta_obr = checar(OBRIGATORIOS, "Obrigatório — o CORPUS não roda sem isto")
    falta_ocr = checar(OCR, "OCR — só para PDF escaneado, sem camada de texto")
    tesseract_ok = checar_tesseract()
    checar(OPCIONAIS, "Opcional — melhora a detecção de nome")
    checar_modelo_spacy()

    print("\n" + "=" * 62)
    if not falta_obr and not falta_ocr and tesseract_ok:
        print("  Tudo pronto. Nada a instalar.")
        return 0

    print("  Para instalar o que falta, rode:\n")
    if falta_obr:
        print(f"    py -m pip install {' '.join(falta_obr)}")
    if falta_ocr:
        print(f"    py -m pip install {' '.join(falta_ocr)}")
    if not tesseract_ok:
        print("\n  E instale o Tesseract com o idioma português — sem ele o OCR")
        print("  não roda, por mais pacote Python que esteja instalado.")
    if falta_obr:
        return 1
    print("\n  O que falta é só de OCR. O CORPUS roda; PDF escaneado fica")
    print("  esperando em corpus/_ocr_pendente/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
