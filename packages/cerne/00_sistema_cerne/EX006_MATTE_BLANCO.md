# FICHA INSTRUCIONAL — EIXO EX006 SIMETRIZAÇÃO (MATTE-BLANCO)

**Código:** EX006
**Nome do método:** Simetrização
**Arquiteto-pai:** Ignacio Matte-Blanco

---

## 0. NÚCLEO EXECUTIVO

*Bloco imperativo — colável diretamente no Roteiro Operacional do módulo de construção do raciocínio.*

---

**EIXO EX006 — SIMETRIZAÇÃO (MATTE-BLANCO)**

**Pergunta operacional:**
> Que distinção juridicamente relevante este output tratou como irrelevante? O que foi equiparado que não é equivalente?

**Sequência operacional:**

1. Identificar operações com categorias jurídicas, regimes, institutos ou situações comparáveis.
2. Verificar se houve equiparação explícita ou implícita entre categorias juridicamente distintas.
3. Mapear a distinção eventualmente suprimida.
4. Testar se a distinção altera conclusão, regime, prazo, ônus, proteção, pressuposto ou efeito jurídico.
5. Verificar se a equiparação foi declarada e qualificada.
6. Classificar o tipo de simetrização: distinção colapsada, simetria indevida ou generalização supressora.
7. Aplicar marcador, classificar severidade, registrar no formato padrão.

**Testes binários de entrada:**

| Critério | Entra? |
|---|---|
| O output equipara categorias, institutos, regimes ou situações jurídicas? | Se sim → entra |
| O output aplica conclusão de um domínio jurídico a outro domínio por semelhança? | Se sim → entra |
| O output generaliza regra, proteção, prazo, ônus ou efeito sem preservar distinção estrutural relevante? | Se sim → entra |
| A distinção suprimida altera conclusão, regime, prazo, ônus, proteção, pressuposto ou efeito jurídico? | Se sim → entra |
| A equiparação foi declarada, qualificada e justificada quanto à diferença relevante? | Se sim → não entra |
| A diferença é apenas terminológica, sem efeito operacional no caso? | Se sim → não entra |
| O problema é erro de inferência de qualificação jurídica? | Se sim → não entra isoladamente (domínio de EX003) |
| O problema é operação técnica de precedente ou analogia jurisprudencial? | Se sim → não entra isoladamente (domínio de EX007) |

**Marcadores canônicos:**

| Marcador | Status | Uso |
|---|---|---|
| `[DISTINÇÃO COLAPSADA]` | core | Categoria com regime jurídico distinto tratada como equivalente, com impacto sobre conclusão, prazo, ônus, proteção ou efeito |
| `[SIMETRIA INDEVIDA]` | core | Relação assimétrica tratada como reversível ou equivalente sem declaração suficiente |
| `[GENERALIZAÇÃO SUPRESSORA]` | core | Generalização a partir de caso, categoria ou precedente apagando diferença estrutural relevante |

Os três marcadores operam em paridade funcional. A severidade não decorre do marcador em abstrato, mas do impacto da distinção suprimida sobre conclusão, regime, prazo, ônus, proteção, pressuposto ou efeito jurídico.

**Regras de não-acionamento:**

- Se a distinção é meramente terminológica, então não marca.
- Se a distinção técnica não altera conclusão, regime, prazo, ônus, proteção, pressuposto ou efeito jurídico no caso concreto, então não marca.
- Se a analogia foi declarada, justificou o ponto de semelhança e reconheceu a diferença relevante, então não marca.
- Se o problema é apenas inferência fraca de qualificação jurídica, então não marca; sinalizar EX003.
- Se o problema é operação técnica de precedente, então não marca isoladamente; sinalizar EX007.
- Se o output usa categoria ampla apenas em exposição introdutória, sem consequência decisória, então não marca.
- Se a diferença entre regimes existe em abstrato, mas não interfere no caso analisado, então não marca.

**Regra de integridade do eixo:**

> Matte-Blanco não é detector universal de analogia. O eixo não pune semelhança; pune equivalência indevida quando uma diferença juridicamente relevante foi apagada.

**Regra de contenção material:**

