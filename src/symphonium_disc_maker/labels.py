from __future__ import annotations
from pathlib import Path
import html

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
) -> str:
    margin_x = 0.55
    margin_y = 0.65
    usable_w = page_width_in - 2*margin_x
    usable_h = page_height_in - 2*margin_y
    dx = usable_w / columns
    dy = usable_h / rows

    title = html.escape(title)
    subtitle = html.escape(subtitle)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_width_in}in" '
        f'height="{page_height_in}in" viewBox="0 0 {page_width_in} {page_height_in}">',
        '<style>.cut{fill:none;stroke:#000;stroke-width:0.006}'
        '.title{font:bold 0.12px Arial;text-anchor:middle}'
        '.sub{font:0.075px Arial;text-anchor:middle}</style>'
    ]

    r = label_diameter_in/2
    hr = center_hole_diameter_in/2
    for row in range(rows):
        for col in range(columns):
            cx = margin_x + (col+0.5)*dx
            cy = margin_y + (row+0.5)*dy
            out.append(f'<circle class="cut" cx="{cx:.4f}" cy="{cy:.4f}" r="{r:.4f}"/>')
            out.append(f'<circle class="cut" cx="{cx:.4f}" cy="{cy:.4f}" r="{hr:.4f}"/>')
            out.append(f'<text class="title" x="{cx:.4f}" y="{cy-0.08:.4f}">{title}</text>')
            if subtitle:
                out.append(f'<text class="sub" x="{cx:.4f}" y="{cy+0.09:.4f}">{subtitle}</text>')
    out.append('</svg>')
    return "\n".join(out) + "\n"

def write_label_sheet_svg(path: str | Path, title: str, subtitle: str = "", **kwargs):
    Path(path).write_text(
        build_label_sheet_svg(title, subtitle, **kwargs),
        encoding="utf-8"
    )
