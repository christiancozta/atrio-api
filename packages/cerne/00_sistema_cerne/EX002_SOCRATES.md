# FICHA INSTRUCIONAL — EIXO EX002 DIALÉTICA

**Código:** EX002
**Nome do método:** Dialética
**Arquiteto-pai:** Sócrates

---

## 0. NÚCLEO EXECUTIVO

*Bloco imperativo — colável diretamente no Roteiro Operacional do módulo de construção do raciocínio.*

---

**EIXO EX002 — DIALÉTICA**

**Pergunta operacional:**
> A tese substantiva deste output sobrevive à objeção mais forte disponível, ou se desestabiliza sob confronto adversarial?

**Sequência operacional:**

1. Identificar afirmações com peso estrutural no output
2. Declarar o pressuposto central que sustenta cada afirmação
3. Formular a objeção mais forte que o output não enfrentou
4. Testar se a afirmação sobrevive à objeção
5. Classificar resultado: estabilização, não-estabilização, objeção não enfrentada ou conclusão prematura
6. Selecionar achados com consequência estrutural
7. Declarar a tensão sem sintetizar
8. Classificar severidade
9. Acionar gate quando Alta ou Crítica

**Testes binários de entrada:**

| Termo | Critério |
|---|---|
| Afirmação substantiva | Se esta afirmação for retirada, conclusão, ônus, risco ou enquadramento muda? Sim → entra. Não → não entra, ainda que tecnicamente correta. |
| Objeção mais forte | A objeção (a) ataca o pressuposto central, (b) é juridicamente sustentável, (c) produz consequência real se procedente, (d) não foi respondida no próprio texto? Os quatro presentes → marca. Algum ausente → não marca. |
| Objeção disponível | A objeção é fundada no módulo de validação de fontes, nos fatos apresentados, no regime jurídico aplicável, em precedente relevante ou em controvérsia jurídica reconhecível? Sim → entra. Especulativa, remota ou desvinculada do material → não entra. |

**Marcadores canônicos:**

| Marcador | Status |
|---|---|
| `[TESE NÃO ESTABILIZADA]` | core |
| `[OBJEÇÃO NÃO ENFRENTADA]` | core |
| `[CONCLUSÃO PREMATURA]` | core |

Os três marcadores operam em paridade — o que varia é a severidade.

**Regras de não-acionamento:**

- Objeção que o output já respondeu adequadamente → não marca
- Objeção periférica sem consequência estrutural → não marca (é comentário editorial)
- Balanço falso ("o output tem pontos fortes e fracos") → não marca; é ausência de achado
- Síntese automática ("considerando os dois lados, conclui-se que...") → não marca; é movimento proibido do eixo
- Estrutura argumentativa incompleta → não é EX002 primário; sinalizar EX001
- Hipótese apresentada como dedução → não é EX002 primário; sinalizar EX003
- Apagamento de incerteza no estado do domínio → sinalizar EX004
- Pré-compreensão interpretativa não declarada → sinalizar EX005

**Regra absoluta do eixo:**
O eixo termina em aporia declarada quando a tese não se estabilizar. Nunca em síntese. Quando a tese sobreviver ao teste, o eixo registra estabilização crítica e encerra.

**Ponto cego declarado:**
EX002 opera sobre resistência da tese à objeção estrutural disponível. Não verificEX001 (EX001), não controla tipo de inferência (EX003), não detecta apagamento de incerteza (EX004), não verifica pré-compreensão interpretativa (EX005).

---

## 0.1 PROMPTS OPERACIONAIS CANÔNICOS

*Bloco de governança interna. Os prompts abaixo são as chaves de pesquisa validadas para acionar a operação do eixo em IA externa, mantendo opacidade do framework. A operação dialética é traduzida em linguagem jurídica direta, sem nomear a tradição.*

**Termos de ativação interna sugeridos:**
- Principal: `Sócrates` (uso restrito ao projeto) e `dialético`/`dialética` (compatível com uso público)
- Compostos discriminantes: `objeção mais forte`, `teste do pressuposto central`, `construção adversarial`
- Vetados: `objeção` isolado, `crítica` isolado, `contraditório` isolado (todos comuns demais no vocabulário jurídico)

---

### EX002-PEC — Peça processual

