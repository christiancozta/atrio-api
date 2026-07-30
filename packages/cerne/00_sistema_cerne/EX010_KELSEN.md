# FICHA INSTRUCIONAL — EIXO EX010 VALIDADE NORMATIVA (KELSEN)

**Código:** EX010
**Nome do método:** Validade Normativa
**Arquiteto-pai:** Hans Kelsen

---

## 0. NÚCLEO EXECUTIVO

*Bloco imperativo — colável diretamente no Roteiro Operacional do módulo de construção do raciocínio.*

---

**EIXO EX010 — VALIDADE NORMATIVA (KELSEN)**

**Pergunta operacional:**
> A fonte mobilizada pelo output possui validade, vigência, competência, hierarquia e âmbito de incidência suficientes para ocupar o papel normativo que lhe foi atribuído?

**Sequência operacional:**

1. Identificar fontes mobilizadas pelo output (Constituição, lei, decreto, regulamento, instrução normativa, resolução, portaria, ato administrativo, norma interna, súmula, precedente qualificado).
2. Classificar o tipo de fonte e a função que o output lhe atribuiu (fundamento central, secundário, reforço, contexto, procedimento).
3. Verificar vigência da fonte no período relevante.
4. Verificar competência da autoridade emissora (material, territorial, funcional, temporal, procedimental).
5. Verificar compatibilidade hierárquica entre fontes inferiores e superiores.
6. Verificar âmbito de incidência (material, subjetivo, temporal, territorial).
7. Verificar se ato infralegal foi usado para inovar além de sua base legal.
8. Aplicar marcador, classificar severidade, registrar no formato padrão.

**Testes binários de entrada:**

| Critério | Entra? |
|---|---|
| O output usa norma, ato administrativo ou fonte tratada como se tivesse força normativa? | Se sim → entra |
| O output sustenta conclusão, pedido, voto, parecer, contrato, sanção, obrigação ou estratégia em fonte jurídica? | Se sim → entra |
| O output mobiliza ato infralegal como fundamento de restrição, obrigação ou sanção? | Se sim → entra |
| O output trata precedente, súmula ou tese repetitiva como fonte com posição formal no sistema? | Se sim → entra (apenas para posição formal) |
| O problema é peso prático ou hierarquia de autoridade entre fontes válidas? | Se sim → não entra (domínio de EX011) |
| O problema é interpretação do texto da norma? | Se sim → não entra (domínio de EX005) |
| O problema é abertura textual ou zona de penumbra do conceito jurídico? | Se sim → não entra (domínio de EX009) |
| O problema é arquitetura interna do argumento? | Se sim → não entra (domínio de EX001) |

**Marcadores canônicos:**

| Marcador | Status | Uso |
|---|---|---|
| `[VIGÊNCIA NÃO CONFIRMADA]` | core | Norma central com vigência temporal não confirmada no período relevante |
| `[COMPETÊNCIA NÃO VERIFICADA]` | core | Autoridade emissora sem competência material, territorial, funcional, temporal ou procedimental demonstrada |
| `[HIERARQUIA INCOMPATÍVEL]` | core | Fonte inferior contraria, restringe ou amplia fonte superior |
| `[NORMA DESLOCADA]` | core | Fonte válida e vigente aplicada fora de seu âmbito material, subjetivo, temporal ou territorial |
| `[ATO INFRALEGAL EXPANDIDO]` | core | Ato infralegal cria obrigação, sanção, restrição, requisito ou exceção sem base legal suficiente |
| `[CONFLITO NORMATIVO NÃO RESOLVIDO]` | core | Tensão entre fontes — superior/inferior, geral/especial, anterior/posterior — sem critério de solução declarado |

**Regras de não-acionamento:**

- Se a fonte é válida, vigente, competente e aplicada dentro de seu âmbito, então não marca, ainda que a interpretação seja discutível (sinalizar EX005 ou EX009).
- Se o problema é peso prático de fonte válida, então não marca; sinalizar EX011.
- Se a fonte é persuasiva e foi usada como reforço, sem pretensão de força normativa autônoma, então não marca.
- Se a fonte é central e estável (Constituição vigente, código consolidado), então não exige verificação documental exaustiva.
- Se a norma é válida mas injusta, ineficiente ou inconveniente, então não marca (Kelsen não mede justiça material).
- Se o problema é divergência interpretativa entre leituras admissíveis, então não marca; sinalizar EX005 ou EX009.

