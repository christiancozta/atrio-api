# Avaliação formal da API

Este documento distingue a validação que o ATRIO já possui do que a avaliação
formal da API procura estabelecer.

**O método ATRIO possui validação operacional em ambiente real. A implementação
backend possui verificação automatizada de engenharia. A avaliação experimental
formal da API está em fechamento e seus resultados ainda não integram esta
baseline.**

Essas três camadas não são equivalentes. A operação anterior demonstra uso,
viabilidade e refinamento do método. Os testes demonstram propriedades do
código. O protocolo formal procura medir causalidade, generalização e eficácia
comparativa da implementação atual.

---

## O que existe hoje

### Validação operacional anterior à API

O ATRIO foi aplicado em fluxo jurídico real por meio de plataformas online de
IA generativa, sob supervisão humana direta. A operação incluiu análise
individual de outputs, definição de padrões, incorporação de críticas,
extração própria de indicadores e refinamento iterativo dos módulos.

As métricas resultantes são evidência operacional contextual. Elas não são
apagadas pela avaliação formal e também não são convertidas, sem desenho
controlado, em estimativas causais da API atual.

### Protocolo desenhado e congelado

O protocolo de avaliação está escrito, na versão 1.0. Junto dele estão o schema
do conjunto de dados (versão 1.0.0), o exemplo de registro (versão 1.0.0) e o
contrato de saída dos braços cegos (versão 1.0.0).

O protocolo declara onze braços, de A0 a A10. A0 a A9 são automatizados. A10 é
o comparador humano e nunca pode ser executado como comando de modelo.

### Emenda pré-dados registrada

Uma emenda foi incorporada antes de qualquer coleta, e o registro de emendas
declara explicitamente quantos dados experimentais foram observados antes da
alteração: nenhum. O único caso cadastrado é fictício e nunca foi executado.

A emenda corrige quatro riscos metodológicos identificados antes da execução:

1. Separação entre teste técnico de instrumentação e piloto de calibração,
   para que um não contamine o outro. Caso exposto em qualquer dos dois nunca
   entra no conjunto final.
2. Fechamento do padrão de referência antes de qualquer contato com a decisão
   judicial original. Só depois a decisão original entra, cega, submetida aos
   mesmos critérios.
3. Duas passagens humanas irreversíveis. A primeira é encerrada e congelada
   antes da abertura dos materiais da segunda. Não é permitido voltar, editar
   registros ou recalibrar notas depois da exposição.
4. Permutação independente dos rótulos por caso, com o mapa em custódia
   separada, para que o avaliador não aprenda a identidade dos braços.

### Instrumento congelado

O adapter de inferência fixa janela de contexto e teto de geração, aplica um
limite conservador antes de chamar o modelo e exige telemetria de tokens na
resposta. O runner do braço técnico carrega o modelo com um prompt sem dados e
confirma que o contexto alocado é ao menos o valor congelado antes de qualquer
execução.

Três testes automatizados foram acrescentados especificamente para travar esse
contrato: o preflight conservador falha antes de qualquer chamada HTTP, as
opções de contexto são obrigatórias e consistentes, e resposta sem telemetria
de tokens não conta como sucesso.

### Instrumento fail-closed

Quatro testes automatizados garantem que o harness falha fechado:

- o gate desabilitado bloqueia antes de o caso ser consumido;
- o caso é consumido de forma irreversível antes de o executor ler a entrada;
- caso já exposto não pode ser reutilizado;
- falha de um braço não impede os demais, e a execução fica marcada como
  concluída com falhas, sem poder ser cegada.

A ordem importa. O caso é queimado antes da leitura, não depois. Isso impede
que uma execução abortada devolva um caso ao pool como se nada tivesse
acontecido.

### Suíte limpa com evidência

O pacote histórico ligado ao commit `dfd509e` registra 169 testes
automatizados, 0 falhas, 0 erros e 0 pulados. A evidência foi exportada
diretamente do Git, com JUnit, saída padrão, saída de erro, tarball da fonte e
um manifesto com hashes e tamanhos de cada artefato, mais o ambiente completo
e a lista de dependências com versões fixas.

A suíte atual possui 175 testes aprovados. Os seis testes adicionais cobrem as
rotas finais de integridade, retorno ao LUX e liberação.

Isso mede uma coisa: o código faz o que os testes dizem. Não mede qualidade
jurídica de nada.

---

## O que o pacote de pré-registro diz de si mesmo

O pacote canônico de pré-registro declara o próprio estado no manifesto:

```
"status": "DRAFT_BLOCKED"
"execution_authorized": false
"external_timestamp": { "provider": null, "receipt_sha256": null, "status": "PENDING" }
```

E o próprio README do pacote afirma: ele ainda não é um pré-registro
externamente demonstrável e não autoriza execução.

O gate do harness está desabilitado no arquivo de configuração. Enquanto
estiver assim, nenhum comando de execução é autorizado, em nenhum nível.

---

## As nove pendências

