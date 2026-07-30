# ATRIO — MASTER de versionamento

Documento único de referência para versão de componente. A base de código e
infraestrutura foi verificada em 2026-07-30 no commit `e109793`; os kits de
entrega foram incorporados em `a759213`.

O relatório anterior, reconstruído a partir de docstrings, **está
desatualizado**. As correções e os acréscimos estão marcados ao longo deste
arquivo. A seção final registra o que mudou.

---

## 1. Quem manda em quê

Três arquivos declaram versão. Eles não competem: cada um é autoridade sobre um
recorte diferente. Em caso de conflito, vale a ordem abaixo.

| Ordem | Arquivo | Autoridade sobre | Como é mantido |
|---|---|---|---|
| 1 | `VERSIONS.yaml` | Versão canônica de cada componente | À mão, por decisão do autor |
| 2 | `infra/atrio_api/RUNTIME_NORMATIVE_MANIFEST.json` | Hash dos 52 artefatos normativos que entram na imagem | Gerado por `tools/build_runtime_normative_manifest.py`, verificado no build |
| 3 | `MANIFEST.yaml` | Proveniência da fonte canônica (origem de cada artefato) | Gerado por `build/build.py`, build `698248`, 2026-07-26 |

Versão também aparece em código, e esses valores são verificados
automaticamente:

- `packages/services/atrio_api/src/atrio_api/__init__.py` → `0.7.0`. O
  Dockerfile aborta se divergir de `ATRIO_API_VERSION` do `.env`.
- `.../release_catalog.py` → `NORMATIVE_BUNDLE_SHA256`. O build aborta se
  divergir do `content_digest` do manifesto normativo.
- `.../database.py` → `DATABASE_SCHEMA_VERSION` e o SHA-256 de cada migração.
  A API não fica pronta se o banco divergir.

**Este documento não é gerado.** Ele é editado à mão quando uma versão muda, e
o `VERSIONS.yaml` é atualizado junto. Se os dois divergirem, o `VERSIONS.yaml`
vence e este arquivo está errado.

---

## 2. Regra de numeração

Semver estrito, três dígitos.

- **major**: mudança de arquitetura, de contrato ou do modo de operação do
  operador.
- **minor**: função nova compatível.
- **patch**: correção de defeito sem mudança de contrato.

Normalização arquivística e textual não move versão, porque não altera contrato
de componente algum.

O corpus documental fica fora de semver. É citado por snapshot datado, porque
cresce sem que uma linha de protocolo se altere.

---

## 3. Estado atual

Pipeline: **CORPUS → RATIO/TROIA → CERNE → LUX**

### Componentes normativos

| Componente | Versão | Fonte de verdade | Função |
|---|---|---|---|
| CORPUS | **1.5.0** | `VERSIONS.yaml` + `corpus_processing.py` (`CORPUS_PIPELINE_VERSION`) | Ingestão, pseudonimização reversível, cofre, inventário, OCR |
| RATIO | 7.0.0 | `VERSIONS.yaml` + `release_catalog.py` | Protocolo decisório governado, módulos RI, ED e MS |
| TROIA | 1.0.0 | `ratio/contract.py` (`TROIA_PROTOCOL_VERSION`) | Protocolo contrafactual interno do RATIO |
| CERNE (módulo) | 1.2.0 | `VERSIONS.yaml` + `release_catalog.py` | Auditoria adversarial, onze eixos, cinco gates |
| CERNE (serviço) | 0.2.0 | `3.CERNE/api/pyproject.toml` e `__init__.py` | Serviço que atende o contrato `/v1` |
| LUX | 6.0.0 | `VERSIONS.yaml` + `lux/execution.py` (`LUX_PACKAGE_VERSION`) | Acabamento textual e anonimização de saída |
| `atrio_pii` | 1.0.0 | `VERSIONS.yaml` + constante `VERSAO` no módulo | Detecção compartilhada entre CORPUS e LUX |

### Componentes de plataforma (ausentes do relatório anterior)