**Regra de fronteira com precedentes:**

> Quando a fonte mobilizada for súmula, precedente qualificado, tese repetitiva, repercussão geral, IRDR ou decisão judicial, o eixo Kelsen verifica apenas sua posição formal no sistema e sua aptidão normativa aparente. A interpretação do precedente pertence EX005; seu peso prático pertence EX011; sua função como suporte argumentativo pertence EX001.

**Regra de distinção conceitual:**

> Validade, vigência e eficácia não são sinônimos. Para fins operacionais do módulo de construção do raciocínio: validade indica pertencimento formal da norma ao sistema; vigência indica aptidão temporal de incidência; eficácia indica produção ou exigibilidade de efeitos no caso concreto. Kelsen controla principalmente validade, vigência, competência, hierarquia e âmbito de incidência.

**Ponto cego declarado:**

O eixo não calibra peso prático de autoridades persuasivas ou precedentes (domínio de EX011). Não interpreta o sentido do texto normativo (domínio de EX005). Não avalia abertura textual ou zona de penumbra (domínio de EX009). Não avalia a arquitetura do argumento (domínio de EX001). Não testa objeções fortes (domínio de EX002). Não avalia integridade principiológica.

---

## 0.1 PROMPTS OPERACIONAIS CANÔNICOS

**Termos de ativação interna sugeridos:**

- Principal: "Kelsen" (uso restrito ao projeto); "validade normativa" (uso público); "posição formal da fonte"
- Compostos discriminantes: "validade, vigência, competência e hierarquia", "ato infralegal expandido", "norma deslocada", "papel normativo atribuído", "escalonamento normativo"
- Vetados isoladamente: "norma", "validade", "vigência", "competência" (comuns demais quando isolados)

**Tabela de lacunas de cobertura:**

| Objeto | Código | Status | Prompt canônico |
|---|---|---|---|
| Peça processual | EX010-PEC | Pendente | — |
| Cláusula contratual | EX010-CON | Pendente | — |
| Parecer jurídico | EX010-PAR | Pendente | — |
| Nota técnica | EX010-NOT | Pendente | — |
| Output de IA jurídica externa | EX010-OUT | Pendente | — |
| Decisão judicial | EX010-DEC | Pendente | — |

---

## 0.2 CLÁUSULA DE ATIVAÇÃO, CONTENÇÃO E DESCARTE

**Regra-mãe (acima da ficha):**

> Achados transitam. Lentes não.
>
> Entre fases do módulo de construção do raciocínio, transferem-se apenas produtos estruturados da análise anterior: achados, marcadores, severidade, gates, pendências, restrições e versões corrigidas. O modo de raciocínio do eixo ativado não se transfere automaticamente para a fase seguinte.

**Cláusula específica do eixo EX010:**

Ao fim da fase em que o eixo Kelsen foi ativado, desativa-se o modo formal-estrutural de leitura. Não permanece em fases subsequentes a tendência de reverificar vigência, competência, hierarquia ou âmbito de incidência. Permanecem como produtos exportáveis: marcadores aplicados, severidade registrada, fontes classificadas, pendências de validação documental (vigência, competência) e versão corrigida.

**Riscos específicos de contaminação por resíduo EX010:**

- Tendência a tratar como inválida qualquer fonte cuja vigência ou competência não tenha sido documentalmente reconfirmada em fase posterior.
- Tendência a converter divergência interpretativa em invalidade formal (problema de EX005 ou EX009 tratado como Kelsen).
- Tendência a invadir o terreno de peso prático (EX011), tratando fonte válida com peso baixo como se fosse inválida.
- Tendência a exigir verificação documental exaustiva em normas estáveis e centrais.
- Tendência a converter ausência de citação formal em ausência de fonte.

**Comportamento em confronto com outro eixo:**

Quando pareado com EX011, Kelsen opera primeiro. Verifica validade da fonte; em seguida Raz calibra peso prático. Kelsen não calibra peso; Raz não salva fonte formalmente inválida.

Quando pareado com EX005, Kelsen opera primeiro quando a fonte é controvertida quanto à validade. Confirmada a validade, Gadamer verifica se a leitura está adequada ao horizonte interpretativo.

Quando pareado com EX009 no Circuito NORMA, Kelsen opera primeiro (validade), seguido por EX011 (EX011), seguido por EX009 (EX009).

**Comportamento na entrega final:**

