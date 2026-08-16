#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hybrid master: the exact label raster (from the reference photo) as the
base, with vector overlays for every hard-edged element, positioned by
direct measurement OF THE RENDERED BASE (same coordinate space, zero
mapping error).  ViewBox 1000 x 1425 = 100 x 142.5 mm.
"""
import math

W, H = 1000, 1425
CLIP = open('die_clip2.txt').read()      # smooth spline die (true shape)
BORDER = open('die_border2.txt').read()


def wavy(cx, cy, r_mid, amp, n, phase=1.5708, samples=240):
    pts = []
    for i in range(samples):
        t = 2 * math.pi * i / samples
        r = r_mid + amp * math.cos(n * t + phase)
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def star4(cx, cy, r, r2=None):
    r2 = r2 or r * 0.3
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r2
        a = math.pi * i / 4 - math.pi / 2
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


DEFS = f"""
<defs>
  <clipPath id="die"><path d="{CLIP}"/></clipPath>
  <linearGradient id="gMetal" x1="0" y1="0" x2="0.3" y2="1">
    <stop offset="0" stop-color="#f6f7f9"/><stop offset="0.25" stop-color="#c9ccd2"/>
    <stop offset="0.5" stop-color="#92969e"/><stop offset="0.7" stop-color="#e4e6ea"/>
    <stop offset="0.88" stop-color="#a9adb4"/><stop offset="1" stop-color="#eef0f2"/>
  </linearGradient>
  <linearGradient id="gGold" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fdf6dc"/><stop offset="0.3" stop-color="#f3d788"/>
    <stop offset="0.55" stop-color="#e9c86c"/><stop offset="0.8" stop-color="#c69a3c"/>
    <stop offset="1" stop-color="#a87b22"/>
  </linearGradient>
  <radialGradient id="gDropA" cx="0.4" cy="0.3" r="1">
    <stop offset="0" stop-color="#fde9a8"/><stop offset="0.55" stop-color="#efb43a"/>
    <stop offset="1" stop-color="#c07a08"/>
  </radialGradient>
  <linearGradient id="gWhiteT" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#f2f4f6"/>
    <stop offset="1" stop-color="#c9d0d8"/>
  </linearGradient>
  <linearGradient id="gNavyBand" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2c3c7c"/><stop offset="0.5" stop-color="#1e2b5c"/>
    <stop offset="1" stop-color="#141f46"/>
  </linearGradient>
  <linearGradient id="gSilverBar" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#6f747c"/><stop offset="0.3" stop-color="#eef1f4"/>
    <stop offset="0.55" stop-color="#f8fafc"/><stop offset="0.82" stop-color="#b0b6be"/>
    <stop offset="1" stop-color="#5f646c"/>
  </linearGradient>
  <linearGradient id="gRing" x1="0" y1="0" x2="0.3" y2="1">
    <stop offset="0" stop-color="#fbfcfd"/><stop offset="0.3" stop-color="#c3c7cd"/>
    <stop offset="0.55" stop-color="#888d95"/><stop offset="0.75" stop-color="#dcdfe3"/>
    <stop offset="1" stop-color="#9599a1"/>
  </linearGradient>
  <radialGradient id="gDiscS" cx="0.42" cy="0.35" r="0.9">
    <stop offset="0" stop-color="#fafbfc"/><stop offset="0.45" stop-color="#e2e6ea"/>
    <stop offset="0.75" stop-color="#c2c8cf"/><stop offset="1" stop-color="#959ba3"/>
  </radialGradient>
  <linearGradient id="gPlate" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3c3f46"/><stop offset="0.5" stop-color="#191a1f"/>
    <stop offset="1" stop-color="#070709"/>
  </linearGradient>
  <pattern id="pCarbon" width="10" height="10" patternUnits="userSpaceOnUse"
           patternTransform="rotate(45 0 0)">
    <rect width="10" height="10" fill="#101114"/>
    <rect width="5" height="5" fill="#1c1e23"/>
    <rect x="5" y="5" width="5" height="5" fill="#1c1e23"/>
    <rect width="5" height="1.4" fill="#2a2d34"/>
    <rect x="5" y="5" width="5" height="1.4" fill="#2a2d34"/>
  </pattern>
  <filter id="fSh" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#02102e" flood-opacity="0.45"/>
  </filter>
  <filter id="fTx" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#01102c" flood-opacity="0.5"/>
  </filter>
  <radialGradient id="gGlossF" cx="0.32" cy="0.22" r="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.4"/>
    <stop offset="0.45" stop-color="#ffffff" stop-opacity="0.06"/>
    <stop offset="1" stop-color="#000000" stop-opacity="0.3"/>
  </radialGradient>
