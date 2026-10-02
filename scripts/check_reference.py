"""Check a scanned reference disk and optionally its audio without changing CAD.

Run with PYTHONPATH=src and the optional analysis dependencies installed.
Results describe optical measurements; record calibration and measurement
confidence before selecting prototype dimensions.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image
from scipy import ndimage, optimize, signal
from scipy.io import wavfile

from symphonium_disc_maker.geometry import drive_hole_vertices, load_geometry, track_radius


def file_identity(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"path": str(path.resolve()), "sha256": digest.hexdigest()}


def fit_disc(gray, threshold):
    labels, _ = ndimage.label(gray < threshold)
    counts = np.bincount(labels.ravel())
    counts[0] = 0
    if counts.max() < 1000:
        raise ValueError("no sufficiently large dark disk component found")
    solid = ndimage.binary_fill_holes(labels == counts.argmax())
    del labels, counts
    y, x = np.nonzero(solid & ~ndimage.binary_erosion(solid))
    mx, my = x.mean(), y.mean()
    u, v = x - mx, y - my
    a, b, c = np.linalg.lstsq(
        np.column_stack([2 * u, 2 * v, np.ones(len(u))]), u * u + v * v, rcond=None,
    )[0]
    fit = optimize.least_squares(
        lambda p: np.hypot(x - p[0], y - p[1]) - p[2],
        [mx + a, my + b, np.sqrt(c + a * a + b * b)],
    )
    return solid, {
        "center_x_pixels": float(fit.x[0]), "center_y_pixels": float(fit.x[1]),
        "radius_pixels": float(fit.x[2]),
        "boundary_residual_rms_pixels": float(np.sqrt(np.mean(fit.fun**2))),
    }


def detect_holes(gray, solid, fit, threshold, pixels_per_inch):
    labels, _ = ndimage.label((gray > threshold) & solid)
    holes = []
    area_scale = (pixels_per_inch / 600)**2
    for number, box in enumerate(ndimage.find_objects(labels), 1):
        if box is None:
            continue
        yy, xx = np.nonzero(labels[box] == number)
        area = len(xx)
        if not 400 * area_scale <= area <= 20000 * area_scale:
            continue
        x, y = xx + box[1].start, yy + box[0].start
        cx, cy = float(x.mean()), float(y.mean())
        z = (x - cx) - 1j * (y - cy)
        theta = math.atan2(fit["center_y_pixels"] - cy, cx - fit["center_x_pixels"])
        radius = math.hypot(cx - fit["center_x_pixels"], cy - fit["center_y_pixels"])
        fraction = radius / fit["radius_pixels"]
        kind = ("drive" if .92 < fraction < .985 else
                "note" if .15 < fraction < .92 else
                "center" if fraction < .05 else "other")
        # An axis-aligned filled square has a negative-real fourth moment.
        # Its phase therefore gives orientation modulo 90 degrees.
        orientation = float(np.angle(-np.mean(z**4)) / 4)
        local = z * np.exp(-1j * theta)
        holes.append({
            "kind": kind, "x_pixels": cx, "y_pixels": cy, "area_pixels": area,
            "radius_in": radius / pixels_per_inch, "theta_radians": theta,
            "square_orientation_radians": orientation,
            "radial_extent_in": float(np.ptp(local.real) + 1) / pixels_per_inch,
            "tangential_extent_in": float(np.ptp(local.imag) + 1) / pixels_per_inch,
            "area_equivalent_circle_diameter_in": 2 * math.sqrt(area / math.pi) / pixels_per_inch,
        })
    return holes


def wrap_square_angle(angle):
    return (angle + math.pi / 4) % (math.pi / 2) - math.pi / 4


def drive_edge_profiles(image, hole, smoothing_pixels=1):
    """Sample central strips in the hole's local axes, including shaded edges."""
    distance = np.arange(-45, 45.125, .25)
    offsets = np.arange(-8, 9)
    cx, cy = hole["x_pixels"], hole["y_pixels"]
    theta = hole["theta_radians"]
    cosine, sine = math.cos(theta), math.sin(theta)
    left, top = int(cx) - 80, int(cy) - 80
    source = np.asarray(image.crop((left, top, left + 161, top + 161)).convert("RGB"))
    result = {}
    for axis in ("radial", "tangential"):
        u, v = np.broadcast_arrays(distance[None, :], offsets[:, None])
        if axis == "tangential":
            u, v = v, u
        x = cx + u * cosine - v * sine - left
        y = cy - u * sine - v * cosine - top
        samples = np.stack([
            ndimage.map_coordinates(source[:, :, channel], [y, x], order=1, output=float)
            for channel in range(3)
        ], axis=-1)
        rgb = np.median(samples, axis=0)
        gray = rgb @ np.array([.299, .587, .114])
        derivative = ndimage.gaussian_filter1d(gray, smoothing_pixels / .25, order=1) / .25
        edges = []
        for side in (-1, 1):
            mask = (distance * side > 15) & (distance * side < 40)
            edges.append(float(distance[mask][np.argmin(side * derivative[mask])]))
        result[axis] = {"gray": gray, "edges_pixels": edges,
                        "width_pixels": edges[1] - edges[0]}
    return distance, result