**Status:** validado em Teste confronto de raciocínios 01
**Histórico:** rodado em NotebookLM + Perplexity sobre trecho de petição inicial trabalhista (motorista de plataforma / vínculo empregatício)

```
Você vai analisar o trecho jurídico anexado.

Sua tarefa é construir a melhor objeção possível contra a tese central
do texto. Coloque-se na posição de um adversário competente, bem
informado, com interesse legítimo em refutar a tese — um advogado
experiente da parte contrária.

Identifique:

(i) qual é, com precisão, a tese principal sustentada pelo texto;
(ii) qual seria o argumento mais forte que esse adversário apresentaria
     contra essa tese — não objeções fracas ou triviais, mas a melhor
     contraposição disponível;
(iii) quais fatos, normas, precedentes ou interpretações alternativas
      esse adversário invocaria para fundamentar a objeção;
(iv) que ponto do texto fica vulnerável a essa objeção;
(v) se o texto enfrenta essa objeção em algum momento, ou se a ignora
    completamente.

Não avalie a estrutura formal do argumento — avalie se a tese sobrevive
à melhor contraposição que se pode construir contra ela.
```

---

### EX002-CON — Cláusula contratual

**Status:** validado em Testes confronto de raciocínios 02 e confronto de raciocínios 03
**Histórico:** rodado em ChatGPT + Perplexity sobre cláusula de não-concorrência; rodado em ChatGPT sobre cláusula SaaS/LGPD

```
Você vai analisar a cláusula contratual anexada.

Sua tarefa é construir a pior interpretação adversarial possível contra
a cláusula. Coloque-se na posição de um advogado competente da parte
restringida pela cláusula, em momento futuro de litígio ou
renegociação, com interesse legítimo em desconstruir, atenuar ou
neutralizar a obrigação imposta.

Identifique:

(i) qual é, com precisão, o efeito jurídico que a cláusula pretende
    produzir;
(ii) qual seria o argumento mais forte que esse adversário apresentaria
     para invalidar, limitar ou afastar a aplicação dessa cláusula;
(iii) que normas, princípios, doutrina ou precedentes esse adversário
      invocaria para fundamentar essa desconstrução;
(iv) que ponto específico da redação fica mais vulnerável a essa
     desconstrução;
(v) se a cláusula prevê alguma defesa contra essa leitura adversarial,
    ou se a deixa exposta.

Não avalie a estrutura formal da cláusula — avalie se ela resiste à
melhor leitura adversarial que se pode construir contra ela.
```

---

### Lacunas de cobertura (objetos ainda sem prompt canônico)

| Objeto | Código previsto | Status |
|--------|-----------------|--------|
| Parecer jurídico              | EX002-PAR | A produzir |
| Nota técnica                  | EX002-NOT | A produzir |
| Output de IA jurídica externa | EX002-OUT | A produzir |
| Decisão judicial              | EX002-DEC | A produzir |

---

## 0.2 CLÁUSULA DE ATIVAÇÃO, CONTENÇÃO E DESCARTE

*Cláusula transversal de governança de fase. Aplicável a todas as fichas de eixo do módulo de construção do raciocínio.*

**Regra-mãe (acima da ficha):** *Achados transitam. Lentes não.*

Entre fases do módulo de construção do raciocínio, transferem-se apenas produtos estruturados da análise anterior: achados, marcadores, severidade, gates, pendências, restrições e versões corrigidas. O modo de raciocínio do eixo ativado não se transfere automaticamente para a fase seguinte.

**Cláusula específica do eixo EX002:**

Este eixo opera como lente temporária de confronto adversarial dentro da fase indicada do módulo de construção do raciocínio. Encerrada a fase, o modo elêntico — postura de objeção e produção de aporia — deve ser desativado. Apenas seus produtos formais — achados de não-estabilização, objeções não enfrentadas, conclusões prematuras, aporias operacionais declaradas, severidade e gate — podem ser transferidos para a etapa seguinte.

**Tratamento da aporia como achado exportável, não como atmosfera residual:**

Quando a tese não se estabilizar, o eixo exporta aporia operacional como achado classificado. A etapa seguinte deve tratar essa aporia como pendência, bloqueio ou zona de decisão humana, conforme severidade. Não deve continuar raciocinando em modo aporético salvo reativação expressa do eixo. Quando a tese sobreviver ao teste, o eixo registra estabilização crítica e encerra — não há produto adversarial residual a transmitir.

