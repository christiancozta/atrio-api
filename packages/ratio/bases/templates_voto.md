---
modulo: ratio
artefato: templates_voto
ordinal: 5
origem: 2.RATIO/05_templates_voto_v4.txt
sha256_origem: e264f3cfc577fd36c5a8523fa547471b01bc3163eeef2443761d7eb607b16263
---

05_TEMPLATES_VOTO_V4 — TEMPLATES DE VOTO

NOTA DE ARQUITETURA
Base de templates de voto de todos os ritos do RATIO.

ESTADO ATUAL DA BASE
Esta base contém, no momento, templates validados dos módulos RI e ED, identificados pelos atributos id: RI-CONHECIDO, RI-NAO-CONHECIDO, ED-REJEICAO, ED-ACOLHIMENTO.

A base não contém, no momento, templates do Módulo MS.

REGRA DE USO HÍBRIDA — APLICÁVEL A TODOS OS MÓDULOS
Template só é usado se localizado nesta base e compatível com módulo, fase, tipo de decisão, rota decisória, matéria e resultado.

Enquanto não houver template do módulo ativo nesta base, o módulo opera com minuta estrutural e marca [TEMPLATE NAO LOCALIZADO — VALIDAR MODELO]. Isso não é erro: é o comportamento previsto para ausência de template.

Quando um template for incorporado a esta base, identificado por id próprio, o módulo passa a localizá-lo e utilizá-lo automaticamente na fase compatível, sem necessidade de alterar regra. A incorporação do template à base é o único ato necessário para ativá-lo.

REGRA DE NOMENCLATURA PARA INCORPORAÇÃO FUTURA
Todo template novo deve ter id no padrão MODULO-TIPO, em caixa alta, para que o módulo o reconheça. Exemplos de id esperados para o Módulo MS, quando vierem a ser incorporados: MS-LIMINAR-DEFERIMENTO, MS-LIMINAR-INDEFERIMENTO, MS-LIMINAR-PARCIAL, MS-INDEFERIMENTO-INICIAL, MS-SENTENCA-CONCESSAO, MS-SENTENCA-DENEGACAO, MS-EXTINCAO-PERDA-OBJETO. A criação do conteúdo desses templates depende de validação do operador; esta nota apenas fixa o padrão de id esperado.

------------------------------------------------------------------------

# TEMPLATES DE VOTO — 2ª Turma Recursal TJPR

Autor: Christian — OAB-PR 89.297
Arquivo de referência para consulta obrigatória na Fase 6 do sistema
de apoio à elaboração de votos.

═══════════════════════════════════════════════════════════════════════
CONVENÇÕES DE MARCAÇÃO
═══════════════════════════════════════════════════════════════════════

[SE condição] ... [/SE]
    Bloco condicional. Ativa conforme o resultado definido na Fase 5
    ou conforme elemento identificado na análise.

{conteúdo variável}
    Lacuna a preencher com conteúdo do caso concreto.

{opção A | opção B}
    Escolha entre alternativas. Selecionar conforme o caso.

Texto fora de marcadores
    Fraseado fixo. Reproduzir na íntegra, sem alteração.

═══════════════════════════════════════════════════════════════════════


<template id="RI-CONHECIDO">
## TEMPLATE RI — CONHECIMENTO

{ementa}

