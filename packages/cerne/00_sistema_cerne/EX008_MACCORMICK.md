# FICHA INSTRUCIONAL — EIXO EX008 JUSTIFICAÇÃO DE SEGUNDA ORDEM (MACCORMICK)

**Código:** EX008
**Nome do método:** Justificação de Segunda Ordem
**Arquiteto-pai:** Neil MacCormick

---

## 0. NÚCLEO EXECUTIVO

*Bloco imperativo — colável diretamente no Roteiro Operacional do módulo de construção do raciocínio.*

---

**EIXO EX008 — JUSTIFICAÇÃO DE SEGUNDA ORDEM (MACCORMICK)**

**Pergunta operacional:**
> A regra de decisão que esta tese instituiria, se universalizada, é praticável, sistemicamente consequente e coerente com o ordenamento?

*Vocabulário operacional:* **justificação de segunda ordem** = avaliação das premissas escolhidas e da regra que a decisão instaura (em oposição à justificação de primeira ordem, que é o silogismo entre premissas já dadas); **universalizabilidade** = a regra deve ser formulável como norma geral aplicável a todos os casos relevantemente semelhantes; **ad hoc** = decisão justificadamente irrepetível, sustentada em elemento singular do caso; **consequência jurídico-sistêmica** = efeito sobre a operação do sistema normativo, distinta de consequência material (econômica, social, comportamental), que está fora do eixo.

**Sequência operacional:**

1. Identificar a conclusão central do output.
2. Reformular a conclusão como regra de decisão implícita.
3. Verificar se a regra é formulável como norma geral.
4. Testar a universalizabilidade da regra em casos relevantemente semelhantes.
5. Testar as consequências jurídico-sistêmicas da regra universalizada.
6. Testar a coerência da regra com escolhas legislativas expressas, estrutura dos institutos e princípios aplicáveis.
7. Verificar se a escolha das premissas concorrentes foi justificada.
8. Aplicar marcador, classificar severidade, registrar no formato padrão.

**Testes binários de entrada:**

| Critério | Entra? |
|---|---|
| O output institui, pressupõe ou recomenda uma regra de decisão? | Se sim → entra |
| A conclusão pode ser reformulada como norma geral aplicável a casos semelhantes? | Se sim → entra |
| A tese resolve o caso por escolha entre premissas concorrentes? | Se sim → entra |
| O output sustenta tese de fronteira, inovadora, extensiva, restritiva ou analógica? | Se sim → entra |
| A regra é universalizável sem exceções indefinidas? | Se não → marca |
| A regra produz consequência jurídico-sistêmica relevante não declarada? | Se sim → marca |
| A regra colide com escolha legislativa expressa ou regime jurídico estruturado? | Se sim → marca |
| O output é puramente subsuntivo, sem escolha relevante entre premissas? | Se sim → não entra |
| A crítica é política, econômica, social ou cultural, sem consequência jurídico-sistêmica? | Se sim → não entra |

**Marcadores canônicos:**

| Marcador | Status | Uso |
|---|---|---|
| `[REGRA NÃO UNIVERSALIZÁVEL]` | core | A tese só funciona no caso concreto ou depende de exceções casuísticas indefinidas |
| `[CONSEQUÊNCIA SISTÊMICA NÃO DECLARADA]` | core | A regra universalizada altera estabilidade, previsibilidade, coerência ou operação do sistema sem declaração |
| `[INCOERÊNCIA COM ESCOLHA LEGISLATIVA EXPRESSA]` | core | A regra contraria regime, lei especial ou escolha normativa explícita sem enfrentar a colisão |
| `[ESCOLHA DE PREMISSA NÃO JUSTIFICADA]` | core | O output escolhe norma, interpretação ou qualificação sem justificar frente a alternativa concorrente |
| `[SOLUÇÃO AD HOC]` | core | A decisão se apresenta como regra, mas depende de elemento irrepetível ou casuístico |

**Regras de não-acionamento:**

- Se o output é puramente subsuntivo e não envolve escolha relevante entre premissas, então não marca.
- Se a crítica é de conveniência política, econômica, social ou cultural, então não marca.
- Se a consequência apontada é material, mas não jurídico-sistêmica, então não marca.
- Se a tese é inovadora, mas declara a regra, mede suas consequências e justifica coerência, então não marca.
- Se a decisão é legitimamente ad hoc por autorização normativa expressa, então não marca.
- Se o problema é objeção direta à tese, então não marca; sinalizar EX002.
- Se o problema é validade formal da norma, então não marca; sinalizar EX010.
- Se o problema é operação técnica de precedente, então não marca; sinalizar EX007.

**Regra de integridade do eixo:**

