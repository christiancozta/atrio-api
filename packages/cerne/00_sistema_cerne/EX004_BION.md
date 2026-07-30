# FICHA INSTRUCIONAL — EIXO EX004 INTEGRIDADE COGNITIVA (BION)

**Código:** EX004
**Nome do método:** Integridade Cognitiva
**Arquiteto-pai:** Wilfred R. Bion

---

## 0. NÚCLEO EXECUTIVO

*Bloco imperativo — colável diretamente no Roteiro Operacional do módulo de construção do raciocínio.*

---

**EIXO EX004 — INTEGRIDADE COGNITIVA**

**Pergunta operacional:**
> Que incerteza este output não declarou apesar de o domínio ou o dado exigir qualificação, método ou ressalva?

**Sequência operacional:**

1. Identificar zona de incerteza genuína no output
2. Classificar estado do domínio (consolidado, controvertido, em formação, indeterminado)
3. Testar fluência (linguagem de certeza vs. estimativa declarada)
4. Verificar base metodológica de dados numéricos, estimativas e avaliações de risco
5. Testar resolução de tensão (divergência tratada como resolvida?)
6. Aplicar protocolo de lastro (defeito de explicitação / segurança não lastreada / incerteza metodológica)
7. Classificar achado por marcador e severidade

**Testes binários de entrada:**

| Termo | Critério |
|---|---|
| Zona de incerteza genuína | O domínio é probabilístico, qualitativo ou doutrinariamente aberto? Sim → entra. Domínio consolidado → não entra. |
| Base metodológica de estimativa | Para cada dado numérico, estimativa ou avaliação de risco: há jurisprudência citada com critério de seleção, parâmetro de cálculo identificado ou critério de comparação nomeado? Os três ausentes → marca `[SEGURANÇA NÃO LASTREADA]`. |
| Tensão tratada como resolvida | A posição adotada é apresentada sem declarar que há divergência real (doutrinária, jurisprudencial ou interpretativa)? Sim → marca `[APAGAMENTO DE INCERTEZA]`. |
| Fluência substitutiva | A coerência verbal ocupa o lugar de uma demonstração, metodologia, qualificação de incerteza ou declaração de lacuna exigida pelo domínio? Sim → marca. Fluência por si só → não marca. |

**Marcadores canônicos e subtipos operacionais:**

| Marcador principal | Status | Subtipos |
|---|---|---|
| `[SEGURANÇA NÃO LASTREADA]` | core | percentual sem método; faixa sem base; risco sem amostra |
| `[APAGAMENTO DE INCERTEZA]` | core | controvérsia omitida; pacificação não demonstrada; tensão resolvida artificialmente |
| `[FLUÊNCIA SUBSTITUTIVA]` | core | lacuna encoberta; metodologia ausente; coerência verbal como prova |

**Regras de não-acionamento:**

- Domínio consolidado (súmula vinculante, repetitivo, precedente vinculante, orientação reiterada) → não marca; afirmação sem ressalva é adequada
- Incerteza declarada adequadamente → não marca; é sinal de integridade cognitiva (não falha)
- Posição adotada em divergência com declaração da tensão e justificativa → não marca
- Persona ou enquadramento retórico → não marca; persona não é mecanismo de apagamento de incerteza
- Imprecisão textual sem apagamento de incerteza → não é EX004 primário
- Falha de EX001 → sinalizar EX001
- Argumento unilateral em questão substantiva → sinalizar EX002
- Pré-compreensão interpretativa não declarada → sinalizar EX005

**Regra de integridade (não-falha):**
Incerteza declarada adequadamente não é falha do output — é sinal de integridade cognitiva. O eixo só marca defeito quando a incerteza exigível é suprimida, substituída por fluência ou convertida em número, probabilidade ou conclusão sem lastro.

**Regra anti-psicologizante (dura):**
O eixo não avalia intenção, ansiedade, defesa psíquica ou estado interno do modelo. Avalia apenas a estrutura epistêmica do output. A pergunta operacional é sobre o texto, não sobre o sistema que o produziu.

**Ponto cego declarado:**
EX004 não detecta problemas de estrutura argumentativa (domínio de EX001), construção adversarial (EX002), tipo de inferência (EX003), nem leiturEX005 situada (EX005).

---

## 0.1 PROMPTS OPERACIONAIS CANÔNICOS

