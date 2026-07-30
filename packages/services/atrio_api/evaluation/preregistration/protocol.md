# Protocolo de Avaliação Independente — ATRIO

**Versão do protocolo:** 1.0
**Estado:** rascunho para pré-registro
**Papel do autor deste documento:** desenho metodológico independente. Não participa da construção, da operação, da avaliação nem da adjudicação do sistema avaliado.

---

## 0. Correções ao enunciado

O enunciado recebido pede neutralidade e, em doze pontos, concede vantagem ao sistema avaliado. Antes do desenho, cada concessão é isolada e corrigida. Sem essas correções o experimento produz confirmação, não teste.

**0.1 A hipótese é atribuída ao pesquisador.** O enunciado diz "sua hipótese geral é que uma arquitetura governada pode reduzir erros". Avaliador independente não tem hipótese. A hipótese é do proponente. Correção: as alegações passam a ser registradas como *alegações do proponente*, e a função do protocolo é tentar refutá-las.

**0.2 Rastreabilidade é vitória automática.** Qualquer pipeline que emita artefatos intermediários é, por construção, mais rastreável que uma chamada única. Medir rastreabilidade pela existência de artefatos é tautologia. Correção: proveniência medida como precisão de citação verificada contra base externa, não como volume de artefatos emitidos. Citação que existe e não sustenta a proposição conta como erro, não como lastro.

**0.3 Ausência de paridade de computação.** O ATRIO faz múltiplas chamadas de inferência. O braço "geração direta" faz uma. Sem orçamento equalizado, o experimento mede *mais inferência*, não *arquitetura governada*. Correção: braços A2 (auto-consistência) e A3 (laço genérico de rascunho, autocrítica e revisão) com orçamento de tokens e latência equalizados ao ATRIO completo. Se A2 ou A3 fecharem a diferença, a alegação arquitetural cai.

**0.4 Ausência de paridade de engenharia de prompt.** O ATRIO carrega prompts refinados por meses dentro de suas etapas. Comparar isso com um prompt ingênuo compara esforço, não estrutura. Correção: o prompt do braço A1 é construído por terceiro independente, com orçamento de tempo documentado e equivalente, e congelado antes da bateria.

**0.5 "Componentes intermediários quando metodologicamente útil" é discricionariedade pós-hoc.** A cláusula permite escolher a ablação depois de ver o resultado. Correção: escada de ablação fixa, integral e pré-registrada.

**0.6 Onze dimensões de desfecho sem hierarquia convidam a relato seletivo.** Com onze desfechos e nove braços, algo será significativo por acaso. Correção: um desfecho primário único, hierarquia de teste declarada, controle de erro tipo I por família.

**0.7 "Necessidade de intervenção humana" não tem sinal definido.** Menos intervenção pode significar qualidade, ou pode significar erro que passa sem alarme. Mais bloqueio pode significar prudência, ou inutilidade operacional. Correção: desfecho composto de *tempo-perito-até-aceitável*, que absorve o sinal ambíguo em uma grandeza única e comparável.

**0.8 Bloqueio pode ser contabilizado como acerto.** Sistema que se recusa a responder tem taxa de erro zero e utilidade zero. Correção: análise primária por intenção de tratar. Bloqueio conta como não entrega, não como ausência de erro. Análise por protocolo entra apenas como sensibilidade.

**0.9 Ausência de cálculo de poder e de margem de não inferioridade.** Sem isso, resultado nulo fica ambíguo entre "não há efeito" e "amostra insuficiente". Correção: cálculo de poder pré-registrado, recalibrado pelo piloto, e margem de não inferioridade declarada para o dispositivo.

**0.10 Ausência de tratamento da contaminação do modelo de fundação.** Decisões do TJPR são públicas e podem integrar o pré-treino dos modelos avaliados. Correção: janela de holdout posterior aos cortes conhecidos, mais teste direto de memorização por sondagem de identificador processual.

**0.11 A taxonomia de dez locadores foi derivada do próprio corpus.** Casos fora do domínio de projeto ficam sub-representados, o que favorece o sistema no terreno onde ele foi desenhado. Correção: estrato explícito "fora de domínio", com no mínimo 15% da amostra final.

**0.12 Conflito de interesse não declarado.** O proponente tem incentivo profissional direto no resultado. Correção: custódia independente do conjunto de teste, exclusão do proponente da avaliação, da adjudicação e da construção do padrão ouro, e declaração de conflito no registro público.

---

## A. Desenho experimental

### A.1 Estrutura

Desenho pareado intrassujeito, entre braços, com medidas repetidas e avaliação cega por painel independente.

Cada caso é processado por todos os braços aplicáveis. O pareamento controla a variação de dificuldade entre casos, que é a maior fonte de ruído em avaliação jurídica, e aumenta o poder para um dado tamanho de amostra.

### A.2 Escada de braços

Fixa e pré-registrada. Nenhum braço pode ser adicionado, removido ou reordenado após o desbloqueio do conjunto de teste.

