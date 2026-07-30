# FICHA INSTRUCIONAL — EIXO EX007 ANALÓGICO-PRECEDENTAL (LEVI)

**Código:** EX007
**Nome do método:** Analógico-Precedental
**Arquiteto-pai:** Edward H. Levi

---

## 0. NÚCLEO EXECUTIVO

*Bloco imperativo — colável diretamente no Roteiro Operacional do módulo de construção do raciocínio.*

---

**EIXO EX007 — ANALÓGICO-PRECEDENTAL (LEVI)**

**Pergunta operacional:**
> A aplicação de precedente ou analogia neste output isolou a ratio decidendi, operou o distinguishing necessário e separou holding de obiter?

*Vocabulário operacional:* **ratio decidendi** = fundamento jurídico necessário à decisão do paradigma; **distinguishing** = demonstração de diferença factual ou normativa relevante que afasta o precedente; **distinguishing reverso** = demonstração de que a diferença factual existente é irrelevante à luz da o módulo de construção do raciocínio; **holding** = passagem necessária à decisão; **obiter dictum** = passagem lateral, hipotética ou doutrinária; **IRDR** = Incidente de Resolução de Demandas Repetitivas; **IAC** = Incidente de Assunção de Competência.

**Sequência operacional:**

1. Identificar toda invocação de precedente, súmula, tema repetitivo, IRDR, IAC, orientação jurisprudencial ou analogia entre casos.
2. Verificar se o output isolou a ratio decidendi do paradigma.
3. Verificar se a o módulo de construção do raciocínio declarada é necessária à conclusão do precedente ou se é apenas passagem lateral.
4. Mapear diferenças factuais e normativas relevantes entre paradigma e caso atual.
5. Verificar se o output operou distinguishing ou distinguishing reverso quando havia diferença relevante.
6. Verificar se houve uso de obiter dictum como holding.
7. Verificar se a consolidação jurisprudencial ou o alcance vinculante foram demonstrados.
8. Aplicar marcador, classificar severidade, registrar no formato padrão.

**Testes binários de entrada:**

| Critério | Entra? |
|---|---|
| O output invoca precedente, súmula, tema repetitivo, IRDR, IAC ou jurisprudência como fundamento? | Se sim → entra |
| O output opera analogia entre casos, decisões ou domínios jurisprudenciais? | Se sim → entra |
| A tese depende da força persuasiva ou vinculante de decisão anterior? | Se sim → entra |
| O output afirma jurisprudência pacífica, consolidada, iterativa ou remansosa? | Se sim → entra |
| A ratio decidendi foi isolada de modo suficiente? | Se sim → prossegue; se não → marca |
| Há diferença factual ou normativa relevante entre paradigma e caso atual? | Se sim → exige distinguishing |
| A diferença relevante foi enfrentada à luz da o módulo de construção do raciocínio? | Se sim → prossegue; se não → marca |
| A passagem invocada era necessária à decisão do paradigma? | Se sim → prossegue; se não → marca |
| O problema é apenas peso prático da autoridade mobilizada? | Se sim → não entra isoladamente (domínio de EX011) |
| O problema é colapso entre categorias jurídicas distintas? | Se sim → não entra isoladamente (domínio de EX006) |

**Marcadores canônicos:**

| Marcador | Status | Uso |
|---|---|---|
| `[RATIO DECIDENDI NÃO ISOLADA]` | core | Precedente central citado sem identificação da razão necessária de decidir |
| `[DISTINGUISHING OMITIDO]` | core | Diferença factual ou normativa relevante não enfrentada à luz da o módulo de construção do raciocínio |
| `[OBITER COMO HOLDING]` | core | Passagem lateral, hipotética ou doutrinária tratada como fundamento necessário ou vinculante |
| `[ANALOGIA EMENTÁRIA]` | core | Aplicação feita por semelhança de ementa, tese ou frase, sem reconstrução da razão de decidir |
| `[CONSOLIDAÇÃO NÃO DEMONSTRADA]` | core | Uso de "pacífico", "consolidado", "iterativo" ou equivalente sem demonstração mínima |
| `[ALCANCE DO PRECEDENTE EXCEDIDO]` | core | Súmula, tema, IRDR, IAC ou precedente vinculante aplicado fora do alcance definido |

**Regras de não-acionamento:**