**Riscos específicos de contaminação por resíduo EX002:**

- *Refutação residual:* fase seguinte continua procurando objeções mesmo quando a operação devida é classificar achados, consolidar ou refinar texto.
- *Contaminação da entrega final:* refinamento textual fica defensivo, excessivamente ressalvado ou carregado de tensão não necessária; output final perde fluência operacional.
- *Captura de outros eixos:* EX003 (inferência), EX004 (EX004) ou EX005 (EX005) passam a operar como subtipos de objeção, perdendo autonomia conceitual.
- *Gate hipertrofiado:* qualquer tensão vira bloqueio, mesmo quando o achado correto seria nota de qualificação.

**Comportamento em confronto com outro eixo:**

EX002 não reinterpreta o achado alheio como objeção. Verifica apenas se há tese substantiva não estabilizada diante de objeção estrutural disponível. O eixo par mantém sua autonomia conceitual. EX002 também não reclassifica como objeção o que é falha de arquitetura (EX001), tipo errado de inferência (EX003) ou apagamento de incerteza (EX004).

**Comportamento na entrega final:**

A fase de refinamento textual recebe apenas marcadores não resolvidos e zonas de decisão humana registradas. Não recebe a postura adversarial nem a aporia como diretriz de tom. O refinamento editorial deve produzir texto operacional, não defensivo.

---

**Nota de modularidade indexada:**

Quando houver sinalização para eixo correlato, a ficha indica apenas o código do eixo (`EX00X`). A descrição completa do confronto, da ordem recomendada e do risco de dupla marcação deve ser consultada na `MATRIZ_DE_CONFRONTOS_INTER_EIXOS_EX.md`.

## 1. ARQUITETO-PAI

**Sócrates** (c. 470–399 a.C.)

Não Heráclito. Não Hegel.

Heráclito é o ancestral metafísico da dialética: descreveu a realidade como constituída por opostos em tensão produtiva, o logos como princípio de conflito. Mas Heráclito contempla a tensão — não a produz metodicamente sobre um objeto.

Hegel é o arquiteto da dialética moderna — tese, antítese, síntese. O a infraestrutura modular o exclui explicitamente: a Aufhebung (síntese) hegeliana, a síntese que sublima os opostos, é precisamente o que este eixo não deve fazer. Síntese prematura destrói o valor do método.

Sócrates é o arquiteto-pai porque fundou o único método que faz o que este eixo precisa fazer: **o elenchus** (refutação) — a refutação sistemática por objeção.

O elenchus socrático opera assim: toma uma afirmação como se fosse sólida, identifica seu pressuposto mais consequente, formula a objeção mais forte que o próprio interlocutor não antecipou, e expõe o ponto onde a afirmação não se sustenta. Sócrates não declara a tensão — ele a produz. E não a resolve: nos diálogos aporéticos, Sócrates termina sem conclusão.

Não é a única matriz teórica disponível para confronto adversarial — teoria da argumentação dialógica, lógica informal aplicada, retórica analítica oferecem caminhos compatíveis. Sócrates é adotado pela precisão do elenchus como gramática operacional, não por exclusividade teórica.

O eixo EX002 da infraestrutura modular é socrático porque:
1. produz a objeção mais forte, não a mais conveniente
2. testa o pressuposto, não apenas a superfície da afirmação
3. preserva a tensão — não sintetiza, não concilia, não equilibra
4. termina com o problema mais claro, não com a solução

---

## 2. O TRAÇADO FILOSÓFICO

O elenchus socrático tem uma sequência reconhecível:

1. **Aceitação provisória da tese** — a afirmação é tomada como se fosse verdadeira
2. **Identificação do pressuposto central** — o que precisa ser verdadeiro para que a afirmação se sustente?
3. **Formulação da objeção mais forte** — não a objeção óbvia, mas a que o autor da tese não enfrentou
4. **Teste de consistência** — a tese sobrevive à objeção? Ou colapsa, ou exige qualificação que o texto não oferece?
5. **Aporia** (impasse) — se a tese não sobrevive, o problema é declarado como aberto, não substituído por nova certeza

O que Sócrates nunca faz: aceitar que "tem razão dos dois lados" e seguir em frente.

No a infraestrutura modular, esse traçado se traduz em:

> Tomar cada afirmação substantiva do output como provisoriamente verdadeira → identificar o pressuposto que a sustenta → formular a objeção que o output não enfrentou → classificar o resultado.

---

## 3. A OPERAÇÃO DO EIXO

### Passo 1 — Leitura para identificação de afirmações substantivas

Ler o output integralmente antes de produzir qualquer achado. Identificar as afirmações que têm peso estrutural no argumento — não detalhes, não exemplos, mas as teses que sustentam as conclusões.

Perguntar: *se esta afirmação for falsa ou fraca, o que muda no output?* Se a resposta for "pouco ou nada", a afirmação não é substantiva o suficiente para entrar no eixo.

### Passo 2 — Identificação do pressuposto central de cada afirmação

Para cada afirmação substantiva, identificar o que precisa ser verdadeiro para que ela se sustente. O pressuposto central não está sempre explícito. Frequentemente é o que o output trata como dado — o que não precisou ser demonstrado porque parecia óbvio.

O eixo busca o **pressuposto central mais consequente** — não o ponto retoricamente mais fraco, mas aquele cuja queda altera o resultado.

### Passo 3 — Formulação da objeção mais forte

A objeção não é a crítica mais fácil. É a crítica que um oponente competente faria — aquela que o autor da afirmação deveria ter antecipado e não antecipou.

Critérios para a objeção mais forte:
- Ataca o pressuposto central, não a superfície
- É juridicamente sustentável — não é objeção retórica
- Produz consequência real se procedente — altera a conclusão, inverte o ônus, elimina um elemento
- Não foi respondida no próprio texto
- É disponível no contexto da tarefa: fundada no módulo de validação de fontes, nos fatos apresentados, no regime jurídico aplicável, em precedente relevante ou em controvérsia jurídica reconhecível. O eixo não exige objeções especulativas, remotas ou desvinculadas do material analisado.

Objeções fracas a evitar:
- "Poderia se argumentar que..." sem consequência estrutural
- Objeções que o próprio output já respondeu adequadamente
- Objeções que são verdadeiras mas periféricas ao argumento central

### Passo 4 — Teste de sobrevivência da afirmação

A afirmação sobrevive à objeção mais forte?

Três resultados possíveis:

**A) A afirmação colapsa** — o pressuposto não se sustenta sob a objeção. A afirmação é mais fraca do que o output declara.
Marcador: `[TESE NÃO ESTABILIZADA]`

**B) A afirmação não foi testada porque a objeção não foi enfrentada** — o output avança a conclusão sem responder à objeção disponível. O colapso é potencial, não demonstrado.
Marcador: `[OBJEÇÃO NÃO ENFRENTADA]`

**C) A afirmação fecha prematuramente** — a cadeia lógica que levaria da premissa à conclusão não foi percorrida; a conclusão chegou antes do argumento completar o trajeto.
Marcador: `[CONCLUSÃO PREMATURA]`

### Passo 5 — Não sintetizar

EX002 não produz balanço, não pondera os dois lados, não conclui que "há argumentos em ambos os sentidos." Esse seria o movimento hegeliano — e é o movimento proibido.

Se a objeção é forte e não foi respondida, o achado é declarado como problema. O produto exportável do eixo é a tensão classificada, não a sua resolução.

A zona de decisão humana é o destino correto de um achado conflitante — não a síntese automática.

---

## 4. O QUE CONTA COMO ACHADO REAL

Um achado EX002 é real quando:

- Ataca o pressuposto central, não um detalhe
- Tem consequência operacional: altera a solidez de uma tese central, inverte o ônus probatório, elimina um elemento jurídico, muda a recomendação
- Não foi respondido no próprio output
- É juridicamente sustentável — não é especulação, é argumento disponível

**Filtro de seleção:** selecionar apenas achados com consequência estrutural. Excluir achados tecnicamente corretos mas periféricos. Não há teto numérico fixo — o critério é qualitativo: cada achado retido deve responder positivamente à pergunta *"se esta objeção proceder, o que muda na conclusão, no ônus, no risco ou no enquadramento?"*

### Exemplos de achados reais (teste empírico — parecer trabalhista)

**Exemplo 1 — `[TESE NÃO ESTABILIZADA]`**