*Bloco de governança interna. Prompts canônicos para os objetos jurídicos ainda não produzidos em ciclo formal de teste.*

**Termos de ativação interna sugeridos:**
- Principal: `Bion` (uso restrito ao projeto) e `integridade cognitiva` (compatível com uso público)
- Compostos discriminantes: `apagamento de incerteza`, `segurança não lastreada`, `fluência substitutiva`
- Vetados: `incerteza` isolado, `risco` isolado, `certeza` isolado (todos genéricos demais)

---

### Lacunas de cobertura (objetos sem prompt canônico)

| Objeto | Código previsto | Status |
|--------|-----------------|--------|
| Peça processual               | EX004-PEC | A produzir |
| Cláusula contratual           | EX004-CON | A produzir |
| Parecer jurídico              | EX004-PAR | A produzir |
| Nota técnica                  | EX004-NOT | A produzir |
| Output de IA jurídica externa | EX004-OUT | A produzir (objeto mais natural do eixo) |
| Decisão judicial              | EX004-DEC | A produzir |

---

## 0.2 CLÁUSULA DE ATIVAÇÃO, CONTENÇÃO E DESCARTE

*Cláusula transversal de governança de fase. Aplicável a todas as fichas de eixo do módulo de construção do raciocínio.*

**Regra-mãe (acima da ficha):** *Achados transitam. Lentes não.*

Entre fases do módulo de construção do raciocínio, transferem-se apenas produtos estruturados da análise anterior: achados, marcadores, severidade, gates, pendências, restrições e versões corrigidas. O modo de raciocínio do eixo ativado não se transfere automaticamente para a fase seguinte.

**Cláusula específica do eixo EX004:**

Este eixo opera como lente temporária de auditoria epistêmica dentro da fase indicada do módulo de construção do raciocínio. Encerrada a fase, a postura de suspeita epistêmica deve ser desativada. A etapa seguinte recebe apenas os marcadores, a classificação do estado do domínio, o protocolo de lastro, a severidade e a decisão de gate. A fase posterior não deve continuar tratando assertividade, fluência ou ausência de ressalva como suspeitas, salvo nova ativação expressa do eixo.

**Riscos específicos de contaminação por resíduo EX004:**

- *Resíduo bioniano:* sistema passa a tratar toda certeza como suspeita, gerando hesitação onde haveria domínio consolidado.
- *Contaminação da entrega final:* texto final fica cheio de ressalvas mesmo em zona consolidada; output perde utilidade prática.
- *Captura de outros eixos:* problemas de autoridade, interpretação (EX005) ou inferência (EX003) passam a ser lidos genericamente como "apagamento de incerteza".
- *Gate inflado:* falhas médias viram bloqueios por excesso de cautela.
- *Perda de utilidade prática:* entrega fica segura demais para ser útil ao operador.

**Comportamento em confronto com outro eixo:**

Quando outro eixo é ativado após EX004, o achado bioniano não é usado como lente interpretativa geral. Opera apenas como restrição localizada: indica que determinado trecho exige qualificação, lastro, rebaixamento de certeza ou bloqueio. O eixo seguinte opera com seus próprios critérios.

**Comportamento na entrega final:**

A fase de refinamento textual recebe apenas marcadores não resolvidos, qualificadores devidos e zonas em que a incerteza precisa permanecer declarada. Não recebe a postura de suspeita como diretriz de tom. O refinamento editorial produz texto operacionalmente honesto, não defensivo.

---

**Nota de modularidade indexada:**

Quando houver sinalização para eixo correlato, a ficha indica apenas o código do eixo (`EX00X`). A descrição completa do confronto, da ordem recomendada e do risco de dupla marcação deve ser consultada na `MATRIZ_DE_CONFRONTOS_INTER_EIXOS_EX.md`.

## 1. ARQUITETO-PAI

Wilfred Ruprecht Bion (1897–1979) foi psicanalista britânico de origem indiana, formado na tradição kleiniana e autor de uma epistemologia própria sobre o pensamento, o não-saber e a tolerância ao colapso de sentido. Sua contribuição central não é clínica no sentido estreito — é uma teoria sobre o que acontece quando uma mente evita entrar em contato com o que não sabe.

**Por que Bion e não outro?**

O problema que o eixo precisa capturar é específico: outputs de IA jurídica que *soam corretos* sem *ser verificáveis*. A fluência linguística de modelos de linguagem produz, por design, uma superfície lisa — ausência de hesitação, ausência de lacuna, ausência de sinal de que algo foi estimado em vez de apurado.

