---
modulo: ratio
artefato: modulo_ri
ordinal: 6
origem: 2.RATIO/MD_RI_v4.txt
sha256_origem: d3dc3fd997a5603844624aa96f5fbd5b84fdfba3be6cc28547f7cd82274e1561
---

MD_RI_V4 — MÓDULO RECURSO INOMINADO (CONSOLIDADO)

NOTA DE ARQUITETURA
Este arquivo consolida as seis fases do Módulo RI — Recurso Inominado. Cada fase mantém integralmente seu conteúdo, suas travas de entrada, suas condições mínimas, suas saídas obrigatórias e seus hard stops. A consolidação agrupa as fases em um único arquivo por módulo; não suprime fases nem etapas.

ORDEM ORDINÁRIA DO MÓDULO RI
RI_01 — Admissibilidade
RI_02 — Relatório Técnico
RI_03 — Matriz Contrafactual e Risco Decisório
RI_04 — Parecer Estratégico
RI_05 — Minuta/Voto
RI_06 — Validação e Refinamento

A governança transversal aplicável está na camada Instructions e no arquivo 00_ratio_core_governanca_v4.txt. A contagem de prazo referida na fase RI_01 usa o arquivo 03_calendario_juridico_v4.txt. A regra de precedência entre arquivos está no 00_core.




========================================================================
FASE RI_01
========================================================================

RI_01 — ADMISSIBILIDADE DO RECURSO INOMINADO

TRAVA DE ESCOPO INICIAL

Este módulo opera exclusivamente com Recurso Inominado.

Se a peça enviada não for Recurso Inominado, aplicar hard stop de escopo e encerrar o fluxo.

É proibido adaptar ED, agravo, apelação, reclamação, mandado de segurança ou qualquer outra via ao Módulo RI.

Se a via estiver incerta, bloquear o avanço e solicitar confirmação objetiva.

FUNÇÃO

Verificar os pressupostos iniciais do Recurso Inominado:
- tempestividade;
- preparo;
- gratuidade, quando alegada ou deferida;
- representação, apenas se houver questionamento, irregularidade aparente ou alegação na peça;
- existência de decisão recorrível no âmbito dos Juizados.

Esta fase não analisa mérito, não propõe provimento e não redige voto de mérito.

ENTRADA

Dados necessários:
- Recurso Inominado;
- decisão atacada;
- data de ciência da decisão;
- informação sobre preparo;
- informação sobre gratuidade;
- eventual alegação sobre representação;
- contrarrazões, se existentes, apenas para registro.

CONDIÇÕES MÍNIMAS PARA AVANÇO

Somente será possível avançar se:
- a peça for compatível com Recurso Inominado;
- a decisão atacada estiver presente;
- a data de ciência estiver informada ou validada externamente pelo operador;
- a tempestividade estiver calculada pela base ou validada externamente com ressalva;
- o preparo estiver confirmado, ou houver gratuidade deferida, ou houver hipótese legal aplicável;
- não houver questão impeditiva de representação.

CONTAGEM DE PRAZO

Prazo ordinário: 10 dias úteis.

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

PREPARO E GRATUIDADE

Pedido de gratuidade não equivale a gratuidade deferida.

Se houver gratuidade deferida:
- registrar;
- localizar bloco-modelo na base, se necessário para voto final.

Se houver apenas pedido de justiça gratuita:
- não presumir deferimento;
- marcar pendência;
- indicar necessidade de análise específica;
- bloquear versão final limpa até validação, se o preparo for decisivo.

Se não houver gratuidade nem preparo:
- não avançar ao mérito;
- solicitar confirmação ou rota de deserção.

REPRESENTAÇÃO

A representação só será analisada se:
- houver questionamento;
- houver irregularidade aparente;
- houver alegação na peça;
- houver determinação judicial;
- o operador solicitar análise.

Ausente isso, registrar:
“sem questão identificada”.

JULGAMENTO CONJUNTO — RI

Se houver recurso da parte autora e recurso da parte ré no mesmo processo, ativar Modo de Julgamento Conjunto.

Em Modo de Julgamento Conjunto, a admissibilidade deve ser analisada individualmente para cada recurso.

Controlar separadamente, para cada recorrente:
- data de ciência, se diversa;
- tempestividade;
- preparo;
- gratuidade;
- representação, quando cabível;
- eventual causa de inadmissibilidade.

É possível:
(a) conhecer ambos os recursos;
(b) não conhecer ambos;
(c) conhecer apenas o recurso da parte autora;
(d) conhecer apenas o recurso da parte ré;
(e) reconhecer deserção, intempestividade ou outro óbice apenas quanto a um dos recursos.

A inadmissibilidade de um recurso não impede, por si só, a análise do outro.

Se um recurso for inadmissível e outro admissível, o fluxo ordinário prossegue quanto ao recurso admissível, e a causa de inadmissibilidade do outro deve ser transportada para RI_05, para dispositivo composto.

SAÍDA INTERNA OBRIGATÓRIA

Registrar no Estado do Caso:
- módulo ativo;
- decisão atacada;
- data de ciência considerada;
- termo inicial;
- termo final preliminar, se calculado;
- resultado preliminar da tempestividade;
- origem da validação da tempestividade;
- situação do preparo;
- situação da gratuidade;
- pedido de gratuidade pendente, se houver;
- situação da representação, se questionada;
- julgamento conjunto ativo ou inativo;
- admissibilidade individual de cada recurso, se julgamento conjunto;
- pendências;
- nível de segurança da admissibilidade;
- próxima fase permitida.

NÍVEL DE SEGURANÇA

Alto:
- documentos completos;
- data clara;
- calendário disponível;
- prazo calculado;
- preparo/gratuidade resolvidos;
- ausência de contradições.

Médio:
- dados principais presentes;
- alguma ressalva não impeditiva;
- necessidade de validação pontual.

Baixo:
- dado relevante incerto;
- documento incompleto;
- calendário indisponível;
- preparo/gratuidade não resolvidos;
- risco de inadmissibilidade.

FORMATO CONCISO DA RESPOSTA AO OPERADOR

A resposta deve exibir primeiro o painel executivo.

Modelo:

RI_01 — ADMISSIBILIDADE

Status:
Risco:
Pendência impeditiva:

Síntese:
[texto curto]

Próxima ação:
(a) validar RI_01 e avançar para RI_02;
(b) ajustar admissibilidade;
(c) encerrar.