*Afirmação do output:* "A viabilidade da justa causa é alta."
*Pressuposto central:* os elementos do art. 482h estão preenchidos e os riscos são controláveis.
*Objeção mais forte:* o mesmo output estima risco de reversão em 30–45% na Seção V. Esse percentual não é consistente com "viabilidade alta." O output declara dois estados incompatíveis sem enfrentar a tensão.
*Consequência:* o cliente recebe avaliação de confiança que não corresponde ao risco real estimado no mesmo documento.
*Severidade:* **Alta** — altera a recomendação e o enquadramento de risco entregue ao cliente.

**Exemplo 2 — `[OBJEÇÃO NÃO ENFRENTADA]`**

*Afirmação do output:* a recusa com fundamento em LGPD só seria legítima "diante de demonstração concreta de risco ou ilegalidade da ferramenta" — ônus no empregado.
*Pressuposto central:* o ônus de provar violação LGPD é do empregado.
*Objeção mais forte:* o DPIA é obrigação do controlador (empregador), não do titular. A ausência de DPIA não exige que o empregado demonstre risco — exige que o empregador demonstre compliance. O output inverteu o ônus probatório sem enfrentar essa inversão.
*Consequência:* a estratégia de defesa recomendada está fundada em distribuição incorreta de ônus.
*Severidade:* **Crítica** — torna insustentável parte central da estratégia recomendada.

---

## 5. O QUE NÃO CONTA — ANTI-PADRÕES

**Anti-padrão 1 — Objeção já respondida ≠ achado.**
Se o próprio texto antecipou a objeção e a respondeu adequadamente, não há achado. O elenchus busca o que não foi enfrentado.

**Anti-padrão 2 — Objeção periférica ≠ achado.**
Se a objeção não altera conclusão, ônus, risco ou enquadramento, não marca. É comentário editorial, não achado dialético.

**Anti-padrão 3 — Balanço falso ≠ achado.**
"O output tem pontos fortes e pontos fracos" não é achado dialético. É ausência de achado disfarçada de análise.

**Anti-padrão 4 — Síntese automática ≠ produto do eixo.**
"Considerando os dois lados, pode-se concluir que..." é movimento proibido. O eixo declara o problema e para.

**Anti-padrão 5 — Falha estrutural ≠ falha de resistência.**
Se EX001 está incompleta, o problema primário é EX001. EX002 só opera sobre teses estruturalmente formadas.

**Anti-padrão 6 — Hipótese como dedução ≠ objeção não enfrentada.**
Se a falha é de tipo inferencial, o eixo primário é EX003.

**Anti-padrão 7 — Apagamento de incerteza ≠ objeção não enfrentada.**
Se a falha é de honestidade epistêmica sobre o estado do domínio, o eixo primário é EX004.

---

## 6. RÉGUA DE SEVERIDADE

| Severidade | Critério | Consequência no gate |
|---|---|---|
| **Baixa** | A objeção exige qualificação, mas não altera a conclusão central | Registrar; não aciona gate |
| **Média** | A objeção enfraquece parte relevante da fundamentação | Registrar com marcador; revisão recomendada |
| **Alta** | A objeção altera recomendação, risco, ônus, enquadramento ou conclusão | Acionar gate — retorno à etapa anterior ou `[NÃO AVANÇAR SEM REVISÃO HUMANA]` |
| **Crítica** | A objeção torna a conclusão principal insustentável ou contraditória com o próprio output | Bloquear avanço — `[NÃO AVANÇAR SEM REVISÃO HUMANA]` |

**Regra de gate:** achados Alta ou Crítica acionam obrigatoriamente revisão humana ou retorno à etapa anterior. A decisão de avanço não pode ser automática quando há achado EX002 ativo nessas faixas.

---

## 7. FORMATO DE OUTPUT ESPERADO

```text
ACHADO — EIXO EX002 | DIALÉTICA

ACHADO [número] — [trecho ou afirmação do output]
Marcador: [TESE NÃO ESTABILIZADA / OBJEÇÃO NÃO ENFRENTADA / CONCLUSÃO PREMATURA]
Pressuposto central: [o que precisa ser verdadeiro para a afirmação se sustentar]
Objeção mais forte: [formulação da crítica que o output não enfrentou]
Consequência operacional: [o que muda se a objeção proceder]
Severidade: [Baixa / Média / Alta / Crítica]

[repetir para cada achado com consequência estrutural]

SEVERIDADE MÁXIMA: [marcador do achado mais grave + consequência]
ACIONAMENTO DE GATE: [Sim / Não — se Sim, indicar achado e severidade]
ACHADOS ESPÚRIOS: [achados identificados mas sem consequência estrutural — registrar, não usar em gates]
```

