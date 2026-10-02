# Read-only Gazelle diagnosis. JSON goes to stdout; no drivers/settings are changed.
param([string]$InstallerPath = "")

$ErrorActionPreference = "Stop"
$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$architecture = switch ($cpu.Architecture) {
    0 { "x86" }
    9 { "x64" }
    12 { "ARM64" }
    default { "unknown ($($cpu.Architecture))" }
}
$present = @(Get-CimInstance Win32_PnPEntity | Where-Object { $_.Present })
$candidates = @($present | Where-Object {
    $_.Name -match "Gazelle|BossKut|CUTOK|DC330|Unknown USB|Unknown device|USB Printing Support" -or
    $_.PNPDeviceID -like "USBPRINT*" -or
    ($_.PNPDeviceID -like "USB*" -and $_.ConfigManagerErrorCode -ne 0)
} | Select-Object Name,PNPClass,Status,ConfigManagerErrorCode,HardwareID)
$drivers = @(Get-CimInstance Win32_PnPSignedDriver | Where-Object {
    $_.DeviceName -match "Gazelle|BossKut|CUTOK|DC330"
} | Select-Object DeviceName,DriverProviderName,DriverVersion,InfName,IsSigned)
$software = @(
    foreach ($key in @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )) {
        Get-ItemProperty $key -ErrorAction SilentlyContinue |
            Where-Object { $_.DisplayName -match "Sure\s*Cuts\s*A\s*Lot|BossKut|Gazelle|CUTOK" } |
            Select-Object DisplayName,DisplayVersion,Publisher
    }
)
$installer = $null
if ($InstallerPath) {
    $signature = Get-AuthenticodeSignature -LiteralPath $InstallerPath
    $installer = [PSCustomObject]@{
        Filename = (Get-Item -LiteralPath $InstallerPath).Name
        SHA256 = (Get-FileHash -LiteralPath $InstallerPath -Algorithm SHA256).Hash
        SignatureStatus = [string]$signature.Status
        Signer = if ($signature.SignerCertificate) { $signature.SignerCertificate.Subject } else { $null }
        FileVersion = (Get-Item -LiteralPath $InstallerPath).VersionInfo.FileVersion
    }
}
[PSCustomObject]@{
    CheckedAtUtc = [DateTime]::UtcNow.ToString("o")
    OS = $os.Caption
    Build = $os.BuildNumber
    Architecture = $architecture
    PresentDeviceCount = $present.Count
    CandidateDevices = $candidates
    MatchingBoundDrivers = $drivers
    InstalledSoftware = $software
    Installer = $installer
    Limits = "Name-based candidates can include other USB printers. No match does not establish driver absence or cutter failure. Disconnected devices and the full driver store are not inventoried."
} | ConvertTo-Json -Depth 6
