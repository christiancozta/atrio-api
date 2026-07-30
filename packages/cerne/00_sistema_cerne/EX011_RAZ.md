# FICHA INSTRUCIONAL — EIXO EX011 AUTORIDADE PRÁTICA (RAZ)

**Código:** EX011
**Nome do método:** Autoridade Prática
**Arquiteto-pai:** Joseph Raz

---

## 0. NÚCLEO EXECUTIVO

*Bloco imperativo — colável diretamente no Roteiro Operacional do módulo de construção do raciocínio.*

---

**EIXO EX011 — AUTORIDADE PRÁTICA (RAZ)**

**Pergunta operacional:**
> Que fonte este output tratou como autoridade suficiente — e essa autoridade realmente possui força prática para sustentar a conclusão, recomendação ou decisão?

**Sequência operacional:**

1. Identificar as autoridades mobilizadas pelo output (normas, precedentes, doutrina, atos administrativos, manuais, fontes técnicas, práticas institucionais).
2. Classificar a natureza de cada autoridade.
3. Verificar se a força declarada no output corresponde à categoria da autoridade.
4. Verificar aplicabilidade da autoridade ao caso concreto (analogia fática, ratio decidendi, contexto vigente).
5. Verificar autoridades concorrentes de peso superior, especial ou vinculante eventualmente omitidas.
6. Verificar declaração de razão excludente, quando aplicável.
7. Aplicar marcador, classificar severidade, registrar no formato padrão.

**Testes binários de entrada:**

| Critério | Entra? |
|---|---|
| O output usa precedente, súmula, tese repetitiva ou decisão judicial como fundamento? | Se sim → entra |
| O output mobiliza doutrina, enunciado, parecer técnico ou nota institucional? | Se sim → entra |
| O output usa prática administrativa, manual, orientação interna ou padrão de mercado como suporte decisório? | Se sim → entra |
| O output trata fonte persuasiva como se eliminasse controvérsia? | Se sim → entra |
| O problema é validade formal, vigência ou competência da fonte? | Se sim → não entra (domínio de EX010) |
| O problema é interpretação do texto do precedente? | Se sim → não entra (domínio de EX005) |
| O problema é estrutura argumentativa (claim/warrant/backing)? | Se sim → não entra (domínio de EX001) |
| O problema é abertura textual do conceito? | Se sim → não entra (domínio de EX009) |

**Marcadores canônicos:**

| Marcador | Status | Uso |
|---|---|---|
| `[AUTORIDADE INAPLICÁVEL]` | core | Fonte não se conecta adequadamente ao caso (sem analogia fática, doutrina deslocada, tribunal irrelevante) |
| `[AUTORIDADE SUPERESTIMADA]` | core | Fonte aplicável recebeu força maior do que possui |
| `[FONTE PERSUASIVA COMO VINCULANTE]` | core | Decisão isolada, doutrina, enunciado, prática institucional ou orientação administrativa tratada como se vinculasse ou eliminasse controvérsia |
| `[AUTORIDADE NÃO HIERARQUIZADA]` | core | Fontes concorrentes de pesos distintos colocadas no mesmo plano ou superior omitida |
| `[RAZÃO EXCLUDENTE NÃO DECLARADA]` | core | Autoridade efetivamente vinculante citada sem explicitar seu efeito excludente, condições de incidência ou possibilidade de distinção |

**Regras de não-acionamento:**

- Se a fonte persuasiva foi apresentada com linguagem adequada de reforço ("a doutrina também sustenta", "há apoio doutrinário", "a posição encontra respaldo"), então não marca.
- Se o problema é validade formal ou vigência, então não marca; sinalizar EX010.
- Se o problema é leitura do precedente ou da ratio decidendi (a razão de decidir do julgado), então não marca como Raz isoladamente; sinalizar EX005, eventualmente em par.
- Se a hierarquia implícita é reconstruível e a conclusão não é afetada, então não marca.
- Se o output não exige autoridade vinculante para o tipo de entrega (parecer estratégico, nota técnica de risco), então não marca por ausência de fonte máxima.
- Se a citação foi omitida mas a regra invocada é conhecida e estável, então não marca como ausência de autoridade.

**Regra de fronteira "razão excludente":**