- Se o output não invoca precedente, jurisprudência ou analogia entre casos, então não marca.
- Se o precedente é apenas ilustração lateral e não sustenta a tese, então não marca como falha central.
- Se a o módulo de construção do raciocínio foi isolada de modo suficiente, ainda que sem vocabulário técnico, então não marca.
- Se a diferença factual ou normativa não altera a o módulo de construção do raciocínio, então não marca `[DISTINGUISHING OMITIDO]`.
- Se a crítica é ao mérito do precedente, e não à sua operação técnica, então não marca.
- Se a ausência é de exaustividade jurisprudencial, e não de operação técnica do precedente, então não marca.
- Se o problema é peso prático da fonte, então não marca isoladamente; sinalizar EX011.
- Se o problema é força epistêmica da analogia, então não marca isoladamente; sinalizar EX003.

**Regra de integridade do eixo:**

> Levi não audita o mérito do precedente. Audita a operação técnica de extração, transporte e aplicação da razão de decidir.

**Regra de fronteira com ementas:**

> Ementa não equivale a o módulo de construção do raciocínio. Tese repetitiva, súmula ou orientação consolidada exigem verificação de alcance e fundamento determinante.

**Ponto cego declarado:**

O eixo não detecta colapso entre categorias jurídicas distintas (domínio de EX006). Não mede a regra que a decisão atual instituiria se universalizada (domínio de EX008). Não calibra o peso prático da autoridade mobilizada (domínio de EX011). Não avalia a força epistêmica da inferência analógica (domínio de EX003). Levi opera exclusivamente sobre a técnica de extração, transporte e aplicação da razão de decidir.

---

## 0.1 PROMPTS OPERACIONAIS CANÔNICOS

**Termos de ativação interna sugeridos:**

- Principal: "Levi" (uso restrito ao projeto); "analógico-precedental" (uso público); "operação técnica do precedente"
- Compostos discriminantes: "ratio decidendi não isolada", "distinguishing omitido", "obiter como holding", "analogia ementária", "consolidação não demonstrada", "alcance do precedente excedido"
- Vetados isoladamente: "precedente", "jurisprudência", "analogia", "ementa", "julgado" (comuns demais quando isolados)

**Tabela de lacunas de cobertura:**

| Objeto | Código | Status | Prompt canônico |
|---|---|---|---|
| Peça processual | EX007-PEC | Pendente | — |
| Cláusula contratual | EX007-CON | Pendente | — |
| Parecer jurídico | EX007-PAR | Pendente | — |
| Nota técnica | EX007-NOT | Pendente | — |
| Output de IA jurídica externa | EX007-OUT | Pendente | — |
| Decisão judicial | EX007-DEC | Pendente | — |
| Precedente como argumento | EX007-PRE | Pendente | — |

---

## 0.2 CLÁUSULA DE ATIVAÇÃO, CONTENÇÃO E DESCARTE

**Regra-mãe (acima da ficha):**

> Achados transitam. Lentes não.
>
> Entre fases do módulo de construção do raciocínio, transferem-se apenas produtos estruturados da análise anterior: achados, marcadores, severidade, gates, pendências, restrições e versões corrigidas. O modo de raciocínio do eixo ativado não se transfere automaticamente para a fase seguinte.

**Cláusula específica do eixo EX007:**

Ao fim da fase em que o eixo Levi foi ativado, desativa-se o modo precedental de leitura. Não permanece em fases subsequentes a tendência de reconstruir todo argumento como aplicação de precedente ou de exigir o módulo de construção do raciocínio, distinguishing e holding onde não há precedente operante. Permanecem como produtos exportáveis: marcadores aplicados, severidade registrada, o módulo de construção do raciocínio identificada ou ausente, diferenças relevantes, alcance do precedente, pendências de verificação e versão corrigida.

**Riscos específicos de contaminação por resíduo EX007:**

- Tendência a jurisprudencializar argumentos normativos, contratuais ou factuais que não dependem de precedente.
- Tendência a exigir distinguishing em situações sem paradigma decisório relevante.
- Tendência a converter problema de peso prático da fonte em defeito de operação precedental (domínio de EX011).
- Tendência a converter colapso categorial em falha de o módulo de construção do raciocínio (domínio de EX006).
- Tendência a tratar ausência de citação exaustiva como falha de aplicação do precedente.

**Comportamento em confronto com outro eixo:**

Quando pareado com EX006, Levi verifica se a ponte entre paradigma e caso foi tecnicamente construída; Matte-Blanco verifica se essa ponte apagou distinção juridicamente relevante.

Quando pareado com EX011, Levi verifica a operação técnica do precedente; Raz calibra o peso prático da autoridade depois de estabilizada a leitura mínima do paradigma.

Quando pareado com EX008, Levi olha para trás, em direção ao paradigma; MacCormick olha para frente, em direção à regra que a aplicação atual passaria a instituir.

