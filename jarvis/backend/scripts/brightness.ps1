# Reads or sets display brightness through WMI (WmiMonitorBrightness).
# Laptop panels support this; most external monitors do not — the script reports
# that honestly instead of pretending the change happened.
# Usage: brightness.ps1 -Json            -> read
#        brightness.ps1 -Level 60       -> set to 60%
[CmdletBinding()]
param(
    [int]$Level = -1,
    [switch]$Json
)

$ErrorActionPreference = 'Stop'

function Get-Brightness {
    (Get-CimInstance -Namespace 'root/WMI' -ClassName 'WmiMonitorBrightness' -ErrorAction Stop |
        Select-Object -First 1).CurrentBrightness
}

$supported = $true
try {
    $null = Get-Brightness
}
catch [Microsoft.Management.Infrastructure.CimException] {
    $supported = $false
}
catch {
    $supported = $false
}

if (-not $supported) {
    [pscustomobject]@{
        supported = $false
        level     = $null
        message   = "This display does not expose brightness control through WMI (typical for external monitors)."
    } | ConvertTo-Json -Compress
    exit 0
}

if ($Level -ge 0) {
    $methods = Get-CimInstance -Namespace 'root/WMI' -ClassName 'WmiMonitorBrightnessMethods' -ErrorAction Stop
    foreach ($method in $methods) {
        $null = Invoke-CimMethod -InputObject $method -MethodName 'WmiSetBrightness' -Arguments @{
            Timeout   = [uint32]0
            Brightness = [byte]([Math]::Max(0, [Math]::Min(100, $Level)))
        }
    }
}

[pscustomobject]@{
    supported = $true
    level     = (Get-Brightness)
    message   = ""
} | ConvertTo-Json -Compress