> `[RAZÃO EXCLUDENTE NÃO DECLARADA]` aplica-se quando uma autoridade efetivamente vinculante ou institucionalmente obrigatória é mobilizada sem explicitar seu efeito sobre razões concorrentes, nem as hipóteses de distinção, superação ou inaplicabilidade. Não confundir com `[FONTE PERSUASIVA COMO VINCULANTE]`, que é o defeito inverso: fonte não vinculante apresentada como se eliminasse controvérsia.

**Ponto cego declarado:**

O eixo não controla validade formal, vigência, competência ou hierarquia normativa em sentido estrito (domínio de EX010). Não testa a arquitetura interna do argumento (domínio de EX001). Não verifica se o precedente foi interpretado a partir de seu contexto (domínio de EX005). Não avaliEX009 de conceito (domínio de EX009). Raz opera sobre o peso prático das autoridades mobilizadas: que razão elas fornecem, com que força e contra quais razões concorrentes.

---

## 0.1 PROMPTS OPERACIONAIS CANÔNICOS

**Termos de ativação interna sugeridos:**

- Principal: "Raz" (uso restrito ao projeto); "autoridade prática" (uso público); "peso prático da fonte"
- Compostos discriminantes: "razão excludente", "razão de segunda ordem", "fonte persuasiva como vinculante", "hierarquização de autoridades", "tese da justificação normal", "calibragem de peso"
- Vetados isoladamente: "autoridade", "peso", "fonte", "precedente", "vinculante" (comuns demais)

**Tabela de lacunas de cobertura:**

| Objeto | Código | Status | Prompt canônico |
|---|---|---|---|
| Peça processual | EX011-PEC | Pendente | — |
| Cláusula contratual | EX011-CON | Pendente | — |
| Parecer jurídico | EX011-PAR | Pendente | — |
| Nota técnica | EX011-NOT | Pendente | — |
| Output de IA jurídica externa | EX011-OUT | Pendente | — |
| Decisão judicial | EX011-DEC | Pendente | — |
| Precedente como argumento | EX011-PRE | Pendente | — |

---

## 0.2 CLÁUSULA DE ATIVAÇÃO, CONTENÇÃO E DESCARTE

**Regra-mãe (acima da ficha):**

> Achados transitam. Lentes não.
>
> Entre fases do módulo de construção do raciocínio, transferem-se apenas produtos estruturados da análise anterior: achados, marcadores, severidade, gates, pendências, restrições e versões corrigidas. O modo de raciocínio do eixo ativado não se transfere automaticamente para a fase seguinte.

**Cláusula específica do eixo EX011:**

Ao fim da fase em que o eixo Raz foi ativado, desativa-se o modo de calibragem de peso prático. Não permanece em fases subsequentes a tendência de hierarquizar fontes, requalificar autoridades ou exigir declaração de razão excludente. Permanecem como produtos exportáveis: marcadores aplicados, severidade registrada, classificação das autoridades, pendências sobre fontes concorrentes omitidas, ressalvas sobre força declarada e versão corrigida.

**Riscos específicos de contaminação por resíduo EX011:**

- Tendência a invadir o terreno de validade formal (EX010), tratando peso baixo como inexistência da fonte.
- Tendência a recalibrar peso em fases posteriores onde a autoridade já foi categorizada.
- Tendência a exigir hierarquização explícita onde a hierarquia é implícita e funcional.
- Tendência a converter problema de interpretação de precedente (EX005) em problema de peso prático.
- Tendência a tratar prestígio abstrato como peso operacional.

**Comportamento em confronto com outro eixo:**

Quando pareado com EX010 no Circuito NORMA, Raz opera depois. Não calibra peso de fonte formalmente inválida.

Quando pareado com EX005, Gadamer pode operar antes quando a autoridade é precedente ou texto interpretado. Raz calibra o peso de uma leitura já adequada.

Quando pareado com EX001, Toulmin identifica se há backing (sustentação de fundo); Raz avalia se o backing existente foi usado com peso correto.

Quando pareado com EX009, Raz precede Hart no Circuito NORMA (validade → peso → EX009).

**Comportamento na entrega final:**

À fase de refinamento textual transmitem-se apenas marcadores não resolvidos e qualificadores de força declarada ("orientação persuasiva", "decisão isolada", "tendência local", "tese vinculante salvo distinção"). Não transmite-se postura cognitiva de calibragem nem instrução de hierarquização.

---

**Nota de modularidade indexada:**

