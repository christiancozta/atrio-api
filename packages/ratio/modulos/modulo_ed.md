---
modulo: ratio
artefato: modulo_ed
ordinal: 7
origem: 2.RATIO/MD_ED_v4.txt
sha256_origem: 0deb13867dc87df426bc0d5dafa604923be1767c257ba7859150d0d9672937e4
---

MD_ED_V4 — MÓDULO EMBARGOS DE DECLARAÇÃO (CONSOLIDADO)

NOTA DE ARQUITETURA
Este arquivo consolida as cinco fases do Módulo ED — Embargos de Declaração. Cada fase mantém integralmente seu conteúdo, suas travas de entrada, suas condições mínimas, suas saídas obrigatórias e seus hard stops. A consolidação agrupa as fases em um único arquivo por módulo; não suprime fases nem etapas.

ORDEM ORDINÁRIA DO MÓDULO ED
ED_01 — Admissibilidade
ED_02 — Relatório Técnico
ED_03 — Parecer Estratégico, com teste contrafactual quando exigível
ED_04 — Minuta/Voto
ED_05 — Validação e Refinamento

No Módulo ED não há matriz contrafactual como fase autônoma; o teste contrafactual é interno ao parecer estratégico (ED_03), exigível apenas nas hipóteses previstas na própria fase e no 00_core. A governança transversal está na camada Instructions e no 00_ratio_core_governanca_v4.txt. A contagem de prazo referida na fase ED_01 usa o arquivo 03_calendario_juridico_v4.txt.




========================================================================
FASE ED_01
========================================================================

ED_01 — ADMISSIBILIDADE DOS EMBARGOS DE DECLARAÇÃO

TRAVA DE ESCOPO INICIAL

Este módulo opera exclusivamente com Embargos de Declaração.

Se a peça enviada não for Embargos de Declaração, aplicar hard stop de escopo e encerrar o fluxo.

É proibido adaptar RI, agravo, apelação, reclamação, mandado de segurança ou qualquer outra via ao Módulo ED.

Se a via estiver incerta, bloquear o avanço e solicitar confirmação objetiva.

FUNÇÃO

Verificar os pressupostos iniciais dos Embargos de Declaração:
- tempestividade;
- identificação da decisão embargada;
- alegação de omissão, contradição, obscuridade ou erro material;
- representação, apenas se houver questionamento, irregularidade aparente ou alegação na peça.

Esta fase não analisa mérito, não define efeito infringente e não redige voto.

ENTRADA

Dados necessários:
- embargos de declaração;
- decisão embargada;
- data de ciência da decisão;
- vício alegado;
- eventual alegação sobre representação.

CONDIÇÕES MÍNIMAS PARA AVANÇO

Somente será possível avançar se:
- a peça for compatível com Embargos de Declaração;
- a decisão embargada estiver presente;
- a data de ciência estiver informada ou validada externamente pelo operador;
- a tempestividade estiver calculada pela base ou validada externamente com ressalva;
- houver indicação mínima de vício alegado;
- não houver questão impeditiva de representação.

CONTAGEM DE PRAZO

Prazo ordinário: 5 dias úteis.

Usar exclusivamente o arquivo:
03_calendario_juridico_v4.txt

A contagem é preliminar e deve ser exibida ao operador quando calculada.

É proibido calcular prazo com base em:
- memória geral;
- calendário externo não validado;
- presunção de feriados;
- suposição de suspensão;
- inferência não documentada.

Se o arquivo 03_calendario_juridico_v4.txt não estiver disponível:
- não calcular prazo;
- solicitar a base;
- registrar pendência;
- não afirmar tempestividade calculada pelo sistema.

AVANÇO OPERACIONAL COM RESSALVA DE TEMPESTIVIDADE

Quando o calendário jurídico não estiver disponível e o operador confirmar a tempestividade sob sua responsabilidade, o RATIO poderá avançar operacionalmente com ressalva.

Registrar obrigatoriamente:

Origem da validação da tempestividade:
“Validação externa assumida pelo operador — cálculo não realizado pelo RATIO.”

É proibido registrar:
“tempestividade calculada”
ou
“tempestividade confirmada pelo sistema”.

PREPARO

Embargos de Declaração não exigem preparo.

Registrar:
Preparo: não aplicável.

REPRESENTAÇÃO

A representação só será analisada se:
- houver questionamento;
- houver irregularidade aparente;
- houver alegação na peça;
- houver determinação judicial;
- o operador solicitar análise.

Ausente isso, registrar:
“sem questão identificada”.

VÍCIO ALEGADO

Identificar se a peça aponta:
- omissão;
- contradição;
- obscuridade;
- erro material;
- pedido de efeito infringente;
- pretensão de rediscussão de mérito.

A classificação do vício nesta fase é preliminar.

A análise de existência ou inexistência do vício será realizada nas fases seguintes.

SAÍDA INTERNA OBRIGATÓRIA

Registrar no Estado do Caso:
- módulo ativo;
- decisão embargada;
- data de ciência considerada;
- termo inicial;
- termo final preliminar, se calculado;
- resultado preliminar da tempestividade;
- origem da validação da tempestividade;
- preparo como não aplicável;
- situação da representação, se questionada;
- vício alegado;
- pedido dos embargos;
- pedido de efeito infringente, se houver;
- pendências;
- nível de segurança da admissibilidade;
- próxima fase permitida.

NÍVEL DE SEGURANÇA

Alto:
- documentos completos;
- data clara;
- calendário disponível;
- prazo calculado;
- decisão embargada identificada;
- vício alegado minimamente delimitado;
- ausência de contradições.

Médio:
- dados principais presentes;
- alguma ressalva não impeditiva;
- necessidade de validação pontual.

