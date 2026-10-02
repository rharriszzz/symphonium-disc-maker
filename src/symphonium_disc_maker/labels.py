from __future__ import annotations
from pathlib import Path
import html
import math

def _label_layout(
    title: str,
    subtitle: str = "",
    *,
    label_diameter_in: float = 1.50,
    center_hole_diameter_in: float = 0.200,
    columns: int = 4,
    rows: int = 5,
    page_width_in: float = 8.5,
    page_height_in: float = 11.0,
    mode: str = "combined",
) -> dict:
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

    return {
        "width": page_width_in, "height": page_height_in, "mode": mode,
        "radius": r, "hole_radius": hr, "title_y": title_y, "subtitle_y": sub_y,
        "title_size": title_size, "subtitle_size": sub_size,
        "centers": [(margin_x + (col + .5) * dx, margin_y + (row + .5) * dy)
                    for row in range(rows) for col in range(columns)],
    }


def build_label_sheet_svg(title: str, subtitle: str = "", **kwargs) -> str:
    layout = _label_layout(title, subtitle, **kwargs)
    mode = layout["mode"]

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{layout["width"]}in" '
        f'height="{layout["height"]}in" viewBox="0 0 {layout["width"]} {layout["height"]}">',
        '<style>.cut{fill:none;stroke:#000;stroke-width:0.006}'
        f'.title{{font:bold {layout["title_size"]:.6f}px Arial;text-anchor:middle}}'
        f'.sub{{font:{layout["subtitle_size"]:.6f}px Arial;text-anchor:middle}}</style>'
    ]

    cuts = ['<g id="cut">']
    artwork = ['<g id="artwork">']
    for cx, cy in layout["centers"]:
        cuts.append(f'<circle class="cut" cx="{cx:.4f}" cy="{cy:.4f}" r="{layout["radius"]:.4f}"/>')
        if layout["hole_radius"]:
            cuts.append(f'<circle class="cut" cx="{cx:.4f}" cy="{cy:.4f}" r="{layout["hole_radius"]:.4f}"/>')
        artwork.append(f'<text class="title" x="{cx:.4f}" y="{cy+layout["title_y"]:.4f}">{html.escape(title)}</text>')
        if subtitle:
            artwork.append(f'<text class="sub" x="{cx:.4f}" y="{cy+layout["subtitle_y"]:.4f}">{html.escape(subtitle)}</text>')
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


def build_label_sheet_pdf(title: str, subtitle: str = "", *, calibration=False, **kwargs) -> bytes:
    """Vector PDF at physical page size using the same layout as the SVG.

    Matplotlib is optional and imported only for PDF output. Calibration adds
    a one-inch ruler and printing instructions outside the label positions.
    """
    import io
    try:
        from matplotlib.backends.backend_pdf import FigureCanvasPdf
        from matplotlib.figure import Figure
        from matplotlib.patches import Circle
    except ImportError as exc:
        raise ValueError("PDF output needs Matplotlib; install this project with pip install -e '.[print]'") from exc
    layout = _label_layout(title, subtitle, **kwargs)
    width, height = layout["width"], layout["height"]
    if calibration and (width < 3 or height < 3):
        raise ValueError("calibration ruler requires a page at least 3 inches wide and tall")
    figure = Figure(figsize=(width, height))
    axes = figure.add_axes([0, 0, 1, 1], xlim=(0, width), ylim=(0, height))
    axes.set_axis_off()
    for cx, cy in layout["centers"]:
        cy = height - cy
        if layout["mode"] != "print":
            for radius in (layout["radius"], layout["hole_radius"]):
                if radius:
                    axes.add_patch(Circle((cx, cy), radius, fill=False, edgecolor="black", linewidth=.006*72))
        if layout["mode"] != "cut":
            axes.text(cx, cy - layout["title_y"], title, ha="center", va="baseline",
                      family="DejaVu Sans", weight="bold", fontsize=layout["title_size"]*72,
                      parse_math=False, usetex=False)
            if subtitle:
                axes.text(cx, cy - layout["subtitle_y"], subtitle, ha="center", va="baseline",
                          family="DejaVu Sans", fontsize=layout["subtitle_size"]*72,
                          parse_math=False, usetex=False)
    if calibration:
        axes.text(width/2, height-.4, "Print at actual size / 100%. Disable Fit or Shrink.",
                  ha="center", va="baseline", fontsize=8, family="DejaVu Sans")
        axes.plot([.6, 1.6], [.35, .35], color="black", linewidth=.7)
        for x in (.6, 1.6):
            axes.plot([x, x], [.29, .41], color="black", linewidth=.7)
        axes.text(1.1, .48, "1 inch / 25.4 mm", ha="center", va="baseline", fontsize=7,
                  family="DejaVu Sans")
    stream = io.BytesIO()
    FigureCanvasPdf(figure).print_pdf(stream, metadata={"Title": title, "CreationDate": None, "ModDate": None})
    return stream.getvalue()


def write_label_sheet_pdf(path: str | Path, title: str, subtitle: str = "", **kwargs):
    Path(path).write_bytes(build_label_sheet_pdf(title, subtitle, **kwargs))