Quando houver sinalização para eixo correlato, a ficha indica apenas o código do eixo (`EX00X`). A descrição completa do confronto, da ordem recomendada e do risco de dupla marcação deve ser consultada na `MATRIZ_DE_CONFRONTOS_INTER_EIXOS_EX.md`.

## 1. ARQUITETO-PAI

Joseph Raz (1939–2022), filósofo do direito vinculado ao positivismo jurídico contemporâneo, conhecido por sua teoria da autoridade prática, das razões para ação e das razões excludentes, oferece uma matriz útil para compreender a autoridade como algo que não apenas adiciona uma razão ao conjunto das razões disponíveis, mas pode pretender substituir ou excluir certas razões de primeira ordem quando legitimamente aplicável. Outros caminhos seriam compatíveis (teorias inferencialistas da autoridade, teorias institucionais do precedente), mas a teoria raziana oferece a linguagem mais econômica para o o módulo de construção do raciocínio.

**Por que Raz e não outro?**

O problema que o eixo precisa capturar é específico: outputs jurídicos que citam autoridades sem calibrar o peso prático que elas realmente possuem. Em textos jurídicos produzidos por IA, é comum que fontes heterogêneas apareçam no mesmo plano: artigo de lei, precedente isolado, julgado antigo, súmula, tese repetitiva, doutrina, manual institucional, orientação administrativa e opinião técnica. A fluência do output pode converter essa heterogeneidade em falsa solidez decisória.

Raz é o arquiteto adequado porque sua teoria permite distinguir autoridade como simples reforço argumentativo, autoridade como razão prática relevante e autoridade como razão de segunda ordem capaz de limitar a deliberação sobre razões concorrentes. Essa distinção é central para outputs jurídicos produzidos por IA, nos quais fontes heterogêneas frequentemente aparecem no mesmo plano retórico. O eixo Raz impede que essa heterogeneidade seja convertida em falsa solidez decisória.

A diferença em relação aos demais eixos é precisa. EX010 controla se a fonte é válida dentro da estrutura normativa. Raz controla que peso prático essa fonte deve receber na deliberação jurídica. EX001 pergunta se a autoridade funciona como backing da garantia; Raz pergunta se esse backing foi superestimado ou mal hierarquizado. EX005 pergunta se o precedente ou texto foi interpretado corretamente; Raz pergunta se, mesmo corretamente lido, ele tem força suficiente para conduzir a conclusão.

---

## 2. O TRAÇADO FILOSÓFICO

**Razões de primeira ordem.**
Na teoria de Raz, razões de primeira ordem são razões comuns para agir ou decidir: fatos, consequências, interesses, finalidades, valores, riscos, vantagens, provas, circunstâncias do caso. No Direito, aparecem como elementos fáticos, argumentos de justiça, conveniência estratégica, impacto econômico, proteção de confiança, boa-fé, segurança jurídica e outros motivos substantivos.

**Razões de segunda ordem.**
Razões de segunda ordem são razões sobre como lidar com outras razões. Uma autoridade jurídica não é apenas mais um argumento ao lado dos demais; ela pode orientar o modo como o decisor deve tratar as razões de primeira ordem. Um precedente vinculante, por exemplo, não apenas recomenda uma conclusão: ele limita o espaço de deliberação do julgador ou do operador.

**Razão excludente** (razão protetora que afasta deliberação sobre razões concorrentes).
A ideia de razão excludente é central. Certas autoridades não apenas contam a favor de uma decisão, mas excluem ou reduzem a relevância de razões concorrentes que, em outro contexto, poderiam ser consideradas. Exemplo: uma tese vinculante do STF ou do STJ pode excluir a necessidade de reabrir discussão já estabilizada, salvo distinção, superação ou inaplicabilidade.

O problema jurídico-operacional ocorre quando o output trata uma autoridade persuasiva como se fosse razão excludente. Uma decisão isolada não elimina razões contrárias. Doutrina respeitável não vincula o julgador. Orientação administrativa pode informar risco prático, mas não necessariamente desloca a norma aplicável.

**Autoridade legítima e tese da justificação normal.**
Raz sustenta que uma autoridade é justificada quando ajuda o sujeito a conformar-se melhor às razões que já se aplicam a ele do que se deliberasse sozinho. Traduzido para o o módulo de construção do raciocínio: uma autoridade deve melhorar a decisão jurídica porque concentra, estabiliza ou qualifica razões relevantes. Se a fonte não tem relação adequada com o caso, não melhora a decisão; apenas cria aparência de lastro.