> MacCormick não testa se a tese parece boa para o caso; testa se a regra que ela instituiria pode ser sustentada como razão jurídica geral.

**Regra de contenção consequencialista:**

> O teste consequencialista restringe-se a consequência jurídico-sistêmica: coerência com o ordenamento, estabilidade do sistema, previsibilidade, praticabilidade da regra universalizada e compatibilidade com escolhas legislativas expressas.

**Ponto cego declarado:**

O eixo não testa validade formal da norma (domínio de EX010), peso prático da autoridade (domínio de EX011), EX009 de termos jurídicos (domínio de EX009), objeção direta à tese (domínio de EX002), operação técnica de precedente (domínio de EX007) ou colapso entre categorias jurídicas (domínio de EX006). MacCormick opera sobre a justificação externa da decisão: a escolha das premissas e a regra que a conclusão instituiria se fosse universalizada.

---

## 0.1 PROMPTS OPERACIONAIS CANÔNICOS

**Termos de ativação interna sugeridos:**

- Principal: "MacCormick" (uso restrito ao projeto); "justificação de segunda ordem" (uso público); "regra de decisão universalizada"
- Compostos discriminantes: "regra não universalizável", "consequência sistêmica não declarada", "incoerência com escolha legislativa expressa", "premissa concorrente não enfrentada", "solução ad hoc", "tese boa para o caso e ruim para o sistema"
- Vetados isoladamente: "consequência", "coerência", "regra", "sistema", "premissa" (comuns demais quando isolados)

**Tabela de lacunas de cobertura:**

| Objeto | Código | Status | Prompt canônico |
|---|---|---|---|
| Peça processual | EX008-PEC | Pendente | — |
| Cláusula contratual | EX008-CON | Pendente | — |
| Parecer jurídico | EX008-PAR | Pendente | — |
| Nota técnica | EX008-NOT | Pendente | — |
| Output de IA jurídica externa | EX008-OUT | Pendente | — |
| Decisão judicial | EX008-DEC | Pendente | — |
| Precedente como regra futura | EX008-PRE | Pendente | — |

---

## 0.2 CLÁUSULA DE ATIVAÇÃO, CONTENÇÃO E DESCARTE

**Regra-mãe (acima da ficha):**

> Achados transitam. Lentes não.
>
> Entre fases do módulo de construção do raciocínio, transferem-se apenas produtos estruturados da análise anterior: achados, marcadores, severidade, gates, pendências, restrições e versões corrigidas. O modo de raciocínio do eixo ativado não se transfere automaticamente para a fase seguinte.

**Cláusula específica do eixo EX008:**

Ao fim da fase em que o eixo MacCormick foi ativado, desativa-se o modo de justificação de segunda ordem. Não permanece em fases subsequentes a tendência de universalizar toda conclusão, transformar toda solução casuística em regra geral ou exigir teste sistêmico em pontos laterais. Permanecem como produtos exportáveis: marcadores aplicados, severidade registrada, regra implícita reformulada, consequências jurídico-sistêmicas identificadas, premissas não justificadas, gates e versão corrigida.

**Riscos específicos de contaminação por resíduo EX008:**

- Tendência a exigir universalização mesmo de conclusões estritamente casuísticas.
- Tendência a transformar ressalvas estratégicas ou textuais em regras gerais.
- Tendência a converter consequência política, econômica ou social em consequência jurídico-sistêmica.
- Tendência a invadir o terreno de validade formal (EX010), peso de autoridade (EX011) ou operação precedental (EX007).
- Tendência a produzir hiperabstração e perda de aderência ao caso concreto.

**Comportamento em confronto com outro eixo:**

Quando pareado com EX002, Sócrates ataca a tese; MacCormick aceita provisoriamente a tese e testa a regra que ela instituiria.

Quando pareado com EX007, Levi extrai e testa a razão do paradigma; MacCormick mede a regra que a aplicação atual instituiria como orientação futura.

Quando pareado com EX010 e EX011, Kelsen estabiliza validade formal da fonte; Raz calibra peso prático; MacCormick testa a escolha entre premissas e a consequência sistêmica da regra resultante.

**Comportamento na entrega final:**

À fase de refinamento textual transmitem-se apenas marcadores não resolvidos e qualificadores de segunda ordem ("regra não universalizável", "consequência sistêmica não declarada", "premissa concorrente não enfrentada", "exige estreitamento da regra"). Não se transmite postura cognitiva de universalização permanente.

---

**Nota de modularidade indexada:**

