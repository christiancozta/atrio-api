# CERNE — integração ATRIO

Este diretório incorpora a base operacional entregue no pacote CERNE API 0.2.0.

A integração preserva o motor de auditoria, os 11 eixos, confrontos, gates,
anti-banalização, sanitização e contratos de saída. O standalone Gemini/SQLite
não integra o runtime ATRIO: o provedor é adaptado ao Ollama governado e o
AuditResponse completo é armazenado apenas como artefato cifrado no cofre ATRIO.

Versões de release continuam distintas por contrato:

- módulo CERNE: 1.2.0
- service build CERNE: 0.2.0
- integração ATRIO/CERNE: 0.1.0