À fase de refinamento textual transmitem-se apenas marcadores não resolvidos e ressalvas formais sobre fontes ("vigência a verificar", "ato infralegal demanda base legal", "conflito hierárquico não resolvido"). Não transmite-se postura cognitiva formal-estrutural nem instrução de reverificação documental.

---

**Nota de modularidade indexada:**

Quando houver sinalização para eixo correlato, a ficha indica apenas o código do eixo (`EX00X`). A descrição completa do confronto, da ordem recomendada e do risco de dupla marcação deve ser consultada na `MATRIZ_DE_CONFRONTOS_INTER_EIXOS_EX.md`.

## 1. ARQUITETO-PAI

Hans Kelsen (1881–1973), jurista e filósofo do direito austríaco, formulador da Teoria Pura do Direito, oferece uma matriz útil para compreender o Direito como sistema escalonado de normas, em que a validade de uma norma depende de sua produção conforme norma superior competente. Outros caminhos seriam compatíveis (positivismo hartiano, normativismo institucional), mas a teoria kelseniana oferece a linguagem mais econômica para controlar o pertencimento formal da norma ao sistema.

**Por que Kelsen e não outro?**

O problema que o eixo precisa capturar é específico: outputs jurídicos que utilizam fontes normativas sem verificar sua posição formal no sistema. A IA pode citar leis, decretos, portarias, resoluções, instruções normativas, atos administrativos, normas internas, precedentes e práticas institucionais como se todos tivessem força equivalente. A fluência do texto dilui a diferença entre validade, vigência, competência e autoridade.

Kelsen é o arquiteto adequado porque sua teoria permite controlar o pertencimento formal da norma ao sistema e sua posição na estrutura escalonada do ordenamento. Para o o módulo de construção do raciocínio, essa pergunta é decisiva: antes de interpretar, ponderar, hierarquizar autoridade ou testar objeções, é necessário verificar se a fonte usada pode ocupar validamente o lugar que o output lhe atribuiu. O eixo Kelsen impede que leis, decretos, portarias, instruções normativas, atos administrativos, normas internas, precedentes e práticas institucionais sejam tratados como fundamentos equivalentes apenas porque foram citados em linguagem jurídica fluente.

A diferença em relação EX011 é essencial. Raz pergunta que peso prático a autoridade tem na decisão. Kelsen pergunta se a norma é formalmente apta a integrar o sistema jurídico e a sustentar a conclusão. Uma fonte pode ter relevância persuasiva e, ainda assim, não possuir validade normativa para criar obrigação. Uma norma pode ser válida e vigente, mas ter peso prático reduzido no caso por ser geral, residual ou deslocada.

---

## 2. O TRAÇADO FILOSÓFICO

**Norma como dever-ser.**
Para Kelsen, a norma jurídica não descreve fatos; prescreve consequências. O Direito opera no plano do dever-ser: se ocorre determinado fato, deve-se aplicar determinada consequência jurídica. Essa estrutura importa para o o módulo de construção do raciocínio porque impede que o output confunda regularidade fática, prática institucional ou conveniência administrativa com norma juridicamente válida.

**Validade como pertencimento ao sistema.**
Uma norma é válida quando pertence ao ordenamento jurídico por ter sido produzida conforme outra norma superior que autoriza sua criação. A validade não depende de a norma ser moralmente boa, conveniente, eficiente ou usual. Depende de sua posição no sistema e do procedimento de produção.

**Escalonamento normativo.**
O ordenamento é estruturado em níveis. Constituição, leis, decretos, regulamentos, atos administrativos e normas internas não ocupam o mesmo plano. Normas inferiores só podem detalhar, executar ou operacionalizar normas superiores dentro dos limites de competência. Quando norma inferior cria obrigação sem base superior, restringe direito além do autorizado ou contraria norma superior, há problema de validade ou de compatibilidade.

**Competência.**
A competência é condição de validade. Não basta que exista um ato normativo; é necessário verificar se a autoridade que o editou podia disciplinar aquele objeto. A incompetência pode ser material, territorial, funcional, temporal ou procedimental.

**Vigência.**
A norma precisa estar vigente no período relevante. Outputs jurídicos frequentemente citam dispositivos revogados, alterações legislativas superadas, normas transitórias fora de prazo ou regimes jurídicos aplicáveis a fatos de outro período. O eixo Kelsen exige teste temporal.