Quando houver sinalização para eixo correlato, a ficha indica apenas o código do eixo (`EX00X`). A descrição completa do confronto, da ordem recomendada e do risco de dupla marcação deve ser consultada na `MATRIZ_DE_CONFRONTOS_INTER_EIXOS_EX.md`.

## 1. ARQUITETO-PAI

Donald Neil MacCormick (1941–2009) foi jurista escocês, professor em Edimburgo, uma das figuras centrais da filosofia do Direito anglo-saxão do século XX. Sua obra-síntese, *Legal Reasoning and Legal Theory* (1978), com desenvolvimentos posteriores em *Rhetoric and the Rule of Law* (2005), formulou a distinção entre **justificação de primeira ordem** e **justificação de segunda ordem** no raciocínio jurídico — distinção que se tornou referência metodológica tanto em sistemas continentais quanto anglo-saxões.

A justificação de primeira ordem opera por silogismo: dada a norma N e o fato F, deduz-se o resultado R. Quando norma e fato estão estabelecidos, a derivação é dedutiva e a justificação é meramente lógica. Mas o jurista raramente trabalha em situação ideal: a norma é ambígua, há normas em conflito, o fato cabe em mais de uma categoria, há lacuna, ou a regra textual do sistema de seu propósito. Nesses casos — que são a vasta maioria dos casos juridicamente difíceis — é preciso **escolher** entre premissas concorrentes. A justificação de primeira ordem não justifica essa escolha. É preciso, então, justificação de segunda ordem.

A justificação de segunda ordem, segundo MacCormick, opera por três testes que devem ser satisfeitos cumulativamente:

(i) **Universalizabilidade** — a regra de decisão deve ser formulável como norma geral aplicável a todos os casos relevantemente semelhantes. Não há decisão jurídica legítima que valha apenas para o caso presente. Toda decisão é, implícita ou explicitamente, instauração de regra.

(ii) **Consequência** — a regra, universalizada, produz consequências aceitáveis no sistema? O teste consequencialista é estritamente **interno ao Direito**: avalia efeitos jurídico-sistêmicos, não conveniência política ou econômica. A pergunta é: se essa regra reger todos os casos análogos, o sistema continua a funcionar coerentemente?

(iii) **Coerência (consistência sistêmica)** — a regra é coerente com o conjunto do ordenamento, com as escolhas legislativas expressas, com a estrutura dos institutos, com os princípios constitucionais? A coerência aqui é estrutural, não valorativa: trata da consistência do sistema como ordem normativa.

Esse aparato tem raízes mais antigas. **Jerzy Wróblewski** (1926–1990), jurista polonês, formulou já nos anos 1960 a distinção entre justificação interna e externa: a interna é a validade lógica do silogismo; a externa é a justificação das premissas escolhidas. MacCormick consolidou e refinou essa estrutura no idioma analítico, ampliando os critérios de avaliação externa.

**Por que MacCormick e não outro?**

O problema que o eixo precisa capturar é específico: outputs jurídicos que vencem o teste de primeira ordem — têm arquitetura toulminiana, resistem a objeção pontual, declaram incerteza — e ainda assim instituem regra de decisão cujo alcance não foi medido. A tese vence o caso, mas se universalizada produz consequência sistêmica destrutiva, ou é incoerente com escolha legislativa expressa, ou simplesmente não é universalizável em termos praticáveis. A decisão é boa para o caso e ruim para o sistema.

MacCormick é o arquiteto adequado porque formulou, com a precisão de um filósofo analítico, os três testes que toda justificação de escolha entre premissas deve satisfazer. Sua teoria é **metodológica, não substantiva**: ela não diz qual regra é correta, diz que toda regra precisa passar pelos três testes para ser justificadamente escolhida. Isso a torna universal — adequada ao módulo de construção do raciocínio — sem precisar embarcar em compromisso valorativo, que seria matéria externa ao eixo.

A diferença em relação aos demais eixos é precisa. EX002 testa a tese por objeção direta; MacCormick testa a regra que a tese instituiria. EX010 testa a validade formal; MacCormick testa a justificação da escolha entre normas válidas concorrentes. EX011 testa a razão protetora da autoridade; MacCormick testa a coerência sistêmica da decisão. EX009 testa EX009 na margem; MacCormick testa a regra mesmo no caso central. EX001 estrutura o argumento; MacCormick avalia a escolha das premissas que sustentam a estrutura. EX004 controla a honestidade epistêmica; MacCormick controla a honestidade normativa — a regra que a decisão cria foi declarada e testada como norma? EX007 trata a extração da *o módulo de construção do raciocínio* do paradigma; MacCormick trata a regra que esta decisão, ela própria, instituiria como paradigma futuro.

---

## 2. O TRAÇADO FILOSÓFICO

