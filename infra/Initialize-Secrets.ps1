[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$secretRoot = Join-Path $PSScriptRoot 'secrets'
$databaseSecret = Join-Path $secretRoot 'atrio_db_password.txt'
$vaultSecret = Join-Path $secretRoot 'atrio_vault_passphrase.txt'

New-Item -ItemType Directory -Path $secretRoot -Force | Out-Null

function Write-Utf8Secret {
    param(
        [Parameter(Mandatory)]
        [string]$Path,
        [Parameter(Mandatory)]
        [string]$Value
    )

    if ((Test-Path -LiteralPath $Path) -and -not $Force) {
        throw "Segredo já existe: $Path. Use -Force somente para rotação planejada."
    }

    [System.IO.File]::WriteAllText(
        $Path,
        $Value,
        [System.Text.UTF8Encoding]::new($false)
    )
}

$randomBytes = [byte[]]::new(32)
[System.Security.Cryptography.RandomNumberGenerator]::Fill($randomBytes)
$databasePassword = [Convert]::ToBase64String($randomBytes)
[Array]::Clear($randomBytes, 0, $randomBytes.Length)

$first = Read-Host 'Defina a frase secreta do cofre ATRIO' -AsSecureString
$second = Read-Host 'Confirme a frase secreta do cofre ATRIO' -AsSecureString
$firstPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($first)
$secondPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($second)

try {
    $vaultPassphrase = [Runtime.InteropServices.Marshal]::PtrToStringBSTR(
        $firstPointer
    )
    $confirmation = [Runtime.InteropServices.Marshal]::PtrToStringBSTR(
        $secondPointer
    )
    if ($vaultPassphrase -cne $confirmation) {
        throw 'As frases secretas do cofre não coincidem.'
    }
    if ($vaultPassphrase.Length -lt 16) {
        throw 'A frase secreta do cofre deve possuir ao menos 16 caracteres.'
    }

    Write-Utf8Secret -Path $databaseSecret -Value $databasePassword
    Write-Utf8Secret -Path $vaultSecret -Value $vaultPassphrase
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($firstPointer)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($secondPointer)
    $databasePassword = $null
    $vaultPassphrase = $null
    $confirmation = $null
}

Write-Host "Segredos criados em $secretRoot."
Write-Host 'Guarde uma cópia offline da frase do cofre; ela não é recuperável.'
