# Endpoints

Extraído de `src/atrio_api/api.py` e `src/atrio_api/api_models.py`. O schema
formal está em [openapi.json](openapi.json), exportado da própria aplicação
(OpenAPI 3.1.0, 23 caminhos).

Base assumida nos exemplos: `http://127.0.0.1:8080`.

---

## Convenções gerais

### Formato de erro

Todo erro tratado devolve o mesmo envelope:

```json
{"error": {"code": "STATE_VERSION_CONFLICT", "expected": 3, "actual": 5}}
```

`code` é sempre presente. As demais chaves variam por handler.

### Validação de corpo

Todos os modelos usam `extra="forbid"`. Campo desconhecido é recusado com
`422 REQUEST_VALIDATION_FAILED`. A resposta de validação devolve localização,
mensagem e tipo do erro, sem ecoar o valor enviado.

### Identificadores

- `Identifier`: 1 a 200 caracteres, padrão `^[A-Za-z0-9_][A-Za-z0-9_.:@/-]*$`.
  Usado em `tenant_id`, `actor_id`, `artifact_id`, `release_id`.
- `Code`: 1 a 128 caracteres, padrão `^[A-Za-z0-9_][A-Za-z0-9_.:-]*$`.
  Usado em `decision_code`, `classification`, `profile`, `blocking_code`.
- `Version`: 1 a 80 caracteres, padrão `^[A-Za-z0-9][A-Za-z0-9_.+-]*$`.
- `{execution_id}` e `{document_id}` são UUID no caminho.

### Header `Idempotency-Key`

Obrigatório em `POST /v1/executions`, `corpus/documents`, `ratio/start`,
`ratio/actions`, `ratio/execute`, `ratio/finalize`, `cerne/audit` e
`lux/refine`. Mesmo padrão de `Identifier`, 1 a 200 caracteres.

Rotas de criação devolvem `201` quando criam e `200` quando reconhecem a mesma
chave com o mesmo conteúdo. Mesma chave com conteúdo diferente devolve
`409 IDEMPOTENCY_CONFLICT`.

### Controle de versão

`expected_version` refere-se ao `state_version` da execução. `expected_revision`
refere-se ao `revision` do runtime RATIO. São contadores distintos.
Divergência devolve `409` com `expected` e `actual`.

### Tabela de erros