**Âmbito de incidência.**
Mesmo válida e vigente, a norma pode estar deslocada. Uma regra trabalhista pode não incidir sobre relação estatutária. Norma consumerista pode não incidir sobre relação paritária. Regra federal pode não resolver competência estadual. Norma administrativa interna pode não vincular terceiro. A pergunta não é apenas se a norma existe; é se ela incide sobre aquele objeto, sujeito, tempo e território.

**Tradução operacional.**
O traçado kelseniano aplica-se ao módulo de construção do raciocínio como protocolo de controle formal da fonte normativa. O eixo não decide se a norma é justa, eficiente ou persuasiva. Decide se ela pode, validamente, ocupar o lugar que o output lhe atribuiu.

---

## 3. A OPERAÇÃO DO EIXO

O o módulo de construção do raciocínio raciocina sob o eixo Kelsen na seguinte sequência:

**Passo 1 — Identificação das fontes normativas mobilizadas.**
O o módulo de construção do raciocínio localiza todas as fontes usadas como fundamento jurídico: Constituição, leis, códigos, medidas provisórias, decretos, regulamentos, instruções normativas, resoluções, portarias, atos administrativos, normas internas, súmulas, precedentes qualificados e enunciados.

A fonte deve ser separada da autoridade persuasiva. Doutrina, prática de mercado, manual interno e orientação institucional podem ser relevantes, mas não são automaticamente normas jurídicas válidas para criar, restringir ou extinguir direitos.

**Passo 2 — Classificação do tipo de fonte.**
Para cada fonte, o o módulo de construção do raciocínio classifica sua natureza:

| Tipo de fonte | Pergunta kelseniana |
|---|---|
| **Constituição** | A norma constitucional é aplicável ao objeto? |
| **Lei formal** | Está vigente e foi editada pelo ente competente? |
| **Medida provisória** | Estava vigente no período e foi convertida, prorrogada ou perdeu eficácia? |
| **Decreto/regulamento** | Apenas executa a lei ou inovou indevidamente? |
| **Instrução normativa/resolução/portaria** | Está dentro da competência administrativa e da lei que regulamenta? |
| **Ato administrativo individual** | Foi praticado por autoridade competente e dentro do procedimento devido? |
| **Norma interna** | Vincula apenas a organização ou pode produzir efeitos externos? |
| **Súmula/precedente qualificado** | Possui posição formal no sistema? (peso é EX011; interpretação é EX005) |
| **Doutrina/enunciado/prática** | Não é norma válida por si; pode funcionar como reforço, não como fonte normativa autônoma |

**Passo 3 — Verificação de vigência.**
O o módulo de construção do raciocínio verifica se a fonte estava vigente no momento relevante. A pergunta temporal é dupla: (1) a norma está vigente hoje? (2) a norma estava vigente no momento dos fatos, do ato ou da relação jurídica analisada?

Se a vigência não puder ser confirmada com o material disponível, o marcador `[VIGÊNCIA NÃO CONFIRMADA]` é aplicado ou a validação humana é exigida antes de uso decisório.

**Passo 4 — Verificação de competência.**
O o módulo de construção do raciocínio verifica se o órgão, ente ou autoridade emissora tinha competência para produzir a norma ou ato. A competência deve ser examinada em cinco dimensões:

- **material:** o tema podia ser disciplinado por aquela autoridade?
- **territorial:** a fonte incide naquele espaço?
- **funcional:** a autoridade ocupava a posição correta?
- **temporal:** a autoridade tinha competência no momento do ato?
- **procedimental:** o procedimento de edição foi minimamente compatível com a forma exigida?

Ausência de verificação em fonte central aciona `[COMPETÊNCIA NÃO VERIFICADA]`.

**Passo 5 — Verificação hierárquica.**
O o módulo de construção do raciocínio verifica se a fonte inferior é compatível com fonte superior. Exemplos: instrução normativa não pode restringir crédito tributário além da lei; regulamento não pode criar obrigação sem base legal; portaria não pode limitar direito constitucional sem autorização normativa; norma interna não pode afastar garantia legal; entendimento administrativo não pode revogar lei; prática institucional não pode substituir norma competente.

Incompatibilidade ou ausência de resolução do conflito aciona `[HIERARQUIA INCOMPATÍVEL]` ou `[CONFLITO NORMATIVO NÃO RESOLVIDO]`.

**Passo 6 — Verificação do âmbito de incidência.**
O o módulo de construção do raciocínio verifica se a norma incide sobre o caso concreto em quatro planos:

