# Latest discoveries and corrections for `symphonium-disc-maker`

Date: October 1, 2026  
Repository: `rharriszzz/symphonium-disc-maker`

This note is intended as the latest handoff back to Codex CLI. It should be read as
an update to, not a replacement for, the older handoff documents.

The main purpose is to record the newest corrections and conclusions that emerged
after the last round of repo work.

---

## 1. Center-hole / center-post values are now corrected

The earlier values:

```text
center hole: 0.196 in
center post: 0.2085 in
```

should no longer be used.

The current trusted measurements and scan result are:

```text
trusted metal post diameter:          0.1925 in
less-certain plastic-hole caliper:    0.1995 in
scan clear-edge center-hole estimate: about 0.198 in
prototype center-hole nominal:        0.2000 in
prototype diametral clearance:        0.0075 in
```

The user's outside-jaw measurement of the metal post is considered more reliable than
the inside-jaw measurement of the small plastic hole.

The scan's downward shadow makes a full-perimeter white-region fit underestimate the
hole diameter. Fits to clearer upper/opposed arcs give values near 0.198 in, consistent
with the user's ~0.1995 in hole reading.

### Consequence

The current prototype value:

```text
center_hole_diameter = 0.200 in
```

is appropriate.

Do not carry forward the older hypothesis that a 0.196-inch hole had to flex over a
0.2085-inch retaining head. That mismatch was caused by earlier measurements that have
now been superseded.

---

## 2. Corrected identities of the mechanism photographs

My earlier response mislabeled several of the four supplied JPEGs.

The correct descriptions are:

### `IMG_3359.jpeg`

- Disk installed in the machine.
- Printed/top face visible.
- Center post visible through the disk.
- Useful for normal installed orientation and overall mechanism relationship.

### `IMG_3360.jpeg`

- Loose disk on a wooden surface.
- Not an installed mechanism view.

### `IMG_3361.jpeg`

- Comb / tine / plucker assembly.
- Useful for counting the 20 note positions and their spacing.
- No useful center-post seating-neck view.

### `IMG_3362.jpeg`

- Drive motor/gears and adjacent pluckers.
- Disk removed from the drive area.
- Useful for observing that the drive tooth is smaller than the disk drive opening.

The center-post photograph issue no longer blocks prototype work because the corrected
post and hole measurements now give a normal positive clearance.

---

## 3. Drive openings: keep 0.100 in radial × 0.090 in tangential

The latest independent checks continue to support the rectangular interpretation.

Current best measurements from the scan:

```text
radial edge spacing:       ~0.09909 in
tangential edge spacing:   ~0.08808 in
```

Current prototype nominals:

```text
radial_size      = 0.100 in
tangential_size  = 0.090 in
```

### Independent support

A separate 143-hole local-coordinate averaging method gives essentially the same
radial/tangential aspect ratio as Codex's opposite-cardinal-hole grayscale-gradient
method.

The user's direct physical measurement of the outer radial clearance also supports
the 0.100-inch radial dimension:

```text
disk radius             = 3.500 in
drive center radius     = 3.373 in
half radial opening     = 0.050 in
predicted edge clearance= 0.077 in
measured clearance      ≈ 0.0760 in
```

Scanner X/Y scale anisotropy is only about 0.1%, far too small to explain the roughly
12% radial/tangential size difference.

### Conclusion

Keep:

```text
drive opening = 0.100 in radial × 0.090 in tangential
```

for the first prototype.

Treat these as prototype nominals, not final calibrated manufacturing tolerances.

---

## 4. Drive-opening orientation remains radial/tangential

This conclusion remains strong.

The 143 openings rotate with their polar position; their sides are approximately
aligned with the local radial and tangential axes.

The repo should continue to generate each rectangular opening rotated by the local
drive-hole polar angle.

Do not revert to globally axis-aligned rectangles.

---

## 5. Playback orientation and face convention remain unchanged

The confirmed convention is:

```text
CAD view:                        printed/top face
0 degrees:                       +X / right
positive mathematical angle:     counterclockwise
physical disk rotation, top view:counterclockwise
chronological event direction:   clockwise
```

Thus the event formula on top-face CAD is:

```python
angle = start_angle - 360.0 * time / revolution_seconds
```