**Comportamento na entrega final:**

À fase de refinamento textual transmitem-se apenas marcadores não resolvidos e qualificadores de operação precedental ("o módulo de construção do raciocínio não isolada", "diferença factual relevante", "alcance não demonstrado", "consolidação não comprovada"). Não se transmite postura cognitiva de dependência jurisprudencial nem instrução de reabrir precedentes já estabilizados.

---

**Nota de modularidade indexada:**

Quando houver sinalização para eixo correlato, a ficha indica apenas o código do eixo (`EX00X`). A descrição completa do confronto, da ordem recomendada e do risco de dupla marcação deve ser consultada na `MATRIZ_DE_CONFRONTOS_INTER_EIXOS_EX.md`.

## 1. ARQUITETO-PAI

Edward Hirsch Levi (1911–2000) foi jurista americano, decano da Faculdade de Direito da Universidade de Chicago e Procurador-Geral dos Estados Unidos. Sua obra central, *An Introduction to Legal Reasoning* (1949), é uma das formulações mais influentes sobre o raciocínio jurídico por analogia e por precedente no *common law*, e tornou-se referência mesmo em sistemas de tradição continental.

A tese de Levi é direta e operacional: o raciocínio jurídico, em sua estrutura nuclear, é raciocínio de caso a caso por semelhança — não derivação dedutiva de regras fixas a partir de textos legais. Cada aplicação de precedente é simultaneamente um ato de **reconhecimento de semelhança** e um ato de **redefinição da regra**. A regra extraída do caso paradigma não pré-existe à sua aplicação a um novo caso — ela é continuamente redefinida pelo conjunto de aplicações.

**Por que Levi e não outro?**

O problema que o eixo precisa capturar é específico: outputs jurídicos brasileiros, em ambiente pós-CPC/2015, operam intensamente com precedentes vinculantes (súmulas, temas repetitivos, IRDR, IAC) e com aplicação analógica de jurisprudência. A operação típica defeituosa é a transposição da ementa, ignorando a *ratio decidendi* do caso paradigma. O output cita o precedente, mas não isola o que, na decisão, foi efetivamente decidido para resolver aquele caso — e tampouco demonstra que essa *o módulo de construção do raciocínio* alcança o caso atual.

Levi é o arquiteto adequado porque formulou, com precisão metodológica, as três operações que toda aplicação rigorosa de precedente exige: (i) identificação da regra extraída do caso anterior; (ii) verificação de que essa regra cobre o caso atual; (iii) tratamento das diferenças factuais como relevantes ou irrelevantes à luz da *o módulo de construção do raciocínio*. Scott Brewer, em *Exemplary Reasoning* (1996), refinou a teoria mostrando que a analogia jurídica é EX003 de uma regra unificadora seguida de teste de aplicação — o que conecta tecnicamente o eixo ao terreno de EX003 sem com ele se confundir.

A dogmática brasileira contemporânea de precedentes (Marinoni, Mitidiero, Didier Jr., Macêdo, Zaneti Jr.) fornece o vocabulário operacional aplicado: *ratio decidendi*, *obiter dictum*, *distinguishing*, *overruling* (superação do precedente por mudança de entendimento), transcendência dos motivos determinantes, eficácia horizontal e vertical do precedente. Esse vocabulário traduz Levi para o sistema brasileiro de precedentes vinculantes do art. 927 do CPC.

A diferença em relação aos demais eixos é precisa. EX006 detecta o colapso entre categorias — aponta a simetria indevida. Levi opera sobre a operação positiva da analogia: o que precisa ser feito para que a aplicação se sustente. EX003 trata a analogia como tipo de inferência (EX003) e cobra que ela seja apresentada como tal. Levi não trata a inferência em si, mas a operação técnica de aplicar precedente — isolamento da *o módulo de construção do raciocínio*, *distinguishing*, separação *holding/obiter*. EX001 pergunta se há EX001; Levi pergunta se a peça do *backing* (sustentação de fundo da garantia) chamada "precedente" foi adequadamente operada. EX002 testa a tese por objeção; Levi testa a aplicação do precedente por rigor analógico. EX008 testa a regra de decisão universalizada; Levi testa o ato de extrair regra do precedente paradigma.

---

## 2. O TRAÇADO FILOSÓFICO

**Raciocínio caso a caso.** Para Levi, o Direito não se desdobra a partir de princípios fixos aplicados por subsunção. Ele se desenvolve por movimento de três tempos: comparação do novo caso com casos anteriores; identificação de semelhança relevante; aplicação ou recusa da regra extraída do caso anterior. Esse movimento é, simultaneamente, conservador (preserva a regra) e criativo (a redefine a cada aplicação). A regra que se aplica a um novo caso nunca é exatamente a regra que se aplicou ao caso anterior — é uma versão refinada pela diferença factual.