Do registro de decisões. Todas em estado PENDENTE. Nenhuma pode ser resolvida
implicitamente pelo código.

| ID | Decisão ou dependência | O que fecha |
|---|---|---|
| **D01** | Um modelo com conclusão estreita, ou desenho fatorial com dois níveis de modelo | Estimando, modelos, snapshots, parâmetros, poder e interação pré-registrados |
| **D02** | Implementações literais dos braços A0 a A9 | Scripts revisados contra as definições e hashes congelados |
| **D03** | Fluxo humano do braço A10 | Instrução, formulário, seleção da subamostra e custódia aprovados |
| **D04** | Tokenização exata | Tokenizer compatível com o snapshot congelado, ou aceitação explícita do limite conservador atual |
| **D05** | Banco experimental isolado | Alvo, usuário, schema e migrations registrados; banco recriável e não compartilhado |
| **D06** | Rubrica, codebook, plano de análise e instrumentos das duas passagens | Artefatos completos, revisados e incluídos no manifesto |
| **D07** | Custodiante, painel e adjudicadores | Pessoas designadas, papéis separados e treinamento documentado |
| **D08** | Pools de smoke, calibração e teste | Casos sob custódia, deduplicados e conjunto de teste selado |
| **D09** | Freeze externo | Recibo externo obtido e verificado criptograficamente |

O registro acrescenta uma restrição própria: até D01 fechar, nenhuma alegação
de generalização entre capacidades de modelo é autorizada. Um resultado obtido
com um modelo não pode ser apresentado como resultado do sistema.

Estado atual dos braços: apenas o A8 tem implementação, e ela cobre a
integração técnica, não a avaliação jurídica. O A8 automatiza decisões de
operador e por isso recusa execução fora do pool de smoke. Os outros nove
braços automatizados não têm implementação. O comparador humano não tem fluxo.

---

## O que falta para produzir o primeiro resultado

Em ordem, do mais barato ao mais caro:

1. **Fechar o pacote de pré-registro.** Decidir D01, o desenho experimental.
   É a decisão que trava as demais.
2. **Implementar os braços A0 a A9.** Cada um com script revisado contra a
   definição literal do protocolo, e hash congelado.
3. **Desenhar o fluxo humano do A10.** Instrução, formulário, critério de
   seleção da subamostra e cadeia de custódia.
4. **Provisionar o banco experimental isolado.** Separado do banco de produto,
   recriável, não compartilhado.
5. **Designar as pessoas.** Custodiante, painel e adjudicadores, com papéis
   separados e treinamento registrado. O custodiante não pode ser o executor.
6. **Constituir os pools.** Casos sob custódia, deduplicados, com o conjunto de
   teste selado antes de qualquer execução.
7. **Obter o timestamp externo.** Recibo de terceiro, verificado
   criptograficamente. Antes disso o pré-registro não é demonstrável a ninguém.
8. **Rodar o smoke técnico** com três a cinco casos fictícios, que testa
   infraestrutura e não estima eficácia jurídica.
9. **Rodar o piloto de calibração**, fora do conjunto final.
10. **Rodar o teste comparativo** conforme o protocolo.

Só depois do item 10 existe uma estimativa experimental da API. Antes disso,
permanecem as métricas da operação anterior, com alcance contextual e sem
atribuição causal à implementação backend.

---

## Por que ainda não existe estimativa experimental da API

Porque validação operacional e avaliação experimental respondem a perguntas
diferentes.

A governança direta do método produziu evidência de uso, viabilidade, falhas e
refinamento em ambiente real. Ela não isola, por si só, causalidade,
generalização ou desempenho comparativo da nova API. Para responder a essas
perguntas, o desenho formal prevê cegamento, protocolo, custódia separada e
conjunto de teste selado.

A arquitetura de avaliação foi montada exatamente para tornar isso impossível
de acontecer por acidente. O gate está desabilitado. O caso é consumido antes
de ser lido. O mapa de cegamento tem chave própria, que não deriva da frase do
cofre do produto e idealmente fica com outra pessoa. A ordem dos braços é
permutada por caso. Falha de braço marca a execução e impede o cegamento.

O sistema de avaliação foi construído para impedir que evidência operacional
seja convertida automaticamente em alegação causal.

---

## O que dizer quando perguntarem "e funciona?"

A resposta honesta tem três partes:

1. **O que foi validado operacionalmente.** O método ATRIO foi utilizado,
   acompanhado e refinado em fluxo jurídico real, sob governança humana direta.
2. **O que está verificado em engenharia.** A suíte atual registra 175 testes
   aprovados. O pacote histórico de 169 testes preserva evidência exportada do
   Git e hashes do estado anterior.
3. **O que a avaliação formal ainda estabelecerá.** O protocolo está em
   fechamento e seus resultados ainda não integram esta baseline. Até a
   incorporação das evidências, as métricas operacionais não são apresentadas
   como estimativas causais da API.

As decisões D01 a D09 registram as condições necessárias para executar essa
terceira etapa com alcance definido.