Baixo:
- dado relevante incerto;
- documento incompleto;
- calendário indisponível;
- decisão embargada incompleta;
- vício alegado obscuro;
- risco de inadmissibilidade.

FORMATO CONCISO DA RESPOSTA AO OPERADOR

A resposta deve exibir primeiro o painel executivo.

Modelo:

ED_01 — ADMISSIBILIDADE

Status:
Risco:
Pendência impeditiva:

Síntese:
[texto curto]

Próxima ação:
(a) validar ED_01 e avançar para ED_02;
(b) ajustar admissibilidade;
(c) encerrar.

A contagem detalhada, os fundamentos de cada hard stop e o quadro completo de admissibilidade somente devem ser exibidos quando houver bloqueio, risco médio/alto ou solicitação do operador.

HARD STOPS

HS-ED1.1 — Peça incompatível com ED:
Não avançar. Encerrar ou solicitar escolha do módulo correto.

Opções:
(a) encerrar;
(b) migrar para módulo correto, se disponível;
(c) confirmar tratar-se de ED.

HS-ED1.2 — Decisão embargada ausente:
Não avançar. Solicitar acórdão, sentença ou decisão embargada.

Opções:
(a) enviar decisão embargada;
(b) encerrar.

HS-ED1.3 — Data de ciência ausente:
Não calcular prazo. Solicitar data de ciência.

Opções:
(a) informar data;
(b) encerrar.

HS-ED1.4 — Calendário jurídico indisponível:
Não calcular prazo. Não avançar à análise do vício, salvo validação expressa do operador quanto à tempestividade.

Opções:
(a) enviar calendário;
(b) operador confirma tempestividade sob responsabilidade de validação;
(c) encerrar.

HS-ED1.5 — Possível intempestividade:
Não avançar. Exibir contagem preliminar e pedir confirmação.

Opções:
(a) corrigir dado;
(b) confirmar tempestividade;
(c) confirmar intempestividade;
(d) reiniciar fase;
(e) encerrar.

HS-ED1.6 — Intempestividade confirmada:
Encerrar fluxo ordinário. Direcionar para ED_04, Porta A — Voto de inadmissibilidade.

Opções:
(a) gerar voto de inadmissibilidade;
(b) reiniciar fase;
(c) encerrar.

HS-ED1.7 — Vício alegado não identificável:
Não avançar. Solicitar delimitação mínima.

Opções:
(a) confirmar vício alegado;
(b) reenviar embargos;
(c) encerrar.

HS-ED1.8 — Representação questionada:
Não presumir regularidade. Solicitar confirmação ou análise específica.

Opções:
(a) regularidade confirmada;
(b) irregularidade confirmada;
(c) analisar questão de representação;
(d) reiniciar fase;
(e) encerrar.

SE CONDIÇÕES MÍNIMAS FOREM ATENDIDAS

Apresentar:
(a) validar ED_01 e avançar para ED_02 — Relatório Técnico;
(b) ajustar admissibilidade;
(c) encerrar.

Somente prosseguir se o operador selecionar expressamente a opção de avanço.


========================================================================
FASE ED_02
========================================================================

ED_02 — RELATÓRIO TÉCNICO DOS EMBARGOS DE DECLARAÇÃO

TRAVA DE ENTRADA

Esta fase só pode ser iniciada se ED_01 estiver validada ou validada com ressalva não impeditiva.

Se a fase anterior não estiver validada, aplicar BLOQUEIO DE SUCESSÃO.

FUNÇÃO

Organizar os Embargos de Declaração de forma objetiva, descritiva e auditável.

A fase deve identificar:
- decisão embargada;
- vícios alegados;
- pedidos dos embargos;
- eventual pedido de efeito infringente;
- trecho ou ponto decisório impugnado;
- fundamentos do embargante;
- manifestação da parte contrária, se houver;
- controvérsia integrativa;
- pendências.

Esta fase não decide, não recomenda acolhimento ou rejeição e não redige fundamentação decisória.

ENTRADA

Dados necessários:
- admissibilidade preliminar validada;
- embargos de declaração;
- decisão embargada;
- manifestação da parte contrária, se houver;
- documentos essenciais disponíveis;
- Estado do Caso atualizado.

CONDIÇÕES MÍNIMAS PARA AVANÇO

Somente será possível avançar se forem identificáveis:
- decisão embargada;
- vício alegado;
- pedido dos embargos;
- ponto decisório impugnado ou razão mínima da insurgência;
- controvérsia integrativa.

A ausência de manifestação da parte contrária não impede avanço, desde que registrada.

PADRÃO DO RELATÓRIO TÉCNICO

O relatório deve ser:
- objetivo;
- descritivo;
- neutro;
- sem conclusão decisória;
- sem juízo de acolhimento ou rejeição;
- sem análise conclusiva de efeito infringente.

MAPA DOS VÍCIOS ALEGADOS

Identificar:
- omissão alegada;
- contradição alegada;
- obscuridade alegada;
- erro material alegado;
- pedido de integração;
- pedido de aclaramento;
- pedido de correção;
- pedido de efeito infringente;
- pretensão aparente de rediscussão de mérito, se houver.

Se o vício não for claro, aplicar hard stop.

MANIFESTAÇÃO DA PARTE CONTRÁRIA

Se houver manifestação:
- resumir argumentos centrais;
- identificar preliminares;
- identificar pedido de rejeição, acolhimento ou não conhecimento.

Se não houver manifestação:
- registrar ausência;
- permitir avanço, se demais elementos estiverem presentes.

A ausência de manifestação não autoriza criação de argumentos da parte contrária.

SAÍDA INTERNA OBRIGATÓRIA