**Dependência e substituição.**
A autoridade legítima depende das razões que deveria refletir. Não é autoridade por ornamentação, prestígio ou frequência de citação. Ela só pode substituir a deliberação direta quando efetivamente incorpora razões relevantes para aquele caso. Precedente sem analogia fática, súmula fora do contexto, doutrina deslocada ou parecer técnico de domínio diverso não produzem autoridade prática suficiente.

**Tradução operacional.**
O traçado raziano aplica-se ao módulo de construção do raciocínio como protocolo de calibração do peso das fontes. A pergunta não é apenas "há autoridade?" A pergunta é: "que tipo de autoridade é esta, que razão ela fornece, que razões ela exclui, e sua força foi corretamente representada?"

---

## 3. A OPERAÇÃO DO EIXO

O o módulo de construção do raciocínio raciocina sob o eixo Raz na seguinte sequência:

**Passo 1 — Identificação das autoridades mobilizadas.**
O o módulo de construção do raciocínio localiza todas as fontes que o output usa para sustentar conclusão, recomendação, estratégia ou decisão. Devem ser identificadas, no mínimo:

- normas constitucionais, legais e infralegais;
- súmulas, teses vinculantes, repetitivos, repercussão geral e IRDR (Incidente de Resolução de Demandas Repetitivas);
- precedentes judiciais vinculantes ou persuasivos;
- decisões isoladas;
- doutrina;
- enunciados, jornadas, notas técnicas e pareceres;
- atos administrativos, regulamentos, manuais e orientações internas;
- práticas institucionais ou padrões de mercado;
- documentos técnicos externos ao Direito.

**Passo 2 — Classificação do tipo de autoridade.**
Para cada fonte, o o módulo de construção do raciocínio classifica a natureza da autoridade:

| Tipo de autoridade | Função prática |
|---|---|
| **Vinculante** | Reduz ou exclui deliberação contrária, salvo distinção, superação ou inaplicabilidade |
| **Normativa aplicável** | Fornece regra ou princípio aplicável, já estabilizado quanto à validade mínima por EX010 |
| **Persuasiva qualificada** | Orienta fortemente, mas não vincula |
| **Persuasiva comum** | Reforça argumentação, sem força decisória autônoma |
| **Técnica** | Informa premissas especializadas, mas não decide a consequência jurídica sozinha |
| **Institucional-administrativa** | Orienta prática, risco, governança ou procedimento, mas pode não vincular juridicamente |
| **Estratégica** | Informa conveniência de atuação, sem substituir fundamento jurídico |
| **Ilustrativa** | Exemplifica ou contextualiza, sem peso decisório próprio |

**Passo 3 — Verificação de força declarada.**
O o módulo de construção do raciocínio verifica se o output apresentou a fonte com força compatível com sua categoria.

Exemplos:
- tese vinculante pode ser tratada como razão forte, salvo distinção;
- decisão isolada não deve ser tratada como orientação consolidada;
- doutrina não deve ser tratada como fonte vinculante;
- parecer técnico não deve substituir juízo jurídico de validade;
- manual interno não deve prevalecer automaticamente sobre norma legal;
- prática de mercado não deve ser tratada como licitude.

Se a fonte recebe peso superior ao que possui, aciona `[AUTORIDADE SUPERESTIMADA]`.

**Passo 4 — Verificação de aplicabilidade ao caso.**
O o módulo de construção do raciocínio verifica se a autoridade mobilizada é aplicável ao caso concreto.

Para precedentes, exige-se ao menos:
- analogia fática;
- identificação da ratio decidendi (a razão jurídica que efetivamente decidiu o caso, distinta dos obiter dicta);
- tribunal competente ou relevante;
- contexto normativo ainda vigente;
- ausência de distinção material relevante.

Para normas, exige-se: pertinência temática; vigência aparente; competência da fonte; relação com os fatos; compatibilidade com norma superior ou especial, quando identificável.

Para doutrina e fontes técnicas, exige-se: pertinência ao problema jurídico específico; compatibilidade com o regime aplicável; distinção entre informação técnica e conclusão jurídica.

Ausência de aplicabilidade demonstrada aciona `[AUTORIDADE INAPLICÁVEL]`.

**Passo 5 — Verificação de autoridades concorrentes.**
O o módulo de construção do raciocínio verifica se há autoridades relevantes em sentido contrário ou de peso superior que foram omitidas, deslocadas ou tratadas no mesmo plano.