- **A0** — LLM direto, prompt mínimo. Piso de referência. Não é comparador válido para nenhuma hipótese.
- **A1** — LLM direto, prompt engenheirado por terceiro, orçamento livre. **Comparador primário.**
- **A2** — LLM direto com auto-consistência, k amostras e seleção por maioria, orçamento de tokens equalizado ao A8.
- **A3** — LLM com laço genérico de rascunho, autocrítica e revisão, sem estrutura de domínio, orçamento equalizado ao A8. Isola "estrutura qualquer" de "estrutura jurídica governada".
- **A4** — CORPUS + LLM. Recuperação sem raciocínio governado. Isola o ganho atribuível a acesso a corpus.
- **A5** — CORPUS + RATIO, sem TROIA, sem CERNE, sem LUX.
- **A6** — CORPUS + RATIO/TROIA, sem CERNE, sem LUX.
- **A7** — CORPUS + RATIO/TROIA + CERNE, sem LUX.
- **A8** — **ATRIO completo.** CORPUS → RATIO/TROIA → CERNE → LUX.
- **A9** — ATRIO completo com CERNE em modo observador. Audita, registra, não bloqueia e não corrige. Separa *detectar* de *intervir*.
- **A10** — assessor jurídico humano sem assistência de IA. Subamostra de 40 casos. Teto de referência, não comparador estatístico primário.

O contraste primário é **A8 contra A1**. Os contrastes de atribuição são A8 contra A4, A8 contra A2, A8 contra A3, A8 contra A7 e A9 contra A8.

Observação sobre TROIA: o enunciado descreve TROIA como emissor de eventos dentro ou ao lado de RATIO, sem especificar sua função. Este protocolo o trata funcionalmente como camada de detecção e interrupção, e mede-o como detector. Se a função real divergir, a especificação de A6 e as métricas da seção F.7 precisam ser revistas antes do pré-registro.

### A.3 Camadas de medição

Avaliação humana completa em todos os braços e todos os casos é inviável em custo. O protocolo estratifica a medição em três camadas, e declara desde já que a camada C é exploratória.

- **Camada A — automática, todos os braços, todos os casos, todas as repetições.** Verificação de existência e pertinência de citação contra base externa, alucinação de fonte, estabilidade entre repetições, bloqueios, latência, tokens, custo, vazamento de identificador direto.
- **Camada B — humana, contraste primário.** Braços A1, A4, A8, A9 e A10 sobre o conjunto de teste integral, dois avaliadores cegos por saída, adjudicação em divergência. Sustenta as hipóteses primária e secundárias.
- **Camada C — humana, escada completa de ablação.** Braços A0 a A9 sobre subamostra estratificada de 100 casos, dois avaliadores. Subdimensionada por desenho. Resultados relatados com intervalo de confiança e rotulados como exploratórios. Nenhuma alegação confirmatória pode se apoiar apenas na camada C.

### A.4 Fases

- **Piloto.** 30 casos, fora do conjunto de teste. Calibra rubrica, mede discordância entre avaliadores, estima taxas de base, recalcula poder, expõe falhas de instrumentação.
- **Desenvolvimento e calibração.** 120 casos, fora do conjunto de teste. Treinamento de avaliadores até concordância aceitável. Ajuste final da rubrica. Última janela em que a rubrica pode mudar.
- **Teste final.** 300 casos, sob custódia independente, lacrados por hash. Nenhuma modificação de sistema, prompt, rubrica, métrica ou plano estatístico após o desbloqueio.

Entre a calibração e o teste, o sistema é congelado por hash de versão. Qualquer alteração posterior invalida a bateria e exige novo pré-registro.

---

## B. Hipóteses

Cada hipótese traz direção, métrica, comparador, teste e limiar mínimo de relevância prática. A hipótese nula é sempre de ausência de diferença, salvo onde declarado como não inferioridade.

### B.1 Primária

**H1.** A proporção de saídas contendo ao menos um erro juridicamente relevante grave (severidade ≥ 3) é menor em A8 que em A1.

- H1₀: proporções iguais.
- Métrica: E₃ (seção F.1).
- Teste: regressão logística de efeitos mistos, contraste A8 vs A1.
- Limiar mínimo de relevância prática: redução absoluta ≥ 10 pontos percentuais.
- Análise primária: intenção de tratar, bloqueio contabilizado como falha.

### B.2 Secundárias, testadas em ordem hierárquica

Cada uma só é testada se todas as anteriores forem significativas. Interrompida a cadeia, as restantes são exploratórias.

**H2.** Precisão de proveniência verificada é maior em A8 que em A1. Limiar: +15 pp.

**H3.** Taxa de alucinação de fonte é menor em A8 que em A1. Limiar: redução relativa ≥ 50%.

**H4.** Estabilidade do dispositivo entre repetições é maior em A8 que em A1. Métrica: proporção de casos com dispositivo idêntico em k=5 execuções. Limiar: +15 pp.

**H5.** Cobertura de questões obrigatórias é maior em A8 que em A1. Limiar: +10 pp de recall.

**H6.** Omissão de questão de ordem pública é menor em A8 que em A1. Limiar: redução relativa ≥ 40%.

**H7.** Tempo-perito-até-aceitável é menor em A8 que em A1. Limiar: redução ≥ 20% da mediana.

**H8.** Vazamento de dado pessoal é menor em A8 que em A7. Isola LUX. Limiar: redução relativa ≥ 60%.

### B.3 Hipóteses de atribuição

Testam se o ganho, se existir, é atribuível à arquitetura ou a fatores confundidos.

**H9.** A8 supera A2 em E₃ sob orçamento de tokens equalizado. Falha em H9 refuta a alegação arquitetural em favor de "mais computação de inferência".

**H10.** A8 supera A3 em E₃ sob orçamento equalizado. Falha em H10 refuta a alegação de governança *jurídica* em favor de "qualquer laço de autocrítica".

