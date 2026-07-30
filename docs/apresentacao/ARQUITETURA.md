# Arquitetura

Descrição dos quatro módulos em linguagem de operação jurídica. Sem código.

---

## CORPUS: a entrada do caso

O que um escritório faz hoje ao receber um caso: junta as peças, lê, separa o
que interessa, anota o que precisa de cuidado.

O CORPUS faz isso de forma registrada.

Cada documento entra pelo sistema e é imediatamente cifrado no cofre local. O
caminho físico do arquivo não sai do servidor. A partir daí, o CORPUS extrai o
texto, usando OCR quando o documento é imagem ou PDF sem camada de texto.
Depois identifica dado pessoal, substitui por pseudônimo com mapa reversível
guardado cifrado, e monta um inventário do documento.

O inventário registra método de extração, número de páginas, quantidade de
caracteres, confiança do OCR, número do processo, classe processual, nível de
sigilo, quantos dados pessoais de cada tipo foram encontrados e quantos
pseudônimos foram criados. O inventário não contém o texto do documento e não
contém o nome do arquivo.

**Onde a pessoa decide.** O processamento para sozinho em três situações:
quando detecta indício de sigilo, quando precisou de OCR e quando o texto
extraído ficou abaixo do mínimo aceitável. Nas três, o caso entra em estado de
revisão e não sai dali sem que alguém aprove ou exclua o documento, com nome
registrado.

Fechar a etapa do CORPUS com qualquer revisão em aberto é recusado pelo
sistema. Não é aviso. É recusa.

---

## RATIO: o protocolo decisório

Um voto não se escreve de uma vez. Primeiro se examina admissibilidade. Depois
se monta o relatório. Depois se avalia o risco da decisão. Depois se forma o
parecer. Só então se minuta.

O RATIO transforma essa sequência em fases nomeadas, com estado próprio, para
três tipos de peça:

| Módulo | Fases |
|---|---|
| **RI** (recurso inominado) | Admissibilidade, Relatório Técnico, TROIA, Parecer Estratégico, Minuta/Voto, Validação e Refinamento |
| **ED** (embargos de declaração) | Admissibilidade, Relatório Técnico, Parecer Estratégico, Minuta/Voto, Validação e Refinamento |
| **MS** (mandado de segurança) | Cabimento e Admissibilidade, Mapa do Ato Coator, Decisão Liminar, Processamento Pós-Liminar, Parecer de Mérito, Sentença/Acórdão, Validação e Refinamento |

Cada fase tem status próprio. Uma fase pode estar em análise, bloqueada,
pendente de remediação, validada, validada com ressalva não bloqueante,
dispensada por exceção, invalidada por mudança substancial, ou encerrada por
ora após liminar. Esse vocabulário existe porque a operação jurídica real
precisa dele.

### TROIA

TROIA é o teste contrafactual interno: a pergunta sobre o que aconteceria se a
premissa central estivesse errada.

A posição de TROIA muda conforme a peça, e essa diferença é normativa:

- No **RI**, TROIA é fase própria e obrigatória. A matriz contrafactual e o
  risco decisório precisam ser produzidos, sempre.
- No **ED**, TROIA é condicional e embutida. Ela se ativa por sete gatilhos,
  entre eles pedido de efeito infringente, mudança material do resultado,
  risco de rediscussão do mérito, contradição entre fundamentação e
  dispositivo, e risco de omissão em voto futuro.
- No **MS**, TROIA não está definida nesta versão. O sistema declara isso
  explicitamente, em vez de fingir cobertura.

**Onde a pessoa decide.** Nenhuma fase avança sozinha. O avanço só ocorre por
uma ação de operador, com nome e número de revisão. São oito ações possíveis:
validar, validar com ressalva, avançar, configurar TROIA, validar TROIA,
bloquear TROIA, retomar TROIA e retornar após mudança.

O modelo de linguagem produz o conteúdo da fase. Ele não valida a fase, não
configura TROIA e não decide avançar. Códigos de bloqueio vêm de um catálogo
fechado; código inventado é recusado.

---

## CERNE: a auditoria adversarial

Um parecer que só se lê a si mesmo não encontra o próprio erro. O CERNE existe
para confrontar o resultado do RATIO antes que ele receba acabamento.

O confronto usa uma base normativa própria: prompt mestre, cards de confronto,
camada de antibanalização, checklist de auditoria e onze eixos de exame
derivados de linhas distintas de teoria da argumentação e do direito. Essa base
é verificada por hash antes de o sistema se declarar pronto. Se um arquivo
normativo for alterado, o identificador da release muda.

O CERNE devolve um veredicto entre cinco:

