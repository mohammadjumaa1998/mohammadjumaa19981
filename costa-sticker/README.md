# COSTA Lubricant 5W-30 (5L) — Label Recreation

Vector recreation of the COSTA Lubricant Engine Oil 5W-30 (5L) bottle sticker,
rebuilt from a product photo as print-ready artwork.

## Files
- `COSTA-5W30-5L-sticker.pdf` — print-ready vector PDF, exactly 100 x 160 mm, no margins.
- `COSTA-5W30-5L-sticker-3000px.png` — high-resolution raster export (3000 x 4800 px).
- `label.html` — the artwork source (inline SVG); open in a browser to view.
- `build.py` — generates `label.html`.
- `fonts/` — Cinzel, Archivo, Barlow Condensed (Google Fonts, OFL license).

## Rebuild
```bash
python3 build.py
chromium --headless --no-sandbox --print-to-pdf=COSTA-5W30-5L-sticker.pdf \
  --no-pdf-header-footer "file://$PWD/label.html"
```
