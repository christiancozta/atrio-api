# MATRIZ DE CONFRONTOS INTER-EIXOS — o módulo de construção do raciocínio EX

**Função:** documento-mãe de governança relacional dos eixos EX.  

---

## 1. Regra arquitetural

As fichas EX declaram operações próprias, critérios de ativação, não-acionamentos e pontos cegos em linguagem funcional. Quando precisarem sinalizar outro eixo, devem usar apenas o código `EX00X`, sem reconstruir o confronto dentro da própria ficha.

A relação nominal entre eixos — confrontos, precedências, sinalizações, pares produtivos, riscos de dupla marcação e achados emergentes — pertence a esta matriz.

> **A ficha nomeia funções e sinaliza códigos.  
> A matriz explica confrontos.  
> O o módulo de construção do raciocínio executa o roteamento.**

---

## 2. Tabela de decodificação dos códigos EX

| Código | Método | Arquiteto-pai |
|---|---|---|
| **EX001** | Arquitetura Argumentativa | Stephen Toulmin |
| **EX002** | Dialética | Sócrates |
| **EX003** | Abdutivo | Charles Sanders Peirce |
| **EX004** | Integridade Cognitiva | Wilfred R. Bion |
| **EX005** | Hermenêutico | Hans-Georg Gadamer |
| **EX006** | Simetrização | Ignacio Matte-Blanco |
| **EX007** | Analógico-Precedental | Edward H. Levi |
| **EX008** | Justificação de Segunda Ordem | Neil MacCormick |
| **EX009** | Textura Aberta | H. L. A. Hart |
| **EX010** | Validade Normativa | Hans Kelsen |
| **EX011** | Autoridade Prática | Joseph Raz |

---

## 3. Tabela-mãe de confrontos

