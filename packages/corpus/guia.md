# GUIA — Anonimização ATRIO (como rodar)

Você tem **três robôs** e dois **motores** que eles usam:

| Arquivo | É o quê |
|---|---|
| `atrio_pii.py` | motor de detecção de dado pessoal (os robôs chamam) |
| `atrio_pdf.py` | motor que abre o PDF e tira o texto (o robô do CORPUS chama) |
| `corpus_pseudonimizar.py` | **robô do CORPUS** — lê os PDFs, limpa, troca dado por código, guarda o cofre |
| `ocr_pendentes.py` | **robô do OCR** — lê os PDFs escaneados que ficaram pendentes e os devolve à linha |
| `lux_pentefino.py` | **robô do LUX** — limpa o texto que vai sair, corta de vez, sinaliza o resto |
| `painel.py` | mostra o estado do CORPUS num painel visual (só lê, não altera) |
| `atrio_inventario.py` | motor do inventário (os robôs registram cada documento aqui) |
| `exportar_inventario.py` | gera o inventário em Excel sob demanda |
| `RODAR_CORPUS.bat` | **atalho de clique** — processa a entrada e abre o painel |
| `PAINEL.bat` | **atalho de clique** — só abre o painel, sem processar |
| `INVENTARIO.bat` | **atalho de clique** — gera e abre o inventário em Excel |

Regra que separa os dois robôs principais: o **CORPUS** é reversível (tem cofre); o **LUX** é irreversível (sem cofre). O cofre nunca sai do CORPUS.

> **Pré-requisito:** Python 3 e a biblioteca de leitura de PDF. No terminal:
> ```
> python3 --version
> pip install pdfplumber
> ```

> **Entrada são PDFs.** Jogue os `.pdf` direto em `corpus/00_entrada/` — o robô abre e extrai sozinho. (Também aceita `.txt`, se um dia precisar.)
>
> **PDF de texto × PDF escaneado.** Decisão nascida digital (o caso normal do TJPR recente) tem camada de texto e é extraída na hora. Decisão **digitalizada** (imagem de papel) não tem texto: o robô não inventa — manda para `corpus/_ocr_pendente/` e segue. Esses ficam esperando OCR (passo opcional, ver no fim).
>
> **A base sai em `.txt`, não em PDF.** A memória governada do ATRIO é texto — é o que o RATIO e a busca consomem. O PDF original fica preservado em `00_entrada/`; o que vira corpus é o texto extraído e pseudonimizado.

---

## Passo 0 — Montar a pasta

No desktop, deixe assim (os scripts juntos numa pasta `scripts/`):

```
ATRIO/
├── scripts/
│   ├── atrio_pii.py
│   ├── atrio_pdf.py
│   ├── corpus_pseudonimizar.py
│   ├── ocr_pendentes.py
│   ├── lux_pentefino.py
│   ├── painel.py
│   ├── RODAR_CORPUS.bat
│   └── PAINEL.bat
└── corpus/
    └── 00_entrada/        ← jogue aqui os .pdf das decisões
```

As outras pastas o robô cria sozinho na primeira vez:

```
ATRIO/corpus/
├── 00_entrada/          ← você põe os PDFs aqui; o robô esvazia depois
├── 00_originais/        ← PDF original, arquivado por processo (DADO BRUTO — proteger)
│   └── 0001234-56.2020.8.16.0001/
│       ├── RI_decisao.pdf
│       └── ED_decisao.pdf
├── 01_pseudonimizado/   ← a base limpa, por processo (o RATIO lê daqui)
│   └── 0001234-56.2020.8.16.0001/
│       ├── RI_decisao.txt
│       └── ED_decisao.txt
├── _cofre/              ← mapa código→dado real (proteger)
├── _segredo/            ← segredo de justiça (fora do reuso)
├── _ocr_pendente/       ← PDFs escaneados, à espera de OCR
└── _log/                ← registro de cada execução
```

Você só cria `00_entrada/` e põe os PDFs dentro. Todos os documentos de um mesmo processo (RI, ED, MS) caem na **mesma pasta**, identificada pelo número CNJ.

---

## O jeito fácil — clique, sem terminal

Depois de montar a pasta uma vez, o dia a dia não precisa de comando nenhum:

1. Jogue os PDFs em `corpus/00_entrada/`.
2. Dê **dois cliques em `RODAR_CORPUS.bat`** (dentro de `scripts/`).

Ele processa a entrada e abre, no navegador, o **painel** — com quantos processos entraram na base, quantos documentos, quanto há no cofre, e se sobrou algo no segredo ou esperando OCR. Para só **olhar o painel** sem processar nada, dois cliques em `PAINEL.bat`.