Quando houver conflito entre autoridades, o output deve hierarquizar:
- vinculante sobre persuasivo;
- especial sobre geral, quando aplicável;
- superior sobre inferior, dentro da estrutura normativa;
- mais recente sobre superado, quando houver mudança relevante;
- autoridade diretamente aplicável sobre autoridade análoga;
- razão institucional sobre conveniência retórica, quando vinculante ao procedimento.

Ausência de hierarquização aciona `[AUTORIDADE NÃO HIERARQUIZADA]`.

**Passo 6 — Verificação de razão excludente.**
O o módulo de construção do raciocínio verifica se o output declarou quando uma autoridade opera como razão excludente.

A pergunta é: esta fonte apenas reforça a conclusão ou pretende excluir razões concorrentes?

Se uma fonte persuasiva foi usada como se eliminasse controvérsia, aciona `[FONTE PERSUASIVA COMO VINCULANTE]`.

Se uma fonte vinculante foi citada sem declarar seu efeito excludente ou sem indicar possibilidade de distinção, aciona `[RAZÃO EXCLUDENTE NÃO DECLARADA]`.

**Passo 7 — Classificação e marcação.**
O o módulo de construção do raciocínio aplica o marcador canônico correspondente, classifica a severidade e registra o achado no formato padrão.

---

## 4. O QUE CONTA COMO ACHADO REAL

Achado real é qualquer instância em que o output mobiliza uma autoridade jurídica, institucional, técnica ou estratégica com peso prático inadequado, sem declarar seu tipo, sua força, sua aplicabilidade ou sua relação com autoridades concorrentes.

**Exemplo operativo — parecer jurídico com precedente isolado.**

O output afirma: "A jurisprudência reconhece a validade da cláusula, de modo que o risco de invalidação é reduzido."

A autoridade mobilizada é jurisprudencial. O o módulo de construção do raciocínio verifica a fonte. Se há apenas uma decisão isolada de tribunal local, sem demonstração de reiteração, analogia fática ou compatibilidade com tribunais superiores, o output superestimou a autoridade.

O problema não é citar a decisão. O problema é tratá-la como jurisprudência consolidada ou razão suficiente para reduzir o risco.

Marcadores possíveis:
- `[AUTORIDADE SUPERESTIMADA]`, se a decisão isolada foi apresentada como entendimento estável;
- `[AUTORIDADE INAPLICÁVEL]`, se os fatos do precedente não são análogos;
- `[AUTORIDADE NÃO HIERARQUIZADA]`, se havia orientação superior em sentido diverso omitida.

---

**Exemplos contrastivos:**

**Falso positivo — o que NÃO é achado Raz:**
Output que cita doutrina como reforço persuasivo, usando linguagem adequada: "a doutrina também sustenta", "há apoio doutrinário", "a posição encontra respaldo". A fonte não foi apresentada como vinculante nem decisiva. Não há achado.

**Zona cinzenta — autoridade persuasiva forte, mas não vinculante:**
Output que usa orientação reiterada de tribunal local em matéria não enfrentada por tribunal superior. Se o texto declara que se trata de orientação persuasiva relevante para risco local, sem tratá-la como tese vinculante, não há achado Raz. Se afirma que "o entendimento é pacífico" sem amostra ou sem ressalva, há `[AUTORIDADE SUPERESTIMADA]`.

**Versão corrigida — como transformar `[FONTE PERSUASIVA COMO VINCULANTE]` em output íntegro:**

> *Versão com achado:* "A decisão citada afasta a tese contrária."

> *Versão corrigida:* "A decisão citada reforça a tese, mas não possui força vinculante. Seu peso é persuasivo e depende da analogia fática com o caso. Para que a conclusão seja usada como orientação segura, é necessário verificar se há precedentes reiterados no mesmo sentido ou autoridade vinculante aplicável."

---

**Outros padrões que contam como achado real:**

- Output que trata julgado antigo como orientação atual sem verificar superação.
- Output que equipara doutrina a precedente vinculante.
- Output que usa prática administrativa como fundamento de validade jurídica.
- Output que cita súmula sem demonstrar pertinência temática.
- Output que invoca entendimento de tribunal incompetente ou distante do foro relevante como se fosse decisivo.
- Output que menciona tese de tribunal superior sem avaliar distinção fática.
- Output que usa fonte técnica para concluir questão jurídica sem mediação normativa.
- Output que coloca norma legal, regulamento interno e prática de mercado no mesmo plano decisório.
- Output que omite autoridade vinculante contrária ao argumento adotado.
- Output que afirma "jurisprudência pacífica" sem demonstrar estabilidade mínima.