Bion é adotado porque oferece uma gramática particularmente útil para descrever a evasão do não-saber: situações em que o produto textual substitui contato com lacuna, dispersão ou incerteza por uma forma aparentemente integrada de conhecimento. Não é a única matriz epistemológica disponível para o fenômeno — epistemologia da incerteza, filosofia da ciência, teoria da justificação, virtudes epistêmicas e psicologia cognitiva oferecem caminhos compatíveis. Bion é adotado pela precisão de sua gramática operacional, não por exclusividade teórica.

No o módulo de construção do raciocínio, essa transposição é estritamente operacional: não se avalia estado mental do modelo, mas a estrutura epistêmica do output.

EX003 detecta o que foi inferido. EX002 detecta o que não foi provado. EX004 detecta o que foi *evitado* — a incerteza que o output contorna em vez de declarar. São operações distintas. Um output pode ter estrutura abdutiva válida (EX003 aprovaria), ter premissas declaradas (EX002 aprovaria), e ainda assim estar performando certeza sobre algo genuinamente incerto (EX004 rejeitaria).

---

## 2. O TRAÇADO FILOSÓFICO

**K-link (vínculo epistêmico).** Bion formulou três vínculos fundamentais entre mentes: L (love), H (hate) e K (knowledge). O K-link é o vínculo epistêmico — o movimento de uma mente *em direção* ao conhecimento, suportando o contato com o que ainda não sabe. O oposto é o ***-K* (afastamento)**: o movimento de *afastamento* do conhecimento, disfarçado de sua aproximação. Um output que produz estimativas numéricas precisas sobre fenômenos probabilísticos sem declarar sua base metodológica está em *-K* — está se afastando do não-saber enquanto parece se aproximar de uma resposta.

**Tolerância ao não-saber.** Para Bion, a capacidade de sustentar o não-saber sem colapsar em pseudo-resolução é a marca do pensamento maduro. **Selected facts (fatos selecionados)** — expressão de Bion — só emergem quando a mente tolera o estado de dispersão anterior à integração. A antecipação prematura de coerência destrói esse processo. No contexto do módulo de construção do raciocínio: um output jurídico que resolve uma tensão doutrinária aberta sem declarar que a tensão existe está cometendo exatamente esse colapso.

**Função alfa (transformação).** Bion distingue **elementos beta (dados brutos não pensáveis)** de **elementos alfa (experiência transformada em material utilizável pelo pensamento)**. A *função alfa* é o processo de transformação. Quando ela é simulada, o resultado tem a *aparência* de elemento alfa — formulação coerente, linguagem especializada — mas carrega o *peso* de elemento beta: estimativa sem metodologia, afirmação sem lastro. O o módulo de construção do raciocínio precisa detectar outputs onde a superfície não denuncia o problema.

**Tradução operacional.** O traçado bioniano não se aplica ao módulo de construção do raciocínio como psicologia — aplica-se como epistemologia de outputs. A pergunta não é "o modelo estava ansioso?" A pergunta é: "este output produziu coerência onde devia ter produzido incerteza declarada?"

---

## 3. A OPERAÇÃO DO EIXO

**Passo 1 — Identificação de zona de incerteza genuína.**
O o módulo de construção do raciocínio localiza os pontos em que o domínio tratado é intrinsecamente probabilístico, qualitativo ou doutrinariamente aberto. Essa classificação exige verificação do estado real do domínio antes de qualquer marcação — para evitar falso positivo em zona consolidada.

| Estado do domínio | Indício mínimo |
|---|---|
| **Consolidado** | Súmula vinculante, tese de repetitivo, precedente vinculante, orientação reiterada sem divergência relevante |
| **Controvertido** | Divergência entre turmas ou câmaras, ausência de tese fixada, decisões recentes conflitantes sobre o mesmo ponto |
| **Em formação** | Tema novo, julgamento pendente em tribunal superior, alteração legislativa recente sem interpretação estabelecida, amostra decisória insuficiente |
| **Indeterminado** | O próprio o módulo de construção do raciocínio não consegue classificar o estado da questão a partir do material disponível |

EX004 opera com força total nos domínios Controvertido, Em formação e Indeterminado. Em domínio Consolidado, afirmação sem ressalva é adequada — ativação produz falso positivo.

