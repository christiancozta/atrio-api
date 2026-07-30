# FICHA INSTRUCIONAL — EIXO EX005 HERMENÊUTICO (GADAMER)

**Código:** EX005
**Nome do método:** Hermenêutico
**Arquiteto-pai:** Hans-Georg Gadamer

---

## 0. NÚCLEO EXECUTIVO

*Bloco imperativo — colável diretamente no Roteiro Operacional do módulo de construção do raciocínio.*

---

**EIXO EX005 — HERMENÊUTICO**

**Identidade funcional:**
EX005 audita se o sentido jurídico atribuído a um texto foi produzido por leitura situada, consciente de seu horizonte, ou por antecipação interpretativa não declarada.

**Pergunta operacional:**
> O texto foi lido ou o sentido foi antecipado? De que horizonte este output partiu para atribuir sentido jurídico ao texto?

**Sequência operacional:**

1. Identificar operação interpretativa (texto com efeito jurídico foi lido e seu sentido foi atribuído)
2. Verificar declaração de horizonte, critério ou posição interpretativa em operação
3. Verificar consciência histórico-efeitual (tradição doutrinária, jurisprudência dominante, alteração legislativa, prática institucional)
4. Verificar pergunta hermenêutica (qual pergunta o texto estava sendo chamado a responder)
5. Verificar aplicação ao caso concreto (sentido produzido em relação ao problema jurídico real)
6. Testar estranhamento e clareza
7. Verificar confronto de horizontes
8. Aplicar subprotocolo de precedentes quando aplicável
9. Classificar achado por marcador e severidade

**Testes binários de entrada:**

| Termo | Critério |
|---|---|
| Operação interpretativa | O output usou o texto para produzir conclusão jurídica sobre o caso? Sim → entra. Apenas citou → não entra. |
| Estranhamento suprimido | Existe interpretação alternativa plausível do mesmo texto que produziria conclusão diferente, e o output não a considerou nem descartou? Sim → marca. Não → não marca. |
| Clareza genuína | A clareza é verificável por ausência de ambiguidade relevante + ausência de leituras concorrentes plausíveis + compatibilidade com o contexto normativo? Os três presentes → não marca. Algum ausente → suspeita de presunção de clareza. |

**Marcadores canônicos:**

| Marcador | Status |
|---|---|
| `[PRÉ-COMPREENSÃO NÃO DECLARADA]` | core |
| `[HORIZONTE NÃO CONFRONTADO]` | core |
| `[ESTRANHAMENTO SUPRIMIDO]` | core |

Os três marcadores operam em paridade — o que varia é a severidade.

**Regras de não-acionamento:**

- Interpretação consolidada pela tradição doutrinária e jurisprudencial sedimentada → não marca; a fusão de horizontes foi realizada historicamente
- Output que declara parcialidade e confronta o texto com a posição contrária → não marca
- Horizonte interpretativo implícito mas consistente e reconstruível → no máximo severidade Baixa
- Output que adota uma posição em divergência doutrinária e nomeia a tensão, apresenta as correntes e justifica → não marca
- Aplicação correta da interpretação ao caso errado → não é EX005 (problema factual ou lógico)
- Apagamento de incerteza no estado do domínio → sinalizar EX004
- Falha de EX001 → sinalizar EX001

**Ponto cego declarado:**
EX005 opera sobre o processo de atribuição de sentido a textos com efeitos jurídicos: de que horizonte se parte, se esse horizonte foi declarado, se o texto resistiu à leitura antecipada e se leituras concorrentes plausíveis foram consideradas quando relevantes. Não verifica validade formal da norma, peso da autoridade, tipo de inferência ou suficiência argumentativa.

---

## 0.1 PROMPTS OPERACIONAIS CANÔNICOS

*Bloco de governança interna. Prompts canônicos ainda não produzidos em ciclo formal de teste.*

**Termos de ativação interna sugeridos:**
- Principal: `Gadamer` (uso restrito ao projeto) e `hermenêutico` (compatível com uso público)
- Compostos discriminantes: `pré-compreensão`, `horizonte interpretativo`, `estranhamento suprimido`, `fusão de horizontes`
- Vetados: `interpretação` isolado (vocabulário jurídico comum), `sentido` isolado (genérico)

