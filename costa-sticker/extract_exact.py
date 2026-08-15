#!/usr/bin/env python3
"""Extracts the complete label artwork from the reference bottle photo as a
die-cut RGBA image (label_exact.png). Usage: python3 extract_exact.py ref.jpg"""
import sys
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from scipy import ndimage

im = Image.open(sys.argv[1]).convert('RGB')
x0, y0, x1, y1 = 92, 216, 708, 1090
crop = im.crop((x0, y0, x1, y1))
a = np.asarray(crop).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]

chroma = np.max(np.stack([np.abs(R-G), np.abs(G-B), np.abs(R-B)]), axis=0)
core = (chroma > 20) | ((R+G+B) < 260)
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

mi = Image.fromarray((mask*255).astype('uint8'))
mi = mi.filter(ImageFilter.MinFilter(29)).filter(ImageFilter.MaxFilter(29))
mask = np.asarray(mi) > 128
left = np.array([np.nonzero(mask[yy])[0][0] if mask[yy].any() else W for yy in range(H)], float)
right = np.array([np.nonzero(mask[yy])[0][-1] if mask[yy].any() else -1 for yy in range(H)], float)
ls = ndimage.median_filter(left, 61, mode='nearest')
rs = ndimage.median_filter(right, 61, mode='nearest')
for yy in range(130, H):
    if mask[yy].any():
        mask[yy, :int(max(ls[yy]-4, 0))] = False
        mask[yy, int(min(rs[yy]+4, W-1))+1:] = False

m = Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(1.2))
out = crop.convert('RGBA'); out.putalpha(m)
big = out.resize((out.width*2, out.height*2), Image.LANCZOS)
rgb = big.convert('RGB').filter(ImageFilter.UnsharpMask(radius=2, percent=110, threshold=2))
rgb = ImageEnhance.Contrast(rgb).enhance(1.02)
final = rgb.convert('RGBA'); final.putalpha(big.getchannel('A'))
final.save('label_exact.png')
print('label_exact.png written')
