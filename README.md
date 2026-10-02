# symphonium-disc-maker

Generate **exact SVG and DXF disc geometry** for the 20-note plastic-disc
mechanism used in a Mr. Christmas Animated Holiday Symphonium
(model 140-24021), plus simple printable/cuttable label sheets.

This repository begins as a reverse-engineering and arranging project.
The geometry is based on measurements, a 600 dpi scan of an original
*Unchained Melody* disc, a recording of the mechanism, and direct measurements
of the comb/plucker assembly.

## Status

**Experimental. Verify dimensions before paying for manufacturing.**

The most important current working values are:

- disc diameter: **7.000 in**
- original disc thickness: **0.020 in**
- prototype center hole: **0.200 in** (rounded from clear-edge scan fits)
- trusted metal center post: **0.1925 in**
- drive holes: **143**
- nominal drive-hole size: **0.100 in radial × 0.090 in tangential**
- drive-hole center radius: **3.373 in**
- note tracks: **20**
- note-hole diameter: **0.116 in**
- innermost track center radius: **0.94968 in**
- track pitch: **0.117921 in**
- provisional scale, inner to outer: **C4 through A6, white notes only**
- measured revolution time: about **28.126 s**

All of these live in `geometry.json` so they can be revised without changing code.

## Repository layout

```text
geometry.json                         measured machine geometry
examples/pachelbel_sampler.json      20-note, one-strike-per-tine sampler loop
examples/minimal_example.json        smallest arrangement example
src/symphonium_disc_maker/
    arrangement.py                   load/validate note events
    geometry.py                      track/note mapping
    svg.py                           exact printable/vector disc
    dxf.py                           manufacturing DXF
    labels.py                        label sheet generator
    cli.py                           command-line interface
tests/                               geometry and file-generation tests
docs/MEASUREMENTS.md                 provenance and open questions
```

## Installation

From the repository root:

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# bash / macOS / Linux / WSL
source .venv/bin/activate

pip install -e .
```

## Make the Pachelbel sampler disc

Validate:

```bash
symphonium-disc validate examples/pachelbel_sampler.json
```

Generate an annotated SVG:

```bash
symphonium-disc svg examples/pachelbel_sampler.json \
  -o output/pachelbel_sampler.svg
```

Generate a manufacturing DXF in millimeters:

```bash
symphonium-disc dxf examples/pachelbel_sampler.json \
  -o output/pachelbel_sampler.dxf
```

The DXF contains only cut geometry: outside circle, center hole, 143 drive
holes, and music-note holes.

## Arrangement format

```json
{
  "title": "Example",
  "revolution_seconds": 28.126,
  "events": [
    {"time_seconds": 0.0, "note": "C5"},
    {"time_seconds": 0.7, "note": "E5"},
    {"time_seconds": 1.4, "note": "G5"}
  ]
}
```

`track` may be supplied instead of `note`.

The disc encodes **note onset**, not conventional note duration.

SVG and DXF show the **printed/top face**. Chronological holes proceed
clockwise around that stationary design, matching the reported counterclockwise
rotation during playback. Positive polar angles are counterclockwise from
the right (+X). `--start-angle` sets an arbitrary layout phase (default 230°),
not a measured reader angle. See the
[rotation follow-up](docs/CODEX_FOLLOWUP_ROTATION_CENTERPOST.md) for the evidence.

## Labels

Generate an 8.5 × 11 inch SVG sheet containing 20 circular labels:

```bash
symphonium-disc labels \
  --title "PACHELBEL" \
  --subtitle "Canon — sampler disc" \
  -o output/pachelbel_labels.svg
```

The label output is intended for a print-and-cut device such as a
BossKut Gazelle, Silhouette, Cricut, or similar machine.

The default 1.50-inch center label stays clear of the music holes. Use
`--mode print` for text only and `--mode cut` for circles only; `combined`
is the default paper fitting preview. The CLI checks the label diameter
against the innermost music holes and reads the center hole from `geometry.json`.
See [the label workflow and Gazelle findings](docs/LABELS.md) for examples,
alignment limitations, and the CUTOK driver investigation.

A [printable fitting PDF](prototype_pack/label_fit_test.pdf) is ready for a
plain-paper test at 100% scale. It has a one-inch calibration ruler and
1.50-inch circles. The [prototype pack](prototype_pack/README.md) also contains
the cutting DXF and supplier drafts. These files are prepared for review;
supplier quotes and physical fit are still pending.

To make PDF labels, install `pip install -e '.[print]'` and choose a `.pdf`
output filename. Add `--calibration` for a paper fitting test. SVG and DXF
exporting still need no third-party runtime dependencies.

## Manufacturing notes

For services such as SendCutSend or Xometry:

- use the generated **DXF**;
- keep manufacturing artwork separate from labels and annotations;
- upload at **1:1 scale**;
- this project defaults to **millimeters** in DXF to avoid unit ambiguity;
- check quoted minimum feature size and material availability before ordering.

The original disc is approximately 0.020 inch thick. Material choice remains
an active experiment.

See [the prototype ordering notes](docs/ORDERING.md) for current supplier
options, draft inquiries, and the measurements to resolve before paying.
The prototype center-hole nominal is now 0.200 inch, rounded from approximately
0.198-inch clear-edge scan fits and consistent with the less certain 0.1995-inch
plastic-hole reading. The trusted metal post measures 0.1925 inch.
The nominal hole gives 0.0075 inch diametral clearance;
supplier tolerances and finished fit need checking. The corrected drive ring
has bridges as narrow as 0.05602 inch. Supplier tolerances and material behavior
still need confirmation.

The [conversation handoff](docs/CODEX_HANDOFF.md) supplies the scan-derived
drive-hole orientation. Both exporters rotate the openings around the ring.
The first material candidates are Xometry's 0.020-inch clear PETG and
SendCutSend's 0.030-inch clear polypropylene; their playback behavior remains
to be tested.

The [original scan and audio check](docs/REFERENCE_CHECK.md) independently
supports the drive-hole orientation and playback direction. It includes a
reproducible analysis script, a calibrated overlay, and detected-hole tables.
Opposite-quadrant edge comparisons distinguish scanner shadows from the
slightly rectangular openings and supply the current prototype dimensions.
Optional analysis dependencies can be installed with `pip install -e '.[analysis]'`.

The follow-up checks align all 143 drive openings and compare 22 starting
pitches. The rectangular shape and global C4–G6 occupied-track map hold across
the independent checks; track 20's A6 remains inferred until the sampler plays it.

## Next steps

- test the scan-derived radial and tangential drive-hole sizes on a prototype;
- cut the 20-note Pachelbel sampler;
- record isolated real tines;
- refine the playable pitch map and rotation timing;
- add MIDI/MusicXML import and arranging helpers;
- add disk PDF previews;
- add optional registration marks for print-and-cut label workflows.

## License

MIT.