**Justificação interna e externa (Wróblewski).** Toda decisão jurídica tem duas dimensões justificáveis. A interna é o silogismo: das premissas decorre a conclusão. A externa é a justificação das próprias premissas: por que esta norma e não outra; por que esta interpretação e não outra; por que este fato é qualificado assim e não de outro modo. A justificação interna é necessária mas insuficiente. Um silogismo perfeito a partir de premissas mal escolhidas produz conclusão tecnicamente válida e juridicamente ilegítima.

**Os três testes da justificação externa (MacCormick).** A justificação externa de uma decisão jurídica exige, cumulativamente:

- **Universalizabilidade.** Adaptação do imperativo categórico kantiano ao Direito: a regra de decisão tem de poder valer como norma geral. Não no sentido de que tem de ser explicitamente formulada como norma — mas no sentido de que tem de ser **formulável** como tal. Decisão é instauração de regra; quem decide instaura, sabendo ou não, uma norma para casos semelhantes. Toda decisão honesta declara a regra que instaura.

- **Consequência (no sentido jurídico-sistêmico).** Universalizada, essa regra produz que efeitos no sistema? O teste é restrito: trata de efeito normativo, não de impacto material. A pergunta certa é: "se essa regra reger todos os casos relevantemente análogos, o sistema permanece operável, coerente, previsível?" A pergunta errada é: "essa regra é boa para a economia, para os trabalhadores, para o desenvolvimento?" — esta última é juízo político ou valorativo, e fica fora do eixo MacCormick.

- **Coerência sistêmica.** A regra é compatível com o restante do ordenamento? Com as escolhas legislativas expressas? Com a estrutura dos institutos jurídicos próximos? Com os princípios constitucionais? A coerência aqui é estrutural — opera por compatibilidade lógica e funcional, não por adesão valorativa.

**Os dois sentidos de "consequência".** Há ambiguidade no termo, e o eixo precisa fixá-la. *Consequência material* — efeito empírico no mundo (econômico, social, comportamental) — é juízo extra-jurídico, fora do eixo. *Consequência jurídico-sistêmica* — efeito sobre a operação do sistema normativo, sobre a previsibilidade, sobre o tratamento de casos análogos — é interno ao Direito e é o objeto do eixo. MacCormick é explícito ao distinguir os dois: o juiz não decide por política econômica; decide por consistência sistêmica.

**Universalizabilidade não é generalização ingênua.** Universalizar não é dizer "isso vale para todo caso parecido sem exame". É dizer: a regra que esta decisão instaura tem de ser **formulável** como norma e tem de ser **aplicável** aos casos cobertos por essa formulação. Se a formulação cobre uma classe ampla e cria absurdo em parte dela, ou a regra precisa ser refinada (estreitada) ou a decisão presente está errada. A universalizabilidade força declaração honesta do alcance.

**Tradução operacional.** O traçado de MacCormick aplica-se ao módulo de construção do raciocínio como protocolo de teste prospectivo. A pergunta não é "esta tese resiste à objeção?" — é "esta tese, formulada como regra geral, sobrevive aos três testes? Universalizada, é praticável? Sistemicamente consequente? Coerente com o ordenamento?".

---

## 3. A OPERAÇÃO DO EIXO

O o módulo de construção do raciocínio raciocina sob o eixo EX008 MacCormick na seguinte sequência:

**Passo 1 — Identificação da conclusão central como regra implícita.**
O o módulo de construção do raciocínio identifica a conclusão central do output e reformula-a como regra de decisão. Toda conclusão pode ser reformulada como norma: "neste caso, decide-se X" implica "em casos com as características C1, C2, C3 que justificaram X, deve-se decidir X". A reformulação é interpretativa — o o módulo de construção do raciocínio precisa identificar quais características são as **operantes** na decisão.

Se a reformulação como regra não é possível (a decisão é puramente *ad hoc*, justificada por elemento irrepetível), aciona `[SOLUÇÃO AD HOC]`.

**Passo 2 — Formulação da regra universalizada.**
O o módulo de construção do raciocínio formula a regra de decisão como norma geral, com sujeito, hipótese de aplicação e consequência. Exemplo: "todo aderente B2B com hipossuficiência técnica em contrato regulado por lei especial atrai aplicação do CDC, com inversão do ônus e revisão de cláusulas abusivas".

A formulação deve ser tão estreita quanto a *o módulo de construção do raciocínio* da decisão exige, e tão ampla quanto ela permite. Estreitar artificialmente para preservar a decisão é desonestidade; ampliar para forçar absurdo é deslealdade ao output.

