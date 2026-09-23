[CmdletBinding()]
param([string]$OutputDirectory = '')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Get-ContentHash([string]$FilePath) {
    $stream = [IO.File]::OpenRead($FilePath)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($algorithm.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() }
    finally { $stream.Dispose(); $algorithm.Dispose() }
}
$packageRoot = Split-Path $PSScriptRoot -Parent
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $packageRoot 'workbook'
}
$payloadPath = Join-Path $packageRoot 'payload\WorkbookPayload.json'
$payload = Get-Content -LiteralPath $payloadPath -Raw -Encoding UTF8 | ConvertFrom-Json
$expected = '6afb0ea4fe142210f3f62e29f1718fa9408c95eb9d99e9a61a05b56ec4d50e20'
if ($payload.schema -ne 1 -or $payload.file -cne 'KSD-R1_restored.xlsx' -or $payload.sha256 -cne $expected) {
    throw 'Unexpected payload identity.'
}
$bytes = [Convert]::FromBase64String($payload.base64)
$hasher = [System.Security.Cryptography.SHA256]::Create()
try { $actual = [BitConverter]::ToString($hasher.ComputeHash($bytes)).Replace('-', '').ToLowerInvariant() }
finally { $hasher.Dispose() }
if ($actual -cne $expected -or $bytes.Length -ne $payload.bytes) { throw 'Payload verification failed.' }
$outputRoot = [IO.Path]::GetFullPath($OutputDirectory)
$target = Join-Path $outputRoot 'KSD-R1_restored.xlsx'
if (Test-Path -LiteralPath $target) {
    if ((Get-ContentHash $target) -cne $expected) {
        throw 'Existing workbook differs. Refusing to overwrite it.'
    }
    Write-Output ('PASS_EXISTING: ' + $target)
    exit 0
}
[void][IO.Directory]::CreateDirectory($outputRoot)
$temporary = Join-Path $outputRoot ('.ksd-restore-' + [Guid]::NewGuid().ToString('N') + '.tmp')
try {
    [IO.File]::WriteAllBytes($temporary, $bytes)
    if ((Get-ContentHash $temporary) -cne $expected) {
        throw 'Restored file verification failed.'
    }
    [IO.File]::Move($temporary, $target)
    Write-Output ('PASS_RESTORED: ' + $target)
}
finally { if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force } }