| HTTP | `code` | Origem |
|---|---|---|
| 404 | `EXECUTION_NOT_FOUND` | execução inexistente |
| 404 | `CORPUS_REVIEW_NOT_FOUND` | documento sem revisão pendente |
| 404 | `RATIO_RUNTIME_NOT_FOUND` | runtime RATIO não iniciado |
| 409 | `IDEMPOTENCY_CONFLICT` | mesma chave, conteúdo diferente |
| 409 | `STATE_VERSION_CONFLICT` | `expected_version` divergente |
| 409 | `RATIO_REVISION_CONFLICT` | `expected_revision` divergente |
| 409 | `INVALID_TRANSITION` | comando inválido para o estágio |
| 409 | `CORPUS_INTAKE_CONFLICT` | reenvio conflitante do documento |
| 409 | `CORPUS_NO_DOCUMENTS` | nenhum documento na execução |
| 409 | `CORPUS_PROCESSING_INCOMPLETE` | há documento pendente ou em revisão |
| 409 | `RATIO_RUNTIME_ALREADY_STARTED` | `ratio/start` repetido |
| 409 | `RATIO_TRANSITION_REJECTED` | ação inválida para a fase |
| 409 | `RATIO_ARTIFACT_REQUIRED` | artefato de entrada ausente |
| 409 | `CERNE_ARTIFACT_REQUIRED` | artefato RATIO ausente |
| 409 | `LUX_ARTIFACT_REQUIRED` | artefato CERNE ausente |
| 413 | `DOCUMENT_TOO_LARGE` | acima de 50 MiB |
| 415 | `UNSUPPORTED_DOCUMENT_TYPE` | media type fora da lista |
| 422 | `REQUEST_VALIDATION_FAILED` | corpo, header ou caminho inválido |
| 422 | `INVALID_COMMAND_PAYLOAD` | comando fora da rota governada |
| 422 | `INVALID_DOCUMENT_SIGNATURE` | assinatura do arquivo não confere |
| 422 | `CORPUS_EXTRACTION_FAILED` | extração ou OCR falhou |
| 422 | `RATIO_HARD_STOP_INVALID` | código de bloqueio fora do catálogo |
| 422 | `RATIO_ACTION_PAYLOAD_INVALID` | campos incompatíveis com a ação |
| 422 | `CERNE_DOMAIN_REJECTED` | saída recusada pelo domínio CERNE |
| 422 | `LUX_REQUEST_REJECTED` | modo, perfil ou data mode inválido |
| 422 | `LUX_PRIVACY_REJECTED` | política de privacidade violada |
| 500 | `VAULT_INTEGRITY_ERROR` | cofre corrompido ou frase incorreta |
| 500 | `CORPUS_INTEGRITY_MISMATCH` | hash do processamento divergente |
| 500 | `RATIO_PERSISTENCE_INTEGRITY_ERROR` | estado RATIO inconsistente |
| 500 | `RATIO_EXECUTOR_INTEGRITY_ERROR` | artefato de fase inconsistente |
| 500 | `CERNE_INTEGRITY_ERROR` | artefato CERNE inconsistente |
| 500 | `CERNE_KNOWLEDGE_ERROR` | base normativa CERNE ilegível |
| 500 | `LUX_INTEGRITY_ERROR` | artefato LUX inconsistente |
| 500 | `INTERNAL_ERROR` | exceção não prevista |
| 502 | `RATIO_GENERATED_OUTPUT_INVALID` | saída do modelo fora do contrato |
| 502 | `CERNE_PROVIDER_ERROR` | falha do provedor de inferência |
| 502 | `LUX_OUTPUT_REJECTED` | saída LUX fora do contrato |
| 502 | `LUX_PROVIDER_ERROR` | falha do provedor de inferência |
| 503 | `PERSISTENCE_UNAVAILABLE` | PostgreSQL indisponível |
| 503 | `CORPUS_INTAKE_UNAVAILABLE` | serviço de entrada não montado |
| 503 | `CORPUS_WORKFLOW_UNAVAILABLE` | workflow CORPUS não montado |
| 503 | `CORPUS_TOOL_UNAVAILABLE` | Poppler ou Tesseract ausente |
| 503 | `RATIO_WORKFLOW_UNAVAILABLE` | workflow RATIO não montado |
| 503 | `RATIO_EXECUTION_UNAVAILABLE` | executor RATIO sem modelo |
| 503 | `CERNE_WORKFLOW_UNAVAILABLE` | workflow CERNE não montado |
| 503 | `CERNE_EXECUTION_UNAVAILABLE` | execução CERNE sem modelo |
| 503 | `LUX_WORKFLOW_UNAVAILABLE` | workflow LUX não montado |
| 503 | `LUX_EXECUTION_UNAVAILABLE` | execução LUX sem modelo |

Os `503` de workflow ocorrem quando a dependência não foi montada na
inicialização. Sem `ATRIO_OLLAMA_MODEL` definido, CERNE, LUX e
`ratio/execute` respondem `503` de forma determinística.

---

## Saúde

### `GET /v1/health/live`

Não toca banco, cofre nem modelo.

```bash
curl http://127.0.0.1:8080/v1/health/live
```

```json
{"status": "live", "atrio_api_version": "0.7.0"}
```

### `GET /v1/health/ready`

Executa `readiness_check`: verifica schema do banco, integridade do cofre,
presença das ferramentas do CORPUS e, se houver modelo configurado, a saúde do
Ollama, a identidade do modelo e as bases normativas de CERNE e LUX.

```bash
curl http://127.0.0.1:8080/v1/health/ready
```

```json
{
  "status": "ready",
  "atrio_api_version": "0.7.0",
  "database_schema_version": "1.3.0",
  "release_id": "atrio-local-0.7.0-f9f81d9d-7ca7a772",
  "corpus_intake_version": "1.0.0",
  "corpus_pipeline_version": "1.5.0",
  "vault_envelope_version": "ATRIO-V1"
}
```

Falha na verificação propaga a exceção da dependência. Banco indisponível
resulta em `503 PERSISTENCE_UNAVAILABLE`.

---

## Execução

### `POST /v1/executions`

Cria a execução e fixa a release. `201` na criação, `200` na repetição
idempotente.

Headers: `Idempotency-Key` (obrigatório).

Corpo:

| Campo | Tipo | Obrigatório |
|---|---|---|
| `tenant_id` | `Identifier` | sim |
| `actor_id` | `Identifier` | sim |
| `ratio_module` | `RI` \| `ED` \| `MS` | sim |
| `destination` | `interno` \| `externo` \| `publico` | sim |

