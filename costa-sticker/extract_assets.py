#!/usr/bin/env python3
"""Extracts the raster assets (engine photo circle, oil splash) from the
reference bottle photo. Expects the reference image path as argv[1]."""
import sys
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

im = Image.open(sys.argv[1]).convert('RGB')

# engine circle: photo centre (250,839), r=104
cx, cy, r = 250, 839, 104
im.crop((cx-r, cy-r, cx+r, cy+r)).resize((520, 520), Image.LANCZOS).save('engine_crop.png')

# oil splash: chroma-key the warm pixels out of the blue background
x0, y0 = 300, 865
sp = im.crop((x0, y0, 710, 1065))
a = np.asarray(sp).astype(int)
R, B = a[..., 0], a[..., 2]
alpha = np.clip(((R - B) - 2) * 5.5, 0, 255).astype(float)
alpha = 255.0 * (alpha / 255.0) ** 0.55
yy, xx = np.mgrid[0:sp.height, 0:sp.width]
alpha[(xx - (528 - x0))**2 + (yy - (1032 - y0))**2 <= 46**2] = 0  # flag circle
alpha[:930 - y0, :595 - x0] = 0                                   # API band area
mask = Image.fromarray(alpha.astype('uint8'), 'L').filter(ImageFilter.GaussianBlur(0.6))
sp = ImageEnhance.Brightness(ImageEnhance.Color(sp).enhance(1.18)).enhance(1.04)
out = sp.convert('RGBA')
out.putalpha(mask)
out.save('splash_crop.png')
print('assets extracted')
