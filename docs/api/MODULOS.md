# Módulos

Quatro módulos em sequência fixa. A API não pula etapa, não permite entrar no
meio da cadeia e não deixa o cliente escolher versões.

```
CORPUS 1.5.0  →  RATIO 7.0.0 / TROIA 1.0.0  →  CERNE 1.2.0  →  LUX 6.0.0
```

Cada handoff é um artefato cifrado, com produtor, versão do produtor,
`release_id`, `schema_version` e SHA-256. `ReleaseEnvelope.assert_artifact`
recusa artefato cujo produtor, versão, release ou schema divirjam da release
fixada na criação da execução.

---

## CORPUS 1.5.0

Ingestão documental, cofre e inventário.

**Entrada.** Corpo binário bruto em
`POST /v1/executions/{id}/corpus/documents`. Limite de 50 MiB. Tipo declarado
em `Content-Type`; `text/plain` só em UTF-8. A assinatura do arquivo é
verificada contra o tipo declarado.

**O que faz.**

1. Cifra o documento em AES-256-GCM no cofre local, envelope `ATRIO-V1`,
   versão de entrada `1.0.0`. O caminho físico nunca sai pela API.
2. Extrai texto por um de cinco métodos: `text_utf8`, `docx_xml`, `pdf_text`,
   `ocr_pdf` ou `ocr_image`. OCR usa Tesseract, com Poppler para rasterizar
   páginas de PDF.
3. Detecta PII com `atrio_pii 1.0.0`, a mesma biblioteca usada pelo LUX.
4. Pseudonimiza de forma reversível, com mapa cifrado por execução
   (`ATRIO-PSEUDONYM-MAP-1`).
5. Classifica a peça por texto (`RI`, `ED`, `MS`, `AGRAVO`, `SENTENCA`,
   `OUTRO`) e detecta nível de sigilo.
6. Grava o inventário: método, contagem de páginas, caracteres extraídos,
   confiança média do OCR, CNJ, classe, sigilo, contagem de PII por tipo,
   contagem de pseudônimos e SHA-256 do texto pseudonimizado.

**Saída.** Inventário por documento, sem texto e sem nome de arquivo.

**Artefato produzido.** Handoff CORPUS cifrado, produtor `corpus`, versão
`1.5.0`, criado em `POST /corpus/finalize`. É a única entrada admissível do
RATIO.

**Onde o juízo humano é obrigatório.** O processamento para no primeiro
documento que dispara revisão. A execução entra em `CORPUS_REVIEW_REQUIRED` e
não avança sem decisão registrada em
`POST /corpus/documents/{document_id}/review`, com `APPROVE` ou `EXCLUDE`.

Três gatilhos, avaliados nesta ordem em `_review_type`:

| `review_type` | Condição |
|---|---|
| `secrecy` | Nível de sigilo detectado no texto |
| `ocr` | Extração feita por `ocr_pdf` ou `ocr_image` |
| `quality` | Texto extraído abaixo do mínimo de caracteres |

Sigilo tem precedência sobre OCR, e OCR sobre qualidade. A constante
`OCR_REVIEW_CONFIDENCE = 80.0` governa o limiar de confiança do OCR.

`POST /corpus/finalize` recusa com `409 CORPUS_PROCESSING_INCOMPLETE` enquanto
houver documento pendente ou em revisão aberta. Não existe caminho que produza
o handoff CORPUS sem que toda revisão disparada tenha decisão humana.

---

## RATIO 7.0.0 e TROIA 1.0.0

Protocolo decisório governado, com três módulos e fases nomeadas.

**Entrada.** Artefato de handoff do CORPUS. `POST /ratio/start` recusa com
`409 RATIO_ARTIFACT_REQUIRED` se ele não existir.

**Fases por módulo.**

| Módulo | Fases |
|---|---|
| RI | `RI_01` Admissibilidade, `RI_02` Relatório Técnico, `RI_03` TROIA (Matriz Contrafactual e Risco Decisório), `RI_04` Parecer Estratégico, `RI_05` Minuta/Voto, `RI_06` Validação e Refinamento |
| ED | `ED_01` Admissibilidade, `ED_02` Relatório Técnico, `ED_03` Parecer Estratégico, `ED_04` Minuta/Voto, `ED_05` Validação e Refinamento |
| MS | `MS_01` Cabimento e Admissibilidade, `MS_02` Mapa do Ato Coator, `MS_03` Decisão Liminar, `MS_04` Processamento Pós-Liminar, `MS_05` Parecer de Mérito, `MS_06` Sentença/Acórdão, `MS_07` Validação e Refinamento |

