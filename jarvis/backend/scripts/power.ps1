# Power actions (lock / sleep / hibernate / restart / shutdown / cancel).
# Destructive actions are only ever reached through JARVIS' confirmation flow.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('lock', 'sleep', 'hibernate', 'restart', 'shutdown', 'cancel', 'status')]
    [string]$Action,
    [int]$DelaySeconds = 15
)

$ErrorActionPreference = 'Stop'

switch ($Action) {
    'lock' {
        Start-Process -FilePath 'rundll32.exe' -ArgumentList 'user32.dll,LockWorkStation' -NoNewWindow
        Write-Output 'locked'
    }
    'sleep' {
        # SetSuspendState(true=suspend, false=force, false=disableWakeEvent)
        $null = & 'rundll32.exe' 'powrprof.dll,SetSuspendState' '0,1,0'
        Write-Output 'sleeping'
    }
    'hibernate' {
        & shutdown.exe /h
        Write-Output 'hibernating'
    }
    'restart' {
        & shutdown.exe /r /t $DelaySeconds /c 'JARVIS requested a restart'
        Write-Output "restarting in $DelaySeconds seconds"
    }
    'shutdown' {
        & shutdown.exe /s /t $DelaySeconds /c 'JARVIS requested a shutdown'
        Write-Output "shutting down in $DelaySeconds seconds"
    }
    'cancel' {
        & shutdown.exe /a
        Write-Output 'cancelled'
    }
    'status' {
        $pending = $false
        try {
            $null = & shutdown.exe /a 2>&1
        }
        catch { $pending = $true }
        [pscustomobject]@{ pendingShutdown = $pending } | ConvertTo-Json -Compress
    }
}