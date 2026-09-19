# Captures the screen (or a single display) to a PNG file.
# Monitor: 0 = all displays stitched together, 1 = primary, 2..n = display index.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Path,
    [int]$Monitor = 0
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

if ($Monitor -le 0) {
    $bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
}
else {
    $screens = [System.Windows.Forms.Screen]::AllScreens
    if ($Monitor -eq 1) {
        $target = $screens | Where-Object { $_.Primary } | Select-Object -First 1
    }
    elseif ($Monitor -le $screens.Count) {
        $target = $screens[$Monitor - 1]
    }
    else {
        $target = $screens | Where-Object { $_.Primary } | Select-Object -First 1
    }
    $bounds = $target.Bounds
}

$directory = Split-Path -Parent $Path
if ($directory -and -not (Test-Path -LiteralPath $directory)) {
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
}

$bitmap = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
try {
    $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
}
finally {
    $graphics.Dispose()
}

try {
    $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
}
finally {
    $bitmap.Dispose()
}

[pscustomobject]@{
    path   = (Resolve-Path -LiteralPath $Path).Path
    width  = $bounds.Width
    height = $bounds.Height
    bytes  = (Get-Item -LiteralPath $Path).Length
} | ConvertTo-Json -Compress