{{shared: gabinete/formulas_voto#relatorio_dispensado}}

[SE houver pedido de justiça gratuita]
De plano, da análise dos autos, verifica-se a presença de elementos 
probatórios aptos a comprovar a situação de vulnerabilidade econômica, 
razão pela qual concedo à parte recorrente a gratuidade da justiça.
[/SE]

Satisfeitos os pressupostos processuais de admissibilidade, tanto 
objetivos quanto subjetivos, o presente recurso merece ser conhecido.

[SE houver preliminares de mérito]
{análise das preliminares}
[/SE]

Cinge-se a controvérsia à {objeto da controvérsia}.

{desenvolvimento da análise de mérito}

Sendo assim, à luz da legalidade e da jurisprudência, a 
{manutenção | reforma} da sentença é a medida que se impõe.

[SE desprovimento]
Ante o exposto, voto pelo CONHECIMENTO e DESPROVIMENTO do recurso 
interposto, mantendo integralmente a sentença de primeiro grau por 
seus próprios fundamentos.

Em razão da sucumbência recursal, condeno a recorrente ao pagamento 
de honorários advocatícios, os quais fixo em 20% sobre o valor 
{atualizado da causa | atualizado da condenação}, nos termos do 
art. 55 da Lei nº 9.099/95.
[/SE]

[SE houver pedido de justiça gratuita]
, cuja exigibilidade fica suspensa em razão da gratuidade da justiça.
[/SE]

[SE parcial provimento]
Ante o exposto, voto pelo CONHECIMENTO e PARCIAL PROVIMENTO do 
recurso interposto, para o fim de {consequência do provimento}, nos 
termos da fundamentação acima.

Diante do parcial êxito recursal, inaplicável a condenação ao 
pagamento de verbas sucumbenciais, nos termos do art. 55 da Lei nº 
9.099/95 e em conformidade com o entendimento firmado no PUIL nº 
3.874/PR.
[/SE]

[SE provimento]
Ante o exposto, voto pelo CONHECIMENTO e PROVIMENTO do recurso 
interposto, para o fim de {consequência do provimento}, nos termos 
da fundamentação acima.

Diante do êxito recursal, inaplicável a condenação ao pagamento de 
verbas sucumbenciais, nos termos do art. 55 da Lei nº 9.099/95.
[/SE]
</template>


<template id="RI-NAO-CONHECIDO">
## TEMPLATE RI — NÃO CONHECIMENTO

Aplicável a qualquer hipótese de inadmissibilidade recursal — 
intempestividade, deserção, ilegitimidade, ausência de interesse 
recursal, irregularidade de representação e demais vícios de 
admissibilidade. O desenvolvimento é livre, adaptado à causa da 
inadmissibilidade.

{ementa}

{{shared: gabinete/formulas_voto#relatorio_dispensado}}

[SE houver pedido de justiça gratuita]
De plano, da análise dos autos, verifica-se a presença de elementos 
probatórios aptos a comprovar a situação de vulnerabilidade econômica, 
razão pela qual concedo à parte recorrente a gratuidade da justiça.
[/SE]

{desenvolvimento da inadmissibilidade — fundamentação sobre a causa 
específica que obsta o conhecimento do recurso}

Ante o exposto, voto pelo NÃO CONHECIMENTO do recurso interposto, 
em razão de {causa da inadmissibilidade}, nos termos da fundamentação 
supra.

Condeno a parte recorrente ao pagamento de 
honorários advocatícios, os quais fixo em 20% sobre o valor 
atualizado da causa, nos termos do art. 55 da Lei nº 9.099/95 e do 
Enunciado nº 122 do Fonaje.

[SE houver pedido de justiça gratuita]
, cuja exigibilidade fica suspensa em razão da gratuidade da justiça.
</template>


<template id="ED-REJEICAO">
## TEMPLATE ED — REJEIÇÃO

{ementa}

{{shared: gabinete/formulas_voto#relatorio_dispensado}}

Recebo os embargos de declaração, vez que tempestivos e presentes 
os pressupostos de admissibilidade.

Destaco que tal medida constitui instrumento processual destinado 
a sanar vícios de omissão, contradição, obscuridade ou erro 
material, conforme dispõem os arts. 48 da Lei nº 9.099/95 e 1.022, 
incisos I a III, do CPC.

Diante da alegação de {citar vícios}, os embargos opostos não 
comportam acolhimento.

Depreende-se dos autos que o julgado enfrentou expressamente todas 
as questões necessárias à solução da controvérsia, inclusive 
{ponto específico enfrentado}.

Desse modo, tem-se que estes aclaratórios constituem mero 
inconformismo com o resultado do julgamento, o que não constitui 
fundamento apto a justificar o cabimento dos embargos (STJ, EDcl 
no AgRg no AREsp 2622962/RJ, Rel. Min. Daniela Teixeira, DJe 
02/12/2024).

Considerando, portanto, que os embargos não podem ser utilizados 
como sucedâneo recursal (TJPR - 2ª Turma Recursal - 0052197-71.2025.
8.16.0021 - Cascavel - Rel.: ALVARO RODRIGUES JUNIOR - J. 02.12.2025; 
0010492-60.2025.8.16.0129 - Paranaguá - Rel.: IRINEU STEIN JUNIOR - 
J. 25.11.2025), o não acolhimento é a medida que se impõe.

Ante o exposto, voto pelo CONHECIMENTO e REJEIÇÃO dos presentes 
embargos de declaração, mantendo na íntegra o acórdão proferido.
</template>


<template id="ED-ACOLHIMENTO">
## TEMPLATE ED — ACOLHIMENTO (INTEGRAL OU PARCIAL)

{ementa}

{{shared: gabinete/formulas_voto#relatorio_dispensado}}

Recebo os embargos de declaração, vez que tempestivos e presentes 
os pressupostos de admissibilidade.

Destaco que tal medida constitui instrumento processual destinado 
a sanar vícios de omissão, contradição, obscuridade ou erro 
material, conforme dispõem os arts. 48 da Lei nº 9.099/95 e 1.022, 
incisos I a III, do CPC.

Diante da alegação de {citar vícios}, os embargos opostos comportam 
acolhimento.

{análise dos vícios identificados}

[SE acolhimento integral]
Ante o exposto, voto pelo CONHECIMENTO e ACOLHIMENTO dos presentes 
embargos de declaração, para o fim de {consequência}, nos termos 
da fundamentação supra.
[/SE]

[SE parcial acolhimento]
Ante o exposto, voto pelo CONHECIMENTO e PARCIAL ACOLHIMENTO dos 
presentes embargos de declaração, para o fim de {consequência}, 
nos termos da fundamentação supra.
[/SE]
</template>
