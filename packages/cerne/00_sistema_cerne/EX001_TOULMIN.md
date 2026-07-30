# FICHA INSTRUCIONAL — EIXO EX001 ARQUITETURA ARGUMENTATIVA

**Código:** EX001
**Nome do método:** Arquitetura Argumentativa
**Arquiteto-pai:** Stephen Toulmin

---

## 0. NÚCLEO EXECUTIVO

*Bloco imperativo — colável diretamente no Roteiro Operacional do módulo de construção do raciocínio.*

---

**EIXO EX001 — ARQUITETURA ARGUMENTATIVA**

**Pergunta operacional:**
> A conclusão deste output está sustentada por uma arquitetura argumentativa completa ou apenas por encadeamento retórico?

**Sequência operacional:**

1. Identificar tese central
2. Mapear dados que a sustentam
3. Verificar garantia (regra de passagem entre dados e tese)
4. Verificar backing (apoio externo da garantia)
5. Verificar qualificador (força declarada da conclusão)
6. Verificar exceções (condições internas de derrota)
7. Classificar achado por marcador e severidade

**Testes binários de entrada:**

| Termo | Critério |
|---|---|
| Tese central | A queda da afirmação altera conclusão, ônus, risco ou enquadramento? Sim → entra. Não → não entra. |
| Exceção relevante | A hipótese é juridicamente reconhecível na matéria + previsível no caso concreto + capaz de alterar a tese central? Os três presentes → marca. Algum ausente → não marca `[EXCEÇÃO NÃO TRATADA]`. |
| Backing reconstruível | Há apoio documental, normativo, lógico ou metodológico identificável no material analisado? Sim → não marca `[BACKING AUSENTE]` por ausência de citação formal. Não → marca. |

**Marcadores canônicos e hierarquia:**

| Marcador | Status |
|---|---|
| `[GARANTIA NÃO DECLARADA]` | core |
| `[BACKING AUSENTE]` | core |
| `[DADO INSUFICIENTE]` | periférico |
| `[QUALIFICADOR SUPRIMIDO]` | periférico |
| `[EXCEÇÃO NÃO TRATADA]` | periférico |

Marcadores periféricos geram severidade reduzida por padrão, salvo impacto direto sobre a tese central.

**Regras de não-acionamento:**

- Peça argumentativa sintética mas reconstruível com segurança no próprio material → não marca `[GARANTIA NÃO DECLARADA]`
- Apoio documental/normativo/lógico/metodológico reconstruível → não marca `[BACKING AUSENTE]` por ausência de citação formal
- Hipótese de exceção remota ou periférica ao caso → não marca `[EXCEÇÃO NÃO TRATADA]`
- Estrutura completa + objeção forte não enfrentada → não é EX001, sinalizar EX002
- Hipótese apresentada como conclusão necessária → não é EX001, sinalizar EX003
- Estimativa numérica sem base metodológica → não é EX001 primário, sinalizar EX004
- Pré-compreensão interpretativa não declarada → sinalizar EX005

**Ponto cego declarado:**
EX001 opera sobre a anatomia do argumento (tese, dados, garantia, backing, qualificador, exceção). Não formula objeção (EX002), não controla tipo de inferência (EX003), não detecta apagamento de incerteza (EX004), não verifica pré-compreensão interpretativa (EX005).

---

## 0.1 PROMPTS OPERACIONAIS CANÔNICOS

*Bloco de governança interna. Os prompts abaixo são as chaves de pesquisa validadas para acionar a operação do eixo em IA externa, mantendo opacidade do framework. As traduções jurídicas dos conceitos operam sem nomear a tradição.*

**Termos de ativação interna sugeridos:**
- Principal: `Toulmin` (uso restrito ao projeto)
- Compostos discriminantes: `arquitetura argumentativa`, `decomposição tese-dados-garantia`, `garantia argumentativa`
- Vetados: `argumentativo` isolado, `estrutural` isolado, `análise de argumento` (todos comuns demais no vocabulário jurídico)

---

### EX001-PEC — Peça processual

**Status:** validado em Teste confronto de raciocínios 01
**Histórico:** rodado em NotebookLM + Perplexity sobre trecho de petição inicial trabalhista (motorista de plataforma / vínculo empregatício)
**Observação operacional:** NotebookLM vazou framework (citou "Toulmin", "backing", "warrant") — confirma necessidade de sanitização no Bloco 7 do prompt do módulo de construção do raciocínio