```bash
curl -X POST http://127.0.0.1:8080/v1/executions \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: caso-2026-0001" \
  -d '{"tenant_id":"gabinete_01","actor_id":"operador_01","ratio_module":"RI","destination":"interno"}'
```

```json
{
  "created": true,
  "execution": {
    "execution_id": "0f2a…",
    "tenant_id": "gabinete_01",
    "created_by": "operador_01",
    "ratio_module": "RI",
    "destination": "interno",
    "release": {
      "release_id": "atrio-local-0.7.0-f9f81d9d-7ca7a772",
      "atrio_api_version": "0.7.0",
      "corpus_version": "1.5.0",
      "ratio_version": "7.0.0",
      "cerne_module_version": "1.2.0",
      "cerne_service_build": "0.2.0",
      "lux_version": "6.0.0",
      "atrio_pii_version": "1.0.0",
      "prompt_bundle_hash": "7ca7a772ec0912dc75bef351dad958631cd3a3ceeed36efaebedc08366c2342f",
      "schema_version": "1.0.0"
    },
    "stage": "CREATED",
    "status": "ACTIVE",
    "state_version": 0,
    "corpus_artifact": null,
    "ratio_artifact": null,
    "cerne_artifact": null,
    "lux_artifact": null,
    "released_artifact": null,
    "current_ratio_phase": null,
    "waiting_reason": null,
    "last_operator_actor": null,
    "last_operator_decision": null,
    "cerne_gate": null,
    "last_error_code": null,
    "retry_stage": null
  }
}
```

Erros: `409 IDEMPOTENCY_CONFLICT`, `422 REQUEST_VALIDATION_FAILED`,
`503 PERSISTENCE_UNAVAILABLE`.

### `GET /v1/executions/{execution_id}`

Devolve o `ExecutionResponse` acima.

```bash
curl http://127.0.0.1:8080/v1/executions/0f2a…
```

Erros: `404 EXECUTION_NOT_FOUND`, `422 REQUEST_VALIDATION_FAILED` (UUID
inválido), `503 PERSISTENCE_UNAVAILABLE`.

### `GET /v1/executions/{execution_id}/events`

Trilha de transições em ordem de sequência. Não contém conteúdo jurídico.

```bash
curl http://127.0.0.1:8080/v1/executions/0f2a…/events
```

```json
[
  {
    "execution_id": "0f2a…",
    "sequence": 1,
    "command": "START_INGESTION",
    "from_stage": "CREATED",
    "to_stage": "CORPUS_INGESTING",
    "component": "atrio_api",
    "component_version": "0.7.0",
    "release_id": "atrio-local-0.7.0-f9f81d9d-7ca7a772",
    "actor_id": "operador_01",
    "occurred_at": "2026-07-30T12:00:00+00:00",
    "metadata": {}
  }
]
```

### `POST /v1/executions/{execution_id}/commands`

Rota genérica de comando. A maior parte dos comandos está bloqueada aqui e
exige a rota governada do módulo correspondente.

Corpo:

| Campo | Tipo | Obrigatório |
|---|---|---|
| `kind` | `CommandKind` | sim |
| `expected_version` | inteiro `>= 0` | sim |
| `actor_id` | `Identifier` | sim |
| `payload` | objeto | não, default `{}` |

Campos aceitos em `payload`: `artifact`, `decision_code`, `error_code`, `gate`,
`phase`, `reason_code`, `review_type`. Todos opcionais.

**Comandos aceitos por esta rota:** `START_INGESTION`, `FAIL_TECHNICAL`,
`RETRY_TECHNICAL`, `CANCEL`.

**Comandos recusados com `422 INVALID_COMMAND_PAYLOAD`,** com a rota governada
correspondente:

| Comandos | Rota governada |
|---|---|
| `REGISTER_CORPUS_DOCUMENT`, `REQUEST_CORPUS_REVIEW`, `RESUME_CORPUS`, `COMPLETE_CORPUS` | `/corpus/*` |
| `START_RATIO`, `REQUEST_OPERATOR_DECISION`, `RECORD_OPERATOR_DECISION`, `COMPLETE_RATIO`, `COMPLETE_RATIO_REWORK` | `/ratio/*` |
| `START_CERNE`, `APPLY_CERNE_GATE`, `RETURN_TO_RATIO`, `REOPEN_TOTAL_BLOCK` | `/cerne/*` |
| `START_LUX`, `COMPLETE_LUX` | `/lux/*` |
| `PASS_FINAL_INTEGRITY`, `FAIL_FINAL_INTEGRITY`, `RETRY_LUX` | `/final-integrity/*` |
| `RELEASE` | `/release` |

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/commands \
  -H "Content-Type: application/json" \
  -d '{"kind":"START_INGESTION","expected_version":0,"actor_id":"operador_01"}'
