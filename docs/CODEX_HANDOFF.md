# Symphonium Disc Maker — ChatGPT → Codex CLI Handoff

**Date:** 2026-10-01\
**Repository:** `rharriszzz/symphonium-disc-maker`\
**Machine:** Mr. Christmas **Animated Holiday Symphonium 140-24021**\
**Goal:** Choose/arrange music for the 20-note mechanism, compile note attacks into exact disc geometry, generate manufacturing-ready DXF/SVG, and optionally generate printable labels.

---

## 1. Executive summary

The project is far enough along that the main job is now **forward generation**, not audio transcription:

```text
composition / MIDI / MusicXML
        ↓
arrangement constrained to 20 playable tines
        ↓
(note, attack time) event list
        ↓
disc compiler
        ↓
DXF for manufacturing
SVG/PDF for checking/printing
label artwork
```

The current repo is a useful starter and has the main measured geometry in `geometry.json`.

### Critical new finding not yet reflected correctly in the repo

The current `svg.py` and `dxf.py` generate the 143 square drive holes **globally axis-aligned**.

A new analysis of the original full-resolution 600 dpi scan indicates this is wrong:

> **The drive-hole squares rotate around the ring. Their sides are approximately radial/tangential at each angular position.**

This should be corrected before sending a manufacturing file out.

The code comments currently say:

```python
# Drive holes: keep them axis-aligned to match the factory scan appearance.
```

That conclusion should be reversed.

---

## 2. Physical machine and original disc

The machine is labeled:

- **Mr. Christmas**
- **Made in China**
- **Animated Holiday Symphonium**
- model **140-24021**

The reference disc used for reverse engineering is **Unchained Melody**.

The mechanism has **20 plucker/tine positions**.

The original disc is thin, translucent/flexible plastic.

---

## 3. Direct caliper measurements from the user

These are the most important directly measured dimensions.

| Feature | Measurement | Confidence / notes |
|---|---:|---|
| Disc outside diameter | **7.000 in** | High; also consistent with scan |
| Disc thickness | **0.020 in** | High |
| Center hole diameter | **0.196 in** | High, caliper |
| Note-hole diameter | **0.116 in** | High-ish, caliper |
| Disc edge → outer edge of drive hole | **0.0760 in** | High-ish |
| Drive-hole side | **~0.09–0.10 in** | Several readings; current nominal repo value 0.095 |
| Center post diameter | **0.2085 in** | High |
| Plucker channel width | **~0.040 in** | Approximate |
| Measurement to innermost channel inner edge | **1.0235 in** from far side of center post | See track-pitch derivation |
| Measurement to outermost channel inner edge | **3.2640 in** from far side of center post | See track-pitch derivation |

The user also observed directly from the mechanism that the **gear tooth engaging a drive hole is smaller than the hole**. Therefore the drive opening has deliberate clearance; do not design it as a tight tooth fit.

---

## 4. 20-note radial track geometry

### Strongest mechanical result: track pitch

The two channel-edge measurements differ by:

```text
3.2640 - 1.0235 = 2.2405 in
```

There are 20 tines/channels, hence 19 intervals:

```text
2.2405 / 19 = 0.1179210526 in
```

Use:

```text
track_pitch = 0.117921 in
```

This agrees very closely with the independently observed row spacing in the scanned factory disc.

### Working absolute track positions

Current repo uses:

```text
inner_track_center_radius = 0.94968 in
track_pitch               = 0.117921 in
track_count               = 20
```

Therefore:

```text
track(n) = 0.94968 + (n - 1) * 0.117921   inches
```

for tracks 1 through 20.

The outermost track center is therefore:

```text
track 20 = 3.190179 in
```

### Provisional pitch map, inner → outer

```text
1   C4
2   D4
3   E4
4   F4
5   G4
6   A4
7   B4
8   C5
9   D5
10  E5
11  F5
12  G5
13  A5
14  B5
15  C6
16  D6
17  E6
18  F6
19  G6
20  A6
```

This is a **working map**, supported by geometry/audio/existing Symphonium work, but the intended Pachelbel sampler disc is a good way to confirm it physically.

---

## 5. Original 600 dpi scan

The original scan is **not currently in the GitHub repo**.

Original uploaded file:

```text
img20261001_00272891.png
```