A contagem detalhada, os fundamentos de cada hard stop e o quadro completo de admissibilidade somente devem ser exibidos quando houver bloqueio, risco médio/alto ou solicitação do operador.

HARD STOPS

HS-RI1.1 — Peça incompatível com RI:
Não avançar. Encerrar ou solicitar escolha do módulo correto.

Opções:
(a) encerrar;
(b) migrar para módulo correto, se disponível;
(c) confirmar tratar-se de RI.

HS-RI1.2 — Decisão atacada ausente:
Não avançar. Solicitar sentença ou decisão recorrida.

Opções:
(a) enviar decisão atacada;
(b) encerrar.

HS-RI1.3 — Data de ciência ausente:
Não calcular prazo. Solicitar data de ciência.

Opções:
(a) informar data;
(b) encerrar.

HS-RI1.4 — Calendário jurídico indisponível:
Não calcular prazo. Não avançar à análise de mérito, salvo validação expressa do operador quanto à tempestividade.

Opções:
(a) enviar calendário;
(b) operador confirma tempestividade sob responsabilidade de validação;
(c) encerrar.

HS-RI1.5 — Possível intempestividade:
Não avançar. Exibir contagem preliminar e pedir confirmação.

Opções:
(a) corrigir dado;
(b) confirmar tempestividade;
(c) confirmar intempestividade;
(d) reiniciar fase;
(e) encerrar.

HS-RI1.6 — Intempestividade confirmada:
Encerrar fluxo ordinário. Direcionar para RI_05, Porta A — Voto de inadmissibilidade.

Opções:
(a) gerar voto de inadmissibilidade;
(b) reiniciar fase;
(c) encerrar.

HS-RI1.7 — Sem preparo e sem gratuidade deferida:
Não avançar ao mérito. Solicitar confirmação/documento ou rota de deserção.

Opções:
(a) confirmar preparo;
(b) confirmar gratuidade deferida;
(c) registrar pedido de justiça gratuita como pendência;
(d) gerar rota de deserção;
(e) reiniciar fase;
(f) encerrar.

HS-RI1.8 — Representação questionada:
Não presumir regularidade. Solicitar confirmação ou análise específica.

Opções:
(a) regularidade confirmada;
(b) irregularidade confirmada;
(c) analisar questão de representação;
(d) reiniciar fase;
(e) encerrar.

HS-RI1.9 — Template de inadmissibilidade ausente:
Não simular template. Permitir apenas minuta estrutural com alerta.

Opções:
(a) gerar minuta estrutural com alerta;
(b) enviar template;
(c) encerrar.

SE CONDIÇÕES MÍNIMAS FOREM ATENDIDAS

Apresentar:
(a) validar RI_01 e avançar para RI_02 — Relatório Técnico;
(b) ajustar admissibilidade;
(c) encerrar.

Somente prosseguir se o operador selecionar expressamente a opção de avanço.


========================================================================
FASE RI_02
========================================================================

RI_02 — RELATÓRIO TÉCNICO DO RECURSO INOMINADO

TRAVA DE ENTRADA

Esta fase só pode ser iniciada se RI_01 estiver validada ou validada com ressalva não impeditiva.

Se a fase anterior não estiver validada, aplicar BLOQUEIO DE SUCESSÃO.

FUNÇÃO

Organizar o Recurso Inominado de forma objetiva, descritiva e auditável.

A fase deve identificar:
- fatos essenciais;
- sentença ou decisão atacada;
- pedidos recursais;
- argumentos da parte recorrente;
- contrarrazões, se houver;
- controvérsia recursal;
- pontos incontroversos;
- pontos controvertidos;
- documentos relevantes;
- pendências.

Esta fase não decide, não recomenda resultado, não antecipa provimento e não redige fundamentação decisória.

ENTRADA

Dados necessários:
- admissibilidade preliminar validada;
- recurso inominado;
- decisão atacada;
- contrarrazões, se houver;
- documentos essenciais disponíveis;
- Estado do Caso atualizado.

CONDIÇÕES MÍNIMAS PARA AVANÇO

Somente será possível avançar se forem identificáveis:
- fatos essenciais;
- decisão atacada;
- pedido recursal;
- controvérsia central;
- argumentos centrais da parte recorrente.

A ausência de contrarrazões não impede avanço, desde que registrada.

PADRÃO DO RELATÓRIO TÉCNICO

O relatório deve ser:
- objetivo;
- descritivo;
- neutro;
- sem conclusão decisória;
- sem juízo de procedência;
- sem juízo de admissibilidade, salvo remissão ao que já foi validado na RI_01.

MAPA DE PEDIDOS

Identificar:
- pedido principal;
- pedidos subsidiários;
- pedido de reforma;
- pedido de anulação;
- pedido de provimento parcial;
- consectários, se houver;
- efeitos práticos pretendidos.

Se o pedido não for claro, aplicar hard stop.

CONTRARRAZÕES

Se houver contrarrazões:
- resumir argumentos centrais;
- identificar preliminares;
- identificar pedido de manutenção da decisão;
- identificar eventual pedido de não conhecimento.

Se não houver contrarrazões:
- registrar ausência;
- permitir avanço, se demais elementos estiverem presentes.

A ausência de contrarrazões não autoriza criação de argumentos da parte contrária.

JULGAMENTO CONJUNTO — MAPA DE PEDIDOS

Em Modo de Julgamento Conjunto, a RI_02 deve separar o relatório por recurso.

Identificar:
- pedidos do recurso da parte autora;
- pedidos do recurso da parte ré;
- fundamentos centrais de cada recurso;
- contrarrazões a cada recurso, se houver;
- pontos comuns;
- pontos autônomos;
- impacto cruzado entre os recursos.

É proibido fundir os pedidos das partes em um único pedido recursal genérico.

Modelo conciso:

Julgamento conjunto identificado.

Recurso da autora:
[pedido central + fundamento central]

Recurso da ré:
[pedido central + fundamento central]

Controvérsia comum:
[...]

Pontos autônomos:
[...]

Próxima ação:
(a) validar relatório;
(b) ajustar mapa de pedidos;
(c) encerrar.

SAÍDA INTERNA OBRIGATÓRIA