**Passo 3 — Teste de universalizabilidade.**
O o módulo de construção do raciocínio verifica se a regra formulada é universalizável em termos praticáveis. Critérios:

- A regra é formulável sem cláusula de exceção indefinida ("salvo casos em que...")?
- A regra cobre a classe de casos que ela logicamente deve cobrir, ou só funciona se restrita ao caso presente?
- A aplicação da regra a outros casos da mesma classe produz resultado análogo, ou resultado absurdo?

Se a regra só é defensável quando estreitada artificialmente, ou quando socorrida por exceções *ad hoc*, aciona `[REGRA NÃO UNIVERSALIZÁVEL]`.

**Passo 4 — Teste de consequência sistêmica.**
O o módulo de construção do raciocínio verifica que consequências jurídico-sistêmicas a regra produz, se universalizada. Quatro vetores típicos:

- **Esvaziamento de regime legal expresso.** A regra, universalizada, torna funcionalmente inaplicável uma lei especial, dispositivo legal ou regime jurídico estabelecido?
- **Reconfiguração de instituto.** A regra altera a estrutura de algum instituto jurídico próximo, sem que essa alteração tenha sido declarada?
- **Insegurança operacional.** A regra exige juízo casuístico em terreno onde o legislador escolheu critério objetivo, ou cria critério tão fluido que destrói previsibilidade?
- **Encadeamento de aplicações destrutivas.** A regra, aplicada coerentemente à classe de casos análogos, produz cascata de consequências cuja agregação é sistemicamente inaceitável?

Identificação de qualquer vetor sem declaração no output aciona `[CONSEQUÊNCIA SISTÊMICA NÃO DECLARADA]`.

**Passo 5 — Teste de coerência sistêmica.**
O o módulo de construção do raciocínio verifica se a regra é coerente com:

- Escolhas legislativas expressas (especialmente lei especial posterior, lei que regula o exato terreno coberto pela regra)
- Estrutura dos institutos jurídicos vizinhos
- Princípios constitucionais aplicáveis ao caso
- Outras regras jurídicas com as quais a regra proposta interage

Incoerência com escolha legislativa expressa aciona `[INCOERÊNCIA COM ESCOLHA LEGISLATIVA EXPRESSA]`.

**Passo 6 — Verificação da justificação da escolha de premissas.**
Para cada premissa relevante da decisão (norma escolhida, interpretação adotada, qualificação fática), o o módulo de construção do raciocínio verifica se o output justificou a escolha frente a premissas concorrentes. Premissas escolhidas sem justificação aciona `[ESCOLHA DE PREMISSA NÃO JUSTIFICADA]`.

**Passo 7 — Classificação e marcação.**
O o módulo de construção do raciocínio aplica o marcador canônico, classifica a severidade e registra o achado no formato padrão.

---

## 4. O QUE CONTA COMO ACHADO REAL

Achado real é qualquer instância em que a regra de decisão instaurada pelo output, se universalizada, falha em ao menos um dos três testes da justificação de segunda ordem, e o output não declarou esse problema.

**Exemplo operativo — memorial em ação revisional (caso de teste 28/05/2026).**

A peça sustenta: aplicação do CDC à relação de franquia por hipossuficiência técnica do aderente → nulidade da cláusula de royalty escalonado.

Regra implícita reformulada: *"todo contrato empresarial de adesão com hipossuficiência técnica do aderente atrai o regime do CDC, inclusive quando regido por lei especial posterior."*

Achados MacCormick:

- `[REGRA NÃO UNIVERSALIZÁVEL]` — universalizada, a regra alcança distribuição, representação comercial, fornecimento de software a pequenas empresas, contratos bancários empresariais, locação em shopping. Em todos esses casos, "hipossuficiência técnica" é a regra, não a exceção. A regra colapsa a fronteira B2B/B2C como categoria operacional.
- `[CONSEQUÊNCIA SISTÊMICA NÃO DECLARADA]` — esvaziamento da Lei 13.966/2019 (qual contrato de franquia *não* envolveria hipossuficiência técnica do franqueado individual?); reconfiguração casuística do regime de contrato de distribuição; substituição de critério objetivo por exame ad hoc em terreno onde o legislador escolheu regime objetivo.
- `[INCOERÊNCIA COM ESCOLHA LEGISLATIVA EXPRESSA]` — a Lei 13.966/2019 é escolha legislativa explícita de regime objetivo paritário para franquia, posterior ao CDC. A regra proposta contradiz frontalmente essa escolha sem reconhecê-la.

Severidade global: **Crítica**. Mesmo que a tese resistisse à objeção socrática (não resiste, mas suponhamos), a regra universalizada falharia em todos os três testes.

---

