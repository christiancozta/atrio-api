# Backup e restauração ATRIO 1.0.0

## Garantias

- backup recusado enquanto a API nativa estiver ativa;
- no modo container, a API é parada e reiniciada automaticamente;
- dump PostgreSQL custom e cópia exata do vault real;
- SHA-256 de cada arquivo;
- autenticação HMAC-SHA-256 do manifesto;
- nenhum conteúdo documental aparece no manifesto;
- nenhuma rotação ou exclusão automática;
- restauração nativa em banco temporário;
- banco e vault anteriores preservados para reversão.

O backup não substitui criptografia do disco. O vault já é cifrado, mas o dump
PostgreSQL contém metadados operacionais e deve permanecer em mídia protegida.

## Backup nativo no Windows

Encerre a API. Na raiz do monorepo:

```powershell
& .\packages\services\atrio_api\.venv\Scripts\python.exe `
    .\packages\services\atrio_api\tools\backup_atrio.py
```

Na primeira execução será criada:

`packages/services/atrio_api/var/backup-authentication.key`

Essa chave não integra o backup. Guarde uma cópia offline; sem ela não há como
autenticar o conjunto restaurado.

## Verificação sem restaurar

```powershell
& .\packages\services\atrio_api\.venv\Scripts\python.exe `
    .\packages\services\atrio_api\tools\verify_backup.py `
    .\_backups\atrio_AAAA...
```

## Restauração nativa reversível

Encerre a API e mantenha o PostgreSQL ativo:

```powershell
& .\packages\services\atrio_api\.venv\Scripts\python.exe `
    .\packages\services\atrio_api\tools\restore_atrio.py `
    .\_backups\atrio_AAAA...
```

A operação pede a senha administrativa do PostgreSQL, restaura primeiro em
banco temporário, confirma o schema `1.3.0` e só então realiza a troca.

O banco anterior recebe nome `atrio_pre_*`; o vault anterior recebe nome
`vault.pre.*`. Remova-os somente após iniciar a API e validar:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/v1/health/ready |
    ConvertTo-Json
```

## Containers

O backup aceita `--mode container` e usa os nomes fixos da infraestrutura
oficial. A restauração em volumes de container permanece bloqueada até que o
procedimento de troca de volume seja homologado em runtime real. Não adapte o
script nativo manualmente para apagar volumes.