---

## 5. O QUE NÃO CONTA — ANTI-PADRÕES

**Citação sem hierarquia explícita ≠ achado.**
Nem todo output precisa explicitar uma taxonomia completa das fontes. O achado só existe quando a ausência de hierarquização afeta a conclusão, a recomendação, o risco ou o enquadramento.

**Fonte persuasiva como reforço ≠ achado.**
Doutrina, decisões isoladas, enunciados ou orientações administrativas podem ser usados legitimamente como reforço. O problema surge quando são tratados como razão suficiente, conclusiva ou excludente.

**EX010 ≠ autoridade prática.**
Se o problema é competência, vigência, hierarquia formal ou validade da fonte, o eixo primário é EX010. Raz só incide quando a fonte é usada com peso prático inadequado.

**Interpretação de precedente ≠ peso do precedente.**
Se o output leu mal a ratio decidendi ou ignorou contexto fático, EX005 pode ser eixo primário. Raz incide quando, mesmo tomada a leitura como válida, a autoridade recebeu peso indevido.

**Argumento jurídico ≠ exigência de autoridade vinculante.**
Nem todo argumento jurídico depende de fonte vinculante. Há pareceres, estratégias, contratos e notas técnicas que operam com autoridade persuasiva ou técnica. O eixo exige que o peso seja declarado corretamente, não que todo argumento seja fundado em autoridade máxima.

**Ausência de citação ≠ ausência de autoridade.**
O output pode estar sustentado por regra normativa conhecida ou documento do caso sem citação formal. A questão raziana é o peso da autoridade mobilizada, não a forma citacional.

**Prestígio abstrato ≠ autoridade prática.**
Autoridade relevante não é a mais famosa. É a que melhor se aplica ao caso, à jurisdição, ao procedimento, ao risco e ao tipo de entrega. Doutrina prestigiosa pode ter baixo peso operacional se deslocada do problema.

---

## 6. RÉGUA DE SEVERIDADE

| Nível | Critério | Consequência no gate |
|---|---|---|
| **Baixa** | Fonte persuasiva ou técnica recebe peso levemente superior, mas sem alterar conclusão central; hierarquia implícita é reconstruível; aplicabilidade provável, embora pouco explicitada | Registro no output. Sem bloqueio. |
| **Média** | Autoridade relevante usada sem classificação adequada; decisão isolada apresentada como orientação forte; ausência de hierarquização afeta fundamento secundário; fonte aplicável, mas com força mal declarada | Registro com marcador. Nota de qualificação recomendada. |
| **Alta** | Fonte persuasiva tratada como vinculante; autoridade decisiva sem demonstração de aplicabilidade; autoridade concorrente de peso superior omitida; conclusão central depende de autoridade superestimada | Bloqueio parcial ou retorno à etapa anterior. |
| **Crítica** | Output estruturado sobre autoridade inexistente, inaplicável ou materialmente inferior a autoridade vinculante contrária; uso de fonte sem força excludente para eliminar controvérsia decisiva; recomendação estratégica ou decisória fundada em hierarquia de autoridades invertida | Bloqueio total ou nota de inviabilidade. |

A severidade depende da função da autoridade no output. Uma autoridade lateral mal calibrada pode gerar achado Baixo ou Médio. Uma autoridade que sustenta a conclusão central, a recomendação ao cliente, o voto ou a estratégia processual aciona gate quando mal classificada.

---

## 7. FORMATO DE OUTPUT ESPERADO