| Plano | Pergunta |
|---|---|
| **Material** | A norma disciplina esse tipo de relação, ato, fato ou sanção? |
| **Subjetivo** | A norma se aplica a esses sujeitos? |
| **Temporal** | A norma incide sobre fatos daquele período? |
| **Territorial** | A norma alcança aquele local, ente ou jurisdição? |

Norma válida mas aplicada fora de seu campo aciona `[NORMA DESLOCADA]`.

**Passo 7 — Verificação de inovação infralegal.**
Quando o output usa ato infralegal como fundamento central, o o módulo de construção do raciocínio verifica se o ato apenas detalha a lei ou se cria obrigação, restrição, sanção, requisito ou exceção não autorizados.

Se o ato infralegal for usado para ampliar ou restringir direitos além da base legal demonstrada, aciona `[ATO INFRALEGAL EXPANDIDO]`.

**Passo 8 — Classificação e marcação.**
O o módulo de construção do raciocínio aplica o marcador canônico correspondente, classifica a severidade e registra o achado no formato padrão.

---

## 4. O QUE CONTA COMO ACHADO REAL

Achado real é qualquer instância em que uma conclusão jurídica depende de fonte normativa cuja vigência, competência, hierarquia, âmbito de incidência ou capacidade regulatória não foi verificada ou se mostra inadequada.

**Exemplo operativo — PIS/COFINS e conceito de insumo.**

O output sustenta a glosa de créditos exclusivamente com base em instruções normativas antigas que adotavam conceito restritivo de insumo, sem confrontá-las com a interpretação consolidada em lei, jurisprudência superior ou critérios posteriores de essencialidade e relevância.

O problema não é citar a instrução normativa. O problema é tratá-la como se pudesse encerrar a interpretação legal do conceito de insumo, sem verificar sua compatibilidade com fonte superior e com a evolução normativa ou jurisprudencial aplicável.

Marcadores possíveis:
- `[HIERARQUIA INCOMPATÍVEL]`, se a instrução normativa restringe além da lei;
- `[ATO INFRALEGAL EXPANDIDO]`, se o ato administrativo cria limitação não prevista em fonte superior;
- `[CONFLITO NORMATIVO NÃO RESOLVIDO]`, se o output ignora tensão entre ato infralegal e interpretação superior.

---

**Exemplos contrastivos:**

**Falso positivo — o que NÃO é achado Kelsen:**
Output que cita lei vigente, aplicável ao caso, editada por ente competente, e usa ato infralegal apenas para detalhar procedimento operacional sem ampliar ou restringir direito. Ainda que a interpretação seja discutível, não há achado Kelsen. O problema pode ser EX005, EX011 ou EX001.

**Zona cinzenta — vigência não confirmável no material disponível:**
Output cita portaria administrativa para sustentar obrigação específica, mas o material não permite confirmar se a portaria está vigente. O eixo não deve declarar invalidade. Deve marcar `[VIGÊNCIA NÃO CONFIRMADA]` e exigir validação antes de uso decisório.

**Versão corrigida — como transformar `[ATO INFRALEGAL EXPANDIDO]` em output íntegro:**

> *Versão com achado:* "A instrução normativa impede o creditamento, razão pela qual a glosa deve ser mantida."

> *Versão corrigida:* "A instrução normativa apresenta orientação administrativa restritiva, mas sua força depende de compatibilidade com a lei de regência e com a interpretação do conceito de insumo segundo critérios de essencialidade e relevância. A glosa não pode ser sustentada exclusivamente por ato infralegal se este restringir crédito além do permitido por fonte superior."

---

**Outros padrões que contam como achado real:**

- Output que usa decreto para criar obrigação sem lei autorizadora.
- Output que aplica norma revogada ou regime jurídico anterior ao fato analisado.
- Output que invoca portaria interna contra terceiro não submetido à organização.
- Output que usa resolução administrativa como se pudesse restringir direito constitucional.
- Output que aplica norma estadual a relação regida por competência federal, sem justificar incidência.
- Output que usa precedente como se fosse norma vinculante sem classificar sua natureza.
- Output que aplica regra de processo civil a processo penal ou administrativo sem ponte normativa.
- Output que sustenta sanção em regulamento sem verificar previsão legal da sanção.
- Output que trata recomendação, manual, nota técnica ou orientação institucional como fonte normativa autônoma.
- Output que resolve conflito entre lei geral e especial sem declarar critério de solução.

