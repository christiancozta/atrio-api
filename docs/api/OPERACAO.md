# Operação

Caminhos relativos à raiz do monorepo ``, salvo indicação
em contrário.

---

## Aviso: dois diretórios `infra/` no repositório

O repositório contém duas árvores de infraestrutura. Elas não são equivalentes.

| Caminho | Situação |
|---|---|
| `infra/` | **Autoritativa.** Compose com secrets por arquivo, Dockerfile com verificação de digest do bundle normativo, entrypoint que aplica migrations, `RUNTIME_NORMATIVE_MANIFEST.json` |
| `infra/` na raiz do repositório | **Divergente.** Contradiz o runtime em vários pontos. Detalhes na seção final |

Use sempre a primeira. A segunda não deve ser executada sem revisão.

---

## Subir com Docker

Toda esta seção é **declarada, não verificada**. A imagem nunca foi construída,
porque Docker não está disponível na máquina de desenvolvimento. Os comandos
vêm do Compose, do Dockerfile e do README de infraestrutura. Nenhum deles foi
executado.

### 1. Configuração

```powershell
Copy-Item .\infra\.env.example .\infra\.env
```

Ajuste `ATRIO_API_PORT` e `OLLAMA_PORT` se já houver serviço nativo ocupando
8080 ou 11434.

### 2. Segredos

```powershell
& .\infra\Initialize-Secrets.ps1
```

O script cria `infra/secrets/atrio_db_password.txt` e
`infra/secrets/atrio_vault_passphrase.txt`. O diretório é ignorado pelo Git.
Se preencher à mão, use valores fortes e reais; nos exemplos deste kit o
marcador é `COLOQUE_SUA_SENHA_AQUI`.

A frase do cofre não é recuperável. Perdê-la torna o cofre e os backups
ilegíveis. Guarde uma cópia offline.

### 3. Validar antes de subir

```powershell
docker compose --env-file .\infra\.env -f .\infra\compose.yaml config
```

Variáveis obrigatórias ausentes abortam aqui, com mensagem em português.

### 4. Subir

```powershell
docker compose --env-file .\infra\.env -f .\infra\compose.yaml up --build -d
```

O que acontece, conforme declarado:

1. `atrio_db` sobe e fica saudável (`pg_isready`).
2. O build da API instala o pacote e aborta se `atrio_api.__version__` divergir
   de `ATRIO_API_VERSION`.
3. Ainda no build, `build_runtime_normative_manifest.py --check` recalcula o
   manifesto dos 52 artefatos normativos e compara `content_digest` com
   `NORMATIVE_BUNDLE_SHA256` de `release_catalog.py`. Divergência aborta o
   build.
4. O entrypoint aguarda o PostgreSQL, aplica as cinco migrations em ordem com
   `ON_ERROR_STOP=1` e passa o SHA-256 de cada uma.
5. O uvicorn sobe com a factory `atrio_api.container_runtime:create_container_app`.

O container roda com `read_only: true`, `cap_drop: ALL`,
`no-new-privileges:true`, usuário não root `atrio` (UID 10001) e `/tmp` em
tmpfs de 256 MB.

### 5. Modelo

O modelo não é baixado automaticamente. Depois que o Ollama ficar saudável:

```powershell
docker compose --env-file .\infra\.env -f .\infra\compose.yaml exec ollama ollama pull qwen3:8b
```

### 6. Verificar

```powershell
Invoke-RestMethod http://127.0.0.1:8080/v1/health/ready | ConvertTo-Json
```

Esperado: `atrio_api_version` `0.7.0`, `database_schema_version` `1.3.0` e
`release_id` começando por `atrio-local-0.7.0-`.

---

## Subir local, sem container

Requer Python `>= 3.11`, PostgreSQL local, e Poppler e Tesseract no `PATH` para
o pipeline documental.

### 1. Ambiente

```powershell
& .\packages\services\atrio_api\.venv\Scripts\python.exe -m pip install -e .\packages\services\atrio_api
```

### 2. Banco

Crie o banco `atrio` e o usuário `atrio_app` no PostgreSQL local.

### 3. Migrations

```powershell
& .\packages\services\atrio_api\tools\apply_migrations.ps1
```

O runner calcula o SHA-256 de cada migração e pede a senha diretamente ao
`psql`. O projeto não armazena a senha.

### 4. Subir

```powershell
& .\packages\services\atrio_api\.venv\Scripts\python.exe .\packages\services\atrio_api\tools\run_api.py
```

Sem `--ollama-model`, RATIO `execute`, CERNE e LUX respondem `503`. Para
habilitar:

```powershell
& .\packages\services\atrio_api\.venv\Scripts\python.exe .\packages\services\atrio_api\tools\run_api.py --ollama-model qwen3:8b
```

