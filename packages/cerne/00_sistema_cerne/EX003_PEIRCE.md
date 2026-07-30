# FICHA INSTRUCIONAL — EIXO EX003 ABDUTIVO

**Código:** EX003
**Nome do método:** Abdutivo
**Arquiteto-pai:** Charles Sanders Peirce

---

## 0. NÚCLEO EXECUTIVO

*Bloco imperativo — colável diretamente no Roteiro Operacional do módulo de construção do raciocínio.*

---

**EIXO EX003 — ABDUTIVO**

**Pergunta operacional:**
> Que hipótese este output apresentou como conclusão necessária, verificada ou juridicamente estabilizada? Qual salto inferencial não foi declarado como passo?

**Sequência operacional:**

1. Identificar conclusões jurídicas sobre qualificação de fatos, configuração de hipótese legal, validade, nulidade ou presença/ausência de elemento legal.
2. Classificar o tipo de inferência em operação: dedução operacional, indução, abdução ou indeterminado.
3. Comparar a força com que a conclusão é apresentada com a força que o tipo inferencial autoriza.
4. Em casos abdutivos, mapear hipóteses concorrentes plausíveis sustentadas pelos fatos do caso.
5. Aplicar régua de plausibilidade antes de acionar `[ABDUÇÕES NÃO HIERARQUIZADAS]`.
6. Aplicar marcador, classificar severidade, registrar no formato padrão.

**Testes binários de entrada:**

| Critério | Entra? |
|---|---|
| O output produz qualificação jurídica de fato (vínculo, ilicitude, responsabilidade)? | Se sim → entra |
| O output afirma validade ou nulidade de ato, contrato ou cláusula? | Se sim → entra |
| O output conclui presença ou ausência de elemento legal a partir de descrição factual? | Se sim → entra |
| O output interpreta cláusula ou dispositivo aplicado a caso concreto? | Se sim → entra |
| O problema é estimativa quantitativa sem base metodológica? | Se sim → não entra (domínio de EX004) |
| O problema é premissa não demonstrada? | Se sim → não entra (domínio de EX002) |
| O problema é lastro factual incorreto? | Se sim → não entra |

**Marcadores canônicos:**

| Marcador | Status | Uso |
|---|---|---|
| `[HIPÓTESE COMO CONCLUSÃO]` | core | Conclusão central abdutiva apresentada como verificada |
| `[SALTO INFERENCIAL]` | core | Passo inferencial não declarado entre dado e conclusão |
| `[ABDUÇÕES NÃO HIERARQUIZADAS]` | core | Hipóteses concorrentes plausíveis e sustentadas pelos fatos não consideradas |

**Regras de não-acionamento:**

- Se a conclusão é dedução operacional válida (regra estabilizada + fatos demonstrados + ausência de hipótese concorrente relevante), então não marca `[HIPÓTESE COMO CONCLUSÃO]`.
- Se o problema é factual e não inferencial, então não marca; encaminhar para verificação de lastro.
- Se hipóteses alternativas foram consideradas e descartadas com justificativa, então não marca `[ABDUÇÕES NÃO HIERARQUIZADAS]`.
- Se a hipótese concorrente é meramente concebível em abstrato sem suporte nos fatos, então não marca `[ABDUÇÕES NÃO HIERARQUIZADAS]`.
- Se a ausência é de motivação, então não marca; sinalizar EX002.
- Se a incerteza é quantitativa sem base, então não marca; sinalizar EX004.

**Regra de integridade do eixo:**

> A abdução não é raciocínio inferior; é hipótese explicativa ainda não confirmada. O defeito não está em abduzir; está em apresentar a hipótese como conclusão verificada.

**Ponto cego declarado:**

O eixo não detecta apagamento de incerteza em estimativas quantitativas (domínio de EX004), nem falha de demonstração de premissas (domínio de EX002), nem ausência de elementos da estrutura argumentativa (domínio de EX001), nem deslocamento de horizonte interpretativo (domínio de EX005). Opera exclusivamente sobre o tipo de inferência e sua representação epistêmica.