**ratio decidendi e obiter dictum.** A *ratio decidendi* é o fundamento jurídico **necessário** à decisão do caso paradigma — aquilo que, removido, faria a decisão cair. O *obiter dictum* é tudo o que o tribunal disse além do necessário: considerações tangenciais, hipóteses, comentários sobre situações análogas, observações sobre a doutrina. Apenas a *o módulo de construção do raciocínio* tem força vinculante ou persuasiva genuína; o *obiter* tem, no máximo, valor argumentativo. A confusão entre os dois é a forma mais comum de aplicação defeituosa de precedente.

**O distinguishing reverso.** O *distinguishing* é a operação pela qual se demonstra que um precedente *não* se aplica ao caso atual, por diferença factual relevante. O *distinguishing reverso* — operação central do eixo Levi — é o inverso: demonstrar que, **apesar** das diferenças factuais entre paradigma e caso atual, essas diferenças são irrelevantes **à luz da *o módulo de construção do raciocínio***. Ambos os movimentos exigem isolamento prévio da *o módulo de construção do raciocínio*. Sem ele, *distinguishing* e *distinguishing reverso* são exercícios retóricos.

**A analogia comEX003 (refinamento de Brewer).** Scott Brewer mostrou que a analogia jurídica tem estrutura inferencial específica: parte-se da semelhança entre caso paradigma e caso atual; abduz-se uma regra unificadora que explicaria a decisão no paradigma; testa-se essa regra contra o caso atual. A regra abduzida é hipótese — pode estar errada. A analogia bem feita declara a regra abduzida e a submete a teste; a analogia mal feita aplica a regra como se ela fosse a evidente da ementa. Brewer conecta tecnicamente o eixo Levi ao terreno de EX003: a analogia *é* EX003. Mas EX003 trata da força epistêmica da inferência; Levi trata da operação técnica de extrair e aplicar a regra.

**Precedentes vinculantes no Direito brasileiro.** O CPC/2015 instituiu sistema robusto de precedentes vinculantes (art. 927): decisões do STF em controle concentrado, súmulas vinculantes, acórdãos em IRDR, IAC, temas repetitivos, orientação do plenário ou órgão especial. A vinculação não é à ementa nem ao dispositivo, mas à *ratio decidendi*. A jurisprudência brasileira sobre transcendência dos motivos determinantes (STF) e sobre os limites da vinculação reforça: o que vincula é a regra de decisão, isolada por rigor metodológico, não a frase mais sonora do acórdão.

**Tradução operacional.** O traçado de Levi aplica-se ao módulo de construção do raciocínio como protocolo de verificação da operação técnica do precedente. A pergunta não é "o precedente é bom?" — é "a aplicação do precedente neste output executou as três operações necessárias: isolamento da *o módulo de construção do raciocínio*, *distinguishing* reverso quando há diferença factual, separação entre *holding* e *obiter*?"

---

## 3. A OPERAÇÃO DO EIXO

O o módulo de construção do raciocínio raciocina sob o eixo EX007 Levi na seguinte sequência:

**Passo 1 — Identificação da operação analógica ou de aplicação de precedente.**
O o módulo de construção do raciocínio localiza no output todos os pontos em que: (i) se invoca decisão judicial específica (REsp, RE, acórdão, monocrática); (ii) se invoca súmula, tema repetitivo, IRDR, IAC ou orientação consolidada; (iii) se afirma "jurisprudência pacífica", "entendimento consolidado", "orientação iterativa"; (iv) se opera analogia entre casos sem invocar precedente formal, mas com estrutura de transposição.

Cada ocorrência abre uma operação de análise pelo eixo.

**Passo 2 — Isolamento da *ratio decidendi* do caso paradigma.**
Para cada precedente invocado, o o módulo de construção do raciocínio verifica se o output isolou o fundamento jurídico **necessário** à decisão do caso paradigma. Três testes operacionais:

- O output explicita qual foi o fato decisivo do caso paradigma?
- O output explicita qual foi a regra jurídica aplicada para resolver esse fato?
- A regra explicitada é necessária à conclusão do paradigma, ou poderia ser substituída por outra sem alterar o resultado?

Se não houver isolamento — apenas citação de ementa ou referência genérica — aciona `[RATIO DECIDENDI NÃO ISOLADA]`.