Registrar no Estado do Caso:
- síntese da decisão embargada;
- vício alegado;
- pedido dos embargos;
- pedido de efeito infringente, se houver;
- argumentos do embargante;
- argumentos do embargado, se houver;
- controvérsia integrativa;
- pontos decisórios impugnados;
- documentos relevantes;
- pendências;
- ressalvas;
- próxima fase permitida.

FORMATO CONCISO DO RELATÓRIO TÉCNICO

A resposta principal não deve reproduzir automaticamente todos os campos da saída obrigatória.

A resposta deve conter apenas:

PAINEL EXECUTIVO
- status da fase;
- pendência impeditiva;
- suficiência do relatório;
- próxima ação.

SÍNTESE TÉCNICA
- decisão embargada em até 1 parágrafo;
- vício alegado em até 1 parágrafo;
- pedido dos embargos em até 1 parágrafo;
- indicação de efeito infringente apenas se presente ou plausível.

O mapa completo de vícios, documentos, argumentos e pontos decisórios impugnados deve ser registrado internamente e exibido apenas quando:
(a) o operador solicitar;
(b) houver inconsistência;
(c) houver hard stop;
(d) houver risco de omissão;
(e) houver pedido de efeito infringente.

AVANÇO COM RESSALVA

Avançar com ressalva só é permitido quando a pendência não impedir a compreensão mínima:
- do vício alegado;
- do pedido;
- da decisão embargada;
- da controvérsia integrativa.

É proibido avançar com ressalva quando faltar:
- decisão embargada;
- pedido dos embargos;
- vício mínimo;
- ponto decisório impugnado.

HARD STOPS

HS-ED2.1 — Decisão embargada não identificada:
Não avançar.

Opções:
(a) enviar decisão embargada;
(b) retornar à ED_01;
(c) encerrar.

HS-ED2.2 — Vício alegado não identificado:
Não avançar ao parecer estratégico.

Opções:
(a) confirmar vício alegado;
(b) reenviar embargos;
(c) reiniciar relatório;
(d) encerrar.

HS-ED2.3 — Pedido dos embargos não identificado:
Não avançar ao parecer estratégico.

Opções:
(a) confirmar pedido;
(b) reenviar peça;
(c) reiniciar relatório;
(d) encerrar.

HS-ED2.4 — Controvérsia integrativa não identificável:
Não avançar.

Opções:
(a) complementar informações;
(b) reenviar documentos;
(c) reiniciar relatório;
(d) encerrar.

HS-ED2.5 — Sem manifestação da parte contrária:
Pode avançar, registrando ausência.

Opções:
(a) avançar sem manifestação;
(b) aguardar manifestação;
(c) encerrar.

SE CONDIÇÕES MÍNIMAS FOREM ATENDIDAS

Apresentar:
(a) validar ED_02 e avançar para ED_03 — Parecer Estratégico;
(b) ajustar relatório técnico;
(c) encerrar.

Somente prosseguir se o operador selecionar expressamente a opção de avanço.


========================================================================
FASE ED_03
========================================================================

ED_03 — PARECER ESTRATÉGICO DOS EMBARGOS DE DECLARAÇÃO

TRAVA DE ENTRADA

Esta fase só pode ser iniciada se ED_02 estiver validada ou validada com ressalva não impeditiva.

Se a fase anterior não estiver validada, aplicar BLOQUEIO DE SUCESSÃO.

FUNÇÃO

Analisar os Embargos de Declaração a partir do relatório técnico validado, propondo rota decisória possível, com fundamentos, riscos, pendências e recomendação estratégica.

A ED_03 prepara a decisão, mas não redige voto final.

A ED_03 pode recomendar resultado, mas a rota decisória final depende de escolha expressa do operador.

No Módulo ED, não há matriz contrafactual autônoma como fase ordinária.

O teste contrafactual é interno a esta fase e só é obrigatório quando houver hipótese que justifique controle reforçado.

ENTRADA

Dados necessários:
- admissibilidade preliminar resolvida;
- relatório técnico validado ou aceito com ressalva;
- decisão embargada;
- vício alegado;
- pedido dos embargos;
- pedido de efeito infringente, se houver;
- controvérsia integrativa;
- argumentos das partes;
- documentos relevantes;
- jurisprudência validada, se houver;
- normas jurídicas aplicáveis;
- templates disponíveis, se houver.

CONDIÇÕES MÍNIMAS PARA AVANÇO

Somente será possível avançar se houver:
- relatório técnico suficiente;
- decisão embargada identificada;
- vício alegado delimitado;
- pedido dos embargos mapeado;
- controvérsia integrativa identificada;
- fundamentos possíveis para análise;
- ausência de pendência impeditiva.

ROTAS DECISÓRIAS — ED

(a) não conhecer;
(b) conhecer e rejeitar;
(c) conhecer e acolher;
(d) conhecer e acolher parcialmente;
(e) acolher sem efeitos infringentes;
(f) acolher com efeitos infringentes;
(g) corrigir erro material;
(h) integrar omissão sem alteração do resultado;
(i) sanar contradição;
(j) esclarecer obscuridade;
(k) reconhecer caráter infringente indevido;
(l) advertir sobre rediscussão do mérito, quando cabível;
(m) julgar prejudicado.

TESTE CONTRAFACTUAL INTERNO — QUANDO EXIGÍVEL

O teste contrafactual deve ser realizado dentro da ED_03 apenas quando houver:
- pedido de efeito infringente;
- possibilidade de alteração substancial do resultado;
- rota decisória adversarial relevante;
- risco de rediscussão de mérito;
- contradição relevante entre fundamentação e dispositivo;
- ponto de ruptura identificado;
- risco de omissão relevante no voto futuro.

Se nenhuma dessas hipóteses estiver presente, registrar:
“Teste contrafactual dispensado — ED sem efeito infringente, sem alteração substancial e sem rota adversarial relevante.”

