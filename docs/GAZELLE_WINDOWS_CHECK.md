# Gazelle Windows connection check

Checked October 1, 2026, Eastern time (October 2, 03:46 UTC).
The [read-only PowerShell diagnostic](../scripts/inspect_gazelle_windows.ps1)
was run on the Windows host. Its [JSON results](data/gazelle_windows_check.json)
record the observations and limits. No software or drivers were installed,
and no device settings were changed.

## Observed on this computer

- Windows 11 Home, build 26200, **x64**.
- **Sure Cuts A Lot 6.085 is already installed**, according to its uninstall
  registry entry. License/trial status and actual cutting have not been checked.
- The existing `SetupSureCutsALot_6_085_64bit.exe` download reports a **Valid**
  Windows Authenticode signature from **Craft Edge Inc**. Its SHA-256 is in
  the JSON report. A valid software signature does not establish Gazelle
  driver availability or working cutter communication.
- Among 247 present Plug and Play entries, none matched Gazelle, BossKut,
  CUTOK, DC330, generic USB printing support, USBPRINT, or the selected
  unknown/problem USB device criteria.
- No bound driver matched the Gazelle/CUTOK/DC330 names. This is not a search
  of the entire driver store and does not prove that a suitable package is absent.

The installed Craft Edge application folder was also checked for filenames
containing Gazelle, CUTOK or DC330, and for INF/CAT files. Only Gazelle help
assets matched; no driver package was found by this limited filename search.
The Gazelle-specific help includes a manual laser-to-blade offset setting.
This is a useful alignment lead, not a verified registration procedure.

## Immediate next action

The user plans to connect the Gazelle later, possibly the next morning. This
hardware check is deferred while supplier disk packages are prepared.

Connect the Gazelle by USB to this Windows computer and power it on, then
repeat the diagnostic to capture the device name, hardware IDs and driver status.
The empty candidate list alone cannot distinguish a disconnected or powered-off
cutter from a cable/port problem or an unexpectedly named device.

After the device appears, use those IDs to determine whether a suitable driver
is already bound. Craft Edge's [Gazelle setup guide](https://www.craftedge.com/tutorials/gazelle/setup.php)
describes the Windows CUTOK printer connection and SCAL's USB / Auto settings.
If a driver is needed, the [prepared Craft Edge inquiry](CRAFT_EDGE_DRIVER_INQUIRY.md)
already includes the confirmed Windows architecture and installed SCAL version.
It has not been sent. The fallback remains the Apple Silicon Mac.

SCAL does not need to be downloaded or installed again to reach this step.
Once communication works, test a simple paper circle at the correct scale;
then establish printed-label alignment. The existing
[label fitting PDF](../prototype_pack/label_fit_test.pdf) can also be printed
and hand-cut independently of the Gazelle connection.

## Repeat the check

From Windows PowerShell in the repository:

```powershell
powershell.exe -NoProfile -NonInteractive -File .\scripts\inspect_gazelle_windows.ps1
```

From WSL on this machine:

```bash
powershell.exe -NoProfile -NonInteractive -File '\\wsl.localhost\Ubuntu\home\rharris\git\symphonium-disc-maker\scripts\inspect_gazelle_windows.ps1'
```

JSON is written to stdout. `-InstallerPath` optionally checks an existing
installer's hash and signature without running it. Generic USB printer
candidates can be unrelated equipment; identify the Gazelle from the change
when it is connected before drawing conclusions about any candidate.
