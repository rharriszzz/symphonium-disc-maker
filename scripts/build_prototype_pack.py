"""Build reviewable cutting files, supplier drafts and a physical-size label test.

Requires the optional print dependencies. Sends no inquiries or orders.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from symphonium_disc_maker.arrangement import load_arrangement, normalize_arrangement
from symphonium_disc_maker.dxf import build_dxf
from symphonium_disc_maker.geometry import load_geometry
from symphonium_disc_maker.labels import build_label_sheet_pdf, build_label_sheet_svg
from symphonium_disc_maker.preflight import prototype_preflight
from symphonium_disc_maker.svg import build_svg


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_pack(geometry_path, arrangement_path, output, start_angle=230):
    geometry_path, arrangement_path, output = map(Path, (geometry_path, arrangement_path, output))
    geometry = load_geometry(geometry_path)
    arrangement = normalize_arrangement(load_arrangement(arrangement_path), geometry)
    tracks = sorted(event["track"] for event in arrangement["events"])
    if tracks != list(range(1, geometry["note_system"]["track_count"] + 1)):
        raise ValueError("sampler pack requires exactly one attack on every track")
    preflight = prototype_preflight(arrangement, geometry, start_angle_degrees=start_angle)
    # Compute PDFs before creating the output folder, so missing dependencies do
    # not leave a half-built pack. Physical cutting success is still unverified.
    common = {"center_hole_diameter_in": geometry["disc"]["center_hole_diameter"]}
    title, subtitle = "PACHELBEL", "20-tine sampler"
    fitting = build_label_sheet_pdf(title, subtitle, calibration=True, **common)
    printed = build_label_sheet_pdf(title, subtitle, mode="print", **common)
    output.mkdir(parents=True, exist_ok=True)
    generated = []
    def write(name, contents):
        path = output / name
        if isinstance(contents, bytes):
            path.write_bytes(contents)
        else:
            path.write_text(contents, encoding="utf-8")
        generated.append(name)
    write("geometry.json", geometry_path.read_bytes())
    write("arrangement.json", arrangement_path.read_bytes())
    write("pachelbel_cut_mm.dxf", build_dxf(arrangement, geometry, start_angle_degrees=start_angle))
    write("pachelbel_preview.svg", build_svg(arrangement, geometry, start_angle_degrees=start_angle))
    for mode in ("combined", "print", "cut"):
        write(f"labels_{mode}.svg", build_label_sheet_svg(title, subtitle, mode=mode, **common))
    write("label_fit_test.pdf", fitting)
    write("labels_print.pdf", printed)
    write("preflight.json", json.dumps(preflight, indent=2) + "\n")

    counts = preflight["expected_dxf_counts"]
    dxf = (output / "pachelbel_cut_mm.dxf").read_text()
    lines = dxf.splitlines()
    for entity, expected in counts.items():
        found = sum(lines[i] == "0" and lines[i+1] == entity for i in range(0, len(lines)-1, 2))
        if found != expected:
            raise ValueError(f"DXF {entity} count {found} differs from expected {expected}")

    ns, disc, drive = geometry["note_system"], geometry["disc"], geometry["drive_ring"]
    radial = drive.get("radial_size", drive.get("hole_size"))
    tangential = drive.get("tangential_size", drive.get("hole_size"))
    for supplier, material in (("xometry", "clear PETG at 0.020 inch"),
                               ("sendcutsend", "clear polypropylene at 0.030 inch as a thickness experiment")):
        write(f"{supplier}_inquiry.txt", f"""DRAFT ONLY - not submitted

Please quote one replacement plastic music disk, with an optional price for two,
for a Mr. Christmas Animated Holiday Symphonium 140-24021.
Please quote {material}; confirm the actual stock and process.
The original polymer is unknown, and the original thickness is {disc['thickness']:.3f} inch.

Attached cutting file: pachelbel_cut_mm.dxf, at 1:1 scale in millimeters.
Outside diameter: {disc['diameter']*25.4:.4f} mm.
Center hole: {disc['center_hole_diameter']*25.4:.4f} mm, matching the working original.
Drive openings: {drive['hole_count']} rectangles, {radial*25.4:.4f} mm radial by {tangential*25.4:.4f} mm tangential.
Their axes rotate with position around the ring.
Music holes: {len(arrangement['events'])} circles, {ns['note_hole_diameter']*25.4:.4f} mm diameter.
Minimum drive-to-drive bridge: {preflight['clearances_mm']['drive_to_drive']:.4f} mm.
Minimum drive-corner clearance to outside edge: {preflight['clearances_mm']['drive_to_outer_edge']:.4f} mm.

