# COSTA Lubricant 5W-30 (5L) — Label

Print-ready recreation of the COSTA Lubricant Engine Oil 5W-30 (5L) sticker.

## Deliverable (vector master)
Full vector artwork — every text, band, medal, frame and background shape is
vector (razor sharp at any zoom); only the engine photo and the oil splash
are raster, extracted from the reference image. Idealized die-cut geometry:
straight edges, clean corner sweep. Colors sampled from the reference.
- `COSTA-5W30-5L-sticker.pdf` — vector print PDF, 100 x 142.5 mm, no margins.
- `COSTA-5W30-5L-sticker-3000px.png` / `-6000px.png` — raster exports.
- `label.html` — the artwork source (inline SVG).
- `build.py` — generates `label.html`.
- `extract_assets.py` — extracts `engine_crop.png` / `splash_crop.png`.
- `fonts/` — Russo One, Montserrat, Lora and others (Google Fonts, OFL).

## Reference-lift version (for comparison)
- `label_exact.html` + `label_full.png` + `make_final.py` — the label lifted
  pixel-for-pixel from the reference photo with a spline die-cut. Identical
  to the source but resolution-limited (kept for reference).

## Rebuild
```bash
python3 build.py
chromium --headless --no-sandbox --print-to-pdf=COSTA-5W30-5L-sticker.pdf \
  --no-pdf-header-footer "file://$PWD/label.html"
```