---

## 5. O QUE NÃO CONTA — ANTI-PADRÕES

**Ausência de citação ≠ invalidade.**
Um argumento pode estar juridicamente correto mesmo com citação incompleta. O achado Kelsen exige que a fonte usada seja inadequada ou que sua validade não tenha sido verificada quando era central.

**Interpretação controvertida ≠ problema de validade.**
Se a norma é válida, vigente e competente, mas seu sentido é discutível, o eixo primário é EX005 ou EX009. Kelsen não decide o melhor sentido da norma.

**Fonte persuasiva ≠ fonte inválida.**
Doutrina, enunciado, parecer e prática institucional não são inválidos por não serem normas. Podem ser usados como reforço persuasivo. O achado ocorre apenas quando são usados como se tivessem força normativa autônoma.

**Precedente mal calibrado ≠ invalidade normativa.**
Se o problema é tratar decisão isolada como vinculante, o eixo primário é EX011. Kelsen pode incidir quando o output confunde precedente com norma formal ou atribui efeito normativo incompatível.

**Moralidade, justiça ou eficiência ≠ validade.**
Norma injusta, inconveniente ou ineficiente pode ser válida. Kelsen não mede justiça material nem eficiência institucional. Mede validade formal e posição normativa.

**Pesquisa exaustiva ≠ exigência kelseniana.**
O eixo não deve bloquear todo output que não comprove exaustivamente vigência e competência de normas básicas e estáveis. O bloqueio ocorre quando a fonte é central, instável, infralegal, especializada, transitória ou controvertida.

**Aplicabilidade ≠ força argumentativa.**
Uma norma pode ser aplicável e ainda não decidir o caso sozinha. Isso é problema de EX011, EX001 ou EX002. Kelsen verifica se ela pode entrar no jogo; outros eixos verificam o que ela faz no jogo.

---

## 6. RÉGUA DE SEVERIDADE

| Nível | Critério | Consequência no gate |
|---|---|---|
| **Baixa** | Vigência ou competência não explicitada, mas reconstruível com segurança; norma lateral aplicada sem impacto na conclusão central; fonte válida com pequena imprecisão de enquadramento | Registro no output. Sem bloqueio. |
| **Média** | Fonte central citada sem confirmação adequada de vigência, competência ou âmbito de incidência; ato infralegal usado sem base superior explicitada, mas com possibilidade de correção simples | Registro com marcador. Revisão ou validação recomendada. |
| **Alta** | Conclusão central depende de fonte cuja competência, vigência ou aplicabilidade não foi demonstrada; norma inferior usada contra norma superior; ato infralegal sustenta restrição ou obrigação sem base legal declarada | Bloqueio parcial ou retorno à etapa anterior. |
| **Crítica** | Output estruturado sobre norma revogada, fonte incompetente, ato infralegal incompatível com lei, conflito hierárquico não resolvido ou regime jurídico manifestamente deslocado, com efeito decisório direto | Bloqueio total ou nota de inviabilidade. |

A severidade depende da função da fonte na entrega. Falha em fonte lateral pode ser registrada sem bloqueio. Falha em fonte que sustenta conclusão, pedido, sanção, voto, recomendação ou orientação estratégica aciona gate.

---

## 7. FORMATO DE OUTPUT ESPERADO

```text
ACHADO — EIXO EX010 KELSEN | VALIDADE NORMATIVA

Marcador: [VIGÊNCIA NÃO CONFIRMADA] / [COMPETÊNCIA NÃO VERIFICADA] /
          [HIERARQUIA INCOMPATÍVEL] / [NORMA DESLOCADA] /
          [ATO INFRALEGAL EXPANDIDO] / [CONFLITO NORMATIVO NÃO RESOLVIDO]
Severidade: Baixa / Média / Alta / Crítica

Localização no output:
[Trecho exato ou identificação precisa do segmento]

Fonte normativa mobilizada:
[Norma, ato, regulamento, instrução, decreto, lei, dispositivo etc.]

Tipo de fonte:
[Constituição / lei / decreto / ato infralegal / ato administrativo /
 norma interna / precedente qualificado / fonte persuasiva etc.]

Função atribuída pelo output:
[Fundamento central / fundamento secundário / reforço / contexto / procedimento]

Teste de vigência:
[Confirmada / não confirmada / inaplicável ao período / exige validação]

Teste de competência:
[Confirmada / não verificada / inadequada / exige validação]

Teste hierárquico:
[Compatível / conflito não resolvido / norma inferior expandida / exige validação]

Âmbito de incidência:
[Material / subjetivo / temporal / territorial — indicar se adequado ou deslocado]

Natureza do problema:
[Descrição do problema segundo a racionalidade do eixo]

Acionamento de gate:
[Sem bloqueio / Nota de qualificação / Bloqueio parcial / Bloqueio total]

Observação:
[Apenas se necessário: distinção de anti-padrão, sobreposição com EX011, EX005,
 EX001, EX009 ou outro eixo.]
```