```

Devolve `ExecutionResponse`. Erros: `404 EXECUTION_NOT_FOUND`,
`409 STATE_VERSION_CONFLICT`, `409 INVALID_TRANSITION`,
`422 INVALID_COMMAND_PAYLOAD`, `422 REQUEST_VALIDATION_FAILED`.

---

## CORPUS

### `POST /v1/executions/{execution_id}/corpus/documents`

Envio do documento. O corpo é o **binário bruto**, não multipart e não JSON.
`201` na criação, `200` na repetição idempotente.

Headers obrigatórios:

| Header | Regra |
|---|---|
| `Idempotency-Key` | `Identifier`, 1 a 200 |
| `X-ATRIO-Expected-Version` | inteiro `>= 0` |
| `X-ATRIO-Actor` | `Identifier`, 1 a 200 |
| `Content-Type` | media type do arquivo |
| `Content-Length` | opcional, inteiro `>= 0` |

`Content-Type: text/plain` só é aceito com `charset` ausente, `utf-8` ou
`utf8`. Qualquer outro charset resulta em `415 UNSUPPORTED_DOCUMENT_TYPE`.

Limite: 50 MiB (`MAX_DOCUMENT_BYTES`). Se `Content-Length` declarar mais que
isso, a API recusa antes de ler o corpo.

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/corpus/documents \
  -H "Idempotency-Key: doc-001" \
  -H "X-ATRIO-Expected-Version: 1" \
  -H "X-ATRIO-Actor: operador_01" \
  -H "Content-Type: application/pdf" \
  --data-binary @peticao.pdf
```

```json
{
  "created": true,
  "document": {
    "document_id": "3c9b…",
    "execution_id": "0f2a…",
    "sha256": "9a4f…",
    "byte_length": 184320,
    "media_type": "application/pdf",
    "encryption_algorithm": "AES-256-GCM",
    "envelope_version": "ATRIO-V1",
    "intake_version": "1.0.0"
  },
  "execution": { "…": "ExecutionResponse" }
}
```

O caminho físico do cofre não é devolvido.

Erros: `409 CORPUS_INTAKE_CONFLICT`, `409 STATE_VERSION_CONFLICT`,
`413 DOCUMENT_TOO_LARGE`, `415 UNSUPPORTED_DOCUMENT_TYPE`,
`422 INVALID_DOCUMENT_SIGNATURE`, `500 VAULT_INTEGRITY_ERROR`,
`503 CORPUS_INTAKE_UNAVAILABLE`.

### `GET /v1/executions/{execution_id}/corpus/documents`

Lista os documentos com status e inventário.

```bash
curl http://127.0.0.1:8080/v1/executions/0f2a…/corpus/documents
```

```json
[
  {
    "document_id": "3c9b…",
    "execution_id": "0f2a…",
    "input_sha256": "9a4f…",
    "byte_length": 184320,
    "media_type": "application/pdf",
    "intake_version": "1.0.0",
    "processing_id": "7d21…",
    "effective_status": "REVIEW_REQUIRED",
    "review_decision": null,
    "inventory": {
      "document_id": "3c9b…",
      "execution_id": "0f2a…",
      "input_sha256": "9a4f…",
      "byte_length": 184320,
      "media_type": "application/pdf",
      "extraction_method": "ocr_pdf",
      "page_count": 12,
      "extracted_char_count": 18422,
      "ocr_mean_confidence": 71.4,
      "cnj": null,
      "procedural_class": "…",
      "secrecy_level": "none",
      "pii_counts": {"CPF": 2, "NOME": 7},
      "pseudonym_count": 9,
      "pseudonymized_sha256": "b18c…",
      "status": "REVIEW_REQUIRED",
      "review_type": "ocr",
      "corpus_pipeline_version": "1.5.0",
      "atrio_pii_version": "1.0.0"
    }
  }
]
```

O inventário não contém texto do documento nem nome de arquivo.

Erros: `404 EXECUTION_NOT_FOUND`, `503 CORPUS_WORKFLOW_UNAVAILABLE`.

### `POST /v1/executions/{execution_id}/corpus/process`