---

### Lacunas de cobertura

| Objeto | Código previsto | Status |
|--------|-----------------|--------|
| Peça processual | EX005-PEC | A produzir |
| Cláusula contratual | EX005-CON | A produzir |
| Parecer jurídico | EX005-PAR | A produzir |
| Nota técnica | EX005-NOT | A produzir |
| Output de IA jurídica externa | EX005-OUT | A produzir |
| Decisão judicial | EX005-DEC | A produzir |
| Precedente como argumento | EX005-PRE | A produzir (objeto mais natural para subprotocolo de precedentes) |

---

## 0.2 CLÁUSULA DE ATIVAÇÃO, CONTENÇÃO E DESCARTE

*Cláusula transversal de governança de fase. Aplicável a todas as fichas de eixo do módulo de construção do raciocínio.*

**Regra-mãe (acima da ficha):** *Achados transitam. Lentes não.*

Entre fases do módulo de construção do raciocínio, transferem-se apenas produtos estruturados da análise anterior: achados, marcadores, severidade, gates, pendências, restrições e versões corrigidas. O modo de raciocínio do eixo ativado não se transfere automaticamente para a fase seguinte.

**Cláusula específica do eixo EX005:**

Este eixo opera como lente temporária de auditoria do processo interpretativo dentro da fase indicada do módulo de construção do raciocínio. Encerrada a fase, o modo de suspeita interpretativa — desconfiança permanente da leitura de qualquer texto — deve ser desativado. Apenas seus produtos formais — marcadores de horizonte não declarado, leituras concorrentes suprimidas, achados do subprotocolo de precedentes, severidade e gate — podem ser transferidos para a etapa seguinte.

**Riscos específicos de contaminação por resíduo EX005:**

- *Suspeita interpretativa residual:* fase seguinte continua tratando toda leitura como pré-compreensão não testada, gerando achados sem consequência.
- *Estranhamento performativo:* output final fica artificialmente cheio de "por outro lado" e "alternativamente", mesmo onde a clareza é genuína.
- *Captura de outros eixos:* problemas de EX001 (EX001), objeção não enfrentada (EX002) ou apagamento de incerteza (EX004) passam a ser lidos como "horizonte não declarado".
- *Hiperinterpretação:* a fase seguinte produz comentário hermenêutico onde a operação devida seria classificar achados, consolidar ou aplicar regra clara.

**Comportamento em confronto com outro eixo:**

EX005 não reinterpreta achados de outros eixos como problemas de horizonte. Verifica apenas se o sentido atribuído ao texto foi produzido por leitura situada e declarada. Quando o problema é controvérsia doutrinária omitida (EX004), achado adversarial (EX002) ou EX001 (EX001), EX005 não absorve — sinaliza para o eixo competente.

**Comportamento na entrega final:**

A fase de refinamento textual recebe apenas marcadores não resolvidos, declarações de horizonte requeridas e leituras concorrentes a explicitar. Não recebe a postura de suspeita interpretativa como diretriz de tom. O refinamento editorial produz texto que situa sua interpretação, sem performar dúvida desnecessária.

---

**Nota de modularidade indexada:**

Quando houver sinalização para eixo correlato, a ficha indica apenas o código do eixo (`EX00X`). A descrição completa do confronto, da ordem recomendada e do risco de dupla marcação deve ser consultada na `MATRIZ_DE_CONFRONTOS_INTER_EIXOS_EX.md`.

## 1. ARQUITETO-PAI

Hans-Georg Gadamer (1900–2002) foi filósofo alemão, discípulo de Heidegger e principal representante da hermenêutica filosófica do século XX. Sua obra central, *Verdade e Método* (1960), não é uma teoria do método hermenêutico — é uma crítica à ilusão de que o intérprete pode suspender sua pré-compreensão para "ler o texto como ele é". Para Gadamer, toda compreensão é historicamente situada: o intérprete já traz um horizonte de sentido que precede e condiciona o encontro com o texto.