| Componente | Versão | Fonte de verdade | Função |
|---|---|---|---|
| `atrio_api` | 0.7.0 | `src/atrio_api/__init__.py` e `pyproject.toml` | Plano de controle local da execução integral |
| `ollama_adapter` | 0.2.0 | `adapters/ollama.py` (`OLLAMA_ADAPTER_VERSION`) | Inferência local versionada, determinística |
| `atrio_infra` | 1.0.0 | `infra/.env.example` (`ATRIO_INFRA_VERSION`) | PostgreSQL, API e Ollama em containers locais |
| `atrio_backup` | 1.0.0 | `VERSIONS.yaml` | Backup autenticado e restauração reversível |
| `atrio_db_schema` | 1.3.0 | `database.py` (`DATABASE_SCHEMA_VERSION`) | Persistência transacional e trilha operacional |

### Versões internas de runtime, sem linha própria

Estas identificam contratos internos e não são componentes de produto.

| Constante | Valor | Onde |
|---|---|---|
| `RATIO_RUNTIME_CONTRACT_VERSION` | 0.1.0 | `ratio/contract.py` |
| `RATIO_EXECUTOR_VERSION` | 0.1.0 | `ratio/execution.py` |
| `CERNE_INTEGRATION_VERSION` | 0.1.0 | `cerne/execution.py` |
| `LUX_RUNTIME_VERSION` | 0.1.0 | `lux/execution.py` |
| `INTAKE_VERSION` | 1.0.0 | `corpus_intake.py` |
| `ENVELOPE_VERSION` | ATRIO-V1 | `corpus_intake.py` |
| Mapa de pseudônimos | ATRIO-PSEUDONYM-MAP-1 | `corpus_processing.py` |
| `harness_version` | 0.2.0 | `evaluation/harness_config.json` |
| Protocolo de avaliação | 1.0 | `evaluation/preregistration/protocol.md` |
| Schema do dataset | 1.0.0 | `evaluation/preregistration/dataset_schema.json` |

### Produto

| Item | Valor |
|---|---|
| Candidato experimental | `1.0.0-rc.1` |
| Estado declarado | pré-dados, não congelado externamente |
| `release_id` em execução | `atrio-local-0.7.0-f9f81d9d-7ca7a772` |
| `schema_version` do envelope de release | 1.0.0 |

**Correção ao relatório anterior:** a entrada "ATRIO — sem release próprio" não
descreve mais o estado. Existe candidato experimental declarado em
`VERSIONS.yaml`, e existe `release_id` composto, emitido pela API em toda
resposta. O `release_id` deriva dos digests do manifesto de build e do pacote
normativo: mudar um arquivo normativo muda o identificador.

---

## 4. Histórico por componente

### RATIO — 7.0.0

Protocolo decisório governado. Módulos RI, ED e MS.

| Versão | Data | Mudança |
|---|---|---|
| 1.0.0 | 24/03/2026 | Release inicial. Prompt operacional com regras de ouro, sanção lógica, acervo JSON de nove anos, ED em prompt paralelo |
| 1.1.0 | 24/03/2026 | Julgamento conjunto de recursos, parágrafos iniciais padronizados, dispositivo uniformizado. Contrato de entrada intacto |
| 2.0.0 | 27/03/2026 | Substituição do substrato jurisprudencial. Banco de modelos cede lugar a biblioteca de fundamentos, com aderência material e prioridade temporal |
| 2.0.1 | 27/03/2026 | Formatação das respostas intermediárias. Sem efeito sobre comportamento |
| 3.0.0 | 28/03/2026 | Pacote de dez arquivos nomeados substitui os acervos hospedados. A configuração anterior deixa de operar |
| 3.0.1 | 30/03/2026 | Correção de invenção de jurisprudência |
| 4.0.0 | 09/04/2026 | Unificação RI e ED sob identificação automática do tipo de peça. O operador deixa de escolher o prompt |
| 5.0.0 | 19/04/2026 | Fontes autorizadas reduzidas a três arquivos nomeados. Acervo excluído, consulta a fonte não listada vedada, módulo PACOTE removido |
| 5.0.1 | 20/04/2026 | Renumeração de dez para sete fases. Comportamento declaradamente inalterado |
| 5.1.0 | 20/04/2026 | Fase 4 desdobrada em submódulos 4a a 4e, modo conjunto transversal, recurso adesivo |
| 5.2.0 | 20/04/2026 | Base de templates separada do guia de estilo, com aviso brando e padrão mínimo na ausência |
| 6.0.0 | 05/2026 | Modularização por fase. Core de governança, Estado do Caso como objeto explícito, separação formal entre RATIO e LUX |
| 7.0.0 | 07/2026 | Camada Instructions com precedência sobre o core. Fase 0 eliminada e escolha de módulo como entrada. Arquivo por fase cede a arquivo por módulo. Entrega em três camadas. Acabamento estético-autoral removido das validações. Módulo MS com rito próprio e sete fases. Protocolo de proveniência com hard stop. Máquina de estados com oito estados e invalidação em cascata tipificada |