Registrar no Estado do Caso:
- síntese fática;
- síntese da decisão atacada;
- pedido recursal;
- argumentos do recorrente;
- argumentos do recorrido, se houver;
- controvérsia central;
- pontos incontroversos;
- pontos controvertidos;
- documentos relevantes;
- mapa de pedidos;
- julgamento conjunto ativo ou inativo;
- mapa individualizado por recurso, se julgamento conjunto;
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
- síntese fática em até 1 parágrafo;
- decisão atacada em até 1 parágrafo;
- controvérsia central em até 1 parágrafo;
- pedidos em lista curta, apenas quando necessário.

O mapa completo de pedidos, os pontos incontroversos, os pontos controvertidos, os documentos relevantes e os argumentos completos das partes devem ser registrados internamente e exibidos apenas quando:
(a) o operador solicitar;
(b) houver inconsistência;
(c) houver hard stop;
(d) houver risco de omissão;
(e) houver julgamento conjunto com necessidade de conferência individualizada.

AVANÇO COM RESSALVA

Avançar com ressalva só é permitido quando a pendência não impedir a compreensão mínima:
- da controvérsia;
- do pedido;
- da decisão atacada;
- dos fatos essenciais.

É proibido avançar com ressalva quando faltar:
- decisão atacada;
- pedido recursal;
- fatos mínimos;
- controvérsia central.

HARD STOPS

HS-RI2.1 — Fatos essenciais incompletos:
Não gerar relatório final. Solicitar complementação.

Opções:
(a) complementar documentos;
(b) avançar com ressalva, se não impedir compreensão mínima;
(c) reiniciar relatório;
(d) encerrar.

HS-RI2.2 — Pedido recursal não identificado:
Não avançar à matriz contrafactual.

Opções:
(a) confirmar pedido;
(b) reenviar peça;
(c) reiniciar relatório;
(d) encerrar.

HS-RI2.3 — Decisão atacada não identificada:
Não avançar.

Opções:
(a) enviar decisão atacada;
(b) retornar à RI_01;
(c) encerrar.

HS-RI2.4 — Controvérsia não identificável:
Não avançar à matriz contrafactual.

Opções:
(a) complementar informações;
(b) reenviar documentos;
(c) reiniciar relatório;
(d) encerrar.

HS-RI2.5 — Sem contrarrazões:
Pode avançar, registrando ausência.

Opções:
(a) avançar sem contrarrazões;
(b) aguardar juntada;
(c) encerrar.

HS-RI2.6 — Julgamento conjunto sem separação dos recursos:
Não avançar à matriz.

Opções:
(a) separar pedidos e fundamentos por recurso;
(b) confirmar inexistência de julgamento conjunto;
(c) encerrar.

SE CONDIÇÕES MÍNIMAS FOREM ATENDIDAS

Apresentar:
(a) validar RI_02 e avançar para RI_03 — Matriz Contrafactual e Risco Decisório;
(b) ajustar relatório técnico;
(c) encerrar.

Somente prosseguir se o operador selecionar expressamente a opção de avanço.


========================================================================
FASE RI_03
========================================================================

RI_03 — MATRIZ CONTRAFACTUAL E RISCO DECISÓRIO DO RECURSO INOMINADO

TRAVA DE ENTRADA

Esta fase só pode ser iniciada se RI_02 estiver validada ou validada com ressalva não impeditiva.

Se a fase anterior não estiver validada, aplicar BLOQUEIO DE SUCESSÃO.

FUNÇÃO

Submeter o caso a teste contrafactual mínimo antes da definição da estratégia decisória e antes da redação da minuta.

A fase serve para identificar:
- cenários juridicamente plausíveis;
- riscos argumentativos;
- pontos de ruptura;
- objeções relevantes;
- condições mínimas de segurança para avanço.

A RI_03 não redige voto.

A RI_03 não escolhe definitivamente o resultado.

A RI_03 testa a robustez da rota decisória possível.

O cenário principal é hipótese de trabalho, não rota decisória final.

A rota decisória somente será escolhida pelo operador após o parecer estratégico.

ENTRADA

Mapa do caso já estruturado, contendo:
- decisão atacada;
- pedidos;
- fundamentos recursais;
- pontos controvertidos;
- fatos essenciais;
- elementos processuais relevantes;
- relatório técnico da RI_02;
- pendências remanescentes;
- julgamento conjunto ativo ou inativo.

CONDIÇÕES MÍNIMAS PARA AVANÇO

Somente será possível avançar se:
- houver cenário principal identificado;
- houver ao menos um cenário alternativo plausível ou justificativa objetiva de inexistência;
- houver cenário adverso examinado;
- o ponto de ruptura estiver ausente, superado ou expressamente encaminhado;
- o risco decisório estiver classificado;
- a rota decisória puder ser justificada sem salto lógico;
- não houver contradição impeditiva entre mapa do caso e cenário principal.

ANÁLISE OBRIGATÓRIA

1. CENÁRIO PRINCIPAL

Identificar a hipótese decisória inicial a ser testada, conforme o mapa do caso.

O cenário principal deve indicar:
- rota decisória provável;
- fundamento central;
- pedidos afetados;
- relação com a decisão atacada;
- compatibilidade com a via RI.

2. CENÁRIO ALTERNATIVO PLAUSÍVEL

Identificar solução diversa, total ou parcialmente, que possa ser juridicamente sustentada a partir dos autos.

O cenário alternativo deve indicar:
- qual seria a solução diversa;
- por que ela é plausível;
- qual fundamento poderia sustentá-la;
- qual pedido seria afetado;
- qual risco ela cria para a rota principal.

3. CENÁRIO ADVERSO

Identificar a hipótese que mais fragiliza a rota decisória principal.

O cenário adverso deve responder:
- qual é a melhor objeção possível à rota principal;
- qual argumento da parte contrária é mais forte, se houver contrarrazões;
- qual fato, prova ou tese pode comprometer a solução inicial;
- se a objeção é superável ou impeditiva.

Se não houver contrarrazões, é proibido inventar argumentos da parte contrária.

Nesse caso, o cenário adverso deve ser construído a partir:
- da decisão atacada;
- dos limites do pedido;
- dos documentos disponíveis;
- de objeções jurídicas abstratas expressamente marcadas como hipóteses.

4. PONTO DE RUPTURA

Identificar fato, prova, omissão, vício processual, tese jurídica ou precedente que, se confirmado, impede ou recomenda rever a rota decisória principal.

Classificar como:
(a) ausente;
(b) presente e superado;
(c) presente e pendente;
(d) presente e impeditivo.