## 5. O QUE NÃO CONTA — ANTI-PADRÕES

**Conveniência política, econômica ou social ≠ achado MacCormick.**
"A regra é ruim para a economia", "favorece concentração", "prejudica trabalhadores" — todos fora do escopo. O eixo testa consequência jurídico-sistêmica, não consequência material.

**Discordância valorativa ≠ achado MacCormick.**
"A interpretação é injusta", "fere o princípio X" — crítica valorativa está fora do escopo.

**Tese inovadora bem justificada ≠ achado.**
Se o output declarou a regra que instaura, mediu suas consequências sistêmicas, e justificou a coerência, não há achado — ainda que se discorde da decisão.

**Decisão ad hoc legítima ≠ achado.**
Há casos em que a decisão é justificadamente irrepetível (situação juridicamente singular, exercício de equidade autorizado). O achado só ocorre quando o output trata como regra o que é *ad hoc*, ou trata como *ad hoc* o que necessariamente instaura regra.

**Consequência material declarada ≠ achado.**
Se o output reconhece efeito econômico ou social mas o trata como informativo, não como justificação jurídica, não há achado.

**Objeção pontual à tese ≠ achado MacCormick.**
Objeção direta à tese pertence EX002. O eixo MacCormick aceita momentaneamente a tese e ataca a regra que ela instituiria.

---

## 6. RÉGUA DE SEVERIDADE

| Nível | Critério | Consequência no gate |
|---|---|---|
| **Baixa** | Regra universalizável, mas escolha de premissa sem justificação explícita; consequência sistêmica menor e contornável. | Registro técnico. Sem bloqueio. |
| **Média** | Regra universalizável com dificuldade; consequência sistêmica identificável mas restrita; tensão moderada com regime jurídico próximo. | Nota de qualificação e *patch* argumentativo. |
| **Alta** | Regra de difícil universalização; consequência jurídico-sistêmica relevante não declarada; tensão clara com escolha legislativa expressa. | Bloqueio parcial. Exige reformulação, estreitamento da regra ou declaração explícita das consequências. |
| **Crítica** | Regra não universalizável em termos praticáveis; esvaziamento de regime legal expresso; incoerência frontal com escolha legislativa expressa; cascata destrutiva no sistema. | Bloqueio total ou nota de inviabilidade. |

A severidade depende da função da regra no output. Falha em regra lateral pode gerar nota técnica. Falha na regra que sustenta conclusão, voto, parecer, recomendação ou orientação estratégica aciona gate.


## 7. FORMATO DE OUTPUT ESPERADO

```
ACHADO — EIXO EX008 MACCORMICK | JUSTIFICAÇÃO DE SEGUNDA ORDEM

Conclusão central identificada:
[Tese ou recomendação central do output]

Regra implícita reformulada:
[Formulação da regra de decisão como norma geral]

Teste de universalizabilidade:
[A regra é formulável como norma? É praticável? Sobrevive à aplicação a casos análogos?]

Teste de consequência sistêmica:
[Que efeitos jurídico-sistêmicos a regra produz, se universalizada? — vetores: esvaziamento de regime,
reconfiguração de instituto, insegurança operacional, cascata destrutiva]

Teste de coerência:
[A regra é coerente com escolhas legislativas expressas, estrutura de institutos, princípios aplicáveis?]

Justificação da escolha de premissas:
[A escolha entre premissas concorrentes foi justificada pelo output? Em que medida?]

Natureza do problema:
[Descrição segundo a racionalidade do eixo — não é objeção à tese, é avaliação da regra que ela instaura]

Acionamento de gate:
[Sem bloqueio / Nota de qualificação / Bloqueio parcial / Bloqueio total]

Observação:
[Apenas se necessário: distinção em relação EX002, EX010, EX009; sinalização fora do eixo quando a crítica
real for valorativa e não sistêmica.]
```

---

## 8. OPERAÇÃO DENTRO DO o módulo de construção do raciocínio

**Ativação primária:**

- Fases que produzem ou revisam parecer com tese inovadora ou de fronteira
- Fases que produzem ou revisam voto, minuta decisória ou nota técnica que instaure orientação
- Fases que envolvem interpretação extensiva ou restritiva atípica
- Fases que aplicam princípio constitucional em terreno coberto por regra
- Fases que sustentam tese contra escolha legislativa expressa
- Fases que envolvem aplicação analógica de regime jurídico a domínio adjacente
- Fases que constroem solução em terreno de lacuna ou conflito de regras