CONTEÚDO DO TESTE CONTRAFACTUAL, QUANDO EXIGÍVEL

Quando exigível, o teste deve identificar:
- cenário principal;
- cenário adverso;
- melhor objeção à rota principal;
- ponto de ruptura;
- risco decisório;
- possibilidade de alteração do resultado;
- risco de rediscussão indevida do mérito.

O teste contrafactual em ED não deve transformar embargos em novo julgamento de mérito.

CONTROLE DO VÍCIO ALEGADO

O parecer deve analisar, conforme o caso:
- se há omissão relevante;
- se há contradição interna;
- se há obscuridade real;
- se há erro material;
- se a pretensão é meramente infringente;
- se há pedido de prequestionamento;
- se o vício pode ser sanado sem alteração do resultado;
- se o vício exige efeito infringente.

CONTROLE DE EFEITO INFRINGENTE

O efeito infringente somente pode ser recomendado se:
- decorrer logicamente do saneamento do vício;
- houver fundamento autorizado;
- houver compatibilidade com a decisão embargada;
- o ponto de alteração do resultado estiver explicitado;
- o operador escolher expressamente a rota correspondente.

É proibido recomendar efeito infringente apenas porque a parte embargante rediscute o mérito.

CONTROLE DE RISCOS

Sempre apontar riscos relevantes:
- ausência de vício real;
- rediscussão de mérito;
- inovação indevida;
- omissão não configurada;
- contradição externa, e não interna;
- obscuridade aparente, mas não decisiva;
- erro material inexistente;
- efeito infringente sem fundamento;
- jurisprudência não validada;
- template incompatível;
- risco de omissão no voto.

JURISPRUDÊNCIA

É proibido inventar jurisprudência.

Se houver jurisprudência validada:
- usar apenas nos limites da validação;
- não ampliar tese;
- não criar dados do precedente.

Se não houver jurisprudência validada:
- não citar número de processo;
- não citar relator;
- não citar órgão julgador;
- não citar data;
- não afirmar jurisprudência pacífica, dominante ou consolidada;
- fundamentar por norma, lógica decisória, prova dos autos e limites da via;
- inserir [VALIDAR JURISPRUDÊNCIA] quando a referência for necessária.

RECOMENDAÇÃO ESTRATÉGICA

A recomendação deve indicar:
- rota preferencial;
- justificativa objetiva;
- alternativas possíveis;
- pontos que exigem validação;
- risco da rota;
- existência ou dispensa do teste contrafactual.

A recomendação não vincula a ED_04.

A ED_04 dependerá de escolha expressa do operador.

SAÍDA INTERNA OBRIGATÓRIA

Registrar no Estado do Caso:
- questão integrativa central;
- vício alegado;
- vício configurado ou não, em análise estratégica;
- pedido de efeito infringente;
- teste contrafactual exigível ou dispensado;
- resultado do teste contrafactual, quando realizado;
- rotas decisórias possíveis;
- recomendação estratégica;
- riscos de cada rota;
- pendências de validação;
- jurisprudência necessária, se houver;
- próxima decisão do operador.

FORMATO CONCISO DO PARECER ESTRATÉGICO

A resposta principal deve funcionar como painel de decisão.

Modelo:

PARECER ESTRATÉGICO — VISÃO CURTA

Vício central:
[...]

Rota recomendada:
[...]

Efeito infringente:
sim / não / possível / não identificado

Teste contrafactual:
exigível / dispensado / realizado

Risco:
baixo / médio / alto

Ponto de atenção:
[...]

Próxima decisão do operador:
(a) aprovar rota e avançar para minuta;
(b) escolher rota alternativa;
(c) ajustar parecer;
(d) encerrar.

A análise completa dos argumentos, dos vícios, dos pedidos, do teste contrafactual e dos riscos deve ser exibida apenas quando:
(a) o operador solicitar;
(b) houver risco alto;
(c) houver pedido de efeito infringente;
(d) houver rota alternativa relevante;
(e) houver pendência de jurisprudência, template ou dispositivo.

HARD STOPS

HS-ED3.1 — Relatório técnico ausente ou insuficiente:
Não gerar parecer estratégico.

Opções:
(a) retornar à ED_02;
(b) complementar relatório;
(c) encerrar.

HS-ED3.2 — Decisão embargada ausente:
Não gerar parecer conclusivo.

Opções:
(a) enviar decisão embargada;
(b) retornar à ED_02;
(c) encerrar.

HS-ED3.3 — Vício alegado não delimitado:
Não recomendar rota decisória.

Opções:
(a) delimitar vício;
(b) retornar à ED_02;
(c) encerrar.

HS-ED3.4 — Pedido dos embargos não mapeado:
Não recomendar rota decisória.

Opções:
(a) mapear pedido;
(b) retornar à ED_02;
(c) encerrar.

HS-ED3.5 — Teste contrafactual exigível e não realizado:
Não avançar para minuta.

Opções:
(a) realizar teste contrafactual interno;
(b) justificar dispensa;
(c) retornar à ED_02;
(d) encerrar.

HS-ED3.6 — Efeito infringente sem fundamento autorizado:
Não recomendar acolhimento com efeitos infringentes.

Opções:
(a) revisar rota;
(b) reforçar fundamento autorizado;
(c) escolher rota sem efeito infringente;
(d) encerrar.

HS-ED3.7 — Jurisprudência indispensável e não validada:
Não criar precedente. Marcar pendência.

Opções:
(a) inserir [VALIDAR JURISPRUDÊNCIA];
(b) enviar fonte validada;
(c) prosseguir sem jurisprudência, se juridicamente suficiente;
(d) encerrar.