| Gate | Significado |
|---|---|
| `AVANCA` | Segue para acabamento |
| `AVANCA_COM_AJUSTE` | Segue, com ressalva registrada |
| `REVISAO_HUMANA` | Para e chama uma pessoa |
| `BLOQUEIO_PARCIAL` | Para, parte do raciocínio não se sustenta |
| `BLOQUEIO_TOTAL` | Para, o resultado não pode seguir |

Junto vem um relatório estruturado: estado do documento, síntese objetiva,
ponto principal de atenção, impacto prático, ajustes necessários, o que pode
ser preservado e recomendação final.

**Onde a pessoa decide.** Três dos cinco gates param o caso e não têm saída
automática. Sair de revisão humana, bloqueio parcial ou bloqueio total exige
uma decisão registrada com código de catálogo e ator identificado: devolver o
caso ao RATIO para retrabalho, ou reabrir um bloqueio total. Não há botão de
seguir assim mesmo.

---

## LUX: o acabamento

A última etapa ajusta o texto e aplica a política de anonimização da saída.

O acabamento tem três modos: padrão, clareza e estilo. Há perfis de estilo
nomeados. E há três modos de dado, que determinam o que pode aparecer no texto
final: público, pseudonimizado e corpus.

A biblioteca que detecta dado pessoal no LUX é a mesma que detectou dado
pessoal na entrada. Uma única versão declarada, gravada no cabeçalho de todo
registro de execução. Isso impede que a mudança de uma biblioteca compartilhada
altere o comportamento de dois módulos sem deixar rastro.

**Onde a pessoa decide.** A escolha do modo de dado é do operador, com nome
registrado. Ela determina o grau de exposição do texto final. Violação da
política de privacidade e saída fora do contrato são recusadas, e nada é
gravado nos dois casos.

---

## Por que a arquitetura é governada

### O que é registrado

Toda passagem entre etapas gera um evento com sequência, comando, estágio de
origem, estágio de destino, componente responsável, versão do componente,
identificador da release, ator e carimbo de tempo.

O evento não contém conteúdo jurídico. Só hashes, códigos, identificadores e
versões. É possível auditar quem fez o quê, quando, com qual versão de qual
módulo, sem que a trilha de auditoria vire uma segunda cópia do processo.

### Versão fixada na origem

A release é escolhida pelo servidor no momento em que o caso é criado, e
permanece a mesma até o fim. Um caso iniciado hoje termina com a mesma
composição de versões com que começou. Um artefato produzido por uma versão
não pode ocupar o lugar de outra: o sistema compara produtor, versão do
produtor, release e schema, e recusa a divergência.

Isso responde a uma pergunta que só aparece meses depois: com qual versão de
qual módulo esta peça foi produzida.

### Nada roda em nuvem

Banco, cofre, modelo e API rodam em máquina local. A API é servida apenas em
`127.0.0.1`. O adapter de inferência ignora proxies do ambiente. Documento
jurídico não sai da máquina.

### Determinismo declarado

Toda chamada ao modelo fixa temperatura zero, semente fixa, janela de contexto
e teto de geração. Antes de chamar, o sistema calcula um teto conservador de
tamanho e recusa localmente o que não caberia com folga. Depois de receber,
exige a telemetria de tokens e recusa resposta truncada. Não existe caminho de
sucesso sem essa telemetria.

Cada inferência registra o digest do modelo e os hashes de entrada, saída e
parâmetros.

---

## Onde o humano decide, e por que isso é desenho

Resumo dos pontos de parada obrigatória:

| Momento | Decisão | Registro |
|---|---|---|
| Documento com sigilo, OCR ou baixa qualidade | Aprovar ou excluir | Ator e decisão |
| Cada fase do RATIO | Uma de oito ações | Ator e número de revisão |
| Configuração de TROIA no ED | Quais gatilhos se aplicam | Ator e gatilhos |
| Gate do CERNE em revisão ou bloqueio | Devolver ao RATIO ou reabrir | Ator e código de catálogo |
| Acabamento no LUX | Modo de dado da saída | Ator e modo |

Nenhum desses pontos é limitação técnica contornável com mais engenharia. Cada
um é uma escolha sobre onde a responsabilidade profissional precisa aparecer no
registro.

O argumento é simples. Um sistema que decide sozinho transfere para o
fornecedor uma responsabilidade que é do profissional. Quando a peça é
questionada, a pergunta não é qual modelo rodou. A pergunta é quem assinou. O
ATRIO organiza o trabalho para que essa resposta exista, com nome, data e
versão.

A consequência é que o sistema não promete autonomia. Ele promete que a decisão
tem dono e que o caminho até ela ficou registrado.