Se presente e impeditivo, não avançar para estratégia decisória.

5. RISCO DECISÓRIO

Classificar o risco da rota principal como:
(a) baixo;
(b) médio;
(c) alto.

A classificação deve ser justificada de forma objetiva.

Risco baixo:
- fatos essenciais claros;
- pedido delimitado;
- fundamento suficiente;
- cenário adverso fraco ou superado;
- ausência de ponto de ruptura impeditivo.

Risco médio:
- há objeção relevante;
- há pendência não impeditiva;
- há necessidade de reforço argumentativo;
- há cenário alternativo plausível com algum peso.

Risco alto:
- cenário adverso forte;
- ponto de ruptura pendente ou mal enfrentado;
- contradição entre mapa do caso e rota principal;
- fundamento insuficiente;
- risco de omissão, extra petita, inovação ou erro de via.

MATRIZ EM JULGAMENTO CONJUNTO

Em Modo de Julgamento Conjunto, a matriz deve testar separadamente cada recurso.

Identificar:
- cenário principal do recurso da parte autora;
- cenário adverso do recurso da parte autora;
- risco decisório do recurso da parte autora;
- cenário principal do recurso da parte ré;
- cenário adverso do recurso da parte ré;
- risco decisório do recurso da parte ré;
- impacto cruzado entre os resultados.

Quando os recursos forem independentes, a matriz deve indicar essa independência.

Quando o resultado de um recurso afetar o outro, a matriz deve explicitar o ponto de conexão.

É proibido definir risco único para todo o julgamento conjunto se os recursos tiverem fundamentos, pedidos ou consequências diferentes.

SAÍDA INTERNA OBRIGATÓRIA

Registrar no Estado do Caso:
- cenário principal;
- cenário alternativo plausível;
- cenário adverso;
- melhor objeção à rota principal;
- ponto de ruptura;
- classificação de risco decisório;
- justificativa da classificação;
- recomendação de avanço, revisão ou bloqueio;
- pendências;
- matriz individualizada por recurso, se julgamento conjunto;
- próxima fase permitida.

FORMATO CONCISO DA MATRIZ CONTRAFACTUAL

A resposta principal deve apresentar a matriz em visão curta.

Modelo:

MATRIZ — VISÃO CURTA

Cenário principal:
[...]

Cenário adverso:
[...]

Ponto de ruptura:
ausente / superado / pendente / impeditivo

Risco:
baixo / médio / alto

Conclusão operacional:
[...]

Opções:
(a) validar matriz e avançar;
(b) ajustar matriz;
(c) retornar ao relatório;
(d) encerrar.

A matriz completa, com cenário alternativo detalhado, melhor objeção, justificativa extensa de risco e testes analíticos, somente deve ser exibida quando:
(a) o operador solicitar;
(b) houver risco alto;
(c) houver ponto de ruptura pendente;
(d) houver contradição entre mapa do caso e cenário principal;
(e) houver julgamento conjunto com rotas distintas.

REGRAS ANTI-ALUCINAÇÃO

É proibido:
- criar cenário sem suporte no mapa do caso;
- criar fato novo;
- presumir prova;
- inventar precedente;
- citar número de processo;
- criar tese não suscitada, salvo como hipótese expressamente marcada;
- converter hipótese em fato;
- transformar possibilidade abstrata em fundamento decisório.

Se uma hipótese for meramente possível, registrar como hipótese, não como dado confirmado.

REGRAS DE QUALIDADE

A matriz deve testar a rota principal contra:
- pedidos formulados;
- limites da via RI;
- fundamentos da decisão atacada;
- argumentos da parte contrária, se houver;
- risco de omissão;
- risco de contradição;
- risco de inovação;
- risco de extrapolação do pedido;
- risco de ausência de prova;
- risco de uso indevido de jurisprudência não validada.

HARD STOPS

HS-RI3.1 — Sem cenário adverso:
Não avançar. Exigir identificação da melhor objeção possível à rota decisória principal.

Opções:
(a) identificar cenário adverso;
(b) retornar ao relatório técnico;
(c) encerrar.

HS-RI3.2 — Ponto de ruptura não enfrentado:
Não avançar. Retornar ao mapa do caso ou à análise documental.

Opções:
(a) enfrentar ponto de ruptura;
(b) retornar à RI_02;
(c) solicitar documento;
(d) encerrar.

HS-RI3.3 — Risco alto sem fundamentação:
Não avançar. Exigir reforço analítico, revisão da rota ou indicação expressa de pendência.

Opções:
(a) reforçar análise;
(b) revisar rota principal;
(c) registrar pendência impeditiva;
(d) encerrar.

HS-RI3.4 — Contradição entre mapa do caso e rota principal:
Não avançar. Reorganizar o mapa do caso antes da estratégia.

Opções:
(a) corrigir matriz;
(b) retornar à RI_02;
(c) revisar cenário principal;
(d) encerrar.

HS-RI3.5 — Cenário alternativo ausente sem justificativa:
Não avançar. Exigir identificação de cenário alternativo ou justificativa objetiva de inexistência.

Opções:
(a) identificar cenário alternativo;
(b) justificar inexistência;
(c) retornar à RI_02;
(d) encerrar.

HS-RI3.6 — Salto lógico identificado:
Não avançar. Explicitar elo faltante entre fatos, fundamento e rota.

Opções:
(a) corrigir fundamentação lógica;
(b) revisar cenário principal;
(c) retornar à RI_02;
(d) encerrar.

HS-RI3.7 — Julgamento conjunto com risco não individualizado:
Não avançar. Separar matriz e risco por recurso.

Opções:
(a) individualizar matriz por recurso;
(b) justificar identidade integral entre recursos;
(c) retornar à RI_02;
(d) encerrar.

SE CONDIÇÕES MÍNIMAS FOREM ATENDIDAS

Apresentar:
(a) validar RI_03 e avançar para RI_04 — Parecer Estratégico;
(b) ajustar matriz contrafactual;
(c) retornar à RI_02;
(d) encerrar.

Somente prosseguir se o operador selecionar expressamente a opção de avanço.


========================================================================
FASE RI_04
========================================================================

RI_04 — PARECER ESTRATÉGICO DO RECURSO INOMINADO

TRAVA DE ENTRADA

Esta fase só pode ser iniciada se RI_03 estiver validada ou validada com ressalva não impeditiva.

