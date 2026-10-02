"""Nominal CAD clearances for reviewing a prototype before requesting a quote."""
from __future__ import annotations

import math
from .geometry import drive_hole_vertices, event_angle_degrees, track_radius


def point_segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length_squared = dx*dx + dy*dy
    if length_squared == 0:
        return math.dist(p, a)
    t = max(0, min(1, ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / length_squared))
    return math.hypot(p[0] - a[0] - t*dx, p[1] - a[1] - t*dy)


def edges(polygon):
    return list(zip(polygon, polygon[1:] + polygon[:1]))


def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def inside_convex_polygon(point, polygon):
    signs = [cross(a, b, point) for a, b in edges(polygon)]
    return all(s >= 0 for s in signs) or all(s <= 0 for s in signs)


def polygon_distance(first, second):
    if any(inside_convex_polygon(p, second) for p in first):
        return 0
    if any(inside_convex_polygon(p, first) for p in second):
        return 0
    for a, b in edges(first):
        for c, d in edges(second):
            if cross(a, b, c)*cross(a, b, d) < 0 and cross(c, d, a)*cross(c, d, b) < 0:
                return 0
    return min(
        min(point_segment_distance(p, a, b) for p in first for a, b in edges(second)),
        min(point_segment_distance(p, a, b) for p in second for a, b in edges(first)),
    )


def circle_polygon_clearance(center, radius, polygon):
    if inside_convex_polygon(center, polygon):
        return -radius
    return min(point_segment_distance(center, a, b) for a, b in edges(polygon)) - radius


def prototype_preflight(arrangement, geometry, *, start_angle_degrees=230, label_diameter_in=1.5):
    disc_radius = float(geometry["disc"]["diameter"]) / 2
    center_radius = float(geometry["disc"]["center_hole_diameter"]) / 2
    note_radius = float(geometry["note_system"]["note_hole_diameter"]) / 2
    if not all(math.isfinite(n) and n > 0 for n in (disc_radius, center_radius, note_radius, label_diameter_in)):
        raise ValueError("disk, hole and label dimensions must be positive and finite")
    count = int(geometry["drive_ring"]["hole_count"])
    if count < 2:
        raise ValueError("drive ring needs at least two openings")
    polygons = [drive_hole_vertices(geometry, i) for i in range(count)]
    if not all(math.isfinite(n) for polygon in polygons for point in polygon for n in point):
        raise ValueError("drive-hole coordinates must be finite")
    music = []
    for event in arrangement["events"]:
        angle = math.radians(event_angle_degrees(event["time_seconds"],
                                                 arrangement["revolution_seconds"], start_angle_degrees))
        radius = track_radius(geometry, event["track"])
        music.append((radius*math.cos(angle), radius*math.sin(angle)))
    if not music:
        raise ValueError("prototype must have at least one music hole")
    if not all(math.isfinite(n) for point in music for n in point):
        raise ValueError("music-hole coordinates must be finite")
    clearances = {
        "drive_to_drive": min(polygon_distance(polygons[i], polygons[(i+1) % count]) for i in range(count)),
        "drive_to_outer_edge": disc_radius - max(math.hypot(*p) for polygon in polygons for p in polygon),
        "drive_to_center_hole": min(circle_polygon_clearance((0, 0), center_radius, p) for p in polygons),
        "music_to_drive": min(circle_polygon_clearance(p, note_radius, polygon) for p in music for polygon in polygons),
        "music_to_outer_edge": disc_radius - max(math.hypot(*p) + note_radius for p in music),
        "music_to_center_hole": min(math.hypot(*p) - note_radius - center_radius for p in music),
        "label_to_innermost_possible_music_hole": track_radius(geometry, 1) - note_radius - label_diameter_in/2,
    }
    if len(music) > 1:
        clearances["music_to_music"] = min(math.dist(p, q) - 2*note_radius
                                            for i, p in enumerate(music) for q in music[i+1:])
    problems = [name for name, value in clearances.items() if value <= 0]
    if center_radius >= disc_radius or label_diameter_in/2 <= center_radius:
        problems.append("center_hole_fit_in_disk_and_label")
    if problems:
        raise ValueError("cut geometry overlaps or touches: " + ", ".join(problems))
    times = sorted(event["time_seconds"] for event in arrangement["events"])
    gaps = [b-a for a, b in zip(times, times[1:])]
    gaps.append(arrangement["revolution_seconds"] - times[-1] + times[0])
    return {
        "status": "nominal CAD has positive clearances; supplier process and fit unverified",
        "units": "inch", "disc_diameter_in": disc_radius*2,
        "expected_dxf_counts": {"CIRCLE": len(music)+2, "LINE": count*4},
        "drive_openings": count, "music_holes": len(music),
        "tracks_present": sorted(set(e["track"] for e in arrangement["events"])),
        "clearances_in": clearances,
        "clearances_mm": {name: value*25.4 for name, value in clearances.items()},
        "minimum_attack_gap_seconds": min(gaps),
        "limits": "nominal 2D geometry only; excludes kerf, tolerances, corner rounding, thickness, post seating and tine reset/decay",
    }