O script pede a senha do PostgreSQL e a frase do cofre pelo terminal, sem eco.
Na primeira inicialização do cofre, pede a frase duas vezes e compara.

Console operacional em `http://127.0.0.1:8080/`. Documentação em
`http://127.0.0.1:8080/docs`.

---

## Banco e schema 1.3.0

Cinco migrations em `packages/services/atrio_api/migrations/`, cada uma com
versão e SHA-256 fixados em `src/atrio_api/database.py`.

| Arquivo | Versão | SHA-256 |
|---|---|---|
| `0001_initial.sql` | 1.0.0 | `3d615cf2fa7896d97eaf55de6369425bd39448d65448d9e0a91050f5273bcc52` |
| `0002_corpus_intake.sql` | 1.1.0 | `285d7d6b867afd9819fb03b5bfe19c0d6ea3564e064d5c6431fa1ac03de4ceac` |
| `0003_corpus_event_metadata.sql` | 1.1.1 | `451adede47251d01d4a77f77a36c7db31730f80a27a003f2664d92f48621b857` |
| `0004_corpus_processing.sql` | 1.2.0 | `f2c8b6c91e0e463bff54804766111ac2296803081a21e1d70bbb518ec29bc00a` |
| `0005_ratio_runtime.sql` | 1.3.0 | `52a1f0e449f0d2c59b74f2dc22c6728e63d8f4368c7bd46ff81143d37f88a9f6` |

O que cada camada acrescenta:

- **1.0.0**: releases, execuções, chaves de idempotência, artefatos, comandos,
  eventos.
- **1.1.0**: registros imutáveis da entrada documental.
- **1.1.1**: restringe a trilha segura a `document_id` e `document_sha256`.
- **1.2.0**: resultados de processamento, decisões de revisão, referências de
  handoff.
- **1.3.0**: execução persistida do RATIO.

`repository.verify_schema()` roda na inicialização e a cada
`GET /v1/health/ready`. Divergência entre a versão gravada no banco e a versão
esperada pelo código impede a API de se declarar pronta.

O adaptador PostgreSQL grava estado, comando e evento em transação única, com
bloqueio por execução e controle otimista de versão. Nos logs entram apenas
hashes, códigos e referências de artefato.

---

## Backup

Ferramentas em `packages/services/atrio_api/tools/`: `backup_atrio.py`,
`restore_atrio.py`, `verify_backup.py`. O backup une dump PostgreSQL e cofre
sob manifesto HMAC-SHA-256. Não há rotação destrutiva, e a restauração preserva
o banco e o cofre anteriores. Detalhes em `docs/BACKUP_RESTORE_1_0.md`.

Backup autenticado deve preceder qualquer remoção de volume.

---

## Testes

A evidência limpa foi produzida com pytest, não com unittest:

```bash
python -m pytest -q packages/services/atrio_api/tests --junitxml=junit.xml
```

Resultado registrado em `evaluation/evidence/dfd509e/`: 169 testes, 0 falhas,
0 erros, 0 pulados, código de retorno 0, Python 3.13.14, Windows 11.

Após a inclusão das rotas finais de integridade e liberação, a suíte local
passou a registrar 175 testes aprovados. O pacote `dfd509e` permanece como
evidência histórica do estado anterior.

O `README.md` do pacote instrui `pytest`.
Os testes são escritos em `unittest` e rodam pelos dois runners, mas o pytest é
o comando canônico porque produz o JUnit exigido pelo manifesto de evidência.

---