**Por que Gadamer e não outro?**

O problema que o eixo precisa capturar é específico: outputs de IA jurídica que interpretam textos — normas, contratos, decisões — sem declarar o horizonte interpretativo em operação, apresentando o sentido atribuído como se fosse o sentido do texto. Isso não é erro lógico, falsa certeza sobre domínio incerto, nem EX003 disfarçada. É algo distinto: leitura que não reconhece a si mesma como leitura.

Gadamer é adotado porque formulou o mecanismo pelo qual o intérprete trata sua pré-compreensão como transparência. Seu conceito de **fusão de horizontes** (Horizontverschmelzung) descreve o que a boa interpretação exige: que o horizonte do intérprete e o horizonte do texto se confrontem e se transformem mutuamente. Em IA jurídica, esse mecanismo é especialmente ativo porque os modelos carregam padrões interpretativos consolidados pelo treinamento que tendem a se impor sobre o texto específico em análise.

Gadamer não é a única matriz teórica compatível com essa operação — teoria da interpretação jurídica, hermenêutica jurídica clássica e teorias da compreensão na filosofia da linguagem oferecem caminhos próximos. Gadamer é adotado pela precisão de sua gramática operacional sobre horizonte, tradição e historicidade.

---

## 2. O TRAÇADO FILOSÓFICO

**Círculo hermenêutico.** Gadamer parte do conceito heideggeriano: compreender um texto exige alguma compreensão prévia do todo para entender as partes, e a compreensão das partes para entender o todo. O problema não é ter pré-compreensão — é não reconhecê-la. Quando o intérprete não percebe que chegou ao texto com um horizonte formado, o círculo se fecha sobre si mesmo: confirma o que já se esperava em vez de se deixar interpelar pelo texto.

**Pré-compreensão e preconceito produtivo.** Para Gadamer, os **Vorurteile (pré-juízos)** não são necessariamente obstáculos à compreensão. O problema é quando o intérprete não os submete ao teste do encontro com o texto. Um output que interpreta uma cláusula projetando sobre ela o sentido padrão do tipo contratual, sem verificar se o texto específico desvia desse padrão, está operando com pré-juízo não testado.

**Fusão de horizontes e confronto.** A boa interpretação é aquela em que o horizonte do intérprete e o horizonte histórico-normativo do texto, da tradição interpretativa e do caso de aplicação se fundem pelo alargamento mútuo. Isso exige confronto: o horizonte do intérprete precisa ser exposto ao texto e corrigido por ele. Confrontar não é fundir — um output pode mencionar leitura alternativa sem que o horizonte tenha sido afetado pelo confronto. O marcador `[HORIZONTE NÃO CONFRONTADO]` captura a ausência do confronto, que é o ato verificável.

**Consciência histórico-efeitual.** Para Gadamer, o intérprete está sempre afetado por uma **wirkungsgeschichtliches Bewusstsein (consciência histórico-efeitual)** — a percepção de que sua leitura é condicionada pela história de efeitos que o texto já produziu. No Direito, isso é especialmente importante: uma norma, cláusula ou precedente nunca chega "puro" ao intérprete; chega atravessado por tradição doutrinária, sedimentação jurisprudencial, práticas institucionais, contexto normativo atual, mutações legislativas e deslocamentos sociais e regulatórios.

**Aplicação como compreensão.** No Direito, o sentido do texto não é produzido em abstrato e depois aplicado ao caso. A aplicação ao caso participa da própria atribuição de sentido. Por isso, o o módulo de construção do raciocínio deve verificar se o output leu o texto em relação ao problema jurídico concreto, sem projetar sobre ele uma interpretação genérica incompatível com o caso.

**Pergunta hermenêutica.** Gadamer dá grande importância à estrutura de pergunta e resposta. Toda interpretação responde a uma pergunta — declarada ou não. Interpretações deslocadas frequentemente surgem quando o output responde a uma pergunta não declarada, diferente da pergunta jurídica real do caso.

**Estranhamento como condição.** Um texto jurídico que parece óbvio na primeira leitura é exatamente o que exige mais suspeita hermenêutica: a obviedade é frequentemente sinal de que a pré-compreensão se impôs antes que o texto pudesse resistir.

