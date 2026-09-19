# JARVIS offline text-to-speech through the Windows SAPI 5 engine.
# Falls back gracefully: JARVIS prefers edge-tts neural voices when available.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Text,
    [string]$Voice = "",
    [int]$Rate = 0,
    [int]$Volume = 100,
    [string]$OutputFile = ""
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    if ($Voice -ne "") {
        try { $synth.SelectVoice($Voice) } catch { Write-Warning "voice '$Voice' unavailable; using default" }
    }
    $synth.Rate = [Math]::Max(-10, [Math]::Min(10, $Rate))
    $synth.Volume = [Math]::Max(0, [Math]::Min(100, $Volume))

    if ($OutputFile -ne "") {
        $synth.SetOutputToWaveFile($OutputFile)
        $synth.Speak($Text)
        $synth.SetOutputToNull()
    }
    else {
        $synth.Speak($Text)
    }
}
finally {
    $synth.Dispose()
}

Write-Output "OK"