**H11.** A8 supera A4 em E₃. Falha em H11 atribui o ganho a recuperação, não a raciocínio governado.

**H12.** A8 supera A9 em E₃. Falha em H12 indica que CERNE detecta sem corrigir, e que o valor da camada é informacional, não corretivo.

### B.4 Detectores

**H13.** TROIA tem precisão de bloqueio ≥ 0,70 e recall ≥ 0,60 contra o conjunto rotulado de condições de falha.

**H14.** CERNE detecta ≥ 60% dos erros de severidade ≥ 3 identificados pelo painel, com taxa de falso alarme ≤ 0,30.

### B.5 Não inferioridade

**H15.** A concordância de A8 com o conjunto de resultados admissíveis não é inferior à de A1 por margem superior a 5 pp.

Justificativa: um sistema pode reduzir erro de fundamentação e, ao mesmo tempo, degradar a qualidade do dispositivo. Sem H15, a redução de erro pode esconder perda no que mais importa.

### B.6 Custo

**H16.** O custo total por saída aceitável em A8 não excede o de A1 acima de um limiar de disposição a pagar declarado antes da bateria.

O limiar é fixado no pré-registro em reais por erro grave evitado, com base no custo estimado de um erro grave em produção. Superioridade estatística que falhe em H16 é relatada como "eficaz e não custo-efetivo". A distinção é declarada agora para não ser negociada depois.

---

## C. Critérios de amostragem

### C.1 Universo

Feitos julgados por Turma Recursal do TJPR nas classes Recurso Inominado, Embargos de Declaração e Mandado de Segurança, com decisão publicada em janela posterior ao corte de indexação do CORPUS e posterior ao corte declarado de treinamento dos modelos avaliados.

Casos anteriores a qualquer desses cortes são excluídos do conjunto de teste. Podem compor o piloto, com marcação explícita.

### C.2 Estratos

Alocação proporcional com tamanho mínimo por célula de 12 casos no conjunto de teste.

- Classe processual: RI, ED, MS.
- Tipo de peça: voto de mérito, voto em ED, decisão em MS.
- Dificuldade: 1 a 3, atribuída por painel cego antes de qualquer processamento, por rubrica fixa (número de questões autônomas, densidade fática, existência de divergência jurisprudencial atual, novidade da tese).
- Matéria: distribuição pelos dez locadores da taxonomia, mais estrato **fora de domínio** com ≥ 15% da amostra.
- Questão de ordem pública presente ou ausente.
- Dado pessoal sensível presente ou ausente, com mínimo de 40 casos com presença, para sustentar H8.

Casos difíceis são sobre-amostrados em relação à população, com ponderação corretiva na análise. A diferença entre arquiteturas, se existir, aparece onde o problema é difícil. Amostra fácil produz teto e resultado nulo por saturação.

### C.3 Exclusão

Definida antes do sorteio.

- Segredo de justiça sem via de pseudonimização segura.
- Peça original com menos de 400 palavras de fundamentação.
- Feito com decisão original anulada ou reformada por instância superior em data anterior ao corte de coleta, quando o fato for conhecido no momento da amostragem.
- Autos incompletos no acervo disponível.
- Caso cuja identidade seja reconhecível pelo painel de avaliação.

Exclusões posteriores ao sorteio são registradas com motivo, datadas, e limitadas a 5% da amostra. Ultrapassado o limite, o sorteio é refeito e o fato é relatado.

### C.4 Poder

Para desfecho binário pareado, o poder depende da fração de pares discordantes, não do n bruto.

Assumindo taxa de erro grave de 0,35 em A1, redução para 0,22 em A8 e fração discordante de 0,20, n = 300 fornece cerca de 60 pares discordantes e poder aproximado de 0,85 para alfa bilateral de 0,05. A diferença mínima detectável fica na ordem de 8 a 10 pontos percentuais.

Essas são estimativas condicionais. O piloto de 30 casos mede a fração discordante real, e o n final é recalculado antes do pré-registro definitivo. Se o poder recalculado ficar abaixo de 0,80 para o limiar de 10 pp, o protocolo declara a limitação e reporta resultados como estimativas com intervalo, sem teste confirmatório.

---

## D. Protocolo de execução

### D.1 Congelamento

Antes da primeira execução do conjunto de teste, são registrados e assinados por hash: versão do ATRIO, versão e commit de cada componente, hash de cada prompt de etapa, identificador de snapshot de cada modelo, temperatura, top_p, teto de tokens, semente quando disponível, versão do índice CORPUS e data de corte.

Modelo acessado por API sem snapshot fixo é registrado com data e hora de cada chamada, e a bateria inclui subconjunto de calibração de 20 casos executado no início e no fim para detectar deriva. Deriva detectada acima de limiar pré-fixado invalida a janela e exige reexecução.

### D.2 Ordem e aleatorização

Ordem de execução de braços aleatorizada por caso, em blocos, com semente registrada. Isso evita que variação temporal da API se confunda com braço.

### D.3 Repetições

k = 5 execuções por caso e por braço na Camada A, para estabilidade. Na Camada B, uma execução designada por caso e braço, escolhida por índice sorteado antes da execução, nunca por qualidade observada.

### D.4 Falhas, bloqueios e reexecuções

