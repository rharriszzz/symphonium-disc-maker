# Pachelbel prototype pack

Prepared for a first fit/playback test. No quote or order has been submitted.
The same cutting geometry is intended for both supplier/material experiments.

## Files to use

- **`pachelbel_cut_mm.dxf`**: attach only this file for cutting. Confirm the
  quote preview shows a 177.800 mm outside diameter, 143 rotating rectangular
  drive openings and 20 round music holes. It contains 22 circles and 572 lines.
- `pachelbel_preview.svg`: annotated top-face inspection preview; guides and
  note names are not cutting geometry. Later attacks proceed clockwise.
- `xometry_inquiry.txt` and `sendcutsend_inquiry.txt`: supplier-specific drafts
  to review with the DXF. Quantity one each is proposed; price and fit are unknown.
- **`label_fit_test.pdf`**: print on plain US Letter paper at actual size / 100%,
  disabling Fit and Shrink. Measure the one-inch ruler and a 1.50-inch circle,
  then hand-cut one label and its 0.200-inch center opening. Check it on the original
  disk before using adhesive stock. This test can proceed without a cutter.
- `labels_print.pdf` and `labels_print.svg`: printing artwork without cut lines.
- `labels_cut.svg`: outer circles and center holes for cutter import.
- `labels_combined.svg`: artwork and outlines for inspection. All label files
  share the same 20-label layout; automatic print-to-cut registration is not provided.
- `recording_sequence.csv`: one attack per track, in time order, with expected
  pitches to test. Align a recorded cycle by its opening C6 attack; the layout
  phase is arbitrary and does not identify the mechanical reader position.
- `preflight.json`: calculated positive nominal clearances. Supplier tolerances,
  material behavior, thickness clearance and center-post fit remain unverified.
- `geometry.json`, `arrangement.json`, `manifest.json`: exact inputs and file
  hashes for identifying this version. Regenerate after changing the geometry.

The proposed materials are Xometry clear PETG at 0.020 inch and SendCutSend
clear polypropylene at 0.030 inch. Confirm material/process availability,
small-feature tolerances, quantity, shipping and total price before paying.
The original disk is 0.020 inch thick; extra thickness in polypropylene needs
a mechanism-clearance check. Retain the 0.200-inch prototype center-hole nominal for this test.
The metal post measures 0.1925 inch (4.8895 mm).
The prototype center hole has only 0.0075 inch (0.1905 mm) diametral clearance.
Please confirm finished-hole tolerances preserve clearance over this post.


Test the manufactured disk without a label first. Record at least two revolutions,
identify the supplier/material, and compare all 20 attacks with the sequence.
Attacks are only 1.4063 seconds apart: acoustic decay can overlap,
so this pack does not guarantee isolated clean samples. Track 20's A6 is inferred
until it is actually heard; tracks 18 and 19 had just one reference attack each.

## Regeneration

From the repository root, with the project and its `print` extras installed:

```bash
python scripts/build_prototype_pack.py --output prototype_pack
```

The builder calculates nominal clearances and checks DXF entity counts.
The source tests check rotated dimensions, units, playback direction and PDF scale.
