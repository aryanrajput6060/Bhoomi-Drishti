# Master volume + mute control through the Windows Core Audio API (MMDevice).
# Usage:  volume.ps1 -Json              -> read current level
#         volume.ps1 -Level 40          -> set level to 40%
#         volume.ps1 -Delta -10         -> relative change
#         volume.ps1 -Mute / -Unmute
[CmdletBinding()]
param(
    [int]$Level = -1,
    [int]$Delta = 0,
    [switch]$Mute,
    [switch]$Unmute,
    [switch]$Json
)

$ErrorActionPreference = 'Stop'

Add-Type -Language CSharp -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioEndpointVolume {
    int RegisterControlChangeNotify(IntPtr pNotify);
    int UnregisterControlChangeNotify(IntPtr pNotify);
    int GetChannelCount(out int pnChannelCount);
    int SetMasterVolumeLevel(float fLevelDB, Guid pguidEventContext);
    int SetMasterVolumeLevelScalar(float fLevel, Guid pguidEventContext);
    int GetMasterVolumeLevel(out float pfLevelDB);
    int GetMasterVolumeLevelScalar(out float pfLevel);
    int SetChannelVolumeLevel(uint nChannel, float fLevelDB, Guid pguidEventContext);
    int SetChannelVolumeLevelScalar(uint nChannel, float fLevel, Guid pguidEventContext);
    int GetChannelVolumeLevel(uint nChannel, out float pfLevelDB);
    int GetChannelVolumeLevelScalar(uint nChannel, out float pfLevel);
    int SetMute([MarshalAs(UnmanagedType.Bool)] bool bMute, Guid pguidEventContext);
    int GetMute(out bool pbMute);
    int GetVolumeStepInfo(out uint pnStep, out uint pnStepCount);
    int VolumeStepUp(Guid pguidEventContext);
    int VolumeStepDown(Guid pguidEventContext);
    int QueryHardwareSupport(out uint pdwHardwareSupportMask);
    int GetVolumeRange(out float pflMin, out float pflMax, out float pflIncrement);
}

[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceEnumerator {
    int EnumAudioEndpoints(int dataFlow, int dwStateMask, out IntPtr ppDevices);
    int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppEndpoint);
}

[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDevice {
    int Activate(ref Guid iid, int dwClsCtx, IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface);
    int OpenPropertyStore(int stgmAccess, out IntPtr ppProperties);
    int GetId([MarshalAs(UnmanagedType.LPWStr)] out string ppstrId);
    int GetState(out int pdwState);
}

[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
public class MMDeviceEnumeratorComObject { }

public class JarvisAudio {
    private static IAudioEndpointVolume Endpoint() {
        var enumerator = (IMMDeviceEnumerator)(new MMDeviceEnumeratorComObject());
        IMMDevice device;
        Marshal.ThrowExceptionForHR(enumerator.GetDefaultAudioEndpoint(0, 1, out device));
        Guid iid = typeof(IAudioEndpointVolume).GUID;
        object iface;
        Marshal.ThrowExceptionForHR(device.Activate(ref iid, 23, IntPtr.Zero, out iface));
        return (IAudioEndpointVolume)iface;
    }
    public static int GetVolume() {
        float level; Endpoint().GetMasterVolumeLevelScalar(out level);
        return (int)Math.Round(level * 100f);
    }
    public static void SetVolume(int percent) {
        float level = Math.Max(0, Math.Min(100, percent)) / 100f;
        Endpoint().SetMasterVolumeLevelScalar(level, Guid.Empty);
    }
    public static bool GetMute() { bool muted; Endpoint().GetMute(out muted); return muted; }
    public static void SetMute(bool muted) { Endpoint().SetMute(muted, Guid.Empty); }
}
"@

$current = [JarvisAudio]::GetVolume()
$muted = [JarvisAudio]::GetMute()

if ($Level -ge 0) {
    [JarvisAudio]::SetVolume($Level)
}
elseif ($Delta -ne 0) {
    [JarvisAudio]::SetVolume($current + $Delta)
}

if ($Mute) { [JarvisAudio]::SetMute($true) }
if ($Unmute) { [JarvisAudio]::SetMute($false) }

$final = [JarvisAudio]::GetVolume()
$finalMute = [JarvisAudio]::GetMute()

if ($Json) {
    [pscustomobject]@{ level = $final; muted = $finalMute; previous = $current } | ConvertTo-Json -Compress
}
else {
    Write-Output "$final"
}