The user reports and the PNG metadata confirms:

```text
5100 × 6600 pixels
~600 dpi (metadata ~599.9988 dpi)
24-bit RGB
~25 MB
```

The scan is excellent for geometry.

### Disc fit from the full-resolution scan

A fitted disc circle was approximately:

```text
center x = 2396.453 px
center y = 4361.565 px
radius   = 2104.615 px
diameter = 4209.231 px
```

A 7.000-inch disc at 600 dpi would nominally be 4200 px across, so the scan scale is very plausible.

### Connected-component observations

From the full-resolution scan:

- **143 drive holes** — very clear
- **145 music-note holes** on the Unchained Melody disc
- **19 occupied note rows** on that particular song disc
- mechanism measurements support a **20th available row**
- the likely unused row on Unchained Melody is the outermost/highest one

### Scan-derived drive-ring center radius

Working value:

```text
drive-hole center radius ≈ 3.373 in
```

This is consistent with:

```text
disc radius 3.500
minus edge gap ~0.076
minus roughly half a ~0.095 hole
≈ 3.3765 in
```

The repo currently uses **3.373 in**, which is reasonable as a working value.

---

## 6. IMPORTANT: drive-hole orientation

This is the most important handoff item for Codex.

### Current repo behavior

`src/symphonium_disc_maker/svg.py` currently draws each drive square as an ordinary unrotated SVG `<rect>`.

`src/symphonium_disc_maker/dxf.py` similarly generates each square using the same global ±x/±y offsets.

Thus every square is globally axis-aligned.

### New full-scan orientation analysis

All 143 drive-hole connected components were analyzed.

A fourth-order complex moment is useful for a nearly square contour because it resolves square orientation modulo 90 degrees.

The observed hole orientation follows the disc polar angle.

After calibrating the fourth-moment phase for an axis-aligned square, the scan result implies:

> **The sides of each factory square are approximately aligned with the local radial and tangential directions.**

Mean orientation residual was roughly **1.6 degrees** from the radial/tangential model.

### What to change

For drive hole `i`:

```python
theta = 2*pi*i / 143
```

Center:

```python
cx = R * cos(theta)
cy = R * sin(theta)
```

The square should then be **rotated by theta** so that:

- one pair of sides is radial/tangential,
- not globally horizontal/vertical.

For DXF, form local square vertices and rotate them:

```python
local = [
    (-h, -h),
    (+h, -h),
    (+h, +h),
    (-h, +h),
]

x = cx + u*cos(theta) - v*sin(theta)
y = cy + u*sin(theta) + v*cos(theta)
```

where `h = hole_size / 2`.

For SVG, either transform each rectangle:

```xml
transform="rotate(angle cx cy)"
```

or explicitly emit a polygon.

### Remaining uncertainty

Exact nominal side length is not fully settled:

```text
user caliper readings: about 0.09 to 0.10 in
repo nominal:          0.095 in
```

Keep `0.095` as a working value, but treat it as a tunable manufacturing parameter.

---

## 7. Drive-hole count and angular pitch

Confirmed count:

```text
143 drive holes
```

Angular pitch:

```text
360 / 143 = 2.517482517... degrees
```

The gear tooth is visibly smaller than the square hole, so exact tooth dimensions are **not** the intended hole dimensions.

---

## 8. Note-hole geometry

Working note-hole diameter:

```text
0.116 in
```

The full-resolution scan gave a somewhat smaller equivalent optical diameter (~0.107 in), but thresholding/translucent plastic affects optical edge detection.

For now, trust the direct caliper measurement more than the thresholded scan for diameter.

Adjacent radial tracks are only ~0.117921 in apart, so a 0.116 in hole is almost one full track pitch in diameter. This is plausible but means nearly simultaneous adjacent-track notes deserve mechanical testing.

---

## 9. Timing and audio

Reference recording:

```text
116 E Main St 15.m4a
```

Properties observed:

```text
~59.97 seconds
mono AAC
48 kHz
```

The recording contains a little more than two complete revolutions.

Working measured revolution period used in the repo:

```text
28.126 seconds / revolution
```

Treat this as preliminary but good enough for first-disc generation.

### Design philosophy

The disc appears to encode:

```text
pitch + attack time
```

not conventional note duration.

