# Configuração

Fonte: `src/atrio_api/container_runtime.py`, `src/atrio_api/adapters/ollama.py`,
`infra/atrio_api/Dockerfile`, `infra/atrio_api/docker-entrypoint.sh`,
`infra/compose.yaml` e `infra/.env.example`, todos sob
``.

Só entram nesta lista variáveis que o runtime de fato lê.

---

## Variáveis lidas pelo runtime de container

`ContainerSettings.from_environment()` lê exatamente estas. Nenhuma outra
variável influencia a montagem da aplicação.

| Variável | Default | Obrigatória | Efeito |
|---|---|---|---|
| `ATRIO_REPOSITORY_ROOT` | `/app` | não | Raiz usada para derivar `ATRIO_PACKAGES_ROOT` e `ATRIO_UI_PATH` quando essas não são informadas |
| `ATRIO_DB_HOST` | `atrio_db` | não | Host PostgreSQL. Recusa valor vazio ou com espaço nas bordas |
| `ATRIO_DB_PORT` | `5432` | não | Porta PostgreSQL. Precisa ser inteiro entre 1 e 65535 |
| `ATRIO_DB_NAME` | `atrio` | não | Nome do banco. Precisa casar `[a-z_][a-z0-9_]{0,62}` |
| `ATRIO_DB_USER` | `atrio_app` | não | Usuário do banco. Mesmo padrão de identificador |
| `ATRIO_DB_PASSWORD_FILE` | `/run/secrets/atrio_db_password` | não | Caminho do arquivo com a senha. O arquivo precisa existir, não estar vazio e não conter `\0`, `\n` ou `\r` |
| `ATRIO_VAULT_ROOT` | `/data/vault` | não | Raiz do cofre documental. O scratch fica em `<vault_root>/scratch` |
| `ATRIO_VAULT_PASSPHRASE_FILE` | `/run/secrets/atrio_vault_passphrase` | não | Caminho do arquivo com a frase do cofre. Mesmas regras de formato da senha |
| `ATRIO_PACKAGES_ROOT` | `<repository_root>/packages` | não | Raiz das bases normativas de RATIO, CERNE, LUX e `atrio_pii` |
| `ATRIO_UI_PATH` | `<repository_root>/ATRIO-Core-Orchestrator.html` | não | Arquivo HTML servido em `GET /`. Se não existir, a aplicação falha ao subir com `FileNotFoundError` |
| `ATRIO_OLLAMA_MODEL` | vazio | não | **Chave de ativação.** Vazio desliga RATIO `execute`, CERNE e LUX |
| `ATRIO_OLLAMA_URL` | `http://atrio_ollama:11434` | não | URL base do Ollama. Sem caminho, sem query, sem credencial embutida |
| `ATRIO_OLLAMA_NUM_CTX` | `40960` | não | Janela de contexto congelada. Inteiro `>= 1` |
| `ATRIO_OLLAMA_NUM_PREDICT` | `4096` | não | Teto de geração congelado. Inteiro `>= 1` e menor que `num_ctx` |

Nenhuma senha é lida de variável de ambiente. A senha do PostgreSQL e a frase
do cofre só entram por arquivo, e o valor é apagado da memória do processo logo
após a construção do repositório e do cofre.

### O que `ATRIO_OLLAMA_MODEL` vazio produz

Sem modelo configurado, o runtime não instancia o adapter, o executor RATIO, o
workflow CERNE nem o workflow LUX. As rotas continuam registradas e respondem
de forma determinística:

- `POST /ratio/execute` devolve `503 RATIO_EXECUTION_UNAVAILABLE`;
- `POST /cerne/audit` devolve `503 CERNE_WORKFLOW_UNAVAILABLE`;
- `POST /lux/refine` devolve `503 LUX_WORKFLOW_UNAVAILABLE`.

CORPUS e as rotas de estado do RATIO seguem funcionando.

---

## Variáveis declaradas mas não consumidas pelo runtime

| Variável | Onde aparece | Situação |
|---|---|---|
| `ATRIO_API_HOST` | `ENV` no Dockerfile, `environment` no Compose | O `CMD` do Dockerfile fixa `--host 0.0.0.0` na linha de comando do uvicorn. O valor da variável não é lido por nenhum código Python |
| `ATRIO_API_PORT` | `ENV` no Dockerfile, `environment` no Compose | O `CMD` fixa `--port 8080`. A porta externa é escolhida no mapeamento do Compose |

Manter as duas declaradas é inofensivo. Alterá-las não muda o comportamento do
processo dentro do container.

---

## Variáveis lidas pelo entrypoint

`docker-entrypoint.sh` roda antes do uvicorn e exige, sob `set -euo pipefail`:

`ATRIO_DB_HOST`, `ATRIO_DB_PORT`, `ATRIO_DB_NAME`, `ATRIO_DB_USER`,
`ATRIO_DB_PASSWORD_FILE`.