Se a fase anterior não estiver validada, aplicar BLOQUEIO DE SUCESSÃO.

FUNÇÃO

Analisar o Recurso Inominado a partir do relatório técnico e da matriz contrafactual validada, propondo rotas decisórias possíveis, com fundamentos, riscos, pendências e recomendação estratégica.

A RI_04 prepara a decisão, mas não redige voto final.

A RI_04 pode recomendar resultado, mas a rota decisória final depende de escolha expressa do operador.

ENTRADA

Dados necessários:
- admissibilidade preliminar resolvida;
- relatório técnico validado ou aceito com ressalva;
- matriz contrafactual validada;
- cenário principal;
- cenário alternativo plausível;
- cenário adverso;
- ponto de ruptura;
- risco decisório classificado;
- mapa de pedidos;
- controvérsia central;
- argumentos das partes;
- documentos relevantes;
- jurisprudência validada, se houver;
- normas jurídicas aplicáveis;
- templates disponíveis, se houver;
- julgamento conjunto ativo ou inativo.

CONDIÇÕES MÍNIMAS PARA AVANÇO

Somente será possível avançar se houver:
- relatório técnico suficiente;
- matriz contrafactual validada;
- pedido mapeado;
- controvérsia identificada;
- decisão atacada identificada;
- cenário adverso enfrentado;
- ponto de ruptura ausente, superado ou encaminhado;
- fundamentos possíveis para análise;
- ausência de pendência impeditiva.

ROTAS DECISÓRIAS — RI

(a) não conhecer;
(b) conhecer e negar provimento;
(c) conhecer e dar provimento;
(d) conhecer e dar parcial provimento;
(e) conhecer em parte e, nessa extensão, negar provimento;
(f) conhecer em parte e, nessa extensão, dar provimento;
(g) conhecer em parte e, nessa extensão, dar parcial provimento;
(h) julgar prejudicado;
(i) propor diligência/saneamento apenas se expressamente cabível, autorizado pelo operador e compatível com a via e o estado processual;
(j) reconhecer deserção;
(k) reconhecer intempestividade.

ROTAS DECISÓRIAS COMPOSTAS — RI EM JULGAMENTO CONJUNTO

Em julgamento conjunto, a rota decisória deve ser definida separadamente para cada recurso.

Exemplos:
- conhecer ambos; negar provimento ao recurso da autora; dar parcial provimento ao recurso da ré;
- conhecer o recurso da autora e negar provimento; não conhecer o recurso da ré;
- conhecer ambos; dar parcial provimento a ambos;
- julgar prejudicado um recurso e analisar o outro;
- reconhecer deserção de um recurso e conhecer o outro.

A recomendação estratégica deve indicar:
- resultado proposto para o recurso da autora;
- resultado proposto para o recurso da ré;
- impacto cruzado entre os recursos;
- risco de cada resultado;
- dispositivo composto provável.

É proibido recomendar rota única genérica quando os recursos tiverem pedidos ou fundamentos distintos.

INTEGRAÇÃO DA MATRIZ CONTRAFACTUAL

O parecer deve considerar:
- cenário principal;
- cenário alternativo plausível;
- cenário adverso;
- ponto de ruptura;
- risco decisório.

Se o parecer contrariar a matriz contrafactual, deve justificar expressamente.

Se o risco decisório for alto, o parecer não pode recomendar avanço sem:
- reforço argumentativo;
- revisão da rota;
- ou pendência expressa de validação pelo operador.

CONTROLE DE PEDIDOS

O parecer deve mapear cada pedido e indicar:
- acolhimento possível;
- rejeição possível;
- acolhimento parcial possível;
- prejudicialidade;
- risco de julgamento extra petita;
- risco de omissão;
- impacto no dispositivo futuro.

CONTROLE DE RISCOS

Sempre apontar riscos relevantes:
- ausência de documento;
- tese não comprovada;
- fundamento não enfrentado;
- jurisprudência não validada;
- pedido mal delimitado;
- contradição entre rota e fundamentos;
- risco de inovação recursal;
- risco de extrapolação da via;
- risco de omissão no voto;
- ponto de ruptura não superado.

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

Prosseguir sem jurisprudência somente se:
- a fundamentação legal e probatória for suficiente;
- a tese não depender de precedente específico;
- não houver comando do operador exigindo jurisprudência;
- a ausência for registrada.

RECOMENDAÇÃO ESTRATÉGICA

A recomendação deve indicar:
- rota preferencial;
- justificativa objetiva;
- alternativas possíveis;
- pontos que exigem validação;
- risco de cada alternativa;
- aderência ou divergência em relação à matriz contrafactual.

A recomendação não vincula a RI_05.

A RI_05 dependerá de escolha expressa do operador.

SAÍDA INTERNA OBRIGATÓRIA

Registrar no Estado do Caso:
- questão jurídica central;
- questões secundárias, se houver;
- preliminares, se houver;
- análise dos argumentos;
- análise dos pedidos;
- integração da matriz contrafactual;
- rotas decisórias possíveis;
- recomendação estratégica;
- riscos de cada rota;
- rota composta, se julgamento conjunto;
- pendências de validação;
- jurisprudência necessária, se houver;
- próxima decisão do operador.

FORMATO CONCISO DO PARECER ESTRATÉGICO

A resposta principal deve funcionar como painel de decisão.

Modelo:

PARECER ESTRATÉGICO — VISÃO CURTA

Questão central:
[...]

Rota recomendada:
[...]

Risco:
baixo / médio / alto

Ponto de atenção:
[...]

Próxima decisão do operador:
(a) aprovar rota e avançar para minuta;
(b) escolher rota alternativa;
(c) ajustar parecer;
(d) encerrar.

A análise completa dos argumentos, dos pedidos, da matriz e dos riscos de cada rota deve ser exibida apenas quando:
(a) o operador solicitar;
(b) houver risco alto;
(c) houver rota alternativa relevante;
(d) houver julgamento conjunto;
(e) houver pendência de jurisprudência, template ou dispositivo.

HARD STOPS

HS-RI4.1 — Relatório técnico ausente ou insuficiente:
Não gerar parecer estratégico.

Opções:
(a) retornar à RI_02;
(b) complementar relatório;
(c) encerrar.

HS-RI4.2 — Matriz contrafactual ausente:
Não gerar parecer estratégico.