Please confirm achievable finished hole dimensions, cutting tolerances, internal
corner rounding and minimum bridges. The disk must remain flat, engage drive pins
and pluckers, and flex over a possibly wider rounded center retainer. The seating
profile is not measured. Please flag required geometry or material changes before
cutting and identify any thickness-clearance concern. Include shipping and all
setup or tooling fees. This is a prototype feasibility request; fit is untested.
""")

    sequence = output / "recording_sequence.csv"
    with sequence.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["attack", "seconds_from_arbitrary_cycle_start", "track", "working_pitch",
                         "expected_fundamental_hz", "reference_status"])
        semitones = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
        for attack, event in enumerate(arrangement["events"], 1):
            pitch = ns["notes_inner_to_outer"][event["track"]-1]
            midi = 12*(int(pitch[-1])+1) + semitones[pitch[0]]
            status = ("inferred; absent from original disk" if event["track"] == 20 else
                      "global map support; one original attack" if event["track"] in (18, 19) else
                      "global map support; per-tine measurement pending")
            writer.writerow([attack, event["time_seconds"], event["track"], pitch,
                             f"{440*2**((midi-69)/12):.3f}", status])
    generated.append(sequence.name)

    write("README.md", f"""# Pachelbel prototype pack

Prepared for a first fit/playback test. No quote or order has been submitted.
The same cutting geometry is intended for both supplier/material experiments.

## Files to use

- **`pachelbel_cut_mm.dxf`**: attach only this file for cutting. Confirm the
  quote preview shows a {disc['diameter']*25.4:.3f} mm outside diameter, {drive['hole_count']} rotating rectangular
  drive openings and {len(arrangement['events'])} round music holes. It contains {counts['CIRCLE']} circles and {counts['LINE']} lines.
- `pachelbel_preview.svg`: annotated top-face inspection preview; guides and
  note names are not cutting geometry. Later attacks proceed clockwise.
- `xometry_inquiry.txt` and `sendcutsend_inquiry.txt`: supplier-specific drafts
  to review with the DXF. Quantity one each is proposed; price and fit are unknown.
- **`label_fit_test.pdf`**: print on plain US Letter paper at actual size / 100%,
  disabling Fit and Shrink. Measure the one-inch ruler and a 1.50-inch circle,
  then hand-cut one label and its {disc['center_hole_diameter']:.3f}-inch center opening. Check it on the original
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
a mechanism-clearance check. Retain the original center-hole nominal for this test.

Test the manufactured disk without a label first. Record at least two revolutions,
identify the supplier/material, and compare all 20 attacks with the sequence.
Attacks are only {preflight['minimum_attack_gap_seconds']:.4f} seconds apart: acoustic decay can overlap,
so this pack does not guarantee isolated clean samples. Track 20's A6 is inferred
until it is actually heard; tracks 18 and 19 had just one reference attack each.

## Regeneration

From the repository root, with the project and its `print` extras installed:

```bash
python scripts/build_prototype_pack.py --output prototype_pack
```

The builder calculates nominal clearances and checks DXF entity counts.
The source tests check rotated dimensions, units, playback direction and PDF scale.
""")
    manifest = {
        "status": "prepared prototype files; no quote submitted; no order placed",
        "units_dxf": "millimeter", "view": "top_printed_face", "start_angle_degrees": start_angle,
        "inputs": {"geometry": {"path": str(geometry_path), "sha256": sha256(geometry_path)},
                   "arrangement": {"path": str(arrangement_path), "sha256": sha256(arrangement_path)}},
        "generator_sources": {
            name: sha256(Path(__file__).resolve().parents[1] / name)
            for name in ["scripts/build_prototype_pack.py", *[
                f"src/symphonium_disc_maker/{module}.py"
                for module in ("arrangement", "dxf", "geometry", "labels", "preflight", "svg")]]
        },
        "files": {name: {"sha256": sha256(output/name), "bytes": (output/name).stat().st_size}
                  for name in generated},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return preflight


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry", type=Path, default=Path("geometry.json"))
    parser.add_argument("--arrangement", type=Path, default=Path("examples/pachelbel_sampler.json"))
    parser.add_argument("--output", type=Path, default=Path("output/prototype_pack"))
    parser.add_argument("--start-angle", type=float, default=230)
    args = parser.parse_args()
    report = build_pack(args.geometry, args.arrangement, args.output, args.start_angle)
    print(json.dumps(report, indent=2))
    print(f"Saved prototype files to {args.output}")


if __name__ == "__main__":
    main()
