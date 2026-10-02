# Prototype orders from SendCutSend and Xometry

Prepare a small test order from each company using the same Pachelbel
20-tine sampler. The current files are suitable for asking about feasibility
and pricing; supplier material, process, and tolerances still need confirmation.
No quote has been submitted and no order has been placed.

The [prepared prototype pack](../prototype_pack/README.md) now contains the
[cutting DXF](../prototype_pack/pachelbel_cut_mm.dxf), an annotated preview,
supplier-specific inquiry drafts, label PDFs/SVGs, and a recording sequence.
Its manifest records source and artifact hashes. The nominal preflight finds
positive clearances throughout, including 0.07486 inch from music holes to
drive openings and 0.22038 inch between the closest music holes. It does not
establish supplier process feasibility or mechanical fit.

Regenerate the pack after changing inputs or exporter code:

```bash
pip install -e '.[print]'
PYTHONPATH=src python3 scripts/build_prototype_pack.py --output prototype_pack
```

Supplier information below was checked on October 1, 2026. The repository
contains [the conversation handoff](CODEX_HANDOFF.md), measurement notes, and
[an independent scan/audio check](REFERENCE_CHECK.md). The original scan and
recording are accessible at external Windows paths; neither is stored in Git.

## Proposed first order

Ask each company for a quote for **one disk**, with two disks as an optional
quantity comparison. This is a proposed quantity, not a confirmed preference.
The first material candidates are **0.020-inch clear PETG from Xometry** and
**0.030-inch clear polypropylene from SendCutSend**. Use the same disk geometry
for both quotes. This compares two supplier/material combinations; differences
in playback cannot be attributed to the supplier alone.

Generate the files from the repository root:

```bash
PYTHONPATH=src python3 -m symphonium_disc_maker.cli validate examples/pachelbel_sampler.json
PYTHONPATH=src python3 -m symphonium_disc_maker.cli dxf examples/pachelbel_sampler.json -o output/pachelbel_quote_only.dxf
PYTHONPATH=src python3 -m symphonium_disc_maker.cli svg examples/pachelbel_sampler.json -o output/pachelbel_sampler.svg
```

Upload only the DXF for cutting. The annotated SVG is a visual reference.
The DXF uses millimeters and contains one disk, with 143 rectangular drive cutouts
and 20 round music cutouts. Confirm the preview shows a **177.800 mm diameter**.
Thickness is a separate material selection; it is not encoded by this 2D file.

## Dimensions to confirm

Values below come from `geometry.json` unless stated otherwise.

| Feature | Inches | Millimeters |
| --- | ---: | ---: |
| Outside diameter | 7.000 | 177.800 |
| Original thickness | 0.020 | 0.508 |
| Center hole, provisional | 0.196 | 4.9784 |
| Center post, recorded in measurement notes | 0.2085 | 5.2959 |
| Each drive cutout, radial | 0.100 | 2.540 |
| Each drive cutout, tangential | 0.090 | 2.286 |
| Drive cutout center radius | 3.373 | 85.6742 |
| Music cutout diameter | 0.116 | 2.9464 |

Retain the known-working original's measured **0.196-inch center hole** for
the first prototype. It is 0.0125 inch (0.3175 mm) smaller than the measured
post feature. The [follow-up](CODEX_FOLLOWUP_ROTATION_CENTERPOST.md) suggests
the wider feature may be a rounded retainer over a smaller seating region,
but does not establish the seating diameter. This makes material flexibility
and finished hole size important fit tests. Do not enlarge the hole merely to
match the widest measured post feature.

Both outputs represent the printed/top face. Chronological note holes are
laid out clockwise to play in order during the reported counterclockwise
physical rotation. The default 230-degree start angle is arbitrary. The
scan/audio direction result has also been independently reproduced locally;
the reference-check document describes its method and limits.

The generator rotates each drive opening with its polar position, so its sides
follow the radial/tangential axes. The local reference check confirms the
orientation and count. Comparing opposite quadrants separates the downward
scanner shadow from the hole dimensions: edge estimates are approximately
0.09909 inch radial and 0.08808 inch tangential. The current **0.100 × 0.090
inch** prototype nominals replace the earlier 0.095-inch square placeholder.
The calibrated scan scale is 601.754 pixels per inch; allow roughly 1–2 pixels
for optical boundary choice. Finished prototype fit determines whether these
nominals need adjustment.

Calculated from the corrected 143 radial/tangential rectangles:

- The smallest remaining bridge between drive cutouts is approximately
  **0.05602 in (1.4228 mm)**.
- The smallest distance from a drive cutout corner to the outside edge is
  approximately **0.07670 in (1.9483 mm)**.

These values replace the earlier bridge and edge distances computed for the
earlier drive-hole geometry.

These are nominal CAD distances, without cutting tolerances. The bridge is
particularly important when asking about manufacturability. Ask for achievable
cut tolerances and corner rounding as well as minimum hole and bridge sizes.
No automatic quote acceptance establishes mechanical fit in the Symphonium.

## SendCutSend material availability