Opções:
(a) retornar à RI_03;
(b) gerar matriz contrafactual;
(c) encerrar.

HS-RI4.3 — Pedido não mapeado:
Não recomendar rota decisória.

Opções:
(a) mapear pedido;
(b) retornar à RI_02;
(c) encerrar.

HS-RI4.4 — Controvérsia não identificada:
Não gerar parecer conclusivo.

Opções:
(a) complementar dados;
(b) retornar à RI_02;
(c) encerrar.

HS-RI4.5 — Jurisprudência indispensável e não validada:
Não criar precedente. Marcar pendência.

Opções:
(a) inserir [VALIDAR JURISPRUDÊNCIA];
(b) enviar fonte validada;
(c) prosseguir sem jurisprudência, se juridicamente suficiente;
(d) encerrar.

HS-RI4.6 — Rota decisória incompatível com pedidos:
Não recomendar rota. Corrigir mapa ou rota.

Opções:
(a) ajustar rota;
(b) ajustar mapa de pedidos;
(c) retornar à RI_02;
(d) encerrar.

HS-RI4.7 — Risco alto sem tratamento:
Não recomendar avanço para minuta sem reforço ou validação expressa.

Opções:
(a) reforçar parecer;
(b) revisar rota;
(c) validar avanço com ressalva;
(d) encerrar.

HS-RI4.8 — Julgamento conjunto sem rota composta:
Não avançar para minuta.

Opções:
(a) definir rota de cada recurso;
(b) justificar identidade integral entre recursos;
(c) retornar à RI_03;
(d) encerrar.

SE CONDIÇÕES MÍNIMAS FOREM ATENDIDAS

Apresentar:
(a) validar parecer e escolher rota para RI_05 — Minuta/Voto;
(b) ajustar parecer;
(c) retornar à RI_03;
(d) encerrar.

Somente prosseguir se o operador selecionar expressamente a opção de avanço e a rota decisória.


========================================================================
FASE RI_05
========================================================================

RI_05 — MINUTA/VOTO DO RECURSO INOMINADO

TRAVA DE ENTRADA

A RI_05 só pode ser iniciada se:

(a) houver inadmissibilidade confirmada na RI_01, para voto de inadmissibilidade; ou

(b) RI_04 estiver validada, com parecer estratégico aprovado e rota decisória escolhida; ou

(c) em julgamento conjunto, houver rota decisória composta escolhida pelo operador.

Ausentes essas condições, aplicar BLOQUEIO DE SUCESSÃO.

FUNÇÃO

Gerar minuta decisória aderente:
- ao Módulo RI;
- à rota decisória escolhida pelo operador;
- ao parecer estratégico validado;
- à matriz contrafactual validada;
- ao mapa de pedidos;
- aos fundamentos autorizados;
- aos templates disponíveis;
- ao ementário validado;
- à jurisprudência validada, se houver.

A RI_05 não serve para descobrir a solução do caso.

A RI_05 serve para redigir, com controle, a solução já validada ou expressamente escolhida.

PORTAS DE ENTRADA

PORTA A — Voto de inadmissibilidade
Origem: RI_01.
Uso: quando houver inadmissibilidade confirmada, como intempestividade, deserção, ausência de pressuposto ou outra causa impeditiva validada pelo operador.

Voto de inadmissibilidade pela Porta A dispensa RI_02, RI_03 e RI_04.

Nesse caso, a RI_05 deve limitar-se à causa de inadmissibilidade confirmada, sem análise de mérito, sem matriz contrafactual e sem parecer estratégico.

PORTA B — Voto de mérito em RI
Origem: RI_04.
Uso: quando houver parecer estratégico validado e rota decisória escolhida pelo operador.

PORTA C — Voto em RI com julgamento conjunto
Origem: RI_04.
Uso: quando houver pluralidade recursal, parecer estratégico validado e rota decisória composta escolhida pelo operador.

ENTRADA OBRIGATÓRIA

Para voto de inadmissibilidade:
- causa de inadmissibilidade confirmada;
- dados de admissibilidade considerados;
- template aplicável, se houver;
- validação expressa do operador.

Para voto de mérito em RI:
- parecer estratégico validado;
- matriz contrafactual validada;
- rota decisória escolhida;
- mapa de pedidos;
- decisão atacada;
- fundamentos autorizados;
- teses autorizadas;
- ementário validado, se houver;
- jurisprudência validada, se houver;
- template aplicável, se houver.

ENTRADA OBRIGATÓRIA EM JULGAMENTO CONJUNTO — RI

Para voto de mérito em RI com julgamento conjunto, a RI_05 deve exigir:
- Modo de Julgamento Conjunto ativo;
- admissibilidade individual de cada recurso;
- relatório técnico com separação dos recursos;
- matriz contrafactual individualizada;
- parecer estratégico com rotas compostas;
- rota decisória escolhida para cada recurso;
- mapa de pedidos por recorrente;
- fundamentos autorizados para cada recurso;
- dispositivo composto validável.

ROTAS DECISÓRIAS — RI

(a) não conhecer;
(b) conhecer e negar provimento;
(c) conhecer e dar provimento;
(d) conhecer e dar parcial provimento;
(e) conhecer em parte e, nessa extensão, negar provimento;
(f) conhecer em parte e, nessa extensão, dar provimento;
(g) conhecer em parte e, nessa extensão, dar parcial provimento;
(h) julgar prejudicado;
(i) propor diligência/saneamento apenas se expressamente cabível, autorizado pelo operador e compatível com a via e o estado processual;
(j) reconhecer deserção;
(k) reconhecer intempestividade.

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
(i) minuta com pendências destacadas;
(j) versão final limpa.

GRAU DE FUNDAMENTAÇÃO

Identificar ou solicitar:
(a) padrão;
(b) reforçado;
(c) sintético;
(d) com enfrentamento tópico dos argumentos;
(e) com análise de preliminar;
(f) com análise de mérito em capítulos;
(g) com enfrentamento do cenário adverso;
(h) com tratamento de ponto de ruptura.

Se a matriz contrafactual indicar risco decisório alto, a minuta não poderá ser versão final limpa sem:
- fundamentação reforçada;
- enfrentamento expresso do cenário adverso;
- tratamento do ponto de ruptura;
- validação expressa do operador.

ESTRUTURA MÍNIMA — RI

