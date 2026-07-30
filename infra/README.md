# ATRIO Infra 1.0.0

Infraestrutura local, gratuita e mínima:

- PostgreSQL `18.4`;
- ATRIO API `0.7.0`;
- Ollama `0.32.4`.

Temporal não integra esta versão. A máquina de estados persistida no
PostgreSQL permanece a única autoridade da execução.

## Segurança

O build usa uma `.dockerignore` por allowlist. Documentos, vault, ambientes
virtuais e backups não entram no contexto enviado ao runtime.

Senhas não ficam no `.env`. O Compose monta dois arquivos locais em
`/run/secrets`; `infra/secrets/*.txt` é ignorado pelo Git.

Os arquivos de segredo são material sigiloso em disco. Proteja a conta do
Windows e mantenha a frase do vault também em meio offline.

## Inicialização no Windows

Na raiz do monorepo:

```powershell
Copy-Item .\infra\.env.example .\infra\.env
& .\infra\Initialize-Secrets.ps1

docker compose `
    --env-file .\infra\.env `
    -f .\infra\compose.yaml `
    config

docker compose `
    --env-file .\infra\.env `
    -f .\infra\compose.yaml `
    up --build -d
```

Com Podman, use os comandos equivalentes de `podman compose`.

Se a API ou o Ollama nativos estiverem ativos, encerre-os ou altere
`ATRIO_API_PORT` e `OLLAMA_PORT` no `.env`.

## Modelo

O modelo não é baixado silenciosamente. Após o Ollama ficar saudável:

```powershell
$model = (
    Get-Content .\infra\.env |
    Where-Object { $_ -like 'OLLAMA_MODEL=*' }
) -replace '^OLLAMA_MODEL=', ''

docker compose `
    --env-file .\infra\.env `
    -f .\infra\compose.yaml `
    exec ollama ollama pull $model
```

O adapter registra o nome e o digest retornados pelo Ollama em cada inferência.

## Verificação

```powershell
Invoke-RestMethod http://127.0.0.1:8080/v1/health/ready |
    ConvertTo-Json
```

O resultado esperado declara API `0.7.0`, schema PostgreSQL `1.3.0` e uma
release iniciada por `atrio-local-0.7.0-`.

## Operações destrutivas

Não use `compose down -v` como comando cotidiano: ele remove os volumes do
banco, vault e modelos. Backup autenticado deve anteceder qualquer remoção.
