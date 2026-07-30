# DECISÃO DE PRODUTO — CERNE API 0.2

**Vigência:** imediata.

Este documento registra a decisão funcional que governa a API e a interface do
CERNE a partir da versão `0.2.0`. Nos pontos em que houver conflito, ele supera
as regras anteriores sobre amplitude de entrada, profundidade progressiva,
interrupção após triagem e escolha de formato de saída.

## 1. Produto

O CERNE é um produto de auditoria de raciocínio decisório para o Judiciário.
Ele não oferece ao usuário modos abreviados, seleção de profundidade ou escolha
de eixos. A extensão do exame pertence ao protocolo de auditoria.

## 2. Portas de entrada

A API aceita apenas:

1. decisão liminar;
2. voto;
3. sentença;
4. acórdão.

Nesta fase, o conteúdo deve ser integralmente fictício ou proveniente de fonte
pública, sem segredo de justiça e sem dados pessoais desnecessários.

## 3. Execução obrigatória

Toda submissão válida inicia uma auditoria completa.

- a triagem organiza a execução, mas não encerra a auditoria;
- resultado preliminar limpo não dispensa os eixos;
- dúvida sobre a base decisória não transfere ao usuário a escolha do método;
- necessidade de validação de fonte é registrada e considerada pelo gate, sem
  transformar a auditoria em modo abreviado;
- os onze eixos `EX001` a `EX011` são executados isoladamente;
- resultados negativos são parte obrigatória do relatório;
- confrontos são executados quando seus critérios de ativação estiverem
  presentes; auditoria completa não significa fabricar confrontos;
- o gate consolida somente achados produzidos pelos eixos e confrontos.

## 4. Saídas

A API sempre produz duas faces da mesma auditoria:

1. **tradução de tela:** linguagem clara, sem nomes de escolas, códigos, lentes,
   confrontos, marcadores ou terminologia interna;
2. **relatório técnico:** documento completo e exportável, com método, escola
   de pensamento, resultado de cada eixo, confrontos, achados, gate e rastro.

O usuário não escolhe entre saída interna, saída cliente ou ambas.

## 5. Interface

A tela deve:

- pedir apenas os dados necessários para identificar o ato, sua origem e o
  texto;
- informar que a auditoria será completa;
- mostrar somente a tradução dos resultados;
- oferecer o relatório técnico completo como arquivo separado;
- não expor controles de profundidade, eixos, camadas ou formato de saída.

## 6. Persistência

O documento submetido e o conteúdo textual da auditoria não são persistidos
pela API. Somente metadados operacionais são gravados.