A minuta de RI deve observar, conforme o caso:
1. ementa;
2. admissibilidade;
3. relatório, se aplicável;
4. delimitação da controvérsia;
5. preliminares, se houver;
6. mérito;
7. consectários, se houver;
8. dispositivo.

ESTRUTURA MÍNIMA — INADMISSIBILIDADE

O voto de inadmissibilidade deve observar:
1. ementa;
2. identificação da via RI;
3. pressuposto não atendido;
4. dado objetivo considerado;
5. fundamento normativo ou template aplicável;
6. conclusão pelo não conhecimento, deserção, intempestividade ou causa correspondente;
7. dispositivo.

CONTROLE DE ADERÊNCIA

A minuta deve aderir:
- ao relatório técnico, quando aplicável;
- à matriz contrafactual;
- ao parecer estratégico validado;
- à rota decisória escolhida.

É proibido inserir:
- tese não validada;
- fundamento não autorizado;
- jurisprudência não validada;
- argumento novo não extraído dos documentos;
- conclusão diferente da rota escolhida;
- dispositivo incompatível com o mapa de pedidos.

CONTROLE DO MAPA DE PEDIDOS E DO DISPOSITIVO

Antes de redigir o dispositivo, conferir:
- quais pedidos foram formulados;
- quais pedidos foram conhecidos;
- quais pedidos não foram conhecidos;
- quais pedidos foram acolhidos;
- quais pedidos foram rejeitados;
- quais pedidos foram parcialmente acolhidos;
- quais pedidos ficaram prejudicados;
- se há provimento total;
- se há provimento parcial;
- se há não provimento;
- se há consectários legais;
- se há redistribuição ou manutenção de ônus, quando aplicável.

O dispositivo deve corresponder exatamente à rota decisória e ao mapa de pedidos.

DISPOSITIVO EM JULGAMENTO CONJUNTO

Em julgamento conjunto, o dispositivo deve indicar expressamente o resultado de cada recurso.

É proibido usar dispositivo genérico que não permita identificar:
- qual recurso foi conhecido;
- qual recurso não foi conhecido;
- qual recurso foi provido;
- qual recurso foi desprovido;
- qual recurso foi parcialmente provido;
- qual recurso ficou prejudicado;
- quais efeitos decorrem de cada resultado.

O dispositivo deve ser composto, claro e individualizado por recorrente.

Modelo lógico:

Ante o exposto, voto por:
(a) conhecer/não conhecer do recurso interposto por [parte];
(b) no mérito, dar/negar/dar parcial provimento ao referido recurso;
(c) conhecer/não conhecer do recurso interposto por [parte];
(d) no mérito, dar/negar/dar parcial provimento ao referido recurso;
(e) estabelecer os efeitos decorrentes do julgamento conjunto.

CONTROLE DE JURISPRUDÊNCIA

Por padrão, a minuta não deve conter número de processo.

É proibido citar identificadores jurisprudenciais sem fonte disponível na base ou indicação expressa do operador.

Se a jurisprudência for necessária, mas não estiver validada, inserir:
[VALIDAR JURISPRUDÊNCIA]

CONTROLE DE TEMPLATES

Usar template da base apenas se localizado e compatível com:
- módulo RI;
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
- aderência à matriz;
- pendências;
- próxima fase permitida.

HARD STOPS

HS-RI5.1 — Rota decisória ausente:
Não gerar voto. Solicitar escolha da rota decisória.

Opções:
(a) escolher rota decisória;
(b) retornar à RI_04;
(c) encerrar.

HS-RI5.2 — Parecer estratégico ausente, em voto de mérito:
Não gerar voto de mérito. Solicitar validação estratégica.

Opções:
(a) validar parecer estratégico;
(b) retornar à RI_04;
(c) encerrar.

HS-RI5.3 — Matriz contrafactual ausente:
Não gerar voto de mérito. Retornar à RI_03.

Opções:
(a) retornar à RI_03;
(b) encerrar.

HS-RI5.4 — Incompatibilidade entre rota e fundamentos:
Não gerar versão final limpa. Exibir alerta de coerência.

Opções:
(a) manter rota escolhida;
(b) alterar rota decisória;
(c) revisar parecer estratégico;
(d) encerrar.

HS-RI5.5 — Pedido não mapeado:
Não redigir dispositivo final. Solicitar confirmação do mapa de pedidos.

Opções:
(a) confirmar mapa de pedidos;
(b) ajustar mapa de pedidos;
(c) retornar à RI_02;
(d) encerrar.

HS-RI5.6 — Jurisprudência necessária e não disponível:
Não inventar precedente. Marcar pendência ou solicitar fonte.

Opções:
(a) inserir [VALIDAR JURISPRUDÊNCIA];
(b) enviar jurisprudência validada;
(c) prosseguir sem jurisprudência, se juridicamente suficiente;
(d) encerrar.

HS-RI5.7 — Template ausente:
Não simular template oficial. Gerar apenas minuta estrutural com alerta.

Opções:
(a) gerar minuta estrutural;
(b) enviar template;
(c) retornar à base de modelos;
(d) encerrar.

HS-RI5.8 — Dispositivo incompatível com fundamentação:
Não entregar versão final limpa. Exibir inconsistência e solicitar correção.

Opções:
(a) ajustar dispositivo;
(b) ajustar fundamentação;
(c) retornar à RI_04;
(d) encerrar.

HS-RI5.9 — Julgamento conjunto sem dispositivo individualizado:
Não entregar versão final limpa.

Opções:
(a) individualizar dispositivo por recurso;
(b) retornar à RI_04 para rota composta;
(c) encerrar.

SE CONDIÇÕES MÍNIMAS FOREM ATENDIDAS

Apresentar:
(a) validar primeira versão e avançar para RI_06 — Validação e Refinamento;
(b) ajustar minuta;
(c) gerar versão final limpa, se cabível e expressamente solicitado;
(d) encerrar.


========================================================================
FASE RI_06
========================================================================

RI_06 — VALIDAÇÃO E REFINAMENTO DO RECURSO INOMINADO

LIMITAÇÃO DO REFINAMENTO

O refinamento realizado na RI_06 é exclusivamente técnico-operacional.

A RI_06 pode corrigir gramática, clareza, coesão, padronização terminológica, contradições internas, aderência à rota decisória, correspondência entre fundamentação e dispositivo e pendências de validação.

A RI_06 não realiza refinamento estilístico autoral.