A tine rings after being plucked. Making a tangentially elongated hole is **not expected to create a sustained MIDI-style note**; it is more likely to affect plucker reset timing.

---

## 10. Do not over-invest in transcription ML

There was discussion of Google's piano-transcription Transformer work.

The user correctly pointed out that a piano-specific transcription model is not central to this project.

The desired direction is:

```text
original composition
→ abbreviated/arranged version
→ legal 20-note event sequence
→ physical disc
```

not:

```text
audio → transcription
```

A custom model for this instrument would be considerable work and mostly solve the inverse problem.

---

## 11. Audio-preview experiments and failure to remember

Two preview strategies were tried.

### Generic clean resonator

A simple clean synthetic music-box sound was musically intelligible but not very faithful to the actual Symphonium.

### Attempted deconvolution/sample extraction from Unchained Melody

This failed badly.

Recovered "per-tine impulse responses" contained ringing from neighboring notes. When reused, the resulting Bach previews sounded like:

> **"wind chimes in a storm"**

Do **not** repeat this raw deconvolution approach without a genuinely sparse source recording.

The Pachelbel sampler is intentionally designed so that a later real recording can provide isolated tine samples.

---

## 12. Pachelbel 20-tine sampler disc

The repo includes:

```text
examples/pachelbel_sampler.json
```

Purpose:

- musically tolerable test disc,
- every provisional tine struck exactly once,
- no simultaneous notes,
- useful later to record isolated tines,
- smooth loop.

Harmony basis, transposed to C:

```text
C – G – Am – Em – F – C – F – G
```

There are:

```text
20 attacks
```

over:

```text
28.126 seconds
```

Nominal attack spacing:

```text
28.126 / 20 = 1.4063 seconds
```

Because there are exactly 20 equally spaced attacks, their angular separation is:

```text
360 / 20 = 18 degrees
```

### Important preview mistake already caught

An early AI-generated illustrative image showed two notes close together near 9 o'clock.

That image was visually realistic but geometrically wrong.

Do **not** use generated illustrative artwork as engineering geometry.

The exact programmatic layout should show all 20 note attacks at **18-degree angular spacing**.

### WAV-loop mistake already caught

The first audio preview appended decay/silence after one revolution, making the last-to-first gap sound longer.

The event data itself was uniform.

For looping previews, render multiple revolutions continuously and extract a middle revolution so ringing crosses the wrap boundary naturally.

---

## 13. Bach arrangement experiments

Three BWV 939 mini-arrangements were made outside the initial repo:

```text
A — Faithful miniature       108 note attacks
B — Flowing music-box        109 note attacks
C — Two-voice miniature      113 note attacks
```

The user liked all three musically.

These were intended to be approximately one revolution each.

They may be useful later as richer first musical discs once the Pachelbel sampler validates the physical geometry.

---

## 14. Manufacturing materials

### Original

Measured original-disc thickness:

```text
0.020 in = 0.508 mm
```

Material identity is **not positively identified**.

It is thin and flexible.

Avoid assuming thick acrylic is mechanically equivalent.

### Xometry — best dimensional match found so far

As of 2026-10-01, Xometry lists:

```text
Clear PETG: 0.020 in
```

as a standard sheet-cutting thickness.

This exactly matches the measured original thickness and is therefore the leading first serious material candidate.

Official source:
https://www.xometry.com/sheet-cutting/standard-sheet-sizes/

Xometry sheet cutting supports 2D DXF and has a dedicated DXF workflow.

Official sources:
https://www.xometry.com/capabilities/sheet-cutting/
https://community.xometry.com/kb/articles/643-what-file-types-does-xometry-accept

Xometry's published sheet-cutting guidance says nominal top-face edge-to-edge tolerance is about ±0.010 in, and specifically warns that holes **0.100 in or smaller** can be slightly enlarged by the cutting/piercing process.

Official source:
https://www.xometry.com/manufacturing-standards/

That warning matters because:

```text
drive hole nominal ~0.095 in
note hole          0.116 in
```

The drive holes may need a tighter/manual tolerance discussion or a test coupon.

### SendCutSend

As of 2026-10-01, SendCutSend stocks:

```text
Clear polypropylene: 0.030 in
```

Their page describes it as flexible/fatigue resistant.

Official source:
https://sendcutsend.com/materials/polypropylene/

This is 50% thicker than the measured original:

```text
0.030 / 0.020 = 1.5
```

It may still work and could be an inexpensive/flexible experiment, but it is not as close dimensionally as Xometry's 0.020 PETG.

SendCutSend says no additional services are available on that clear polypropylene.

They also currently list clear Mylar in 0.005 and 0.010 in, but not 0.020 in.

Official material list:
https://sendcutsend.com/materials/

### No vendor contact has happened

Important:

> **No order, quote, email, phone call, or engineering discussion has yet occurred with either SendCutSend or Xometry.**

All conclusions are from public web information only.

The right comparison should happen after the corrected manufacturing DXF exists: upload the **same DXF** to both quote systems and compare actual price/process/material.

---

## 15. Manufacturing file formats

### Preferred output: DXF

DXF = Drawing Exchange Format, a vector CAD format.

Use DXF for the cutter; SVG/PDF are better for visual checking and labels.

### Xometry

For sheet cutting, Xometry explicitly supports **2D DXF**.

Guidance:

- cut geometry only,
- 1:1 scale,
- XY plane,
- no title blocks,
- tolerance callouts separate if needed.

Useful unit rule from Xometry:

- DXF max dimension >48.5 units → assumes millimeters.

Because a 7-inch disc is:

```text
177.800 mm
```

generating DXF in **millimeters** is a good way to avoid unit ambiguity.

Official source:
https://www.xometry.com/resources/sheet/preparing-dxf-files/

### SendCutSend

DXF is also appropriate for SendCutSend.

Keep label graphics, text, annotations, dimensions, guides, etc. out of the manufacturing cut file.

### Suggested artifact set per song

```text
song.json       arrangement/event source
song.mid        optional musical interchange
song.musicxml   optional score interchange
song.dxf        manufacturing cut file
song.svg        exact geometric preview
song.pdf        printable 1:1 verification
song-label.svg  label artwork / cut paths
song-label.pdf  printable label sheet
```

---

## 16. Labels

Keep the **label workflow separate from disc manufacturing geometry**.

A roughly **1.5-inch circular label** was considered a useful starting size, positioned inside the musical region.

Center cutout should match the center hole when desired.

### Suggested label stock

A good candidate is OnlineLabels white Weatherproof Matte Inkjet material.

Current product/material information:

- full-sheet 8.5 × 11 available,
- inkjet compatible,
- white matte,
- permanent adhesive,
- facestock caliper ~4 mil,
- full construction including liner ~8 mil before application.

Official sources:
https://www.onlinelabels.com/products/ol175wj
https://www.onlinelabels.com/materials/weatherproof-matte-inkjet-labels

OnlineLabels also lists a **1.5-inch circle** format (OL2088), 30 labels per sheet, although a full sheet is more flexible if doing custom print-and-cut registration.

Note: ordinary home printers generally do **not** print white ink. Clear labels will therefore show the plastic through any "white" artwork.

---

## 17. Label cutter

The user already owns a:

```text
BossKut Gazelle
```

The original software has been lost.

Current Sure Cuts A Lot 6 documentation explicitly lists **BossKut Gazelle** as supported and supports Windows 11.

Official sources:
https://surecutsalot.com/support/faq/faq_surecutsalot.php
https://www.craftedge.com/support/faq/faq_surecutsalot6.php

Therefore, before buying another cutter, first try to revive the existing Gazelle with **Sure Cuts A Lot 6**.

The repo's label SVG output is a good match for this workflow.

---

## 18. Current GitHub repo state

Repo is live:

```text
rharriszzz/symphonium-disc-maker
```

Default branch:

```text
main
```

Current checked-in `geometry.json` contains:

```json
{
  "disc": {
    "diameter": 7.0,
    "thickness": 0.02,
    "center_hole_diameter": 0.196
  },
  "drive_ring": {
    "hole_count": 143,
    "hole_shape": "square",
    "hole_size": 0.095,
    "center_radius": 3.373,
    "angular_pitch_degrees": 2.5174825174825175
  },
  "note_system": {
    "track_count": 20,
    "note_hole_diameter": 0.116,
    "inner_track_center_radius": 0.94968,
    "track_pitch": 0.117921
  },
  "timing": {
    "measured_revolution_seconds": 28.126
  }
}
```

These remain good **working** values.