> O eixo só aciona quando a distinção suprimida altera conclusão, regime, prazo, ônus, proteção, pressuposto ou efeito jurídico.

**Ponto cego declarado:**

O eixo não detecta erro de classificação factual, nem avalia a força epistêmica da inferência (domínio de EX003). Não audita a operação técnica de precedente ou analogia jurisprudencial (domínio de EX007). Não mede a regra universalizada que a decisão instituiria (domínio de EX008). Opera exclusivamente sobre o apagamento de distinções jurídicas relevantes e sobre os efeitos jurídicos dessa equiparação.

---

## 0.1 PROMPTS OPERACIONAIS CANÔNICOS

**Termos de ativação interna sugeridos:**

- Principal: "Matte-Blanco" (uso restrito ao projeto); "simetrização" (uso público); "distinção juridicamente relevante"
- Compostos discriminantes: "distinção colapsada", "simetria indevida", "equiparação indevida", "regime distinto", "categoria jurídica não equivalente", "generalização supressora"
- Vetados isoladamente: "semelhança", "analogia", "diferença", "generalização", "categoria" (comuns demais quando isolados)

**Tabela de lacunas de cobertura:**

| Objeto | Código | Status | Prompt canônico |
|---|---|---|---|
| Peça processual | EX006-PEC | Pendente | — |
| Cláusula contratual | EX006-CON | Pendente | — |
| Parecer jurídico | EX006-PAR | Pendente | — |
| Nota técnica | EX006-NOT | Pendente | — |
| Output de IA jurídica externa | EX006-OUT | Pendente | — |
| Decisão judicial | EX006-DEC | Pendente | — |
| Precedente como analogia | EX006-PRE | Pendente | — |

---

## 0.2 CLÁUSULA DE ATIVAÇÃO, CONTENÇÃO E DESCARTE

**Regra-mãe (acima da ficha):**

> Achados transitam. Lentes não.
>
> Entre fases do módulo de construção do raciocínio, transferem-se apenas produtos estruturados da análise anterior: achados, marcadores, severidade, gates, pendências, restrições e versões corrigidas. O modo de raciocínio do eixo ativado não se transfere automaticamente para a fase seguinte.

**Cláusula específica do eixo EX006:**

Ao fim da fase em que o eixo Matte-Blanco foi ativado, desativa-se o modo de suspeita contra equivalências. Não permanece em fases subsequentes a tendência de tratar toda analogia, aproximação conceitual ou generalização como colapso de distinção. Permanecem como produtos exportáveis: marcadores aplicados, severidade registrada, distinções suprimidas, consequências jurídicas da supressão, pendências de enquadramento e versão corrigida.

**Riscos específicos de contaminação por resíduo EX006:**

- Tendência a transformar toda analogia legítima em simetria indevida.
- Tendência a marcar diferenças meramente terminológicas como distinções juridicamente relevantes.
- Tendência a bloquear generalizações necessárias ao raciocínio jurídico.
- Tendência a invadir o terreno de inferência abdutiva (EX003), tratando qualificação jurídica incerta como colapso categorial.
- Tendência a invadir o terreno precedental (EX007), tratando falha de o módulo de construção do raciocínio ou distinguishing como simetrização.

**Comportamento em confronto com outro eixo:**

Quando pareado com EX007, Levi verifica a operação técnica da analogia ou do precedente; Matte-Blanco verifica se a aplicação apagou distinção juridicamente relevante. Levi constrói a ponte; Matte-Blanco testa se a ponte apagou o desnível entre os regimes.

Quando pareado com EX003, Peirce verifica o tipo de inferência usado para qualificar o fato; Matte-Blanco verifica se, depois da qualificação, os efeitos de categorias distintas foram tratados como equivalentes.

Quando pareado com EX005, Gadamer verifica o horizonte de leitura do texto ou regime; Matte-Blanco verifica se o resultado da leitura equiparou categorias com efeitos jurídicos distintos.

**Comportamento na entrega final:**

À fase de refinamento textual transmitem-se apenas marcadores não resolvidos e qualificadores de distinção ("regime diverso", "efeitos não equivalentes", "distinção relevante", "transposição exige declaração"). Não se transmite postura cognitiva antianalógica nem instrução de suspeita permanente contra semelhanças.