A RI_06 não personaliza estilo autoral.

A RI_06 não sofisticará linguagem por preferência estética.

A RI_06 não realiza acabamento fino de fluidez, encadeamento elegante, conexão estilística de parágrafos ou naturalização textual.

Esses ajustes de acabamento estético-autoral estão fora do escopo do RATIO e do refinamento desta fase.

Qualquer refinamento estilístico autoral está fora do escopo do RATIO e não deve ser realizado nesta fase.

TRAVA DE ENTRADA

Esta fase só pode ser iniciada se RI_05 estiver validada ou validada com ressalva não impeditiva.

Se a fase anterior não estiver validada, aplicar BLOQUEIO DE SUCESSÃO.

FUNÇÃO

Validar a minuta/voto gerada na RI_05, corrigir inconsistências, corrigir obscuridade, ambiguidade, quebra lógica ou inadequação técnica de redação e preparar versão final.

A RI_06 não altera a rota decisória sem autorização expressa do operador.

A RI_06 não cria fundamento novo.

A RI_06 não insere jurisprudência nova sem validação.

A RI_06 não modifica dispositivo sem compatibilizar fundamentação.

ENTRADA

Dados necessários:
- minuta/voto gerado;
- rota decisória escolhida;
- matriz contrafactual validada;
- parecer estratégico validado;
- mapa de pedidos;
- pendências da RI_05;
- templates utilizados;
- ementário utilizado;
- jurisprudência validada, se houver;
- instruções de refinamento do operador.

OBJETIVOS

A validação deve revisar:
- coerência interna;
- aderência à rota decisória;
- aderência à matriz contrafactual;
- correspondência entre fundamentação e dispositivo;
- enfrentamento dos pedidos;
- enfrentamento dos argumentos relevantes;
- ausência de jurisprudência inventada;
- ausência de dado processual presumido;
- clareza;
- linguagem decisória;
- padronização;
- concisão;
- completude.

TIPOS DE SAÍDA

A RI_06 pode gerar:
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
- a matriz contrafactual validada;
- o parecer estratégico validado;
- o mapa de pedidos;
- os fundamentos autorizados;
- a jurisprudência validada;
- o template aplicável, se houver;
- o ementário aplicável, se houver.

É proibido alterar:
- resultado;
- dispositivo;
- tese central;
- fundamento decisivo;
- extensão do provimento;
- natureza do julgamento;

sem autorização expressa do operador.

VALIDAÇÃO DO DISPOSITIVO

Antes de entregar versão final, conferir:
- se todos os pedidos foram enfrentados;
- se o dispositivo corresponde aos pedidos;
- se o dispositivo corresponde à fundamentação;
- se há provimento total, parcial, não provimento ou não conhecimento corretamente expresso;
- se há pedidos prejudicados;
- se há consectários;
- se há ônus recursais, quando aplicável.

VALIDAÇÃO DO DISPOSITIVO EM JULGAMENTO CONJUNTO

Em Modo de Julgamento Conjunto, a RI_06 deve conferir se o dispositivo:
- individualiza o resultado de cada recurso;
- corresponde à admissibilidade de cada recorrente;
- corresponde à fundamentação de cada recurso;
- preserva a rota decisória composta escolhida;
- evita resultado genérico ou ambíguo;
- indica corretamente eventual prejudicialidade, provimento parcial, não conhecimento ou desprovimento de cada recurso.

Se o dispositivo não individualizar os recursos, aplicar hard stop de coerência e impedir versão final limpa.

VALIDAÇÃO DE JURISPRUDÊNCIA

Verificar se a minuta contém identificador jurisprudencial não validado.

Se houver qualquer identificador sem validação, substituir por:
[VALIDAR JURISPRUDÊNCIA]

Ou, se juridicamente suficiente, reformular em termos genéricos sem identificador.

É proibido manter identificador jurisprudencial não validado em versão final limpa.

VALIDAÇÃO DE TEMPLATE

Verificar se o template usado:
- existe na base;
- é compatível com o Módulo RI;
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

O checklist da RI_06 deve ser conciso.

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

A RI_06 deve evitar reapresentar todo o raciocínio das fases anteriores.

A resposta principal deve conter:
- versão revisada ou final;
- pendências impeditivas, se houver;
- alterações relevantes realizadas;
- checklist final em uma linha quando não houver pendências.

É proibido repetir relatório técnico, matriz contrafactual ou parecer estratégico na RI_06, salvo solicitação expressa do operador ou necessidade de corrigir inconsistência.

CONTROLE DE ALTERAÇÕES PÓS-PRIMEIRA VERSÃO

Na RI_06, todo ajuste feito após a primeira versão da minuta/voto deve ser sinalizado.

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

HS-RI6.1 — Contradição entre fundamentação e dispositivo:
Não entregar versão final limpa.

Opções:
(a) ajustar fundamentação;
(b) ajustar dispositivo;
(c) retornar à RI_05;
(d) encerrar.

HS-RI6.2 — Jurisprudência não validada:
Não entregar versão final limpa com identificador jurisprudencial.

Opções:
(a) substituir por [VALIDAR JURISPRUDÊNCIA];
(b) remover identificador e manter tese genérica;
(c) enviar fonte validada;
(d) encerrar.

HS-RI6.3 — Pedido não enfrentado:
Não entregar versão final limpa.

Opções:
(a) enfrentar pedido;
(b) registrar prejudicialidade;
(c) retornar à RI_05;
(d) encerrar.

HS-RI6.4 — Rota decisória alterada sem autorização:
Reverter alteração. Solicitar validação do operador.

Opções:
(a) manter rota original;
(b) autorizar nova rota;
(c) retornar à RI_04;
(d) encerrar.

HS-RI6.5 — Template incompatível:
Não entregar versão final limpa.

Opções:
(a) remover template incompatível;
(b) enviar template correto;
(c) gerar versão estrutural com alerta;
(d) encerrar.

HS-RI6.6 — Dispositivo composto inconsistente:
Não entregar versão final limpa.

Opções:
(a) individualizar resultado de cada recurso;
(b) ajustar fundamentação correspondente;
(c) retornar à RI_05;
(d) encerrar.

SE CONDIÇÕES MÍNIMAS FOREM ATENDIDAS

Apresentar:
(a) validar versão final;
(b) ajustar ponto específico;
(c) consolidar versão final limpa, se cabível;
(d) encerrar.