**Acréscimo:** desde 2026-07-28 (`ebc8e2e`, `f50d43c`, `c0b61dc`) o RATIO 7.0.0
ganhou runtime executável e persistido, sem mudar a versão do protocolo. Esse
runtime é rastreado por linhas próprias: `RATIO_RUNTIME_CONTRACT_VERSION`
0.1.0, `RATIO_EXECUTOR_VERSION` 0.1.0 e `atrio_db_schema` 1.3.0. A separação é
correta: o protocolo não mudou, a implementação nasceu.

### LUX — 6.0.0

Acabamento textual e anonimização irreversível de saída.

| Versão | Data | Mudança |
|---|---|---|
| 1.0.0 | 30/03/2026 | Release inicial. Refinador final com entrega em três blocos, sem fases, sem gatilhos, sem handshake |
| 2.0.0 | 13/04/2026 | Protocolo de sete fases com aprovação obrigatória na Fase 3. Sistema de marcação, classificação `[C]` e `[S]`, hierarquia de regras. Nome consolidado |
| 2.1.0 | 14/04/2026 | Gatilhos de modo `#REV`, `#SIMP`, `#COMP` e `#EST`, com `#COMP` como padrão. Ausência de gatilho preserva o fluxo anterior |
| 3.0.0 | 21/04/2026 | Gatilhos de modo eliminados, substituídos por `#GUIA`. Sete fases reduzidas a seis, estilo promovido a fase própria |
| 3.1.0 | 21/04/2026 | Alertas críticos, verificação de integridade, gravidade em três níveis, resumo final de decisões |
| 4.0.0 | 22/04/2026 | Obrigatoriedade do fluxo revogada. Entrega integral por padrão, perguntas intermediárias opcionais, `#CONSOLIDAR` sobrepondo-se às fases. Arquivado à época como correção de defeito; era a maior ruptura da linha |
| 5.0.0 | 04/05/2026 | Modularização em onze arquivos. Núcleo, três camadas de intervenção graduada, perfil de estilo do usuário, validação silenciosa, instalação própria. O sistema deixa de ser prompt |
| 5.1.0 | 06/05/2026 | Revisão padrão restaurada como automática, entrega em duas camadas, caminhos reduzidos a três |
| 6.0.0 | 07/2026 | Camada 0 de anonimização com três modos de destino, quarenta tipos de identificador, supressão reforçada, público como presumido. Onze arquivos reduzidos a três. Perfil único cede a biblioteca de perfis nomeados por gatilho. Entrega em três blocos com nova convenção. Kernel único para qualquer plataforma. Tokens intocáveis como lista positiva. Interface declarada com o CORPUS e recusa expressa do cofre |

**Acréscimo:** o LUX 6.0.0 tem runtime na API desde 2026-07-28, com
`LUX_RUNTIME_VERSION` 0.1.0. Os três modos de destino aparecem no contrato HTTP
como `data_mode` (`PUBLICO`, `PSEUDONIMIZADO`, `CORPUS`), e os perfis nomeados
como `CHRISTIAN`, `ISABELLA`, `LUARA`.

### CORPUS — 1.5.0

Ingestão, pseudonimização reversível, cofre, inventário e OCR.

Linha reconstruída dos docstrings dos scripts. Não há registro formal, e as
datas de 1.0.0 a 1.4.0 não são recuperáveis com precisão.