## Falhas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| API não sobe, `FileNotFoundError: Interface ATRIO não encontrada` | `ATRIO_UI_PATH` aponta para arquivo inexistente | Corrija o caminho ou remova a variável para usar o default |
| `RuntimeError: Arquivo de senha PostgreSQL indisponível` | Secret não montado ou sem permissão de leitura | Verifique `infra/secrets/` e o mapeamento de secrets no Compose |
| `RuntimeError: Arquivo de frase secreta do cofre contém formato inválido` | O arquivo tem quebra de linha, `\r` ou byte nulo | Regrave sem newline final |
| `ValueError: Identificador de banco inválido` | `ATRIO_DB_NAME` ou `ATRIO_DB_USER` fora de `[a-z_][a-z0-9_]{0,62}` | Use apenas minúsculas, dígitos e sublinhado |
| `503 PERSISTENCE_UNAVAILABLE` em toda rota | PostgreSQL fora do ar ou schema divergente | Confira `pg_isready` e reaplique as migrations |
| `/v1/health/ready` falha, `/v1/health/live` responde | Cofre, ferramentas do CORPUS, Ollama ou bases normativas | O `readiness_check` verifica todos em sequência; o erro identifica qual |
| `503 CORPUS_TOOL_UNAVAILABLE` | Poppler ou Tesseract ausente | Instale `poppler-utils` e `tesseract-ocr` com os pacotes de idioma `por` e `eng` |
| `503 RATIO_EXECUTION_UNAVAILABLE`, `503 CERNE_WORKFLOW_UNAVAILABLE`, `503 LUX_WORKFLOW_UNAVAILABLE` | `ATRIO_OLLAMA_MODEL` vazio | Defina o modelo e confirme que ele está instalado no Ollama |
| `OllamaModelUnavailable: Modelo Ollama não instalado` | Modelo não baixado | Rode o `ollama pull` da seção 5 |
| `ValueError: Prompt excede o orçamento de contexto sob o limite conservador pré-inferência` | O preflight recusou antes de chamar o modelo | Reduza a entrada ou aumente `OLLAMA_NUM_CTX` no `.env` e recrie os containers |
| `OllamaProtocolError: Métrica Ollama obrigatória ausente` | Servidor devolveu resposta sem `prompt_eval_count` ou `eval_count` | Confirme a versão do Ollama; o adapter não aceita resposta sem telemetria |
| `OllamaProtocolError: Ollama atingiu o teto de saída` | `done_reason == "length"` | Aumente `OLLAMA_NUM_PREDICT` ou reduza a entrada. O resultado truncado é descartado |
| `409 STATE_VERSION_CONFLICT` | Outro ator alterou a execução | Releia com `GET /v1/executions/{id}` e reenvie com o `state_version` atual |
| `409 RATIO_REVISION_CONFLICT` | `expected_revision` desatualizado | Releia com `GET /ratio` e reenvie |
| `409 IDEMPOTENCY_CONFLICT` | Mesma `Idempotency-Key` com corpo diferente | Use uma chave nova |
| `409 CORPUS_PROCESSING_INCOMPLETE` no `finalize` | Há documento pendente ou revisão aberta | Rode `corpus/process` e resolva as revisões |
| `422 INVALID_COMMAND_PAYLOAD` | Comando enviado por `POST /commands` em vez da rota governada | Ver a tabela de rotas governadas em ENDPOINTS.md |

### Operações destrutivas

`docker compose down -v` remove os volumes de banco, cofre e modelos. Não use
como comando cotidiano. Faça backup autenticado antes de qualquer remoção.

---

## Divergências do `infra/` da raiz

Registro do que separa a árvore da raiz do runtime real. Nenhum desses pontos
foi corrigido nesta entrega, porque a tarefa não autoriza alterar código.

1. **Credenciais por variável de ambiente.** Usa `ATRIO_DB_PASSWORD` e
   `ATRIO_VAULT_PASSPHRASE`. `container_runtime.py` lê senha e frase somente de
   arquivo, por `ATRIO_DB_PASSWORD_FILE` e `ATRIO_VAULT_PASSPHRASE_FILE`.
   Nenhum código lê as duas variáveis da raiz.

2. **Factory errada.** `CMD` e entrypoint invocam
   `atrio_api.api:create_app --factory`. Essa função exige `service`, `release`
   e `readiness_check` como argumentos e não pode ser chamada sem parâmetros.
   A factory de container é `atrio_api.container_runtime:create_container_app`.

3. **Entrypoint inexistente na imagem.** O `ENTRYPOINT` aponta para
   `/app/tools/docker-entrypoint.sh`, mas o `COPY` que popula `/app/tools/`
   traz `packages/services/atrio_api/tools/`, que não contém esse arquivo. O
   script real fica em `infra/atrio_api/tools/docker-entrypoint.sh` e nunca é
   copiado.

4. **Temporal.** Declara cinco serviços de Temporal. `VERSIONS.yaml` e o README
   da infraestrutura autoritativa registram que Temporal está deliberadamente
   fora desta versão.

5. **Bundle normativo ausente.** Não copia as bases de CERNE e LUX, não copia
   `RUNTIME_NORMATIVE_MANIFEST.json` e não executa a verificação de digest. Um
   container construído por ele falharia no `readiness_check` de CERNE e LUX.

6. **Versões defasadas.** Python 3.11 contra 3.13.5 do Dockerfile
   autoritativo, PostgreSQL 16 contra 18.4, imagens `:latest` contra tags
   fixas, rótulo `version: "0.6.0"` contra a versão real `0.7.0`.

7. **`COPY dist/`.** Copia um diretório gerado, que não é fonte editável.

8. **Senha default gerada em string de compose.**
   `"${ATRIO_DB_PASSWORD:-change_me_$(openssl rand -hex 16)}"` não expande
   substituição de comando em Compose e produziria uma senha literal contendo
   `$(openssl rand -hex 16)`.
