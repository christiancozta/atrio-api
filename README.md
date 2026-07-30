# ATRIO API

[![tests](https://github.com/christiancozta/atrio-api/actions/workflows/tests.yml/badge.svg)](https://github.com/christiancozta/atrio-api/actions/workflows/tests.yml)

Método governado de produção jurídica, formalizado como uma API local,
versionada e verificável.

## Em uma frase

A ATRIO API organiza o caminho entre documentos e peça final sem entregar ao
modelo a decisão sobre quando o trabalho pode avançar.

```text
CORPUS → RATIO/TROIA → CERNE → LUX
```

- **CORPUS** recebe, protege, extrai e pseudonimiza os documentos.
- **RATIO/TROIA** estrutura o raciocínio e o submete a testes contrafactuais.
- **CERNE** confronta a formulação e emite um gate técnico.
- **LUX** refina a forma e aplica a política de anonimização da saída.

Nas transições críticas, o sistema para. O avanço depende de uma decisão
humana identificada e registrada.

## Do método à API

O ATRIO existia antes deste backend. Seu método foi aplicado e refinado em
fluxo jurídico real por meio de plataformas de IA generativa, com supervisão
humana direta, revisão individual dos resultados, definição de padrões,
incorporação de críticas e extração de indicadores.

A API transforma essa operação em infraestrutura: contratos tipados,
persistência PostgreSQL, máquina de estados, idempotência, controle de versão,
proteção de dados, proveniência e testes automatizados.

O princípio permanece o mesmo:

> O modelo formula. A regra governa. O operador decide.

## O que está implementado

- aplicação FastAPI com 23 caminhos sob `/v1`;
- execução local, com banco, cofre e inferência na própria máquina;
- ingestão de TXT, DOCX e PDF, com OCR local;
- cofre AES-256-GCM e pseudonimização reversível;
- fluxo persistido entre CORPUS, RATIO/TROIA, CERNE e LUX;
- conferência final, retorno ao LUX e liberação pela API;
- revisão humana obrigatória nos pontos sensíveis;
- versões e hashes registrados em releases, artefatos, comandos e eventos;
- contrato OpenAPI 3.1.0 exportado da aplicação.

## Evidências

O projeto separa três tipos de evidência:

1. **Operação:** o método ATRIO foi utilizado e refinado em ambiente jurídico
   real antes da implementação da API.
2. **Engenharia:** a suíte automatizada registra 175 testes aprovados, sem
   falhas, erros ou testes pulados.
3. **Avaliação formal da API:** o protocolo está em fechamento e seus
   resultados serão incorporados com registro próprio.

Essa separação preserva o alcance de cada afirmação sem apagar o histórico
operacional que originou o sistema.

## Estado atual

- API: `0.7.0`
- schema PostgreSQL: `1.3.0`
- release técnica pública: `0.7.0`
- finalidade: ativo técnico autoral, demonstrativo e não comercial

O fluxo atual percorre os quatro módulos e alcança a liberação final pela API.
Os termos de uso estão fixados no
[LICENSE](LICENSE): código público para leitura e
avaliação, com todos os direitos reservados.

## Onde começar

- [Visão geral e diagrama](docs/apresentacao/LEIA-PRIMEIRO.md)
- [Resumo de uma página](docs/apresentacao/UMA-PAGINA.md)
- [Arquitetura](docs/apresentacao/ARQUITETURA.md)
- [Documentação técnica da API](docs/api/README.md)
- [Contrato OpenAPI](docs/api/openapi.json)
- [Código da API](packages/services/atrio_api)
- [Apresentação pública do ATRIO](https://christiancozta.github.io/arco.html)

Para instalar e executar localmente, consulte o
[guia de operação](docs/api/OPERACAO.md).