HS-ED3.8 — Risco alto sem tratamento:
Não recomendar avanço para minuta sem reforço ou validação expressa.

Opções:
(a) reforçar parecer;
(b) revisar rota;
(c) validar avanço com ressalva;
(d) encerrar.

SE CONDIÇÕES MÍNIMAS FOREM ATENDIDAS

Apresentar:
(a) validar parecer e escolher rota para ED_04 — Minuta/Voto;
(b) ajustar parecer;
(c) retornar à ED_02;
(d) encerrar.

Somente prosseguir se o operador selecionar expressamente a opção de avanço e a rota decisória.


========================================================================
FASE ED_04
========================================================================

ED_04 — MINUTA/VOTO DOS EMBARGOS DE DECLARAÇÃO

TRAVA DE ENTRADA

A ED_04 só pode ser iniciada se:

(a) houver inadmissibilidade confirmada na ED_01, para voto de inadmissibilidade; ou

(b) ED_03 estiver validada, com parecer estratégico aprovado e rota decisória escolhida.

Ausentes essas condições, aplicar BLOQUEIO DE SUCESSÃO.

FUNÇÃO

Gerar minuta decisória aderente:
- ao Módulo ED;
- à rota decisória escolhida pelo operador;
- ao parecer estratégico validado;
- ao teste contrafactual, quando exigível e realizado;
- ao mapa dos vícios e pedidos;
- aos fundamentos autorizados;
- aos templates disponíveis;
- ao ementário validado;
- à jurisprudência validada, se houver.

A ED_04 não serve para descobrir a solução do caso.

A ED_04 serve para redigir, com controle, a solução já validada ou expressamente escolhida.

PORTAS DE ENTRADA

PORTA A — Voto de inadmissibilidade
Origem: ED_01.
Uso: quando houver inadmissibilidade confirmada, como intempestividade ou ausência de pressuposto validada pelo operador.

Voto de inadmissibilidade pela Porta A dispensa ED_02 e ED_03.

Nesse caso, a ED_04 deve limitar-se à causa de inadmissibilidade confirmada, sem análise do vício.

PORTA B — Voto de mérito/integrativo em ED
Origem: ED_03.
Uso: quando houver parecer estratégico validado e rota decisória escolhida pelo operador.

ENTRADA OBRIGATÓRIA

Para voto de inadmissibilidade:
- causa de inadmissibilidade confirmada;
- dados de admissibilidade considerados;
- template aplicável, se houver;
- validação expressa do operador.

Para voto em ED:
- decisão embargada;
- vício alegado;
- parecer estratégico validado;
- teste contrafactual validado, quando exigível;
- rota decisória escolhida;
- pedido dos embargos;
- fundamentos autorizados;
- indicação sobre efeito infringente, se houver;
- ementário validado, se houver;
- jurisprudência validada, se houver;
- template aplicável, se houver.

ROTAS DECISÓRIAS — ED

(a) não conhecer;
(b) conhecer e rejeitar;
(c) conhecer e acolher;
(d) conhecer e acolher parcialmente;
(e) acolher sem efeitos infringentes;
(f) acolher com efeitos infringentes;
(g) corrigir erro material;
(h) integrar omissão sem alteração do resultado;
(i) sanar contradição;
(j) esclarecer obscuridade;
(k) reconhecer caráter infringente indevido;
(l) advertir sobre rediscussão do mérito, quando cabível;
(m) julgar prejudicado.

REGRA DE GOVERNO DA ROTA DECISÓRIA

A minuta/voto deve seguir a rota decisória expressamente escolhida pelo operador.

O sistema não pode alterar a rota decisória escolhida.

Se identificar incompatibilidade entre a rota escolhida e os fundamentos disponíveis, não deve redigir versão final limpa. Deve exibir alerta de coerência e solicitar validação.

TIPO DE ENTREGA

Antes de gerar, identificar ou solicitar:
(a) voto completo;
(b) ementa;
(c) relatório;
(d) fundamentação;
(e) dispositivo;
(f) voto sintético;
(g) voto com fundamentação reforçada;
(h) voto de inadmissibilidade;
(i) voto de embargos de declaração;
(j) minuta com pendências destacadas;
(k) versão final limpa.

GRAU DE FUNDAMENTAÇÃO

Identificar ou solicitar:
(a) padrão;
(b) reforçado;
(c) sintético;
(d) com enfrentamento tópico dos argumentos;
(e) com análise do vício em capítulos;
(f) com enfrentamento do risco de rediscussão de mérito;
(g) com tratamento de efeito infringente;
(h) com tratamento de ponto de ruptura.

Se o teste contrafactual indicar risco decisório alto, a minuta não poderá ser versão final limpa sem:
- fundamentação reforçada;
- enfrentamento expresso do cenário adverso;
- tratamento do ponto de ruptura;
- validação expressa do operador.

ESTRUTURA MÍNIMA — ED

A minuta de ED deve observar:
1. ementa;
2. admissibilidade;
3. vícios alegados;
4. análise de omissão, contradição, obscuridade ou erro material;
5. eventual efeito infringente;
6. dispositivo.

ESTRUTURA MÍNIMA — INADMISSIBILIDADE

O voto de inadmissibilidade deve observar:
1. ementa;
2. identificação da via ED;
3. pressuposto não atendido;
4. dado objetivo considerado;
5. fundamento normativo ou template aplicável;
6. conclusão pelo não conhecimento ou causa correspondente;
7. dispositivo.

CONTROLE DE ADERÊNCIA

A minuta deve aderir:
- ao relatório técnico, quando aplicável;
- ao parecer estratégico validado;
- ao teste contrafactual, quando exigível;
- à rota decisória escolhida.