Processa os documentos pendentes: extração, OCR quando necessário, detecção de
PII, pseudonimização e inventário. Para no primeiro documento que exige revisão
humana.

Corpo:

| Campo | Tipo | Obrigatório |
|---|---|---|
| `expected_version` | inteiro `>= 0` | sim |
| `actor_id` | `Identifier` | sim |

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/corpus/process \
  -H "Content-Type: application/json" \
  -d '{"expected_version":2,"actor_id":"operador_01"}'
```

```json
{
  "execution": { "…": "ExecutionResponse" },
  "documents": [ "…CorpusDocumentStatusResponse" ],
  "processed_count": 3,
  "halted_for_review": true
}
```

`halted_for_review: true` significa que o estágio virou
`CORPUS_REVIEW_REQUIRED` e a execução aguarda decisão humana.

Erros: `409 CORPUS_NO_DOCUMENTS`, `409 STATE_VERSION_CONFLICT`,
`422 CORPUS_EXTRACTION_FAILED`, `500 CORPUS_INTEGRITY_MISMATCH`,
`503 CORPUS_TOOL_UNAVAILABLE`, `503 CORPUS_WORKFLOW_UNAVAILABLE`.

### `POST /v1/executions/{execution_id}/corpus/documents/{document_id}/review`

Registra a decisão humana sobre um documento que parou em revisão.

Corpo:

| Campo | Tipo | Obrigatório |
|---|---|---|
| `expected_version` | inteiro `>= 0` | sim |
| `actor_id` | `Identifier` | sim |
| `decision` | `APPROVE` \| `EXCLUDE` | sim |

```bash
curl -X POST "http://127.0.0.1:8080/v1/executions/0f2a…/corpus/documents/3c9b…/review" \
  -H "Content-Type: application/json" \
  -d '{"expected_version":3,"actor_id":"revisor_01","decision":"APPROVE"}'
```

```json
{
  "execution": { "…": "ExecutionResponse" },
  "document": { "…": "CorpusDocumentStatusResponse" }
}
```

Erros: `404 CORPUS_REVIEW_NOT_FOUND`, `409 STATE_VERSION_CONFLICT`,
`503 CORPUS_WORKFLOW_UNAVAILABLE`.

### `POST /v1/executions/{execution_id}/corpus/finalize`

Fecha o CORPUS e produz o artefato de handoff cifrado.

Corpo: igual a `corpus/process`.

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/corpus/finalize \
  -H "Content-Type: application/json" \
  -d '{"expected_version":4,"actor_id":"operador_01"}'
```

```json
{
  "execution": { "…": "ExecutionResponse" },
  "artifact": {
    "artifact_id": "corpus-0f2a…",
    "sha256": "c07e…",
    "media_type": "application/json",
    "classification": "…",
    "producer": "corpus",
    "producer_version": "1.5.0",
    "release_id": "atrio-local-0.7.0-f9f81d9d-7ca7a772",
    "schema_version": "1.0.0"
  },
  "document_count": 3
}
```

Erros: `409 CORPUS_NO_DOCUMENTS`, `409 CORPUS_PROCESSING_INCOMPLETE`,
`409 STATE_VERSION_CONFLICT`, `503 CORPUS_WORKFLOW_UNAVAILABLE`.

---

## RATIO e TROIA

### `POST /v1/executions/{execution_id}/ratio/start`

Inicia o runtime RATIO na primeira fase do módulo escolhido na criação da
execução. `201` na criação, `200` na repetição idempotente.

Headers: `Idempotency-Key`.

Corpo:

| Campo | Tipo | Obrigatório |
|---|---|---|
| `expected_version` | inteiro `>= 0` | sim |
| `actor_id` | `Identifier` | sim |

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/ratio/start \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: ratio-start-0f2a" \
  -d '{"expected_version":5,"actor_id":"operador_01"}'