---

**Nota de modularidade indexada:**

Quando houver sinalização para eixo correlato, a ficha indica apenas o código do eixo (`EX00X`). A descrição completa do confronto, da ordem recomendada e do risco de dupla marcação deve ser consultada na `MATRIZ_DE_CONFRONTOS_INTER_EIXOS_EX.md`.

## 1. ARQUITETO-PAI

Ignacio Matte-Blanco (1908–1995) foi psiquiatra e psicanalista chileno formado na tradição freudiana, professor em Santiago e Roma. Sua obra principal, *The Unconscious as Infinite Sets* (1975), formulou a teoria da bi-lógica: a coexistência, no pensamento humano, de dois modos de lógica com princípios opostos.

A **lógica assimétrica** — o modo consciente — opera com distinções: A é diferente de B, a causa precede o efeito, a relação de A com B não é a mesma que a relação de B com A. É a lógica do cotidiano e do raciocínio jurídico técnico.

A **lógica simétrica** — o modo que Matte-Blanco associa ao inconsciente e às formas primárias de pensamento — opera com o **Princípio da Simetria**: se A se relaciona com B, então B se relaciona com A da mesma forma. As relações são reversíveis. As classes colapsam em seus membros. O tempo deixa de distinguir passado de futuro. A negação perde força. O todo e a parte se tornam equivalentes.

**Por que Matte-Blanco e não outro?**

O problema que o eixo precisa capturar é específico: outputs de IA jurídica que, por generalização treinada em grandes volumes de texto, colapsam distinções que o Direito mantém com precisão técnica. O modelo viu "responsabilidade" mencionada em milhares de contextos distintos e tende a tratar esses contextos como mais semelhantes do que são. Viu "prazo" em centenas de situações e pode confundir prescrição com decadência. Viu "nulidade" aplicada em campos diferentes e pode uniformizar o que é heterogêneo.

Nenhum outro filósofo formula com a precisão de Matte-Blanco o mecanismo específico pelo qual pensamento inteligente apaga distinções por força de uma lógica de simetria — não por ignorância, mas por um modo de operar que tende a tratar o semelhante como idêntico. Essa é a operação que produz, em IA jurídica, os erros mais difíceis de detectar: não a confabulação grosseira, mas a transposição sutil entre categorias que se parecem mas têm regimes distintos.

A diferença em relação aos demais eixos é precisa: EX004 detecta o que foi evitado declarar. EX003 detecta o que foi inferido com força errada. EX002 detecta o que não foi demonstrado. EX005 detecta o horizonte não confrontado na leitura do texto. Matte-Blanco detecta o que foi *equiparado* sem ser equivalente — a distinção que o output apagou ao operar.

---

## 2. O TRAÇADO FILOSÓFICO

**Os dois princípios da bi-lógica.** Matte-Blanco formula dois princípios fundamentais da lógica simétrica:

O **Princípio da Generalização**: todo indivíduo é tratado como membro de uma classe, toda classe como membro de uma classe mais ampla. O pensamento tende a generalizar — a ver o caso particular como representante de um tipo. No limite, a parte vale pelo todo.

O **Princípio da Simetria**: toda relação assimétrica é tratada como simétrica. Se A implica B, então B implica A. Se a regra X se aplica à situação Y, a situação Z que se parece com Y recebe a regra X sem verificação das diferenças. O que vale para o credor vale para o devedor. O que se aplica ao consumidor se aplica ao fornecedor.

**A lógica simétrica no pensamento de alta performance.** Matte-Blanco não localiza a lógica simétrica apenas no pensamento primitivo ou patológico. Ele a identifica como estrutura ativa no pensamento matemático, poético, e — relevante para o a infraestrutura modular — no pensamento analógico sofisticado. A analogia jurídica é uma operação que exige, ao mesmo tempo, reconhecimento de semelhança (lógica simétrica) e verificação das diferenças que preservam a distinção (lógica assimétrica). Quando a lógica simétrica opera sem o contrapeso assimétrico, a analogia não declara o que suprimiu.