---

## 0.1 PROMPTS OPERACIONAIS CANÔNICOS

**Termos de ativação interna sugeridos:**

- Principal: "Peirce" (uso restrito ao projeto); "abdução" (uso público); "qualificação jurídica do fato"
- Compostos discriminantes: "hipótese como conclusão", "salto inferencial não declarado", "tipo de inferência", "abduções não hierarquizadas", "representação epistêmica da inferência"
- Vetados isoladamente: "inferência", "hipótese", "conclusão", "interpretação", "raciocínio" (comuns demais)

**Tabela de lacunas de cobertura:**

| Objeto | Código | Status | Prompt canônico |
|---|---|---|---|
| Peça processual | EX003-PEC | Pendente | — |
| Cláusula contratual | EX003-CON | Pendente | — |
| Parecer jurídico | EX003-PAR | Pendente | — |
| Nota técnica | EX003-NOT | Pendente | — |
| Output de IA jurídica externa | EX003-OUT | Pendente | — |
| Decisão judicial | EX003-DEC | Pendente | — |

---

## 0.2 CLÁUSULA DE ATIVAÇÃO, CONTENÇÃO E DESCARTE

**Regra-mãe (acima da ficha):**

> Achados transitam. Lentes não.
>
> Entre fases do módulo de construção do raciocínio, transferem-se apenas produtos estruturados da análise anterior: achados, marcadores, severidade, gates, pendências, restrições e versões corrigidas. O modo de raciocínio do eixo ativado não se transfere automaticamente para a fase seguinte.

**Cláusula específica do eixo EX003:**

Ao fim da fase em que o eixo Peirce foi ativado, desativa-se o modo abdutivo de leitura. Não permanece em fases subsequentes a tendência de reclassificar inferências, mapear hipóteses concorrentes ou exigir declaração do tipo inferencial. Permanecem como produtos exportáveis: marcadores aplicados, severidade registrada, hipóteses concorrentes identificadas, versão corrigida com qualificadores de plausibilidade preservados e pendências de verificação.

**Riscos específicos de contaminação por resíduo EX003:**

- Tendência a reclassificar como abdutivas conclusões que já foram estabilizadas em fase anterior como dedução operacional válida.
- Tendência a multiplicar hipóteses concorrentes em fases posteriores, gerando ruído sobre conclusões já calibradas.
- Tendência a exigir qualificadores de plausibilidade onde a régua do eixo não acionaria achado.
- Tendência a sobrepor leitura abdutiva em zonas que pertencem a outros eixos (EX002 socrático, EX004 cognitivo, EX001 argumentativo).

**Comportamento em confronto com outro eixo:**

Quando pareado, o eixo Peirce não absorve achados de outros eixos. Não converte premissa não demonstrada (EX002) em salto inferencial. Não converte estimativa sem base (EX004) em abdução. Apenas opera sobre a relação entre tipo de inferência declarada e força com que a conclusão é apresentada.

**Comportamento na entrega final:**

À fase de refinamento textual transmitem-se apenas marcadores não resolvidos e qualificadores de plausibilidade ("plausível", "provável", "hipótese", "depende de verificação", "não descartada hipótese concorrente"). Não transmite-se postura cognitiva abdutiva nem instrução de reabertura de tipo inferencial.

---

**Nota de modularidade indexada:**

Quando houver sinalização para eixo correlato, a ficha indica apenas o código do eixo (`EX00X`). A descrição completa do confronto, da ordem recomendada e do risco de dupla marcação deve ser consultada na `MATRIZ_DE_CONFRONTOS_INTER_EIXOS_EX.md`.

## 1. ARQUITETO-PAI

Charles Sanders Peirce (1839–1914), matemático, lógico e filósofo norte-americano, formulou a tríade inferencial — dedução, indução e abdução — e identificou a abdução como o único modo de raciocínio capaz de gerar hipóteses genuínas. A abdução não é raciocínio inferior; é a operação que introduz uma hipótese explicativa capaz de dar conta dos fatos observados. Sua limitação está em não confirmar, sozinha, a conclusão que propõe.