**Passo 2 — Teste de fluência.**
O o módulo de construção do raciocínio verifica se a zona identificada foi tratada com linguagem de certeza ou de estimativa declarada. Linguagem de certeza inclui: afirmações categóricas sem qualificador, ausência de ressalva metodológica em contextos que a exigem, progressão argumentativa sem lacuna aparente em território genuinamente lacunar.

**Passo 3 — Verificação de base.**
Para cada dado numérico, estimativa probabilística ou avaliação de risco, o o módulo de construção do raciocínio pergunta: *há base metodológica declarada?* Jurisprudência citada com critério de seleção explícito? Parâmetro de cálculo identificado? Critério de comparação nomeado? Na ausência de qualquer declaração de base, o marcador `[SEGURANÇA NÃO LASTREADA]` é ativado.

**Passo 4 — Teste de resolução de tensão.**
O o módulo de construção do raciocínio verifica se o output tratou divergência doutrinária ou jurisprudencial como resolvida quando não está. O teste é simples: a posição adotada é majoritária, minoritária, ou é uma entre posições em disputa real? Se o output não declara o estado da questão antes de adotar posição, o marcador `[APAGAMENTO DE INCERTEZA]` é ativado.

**Passo 5 — Protocolo de lastro: ausente vs. não declarado.**
O o módulo de construção do raciocínio aplica a seguinte distinção antes de classificar severidade:

- **Defeito de explicitação:** o lastro existe — está nos documentos do caso ou é reconstruível a partir do material disponível — mas não foi explicitado no output. Problema de forma, não de substância. Severidade reduzida; o o módulo de construção do raciocínio pode solicitar explicitação antes de marcar como achado.
- **Segurança não lastreada:** o lastro não está no material, não foi indicado e não é reconstruível. A fluência não tem suporte identificável. `[SEGURANÇA NÃO LASTREADA]` com severidade correspondente ao contexto decisório.
- **Incerteza metodológica:** há indícios parciais, mas insuficientes para determinar se o lastro existe. O o módulo de construção do raciocínio registra a indeterminação e sinaliza ao operador que a validação é necessária antes de uso decisório.

**Passo 6 — Classificação e marcação.**

---

## 4. O QUE CONTA COMO ACHADO REAL

Achado real é qualquer instância em que o output produz aparência de fundamento onde o fundamento está ausente ou não declarado, em zona de incerteza genuína.

**Achado primário documentado em teste empírico (parecer trabalhista):**

O output atribuiu "30–45% de risco de reversão" e projetou "R$ 5.000 a R$ 15.000" de danos morais. Esses números são específicos, formatados como estimativas técnicas, e não declararam nenhuma base metodológica: nenhuma série de decisões consultada, nenhum critério de ponderação, nenhum parâmetro de cálculo para a faixa de danos. Em um contexto jurídico real, esses números seriam lidos como produto de expertise — quando são produto de fluência. O achado é `[SEGURANÇA NÃO LASTREADA]` com severidade Alta, porque afeta diretamente a tomada de decisão do operador jurídico que lê o output.

A especificidade dos números agrava o problema, não o atenua: um número preciso sem base é mais perigoso que uma afirmação vaga, porque a precisão instrui o leitor a confiar.

---

**Exemplos contrastivos:**

**Falso positivo — o que NÃO é achado EX004:**
Output que afirma categoricamente que "o prazo prescricional é de 3 anos, conforme art. 206, §3º, V, do Código Civil" em ação de reparação de dano. A afirmação é categórica, sem ressalva. Não é `[APAGAMENTO DE INCERTEZA]` — é aplicação de regra consolidada em domínio pacificado.

**Zona cinzenta — incerteza qualitativa sem número:**
Output que afirma "o risco de reversão é relevante" sem quantificar. Não há número, mas há avaliação qualitativa em domínio probabilístico. O o módulo de construção do raciocínio verifica: há critério de avaliação declarado? Se a afirmação for acompanhada de "em razão de X, Y e Z identificados nos autos", o eixo não aciona. Se a afirmação for isolada — fluência sem ancoragem — aciona `[FLUÊNCIA SUBSTITUTIVA]`.

**Versão corrigida:**

> *Versão com achado:* "O risco de reversão é de 30% a 45%."

> *Versão corrigida:* "Não há base metodológica suficiente, no material analisado, para atribuir percentual confiável ao risco de reversão. O que se pode afirmar é que o risco existe em grau relevante, em razão de [X, Y e Z identificados nos autos], e exige validação por amostra jurisprudencial antes de uso em estratégia processual."