Ausência de qualquer uma interrompe o start. O arquivo de senha precisa ser
legível. O script aguarda o `pg_isready`, exporta `PGPASSWORD` a partir do
arquivo, aplica todas as migrations em ordem passando o SHA-256 de cada uma
como `-v migration_checksum`, e só então executa o `CMD`.

---

## Variáveis do arquivo `.env` do Compose

`infra/.env.example` contém somente configuração não sigilosa.

| Variável | Valor de exemplo | Efeito |
|---|---|---|
| `ATRIO_INFRA_VERSION` | `1.0.0` | Rótulo `org.atrio.infra.version` |
| `ATRIO_API_VERSION` | `0.7.0` | Tag da imagem e `ARG` do build. O Dockerfile aborta se `atrio_api.__version__` divergir |
| `POSTGRES_IMAGE` | `postgres:18.4-alpine3.24` | Imagem do banco |
| `OLLAMA_IMAGE` | `ollama/ollama:0.32.4` | Imagem do Ollama |
| `ATRIO_API_PORT` | `8080` | Porta publicada em `127.0.0.1` |
| `OLLAMA_PORT` | `11434` | Porta publicada em `127.0.0.1` |
| `OLLAMA_MODEL` | `qwen3:8b` | Vira `ATRIO_OLLAMA_MODEL` |
| `OLLAMA_NUM_CTX` | `40960` | Vira `ATRIO_OLLAMA_NUM_CTX` e `OLLAMA_CONTEXT_LENGTH` |
| `OLLAMA_NUM_PREDICT` | `4096` | Vira `ATRIO_OLLAMA_NUM_PREDICT` |

As quatro últimas usam a sintaxe `${VAR:?mensagem}` no Compose: ausência
aborta o `compose config` com mensagem em português.

Senhas não ficam no `.env`. O Compose monta dois arquivos como secrets:

```
infra/secrets/atrio_db_password.txt        → /run/secrets/atrio_db_password
infra/secrets/atrio_vault_passphrase.txt   → /run/secrets/atrio_vault_passphrase
```

`infra/secrets/*.txt` é ignorado pelo Git. Preencha com valores reais fora do
repositório; qualquer exemplo neste kit usa `COLOQUE_SUA_SENHA_AQUI` como
marcador.

---

## Reconciliação entre Compose e runtime

Registro explícito: as variáveis Ollama de `infra/compose.yaml` e as variáveis
lidas por `container_runtime.py` estão reconciliadas. Uma única fonte no `.env`
alimenta os dois lados.

| Fonte `.env` | Serviço `atrio_api` | Serviço `ollama` | Leitura no código |
|---|---|---|---|
| `OLLAMA_MODEL` | `ATRIO_OLLAMA_MODEL` | (não usa) | `os.environ["ATRIO_OLLAMA_MODEL"]` |
| `OLLAMA_NUM_CTX` | `ATRIO_OLLAMA_NUM_CTX` | `OLLAMA_CONTEXT_LENGTH` | `_positive_int(...)`, vira `num_ctx` |
| `OLLAMA_NUM_PREDICT` | `ATRIO_OLLAMA_NUM_PREDICT` | (não usa) | `_positive_int(...)`, vira `num_predict` |

O mesmo número que a API usa como orçamento de contexto é o número que o
servidor Ollama aloca. Não há dois valores concorrentes.

Uma diferença nominal permanece e não é defeito: `container_runtime.py` tem
`http://atrio_ollama:11434` como default de `ATRIO_OLLAMA_URL`, enquanto o
Compose injeta `http://ollama:11434`. O serviço se chama `ollama` e o container
se chama `atrio_ollama`. O valor injetado pelo Compose prevalece.

---

## Contrato de inferência

Implementado em `src/atrio_api/adapters/ollama.py`, versão `0.2.0`. Vale para
toda chamada de RATIO `execute`, CERNE e LUX.

### Opções congeladas

Defaults do adapter: `temperature: 0.0`, `seed: 0`, `num_ctx: 40960`,
`num_predict: 4096`. O runtime de container sobrescreve `num_ctx` e
`num_predict` com os valores do ambiente.

Lista fechada de opções aceitas: `temperature`, `seed`, `num_ctx`,
`num_predict`, `top_k`, `top_p`, `min_p`, `repeat_last_n`, `repeat_penalty`,
`stop`. Qualquer outra chave é recusada com `ValueError` nomeando as opções
inválidas.

Duas invariantes verificadas antes de qualquer chamada: `num_ctx` e
`num_predict` precisam ser inteiros positivos, e `num_predict` precisa ser
estritamente menor que `num_ctx`.

### Preflight conservador

Antes de abrir a conexão HTTP, o adapter calcula um teto superior de tokens do
prompt somando o comprimento em bytes UTF-8 de prompt, instrução de sistema e
schema de saída serializado. Reserva 256 tokens de overhead de template. Se