**Passo 3 — Mapeamento das diferenças factuais entre paradigma e caso atual.**
O o módulo de construção do raciocínio identifica as diferenças factuais entre o caso paradigma (na medida em que o output o descreva ou que sejam verificáveis no material disponível) e o caso atual. As diferenças relevantes incluem: perfil das partes, regime jurídico aplicável, momento processual, base normativa em vigor à época, tipo contratual ou processual, natureza do litígio.

Diferenças factuais não são, em si, achado. O achado emerge no Passo 4.

**Passo 4 — Operação do *distinguishing* reverso.**
Quando há diferenças factuais relevantes entre paradigma e caso atual, o o módulo de construção do raciocínio verifica se o output demonstrou que **essas diferenças são irrelevantes à luz da *o módulo de construção do raciocínio***. A demonstração tem estrutura específica: "a *o módulo de construção do raciocínio* do paradigma é R; R depende dos fatos F1, F2, F3; o caso atual possui F1, F2, F3, embora difira em F4; F4 não integra a *o módulo de construção do raciocínio*; logo, R se aplica."

Ausência dessa demonstração, quando há diferenças factuais relevantes, aciona `[DISTINGUISHING OMITIDO]`.

**Passo 5 — Separação entre *holding* e *obiter*.**
O o módulo de construção do raciocínio verifica se o output, ao invocar o precedente, está sustentando-se no *holding* (regra de decisão necessária) ou em *obiter* (passagem tangencial). Sinais de uso de *obiter* como *holding*:

- A passagem invocada é hipotética ("ainda que se entendesse...", "mesmo na hipótese de...")
- A passagem invocada trata de situação distinta da efetivamente decidida
- A passagem invocada é considerando geral ou doutrinário, não razão de decidir

Uso de *obiter* como *holding* aciona `[OBITER COMO HOLDING]`.

**Passo 6 — Verificação de "consolidação" alegada.**
Quando o output afirma "jurisprudência pacífica", "entendimento consolidado", "orientação iterativa", o o módulo de construção do raciocínio verifica:

- A consolidação é demonstrada por amostra mínima de julgados convergentes?
- Os julgados citados (ou verificáveis no material disponível) compartilham a mesma *o módulo de construção do raciocínio*?
- Há decisões divergentes do mesmo tribunal ou de tribunais paralelos?
- A consolidação alegada cobre o exato ponto controvertido, ou apenas adjacências?

Afirmação de consolidação sem lastro estrutural aciona `[CONSOLIDAÇÃO NÃO DEMONSTRADA]`.

**Passo 7 — Verificação do alcance do precedente.**
Para precedentes formalmente vinculantes (súmulas, temas repetitivos, IRDR, IAC), o o módulo de construção do raciocínio verifica se o caso atual está dentro do alcance definido no acórdão de origem. O alcance é definido pela *o módulo de construção do raciocínio* do precedente, não pela amplitude da ementa.

Aplicação fora do alcance aciona `[ALCANCE DO PRECEDENTE EXCEDIDO]`.

**Passo 8 — Classificação e marcação.**
O o módulo de construção do raciocínio aplica o marcador canônico, classifica a severidade e registra o achado no formato padrão.

---

## 4. O QUE CONTA COMO ACHADO REAL

Achado real é qualquer instância em que a aplicação de precedente ou analogia no output depende de operação técnica ausente, incompleta ou substituída por atalho retórico, com consequência para a sustentação da tese.

**Exemplo operativo — memorial em ação revisional (caso de teste 28/05/2026).**

A peça invocou: *"é pacífica a jurisprudência do STJ no sentido da aplicação do CDC a contratos empresariais de adesão quando demonstrada hipossuficiência técnica da parte aderente (REsp [P-1]; REsp [P-2])"*, transpondo essa orientação para contrato de franquia regulado por lei especial posterior.

Achados Levi:

- `[RATIO DECIDENDI NÃO ISOLADA]` — o output não isola se a *o módulo de construção do raciocínio* dos precedentes invocados é (a) mera adesão como forma contratual, (b) hipossuficiência técnica concreta provada nos autos, (c) ausência de regime especial regente, ou (d) destinação final fática. Sem esse isolamento, a "pacificação" alegada não tem objeto definido.
- `[DISTINGUISHING OMITIDO]` — o caso atual difere do paradigma em ponto estrutural: existência de lei especial regente (Lei 13.966/2019) posterior ao CDC. Essa diferença não é tratada. A peça não demonstra que a diferença é irrelevante à luz da *o módulo de construção do raciocínio* — porque, se a *o módulo de construção do raciocínio* envolve "ausência de regime especial", a diferença é determinante e a aplicação cai.
- `[CONSOLIDAÇÃO NÃO DEMONSTRADA]` — "pacífica" é afirmado, mas a demonstração estrutural (amostra convergente, ausência de divergência, mesma *o módulo de construção do raciocínio*) não é apresentada.