```text
ACHADO — EIXO EX011 RAZ | AUTORIDADE PRÁTICA

Marcador: [AUTORIDADE INAPLICÁVEL] / [AUTORIDADE SUPERESTIMADA] /
          [FONTE PERSUASIVA COMO VINCULANTE] /
          [AUTORIDADE NÃO HIERARQUIZADA] / [RAZÃO EXCLUDENTE NÃO DECLARADA]
Severidade: Baixa / Média / Alta / Crítica

Localização no output:
[Trecho exato ou identificação precisa do segmento]

Autoridade mobilizada:
[Norma, precedente, doutrina, orientação, parecer, prática, manual, fonte técnica etc.]

Tipo de autoridade:
[Vinculante / normativa aplicável / persuasiva qualificada / persuasiva comum /
 técnica / institucional-administrativa / estratégica / ilustrativa]

Força apresentada pelo output:
[Como o output tratou a fonte: decisiva, vinculante, reforço, orientação, exemplo etc.]

Força adequada:
[Peso correto da autoridade no caso]

Aplicabilidade ao caso:
[Demonstrada / insuficiente / ausente / dependente de verificação]

Autoridades concorrentes:
[Indicar se há autoridade superior, especial, vinculante ou contrária relevante]

Natureza do problema:
[Descrição do problema segundo a racionalidade do eixo]

Acionamento de gate:
[Sem bloqueio / Nota de qualificação / Bloqueio parcial / Bloqueio total]

Observação:
[Apenas se necessário: distinção de anti-padrão, sobreposição com outro eixo,
 informação relevante para o operador.]
```

---

## 8. OPERAÇÃO DENTRO DO o módulo de construção do raciocínio

**Ativação primária:**

- Fases que produzem parecer jurídico com precedentes, doutrina ou fontes normativas
- Fases que elaboram votos, minutas decisórias ou notas técnicas
- Fases que revisam fundamentação jurisprudencial
- Fases que avaliam estratégia processual com base em tendências decisórias
- Fases que classificam risco jurídico com apoio em autoridades externas
- Fases que estruturam tese jurídica com fontes concorrentes
- Fases que auditam peças com excesso de citação e baixa hierarquização

**Ativação em elaboração:**
O eixo Raz opera como fase de calibragem das fontes. Antes de usar uma autoridade como fundamento, o o módulo de construção do raciocínio deve classificar sua natureza, força, aplicabilidade e relação com autoridades concorrentes.

**Ativação em revisão:**
O eixo Raz opera como auditoria de peso. O o módulo de construção do raciocínio deve verificar se cada fonte foi apresentada com força adequada e se alguma autoridade de maior peso foi omitida, deslocada ou igualada indevidamente a fonte inferior.

**Ativação em confronto com EX010:**
Quando pareado com Kelsen, Raz deve operar depois da verificação mínima de validade formal da fonte.

> Instrução para confronto: "Ative Kelsen para verificar validade, competência, vigência e hierarquia normativa. Em seguida, ative Raz para calibrar o peso prático da autoridade válida ou existente. Não use Raz para sanar fonte formalmente inválida; não use Kelsen para decidir o peso prático de autoridade persuasiva."

**Ativação em confronto com EX005:**
Quando a autoridade é precedente, decisão, cláusula ou texto jurídico interpretado, Gadamer pode operar antes de Raz.

> Instrução para confronto: "Ative Gadamer para verificar se o texto ou precedente foi lido em seu horizonte adequado. Em seguida, ative Raz para verificar que força prática essa leitura pode receber no caso."

**Ativação no Circuito NORMA (EX010 → EX011 → EX009):**
Em outputs com forte componente normativo, a sequência canônica é Kelsen → Raz → Hart: validade formal, peso prático, EX009.

**Ativação secundária por sinalização:**
Outros eixos podem sinalizar necessidade de Raz quando identificarem:
- citação usada como fundamento conclusivo;
- precedente tratado como decisivo sem análise de aplicabilidade;
- doutrina usada como se vinculasse;
- fonte técnica deslocando juízo jurídico;
- ausência de distinção entre autoridade vinculante e persuasiva;
- conflito de fontes sem hierarquização.

---

## 9. DISTINÇÕES confronto de raciocíniosÍTICAS

### 9.1. Autoridade prática vs. EX010 (EX011 vs. EX010)

| | Raz | Kelsen |
|---|---|---|
| Pergunta | Que peso esta autoridade deve receber na decisão? | Esta fonte é válida, competente e hierarquicamente aplicável? |
| Unidade de análise | Fonte como razão prática | Norma como elemento do sistema jurídico |
| Defeito típico | Autoridade superestimada ou mal hierarquizada | Fonte inválida, incompetente, revogada ou hierarquicamente incompatível |
| Produto | Peso adequado da fonte | Estado formal da norma |
| Gate | Mau uso da autoridade | Falha de EX010 |

Uma fonte pode ser válida e receber peso inadequado. Uma fonte pode ser persuasiva e juridicamente útil sem possuir EX010 no sentido kelseniano.

