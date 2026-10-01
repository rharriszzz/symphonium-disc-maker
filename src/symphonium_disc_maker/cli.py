from __future__ import annotations
import argparse
from pathlib import Path
from .geometry import load_geometry
from .arrangement import load_arrangement, normalize_arrangement, validate_minimum_same_track_gap
from .svg import write_svg
from .dxf import write_dxf
from .labels import write_label_sheet_svg

def _common(parser):
    parser.add_argument("arrangement", help="Arrangement JSON file")
    parser.add_argument("--geometry", default="geometry.json", help="Geometry JSON file")
    parser.add_argument("--start-angle", type=float, default=230.0, help="Angle for time zero, degrees")

def main(argv=None):
    p = argparse.ArgumentParser(prog="symphonium-disc")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_svg = sub.add_parser("svg", help="Generate exact disc SVG")
    _common(p_svg)
    p_svg.add_argument("-o", "--output", required=True)

    p_dxf = sub.add_parser("dxf", help="Generate manufacturing DXF")
    _common(p_dxf)
    p_dxf.add_argument("-o", "--output", required=True)
    p_dxf.add_argument("--inches", action="store_true", help="Write DXF in inches instead of mm")

    p_val = sub.add_parser("validate", help="Validate arrangement")
    _common(p_val)
    p_val.add_argument("--same-track-gap", type=float, default=0.0)

    p_label = sub.add_parser("labels", help="Generate a printable/cuttable label sheet SVG")
    p_label.add_argument("--title", required=True)
    p_label.add_argument("--subtitle", default="")
    p_label.add_argument("-o", "--output", required=True)
    p_label.add_argument("--diameter", type=float, default=1.50)

    args = p.parse_args(argv)

    if args.cmd == "labels":
        write_label_sheet_svg(
            args.output,
            args.title,
            args.subtitle,
            label_diameter_in=args.diameter,
        )
        return 0

    g = load_geometry(args.geometry)
    a = normalize_arrangement(load_arrangement(args.arrangement), g)

    if args.cmd == "svg":
        write_svg(args.output, a, g, start_angle_degrees=args.start_angle)
    elif args.cmd == "dxf":
        write_dxf(
            args.output, a, g,
            start_angle_degrees=args.start_angle,
            millimeters=not args.inches
        )
    elif args.cmd == "validate":
        warnings = validate_minimum_same_track_gap(a, args.same_track_gap)
        print(f"{len(a['events'])} events; {a['revolution_seconds']:.3f} s/revolution")
        if warnings:
            for warning in warnings:
                print("WARNING:", warning)
            return 2
        print("OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