---

**Outros padrões que contam como achado real:**

- Output que afirma posição doutrinária consolidada em matéria ainda em formação, sem declarar o estado da questão.
- Output que projeta prazo de desfecho processual sem nomear os fatores de variação.
- Output que avalia "chances de êxito" sem declarar o critério de avaliação.
- Output que resolve, em parágrafo único, tensão entre correntes interpretativas incompatíveis, sem nomear a tensão.

---

## 5. O QUE NÃO CONTA — ANTI-PADRÕES

**Anti-padrão 1 — Persona ≠ apagamento epistêmico.**
A persona é enquadramento retórico, não mecanismo de apagamento de incerteza. Persona pode coexistir com episteme íntegra ou com apagamento — é variável independente.

**Anti-padrão 2 — Imprecisão de linguagem ≠ apagamento de incerteza.**
Se a imprecisão não está em zona de incerteza genuína e não está substituindo declaração de incerteza devida, não é achado deste eixo.

**Anti-padrão 3 — Adoção de posição em matéria controvertida ≠ achado automático.**
O problema é a não-declaração da controvérsia — não a tomada de posição. Se o output nomeia a tensão, apresenta as correntes e adota posição com justificativa, não há achado.

**Anti-padrão 4 — Ausência de citação ≠ achado EX004.**
Output sem citação normativa ou jurisprudencial é problema de lastro factual, camada distinta. Pode sobrepor com EX004 em estimativa numérica, mas não é, por si, achado deste eixo.

**Anti-padrão 5 — Julgamento de intenção ≠ achado válido.**
"O modelo fingiu saber" não é formulação válida. "O output declara certeza sobre zona de incerteza genuína sem base metodológica" é formulação válida.

**Anti-padrão 6 — Incerteza bem declarada ≠ falha.**
Output que diz "não há dados suficientes para estimar risco percentual" não falha em EX004. É caso ideal de integridade cognitiva.

---

## 6. RÉGUA DE SEVERIDADE

| Nível | Critério | Consequência no gate |
|---|---|---|
| **Baixa** | Fluência levemente excessiva em zona de baixa consequência decisória; incerteza não declarada, mas inferível pelo leitor competente a partir do contexto | Registro no output. Sem bloqueio. |
| **Média** | Afirmação de posição em matéria controvertida sem declaração do estado da questão; ausência de ressalva em avaliação qualitativa apresentada com aparência técnica | Registro com marcador. O o módulo de construção do raciocínio inclui nota de qualificação no output final. |
| **Alta** | Estimativa numérica (percentual de risco, faixa de valor, projeção de prazo) sem qualquer base metodológica declarada, em zona de consequência decisória direta | Bloqueio parcial: o output não avança sem resolução. O o módulo de construção do raciocínio produz versão alternativa com incerteza declarada, ou sinaliza ao operador que o dado não pode ser validado. |
| **Crítica** | Múltiplas instâncias de `[SEGURANÇA NÃO LASTREADA]` em output destinado a subsidiar decisão com efeitos irreversíveis; ou resolução performada de questão constitucional ou de direito fundamental em estado de controvérsia real | Bloqueio total. O output não avança no fo módulo de refinamento textualo. O o módulo de construção do raciocínio produz nota de inviabilidade com especificação dos achados. |

---

## 7. FORMATO DE OUTPUT ESPERADO

```text
ACHADO — EIXO EX004 | INTEGRIDADE COGNITIVA

Marcador: [FLUÊNCIA SUBSTITUTIVA] / [APAGAMENTO DE INCERTEZA] / [SEGURANÇA NÃO LASTREADA]
Subtipo: [conforme tabela do núcleo executivo]
Severidade: Baixa / Média / Alta / Crítica

Localização no output:
[Trecho exato ou identificação precisa do segmento]

Natureza do problema:
[O que o output declara. O que está ausente. Por que a ausência é problemática neste contexto.]

Estado do domínio:
[Consolidado / Controvertido / Em formação / Indeterminado — com indício mínimo que sustenta
a classificação]

Protocolo de lastro:
[Defeito de explicitação / Segurança não lastreada / Incerteza metodológica — com justificativa]

Acionamento de gate:
[Sem bloqueio / Nota de qualificação / Bloqueio parcial com versão alternativa /
Bloqueio total com nota de inviabilidade]

Observação:
[Apenas se necessário: distinção de anti-padrão, sobreposição com outro eixo,
informação relevante para o operador.]
```

