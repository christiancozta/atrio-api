# Demonstração

Roteiro de dez minutos para apresentar o ATRIO em tela compartilhada.

Premissa do roteiro: o método ATRIO já operou em ambiente jurídico real, sob
governança humana direta. A demonstração apresenta sua formalização como API
local, o fluxo governado e as evidências de engenharia.

---

## Antes de começar

Abrir e deixar pronto, em abas separadas:

1. <https://christiancozta.github.io/arco.html>, na seção ATRIO
2. `docs/apresentacao/LEIA-PRIMEIRO.md`, no diagrama Mermaid
3. `http://127.0.0.1:8080/v1/health/ready` (API local no ar)
4. `http://127.0.0.1:8080/docs`
5. `VERSIONS.yaml`
6. `.../evaluation/evidence/dfd509e/evidence_manifest.json`

Fechar tudo o mais. Se a API não estiver no ar, o roteiro funciona igual com o
`openapi.json` estático e as capturas.

---

## Minuto 0 a 1: origem e proposta

**Abrir:** a seção ATRIO da apresentação pública.

**Dizer:**

> O ATRIO nasceu em operação jurídica real e foi aplicado por meio de
> plataformas online de IA, sob revisão humana direta. O que esta demonstração
> apresenta é a formalização desse método como API local: quatro etapas
> governadas, persistência, rastreabilidade e controle humano sobre cada
> transição crítica.

O objetivo desta abertura é estabelecer continuidade: primeiro existiu o
método em operação; depois veio sua formalização em software.

---

## Minuto 1 a 3: o fluxo

**Abrir:** o diagrama Mermaid em `LEIA-PRIMEIRO.md`.

**Dizer:** percorrer as quatro caixas em vinte segundos cada, e depois parar
nas três caixas destacadas.

> Documento entra, é cifrado e inventariado. O protocolo decisório conduz o
> raciocínio por fases nomeadas, específicas por tipo de peça. A auditoria
> confronta o resultado antes do acabamento. O acabamento ajusta o texto e
> aplica anonimização.
>
> As três caixas destacadas são onde o sistema para e espera uma pessoa. Não é
> tratamento de erro. É o desenho: o modelo formula, a regra governa e o
> operador decide.

**Não abrir:** o código. Ninguém aqui vai ler Python.

---

## Minuto 3 a 5: por que é governado

**Abrir:** `VERSIONS.yaml`.

**Dizer:**

> Cada componente tem versão declarada em um único lugar. Quando um caso é
> criado, essa composição é fixada e viaja em toda resposta até o fim. Um caso
> aberto hoje termina com a mesma composição com que começou.
>
> Este identificador de release aqui termina em dois recortes de hash. Um é do
> manifesto de build, outro é do pacote normativo, os 52 arquivos que contêm as
> regras de RATIO, CERNE, LUX e detecção de dado pessoal. Se alguém mudar uma
> vírgula em qualquer um deles, o identificador muda. Seis meses depois, quando
> perguntarem com qual versão de qual regra aquela peça foi produzida, a
> resposta existe.

**Se houver tempo, abrir:** `/v1/health/ready` e mostrar o JSON com
`release_id`, `database_schema_version` e as versões de pipeline.

---

## Minuto 5 a 7: onde a pessoa decide

**Abrir:** `/docs`, rolar até as rotas de `cerne` e `ratio/actions`.

**Dizer:**

> O CERNE devolve um de cinco vereditos. Três deles param o caso e não têm
> saída automática. Para sair, alguém precisa devolver ao RATIO ou reabrir o
> bloqueio, com código de catálogo e nome. Não existe botão de seguir assim
> mesmo.
>
> No RATIO, o avanço de fase é sempre ação de operador, com nome e número de
> revisão. O modelo produz o conteúdo da fase. Ele não valida a fase e não
> decide avançar.
>
> Tudo isso vira evento na trilha: sequência, comando, estágio de origem,
> estágio de destino, componente, versão, ator, carimbo de tempo. Sem conteúdo
> jurídico. A trilha de auditoria não é uma segunda cópia do processo.

