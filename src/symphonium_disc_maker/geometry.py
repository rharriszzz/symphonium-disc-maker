from __future__ import annotations
import json
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

def note_to_track(geometry: dict, note: str) -> int:
    notes = geometry["note_system"]["notes_inner_to_outer"]
    try:
        return notes.index(note) + 1
    except ValueError as exc:
        raise ValueError(
            f"{note!r} is not playable. Allowed notes: {', '.join(notes)}"
        ) from exc
