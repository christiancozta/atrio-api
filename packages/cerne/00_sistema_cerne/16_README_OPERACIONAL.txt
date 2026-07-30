# README OPERACIONAL

## Finalidade

O o sistema é o sistema de confronto de raciocínios jurídicos infraestrutura modular externa.

Sua função é auditar outputs jurídicos antes do avanço, identificando riscos de raciocínio que possam comprometer tese, conclusão, enquadramento, uso de autoridade, transporte de regime, aplicação de precedente, estimativa de risco ou recomendação estratégica.

O o sistema não substitui o operador jurídico.

O o sistema controla se o raciocínio pode avançar com segurança operacional.

---

# 1. Quando usar o sistema

Use o sistema quando houver:

- parecer jurídico;
- peça processual;
- nota técnica;
- cláusula contratual;
- decisão judicial;
- memorial;
- output de IA jurídica externa;
- recomendação estratégica;
- análise de risco;
- tese inovadora;
- uso de precedente;
- estimativa de êxito;
- aplicação de conceito aberto;
- transporte de regime jurídico;
- autoridade jurisprudencial relevante;
- conclusão forte em matéria incerta.

---

# 2. Quando não usar o sistema

Não use o sistema quando o problema for apenas:

- revisão gramatical;
- clareza textual;
- estilo;
- tom;
- formatação;
- padronização visual;
- ajuste de linguagem;
- resumo simples;
- organização editorial.

Essas tarefas pertencem ao módulo de refinamento textual.

Se houver falha de raciocínio, use o sistema antes do módulo de refinamento textual.

---

# 3. Papel do sistema dentro infraestrutura modular externa

## o módulo de validação de fontes

Valida fontes, documentos, vigência, precedentes, lastro e material de entrada.

## o módulo de construção do raciocínio

Constrói ou reconstrói o raciocínio jurídico.

## o sistema

Confronta o raciocínio, identifica riscos e decide se pode avançar.

## o módulo de refinamento textual

Refina linguagem, clareza, tom, forma e apresentação.

---

# 4. Regra principal

A pergunta central do sistema não é:

> O texto está bonito?

A pergunta correta é:

> O raciocínio pode avançar com segurança operacional?

---

# 5. Arquivos do pacote

## 1. CARDS_OPERACIONAIS_CONFRONTOS_ATIVOS.txt

Matriz dos confrontos ativos.

Contém:

- sintomas;
- lentes confrontadas;
- marcadores emergentes;
- critérios de irredutibilidade;
- gate típico;
- roteamento corretivo.

Use como base material dos confrontos.

---

## 2. PROMPT_TRIAGEM.txt

Prompt para identificar:

- tipo de objeto;
- tese principal;
- trechos de risco;
- lentes prováveis;
- confrontos prováveis;
- prioridade;
- sequência de auditoria.

Não produz achado definitivo.

---

## 3. PROMPT_RODADA_A_B.txt

Prompt para aplicar lentes isoladas.

Uma lente por rodada.

Gera achados próprios da lente, sem confronto.

---

## 4. PROMPT_mecanismo interno de confronto_RODADA_C.txt

Prompt para confrontar achados isolados e verificar se há achado emergente.

É o núcleo distintivo do sistema.

---

## 5. PROMPT_GATE_TECNICO.txt

Prompt para decidir avanço:

- AVANÇA;
- AVANÇA COM AJUSTE;
- REVISÃO HUMANA;
- BLOQUEIO PARCIAL;
- BLOQUEIO TOTAL.

---

## 6. OUTPUT_INTERNO.txt

Modelo de saída técnica interna.

Pode expor:

- códigos;
- lentes;
- confrontos;
- marcadores;
- gate;
- risco de dupla marcação;
- roteamento.

---

## 7. OUTPUT_CLIENTE.txt

Modelo de saída externa.

Não expõe:

- códigos;
- lentes;
- confrontos;
- autores;
- metodologia interna;
- marcadores técnicos.

---

## 8. PROMPT_MESTRE.txt

Prompt de orquestração geral.

Pode acionar:

- triagem;
- lentes isoladas;
- Rodada de confronto;
- gate;
- saída interna;
- saída cliente.

---

## 9. PACOTE_OPERACIONAL_INDICE.txt

Mapa do pacote.

Indica função dos arquivos, ordem de uso e organização de pasta.

---

## 10. PROTOCOLO_DE_TESTE.txt

Protocolo para validar o pacote contra outputs reais ou simulados.

Contém critérios de aprovação, reprovação, falso positivo, falso negativo e dupla marcação.

---

## 11. CASOS_TESTE_BASE.txt

Conjunto de casos sintéticos para testar o sistema.

Inclui casos ruins, médios e bons.

---

## 12. CHECKLIST_AUDITORIA.txt

Checklist rápido para controlar execução.

Usar antes, durante e depois da auditoria.

---

# 6. Fo módulo de refinamento textualo recomendado de uso

## Fo módulo de refinamento textualo completo

```text
1. Rodar PROMPT_TRIAGEM
2. Verificar se há necessidade de o módulo de validação de fontes
3. Rodar PROMPT_RODADA_A_B para cada lente necessária
4. Rodar PROMPT_mecanismo interno de confronto_RODADA_C quando houver confronto ativo
5. Rodar PROMPT_GATE_TECNICO
6. Gerar OUTPUT_INTERNO
7. Gerar OUTPUT_CLIENTE, se necessário
```

---

# 7. Fo módulo de refinamento textualo rápido