The machine reads/plucks the disk from underneath, so the same physical motion appears
clockwise when viewed directly from below.

The current default:

```text
start_angle = 230 degrees
```

remains an arbitrary layout phase and has no measured mechanical significance.

---

## 6. Pitch map is better supported, but track 20 remains inferred

The current map is:

```text
track  1  C4
track  2  D4
track  3  E4
track  4  F4
track  5  G4
track  6  A4
track  7  B4
track  8  C5
track  9  D5
track 10  E5
track 11  F5
track 12  G5
track 13  A5
track 14  B5
track 15  C6
track 16  D6
track 17  E6
track 18  F6
track 19  G6
track 20  A6
```

The map is no longer just a convenient sampler assumption.

Independent scan/audio tests now show that, among tested consecutive-white-key starts,
the occupied tracks are best explained by:

```text
track 1 = C4
through
track 19 = G6
```

This conclusion survives:

- multiple FFT sizes;
- with and without harmonic weighting;
- each complete recorded revolution separately;
- second-revolution evaluation using phases fitted from the first.

### Remaining limitation

```text
tracks 18 and 19: only one physical hole each on Unchained Melody
track 20:         no hole on Unchained Melody
```

Therefore:

```text
track 20 = A6
```

remains inferred by continuation.

There is still no clean isolated-tine recording set and no trustworthy full MIDI
transcription of Unchained Melody that should replace the current reproducible
scan/audio analysis.

---

## 7. Pachelbel sampler: useful but not guaranteed to produce isolated samples

The sampler disk has:

```text
20 attacks
1 attack per provisional tine
28.126 s revolution
1.4063 s nominal attack spacing
```

It remains a very useful calibration/recording disk.

However, avoid calling the resulting sounds "guaranteed isolated tine samples."

Real music-box tines may ring longer than 1.4063 seconds, so neighboring decays may
overlap.

The safer description is:

> sparse calibration sequence with one known attack per tine and no simultaneous
> attacks

That is still much better than extracting overlapping notes from Unchained Melody.

---

# 8. Major Gazelle/CUTOK correction: treat all `cutok.com` material as unavailable

The user's `whois` check found no match for `WWW.CUTOK.COM`, and live attempts to load
the previously referenced CUTOK resources currently fail.

Therefore, for practical purposes:

> **Treat everything hosted on `cutok.com` as unavailable historical material.**

Do not rely on any of the following as current usable resources:

```text
https://www.cutok.com/Support.htm
https://www.cutok.com/down/Manual.pdf
https://www.cutok.com/down/cutok_Signed.rar
```

Even where those URLs were historically cited by users, they should now be considered:

```text
historical references only
not live setup dependencies
```

Do not tell the user that the official CUTOK manual or driver is currently accessible.

---

## 9. What remains currently verified for the BossKut Gazelle

Current Craft Edge material still supports these statements:

- Sure Cuts A Lot 6 lists **BossKut Gazelle** as a supported cutter.
- SCAL 6 supports **Windows 11**.
- Craft Edge has a live Gazelle setup page.
- That page says Windows uses a **CUTOK printer driver**.
- It says the Gazelle should appear as a CUTOK printer and SCAL should use USB / Auto.
- The setup page says Mac does not require a separate driver.

Current useful Craft Edge pages:

```text
https://www.craftedge.com/tutorials/gazelle/setup.php
https://www.surecutsalot.com/software/software_scal.php
https://craftedge.com/help/surecutsalot6/index.php
https://www.craftedge.com/download/downloads.php
https://www.craftedge.com/support/
```

### Important distinction

This verifies:

```text
SCAL 6 supports Windows 11
SCAL 6 supports BossKut Gazelle
Craft Edge expects a CUTOK driver on Windows
```

It does **not** verify that a current official Windows 11-compatible CUTOK driver
package is presently downloadable.

That is still unresolved.

---

# 10. Updated Gazelle recommendation

The active workflow should now be:

## Windows 11 first

1. Connect the Gazelle by USB.
2. Power it on.
3. Check:
   - Device Manager
   - Devices and Printers
4. Record:
   - device name;
   - whether it appears as CUTOK / DC330;
   - hardware IDs if Windows shows an unknown device.
5. Install the current **SCAL 6 trial** from Craft Edge.
6. If Windows already recognizes the device correctly, test a simple scrap-paper cut.