> Dica: clique com o botão direito no `RODAR_CORPUS.bat` → *Enviar para* → *Área de trabalho (criar atalho)*. Aí você roda o CORPUS de um clique na sua área de trabalho.

Quem prefere o terminal, ou quer entender o que cada passo faz por dentro, segue abaixo.

---

## Passo 1 — Rodar o CORPUS (a base)

Abra o terminal **dentro da pasta `scripts/`** e rode:

```
python3 corpus_pseudonimizar.py --base ../
```

(`--base ../` diz ao robô que a pasta-mãe `ATRIO` está um nível acima de `scripts/`.)

O que ele faz, em cima de cada arquivo de `00_entrada/`:

1. **abre o PDF e extrai o texto**; se for PDF escaneado (sem texto), manda para `_ocr_pendente/` e segue (não finge que limpou);
2. se for **segredo de justiça** (guarda, alimentos, menor, violência doméstica...), copia para `_segredo/` e **não** usa no reuso;
3. acha CPF, CNPJ, OAB, e-mail, telefone, CEP e nomes, e troca por código (`[PESSOA_0001]`...);
4. **não toca no número do processo** (é a chave do acervo);
5. cria a **pasta do processo** (pelo número CNJ) e guarda ali o texto limpo, em `.txt` — é daqui que o RATIO lê;
6. **tira o PDF original da entrada** e o arquiva em `00_originais/<processo>/` (preservado, mas é dado bruto — proteger);
7. guarda o mapa `código → dado real` em `_cofre/cofre.json`;
8. anota tudo em `_log/corpus.log`.

Ao fim, a `00_entrada/` fica **vazia**: tudo que entrou foi para o seu lugar (base, segredo, OCR ou originais). Rodar de novo não reprocessa o que já passou.

**Consistência:** o mesmo CPF (ou a mesma pessoa) recebe **sempre o mesmo código**, em todos os arquivos. Por isso você ainda consegue cruzar processos sem saber quem é a pessoa.

---

## Passo 2 — Rodar o LUX (a saída)

Quando o RATIO produzir um texto (minuta, parecer) e ele for **sair**, passe o LUX antes:

```
python3 lux_pentefino.py ../minuta.txt --destino publico
```

`--destino` pode ser `interno`, `externo` ou `publico` (o padrão é `publico` — o mais seguro).

O LUX gera dois arquivos ao lado do original:

- `minuta_LUX.txt` → o texto **limpo**, com os dados cortados de vez (`[NOME]`, `[CPF]`...). Esse é o que sai.
- `minuta_LUX_revisao.txt` → um **relatório para você ler**: o que foi cortado no automático, e o que ele **não** cortou porque depende de juízo (ex.: "o ex-prefeito do município X"). Isso o robô só aponta — quem decide é você.

---

## As duas decisões que são suas

O sistema funciona, mas há duas escolhas que mudam o comportamento e que eu deixei para você:

1. **Agente público** (magistrado, servidor, advogado nominado): hoje o robô **trata nome como dado** e mascara. Se você quiser **preservar** quem atua em função pública, dá para criar uma lista de exceção. Diga e eu monto.
2. **Nível por destino:** hoje o LUX corta igual para qualquer destino. Se quiser que `interno` corte menos que `publico`, também dá — é regra a definir.

---

## Limites — ditos com honestidade

O robô economiza trabalho. Ele **não** zera a revisão humana.

- **Nome é o ponto fraco.** A detecção de nome funciona por pista ("requerente Fulano", "interposto por Fulano"). Nome solto, sem pista, pode escapar. Por isso o LUX entrega o relatório de revisão — para o seu olho fechar o que a máquina deixou.
- **Endereço:** hoje pega o CEP, não a rua inteira. "Rua das Flores, 100" sem CEP pode passar.
- **Regex erra nas duas pontas:** às vezes pega o que não devia (um número que parecia CPF), às vezes deixa passar. Olhe o log.
- **Pseudonimizar a base não é "estar em conformidade".** É segurança e minimização na base em repouso. A conformidade é do sistema inteiro; o corte que tira o dado do escopo da lei é o do LUX, na saída.

---

## PDFs escaneados — rodar o OCR

Os PDFs que caírem em `_ocr_pendente/` são imagens de papel: não têm texto para extrair. O **robô do OCR** lê esses por reconhecimento de imagem e os devolve à linha normal (segredo → pseudonimização → pasta do processo → mesmo cofre).