```
Você vai analisar o trecho jurídico anexado.

Sua tarefa é examinar a estrutura interna do argumento, e apenas isso.
Não avalie o conteúdo jurídico do ponto de vista de quem discorda da
tese; avalie se a arquitetura do argumento se sustenta por dentro.

Para cada afirmação que o texto apresenta como conclusão, verifique:

(i) os fatos ou dados que o próprio texto oferece como sustentação;
(ii) a justificativa que liga esses fatos à conclusão — por que esses
     fatos, especificamente, implicam essa conclusão e não outra;
(iii) a fonte, autoridade ou apoio externo que confirma essa
      justificativa;
(iv) o grau de força com que a conclusão é apresentada — é certeza,
     probabilidade, presunção?
(v) as exceções, ressalvas ou condições de afastamento que o argumento
    reconhece.

Aponte cada lacuna ou fragilidade estrutural que encontrar. Seja
específico: cite o trecho exato onde a lacuna aparece e descreva qual
elemento está faltando ou frouxo.
```

---

### EX001-CON — Cláusula contratual

**Status:** validado em Testes confronto de raciocínios 02 e confronto de raciocínios 03
**Histórico:** rodado em ChatGPT + Perplexity sobre cláusula de não-concorrência; rodado em ChatGPT sobre cláusula SaaS/LGPD
**Observação operacional:** opacidade mantida em todas as execuções; nenhum vazamento de framework

```
Você vai analisar a cláusula contratual anexada.

Sua tarefa é examinar a estrutura interna da cláusula, e apenas isso.
Não avalie a cláusula do ponto de vista de quem ela prejudica ou
favorece; avalie se a sua arquitetura interna se sustenta por dentro.

Para cada obrigação, restrição ou consequência prevista na cláusula,
verifique:

(i) os elementos que definem o alcance e o conteúdo da obrigação;
(ii) a justificativa interna que liga a obrigação à consequência
     prevista;
(iii) os critérios objetivos que permitiriam identificar, na prática,
      quando a obrigação foi cumprida ou descumprida;
(iv) o grau de força com que a cláusula é redigida — admite gradação,
     exceção, modulação, ou é absoluta?
(v) as condições de afastamento, ressalvas ou hipóteses de não
    aplicação que a cláusula reconhece;
(vi) a coerência interna entre as obrigações, prazos, definições e
     consequências da própria cláusula.

Aponte cada lacuna ou fragilidade estrutural que encontrar. Seja
específico: cite o trecho exato onde a lacuna aparece e descreva qual
elemento está faltando, indefinido ou frouxo.
```

---

### Lacunas de cobertura (objetos ainda sem prompt canônico)

| Objeto | Código previsto | Status |
|--------|-----------------|--------|
| Parecer jurídico              | EX001-PAR | A produzir |
| Nota técnica                  | EX001-NOT | A produzir |
| Output de IA jurídica externa | EX001-OUT | A produzir |
| Decisão judicial              | EX001-DEC | A produzir |

---

## 0.2 CLÁUSULA DE ATIVAÇÃO, CONTENÇÃO E DESCARTE

*Cláusula transversal de governança de fase. Aplicável a todas as fichas de eixo do módulo de construção do raciocínio.*

**Regra-mãe (acima da ficha):** *Achados transitam. Lentes não.*

Entre fases do módulo de construção do raciocínio, transferem-se apenas produtos estruturados da análise anterior: achados, marcadores, severidade, gates, pendências, restrições e versões corrigidas. O modo de raciocínio do eixo ativado não se transfere automaticamente para a fase seguinte.

**Cláusula específica do eixo EX001:**

Este eixo opera como lente temporária de decomposição argumentativa dentro da fase indicada do módulo de construção do raciocínio. Encerrada a fase, o modo decompositivo (tese-dados-garantia-backing-qualificador-exceção) deve ser desativado. Apenas seus produtos formais — achados estruturais, marcadores canônicos, severidade, gate e pendências de sustentação — podem ser transferidos para a etapa seguinte.

**Riscos específicos de contaminação por resíduo EX001:**

