# ATRIO API 0.7.0

Plano de controle local da execução ATRIO. A API não interpreta direito e não
gera texto por conta própria. Ela transporta comandos, códigos, versões e
referências de artefato, e registra cada transição de estado.

Origem do código: `packages/services/atrio_api`.

O método ATRIO é anterior ao backend. Ele já foi aplicado em ambiente real de
trabalho jurídico por meio de plataformas online de IA generativa, sob
supervisão humana direta, análise individual dos resultados, definição de
padrões e refinamento iterativo. A API formaliza esse método em infraestrutura
local, persistente e verificável.

## O que a API é

Uma aplicação FastAPI que expõe 23 rotas sob `/v1`, servidas apenas em
`127.0.0.1`. Ela coordena quatro módulos em sequência:

```
CORPUS  →  RATIO/TROIA  →  CERNE  →  LUX
```

Todo avanço passa por uma máquina de estados persistida em PostgreSQL
(`ExecutionStage`, 20 estados). Controle otimista de versão em cada mutação.
Idempotência por tenant. Nenhum conteúdo jurídico trafega nos eventos de
auditoria: só hashes, códigos, identificadores e versões.

A release é definida pelo servidor. O cliente não escolhe versões de CORPUS,
RATIO, CERNE ou LUX; ele recebe o envelope `release` em cada resposta.

## Evidências

Distinção que vale para todo este kit:

- **Validado operacionalmente**: o método ATRIO foi aplicado e refinado em
  fluxo jurídico real antes da implementação backend. As métricas disponíveis
  descrevem essa operação e não são convertidas aqui em estimativas causais da
  API atual.
- **Verificado em engenharia**: a suíte atual registra 175 testes
  automatizados aprovados, incluindo as rotas finais de integridade e
  liberação. O pacote de evidência anterior, ligado ao commit `dfd509e`,
  registra os 169 testes que existiam naquele ponto.
- **Avaliação experimental formal da API**: o protocolo está em fechamento.
  Execução e resultados serão incorporados ao kit somente com as respectivas
  evidências. Ver `../apresentacao/AVALIACAO.md`.

Condições de instalação e homologação estão concentradas em
[OPERACAO.md](OPERACAO.md).

## Primeira chamada funcionando

Com PostgreSQL local ativo, banco `atrio` criado e migrations aplicadas:

```bash
python packages/services/atrio_api/tools/run_api.py
```

O script pede a senha do PostgreSQL e a frase do cofre pelo terminal, sem eco.
Em outro terminal:

```bash
curl http://127.0.0.1:8080/v1/health/live
```

Resposta:

```json
{"status": "live", "atrio_api_version": "0.7.0"}
```

`/v1/health/live` não toca banco, cofre nem modelo. Serve para confirmar que o
processo subiu. Para confirmar que as dependências estão íntegras, use
`/v1/health/ready`, descrito em [ENDPOINTS.md](ENDPOINTS.md).

## Onde está cada coisa

| Documento | Conteúdo |
|---|---|
| [ENDPOINTS.md](ENDPOINTS.md) | As 23 rotas, corpos, códigos de erro, `curl` real |
| [CONFIGURACAO.md](CONFIGURACAO.md) | Variáveis de ambiente e contrato de inferência |
| [MODULOS.md](MODULOS.md) | CORPUS, RATIO/TROIA, CERNE, LUX: entrada, saída, juízo humano |
| [OPERACAO.md](OPERACAO.md) | Subir, migrar, diagnosticar falha |
| [openapi.json](openapi.json) | Schema OpenAPI 3.1.0 exportado da aplicação |

## Composição da release

Valores de `src/atrio_api/release_catalog.py`, devolvidos em cada resposta:

| Componente | Versão |
|---|---|
| `atrio_api_version` | 0.7.0 |
| `corpus_version` | 1.5.0 |
| `ratio_version` | 7.0.0 |
| `cerne_module_version` | 1.2.0 |
| `cerne_service_build` | 0.2.0 |
| `lux_version` | 6.0.0 |
| `atrio_pii_version` | 1.0.0 |
| `schema_version` | 1.0.0 |
| `prompt_bundle_hash` | `7ca7a772ec09…` (digest do bundle normativo) |

`release_id` é derivado: `atrio-local-0.7.0-<manifesto[:8]>-<bundle[:8]>`.

Schema do banco: `1.3.0`, cinco migrations, cada uma verificada por SHA-256.

## Requisitos

- Python `>=3.11`. O Dockerfile fixa `python:3.13.5-slim-bookworm`.
- PostgreSQL. O Compose fixa `postgres:18.4-alpine3.24`.
- Ollama, opcional. Sem `ATRIO_OLLAMA_MODEL` definido, as rotas de RATIO
  `execute`, CERNE e LUX respondem `503`.
- `poppler-utils` e `tesseract-ocr` para o pipeline documental do CORPUS.