```

```json
{
  "created": true,
  "execution": { "…": "ExecutionResponse" },
  "ratio": {
    "module": "RI",
    "current_phase": "RI_01",
    "current_phase_title": "Admissibilidade",
    "revision": 0,
    "last_operator_action": null,
    "phases": [
      {"phase": "RI_01", "title": "Admissibilidade", "status": "ANALYZING"},
      {"phase": "RI_02", "title": "Relatório Técnico", "status": "NOT_STARTED"},
      {"phase": "RI_03", "title": "TROIA — Matriz Contrafactual e Risco Decisório", "status": "NOT_STARTED"},
      {"phase": "RI_04", "title": "Parecer Estratégico", "status": "NOT_STARTED"},
      {"phase": "RI_05", "title": "Minuta/Voto", "status": "NOT_STARTED"},
      {"phase": "RI_06", "title": "Validação e Refinamento", "status": "NOT_STARTED"}
    ],
    "troia": {
      "mode": "AUTONOMOUS_REQUIRED",
      "phase": "RI_03",
      "status": "NOT_STARTED",
      "triggers": [],
      "blocking_code": null
    }
  }
}
```

Erros: `409 RATIO_RUNTIME_ALREADY_STARTED`, `409 STATE_VERSION_CONFLICT`,
`409 RATIO_ARTIFACT_REQUIRED`, `503 RATIO_WORKFLOW_UNAVAILABLE`.

### `GET /v1/executions/{execution_id}/ratio`

Devolve o `RatioStateResponse` acima.

```bash
curl http://127.0.0.1:8080/v1/executions/0f2a…/ratio
```

Erros: `404 RATIO_RUNTIME_NOT_FOUND`, `503 RATIO_WORKFLOW_UNAVAILABLE`.

### `POST /v1/executions/{execution_id}/ratio/actions`

Ação de operador sobre a fase corrente. É o ponto de decisão humana do RATIO.

Headers: `Idempotency-Key`.

Corpo:

| Campo | Tipo | Obrigatório |
|---|---|---|
| `action` | `RatioActionKind` | sim |
| `expected_revision` | inteiro `>= 0` | sim |
| `actor_id` | `Identifier` | sim |
| `troia_triggers` | lista de `TroiaTrigger` | não, default `[]` |
| `blocking_code` | `Code` | não |
| `target_phase` | `RatioPhase` | não |

Valores de `action`: `VALIDATE`, `VALIDATE_WITH_CAVEAT`, `ADVANCE`,
`CONFIGURE_TROIA`, `VALIDATE_TROIA`, `BLOCK_TROIA`, `RESUME_TROIA`,
`RETURN_AFTER_CHANGE`.

Valores de `troia_triggers` (aplicáveis ao módulo ED):
`INFRINGING_EFFECT_REQUEST`, `MATERIAL_RESULT_CHANGE`,
`RELEVANT_ADVERSARIAL_ROUTE`, `MERITS_REDISCUSSION_RISK`,
`REASONING_DISPOSITION_CONTRADICTION`, `BREAKING_POINT_IDENTIFIED`,
`FUTURE_VOTE_OMISSION_RISK`.

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/ratio/actions \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: ratio-act-001" \
  -d '{"action":"VALIDATE","expected_revision":1,"actor_id":"operador_01"}'
```

Devolve `RatioMutationResponse` (mesmo formato de `ratio/start`).

Erros: `409 RATIO_REVISION_CONFLICT`, `409 RATIO_TRANSITION_REJECTED`,
`422 RATIO_ACTION_PAYLOAD_INVALID`, `422 RATIO_HARD_STOP_INVALID`,
`500 RATIO_PERSISTENCE_INTEGRITY_ERROR`, `503 RATIO_WORKFLOW_UNAVAILABLE`.

### `POST /v1/executions/{execution_id}/ratio/execute`

Executa a fase corrente com o modelo local e produz o artefato da fase.
Exige `ATRIO_OLLAMA_MODEL` configurado.

Headers: `Idempotency-Key`.

Corpo:

| Campo | Tipo | Obrigatório |
|---|---|---|
| `expected_revision` | inteiro `>= 0` | sim |
| `actor_id` | `Identifier` | sim |

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/ratio/execute \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: ratio-exec-RI01" \
  -d '{"expected_revision":1,"actor_id":"operador_01"}'
```

```json
{
  "created": true,
  "execution": { "…": "ExecutionResponse" },
  "ratio": { "…": "RatioStateResponse" },
  "artifact": { "…": "ArtifactResponse" },
  "artifact_roles": ["phase_output"]
}
```

Erros: `409 RATIO_ARTIFACT_REQUIRED`, `409 RATIO_REVISION_CONFLICT`,
`500 RATIO_EXECUTOR_INTEGRITY_ERROR`, `502 RATIO_GENERATED_OUTPUT_INVALID`,
`503 RATIO_EXECUTION_UNAVAILABLE`.

### `POST /v1/executions/{execution_id}/ratio/finalize`

Fecha o RATIO e produz o handoff para o CERNE.

Headers: `Idempotency-Key`.

Corpo:

| Campo | Tipo | Obrigatório |
|---|---|---|
| `expected_revision` | inteiro `>= 0` | sim |
| `expected_version` | inteiro `>= 0` | sim |
| `actor_id` | `Identifier` | sim |

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/ratio/finalize \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: ratio-final-0f2a" \
  -d '{"expected_revision":9,"expected_version":12,"actor_id":"operador_01"}'
```