Severidade global da aplicação do precedente nesta peça: **Alta**. A tese central depende da aplicação do CDC; a aplicação do CDC depende dos precedentes invocados; a operação técnica dos precedentes está estruturalmente comprometida.

---

## 5. O QUE NÃO CONTA — ANTI-PADRÕES

**Mérito do precedente ≠ aplicação do precedente.**
O eixo não diz se o precedente está certo; diz se ele foi adequadamente operado.

**Diferença factual ≠ diferença relevante.**
Toda peça tem fatos diferentes do paradigma. Só conta como achado quando a diferença afeta a *o módulo de construção do raciocínio*.

**Ausência de citação exaustiva ≠ falha de operação.**
Exaustividade jurisprudencial não é critério do eixo; rigor de aplicação é.

**Discordância doutrinária ≠ achado Levi.**
Crítica doutrinária ao precedente está fora do escopo.

**Crítica retórica ao tribunal ≠ achado Levi.**
Não pertence ao escopo do eixo.

**Ausência de vocabulário técnico ≠ ausência de operação.**
Se a *o módulo de construção do raciocínio* foi corretamente isolada e o *distinguishing* operado, ainda que sem nomenclatura formal, não há achado.

---

## 6. RÉGUA DE SEVERIDADE

| Nível | Critério | Consequência no gate |
|---|---|---|
| **Baixa** | Precedente invocado com isolamento implícito mas suficiente da *o módulo de construção do raciocínio*; ausência de vocabulário técnico, mas operação reconstruível. | Registro técnico. Sem bloqueio. |
| **Média** | *Distinguishing* omitido em diferença factual ou normativa relevante; *obiter* tratado como *holding* em ponto secundário; consolidação pouco demonstrada em fundamento lateral. | Nota de qualificação ou *patch* argumentativo. |
| **Alta** | *ratio decidendi* não isolada em precedente central; consolidação alegada sem lastro estrutural; alcance de precedente vinculante excedido em ponto relevante. | Bloqueio parcial. Exige reformulação da operação precedental antes do avanço. |
| **Crítica** | Tese central depende inteiramente de precedente cuja *o módulo de construção do raciocínio* não foi isolada, com diferença factual determinante não enfrentada, ou aplicação de súmula, tema repetitivo, IRDR ou IAC fora do alcance original. | Bloqueio total ou nota de inviabilidade. |

A severidade depende da função do precedente no output. Falha em precedente lateral pode gerar registro técnico. Falha em precedente que sustenta conclusão, pedido, voto, parecer ou estratégia processual aciona gate.


## 7. FORMATO DE OUTPUT ESPERADO

```
ACHADO — EIXO EX007 LEVI | ANALÓGICO-PRECEDENTAL

Operação analógica identificada:
[Qual precedente, súmula, tema, ou analogia é invocada — citação tal como aparece no output]

ratio decidendi declarada pelo output:
[Tal como o output a apresenta — ou registrar "não declarada"]

ratio decidendi verificável (do paradigma):
[Quando verificável no material disponível ou descritível com base em informação disponível — ou registrar "não verificável neste turno"]

Diferenças factuais relevantes entre paradigma e caso atual:
[Lista das diferenças que tocam a o módulo de construção do raciocínio]

Distinguishing reverso operado:
[Sim / Não / Parcial — descrever a operação ou sua ausência]

Holding × obiter:
[Identificação se o output se sustenta em o módulo de construção do raciocínio (holding) ou passagem tangencial (obiter)]

Consolidação alegada:
[Termo usado pelo output, e lastro apresentado — ou registrar "alegada sem lastro"]

Alcance do precedente:
[Para precedente vinculante: o caso atual está dentro do alcance definido? Justificativa]

Natureza do problema:
[Descrição segundo a racionalidade do eixo]

Acionamento de gate:
[Sem bloqueio / Nota de qualificação / Bloqueio parcial / Bloqueio total]

Observação:
[Apenas se necessário: distinção de anti-padrão, sobreposição com EX006, EX003 ou EX008, sinalização para outro eixo.]
```

---

## 8. OPERAÇÃO DENTRO DO o módulo de construção do raciocínio

**Ativação primária:**

