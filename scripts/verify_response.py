"""Independently check the supplied ChatGPT shape and pitch-map conclusions.

Requires the optional analysis dependencies and ffmpeg. Original files and CAD
dimensions are unchanged. Run from the repository root with PYTHONPATH=src.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image
from scipy import ndimage, signal
from scipy.io import wavfile

if __package__:
    from .check_reference import detect_holes, file_identity, fit_disc, summarize_holes
else:
    from check_reference import detect_holes, file_identity, fit_disc, summarize_holes
from symphonium_disc_maker.geometry import load_geometry


def ellipse_axes(x, y):
    """Fit a general ellipse to boundary points with a normalized conic fit."""
    origin = np.array([np.mean(x), np.mean(y)])
    scale = np.sqrt(np.mean((x - origin[0])**2 + (y - origin[1])**2))
    u, v = (x - origin[0]) / scale, (y - origin[1]) / scale
    a, b, c, d, e = np.linalg.lstsq(
        np.column_stack([u*u, u*v, v*v, u, v]), np.ones(len(x)), rcond=None,
    )[0]
    q = np.array([[a, b/2], [b/2, c]])
    center = -.5 * np.linalg.solve(q, [d, e])
    eigenvalues = np.linalg.eigvalsh(q)
    constant = 1 + center @ q @ center
    if np.any(eigenvalues <= 0) or constant <= 0:
        raise ValueError("boundary does not fit an ellipse")
    axes = np.sqrt(constant / eigenvalues) * scale
    return {"semimajor_pixels": float(axes.max()), "semiminor_pixels": float(axes.min()),
            "axis_ratio": float(axes.max() / axes.min()),
            "axis_difference_percent": float((axes.max() / axes.min() - 1) * 100)}


def central_width(coordinates, profile, threshold):
    """Interpolated crossings of the bright component containing coordinate zero.

    Neighboring drive holes or the outside paper must not extend this component.
    """
    center = int(np.argmin(abs(coordinates)))
    if profile[center] <= threshold:
        raise ValueError("central profile does not exceed threshold")
    left = right = center
    while left > 0 and profile[left - 1] > threshold:
        left -= 1
    while right < len(profile) - 1 and profile[right + 1] > threshold:
        right += 1
    if left == 0 or right == len(profile) - 1:
        raise ValueError("central bright component extends beyond sampled profile")
    def crossing(i, j):
        return coordinates[i] + ((threshold - profile[i]) / (profile[j] - profile[i])
                                  * (coordinates[j] - coordinates[i]))
    return float(crossing(right, right + 1) - crossing(left - 1, left))


def ensemble_check(image, gray, holes, output, provided_profiles):
    ring = [hole for hole in holes if hole["kind"] == "drive"]
    coordinates = np.arange(-80, 81, dtype=float)
    radial, tangent = np.meshgrid(coordinates, coordinates)
    total = np.zeros(radial.shape)
    for hole in ring:
        cx, cy, theta = hole["x_pixels"], hole["y_pixels"], hole["theta_radians"]
        left, top = int(cx) - 120, int(cy) - 120
        patch = np.asarray(image.crop((left, top, left + 241, top + 241)).convert("L"))
        x = cx + radial * math.cos(theta) - tangent * math.sin(theta) - left
        y = cy - radial * math.sin(theta) - tangent * math.cos(theta) - top
        total += ndimage.map_coordinates(patch, [y, x], order=1, output=float)
    average = total / len(ring)
    center = len(coordinates) // 2
    radial_profile, tangent_profile = average[center, :], average[:, center]
    checks = []
    for threshold in (130, 150, 170, 190):
        width_r = central_width(coordinates, radial_profile, threshold)
        width_t = central_width(coordinates, tangent_profile, threshold)
        checks.append({"threshold": threshold, "radial_width_pixels": width_r,
                       "tangential_width_pixels": width_t, "aspect_ratio": width_r / width_t})
    np.savetxt(output / "aligned_drive_profiles.csv",
               np.column_stack([coordinates, radial_profile, tangent_profile]), delimiter=",",
               header="coord_px,radial_profile,tangential_profile", comments="")
    ellipse_checks = []
    for threshold in (140, 160, 180):
        solid, _ = fit_disc(gray, threshold)
        y, x = np.nonzero(solid & ~ndimage.binary_erosion(solid))
        ellipse_checks.append({"disc_threshold": threshold, **ellipse_axes(x, y)})

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].imshow(average, extent=(-80.5, 80.5, 80.5, -80.5), cmap="gray", vmin=0, vmax=255)
    axes[0].set(xlim=(-40, 40), ylim=(40, -40), xlabel="Radial coordinate (pixels)",
                ylabel="Tangential coordinate (pixels)", title="143 aligned drive openings")
    axes[1].plot(coordinates, radial_profile, label="Local radial")
    axes[1].plot(coordinates, tangent_profile, label="Local tangential")
    supplied = None
    if provided_profiles:
        data = np.genfromtxt(provided_profiles, names=True, delimiter=",")
        axes[1].plot(data["coord_px"], data["radial_profile"], "--", alpha=.6, label="Supplied radial")
        axes[1].plot(data["coord_px"], data["tangential_profile"], "--", alpha=.6, label="Supplied tangential")
        supplied = {"source": file_identity(provided_profiles), "threshold_width_checks": []}
        for threshold in (130, 150, 170, 190):
            r = central_width(data["coord_px"], data["radial_profile"], threshold)
            t = central_width(data["coord_px"], data["tangential_profile"], threshold)
            supplied["threshold_width_checks"].append({"threshold": threshold,
                "radial_width_pixels": r, "tangential_width_pixels": t, "aspect_ratio": r/t})
    axes[1].set(xlim=(-40, 40), xlabel="Local coordinate (pixels)", ylabel="Average grayscale",
                title="Central-opening profiles; neighboring holes excluded")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(output / "drive_ensemble.png", dpi=180)
    plt.close(fig)
    return {"aligned_hole_count": len(ring), "threshold_width_checks": checks,
            "outer_ellipse_checks": ellipse_checks, "supplied_profile_check": supplied,
            "limits": "ensemble bright-interior crossings support shape ratio, not absolute cut size; ellipse variation combines scan scaling and actual disk shape"}


def midi_name(midi):
    return ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][midi % 12] + str(midi // 12 - 1)


def folded_onsets(energy, frequencies, times, midis, period, harmonics, time_window=None):
    bins = round(period / .01)
    folded = np.zeros((len(midis), bins))
    included = np.ones(len(times), dtype=bool)
    if time_window:
        included = (times >= time_window[0]) & (times < time_window[1])
    phase_bin = np.floor((times[included] % period) / period * bins).astype(int)
    for channel, midi in enumerate(midis):
        fundamental = 440 * 2**((midi - 69) / 12)
        strength = np.zeros(len(times))
        for harmonic, weight in harmonics:
            frequency = fundamental * harmonic
            band = abs(frequencies - frequency) < max(12, frequency * .025)
            strength += weight * energy[band].sum(axis=0)
        strength = np.log1p(strength / max(np.percentile(strength, 75), 1e-12))
        onset = np.maximum(0, strength - np.roll(strength, 3))
        onset[:3] = 0
        np.add.at(folded[channel], phase_bin, onset[included])
    folded = sum(np.roll(folded, shift, axis=1) for shift in range(-2, 3)) / 5
    return ((folded - folded.mean(axis=1, keepdims=True))
            / np.maximum(folded.std(axis=1, keepdims=True), 1e-12))


def map_curve(folded, holes, start_channel):
    bins = folded.shape[1]
    curve = np.zeros(bins)
    for hole in holes:
        event = round((-hole["theta_radians"] / (2 * math.pi) % 1) * bins) % bins
        curve += np.roll(folded[start_channel + hole["track"] - 1], -event)
    return curve


def rank_pitch_maps(folded, holes, candidates, midis, period, held_out=None):
    results = []
    for start in candidates:
        channel = midis.index(start)
        curve = map_curve(folded, holes, channel)
        phase = int(curve.argmax())
        row = {"start_pitch": midi_name(start), "last_occupied_pitch": midi_name(midis[channel + 18]),
               "score": float(curve[phase]), "phase_seconds": phase / len(curve) * period}
        if held_out is not None:
            row["held_out_score_at_training_phase"] = float(map_curve(held_out, holes, channel)[phase])
        results.append(row)
    return sorted(results, key=lambda row: row["score"], reverse=True)


def pitch_map_check(path, holes, geometry, output):
    decoded = output / "reference_audio.wav"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path),
                    "-ac", "1", "-ar", "24000", "-y", str(decoded)], check=True)
    sample_rate, audio = wavfile.read(decoded)
    audio = audio.astype(float) / 32768
    # C2..C5 starts: all 22 consecutive white-key sequences in this range.
    midis = [m for m in range(36, 106) if m % 12 in (0, 2, 4, 5, 7, 9, 11)]
    candidates = [m for m in midis if m <= 72]
    notes = [hole for hole in holes if hole["kind"] == "note"]
    period = geometry["timing"]["measured_revolution_seconds"]
    trials = []
    for window_size in (4096, 8192):
        frequencies, times, spectrum = signal.stft(
            audio, fs=sample_rate, nperseg=window_size, noverlap=window_size - 240, boundary="zeros")
        energy = abs(spectrum)**2
        for name, harmonics in (("fundamental_only", [(1, 1)]),
                                ("fundamental_and_harmonics", [(1, 1), (2, .35), (3, .15)])):
            folded = folded_onsets(energy, frequencies, times, midis, period, harmonics)
            ranking = rank_pitch_maps(folded, notes, candidates, midis, period)
            first = folded_onsets(energy, frequencies, times, midis, period, harmonics, (0, period))
            second = folded_onsets(energy, frequencies, times, midis, period, harmonics, (period, 2*period))
            train = rank_pitch_maps(first, notes, candidates, midis, period, held_out=second)
            second_rank = rank_pitch_maps(second, notes, candidates, midis, period)
            trials.append({"fft_window_samples": window_size, "frequency_evidence": name,
                           "full_recording_ranking": ranking, "first_revolution_ranking": train,
                           "second_revolution_ranking": second_rank})
    primary = trials[1]["full_recording_ranking"]
    with (output / "pitch_map_candidates.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(primary[0]))
        writer.writeheader()
        writer.writerows(primary)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar([r["start_pitch"] for r in primary], [r["score"] for r in primary], color="#287b8e")
    ax.set(xlabel="First occupied track pitch (consecutive white keys outward)",
           ylabel="Best summed onset score", title="Independent pitch-map comparison: full recording, 4096-sample FFT")
    fig.tight_layout()
    fig.savefig(output / "pitch_map_candidates.png", dpi=180)
    plt.close(fig)
    return {"source": file_identity(path), "duration_seconds": len(audio)/sample_rate,
            "candidate_start_count": len(candidates), "period_seconds": period, "trials": trials,
            "assumptions": "consecutive white keys, increasing outward, clockwise chronological hole order; 19 occupied tracks",
            "limits": "descriptive scores with freely fitted phase; octave alternatives can respond to harmonics; not isolated per-tine measurements; track 20 absent from reference"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--geometry", type=Path, default=Path("geometry.json"))
    parser.add_argument("--provided-profiles", type=Path, default=Path("docs/data/aligned_drive_profiles.csv"))
    parser.add_argument("--output", type=Path, default=Path("output/response_check"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    image = Image.open(args.scan)
    gray = np.asarray(image.convert("L"))
    geometry = load_geometry(args.geometry)
    solid, fit = fit_disc(gray, 140)
    scale = 2 * fit["radius_pixels"] / geometry["disc"]["diameter"]
    holes = detect_holes(gray, solid, fit, 150, scale)
    summary = summarize_holes(holes, geometry, scale)
    if summary["component_counts"] != {"drive": 143, "note": 145, "center": 1}:
        raise ValueError("reference hole counts differ; inspect detection")
    report = {"scan_source": file_identity(args.scan), "geometry_source": file_identity(args.geometry),
              "script_source": file_identity(Path(__file__)),
              "ensemble_check": ensemble_check(image, gray, holes, args.output, args.provided_profiles),
              "pitch_map_check": pitch_map_check(args.audio, holes, geometry, args.output)}
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["ensemble_check"], indent=2))
    for trial in report["pitch_map_check"]["trials"]:
        print(json.dumps({key: (value[:3] if isinstance(value, list) else value)
                          for key, value in trial.items()}, indent=2))
    print(f"Saved independent response check to {args.output}")


if __name__ == "__main__":
    main()
