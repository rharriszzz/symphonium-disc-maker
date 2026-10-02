from __future__ import annotations
from pathlib import Path
import html
import math

def build_label_sheet_svg(
    title: str,
    subtitle: str = "",
    *,
    label_diameter_in: float = 1.50,
    center_hole_diameter_in: float = 0.196,
    columns: int = 4,
    rows: int = 5,
    page_width_in: float = 8.5,
    page_height_in: float = 11.0,
    mode: str = "combined",
) -> str:
    if mode not in {"combined", "print", "cut"}:
        raise ValueError("mode must be combined, print, or cut")
    for name, value in (
        ("label diameter", label_diameter_in),
        ("page width", page_width_in), ("page height", page_height_in),
    ):
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be positive and finite")
    if (not math.isfinite(center_hole_diameter_in)
            or not 0 <= center_hole_diameter_in < label_diameter_in):
        raise ValueError("center hole must be nonnegative and smaller than the label")
    if any(isinstance(n, bool) or not isinstance(n, int) or n <= 0 for n in (columns, rows)):
        raise ValueError("columns and rows must be positive integers")
    margin_x = 0.55
    margin_y = 0.65
    usable_w = page_width_in - 2*margin_x
    usable_h = page_height_in - 2*margin_y
    dx = usable_w / columns
    dy = usable_h / rows
    if label_diameter_in > min(dx, dy):
        raise ValueError("labels overlap or do not fit within the page margins")

    r = label_diameter_in/2
    hr = center_hole_diameter_in/2
    # Put the entire line above/below the hole, with room for descenders.
    title_y = -hr - 0.08
    sub_y = hr + 0.14
    def font_size(text, baseline, preferred):
        extent = abs(baseline) + preferred
        if extent >= r - 0.05:
            raise ValueError("label is too small for text around the center hole")
        width = 2 * math.sqrt((r - 0.05)**2 - extent**2)
        return min(preferred, width / max(1, len(text)) / 0.8)

    title_size = font_size(title, title_y, 0.12) if title and mode != "cut" else 0.12
    sub_size = font_size(subtitle, sub_y, 0.075) if subtitle and mode != "cut" else 0.075

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_width_in}in" '
        f'height="{page_height_in}in" viewBox="0 0 {page_width_in} {page_height_in}">',
        '<style>.cut{fill:none;stroke:#000;stroke-width:0.006}'
        f'.title{{font:bold {title_size:.6f}px Arial;text-anchor:middle}}'
        f'.sub{{font:{sub_size:.6f}px Arial;text-anchor:middle}}</style>'
    ]

    cuts = ['<g id="cut">']
    artwork = ['<g id="artwork">']
    for row in range(rows):
        for col in range(columns):
            cx = margin_x + (col+0.5)*dx
            cy = margin_y + (row+0.5)*dy
            cuts.append(f'<circle class="cut" cx="{cx:.4f}" cy="{cy:.4f}" r="{r:.4f}"/>')
            if hr:
                cuts.append(f'<circle class="cut" cx="{cx:.4f}" cy="{cy:.4f}" r="{hr:.4f}"/>')
            artwork.append(f'<text class="title" x="{cx:.4f}" y="{cy+title_y:.4f}">{html.escape(title)}</text>')
            if subtitle:
                artwork.append(f'<text class="sub" x="{cx:.4f}" y="{cy+sub_y:.4f}">{html.escape(subtitle)}</text>')
    if mode != "print":
        out.extend(cuts + ['</g>'])
    if mode != "cut":
        out.extend(artwork + ['</g>'])
    out.append('</svg>')
    return "\n".join(out) + "\n"

def write_label_sheet_svg(path: str | Path, title: str, subtitle: str = "", **kwargs):
    Path(path).write_text(
        build_label_sheet_svg(title, subtitle, **kwargs),
        encoding="utf-8"
    )
