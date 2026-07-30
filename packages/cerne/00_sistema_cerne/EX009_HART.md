# FICHA INSTRUCIONAL — EIXO EX009 TEXTURA ABERTA (HART)

**Código:** EX009
**Nome do método:** Textura Aberta
**Arquiteto-pai:** H. L. A. Hart

---

## 0. NÚCLEO EXECUTIVO

*Bloco imperativo — colável diretamente no Roteiro Operacional do módulo de construção do raciocínio.*

---

**EIXO EX009 — TEXTURA ABERTA (HART)**

**Pergunta operacional:**
> Este output tratou linguagem normativa aberta, standard jurídico ou conceito de aplicação contextual como se fosse regra fechada?

**Sequência operacional:**

1. Identificar conceito jurídico aberto, standard normativo ou linguagem normativa aberta no output
2. Classificar o caso: núcleo claro ou zona de penumbra
3. Verificar o fechamento adotado pelo output
4. Verificar a presença e suficiência do critério de fechamento
5. Aplicar teste de falsa clareza
6. Verificar standards mecanizados
7. Classificar achado por marcador e severidade

**Testes binários de entrada:**

| Termo | Critério |
|---|---|
| Conceito aplicado | O output aplica linguagem normativa aberta, standard, conceito indeterminado ou categoria de aplicação contextual (razoável, proporcional, essencial, grave, adequado, abusivo, fundado, necessário, interesse público, boa-fé, justa causa, risco concreto, prova suficiente, insumo, atividade essencial, ou equivalentes)? Sim → entra. Norma fechada sem termo aberto → não entra. |
| Caso de penumbra | Há leituras concorrentes plausíveis + consequências jurídicas diferentes + a linguagem da norma não resolve sozinha? Os três presentes → penumbra relevante. Algum ausente → núcleo claro ou penumbra leve. |
| Fechamento sem critério | O output conclui aplicando conceito aberto + não declara o critério que permitiu passar da abertura ao fechamento + a conclusão é central para o caso? Os três presentes → marca. Algum ausente → não marca. |

**Marcadores canônicos e hierarquia:**

| Marcador | Status | Quando usar |
|---|---|---|
| `[CRITÉRIO DE FECHAMENTO AUSENTE]` | core | O problema central é ausência do critério que permitiu aplicar o conceito aberto |
| `[PENUMBRA SUPRIMIDA]` | core | O output ignora a existência de leituras concorrentes plausíveis |
| `[FALSA CLAREZA NORMATIVA]` | core | O output apresenta como evidente uma conclusão que depende de escolha interpretativa |
| `[STANDARD MECANIZADO]` | periférico | O output transforma um teste avaliativo em fórmula ou rótulo |
| `[CASO DIFÍCIL COMO CASO FÁCIL]` | periférico | A própria estrutura do caso exigia tratamento problemático, mas foi apresentada como aplicação simples |

**Regras de não-acionamento:**

- Caso situado no núcleo claro da regra → não marca achado; aplicação direta é adequada
- Conceito aberto aplicado com critério declarado e suficiente → não marca
- Divergência estratégica entre advogados ≠ penumbra normativa → não marca por esse fundamento
- Ausência de precedente específico ≠ textura aberta → pode ser problema de outro eixo
- Dúvida sobre vigência, competência ou hierarquia da norma → não é EX009; problema de EX010
- Dúvida sobre o peso prático da fonte ou autoridade → não é EX009; problema de calibragem de autoridade
- Pré-compreensão interpretativa do intérprete não declarada → sinalizar EX005
- Falha de EX001 → sinalizar EX001

**Regra de precedência:**
EX009 só opera sobre norma ou autoridade minimamente apta a ingressar na análise. Se a norma é inválida, revogada, incompetente ou hierarquicamente deslocada, o problema primário não é EX009.

**Princípio operacional central:**
O fechamento em si não é problema. O problema é fechamento sem critério declarado.

**Ponto cego declarado:**
EX009 opera sobre a abertura da linguagem normativa e sobre a distinção entre núcleo claro e zona de penumbra. Não verifica validade formal da norma, não calibra peso prático de autoridade, não reconstrói horizonte histórico-interpretativo do texto (EX005), não detecta apagamento de incerteza (EX004), não controlEX001 (EX001).

