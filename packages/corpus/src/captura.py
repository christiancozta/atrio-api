# -*- coding: utf-8 -*-
"""
captura.py — ATRIO · CORPUS
Orquestrador de captura completa.

Executa, em ordem:
1. corpus_pseudonimizar.py
2. ocr_pendentes.py, se houver PDF em corpus/_ocr_pendente
3. painel.py, se existir
4. exportar_inventario.py, se existir

Melhorias desta versão:
- não confunde ausência de script com ausência de openpyxl;
- informa exatamente qual script não foi encontrado;
- mostra arquivos que permanecerem em corpus/00_entrada após o CORPUS;
- resolve a pasta-base em caminho absoluto para reduzir erro de ../.

Rodar, dentro de scripts/:
    py captura.py --base ../
"""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

# Pasta-mãe resolvida a partir da localização do próprio script, para rodar
# sem .bat e sem --base. Os .bat continuam passando --base ../ e funcionam igual.
BASE_PADRAO = str(Path(__file__).resolve().parent.parent)

AQUI = Path(__file__).resolve().parent


def existe_modulo(nome: str) -> bool:
    return importlib.util.find_spec(nome) is not None


def caminho_script(nome: str) -> Path:
    return AQUI / nome


def roda(script: str, base: Path, extra: list[str] | None = None) -> int:
    alvo = caminho_script(script)

    if not alvo.exists():
        print(f"      [ERRO] Script não encontrado: {alvo}")
        print("      Verifique se o arquivo está na mesma pasta do captura.py.")
        return 127

    cmd = [sys.executable, str(alvo), "--base", str(base)] + (extra or [])
    try:
        return subprocess.run(cmd).returncode
    except Exception as exc:
        print(f"      [ERRO] Falha ao executar {script}: {exc}")
        return 1


def listar_sobras_entrada(base: Path) -> None:
    entrada = base / "corpus" / "00_entrada"

    if not entrada.exists():
        print(f"      [AVISO] Pasta de entrada não encontrada: {entrada}")
        return

    sobras = [p for p in entrada.rglob("*") if p.is_file()]

    if not sobras:
        print("      Entrada verificada: nenhum arquivo restante.")
        return

    print("      [ATENÇÃO] Arquivos ainda presentes em corpus/00_entrada:")
    for p in sobras:
        try:
            rel = p.relative_to(entrada)
        except ValueError:
            rel = p
        print(f"        - {rel}")

    print("      Isso indica que o CORPUS não capturou esses itens, embora tenha finalizado.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_PADRAO,
                    help=f"pasta-mãe do ATRIO (padrão: {BASE_PADRAO})")
    args = ap.parse_args()

    base = Path(args.base).expanduser().resolve()

    print("=" * 52)
    print("  ATRIO · CORPUS — captura automática")
    print("=" * 52)
    print(f"  Base: {base}")
    print(f"  Scripts: {AQUI}")

    # 1. CORPUS
    print("\n[1/4] CORPUS — processando a pasta de captura...")
    cod_corpus = roda("corpus_pseudonimizar.py", base)
    if cod_corpus != 0:
        print(f"      [AVISO] CORPUS retornou código {cod_corpus}.")

    listar_sobras_entrada(base)

    # 2. OCR
    pendentes_dir = base / "corpus" / "_ocr_pendente"
    pendentes = list(pendentes_dir.glob("*.pdf")) if pendentes_dir.exists() else []

    if pendentes:
        print(f"\n[2/4] OCR — {len(pendentes)} escaneado(s) pendente(s)...")
        cod_ocr = roda("ocr_pendentes.py", base)
        if cod_ocr != 0:
            print("      OCR não concluiu. Os arquivos seguem em corpus/_ocr_pendente.")
    else:
        print("\n[2/4] OCR — nada pendente, pulando.")

    # 3. PAINEL
    print("\n[3/4] PAINEL — atualizando o painel visual...")
    cod_painel = roda("painel.py", base)
    if cod_painel == 127:
        print("      Painel não atualizado porque painel.py não foi encontrado.")
    elif cod_painel != 0:
        print(f"      Painel falhou com código {cod_painel}.")

    # 4. INVENTÁRIO
    print("\n[4/4] INVENTÁRIO — atualizando a planilha...")
    cod_excel = roda("exportar_inventario.py", base, ["--nao-abrir"])

    if cod_excel == 127:
        print("      Inventário Excel não atualizado porque exportar_inventario.py não foi encontrado.")
    elif cod_excel != 0:
        if not existe_modulo("openpyxl"):
            print("      Excel não gerado: falta instalar openpyxl neste Python.")
            print("      Comando: py -m pip install openpyxl")
        else:
            print(f"      Excel não gerado. openpyxl existe, mas exportar_inventario.py falhou com código {cod_excel}.")
    else:
        print("      Inventário atualizado.")

    print("\n" + "=" * 52)
    print("  Captura concluída.")
    print("=" * 52)


if __name__ == "__main__":
    main()
