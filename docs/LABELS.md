# Small center labels and BossKut Gazelle setup

Use a **1.50-inch circular center label** that leaves the music and drive holes
uncovered. At the current dimensions its edge is 0.14168 inch (3.5987 mm)
inside the nearest music-hole edge. The largest circle that would just touch
that hole ring is 1.78336 inches; the CLI rejects labels at or above that size.
Leave room for cutting and placement error when choosing a size.

The label center-hole diameter defaults to `geometry.json`. The current
0.196-inch value duplicates the measured working original; material fit over
the retaining post still needs testing, as described in
[the ordering notes](ORDERING.md). `--center-hole` allows a larger
label opening without changing the manufacturing geometry. A paper fitting
test should establish the final label opening.

## Generate printing artwork and cutting outlines

Run these commands from the repository root. All three sheets share the same
20-label layout on US Letter paper. Text sits above and below the center hole.
Long lines use a smaller font; inspect them before printing.

```bash
PYTHONPATH=src python3 -m symphonium_disc_maker.cli labels --title PACHELBEL --subtitle "Canon sampler" --mode combined -o output/pachelbel_labels.svg
PYTHONPATH=src python3 -m symphonium_disc_maker.cli labels --title PACHELBEL --subtitle "Canon sampler" --mode print -o output/pachelbel_labels_print.svg
PYTHONPATH=src python3 -m symphonium_disc_maker.cli labels --title PACHELBEL --subtitle "Canon sampler" --mode cut -o output/pachelbel_labels_cut.svg
```

- **Combined** contains the artwork and circles for inspecting the layout or
  printing a paper test to cut by hand.
- **Print** contains only the text. There are no printed cut lines.
- **Cut** contains only the outer circles and center holes. Import this for
  cutting outlines, so the cutter does not cut the letters.

`--rows`, `--columns`, `--diameter`, and `--center-hole` are adjustable.
This is a layout for full-sheet adhesive stock, not a verified template for
any brand of precut labels. Unsupported sizes and overlapping layouts are
rejected before a file is written.

Print at actual size / 100%, with page fitting disabled. Measure an outer
circle on the combined paper test: it should be 1.50 inches (38.10 mm).
Check the label on the original disk before using adhesive stock. A hand-cut
paper prototype allows label work to continue while the cutter is unresolved.

The separate files do **not** provide automatic print-to-cut registration.
Cutter imports may reposition artwork, discard the page origin, or rescale it.
Keep both files at the same scale and origin in the cutting software, then use
that software's supported alignment procedure. Do a plain-paper test before
cutting a printed adhesive sheet. Device-specific registration marks are not
yet implemented or verified for the Gazelle.

## Gazelle software and driver findings

Checked October 1, 2026. Craft Edge currently lists BossKut Gazelle among the
cutters supported by [Sure Cuts A Lot 6](https://www.surecutsalot.com/software/software_scal.php).
Its [official downloads page](https://www.craftedge.com/download/downloads.php)
provides the starting point for software evaluation.

This does not resolve Windows driver availability. Craft Edge's
[Gazelle setup guide](https://www.craftedge.com/tutorials/gazelle/setup.php)
specifies a **CUTOK printer driver** on Windows, with the device appearing as a
CUTOK printer and cutting connection set to USB / Auto. This is a different
driver path from the generic FTDI serial drivers used by some other cutters.
The guide says a Mac does not need a separate driver, but that is not a test
of this particular Gazelle on a current Mac.

The guide links to [CUTOK support](https://www.cutok.com/Support.htm).
That page could not be retrieved during this research, so a working original
driver download has **not** been verified. The existing dead-link problem
is real; the live SCAL listing alone is not a solution.

The handoff says the original Gazelle software has been lost. Useful next steps
depend on obtaining a driver for the user's **Windows 11** computer. **Windows
10 is excluded**. A Mac is the fallback if the Windows 11 connection cannot
be established. Architecture (x64 or ARM64) and any surviving installer backup
are still unknown.

1. Identify the Windows 11 architecture and locate any original CD
   or installer backup. Note whether the Gazelle already appears
   as a CUTOK printer or an unknown USB device.
2. If the Windows driver is missing, ask
   [Craft Edge support](https://www.craftedge.com/support/)
   whether they can provide the Gazelle CUTOK driver and confirm support for
   Windows 11 on that architecture. Include the USB device's hardware IDs
   if available. If this route fails, evaluate the Mac connection described
   in their setup guide against the actual Mac's OS version and hardware.
3. Once connection works, test the software with a small scrap-paper circle
   before buying a license or using a printed label sheet. SCAL trial cuts
   include extra watermark lines, according to its
   [FAQ](https://www.craftedge.com/support/faq/faq_surecutsalot4.php).
4. Confirm that the chosen software edition supports the Gazelle alignment
   workflow needed for printed labels. Cutter support and print-and-cut
   registration support are separate questions.

## Draft question for Craft Edge

This draft has not been sent. Fill in the computer details first.

> I own a BossKut Gazelle and want to cut small printed paper labels from SVG
> artwork. My computer runs Windows 11 [x64 or ARM64]. Your Gazelle setup
> guide requires a CUTOK printer driver on Windows, but the linked download
> is unavailable to me. Can you supply the original driver or a current
> official download and confirm compatibility with Windows 11 on that
> architecture? Windows 10 is not an option. A Mac is my fallback; can you
> confirm whether the Gazelle works without a separate driver on current
> macOS, including any Apple Silicon limitations? Also, which SCAL
> edition supports printed-label alignment with the Gazelle, and what
> registration procedure does it use? I would like to verify connection and
> alignment before purchasing software.