---

## 8. OPERAÇÃO DENTRO DO o módulo de construção do raciocínio

**Ativação primária:**

- Fases que produzem parecer com base normativa complexa
- Fases que revisam peça processual com múltiplas fontes
- Fases que elaboram voto, minuta decisória ou nota técnica
- Fases que examinam ato administrativo, sanção, regulação ou política pública
- Fases que analisam direito tributário, administrativo, constitucional, regulatório ou processual
- Fases que auditam uso de instruções normativas, portarias, resoluções ou normas internas
- Fases que verificam compatibilidade entre lei, regulamento e ato administrativo

**Ativação em elaboração:**
O eixo Kelsen opera como etapa de controle da base normativa. Antes de sustentar conclusão em fonte jurídica, o o módulo de construção do raciocínio deve verificar tipo da fonte, vigência, competência, hierarquia e âmbito de incidência.

**Ativação em revisão:**
O eixo Kelsen opera como auditoria da normatividade. O o módulo de construção do raciocínio deve verificar se o output tratou fonte inexistente, revogada, incompetente, infralegal ou deslocada como fundamento apto.

**Ativação em confronto com EX011:**
Quando pareado com Raz, Kelsen deve operar primeiro.

> Instrução para confronto: "Ative Kelsen para verificar validade, competência, vigência, hierarquia e âmbito de incidência da fonte. Em seguida, ative Raz para calibrar o peso prático da autoridade existente ou válida. Não use Raz para salvar fonte formalmente inválida; não use Kelsen para decidir a força persuasiva de autoridade válida."

**Ativação em confronto com EX005:**
Quando a fonte é válida, mas o problema está no sentido atribuído ao texto, Gadamer deve operar depois de Kelsen.

> Instrução para confronto: "Ative Kelsen para confirmar que a fonte pode entrar no sistema argumentativo. Em seguida, ative Gadamer para verificar se o texto foi lido a partir de horizonte interpretativo adequado."

**Ativação no Circuito NORMA (EX010 → EX011 → EX009):**
Em outputs com forte componente normativo, a sequência canônica é Kelsen → Raz → Hart: validade formal, peso prático, EX009.

**Ativação secundária por sinalização:**
Outros eixos podem sinalizar necessidade de Kelsen quando identificarem:
- fonte infralegal usada como fundamento central;
- norma antiga, transitória ou especializada;
- conflito entre lei e regulamento;
- sanção fundada em norma administrativa;
- direito restringido por ato interno;
- precedente tratado como norma;
- ausência de verificação de competência;
- regime jurídico possivelmente deslocado.

---

## 9. DISTINÇÕES confronto de raciocíniosÍTICAS

### 9.1. Validade normativa vs. EX011 (EX010 vs. EX011)

| | Kelsen | Raz |
|---|---|---|
| Pergunta | A fonte é válida, vigente, competente e hierarquicamente apta? | Que peso prático essa autoridade deve ter? |
| Unidade de análise | Norma ou fonte como elemento do sistema | Autoridade como razão para decidir |
| Defeito típico | Fonte inválida, revogada, incompetente ou hierarquicamente deslocada | Fonte persuasiva tratada como vinculante ou decisiva |
| Produto | Estado formal da fonte | Peso adequado da autoridade |
| Gate | Falha de normatividade | Mau uso da autoridade |

A sequência correta é: primeiro Kelsen, depois Raz. Fonte inválida não deve ser calibrada como se fosse autoridade válida.

### 9.2. Validade normativa vs. EX005 (EX010 vs. EX005)