**Tradução operacional.** O traçado gadameriano aplica-se ao módulo de construção do raciocínio como protocolo de auditoria do processo interpretativo. A pergunta não é "a interpretação é correta?" — é "o output reconheceu que estava interpretando, declarou o horizonte em operação, e deixou o texto resistir?"

---

## 3. A OPERAÇÃO DO EIXO

**Passo 1 — Identificação de operação interpretativa.**
Localizar os pontos em que um texto com efeitos jurídicos foi lido e seu sentido atribuído: dispositivo normativo, cláusula contratual, ementa, decisão judicial, regulamento, instrução normativa. O eixo aciona quando o output usa o texto para produzir conclusão jurídica sobre o caso — não quando apenas cita.

**Passo 2 — Verificação de declaração de horizonte.**
Verificar se o output declara o horizonte, critério ou posição interpretativa em operação: leitura literal, sistemática, teleológica, histórica, consumerista, conforme jurisprudência dominante, conforme precedente específico ou em contraste com orientação consolidada. A ausência total de qualquer referência ao critério interpretativo é sinal de pré-compreensão operando sem se declarar.

**Passo 3 — Verificação de consciência histórico-efeitual.**
O output reconhece a tradição interpretativa que já incide sobre o texto: doutrina sedimentada, jurisprudência dominante, alteração legislativa, superação jurisprudencial, prática institucional ou contexto regulatório? A ausência dessa consciência é relevante quando o output apresenta uma leitura como imediata, ignorando que o texto já chega ao caso carregado por uma história interpretativa.

**Passo 4 — Verificação da pergunta hermenêutica.**
O output explicitou qual pergunta o texto estava sendo chamado a responder? Se a pergunta interpretativa está deslocada, a resposta pode parecer correta e ainda assim produzir sentido inadequado ao caso.

**Passo 5 — Verificação da aplicação ao caso.**
O output leu o texto em relação ao problema jurídico concreto, ou projetou interpretação genérica incompatível com o caso?

**Passo 6 — Teste de estranhamento e verificação de clareza.**
A clareza não deve ser presumida pela fluência da leitura. Deve ser verificada pela ausência de ambiguidade relevante, ausência de leituras concorrentes plausíveis e compatibilidade com o contexto normativo ou contratual. O teste binário: existe interpretação alternativa plausível do mesmo texto que produziria conclusão diferente? Se sim, e se o output não a considerou nem descartou, ativa `[ESTRANHAMENTO SUPRIMIDO]`.

**Passo 7 — Verificação de confronto de horizontes.**
O output realizou o confronto mínimo: (a) declarou de onde parte; (b) confrontou essa partida com o que o texto especificamente diz; (c) produziu interpretação que integra os dois movimentos? Um output que vai diretamente do texto à conclusão, sem declarar a mediação interpretativa, está em `[HORIZONTE NÃO CONFRONTADO]`.

**Passo 8 — Subprotocolo de precedentes.**
Para interpretação de precedentes judiciais:

| Elemento | Pergunta |
|---|---|
| **Contexto fático** | Os fatos do caso atual são realmente análogos aos do precedente? A analogia foi declarada ou presumida? |
| **ratio decidendi** | O output usou a razão de decidir ou apenas a ementa? A ementa foi tratada como substituto do acórdão? |
| **Horizonte decisório** | A decisão foi produzida em contexto normativo ou jurisprudencial ainda válido? Houve alteração legislativa ou superação jurisprudencial relevante? |
| **Transposição** | O precedente foi aplicado ao caso ou apenas citado como reforço retórico? A transposição foi declarada? |

Ausência de verificação em qualquer desses elementos, quando o precedente é central, gera `[PRÉ-COMPREENSÃO NÃO DECLARADA]` com severidade correspondente.

**Passo 9 — Classificação e marcação.**
O o módulo de construção do raciocínio aplica o marcador canônico, classifica a severidade e registra o achado com todos os campos obrigatórios preenchidos.

---