---

## 0.1 PROMPTS OPERACIONAIS CANÔNICOS

*Bloco de governança interna. Prompts canônicos ainda não produzidos em ciclo formal de teste.*

**Termos de ativação interna sugeridos:**
- Principal: `Hart` (uso restrito ao projeto) e `textura aberta` (compatível com uso público)
- Compostos discriminantes: `textura aberta`, `penumbra normativa`, `critério de fechamento`, `standard mecanizado`
- Vetados: `interpretação` isolado, `norma aberta` isolado, `conceito jurídico` isolado (todos genéricos demais)

---

### Lacunas de cobertura

| Objeto | Código previsto | Status |
|--------|-----------------|--------|
| Peça processual | EX009-PEC | A produzir |
| Cláusula contratual | EX009-CON | A produzir |
| Parecer jurídico | EX009-PAR | A produzir |
| Nota técnica | EX009-NOT | A produzir |
| Output de IA jurídica externa | EX009-OUT | A produzir |
| Decisão judicial | EX009-DEC | A produzir |

---

## 0.2 CLÁUSULA DE ATIVAÇÃO, CONTENÇÃO E DESCARTE

*Cláusula transversal de governança de fase. Aplicável a todas as fichas de eixo do módulo de construção do raciocínio.*

**Regra-mãe (acima da ficha):** *Achados transitam. Lentes não.*

Entre fases do módulo de construção do raciocínio, transferem-se apenas produtos estruturados da análise anterior: achados, marcadores, severidade, gates, pendências, restrições e versões corrigidas. O modo de raciocínio do eixo ativado não se transfere automaticamente para a fase seguinte.

**Cláusula específica do eixo EX009:**

Este eixo opera como lente temporária de auditoria da abertura normativa dentro da fase indicada do módulo de construção do raciocínio. Encerrada a fase, o modo de suspeita semântica permanente — desconfiança de todo conceito jurídico — deve ser desativado. Apenas seus produtos formais — marcadores de fechamento sem critério, leituras concorrentes plausíveis, classificação de núcleo ou penumbra, severidade e gate — podem ser transferidos para a etapa seguinte.

**Riscos específicos de contaminação por resíduo EX009:**

- *Suspeita semântica residual:* fase seguinte continua tratando todo conceito jurídico como aberto, gerando achados onde havia núcleo claro.
- *Hiperqualificação na entrega final:* output final fica artificialmente cheio de "salvo demonstração de critério" mesmo onde a aplicação era direta.
- *Captura de outros eixos:* problemas de EX010, peso de autoridade, pré-compreensão interpretativa (EX005) ou apagamento de incerteza (EX004) passam a ser lidos como "textura aberta", esvaziando os eixos vizinhos.
- *Gate excessivo:* falhas médias viram bloqueios por excesso de rigor semântico.

**Comportamento em confronto com outro eixo:**

EX009 não reinterpreta achados de outros eixos como abertura semântica. Verifica apenas se há linguagem normativa aberta sendo aplicada sem critério de fechamento declarado. Quando o problema é pré-compreensão do intérprete (EX005), apagamento de incerteza (EX004), EX001 (EX001) ou objeção não enfrentada (EX002), EX009 não absorve — sinaliza para o eixo competente.

**Comportamento na entrega final:**

A fase de refinamento textual recebe apenas marcadores não resolvidos, critérios de fechamento requeridos e leituras concorrentes a explicitar. Não recebe a postura de suspeita semântica como diretriz de tom. O refinamento editorial produz texto que declara seus critérios, sem performar dúvida desnecessária.

---

**Nota de modularidade indexada:**

Quando houver sinalização para eixo correlato, a ficha indica apenas o código do eixo (`EX00X`). A descrição completa do confronto, da ordem recomendada e do risco de dupla marcação deve ser consultada na `MATRIZ_DE_CONFRONTOS_INTER_EIXOS_EX.md`.

## 1. ARQUITETO-PAI

Herbert Lionel Adolphus Hart (1907–1992) foi filósofo do direito britânico e uma das principais figuras do positivismo jurídico analítico. Sua obra central, *The Concept of Law*, deslocou a teoria jurídica para a análise das regras, da linguagem normativa, da regra de reconhecimento e da textura aberta do Direito.