- Fases que produzem ou revisam peça processual que invoca precedente
- Fases que produzem ou revisam parecer fundado em jurisprudência consolidada
- Fases que operam transposição entre domínios (CDC para contratos B2B, regime trabalhista para autônomos, etc.)
- Fases que aplicam súmula vinculante, tema repetitivo, IRDR ou IAC
- Fases que constroem tese a partir de agregação de julgados
- Fases que utilizam material jurisprudencial como fonte de precedentes para sustentar argumento

**Ativação em elaboração.**
Na elaboração, o eixo Levi opera como protocolo construtivo. Antes de invocar precedente, o o módulo de construção do raciocínio deve: (i) isolar a *o módulo de construção do raciocínio* do paradigma; (ii) mapear diferenças factuais para o caso atual; (iii) operar *distinguishing* reverso se houver diferença; (iv) declarar se a sustentação se dá em *holding* ou em *obiter*; (v) verificar alcance, se o precedente for vinculante. A redação só avança quando essas operações estão executadas.

**Ativação em revisão.**
Na revisão, o eixo Levi opera como auditoria de aplicação. Para cada precedente ou analogia invocada pelo output, o o módulo de construção do raciocínio executa os Passos 2 a 7. Achados acionam marcadores e severidade.

**Par de confronto de raciocínios primário: Levi × EX006.**
É o par de fricção mais produtivo do eixo. Levi opera construtivamente: "qual a *o módulo de construção do raciocínio* e como ela se aplica?". EX006 opera contentor: "que distinção foi colapsada ao aplicar?". A fricção produz achado emergente: o rigor analógico, quando aplicado, frequentemente faz emergir exatamente a distinção que EX006 aponta como colapsada — porque o regime especial não declarado costuma ser, ele próprio, parte da *o módulo de construção do raciocínio* do precedente paradigma.

Instrução para confronto:
> "Ative Levi para isolar *o módulo de construção do raciocínio*, mapear diferenças factuais e operar *distinguishing*. Em seguida — ou em paralelo — ative EX006 para verificar se distinções juridicamente relevantes foram apagadas pela operação analógica. Convergência dos dois eixos sobre o mesmo ponto eleva severidade. Divergência (Levi aprova a operação, EX006 aponta colapso) força reexame humano."

**Par de confronto de raciocínios secundário: Levi × EX003.**
Levi trata a *operação técnica* da analogia; EX003 trata a *força epistêmica* da inferência analógica comEX003. O par opera quando o output apresenta a aplicação do precedente com força dedutiva ("logo, aplica-se") em vez de abdutiva ("a *o módulo de construção do raciocínio* é plausivelmente extensível"). EX003 cobra a qualificação epistêmica; Levi cobra a operação técnica.

**Par de confronto de raciocínios terciário: Levi × EX008.**
Levi trata o ato de extrair regra do precedente paradigma; EX008 trata a regra que essa extração instituiria como norma universalizada. O par opera em precedentes de fronteira, em que a aplicação ao caso atual *redefine* a *o módulo de construção do raciocínio* do paradigma — ato com consequência sistêmica que EX008 precisa medir.

**Ativação secundária por sinalização.**
Outros eixos podem sinalizar necessidade de Levi quando identificarem:
- Citação de precedente sem operação técnica visível (sinalizaçãEX001)
- Conclusão dedutiva apresentada com lastro analógico (sinalizaçãEX003)
- Equiparação entre categorias com regimes distintos sustentada em jurisprudência (sinalizaçãEX006)
- Tese que, se vence, redefine o alcance de precedente vinculante (sinalizaçãEX008)

---

## 9. DISTINÇÕES confronto de raciocíniosÍTICAS

### 9.1. Analógico-precedental vs. EX006 (EX007 vs. EX006)

Levi constrói. Matte-Blanco detecta colapso.

| | Levi | Matte-Blanco |
|---|---|---|
| Pergunta | A operação analógica isolou *o módulo de construção do raciocínio* e operou *distinguishing*? | Que distinção foi suprimida ao equiparar? |
| Unidade de análise | Operação técnica de aplicar precedente | Equivalência entre categorias |
| Defeito típico | *o módulo de construção do raciocínio* não isolada; *distinguishing* omitido | Categoria com regime distinto tratada como equivalente |
| Movimento | Positivo — o que precisa ser feito | Negativo — o que foi indevidamente apagado |
| Correção | Executar a operação ausente | Declarar a distinção e ajustar conclusão |

Erro comum: tratar todo problema analógico como colapso (EX006) sem examinar se a operação técnica de aplicação foi tentada (Levi). Outro erro: tratar todo defeito de operação técnica (Levi) como mero formalismo, quando ele esconde colapso real (EX006).