## 4. O QUE CONTA COMO ACHADO REAL

Achado real é qualquer instância em que o output atribui sentido a texto com efeitos jurídicos sem declarar o horizonte interpretativo em operação, sem confrontar o texto com esse horizonte, ou sem deixar o texto resistir à interpretação antecipada.

**Achado documentado — análise de plano de saúde (Gemini):**

O output interpretou cláusula de exclusão de cobertura como "clara e inequívoca", sem declarar o critério interpretativo em uso e sem considerar a leitura conforme o CDC (interpretação mais favorável ao consumidor de cláusula ambígua em contrato de adesão). A "clareza" era produto da pré-compreensão do intérprete, não verificada contra o texto. O output não realizou o estranhamento: aplicou o sentido que a cláusula pareceria ter em leitura direta, sem testar se o contexto consumerista alteraria esse sentido. Achado: `[ESTRANHAMENTO SUPRIMIDO]` com `[PRÉ-COMPREENSÃO NÃO DECLARADA]`, severidade Alta.

**Exemplos contrastivos:**

**Falso positivo — o que NÃO é achado EX005:**
Output que interpreta o art. 186 do CC e conclui que culpa é elemento da responsabilidade subjetiva, sem declaração explícita de método. Está em domínio consolidado pela tradição doutrinária sedimentada — a fusão de horizontes foi realizada historicamente, não há horizonte alternativo plausível que produza conclusão materialmente diferente, e a clareza é genuína. O eixo EX005 não tem achado.

**Zona cinzenta — critério implícito mas reconstruível:**
Output que interpreta cláusula de reajuste sem declarar o critério, mas cujo raciocínio revela consistentemente a adoção de interpretação sistemática (confronta a cláusula com outras disposições do contrato). O horizonte está implícito mas é reconstruível. `[PRÉ-COMPREENSÃO NÃO DECLARADA]` de severidade Baixa.

**Versão corrigida — como transformar `[ESTRANHAMENTO SUPRIMIDO]` em output íntegro:**

> *Versão com achado:* "A cláusula é clara ao excluir o procedimento X da cobertura."

> *Versão corrigida:* "A cláusula exclui o procedimento X em sua leitura literal. Sob o critério de interpretação mais favorável ao consumidor (art. 47 do CDC), aplicável a contratos de adesão, a exclusão poderia ser questionada por [razão específica]. A interpretação que prevalece depende do enquadramento contratual adotado — relação de consumo sujeita ao CDC ou contrato paritário — questão que exige verificação antes de usar esta conclusão como premissa de orientação."

**Outros padrões que contam como achado real:**

- Output que aplica precedente formado em contexto diferente sem verificar a analogia fática, a ratio decidendi ou o horizonte decisório vigente.
- Output que interpreta norma tributária segundo sua letra sem considerar a finalidade declarada do dispositivo quando o contexto de produção indica finalidade diversa.
- Output que lê contrato de trabalho com categorias do direito civil sem declarar a transposição.
- Output que aplica interpretação doutrinária dominante como se fosse o único sentido possível, sem declarar que se trata de interpretação e não de leitura direta.

---

## 5. O QUE NÃO CONTA — ANTI-PADRÕES

**Anti-padrão 1 — Toda interpretação sem critério explicitado ≠ achado automático.**
Se o critério é implícito mas consistente e reconstruível, o achado é no máximo severidade Baixa.

**Anti-padrão 2 — Interpretação consolidada ≠ pré-compreensão não testada.**
Quando a interpretação adotada é aquela que a doutrina e jurisprudência dominantes sedimentaram, a fusão de horizontes foi realizada historicamente. Aplicar interpretação pacificada sem reabrir o debate não é `[ESTRANHAMENTO SUPRIMIDO]`.

**Anti-padrão 3 — Divergência doutrinária ≠ fusão não realizada.**
A existência de divergência não é, por si, achado EX005. O achado ocorre quando o output adota uma posição sem declarar que há posições concorrentes.

**Anti-padrão 4 — Erro de aplicação ≠ erro hermenêutico.**
Output que aplica corretamente a interpretação ao caso errado tem problema factual ou lógico, não hermenêutico.

