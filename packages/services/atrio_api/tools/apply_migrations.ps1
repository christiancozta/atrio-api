[CmdletBinding()]
param(
    [string]$DatabaseHost = '127.0.0.1',
    [ValidateRange(1, 65535)]
    [int]$DatabasePort = 5432,
    [string]$DatabaseName = 'atrio',
    [string]$DatabaseUser = 'atrio_app'
)

$ErrorActionPreference = 'Stop'
$env:PGCLIENTENCODING = 'UTF8'

$migrationsRoot = Join-Path (
    Split-Path -Parent $PSScriptRoot
) 'migrations'

if (-not (Test-Path -LiteralPath $migrationsRoot -PathType Container)) {
    throw "Diretorio de migracoes nao encontrado: $migrationsRoot"
}

$migrationPaths = Get-ChildItem `
    -LiteralPath $migrationsRoot `
    -Filter '*.sql' `
    -File |
    Sort-Object Name

if ($migrationPaths.Count -eq 0) {
    throw "Nenhuma migracao encontrada em: $migrationsRoot"
}

$psqlCommand = Get-Command 'psql.exe' -ErrorAction SilentlyContinue
if ($null -ne $psqlCommand) {
    $psqlPath = $psqlCommand.Source
}
else {
    $postgresRoot = 'C:\Program Files\PostgreSQL'
    if (-not (Test-Path -LiteralPath $postgresRoot -PathType Container)) {
        throw 'PostgreSQL nao foi localizado em C:\Program Files\PostgreSQL.'
    }

    $installation = Get-ChildItem -LiteralPath $postgresRoot -Directory |
        Where-Object { $_.Name -match '^\d+$' } |
        Sort-Object { [int]$_.Name } -Descending |
        Select-Object -First 1

    if ($null -eq $installation) {
        throw 'PostgreSQL nao foi localizado em C:\Program Files\PostgreSQL.'
    }

    $psqlPath = Join-Path $installation.FullName 'bin\psql.exe'
}

if (-not (Test-Path -LiteralPath $psqlPath -PathType Leaf)) {
    throw "psql.exe nao encontrado: $psqlPath"
}

Write-Host "Banco: $DatabaseUser@$DatabaseHost`:$DatabasePort/$DatabaseName"
Write-Host "Migracoes localizadas: $($migrationPaths.Count)"

foreach ($migrationPath in $migrationPaths) {
    $migrationFullPath = $migrationPath.FullName
    $checksum = (
        Get-FileHash -LiteralPath $migrationFullPath -Algorithm SHA256
    ).Hash.ToLowerInvariant()

    Write-Host "Migracao: $($migrationPath.Name)"
    Write-Host "SHA-256: $checksum"

    & $psqlPath `
        --host=$DatabaseHost `
        --port=$DatabasePort `
        --username=$DatabaseUser `
        --dbname=$DatabaseName `
        --set=ON_ERROR_STOP=1 `
        --set="migration_checksum=$checksum" `
        --file="$migrationFullPath"

    if ($LASTEXITCODE -ne 0) {
        throw (
            "A migracao $($migrationPath.Name) falhou " +
            "com codigo $LASTEXITCODE."
        )
    }
}

Write-Host 'Todas as migracoes foram concluidas e verificadas.'