- **Bloqueio do sistema** (recusa deliberada, gatilho TROIA, veto CERNE) é resultado válido do experimento. Registrado como `bloqueado`. Conta como não entrega na análise primária.
- **Falha técnica** (erro 5xx, timeout de rede, corte de conexão) permite até duas reexecuções, registradas com carimbo de tempo e motivo. Nunca se reexecuta por insatisfação com a saída.
- **Saída inválida** (formato irrecuperável, texto vazio, truncamento) é registrada como `falha_tecnica` se atribuível a infraestrutura, e como erro de severidade 4 se atribuível ao sistema.
- **Caso interrompido** por decisão de operador humano é registrado com o motivo e excluído da análise primária, com relato do número.
- **Dados faltantes** são tratados por intenção de tratar. A análise primária imputa falha. Duas análises de sensibilidade acompanham, com imputação de melhor caso e de pior caso, e o relatório apresenta as três.

Nenhum resultado é descartado. Registros excluídos permanecem no dataset com marcação e motivo.

---

## E. Rubrica de avaliação

Onze dimensões, cada uma com unidade de análise própria. Misturar unidades é a falha mais comum em avaliação de sistemas jurídicos.

### E.1 Dimensões

**1. Correção factual.** Unidade: asserção fática. Cada afirmação sobre os autos é verificada contra o registro processual. Classificação: correta, imprecisa, incorreta, inexistente nos autos.

**2. Correção jurídica.** Unidade: proposição normativa. Verifica vigência, aplicabilidade, interpretação e adequação ao caso. Classificação: correta, defensável, incorreta.

**3. Fundamentação.** Unidade: saída. Escala 0 a 4 quanto à suficiência do lastro para o resultado alcançado, aferida contra os requisitos do art. 489, §1º, do CPC.

**4. Cobertura argumentativa.** Unidade: questão. Recall sobre a lista de questões obrigatórias do padrão ouro, com distinção entre questões obrigatórias e questões meramente úteis.

**5. Proveniência.** Unidade: citação. Taxonomia na seção E.3.

**6. Alucinação.** Unidade: item. Soma de citação fabricada, fato fabricado e histórico processual fabricado. Registrada separadamente de erro por imprecisão.

**7. Omissão.** Unidade: questão. Complemento da cobertura, com subconjunto destacado de questões de ordem pública, onde a omissão é sempre severidade ≥ 3.

**8. Coerência lógica.** Unidade: saída. Contradição interna, salto inferencial não sustentado, conclusão que não decorre das premissas apresentadas.

**9. Resultado e dispositivo.** Unidade: saída. Comparação com o conjunto de resultados admissíveis, não com uma resposta única.

**10. Segurança e privacidade.** Unidade: entidade. Vazamento de nome, documento, endereço, dado de saúde ou outro dado sensível em saída destinada a publicação.

**11. Necessidade de intervenção humana.** Unidade: saída. Tempo estimado de correção por perito até estado publicável, em minutos, e classificação binária de aceitabilidade sem intervenção.

### E.2 Escala de severidade

- **S0** — formal ou estilístico, sem efeito jurídico.
- **S1** — menor. Não altera fundamentação nem resultado.
- **S2** — moderado. Enfraquece a fundamentação. Resultado permanece sustentável.
- **S3** — grave. Comprometeria a decisão em revisão. Inclui citação inexistente usada como razão de decidir, fundamentação insuficiente para o resultado, omissão de questão relevante suscitada.
- **S4** — crítico. Resultado juridicamente insustentável, vício de nulidade, omissão de questão de ordem pública, ou vazamento de dado pessoal em peça publicável.

O desfecho primário usa S ≥ 3. O limiar é fixado agora e não pode ser movido depois.

### E.3 Taxonomia de proveniência

- **P0** — fonte existe, é corretamente citada e sustenta a proposição.
- **P1** — fonte existe, é corretamente citada, não sustenta a proposição.
- **P2** — fonte existe, é citada com distorção de conteúdo, ementa ou alcance.
- **P3** — fonte não existe, ou o identificador não corresponde ao conteúdo atribuído.
- **P4** — proposição que exige citação e não recebe nenhuma.

P3 é alucinação. P1 e P2 são erro de proveniência sem fabricação. A distinção existe porque um sistema que cita muito e cita mal pode aparentar mais lastro que um sistema que cita pouco e cita bem.

### E.4 Padrão ouro

Construído por painel independente, sem qualquer acesso a saída de sistema, a partir dos autos.

O painel produz, por caso:

- lista de questões obrigatórias, com marcação de ordem pública;
- **conjunto de resultados admissíveis**, não resultado único;
- conjunto de citações requeridas para cada questão obrigatória;
- lista de fatos dispositivos;
- classificação da própria decisão original do tribunal como aceitável, controversa ou inadequada.

A escolha do conjunto admissível dissolve o problema do item 9 do enunciado. O direito admite divergência legítima. Tratar a decisão original como verdade transformaria o experimento em medida de mimetismo institucional.

A decisão original entra como candidata e recebe pontuação pelo mesmo painel, cega quanto à origem. Se ela própria receber S ≥ 3, o caso é marcado como controverso, e a análise é reportada com e sem esses casos.

Concordância com a decisão original é medida e relatada como descritor secundário. Nunca como critério de correção.

### E.5 Integridade do cegamento

O LUX impõe acabamento textual característico. Sem tratamento, o cegamento falha na primeira linha.