- *Decomposição residual:* fase seguinte continua mapeando tese-dados-garantia em afirmações secundárias sem peso operacional, gerando achados sem consequência.
- *Formalismo na entrega final:* refinamento textual passa a privilegiar visibilidade da arquitetura argumentativa quando o texto pediria fluência.
- *Captura de outros eixos:* problemas de objeção não enfrentada (EX002), apresentação de hipótese como dedução (EX003) ou apagamento de incerteza (EX004) passam a ser lidos como "garantia ausente" ou "backing fraco", esvaziando os eixos vizinhos.

**Comportamento em confronto com outro eixo:**

No confronto com EX002, EX001 opera primeiro e cessa antes da ativação de EX002. EX001 não classifica como achado o que pertence EX002 (objeção não enfrentada sobre estrutura íntegra). EX001 também não reabsorve achados de EX002 como falhas estruturais — a fragilidade diante de objeção é território de EX002, ainda que a estrutura argumentativa esteja completa.

**Comportamento na entrega final:**

A fase de refinamento textual recebe apenas marcadores não resolvidos e qualificadores de força adequada. Não recebe o esqueleto decompositivo como diretriz de reescrita. A arquitetura argumentativa interna do output revisado deve permanecer invisível à camada editorial.

---

**Nota de modularidade indexada:**

Quando houver sinalização para eixo correlato, a ficha indica apenas o código do eixo (`EX00X`). A descrição completa do confronto, da ordem recomendada e do risco de dupla marcação deve ser consultada na `MATRIZ_DE_CONFRONTOS_INTER_EIXOS_EX.md`.

## 1. ARQUITETO-PAI

Stephen Edelston Toulmin (1922–2009) foi filósofo britânico da argumentação, conhecido por deslocar a análise lógica do modelo formal abstrato para o funcionamento real dos argumentos em contextos práticos. Sua contribuição central, especialmente em *The Uses of Argument*, é a ideia de que argumentos não se sustentam apenas por forma lógica, mas por uma arquitetura composta por elementos distinguíveis: tese, dados, garantia, backing, qualificador e exceção.

**Por que Toulmin e não outro?**

O problema que o eixo precisa capturar é específico: outputs jurídicos que parecem bem fundamentados porque apresentam linguagem técnica, citações ou progressão discursiva, mas cuja arquitetura interna está incompleta. O texto conclui, mas não mostra adequadamente de que dados parte; invoca dados, mas não declara a garantia que permite passar deles à tese; declara uma garantia, mas não demonstra seu apoio normativo ou jurisprudencial; apresenta conclusão forte sem qualificador; ou ignora exceções que limitariam a conclusão.

Toulmin é o arquiteto adequado porque sua teoria permite decompor o argumento em peças auditáveis. A pergunta não é apenas "há fundamento?", mas "qual peça da estrutura argumentativa está ausente, fraca ou deslocada?" Não é a única matriz teórica disponível para auditoria estrutural de argumento — lógica informal, teoria da argumentação, retórica analítica oferecem caminhos compatíveis. Toulmin é adotado pela precisão de sua gramática operacional, não por exclusividade teórica.

Em termos operacionais, EX001 produz mapa estrutural auditável a partir do argumento apresentado.

---

## 2. O TRAÇADO FILOSÓFICO

**Claim (tese).**
Todo argumento possui uma afirmação que pretende fazer o leitor aceitar algo: uma conclusão jurídica, uma recomendação, uma qualificação, uma invalidação, uma estratégia, uma interpretação. No o módulo de construção do raciocínio, a tese é a unidade de risco central: se ela não estiver sustentada, o output inteiro pode parecer correto sem sê-lo.

**Data (dados).**
Os dados são aquilo que o argumento oferece como base imediata da tese: fatos do caso, documentos, cláusulas, dispositivos normativos, precedentes, trechos de decisão, elementos probatórios ou premissas já estabelecidas. Sem dados suficientes, a tese fica suspensa.

**Warrant (garantia).**
A garantia é a ponte entre os dados e a tese. Ela explica por que aqueles dados autorizam aquela conclusão. No Direito, a garantia costuma aparecer como regra jurídica, critério interpretativo, estrutura dogmática, orientação jurisprudencial, standard probatório ou princípio aplicável.

O problema mais comum em outputs de IA jurídica não é ausência total de dados. É dado sem garantia: o texto mostra fatos e conclui, mas não explicita a regra de passagem.