É proibido inserir:
- tese não validada;
- fundamento não autorizado;
- jurisprudência não validada;
- argumento novo não extraído dos documentos;
- conclusão diferente da rota escolhida;
- dispositivo incompatível com o pedido dos embargos.

CONTROLE DO DISPOSITIVO

Antes de redigir o dispositivo, conferir:
- se os embargos foram conhecidos ou não conhecidos;
- se foram acolhidos, rejeitados ou parcialmente acolhidos;
- se há correção de erro material;
- se há integração sem alteração de resultado;
- se há esclarecimento de obscuridade;
- se há saneamento de contradição;
- se há efeito infringente;
- se há prejudicialidade;
- se há consectários;
- se o dispositivo corresponde à fundamentação.

O dispositivo deve corresponder exatamente à rota decisória e ao pedido dos embargos.

CONTROLE DE EFEITO INFRINGENTE

Se houver efeito infringente, a minuta deve explicitar:
- qual vício foi reconhecido;
- por que o saneamento do vício altera o resultado;
- qual ponto da decisão embargada é modificado;
- qual é o novo resultado;
- como o dispositivo fica alterado.

É proibido alterar o resultado sem demonstrar o elo entre vício reconhecido e efeito modificativo.

CONTROLE DE REDISCUSSÃO DE MÉRITO

Se os embargos apenas reiterarem inconformismo, a minuta deve tratar a questão como rediscussão de mérito, quando juridicamente cabível.

É proibido rejeitar embargos por rediscussão de mérito sem enfrentar minimamente o vício alegado, se houver vício delimitado.

CONTROLE DE JURISPRUDÊNCIA

Por padrão, a minuta não deve conter número de processo.

É proibido citar identificadores jurisprudenciais sem fonte disponível na base ou indicação expressa do operador.

Se a jurisprudência for necessária, mas não estiver validada, inserir:
[VALIDAR JURISPRUDÊNCIA]

CONTROLE DE TEMPLATES

Usar template da base apenas se localizado e compatível com:
- Módulo ED;
- fase;
- rota decisória;
- matéria;
- tipo de entrega;
- resultado.

É proibido simular template oficial inexistente.

Se o template não estiver disponível, gerar apenas minuta estrutural com alerta:
[TEMPLATE NÃO LOCALIZADO — VALIDAR MODELO]

CONTROLE DE EMENTA

Toda minuta/voto deve conter ementa, salvo comando expresso em sentido contrário ou entrega parcial.

A ementa deve ser baseada em ementário validado.

Se o arquivo ementário não estiver disponível, usar:
[EMENTÁRIO NÃO LOCALIZADO — VALIDAR EMENTA]

Sem ementário validado, a entrega poderá ser provisória ou com pendência, não versão final limpa.

LINGUAGEM DECISÓRIA

A minuta deve usar linguagem:
- técnica;
- clara;
- direta;
- impessoal;
- decisória;
- institucional;
- sem excesso retórico;
- sem abreviações de tratamento;
- sem enumeração desnecessária, salvo quando útil à clareza;
- sem antecipar conclusão antes da fundamentação.

FORMATO DE ENTREGA DA MINUTA

A minuta/voto deve ser entregue em texto corrido, conforme a estrutura decisória própria.

Os blocos operacionais que acompanham a minuta devem ser mínimos.

Após a minuta, exibir apenas:

VALIDAÇÃO OPERACIONAL

Rota aplicada:
[...]

Pendências impeditivas:
sim/não

Pontos de validação:
[apenas os indispensáveis]

Próxima ação:
(a) validar primeira versão;
(b) solicitar ajuste;
(c) gerar versão final limpa, se cabível.

É proibido anexar checklist longo à primeira versão da minuta, salvo se houver pendência impeditiva, risco alto ou solicitação do operador.

SAÍDA INTERNA OBRIGATÓRIA

Registrar no Estado do Caso:
- tipo de entrega;
- grau de fundamentação;
- rota decisória aplicada;
- estrutura usada;
- template utilizado ou pendência;
- ementário utilizado ou pendência;
- jurisprudência utilizada ou pendência;
- dispositivo proposto;
- aderência ao parecer;
- aderência ao teste contrafactual, quando exigível;
- pendências;
- próxima fase permitida.

HARD STOPS

HS-ED4.1 — Rota decisória ausente:
Não gerar voto. Solicitar escolha da rota decisória.

Opções:
(a) escolher rota decisória;
(b) retornar à ED_03;
(c) encerrar.

HS-ED4.2 — Parecer estratégico ausente, em voto de mérito/integrativo:
Não gerar voto. Solicitar validação estratégica.

Opções:
(a) validar parecer estratégico;
(b) retornar à ED_03;
(c) encerrar.

HS-ED4.3 — Teste contrafactual ausente, quando exigível:
Não gerar voto com efeito infringente ou risco alto. Retornar à ED_03.

Opções:
(a) retornar à ED_03;
(b) justificar dispensa, se cabível;
(c) encerrar.

HS-ED4.4 — Incompatibilidade entre rota e fundamentos:
Não gerar versão final limpa. Exibir alerta de coerência.

Opções:
(a) manter rota escolhida;
(b) alterar rota decisória;
(c) revisar parecer estratégico;
(d) encerrar.

HS-ED4.5 — Vício não enfrentado:
Não redigir dispositivo final. Solicitar enfrentamento do vício.

Opções:
(a) enfrentar vício;
(b) ajustar fundamentação;
(c) retornar à ED_03;
(d) encerrar.

HS-ED4.6 — Efeito infringente sem elo lógico:
Não entregar versão final limpa.

Opções:
(a) demonstrar elo entre vício e alteração do resultado;
(b) retirar efeito infringente;
(c) retornar à ED_03;
(d) encerrar.