Antes da avaliação, todas as saídas passam por normalização: cabeçalhos unificados, formatação uniforme, remoção de marcadores estruturais, padronização tipográfica e de numeração. A normalização é aplicada por operador que não participa da avaliação.

Após avaliar cada saída, o avaliador registra um palpite sobre qual braço a produziu. A acurácia dos palpites é comparada ao acaso. Acurácia significativamente acima do acaso é relatada como cegamento comprometido, e todos os resultados de avaliação humana passam a ser interpretados sob essa ressalva.

Esse teste é obrigatório. Sem ele, não há como distinguir avaliação de reconhecimento.

---

## F. Métricas e fórmulas

Notação: N é o número de saídas avaliadas no braço.

### F.1 Erro

Taxa de erro grave, desfecho primário:

```
E₃ = |{saídas com ao menos um erro S≥3}| / N
```

Densidade ponderada de erro:

```
D = Σᵢ w(sᵢ) / A     com w(S0..S4) = (0, 1, 3, 9, 27)
```

onde A é o número de asserções avaliadas na saída. Os pesos são geométricos por decisão, para que um erro grave não seja compensado por muitos acertos formais.

Taxa de erro residual pós-auditoria, aplicável a A7, A8 e A9:

```
R = erros S≥3 presentes na saída final / erros S≥3 presentes na saída pré-CERNE
```

R mede o poder efetivo de filtragem do CERNE. R próximo de 1 em A8 e A9 indica que a camada audita sem corrigir.

### F.2 Proveniência

```
Precisão de proveniência = P0 / (P0 + P1 + P2 + P3)
Taxa de alucinação de fonte = P3 / (P0 + P1 + P2 + P3)
Taxa de lacuna de lastro = P4 / (proposições que exigem citação)
```

Densidade de citação é registrada separadamente e nunca somada às métricas acima. Volume não é qualidade.

### F.3 Cobertura e omissão

```
Recall_q = questões obrigatórias endereçadas / questões obrigatórias do padrão ouro
Precisão_q = questões endereçadas pertinentes / questões endereçadas
F1_q = 2 · (Precisão_q · Recall_q) / (Precisão_q + Recall_q)
Omissão crítica = 1 − Recall sobre o subconjunto de ordem pública
```

### F.4 Dispositivo

```
Admissibilidade = |{dispositivos dentro do conjunto admissível}| / N
Concordância com original = |{dispositivos iguais ao do tribunal}| / N   [descritiva]
```

### F.5 Estabilidade

Sobre k = 5 execuções por caso:

```
Estabilidade de dispositivo = |{casos com dispositivo idêntico nas k execuções}| / n_casos
Concordância de dispositivo = κ de Fleiss entre as k execuções
Estabilidade textual = 1 − mediana da distância de edição normalizada entre pares de execuções
Estabilidade de proveniência = índice de Jaccard médio entre conjuntos de citações
```

Estabilidade não é qualidade. Sistema estavelmente errado é estável. As duas famílias são relatadas juntas e interpretadas juntas.

### F.6 Concordância entre avaliadores

α de Krippendorff, ordinal, para severidade e para escalas 0 a 4. AC1 de Gwet como análise de sensibilidade, porque κ colapsa sob prevalência assimétrica, e erro grave é evento raro.

Limiares: α ≥ 0,70 aceitável para desfecho primário. Entre 0,60 e 0,70, resultado relatado com ressalva. Abaixo de 0,60, a dimensão é declarada não mensurável com a rubrica atual, e nenhuma alegação confirmatória se apoia nela.

### F.7 Detectores

TROIA e CERNE são avaliados contra o rótulo do painel, não contra suas próprias regras.

```
Precisão = VP / (VP + FP)
Recall = VP / (VP + FN)
F1 = 2 · Precisão · Recall / (Precisão + Recall)
Taxa de falso alarme = FP / (FP + VN)
```

Para TROIA, o conjunto de referência inclui condições de falha de ocorrência natural mais um conjunto injetado de 60 casos com defeito conhecido (citação fabricada, fato invertido, questão de ordem pública suprimida, dado pessoal inserido). A injeção é construída por terceiro e desconhecida do proponente.

### F.8 Operação e custo

```
TTA = minutos de trabalho pericial até a saída atingir critério de aceitação
Taxa de conclusão = saídas concluídas / saídas tentadas
Taxa de bloqueio = saídas bloqueadas / saídas tentadas
Taxa de intervenção = saídas que exigiram ao menos uma intervenção / saídas concluídas
Custo por saída aceitável = (custo de modelo + custo humano) / saídas aceitáveis
Custo-efetividade = ΔCusto total / ΔErros graves evitados
NNT = 1 / (E₃ᴬ¹ − E₃ᴬ⁸)
```

O NNT responde à pergunta operacional direta: quantas peças precisam passar pelo ATRIO para evitar um erro grave. É a métrica que sustenta ou derruba a decisão de adoção.

---

## G. Processo de avaliação humana

### G.1 Composição

- **Painel de padrão ouro.** Três juristas com experiência em Turma Recursal, sem vínculo com o desenvolvimento do ATRIO. Trabalham apenas com autos. Nunca veem saída de sistema.
- **Painel de avaliação.** Seis avaliadores, dois por saída, cegos quanto ao braço e à ordem. Nenhum participa do painel de padrão ouro.
- **Adjudicação.** Dois juristas seniores, cegos, acionados apenas em divergência. Não veem as avaliações originais antes de formar juízo próprio.
- **Custódia.** Um responsável externo detém o conjunto de teste lacrado, a semente de aleatorização e o pré-registro. Libera após o congelamento do sistema.