**Backing (apoio).**
O backing é o suporte da própria garantia. Uma garantia pode parecer plausível, mas precisa estar apoiada em fonte adequada: norma vigente, precedente aplicável, doutrina reconhecida, documento do caso, prática institucional ou matriz metodológica declarada. O backing responde à pergunta: por que essa garantia pode ser usada aqui?

**Qualifier (qualificador).**
O qualificador indica a força da tese: necessariamente, provavelmente, em princípio, salvo melhor prova, em tese, com alta plausibilidade, de modo preliminar, sob determinado enquadramento. Em Direito, quase toda conclusão depende de condições. A supressão do qualificador transforma argumento situado em afirmação absoluta.

**Rebuttal (exceção).**
A exceção indica quando a tese deixaria de valer. Não é objeção adversarial em sentido forte; é a condição interna de limitação do próprio argumento. Exemplo: "a cláusula é válida, salvo se demonstrada abusividade concreta"; "a tese se sustenta, desde que o precedente seja analogicamente aplicável"; "a recomendação depende de confirmação documental."

---

## 3. A OPERAÇÃO DO EIXO

**Passo 1 — Identificação da tese.**
O o módulo de construção do raciocínio localiza a conclusão que o output pretende sustentar. A tese pode estar expressa como recomendação, enquadramento jurídico, juízo de validade, avaliação de risco, proposta de estratégia, interpretação de cláusula, conclusão sobre responsabilidade ou orientação ao operador. Se não houver tese identificável, registra problema de arquitetura global: o output não possui centro argumentativo auditável.

**Passo 2 — Separação dos dados.**
O o módulo de construção do raciocínio identifica quais dados sustentam a tese. Teste: se estes dados forem retirados, a tese ainda se sustenta? Se sim, os dados não eram estruturais. Se não, eles devem ser mapeados e avaliados quanto à suficiência.

**Passo 3 — Verificação da garantia.**
O o módulo de construção do raciocínio verifica se o output declarou a regra de passagem entre dados e tese. A garantia responde: por que estes dados autorizam esta conclusão?

Exemplos:
- Dados sobre subordinação, habitualidade e pessoalidade só levam à tese de vínculo empregatício se a garantia jurídica trabalhista for declarada.
- A existência de precedente só leva à aplicação ao caso se houver garantia de analogia fática e ratio decidendi aplicável.
- Uma cláusula contratual só leva à conclusão de validade se a garantia de autonomia privada, equilíbrio contratual ou ausência de abusividade for declarada.

Ausência de garantia aciona `[GARANTIA NÃO DECLARADA]`.

**Passo 4 — Verificação do backing.**
O o módulo de construção do raciocínio verifica se a garantia possui apoio. A garantia pode estar declarada, mas sem base suficiente.

Exemplos:
- "A jurisprudência admite essa tese" é garantia aparente. O backing exige indicar que jurisprudência, de qual tribunal, em que contexto, com que grau de estabilidade.
- "A cláusula é válida pela autonomia privada" é garantia. O backing exige fonte normativa, matriz contratual e ausência de incidência de regime protetivo que limite essa autonomia.
- "A conduta configura falta grave" é garantia. O backing exige norma, precedente, regulamento aplicável ou standard disciplinar reconhecido.

Ausência de backing aciona `[BACKING AUSENTE]`.

**Passo 5 — Verificação de qualificador.**
Conclusões juridicamente condicionadas não devem aparecer como absolutas. Quando a tese depende de prova, confirmação documental, analogia jurisprudencial, interpretação controvertida, enquadramento fático ou estado do domínio, deve haver qualificador. Ausência aciona `[QUALIFICADOR SUPRIMIDO]`.

**Passo 6 — Verificação de exceções.**
A exceção não é toda objeção possível. É a condição de derrota já interna ao próprio argumento. O eixo pergunta: o argumento declarou o que o faria cair? Ausência de exceção relevante aciona `[EXCEÇÃO NÃO TRATADA]`.

**Passo 7 — Classificação e marcação.**
O o módulo de construção do raciocínio aplica o marcador canônico correspondente, classifica a severidade e registra o achado no formato padrão.

---

## 4. O QUE CONTA COMO ACHADO REAL

Achado real é qualquer instância em que uma tese relevante do output depende de peça argumentativa ausente, fraca, implícita ou deslocada, com consequência para a conclusão, recomendação, risco ou enquadramento.