**Por que Peirce e não outro?**

O problema que o eixo precisa capturar é específico: outputs de IA jurídica que chegam a conclusões por abdução — o caminho mais plausível dado o contexto — e as apresentam com força de dedução — como se a conclusão se seguisse necessariamente dos fatos. O leitor jurídico lê "o contrato é nulo" quando a estrutura real da afirmação é "dado o que observo, a hipótese mais plausível é que o contrato seja nulo, mas há outras hipóteses que não foram eliminadas".

Peirce é uma matriz útil para esse problema porque distinguiu os três tipos de inferência com precisão técnica e identificou a abdução especificamente como inferência criativa mas falível. Outros caminhos seriam compatíveis (lógica do não-monotônico, teoria da inferência ampliativa), mas a tríade peirceana oferece a linguagem mais econômica para o o módulo de construção do raciocínio.

A diferença em relação aos demais eixos é precisa: EX004 pergunta se a incerteza foi evitada. EX002 pergunta se a cadeia argumentativa está demonstrada. Peirce pergunta se o *tipo de inferência* que gerou a conclusão está sendo representado com o grau de força epistêmica correto. Um output pode declarar incerteza, ter premissas estabelecidas, e ainda assim apresentar uma abdução como dedução.

---

## 2. O TRAÇADO FILOSÓFICO

**A tríade inferencial.** Peirce distinguiu três formas de raciocínio com estrutura e força epistêmica diferentes:

- **Dedução** (inferência necessária): parte de uma lei geral e de um caso, e deriva um resultado necessário. "Todos os contratos com vício de consentimento são anuláveis. Este contrato tem vício de consentimento demonstrado. Portanto, este contrato é anulável."
- **Indução** (inferência ampliativa): parte de casos observados e deriva uma regra geral provável. A força é tão boa quanto a amostra que a suporta.
- **Abdução** (inferência hipotética): parte de um resultado e de uma lei geral, e infere o caso mais plausível. "Este contrato apresenta os elementos Z. Se houvesse vício de consentimento, Z seria esperado. Portanto, é plausível que haja vício de consentimento." A hipótese explica os fatos, mas outras hipóteses podem explicá-los igualmente ou melhor.

**A abdução como hipótese.** Em Peirce, a investigação completa exige que a hipótese abdutiva seja seguida pela dedução de consequências verificáveis e por procedimentos indutivos ou probatórios de teste. A abdução, sozinha, formula a hipótese capaz de explicar os fatos — não demonstra, por si, que a hipótese é verdadeira.

**O problema jurídico específico.** A qualificação jurídica de fatos é, na maioria dos casos, uma operação abdutiva. O problema ocorre quando a abdução é apresentada com força dedutiva: a qualificação não é declarada como interpretação mais plausível, mas como derivação necessária dos fatos.

**Tradução operacional.** O traçado peirceano aplica-se ao módulo de construção do raciocínio como mapa de verificação do tipo de inferência em operação. A pergunta não é "o output está errado?" — é "o output declara o tipo de inferência que gerou esta conclusão, e a força com que a apresenta corresponde a esse tipo?"

---

## 3. A OPERAÇÃO DO EIXO

O o módulo de construção do raciocínio raciocina sob o eixo Peirce na seguinte sequência:

**Passo 1 — Identificação de conclusões jurídicas.**
O o módulo de construção do raciocínio localiza no output afirmações conclusivas sobre: qualificação jurídica de fatos (configuração de vínculo, responsabilidade, ilicitude); validade ou nulidade de atos; presença ou ausência de elemento legal; interpretação de cláusula ou dispositivo aplicada ao caso concreto.

**Passo 2 — Mapeamento do tipo de inferência.**
Para cada conclusão identificada, o o módulo de construção do raciocínio classifica o tipo de inferência que a sustenta:

| Tipo | Estrutura presente no output | Força declarável |
|---|---|---|
| **Dedução operacional** | Regra estabilizada + caso demonstrado + ausência de hipóteses concorrentes relevantes no contexto | Necessária dentro do contexto analisado |
| **Indução** | Amostra de casos documentada → regra | Provável — limitada pela representatividade da amostra |
| **Abdução** | Fato + hipótese explicativa → candidato plausível | Candidatura — outras hipóteses não foram eliminadas |
| **Indeterminado** | Não é possível identificar a estrutura inferencial | Registrar como `[SALTO INFERENCIAL]` para verificação |

> **Nota sobre dedução operacional.** No Direito, não existe dedução lógica pura — toda aplicação envolve alguma mediação interpretativa. "Dedução operacional" não pressupõe ausência absoluta de interpretação; significa aplicação de regra suficientemente estabilizada a fatos suficientemente demonstrados, sem hipóteses concorrentes relevantes no contexto analisado. A conclusão categórica é legítima quando: a norma é clara e pacificada, os fatos estão demonstrados, e não há hipótese alternativa juridicamente plausível e sustentada pelos fatos do caso. A dedução operacional só pode ser reconhecida depois da estabilização mínima da fonte, dos fatos e do conceito aplicado.

**Passo 3 — Teste de representação epistêmica.**
O o módulo de construção do raciocínio verifica se a força com que a conclusão é apresentada corresponde ao tipo de inferência que a gerou. Abdução apresentada com força dedutiva (afirmação categórica sem qualificação de plausibilidade) aciona `[HIPÓTESE COMO CONCLUSÃO]`.

**Passo 4 — Teste de abduções competidoras.**
Em casos de abdução, o o módulo de construção do raciocínio verifica se existem hipóteses alternativas plausíveis que explicam os mesmos fatos. A verificação é sobre o material disponível, não sobre todas as hipóteses concebivelmente possíveis. O grau de exigência segue a seguinte régua:

| Grau da hipótese concorrente | Tratamento |
|---|---|
| **Meramente concebível** — possível em abstrato, sem suporte nos fatos do caso | Não exige enfrentamento |
| **Juridicamente plausível, mas fraca** — existe no ordenamento, mas os fatos do caso não a sustentam com força | Pode ser mencionada se relevante; ausência não gera achado |
| **Plausível e sustentada por fatos do caso** — o material disponível suporta a hipótese alternativa com alguma força | Deve ser enfrentada; ausência de enfrentamento gera `[ABDUÇÕES NÃO HIERARQUIZADAS]` |
| **Igual ou superior à hipótese adotada** — a hipótese alternativa tem suporte igual ou maior nos fatos | Ausência de enfrentamento gera achado de severidade Alta ou Crítica |

**Passo 5 — Verificação de salto inferencial declarado.**
O o módulo de construção do raciocínio verifica se há passo inferencial não declarado entre dado observado e conclusão apresentada. Se o salto não está declarado e não é inferível pelo leitor sem análise especializada adicional, `[SALTO INFERENCIAL]` é ativado.

**Passo 6 — Classificação e marcação.**
O o módulo de construção do raciocínio aplica o marcador canônico, classifica a severidade e registra o achado no formato padrão.

---

## 4. O QUE CONTA COMO ACHADO REAL

Achado real é qualquer instância em que o output apresenta uma abdução com força epistêmica de dedução ou de conclusão verificada, em zona de qualificação jurídica com consequência decisória.

**Achado documentado — CT-002 (parecer trabalhista):**

O output concluiu pela configuração de vínculo empregatício a partir da descrição factual do caso, de forma categórica, sem declarar o caráter abdutivo da inferência e sem considerar hipóteses alternativas (trabalho autônomo com habitualidade, prestação de serviços com elementos fronteiriços). A qualificação como emprego é uma das abduções possíveis dado o conjunto de indícios — não é derivação necessária. O achado é `[HIPÓTESE COMO CONCLUSÃO]` com severidade Média.

---

**Exemplos contrastivos:**

