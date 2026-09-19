# Lists the SAPI 5 voices installed on this machine as JSON.
Add-Type -AssemblyName System.Speech

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voices = @()
try {
    foreach ($voice in $synth.GetInstalledVoices()) {
        if ($voice.Enabled) {
            $voices += [pscustomobject]@{
                name    = $voice.VoiceInfo.Name
                culture = $voice.VoiceInfo.Culture.Name
                gender  = [string]$voice.VoiceInfo.Gender
                age     = [string]$voice.VoiceInfo.Age
            }
        }
    }
}
finally {
    $synth.Dispose()
}

ConvertTo-Json -InputObject @($voices) -Depth 4 -Compress
