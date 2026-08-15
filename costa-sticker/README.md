# COSTA Lubricant 5W-30 (5L) — Label Recreation

Reproduction of the COSTA Lubricant Engine Oil 5W-30 (5L) bottle sticker.
Two versions are included:

## 1. Exact version (the deliverable)
The complete label artwork lifted directly from the reference photo —
identical logo, blue zones, curves, medal, engine image and oil splash —
die-cut along the label's real contour with a transparent background.
- `COSTA-5W30-5L-sticker.pdf` — print PDF, 100 x 142.5 mm.
- `COSTA-5W30-5L-sticker-3000px.png` — high-resolution export.
- `label_exact.png` — the extracted die-cut artwork (RGBA).
- `label_exact.html` — page wrapper used for the PDF export.
- `extract_exact.py` — regenerates label_exact.png from the reference photo.

## 2. Vector version (editable)
A full vector rebuild (measured off the photo) for future edits — change
viscosity, size, or text and re-export at any print resolution.
- `label.html` (source), `build.py` (generator), `extract_assets.py`
  (engine/splash extraction), `fonts/` (Russo One, Montserrat, Lora — OFL).

## Rebuild
```bash
python3 extract_exact.py reference.jpg   # exact artwork
python3 build.py                          # vector version
chromium --headless --no-sandbox --print-to-pdf=out.pdf \
  --no-pdf-header-footer "file://$PWD/label_exact.html"
```