**Anti-padrão 5 — Toda preferência interpretativa ≠ pré-compreensão ilegítima.**
Toda interpretação parte de algum horizonte — isso é condição da compreensão, não defeito. O eixo não exige neutralidade interpretativa. Exige que o horizonte seja declarado e que o texto seja deixado resistir a ele.

---

## 6. RÉGUA DE SEVERIDADE

| Nível | Critério | Consequência no gate |
|---|---|---|
| **Baixa** | Pré-compreensão implícita mas reconstruível; critério interpretativo não declarado em questão de baixa consequência; clareza genuína verificável | Registro no output. Sem bloqueio. |
| **Média** | Interpretação de texto ambíguo sem declaração de critério; estranhamento suprimido em questão acessória; horizonte não confrontado identificável mas sem impacto direto na conclusão central | Registro com marcador. Nota sobre horizonte em operação e interpretações concorrentes. |
| **Alta** | Interpretação de cláusula, dispositivo ou decisão central sem declaração de horizonte; sentido atribuído como único quando existem leituras concorrentes plausíveis com consequências materialmente diferentes; contexto de produção ignorado quando relevante; precedente usado sem verificação de ratio decidendi ou analogia fática | Bloqueio parcial: o output não é encaminhado adiante sem resolução. |
| **Crítica** | Múltiplas interpretações centrais com pré-compreensão não declarada; horizonte do intérprete sobrepõe o horizonte do texto em todas as questões interpretativas relevantes; o output torna impossível ao operador identificar onde termina o texto e começa a interpretação | Bloqueio total. Nota de inviabilidade com mapeamento das operações interpretativas não declaradas. |

---

## 7. FORMATO DE OUTPUT ESPERADO

Os cinco campos abaixo são **obrigatórios** em todo achado EX005. Achado sem preenchimento completo não é auditável.

```text
ACHADO — EIXO EX005 | HERMENÊUTICO

Marcador: [PRÉ-COMPREENSÃO NÃO DECLARADA] / [HORIZONTE NÃO CONFRONTADO] /
          [ESTRANHAMENTO SUPRIMIDO]
Severidade: Baixa / Média / Alta / Crítica

① Texto interpretado:
[Dispositivo, cláusula, decisão ou texto com efeitos jurídicos sobre o qual a interpretação
opera — identificação precisa, não paráfrase]

② Sentido atribuído pelo output:
[O que o output concluiu que o texto diz ou significa no caso concreto]

③ Horizonte interpretativo em operação:
[Qual critério o output aplicou, mesmo que não declarado — literal, sistemático, teleológico,
histórico, conforme CDC, conforme doutrina dominante, conforme precedente X]

④ Leitura concorrente suprimida:
[Qual interpretação alternativa plausível o texto admite e não foi considerada — apenas para
[ESTRANHAMENTO SUPRIMIDO] e [HORIZONTE NÃO CONFRONTADO]]

⑤ Impacto na conclusão:
[Por que a supressão altera, ou pode alterar, a conclusão central ou a orientação ao operador]

Acionamento de gate:
[Sem bloqueio / Nota de horizonte e leituras concorrentes / Bloqueio parcial /
Bloqueio total com nota de inviabilidade]

Observação:
[Apenas se necessário: distinção de anti-padrão, sobreposição com outro eixo,
resultado do subprotocolo de precedentes]
```

---

## 8. OPERAÇÃO DENTRO DO o módulo de construção do raciocínio

**Roteiros Operacionais de ativação primária:**

- ROs que produzem ou avaliam interpretação de dispositivo normativo aplicado ao caso concreto
- ROs que produzem ou avaliam interpretação de cláusula contratual com efeito sobre direitos ou obrigações
- ROs que utilizam decisão judicial como precedente
- ROs que identificam sentido de regulamento, instrução normativa ou ato administrativo com efeitos jurídicos
- ROs que produzem qualificação de relação jurídica a partir da leitura do instrumento que a constitui

**Casos secundários — ativação por sinalização:**