```json
{
  "created": true,
  "execution": { "…": "ExecutionResponse" },
  "ratio": { "…": "RatioStateResponse" },
  "artifact": { "…": "ArtifactResponse" }
}
```

Erros: `409 RATIO_REVISION_CONFLICT`, `409 STATE_VERSION_CONFLICT`,
`409 RATIO_TRANSITION_REJECTED`, `503 RATIO_WORKFLOW_UNAVAILABLE`.

---

## CERNE

### `POST /v1/executions/{execution_id}/cerne/audit`

Auditoria adversarial do artefato RATIO. Produz o gate e o output de cliente.
Rota assíncrona. `201` na criação, `200` na repetição idempotente.

Headers: `Idempotency-Key`.

Corpo:

| Campo | Tipo | Obrigatório |
|---|---|---|
| `expected_version` | inteiro `>= 0` | sim |
| `actor_id` | `Identifier` | sim |

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/cerne/audit \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: cerne-audit-0f2a" \
  -d '{"expected_version":13,"actor_id":"operador_01"}'
```

```json
{
  "created": true,
  "execution": { "…": "ExecutionResponse" },
  "artifact": { "…": "ArtifactResponse" },
  "gate": "REVISAO_HUMANA",
  "client_output": {
    "estado_documento": "…",
    "sintese_objetiva": "…",
    "ponto_principal_atencao": "…",
    "impacto_pratico": "…",
    "ajustes_necessarios": ["…"],
    "pode_ser_preservado": ["…"],
    "recomendacao_final": "…"
  },
  "warnings": []
}
```

Valores de `gate`: `AVANCA`, `AVANCA_COM_AJUSTE`, `REVISAO_HUMANA`,
`BLOQUEIO_PARCIAL`, `BLOQUEIO_TOTAL`.

Erros: `409 CERNE_ARTIFACT_REQUIRED`, `409 STATE_VERSION_CONFLICT`,
`422 CERNE_DOMAIN_REJECTED`, `500 CERNE_INTEGRITY_ERROR`,
`500 CERNE_KNOWLEDGE_ERROR`, `502 CERNE_PROVIDER_ERROR`,
`503 CERNE_EXECUTION_UNAVAILABLE`, `503 CERNE_WORKFLOW_UNAVAILABLE`.

### `POST /v1/executions/{execution_id}/cerne/return-to-ratio`

Devolve a execução ao RATIO para retrabalho. Decisão humana.

Corpo:

| Campo | Tipo | Obrigatório |
|---|---|---|
| `expected_version` | inteiro `>= 0` | sim |
| `actor_id` | `Identifier` | sim |
| `decision_code` | `Code` | sim |

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/cerne/return-to-ratio \
  -H "Content-Type: application/json" \
  -d '{"expected_version":14,"actor_id":"revisor_01","decision_code":"AJUSTE_FUNDAMENTACAO"}'
```

Devolve `ExecutionResponse`.

Erros: `409 STATE_VERSION_CONFLICT`, `409 INVALID_TRANSITION`,
`503 CERNE_WORKFLOW_UNAVAILABLE`.

### `POST /v1/executions/{execution_id}/cerne/reopen-total-block`

Reabre uma execução em `CERNE_TOTAL_BLOCK`. Decisão humana. Mesmo corpo e
mesmos erros de `return-to-ratio`.

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/cerne/reopen-total-block \
  -H "Content-Type: application/json" \
  -d '{"expected_version":14,"actor_id":"revisor_01","decision_code":"REABERTURA_AUTORIZADA"}'
```

---

## LUX

### `POST /v1/executions/{execution_id}/lux/refine`

Acabamento textual e anonimização de saída. `201` na criação, `200` na
repetição idempotente.

Headers: `Idempotency-Key`.

Corpo:

| Campo | Tipo | Obrigatório | Default |
|---|---|---|---|
| `expected_version` | inteiro `>= 0` | sim | |
| `actor_id` | `Identifier` | sim | |
| `mode` | `PADRAO` \| `CLAREZA` \| `ESTILO` | não | `PADRAO` |
| `profile` | `Code` | não | `null` |
| `data_mode` | `PUBLICO` \| `PSEUDONIMIZADO` \| `CORPUS` | não | `null` |

Perfis reconhecidos em `lux/execution.py`: `CHRISTIAN`, `ISABELLA`, `LUARA`.

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/lux/refine \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: lux-refine-0f2a" \
  -d '{"expected_version":15,"actor_id":"operador_01","mode":"PADRAO"}'
```

