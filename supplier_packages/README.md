# Supplier quote packages

Prepared for feasibility review and pricing. Neither package has been submitted.

- [Xometry package](xometry_quote.zip): clear PETG, 0.020 inch (0.508 mm).
- [SendCutSend package](sendcutsend_quote.zip): clear polypropylene, 0.030 inch (0.762 mm).
- [Dimensioned reference drawing](reference_drawing.pdf): one-page overview for both suppliers.
- [Cut-file audit](cut_file_audit.json): closed contours, units, sizes and duplicate checks.

Each ZIP contains the same cutting DXF and reference drawing, its supplier's
quote request, a README and content hashes. Extract it and upload the DXF alone
as manufacturing CAD; provide the PDF and request as supporting material.
The drawing is illustrative, not an actual-size printing or cutting template.

The proposed quantity is one disk from each company, with an optional price
for two. Confirm the material/process, finished-hole fit, drive-opening sizes,
corner rounding, thickness, shipping and total price before paying.
SendCutSend's proposed stock is thicker than the 0.020-inch original; mechanism
clearance remains a physical test. Labels are separate from the cutting files.

The 5.0800 mm center-hole nominal has only
0.1905 mm diametral clearance over the trusted
4.8895 mm post. Each request asks for the minimum clear opening
through the full thickness. General published cutting tolerances are not
a guarantee that this hole will fit. Supplier dimensional changes need review.

See [ordering instructions and supplier links](../docs/ORDERING.md) and the
[complete prototype pack](../prototype_pack/README.md). The latter includes
label files and the sampler recording sequence for the delivered disks.

Regenerate after updating the prototype pack:

```bash
PYTHONPATH=src python3 scripts/build_supplier_packages.py
```
