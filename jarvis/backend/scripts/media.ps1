# Reads and controls the system media session (Spotify, browsers, Groove, VLC …)
# through Windows.Media.Control — the same API the volume flyout uses.
# Usage: media.ps1 -Action info|play|pause|toggle|next|previous
[CmdletBinding()]
param(
    [ValidateSet('info', 'play', 'pause', 'toggle', 'next', 'previous')]
    [string]$Action = 'info'
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
        $_.Name -eq 'AsTask' -and
        $_.GetParameters().Count -eq 1 -and
        $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
    })[0]

function Await($operation, $resultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($resultType)
    $netTask = $asTask.Invoke($null, @($operation))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

function Empty-Result {
    param([string]$Reason)
    [pscustomobject]@{
        ok      = $false
        playing = $false
        title   = ''
        artist  = ''
        album   = ''
        app     = ''
        status  = 'none'
        message = $Reason
    } | ConvertTo-Json -Compress
    exit 0
}

try {
    $managerType = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media.Control, ContentType = WindowsRuntime]
}
catch {
    Empty-Result "Windows media control is unavailable: $($_.Exception.Message)"
}

try {
    $manager = Await ($managerType::RequestAsync()) ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager])
}
catch {
    Empty-Result "Could not reach the system media session: $($_.Exception.Message)"
}

$session = $manager.GetCurrentSession()
if ($null -eq $session) { Empty-Result 'Nothing is currently playing.' }

switch ($Action) {
    'play' { $null = Await ($session.TryPlayAsync()) ([bool]) }
    'pause' { $null = Await ($session.TryPauseAsync()) ([bool]) }
    'toggle' { $null = Await ($session.TryTogglePlayPauseAsync()) ([bool]) }
    'next' { $null = Await ($session.TrySkipNextAsync()) ([bool]) }
    'previous' { $null = Await ($session.TrySkipPreviousAsync()) ([bool]) }
}

$session = $manager.GetCurrentSession()
if ($null -eq $session) { Empty-Result 'The media session ended.' }

$properties = Await ($session.TryGetMediaPropertiesAsync()) ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties])
$playback = $session.GetPlaybackInfo()
$timeline = $session.GetTimelineProperties()

[pscustomobject]@{
    ok       = $true
    playing  = ($playback.PlaybackStatus.ToString() -eq 'Playing')
    status   = $playback.PlaybackStatus.ToString()
    title    = [string]$properties.Title
    artist   = [string]$properties.Artist
    album    = [string]$properties.AlbumTitle
    app      = [string]$session.SourceAppUserModelId
    position = [math]::Round($timeline.Position.TotalSeconds, 1)
    duration = [math]::Round($timeline.EndTime.TotalSeconds, 1)
    message  = ''
} | ConvertTo-Json -Compress