**Exemplo operativo — parecer trabalhista.**

O output afirma: "A justa causa é juridicamente viável diante da recusa do empregado em utilizar ferramenta tecnológica indicada pelo empregador."

A tese está clara. Os dados podem estar presentes: recusa do empregado, determinação empresarial, ferramenta tecnológica, contexto de trabalho. Mas a garantia precisa ser declarada: em que condições a recusa configura insubordinação ou ato de indisciplina? O backing precisa sustentar essa garantia: art. 482 da CLT, regulamento interno, jurisprudência aplicável, proporcionalidade da sanção, gradação disciplinar, prova da ordem legítima.

Se o output apenas salta dos dados para a tese, há `[GARANTIA NÃO DECLARADA]`.
Se declara que a recusa pode configurar insubordinação, mas não demonstra a fonte normativa ou jurisprudencial que sustenta a passagem, há `[BACKING AUSENTE]`.
Se afirma "a justa causa é viável" sem qualificar "em tese", "desde que comprovada ordem legítima", "se observada proporcionalidade" ou "salvo ausência de treinamento/informação", há `[QUALIFICADOR SUPRIMIDO]`.
Se não trata exceções previsíveis — ferramenta insegura, ausência de política interna, risco de violação à proteção de dados, ordem abusiva, inexistência de treinamento — há `[EXCEÇÃO NÃO TRATADA]`.

---

**Exemplos contrastivos:**

**Falso positivo — o que NÃO é achado EX001:**
Output que apresenta tese, fatos essenciais, regra de passagem e fundamento normativo, ainda que de forma sintética. A ausência de longa fundamentação não é achado. EX001 não exige exaustividade; exige arquitetura mínima auditável.

**Zona cinzenta — garantia implícita mas reconstruível:**
Output que afirma a incidência do CDC em relação entre consumidor e fornecedor, com descrição clara das partes e referência ao contrato de consumo, mas sem explicitar todos os elementos dogmáticos. Se a garantia é reconstruível com segurança e o contexto é simples, o achado é no máximo Baixo: defeito de explicitação, não ausência estrutural.

**Versão corrigida — como transformar `[GARANTIA NÃO DECLARADA]` em output íntegro:**

> *Versão com achado:* "A recusa do empregado torna juridicamente viável a justa causa."

> *Versão corrigida:* "A recusa pode sustentar, em tese, apuração de falta disciplinar se ficar demonstrado que a ordem empresarial era legítima, previamente comunicada, proporcional à função desempenhada e compatível com as normas aplicáveis. A passagem da recusa à justa causa depende de comprovação adicional de gravidade, proporcionalidade e inexistência de justificativa legítima pelo empregado."

---

**Outros padrões que contam como achado real:**

- Tese processual sustentada por precedente sem demonstração de analogia fática.
- Conclusão sobre nulidade contratual baseada em cláusula isolada, sem regra de passagem entre texto, regime jurídico e consequência.
- Recomendação estratégica baseada em risco, sem explicitação dos dados que sustentam a avaliação.
- Afirmação de EX010 sem backing de competência, vigência ou hierarquia.
- Pedido judicial formulado sem conexão clara entre fatos narrados, fundamento jurídico e consequência pretendida.
- Parecer que apresenta exceções apenas depois da conclusão, sem integrá-las à força real da tese.

---

## 5. O QUE NÃO CONTA — ANTI-PADRÕES

**Anti-padrão 1 — Síntese ≠ insuficiência.**
Se a passagem entre dados, garantia, backing, qualificador e exceção é auditável, não marca achado, ainda que o argumento seja sintético. O eixo não exige extensão.

**Anti-padrão 2 — Ausência de citação ≠ backing ausente.**
Se há apoio reconstruível no material analisado (documental, normativo, lógico ou metodológico), não marca `[BACKING AUSENTE]` apenas por falta de citação formal.

**Anti-padrão 3 — Exceção remota ≠ exceção obrigatória.**
Marca `[EXCEÇÃO NÃO TRATADA]` apenas para hipóteses juridicamente relevantes, previsíveis e capazes de alterar a tese. Hipóteses remotas não entram.

**Anti-padrão 4 — Falha estrutural ≠ falha de resistência.**
Se a arquitetura está completa mas uma objeção forte não foi enfrentada, o achado é EX002, nãEX001.