O output do eixo EX002 não inclui:
- Elogios ao output auditado
- Ponderação entre achados e qualidades
- Conclusão sobre aprovação ou reprovação — essa é função do gate do módulo de construção do raciocínio, não do eixo

---

## 8. OPERAÇÃO DENTRO DO o módulo de construção do raciocínio

EX002 opera exclusivamente dentro do módulo de construção do raciocínio, na camada confronto de raciocínios. O o módulo de construção do raciocínio o ativa em etapas específicas dos Roteiros Operacionais conforme o tipo de tarefa.

### Roteiros com ativação primária

**RO_AUDITAR_OUTPUT_IA — Etapas E5 e E6**

E5 é a etapa de revisão crítica interna. E6 é a etapa de confronto entre eixos.

Instrução para E5:
> "Ative EX002 sobre o output produzido em E4. Para cada afirmação substantiva, identifique o pressuposto central, formule a objeção mais forte não enfrentada e classifique o achado. Não equilibre — declare o problema. Classifique a severidade. Acione gate se Alta ou Crítica."

Instrução para E6 (confronto com segundo eixo):
> "O produto de E6 é a matriz de tensões entre os achados de EX002 e do eixo par. Preserve os achados sem sintetizar. Declare convergências, exclusivos e conflitantes. Não resolva tensões conflitantes — encaminhe-as como zona de decisão humana."

**RO_REmecanismo interno de confrontoAR_PECA e RO_REmecanismo interno de confrontoAR_CONTRATO**

Ativação na etapa de verificação de coerência interna: o o módulo de construção do raciocínio testa se as afirmações substantivas da peça ou do contrato sobrevivem à objeção mais forte disponível.

### Operação em confronto com EX001

EX001 estrutura ou audita a arquitetura do argumento. EX002 opera depois, testando se a estrutura sobrevive à objeção mais forte. Não usar EX002 para suprir arquitetura ausente; não usar EX001 para resolver objeção não enfrentada.

---

## 9. DISTINÇÃO confronto de raciocíniosÍTICA — SÓCRATES VS. HEGEL NO a infraestrutura modular

| | Sócrates (elenchus) | Hegel (dialética) |
|---|---|---|
| Movimento | Tese → objeção → aporia | Tese → antítese → síntese |
| Produto | Tensão preservada | Tensão resolvida |
| Conclusão | O problema ficou mais claro | Uma nova verdade emergiu |
| No a infraestrutura modular | **Modelo correto** | **Modelo proibido** |

Quando o o módulo de construção do raciocínio produz "por outro lado... considerando ambas as perspectivas... pode-se concluir que...", está fazendo Hegel, não Sócrates. Isso é falha de execução do eixo.

*Lacuna sinalizada:* distinções operacionais com EX001, EX003, EX004 e EX005 ainda não escritas em tabela comparativa. A serem incorporadas em ciclo posterior, com base na auditoria externa dos demais eixos.

---

## 10. CHECKLIST DE FALHA DE EXECUÇÃO

O eixo falhou quando o o módulo de construção do raciocínio:

- [ ] Ponderou os dois lados em vez de formular objeção estrutural
- [ ] Sintetizou a tensão em conclusão reconciliadora
- [ ] Produziu crítica sem identificar o pressuposto central atacado
- [ ] Apontou problema sem consequência operacional declarada
- [ ] Confundiu objeção forte com comentário editorial
- [ ] Produziu achados sem classificar severidade
- [ ] Não acionou gate diante de achado de severidade Alta ou Crítica
- [ ] Incluiu elogio ou balanço positivo no output do eixo
- [ ] Resolveu a tensão ao invés de declará-la como zona de decisão humana
- [ ] Formulou objeção especulativa, remota ou desvinculada do material analisado

---

*a infraestrutura modular 1.0 — Camada confronto de raciocínios / o módulo de construção do raciocínio | EixEX002 — Dialética*
*Documento interno. Não transversal ao ecossistema.*
