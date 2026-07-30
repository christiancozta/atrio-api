# ATRIO

Sistema local de produção de peça jurídica em quatro etapas governadas, com
parada humana obrigatória em cada transição crítica e trilha de auditoria sem
conteúdo jurídico.

---

**O fluxo.** CORPUS recebe os documentos, cifra no cofre local, extrai texto
com OCR quando necessário, detecta dado pessoal, pseudonimiza de forma
reversível e monta um inventário sem conteúdo. RATIO conduz o raciocínio por
fases nomeadas, específicas para recurso inominado, embargos de declaração ou
mandado de segurança, com o teste contrafactual TROIA em posição definida por
tipo de peça. CERNE confronta o resultado contra uma base normativa de onze
eixos e devolve um de cinco vereditos. LUX ajusta o texto e aplica a política
de anonimização da saída.

**Onde a pessoa decide.** O sistema para e espera decisão registrada em cinco
momentos: documento com indício de sigilo, com OCR ou com texto abaixo do
mínimo; cada fase do RATIO, por ação de operador entre oito possíveis;
configuração do teste contrafactual nos embargos; gate do CERNE em revisão ou
bloqueio, que exige código de catálogo para sair; e a escolha do modo de dado
no acabamento. Nenhuma dessas paradas é limitação contornável. Cada uma é uma
escolha sobre onde a responsabilidade profissional precisa aparecer no
registro.

**Governança de versão.** A composição de versões é fixada quando o caso é
criado e viaja em toda resposta até o fim. O identificador da release deriva do
digest de 52 arquivos normativos. Se qualquer regra de RATIO, CERNE, LUX ou
detecção de dado pessoal mudar, o identificador muda. A pergunta "com qual
versão de qual regra esta peça foi produzida" tem resposta meses depois.

**Local.** Banco, cofre, modelo e API rodam em máquina local. A API é servida
apenas em `127.0.0.1`. O adapter de inferência ignora proxies do ambiente.
Documento jurídico não sai da máquina. Não há dependência de nuvem em nenhuma
etapa.

**Determinismo.** Toda chamada ao modelo fixa temperatura zero, semente fixa,
janela de contexto e teto de geração. Antes de chamar, um limite conservador
recusa localmente o que não caberia com folga. Depois de receber, a telemetria
de tokens é obrigatória e resposta truncada é descartada. Cada inferência
registra o digest do modelo e os hashes de entrada, saída e parâmetros.

---

## Evidências

**Validado operacionalmente.** O método ATRIO já foi aplicado e refinado em
fluxo jurídico real, sob supervisão humana direta. Houve revisão individual de
resultados, definição de padrões, incorporação de críticas e extração de
indicadores. Essas métricas são evidência operacional contextual.

**Verificado em engenharia.** 175 testes automatizados passam, com 0 falhas, 0
erros e 0 pulados. A evidência inclui código-fonte, JUnit, ambiente,
dependências e hashes dos artefatos.

---

## Avaliação formal

O protocolo de avaliação da API está em fechamento. Quando essa etapa for
executada, seus resultados serão incorporados com evidências próprias. Até lá,
as métricas anteriores descrevem a operação observada do método ATRIO, sem
serem atribuídas automaticamente ao backend atual.

## Estado da API

A versão `0.7.0` percorre CORPUS, RATIO/TROIA, CERNE e LUX, com persistência,
controle de versão e trilha de auditoria. A conferência final pode aprovar,
bloquear, devolver ao LUX ou registrar a liberação.

Documentação completa: kit de integração técnica em `docs/api/`, kit de
apresentação em `docs/apresentacao/` e apresentação pública em
<https://christiancozta.github.io/arco.html>.