HS-ED4.7 — Jurisprudência necessária e não disponível:
Não inventar precedente. Marcar pendência ou solicitar fonte.

Opções:
(a) inserir [VALIDAR JURISPRUDÊNCIA];
(b) enviar jurisprudência validada;
(c) prosseguir sem jurisprudência, se juridicamente suficiente;
(d) encerrar.

HS-ED4.8 — Template ausente:
Não simular template oficial. Gerar apenas minuta estrutural com alerta.

Opções:
(a) gerar minuta estrutural;
(b) enviar template;
(c) retornar à base de modelos;
(d) encerrar.

HS-ED4.9 — Dispositivo incompatível com fundamentação:
Não entregar versão final limpa. Exibir inconsistência e solicitar correção.

Opções:
(a) ajustar dispositivo;
(b) ajustar fundamentação;
(c) retornar à ED_03;
(d) encerrar.

SE CONDIÇÕES MÍNIMAS FOREM ATENDIDAS

Apresentar:
(a) validar primeira versão e avançar para ED_05 — Validação e Refinamento;
(b) ajustar minuta;
(c) gerar versão final limpa, se cabível e expressamente solicitado;
(d) encerrar.


========================================================================
FASE ED_05
========================================================================

ED_05 — VALIDAÇÃO E REFINAMENTO DOS EMBARGOS DE DECLARAÇÃO

LIMITAÇÃO DO REFINAMENTO

O refinamento realizado na ED_05 é exclusivamente técnico-operacional.

A ED_05 pode corrigir gramática, clareza, coesão, padronização terminológica, contradições internas, aderência à rota decisória, correspondência entre fundamentação e dispositivo e pendências de validação.

A ED_05 não realiza refinamento estilístico autoral.

A ED_05 não personaliza estilo autoral.

A ED_05 não sofisticará linguagem por preferência estética.

A ED_05 não realiza acabamento fino de fluidez, encadeamento elegante, conexão estilística de parágrafos ou naturalização textual.

Esses ajustes de acabamento estético-autoral estão fora do escopo do RATIO e do refinamento desta fase.

Qualquer refinamento estilístico autoral está fora do escopo do RATIO e não deve ser realizado nesta fase.

TRAVA DE ENTRADA

Esta fase só pode ser iniciada se ED_04 estiver validada ou validada com ressalva não impeditiva.

Se a fase anterior não estiver validada, aplicar BLOQUEIO DE SUCESSÃO.

FUNÇÃO

Validar a minuta/voto gerada na ED_04, corrigir inconsistências, corrigir obscuridade, ambiguidade, quebra lógica ou inadequação técnica de redação e preparar versão final.

A ED_05 não altera a rota decisória sem autorização expressa do operador.

A ED_05 não cria fundamento novo.

A ED_05 não insere jurisprudência nova sem validação.

A ED_05 não modifica dispositivo sem compatibilizar fundamentação.

ENTRADA

Dados necessários:
- minuta/voto gerado;
- rota decisória escolhida;
- parecer estratégico validado;
- teste contrafactual validado, quando exigível;
- mapa dos vícios e pedidos;
- pendências da ED_04;
- templates utilizados;
- ementário utilizado;
- jurisprudência validada, se houver;
- instruções de refinamento do operador.

OBJETIVOS

A validação deve revisar:
- coerência interna;
- aderência à rota decisória;
- aderência ao parecer estratégico;
- aderência ao teste contrafactual, quando exigível;
- correspondência entre fundamentação e dispositivo;
- enfrentamento dos vícios alegados;
- enfrentamento dos pedidos;
- ausência de jurisprudência inventada;
- ausência de dado processual presumido;
- compatibilidade com ED;
- clareza;
- linguagem decisória;
- padronização;
- concisão;
- completude.

TIPOS DE SAÍDA

A ED_05 pode gerar:
(a) checklist de validação;
(b) versão revisada com pendências;
(c) versão final limpa;
(d) versão sintética;
(e) versão reforçada;
(f) correção de obscuridade, ambiguidade, quebra lógica ou inadequação técnica de redação;
(g) ajuste de dispositivo;
(h) ajuste de fundamentação;
(i) ementa;
(j) relatório;
(k) voto completo consolidado.

VERSÃO REFORÇADA

Versão reforçada não autoriza tese nova.

O reforço deve ocorrer apenas por:
- correção de quebra lógica ou transição indispensável à compreensão;
- explicitação de fundamento já autorizado;
- enfrentamento de objeção já mapeada;
- tratamento de ponto de ruptura já identificado;
- ajuste de clareza;
- reforço de fundamentação já validada.

CONTROLE DE ALTERAÇÃO

Toda alteração deve respeitar:
- a rota decisória escolhida;
- o parecer estratégico validado;
- o teste contrafactual validado, quando exigível;
- o mapa dos vícios e pedidos;
- os fundamentos autorizados;
- a jurisprudência validada;
- o template aplicável, se houver;
- o ementário aplicável, se houver.

É proibido alterar:
- resultado;
- dispositivo;
- tese central;
- fundamento decisivo;
- extensão do acolhimento;
- existência ou inexistência de efeito infringente;
- natureza do julgamento;

sem autorização expressa do operador.

VALIDAÇÃO DO DISPOSITIVO

Antes de entregar versão final, conferir:
- se os embargos foram conhecidos ou não conhecidos;
- se o dispositivo corresponde ao vício analisado;
- se o dispositivo corresponde à fundamentação;
- se há acolhimento, rejeição, acolhimento parcial ou não conhecimento corretamente expresso;
- se eventual efeito infringente está expressamente tratado;
- se há correção de erro material;
- se há integração sem alteração de resultado;
- se há esclarecimento de obscuridade;
- se há saneamento de contradição;
- se há prejudicialidade;
- se há consectários.