**Ativação em elaboração.**
Na elaboração, o eixo MacCormick opera como protocolo prospectivo. Antes de redigir a conclusão, o o módulo de construção do raciocínio deve formular a regra que a conclusão instauraria, testá-la quanto a universalizabilidade, consequência sistêmica e coerência, e declarar o resultado dos três testes — ou estreitar a tese até que ela passe nos testes, ou abandonar a porta argumentativa.

**Ativação em revisão.**
Na revisão, o eixo MacCormick opera como auditoria de segunda ordem. Para cada conclusão central do output, o o módulo de construção do raciocínio reformula a regra implícita e aplica os três testes. Achados acionam marcadores e severidade.

**Par de confronto de raciocínios primário: MacCormick × EX002.**
É o par de fricção mais produtivo do eixo. Sócrates ataca a tese pontualmente: "esta tese cai por essa objeção". MacCormick aceita momentaneamente a tese e ataca a regra: "mesmo que a tese resistisse, a regra que ela cria não pode reger casos análogos". A fricção produz achado emergente: a tese precisa, simultaneamente, derrubar a objeção da lei especial (EX002) e formular uma regra suficientemente estreita para não destruir o sistema (MacCormick) — duas exigências que tendem a se anular mutuamente, porque a estreiteza necessária para passar em MacCormick enfraquece a generalidade necessária para passar em EX002.

Instrução para confronto:
> "Ative EX002 para identificar a objeção mais forte à tese. Em seguida — ou em paralelo — ative MacCormick para reformular a tese como regra universalizada e testá-la nos três planos. Tese que sobrevive EX002 mas falha em MacCormick exige reformulação ou declaração explícita. Tese que sobrevive a MacCormick mas cai em EX002 não chega ao teste sistêmico — EX002 é gate anterior."

**Par de confronto de raciocínios secundário: MacCormick × Circuito NORMA (EX010 / EX011 / EX009).**
Quando há conflito entre normas válidas, EX010 declara ambas válidas; EX011 indica qual é a razão protetora; EX009 tratEX009. MacCormick *escolhe* entre normas válidas com base nos três testes. O par opera em outputs com forte componente normativo: MacCormick supre o que o Circuito NORMA não decide — a justificação da escolha entre normas que o Circuito considera ambas operáveis.

**Par de confronto de raciocínios terciário: MacCormick × EX007.**
EX007 extrai a *o módulo de construção do raciocínio* do paradigma; MacCormick mede a regra que esta decisão instituiria como paradigma futuro. O par opera quando a aplicação do precedente *redefine* a *o módulo de construção do raciocínio* do paradigma — ato que precisa ser medido prospectivamente.

**Ativação secundária por sinalização.**
Outros eixos podem sinalizar necessidade de MacCormick quando identificarem:
- Tese inovadora com arquitetura toulminiana completa, mas alcance não declarado
- Conclusão que sobrevive à objeção socrática mas instaura regra ampla
- Aplicação de precedente que redefine seu alcance original (sinalizaçãEX007)
- Equiparação entre regimes que, se aceita, esvazia lei especial (sinalizaçãEX006)
- Interpretação em terreno de EX009 com consequência sistêmica não medida (sinalizaçãEX009)

---

## 9. DISTINÇÕES confronto de raciocíniosÍTICAS

### 9.1. Justificação de segunda ordem vs. EX002 (EX008 vs. EX002)

Sócrates ataca a tese. MacCormick ataca a regra que a tese instaura.

| | MacCormick | Sócrates |
|---|---|---|
| Pergunta | A regra universalizada sobrevive aos três testes? | A tese resiste à melhor objeção? |
| Unidade | Regra de decisão universalizada | Tese particular do output |
| Direção | Prospectiva (efeito sistêmico) | Retrospectiva/imediata (sustentação) |
| Convivência | Tese pode resistir a Sócrates e falhar em MacCormick — e vice-versa |

Erro comum: tratar problema de regra universalizada (MacCormick) como objeção direta (Sócrates). O ataque socrático é frontal; o ataque maccormickiano é lateral — aceita a tese e ataca o que ela cria.

### 9.2. Justificação de segunda ordem vs. EX010 (EX008 vs. EX010)

Kelsen testa validade formal. MacCormick testa justificação da escolha entre válidas.

| | MacCormick | Kelsen |
|---|---|---|
| Pergunta | Por que esta norma e não a outra, entre as válidas? | A norma é juridicamente válida? |
| Foco | Escolha entre opções legítimas | Validade da norma como tal |
| Convivência | Kelsen é gate anterior — não há escolha entre normas se nenhuma é válida |

### 9.3. Justificação de segunda ordem vs. EX011 (EX008 vs. EX011)

Raz identifica razão protetora. MacCormick mede coerência sistêmica.