The main known code correction is drive-hole rotation.

---

## 19. Recommended immediate Codex tasks

### Priority 1 — fix drive-hole orientation

Patch both:

```text
src/symphonium_disc_maker/svg.py
src/symphonium_disc_maker/dxf.py
```

so each square rotates with its polar position, with sides radial/tangential.

Add tests that fail if all square edges are globally parallel.

A good test could inspect generated vertices for e.g. holes at approximately 0°, 45°, and 90°.

### Priority 2 — add/retain geometry provenance

Extend `geometry.json` or add a provenance document with fields such as:

```json
"drive_ring": {
  "hole_count": 143,
  "hole_size": 0.095,
  "hole_size_status": "working nominal; user measured ~0.09–0.10",
  "center_radius": 3.373,
  "orientation": "radial_tangential"
}
```

Do not silently turn uncertain measurements into exact truths.

### Priority 3 — use the full 600 dpi scan as a regression reference

The original scan should be made available to the local Codex workflow.

Suggested choices:

1. keep the 25 MB original outside Git and point tools to it, or
2. use Git LFS, or
3. commit a smaller analysis/reference derivative and keep the original locally.

The file is below GitHub's hard 100 MB per-file limit, but a 25 MB binary will bloat normal Git history if repeatedly changed.

### Priority 4 — generate an overlay/regression image

Write a script that:

- loads the original scan,
- finds disc center/radius,
- overlays the generated 143 drive-hole geometry,
- overlays the 20 note-track circles,
- reports residual distances/orientations.

This is a much better pre-manufacturing check than eyeballing an SVG.

### Priority 5 — manufacturing sanity checks

Before ordering:

- confirm 7.000-inch final diameter,
- confirm 0.196 center hole,
- confirm radial/tangential drive-square orientation,
- decide whether first part is:
  - 0.020 PETG from Xometry, or
  - 0.030 PP from SendCutSend,
- verify supplier's minimum feature/tolerance handling for the ~0.095 drive squares,
- generate an unannotated, 1:1 mm DXF.

### Priority 6 — optional test coupon

Because vendor tolerances on ~0.095-inch cutouts may matter, consider a small test coupon containing:

```text
0.085
0.090
0.095
0.100
0.105 in
```

square holes plus a few round holes near 0.116 in.

However, the most useful real test remains a full musical sampler disc because fit also depends on overall geometry and disc flexibility.

---

## 20. Useful future mechanical tests

The first or second physical test disc can investigate:

- repeated-note reset time,
- two-note adjacent-track attacks,
- 3- or 4-note chords,
- high vs low track reliability,
- slight radial offsets to estimate tolerance,
- different note-hole diameters,
- tangentially elongated note holes,
- loop boundary behavior,
- whether heavy chord loads slow the mechanism.

Do not make the first test purely "Hanon." The user prefers a real musical piece that also collects engineering information.

---

## 21. Confidence summary

### Very high confidence

- 7.000 in outside diameter
- 0.020 in original thickness
- 0.196 in center hole
- 143 drive holes
- 20 tines/tracks in mechanism
- ~0.117921 in track pitch
- drive holes rotate around the ring rather than remaining globally axis-aligned

### High / good working confidence

- 0.116 in note-hole diameter
- drive-ring center radius ~3.373 in
- inner track center radius ~0.94968 in
- 28.126 s/revolution
- pitch ordering C4–A6 diatonic, inner→outer

### Still worth physically validating

- exact nominal drive-hole side: 0.090? 0.095? 0.100?
- exact absolute radial offset of note track 1
- final pitch/octave naming of every tine
- material identity of original disc
- whether 0.030 PP works as well as 0.020 material
- vendor kerf/tolerance effect on ~0.095 square drive openings

---

## 22. Bottom line for Codex

Do **not** restart the project from scratch.

The repo architecture is appropriate.

The immediate engineering correction is:

> **Rotate every drive-hole square so its sides follow the local radial/tangential axes.**

Then use the original 600 dpi scan as a geometric regression test.

After that, generate a clean Pachelbel sampler DXF and get an actual quote for:

1. Xometry 0.020 clear PETG
2. SendCutSend 0.030 clear polypropylene

No supplier has yet been contacted or quoted.

The first manufactured musical sampler should then provide the data needed to refine geometry and record isolated real tines.