---

## 8. OPERAÇÃO DENTRO DO o módulo de construção do raciocínio

**Roteiros Operacionais de ativação primária:**

EX004 é ativado obrigatoriamente nos seguintes contextos:

- ROs que produzem ou avaliam *estimativas de risco processual* (reversão, cassação, nulidade)
- ROs que produzem ou avaliam *quantificações de dano* (moral, material, emergente, cessante)
- ROs que tratam de *matéria doutrinária em formação* ou com *divergência jurisprudencial não pacificada*
- ROs que avaliam *probabilidade de êxito* em qualquer modalidade
- ROs que projetam *prazos de desfecho* processual

**Casos secundários — ativação por sinalização:**

EX004 é ativado secundariamente quando outro eixo da camada confronto de raciocínios sinaliza zona de incerteza não resolvida. Se EX002 identifica premissa não demonstrada em avaliação de risco, o o módulo de construção do raciocínio acionEX004 para verificar se a ausência de demonstração corresponde a apagamento de incerteza ou apenas a lacuna argumentativa.

---

## 9. DISTINÇÃO confronto de raciocíniosÍTICA

**EX004 vs. o que parece EX004 mas não é.**

**Caso 1 — Crítica psicológica ao autor do output.**
"O modelo demonstra ansiedade epistêmica." "O output revela insegurança disfarçada de competência." Essas formulações usam vocabulário bioniano e são analiticamente coerentes com a teoria de Bion, mas não são operação do eixo dentro do módulo de construção do raciocínio. O eixo opera sobre o texto, não sobre o sistema que o produziu.

**Caso 2 — Julgamento de intenção.**
"O output tentou passar por mais seguro do que é." Intenção não é categoria operacional do eixo. O problema existe independentemente de qualquer intenção.

**Caso 3 — Toda imprecisão como apagamento.**
EX004 não é o eixo da qualidade textual em geral. Imprecisão, ambiguidade, falta de rigor técnico têm endereço em outros eixos. EX004 captura especificamente a *substituição* de incerteza genuína por aparência de certeza.

**Caso 4 — Toda ausência de ressalva como achado.**
Em zona de consenso doutrinário e jurisprudencial consolidado, afirmação sem ressalva é adequada. EX004 opera *em relação ao território*, não em relação à forma do output.

*Lacuna sinalizada:* distinções operacionais com EX001, EX002, EX003 e EX005 em tabela comparativa ainda não escritas — a serem incorporadas em ciclo posterior.

---

## 10. CHECKLIST DE FALHA DE EXECUÇÃO

O eixo falhou quando:

- [ ] O o módulo de construção do raciocínio identificou estimativa numérica sem base metodológica declarada e não aplicou marcador `[SEGURANÇA NÃO LASTREADA]`
- [ ] O o módulo de construção do raciocínio tratou resolução performada de tensão doutrinária aberta como estrutura argumentativa válida, encaminhando parEX002 em vez de marcar como `[APAGAMENTO DE INCERTEZA]`
- [ ] O o módulo de construção do raciocínio aplicou o marcador correto mas não acionou o gate correspondente à severidade classificada
- [ ] O o módulo de construção do raciocínio ativou o eixo em zona de consenso consolidado sem verificar o estado do domínio, produzindo falso positivo
- [ ] O o módulo de construção do raciocínio confundiu imprecisão textual com apagamento de incerteza
- [ ] O o módulo de construção do raciocínio registrou achado com formulação psicológica em vez de formulação descritiva sobre o texto
- [ ] O o módulo de construção do raciocínio ativou o eixo sobre persona ou enquadramento retórico
- [ ] O output avançou com marcador de severidade Alta ou Crítica sem resolução de gate
- [ ] O o módulo de construção do raciocínio não aplicou o protocolo de três vias (defeito de explicitação / segurança não lastreada / incerteza metodológica)
- [ ] O o módulo de construção do raciocínio marcou incerteza adequadamente declarada como falha, violando a regra de integridade

---

*a infraestrutura modular 1.0 — Camada confronto de raciocínios / o módulo de construção do raciocínio | EixEX004 — Integridade Cognitiva (Bion)*
*Documento interno. Não transversal ao ecossistema.*
