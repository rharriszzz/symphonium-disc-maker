# Small center labels and BossKut Gazelle setup

Use a **1.50-inch circular center label** that leaves the music and drive holes
uncovered. At the current dimensions its edge is 0.14168 inch (3.5987 mm)
inside the nearest music-hole edge. The largest circle that would just touch
that hole ring is 1.78336 inches; the CLI rejects labels at or above that size.
Leave room for cutting and placement error when choosing a size.

The label center-hole diameter defaults to `geometry.json`. The current
0.200-inch value is a rounded prototype nominal from approximately 0.198-inch
clear-edge scan fits, consistent with the less certain 0.1995-inch inside-jaw
reading of the plastic hole. The trusted metal post is 0.1925 inch.
Finished fit still needs testing, as described in
[the ordering notes](ORDERING.md). `--center-hole` allows a larger
label opening without changing the manufacturing geometry. A paper fitting
test should establish the final label opening.

## Generate printing artwork and cutting outlines

The ready-to-print [paper fitting PDF](../prototype_pack/label_fit_test.pdf)
has a US Letter page, 20 labels, and a one-inch calibration ruler. It can be
printed from Windows 11 or a Mac and hand-cut while the Gazelle connection
is unresolved. The [printing PDF](../prototype_pack/labels_print.pdf) contains
only label text. Both are in [the prepared prototype pack](../prototype_pack/README.md).

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

For a new PDF, install the optional printing dependencies and use a `.pdf`
output filename:

```bash
pip install -e '.[print]'
PYTHONPATH=src python3 -m symphonium_disc_maker.cli labels --title PACHELBEL --subtitle "20-tine sampler" --calibration -o output/label_fit_test.pdf
PYTHONPATH=src python3 -m symphonium_disc_maker.cli labels --title PACHELBEL --subtitle "20-tine sampler" --mode print -o output/labels_print.pdf
```

PDF and SVG share the same layout calculations and physical dimensions.
PDF embeds DejaVu Sans for portable text rendering; SVG requests Arial or a
sans-serif fallback. The paper-test PDF adds the ruler and printing instructions
outside the label positions. `--calibration` is a PDF-only option. A raster
verification at 144 dpi confirms the 1.50-inch circle and one-inch ruler; the
PDF page is exactly 612 × 792 points. Printer settings still determine the
physical result, so measure the printed ruler before fitting a label.

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
The software lists Windows 11 support. Craft Edge's
[product page](https://www.craftedge.com/products/products_scal.php) also lists
native Apple Silicon Mac versions. These are software capabilities; connection
to this particular Gazelle has not yet been demonstrated.
Its [official downloads page](https://www.craftedge.com/download/downloads.php)
provides the starting point for software evaluation.

This does not resolve Windows driver availability. Craft Edge's
[Gazelle setup guide](https://www.craftedge.com/tutorials/gazelle/setup.php)
specifies a **CUTOK printer driver** on Windows, with the device appearing as a
CUTOK printer and cutting connection set to USB / Auto. This is a different
driver path from the generic FTDI serial drivers used by some other cutters.
The guide says a Mac does not need a separate driver, but that is not a test
of this particular Gazelle on a current Mac.

The CUTOK-hosted resources are unavailable for this workflow. The
[latest handoff](CHATGPT_LATEST_DISCOVERIES.md) confirms the user's dead-link
experience; the old URLs are retained below as historical references only.
A current official Windows 11-compatible Gazelle/CUTOK driver download remains
**unverified**. Use Craft Edge's live downloads and support pages for the active
setup path.

The [Windows host check](GAZELLE_WINDOWS_CHECK.md) now confirms **Windows 11
Home x64** and an existing **SCAL 6.085** installation. No candidate cutter/USB
printer appeared in the present-device check; connection and power need to be
confirmed before deciding that a driver is missing. **Windows 10 is excluded**.
A Mac is the fallback if the Windows 11 connection cannot be established.
The latest handoff reports an Apple Silicon Mac; its macOS version and any
surviving original Gazelle installer remain unknown.

1. Connect and power on the Gazelle to inspect its Windows 11 enumeration in
   Device Manager and Devices and Printers. Record its device name, whether it
   appears as CUTOK/DC330 or an unknown USB device, and hardware IDs. This
   identifies the device; it does not establish that an unknown device can cut.
   Record the Windows architecture and any surviving original installer.
2. Use the installed SCAL 6.085 for evaluation; its license/trial status has
   not been checked. If Windows already has
   a working CUTOK printer driver, use the documented USB / Auto connection
   and try a small scrap-paper circle. Craft Edge's guide expects a driver
   before the cutting connection is made; the enumeration check above is
   diagnostic when that historical driver download is unavailable.
3. If the Windows driver is missing, ask
   [Craft Edge support](https://www.craftedge.com/support/)
   whether they can provide the Gazelle CUTOK driver and confirm support for
   Windows 11 on that architecture. Include the USB device's hardware IDs
   and model information. The [prepared inquiry](CRAFT_EDGE_DRIVER_INQUIRY.md)
   includes the confirmed Windows architecture and SCAL version; it has not been sent.
4. If Craft Edge cannot establish a working Windows 11 path, evaluate the
   Apple Silicon Mac using the SCAL trial. Their setup guide says no separate
   Mac driver is needed. Verify actual USB communication and a correctly
   scaled paper cut before buying a platform-specific license. SCAL trial cuts
   include extra watermark lines, according to its
   [FAQ](https://www.craftedge.com/support/faq/faq_surecutsalot4.php).
5. After simple cutting works, confirm the chosen software edition supports
   the Gazelle alignment workflow needed for printed labels. Cutter support
   and print-and-cut registration support are separate questions.

Third-party CUTOK/DC330 mirrors remain research leads, after the existing
Windows driver, Craft Edge support, and Mac routes. No mirrored package has
been verified or installed. If one is evaluated later, preserve and hash it,
inspect its INF/CAT files, hardware IDs, architecture and signatures, and scan
it before installation. Do not disable signature enforcement to force an
unknown driver. This mirrors the latest handoff's revised recommendation.

Automatic registration can wait: fit a plain-paper label, prove simple cutting
at the correct scale, then establish the actual Gazelle/SCAL alignment procedure
before adding device-specific marks. The existing print and cut files use the
same page origin and physical scale.

## Historical references — currently unavailable

These CUTOK-hosted URLs appeared in earlier research. They are historical
references, with no verified usable download, and are excluded from the active
setup workflow:

- `https://www.cutok.com/Support.htm`
- `https://www.cutok.com/down/Manual.pdf`
- `https://www.cutok.com/down/cutok_Signed.rar`

## Draft question for Craft Edge

The [current prepared inquiry](CRAFT_EDGE_DRIVER_INQUIRY.md) includes the
confirmed Windows 11 x64 and SCAL 6.085 details. The generic draft below is
retained for reference; neither draft has been sent.

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