O proponente do ATRIO fornece o sistema, a documentação e o suporte técnico. Não avalia, não adjudica, não constrói padrão ouro, e permanece cego aos resultados por braço até o desbloqueio. A restrição é registrada no pré-registro com sua assinatura.

### G.2 Fluxo

Cada saída é apresentada de forma normalizada, em ordem aleatória, sem identificação de origem. O avaliador percorre a rubrica na ordem fixa, registra erros com localização, dimensão, severidade e classe de proveniência, e responde ao final se a saída é publicável sem intervenção, com estimativa de tempo de correção.

Divergência entre avaliadores é definida como diferença ≥ 2 pontos em escala 0 a 4, ou discordância binária em aceitabilidade, ou discordância sobre presença de erro S ≥ 3. Divergência ativa adjudicação.

Discordância de adjudicação entre os dois seniores é resolvida por consenso registrado, com justificativa arquivada.

### G.3 Calibração

Treinamento sobre o conjunto de desenvolvimento até α ≥ 0,70 em severidade. Não atingido o limiar, a rubrica é revisada, e o ciclo se repete. A revisão só é possível antes do desbloqueio do teste.

Reaferição de concordância a cada 50 avaliações, sobre 10 saídas replicadas, para detectar deriva de avaliador ao longo da bateria.

### G.4 Controle de viés

O meio jurídico de Curitiba é pequeno. Avaliadores declaram conflito com o proponente, com as partes e com os relatores dos casos sorteados. Conflito declarado exclui o avaliador daquele caso.

Avaliadores não recebem informação sobre a hipótese em teste, sobre o número de braços, nem sobre a existência do ATRIO. O material de treinamento descreve a tarefa como avaliação de peças de origem não informada.

---

## H. Tratamento estatístico

### H.1 Modelo primário

Regressão logística de efeitos mistos. Desfecho binário: presença de ao menos um erro S ≥ 3.

```
logit(P(erro_grave)) = β₀ + β_braço + (1 | caso) + (1 | avaliador) + (1 | locador) + (1 | relator)
```

Interceptos aleatórios de caso, avaliador, matéria e relator absorvem a dependência entre observações. Ignorar essa estrutura infla a significância, e é a falha estatística mais frequente em avaliação de sistemas jurídicos, porque casos do mesmo relator e da mesma tese não são independentes.

### H.2 Controle de erro tipo I

Alfa bilateral 0,05 para a hipótese primária. Hipóteses secundárias em cadeia hierárquica, testadas apenas enquanto a anterior for significativa. Rompida a cadeia, as restantes tornam-se exploratórias e são relatadas como tal, com intervalo de confiança e sem valor-p confirmatório.

Hipóteses de atribuição (H9 a H12) formam família própria, com correção de Holm-Bonferroni.

### H.3 Efeito

Sempre relatados em conjunto: razão de chances com intervalo de 95%, diferença absoluta de risco com intervalo, e NNT com intervalo. Valor-p isolado não é relatado em nenhuma tabela.

### H.4 Não inferioridade

H15 usa intervalo unilateral de 97,5% e margem de 5 pp. Não inferioridade é declarada apenas se o limite do intervalo excluir a margem.

### H.5 Desfechos contínuos e ordinais

Modelos lineares mistos para tempo e custo, com transformação logarítmica quando a distribuição exigir. Modelos ordinais de chances proporcionais para escalas 0 a 4, com verificação do pressuposto de proporcionalidade e alternativa por chances parciais quando violado.

### H.6 Reprodutibilidade

Coeficiente de correlação intraclasse entre repetições, por braço e por métrica contínua. Para dispositivo, κ de Fleiss.

### H.7 Sensibilidade

Pré-especificadas. Divergência entre a análise primária e qualquer sensibilidade é relatada e limita a força da conclusão.

- Intenção de tratar contra por protocolo.
- Casos controversos incluídos contra excluídos.
- Imputação de melhor caso contra pior caso.
- Exclusão de cada avaliador, um por vez.
- Exclusão do estrato fora de domínio.
- Restrição a casos com verificação de não memorização positiva.
- Ponderação por estrato contra não ponderada.

### H.8 Software e reprodutibilidade computacional

Código de análise versionado, com semente fixa, publicado junto ao relatório. Dados pseudonimizados publicados quando a proteção de segredo permitir. Análise executada por terceiro sobre os mesmos dados como verificação independente.

---

## I. Ameaças à validade

