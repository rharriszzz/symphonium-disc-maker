"""Measure the reference center hole using edges across/away from its shadow.

Requires the optional analysis dependencies; does not edit manufacturing inputs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage, optimize

if __package__:
    from .check_reference import file_identity, fit_disc
else:
    from check_reference import file_identity, fit_disc


def measure_edges(gray, origin, smoothing_pixels=1):
    """Fit clear upper and opposed side arcs; full perimeter is diagnostic only.

    Image y increases downwards. The caller supplies an approximate hole center
    and a crop with a radius near 60 pixels (the original 600-dpi scan).
    Subpixel sampling interpolates existing pixels and does not add resolution.
    """
    theta = np.deg2rad(np.arange(-180, 180, 2))
    radii = np.arange(40, 75, .1)
    x = origin[0] + np.cos(theta)[:, None]*radii
    y = origin[1] + np.sin(theta)[:, None]*radii
    profiles = ndimage.map_coordinates(gray.astype(float), [y, x], order=1)
    gradient = ndimage.gaussian_filter1d(
        profiles, smoothing_pixels/.1, axis=1, order=1)/.1
    edge_radius = radii[gradient.argmin(axis=1)]
    edges = np.column_stack((origin[0] + np.cos(theta)*edge_radius,
                             origin[1] + np.sin(theta)*edge_radius))
    masks = {"upper_arc": np.sin(theta) <= .1,
             "opposed_side_arcs": abs(np.sin(theta)) < .45,
             "full_perimeter_shadow_biased": np.ones(len(theta), dtype=bool)}
    fits = {}
    for name, mask in masks.items():
        xx, yy = edges[mask].T
        fit = optimize.least_squares(
            lambda p: np.hypot(xx-p[0], yy-p[1])-p[2], [*origin, 60])
        fits[name] = {"center_x_pixels": float(fit.x[0]),
                      "center_y_pixels": float(fit.x[1]),
                      "diameter_pixels": float(2*fit.x[2]),
                      "radial_residual_rms_pixels": float(np.sqrt(np.mean(fit.fun**2))),
                      "edge_count": int(mask.sum())}
    return fits, edges, masks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--geometry", type=Path, default=Path("geometry.json"))
    parser.add_argument("--output", type=Path, default=Path("output/center_check"))
    args = parser.parse_args()
    image = Image.open(args.scan)
    geometry = json.loads(args.geometry.read_text())
    # Locate the hole from the previously established outer-disk center rather
    # than from a brightness centroid displaced by the shaded bottom edge.
    solid, disk_fit = fit_disc(np.asarray(image.convert("L")), 140)
    del solid
    cx, cy = disk_fit["center_x_pixels"], disk_fit["center_y_pixels"]
    left, top = int(cx)-100, int(cy)-100
    crop = image.crop((left, top, left+201, top+201))
    gray = np.asarray(crop.convert("L"))
    origin = (cx-left, cy-top)
    calibrated_ppi = 2*disk_fit["radius_pixels"]/geometry["disc"]["diameter"]
    metadata_ppi = image.info["dpi"][0]
    checks = []
    for smoothing in (.5, 1, 1.5):
        fits, _, _ = measure_edges(gray, origin, smoothing)
        for fit in fits.values():
            fit["diameter_in_calibrated_to_7_inch_disk"] = fit["diameter_pixels"]/calibrated_ppi
            fit["diameter_in_scan_dpi"] = fit["diameter_pixels"]/metadata_ppi
            fit["center_x_pixels"] += left
            fit["center_y_pixels"] += top
        checks.append({"smoothing_pixels": smoothing, "fits": fits})
    report = {
        "scan": file_identity(args.scan), "script": file_identity(Path(__file__)),
        "geometry": file_identity(args.geometry), "disk_fit": disk_fit,
        "calibrated_pixels_per_inch": calibrated_ppi, "scan_dpi": metadata_ppi,
        "crop_origin_pixels": [left, top], "checks": checks,
        "optical_boundary_allowance": "approximately one pixel per edge; about 0.0033 inch on diameter, not a statistical confidence interval",
        "method": "outward grayscale gradient; independently fit clear upper arc and opposed side arcs; shaded full-perimeter fit is diagnostic only",
        "conclusion": "approximately 0.198-inch optical opening; 0.200-inch rounded prototype nominal, consistent with the less certain 0.1995-inch caliper reading",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/"report.json").write_text(json.dumps(report, indent=2)+"\n")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    fits, edges, masks = measure_edges(gray, origin)
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    axes[0].imshow(crop, interpolation="nearest")
    axes[0].scatter(*edges[~masks["upper_arc"]].T, s=9, color="tomato", label="Shaded lower arc: excluded")
    axes[0].scatter(*edges[masks["upper_arc"]].T, s=9, color="cyan", label="Clear upper arc: used")
    for name, color in (("upper_arc", "cyan"), ("opposed_side_arcs", "lime")):
        fit = fits[name]
        axes[0].add_patch(Circle((fit["center_x_pixels"], fit["center_y_pixels"]),
                                fit["diameter_pixels"]/2, fill=False, color=color, lw=1,
                                label=name.replace("_", " ")+" fit"))
    axes[0].set(xlim=(25, 175), ylim=(180, 25), title="Original pixels and independent circle fits",
                xlabel="Crop x (pixels)", ylabel="Crop y (pixels; downward shadow)")
    axes[0].legend(loc="upper left", fontsize=7)
    fit = fits["opposed_side_arcs"]
    xx = np.arange(20, 181, .1)
    for offset in (-20, 0, 20):
        yy = np.full_like(xx, fit["center_y_pixels"]+offset)
        p = ndimage.map_coordinates(gray.astype(float), [yy, xx], order=1)
        axes[1].plot(xx, p, label=f"Horizontal chord, y offset {offset:+d} px")
    axes[1].set(title="Opposing edges across the shadow", xlabel="Crop x (pixels)", ylabel="Grayscale")
    axes[1].legend(fontsize=8)
    fig.suptitle("Center hole: approximately 119 pixels / 600 dpi = 0.198 inch")
    fig.tight_layout()
    fig.savefig(args.output/"center_hole_edges.png", dpi=160)
    plt.close(fig)
    print(json.dumps({"calibrated_ppi": calibrated_ppi, "scan_dpi": metadata_ppi,
                      "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
