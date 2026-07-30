[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$custodyRoot = Join-Path $PSScriptRoot '_custody'
$secretPath = Join-Path $custodyRoot 'secret.key'

if ((Test-Path -LiteralPath $secretPath) -and -not $Force) {
    throw 'A chave de custodia experimental ja existe.'
}

New-Item -ItemType Directory -Path $custodyRoot -Force | Out-Null
$secret = [byte[]]::new(32)
$rng = [Security.Cryptography.RandomNumberGenerator]::Create()
try {
    $rng.GetBytes($secret)
    [IO.File]::WriteAllBytes($secretPath, $secret)
}
finally {
    $rng.Dispose()
    [Array]::Clear($secret, 0, $secret.Length)
}

$identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$acl = Get-Acl -LiteralPath $secretPath
$acl.SetAccessRuleProtection($true, $false)
$rule = [Security.AccessControl.FileSystemAccessRule]::new(
    $identity,
    [Security.AccessControl.FileSystemRights]::FullControl,
    [Security.AccessControl.AccessControlType]::Allow
)
$acl.SetAccessRule($rule)
Set-Acl -LiteralPath $secretPath -AclObject $acl

Write-Host "Custodia experimental inicializada em: $secretPath"
Write-Host 'Esta chave e exclusiva do cegamento e nao abre o cofre CORPUS.'