</defs>"""

BASE = """
<g clip-path="url(#die)">
  <image x="-13.3" y="-15" width="1026.7" height="1456.7" preserveAspectRatio="none"
         href="label_full.png"/>
</g>"""

# ---- logo: cap 66 (241..307), x 270..680, centre 472; O centre 395 --------
LOGO = """
<g filter="url(#fTx)">
  <text x="484" y="331.5" text-anchor="middle" font-family="Russo" font-size="101"
        letter-spacing="22.5" fill="#5a3d0e">COSTA</text>
  <text x="484" y="329" text-anchor="middle" font-family="Russo" font-size="101"
        letter-spacing="22.5" fill="url(#gGold)" stroke="#7a5716" stroke-width="1">COSTA</text>
</g>
<path d="M 382.6 260 C 375.5 278 369 288 369 296 a 13.6 13.6 0 0 0 27.2 0 C 396.2 288 389.7 278 382.6 260 Z"
      fill="url(#gDropA)" stroke="#ffffff" stroke-width="2.2"/>
<ellipse cx="377.5" cy="292" rx="2.9" ry="4.5" fill="#fff6d8" opacity="0.85" transform="rotate(-14 377.5 292)"/>
<text x="486" y="381" text-anchor="middle" font-family="Montserrat" font-weight="500"
      font-size="16" letter-spacing="19" fill="#f0e8d0">LUBRICANT</text>"""

# ---- ENGINE OIL: cap 48 (497..545), x 192..560, centre 376 ----------------
EOIL = """
<g filter="url(#fTx)">
  <text x="376" y="582" text-anchor="middle" font-family="Russo" font-size="55"
        letter-spacing="9" fill="url(#gWhiteT)">ENGINE OIL</text>
</g>"""

# ---- medal: centre (818,682), scallop outer 99 ----------------------------
bcx, bcy = 850, 743
BADGE = f"""
<g filter="url(#fSh)">
  <path d="{wavy(bcx, bcy, 103, 8, 13)}" fill="url(#gRing)" stroke="#63676e" stroke-width="1.4"/>
  <circle cx="{bcx}" cy="{bcy}" r="100" fill="url(#gDiscS)"/>
  <circle cx="{bcx}" cy="{bcy}" r="86" fill="none" stroke="#16264f" stroke-width="11.5"/>
  <circle cx="{bcx}" cy="{bcy}" r="79.5" fill="url(#gDiscS)"/>
  <g fill="#16264f">
    <path d="{star4(bcx - 52, bcy - 42, 7.5)}"/>
    <path d="{star4(bcx + 52, bcy - 42, 7.5)}"/>
    <text x="{bcx}" y="{bcy - 32}" text-anchor="middle" font-family="Montserrat" font-weight="800"
          font-size="30">100%</text>
    <g transform="scale(0.62 1)">
      <text x="{bcx / 0.62:.1f}" y="{bcy + 40}" text-anchor="middle" font-family="Lora"
            font-weight="700" font-size="84">BEST</text>
    </g>
    <text x="{bcx}" y="{bcy + 55}" text-anchor="middle" font-family="Montserrat" font-weight="600"
          font-size="19" letter-spacing="4">QUALITY</text>
    <rect x="{bcx - 43}" y="{bcy + 62}" width="86" height="2.2"/>
    <rect x="{bcx - 30}" y="{bcy + 69}" width="60" height="2.2"/>
  </g>
</g>"""

# ---- bands: rows 834..1097, left end 452 (rounded), texts at x=480 --------
BANDS = f"""
<defs><clipPath id="bandsClip">
  <path d="M 474 878 H 992 V 1183 H 474 A 22 22 0 0 1 452 1161 V 900 A 22 22 0 0 1 474 878 Z"/>