**Por que Hart e não outro?**

O problema que o eixo precisa capturar é específico: outputs jurídicos que aplicam conceitos abertos como se fossem comandos fechados. A IA tende a produzir respostas fluentes e decisivas. Essa fluência pode apagar o fato de que muitas normas jurídicas não se aplicam mecanicamente, porque sua linguagem contém zonas de incerteza legítima.

Hart é adotado porque formulou com precisão o problema da textura aberta. Toda regra possui casos centrais, nos quais sua aplicação parece clara, e casos periféricos, nos quais a linguagem não determina sozinha a resposta. O Direito precisa de regras, mas nenhuma formulação linguística antecipa todas as situações futuras.

Hart não é a única matriz teórica compatível com essa operação — teoria da interpretação jurídica, semântica jurídica e teorias da aplicação normativa oferecem caminhos próximos. Hart é adotado pela precisão de sua gramática operacional sobre núcleo, penumbra e textura aberta.

A diferença em relação EX005 é importante: EX005 pergunta de que horizonte interpretativo o texto foi lido; EX009 pergunta se o próprio texto, por sua linguagem, comporta abertura que impede fechamento automático. EX005 controla o encontro entre intérprete e texto; EX009 controla a estrutura aberta da regra.

EX009 impede que o o módulo de construção do raciocínio transforme conceitos jurídicos abertos em comandos automáticos.

---

## 2. O TRAÇADO FILOSÓFICO

**Regras e casos centrais.**
Hart reconhece que regras jurídicas possuem um núcleo de aplicação clara. Em muitos casos, a linguagem normativa funciona adequadamente: há situações que se enquadram sem grande controvérsia. O eixo EX009 não deve transformar toda aplicação jurídica em problema interpretativo. Quando o caso está no núcleo claro da regra, a conclusão pode ser direta.

**Textura aberta (open texture).**
A linguagem jurídica não antecipa todas as circunstâncias futuras de sua aplicação. Termos gerais são necessários para estabilizar condutas e orientar decisões, mas essa generalidade produz uma margem inevitável de abertura. A regra opera com relativa segurança nos casos centrais; nos casos de penumbra, sua linguagem não determina sozinha a solução. Essa abertura não é falha acidental da norma, mas característica estrutural do Direito enquanto sistema de regras gerais aplicado a situações particulares.

**Zona de penumbra.**
A zona de penumbra é o espaço em que a aplicação da regra não é automaticamente determinada pela linguagem. Nesses casos, o intérprete precisa declarar critérios de fechamento: finalidade da norma, coerência sistêmica, precedentes, consequências, princípios, política legislativa, analogia, distinção ou outro critério juridicamente aceitável.

**Discricionariedade limitada.**
Hart não transforma a penumbra em liberdade absoluta. A abertura normativa exige decisão, mas essa decisão deve ser justificada. No o módulo de construção do raciocínio, o problema ocorre quando o output decide sem declarar que decidiu — quando apresenta fechamento interpretativo como se fosse simples leitura textual.

**Regra de reconhecimento.**
A regra de reconhecimento permite identificar quais fontes contam como Direito em determinado sistema. Mesmo após reconhecida a fonte válida, resta a pergunta sobre o alcance semântico e prático da regra nos casos difíceis.

**Tradução operacional.**
O traçado hartiano aplica-se ao módulo de construção do raciocínio como teste de abertura normativa. A pergunta não é apenas "qual norma se aplica?" A pergunta é: "a norma aplicada contém termo aberto ou zona de penumbra que exigia critério de fechamento antes da conclusão?"

---

## 3. A OPERAÇÃO DO EIXO

**Passo 1 — Identificação de linguagem normativa aberta.**
O o módulo de construção do raciocínio localiza termos, standards ou categorias normativas cuja aplicação dependa de avaliação contextual.

Exemplos recorrentes:
- razoabilidade
- proporcionalidade
- boa-fé
- justa causa
- atividade essencial
- insumo
- relevância
- essencialidade
- risco concreto
- fundado receio
- prova suficiente
- interesse público
- abuso
- gravidade
- necessidade
- adequação
- urgência
- diligência razoável
- perigo de dano
- motivação idônea

