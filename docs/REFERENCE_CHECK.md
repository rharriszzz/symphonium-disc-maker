# Original scan and audio verification

The original scan and recording were checked locally on October 1, 2026.
They support the corrected radial/tangential drive holes and clockwise
chronological note layout on the printed face. Comparing opposite drive holes
also resolves the earlier size uncertainty well enough to select prototype
nominals: **0.100 inch radial × 0.090 inch tangential**. These are scan-informed
dimensions for a fit test, rather than exact manufacturing tolerances.

## Supporting files

Both originals are accessible directly through WSL; they were not copied into Git.

- Scan: `/mnt/c/Users/rharr/OneDrive/Documents/img20261001_00272891.png`
- Recording: `/mnt/c/Users/rharr/Downloads/116 E Main St 15.m4a`

The scan is 5100 × 6600 pixels, RGB, with 599.9988 dpi metadata. The recording
is mono AAC at 48 kHz and approximately 59.968 seconds long. The report records
SHA-256 fingerprints of the source files and geometry used.

The subsequent [ChatGPT response](CHATGPT_RESPONSE.md) and its
[aligned-drive profile CSV](data/aligned_drive_profiles.csv) were imported
unchanged from `CHATGPT_RESPONSE_SYMPHONIUM.zip`. Both downloaded Markdown
copies and the archive's Markdown member were byte-identical. The response
reports a separate ensemble shape check and pitch-map comparison. Both have
now been checked independently with the original scan and recording, as
described below. Its four photos are
stored locally under `reference_material/`, with source hashes in
`reference_material/chatgpt_response_import.json`. Several photo descriptions
do not match the attachments; see the follow-up in
[the questions file](QUESTIONS_FOR_CHATGPT.md).

## Scan results

The script fits the outer boundary of the largest dark connected component,
then detects bright enclosed regions. With a grayscale disk threshold of 140
and hole thresholds of **both 150 and 170**, it finds:

- **143 drive holes**, each assigned to a distinct position in a regular ring.
- **145 music holes**, assigned to tracks 1 through 19.
- **One center hole**. Track 20 has no music hole on this reference song.

Hole centers, not printed graphics, supply the geometric comparisons.
Each hole's fourth complex moment estimates the orientation of these nearly
square openings modulo 90°. The radial/tangential orientation is substantially
closer than globally axis-aligned openings.

| Measurement | Hole threshold 150 | Hole threshold 170 |
| --- | ---: | ---: |
| Mean absolute radial/tangential orientation residual | 1.602° | 1.801° |
| Mean absolute globally axis-aligned orientation residual | 23.003° | 23.271° |
| Regular drive-ring angular RMS residual | 0.0381° | 0.0397° |
| Drive radius RMS difference from CAD | 0.00286 in | 0.00315 in |
| Music-hole radius RMS difference from assigned track | 0.00351 in | 0.00399 in |
| Maximum music-hole radius difference | 0.00759 in | 0.00878 in |

The fitted outer circle is centered at **(2396.327, 4361.877) pixels**, with a
radius of **2106.139 pixels** and a boundary RMS residual of 1.101 pixels.
Calibrating its diameter to the measured 7.000 inches gives **601.754 pixels
per inch**, approximately 0.29% above the nominal scan DPI. This chosen
calibration is explicit; it assumes the caliper diameter is correct.

The fitted radius differs from the earlier handoff's 2104.615-pixel value by
about 1.524 pixels. Different boundary thresholds include different amounts of
the edge shadow. In exploratory fits, raising the disk threshold from 140 to
180 changed the fitted radius to 2107.259 pixels. These are optical boundary
choices, not evidence that the physical disk changed size.

The selected scan calibration gives a mean drive-center radius of **3.37056
inches**, versus the CAD nominal 3.373 inches. Keep the working CAD nominal
pending physical tests rather than adjusting it from this threshold-dependent
measurement alone.

## Opposite drive-hole edges and prototype dimensions

The original scan has enough resolution to distinguish the two drive-hole
dimensions. A bright-pixel mask alone discards the shaded part of an opening;
that was the limitation of the first local check, not of the supplied image.

Following the user's suggestion, compare top with bottom and left with right.
The shadow stays toward the bottom of the scanner image. In radial/tangential
coordinates it switches sides between opposite holes. Because there are an
odd **143** openings, none has an exactly opposite partner; the representative
holes are approximately 179° apart.

Measure edges **across** the shadow: radial width at the left and right of the
disk, and tangential width at the top and bottom. The script samples central
17-pixel strips along each local axis, interpolated at quarter-pixel intervals,
and finds opposing grayscale edge gradients after 1-pixel smoothing. This
sampling interpolates existing pixels; it does not increase source resolution.
Groups within 10° of each cardinal position give:

| Group | Axis measured across shadow | Holes | Median pixels | Inches |
| --- | --- | ---: | ---: | ---: |
| Right | Radial | 8 | 59.750 | 0.09929 |
| Left | Radial | 8 | 59.500 | 0.09888 |
| Top | Tangential | 7 | 52.750 | 0.08766 |
| Bottom | Tangential | 8 | 53.125 | 0.08828 |
| Left and right combined | Radial | 16 | 59.625 | **0.09909** |
| Top and bottom combined | Tangential | 15 | 53.000 | **0.08808** |

The opposite groups agree within 0.4 source pixels. Repeating with smoothing
of 0.5 and 1.5 pixels changes group medians by at most 0.25 pixel relative to
the 1-pixel result. The approximately **6.625-pixel** difference between axes
is substantially larger than those variations. The openings appear slightly
rectangular, with rounded corners; their size difference cannot be explained
by a fixed downward shadow alone.

Allow approximately 1–2 pixels (0.0017–0.0033 inch) for optical boundary
choice; this is a practical allowance, not a calibrated confidence interval.
Use **0.100 × 0.090 inch**, rounded prototype nominals consistent with the
earlier 0.09–0.10-inch caliper readings. `geometry.json` now records the two
axes separately, and SVG/DXF use them. The former 0.095-inch square was an
average placeholder. No further caliper measurement is needed to choose this
first prototype geometry; finished part fit still supplies the mechanical test.

With the unchanged 3.373-inch center radius, the nominal outer clearance is
**0.07670 inch**, close to the user's approximately 0.0760-inch measurement.
The minimum bridge between adjacent drive cutouts is **0.05602 inch**.

[The opposite-hole figure](figures/drive_opposites.png) shows native-resolution
crops enlarged without smoothing and the radial/tangential edge profiles.
A compact copy is retained with these notes; the full analysis output remains
local. `report.json` records the group
measurements, smoothing checks, and selected pair separations.

## Independent ensemble and ellipse checks

`scripts/verify_response.py` aligns all 143 openings into radial/tangential
coordinates and averages their grayscale patches. A fixed scanner shadow
rotates through local directions while the opening shape reinforces. Central
profile crossings give:

| Brightness threshold | Local radial width, pixels | Local tangential width, pixels | Local aspect ratio | Supplied CSV aspect ratio |
| --- | ---: | ---: | ---: | ---: |
| 130 | 55.292 | 49.565 | 1.1155 | 1.1151 |
| 150 | 53.788 | 47.861 | **1.1238** | **1.1250** |
| 170 | 52.529 | 46.200 | 1.1370 | 1.1370 |
| 190 | 51.174 | 44.736 | 1.1439 | 1.1497 |

The supplied CSV reproduces the threshold widths stated in the response.
Our fresh average gives closely agreeing shape ratios; absolute crossings
differ slightly with centering and detection choices. The crossing calculation
uses only the connected bright region containing zero. Neighboring drive
openings and outside paper at the profile ends do not enlarge the measured span.
These are bright-interior measurements, so retain the across-shadow dimensions
as the better basis for absolute prototype cut size.

A general conic ellipse fit to the outer boundary gives axis differences of
**0.0937%, 0.1091%, and 0.1139%** at disk thresholds 140, 160, and 180.
This agrees with the response's approximately 0.1% result, far smaller than
the approximately 12% opening aspect difference. The small ellipse difference
combines physical disk shape and scanner scale; it does not isolate either.

See [the averaged openings and overlaid profiles](figures/drive_ensemble.png).
The full results and input fingerprints are retained in
[the verification report](data/response_verification.json).

## Music-hole size limits

The detected music-hole area corresponds to a median circular diameter of
0.10934 inch at threshold 150, falling to 0.10660 inch at threshold 170.
This supports retaining the direct 0.116-inch caliper measurement instead of
substituting the white-region diameter.

For comparison, the original threshold-150 drive mask had median projected
spans of 0.09558 inch radial and 0.08572 inch tangential. The edge comparison
above replaces those white-region spans as the basis for drive-hole size.

## Audio direction results

The recording is decoded to mono 24 kHz for analysis. A short-time Fourier
transform supplies energy near each provisional tine's fundamental and weaker
second and third harmonics. Positive changes in log energy supply onset
evidence. These channels are folded across the revolution period, smoothed
periodically, and normalized separately.

For each scanned music hole, the script compares both signs of the angle-to-time
mapping while searching recording phase. At **28.126 seconds per revolution**:

| Chronological angle direction | Best summed onset score |
| --- | ---: |
| Increasing angle | 67.37 |
| Decreasing angle | 261.74 |

Decreasing-angle order scores about **3.89 times higher**, and wins for every
tested period: 28.08, 28.10, 28.12, 28.126, 28.14, and 28.16 seconds. This
independently supports clockwise chronological holes on the stationary top-face
CAD design and counterclockwise physical rotation viewed from above.