**TROIA.** Protocolo contrafactual interno, versão `1.0.0`. A posição muda por
módulo:

| Módulo | Modo | Fase | Gatilhos |
|---|---|---|---|
| RI | `AUTONOMOUS_REQUIRED` | `RI_03` | nenhum, é fase própria e obrigatória |
| ED | `EMBEDDED_CONDITIONAL` | `ED_03` | sete gatilhos normativos |
| MS | `NOT_DEFINED` | nenhuma | nenhum |

Gatilhos do ED: `INFRINGING_EFFECT_REQUEST`, `MATERIAL_RESULT_CHANGE`,
`RELEVANT_ADVERSARIAL_ROUTE`, `MERITS_REDISCUSSION_RISK`,
`REASONING_DISPOSITION_CONTRADICTION`, `BREAKING_POINT_IDENTIFIED`,
`FUTURE_VOTE_OMISSION_RISK`.

**O que faz.** `POST /ratio/execute` executa a fase corrente com o modelo local
e grava o artefato da fase. As bases normativas ficam em
`<packages_root>/ratio`, com hashes registrados no manifesto normativo.

**Saída.** Estado do runtime com nove valores possíveis de status por fase:
`NOT_STARTED`, `ANALYZING`, `BLOCKED`, `PENDING_REMEDIATION`, `VALIDATED`,
`VALIDATED_WITH_NONBLOCKING_CAVEAT`, `DISPENSED_BY_EXCEPTION`,
`INVALIDATED_BY_SUBSTANTIAL_CHANGE`, `ENDED_FOR_NOW_AFTER_INJUNCTION`.

**Artefato produzido.** Artefato por fase em `execute`, e o handoff RATIO em
`POST /ratio/finalize`, produtor `ratio`, versão `7.0.0`.

**Onde o juízo humano é obrigatório.** Nenhuma fase avança sozinha. O avanço
só acontece por `POST /ratio/actions`, com `actor_id` e `expected_revision`.
As oito ações disponíveis são todas de operador:

`VALIDATE`, `VALIDATE_WITH_CAVEAT`, `ADVANCE`, `CONFIGURE_TROIA`,
`VALIDATE_TROIA`, `BLOCK_TROIA`, `RESUME_TROIA`, `RETURN_AFTER_CHANGE`.

O modelo produz o conteúdo da fase. Ele não valida a fase, não configura TROIA
e não decide o avanço. Códigos de bloqueio são verificados contra um catálogo
fechado; código fora do catálogo devolve `422 RATIO_HARD_STOP_INVALID`.

---

## CERNE 1.2.0

Auditoria adversarial do raciocínio produzido pelo RATIO.

**Entrada.** Artefato de handoff do RATIO. `POST /cerne/audit` recusa com
`409 CERNE_ARTIFACT_REQUIRED` se ele não existir.

**O que faz.** Confronta o artefato contra a base normativa em
`<packages_root>/cerne`: prompt mestre, cards de confronto, camada de
antibanalização, checklist de auditoria e onze eixos de exame documentados nos
arquivos `EX001` a `EX011`. A base é verificada por hash no manifesto
normativo, e `readiness_check` confirma sua legibilidade antes de a API se
declarar pronta.

**Saída.** Um gate, um output de cliente estruturado e uma lista de avisos.

Gates possíveis:

| Gate | Efeito no estágio |
|---|---|
| `AVANCA` | Segue para o LUX |
| `AVANCA_COM_AJUSTE` | Segue com ressalva registrada |
| `REVISAO_HUMANA` | Para em `CERNE_HUMAN_REVIEW` |
| `BLOQUEIO_PARCIAL` | Para em `CERNE_PARTIAL_BLOCK` |
| `BLOQUEIO_TOTAL` | Para em `CERNE_TOTAL_BLOCK` |

Output de cliente: `estado_documento`, `sintese_objetiva`,
`ponto_principal_atencao`, `impacto_pratico`, `ajustes_necessarios`,
`pode_ser_preservado`, `recomendacao_final`.

**Artefato produzido.** Artefato CERNE, produtor `cerne`, versão de módulo
`1.2.0`, build de serviço `0.2.0`.