| Código | Eixo A | Eixo B | Tipo de relação | Risco de confusão | Ordem recomendada | Fronteira decisiva | Achado emergente possível |
|---|---|---|---|---|---|---|---|
| **CF-001** | EX010 Validade Normativa | EX011 Autoridade Prática | Sequencial | Confundir validade formal com peso prático | EX010 → EX011 | Fonte válida não significa fonte decisiva | Fonte formalmente apta, mas autoridade superestimada |
| **CF-002** | EX010 Validade Normativa | EX009 Textura Aberta | Sequencial | Tratar abertura semântica como problema de validade | EX010 → EX009 | Primeiro estabiliza a fonte; depois testa abertura do conceito | Norma válida aplicada com conceito aberto fechado sem critério |
| **CF-003** | EX010 Validade Normativa | EX005 Hermenêutico | Sequencial | Interpretar fonte formalmente deslocada antes de verificar sua aptidão | EX010 → EX005 | Fonte inválida ou deslocada não deve ser refinada hermeneuticamente | Fonte apta, mas leitura situada não declarada |
| **CF-004** | EX011 Autoridade Prática | EX007 Analógico-Precedental | Sequencial/paralelo | Confundir peso da autoridade com operação técnica do precedente | EX007 → EX011 | Primeiro estabiliza a razão de decidir; depois calibra o peso | Precedente tecnicamente mal aplicado e ainda superestimado |
| **CF-005** | EX011 Autoridade Prática | EX001 Arquitetura Argumentativa | Complementar | Confundir backing existente com backing suficiente | EX001 → EX011 | Arquitetura pergunta se há suporte; autoridade prática pergunta quanto esse suporte pesa | Backing presente, mas autoridade usada com força excessiva |
| **CF-006** | EX011 Autoridade Prática | EX004 Integridade Cognitiva | Sobreposição controlada | Tratar certeza performada como autoridade, ou autoridade fraca como certeza | EX011 ↔ EX004 | Um eixo calibra peso; outro verifica lastro da segurança declarada | “Jurisprudência pacífica” sem lastro e com força decisiva |
| **CF-007** | EX007 Analógico-Precedental | EX006 Simetrização | Confronto paralelo | Tratar falha de o módulo de construção do raciocínio como colapso categorial, ou o inverso | EX007 ↔ EX006 | Levi testa a ponte; Matte-Blanco testa se a ponte apagou diferença relevante | Precedente aplicado por analogia que suprime regime jurídico distinto |
| **CF-008** | EX007 Analógico-Precedental | EX003 Abdutivo | Complementar | Tratar analogia como dedução ou falha técnica como problema inferencial | EX007 → EX003 ou paralelo | Levi testa a técnica do precedente; Peirce testa a força inferencial da analogia | Analogia bem construída, mas apresentada com força dedutiva |
| **CF-009** | EX007 Analógico-Precedental | EX008 Justificação de Segunda Ordem | Sequencial/prospectivo | Confundir extração de o módulo de construção do raciocínio com regra futura universalizada | EX007 → EX008 | Levi olha para trás; MacCormick olha para frente | o módulo de construção do raciocínio extraída corretamente, mas regra futura não universalizável |
| **CF-010** | EX006 Simetrização | EX003 Abdutivo | Fronteira negativa | Confundir qualificação incerta com colapso de categorias | EX003 → EX006 quando necessário | Peirce testa inferência; Matte-Blanco testa efeitos de categorias equiparadas | Hipótese de enquadramento mal representada e efeitos de regimes distintos colapsados |
| **CF-011** | EX006 Simetrização | EX005 Hermenêutico | Complementar | Confundir horizonte interpretativo com equiparação indevida de regimes | EX005 → EX006 ou paralelo | Gadamer testa a leitura; Matte-Blanco testa o efeito categorial da leitura | Texto lido por horizonte civilista e aplicado a regime consumerista |
| **CF-012** | EX006 Simetrização | EX008 Justificação de Segunda Ordem | Complementar | Confundir colapso categorial com consequência sistêmica da regra | EX006 → EX008 | Um eixo detecta distinção apagada; outro mede a regra universalizada | Equiparação indevida que, universalizada, esvazia regime especial |
| **CF-013** | EX001 Arquitetura Argumentativa | EX002 Dialética | Sequencial clássico | Confundir falha estrutural com objeção não enfrentada | EX001 → EX002 | Primeiro verifica se a tese tem arquitetura; depois testa resistência adversarial | Argumento estruturalmente completo, mas vulnerável à melhor objeção |
| **CF-014** | EX001 Arquitetura Argumentativa | EX003 Abdutivo | Fronteira negativa | Tratar hipótese como conclusão como simples garantia ausente | EX003 após EX001, se houver qualificação jurídica | Toulmin mapeia peças do argumento; Peirce calibra tipo de inferência | Tese com estrutura aparente, mas conclusão abdutiva apresentada como necessária |
| **CF-015** | EX001 Arquitetura Argumentativa | EX008 Justificação de Segunda Ordem | Sequencial | Confundir arquitetura interna com justificação externa da regra | EX001 → EX008 | Toulmin testa sustentação da tese; MacCormick testa regra que a tese instituiria | Argumento internamente completo, mas regra universalizada falha |
| **CF-016** | EX002 Dialética | EX003 Abdutivo | Fronteira negativa | Tratar hipótese mal representada como objeção adversarial | EX003 ↔ EX002 | Peirce testa força inferencial; Sócrates testa resistência da tese | Conclusão abdutiva que também não sobrevive à objeção central |
| **CF-017** | EX002 Dialética | EX004 Integridade Cognitiva | Sobreposição controlada | Tratar incerteza apagada como mera objeção | EX004 ↔ EX002 | Bion testa honestidade epistêmica; Sócrates testa objeção estrutural | Risco não lastreado que desestabiliza a tese sob confronto |
| **CF-018** | EX002 Dialética | EX008 Justificação de Segunda Ordem | Sequencial/contraponto | Confundir objeção direta à tese com teste da regra universalizada | EX002 → EX008 ou paralelo | Sócrates ataca a tese; MacCormick testa a regra que ela criaria | Tese resiste à objeção, mas falha como regra geral |
| **CF-019** | EX003 Abdutivo | EX004 Integridade Cognitiva | Sobreposição controlada | Confundir hipótese não verificada com certeza sem lastro | EX003 ↔ EX004 | Peirce testa tipo de inferência; Bion testa declaração de incerteza | Hipótese apresentada como conclusão e performada com segurança excessiva |
| **CF-020** | EX003 Abdutivo | EX009 Textura Aberta | Complementar | Confundir aplicação de conceito aberto com inferência abdutiva | EX009 ↔ EX003 | Hart testa abertura do conceito; Peirce testa força da conclusão aplicada | Conceito aberto fechado sem critério e conclusão tratada como dedução |
| **CF-021** | EX003 Abdutivo | EX005 Hermenêutico | Complementar | Confundir leitura de texto com qualificação inferencial do resultado | EX005 → EX003 | Gadamer testa horizonte de leitura; Peirce testa força da conclusão extraída | Texto lido sem horizonte e conclusão interpretativa apresentada como necessária |
| **CF-022** | EX004 Integridade Cognitiva | EX005 Hermenêutico | Complementar | Confundir controvérsia omitida com horizonte não declarado | EX005 ↔ EX004 | Gadamer testa leitura situada; Bion testa estado de certeza do domínio | Interpretação em matéria controvertida apresentada como pacificada |
| **CF-023** | EX004 Integridade Cognitiva | EX009 Textura Aberta | Complementar | Confundir incerteza do domínio com abertura da linguagem normativa | EX009 ↔ EX004 | Hart testa textura do conceito; Bion testa segurança declarada | Standard aberto fechado sem critério e apresentado com certeza não lastreada |
| **CF-024** | EX005 Hermenêutico | EX009 Textura Aberta | Analítico | Confundir horizonte interpretativo com penumbra semântica | EX005 ↔ EX009 | Gadamer testa o encontro intérprete-texto; Hart testa abertura da regra | Texto lido sem horizonte e conceito aberto fechado sem critério |

