---
modulo: ratio
artefato: ri_conjunto
estado: pendente
fora_da_base_ativa: true
removido_de: 05_templates_voto_v4.txt
correcao: secao 7, item 1
---

# Template RI-CONJUNTO — retirado da base ativa

Este template foi removido de `packages/ratio/bases/templates_voto.md` e
guardado aqui, fora da base ativa, para retomada futura. **Não é carregado
pelo RATIO e não entra em nenhuma distribuição.**

## Por que saiu

O template termina em `{a preencher}`. A regra de uso híbrida da própria base
manda usar todo template localizado e compatível com módulo, fase, tipo de
decisão, rota decisória, matéria e resultado. Como o RI-CONJUNTO era
localizável e formalmente compatível com julgamento conjunto, o resultado
prático era o sistema aplicar um modelo vazio justamente no caso mais
complexo, o de múltiplos recursos.

Sem ele na base, o julgamento conjunto cai em
`[TEMPLATE NAO LOCALIZADO — VALIDAR MODELO]`, que é o comportamento previsto
pela própria base para ausência de template, e não erro.

## Para reativar

Completar o desenvolvimento a partir de `{a preencher}` e devolver o bloco
para `templates_voto.md`, reinserindo `RI-CONJUNTO` na lista de ids do
ESTADO ATUAL DA BASE. A incorporação à base é o único ato necessário para
ativá-lo; nenhuma regra precisa mudar.

## Texto preservado, sem alteração

<template id="RI-CONJUNTO">
## TEMPLATE RI — MODO CONJUNTO

Aplicável a julgamento simultâneo de múltiplos recursos inominados 
decorrentes da mesma causa ou de causas conexas. Estrutura com 
abertura unificada, admissibilidade individualizada, controvérsia 
unificada, mérito por tema, dispositivo individualizado, sucumbência 
por recorrente.

{ementa}

Relatório dispensado, nos termos do Enunciado nº 92 do Fonaje.

[SE houver pedido de justiça gratuita]
De plano, da análise dos autos, verifica-se a presença de elementos 
probatórios aptos a comprovar a situação de vulnerabilidade econômica da recorrente […], 
razão pela qual concedo à parte a gratuidade da justiça.
[/SE]

Satisfeitos os pressupostos processuais de admissibilidade, tanto 
objetivos quanto subjetivos, os recursos merecem ser conhecidos.

{a preencher}
</template>