def check_opposite_drive_edges(image, holes, pixels_per_inch, output):
    """Use opposite quadrants and edges perpendicular to the scanner shadow.

    The shaded edge moves inward in a bright-region mask. Horizontal crossings
    near the cardinal positions avoid it: radial at left/right, tangent at
    top/bottom. Opposite groups independently check the inferred dimensions.
    Quarter-pixel sampling interpolates the scan; it does not add resolution.
    """
    ring = [hole for hole in holes if hole["kind"] == "drive"]
    groups = []
    for name, angle, axis in (("right", 0, "radial"), ("left", math.pi, "radial"),
                              ("top", math.pi / 2, "tangential"),
                              ("bottom", -math.pi / 2, "tangential")):
        group = [hole for hole in ring if abs(math.atan2(
            math.sin(hole["theta_radians"] - angle),
            math.cos(hole["theta_radians"] - angle),
        )) < math.radians(10)]
        checks = []
        for smoothing in (.5, 1, 1.5):
            widths = [drive_edge_profiles(image, hole, smoothing)[1][axis]["width_pixels"]
                      for hole in group]
            checks.append({"smoothing_pixels": smoothing,
                           "median_width_pixels": float(np.median(widths)),
                           "median_width_in": float(np.median(widths)) / pixels_per_inch,
                           "p10_p90_width_pixels": np.percentile(widths, [10, 90]).tolist()})
        groups.append({"quadrant": name, "measured_axis": axis, "hole_count": len(group),
                       "edge_checks": checks})
    combined = {}
    for axis in ("radial", "tangential"):
        widths = []
        for hole in ring:
            projection = (abs(math.sin(hole["theta_radians"])) if axis == "radial"
                          else abs(math.cos(hole["theta_radians"])))
            if projection < math.sin(math.radians(10)):
                widths.append(drive_edge_profiles(image, hole)[1][axis]["width_pixels"])
        combined[axis] = {"hole_count": len(widths),
                          "median_width_pixels": float(np.median(widths)),
                          "median_width_in": float(np.median(widths)) / pixels_per_inch}

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 4, figsize=(14, 9))
    representatives = []
    for column, target in enumerate((math.pi / 2, -math.pi / 2, 0, math.pi)):
        hole = min(ring, key=lambda h: abs(math.atan2(
            math.sin(h["theta_radians"] - target), math.cos(h["theta_radians"] - target))))
        representatives.append(hole)
        cx, cy = int(hole["x_pixels"]), int(hole["y_pixels"])
        ax = axes[0, column]
        ax.imshow(image.crop((cx - 48, cy - 48, cx + 49, cy + 49)), interpolation="nearest")
        ax.set_title(f"{math.degrees(hole['theta_radians']):.2f} degrees")
        ax.set_axis_off()
        distance, profiles = drive_edge_profiles(image, hole)
        for row, axis in enumerate(("radial", "tangential"), 1):
            ax = axes[row, column]
            profile = profiles[axis]
            ax.plot(distance, profile["gray"], color="#444444")
            for edge in profile["edges_pixels"]:
                ax.axvline(edge, color="#009688", linestyle="--", linewidth=.8)
            theta = hole["theta_radians"]
            projection = abs(math.sin(theta)) if axis == "radial" else abs(math.cos(theta))
            use = "across shadow" if projection < math.sin(math.radians(10)) else "along shadow"
            ax.set_title(f"{axis}: {profile['width_pixels']:.2f} px ({use})", fontsize=10)
            ax.set_ylim(0, 270)
            ax.grid(alpha=.2)
            if row == 2:
                ax.set_xlabel("Local distance from bright-region centroid (pixels)", fontsize=8)
    fig.suptitle("Opposite drive holes: shadow stays downward in scanner coordinates\n"
                 "Use edges across the shadow: radial at left/right; tangential at top/bottom")
    fig.tight_layout(rect=(0, 0, 1, .94))
    fig.savefig(output / "drive_opposites.png", dpi=180)
    plt.close(fig)
    separations = []
    for first, second in ((0, 1), (2, 3)):
        separation = abs(math.atan2(
            math.sin(representatives[first]["theta_radians"] - representatives[second]["theta_radians"]),
            math.cos(representatives[first]["theta_radians"] - representatives[second]["theta_radians"])))
        separations.append(math.degrees(separation))
    return {"method": "median central-strip grayscale edge gradients; +/-10 degree cardinal groups; opposite groups and 0.5/1/1.5-pixel smoothing cross-checks",
            "shadow_direction": "downward in scanner image coordinates; qualitative from paired crops",
            "limits": "scan edge estimates, not exact tool tolerances; allow roughly 1-2 source pixels for boundary choice; odd 143-hole ring has no exactly opposite hole",
            "representative_opposite_separations_degrees": separations,
            "opposite_groups": groups, "combined_across_shadow_dimensions": combined}