**O colapso de distinções jurídicas.** O Direito opera fundamentalmente por distinções: prescrição e decadência têm regimes diferentes e não são intercomutáveis. Nulidade absoluta e relativa têm efeitos, legitimidade e prazos distintos. Responsabilidade objetiva e subjetiva têm elementos constitutivos diferentes. Contrato de consumo e contrato paritário têm regras de interpretação, proteção e desequilíbrio distintas. Empregado e autônomo têm regimes trabalhistas opostos. Quando um output trata essas categorias como operacionalmente equivalentes — mesmo que implicitamente, por transposição não declarada — comete o colapso que este eixo detecta.

**Tradução operacional.** O traçado de Matte-Blanco aplica-se ao módulo de construção do raciocínio não como psicologia do modelo, mas como mapa das operações de colapso. A pergunta não é "o modelo confundiu conscientemente" — é "este output tratou como equivalentes categorias que o ordenamento distingue com consequências jurídicas relevantes, e essa equiparação foi declarada?"

---

## 3. A OPERAÇÃO DO EIXO

O o módulo de construção do raciocínio raciocina sob o eixo EX006 Matte-Blanco na seguinte sequência:

**Passo 1 — Identificação de operação com categorias jurídicas.**  
O o módulo de construção do raciocínio localiza no output os pontos em que categorias jurídicas são operadas: quando dois institutos são tratados como equivalentes, quando uma regra é transportada de um domínio para outro, quando uma conclusão obtida para um tipo de relação é aplicada a outro tipo, quando a generalização de um caso serve de premissa para outro.

**Passo 2 — Mapeamento de distinções relevantes suprimidas.**  
Para cada operação identificada, o o módulo de construção do raciocínio verifica se há distinção juridicamente relevante entre as categorias equiparadas. A verificação não é exaustiva — o o módulo de construção do raciocínio verifica se a distinção é relevante *para o caso concreto*, não todas as distinções possíveis entre os institutos. Distinção relevante é aquela que, se preservada, alteraria a conclusão, o regime aplicável, o prazo, o ônus ou a proteção.

A relevância da distinção para o caso concreto é verificada conforme a seguinte régua antes de qualquer marcação:

| Distinção | Tratamento |
|---|---|
| **Meramente terminológica** — diferença de vocabulário sem consequência operacional | Não aciona |
| **Técnica, mas irrelevante para o caso** — diferença real entre institutos que não altera conclusão, prazo, ônus ou proteção no caso analisado | Não aciona |
| **Relevante, mas declarada** — o output reconhece a diferença de regime, ainda que com qualificação insuficiente | Pode gerar registro de severidade Baixa |
| **Relevante e não declarada** — diferença de regime com consequência para o caso, suprimida sem declaração | Achado — severidade Média ou Alta conforme o impacto |
| **Determinante da conclusão** — a distinção colapsada é o que define o regime aplicável, o resultado ou a proteção central do output | Achado de severidade Alta ou Crítica — gate obrigatório |

**Passo 3 — Teste de declaração da equiparação.**  
O o módulo de construção do raciocínio verifica se a equiparação foi declarada. Uma transposição analógica declarada — "aplica-se por analogia o regime X, considerando que Y e Z são semelhantes em A e B, embora difiram em C" — não é achado. A ausência de declaração, quando a transposição existe e tem relevância, aciona `[SIMETRIA INDEVIDA]`.

**Passo 4 — Teste de generalização supressora.**  
O o módulo de construção do raciocínio verifica se o output generalizou a partir de um caso ou categoria de modo a apagar distinção estrutural. A generalização supressora ocorre quando: (a) a conclusão obtida para o caso A é estendida ao caso B sem declaração; (b) a extensão depende de tratar A e B como equivalentes; (c) há diferença estrutural relevante entre A e B que torna a extensão problemática ou que exigiria qualificação. Aciona `[GENERALIZAÇÃO SUPRESSORA]`.

**Passo 5 — Verificação de colapso de categorias com regimes distintos.**  
O o módulo de construção do raciocínio verifica se o output opera com categorias jurídicas que têm regimes, efeitos ou pressupostos distintos como se fossem a mesma categoria. Pares de risco frequente:

| Par | Distinção relevante |
|---|---|
| Prescrição / Decadência | Regime de impedimento, suspensão e interrupção; alegabilidade de ofício; disponibilidade |
| Nulidade absoluta / Relativa | Legitimidade para arguição; possibilidade de confirmação; reconhecimento de ofício |
| Responsabilidade objetiva / Subjetiva | Elemento culpa; ônus probatório; excludentes aplicáveis |
| Contrato de consumo / Paritário | Regras de interpretação; proteção contra cláusulas abusivas; inversão do ônus |
| Vínculo empregatício / Autônomo | Regime trabalhista; direitos e obrigações; legislação aplicável |
| Dano moral / Material | Pressupostos, critérios de quantificação, cumulabilidade, prova |
| Posse / Propriedade | Efeitos, ações cabíveis, prazo aquisitivo, proteção possessória |

A ocorrência de colapso entre categorias deste espectro, sem declaração, aciona `[DISTINÇÃO COLAPSADA]`.

**Passo 6 — Classificação e marcação.**  
O o módulo de construção do raciocínio aplica o marcador canônico, classifica a severidade e registra o achado no formato padrão.

---

## 4. O QUE CONTA COMO ACHADO REAL

Achado real é qualquer instância em que o output equipara categorias jurídicas com regimes distintos sem declarar a equiparação, ou generaliza de modo a suprimir diferença estrutural relevante para o caso concreto.

**Padrões documentados — CT-002 (Grok 2 e Gemini):**

*CT-002, Grok 2 (parecer trabalhista):* O output operou com elementos fáticos compatíveis tanto com vínculo empregatício quanto com prestação de serviços autônoma e os tratou como se produzissem o mesmo enquadramento jurídico — sem declarar que os regimes são distintos e que a diferença de enquadramento altera radicalmente o conjunto de direitos, obrigações e proteções aplicáveis. O colapso não foi na qualificação (que é domínio de EX003), mas no tratamento dos efeitos: o output operou sobre os elementos do caso como se a distinção entre os dois regimes não tivesse consequência para a análise. Marcador: `[DISTINÇÃO COLAPSADA]`, severidade Média.

*CT-002, Gemini (plano de saúde):* O output aplicou princípios de interpretação de contratos paritários a contrato de consumo (plano de saúde, contrato de adesão) sem declarar a transposição. As regras de interpretação do CDC — que invertem a presunção em favor do consumidor em cláusulas ambíguas — foram suprimidas pela aplicação do critério civilista geral. Marcador: `[SIMETRIA INDEVIDA]`, severidade Alta (a distinção de regime alterava a conclusão sobre a validade da exclusão de cobertura).

---

**Exemplos contrastivos:**

**Falso positivo — o que NÃO é achado Matte-Blanco:**  
Output que trata prescrição e decadência como "prazos extintivos" ao descrever o contexto geral de um caso, sem que a distinção entre os dois regimes seja relevante para a conclusão específica analisada. A generalização existe, mas não suprime distinção relevante para o caso concreto. O eixo não tem achado.

**Zona cinzenta — analogia declarada com ressalva insuficiente:**  
Output que aplica, "por analogia", o regime de responsabilidade objetiva do CDC a uma relação que pode ou não ser de consumo, declarando a analogia mas sem verificar se os pressupostos do regime estão preenchidos. A declaração existe — o colapso não é total. `[SIMETRIA INDEVIDA]` de severidade Baixa: a transposição foi declarada mas não qualificada quanto às diferenças que exigiriam verificação.

**Versão corrigida — como transformar `[DISTINÇÃO COLAPSADA]` em output íntegro:**

> *Versão com achado:* "O fornecedor responde pelos danos causados ao consumidor."

> *Versão corrigida:* "Se a relação for de consumo — o que exige verificação do enquadramento do contratante como destinatário final — o fornecedor responde objetivamente pelos danos, independentemente de culpa (art. 14 do CDC). Se a relação não for de consumo, a responsabilidade segue o regime civil, exigindo demonstração de culpa. A conclusão sobre o regime aplicável depende do enquadramento da relação, que não está estabelecido no material analisado."

