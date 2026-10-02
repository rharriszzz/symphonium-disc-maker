# Symphonium Disc Maker — Follow-up on Rotation Direction, Scan Face, Time Zero, and Center Post

**Date:** 2026-10-01\
**Repository:** `rharriszzz/symphonium-disc-maker`\
**Reference disc:** *Unchained Melody*\
**Machine:** Mr. Christmas Animated Holiday Symphonium 140-24021

This document answers two follow-up questions from the Codex CLI agent and supersedes the more conservative wording in the earlier handoff where noted.

---

# 1. What face was scanned?

## Confirmed

The 600 dpi scan is of the **top / printed face** of the original disc.

The machine, however, **reads/plucks the disc from underneath**.

Therefore:

- the scan coordinate system is a **top-view coordinate system**;
- the plucker/follower mechanism contacts the opposite face;
- looking at the same physical disc from underneath produces a mirror image of the angular ordering seen in the scan.

The radial positions do not change when switching faces, but clockwise/counterclockwise descriptions do.

For clarity, all conclusions below first use the **top-face / scan view**.

---

# 2. Can the playback rotation direction be determined?

## Yes — with high confidence

The 600 dpi scan and the audio recording are sufficient to determine the direction.

The earlier handoff said the direction was "not established." That was too conservative.

## Coordinate convention

For the full-resolution scan:

- disc center is the origin;
- 0 degrees points to the right;
- positive angle is **counterclockwise when viewed from the scanned/top face**.

This is the ordinary mathematical polar-angle convention after reversing the image Y axis.

The scan contains:

- 145 music-note holes;
- 19 occupied radial note tracks;
- lower-pitch tracks closer to the center;
- higher-pitch tracks farther outward.

The mechanism itself has 20 tracks/tines; *Unchained Melody* appears not to use the outermost one.

## Audio method

The original M4A was analyzed directly.

A complete, reliable MIDI transcription of *Unchained Melody* was **not** required and should not be claimed.

Instead, the direction test used the much stronger prior information already available:

1. The radial track of every scanned hole is known.
2. The inner-to-outer pitch order is known/provisionally mapped:
   `C4, D4, E4, ... G6` for the 19 occupied rows.
3. The recording contains a little more than two revolutions.
4. The revolution time is about 28.1 seconds.
5. For each of the 19 possible recorded pitches, a pitch-specific onset-strength channel was calculated from the recording.
6. The 145 scanned holes were mapped into those 19 channels.
7. The angular sequence was tested in both possible directions while allowing an arbitrary phase offset.

The audio analysis used each target pitch's fundamental plus weaker harmonic contributions, then looked for increases in energy associated with attacks.

The audio was folded by the revolution period so both recorded revolutions contributed to the comparison.

---

# 3. Numerical direction result

For a working revolution period near 28.126 s, the two angular hypotheses gave approximately:

| Top-face angular relationship | Best correlation score | Peak significance |
|---|---:|---:|
| time increases as angle **increases** | ~63 | ~3.7 sigma |
| time increases as angle **decreases** | **~319** | **~9.6 sigma** |

The result remains essentially unchanged when the assumed revolution period is varied over a useful range:

| Trial period | Increasing-angle score | Decreasing-angle score |
|---:|---:|---:|
| 28.08 s | 62.0 | **321.0** |
| 28.10 s | 65.7 | **321.1** |
| 28.12 s | 65.9 | **320.4** |
| 28.126 s | 63.0 | **318.8** |
| 28.14 s | 62.0 | **319.6** |
| 28.16 s | 55.3 | **316.2** |

So the preferred sequence direction is not a marginal result.

It is roughly five times stronger in raw score and substantially more statistically distinct.

---

# 4. What does that imply about physical rotation?

Let:

- `alpha` = a hole's angular coordinate on the stationary disc, viewed from the top;
- `beta` = fixed reader/plucker angular location;
- `omega` = physical angular velocity, positive for counterclockwise rotation viewed from the top.

A hole plays when:

