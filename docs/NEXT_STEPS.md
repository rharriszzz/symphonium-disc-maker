# Next steps: request quotes for prototype disks

Prepared October 2, 2026.

The files are ready for supplier feasibility review and pricing. No further
questions for the other AI, or new measurements from you, are needed before
requesting quotes. No request has been submitted and no order has been placed.

## Read this plan in VS Code

Open `docs/NEXT_STEPS.md` in VS Code. Use **Ctrl + Shift + V** for the Markdown
preview; the file and website links below are clickable there.

If you want to read it in the repository's WSL terminal instead, type:

```bash
cat docs/NEXT_STEPS.md
```

## 1. Find and extract the supplier packages

The packages are:

- [Xometry quote package](../supplier_packages/xometry_quote.zip)
- [SendCutSend quote package](../supplier_packages/sendcutsend_quote.zip)
- [Dimensioned reference drawing](../supplier_packages/reference_drawing.pdf)

To copy and extract the ZIPs, press **Windows + E** to open File Explorer.
Press **Ctrl + L**, paste this folder address, and press **Enter**:

```text
\\wsl.localhost\Ubuntu\home\rharris\git\symphonium-disc-maker\supplier_packages
```

The two files to use are:

```text
xometry_quote.zip
sendcutsend_quote.zip
```

Copy both ZIPs to your Windows Downloads folder. Right-click each copied ZIP
and choose **Extract All**. Keep the extracted folders separate because their
quote requests specify different materials.

Each extracted package contains:

- `pachelbel_cut_mm.dxf`: the manufacturing cutting file.
- `reference_drawing.pdf`: a dimensioned reference drawing.
- `quote_request.txt`: the request to send to that supplier; open it in Notepad.
- `README.txt`: short instructions for the package.
- `package_manifest.json`: file hashes for identifying this version; keep it
  with the package.

## 2. Request one prototype from each supplier

Use these proposed first requests:

| Supplier | Requested material | Quantity |
| --- | --- | --- |
| Xometry | Clear PETG, 0.020 inch thick | Quote one disk; optional price for two |
| SendCutSend | Clear polypropylene, 0.030 inch thick | Quote one disk; optional price for two |

The SendCutSend material is thicker than the 0.020-inch original disk and is a
thickness experiment. Its fit in the mechanism is not yet established.

Use these website links:

- [Xometry sheet cutting and quote entry](https://www.xometry.com/capabilities/sheet-cutting/)
- [SendCutSend contact / feasibility questions](https://sendcutsend.com/contact/)
- [SendCutSend polypropylene material / quote entry](https://sendcutsend.com/materials/polypropylene/)

Upload `pachelbel_cut_mm.dxf` as the manufacturing CAD file, using **millimeters
and 1:1 scale**. Supply `reference_drawing.pdf` as supporting material and
paste the contents of that supplier's `quote_request.txt` into its notes or
inquiry form. If the portal cannot offer the requested material or thickness,
ask for manual feasibility review rather than accepting a substitution.

The preview should show one disk with:

- **177.800 mm outside diameter** (7.000 inches).
- **5.0800 mm center opening** (0.200 inch).
- **143 rectangular drive openings** and **20 round music holes**.

The reference PDF is illustrative. Use the DXF for cutting; do not measure the
PDF to determine manufacturing dimensions.

## 3. Get the supplier's confirmations before paying

The quote requests already ask about these details, so you do not need to
write the technical questions yourself:

- Whether the small drive openings can be made at the specified dimensions,
  with suitable hole-location tolerances and corner rounding.
- Whether the finished center opening, through the full material thickness,
  will clear the trusted **0.1925-inch metal post** (4.8895 mm). Its nominal
  diametral clearance is only 0.0075 inch; general cutting tolerances alone
  do not establish fit.
- Actual material, stock thickness, flatness and clean edge condition.
- Price for the proposed quantity, shipping, and any setup or tooling fees.
- Any proposed dimensional or material changes, for review before cutting.

## 4. Bring the replies back to Codex

Save or copy each company's reply and quote, and provide it here before paying.
Include any proposed changes to material, thickness, dimensions or tolerances.
I can compare the two replies and revise the files if necessary.

After those details are settled, the next step is ordering the agreed
prototypes. On arrival, test the disks without labels first and record the
sampler playback to check all 20 tines.

## Optional: fit a paper label while waiting

Open the [label fitting PDF](../prototype_pack/label_fit_test.pdf). You can
also find it in this folder using Windows File Explorer:

```text
\\wsl.localhost\Ubuntu\home\rharris\git\symphonium-disc-maker\prototype_pack
```

Open `label_fit_test.pdf` and print it on plain US Letter paper at
**100% / actual size**, with **Fit** and **Shrink** disabled. Check the
one-inch ruler, then hand-cut one 1.50-inch label and its center opening.
Place it on the original disk and check that it covers no music or drive holes.

The Gazelle can wait until you are ready to connect and power it on. Supplier
quote preparation and this paper fitting test can proceed independently.