Se o output não aplica conceito aberto, o eixo não deve ser ativado.

**Passo 2 — Classificação do caso: núcleo claro ou penumbra.**

| Situação | Critério |
|---|---|
| **Núcleo claro** | A aplicação da norma é amplamente estabilizada, com baixo espaço de controvérsia razoável |
| **Penumbra leve** | Há abertura, mas o contexto favorece fortemente um enquadramento |
| **Penumbra relevante** | Há leituras concorrentes plausíveis e consequências jurídicas diferentes |
| **Penumbra intensa** | A norma não resolve o caso sem escolha interpretativa substancial |
| **Indeterminado** | O material não permite classificar a abertura com segurança |

EX009 opera com maior força em penumbra relevante, penumbra intensa e indeterminação.

**Passo 3 — Verificação do fechamento adotado.**
O o módulo de construção do raciocínio identifica se o output fechou o conceito aberto em uma direção específica.

Exemplos:
- "a despesa é essencial"
- "há justa causa"
- "a decisão foi devidamente fundamentada"
- "o risco é concreto"
- "a medida é proporcional"
- "a prova é suficiente"
- "o interesse público justifica a restrição"

**Passo 4 — Verificação do critério de fechamento.**
O o módulo de construção do raciocínio pergunta: qual critério permitiu passar da abertura do termo à conclusão concreta?

Critérios possíveis:
- finalidade da norma
- estrutura do regime jurídico
- precedentes aplicáveis
- analogia
- distinção
- prova documental
- prática institucional juridicamente relevante
- proporcionalidade
- função econômica ou social da relação
- proteção de direito fundamental
- coerência com norma superior
- critérios técnicos externos juridicamente incorporados

Se o critério não está declarado, ativa `[CRITÉRIO DE FECHAMENTO AUSENTE]`.

**Passo 5 — Teste de falsa clareza.**
O o módulo de construção do raciocínio verifica se o output apresentou o caso como simples quando havia abertura relevante.

Indícios de falsa clareza:
- uso de "evidente", "inequívoco", "naturalmente", "necessariamente" em caso aberto
- ausência de leitura concorrente plausível
- ausência de qualificador
- passagem direta do termo aberto à conclusão
- exclusão retórica de controvérsia
- tratamento de standard como regra mecânica

Se a abertura foi apagada, ativa `[FALSA CLAREZA NORMATIVA]` ou `[PENUMBRA SUPRIMIDA]`.

**Passo 6 — Verificação de standards mecanizados.**
Quando o output aplica teste normativo que exige ponderação ou avaliação contextual, o o módulo de construção do raciocínio verifica se o standard foi reduzido a fórmula.

Exemplos:
- proporcionalidade tratada como simples afirmação de adequação
- boa-fé usada como rótulo de resultado
- interesse público invocado sem demonstração
- essencialidade afirmada sem teste de dependência
- risco concreto afirmado sem circunstâncias concretas

Se o standard foi aplicado mecanicamente, ativa `[STANDARD MECANIZADO]`.

**Passo 7 — Classificação e marcação.**

---

## 4. O QUE CONTA COMO ACHADO REAL

Achado real é qualquer instância em que o output aplica linguagem normativa aberta, standard ou conceito de aplicação contextual como se fosse categoria fechada, sem declarar a zona de penumbra nem o critério de fechamento usado.

**Exemplo operativo — conceito de insumo em PIS/COFINS.**

O output afirma que despesas com infraestrutura em nuvem, segurança e monitoramento são insumos porque são "essenciais" à atividade SaaS.

A conclusão pode ser defensável. O problema surge se o output não demonstrar por que "essencial" significa, no caso concreto, dependência funcional da prestação, e não mera utilidade empresarial. "Essencialidade" é conceito aberto. Exige critério de fechamento.

Marcadores possíveis:
- `[CRITÉRIO DE FECHAMENTO AUSENTE]`, se o output não mostra como avaliou essencialidade
- `[FALSA CLAREZA NORMATIVA]`, se apresenta o enquadramento como óbvio
- `[CASO DIFÍCIL COMO CASO FÁCIL]`, se ignora rubricas periféricas como marketing, treinamento ou compliance genérico