| | Kelsen | Gadamer |
|---|---|---|
| Pergunta | A norma está formalmente apta a incidir? | Que sentido foi atribuído à norma? |
| Defeito típico | Norma deslocada ou inválida | Pré-compreensão não declarada |
| Foco | Validade, vigência, competência e hierarquia | Horizonte interpretativo |
| Exemplo | Instrução normativa usada contra lei | Lei lida sem considerar contexto e leituras concorrentes |

Se a fonte não é válida ou está deslocada, Gadamer não deve ser usado para aperfeiçoar sua interpretação antes de resolver a falha kelseniana.

### 9.3. Validade normativa vs. EX001 (EX010 vs. EX001)

| | Kelsen | Toulmin |
|---|---|---|
| Pergunta | A fonte normativa pode ser usada? | A tese possui dados, garantia, backing, qualificador e exceção? |
| Defeito típico | Norma inválida ou incompatível | Backing (sustentação de fundo da garantia) ausente ou garantia não declarada |
| Correção | Substituir, validar ou reposicionar a fonte | Completar a estrutura argumentativa |
| Exemplo | Portaria usada para criar sanção sem lei | Lei citada sem regra de passagem para a tese |

Uma peça pode ter fontes válidas e ainda ser mal argumentada. Também pode ter boa estrutura, mas fundada em norma inválida.

### 9.4. Validade normativa vs. EX009 (EX010 vs. EX009)

| | Kelsen | Hart |
|---|---|---|
| Pergunta | A norma pertence validamente ao sistema? | O texto normativo possui zona de abertura? |
| Defeito típico | Norma inválida, revogada ou hierarquicamente incompatível | Termo aberto tratado como conceito fechado |
| Foco | Estrutura formal do ordenamento | EX009 da linguagem jurídica |
| Exemplo | Decreto usado contra lei | "Razoável" tratado como critério mecânico |

Os eixos podem operar em sequência: Kelsen confirma a fonte; Hart verifica se sua linguagem permite fechamento categórico.

### 9.5. Kelsen vs. integridade principiológica

Caso o o módulo de construção do raciocínio venha a incorporar futuramente um protocolo de integridade principiológica, este controlaria coerência, igualdade institucional e melhor leitura do Direito. Tal protocolo não substitui Kelsen: só faz sentido discutir integridade depois de estabilizar a fonte normativa aplicável. Enquanto não houver eixo formal correspondente no módulo de construção do raciocínio, a integridade principiológica não é vetor operacional autônomo.

### 9.6. Validade normativa vs. EX003 (EX010 vs. EX003) — *lacuna*

Distinção provisória: Peirce opera sobre o tipo de inferência usada para chegar à conclusão; Kelsen opera sobre a fonte normativa que sustenta a conclusão. Um output pode usar fonte válida (sem achado Kelsen) e ainda apresentar EX003 como dedução (achado Peirce). Fechamento da distinção pendente.

---

## 10. CHECKLIST DE FALHA DE EXECUÇÃO

O eixo falhou quando:

- [ ] O o módulo de construção do raciocínio aceitou fonte normativa sem identificar seu tipo
- [ ] O o módulo de construção do raciocínio não verificou vigência de norma central
- [ ] O o módulo de construção do raciocínio não verificou competência da autoridade emissora
- [ ] O o módulo de construção do raciocínio não verificou se norma inferior extrapolou fonte superior
- [ ] O o módulo de construção do raciocínio aplicou norma fora de seu âmbito material, subjetivo, temporal ou territorial
- [ ] O o módulo de construção do raciocínio tratou ato infralegal como fundamento autônomo para criar obrigação, sanção ou restrição
- [ ] O o módulo de construção do raciocínio confundiu orientação administrativa com lei
- [ ] O o módulo de construção do raciocínio confundiu norma interna com fonte vinculante para terceiros
- [ ] O o módulo de construção do raciocínio tratou precedente ou súmula como norma formal sem classificar sua natureza
- [ ] O o módulo de construção do raciocínio não identificou conflito entre lei geral e especial, norma anterior e posterior, ou fonte superior e inferior
- [ ] O o módulo de construção do raciocínio usou Kelsen para resolver problema de interpretação que pertence EX005
- [ ] O o módulo de construção do raciocínio usou Kelsen para resolver peso de autoridade que pertence EX011
- [ ] O o módulo de construção do raciocínio usou Kelsen para resolver abertura textual que pertence EX009
- [ ] O o módulo de construção do raciocínio classificou como invalidade uma simples divergência interpretativa
- [ ] O output avançou à fase seguinte com achado Alta ou Crítica sem resolução de gate
