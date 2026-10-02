from __future__ import annotations
import json
import math
from pathlib import Path

def load_geometry(path: str | Path) -> dict:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def track_radius(geometry: dict, track: int) -> float:
    ns = geometry["note_system"]
    if not 1 <= track <= ns["track_count"]:
        raise ValueError(f"track must be 1..{ns['track_count']}")
    return ns["inner_track_center_radius"] + (track - 1) * ns["track_pitch"]

def event_angle_degrees(time_seconds: float, revolution_seconds: float,
                        start_angle_degrees: float) -> float:
    """Top-face polar angle: later events lie clockwise of the arbitrary phase."""
    return start_angle_degrees - 360.0 * time_seconds / revolution_seconds

def drive_hole_vertices(geometry: dict, index: int) -> list[tuple[float, float]]:
    """Return a radial/tangential drive opening in Cartesian inches (y upward)."""
    drive = geometry["drive_ring"]
    if drive.get("orientation", "radial_tangential") != "radial_tangential":
        raise ValueError("drive-ring orientation must be radial_tangential")
    count = int(drive["hole_count"])
    if not 0 <= index < count:
        raise ValueError(f"drive-hole index must be 0..{count - 1}")
    angle = 2 * math.pi * index / count
    cosine, sine = math.cos(angle), math.sin(angle)
    radius = float(drive["center_radius"])
    # Accept older square geometries as well as separately measured axes.
    half_radial = float(drive.get("radial_size", drive.get("hole_size", 0))) / 2
    half_tangential = float(drive.get("tangential_size", drive.get("hole_size", 0))) / 2
    if half_radial <= 0 or half_tangential <= 0:
        raise ValueError("drive-hole radial and tangential sizes must be positive")
    return [
        (radius * cosine + u * cosine - v * sine,
         radius * sine + u * sine + v * cosine)
        for u, v in ((-half_radial, -half_tangential), (half_radial, -half_tangential),
                     (half_radial, half_tangential), (-half_radial, half_tangential))
    ]

def note_to_track(geometry: dict, note: str) -> int:
    notes = geometry["note_system"]["notes_inner_to_outer"]
    try:
        return notes.index(note) + 1
    except ValueError as exc:
        raise ValueError(
            f"{note!r} is not playable. Allowed notes: {', '.join(notes)}"
        ) from exc