```
teto_do_prompt + num_predict + 256 > num_ctx
```

a chamada é recusada localmente, sem tráfego de rede.

Bytes UTF-8 são um teto superior grosseiro para tokens. O preflight pode
recusar um prompt que caberia no tokenizer real. Ele não aceita silenciosamente
um prompt que poderia ser truncado. Adotar um tokenizer exato exige emenda
explícita do instrumento de avaliação.

### Telemetria obrigatória

A resposta do Ollama precisa trazer `prompt_eval_count` e `eval_count`. Ausência
de qualquer um resulta em `OllamaProtocolError`. Não há caminho de sucesso sem
telemetria de tokens.

Verificações pós-resposta, todas bloqueantes:

- `num_ctx - prompt_eval_count - num_predict` precisa ser `>= 0`;
- `eval_count` não pode exceder `num_predict`;
- `done_reason == "length"` é recusado como resultado truncado;
- o modelo respondente precisa coincidir com o modelo validado, aceitando a
  forma sem o sufixo `:latest`.

### Proveniência registrada

Cada inferência produz `InferenceMetadata` com: versão do adapter, nome e
digest do modelo, SHA-256 de prompt, resposta e opções, contagem de caracteres
de entrada e saída, durações em nanossegundos, `prompt_eval_count`,
`eval_count`, o teto conservador calculado, a folga de contexto e o número de
tentativas.

O texto confidencial fica em `InferenceResult.content`, separado dos metadados.
A resposta HTTP bruta do Ollama não integra nenhum contrato público.

### Rede

Timeout de conexão 5 s, de leitura 300 s. Até duas tentativas adicionais com
recuo exponencial (0,25 s, 0,5 s) para timeouts, erros de rede e os status 408,
429, 500, 502, 503 e 504. `follow_redirects=False` e `trust_env=False`: o
cliente ignora proxies do ambiente.

### Verificação via `/api/ps`

O adapter usa `/api/tags` para healthcheck e identidade do modelo. Ele não
consulta `/api/ps`.

`/api/ps` é usado pelo runner de avaliação
`tools/evaluation/run_atrio_smoke_arm.py`, que carrega o modelo com um prompt
sem dados e confirma que o contexto efetivamente alocado é pelo menos o valor
congelado. Se o modelo não aparecer carregado após o preflight, o runner
aborta. Essa verificação pertence ao instrumento de avaliação, não ao caminho
de produção da API.

---

## Variáveis do harness de avaliação

Lidas por `tools/evaluation/run_atrio_smoke_arm.py`, configuradas em
`evaluation/harness_config.json`, braço A8. Não afetam a API.

| Variável | Efeito |
|---|---|
| `ATRIO_EVAL_API_URL` | Endereço da API sob teste |
| `ATRIO_EVAL_OLLAMA_URL` | Endereço do Ollama |
| `ATRIO_EVAL_MODEL` | Modelo pinado |
| `ATRIO_EVAL_MODEL_DIGEST` | Digest exigido do modelo |
| `ATRIO_EVAL_CANDIDATE_COMMIT` | Commit do produto candidato |
| `ATRIO_EVAL_NUM_CTX` | Contexto congelado do experimento |
| `ATRIO_EVAL_NUM_PREDICT` | Teto de geração do experimento |
| `ATRIO_EVAL_VAULT_ROOT` | Raiz do cofre do produto |
| `ATRIO_EVAL_VAULT_PASSPHRASE_FILE` | Caminho do arquivo com a frase do cofre |

No arquivo versionado, `ATRIO_EVAL_VAULT_PASSPHRASE_FILE` tem o valor sentinela
`REQUIRED_CORPUS_VAULT_SECRET_PATH`. Substitua apenas em configuração
operacional fora do Git.

O gate em `execution.gate.enabled` está `false`. Nenhum comando `run` é
autorizado enquanto isso não mudar.

---

## Local, sem container

`tools/run_api.py` não lê variáveis de ambiente. Toda configuração vem de
argumentos de linha de comando, e os segredos são pedidos pelo terminal com
`getpass`, sem eco e sem gravação em disco.

| Argumento | Default |
|---|---|
| `--api-port` | `8080` |
| `--database-host` | `127.0.0.1` |
| `--database-port` | `5432` |
| `--database-name` | `atrio` |
| `--database-user` | `atrio_app` |
| `--ollama-url` | `http://127.0.0.1:11434` |
| `--ollama-model` | nenhum, desliga RATIO `execute`, CERNE e LUX |
| `--vault-root` | `<serviço>/var/vault` |
| `--ui-path` | `<repositório>/ATRIO-Core-Orchestrator.html` |

Na primeira inicialização do cofre, o script pede a frase duas vezes e compara.
A frase não é gravada e será exigida em toda reinicialização e em toda
restauração de backup.

O uvicorn é iniciado com `host="127.0.0.1"`, `access_log=False`,
`server_header=False` e `date_header=False`.