def summarize_holes(holes, geometry, pixels_per_inch):
    drive = geometry["drive_ring"]
    ns = geometry["note_system"]
    ring = [hole for hole in holes if hole["kind"] == "drive"]
    notes = [hole for hole in holes if hole["kind"] == "note"]
    if not ring or not notes:
        raise ValueError("drive or note holes were not detected")
    angles = np.array([hole["theta_radians"] for hole in ring])
    count = int(drive["hole_count"])
    pitch = 2 * math.pi / count
    phase = float(np.angle(np.exp(1j * count * angles).mean()) / count)
    indices = np.rint((angles - phase) / pitch).astype(int) % count
    angular_residual = (angles - phase - indices * pitch + math.pi) % (2 * math.pi) - math.pi
    orientation_residual = np.array([
        wrap_square_angle(hole["square_orientation_radians"] - hole["theta_radians"])
        for hole in ring
    ])
    drive_residual = np.array([hole["radius_in"] - drive["center_radius"] for hole in ring])
    for hole in notes:
        track = round((hole["radius_in"] - ns["inner_track_center_radius"]) / ns["track_pitch"]) + 1
        if not 1 <= track <= ns["track_count"]:
            raise ValueError(f"detected note assigned outside track range: {track}")
        hole["track"] = track
        hole["note"] = ns["notes_inner_to_outer"][track - 1]
        hole["track_residual_in"] = hole["radius_in"] - track_radius(geometry, track)
    note_residual = np.array([hole["track_residual_in"] for hole in notes])
    return {
        "component_counts": dict(Counter(hole["kind"] for hole in holes)),
        "occupied_tracks": dict(sorted(Counter(hole["track"] for hole in notes).items())),
        "drive_ring_phase_degrees": math.degrees(phase),
        "unique_drive_positions": len(set(indices)),
        "drive_angular_residual_rms_degrees": float(np.sqrt(np.mean(angular_residual**2)) * 180 / math.pi),
        "radial_tangential_orientation_mean_absolute_residual_degrees": float(np.mean(abs(orientation_residual)) * 180 / math.pi),
        "axis_aligned_orientation_mean_absolute_residual_degrees": float(np.mean([
            abs(wrap_square_angle(hole["square_orientation_radians"])) for hole in ring
        ]) * 180 / math.pi),
        "drive_radius_mean_in": float(np.mean([hole["radius_in"] for hole in ring])),
        "drive_radius_residual_rms_in": float(np.sqrt(np.mean(drive_residual**2))),
        "note_track_residual_rms_in": float(np.sqrt(np.mean(note_residual**2))),
        "note_track_residual_max_absolute_in": float(np.max(abs(note_residual))),
        "optical_drive_area_equivalent_side_median_in": float(np.median([
            math.sqrt(hole["area_pixels"]) for hole in ring
        ])) / pixels_per_inch,
        "optical_drive_radial_extent_median_in": float(np.median([hole["radial_extent_in"] for hole in ring])),
        "optical_drive_tangential_extent_median_in": float(np.median([hole["tangential_extent_in"] for hole in ring])),
        "optical_note_circle_diameter_median_in": float(np.median([
            hole["area_equivalent_circle_diameter_in"] for hole in notes
        ])),
    }


