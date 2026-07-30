# -*- coding: utf-8 -*-
"""
atrio_pdf.py — abre o PDF e tira o texto.

Devolve (texto, num_paginas, suspeita_ocr).
- texto: o que deu pra extrair.
- suspeita_ocr: True quando o PDF parece ser DIGITALIZADO (imagem, sem camada
  de texto). Nesse caso o texto vem vazio/curto e o robô NÃO deve fingir que
  limpou — manda para a fila de OCR.

Precisa do pdfplumber:  pip install pdfplumber
"""

try:
    import pdfplumber
    _TEM_PDFPLUMBER = True
except ImportError:
    _TEM_PDFPLUMBER = False

# se o PDF rende menos que isto de texto por página, tratamos como escaneado
_MIN_CHARS_POR_PAGINA = 60


def extrai_texto(caminho_pdf):
    if not _TEM_PDFPLUMBER:
        raise RuntimeError(
            "pdfplumber não instalado. Rode:  pip install pdfplumber"
        )

    partes = []
    n_paginas = 0
    with pdfplumber.open(str(caminho_pdf)) as pdf:
        n_paginas = len(pdf.pages)
        for pagina in pdf.pages:
            t = pagina.extract_text() or ""
            if t.strip():
                partes.append(t)

    texto = "\n".join(partes).strip()
    densidade = len(texto) / n_paginas if n_paginas else 0
    suspeita_ocr = densidade < _MIN_CHARS_POR_PAGINA
    return texto, n_paginas, suspeita_ocr
