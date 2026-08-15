# COSTA Lubricant 5W-30 (5L) — Label Recreation

Faithful recreation of the COSTA Lubricant Engine Oil 5W-30 (5L) bottle
sticker, rebuilt from the reference product photo. All geometry, colors and
typography were measured off the photo; the engine image and the oil splash
are extracted from the reference itself.

## Files
- `COSTA-5W30-5L-sticker.pdf` — print-ready PDF, 100 x 142.5 mm (the label's
  true aspect ratio), die-cut contour shape, no margins.
- `COSTA-5W30-5L-sticker-3000px.png` — high-resolution raster export.
- `label.html` — the artwork source (inline SVG); open in a browser to view.
- `build.py` — generates `label.html` (embeds the extracted assets).
- `extract_assets.py` — extracts `engine_crop.png` / `splash_crop.png` from
  the reference photo (`python3 extract_assets.py reference.jpg`).
- `fonts/` — Russo One, Montserrat, Lora + others (Google Fonts, OFL).

## Rebuild
```bash
python3 extract_assets.py reference.jpg   # only if assets are missing
python3 build.py
chromium --headless --no-sandbox --print-to-pdf=COSTA-5W30-5L-sticker.pdf \
  --no-pdf-header-footer "file://$PWD/label.html"
```