Quando o tempo for limitado:

```text
1. Usar PROMPT_MESTRE
2. Pedir modo triagem
3. Rodar apenas lentes ou confrontos de prioridade alta
4. Gerar gate técnico
5. Produzir saída cliente
```

---

# 8. Fo módulo de refinamento textualo de teste

Para validar o pacote:

```text
1. Selecionar caso em CASOS_TESTE_BASE
2. Rodar triagem
3. Rodar lentes indicadas
4. Rodar Rodada de confronto, se houver confronto ativo
5. Rodar gate
6. Gerar saída interna
7. Gerar saída cliente
8. Avaliar com PROTOCOLO_DE_TESTE
9. Conferir com CHECKLIST_AUDITORIA
```

---

# 9. Estados internos de gate

Use apenas:

```text
AVANÇA
AVANÇA COM AJUSTE
REVISÃO HUMANA
BLOQUEIO PARCIAL
BLOQUEIO TOTAL
```

Não criar estados intermediários.

---

# 10. Estados externos para cliente

Converter assim:

```text
AVANÇA → Pode avançar
AVANÇA COM AJUSTE → Pode avançar com ajuste
REVISÃO HUMANA → Exige revisão técnica
BLOQUEIO PARCIAL → Não deve avançar parcialmente
BLOQUEIO TOTAL → Não deve avançar na forma atual
```

---

# 11. Confrontos ativos

## Núcleo de produção

```text
CF-019 — Peirce × Bion
[HIPÓTESE BLINDADA POR PSEUDOCERTEZA]

CF-010 — Matte-Blanco × Peirce
[COLAPSO DE REGIME POR SALTO INFERENCIAL]

CF-017 — Sócrates × Bion
[RISCO NÃO LASTREADO QUE DESESTABILIZA A TESE]

CF-012 — Matte-Blanco × MacCormick
[REGIME ESPECIAL SUBSTITUÍDO POR REGRA SISTÊMICA NÃO UNIVERSALIZÁVEL]

CF-006 — Raz × Bion
[AUTORIDADE PERFORMADA COMO CERTEZA NÃO LASTREADA]
```

## Produção assistida

```text
CF-024 — Gadamer × Hart
[FECHAMENTO REGULATÓRIO SEM DUPLA MEDIAÇÃO]

CF-007 — Levi × Matte-Blanco
[PONTE EMENTÁRIA COMO VEÍCULO DE COLAPSO CATEGORIAL]

CF-008 — Levi × Peirce
[ANALOGIA TÉCNICA COM FORÇA INFERENCIAL EXCEDIDA]

CF-014 — Toulmin × Peirce
[ARQUITETURA FORMAL COM INFERÊNCIA NÃO ESTABILIZADA]

CF-016 — Sócrates × Peirce
[TESE INOVADORA NÃO ESTABILIZADA COMO HIPÓTESE]
```

---

# 12. Comandos operacionais

## Triagem

```text
Aplique o sistema em modo triagem ao output jurídico abaixo. Não produza achados definitivos. Indique apenas lentes, confrontos, prioridade e sequência de auditoria.
```

## Lente isolada

```text
Aplique o sistema em modo lente isolada ao output jurídico abaixo, usando apenas a lente [EX000]. Não execute confronto e não produza achado emergente.
```

## Rodada de confronto

```text
Aplique o sistema em modo Rodada de confronto ao confronto [CF-000], usando os achados isolados abaixo. Verifique se há achado emergente não redutível à soma A+B.
```

## Gate técnico

```text
Aplique o gate técnico do sistema aos achados abaixo. Defina se o output avança, avança com ajuste, exige revisão humana, sofre bloqueio parcial ou bloqueio total.
```

## Saída cliente

```text
Converta o resultado interno do sistema em saída cliente, sem expor códigos, lentes, confrontos, autores ou metodologia interna.
```

## Execução completa

```text
Aplique o sistema em modo completo ao output jurídico abaixo, produzindo triagem, lentes necessárias, Rodada de confronto quando cabível, gate técnico e saída interna.
```

---

# 13. Regras de segurança operacional

Não inventar fonte.

Não validar jurisprudência sem base.

Não aplicar todas as lentes por padrão.

Não transformar toda fragilidade em bloqueio.

Não somar severidades aritmeticamente.

Não produzir Rodada de confronto sem achados isolados.

Não expor metodologia interna ao cliente.

Não encaminhar ao módulo de refinamento textual se houver falha de raciocínio.

Não tratar problema de raciocínio como problema de redação.

Não criticar por criticar.

---

# 14. Critério de boa execução

Uma execução correta do sistema deve ser:

- parcimoniosa;
- rastreável;
- proporcional;
- tecnicamente precisa;
- orientada a decisão;
- sem inflação crítica;
- sem vazamento metodológico ao cliente.

---

# 15. Resultado esperado

Ao final da auditoria, deve ser possível decidir:

```text
1. O output pode avançar?
2. Precisa de ajuste?
3. Precisa de revisão humana?
4. Deve ser bloqueado parcialmente?
5. Deve ser bloqueado totalmente?
6. Deve voltar ao módulo de validação de fontes?
7. Deve voltar ao módulo de construção do raciocínio?
8. Pode seguir para o módulo de refinamento textual?
```

---

# 16. Regra final

O o sistema não é uma camada de crítica.

O o sistema é uma camada de contenção.

Sua função é impedir que raciocínios jurídicos instáveis avancem como se estivessem prontos.
