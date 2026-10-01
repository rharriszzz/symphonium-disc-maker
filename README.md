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
- center hole: **0.196 in**
- drive holes: **143**
- nominal drive-hole size: **0.095 in square**
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

## Manufacturing notes

For services such as SendCutSend or Xometry:

- use the generated **DXF**;
- keep manufacturing artwork separate from labels and annotations;
- upload at **1:1 scale**;
- this project defaults to **millimeters** in DXF to avoid unit ambiguity;
- check quoted minimum feature size and material availability before ordering.

The original disc is approximately 0.020 inch thick. Material choice remains
an active experiment.

## Next steps

- confirm exact drive-hole size and orientation;
- cut the 20-note Pachelbel sampler;
- record isolated real tines;
- refine the playable pitch map and rotation timing;
- add MIDI/MusicXML import and arranging helpers;
- add PDF preview output;
- add optional registration marks for print-and-cut label workflows.

## License

MIT.
