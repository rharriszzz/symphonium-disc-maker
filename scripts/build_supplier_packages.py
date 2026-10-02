"""Audit the prepared DXF and build separate, unsent supplier quote packages.

Requires the print extras for the reference drawing. No network or submission.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def audit_dxf(text, geometry, expected_counts):
    """Check this project's exported DXF independently of its input preflight.

    This deliberately accepts only CUT-layer circles and lines, not arbitrary
    DXF entities. Quantized endpoints must join into separate four-edge loops.
    """
    lines = text.splitlines()
    if len(lines) % 2:
        raise ValueError("incomplete DXF group/value pair")
    pairs = [(int(lines[i]), lines[i+1]) for i in range(0, len(lines), 2)]
    units = [pairs[i+1] for i, pair in enumerate(pairs[:-1]) if pair == (9, "$INSUNITS")]
    if units != [(70, "4")]:
        raise ValueError("DXF must explicitly use millimeters")
    start = pairs.index((2, "ENTITIES")) + 1
    end = pairs.index((0, "ENDSEC"), start)
    entities, current = [], None
    for code, value in pairs[start:end]:
        if code == 0:
            if value not in ("CIRCLE", "LINE"):
                raise ValueError(f"unexpected cutting entity: {value}")
            current = {0: value}
            entities.append(current)
        elif current is None:
            raise ValueError("orphan DXF entity property")
        else:
            current[code] = value
    counts = Counter(e[0] for e in entities)
    if dict(counts) != expected_counts:
        raise ValueError(f"DXF entity counts differ: {dict(counts)}")
    if any(e.get(8) != "CUT" for e in entities):
        raise ValueError("all geometry must be on the CUT layer")
    circles, segments, seen, neighbors = [], [], set(), defaultdict(list)
    for e in entities:
        if any(float(e.get(code, 0)) != 0 for code in (30, 31)):
            raise ValueError("cut geometry must be planar at z=0")
        point = (float(e[10]), float(e[20]))
        if e[0] == "CIRCLE":
            r = float(e[40])
            if not all(math.isfinite(v) for v in (*point, r)) or r <= 0:
                raise ValueError("invalid circle")
            key = ("CIRCLE", *point, r)
            circles.append((*point, r))
        else:
            other = (float(e[11]), float(e[21]))
            if not all(math.isfinite(v) for v in (*point, *other)) or point == other:
                raise ValueError("invalid or zero-length cut line")
            key = ("LINE", *sorted((point, other)))
            segments.append((point, other))
            neighbors[point].append(other)
            neighbors[other].append(point)
        if key in seen:
            raise ValueError("duplicate cut geometry")
        seen.add(key)
    if any(len(adjacent) != 2 for adjacent in neighbors.values()):
        raise ValueError("open or branching drive contour")
    remaining, loops = set(neighbors), []
    while remaining:
        component, pending = set(), [next(iter(remaining))]
        while pending:
            vertex = pending.pop()
            if vertex in component:
                continue
            component.add(vertex)
            pending.extend(neighbors[vertex])
        if len(component) != 4:
            raise ValueError("drive opening must have four joined edges")
        remaining -= component
        loops.append(component)
    if len(loops) != geometry["drive_ring"]["hole_count"]:
        raise ValueError("wrong number of closed drive openings")
    concentric = sorted(r for x, y, r in circles if x == y == 0)
    expected = [geometry["disc"]["center_hole_diameter"]*25.4/2,
                geometry["disc"]["diameter"]*25.4/2]
    if len(concentric) != 2 or not all(math.isclose(a, b, abs_tol=1e-6)
                                                   for a, b in zip(concentric, expected)):
        raise ValueError("outside or center-hole diameter differs from geometry")
    note_radius = geometry["note_system"]["note_hole_diameter"]*25.4/2
    if any(not math.isclose(r, note_radius, abs_tol=1e-6)
           for x, y, r in circles if x != 0 or y != 0):
        raise ValueError("music-hole diameter differs from geometry")
    outer = concentric[-1]
    if any(math.hypot(*p) >= outer for line in segments for p in line):
        raise ValueError("drive contour reaches outside perimeter")
    report = {"status": "exported cut-file checks passed; supplier process/fit unverified",
              "units": "millimeter", "layers": ["CUT"], "entity_counts": dict(counts),
              "closed_drive_contours": len(loops), "drive_edges_per_contour": 4,
              "circle_contours": len(circles), "total_closed_contours": len(loops)+len(circles),
              "outside_diameter_mm": 2*outer, "center_hole_diameter_mm": 2*concentric[0],
              "duplicate_entities": 0, "open_drive_endpoints": 0,
              "annotation_entities": 0,
              "limits": "checks this exporter layout, not a general DXF parser or supplier CAM; input preflight separately checks nominal clearances"}
    return report, circles, segments


def reference_pdf(geometry, preflight, circles, segments, cut_hash):
    """One-page dimensioned reference, drawn from the audited DXF coordinates."""
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_pdf import FigureCanvasPdf
    from matplotlib.patches import Circle
    disc, drive, note = geometry["disc"], geometry["drive_ring"], geometry["note_system"]
    fig = Figure(figsize=(8.5, 11))
    FigureCanvasPdf(fig)
    def text(x, y, value, size=9, **kw):
        fig.text(x, y, value, fontsize=size, family="DejaVu Sans", parse_math=False,
                 usetex=False, **kw)
    text(.07, .958, "SYMPHONIUM MUSIC DISK - PROTOTYPE QUOTE", 15, weight="bold")
    text(.07, .931, "Pachelbel 20-tine sampler | Printed/top-face view | All dimensions in mm", 10)
    text(.07, .909, "Reference drawing only. Manufacture from pachelbel_cut_mm.dxf at 1:1 scale.", 9)
    ax = fig.add_axes([.06, .405, .70, .49])
    for x, y, r in circles:
        ax.add_patch(Circle((x, y), r, fill=False, color="black", lw=.5))
    for first, second in segments:
        ax.plot([first[0], second[0]], [first[1], second[1]], color="black", lw=.45)
    radius = disc["diameter"]*25.4/2
    ax.set(xlim=(-radius-11, radius+11), ylim=(-radius-9, radius+18), aspect="equal")
    ax.axis("off")
    ax.annotate("", xy=(-radius, radius+10), xytext=(radius, radius+10),
                arrowprops={"arrowstyle": "<->", "lw": .7})
    for x in (-radius, radius):
        ax.plot([x, x], [0, radius+12], color="gray", lw=.4)
    ax.text(0, radius+12, f"Outside diameter {2*radius:.3f} ({disc['diameter']:.3f} in)",
            ha="center", fontsize=8)
    ax.annotate(f"Center hole\n{disc['center_hole_diameter']*25.4:.4f}", xy=(0, 0),
                xytext=(-12, 8), fontsize=8, arrowprops={"arrowstyle": "->", "lw": .6})
    ax.annotate(f"{len(circles)-2} music holes\nDiameter {note['note_hole_diameter']*25.4:.4f}",
                xy=circles[2][:2], xytext=(-22, -22), fontsize=8,
                arrowprops={"arrowstyle": "->", "lw": .6})
    text(.775, .851, "DRIVE OPENING", 9, weight="bold")
    text(.775, .829, "Detail, enlarged", 8)
    detail = fig.add_axes([.795, .71, .14, .115])
    radial = drive.get("radial_size", drive.get("hole_size"))*25.4
    tangent = drive.get("tangential_size", drive.get("hole_size"))*25.4
    detail.plot([0, tangent, tangent, 0, 0], [0, 0, radial, radial, 0], color="black", lw=1)
    detail.annotate("", xy=(-.35, 0), xytext=(-.35, radial), arrowprops={"arrowstyle": "<->", "lw": .7})
    detail.text(-.48, radial/2, f"{radial:.3f}", rotation=90, ha="right", va="center", fontsize=8)
    detail.annotate("", xy=(0, -.4), xytext=(tangent, -.4), arrowprops={"arrowstyle": "<->", "lw": .7})
    detail.text(tangent/2, -.55, f"{tangent:.3f}", ha="center", va="top", fontsize=8)
    detail.set(xlim=(-.9, tangent+.3), ylim=(-.95, radial+.3), aspect="equal")
    detail.axis("off")
    text(.775, .678, "Long side: radial\nShort side: tangential\nAxes rotate with ring", 8, linespacing=1.5)
    rows = [
        ("Drive openings", f"{drive['hole_count']} rectangles, {radial:.3f} radial x {tangent:.3f} tangential"),
        ("Drive center radius", f"{drive['center_radius']*25.4:.4f}; equal angular spacing"),
        ("Minimum drive bridge", f"{preflight['clearances_mm']['drive_to_drive']:.4f}"),
        ("Minimum outer edge margin", f"{preflight['clearances_mm']['drive_to_outer_edge']:.4f} at drive corner"),
        ("Xometry material request", "Clear PETG, 0.508 mm (0.020 in); original thickness reference"),
        ("SendCutSend material request", "Clear polypropylene, 0.762 mm (0.030 in); thickness experiment"),
    ]
    for i, (label, value) in enumerate(rows):
        y = .393-i*.028
        text(.07, y, label, 9, weight="bold")
        text(.40, y, value, 8)
    fit = preflight["center_fit"]
    text(.07, .195, "SUPPLIER CONFIRMATION REQUIRED BEFORE CUTTING", 10, weight="bold")
    text(.07, .168,
         f"Center post: {fit['post_diameter_in']*25.4:.4f} mm. Nominal diametral clearance: "
         f"{fit['diametral_clearance_mm']:.4f} mm.\n"
         "Confirm the minimum finished opening through the full thickness clears the post.\n"
         "State achievable hole/position tolerances and corner rounding; propose any changes for review.\n"
         "Confirm stock thickness and flat, clean-edged delivery. Quantity: quote 1, optional price for 2.\n"
         "Dimensions are prototype nominals. This drawing does not impose an unverified +/- tolerance.",
         8, va="top", linespacing=1.55)
    text(.07, .046, f"Cut-file SHA-256: {cut_hash}", 6.7)
    text(.07, .027, "Sheet 1 of 1 | Drawing scale: illustrative; do not measure this PDF | No quote submitted", 7)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="pdf", metadata={"CreationDate": None, "ModDate": None,
                                              "Title": "Symphonium prototype quote reference"})
    return buffer.getvalue()


def deterministic_zip(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, content)
    return buffer.getvalue()


def build_packages(pack, output):
    pack, output = Path(pack), Path(output)
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((pack/"manifest.json").read_text())
    for name, expected in manifest["generator_sources"].items():
        if digest((root/name).read_bytes()) != expected:
            raise ValueError(f"prototype pack generator changed: {name}; regenerate pack first")
    for entry in manifest["inputs"].values():
        if digest((root/entry["path"]).read_bytes()) != entry["sha256"]:
            raise ValueError("prototype inputs changed; regenerate pack first")
    for name, entry in manifest["files"].items():
        if digest((pack/name).read_bytes()) != entry["sha256"]:
            raise ValueError(f"prototype artifact changed: {name}; regenerate pack first")
    geometry = json.loads((pack/"geometry.json").read_text())
    preflight = json.loads((pack/"preflight.json").read_text())
    fit = preflight["center_fit"]
    if not fit:
        raise ValueError("supplier packages require a known center-post fit check")
    post_mm = fit["post_diameter_in"]*25.4
    cut = (pack/"pachelbel_cut_mm.dxf").read_bytes()
    audit, circles, segments = audit_dxf(cut.decode("ascii"), geometry, preflight["expected_dxf_counts"])
    drawing = reference_pdf(geometry, preflight, circles, segments, digest(cut))
    output.mkdir(parents=True, exist_ok=True)
    artifacts = {"reference_drawing.pdf": drawing,
                 "cut_file_audit.json": (json.dumps(audit, indent=2)+"\n").encode()}
    packages = {}
    for supplier, title, material in (("xometry", "Xometry", "clear PETG, 0.020 inch (0.508 mm)"),
                                      ("sendcutsend", "SendCutSend", "clear polypropylene, 0.030 inch (0.762 mm)")):
        inquiry = (pack/f"{supplier}_inquiry.txt").read_text() + (
            "\nReference attachment: reference_drawing.pdf (dimensions only, not cutting artwork).\n"
            "Please state the minimum finished center-hole opening through the full thickness,\n"
            f"including any taper or melt lip, and confirm it clears the {post_mm:.4f} mm metal post.\n"
            "Please state achievable hole-location tolerances as well as opening sizes.\n")
        instruction = (
            f"{title} - Symphonium prototype feasibility/quote request\n\n"
            f"Proposed material: {material}. Proposed quantity: 1; optional price for 2.\n"
            "Upload pachelbel_cut_mm.dxf alone as the manufacturing CAD, millimeters, 1:1.\n"
            f"Expected outside diameter: {audit['outside_diameter_mm']:.3f} mm; "
            f"center hole: {audit['center_hole_diameter_mm']:.4f} mm.\n"
            f"{audit['closed_drive_contours']} drive rectangles and {audit['circle_contours']-2} "
            "round music holes, plus the center hole.\n"
            "Provide reference_drawing.pdf as a supporting drawing and quote_request.txt as notes.\n"
            "Extract this ZIP first if the portal expects individual files.\n"
            "All dimensions are prototype nominals; request supplier review before cutting.\n"
            "The center-hole fit needs confirmation beyond general cutting tolerances.\n"
            "This package requests feasibility and pricing; no order has been placed.\n"
            "Flag any geometry/material substitution before manufacturing.\n"
            f"Cut-file SHA-256: {digest(cut)}\n"
        )
        members = {"pachelbel_cut_mm.dxf": cut, "reference_drawing.pdf": drawing,
                   "quote_request.txt": inquiry.encode(), "README.txt": instruction.encode()}
        hashes = {name: digest(data) for name, data in members.items()}
        package_manifest = {"supplier": title, "proposed_material": material,
                            "status": "unsent quote request; dimensional tolerances require confirmation",
                            "files": hashes}
        members["package_manifest.json"] = (json.dumps(package_manifest, indent=2)+"\n").encode()
        name = f"{supplier}_quote.zip"
        artifacts[name] = deterministic_zip(members)
        packages[supplier] = {"archive": name, "members": hashes}
    artifacts["README.md"] = f"""# Supplier quote packages