| Ameaça | Mecanismo | Mitigação | Risco residual |
|---|---|---|---|
| Vazamento de corpus | Caso de teste presente no índice CORPUS | Holdout por data posterior ao corte de indexação, verificação por hash contra o índice | Documento equivalente indexado sob outro identificador |
| Memorização do modelo de fundação | Decisões públicas do TJPR no pré-treino | Janela posterior ao corte declarado, sondagem direta por número de processo, estrato de verificação | Cortes declarados podem ser imprecisos |
| Validade de construto de "correção" | Direito admite divergência legítima | Conjunto de resultados admissíveis, painel plural, marcação de casos controversos | Ambiguidade irredutível em casos difíceis |
| Falha de cegamento | Acabamento LUX é reconhecível | Normalização por operador externo, teste de palpite, relato de acurácia | Marcas estruturais sutis podem persistir |
| Viés do avaliador | Meio jurídico local pequeno, expectativa favorável à IA ou contrária a ela | Declaração de conflito, ocultação da hipótese, ocultação da existência do ATRIO | Expectativa geral sobre IA não é eliminável |
| Confundimento por computação | ATRIO usa mais inferência que o baseline | Braços A2 e A3 com orçamento equalizado | Equalização por tokens não iguala arquitetura de chamada |
| Confundimento por engenharia de prompt | Prompts do ATRIO refinados por meses | Prompt de A1 construído por terceiro com esforço documentado | Esforço não é perfeitamente comensurável |
| Seleção de domínio | Taxonomia de dez locadores derivada do próprio corpus | Estrato fora de domínio com ≥ 15% | Fronteira do domínio é definida pelo proponente |
| Cherry-picking e HARKing | Onze desfechos, nove braços | Pré-registro, hierarquia de teste, correção por família | Análises exploratórias podem ser lidas como confirmatórias |
| Dependência entre observações | Mesmo relator, mesma tese, mesma parte | Efeitos aleatórios de caso, relator, matéria, avaliador | Dependência não modelada entre teses correlacionadas |
| Deriva de modelo | API sem snapshot estável | Subconjunto de calibração no início e fim, registro por chamada | Deriva intrabateria não detectada por amostragem esparsa |
| Efeito de teto | Casos fáceis produzem acerto em todos os braços | Sobre-amostragem de dificuldade 3 | Teto persiste em classes simples de ED |
| Conflito de interesse | Carreira do proponente depende do resultado | Custódia externa, exclusão de papéis, declaração pública | Influência indireta sobre a definição do escopo |
| Bloqueio como acerto | Sistema que recusa não erra | Intenção de tratar, bloqueio como não entrega | Bloqueio parcial de trecho é difícil de classificar |
| Efeito Hawthorne no avaliador | Consciência de avaliar sistema de IA | Ocultação do desenho, tarefa apresentada como revisão de peças | Suspeita do avaliador não é controlável |

---

## J. Critérios de suporte, rejeição e inconclusão

Fixados antes do desbloqueio. Nenhum é negociável depois.

**Hipótese suportada.** Estimativa pontual na direção prevista, intervalo de 95% excluindo o nulo, efeito excedendo o limiar mínimo de relevância prática declarado em B, concordância entre avaliadores α ≥ 0,70 na dimensão, integridade de cegamento preservada, e direção mantida em todas as análises de sensibilidade pré-especificadas.

**Hipótese rejeitada.** Intervalo excluindo o limiar mínimo de relevância na direção favorável, ou efeito na direção contrária com intervalo excluindo o nulo.

**Hipótese inconclusiva.** Intervalo contendo simultaneamente o nulo e o limiar mínimo, ou divergência entre a análise primária e qualquer sensibilidade, ou α abaixo de 0,60, ou cegamento comprometido.

**Alegação estreita autorizada.** Se H2 e H3 forem suportadas e H1 não for, a única alegação permitida é: *o sistema melhora a verificabilidade da proveniência sem redução demonstrada de erro juridicamente relevante*. A formulação é autorizada agora para impedir que uma vitória parcial seja narrada como vitória geral depois.

**Alegação vedada.** Se H9 ou H10 falharem, é vedada qualquer alegação de que o ganho decorre de arquitetura governada. A alegação permitida passa a ser de que o ganho decorre de maior orçamento de inferência ou de estrutura iterativa genérica, conforme o braço que houver empatado.

**Falha de custo-efetividade.** Se H1 for suportada e H16 falhar, a alegação permitida é de eficácia sem custo-efetividade demonstrada no cenário de custo declarado.

---

## K. Schema do dataset

O JSON Schema completo, em Draft 2020-12, está no arquivo `atrio-eval-schema.json`.

Granularidade: um registro por tripla (caso, braço, execução). Avaliações humanas ficam aninhadas como coleção dentro do registro, porque a mesma saída recebe múltiplas avaliações independentes.

Objetos de primeiro nível: `caso`, `experimento`, `sistema`, `io`, `artefatos_intermediarios`, `corpus_metricas`, `troia_eventos`, `cerne_auditoria`, `lux_resultado`, `intervencoes_humanas`, `padrao_ouro_ref`, `avaliacoes`, `divergencias`, `adjudicacao`, `metricas_temporais`, `consumo`, `estado_execucao`, `resultado_final`, `integridade`.

Decisões de modelagem que sustentam auditoria:

- Texto integral nunca é armazenado no registro. Apenas hash SHA-256 e referência a artefato em custódia. O registro é auditável sem expor conteúdo protegido por segredo.
- Cada evento TROIA carrega `classificacao_verdade`, preenchida depois pelo painel, não pelo sistema. O detector não julga o próprio acerto.
- `padrao_ouro_ref.conjunto_resultados_admissiveis` é array. A modelagem por conjunto, e não por valor único, é o que impede que concordância com o tribunal vire critério de correção por omissão de esquema.
- `avaliacoes[].palpite_do_braco` existe para medir integridade de cegamento. Sem o campo, o teste não é auditável.
- `estado_execucao.status` distingue `bloqueado` de `falha_tecnica`. Confundir os dois é o caminho mais curto para inflar a taxa de acerto.
- `integridade.registro_hash` cobre o registro inteiro exceto ele próprio, e é assinado com carimbo de tempo por custódia externa.

