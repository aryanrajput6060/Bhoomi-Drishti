# Enumerates every launchable Start Menu application (Win32 + UWP/Store apps).
# Returns JSON: [ { name, appId, kind } ]
[CmdletBinding()]
param()

$ErrorActionPreference = 'SilentlyContinue'
$apps = @()

foreach ($app in (Get-StartApps)) {
    if ([string]::IsNullOrWhiteSpace($app.Name)) { continue }
    $apps += [pscustomobject]@{
        name  = $app.Name
        appId = $app.AppID
        kind  = 'startapp'
    }
}

$shortcutRoots = @(
    (Join-Path $env:ProgramData 'Microsoft\Windows\Start Menu\Programs'),
    (Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs')
)

foreach ($root in $shortcutRoots) {
    if (-not (Test-Path -LiteralPath $root)) { continue }
    foreach ($item in (Get-ChildItem -LiteralPath $root -Recurse -Include *.lnk, *.url -ErrorAction SilentlyContinue)) {
        $apps += [pscustomobject]@{
            name  = [System.IO.Path]::GetFileNameWithoutExtension($item.Name)
            appId = $item.FullName
            kind  = 'shortcut'
        }
    }
}

ConvertTo-Json -InputObject @($apps) -Depth 3 -Compress