```text
alpha + omega*t = beta   (mod 2*pi)
```

Therefore:

```text
t = (beta - alpha) / omega
```

The scan/audio result shows:

```text
play time decreases as top-face alpha increases
```

or equivalently:

```text
t ∝ -alpha
```

That requires:

```text
omega > 0
```

under the coordinate convention above.

## Conclusion

> **The disc rotates counterclockwise when viewed from the top / printed / scanned face.**

Because the machine reads the underside:

> **The same physical rotation appears clockwise when viewed from underneath, looking directly at the plucker side.**

These are the same physical motion described from opposite sides.

---

# 5. What direction should chronological note events be laid out on the top face?

This distinction is important.

The disc physically rotates **counterclockwise viewed from above**.

For a fixed underside reader, later-playing holes must initially lie progressively in the opposite angular direction.

Therefore, on a stationary design viewed from the **top face**:

> **Chronological playback order proceeds clockwise around the disc.**

Using standard mathematical top-face angles:

```text
angle(t) = start_angle - 360° * t / revolution_time
```

not:

```text
angle(t) = start_angle + 360° * t / revolution_time
```

## Consequence for the current repo

The current code uses an increasing angle for later events.

For example, `svg.py` currently has the equivalent of:

```python
angle_deg = start_angle_degrees + 360.0 * frac
```

and `dxf.py` similarly adds the event phase.

Given the now-established top-face playback direction, this should be reviewed and very likely changed to:

```python
angle_deg = start_angle_degrees - 360.0 * frac
```

with equivalent handling in DXF.

The repo should explicitly document which face its geometric output represents.

Recommended convention:

> **All SVG/DXF arrangement geometry is defined as viewed from the disc's printed/top face.**

Then chronological events use decreasing polar angle.

---

# 6. What does the underside-reading fact change?

The note holes and drive holes are through-cuts, but the musical pattern is not rotationally mirror-symmetric.

If the top-face design is viewed from underneath, its angular ordering is mirrored.

Thus:

- top face: physical rotation = counterclockwise;
- underside view: physical rotation appears clockwise;
- chronological hole sequence on the stationary top-face artwork = clockwise;
- chronological hole sequence as seen from underneath = counterclockwise.

This needs to be kept straight when comparing:

- the top-face scan,
- photographs of the installed disc,
- underside mechanism geometry,
- CAD files,
- labels.

For manufacturing, the DXF itself is only 2-D through-cut geometry and does not inherently have a "top" unless we assign one.

For this project, assign the CAD view to the **printed/top face** and keep that convention everywhere.

---

# 7. What is the meaning of the current `230°` time-zero angle?

## Confirmed: it has no established mechanical significance

The value:

```text
start_angle_degrees = 230.0
```

was chosen for visual/layout convenience when generating an early disc preview.

It was **not** measured from:

- the plucker assembly;
- a particular drive tooth;
- an index mark;
- the label;
- a keyed mounting feature;
- the scanner;
- the start of the M4A recording.

Therefore:

> **230° is an arbitrary rotational phase.**

It may remain a user-selectable layout phase, but it must not be documented as a measured mechanism angle.

---

# 8. Can the scan/audio correlation determine the physical reader angle?

Not from the current data alone.

The best audio correlation has a phase offset around 21.1 s within the revolution.

However, that offset contains at least two unknown phases:

1. the arbitrary rotational orientation in which the loose disc was placed on the scanner;
2. the arbitrary rotational phase of the disc at the instant the audio recording began.

Therefore that correlation phase cannot be converted directly into a physical "reader is at N degrees" statement.

The **sign/direction** is robust because those arbitrary rotations only add a constant phase.

The **absolute angular zero** is not.

---

# 9. Summary of rotation conclusions

## Confirmed / high confidence