```json
{
  "created": true,
  "execution": { "…": "ExecutionResponse" },
  "artifact": { "…": "ArtifactResponse" },
  "mode": "PADRAO",
  "data_mode": "PSEUDONIMIZADO",
  "profile": null,
  "privacy_applied": true,
  "suppression_reinforced": false
}
```

Erros: `409 LUX_ARTIFACT_REQUIRED`, `409 STATE_VERSION_CONFLICT`,
`422 LUX_REQUEST_REJECTED`, `422 LUX_PRIVACY_REJECTED`,
`500 LUX_INTEGRITY_ERROR`, `502 LUX_OUTPUT_REJECTED`,
`502 LUX_PROVIDER_ERROR`, `503 LUX_EXECUTION_UNAVAILABLE`,
`503 LUX_WORKFLOW_UNAVAILABLE`.

---

## Integridade final e liberação

As quatro rotas abaixo fecham o fluxo depois do LUX. Todas devolvem
`ExecutionResponse`, exigem `expected_version` e registram `actor_id` na trilha
de eventos.

### `POST /v1/executions/{execution_id}/final-integrity/pass`

Aprova a conferência final e move a execução de `FINAL_INTEGRITY_CHECK` para
`READY_FOR_RELEASE`.

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/final-integrity/pass \
  -H "Content-Type: application/json" \
  -d '{"expected_version":16,"actor_id":"revisor_final"}'
```

Erros: `404 EXECUTION_NOT_FOUND`, `409 STATE_VERSION_CONFLICT`,
`409 INVALID_TRANSITION`, `422 REQUEST_VALIDATION_FAILED`.

### `POST /v1/executions/{execution_id}/final-integrity/fail`

Bloqueia a liberação e registra um código de motivo.

| Campo | Tipo | Obrigatório |
|---|---|---|
| `expected_version` | inteiro `>= 0` | sim |
| `actor_id` | `Identifier` | sim |
| `reason_code` | `Code` | sim |

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/final-integrity/fail \
  -H "Content-Type: application/json" \
  -d '{"expected_version":16,"actor_id":"revisor_final","reason_code":"DIVERGENCIA_DE_INTEGRIDADE"}'
```

O novo estágio é `FINAL_INTEGRITY_BLOCK`, e `waiting_reason` recebe o código
informado.

### `POST /v1/executions/{execution_id}/final-integrity/retry-lux`

Registra a decisão humana de devolver uma execução bloqueada ao LUX. O
artefato anterior é retirado da execução antes da nova tentativa.

| Campo | Tipo | Obrigatório |
|---|---|---|
| `expected_version` | inteiro `>= 0` | sim |
| `actor_id` | `Identifier` | sim |
| `decision_code` | `Code` | sim |

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/final-integrity/retry-lux \
  -H "Content-Type: application/json" \
  -d '{"expected_version":17,"actor_id":"revisor_final","decision_code":"RETORNAR_AO_LUX"}'
```

O novo estágio é `LUX_REFINING`.

### `POST /v1/executions/{execution_id}/release`

Libera uma execução em `READY_FOR_RELEASE`. O artefato LUX conferido é fixado
como `released_artifact`, e o estágio terminal passa a `RELEASED`.

```bash
curl -X POST http://127.0.0.1:8080/v1/executions/0f2a…/release \
  -H "Content-Type: application/json" \
  -d '{"expected_version":17,"actor_id":"operador_release"}'
```

O status resultante é `COMPLETED`. Erros: `404 EXECUTION_NOT_FOUND`,
`409 STATE_VERSION_CONFLICT`, `409 INVALID_TRANSITION`,
`422 REQUEST_VALIDATION_FAILED`.

---

## Interface e documentação

| Caminho | Observação |
|---|---|
| `GET /` | Console operacional em HTML. Só existe se `ui_path` foi informado. Fora do schema OpenAPI. Headers `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Permissions-Policy: camera=(), microphone=(), geolocation=()` |
| `GET /docs` | Swagger UI |
| `GET /openapi.json` | Schema servido pela aplicação |

`redoc_url` está desabilitado.