---

**Exemplos contrastivos:**

**Falso positivo — o que NÃO é achado EX009:**
Output que aplica prazo legal objetivo, competência expressamente prevista ou requisito formal fechado, sem termo aberto relevante. Exemplo: "o prazo decadencial do mandado de segurança é de 120 dias". A norma pode exigir verificação temporal, mas não há textura aberta significativa na expressão. EX009 não tem achado.

**Zona cinzenta — conceito aberto com critério suficiente:**
Output que afirma que determinada despesa é essencial porque: (i) está prevista no contrato como obrigação de entrega; (ii) sua ausência inviabiliza cumprimento de SLA; (iii) há demonstração técnica de dependência operacional; (iv) não se trata de despesa comercial ou administrativa genérica. Aqui há fechamento do conceito, mas com critério. Não há achado.

**Versão corrigida:**

> *Versão com achado:* "A despesa é essencial à atividade da empresa e, portanto, gera crédito."

> *Versão corrigida:* "A essencialidade não decorre da simples utilidade empresarial da despesa. No caso, a despesa será defensável como insumo se demonstrado que sua ausência compromete a própria prestação contratada, especialmente por afetar disponibilidade, segurança ou funcionalidade da plataforma. Sem essa demonstração, o enquadramento permanece em zona de penumbra."

**Outros padrões que contam como achado real:**

- Output que afirma "justa causa configurada" sem demonstrar gravidade, proporcionalidade e atualidade da falta.
- Output que diz "fundado receio" sem identificar fatos concretos que fundamentem o receio.
- Output que afirma "interesse público" sem declarar qual interesse, sua base normativa e sua relação com a medida.
- Output que trata "boa-fé" como sinônimo de intenção subjetiva sem critério jurídico.
- Output que afirma "prova suficiente" sem explicar suficiência para qual standard decisório.
- Output que aplica "razoabilidade" como palavra de conclusão, não como critério.
- Output que usa "risco concreto" com base em risco abstrato.
- Output que chama medida de "proporcional" sem distinguir adequação, necessidade e proporcionalidade em sentido estrito.
- Output que lê "atividade essencial" como toda atividade importante para a empresa.
- Output que afirma "motivação idônea" sem enfrentar a suficiência concreta da fundamentação.

---

## 5. O QUE NÃO CONTA — ANTI-PADRÕES

**Anti-padrão 1 — Toda interpretação ≠ textura aberta.**
Nem toda norma possui abertura relevante no caso. Onde há núcleo claro, não há achado EX009.

**Anti-padrão 2 — Divergência estratégica ≠ penumbra normativa.**
Duas estratégias processuais possíveis não significam que o texto normativo seja aberto. A penumbra pertence à linguagem da norma ou categoria jurídica, não à conveniência da atuação.

**Anti-padrão 3 — Falta de precedente ≠ textura aberta.**
A ausência de precedente específico pode aumentar incerteza, mas não é, por si, achado EX009. Pode ser EX004 ou EX001. EX009 exige termo aberto ou standard normativo aplicado.

**Anti-padrão 4 — Conceito aberto corretamente fechado ≠ achado.**
O uso de conceito aberto não gera achado automático. Se o output declara critérios suficientes para aplicá-lo, não há `[PENUMBRA SUPRIMIDA]`.

**Anti-padrão 5 — EX010 ≠ textura aberta.**
Se a dúvida é se a norma está vigente, se o órgão era competente ou se o ato infralegal extrapolou a lei, o problema não é de EX009.

**Anti-padrão 6 — Peso de autoridade ≠ textura aberta.**
Se o problema é tratar decisão isolada como vinculante ou doutrina como decisiva, o problema não é de EX009. EX009 incide apenas se a autoridade aplica conceito aberto sem critério.

**Anti-padrão 7 — Horizonte interpretativo ≠ textura aberta.**
Se o problema é a pré-compreensão do intérprete ou a ausência de confronto com o contexto do texto, EX005 pode ser eixo primário. EX009 se concentra na abertura da linguagem normativa.

---

## 6. RÉGUA DE SEVERIDADE