### 9.2. Analógico-precedental vs. EX003 (EX007 vs. EX003)

Levi opera sobre a operação técnica. Peirce opera sobre o tipo de inferência.

| | Levi | Peirce |
|---|---|---|
| Pergunta | A *o módulo de construção do raciocínio* foi isolada e o *distinguishing* operado? | O tipo de inferência está adequadamente representado? |
| Defeito típico | Precedente citado sem isolamento da *o módulo de construção do raciocínio* | EX003 analógica apresentada como dedução |
| Correção | Executar isolamento e *distinguishing* | Qualificar a força epistêmica da conclusão |
| Convivência | Levi pode aprovar a operação e Peirce ainda reprovar a força com que foi apresentada |

### 9.3. Analógico-precedental vs. EX001 (EX007 vs. EX001)

Toulmin trata EX001 global. Levi trata especificamente a peça "precedente" do *backing*.

| | Levi | Toulmin |
|---|---|---|
| Pergunta | O *backing* "precedente" foi adequadamente operado? | A tese tem dados, garantia, *backing*, qualificador e exceção? |
| Unidade | Operação de aplicar precedente | Arquitetura inteira do argumento |
| Relação | Levi opera *dentro* da peça *backing* quando o *backing* é jurisprudencial |

### 9.4. Analógico-precedental vs. EX002 (EX007 vs. EX002)

Sócrates confronta a tese por objeção. Levi audita a aplicação do precedente.

| | Levi | Sócrates |
|---|---|---|
| Pergunta | A operação técnica foi executada? | A tese resiste à melhor objeção? |
| Foco | Procedimento analógico | Sustentação da tese |
| Convivência | Levi pode aprovar a operação técnica e Sócrates ainda derrubar a tese por outra via |

### 9.5. Analógico-precedental vs. EX008 (EX007 vs. EX008)

Levi olha para trás (paradigma). MacCormick olha para frente (regra universalizada).

| | Levi | MacCormick |
|---|---|---|
| Pergunta | A *o módulo de construção do raciocínio* do paradigma foi corretamente extraída? | A regra que esta decisão instituiria é universalizável e sistemicamente coerente? |
| Direção | Retrospectiva | Prospectiva |
| Convivência | Levi pode aprovar a extração e MacCormick reprovar a regra resultante |

### 9.6. Levi vs. Raz (EX007 vs. EX011)

Levi audita a operação técnica do precedente. Raz calibra o peso prático da autoridade.

| | Levi | Raz |
|---|---|---|
| Pergunta | A *o módulo de construção do raciocínio* foi isolada e o *distinguishing* operado? | A autoridade recebeu peso compatível com sua categoria? |
| Foco | Procedimento técnico de aplicar precedente | Força prática da fonte |
| Defeito típico | Citação sem isolamento da *o módulo de construção do raciocínio* | Decisão isolada tratada como vinculante |
| Sequência típica | Raz precede Levi quando a autoridade está mal calibrada; Levi precede Raz quando a operação técnica é o problema central |

**Lacunas remanescentes:** distinções com EX004, EX005, EX009 e EX010 a fechar quando todas as fichas estiverem consolidadas.

---

## 10. CHECKLIST DE FALHA DE EXECUÇÃO

O eixo falhou quando:

- [ ] O o módulo de construção do raciocínio aceitou citação de ementa como isolamento de *ratio decidendi*
- [ ] O o módulo de construção do raciocínio não identificou diferenças factuais relevantes entre paradigma e caso atual
- [ ] O o módulo de construção do raciocínio aceitou afirmação de "jurisprudência pacífica" sem lastro estrutural
- [ ] O o módulo de construção do raciocínio confundiu uso de *obiter* com uso de *holding*
- [ ] O o módulo de construção do raciocínio aplicou súmula vinculante ou tema repetitivo sem verificar alcance original
- [ ] O o módulo de construção do raciocínio confundiu *distinguishing* (afasta o precedente) com *distinguishing* reverso (afirma a aplicação apesar da diferença)
- [ ] O o módulo de construção do raciocínio tratou problema de operação técnica como problema de colapso categorial sem acionar EX006
- [ ] O o módulo de construção do raciocínio tratou problema de força epistêmica como problema de operação técnica sem acionar EX003
- [ ] O o módulo de construção do raciocínio classificou como achado a ausência de citação exaustiva
- [ ] O o módulo de construção do raciocínio confundiu mérito do precedente (não é objeto) com aplicação do precedente (é objeto)
- [ ] O output avançou com achado Alta ou Crítica sem resolução de gate