</clipPath></defs>
<g clip-path="url(#die)">
<g clip-path="url(#bandsClip)">
  <rect x="440" y="878" width="560" height="305" fill="url(#gNavyBand)"/>
  <rect x="440" y="878" width="560" height="17" fill="url(#gSilverBar)"/>
  <rect x="440" y="965" width="560" height="12" fill="url(#gSilverBar)"/>
  <rect x="440" y="977" width="560" height="112" fill="#101114"/>
  <rect x="440" y="977" width="560" height="112" fill="url(#pCarbon)" opacity="0.95"/>
  <rect x="440" y="1089" width="560" height="11" fill="url(#gSilverBar)"/>
  <rect x="440" y="1172" width="560" height="9" fill="url(#gSilverBar)"/>
  <text x="481" y="943" font-family="Russo" font-size="33" letter-spacing="13"
        fill="#f2e8c0">SYNTHETIC</text>
  <g filter="url(#fTx)">
    <text x="480" y="1064" font-family="Russo" font-size="82" letter-spacing="15.5"
          fill="url(#gWhiteT)">5W-30</text>
  </g>
  <text x="489" y="1151" font-family="Russo" font-size="40" fill="url(#gWhiteT)">API<tspan
        fill="#f2e8c0" dx="18">SP</tspan></text>
</g>
</g>"""

# ---- engine ring: centre (265,967), band 157..171 -------------------------
RING = """
<circle cx="255" cy="1034" r="178" fill="none" stroke="url(#gRing)" stroke-width="13"/>
<circle cx="255" cy="1034" r="171" fill="none" stroke="#71767d" stroke-width="1.5"/>
<circle cx="255" cy="1034" r="185" fill="none" stroke="#83878d" stroke-width="1.4"/>"""

# ---- 5L: x 88..275, cap 112 (1218..1330) ----------------------------------
FIVEL = """
<g filter="url(#fTx)">
  <g transform="scale(1.23 1)">
    <text x="55.3" y="1397" font-family="Russo" font-size="99"
          fill="url(#gWhiteT)">5<tspan font-size="59" dx="2">L</tspan></text>
  </g>
</g>"""

# ---- german: rosette (712,1262), plate to x 916 ---------------------------
GER = f"""
<g filter="url(#fSh)">
  <path d="M 775 1300 H 908 L 948 1342 L 908 1384 H 775 Z" fill="url(#gPlate)"
        stroke="#8b8f96" stroke-width="1.4" stroke-linejoin="round"/>
  <text x="792" y="1341" font-family="Montserrat" font-weight="500" font-size="20"
        letter-spacing="9" fill="#e8ebef">GERMAN</text>
  <text x="792" y="1359" font-family="Montserrat" font-weight="800" font-size="20"
        letter-spacing="0.5" fill="#ffffff">TECHNOLOGY</text>
</g>
<g filter="url(#fSh)">
  <path d="{wavy(728, 1342, 55, 6, 10)}" fill="#17181c" stroke="#3a3d43" stroke-width="1.4"/>
  <circle cx="728" cy="1342" r="48" fill="url(#gRing)"/>
  <clipPath id="fcl"><circle cx="728" cy="1342" r="45"/></clipPath>
  <g clip-path="url(#fcl)">
    <rect x="683" y="1297" width="90" height="30" fill="#161616"/>
    <rect x="683" y="1327" width="90" height="30" fill="#d5121e"/>
    <rect x="683" y="1357" width="90" height="30" fill="#f7c500"/>
    <circle cx="728" cy="1342" r="45" fill="url(#gGlossF)"/>
  </g>
</g>"""

FRAME = f"""
<path d="{BORDER}" fill="none" stroke="#565a61" stroke-width="13" stroke-linejoin="round"/>
<path d="{BORDER}" fill="none" stroke="url(#gMetal)" stroke-width="10" stroke-linejoin="round"/>
<path d="{BORDER}" fill="none" stroke="#ffffff" stroke-width="1.6" opacity="0.7" stroke-linejoin="round"/>"""

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">
{DEFS}
{BASE}
{LOGO}
{EOIL}
{BADGE}
{BANDS}
{RING}
{FIVEL}
{GER}
{FRAME}
</svg>"""

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>COSTA 5W-30 Label — master</title>
<style>
@font-face {{ font-family:'Russo';      src:url('fonts/RussoOne-400.ttf'); }}
@font-face {{ font-family:'Montserrat'; font-weight:500; src:url('fonts/Montserrat-500.ttf'); }}
@font-face {{ font-family:'Montserrat'; font-weight:600; src:url('fonts/Montserrat-600.ttf'); }}
@font-face {{ font-family:'Montserrat'; font-weight:800; src:url('fonts/Montserrat-800.ttf'); }}
@font-face {{ font-family:'Lora';       font-weight:700; src:url('fonts/Lora-Bold.ttf'); }}
@page {{ size: 100mm 142.5mm; margin: 0; }}
html,body {{ margin:0; padding:0; }}
svg {{ display:block; width:100vw; height:100vh; }}
</style></head>
<body>{svg}</body></html>"""

open('label_hybrid.html', 'w').write(html)
print('hybrid v2 written')
