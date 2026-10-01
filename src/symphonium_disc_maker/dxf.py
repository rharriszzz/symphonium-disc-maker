from __future__ import annotations
import math
from pathlib import Path
from .geometry import track_radius

MM_PER_INCH = 25.4

def _pair(code, value):
    return f"{code}\n{value}\n"

def _circle(lines, x, y, r, layer="CUT"):
    lines.append(_pair(0, "CIRCLE"))
    lines.append(_pair(8, layer))
    lines.append(_pair(10, f"{x:.6f}"))
    lines.append(_pair(20, f"{y:.6f}"))
    lines.append(_pair(30, "0.0"))
    lines.append(_pair(40, f"{r:.6f}"))

def _line(lines, x1, y1, x2, y2, layer="CUT"):
    lines.append(_pair(0, "LINE"))
    lines.append(_pair(8, layer))
    lines.append(_pair(10, f"{x1:.6f}"))
    lines.append(_pair(20, f"{y1:.6f}"))
    lines.append(_pair(30, "0.0"))
    lines.append(_pair(11, f"{x2:.6f}"))
    lines.append(_pair(21, f"{y2:.6f}"))
    lines.append(_pair(31, "0.0"))

def build_dxf(
    arrangement: dict,
    geometry: dict,
    *,
    start_angle_degrees: float = 230.0,
    millimeters: bool = True,
) -> str:
    scale = MM_PER_INCH if millimeters else 1.0
    disc = geometry["disc"]
    drive = geometry["drive_ring"]
    notes = geometry["note_system"]
    rev = arrangement["revolution_seconds"]

    lines = []
    lines.append(_pair(0, "SECTION"))
    lines.append(_pair(2, "HEADER"))
    lines.append(_pair(9, "$INSUNITS"))
    lines.append(_pair(70, "4" if millimeters else "1"))
    lines.append(_pair(0, "ENDSEC"))
    lines.append(_pair(0, "SECTION"))
    lines.append(_pair(2, "ENTITIES"))

    _circle(lines, 0, 0, disc["diameter"]/2*scale)
    _circle(lines, 0, 0, disc["center_hole_diameter"]/2*scale)

    # Square drive holes as 4 LINE entities each.
    s = drive["hole_size"] * scale
    half = s/2
    for i in range(int(drive["hole_count"])):
        a = math.radians(i * 360.0 / drive["hole_count"])
        cx = drive["center_radius"] * math.cos(a) * scale
        cy = drive["center_radius"] * math.sin(a) * scale
        pts = [
            (cx-half, cy-half),
            (cx+half, cy-half),
            (cx+half, cy+half),
            (cx-half, cy+half),
        ]
        for j in range(4):
            x1,y1 = pts[j]
            x2,y2 = pts[(j+1)%4]
            _line(lines, x1,y1,x2,y2)

    nr = notes["note_hole_diameter"]/2*scale
    for event in arrangement["events"]:
        frac = event["time_seconds"] / rev
        a = math.radians(start_angle_degrees + 360.0*frac)
        r = track_radius(geometry, event["track"]) * scale
        _circle(lines, r*math.cos(a), r*math.sin(a), nr)

    lines.append(_pair(0, "ENDSEC"))
    lines.append(_pair(0, "EOF"))
    return "".join(lines)

def write_dxf(path: str | Path, arrangement: dict, geometry: dict, **kwargs) -> None:
    Path(path).write_text(build_dxf(arrangement, geometry, **kwargs), encoding="ascii")
