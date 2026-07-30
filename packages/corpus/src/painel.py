# -*- coding: utf-8 -*-
"""
painel.py — Painel CORPUS em linguagem visual ATRIO.

Substitui o painel visual antigo sem alterar a orquestra:
    captura.py continua chamando: py painel.py --base ../

Gera:
    corpus/painel.html

Características:
- calcula os dados a partir da estrutura real do CORPUS;
- não depende de bibliotecas externas;
- abre em navegador via webbrowser, não por associação .html do Windows;
- no nome CORPUS, apenas o C fica terracota.
"""

import argparse
import html
import json
import re
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

# Pasta-mãe resolvida a partir da localização do próprio script, para rodar
# sem .bat e sem --base. Os .bat continuam passando --base ../ e funcionam igual.
BASE_PADRAO = str(Path(__file__).resolve().parent.parent)

CNJ_RE = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")


def esc(value):
    return html.escape(str(value), quote=True)


def count_files(path: Path, patterns=None) -> int:
    if not path.exists():
        return 0
    if patterns:
        total = 0
        for pattern in patterns:
            total += sum(1 for p in path.rglob(pattern) if p.is_file())
        return total
    return sum(1 for p in path.rglob("*") if p.is_file())


def infer_cnj(text: str) -> str:
    match = CNJ_RE.search(text or "")
    return match.group(0) if match else "—"