| Nível | Critério | Consequência no gate |
|---|---|---|
| **Baixa** | Conceito aberto aplicado com critério implícito, reconstruível e sem impacto decisivo; caso próximo do núcleo claro da regra | Registro no output. Sem bloqueio. |
| **Média** | Termo aberto relevante aplicado com critério pouco declarado; penumbra leve ou moderada ignorada; standard usado de modo conclusivo, mas corrigível com qualificação | Registro com marcador. Revisão ou qualificação recomendada. |
| **Alta** | Conclusão central depende de conceito aberto fechado sem critério; caso de penumbra relevante tratado como caso fácil; standard normativo mecanizado em ponto decisivo | Bloqueio parcial ou retorno à etapa anterior. |
| **Crítica** | Output estruturado sobre múltiplos fechamentos indevidos de conceitos abertos, com efeito decisório direto; zona de penumbra intensa apagada, levando a conclusão potencialmente inválida ou estratégia gravemente insegura | Bloqueio total ou nota de inviabilidade. |

A severidade depende do papel do conceito aberto na entrega. Termo aberto lateral pode gerar achado baixo. Termo aberto que sustenta pedido, conclusão, sanção, recomendação ou voto aciona gate.

---

## 7. FORMATO DE OUTPUT ESPERADO

```text
ACHADO — EIXO EX009 HART | TEXTURA ABERTA

Marcador: [FALSA CLAREZA NORMATIVA] / [PENUMBRA SUPRIMIDA] /
          [CRITÉRIO DE FECHAMENTO AUSENTE] / [STANDARD MECANIZADO] /
          [CASO DIFÍCIL COMO CASO FÁCIL]
Status do marcador: core / periférico
Severidade: Baixa / Média / Alta / Crítica

Localização no output:
[Trecho exato ou identificação precisa do segmento]

Conceito aberto ou standard aplicado:
[Termo normativo, cláusula geral, conceito indeterminado ou standard]

Núcleo ou penumbra:
[Núcleo claro / penumbra leve / penumbra relevante / penumbra intensa / indeterminado]

Fechamento adotado pelo output:
[Conclusão concreta que o output extraiu do conceito aberto]

Critério de fechamento declarado:
[Finalidade, precedente, prova, analogia, proporcionalidade, regime jurídico etc.]

Critério ausente ou insuficiente:
[O que faltou para justificar o fechamento]

Leitura concorrente plausível:
[Se houver, indicar alternativa que o output deveria ter enfrentado]

Natureza do problema:
[Descrição do problema segundo a racionalidade do eixo]

Acionamento de gate:
[Sem bloqueio / Nota de qualificação / Bloqueio parcial / Bloqueio total]

Observação:
[Apenas se necessário: distinção de anti-padrão, sobreposição com outro eixo.]
```

---

## 8. OPERAÇÃO DENTRO DO o módulo de construção do raciocínio

**Roteiros Operacionais de ativação primária:**

- ROs que interpretam conceitos jurídicos indeterminados
- ROs que aplicam cláusulas gerais
- ROs que revisam pareceres baseados em standards normativos
- ROs que elaboram voto ou minuta decisória em casos difíceis
- ROs que analisam Direito Tributário, Administrativo, Constitucional, Penal, Trabalhista ou Contratual com termos abertos
- ROs que avaliam justa causa, boa-fé, proporcionalidade, razoabilidade, interesse público, insumo, risco concreto ou prova suficiente
- ROs que auditam textos que usam linguagem de evidência em matéria aberta

**Ativação em elaboração.**
O eixo opera antes do fechamento categórico da conclusão. O o módulo de construção do raciocínio identifica se há conceito aberto e declara o critério de fechamento antes de afirmar o resultado.

**Ativação em revisão.**
O eixo verifica se o output tratou caso difícil como caso fácil, se suprimiu zona de penumbra ou se aplicou standard sem critério.

**Ativação em confronto com EX005.**
EX009 e EX005 podem operar juntos quando o problema envolve tanto abertura semântica quanto pré-compreensão interpretativa.

Instrução:
> "Use EX009 para identificar se há textura aberta no termo normativo. Use EX005 para verificar se a leitura do termo foi condicionada por horizonte interpretativo não declarado."