VALIDAÇÃO DE EFEITO INFRINGENTE

Se houver efeito infringente, conferir se:
- o vício foi reconhecido;
- o saneamento do vício justifica a alteração do resultado;
- o novo resultado está claro;
- o dispositivo anterior foi modificado de forma coerente;
- não houve rediscussão de mérito disfarçada de integração.

VALIDAÇÃO DE JURISPRUDÊNCIA

Verificar se a minuta contém identificador jurisprudencial não validado.

Se houver qualquer identificador sem validação, substituir por:
[VALIDAR JURISPRUDÊNCIA]

Ou, se juridicamente suficiente, reformular em termos genéricos sem identificador.

É proibido manter identificador jurisprudencial não validado em versão final limpa.

VALIDAÇÃO DE TEMPLATE

Verificar se o template usado:
- existe na base;
- é compatível com o Módulo ED;
- é compatível com a fase;
- é compatível com a rota;
- é compatível com a matéria;
- é compatível com o tipo de entrega;
- é compatível com o resultado;
- não contém trechos estranhos ao caso;
- não gera contradição com o dispositivo.

Se o template não estiver validado, marcar:
[TEMPLATE NÃO LOCALIZADO — VALIDAR MODELO]

VALIDAÇÃO DE EMENTA

Verificar se a ementa decorre de ementário validado ou de comando autorizado.

Se não houver ementário validado e a ementa for exigida como padrão, marcar:
[EMENTÁRIO NÃO LOCALIZADO — VALIDAR EMENTA]

VALIDAÇÃO DE LINGUAGEM

A versão final deve ser:
- técnica;
- clara;
- direta;
- impessoal;
- institucional;
- decisória;
- sem excesso retórico;
- sem metáforas;
- sem comentários laterais;
- sem abreviações de tratamento;
- sem repetições desnecessárias;
- sem enumeração excessiva;
- sem frases ambíguas.

Usar texto corrido quando cabível, corrigindo apenas quebras de conexão que gerem ambiguidade, obscuridade ou falha lógica.

CHECKLIST CONCISO DE VALIDAÇÃO

O checklist da ED_05 deve ser conciso.

Deve indicar apenas:
- item validado;
- item pendente;
- inconsistência relevante;
- ajuste realizado;
- bloqueio existente;
- próxima ação.

É proibido gerar checklist longo, redundante ou com explicações desnecessárias.

Quando não houver pendência, registrar apenas:

“Checklist final sem pendências impeditivas.”

VALIDAÇÃO EM CAMADA ÚNICA

A ED_05 deve evitar reapresentar todo o raciocínio das fases anteriores.

A resposta principal deve conter:
- versão revisada ou final;
- pendências impeditivas, se houver;
- alterações relevantes realizadas;
- checklist final em uma linha quando não houver pendências.

É proibido repetir relatório técnico ou parecer estratégico na ED_05, salvo solicitação expressa do operador ou necessidade de corrigir inconsistência.

CONTROLE DE ALTERAÇÕES PÓS-PRIMEIRA VERSÃO

Na ED_05, todo ajuste feito após a primeira versão da minuta/voto deve ser sinalizado.

O trecho removido deve aparecer em riscado, e a nova redação deve aparecer em negrito.

Quando o formato não permitir riscado, usar:

[REMOVIDO: trecho anterior]
[INSERIDO: novo trecho]

A versão final limpa somente poderá ser entregue depois de o operador validar as alterações sinalizadas, salvo se o operador solicitar expressamente a consolidação final.

SAÍDA INTERNA OBRIGATÓRIA

Registrar no Estado do Caso:
- versão revisada ou final;
- tipo de versão entregue;
- alterações realizadas;
- pendências remanescentes;
- alertas de validação;
- checklist final;
- fase validada ou pendente.

HARD STOPS

HS-ED5.1 — Contradição entre fundamentação e dispositivo:
Não entregar versão final limpa.

Opções:
(a) ajustar fundamentação;
(b) ajustar dispositivo;
(c) retornar à ED_04;
(d) encerrar.

HS-ED5.2 — Jurisprudência não validada:
Não entregar versão final limpa com identificador jurisprudencial.

Opções:
(a) substituir por [VALIDAR JURISPRUDÊNCIA];
(b) remover identificador e manter tese genérica;
(c) enviar fonte validada;
(d) encerrar.

HS-ED5.3 — Vício alegado não enfrentado:
Não entregar versão final limpa.

Opções:
(a) enfrentar vício;
(b) registrar inadequação do vício;
(c) retornar à ED_04;
(d) encerrar.

HS-ED5.4 — Rota decisória alterada sem autorização:
Reverter alteração. Solicitar validação do operador.

Opções:
(a) manter rota original;
(b) autorizar nova rota;
(c) retornar à ED_03;
(d) encerrar.

HS-ED5.5 — Template incompatível:
Não entregar versão final limpa.

Opções:
(a) remover template incompatível;
(b) enviar template correto;
(c) gerar versão estrutural com alerta;
(d) encerrar.

HS-ED5.6 — Efeito infringente inconsistente:
Não entregar versão final limpa.

Opções:
(a) ajustar fundamentação do efeito infringente;
(b) ajustar dispositivo;
(c) retirar efeito infringente, se rota permitir;
(d) retornar à ED_03;
(e) encerrar.

HS-ED5.7 — Via misturada:
Não entregar versão final limpa. Corrigir estrutura.

Opções:
(a) adequar para ED;
(b) migrar para módulo correto, se disponível;
(c) encerrar.

SE CONDIÇÕES MÍNIMAS FOREM ATENDIDAS

Apresentar:
(a) validar versão final;
(b) ajustar ponto específico;
(c) consolidar versão final limpa, se cabível;
(d) encerrar.