## If a Windows driver is missing

Ask **Craft Edge directly** for:

```text
BossKut Gazelle / CUTOK printer driver for Windows 11
```

Include:

```text
Windows architecture
USB hardware IDs
exact Gazelle model if known
```

Do not spend time chasing dead CUTOK URLs.

## If Craft Edge cannot provide a working Windows 11 driver

Switch to the **Mac path** rather than installing arbitrary driver packages.

Craft Edge's current setup says Mac does not need a separate driver.

The user has an Apple Silicon Mac, and current SCAL 6 supports Apple Silicon.

Use the SCAL trial first and verify direct USB communication before purchasing a
platform-specific license.

---

## 11. Third-party driver mirrors: downgraded recommendation

There are third-party CUTOK/DC330 driver listings that claim Windows 11 compatibility.

These may remain useful as **research leads**, but should not be recommended as the
default installation path.

For a printer/kernel-style driver, preferred order is now:

```text
1. Windows already has a usable driver
2. Craft Edge supplies a current package or procedure
3. Mac path
4. only then evaluate a third-party legacy driver package
```

If a third-party package is eventually considered:

- preserve the original download;
- compute SHA-256;
- inspect INF/CAT contents;
- check hardware IDs;
- verify architecture;
- check signatures where possible;
- scan before installation.

Do not disable Windows driver-signature enforcement simply to force an unknown package.

---

## 12. Print-and-cut / registration recommendation

Do not make automatic registration a prerequisite for continuing the project.

The repository already generates:

```text
labels_print.pdf / labels_print.svg
labels_cut.svg
label_fit_test.pdf
```

The immediate sequence should be:

1. test physical label size on plain paper;
2. prove simple Gazelle cutting at correct scale;
3. determine the actual registration/alignment procedure supported by the working
   Gazelle + SCAL combination;
4. only then add device-specific registration marks to the repository.

Until the actual cutter workflow is demonstrated, keep print artwork and cut geometry
separate and aligned to the same physical page origin/scale.

---

## 13. Recommended repo documentation updates

### `docs/LABELS.md`

Remove live-workflow dependence on `cutok.com`.

Any old CUTOK URLs should be moved to a section clearly labeled:

```text
Historical references — currently unavailable
```

The active setup should read:

```text
Windows 11
→ inspect enumeration
→ SCAL 6 trial
→ Craft Edge support for missing driver
→ Mac fallback if no working Windows path
```

### `docs/QUESTIONS_FOR_CHATGPT.md`

The following are now effectively closed:

- center-post mismatch;
- photo identity question;
- drive rectangle interpretation.

The principal remaining hardware/software uncertainty is:

```text
verified working Gazelle connection on a current OS
```

### `geometry.json`

The current values are appropriate:

```text
center hole: 0.200 in prototype nominal
center post: 0.1925 in trusted measurement
drive:       0.100 radial × 0.090 tangential
track map:   C4–A6, with track 20 inferred
```

---

# 14. Current state summary

## Strong enough for first physical prototype

- 7.000 in disk
- 0.020 in original thickness reference
- 0.200 in prototype center hole
- 0.1925 in trusted center post
- 143 drive openings
- 0.100 × 0.090 in drive opening
- radial/tangential drive orientation
- 20 note tracks
- ~0.117921 in track pitch
- top-face chronological direction
- C4→G6 well-supported for tracks 1–19
- A6 inferred for track 20
- Pachelbel sampler arrangement
- DXF/SVG prototype pack
- label print/cut files

## Still unresolved

- first real manufactured-disk fit and playback;
- actual supplier finished-hole tolerances;
- track-20 pitch by direct playback;
- repeated-note mechanical reset limit;
- real tine decay overlap;
- current working Gazelle connection under Windows 11 or macOS;
- current official Windows Gazelle/CUTOK driver package.

---

# 15. Bottom line for Codex

The most important newest correction is:

> **Do not rely on `cutok.com` at all. Treat it as gone/unavailable.**

The Gazelle workflow should now be:

```text
Windows 11 device enumeration
→ SCAL 6 trial
→ Craft Edge support if driver missing
→ Mac fallback
→ only then consider vetted legacy third-party driver packages
```

The current disc geometry work remains valid and is strong enough to proceed toward
a first prototype order.