- The scan is the **top / printed face**.
- The machine reads/plucks the disc from **underneath**.
- The disc rotates **counterclockwise viewed from the top**.
- The same rotation appears **clockwise viewed from underneath**.
- On stationary top-face CAD artwork, chronological note events proceed **clockwise**, i.e. toward decreasing mathematical angle.
- The repo's current positive-time/positive-angle arrangement convention should be corrected or explicitly redefined.
- `230°` is arbitrary, not a measured mechanical time-zero angle.

## Not established

- A physically meaningful absolute reader angle in scan coordinates.
- A unique mechanical time-zero location.

---

# 10. Center hole versus center post

The two direct measurements are:

```text
original disc center-hole diameter = 0.1960 in
measured center-post feature       = 0.2085 in
```

Difference:

```text
0.2085 - 0.1960 = 0.0125 in
```

That is:

```text
0.00625 in interference per side
```

and the measured post feature is about 6.4% larger in diameter than the hole.

If those were a rigid uniform shaft and rigid hole at the same seating diameter, they would not be a normal sliding clearance fit.

---

# 11. Can the center-post discrepancy be resolved from the existing information?

## Partly, but not completely

The photographs of the bare mechanism show that the visible central black post is **not obviously a long uniform precision cylinder**.

It appears rounded / tapered / retaining-post-like.

That supports the interpretation that the 0.2085-inch caliper reading may be the maximum diameter of a retaining portion rather than the diameter on which the disc finally seats.

The original disc is also:

```text
~0.020 in thick
```

and flexible plastic.

A plausible mechanical arrangement is therefore:

1. the 0.196-inch hole passes over a slightly larger rounded/tapered retaining feature;
2. the thin disc flexes temporarily during installation;
3. the disc then rests around or below a smaller neck/seating diameter.

This is mechanically plausible and consistent with the visible shape.

## But this is not fully proven

The photographs do not clearly expose the entire post profile at sufficient resolution to measure:

- the minimum neck diameter;
- the seating diameter directly under the cap;
- the taper;
- the exact height at which the original disc rests.

Therefore do **not** claim that a particular hidden shaft diameter has been measured.

---

# 12. Best-supported interpretation of the 0.196 / 0.2085 discrepancy

The strongest statement justified by the evidence is:

> The original working disc really has a ~0.196-inch center hole.\
> The visible post has a measured feature of ~0.2085 inch.\
> The post appears to have retaining/tapered geometry rather than being a simple uniform shaft.\
> The original thin flexible disc therefore most likely passes over a larger retaining portion and seats on a smaller region, or flexes over the retainer during installation.

This is more plausible than treating 0.2085 inch as the required manufacturing hole diameter.

---

# 13. Manufacturing consequence: keep the center hole at 0.196 inch for now

The original disc is the known-working reference.

Therefore the first manufactured disc should duplicate:

```text
center hole = 0.196 in
```

unless a direct new measurement proves otherwise.

Do **not** enlarge it to 0.2085 inch merely because the visible post feature measures 0.2085 inch.

A 0.2085-inch hole could remove whatever retention the original design intentionally has.

---

# 14. Material consequence of the center-post fit

This discrepancy makes material flexibility more important than previously appreciated.

If the original 0.196-inch hole must flex over a ~0.2085-inch retaining feature, then a replacement material must tolerate that snap-over action.

This affects the comparison between candidate materials:

### 0.020-inch PETG

Advantages:

- matches original thickness exactly;
- readily available from Xometry in the required nominal thickness.

Possible concern:

- PETG may be stiffer and less forgiving in a snap-over center-post fit than the original unknown plastic.

### 0.030-inch polypropylene

Advantages:

- polypropylene is very flexible and fatigue-resistant;
- likely comfortable with a snap-over retaining post.

Possible concern:

- 0.030 inch is 50% thicker than the measured 0.020-inch original.

Therefore center-post fit is another reason that material choice should be physically tested rather than decided from thickness alone.

---

# 15. Very useful low-cost center-hole test

Before paying for multiple complete discs, a small material test coupon could include several center holes:

```text
0.190
0.194
0.196
0.198
0.202
0.206
0.210 in
```

in the candidate material.

Try them manually over the post.