**Anti-padrão 5 — Falha estrutural ≠ falha inferencial.**
Se o problema é hipótese apresentada como conclusão necessária, o eixo principal é EX003.

**Anti-padrão 6 — Falha estrutural ≠ apagamento de incerteza.**
Se o problema é estimativa numérica sem base metodológica, o eixo primário é EX004.

**Anti-padrão 7 — Estilo ≠ arquitetura.**
O eixo não avalia elegância, persuasão ou organização visual. Texto elegante pode estar incompleto; texto seco pode estar íntegro.

---

## 6. RÉGUA DE SEVERIDADE

| Nível | Critério | Consequência no gate |
|---|---|---|
| **Baixa** | Peça argumentativa implícita, mas reconstruível com segurança; qualificador ausente em ponto acessório; exceção remota não tratada | Registro no output. Sem bloqueio. |
| **Média** | Tese relevante com garantia pouco declarada; backing insuficiente em fundamento secundário; qualificador ausente em conclusão que exige ressalva, mas sem alteração imediata da orientação central | Registro com marcador. Revisão ou qualificação recomendada. |
| **Alta** | Conclusão central sem dados suficientes, garantia não declarada ou backing ausente; qualificador suprimido altera a força da recomendação; exceção juridicamente relevante não tratada pode modificar o enquadramento | Bloqueio parcial ou retorno à etapa anterior. |
| **Crítica** | Output estruturado sobre tese principal sem arquitetura argumentativa auditável; múltiplas conclusões centrais sem dados, garantia ou backing; exceções conhecidas tornam a conclusão principal potencialmente inviável | Bloqueio total ou nota de inviabilidade. |

A severidade depende da função da tese no output. Falha estrutural em fundamento lateral não bloqueia. Falha estrutural na tese que sustenta recomendação, pedido, voto ou conclusão decisória aciona gate.

---

## 7. FORMATO DE OUTPUT ESPERADO