---

**Outros padrões que contam como achado real:**

- Output que aplica prazo prescricional quando o prazo aplicável é decadencial, ou vice-versa, sem declarar a distinção de regime.
- Output que trata nulidade relativa como nulidade absoluta (ou o contrário) ao determinar os efeitos do vício, a legitimidade para arguição ou a possibilidade de confirmação.
- Output que aplica critério de quantificação de dano material ao dano moral sem declarar que os pressupostos e critérios são distintos.
- Output que transporta conclusão sobre contrato bilateral para contrato unilateral sem declarar que a reciprocidade de obrigações não existe no segundo.
- Output que generaliza a partir de precedente de uma câmara ou turma e aplica como se fosse orientação consolidada, sem verificar se outras câmaras/turmas seguem o mesmo entendimento.

---

## 5. O QUE NÃO CONTA — ANTI-PADRÕES

**Generalização ≠ supressão.**
Generalizar é operação necessária do raciocínio jurídico. O eixo captura apenas a generalização que suprime distinção *relevante para o caso concreto*. Se a distinção não altera conclusão, ônus, prazo ou regime, não há achado.

**Analogia declarada ≠ simetria indevida.**
Analogia é técnica legítima. Se o output declarou a analogia, identificou o ponto de semelhança e reconheceu a diferença relevante, não há `[SIMETRIA INDEVIDA]`.

**Erro de qualificação ≠ colapso de distinção.**
Qualificação errada de fatos é problema de EX003. O eixo EX006 aciona quando, *independentemente da qualificação adotada*, o output opera sobre os efeitos como se categorias distintas fossem equivalentes.

**Imprecisão terminológica ≠ colapso operacional.**
Uso do termo errado sem efeito sobre conclusão, prazo, ônus, proteção ou regime não fundamenta achado. O colapso de Matte-Blanco é operacional, não terminológico.

**Diferença técnica ≠ distinção relevante.**
Nem toda diferença entre institutos altera o caso. O o módulo de construção do raciocínio só aciona quando a distinção, se preservada, alteraria a conclusão ou a orientação ao operador.

---

## 6. RÉGUA DE SEVERIDADE

| Nível | Critério | Consequência no gate |
|---|---|---|
| **Baixa** | Colapso de distinção em ponto acessório; a distinção suprimida não altera a conclusão central; generalização em contexto de baixa consequência decisória | Registro no output. Sem bloqueio. A fase de refinamento textual pode incorporar qualificação de regime. |
| **Média** | Colapso de distinção em ponto de suporte à conclusão central; transposição analógica não declarada com diferença estrutural relevante; generalização que apaga distinção de regime em zona de consequência indireta | Registro com marcador. O o módulo de construção do raciocínio inclui nota sobre a distinção suprimida e o regime aplicável antes de encaminhar à fase seguinte. |
| **Alta** | Colapso de distinção diretamente determinante da conclusão; simetria indevida que inverte ônus, prazo ou proteção; equiparação de regimes incompatíveis (ex: objetiva/subjetiva, consumo/paritário) sem declaração, em questão central do output | Bloqueio parcial: o output não é encaminhado à fase seguinte sem resolução. O o módulo de construção do raciocínio produz nota sobre a distinção colapsada e suas consequências para o caso, ou sinaliza ao operador que a conclusão depende de definição prévia do regime aplicável. |
| **Crítica** | Múltiplos colapsos de distinção em conclusões decisórias; equiparação de categorias com regimes opostos em questão central; o output torna impossível ao operador identificar qual regime foi aplicado e se as proteções corretas foram consideradas | Bloqueio total. O o módulo de construção do raciocínio produz nota de inviabilidade com mapeamento das distinções colapsadas. |

---

## 7. FORMATO DE OUTPUT ESPERADO