def check_audio(path, holes, geometry, output):
    decoded = output / "reference_audio.wav"
    subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-i", str(path),
        "-ac", "1", "-ar", "24000", "-y", str(decoded),
    ], check=True)
    sample_rate, audio = wavfile.read(decoded)
    audio = audio.astype(float) / 32768
    frequencies, times, spectrum = signal.stft(
        audio, fs=sample_rate, nperseg=4096, noverlap=4096 - 240, boundary="zeros",
    )
    energy = abs(spectrum)**2
    semitones = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    channels = []
    for note in geometry["note_system"]["notes_inner_to_outer"]:
        midi = 12 * (int(note[-1]) + 1) + semitones[note[0]]
        fundamental = 440 * 2**((midi - 69) / 12)
        strength = np.zeros(len(times))
        for harmonic, weight in [(1, 1), (2, .35), (3, .15)]:
            frequency = fundamental * harmonic
            band = np.abs(frequencies - frequency) < max(12, frequency * .025)
            strength += weight * energy[band].sum(axis=0)
        strength = np.log1p(strength / max(np.percentile(strength, 75), 1e-12))
        onset = np.maximum(0, strength - np.roll(strength, 3))
        onset[:3] = 0
        channels.append(onset)
    channels = np.asarray(channels)
    notes = [hole for hole in holes if hole["kind"] == "note"]
    nominal_period = geometry["timing"]["measured_revolution_seconds"]
    results = []
    curves = None
    for period in sorted(set([28.08, 28.1, 28.12, nominal_period, 28.14, 28.16])):
        bins = round(period / .01)
        folded = np.zeros((len(channels), bins))
        phase_bin = np.floor((times % period) / period * bins).astype(int)
        for channel in range(len(channels)):
            np.add.at(folded[channel], phase_bin, channels[channel])
        # Periodic smoothing avoids introducing an arbitrary seam at phase zero.
        folded = sum(np.roll(folded, shift, axis=1) for shift in range(-2, 3)) / 5
        folded = ((folded - folded.mean(axis=1, keepdims=True))
                  / np.maximum(folded.std(axis=1, keepdims=True), 1e-12))
        hypotheses = {}
        period_curves = {}
        for direction, label in [(1, "increasing_angle"), (-1, "decreasing_angle")]:
            curve = np.zeros(bins)
            for hole in notes:
                event_bin = round((direction * hole["theta_radians"] / (2 * math.pi) % 1) * bins) % bins
                curve += np.roll(folded[hole["track"] - 1], -event_bin)
            best = int(curve.argmax())
            hypotheses[label] = {"score": float(curve[best]), "phase_seconds": best / bins * period}
            period_curves[label] = curve
        results.append({"period_seconds": period, "hypotheses": hypotheses})
        if period == nominal_period:
            curves = (np.arange(bins) / bins * period, period_curves)
    return {
        "source": file_identity(path), "decoded_duration_seconds": len(audio) / sample_rate,
        "method": "pitch-specific positive log-energy differences; folded across revolutions; unit-standard-deviation channels; summed onset evidence at scanned holes",
        "limits": "uses the provisional pitch map; scores are descriptive, not statistical significance or a full transcription; fitted phase is not a mechanical reader angle",
        "period_checks": results,
    }, curves