```text
ACHADO — EIXO EX001 | ARQUITETURA ARGUMENTATIVA

Marcador: [DADO INSUFICIENTE] / [GARANTIA NÃO DECLARADA] / [BACKING AUSENTE] /
          [QUALIFICADOR SUPRIMIDO] / [EXCEÇÃO NÃO TRATADA]
Severidade: Baixa / Média / Alta / Crítica

Localização no output:
[Trecho exato ou identificação precisa do segmento]

Tese identificada:
[Conclusão, recomendação, enquadramento ou afirmação central sustentada pelo output]

Dados apresentados:
[Quais dados o output usa para sustentar a tese]

Garantia argumentativa:
[Regra de passagem entre dados e tese — declarar se está ausente, implícita ou expressa]

Backing da garantia:
[Fonte normativa, jurisprudencial, doutrinária, documental ou metodológica que sustenta a garantia]

Qualificador devido:
[Força adequada da conclusão: necessária, provável, em tese, condicionada, preliminar,
dependente de prova, salvo exceção etc.]

Exceção relevante:
[Condição de derrota da tese que deveria ter sido tratada]

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

**Roteiros Operacionais de ativação primária:**

- ROs que produzem parecer jurídico
- ROs que revisam peça processual
- ROs que elaboram voto, minuta decisória ou nota técnica
- ROs que estruturam tese jurídica
- ROs que avaliam estratégia processual
- ROs que produzem análise de risco qualitativa

**Ativação em elaboração.**
Na elaboração, EX001 opera como fase de estruturação. Antes da redação final, o o módulo de construção do raciocínio deve mapear tese, dados, garantia, backing, qualificador e exceção das conclusões centrais. A redação só deve avançar quando a arquitetura mínima estiver formada.

**Ativação em revisão.**
Na revisão, EX001 opera como auditoria de sustentação. O o módulo de construção do raciocínio deve verificar se cada conclusão central do output possui dados suficientes, garantia declarada, backing verificável, qualificador adequado e exceções tratadas.

**Ativação em confronto com EX002.**
Quando pareado com EX002, EX001 opera primeiro. Sua função é montar ou auditar a arquitetura do argumento. EX002 opera depois, testando se a estrutura sobrevive à objeção mais forte.

Instrução para confronto:
> "Ative EX001 para decompor a tese em dados, garantia, backing, qualificador e exceção. Em seguida, ative EX002 apenas sobre teses estruturalmente formadas. Não use EX002 para suprir arquitetura ausente; não use EX001 para resolver objeção não enfrentada."

**Ativação secundária por sinalização.**
Outros eixos podem sinalizar necessidade de EX001 quando identificarem:
- conclusão sem cadeia de sustentação;
- premissa relevante não demonstrada;
- fundamento retórico sem regra de passagem;
- ausência de qualificador em tese juridicamente condicionada.

---

## 9. DISTINÇÕES confronto de raciocíniosÍTICAS

### 9.1. EX001 vs. EX002

EX001 estrutura. EX002 confronta.

| | EX001 | EX002 |
|---|---|---|
| Pergunta | A tese tem arquitetura? | A tese sobrevive à objeção forte? |
| Unidade de análise | Tese, dados, garantia, backing, qualificador, exceção | Afirmação substantiva, pressuposto central, objeção |
| Defeito típico | Peça argumentativa ausente | Objeção não enfrentada |
| Produto | Mapa estrutural do argumento | Aporia ou fragilidade declarada |
| Gate | Falha de sustentação | Falha de resistência |

Erro comum: usar EX002 para atacar tese que nem possui arquitetura suficiente. Nesse caso, o primeiro achado é EX001, nãEX002.

### 9.2. EX001 vs. EX003

EX001 controla a arquitetura do argumento. EX003 controla o tipo de inferência.

| | EX001 | EX003 |
|---|---|---|
| Pergunta | Como a tese é sustentada? | Que tipo de inferência gerou a tese? |
| Defeito típico | Dados, garantia ou backing ausentes | EX003 apresentada como dedução |
| Correção | Completar a estrutura argumentativa | Ajustar força epistêmica e hipóteses concorrentes |

Os eixos podem coexistir. Um output pode ter garantia ausente e, ao mesmo tempo, apresentar EX003 como conclusão.

### 9.3. EX001 vs. EX004

EX001 controla sustentação. EX004 controla honestidade diante da incerteza.

| | EX001 | EX004 |
|---|---|---|
| Pergunta | A tese possui suporte argumentativo? | A incerteza foi declarada? |
| Defeito típico | Backing ausente | Segurança não lastreada |
| Foco | Estrutura do argumento | Estado epistêmico do domínio |

### 9.4. EX001 vs. EX005

EX001 controla a passagem argumentativa. EX005 controla a leitura situada do texto.

| | EX001 | EX005 |
|---|---|---|
| Pergunta | Como o texto interpretado sustenta a tese? | De que horizonte o texto foi interpretado? |
| Defeito típico | Garantia ou backing ausente | Pré-compreensão não declarada |
| Foco | Estrutura de sustentação | Processo interpretativo |

---

## 10. CHECKLIST DE FALHA DE EXECUÇÃO

O eixo falhou quando:

- [ ] O o módulo de construção do raciocínio identificou tese central e não mapeou os dados que a sustentam
- [ ] O o módulo de construção do raciocínio aceitou dados como suficientes sem verificar a garantia de passagem até a tese
- [ ] O o módulo de construção do raciocínio registrou backing genérico sem verificar sua relação com a garantia usada
- [ ] O o módulo de construção do raciocínio tratou citação isolada como backing suficiente sem análise de aplicabilidade
- [ ] O o módulo de construção do raciocínio deixou conclusão condicionada aparecer como absoluta
- [ ] O o módulo de construção do raciocínio não identificou exceção interna capaz de derrotar a tese
- [ ] O o módulo de construção do raciocínio confundiu objeção forte com exceção interna
- [ ] O o módulo de construção do raciocínio confundiu ausência de arquitetura com problema exclusivamente de EX002
- [ ] O o módulo de construção do raciocínio confundiu EX003 não declarada com garantia ausente, sem acionar EX003 quando necessário
- [ ] O o módulo de construção do raciocínio classificou como achado a ausência de elemento meramente ornamental ou periférico
- [ ] O o módulo de construção do raciocínio não classificou severidade conforme impacto da tese no output
- [ ] O output avançou com achado Alta ou Crítica sem resolução de gate

---

*a infraestrutura modular 1.0 — Camada confronto de raciocínios / o módulo de construção do raciocínio | EixEX001 — Arquitetura Argumentativa*
*Documento interno. Não transversal ao ecossistema.*