**Não abrir:** documento ou conteúdo de caso real. Esse material é protegido e
não integra uma demonstração pública.

---

## Minuto 7 a 8: o que está verificado

**Abrir:** `evidence_manifest.json`.

**Dizer:**

> 175 testes automatizados, zero falhas, zero erros, zero pulados. A suíte
> foi exportada direto do Git, com JUnit, tarball da fonte, hash de cada
> artefato, ambiente e lista de dependências com versão fixa.
>
> Essa suíte verifica os contratos, estados, gates, persistência e falhas
> previstas da implementação. Ela se soma à validação operacional anterior do
> método.

---

## Minuto 8 a 10: por que isso não é apenas uma camada sobre o modelo

**Abrir:** a tabela de versões ou o OpenAPI.

**Dizer:**

> O modelo é uma dependência intercambiável. O ativo está na cadeia governada:
> regras versionadas, pontos de decisão humana, persistência, proveniência,
> privacidade local e auditoria sem conteúdo jurídico.
>
> O ATRIO já operou como método. A API transforma essa operação em uma
> implementação reproduzível, inspecionável e testável. A avaliação formal da
> API está sendo fechada e terá evidências próprias.

**Encerrar com a ideia central:** não é uma conversa automatizada; é um fluxo
de produção governado.

---

## O que não abrir, em nenhuma hipótese

| Não abrir | Motivo |
|---|---|
| Código-fonte Python | Pode ser mostrado se houver interesse técnico, mas não é a abertura adequada para este roteiro de dez minutos |
| O diretório `infra/` da raiz do repositório | Cópia divergente e quebrada, documentada em `../api/OPERACAO.md` |
| Qualquer caso real | Conteúdo protegido e fora do escopo de uma demonstração pública |
| Arquivos de segredo, `.env` preenchido, frase do cofre | Óbvio, mas fácil de esquecer com a tela compartilhada |

---

## As três perguntas prováveis

### 1. "E funciona?"

> O método já funcionou em operação jurídica real, sob supervisão direta, e
> suas métricas estão documentadas. A API faz o que 175 testes automatizados
> verificam, com evidência exportada do Git e hashes. A avaliação formal da
> implementação atual acrescentará uma terceira camada de evidência, com
> registro próprio.

### 2. "Quanto tempo economiza?"

> Existem métricas do período operacional do método. Uma medida comparável e
> atribuível à API atual será registrada na avaliação formal. Nesta
> demonstração, o ponto verificável é onde o sistema controla o trabalho:
> revisão de documento com sigilo ou OCR, validação de cada fase e tratamento
> dos bloqueios da auditoria.

### 3. "Isso não é só um wrapper de modelo de linguagem?"

> O modelo produz texto dentro de uma fase. Ele não escolhe a fase, não valida
> a fase, não decide avançar, não emite o veredicto da auditoria e não escolhe
> o modo de anonimização da saída. Toda decisão de avanço é ação de operador
> registrada com nome e versão.
>
> O que está sob controle de versão aqui não é o modelo, que é intercambiável.
> É a base normativa: 52 arquivos com hash verificado, que definem as fases de
> cada tipo de peça, os gatilhos do teste contrafactual, os eixos da auditoria
> e a política de anonimização. Troque o modelo e a governança continua igual.
> Mude uma vírgula na base normativa e o identificador da release muda.

---

## Se a demonstração ao vivo falhar

Ordem de recuo, cada passo custa menos que o anterior:

1. A API não sobe: usar `docs/api/openapi.json` e a lista de rotas em
   `ENDPOINTS.md`.
2. Nada abre: usar o diagrama de `LEIA-PRIMEIRO.md` e a tabela de versões.
3. Sem tela: `UMA-PAGINA.md` cobre a conversa inteira em voz.

O OpenAPI, o diagrama e as evidências preservam a apresentação mesmo sem a
execução ao vivo. Não improvisar métricas para compensar uma falha de ambiente.