**Onde o juízo humano é obrigatório.** Três dos cinco gates param a execução e
não têm saída automática. Sair de `CERNE_HUMAN_REVIEW`,
`CERNE_PARTIAL_BLOCK` ou `CERNE_TOTAL_BLOCK` exige uma de duas rotas, ambas
com `decision_code` obrigatório e ator identificado:

- `POST /cerne/return-to-ratio`, que devolve a execução para retrabalho;
- `POST /cerne/reopen-total-block`, que reabre um bloqueio total.

`decision_code` é um código do catálogo, não texto livre. A decisão fica na
trilha de eventos com ator, sequência e carimbo de tempo.

---

## LUX 6.0.0

Acabamento textual e anonimização irreversível da saída.

**Entrada.** Artefato CERNE. `POST /lux/refine` recusa com
`409 LUX_ARTIFACT_REQUIRED` se ele não existir.

**O que faz.** Aplica o kernel e as bases de estilo em `<packages_root>/lux`,
e a política de privacidade usando `atrio_pii 1.0.0` a partir de
`<packages_root>/atrio_pii/atrio_pii.py`. A mesma biblioteca que detectou PII
na entrada governa a supressão na saída.

Parâmetros:

| Parâmetro | Valores | Default |
|---|---|---|
| `mode` | `PADRAO`, `CLAREZA`, `ESTILO` | `PADRAO` |
| `data_mode` | `PUBLICO`, `PSEUDONIMIZADO`, `CORPUS` | resolvido pelo serviço |
| `profile` | `CHRISTIAN`, `ISABELLA`, `LUARA` | nenhum |

**Saída.** Artefato LUX mais dois sinalizadores de auditoria:
`privacy_applied` e `suppression_reinforced`.

**Artefato produzido.** Artefato LUX, produtor `lux`, versão `6.0.0`.

**Onde o juízo humano é obrigatório.** O LUX é chamado por um operador, com
`actor_id` e `expected_version` explícitos. A escolha de `data_mode` decide o
que pode aparecer no texto final e é do operador. Violação de política devolve
`422 LUX_PRIVACY_REJECTED`, e saída fora do contrato devolve
`502 LUX_OUTPUT_REJECTED`. Em ambos os casos, nada é gravado.

---

## Máquina de estados

Vinte estágios em `ExecutionStage`:

`CREATED`, `CORPUS_INGESTING`, `CORPUS_REVIEW_REQUIRED`, `CORPUS_READY`,
`RATIO_RUNNING`, `RATIO_WAITING_OPERATOR`, `RATIO_READY`, `RATIO_REWORK`,
`CERNE_AUDITING`, `CERNE_APPROVED`, `CERNE_HUMAN_REVIEW`,
`CERNE_PARTIAL_BLOCK`, `CERNE_TOTAL_BLOCK`, `LUX_REFINING`,
`FINAL_INTEGRITY_CHECK`, `FINAL_INTEGRITY_BLOCK`, `READY_FOR_RELEASE`,
`RELEASED`, `TECHNICAL_FAILURE`, `CANCELLED`.

Seis status: `ACTIVE`, `WAITING_HUMAN`, `BLOCKED`, `COMPLETED`, `FAILED`,
`CANCELLED`. Estágios terminais: `RELEASED` e `CANCELLED`.

Falha técnica é retomável: `FAIL_TECHNICAL` grava `last_error_code` e
`retry_stage`; `RETRY_TECHNICAL` devolve a execução ao estágio guardado.

---

## Lacunas conhecidas

Itens que não estão no código e por isso não são documentados como
funcionalidade.

1. **Sem autenticação e sem autorização.** Não existe verificação de
   credencial, token, papel ou tenant no nível da rota. `actor_id` e
   `tenant_id` são campos declarados pelo cliente, sem verificação. A proteção
   é o vínculo de rede: `127.0.0.1` no modo local, e `127.0.0.1:<porta>` no
   mapeamento do Compose.

2. **Sem limite de taxa e sem paginação.** `GET /events` e
   `GET /corpus/documents` devolvem a coleção inteira.

3. **CERNE não expõe o output interno.** O contrato de resposta traz apenas
   `CerneClientOutputResponse`. A trilha interna dos onze eixos, descrita nas
   bases normativas, não tem rota de leitura.