SendCutSend currently lists laser-cut
[clear Mylar at 0.005 and 0.010 in](https://sendcutsend.com/materials/mylar-clear/)
and [clear polypropylene at 0.030 in](https://sendcutsend.com/materials/polypropylene/).
Neither matches the measured 0.020-inch original. Mylar at 0.010 inch is half
the original thickness; polypropylene at 0.030 inch is 50% thicker.
Their stiffness and mechanical behavior in this mechanism remain untested.

The intended SendCutSend experiment is one disk in 0.030-inch clear
polypropylene, subject to confirming clearance for the extra thickness.
Mylar is a thinner alternative, not the current first candidate. An exact
0.020-inch plastic option can also be discussed if polypropylene will not fit.

The published stock pages state a cutting tolerance of ±0.009 inch for these
two plastics. Ask how that applies to the small drive cutouts and thin bridges.
SendCutSend explains that its minimum hole, bridge, and hole-to-edge values
depend on the exact material and thickness in its
[preflight guidance](https://sendcutsend.com/blog/10-common-reasons-your-design-is-failing-sendcutsend-preflight/).

Use their [contact page](https://sendcutsend.com/contact/) for feasibility
questions, then the quote portal linked from their material pages. A price and
an accepted material/process have not been verified for this disk.

## Xometry material availability

Xometry's [standard sheet thickness table](https://www.xometry.com/sheet-cutting/standard-sheet-sizes/)
explicitly lists **clear PETG at 0.020 inch**. This matches the measured original
thickness and is the leading candidate for the Xometry prototype. It does not
establish the original polymer identity or prove mechanical compatibility.

Xometry's [sheet cutting standards](https://www.xometry.com/manufacturing-standards/)
give nominal top-face edge-to-edge tolerances of ±0.010 inch and warn that
holes at or below 0.100 inch diameter can exceed standard tolerances on the
top face because of piercing. The warning describes round holes; ask how
piercing affects the 0.100 × 0.090-inch rectangular drive cutouts as well. Confirm achievable
dimensions and corner rounding before accepting the quote.

Request a manual review of the material, thickness, bridges, and drive cutouts
if the instant quote does not offer an appropriate option. Xometry's
[quoting guidance](https://community.xometry.com/kb/articles/678-troubleshooting-common-quoting-issues)
says unsupported sheet gauges and custom materials can require manual review.
Ask the supplier to select a process that preserves the small cutouts and to
state any tooling charge separately.

## Draft inquiry for each company

Copy this into the supplier's inquiry form with the DXF attached after reviewing
the dimensions. It is a draft; it has not been sent. Add **"Please quote clear
PETG at 0.020 inch"** for Xometry, or **"Please quote clear polypropylene at
0.030 inch as a thickness experiment"** for SendCutSend.

> I am seeking a prototype quote for a replacement plastic music disk for a
> Mr. Christmas Animated Holiday Symphonium, model 140-24021. Please quote
> one piece, with an optional price for two. The original is 7.000 inches
> (177.800 mm) in diameter and approximately 0.020 inches (0.508 mm) thick.
> The original polymer is not yet identified. Can you offer thin plastic
> suitable for a disk that must remain flat while engaging drive pins and
> music pluckers? Please identify the polymer and actual stock thickness.
>
> The attached DXF is at 1:1 scale in millimeters. It contains 143 rectangular
> drive cutouts, nominally 2.540 mm radial × 2.286 mm tangential, and 20 round music cutouts,
> nominally 2.9464 mm in diameter. The narrowest bridge between drive
> cutouts is approximately 1.4228 mm. The drive openings follow the local
> radial/tangential axes. Please confirm these features are
> manufacturable, the cut tolerances and internal corner rounding, and
> whether the finished disk can be supplied flat with clean edges.
>
> The 4.9784 mm center hole duplicates the measured working original. The
> material must tolerate fitting over a possibly wider rounded retaining post;
> the seating profile is not yet measured. Please treat this file as a
> prototype feasibility and pricing request. Flag any required dimensional
> changes or material substitutions before cutting.
> Please include shipping and any setup or tooling fees in the quote.

## Before ordering and after delivery

1. Retain the original 0.196-inch hole and use the scan-derived 0.100 × 0.090-inch
   drive cutout nominals. Check the post seating profile if accessible.
2. Confirm material, thickness, feature limits, tolerances, quantity, and total
   price with each company. Regenerate the DXF if dimensions change.
3. Compare the quote preview with the original disk and pay for the agreed
   prototype only after those details are settled.
4. On receipt, check flatness, thickness, hole dimensions, and whether the
   material flexes over the post and seats like the original without forcing
   it. Confirm the top face and first test playback without a label.
5. Record at least two revolutions and identify each supplier/material.
   Follow `prototype_pack/recording_sequence.csv` to check all 20 tines.
   Attacks are 1.4063 seconds apart; acoustic decay may overlap. Use the
   recording to refine the pitch map and geometry, especially inferred track 20.

| Supplier | Material and thickness | Quantity | Delivered price | Quote status |
| --- | --- | --- | --- | --- |
| SendCutSend | Candidate: clear PP, 0.030 in | Proposed 1 | Not quoted | Not submitted |
| Xometry | Candidate: clear PETG, 0.020 in | Proposed 1 | Not quoted | Not submitted |