This would establish:

- whether the post is acting as a snap retainer;
- how much material flex is needed;
- whether PETG is acceptable;
- what manufacturing kerf/tolerance does to the effective hole size.

This test is especially useful if the vendor can add the coupon to the same sheet/order inexpensively.

---

# 16. Additional important repo issue: drive-hole orientation

Independent of the note-direction issue, a separate scan analysis showed that the 143 square drive holes are approximately oriented with their sides **radial/tangential** around the ring.

They are not all globally axis-aligned.

So Codex should fix both:

1. **music-event angular sign**
2. **individual drive-square rotation**

They are separate issues.

---

# 17. Recommended coordinate convention for the repo

To eliminate ambiguity, define this explicitly in code/docs:

```text
View:
    printed/top face of disc

Origin:
    disc center

0 degrees:
    +X / right

Positive angle:
    counterclockwise

Physical playback rotation:
    counterclockwise

Chronological event placement:
    decreasing angle

Event formula:
    theta_event = theta_zero - 360 * time / revolution_seconds
```

The underside mechanism view is then the mirror of this convention.

This convention matches:

- the scanned face;
- ordinary mathematical polar coordinates;
- CAD reasoning;
- the measured playback direction.

---

# 18. Suggested Codex changes

## Geometry / convention

Add something like this to `geometry.json`:

```json
"orientation": {
  "cad_view": "top_printed_face",
  "physical_rotation_top_view": "counterclockwise",
  "chronological_event_direction_top_view": "clockwise",
  "angle_zero_axis": "+x",
  "positive_angle": "counterclockwise",
  "start_angle_degrees": 230.0,
  "start_angle_status": "arbitrary layout phase, not mechanically measured"
}
```

## Arrangement code

Change event angular placement from increasing to decreasing angle, assuming the repo adopts the top-face convention:

```python
angle_deg = start_angle_degrees - 360.0 * frac
```

## Drive holes

Rotate each square with its local polar angle so its sides are radial/tangential.

## Tests

Add tests that establish:

- later events have decreasing top-face angle;
- two events 1/4 revolution apart differ by -90 degrees;
- drive squares at different polar positions have appropriately rotated vertices;
- arbitrary changes to `start_angle_degrees` rotate the entire musical pattern without changing relative timing.

---

# 19. Confidence table

| Question | Conclusion | Confidence |
|---|---|---|
| Which face was scanned? | Top / printed face | **Confirmed by user** |
| Which face does mechanism read? | Underside | **Confirmed by user** |
| Rotation viewed from top? | Counterclockwise | **High; strong scan/audio correlation** |
| Rotation viewed from underneath? | Clockwise | **High; geometric consequence** |
| Chronological pattern direction on top-face CAD? | Clockwise / decreasing angle | **High** |
| Does 230° identify reader location? | No | **Confirmed: it was arbitrary** |
| Absolute reader angle from scan? | Not determined | **High confidence in non-determination** |
| Center hole diameter? | 0.196 in | **Direct measurement** |
| Visible post feature diameter? | 0.2085 in | **Direct measurement** |
| Exact reason smaller hole fits larger post? | Likely tapered/retaining geometry + flexible disc | **Plausible, supported by photo, not fully proven** |
| Should first CAD center hole remain 0.196? | Yes | **Strong recommendation based on known-working original** |

---

# 20. Bottom line for Codex

The top/underside distinction is now clear enough to remove the earlier ambiguity.

For a CAD file defined as viewed from the **printed/top face**:

```text
physical disc rotation = COUNTERCLOCKWISE
playback-event sequence around stationary design = CLOCKWISE
event angle = start_angle - 360*time/revolution
```

The `230°` start angle remains merely a convenient arbitrary rotational phase.

The center-hole mismatch is not fully geometrically measured, but the evidence favors a rounded/tapered/snap-retaining center post. Continue to duplicate the original **0.196-inch hole** until direct measurement of the seating neck proves otherwise, and treat flexibility at the center post as an important material-selection test.