**Ativação secundária por sinalização.**
Outros eixos podem sinalizar necessidade de EX009 quando identificarem:
- conclusão categórica baseada em termo aberto
- uso de standard como rótulo
- ausência de critério para essencialidade, relevância, razoabilidade ou proporcionalidade
- linguagem de evidência em caso juridicamente difícil
- conceito indeterminado aplicado a fato novo ou tecnologia emergente

---

## 9. DISTINÇÕES confronto de raciocíniosÍTICAS

### 9.1. EX009 vs. EX005

EX009 controla textura aberta. EX005 controla horizonte interpretativo.

| | EX009 | EX005 |
|---|---|---|
| Pergunta | O termo jurídico é aberto no caso? | De que pré-compreensão o texto foi lido? |
| Defeito típico | Penumbra suprimida | Horizonte não confrontado |
| Foco | Linguagem da regra | Encontro entre intérprete e texto |
| Exemplo | "Risco concreto" sem fato concreto | Texto lido como claro por pré-compreensão acusatória |

Os eixos são próximos, mas não substituíveis. EX009 pergunta se há abertura na linguagem normativa. EX005 pergunta como o intérprete atravessou essa abertura.

### 9.2. EX009 vs. EX003

EX009 controla abertura do conceito. EX003 controla tipo de inferência.

| | EX009 | EX003 |
|---|---|---|
| Pergunta | O conceito aplicado é aberto? | A conclusão foi inferida por dedução, indução ou EX003? |
| Defeito típico | Conceito aberto tratado como fechado | Hipótese apresentada como conclusão |
| Foco | Norma e linguagem | Inferência |
| Exemplo | "Justa causa" como categoria automática | Indícios de falta grave tratados como prova conclusiva |

Podem coexistir: o output pode fechar indevidamente um conceito aberto e ainda apresentar uma hipótese fática como conclusão.

### 9.3. EX009 vs. EX001

EX009 controla textura aberta na linguagem normativa. EX001 controlEX001.

| | EX009 | EX001 |
|---|---|---|
| Pergunta | A linguagem normativa permite fechamento automático? | A tese tem dados, garantia, backing, qualificador, exceção? |
| Defeito típico | Conceito aberto fechado sem critério | Peça argumentativa ausente |
| Foco | Linguagem da norma | Estrutura do argumento |

Podem coexistir: o output pode fechar conceito aberto sem critério (EX009) e ainda ter EX001 incompleta (EX001).

*Lacuna sinalizada:* tabelas comparativas operacionais com EX002 e EX004 a serem incorporadas em ciclo posterior.

---

## 10. CHECKLIST DE FALHA DE EXECUÇÃO

O eixo falhou quando:

- [ ] O o módulo de construção do raciocínio não identificou conceito jurídico aberto central
- [ ] O o módulo de construção do raciocínio tratou termo indeterminado como regra fechada
- [ ] O o módulo de construção do raciocínio não distinguiu núcleo claro e zona de penumbra
- [ ] O o módulo de construção do raciocínio aceitou conclusão categórica sem critério de fechamento
- [ ] O o módulo de construção do raciocínio não verificou se havia leitura concorrente plausível
- [ ] O o módulo de construção do raciocínio aceitou "razoável", "proporcional", "essencial", "relevante" ou "grave" como palavras de conclusão
- [ ] O o módulo de construção do raciocínio não exigiu demonstração concreta de risco concreto, prova suficiente ou motivação idônea
- [ ] O o módulo de construção do raciocínio aplicou standard normativo como fórmula mecânica
- [ ] O o módulo de construção do raciocínio confundiu ausência de precedente com textura aberta
- [ ] O o módulo de construção do raciocínio confundiu EX010 com fechamento semântico
- [ ] O o módulo de construção do raciocínio usou EX009 para resolver problema que pertence a outro eixo (pré-compreensão, peso de autoridade, validade)
- [ ] O o módulo de construção do raciocínio classificou como achado aplicação de regra situada no núcleo claro
- [ ] O output avançou com achado Alta ou Crítica sem resolução de gate

---

*a infraestrutura modular 1.0 — Camada confronto de raciocínios / o módulo de construção do raciocínio | EixEX009*
*Documento interno. Não transversal ao ecossistema.*