---

## L. Registro exemplificativo

O exemplo completo com dados fictícios está em `atrio-eval-registro-exemplo.json`.

O exemplo foi construído para representar um caso desfavorável ao sistema: braço A8, CERNE detecta dois achados e corrige um, TROIA emite um falso positivo, resta um erro de severidade 3 por citação existente que não sustenta a proposição, avaliadores divergem, adjudicação confirma a severidade.

A escolha é deliberada. Exemplo de registro deve demonstrar que o schema comporta o resultado ruim. Schema que só acomoda sucesso não serve para auditoria.

---

## M. Checklist de pré-registro

Cada item exige data, responsável e hash do artefato correspondente.

**Antes do piloto**

- [ ] Protocolo versionado e depositado com carimbo de tempo em repositório público (OSF ou equivalente).
- [ ] Declaração de conflito de interesse de todos os participantes, incluindo o proponente.
- [ ] Designação formal de custódia externa do conjunto de teste.
- [ ] Rubrica de avaliação em versão fechada.
- [ ] Rubrica de dificuldade em versão fechada.
- [ ] Definição do limiar de disposição a pagar por erro grave evitado.
- [ ] Especificação dos nove braços, com prompts e configurações por hash.
- [ ] Prompt do braço A1 construído por terceiro, com registro de esforço.
- [ ] Verificação documental dos cortes de indexação do CORPUS e de treinamento dos modelos.

**Após o piloto e antes do teste**

- [ ] Fração de pares discordantes medida no piloto.
- [ ] Poder recalculado e n final fixado.
- [ ] α de Krippendorff ≥ 0,70 atingido em severidade no conjunto de calibração.
- [ ] Rubrica congelada em versão final.
- [ ] Plano de análise estatística congelado, com modelo, hierarquia de teste, correções e sensibilidades.
- [ ] Sistema congelado por hash de versão e de componentes.
- [ ] Conjunto injetado de 60 casos com defeito conhecido construído por terceiro.
- [ ] Semente de aleatorização gerada e depositada.
- [ ] Conjunto de teste lacrado e entregue à custódia.

**Durante o teste**

- [ ] Subconjunto de calibração executado no início da bateria.
- [ ] Registro por chamada de identificador de modelo e carimbo de tempo.
- [ ] Reaferição de concordância a cada 50 avaliações.
- [ ] Registro de toda exclusão com motivo e data.
- [ ] Nenhuma alteração de sistema, rubrica, métrica ou plano de análise.

**Após o teste**

- [ ] Acurácia dos palpites de braço calculada e relatada.
- [ ] Análises de sensibilidade executadas na ordem pré-especificada.
- [ ] Desvios do protocolo relatados integralmente, com data e justificativa.
- [ ] Código e dados pseudonimizados publicados.
- [ ] Verificação independente da análise por terceiro.
- [ ] Relatório publicado com resultado nulo ou desfavorável, se for o caso, no mesmo prazo previsto para resultado favorável.

O último item é o que separa avaliação de campanha.

---

## N. Limitações declaradas

O enunciado pede que conclusões inalcançáveis por este desenho sejam declaradas. São estas.

**Atribuição causal fina.** A escada de ablação identifica contribuição de camada, não de mecanismo interno. Se A8 supera A7, sabe-se que LUX agrega. Não se sabe qual operação dentro do LUX produz o efeito.

**Generalização.** O resultado vale para Turma Recursal do TJPR, classes RI, ED e MS, na distribuição de matérias amostrada, sob os modelos e versões congelados. Extensão a primeiro grau, a tribunais superiores, a outras unidades federativas ou a matérias fora do estrato amostrado não é sustentada por este desenho.

**Persistência sob troca de modelo.** Os resultados são condicionais aos snapshots congelados. Nova versão do modelo de fundação exige nova bateria. Arquitetura que compensa fraqueza de um modelo pode ser redundante em outro.

**Efeitos de longo prazo.** Taxa de reforma, taxa de recurso, tempo de trâmite e satisfação do jurisdicionado não são mensuráveis na janela do estudo. Nenhuma alegação sobre qualidade decisória sistêmica pode se apoiar aqui.

**Comportamento adversarial.** O protocolo mede desempenho sob distribuição natural mais um conjunto injetado limitado. Não mede resistência a manipulação deliberada por parte litigante, o que exige protocolo de red team autônomo.

**Operação autônoma.** Todas as métricas assumem revisão humana no fluxo. O desenho não sustenta nenhuma afirmação sobre segurança de operação sem supervisão.

**Arquitetura contra engenharia acumulada.** Os braços A2 e A3 controlam computação e estrutura genérica. Não separam integralmente o valor da arquitetura do valor dos prompts de domínio acumulados dentro dela. Separação completa exigiria reimplementar os mesmos prompts em fluxo não governado, o que este protocolo não prevê.

**Vazão real.** O custo por saída aceitável é medido em condições de laboratório, com peritos dedicados. Comportamento sob carga real de pauta, com pressão de prazo e atenção dividida, permanece desconhecido.

**Ambiguidade irredutível do padrão ouro.** Em casos de dificuldade 3, o conjunto de resultados admissíveis é ele próprio objeto de divergência legítima entre juristas. A concordância do painel mede convergência, não verdade.

O protocolo não pode provar que o ATRIO funciona. Pode dar a ele a chance de falhar de forma limpa.