| Versão | Data | Mudança |
|---|---|---|
| 1.0.0 | não recuperável | Release inicial. Robô de entrada com pseudonimização por cofre, triagem de segredo de justiça, arquivamento por processo, log de execução |
| 1.1.0 | não recuperável | Inventário em CSV como fonte da verdade. Hash SHA-256 como chave, deduplicação por arquivo e por número CNJ |
| 1.2.0 | não recuperável | OCR como quarto robô, para PDF digitalizado sem camada de texto, reaproveitando motores e cofre existentes |
| 1.3.0 | não recuperável | Painel operacional em linguagem visual ATRIO, somente leitura, sem alterar a orquestra de chamadas |
| 1.4.0 | não recuperável | Inventários separados, documental e de pseudônimos, com consolidado XLSX e alias de compatibilidade |
| **1.5.0** | **26/07/2026** (`917a8dd`) | **Reorganização do monorepo e fechamento do CORPUS como pacote versionado. Homologado contra PostgreSQL vivo em 27/07/2026 (`2bb96e3`)** |

**Correção ao relatório anterior:** o relatório registra 1.4.0 como versão
corrente. O componente está em **1.5.0** desde 2026-07-26, declarado em
`VERSIONS.yaml`, em `MANIFEST.yaml` (nove artefatos marcados `versao: 1.5.0`) e
em código, na constante `CORPUS_PIPELINE_VERSION`. A API devolve
`corpus_pipeline_version: "1.5.0"` em `/v1/health/ready`.

A afirmação "único componente que nunca quebrou contrato" continua válida. A
assinatura estável de linha de comando disciplinou a evolução.

### CERNE — módulo 1.2.0, serviço 0.2.0

Auditoria adversarial do raciocínio. Onze eixos, cinco gates.

| Versão | Data | Mudança |
|---|---|---|
| 1.2.0 | não recuperável | Cliente e serviço liberados em conjunto. Arena em arquivo único, contrato `POST /v1/auditorias` com cinco campos de entrada, cinco gates de saída, limite de 40 a 250.000 caracteres |

Histórico anterior a 1.2.0 não é recuperável a partir dos artefatos
disponíveis. A lacuna fica visível de propósito, em vez de preenchida por
inferência.

**Divergência conhecida e não resolvida:** o módulo é 1.2.0, mas o serviço em
`CORPUS/.ATRIO/3.CERNE/api/` declara `0.2.0` no `pyproject.toml` e no
`__init__.py`. Os dois números foram preservados como estão. O envelope de
release da API carrega os dois campos separados,
`cerne_module_version: "1.2.0"` e `cerne_service_build: "0.2.0"`, o que torna
a divergência explícita em vez de ambígua. Fechar isso é decisão do autor.

**Acréscimo:** o CERNE 1.2.0 tem runtime na API desde 2026-07-29, com
`CERNE_INTEGRATION_VERSION` 0.1.0 e base normativa de 35 arquivos verificada
por hash no manifesto normativo.

### `atrio_pii` — 1.0.0

Biblioteca de detecção compartilhada entre CORPUS e LUX.

| Versão | Data | Mudança |
|---|---|---|
| 1.0.0 | 26/07/2026 | Linha aberta na auditoria de versionamento. Motor único de detecção por expressão regular e heurística de nome, spaCy opcional, triagem de segredo, resolução de sobreposição |

A razão de existir a linha continua a mesma: consumida por dois componentes,
uma alteração aqui mudaria o comportamento de ambos sem mover nenhuma das duas
versões. Desde a normalização, a versão também está declarada em código, na
constante `VERSAO`, e é gravada no cabeçalho de todo log de execução.

### `atrio_api` — 0.7.0 (linha ausente do relatório anterior)

Plano de controle local da execução integral dos quatro módulos.

| Versão | Data | Mudança |
|---|---|---|
| ≤ 0.6.0 | 07/2026 | Núcleo, contratos de execução, release imutável, idempotência por tenant, máquina de estados, persistência PostgreSQL, entrada documental CORPUS, cofre AES-256-GCM |
| 0.7.0 | 28/07/2026 a 29/07/2026 | Runtime não interativo para containers com segredos por arquivo. Contrato governado do adapter Ollama. Runtime executável de RATIO e TROIA. Rotas governadas de CERNE e LUX. Console operacional servida pela própria API |