These are descriptive scores, not probabilities or statistical significance.
The analysis uses the provisional pitch map, does not transcribe the whole
song, and does not establish every tine's pitch independently. It tests
direction, not an exact new revolution period. The best recording phase near
21.107 seconds includes the loose disk's scan orientation and recording start;
it is not a mechanical reader angle. The CAD default 230° remains arbitrary.

## Independent pitch-map comparison

The new check searches **22 starting white keys from C2 through C5**, each
followed by consecutive white keys increasing outward. It retains the already
supported decreasing-angle chronology and 28.126-second period. It computes
pitch-specific positive log-energy changes at 24 kHz, folds them into 10 ms
phase bins, and searches recording phase. Two FFT windows (4096 and 8192
samples) and two frequency-evidence choices test sensitivity:

| FFT samples | Frequency evidence | Best start | Score | Next start | Next score |
| --- | --- | --- | ---: | --- | ---: |
| 4096 | Fundamental only | **C4** | 279.0 | A3 | 161.8 |
| 4096 | Fundamental plus weaker harmonics | **C4** | 261.7 | C3 | 199.8 |
| 8192 | Fundamental only | **C4** | 302.2 | A3 | 169.1 |
| 8192 | Fundamental plus weaker harmonics | **C4** | 265.5 | C3 | 196.1 |

C4 also ranks first when the first and second complete recording revolutions
are analyzed separately in all four configurations. A further check fits
each candidate's phase on the first revolution and evaluates the second
revolution **at that fixed training phase**. C4 again has the highest held-out
score in each configuration. Later partial-revolution audio is excluded from
those separate-revolution checks.

This independently supports **C4 through G6 on occupied tracks 1–19** under
the consecutive-white-key assumption. It is not an independent isolated
measurement of every tine. Tracks 18 and 19 have only one reference attack
each; track 20 has none, so **A6 remains inferred by continuation**.
`geometry.json` now records that provenance explicitly without changing pitches.

Octave alternatives receive some harmonic evidence, which is why the
fundamental-only comparison is useful. Scores are descriptive, not probabilities
or calibrated significance. They do not test arbitrary per-track tuning or
non-diatonic maps, and their magnitude depends on analysis settings. The other
AI's different numeric scores need not match these to support the same ranking.

See [the primary candidate comparison](figures/pitch_map_candidates.png) and
[all rankings and separate-revolution checks](data/response_verification.json).

## Reproduce the check

The production exporters still have no third-party runtime dependencies.
The optional analysis script needs NumPy, SciPy, Pillow, Matplotlib, and an
`ffmpeg` executable for the audio check.

```bash
pip install -e '.[analysis]'
MPLCONFIGDIR=/tmp/symphonium-matplotlib PYTHONPATH=src python3 scripts/check_reference.py \
  --scan /mnt/c/Users/rharr/OneDrive/Documents/img20261001_00272891.png \
  --audio '/mnt/c/Users/rharr/Downloads/116 E Main St 15.m4a'
```

Omit `--audio` for a scan-only run. `--disc-threshold`, `--hole-thresholds`,
`--geometry`, and `--output` are adjustable. The first hole threshold supplies
the overlay and audio-hole positions; the remaining thresholds check sensitivity.

Reproduce the independent response checks with:

```bash
MPLCONFIGDIR=/tmp/symphonium-matplotlib PYTHONPATH=src python3 scripts/verify_response.py \
  --scan /mnt/c/Users/rharr/OneDrive/Documents/img20261001_00272891.png \
  --audio '/mnt/c/Users/rharr/Downloads/116 E Main St 15.m4a'
```

This writes averaged-hole profiles, figures, candidate scores, a decoded audio
copy, and a full report under `output/response_check/`. The committed report
records the scan, audio, geometry, script, and supplied CSV fingerprints. The
original supporting files remain unchanged and outside Git.

Generated files in `output/reference_check/` include:

- `scan_overlay.png`: cyan CAD drive openings, purple track centers, green
  detected music-hole centers. Only the regular drive ring's phase is aligned
  to the loose scan; its CAD radius and hole size are unchanged.
- `drive_opposites.png`: opposite drive-hole crops and both local edge profiles,
  identifying measurements across versus along the scanner shadow.
- `audio_direction.png` and `audio_direction.csv`: both direction scores over
  recording phase at the nominal period.
- `report.json`: calibration, threshold checks, source fingerprints, and audio
  scores across trial periods.
- `detected_holes.json` and `detected_holes.csv`: detected positions,
  orientations, optical dimensions, and note-track assignments.
- `reference_audio.wav`: decoded analysis copy; the original M4A is unchanged.
