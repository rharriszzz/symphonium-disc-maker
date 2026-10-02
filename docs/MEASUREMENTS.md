# Measurements and reverse-engineering notes

## Machine

Mr. Christmas Animated Holiday Symphonium, model 140-24021.

## User measurements

- Disc diameter: 7.000 in
- Disc thickness: 0.020 in
- Center-hole diameter: 0.196 in
- Note-hole diameter: approximately 0.116 in
- Disc edge to outer edge of drive hole: approximately 0.0760 in
- Drive holes: approximately 0.09–0.10 in, initially described as square
- Center-post diameter: 0.2085 in
- Approximate plucker-channel width: 0.040 in
- Innermost-to-outermost plucker geometry implies about 0.11792 in pitch

## Scan-derived observations

A 600 dpi scan of an original 7-inch disc established:

- 143 drive holes
- 145 note holes on the scanned *Unchained Melody* disc
- 19 occupied note rows on that disc
- row spacing approximately 0.118 in
- one additional outer track is consistent with the 20-tine mechanism

## Drive hole orientation and scan provenance

The October 1, 2026 [conversation handoff](CODEX_HANDOFF.md), sections 5 and 6,
reports analysis of all 143 drive-hole components in the original full-resolution
scan. The reported square orientations follow the local radial/tangential axes,
with a mean residual of roughly 1.6 degrees. Both exporters now use this
orientation. The earlier globally axis-aligned squares were incorrect.

The original scan is named `img20261001_00272891.png`, reportedly 5100 × 6600
pixels at approximately 600 dpi. The reported disc fit is centered at
(2396.453, 4361.565) pixels with radius 2104.615 pixels. These are handoff results,
not the local fit. The original image is now accessible from its Windows
location, and a separate local analysis is saved in
[the reference check](REFERENCE_CHECK.md). It confirms 143 drive holes, 145
music holes, and radial/tangential orientation, with approximately 1.60° mean
absolute orientation residual at the selected threshold.

That fitted diameter is 4209.231 pixels versus 4200 pixels for a 7.000-inch disk
at exactly 600 dpi, a difference of about 0.22%. The local fit uses a different
edge threshold and calibrates its 4212.277-pixel diameter to the measured
7.000 inches. Its overlay makes that calibration explicit.
Keep the original outside ordinary Git history if possible, with any derivative
and its calibration recorded separately.

Opposite-quadrant edge comparisons in the local reference check resolve the
size question beyond the initial bright-region mask. The scanner shadow stays
downward while the openings rotate. Edges across the shadow give approximately
**0.09909 inch radial × 0.08808 inch tangential**; opposite groups agree within
0.4 pixel. The openings appear slightly rectangular. `geometry.json` uses
rounded prototype nominals **0.100 inch radial × 0.090 inch tangential**,
replacing the earlier averaged 0.095-inch square. Optical boundary choice is
approximately 1–2 pixels, or 0.0017–0.0033 inch. See the paired crops and
method in [the reference check](REFERENCE_CHECK.md).

The drive tooth is reported to be smaller than the opening; deliberate
clearance should be preserved rather than sizing the opening to the tooth.

## Playback direction and layout angle

The [rotation and center-post follow-up](CODEX_FOLLOWUP_ROTATION_CENTERPOST.md)
reports that the user confirmed the scan shows the printed/top face and the
mechanism reads underneath. It also reports scan/audio correlation favoring
decreasing hole angle with increasing playback time. That result has
now also been checked independently against the original scan and M4A:
decreasing-angle chronological order scores about 3.89 times higher at the
nominal period and wins across all tested periods. Its inferred physical
rotation is counterclockwise when viewed from the top, or clockwise when
viewed from underneath. See [the local methods and limits](REFERENCE_CHECK.md).

Both exporters define the geometry as viewed from the printed/top face. Zero
degrees points right (+X), and positive polar angles are counterclockwise.
Chronological note holes therefore proceed clockwise:

```text
event angle = start angle - 360 * time / revolution seconds
```

SVG reflects Cartesian y to display the same physical geometry as DXF. Its
annotations use the same event angles as the holes. The default 230-degree
start angle is an arbitrary layout choice, not a measured reader angle or a
mechanical index. Changing it rotates the music pattern relative to the drive
ring while preserving relative note timing.

## Center hole and material fit

Keep the original measured **0.196-inch center hole** for the first prototype.
The measured 0.2085-inch post feature may be a wider rounded retainer above
a smaller seating region. The follow-up describes that interpretation as
plausible from the mechanism photographs, not a measured post profile.
Do not enlarge the hole to the retainer diameter solely from that reading;
doing so could change retention.

The seating diameter and exact fit remain unmeasured. Test whether the
candidate material flexes over the post and seats like the original disk.
A small sample with center holes near the nominal size is an optional way
to investigate this before buying several full disks.

## Original supporting files

Place local originals in `reference_material/`, whose contents are ignored by
Git, or provide an accessible external path. Useful evidence includes:

- `img20261001_00272891.png`: original 600 dpi scan, preserving DPI metadata.
- `116 E Main St 15.m4a`: original mechanism recording.
- The scan/audio analysis scripts and any detected-hole tables, if retained.
- Mechanism photographs showing the center post and disk seating position.

The original scan and recording are now accessible at the external paths in
[the reference check](REFERENCE_CHECK.md). They have not been copied into Git.
The response package supplied four 640 × 480 photographs, now copied to
`reference_material/IMG_3359.jpeg` through `IMG_3362.jpeg` (ignored by Git).
Direct inspection shows an installed disk, a loose disk, the comb/plucker
assembly, and the drive mechanism respectively. These do not match several
photo descriptions in [the supplied response](CHATGPT_RESPONSE.md); in
particular `IMG_3361.jpeg` does not show the center post. No unobstructed
center-post seating-profile photograph has been identified in this package.
The response and its [aligned drive profiles](data/aligned_drive_profiles.csv)
are retained in Git. The earlier analysis scripts have not been supplied.
The reference-check overlay uses the actual scan; other disk previews in
`output/` are generated CAD artwork.

## Working pitch map

Provisional, inner to outer:

C4 D4 E4 F4 G4 A4 B4
C5 D5 E5 F5 G5 A5 B5
C6 D6 E6 F6 G6 A6

This map is good enough for arranging experiments but should be confirmed
with a deliberately sparse sampler disc.

## Timing

A recording of the original disc gave approximately 28.126 seconds per revolution.

## Important distinction

The disc encodes a note **attack**. A larger or longer hole is not assumed to
encode musical duration. The tine's acoustic decay supplies the perceived duration.
