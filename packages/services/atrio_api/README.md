# ATRIO API

Implementação local, versionada e governada do método operacional ATRIO.

- **Versão da API:** `0.7.0`
- **Schema PostgreSQL:** `1.3.0`
- **Estado:** release técnica pública
- **Distribuição prevista:** repositório público de código-fonte

## Definição

A ATRIO API é o plano de controle que formaliza, em software, a cadeia:

```text
CORPUS → RATIO/TROIA → CERNE → LUX
```

Sua função é coordenar documentos, estados, comandos, revisões humanas,
artefatos e versões ao longo dessa cadeia. A API não decide matéria jurídica e
não delega ao modelo a autoridade para avançar entre etapas sensíveis.

O ATRIO é anterior a esta implementação. Antes de existir como backend, seu
método modular foi aplicado em ambiente real de trabalho jurídico por meio de
plataformas online de IA generativa. A operação era conduzida sob supervisão
humana direta, com análise individual de resultados, definição de padrões,
incorporação de críticas, extração de indicadores e revisão iterativa dos
módulos.

A API traduz esse método para uma infraestrutura local e reproduzível. Essa
transição acrescenta contratos tipados, persistência, máquina de estados,
idempotência, proteção de dados, proveniência e verificação automática sem
alterar o princípio central: o modelo formula; a regra governa; o operador
decide.

## O que a API é

- uma aplicação FastAPI de execução local;
- uma máquina de estados persistida em PostgreSQL;
- uma camada de coordenação para os quatro módulos do ATRIO;
- um registro de versões, comandos, eventos e referências de artefato;
- uma fronteira entre inferência de modelo e decisão operacional;
- uma implementação orientada a privacidade, rastreabilidade e revisão humana.

## O que a API não é

- um sistema autônomo de decisão jurídica;
- um substituto para revisão profissional;
- uma autorização para retirar documentos jurídicos do ambiente local;
- apenas um conjunto de prompts reunidos sob uma interface HTTP.

## Módulos

| Módulo | Responsabilidade |
|---|---|
| **CORPUS 1.5.0** | Receber, validar, extrair, inventariar, pseudonimizar e proteger documentos antes do uso por modelo |
| **RATIO 7.0.0** | Estruturar a formulação decisória em fases, com estados, hard stops e decisões expressas do operador |
| **TROIA 1.0.0** | Executar a camada obrigatória de risco dentro do fluxo governado do RATIO |
| **CERNE 1.2.0** | Confrontar criticamente a formulação, registrar achados e produzir gate técnico |
| **LUX 6.0.0** | Refinar forma, clareza e proteção da saída sem autorização para alterar o mérito |

Cada artefato declara produtor, versão do produtor, release e versão do schema.
Handoffs incompatíveis são recusados.

## Princípios de operação

1. **Autoridade humana.** Transições sensíveis exigem regra determinística ou
   decisão expressa do operador.
2. **Falha fechada.** Ausência de dependência, divergência de versão ou quebra
   de integridade bloqueia o avanço.
3. **Privacidade por desenho.** Originais e mapas reversíveis permanecem no
   cofre local cifrado. Eventos operacionais não recebem conteúdo jurídico.
4. **Proveniência.** Releases, artefatos, comandos e eventos carregam versões,
   identificadores e hashes.
5. **Idempotência.** Repetir a mesma operação não deve duplicar execução,
   documento ou efeito persistido.
6. **Separação de responsabilidades.** Inferência, regra de domínio,
   persistência e interface permanecem desacopladas.
7. **Sem fallback silencioso.** A edição local não envia dados a serviço de
   nuvem quando uma dependência local falha.

## Estado da implementação

A versão `0.7.0` oferece 23 caminhos sob `/v1` e uma console operacional local.
O núcleo atual inclui:

- criação idempotente de execução por tenant;
- release definida pelo servidor e fixada desde a criação;
- controle otimista de versão em toda mutação;
- persistência transacional PostgreSQL;
- entrada documental de até 50 MiB;
- validação de tipo, assinatura e integridade;
- cofre AES-256-GCM;
- extração local de TXT, DOCX e PDF;
- OCR local com Tesseract e Poppler;
- pseudonimização reversível com mapa cifrado separado;
- revisão humana obrigatória para OCR, sigilo e baixa qualidade;
- execução governada de RATIO/TROIA, CERNE e LUX;
- conferência final, retorno ao LUX e liberação pela API;
- adapter Ollama `0.2.0`, com opções congeladas, digest do modelo e hashes de
  proveniência;
