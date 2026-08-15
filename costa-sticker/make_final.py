#!/usr/bin/env python3
"""Full pipeline: extract the label from the reference photo, fit a smooth
vector die-cut contour, and emit label_exact.html (artwork clipped by the
spline path + clean metallic frame). Usage: python3 make_final.py ref.jpg"""
import sys
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from scipy import ndimage, interpolate

im = Image.open(sys.argv[1]).convert('RGB')
x0, y0 = 92, 216
crop = im.crop((x0, y0, 708, 1090))
a = np.asarray(crop).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]

# label mask: colored/dark artwork, closed across thin silver lines
core = (np.max(np.stack([np.abs(R-G), np.abs(G-B), np.abs(R-B)]), axis=0) > 20) | ((R+G+B) < 260)
ci = Image.fromarray((core*255).astype('uint8')).filter(ImageFilter.MedianFilter(5))
ci = ci.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.MinFilter(15))
core = np.asarray(ci) > 128
lbl, _ = ndimage.label(core)
core = lbl == lbl[430, 300]
H, W = core.shape
rowfill = np.zeros_like(core)
for yy in range(H):
    xs = np.nonzero(core[yy])[0]
    if len(xs) > 10:
        rowfill[yy, xs[0]:xs[-1]+1] = True
colfill = np.zeros_like(core)
for xx in range(W):
    ys = np.nonzero(core[:, xx])[0]
    if len(ys) > 10:
        colfill[ys[0]:ys[-1]+1, xx] = True
mask = rowfill & colfill
mi = Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.MinFilter(29)).filter(ImageFilter.MaxFilter(29))
mask = np.asarray(mi) > 128

# radial boundary trace from centroid + median + periodic smoothing spline
ys_i, xs_i = np.nonzero(mask)
cy, cx = ys_i.mean(), xs_i.mean()
NA = 1440
rr = np.arange(0, 620, 0.5)
angles = np.linspace(0, 2*np.pi, NA, endpoint=False)
rad = np.zeros(NA)
for i, t in enumerate(angles):
    xs_r = cx + rr*np.cos(t); ys_r = cy + rr*np.sin(t)
    ok = (xs_r >= 0) & (xs_r < W) & (ys_r >= 0) & (ys_r < H)
    inside = np.zeros(len(rr), bool)
    inside[ok] = mask[ys_r[ok].astype(int), xs_r[ok].astype(int)]
    idx = np.nonzero(inside)[0]
    rad[i] = rr[idx[-1]] if len(idx) else 0
rad = ndimage.median_filter(np.r_[rad[-40:], rad, rad[:40]], size=17)[40:-40]
px = cx + rad*np.cos(angles); py = cy + rad*np.sin(angles)
tck, _ = interpolate.splprep([np.r_[px, px[0]], np.r_[py, py[0]]], per=1, s=len(px)*6.0)
u = np.linspace(0, 1, 900, endpoint=False)
sx, sy = interpolate.splev(u, tck)
pts = np.stack([sx, sy], 1)

d1 = np.roll(pts, -4, 0) - np.roll(pts, 4, 0)
nrm = np.stack([-d1[:, 1], d1[:, 0]], 1)
nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
sign = 1.0 if np.dot(nrm[0], np.array([cx, cy]) - pts[0]) > 0 else -1.0
clip_pts = pts + sign*10.5*nrm
border_pts = pts + sign*8.0*nrm

def path_of(p):
    xv = (p[:, 0] + x0 - 100) * (1000/600.0)
    yv = (p[:, 1] + y0 - 225) * (1000/600.0)
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in zip(xv, yv)) + " Z"

# sharpened artwork (clipped by the vector path at render time)
big = crop.resize((crop.width*2, crop.height*2), Image.LANCZOS)
big = big.filter(ImageFilter.UnsharpMask(radius=2, percent=110, threshold=2))
big = ImageEnhance.Contrast(big).enhance(1.02)
big.save('label_full.png')

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>COSTA 5W-30 Label (exact, clean edges)</title>
<style>
@page {{ size: 100mm 142.5mm; margin: 0; }}
html,body {{ margin:0; padding:0; }}
svg {{ display:block; width:100vw; height:100vh; }}
</style></head>
<body>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1425" width="100%" height="100%">
  <defs>
    <clipPath id="die"><path d="{path_of(clip_pts)}"/></clipPath>
    <linearGradient id="gMetal" x1="0" y1="0" x2="0.3" y2="1">
      <stop offset="0" stop-color="#f6f7f9"/><stop offset="0.25" stop-color="#c9ccd2"/>
      <stop offset="0.5" stop-color="#92969e"/><stop offset="0.7" stop-color="#e4e6ea"/>
      <stop offset="0.88" stop-color="#a9adb4"/><stop offset="1" stop-color="#eef0f2"/>
    </linearGradient>
  </defs>
  <g clip-path="url(#die)">
    <image x="-13.3" y="-15" width="1026.7" height="1456.7" preserveAspectRatio="none"
           href="label_full.png"/>
  </g>
  <path d="{path_of(border_pts)}" fill="none" stroke="#565a61" stroke-width="13" stroke-linejoin="round"/>
  <path d="{path_of(border_pts)}" fill="none" stroke="url(#gMetal)" stroke-width="10" stroke-linejoin="round"/>
  <path d="{path_of(border_pts)}" fill="none" stroke="#ffffff" stroke-width="1.6" opacity="0.7" stroke-linejoin="round"/>
</svg>
</body></html>"""
open('label_exact.html', 'w').write(html)
print('label_full.png + label_exact.html written')