Primeiro, instale o OCR (uma vez só) — **sem Poppler**:

```
pip install pymupdf pytesseract pillow
```

E o motor de OCR (o Tesseract), com o idioma português:
- **Windows:** baixe o instalador do Tesseract (build da UB-Mannheim) e, na instalação, marque o idioma **Portuguese**. Se ele não ficar no PATH, não tem problema — você passa o caminho na hora de rodar (veja abaixo).
- **Mac:** `brew install tesseract tesseract-lang`
- **Linux:** `apt install tesseract-ocr tesseract-ocr-por`

Depois, de dentro de `scripts/`:

```
py ocr_pendentes.py --base ../
```

Se o Windows reclamar que não acha o Tesseract, aponte o caminho do `.exe`:

```
py ocr_pendentes.py --base ../ --tesseract "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Se o scan for de baixa qualidade e vier pouco texto, aumente a resolução: `--dpi 400` (ou `600`).

Ele lê cada PDF de `_ocr_pendente/`, pseudonimiza, arquiva na pasta do processo (com sufixo `_ocr` no nome) e esvazia a fila. O que não conseguir ler vai para `_ocr_falhou/` — e o motivo fica registrado no `_log/corpus.log`.

> **OCR erra mais que texto nativo.** Letra trocada pode esconder um CPF ou um nome do detector. Por isso os arquivos `_ocr` ficam marcados: merecem um olhar humano antes de virarem base definitiva.

> Decisão do TJPR recente costuma ser nascida digital (tem texto), e nem passa por aqui. A chance é que `_ocr_pendente/` fique quase vazio. Rode o passo 1 e veja.

---

## Como melhorar a detecção de nome (quando quiser)

A forma robusta é trocar a heurística por um reconhecedor de verdade (spaCy, modelo de português). É um passo opcional:

```
pip install spacy
python3 -m spacy download pt_core_news_lg
```

Depois é só substituir a função `detectar_nomes()` em `atrio_pii.py` por uma versão que use o spaCy. Quando você quiser dar esse passo, eu te entrego a função pronta — o resto do sistema não muda, porque tudo já passa por esse mesmo ponto.

---

## O inventário — uma linha por documento

Todo documento que sai da entrada é registrado num inventário: `corpus/_inventario/inventario.csv`. Os robôs escrevem ali sozinhos — você não preenche nada à mão. Cada linha é um documento, com hash, processo (CNJ), classe (RI/ED/...), situação (`na_base`, `segredo`, `aguardando_ocr`, `ocr_falhou`), origem do texto, quantos dados foram trocados, e os caminhos. As colunas de **assunto / localizador / núcleo** ficam reservadas e vazias — é onde a taxonomia do ECHO entra depois.

Duas propriedades que valem entender:

- **O hash deduplica.** Se você soltar o mesmo PDF de novo, o robô reconhece pelo conteúdo e manda para `_duplicados/` em vez de processar duas vezes. O CNJ deduplica o processo; o hash deduplica o arquivo.
- **O inventário não tem dado pessoal cru.** Nome já virou código; ele guarda CNJ, nomes de arquivo, contagens. Por isso é o único registro da governança que **pode circular** — você o mostra a um auditor ou cliente sem expor ninguém. O cofre e os originais ficam trancados; o inventário, não.

**Para ver/trabalhar no Excel:** dois cliques em `INVENTARIO.bat` (precisa de `pip install openpyxl` uma vez). Ele lê o CSV e gera `inventario.xlsx` formatado, que abre sozinho — com cabeçalho fixo e filtro. O CSV é a verdade que a máquina escreve; o Excel é a foto que você abre. Por isso nunca há conflito de "arquivo aberto": você pode deixar o `.xlsx` aberto à vontade que o robô não mexe nele.

---

## Proteger o cofre — o mais importante

O `_cofre/cofre.json` é o que torna a base reversível. Se ele vaza, a proteção toda cai junto. Então:

- mantenha o cofre **fora** de qualquer pasta que você compartilhe ou suba para nuvem aberta;
- o RATIO lê `01_pseudonimizado/`, **nunca** o `_cofre/`;
- faça backup do cofre à parte, e de preferência criptografado.

É a única peça que você guarda com mais zelo do que o próprio acervo.

> **Atenção a `00_originais/`.** Os PDFs originais arquivados ali ainda têm o dado bruto (é a fonte). Trate-os com o mesmo cuidado do cofre: fora de pasta compartilhada, backup à parte. Se sua política for não guardar original, dá para apagar essa pasta depois de cada rodada — é uma linha no script, me avise.