- respostas de erro que não ecoam payload jurídico inválido;
- contrato OpenAPI 3.1.0 exportado da aplicação.

O schema `1.3.0` é composto por cinco migrations verificadas por SHA-256. A API
recusa readiness quando a versão ou o checksum do banco divergem do runtime.

## Evidências e alcance das afirmações

O projeto distingue três níveis de evidência:

| Nível | Objeto | Estado |
|---|---|---|
| **Validação operacional** | Método ATRIO aplicado e refinado em fluxo jurídico real, sob supervisão humana direta | Realizada na operação anterior à API |
| **Verificação de engenharia** | Contratos, estados, gates, persistência, integrações e falhas da implementação local | Suíte automatizada de 175 testes aprovados |
| **Avaliação experimental formal** | Causalidade, generalização e eficácia comparativa | Protocolo em fechamento; execução e evidências serão registradas em etapa própria |

As métricas operacionais descrevem o contexto em que o método foi utilizado.
Elas permanecem documentadas como evidência do método; os resultados da
avaliação formal da API serão incorporados em registro próprio.

## Escopo da versão 0.7.0

- o fluxo implementado percorre CORPUS, RATIO/TROIA, CERNE e LUX;
- a conferência final pode aprovar, bloquear, devolver ao LUX ou liberar a
  execução;
- as etapas de inferência exigem Ollama e um modelo local configurado;
- a execução foi desenhada para ambiente local e operação individual.

Detalhes de instalação, dependências e condições técnicas de entrega ficam no
[guia de operação](../../../docs/api/OPERACAO.md).

## Verificação

Na raiz do monorepo:

```powershell
& .\packages\services\atrio_api\.venv\Scripts\python.exe `
    -m pytest -q .\packages\services\atrio_api\tests
```

Resultado registrado:

```text
175 passed
```

Verificação do bundle normativo:

```powershell
& .\packages\services\atrio_api\.venv\Scripts\python.exe `
    .\tools\build_runtime_normative_manifest.py --check
```

O contrato OpenAPI entregue em `docs/api/openapi.json` deve permanecer
semanticamente idêntico ao schema exportado pela instância da aplicação.

## Execução local

Requisitos:

- Python `>=3.11`;
- PostgreSQL;
- Poppler e Tesseract com idiomas `por` e `eng`;
- Ollama e modelo local para as etapas de inferência.

Instalação do pacote:

```powershell
& .\packages\services\atrio_api\.venv\Scripts\python.exe `
    -m pip install -e .\packages\services\atrio_api
```

Aplicação das migrations:

```powershell
& .\packages\services\atrio_api\tools\apply_migrations.ps1
```

Inicialização com inferência local:

```powershell
& .\packages\services\atrio_api\.venv\Scripts\python.exe `
    .\packages\services\atrio_api\tools\run_api.py `
    --ollama-model qwen3:8b
```

Superfícies locais:

- console: `http://127.0.0.1:8080/`;
- liveness: `http://127.0.0.1:8080/v1/health/live`;
- readiness: `http://127.0.0.1:8080/v1/health/ready`;
- OpenAPI interativo: `http://127.0.0.1:8080/docs`.

`live` confirma que o processo responde. `ready` verifica banco, cofre e
ferramentas documentais. Quando a inferência está configurada, verifica também
o modelo e as bases normativas de CERNE e LUX.

## Documentação

- [Kit técnico da API](../../../docs/api/README.md)
- [Endpoints](../../../docs/api/ENDPOINTS.md)
- [Configuração](../../../docs/api/CONFIGURACAO.md)
- [Módulos e máquina de estados](../../../docs/api/MODULOS.md)
- [Operação](../../../docs/api/OPERACAO.md)
- [OpenAPI 3.1.0](../../../docs/api/openapi.json)
- [MASTER de versionamento](../../../VERSIONAMENTO.md)
- [Apresentação pública do ATRIO](https://christiancozta.github.io/arco.html)

## Posição de release

A ATRIO API é um ativo técnico autoral, demonstrativo e não comercial. Sua
publicação no GitHub apresenta a implementação, a arquitetura e as evidências
do projeto.

As condições de uso estão fixadas no arquivo
[LICENSE](../../../LICENSE): código público para leitura e avaliação, com
todos os direitos reservados.

A versão `0.7.0` corresponde à release técnica pública. O acompanhamento
detalhado permanece em
[VERSIONAMENTO.md](../../../VERSIONAMENTO.md) e no
[guia de operação](../../../docs/api/OPERACAO.md).