Prepared for feasibility review and pricing. Neither package has been submitted.

- [Xometry package](xometry_quote.zip): clear PETG, 0.020 inch (0.508 mm).
- [SendCutSend package](sendcutsend_quote.zip): clear polypropylene, 0.030 inch (0.762 mm).
- [Dimensioned reference drawing](reference_drawing.pdf): one-page overview for both suppliers.
- [Cut-file audit](cut_file_audit.json): closed contours, units, sizes and duplicate checks.

Each ZIP contains the same cutting DXF and reference drawing, its supplier's
quote request, a README and content hashes. Extract it and upload the DXF alone
as manufacturing CAD; provide the PDF and request as supporting material.
The drawing is illustrative, not an actual-size printing or cutting template.

The proposed quantity is one disk from each company, with an optional price
for two. Confirm the material/process, finished-hole fit, drive-opening sizes,
corner rounding, thickness, shipping and total price before paying.
SendCutSend's proposed stock is thicker than the 0.020-inch original; mechanism
clearance remains a physical test. Labels are separate from the cutting files.

The {audit['center_hole_diameter_mm']:.4f} mm center-hole nominal has only
{fit['diametral_clearance_mm']:.4f} mm diametral clearance over the trusted
{post_mm:.4f} mm post. Each request asks for the minimum clear opening
through the full thickness. General published cutting tolerances are not
a guarantee that this hole will fit. Supplier dimensional changes need review.

See [ordering instructions and supplier links](../docs/ORDERING.md) and the
[complete prototype pack](../prototype_pack/README.md). The latter includes
label files and the sampler recording sequence for the delivered disks.

Regenerate after updating the prototype pack:

```bash
PYTHONPATH=src python3 scripts/build_supplier_packages.py
```
""".encode()
    for name, content in artifacts.items():
        (output/name).write_bytes(content)
    result = {"status": "prepared; not submitted", "pack_manifest_sha256": digest((pack/"manifest.json").read_bytes()),
              "generator_sha256": digest(Path(__file__).read_bytes()), "packages": packages,
              "files": {name: digest(data) for name, data in artifacts.items()}}
    (output/"manifest.json").write_text(json.dumps(result, indent=2)+"\n")
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=Path("prototype_pack"))
    parser.add_argument("--output", type=Path, default=Path("supplier_packages"))
    args = parser.parse_args()
    print(json.dumps(build_packages(args.pack, args.output), indent=2))


if __name__ == "__main__":
    main()
