# Clipboard read/append. Usage: clipboard.ps1 -Json   |   clipboard.ps1 -Set "text"
#                                   clipboard.ps1 -Append "text"
[CmdletBinding()]
param(
    [string]$Set = "",
    [string]$Append = "",
    [switch]$Json
)

$ErrorActionPreference = 'Stop'

if ($PSBoundParameters.ContainsKey('Set')) {
    Set-Clipboard -Value $Set
    Write-Output "OK"
    exit 0
}

if ($PSBoundParameters.ContainsKey('Append')) {
    $existing = ""
    try { $existing = Get-Clipboard -Raw -ErrorAction Stop } catch { $existing = "" }
    Set-Clipboard -Value ($existing + $Append)
    Write-Output "OK"
    exit 0
}

$text = ""
$hasText = $true
try {
    $text = Get-Clipboard -Raw -ErrorAction Stop
    if ($null -eq $text) { $text = "" }
}
catch {
    $hasText = $false
}

if ($Json) {
    [pscustomobject]@{
        text    = [string]$text
        hasText = $hasText
        length  = ([string]$text).Length
    } | ConvertTo-Json -Compress
}
else {
    Write-Output ([string]$text)
}