EX005 é ativado secundariamente quande EX004 sinaliza `[APAGAMENTO DE INCERTEZA]` em questão interpretativa — o o módulo de construção do raciocínio verifica se o apagamento corresponde a supressão de divergência doutrinária real (EX004) ou a estranhamento suprimido na leitura do texto (EX005). Podem coexistir.

EX005 é ativado secundariamente quande EX002 identifica argumento unilateral em questão interpretativa — o o módulo de construção do raciocínio verifica se a unilateralidade é de estrutura argumentativa (EX002) ou de horizonte interpretativo não confrontado com o texto (EX005).

---

## 9. DISTINÇÃO confronto de raciocíniosÍTICA

**Caso 1 — Interpretação equivocada como erro hermenêutico.**
O eixo opera sobre o processo de atribuição de sentido, não sobre a correção do sentido atribuído. Um output pode interpretar corretamente e ter achado EX005 (horizonte não declarado); pode interpretar erroneamente e não ter achado EX005 (o erro é factual).

**Caso 2 — EX004 vs. EX005 em questão interpretativa ambígua.**
Quando um output afirma que "a doutrina é pacífica" sobre interpretação controvertida, há dois achados possíveis: EX004 (`[APAGAMENTO DE INCERTEZA]` — a controvérsia existe e não foi declarada) e EX005 (`[ESTRANHAMENTO SUPRIMIDO]` — o texto foi lido como tendo sentido único quando admite leituras concorrentes). Marcar os dois separadamente é correto; fundir obscurece a natureza do problema.

**Caso 3 — EX003 vs. EX005 em qualificação jurídica a partir de texto.**
Podem estar presentes simultaneamente um achado EX003 (EX003 não declarada na qualificação) e um achado EX005 (horizonte não declarado na leitura do contrato que fornece os elementos para a inferência). São operações distintas na mesma análise.

**Caso 4 — Preferência de parte como pré-compreensão ilegítima.**
Output parcial que declara sua parcialidade e confronta o texto com a posição contrária não é achado. Output parcial que apresenta a interpretação favorável como única leitura possível é `[ESTRANHAMENTO SUPRIMIDO]`.

*Lacuna sinalizada:* distinções operacionais com EX001 e demais eixos em tabela comparativa interna a esta ficha — a serem incorporadas em ciclo posterior.

---

## 10. CHECKLIST DE FALHA DE EXECUÇÃO

O eixo falhou quando:

- [ ] O o módulo de construção do raciocínio identificou interpretação de texto com efeitos jurídicos e não verificou a declaração de horizonte interpretativo
- [ ] O o módulo de construção do raciocínio presumiu clareza do texto pela fluência da leitura, sem verificar ausência de ambiguidade relevante e de leituras concorrentes plausíveis
- [ ] O o módulo de construção do raciocínio tratou interpretação consolidada pela tradição como pré-compreensão não testada, produzindo falso positivo
- [ ] O o módulo de construção do raciocínio não verificou leituras concorrentes plausíveis antes de marcar `[ESTRANHAMENTO SUPRIMIDO]`
- [ ] O o módulo de construção do raciocínio não aplicou o subprotocolo de precedentes quando decisão judicial era central para a conclusão
- [ ] O o módulo de construção do raciocínio confundiu erro factual de aplicação da norma com erro hermenêutico
- [ ] O o módulo de construção do raciocínio fundiu achado EX004 e achado EX005 em marcação única
- [ ] O o módulo de construção do raciocínio fundiu achado EX003 e achado EX005 em marcação única em questão de qualificação jurídica a partir de texto
- [ ] O o módulo de construção do raciocínio produziu achado EX005 sem preencher os cinco campos obrigatórios
- [ ] O o módulo de construção do raciocínio exigiu neutralidade interpretativa como condição de output íntegro, quando a condição correta é declaração de horizonte e confronto com o texto
- [ ] O output avançou com marcador de severidade Alta ou Crítica sem resolução de gate

---

*a infraestrutura modular 1.0 — Camada confronto de raciocínios / o módulo de construção do raciocínio | EixEX005 — Hermenêutico (Gadamer)*
*Documento interno. Não transversal ao ecossistema.*