A versão está em pré-1.0 de propósito. O contrato HTTP ainda pode quebrar.

### `ollama_adapter` — 0.2.0 (linha ausente do relatório anterior)

Inferência local versionada, determinística, sem resposta bruta.

| Versão | Data | Mudança |
|---|---|---|
| 0.1.0 | 07/2026 | Digest do modelo e hashes de proveniência |
| 0.2.0 | 29/07/2026 (`e39584f`) | Contrato de inferência congelado: `num_ctx` e `num_predict` obrigatórios, limite conservador antes da chamada HTTP, telemetria de tokens obrigatória, recusa de resposta truncada |

Três testes automatizados travam esse contrato. O adapter não autoriza
transições na máquina de estados e não produz artefato jurídico.

### `atrio_infra` — 1.0.0 (linha ausente do relatório anterior)

PostgreSQL, API e Ollama em containers locais.

| Versão | Data | Mudança |
|---|---|---|
| 1.0.0 | 29/07/2026 | Primeira infraestrutura oficial. Imagens fixas, segredos por arquivo, contexto de build por allowlist, verificação de digest do bundle normativo. Temporal deliberadamente fora |

**Estado de verificação: declarado, não construído.** A imagem nunca foi
gerada, porque Docker não está disponível na máquina de desenvolvimento.

### `atrio_backup` — 1.0.0 (linha ausente do relatório anterior)

| Versão | Data | Mudança |
|---|---|---|
| 1.0.0 | 07/2026 | Dump PostgreSQL e cofre sob manifesto HMAC-SHA-256. Sem rotação destrutiva; a restauração preserva banco e cofre anteriores |

### `atrio_db_schema` — 1.3.0 (linha ausente do relatório anterior)

Cada migração é identificada por versão e SHA-256, ambos fixados em
`database.py` e verificados na inicialização.

| Versão | Arquivo | Mudança |
|---|---|---|
| 1.0.0 | `0001_initial.sql` | Releases, execuções, idempotência, artefatos, comandos, eventos |
| 1.1.0 | `0002_corpus_intake.sql` | Registros imutáveis da entrada documental |
| 1.1.1 | `0003_corpus_event_metadata.sql` | Trilha segura restrita a `document_id` e `document_sha256` |
| 1.2.0 | `0004_corpus_processing.sql` | Resultados de processamento, decisões de revisão, referências de handoff |
| 1.3.0 | `0005_ratio_runtime.sql` | Execução persistida do RATIO |

---

## 5. Pendências abertas

### Correções aprovadas, ainda não aplicadas

Do relatório anterior, e ainda válidas:

- RATIO **7.0.1**
- LUX **6.0.1**
- CORPUS **1.4.1** → **agora seria 1.5.1**, porque a base saiu de 1.4.0

Quando aplicadas, cada uma exige atualização simultânea de `VERSIONS.yaml` e
deste arquivo.

### Divergências encontradas na verificação de 2026-07-30

