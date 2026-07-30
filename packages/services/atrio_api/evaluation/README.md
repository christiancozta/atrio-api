# Instrumento de avaliação do ATRIO

O produto candidato e o instrumento experimental são objetos congelados
separadamente. Nenhum comando `run` é autorizado enquanto o gate em
`harness_config.json` estiver desabilitado ou enquanto o freeze configurado não
possuir timestamp externo criptograficamente verificado.

O fluxo possui níveis distintos:

1. suíte isolada exportada diretamente do Git;
2. Tier 0 de instrumentação e métricas automáticas;
3. smoke técnico com 3–5 casos fictícios;
4. piloto de calibração fora do conjunto final;
5. teste comparativo conforme o protocolo pré-registrado.

Tier 0 e smoke não estimam eficácia jurídica. Todo caso exposto em qualquer
nível é consumido de forma irreversível antes da leitura do conteúdo.

## Braços

O protocolo autoritativo declara A0–A10. A0–A9 são braços automatizados; A10 é
o comparador humano e nunca pode ser executado como um comando de modelo.

O runner `tools/evaluation/run_atrio_smoke_arm.py` implementa somente a
integração técnica de A8. Ele automatiza decisões de operador e, por isso,
recusa execução fora do pool `smoke`. Os demais braços continuam bloqueados até
terem implementações literais, revisadas e congeladas.

## Contexto e telemetria

Toda chamada Ollama fixa `num_ctx` e `num_predict`, aplica limite conservador
pré-inferência e exige `prompt_eval_count` e `eval_count`. O runner também
carrega o modelo com um prompt sem dados e confirma em `/api/ps` que o contexto
efetivamente alocado é pelo menos o valor congelado.

O limite conservador usa bytes UTF-8 como teto superior de tokens e reserva
overhead do template. Ele pode recusar um prompt que caberia no tokenizer real,
mas não aceita silenciosamente um prompt potencialmente truncado. A adoção de
um tokenizer exato e congelado exige emenda explícita do instrumento.

## Custódias separadas

`Initialize-EvalCustody.ps1` cria uma chave aleatória exclusiva para os mapas de
cegamento em `evaluation/_custody/secret.key`. Essa chave:

- não deriva da frase do cofre CORPUS;
- não abre artefatos do CORPUS;
- não é registrada no Git;
- deve ficar, idealmente, com custodiante diferente do executor.

O runner A8 ainda precisa ler o artefato LUX do cofre do produto. O caminho da
frase desse cofre deve ser fornecido separadamente em
`ATRIO_EVAL_VAULT_PASSPHRASE_FILE`. O valor sentinela no config deve ser
substituído apenas na configuração operacional não versionada.

## Cegamento e falhas

A ordem dos braços automatizados é permutada por caso e a semente é registrada
fora do pacote do avaliador. Os identificadores cegos e a permutação de outputs
também são novos para cada caso. Se um braço falhar, os demais continuam sob a
mesma política; a execução fica `completed_with_failures` e não pode ser
cegada.

Cada `output.json` é validado de forma bloqueante contra
`prereg/arm_output_schema_1.0.0.json`.

## Estado atual

O gate permanece deliberadamente desabilitado. Antes de qualquer smoke ainda
faltam:

- pacote canônico decidido e congelado;
- implementações A0–A9 e fluxo humano A10;
- banco experimental isolado;
- segredo do cofre CORPUS configurado fora do Git;
- custodiante e avaliadores;
- timestamp externo verificado.

O caso em `fixtures/smoke_ri_001.txt` é fictício e pertence somente ao smoke.
Ele nunca pode migrar para calibração ou teste.