def file_mtime_safe(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def process_inventory(corpus_dir: Path):
    """Retorna lista de processos a partir de corpus/01_pseudonimizado."""
    pseudo = corpus_dir / "01_pseudonimizado"
    rows = []

    if not pseudo.exists():
        return rows

    for item in pseudo.iterdir():
        if item.is_dir():
            files = [p for p in item.rglob("*") if p.is_file()]
            if not files:
                continue
            cnj = infer_cnj(item.name)
            last = max(file_mtime_safe(p) for p in files)
            rows.append({
                "processo": cnj,
                "documentos": len(files),
                "last": last,
            })
        elif item.is_file():
            cnj = infer_cnj(item.name)
            rows.append({
                "processo": cnj,
                "documentos": 1,
                "last": file_mtime_safe(item),
            })

    grouped = {}
    for row in rows:
        key = row["processo"]
        if key not in grouped:
            grouped[key] = row
        else:
            grouped[key]["documentos"] += row["documentos"]
            grouped[key]["last"] = max(grouped[key]["last"], row["last"])

    return sorted(grouped.values(), key=lambda r: r["last"], reverse=True)


def count_cofre_records(obj) -> int:
    """Conta registros reais do cofre sem presumir formato único.

    Se encontrar dicionários com aparência de registro de pseudonimização,
    conta 1. Caso contrário, percorre recursivamente.
    """
    if isinstance(obj, dict):
        keys = set(str(k).lower() for k in obj.keys())
        record_markers = {"token", "valor_real", "valor", "origem", "severidade", "visto_em"}
        if keys.intersection(record_markers) and ("token" in keys or "valor_real" in keys or "valor" in keys):
            return 1
        return sum(count_cofre_records(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_cofre_records(v) for v in obj)
    return 0


def count_cofre(corpus_dir: Path) -> int:
    cofre = corpus_dir / "_cofre" / "cofre.json"
    if not cofre.exists():
        return 0
    try:
        with cofre.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0

    counted = count_cofre_records(data)
    if counted:
        return counted

    # Fallback conservador para formatos simples tipo {chave: valor}
    if isinstance(data, dict):
        return len(data)
    if isinstance(data, list):
        return len(data)
    return 0


def latest_execution_label(corpus_dir: Path) -> str:
    log = corpus_dir / "_log" / "corpus.log"
    if log.exists():
        try:
            mtime = datetime.fromtimestamp(log.stat().st_mtime)
            return "execução " + mtime.strftime("%Y-%m-%dT%H:%M:%S")
        except OSError:
            pass
    return "execução não localizada"


def build_html(metrics):
    cards_html = "\n".join(
        f'''      <article class="metric-card"><div class="metric-value">{esc(value)}</div><div class="metric-label">{esc(label)}</div></article>'''
        for label, value in metrics["cards"]
    )

    if metrics["processos"]:
        rows_html = "\n".join(
            f'''            <tr><td class="cnj">{esc(row["processo"])}</td><td class="num">{esc(row["documentos"])}</td></tr>'''
            for row in metrics["processos"][:8]
        )
    else:
        rows_html = '''            <tr><td class="empty" colspan="2">Nenhum processo localizado em 01_pseudonimizado.</td></tr>'''

    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>CORPUS — Painel</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..700&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
<style>
:root{{
  --white:#FFFFFF;
  --ink:#0C0C0C;
  --graph:#181310;
  --terra:#A63A23;
  --gray:#E5E2DC;
  --rule:rgba(12,12,12,.12);
  --mut:#6B6B6B;
  --mut2:#8C8881;
  --serif:'Fraunces',serif;
  --sans:'IBM Plex Sans',sans-serif;
  --mono:'IBM Plex Mono',monospace;
}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html{{background:var(--white);}}
body{{font-family:var(--sans);background:var(--white);color:var(--ink);line-height:1.6;-webkit-font-smoothing:antialiased;font-weight:400;}}
::selection{{background:var(--terra);color:var(--white);}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 56px;}}
.page{{min-height:100vh;padding:72px 0 58px;}}
.topbar{{display:flex;align-items:center;justify-content:space-between;gap:24px;border-bottom:1px solid var(--ink);padding-bottom:18px;margin-bottom:48px;}}
.kicker{{font-family:var(--mono);font-size:11px;letter-spacing:.26em;text-transform:uppercase;color:var(--mut);}}
.generated{{font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--mut2);text-align:right;}}
.hero{{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:64px;align-items:end;margin-bottom:64px;}}
h1{{font-family:var(--serif);font-weight:650;font-size:clamp(72px,12vw,156px);line-height:.84;letter-spacing:-.05em;font-optical-sizing:auto;font-variation-settings:"SOFT" 0,"WONK" 0;}}
h1 .cmark{{color:var(--terra);}}
.subtitle{{margin-top:22px;font-size:clamp(18px,1.7vw,22px);font-weight:300;max-width:760px;color:var(--ink);}}
.exec-box{{border-top:1px solid var(--ink);border-bottom:1px solid var(--ink);padding:18px 0;font-family:var(--mono);font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:var(--mut);}}
.exec-box b{{display:block;margin-top:8px;color:var(--ink);font-weight:500;text-transform:none;letter-spacing:.04em;}}
.flow{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0 0 46px;font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);}}
.flow span{{border:1px solid var(--gray);padding:7px 12px;background:#fff;}}
.flow .core{{color:var(--ink);border-color:var(--ink);}}
.flow .core .cmark{{color:var(--terra);}}
.flow i{{font-style:normal;color:var(--mut2);}}
.metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--gray);border:1px solid var(--gray);margin-bottom:70px;}}
.metric-card{{background:var(--white);padding:34px 32px 32px;min-height:150px;display:flex;flex-direction:column;justify-content:space-between;}}
.metric-value{{font-family:var(--serif);font-weight:650;font-size:clamp(44px,5vw,70px);line-height:1;letter-spacing:-.035em;color:var(--ink);}}
.metric-label{{margin-top:18px;font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--mut);}}
.section-head{{display:grid;grid-template-columns:220px 1fr;gap:54px;border-top:1px solid var(--rule);padding-top:28px;margin-bottom:20px;}}
.index{{font-family:var(--serif);font-size:106px;font-weight:650;line-height:.8;letter-spacing:-.055em;color:rgba(12,12,12,.13);}}
h2{{font-family:var(--serif);font-size:clamp(34px,4vw,54px);font-weight:600;line-height:1.03;letter-spacing:-.03em;}}
.table-wrap{{display:grid;grid-template-columns:220px 1fr;gap:54px;margin-bottom:64px;}}
table{{width:100%;border-collapse:collapse;font-size:14px;}}
td{{padding:13px 0;border-bottom:1px solid var(--gray);}}
.cnj{{font-family:var(--mono);font-size:13px;letter-spacing:.02em;}}
.num{{width:120px;text-align:right;font-family:var(--mono);color:var(--mut);}}
.empty{{text-align:center;color:var(--mut);font-family:var(--mono);font-size:12px;letter-spacing:.04em;}}
.footer{{border-top:1px solid var(--gray);padding-top:22px;font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;color:var(--mut);max-width:760px;line-height:1.8;}}
@media(max-width:900px){{
  .wrap{{padding:0 28px;}}
  .page{{padding:42px 0;}}
  .topbar{{align-items:flex-start;flex-direction:column;}}
  .generated{{text-align:left;}}
  .hero{{grid-template-columns:1fr;gap:34px;}}
  .metrics{{grid-template-columns:1fr 1fr;}}
  .section-head,.table-wrap{{grid-template-columns:1fr;gap:18px;}}
  .index{{font-size:86px;}}
}}
@media(max-width:560px){{.metrics{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>
<main class="page">
  <div class="wrap">
    <div class="topbar">
      <div class="kicker">ATRIO · CORPUS · painel operacional</div>
      <div class="generated">gerado em {esc(metrics["gerado_em"])}</div>
    </div>

    <section class="hero" aria-label="Painel CORPUS">
      <div>
        <h1><span class="cmark">C</span>ORPUS</h1>
        <p class="subtitle">Painel de leitura da base documental governada. Não altera cofre, originais, pseudônimos ou documentos capturados.</p>
      </div>
      <div class="exec-box">última execução <b>{esc(metrics["execucao"])}</b></div>
    </section>

    <div class="flow" aria-label="Fluxo do CORPUS">
      <span>entrada</span><i>→</i><span class="core"><span class="cmark">C</span>ORPUS</span><i>→</i><span>base limpa</span>
      <i>·</i><span>segredo</span><i>/</i><span>OCR</span>
    </div>

    <section class="metrics" aria-label="Indicadores">
{cards_html}
    </section>

    <section class="section-head">
      <div class="index">01</div>
      <div><h2>Processos recentes</h2></div>
    </section>

    <section class="table-wrap">
      <div></div>
      <table aria-label="Processos recentes">
        <tbody>
{rows_html}
        </tbody>
      </table>
    </section>

    <footer class="footer">
      Painel somente de leitura. Atualize rodando o atalho de captura novamente. O cofre e os originais permanecem fora desta visualização.
    </footer>
  </div>
</main>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=BASE_PADRAO,
                        help=f"pasta-mãe do ATRIO (padrão: {BASE_PADRAO})")
    parser.add_argument("--nao-abrir", action="store_true", help="gera o painel sem abrir no navegador")
    args = parser.parse_args()

    base = Path(args.base).resolve()
    corpus_dir = base / "corpus"
    output = corpus_dir / "painel.html"

    try:
        corpus_dir.mkdir(parents=True, exist_ok=True)

        processos = process_inventory(corpus_dir)
        docs_limpos = sum(row["documentos"] for row in processos)
        cofre_count = count_cofre(corpus_dir)
        segredo_count = count_files(corpus_dir / "_segredo")
        revisar_count = count_files(corpus_dir / "_revisar_segredo")
        ocr_pendente = count_files(corpus_dir / "_ocr_pendente", ["*.pdf", "*.PDF"])
        ocr_falhou = count_files(corpus_dir / "_ocr_falhou")

        metrics = {
            "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "execucao": latest_execution_label(corpus_dir),
            "processos": processos,
            "cards": [
                ("processos na base", len(processos)),
                ("documentos limpos", docs_limpos),
                ("itens no cofre", cofre_count),
                ("em segredo", segredo_count),
                ("a revisar", revisar_count),
                ("OCR pendente", ocr_pendente),
                ("OCR falhou", ocr_falhou),
            ],
        }

        output.write_text(build_html(metrics), encoding="utf-8")

        print(f"Painel gerado: {output}")
        print(
            f"  processos={len(processos)}  documentos={docs_limpos}  "
            f"cofre={cofre_count}  segredo={segredo_count}  "
            f"revisar={revisar_count}  "
            f"ocr_pendente={ocr_pendente}  ocr_falhou={ocr_falhou}"
        )

        if not args.nao_abrir:
            webbrowser.open(output.resolve().as_uri())

        return 0

    except Exception as exc:
        print(f"ERRO ao gerar painel: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