| # | Divergência | Impacto | Decisão pendente |
|---|---|---|---|
| 1 | `MANIFEST.yaml` traz hash obsoleto para `ratio/governanca/core_governanca.md`: declara `e95e3057…`, o arquivo real é `786c71ac…`, que é o valor do manifesto normativo | Baixo. O `RUNTIME_NORMATIVE_MANIFEST.json` está certo e é ele que o build verifica. O `MANIFEST.yaml` ficou para trás | Regerar `MANIFEST.yaml` com `build/build.py` |
| 2 | `packages/lux/` tem duas famílias normativas em paralelo: os três `.txt` legados, que o Dockerfile copia e o manifesto normativo rastreia, e `kernel/*.md` + `conhecimento/*.md`, que o `MANIFEST.yaml` rastreia. Conteúdos diferentes | **Alto.** Editar os `.md` normalizados não muda o comportamento do runtime, que lê os `.txt` | Escolher uma família e remover a outra, ou declarar qual é fonte e qual é derivada |
| 3 | Serviço CERNE em `0.2.0` contra módulo em `1.2.0` | Baixo, porque o envelope de release separa os dois campos | Decisão do autor, registrada em `RELATORIO_NORMALIZACAO.md` |
| 4 | `infra/` na raiz do repositório contradiz o runtime em oito pontos, incluindo credenciais por variável de ambiente e factory inexistente | **Alto** se alguém executar | Remover, ou marcar como legado. Detalhado em `docs/api/OPERACAO.md` |
| 5 | `README.md` do `atrio_api` citava adapter `0.1.0`, schema `1.2.0`, `unittest discover` e omitia sete rotas | **Resolvido.** O README foi reconciliado com a API `0.7.0`, schema `1.3.0`, suíte pytest e 23 caminhos `/v1` | Preservar o README do pacote como definição canônica da API |
| 6 | Quatro referências de commit circulam: pré-registro fixa `e39584f`, evidência é de `dfd509e`, código/infra foram consolidados em `e109793` e os kits entraram em `a759213` | Baixo, porque `src` e `tests` não mudaram entre eles | Realinhar o `candidate_product_commit` quando o protocolo for fechado |

### Artefatos ausentes do inventário

Do relatório anterior, verificados e ainda pertinentes:

- Bloco de governança crítica do RATIO. **Situação atualizada:** já entrou no
  monorepo como `packages/ratio/governanca/instructions.md`, com hash
  `f0429a1a…` no manifesto normativo. Origem registrada no `MANIFEST.yaml`
  como "entregue pelo autor em 2026-07-26". Pendência **resolvida**.
- Serviço que atende o contrato `/v1` do CERNE. **Situação atualizada:**
  presente em `packages/cerne/api/`, versão `0.2.0`. Pendência **resolvida**,
  restando a divergência de numeração (item 3 acima).
- Script de captura do CORPUS. **Situação atualizada:** presente como
  `packages/corpus/src/captura.py`, hash `7e337c51…` no `MANIFEST.yaml`.
  Pendência **resolvida**.

---

## 6. Procedimento para mover uma versão

Quatro passos, na ordem. Pular um deles quebra a verificação automática.

1. **Alterar o artefato.** Código, base normativa ou migração.
2. **Atualizar `VERSIONS.yaml`.** É a autoridade. Se a mudança for em base
   normativa, regerar o manifesto normativo:
   ```bash
   python tools/build_runtime_normative_manifest.py
   ```
   e copiar o novo `content_digest` para `NORMATIVE_BUNDLE_SHA256` em
   `release_catalog.py`. Sem isso, o build da imagem aborta.
3. **Atualizar este arquivo.** Linha nova na tabela do componente, com data e
   descrição da mudança em uma frase.
4. **Rodar a suíte.**
   ```bash
   python -m pytest -q packages/services/atrio_api/tests
   ```

Se a versão da API mudou, atualizar também `ATRIO_API_VERSION` no
`infra/.env.example`, senão o build aborta na verificação de versão.

---

## 7. Registro deste documento

| Data | Ação |
|---|---|
| 2026-07-30 | Criação. Verificado contra o commit `e109793`. Corrigido CORPUS de 1.4.0 para 1.5.0. Acrescentadas cinco linhas de plataforma ausentes do relatório anterior: `atrio_api`, `ollama_adapter`, `atrio_infra`, `atrio_backup`, `atrio_db_schema`. Substituída a entrada "ATRIO sem release próprio" pelo candidato `1.0.0-rc.1` e pelo `release_id` composto. Três artefatos antes ausentes do inventário confirmados como presentes. Seis divergências novas registradas na seção 5 |
| 2026-07-30 | README canônico da API reconciliado com `0.7.0`, schema `1.3.0`, 19 caminhos `/v1` e suíte pytest. Kits harmonizados para distinguir validação operacional do método, verificação de engenharia da API e avaliação experimental formal em fechamento. |
| 2026-07-30 | Runtime HTTP final fechado com quatro rotas governadas para integridade, retorno ao LUX e liberação. API passa a expor 23 caminhos `/v1`; suíte ampliada para 175 testes. Prefixo `oss` removido do `release_id` para refletir a distribuição pública com todos os direitos reservados. |