```
ACHADO — EIXO EX006 MATTE-BLANCO | SIMETRIZAÇÃO

Marcador: [DISTINÇÃO COLAPSADA] / [SIMETRIA INDEVIDA] / [GENERALIZAÇÃO SUPRESSORA]
Severidade: Baixa / Média / Alta / Crítica

Localização no output:
[Trecho exato ou identificação precisa do segmento]

Categorias equiparadas:
[Quais institutos, regimes ou categorias jurídicas foram tratados como equivalentes]

Distinção suprimida:
[Qual diferença de regime, efeito, pressuposto ou prazo foi apagada pela equiparação —
e por que essa diferença é relevante para o caso concreto]

Consequência da supressão:
[Como o colapso altera ou pode alterar a conclusão, o ônus, o prazo ou a proteção aplicável]

A equiparação foi declarada?
[Sim — com qualificação insuficiente / Não — colapso implícito]

Acionamento de gate:
[Sem bloqueio / Nota de distinção e regime aplicável / Bloqueio parcial /
Bloqueio total com nota de inviabilidade]

Observação:
[Apenas se necessário: distinção de anti-padrão, sobreposição com EX003 ou EX005,
informação relevante para o operador.]
```

---

## 8. OPERAÇÃO DENTRO DO o módulo de construção do raciocínio

**Ativação primária:**

- Fases que operam sobre *responsabilidade civil* em contexto de possível sobreposição de regimes (objetiva/subjetiva, contratual/extracontratual, CDC/Código Civil)
- Fases que analisam *prazos* — prescrição, decadência, preclusão — onde a distinção de regime altera a estratégia
- Fases que avaliam *validade de atos* com possível confusão entre nulidade absoluta e relativa
- Fases que operam sobre *relações jurídicas* com possível equívoco de enquadramento (consumo/paritário, emprego/autônomo, posse/propriedade)
- Fases que aplicam *conclusões por analogia* ou generalizam a partir de precedente para caso com distinção estrutural relevante

**Casos secundários — ativação por sinalização:**

O eixo Matte-Blanco é ativado secundariamente quande EX003 sinaliza `[HIPÓTESE COMO CONCLUSÃO]` em qualificação jurídica — o o módulo de construção do raciocínio verifica se o problema é de tipo inferencial (Peirce) ou se, além disso, a qualificação adotada opera com colapso de distinção nos efeitos (Matte-Blanco). Podem coexistir com endereços distintos.

O eixo Matte-Blanco é ativado secundariamente quande EX005 sinaliza `[HORIZONTE NÃO CONFRONTADO]` em interpretação que transpõe regime de um domínio para outro — o o módulo de construção do raciocínio verifica se o problema é hermenêutico (horizonte não declarado na leitura) ou de simetrização (equiparação de regimes distintos no resultado da interpretação).

**Comportamento na entrega final:**

À fase de refinamento textual transmitem-se apenas marcadores não resolvidos e qualificadores de distinção. Achados de severidade Baixa podem gerar ajuste terminológico ou nota de regime. Achados de severidade Média, Alta ou Crítica devem ser resolvidos no próprio o módulo de construção do raciocínio antes de qualquer acabamento redacional.

---

## 9. DISTINÇÕES confronto de raciocíniosÍTICAS

**Matte-Blanco vs. o que parece Matte-Blanco mas não é.**

**Caso 1 — EX003 vs. EX006 em qualificação e efeitos.**
Peirce opera sobre a *inferência de qualificação*: se a conclusão de que "há vínculo empregatício" foi apresentada com força dedutiva quando é abdutiva. Matte-Blanco opera sobre os *efeitos da qualificação*: se, uma vez que o vínculo foi qualificado (correta ou incorretamente), o output tratou os efeitos do emprego como se fossem os mesmos que os do trabalho autônomo. São dois defeitos distintos que podem ocorrer separadamente ou juntos.

**Caso 2 — EX005 vs. EX006 em transposição de regime.**
Gadamer opera sobre o *processo de leitura do texto*: se o horizonte interpretativo foi declarado e o texto foi confrontado com ele. Matte-Blanco opera sobre *o resultado da aplicação*: se categorias com regimes distintos foram tratadas como equivalentes no output. Um output pode ter declarado o horizonte interpretativo (Gadamer aprovaria) e ainda assim colapsar a distinção de regime no resultado (Matte-Blanco rejeitaria). São planos distintos.