def plot_overlay(image, fit, pixels_per_inch, holes, summary, geometry, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon
    cx, cy, radius = fit["center_x_pixels"], fit["center_y_pixels"], fit["radius_pixels"]
    bounds = (int(cx - radius - 45), int(cy - radius - 45),
              int(cx + radius + 45), int(cy + radius + 45))
    background = image.crop(bounds)
    background.thumbnail((1700, 1700))
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(background, extent=(bounds[0], bounds[2], bounds[3], bounds[1]))
    phase = math.radians(summary["drive_ring_phase_degrees"])
    cosine, sine = math.cos(phase), math.sin(phase)
    for i in range(geometry["drive_ring"]["hole_count"]):
        vertices = [(cx + pixels_per_inch * (x * cosine - y * sine),
                     cy - pixels_per_inch * (x * sine + y * cosine))
                    for x, y in drive_hole_vertices(geometry, i)]
        ax.add_patch(Polygon(vertices, fill=False, edgecolor="#00e5ff", linewidth=.55))
    for track in range(1, geometry["note_system"]["track_count"] + 1):
        ax.add_patch(Circle((cx, cy), track_radius(geometry, track) * pixels_per_inch,
                            fill=False, edgecolor="#b388ff", linewidth=.45, alpha=.8))
    ax.add_patch(Circle((cx, cy), geometry["disc"]["center_hole_diameter"] / 2 * pixels_per_inch,
                        fill=False, edgecolor="#00e5ff", linewidth=.7))
    notes = [hole for hole in holes if hole["kind"] == "note"]
    ax.scatter([hole["x_pixels"] for hole in notes], [hole["y_pixels"] for hole in notes],
               marker="+", s=7, linewidths=.5, color="#40ff70")
    ax.set_title("Original scan with CAD drive openings and note tracks\n"
                 "Cyan: CAD cut edges   Purple: track centers   Green: detected music holes", fontsize=11)
    ax.set_aspect("equal")
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(output / "scan_overlay.png", dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--audio", type=Path)
    parser.add_argument("--geometry", type=Path, default=Path("geometry.json"))
    parser.add_argument("--output", type=Path, default=Path("output/reference_check"))
    parser.add_argument("--disc-threshold", type=int, default=140)
    parser.add_argument("--hole-thresholds", type=int, nargs="+", default=[150, 170])
    args = parser.parse_args()
    if any(not 0 < value < 255 for value in [args.disc_threshold, *args.hole_thresholds]):
        parser.error("thresholds must be between 1 and 254")
    args.output.mkdir(parents=True, exist_ok=True)
    geometry = load_geometry(args.geometry)
    image = Image.open(args.scan)
    gray = np.asarray(image.convert("L"))
    solid, fit = fit_disc(gray, args.disc_threshold)
    pixels_per_inch = 2 * fit["radius_pixels"] / geometry["disc"]["diameter"]
    report = {
        "scan_source": file_identity(args.scan), "geometry_source": file_identity(args.geometry),
        "image_size_pixels": list(image.size), "metadata_dpi": image.info.get("dpi"),
        "disc_threshold": args.disc_threshold, "outer_circle_fit": fit,
        "scale": {"pixels_per_inch": pixels_per_inch,
                  "basis": "fitted outer diameter calibrated to measured disk diameter",
                  "measured_disc_diameter_in": geometry["disc"]["diameter"]},
        "limits": "optical centroids and edges depend on threshold, shadows, and scan calibration; CAD dimensions are not changed",
        "hole_threshold_checks": [],
    }
    selected = None
    for threshold in args.hole_thresholds:
        holes = detect_holes(gray, solid, fit, threshold, pixels_per_inch)
        summary = summarize_holes(holes, geometry, pixels_per_inch)
        report["hole_threshold_checks"].append({"hole_threshold": threshold, **summary})
        if selected is None:
            selected = (holes, summary)
    holes, summary = selected
    if summary["component_counts"].get("drive") != geometry["drive_ring"]["hole_count"]:
        raise ValueError("drive-hole count does not match geometry; inspect detection before using this report")
    if summary["unique_drive_positions"] != geometry["drive_ring"]["hole_count"]:
        raise ValueError("drive holes do not match unique regular-ring positions")
    report["selected_hole_threshold"] = args.hole_thresholds[0]
    report["opposite_drive_edge_check"] = check_opposite_drive_edges(
        image, holes, pixels_per_inch, args.output)
    (args.output / "detected_holes.json").write_text(json.dumps(holes, indent=2) + "\n")
    fields = sorted(set().union(*(hole.keys() for hole in holes)))
    with (args.output / "detected_holes.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(holes)
    plot_overlay(image, fit, pixels_per_inch, holes, summary, geometry, args.output)
    if args.audio:
        report["audio_direction_check"], curves = check_audio(args.audio, holes, geometry, args.output)
        import matplotlib.pyplot as plt
        phases, scores = curves
        fig, ax = plt.subplots(figsize=(10, 4))
        for label, curve in scores.items():
            ax.plot(phases, curve, label=label.replace("_", " "))
        ax.set(xlabel="Recording phase offset within a revolution (seconds)",
               ylabel="Summed normalized onset evidence", title="Audio evidence for chronological hole direction")
        ax.legend()
        fig.tight_layout()
        fig.savefig(args.output / "audio_direction.png", dpi=160)
        plt.close(fig)
        np.savetxt(args.output / "audio_direction.csv", np.column_stack([
            phases, scores["increasing_angle"], scores["decreasing_angle"],
        ]), delimiter=",", header="phase_seconds,increasing_angle,decreasing_angle", comments="")
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if args.audio:
        print(json.dumps(report["audio_direction_check"]["period_checks"], indent=2))
    print(f"Saved report, detected holes, and figures to {args.output}")


if __name__ == "__main__":
    main()