**Falso positivo — o que NÃO é achado Peirce:**
Output que afirma "a cláusula de não-concorrência é nula por violação ao art. 122 do Código Civil, conforme orientação do STJ". A conclusão é forte e categórica — mas está estruturada como dedução operacional: lei explícita + enquadramento do caso + precedente estabilizado + ausência de hipótese concorrente relevante. O eixo Peirce não tem achado.

**Zona cinzenta — abdução com hipótese dominante justificada:**
Output que afirma "os elementos descritos configuram, com alta probabilidade, relação de consumo nos termos do CDC, principalmente em razão de X e Y; a hipótese de relação entre iguais existe mas é menos sustentável diante de Z". A conclusão é abdutiva, mas declara o caráter probabilístico, identifica as hipóteses competidoras e fundamenta a hierarquização. Não é achado — é abdução bem-representada.

**Versão corrigida — como transformar `[HIPÓTESE COMO CONCLUSÃO]` em output íntegro:**

> *Versão com achado:* "Os fatos descritos configuram vínculo empregatício."

> *Versão corrigida:* "Os fatos descritos são compatíveis com vínculo empregatício, sendo essa a qualificação mais plausível diante de [elementos X, Y e Z]. A hipótese de prestação de serviços autônoma com habitualidade não pode ser descartada sem análise dos documentos contratuais e da forma efetiva de execução. A conclusão final sobre a qualificação jurídica depende de verificação adicional."

---

**Outros padrões que contam como achado real:**

- Output que qualifica ato como ilícito a partir de descrição de fatos sem enunciar a norma de subsunção em operação.
- Output que conclui pela responsabilidade do fornecedor sem verificar hipóteses de excludente quando os fatos do caso as tornam plausíveis e sustentadas.
- Output que interpreta cláusula ambígua e adota uma das interpretações sem declarar que há interpretação concorrente com plausibilidade comparável e sustentada pelo texto.
- Output que conclui pela ausência de elemento legal sem examinar os fatos sob as hipóteses que poderiam configurá-lo.

---

## 5. O QUE NÃO CONTA — ANTI-PADRÕES

**Conclusão forte ≠ salto inferencial.**
Deduções operacionais válidas não são achados Peirce. A questão não é se a conclusão é afirmada com força — é se o tipo de inferência que a suporta justifica essa força.

**Imprecisão factual ≠ salto inferencial.**
Output que cita fatos incorretos tem problema de lastro factual — não de tipo inferencial. O salto de Peirce pressupõe que os fatos estão corretos; o problema é a relação entre fatos e conclusão.

**Ausência de motivação ≠ achado Peirce.**
Output que não justifica uma conclusão tem problema socrático (EX002). Peirce não trata de ausência de justificativa — trata do tipo inadequado de justificativa para a força da conclusão apresentada.

**Estimativa quantitativa sem base ≠ abdução não declarada.**
Estimativas de risco, percentuais e faixas de valor sem base metodológica são domínio cognitivo (EX004). Peirce opera sobre inferências qualitativas — qualificação jurídica, configuração de hipótese legal.

**Hipótese descartada com justificativa ≠ achado.**
Se o output considerou hipóteses alternativas e as descartou com justificativa, não há `[ABDUÇÕES NÃO HIERARQUIZADAS]`. O eixo exige que hipóteses concorrentes plausíveis e sustentadas pelos fatos *não tenham sido consideradas ou eliminadas* — não exige que toda hipótese concebível seja examinada.

**Julgamento sobre raciocínio interno do modelo ≠ achado.**
O eixo opera sobre a estrutura inferencial declarada no output. "O modelo raciocinou abdutivamente" não é formulação válida. "O output apresenta conclusão sobre qualificação jurídica sem declarar o caráter abdutivo da inferência e sem considerar hipóteses concorrentes plausíveis e sustentadas" é formulação válida.

---

## 6. RÉGUA DE SEVERIDADE

