from __future__ import annotations
import json
from pathlib import Path
from .geometry import note_to_track

def load_arrangement(path: str | Path) -> dict:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def normalize_arrangement(arrangement: dict, geometry: dict) -> dict:
    rev = float(arrangement.get(
        "revolution_seconds",
        geometry["timing"]["measured_revolution_seconds"]
    ))
    if rev <= 0:
        raise ValueError("revolution_seconds must be positive")

    out = dict(arrangement)
    normalized = []
    for i, event in enumerate(arrangement.get("events", []), start=1):
        t = float(event["time_seconds"])
        if not 0 <= t < rev:
            raise ValueError(
                f"event {i}: time_seconds {t} must be within [0, {rev})"
            )

        note = event.get("note")
        track = event.get("track")
        if track is None:
            if note is None:
                raise ValueError(f"event {i}: supply note or track")
            track = note_to_track(geometry, note)
        track = int(track)

        if not 1 <= track <= geometry["note_system"]["track_count"]:
            raise ValueError(f"event {i}: invalid track {track}")

        if note is None:
            note = geometry["note_system"]["notes_inner_to_outer"][track - 1]

        e = dict(event)
        e["time_seconds"] = t
        e["track"] = track
        e["note"] = note
        normalized.append(e)

    normalized.sort(key=lambda e: (e["time_seconds"], e["track"]))
    out["revolution_seconds"] = rev
    out["events"] = normalized
    return out

def validate_minimum_same_track_gap(arrangement: dict, minimum_seconds: float) -> list[str]:
    if minimum_seconds <= 0:
        return []
    rev = arrangement["revolution_seconds"]
    by_track = {}
    for e in arrangement["events"]:
        by_track.setdefault(e["track"], []).append(e["time_seconds"])

    warnings = []
    for track, times in sorted(by_track.items()):
        times = sorted(times)
        if len(times) < 2:
            continue
        gaps = [times[i+1] - times[i] for i in range(len(times)-1)]
        gaps.append(rev - times[-1] + times[0])
        for gap in gaps:
            if gap < minimum_seconds:
                warnings.append(
                    f"track {track}: repeated-note gap {gap:.3f}s "
                    f"< requested minimum {minimum_seconds:.3f}s"
                )
    return warnings