### 9.2. Autoridade prática vs. EX001 (EX011 vs. EX001)

| | Raz | Toulmin |
|---|---|---|
| Pergunta | A autoridade usada como suporte tem peso adequado? | A tese possui dados, garantia, backing, qualificador e exceção? |
| Defeito típico | Fonte inferior tratada como decisiva | Peça argumentativa ausente |
| Correção | Reclassificar força da autoridade | Completar a estrutura argumentativa |
| Exemplo | Decisão isolada tratada como jurisprudência pacífica | Precedente citado sem regra de passagem para a tese |

Toulmin pode identificar que há backing ausente. Raz avalia se o backing existente foi usado com peso correto.

### 9.3. Autoridade prática vs. EX005 (EX011 vs. EX005)

| | Raz | Gadamer |
|---|---|---|
| Pergunta | Que peso esta fonte possui? | O texto da fonte foi interpretado adequadamente? |
| Defeito típico | Autoridade persuasiva como vinculante | Precedente lido sem contexto ou o módulo de construção do raciocínio |
| Foco | Peso prático | Processo interpretativo |
| Exemplo | Julgado local tratado como vinculante | Ementa tratada como substituto do acórdão |

Os eixos podem coexistir. Um precedente pode ser mal lido e, além disso, receber peso indevido.

### 9.4. Autoridade prática vs. EX004 (EX011 vs. EX004)

| | Raz | Bion |
|---|---|---|
| Pergunta | A autoridade foi calibrada corretamente? | A incerteza foi declarada? |
| Defeito típico | Fonte persuasiva apresentada como decisiva | Segurança não lastreada |
| Foco | Peso institucional e jurídico da fonte | Estado de certeza do output |
| Exemplo | "Jurisprudência pacífica" com base em um julgado | Percentual de risco sem metodologia |

Quando o output diz "jurisprudência pacífica" sem base, Raz verifica o peso da autoridade e Bion verifica se a certeza foi performada sem lastro.

### 9.5. Autoridade prática vs. EX009 (EX011 vs. EX009) — *lacuna*

Distinção provisória: Hart opera sobre EX009 do conceito (a zona de penumbra em que a linguagem normativa não fecha automaticamente); Raz opera sobre o peso prático da fonte que se mobiliza para preencher essa textura. Um precedente pode preencher zona de penumbra (caso Hart) e ainda assim receber peso indevido na cadeia decisória (caso Raz). Fechamento da distinção pendente.

### 9.6. Autoridade prática vs. EX003 (EX011 vs. EX003) — *lacuna*

Distinção provisória: Peirce opera sobre o tipo de inferência usada para concluir; Raz opera sobre o peso prático das fontes mobilizadas no caminho dessa inferência. Fechamento da distinção pendente.

---

## 10. CHECKLIST DE FALHA DE EXECUÇÃO

O eixo falhou quando:

- [ ] O o módulo de construção do raciocínio identificou fonte citada e não classificou seu tipo de autoridade
- [ ] O o módulo de construção do raciocínio tratou toda fonte jurídica como equivalente
- [ ] O o módulo de construção do raciocínio aceitou decisão isolada como jurisprudência consolidada sem verificação
- [ ] O o módulo de construção do raciocínio aceitou doutrina como se fosse autoridade vinculante
- [ ] O o módulo de construção do raciocínio não verificou se a autoridade era aplicável ao caso concreto
- [ ] O o módulo de construção do raciocínio não verificou analogia fática mínima em precedente usado como fundamento
- [ ] O o módulo de construção do raciocínio não diferenciou ratio decidendi de ementa ou reforço retórico
- [ ] O o módulo de construção do raciocínio ignorou autoridade concorrente de peso superior
- [ ] O o módulo de construção do raciocínio não declarou quando uma autoridade opera como razão excludente
- [ ] O o módulo de construção do raciocínio usou Raz para resolver problema de EX010 que pertence EX010
- [ ] O o módulo de construção do raciocínio usou Raz para resolver problema de interpretação que pertence EX005
- [ ] O o módulo de construção do raciocínio usou Raz para resolver problema de EX009 que pertence EX009
- [ ] O o módulo de construção do raciocínio classificou como achado fonte persuasiva corretamente apresentada como reforço
- [ ] O output avançou à fase seguinte com achado Alta ou Crítica sem resolução de gate
