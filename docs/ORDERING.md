# Prototype orders from SendCutSend and Xometry

Prepare a small test order from each company using the same Pachelbel
20-tine sampler. The current files are suitable for asking about feasibility
and pricing; supplier material, process, and tolerances still need confirmation.
No quote has been submitted and no order has been placed.

## Packages ready for supplier review

- [Xometry quote ZIP](../supplier_packages/xometry_quote.zip): request one
  clear PETG disk at 0.020 inch, with an optional price for two.
- [SendCutSend quote ZIP](../supplier_packages/sendcutsend_quote.zip): request
  one clear polypropylene disk at 0.030 inch as the thickness experiment,
  with an optional price for two.
- [Dimensioned reference drawing](../supplier_packages/reference_drawing.pdf):
  geometry and critical dimensions for reviewing both requests.

Each ZIP contains the same `pachelbel_cut_mm.dxf`, a reference PDF, the specific
supplier's `quote_request.txt`, a short README and file hashes. Extract the ZIP
before using a portal that expects individual files. Upload **only the DXF as
manufacturing CAD**, at 1:1 scale in millimeters. Provide the PDF and request
as supporting material for feasibility review. The PDF is illustrative and
must not be measured or used as cutting artwork.

The independent [exported-file audit](../supplier_packages/cut_file_audit.json)
finds 143 separate closed four-edge drive contours and 22 circle contours:
one perimeter, one center opening and 20 music holes. All 165 contours are on
the CUT layer, with no duplicate entities or open drive endpoints. The outer
diameter is 177.800 mm and the center opening is 5.0800 mm. Existing tests
separately check the rotated drive dimensions and nominal clearances.

The next supplier action is **feasibility confirmation and pricing**: use
[SendCutSend contact](https://sendcutsend.com/contact/) for the PP request and
Xometry's [sheet cutting quote entry](https://www.xometry.com/capabilities/sheet-cutting/)
for PETG, requesting manual review if that gauge is unavailable in the portal.
Ask both to state the minimum finished center-hole opening through the full
thickness, so taper or a melted lip cannot prevent clearance over the
4.8895 mm post. Also confirm drive-opening dimensions, location tolerances,
corner rounding, stock thickness, flatness/edge condition and delivered price.
No package has been uploaded or sent; no order has been placed.

Regenerate these delivery packages after updating the prototype pack:

```bash
PYTHONPATH=src python3 scripts/build_supplier_packages.py
```

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
| Center hole, rounded prototype nominal | 0.200 | 5.0800 |
| Metal center post, corrected trusted measurement | 0.1925 | 4.8895 |
| Each drive cutout, radial | 0.100 | 2.540 |
| Each drive cutout, tangential | 0.090 | 2.286 |
| Drive cutout center radius | 3.373 | 85.6742 |
| Music cutout diameter | 0.116 | 2.9464 |

Use **0.200 inch as the first-prototype center-hole nominal**. Clear upper and
opposed side edges in the original scan give approximately 0.198 inch,
consistent with the user's less certain 0.1995-inch inside-jaw reading of the
plastic hole. The corrected trusted metal-post measurement is **0.1925 inch**.
This resolves the earlier apparent mismatch; a retaining-head explanation is
unnecessary. The original handoffs retain the superseded values as history.

The prototype has **0.0075 inch (0.1905 mm) diametral clearance**, or 0.00375 inch
per side. This is smaller than the suppliers' published general cutting
tolerances below. Ask each supplier to confirm that the finished center hole
will clear the 4.8895 mm post; nominal preflight cannot establish finished fit.
See the [center-hole edge analysis](REFERENCE_CHECK.md#center-hole-edges-and-post-fit)
for calibration, boundary allowance and the annotated crop.

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

Its [sheet cutting capability page](https://www.xometry.com/capabilities/sheet-cutting/)
also advertises automatic quotes for tolerances as tight as ±0.005 inch and
manual review for tighter requirements. This is a capability statement, not
confirmation for this thin PETG disk. Ask which tolerance is actually achievable
for the center opening, small drive cutouts and their positions.

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
> The 5.0800 mm center hole is a rounded, scan-informed prototype nominal.
> The trusted metal-post measurement is 4.8895 mm (0.1925 inch), giving only
> 0.1905 mm (0.0075 inch) nominal diametral clearance. Please confirm finished-hole
> tolerances preserve clearance over that post. Please treat this file as a
> prototype feasibility and pricing request. Flag any required dimensional
> changes or material substitutions before cutting.
> Please include shipping and any setup or tooling fees in the quote.

## Before ordering and after delivery

1. Use the rounded 0.200-inch center hole and scan-derived 0.100 × 0.090-inch
   drive cutout nominals. The trusted metal post is 0.1925 inch.
2. Confirm material, thickness, feature limits, tolerances, quantity, and total
   price with each company. Regenerate the DXF if dimensions change.
3. Compare the quote preview with the original disk and pay for the agreed
   prototype only after those details are settled.
4. On receipt, check flatness, thickness, hole dimensions, and whether the
   hole clears the post and the disk seats like the original without forcing
   it. Confirm the top face and first test playback without a label.
5. Record at least two revolutions and identify each supplier/material.
   Follow `prototype_pack/recording_sequence.csv` to check all 20 tines.
   Attacks are 1.4063 seconds apart; acoustic decay may overlap. Use the
   recording to refine the pitch map and geometry, especially inferred track 20.

| Supplier | Material and thickness | Quantity | Delivered price | Quote status |
| --- | --- | --- | --- | --- |
| SendCutSend | Candidate: clear PP, 0.030 in | Proposed 1 | Not quoted | Not submitted |
| Xometry | Candidate: clear PETG, 0.020 in | Proposed 1 | Not quoted | Not submitted |