| | MacCormick | Raz |
|---|---|---|
| Pergunta | A regra é coerente com o sistema? | A norma é razão protetora para a ação? |
| Foco | Conjunto do ordenamento | Função normativa da norma |
| Convivência | Raz pode identificar razão protetora; MacCormick pode reprovar a coerência sistêmica da aplicação |

### 9.4. Justificação de segunda ordem vs. EX009 (EX008 vs. EX009)

Hart tratEX009 na margem. MacCormick trata a regra mesmo no caso central.

| | MacCormick | Hart |
|---|---|---|
| Pergunta | A regra resultante é universalizável, consequente e coerente? | A norma cobre o caso da penumbra? |
| Foco | Regra construída pela decisão | Aplicação da norma a caso de indeterminação |
| Convivência | Hart pode reconhecer indeterminação; MacCormick avalia a regra escolhida para resolvê-la |

### 9.5. Justificação de segunda ordem vs. EX001 (EX008 vs. EX001)

Toulmin estrutura o argumento. MacCormick avalia a escolha das premissas.

| | MacCormick | Toulmin |
|---|---|---|
| Pergunta | A escolha entre premissas concorrentes foi justificada? | A tese tem EX001? |
| Foco | Justificação externa | Justificação interna |
| Convivência | Toulmin valida a arquitetura; MacCormick pode reprovar a escolha das premissas que ela articulou |

### 9.6. Justificação de segunda ordem vs. EX007 (EX008 vs. EX007)

Levi olha para o paradigma. MacCormick olha para o paradigma futuro.

| | MacCormick | Levi |
|---|---|---|
| Pergunta | A regra que esta decisão instaura sobrevive aos testes? | A *o módulo de construção do raciocínio* do paradigma foi corretamente extraída? |
| Direção | Prospectiva | Retrospectiva |
| Convivência | Levi pode aprovar a extração da *o módulo de construção do raciocínio*; MacCormick pode reprovar a regra resultante de aplicar essa *o módulo de construção do raciocínio* ao caso atual |

### 9.7. MacCormick vs. Bion (EX008 vs. EX004)

Bion controla honestidade epistêmica. MacCormick controla honestidade normativa.

| | MacCormick | Bion |
|---|---|---|
| Pergunta | A regra que a decisão instaura foi declarada e testada? | A incerteza presente no output foi declarada? |
| Foco | Honestidade sobre a regra instaurada | Honestidade sobre o que não se sabe |
| Convivência | Output pode declarar toda incerteza relevante (Bion aprova) e ainda instaurar regra cujo alcance não foi medido (MacCormick rejeita) |

### 9.8. MacCormick vs. Matte-Blanco (EX008 vs. EX006)

Matte-Blanco detecta colapso entre categorias. MacCormick testa a regra universalizada.

| | MacCormick | Matte-Blanco |
|---|---|---|
| Pergunta | A regra universalizada é praticável, consequente e coerente? | A equiparação apagou distinção juridicamente relevante? |
| Unidade | Regra prospectiva da decisão | Equivalência operacional entre categorias |
| Convivência | Output pode formular regra universalizável (sem achado MacCormick) e ainda colapsar distinção de regime nos efeitos (achado Matte-Blanco) |

**Lacunas remanescentes:** distinções com EX003 e EX005 a fechar quando todas as fichas estiverem consolidadas.

---

## 10. CHECKLIST DE FALHA DE EXECUÇÃO

O eixo falhou quando:

- [ ] O o módulo de construção do raciocínio confundiu objeção direta (EX002) com teste sistêmico (MacCormick)
- [ ] O o módulo de construção do raciocínio usou critério de conveniência política, econômica ou social como achado MacCormick (deslizamento para fora do eixo)
- [ ] O o módulo de construção do raciocínio formulou regra universalizada artificialmente estreita para preservar a tese
- [ ] O o módulo de construção do raciocínio formulou regra universalizada artificialmente ampla para forçar falha sistêmica
- [ ] O o módulo de construção do raciocínio confundiu consequência material com consequência jurídico-sistêmica
- [ ] O o módulo de construção do raciocínio classificou tese inovadora como problema sem aplicar os três testes
- [ ] O o módulo de construção do raciocínio ignorou escolha legislativa expressa posterior na avaliação de coerência
- [ ] O o módulo de construção do raciocínio tratou decisão legitimamente *ad hoc* como instauração de regra
- [ ] O o módulo de construção do raciocínio tratou instauração de regra como decisão *ad hoc*
- [ ] O o módulo de construção do raciocínio acionou MacCormick em terreno onde a tese é puramente subsuntiva (sem escolha entre premissas)
- [ ] O output avançou com achado Alta ou Crítica sem resolução de gate