| Nível | Critério | Consequência no gate |
|---|---|---|
| **Baixa** | Abdução não declarada em ponto acessório; hipótese adotada claramente dominante; hipóteses concorrentes meramente concebíveis ou juridicamente plausíveis mas fracas | Registro no output. Sem bloqueio. Qualificador de plausibilidade preservado na entrega final. |
| **Média** | Conclusão central baseada em abdução apresentada como dedução; hipóteses alternativas plausíveis e com algum suporte nos fatos existem e não foram consideradas; o salto não compromete a orientação geral mas afeta a estratégia de verificação | Registro com marcador. Nota sobre o caráter abdutivo da conclusão e as hipóteses não examinadas. |
| **Alta** | Conclusão com efeito decisório direto apresentada como dedução quando é abdução; hipóteses alternativas sustentadas pelos fatos com plausibilidade comparável não foram consideradas ou eliminadas | Bloqueio parcial: o output não avança sem resolução. Produz-se versão com representação epistêmica corrigida, ou sinaliza-se que a conclusão exige verificação adicional antes de uso. |
| **Crítica** | Múltiplas conclusões decisórias baseadas em abduções apresentadas como deduções; hipóteses suprimidas têm plausibilidade igual ou superior à adotada; a estrutura do output impossibilita que o operador identifique o caráter inferencial das conclusões | Bloqueio total. Produz-se nota de inviabilidade com mapeamento das inferências não declaradas. |

---

## 7. FORMATO DE OUTPUT ESPERADO

```text
ACHADO — EIXO EX003 PEIRCE | ABDUTIVO

Marcador: [HIPÓTESE COMO CONCLUSÃO] / [SALTO INFERENCIAL] / [ABDUÇÕES NÃO HIERARQUIZADAS]
Severidade: Baixa / Média / Alta / Crítica

Localização no output:
[Trecho exato ou identificação precisa do segmento]

Tipo de inferência identificado:
[Dedução operacional / Indução / Abdução / Indeterminado — com justificativa da classificação]

Natureza do problema:
[O que o output conclui. Qual o tipo real de inferência em operação. Por que a força de
apresentação não corresponde ao tipo inferencial.]

Hipóteses concorrentes não examinadas:
[Apenas para [ABDUÇÕES NÃO HIERARQUIZADAS]: quais hipóteses têm plausibilidade comparável
e suporte nos fatos do caso, e não foram consideradas ou eliminadas. Classificar o grau
conforme a régua do Passo 4.]

Acionamento de gate:
[Sem bloqueio / Nota de representação epistêmica / Bloqueio parcial com versão corrigida /
Bloqueio total com nota de inviabilidade]

Observação:
[Apenas se necessário: distinção de anti-padrão, sobreposição com outro eixo,
informação relevante para o operador.]
```

---

## 8. OPERAÇÃO DENTRO DO o módulo de construção do raciocínio

**Ativação primária:**

- Fases que produzem ou avaliam qualificação jurídica de fatos
- Fases que concluem sobre responsabilidade (contratual, extracontratual, tributária, trabalhista, consumerista)
- Fases que avaliam validade ou nulidade de atos, contratos ou cláusulas
- Fases que identificam presença ou ausência de elementos legais a partir de descrição factual
- Fases que produzem interpretação de dispositivo ou cláusula aplicada ao caso concreto

**Ativação secundária por sinalização:**

O eixo Peirce é ativado secundariamente quande EX004 sinaliza apagamento de incerteza em conclusão sobre configuração de hipótese legal — o o módulo de construção do raciocínio verifica se o apagamento corresponde a abdução disfarçada de dedução ou a incerteza quantitativa sem base. São achados distintos que podem coexistir.

O eixo Peirce é ativado secundariamente quande EX002 identifica premissa não demonstrada em zona de qualificação jurídica — o o módulo de construção do raciocínio verifica se a lacuna é de demonstração de premissa (socrático) ou de declaração do tipo inferencial (Peirce).

**Pares de confronto típicos:**

- Peirce × Sócrates (EX003 × EX002): zona em que conclusão abdutiva carece de premissas estabilizadas.
- Peirce × Bion (EX003 × EX004): zona em que a hipótese abdutiva foi apresentada com fluência substitutiva que apaga sua condição hipotética.

---

## 9. DISTINÇÕES confronto de raciocíniosÍTICAS

