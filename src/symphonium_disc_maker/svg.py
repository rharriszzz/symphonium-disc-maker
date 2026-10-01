from __future__ import annotations
import math
from pathlib import Path
from .geometry import track_radius

def _circle(cx, cy, r, cls="cut"):
    return f'<circle class="{cls}" cx="{cx:.4f}" cy="{cy:.4f}" r="{r:.4f}" />'

def _rect_centered(cx, cy, w, h, cls="cut"):
    return (
        f'<rect class="{cls}" x="{cx-w/2:.4f}" y="{cy-h/2:.4f}" '
        f'width="{w:.4f}" height="{h:.4f}" />'
    )

def build_svg(
    arrangement: dict,
    geometry: dict,
    *,
    start_angle_degrees: float = 230.0,
    include_track_guides: bool = True,
    include_note_labels: bool = True,
) -> str:
    disc = geometry["disc"]
    drive = geometry["drive_ring"]
    notes = geometry["note_system"]

    d = float(disc["diameter"])
    r_disc = d / 2.0
    pad = 0.35
    size = d + 2*pad
    center = size / 2.0
    rev = arrangement["revolution_seconds"]

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}in" height="{size}in" '
        f'viewBox="0 0 {size:.4f} {size:.4f}">',
        '<style>.cut{fill:none;stroke:#000;stroke-width:0.006}'
        '.guide{fill:none;stroke:#888;stroke-width:0.002;stroke-dasharray:0.025 0.025}'
        '.label{font-family:Arial,sans-serif;font-size:0.07px;text-anchor:middle;dominant-baseline:middle}'
        '</style>',
        '<g id="cut">',
        _circle(center, center, r_disc),
        _circle(center, center, float(disc["center_hole_diameter"])/2.0),
    ]

    # Drive holes: keep them axis-aligned to match the factory scan appearance.
    for i in range(int(drive["hole_count"])):
        angle = math.radians(i * 360.0 / drive["hole_count"])
        x = center + drive["center_radius"] * math.cos(angle)
        y = center - drive["center_radius"] * math.sin(angle)
        s = float(drive["hole_size"])
        lines.append(_rect_centered(x, y, s, s))

    note_r = float(notes["note_hole_diameter"]) / 2.0
    for event in arrangement["events"]:
        frac = event["time_seconds"] / rev
        angle_deg = start_angle_degrees + 360.0 * frac
        angle = math.radians(angle_deg)
        radius = track_radius(geometry, event["track"])
        x = center + radius * math.cos(angle)
        y = center - radius * math.sin(angle)
        lines.append(_circle(x, y, note_r))

    lines.append('</g>')

    if include_track_guides or include_note_labels:
        lines.append('<g id="annotation">')
        if include_track_guides:
            for track in range(1, notes["track_count"] + 1):
                lines.append(_circle(center, center, track_radius(geometry, track), "guide"))
        if include_note_labels:
            for event in arrangement["events"]:
                frac = event["time_seconds"] / rev
                angle_deg = start_angle_degrees + 360.0 * frac
                angle = math.radians(angle_deg)
                radius = max(0.35, track_radius(geometry, event["track"]) - 0.17)
                x = center + radius * math.cos(angle)
                y = center - radius * math.sin(angle)
                lines.append(
                    f'<text class="label" x="{x:.4f}" y="{y:.4f}">{event["note"]}</text>'
                )
        lines.append('</g>')

    lines.append('</svg>')
    return "\n".join(lines) + "\n"

def write_svg(path: str | Path, arrangement: dict, geometry: dict, **kwargs) -> None:
    Path(path).write_text(build_svg(arrangement, geometry, **kwargs), encoding="utf-8")
