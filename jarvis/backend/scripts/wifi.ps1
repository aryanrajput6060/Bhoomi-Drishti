# Wi-Fi adapter status and on/off control.
# Changing the adapter state requires an elevated (Administrator) shell; the
# script reports that clearly instead of silently failing.
# Usage: wifi.ps1 -Action status | wifi.ps1 -Action off | wifi.ps1 -Action on
[CmdletBinding()]
param(
    [ValidateSet('status', 'on', 'off')]
    [string]$Action = 'status'
)

$ErrorActionPreference = 'Continue'

function Get-WifiAdapter {
    $adapters = Get-NetAdapter -ErrorAction SilentlyContinue |
        Where-Object { $_.PhysicalMediaType -like '*802.11*' -or $_.Name -match 'Wi-?Fi|Wireless|WLAN' }
    return $adapters | Select-Object -First 1
}

$adapter = Get-WifiAdapter
$interfaceName = if ($adapter) { $adapter.Name } else { '' }

if ($Action -ne 'status') {
    if (-not $interfaceName) {
        [pscustomobject]@{ ok = $false; message = 'No Wi-Fi adapter was found on this machine.' } | ConvertTo-Json -Compress
        exit 0
    }
    $target = if ($Action -eq 'on') { 'enabled' } else { 'disabled' }
    $output = & netsh interface set interface name="$interfaceName" admin=$target 2>&1 | Out-String
    $adapter = Get-WifiAdapter
    [pscustomobject]@{
        ok      = ($adapter.Status -ne 'Disabled') -eq ($Action -eq 'on')
        action  = $Action
        adapter = $interfaceName
        status  = if ($adapter) { $adapter.Status } else { 'unknown' }
        output  = $output.Trim()
        message = if ($output -match 'elevat|Access is denied') { 'Administrator privileges are required to change the Wi-Fi adapter state.' } else { '' }
    } | ConvertTo-Json -Compress
    exit 0
}

$signal = $null
$ssid = ''
$state = 'unknown'
if ($interfaceName) {
    $state = (Get-WifiAdapter).Status
    $wlan = & netsh wlan show interfaces 2>&1 | Out-String
    $ssidMatch = [regex]::Match($wlan, 'SSID\s*:\s*(.+)')
    if ($ssidMatch.Success) { $ssid = $ssidMatch.Groups[1].Value.Trim() }
    $signalMatch = [regex]::Match($wlan, 'Signal\s*:\s*(\d+)%')
    if ($signalMatch.Success) { $signal = [int]$signalMatch.Groups[1].Value }
}

[pscustomobject]@{
    ok      = $true
    adapter = $interfaceName
    status  = $state
    ssid    = $ssid
    signal  = $signal
    message = ''
} | ConvertTo-Json -Compress