**Caso 3 — EX004 vs. EX006 em incerteza de regime.**
Bion opera sobre a *certeza epistêmica*: se o output declarou incerteza onde havia incerteza real. Matte-Blanco opera sobre *distinção de categorias*: se o output tratou como equivalentes categorias com regimes distintos. Um output pode declarar incerteza sobre qual regime é aplicável (Bion aprovaria) e ainda assim, ao analisar as consequências, tratar os dois regimes como se produzissem os mesmos efeitos (Matte-Blanco rejeitaria).

**Caso 4 — Imprecisão terminológica vs. colapso operacional.**
Usar o termo errado sem que a distinção afete a análise é problema de refinamento terminológico, não de EX006 Matte-Blanco. O eixo detecta colapso *operacional* — quando o output age sobre os efeitos como se as categorias fossem equivalentes — não imprecisão de vocabulário sem consequência para o resultado.

**Caso 5 — Toda analogia como simetria indevida.**
Analogia é instrumento legítimo do raciocínio jurídico. O eixo não é contrário à operação analógica; é contrário à analogia que suprime a diferença que exigiria qualificação ou que tornaria a transposição inaplicável. A analogia declarada, com identificação do ponto de semelhança e reconhecimento da diferença estrutural, não é achado.

**Caso 6 — EX007 vs. EX006** — *lacuna*
Distinção provisória: Levi audita a operação técnica de extração e aplicação da *ratio decidendi* do precedente paradigma; Matte-Blanco verifica se a aplicação dessa *o módulo de construção do raciocínio* apagou distinção juridicamente relevante entre regimes. Levi constrói a ponte; Matte-Blanco testa se a ponte apagou o desnível. Fechamento da distinção pendente.

**Caso 7 — EX008 vs. EX006** — *lacuna*
Distinção provisória: MacCormick mede a regra que a conclusão instituiria se universalizada; Matte-Blanco mede se a aplicação atual apagou distinção de regime entre categorias jurídicas. Um output pode formular regra universalizável (sem achado MacCormick) e ainda colapsar distinção de regime nos efeitos (achado Matte-Blanco). Fechamento da distinção pendente.

**Lacunas remanescentes:** distinções com EX001, EX002, EX009, EX010 e EX011 a fechar quando todas as fichas estiverem consolidadas.

---

## 10. CHECKLIST DE FALHA DE EXECUÇÃO

O eixo falhou quando:

- [ ] O o módulo de construção do raciocínio identificou aplicação de categoria jurídica a caso com regime distinto e não verificou se a distinção era relevante para o caso concreto
- [ ] O o módulo de construção do raciocínio marcou como `[DISTINÇÃO COLAPSADA]` uma diferença técnica que não alterava a conclusão, o ônus, o prazo ou o regime aplicável no caso analisado — falso positivo por não verificar relevância
- [ ] O o módulo de construção do raciocínio confundiu erro de qualificação jurídica (domínio de EX003) com colapso de distinção nos efeitos (domíniEX006 Matte-Blanco)
- [ ] O o módulo de construção do raciocínio marcou imprecisão terminológica sem consequência operacional como colapso de distinção
- [ ] O o módulo de construção do raciocínio não aplicou o Passo 3 (teste de declaração da equiparação) antes de marcar `[SIMETRIA INDEVIDA]` — deixou de verificar se a transposição havia sido declarada com qualificação suficiente
- [ ] O o módulo de construção do raciocínio não verificou os pares de risco do Passo 5 em output sobre responsabilidade, prazos ou validade de atos
- [ ] O o módulo de construção do raciocínio fundiu achado EX006 Matte-Blanco e achado EX003 em marcação única em questão de qualificação jurídica com colapso de efeitos
- [ ] O o módulo de construção do raciocínio fundiu achado EX006 Matte-Blanco e achado EX005 em marcação única em questão de transposição de regime interpretativo
- [ ] O output avançou à fase seguinte com marcador de severidade Alta ou Crítica sem resolução de gate
- [ ] O o módulo de construção do raciocínio não preencheu o campo "Consequência da supressão" no formato de output, tornando o achado inauditável

