# Registro de emendas

## Emenda 01 — proteção pré-dados

**Status:** incorporada ao pacote canônico antes da coleta; ainda não submetida
a pré-registro ou timestamp externo.

**Dados experimentais observados antes da alteração:** nenhum. O caso fictício
`smoke_ri_001` foi apenas cadastrado e não executado.

### Alterações

1. **Separação entre smoke e piloto de calibração.** O smoke usa 3–5 casos
   fictícios e testa apenas infraestrutura. O piloto de calibração conserva a
   função e a amostra definidas no protocolo. Casos expostos em qualquer dos
   dois nunca entram no conjunto final.
2. **Gold fechado antes da decisão original.** O painel fecha e assina por hash
   o conjunto de resultados admissíveis, erros e omissões antes de qualquer
   integrante ter acesso à decisão judicial original. Só depois a decisão
   original entra, cega, como candidata submetida aos mesmos critérios.
3. **Duas passagens humanas irreversíveis.** A passagem 1 é encerrada e
   congelada antes da abertura dos materiais reservados à passagem 2. Não é
   permitido voltar à passagem 1, editar seus registros ou recalibrar notas
   depois da exposição.
4. **Permutação independente dos rótulos por caso.** Ordem, identificadores e
   associação entre output e braço são sorteados novamente em cada caso. O mapa
   permanece em custódia separada e não integra o pacote do avaliador.

### Motivo

Correção de riscos metodológicos identificados antes da execução: mistura entre
teste de instrumentação e calibração, contaminação temporal do padrão de
referência, revisão retrospectiva de julgamento e aprendizado da identidade dos
braços por rótulos estáveis.

### Efeito normativo

Esta emenda complementa o protocolo 1.0 sem renomeá-lo. Em conflito, a emenda
prevalece somente nos quatro pontos acima. Qualquer mudança futura em hipótese,
braço, desfecho, limiar, exclusão, severidade, amostra ou análise exige nova
emenda explícita antes de exposição a dados.