### 9.1. Abdução vs. EX002 (EX003 vs. EX002)

| | Peirce | Sócrates |
|---|---|---|
| Pergunta | A conclusão decorre necessariamente dos fatos ou é a hipótese mais plausível? | A premissa que sustenta a tese foi demonstrada? |
| Unidade de análise | Relação entre tipo inferencial e força de apresentação | Cadeia de demonstração das premissas |
| Defeito típico | Abdução apresentada como dedução | Premissa pressuposta como verdadeira |
| Risco de dupla marcação | Tratar ausência de motivação como salto inferencial | — |

### 9.2. Abdução vs. EX004 (EX003 vs. EX004)

| | Peirce | Bion |
|---|---|---|
| Pergunta | A inferência foi representada com o tipo correto? | A incerteza foi declarada? |
| Unidade de análise | Estrutura inferencial qualitativa | Estado epistêmico do output |
| Defeito típico | Hipótese como conclusão | Apagamento de incerteza, número performativo |
| Risco de dupla marcação | Tratar estimativa quantitativa sem base como abdução | — |

### 9.3. Abdução vs. EX001 (EX003 vs. EX001)

| | Peirce | Toulmin |
|---|---|---|
| Pergunta | O tipo de inferência foi representado adequadamente? | A estrutura claim/warrant/backing está completa? |
| Defeito típico | Hipótese disfarçada de derivação necessária | Componente argumentativo ausente |
| Foco | Força epistêmica da conclusão | Arquitetura do argumento |

### 9.4. Abdução vs. EX009 (EX003 vs. EX009) — *lacuna*

A distinção será fechada quando o conjunto de fichas estiver consolidado. Hipótese provisória: Peirce opera sobre o tipo da inferência; Hart opera sobre EX009 do conceito jurídico aplicado. Um output pode usar conceito aberto sem fechamento (achado Hart) e ainda assim apresentar a aplicação como derivação necessária (achado Peirce).

### 9.5. Abdução vs. EX005 (EX003 vs. EX005) — *lacuna*

Distinção provisória: Gadamer pergunta a partir de qual horizonte interpretativo o texto foi lido; Peirce pergunta se a conclusão derivada dessa leitura foi apresentada com força compatível com o tipo de inferência. Fechamento da distinção pendente.

---

## 10. CHECKLIST DE FALHA DE EXECUÇÃO

O eixo falhou quando:

- [ ] O o módulo de construção do raciocínio identificou conclusão sobre qualificação jurídica e não verificou o tipo de inferência que a sustenta
- [ ] O o módulo de construção do raciocínio tratou dedução operacional válida como salto inferencial sem verificar se regra, fato e ausência de hipótese concorrente relevante estavam estabelecidos
- [ ] O o módulo de construção do raciocínio confundiu ausência de motivação (EX002) com ausência de declaração do tipo inferencial (EX003)
- [ ] O o módulo de construção do raciocínio confundiu estimativa quantitativa sem base (EX004) com abdução não declarada (EX003)
- [ ] O o módulo de construção do raciocínio não aplicou a régua de plausibilidade antes de acionar `[ABDUÇÕES NÃO HIERARQUIZADAS]` — marcou hipótese meramente concebível como se fosse hipótese sustentada pelos fatos
- [ ] O o módulo de construção do raciocínio não verificou hipóteses abdutivas concorrentes em output sobre responsabilidade ou qualificação jurídica de fatos
- [ ] O o módulo de construção do raciocínio ativou `[ABDUÇÕES NÃO HIERARQUIZADAS]` quando as hipóteses alternativas haviam sido consideradas e descartadas com justificativa
- [ ] O o módulo de construção do raciocínio aplicou marcador Peirce onde o problema era de estrutura argumentativa (EX001), gerando dupla marcação indevida
- [ ] O output avançou à fase seguinte com marcador de severidade Alta ou Crítica sem resolução de gate
- [ ] O o módulo de construção do raciocínio registrou achado com avaliação de qualidade do raciocínio em vez de classificação do tipo inferencial e sua representação epistêmica