---

## 4. Campos de indexação por confronto

Cada confronto pode ser indexado pelos seguintes campos:

```yaml
codigo: CF-000
eixos:
  - EX000
  - EX000
tipo_relacao: sequencial | paralelo | complementar | fronteira_negativa | sobreposicao_controlada | gate
sintoma_ativacao: 
erro_roteamento:
ordem_recomendada:
fronteira_decisiva:
produto_exportavel:
lente_descartavel:
achado_emergente:
gate:
```

---

## 5. Índice por sintoma de ativação

| Sintoma no output | Confrontos prováveis |
|---|---|
| Fonte normativa usada como fundamento decisivo | CF-001, CF-002, CF-003 |
| Precedente citado como razão central | CF-004, CF-007, CF-008, CF-009 |
| Jurisprudência pacífica afirmada sem demonstração | CF-004, CF-006, CF-007 |
| Analogia entre regimes jurídicos | CF-007, CF-010, CF-012 |
| Conclusão de qualificação jurídica forte | CF-010, CF-014, CF-016, CF-019 |
| Estimativa de risco ou certeza sem método | CF-006, CF-017, CF-019, CF-023 |
| Texto jurídico interpretado como claro | CF-011, CF-021, CF-022, CF-024 |
| Conceito aberto aplicado como regra fechada | CF-002, CF-020, CF-023, CF-024 |
| Tese inovadora ou extensiva | CF-012, CF-015, CF-018 |
| Argumento estruturalmente completo, mas frágil | CF-013, CF-015, CF-018 |

---

## 6. Índice por ordem de ativação

### 6.1 Sequências fortes

| Sequência | Uso |
|---|---|
| EX010 → EX011 | Fonte normativa ou autoridade mobilizada |
| EX010 → EX009 | Norma apta com conceito aberto |
| EX010 → EX005 | Fonte apta que exige interpretação situada |
| EX001 → EX002 | Tese com arquitetura mínima que precisa ser confrontada |
| EX001 → EX008 | Tese estruturada que pode instituir regra futura |
| EX007 → EX011 | Precedente primeiro como operação técnica, depois como autoridade |
| EX007 → EX008 | Precedente aplicado hoje e regra futura gerada pela aplicação |

### 6.2 Pares paralelos

| Par | Uso |
|---|---|
| EX007 ↔ EX006 | Analogia precedental com possível apagamento de distinção |
| EX003 ↔ EX004 | Hipótese inferencial e segurança epistêmica |
| EX005 ↔ EX009 | Horizonte interpretativo e textura aberta |
| EX006 ↔ EX008 | Distinção colapsada e regra universalizada |
| EX002 ↔ EX008 | Objeção à tese e teste da regra futura |

---

## 7. Regra de roteamento

O o módulo de construção do raciocínio deve evitar dupla marcação quando o defeito pertence primariamente a um eixo.

1. Se a fonte é formalmente inválida ou deslocada, estabilizar validade antes de discutir peso, textura, interpretação ou consequência sistêmica.
2. Se o problema é operação técnica de precedente, estabilizar o módulo de construção do raciocínio, distinguishing e alcance antes de calibrar peso prático.
3. Se o problema é qualificação jurídica por hipótese, testar tipo de inferência antes de tratar como objeção ou colapso categorial.
4. Se o problema é conceito aberto, testar critério de fechamento antes de tratar como incerteza genérica.
5. Se a tese não tem arquitetura mínima, corrigir arquitetura antes de submetê-la à objeção adversarial.
6. Se a tese está estruturada e resiste à objeção, testar a regra futura que ela instituiria quando houver alcance generalizável.

---

## 8. Regra de exportação

Entre fichas e fases, exportam-se apenas:

- achado;
- marcador;
- severidade;
- gate;
- pendência;
- restrição;
- versão corrigida ou nota de inviabilidade;
- sinalização de eixo seguinte, quando necessária.

Não se exporta:

- postura cognitiva;
- lente permanente;
- suspeita generalizada;
- modo adversarial;
- modo formalista;
- modo antianalógico;
- modo hermenêutico residual;
- modo de hiperabstração.

---

## 9. Observação de manutenção

Sempre que um eixo for renomeado, dividido, fundido ou deslocado, a alteração deve ocorrer primariamente nesta matriz. As fichas individuais só precisam ser reabertas se a operação interna do eixo mudar.

Essa regra reduz acoplamento, preserva modularidade e facilita futura indexação em backend, banco vetorial, roteador de eixos ou painel de auditoria.
