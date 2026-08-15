#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generates the COSTA Lubricant 5W-30 5L label as HTML with inline SVG.

Geometry, colors and typography are measured directly off the reference
bottle photo.  Photo label region: x 100..700, y 225..1080 (600 x 855 px)
mapped uniformly (x1.6667) to a 1000 x 1425 viewBox = 100 x 142.5 mm print.
The engine photo and the oil splash are extracted from the reference image
itself (engine_crop.png / splash_crop.png) and embedded as raster elements.
"""
import base64
import math
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "fonts"
OUT = os.path.join(BASE, "label.html")

W, H = 1000, 1425

# The sticker die-cut follows the bottle panel: slanted left edge, straight
# top, a big sweeping top-right corner, gently bulging right edge.
DIE = ("M 168 3 H 753 "
       "C 852 25 936 180 948 424 "
       "L 999 1392 "
       "Q 1000 1420 974 1420 "
       "L 34 1420 Q 8 1420 9 1394 "
       "C 34 1030 100 420 146 26 "
       "Q 150 3 168 3 Z")

# Diagonal divider between the dark navy zone (upper-left) and the light
# glow wedge (lower-right).
DIVIDER = "M -2 867 C 250 852 520 780 720 705 C 850 655 902 540 925 425"
DARKSIDE = ("M -2 867 C 250 852 520 780 720 705 C 850 655 902 540 925 425 "
            "L 1004 465 L 1004 -4 L -4 -4 Z")
WEDGE = ("M -2 867 C 250 852 520 780 720 705 C 850 655 902 540 925 425 "
         "L 1004 465 L 1004 1429 L -4 1429 Z")

# Decorative silver S-arc inside the dark zone (parallels the top-right
# corner, then sweeps left underneath the logo block).
SARC = "M 614 4 C 780 100 870 280 820 390 C 740 470 350 460 -2 462"


def b64(path):
    with open(os.path.join(BASE, path), "rb") as f:
        return base64.b64encode(f.read()).decode()


# ---------------------------------------------------------------- helpers
def wavy_rosette(cx, cy, r_mid, amp, n, samples=240):
    pts = []
    for i in range(samples):
        t = 2 * math.pi * i / samples
        r = r_mid + amp * math.cos(n * t)
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


def streaks(seed, n_light, n_dark, alpha_lo, alpha_hi):
    import random
    random.seed(seed)
    out = []
    for i in range(n_light):
        x = -700 + i * (2400 // max(n_light, 1)) + random.uniform(-16, 16)
        w = random.choice([3, 4, 6, 9, 14, 22, 34])
        op = random.uniform(alpha_lo, alpha_hi)
        out.append(f'<rect x="{x:.0f}" y="-400" width="{w}" height="2400" fill="#cfe4ff" opacity="{op:.3f}"/>')
    for i in range(n_dark):
        x = -650 + i * (2300 // max(n_dark, 1)) + random.uniform(-30, 30)
        w = random.choice([8, 14, 24, 40])
        op = random.uniform(alpha_lo * 0.8, alpha_hi * 0.8)
        out.append(f'<rect x="{x:.0f}" y="-400" width="{w}" height="2400" fill="#021030" opacity="{op:.3f}"/>')
    return "\n".join(out)


# ---------------------------------------------------------------- defs
def defs():
    return f"""
<defs>
  <clipPath id="clipDie"><path d="{DIE}"/></clipPath>
  <clipPath id="clipDark"><path d="{DARKSIDE}"/></clipPath>
  <clipPath id="clipWedge"><path d="{WEDGE}"/></clipPath>
  <clipPath id="clipEngine"><circle cx="250" cy="1033" r="175"/></clipPath>
  <clipPath id="clipFlagC"><circle cx="720" cy="1338" r="44"/></clipPath>

  <linearGradient id="gFrame" x1="0" y1="0" x2="0.25" y2="1">
    <stop offset="0" stop-color="#f4f5f7"/><stop offset="0.22" stop-color="#c7cad0"/>
    <stop offset="0.45" stop-color="#94989f"/><stop offset="0.62" stop-color="#e2e4e8"/>
    <stop offset="0.8" stop-color="#a4a8af"/><stop offset="1" stop-color="#eceef0"/>
  </linearGradient>
  <linearGradient id="gBase" x1="0" y1="0" x2="0.45" y2="1">
    <stop offset="0" stop-color="#212a63"/><stop offset="0.4" stop-color="#273176"/>
    <stop offset="0.75" stop-color="#24409a"/><stop offset="1" stop-color="#2a4aa6"/>
  </linearGradient>
  <linearGradient id="gWedge" x1="0.2" y1="0" x2="0.7" y2="1">
    <stop offset="0" stop-color="#3a7dc0"/><stop offset="0.45" stop-color="#4c93d6"/>
    <stop offset="1" stop-color="#357cc0"/>
  </linearGradient>
  <radialGradient id="gGlow" cx="0.66" cy="0.44" r="0.62">
    <stop offset="0" stop-color="#bfe2fa" stop-opacity="0.95"/>
    <stop offset="0.45" stop-color="#8ec6f2" stop-opacity="0.6"/>
    <stop offset="1" stop-color="#8ec6f2" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="gSilverLine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.3"/>
    <stop offset="0.35" stop-color="#eef1f5" stop-opacity="0.95"/>
    <stop offset="0.65" stop-color="#b3bac3" stop-opacity="0.9"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0.35"/>
  </linearGradient>
  <linearGradient id="gSilverBar" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#6f747c"/><stop offset="0.25" stop-color="#e9edf1"/>
    <stop offset="0.55" stop-color="#f8fafc"/><stop offset="0.8" stop-color="#b9bfc7"/>
    <stop offset="1" stop-color="#5f646c"/>
  </linearGradient>
  <linearGradient id="gGold" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fbeed0"/><stop offset="0.3" stop-color="#f3d788"/>
    <stop offset="0.55" stop-color="#e9c86c"/><stop offset="0.8" stop-color="#c69a3c"/>
    <stop offset="1" stop-color="#a87b22"/>
  </linearGradient>
  <radialGradient id="gDropAmber" cx="0.4" cy="0.3" r="1">
    <stop offset="0" stop-color="#fde9a8"/><stop offset="0.55" stop-color="#efb43a"/>
    <stop offset="1" stop-color="#c07a08"/>
  </radialGradient>
  <linearGradient id="gSilverText" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#eef1f4"/>
    <stop offset="1" stop-color="#c3cad2"/>
  </linearGradient>
  <linearGradient id="gNavyBand" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#25376c"/><stop offset="0.5" stop-color="#16264f"/>
    <stop offset="1" stop-color="#0e1a3a"/>
  </linearGradient>
  <linearGradient id="gBlueBand" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3a68c8"/><stop offset="0.5" stop-color="#2650aa"/>
    <stop offset="1" stop-color="#183a86"/>
  </linearGradient>
  <linearGradient id="gRing" x1="0" y1="0" x2="0.3" y2="1">
    <stop offset="0" stop-color="#fbfcfd"/><stop offset="0.3" stop-color="#c3c7cd"/>
    <stop offset="0.55" stop-color="#888d95"/><stop offset="0.75" stop-color="#dcdfe3"/>
    <stop offset="1" stop-color="#9599a1"/>
  </linearGradient>
  <radialGradient id="gDiscSilver" cx="0.42" cy="0.35" r="0.9">
    <stop offset="0" stop-color="#fafbfc"/><stop offset="0.45" stop-color="#dfe3e7"/>
    <stop offset="0.75" stop-color="#bcc2c9"/><stop offset="1" stop-color="#8f959d"/>
  </radialGradient>
  <linearGradient id="gDiscSheen" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.7"/>
    <stop offset="0.4" stop-color="#ffffff" stop-opacity="0"/>
    <stop offset="0.7" stop-color="#6d737b" stop-opacity="0.25"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0.4"/>
  </linearGradient>
  <linearGradient id="gPlate" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3c3f46"/><stop offset="0.5" stop-color="#191a1f"/>
    <stop offset="1" stop-color="#070709"/>
  </linearGradient>
  <pattern id="pCarbon" width="12" height="12" patternUnits="userSpaceOnUse"
           patternTransform="rotate(45 0 0)">
    <rect width="12" height="12" fill="#131417"/>
    <rect width="6" height="6" fill="#1e2025"/>
    <rect x="6" y="6" width="6" height="6" fill="#1e2025"/>
    <rect width="6" height="1.6" fill="#2c2f36"/>
    <rect x="6" y="6" width="6" height="1.6" fill="#2c2f36"/>
  </pattern>
  <filter id="fShadow" x="-40%" y="-40%" width="180%" height="180%">
    <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#02102e" flood-opacity="0.5"/>
  </filter>
  <filter id="fShadowS" x="-40%" y="-40%" width="180%" height="180%">
    <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#02102e" flood-opacity="0.45"/>
  </filter>
  <filter id="fTextShadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="2.5" stdDeviation="2.5" flood-color="#01102c" flood-opacity="0.5"/>
  </filter>
  <radialGradient id="gGlossFlag" cx="0.32" cy="0.22" r="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.4"/>
    <stop offset="0.45" stop-color="#ffffff" stop-opacity="0.06"/>
    <stop offset="1" stop-color="#000000" stop-opacity="0.3"/>
  </radialGradient>
</defs>"""


# ---------------------------------------------------------------- pieces
def background():
    return f"""
<!-- ================= background ================= -->
<g clip-path="url(#clipDie)">
  <rect x="0" y="0" width="1000" height="1425" fill="url(#gBase)"/>
  <!-- strong brushed streaks over the dark zone -->
  <g clip-path="url(#clipDark)">
    <g transform="rotate(-55 480 500)">{streaks(7, 44, 15, 0.06, 0.17)}</g>
  </g>
  <!-- light glow wedge, lower-right of the divider -->
  <path d="{WEDGE}" fill="url(#gWedge)"/>
  <g clip-path="url(#clipWedge)">
    <rect x="280" y="380" width="740" height="1050" fill="url(#gGlow)"/>
    <!-- giant glossy swirl across the bottom half -->
    <circle cx="520" cy="1270" r="420" fill="#8fc8f3" opacity="0.20"/>
    <circle cx="560" cy="1300" r="330" fill="#a5d3f6" opacity="0.14"/>
    <g fill="none">
      <circle cx="520" cy="1270" r="420" stroke="#cfe8fb" stroke-width="16" opacity="0.85"/>
      <circle cx="560" cy="1300" r="330" stroke="#daeefc" stroke-width="10" opacity="0.65"/>
      <circle cx="500" cy="1240" r="492" stroke="#8ec6f2" stroke-width="24" opacity="0.35"/>
      <circle cx="600" cy="1340" r="245" stroke="#cfe8fb" stroke-width="8" opacity="0.4"/>
    </g>
    <g transform="rotate(-55 700 800)">{streaks(5, 26, 9, 0.035, 0.10)}</g>
  </g>
  <!-- divider piping -->
  <path d="{DIVIDER}" stroke="#0a1c4a" stroke-width="2.5" fill="none" opacity="0.4" transform="translate(3,3)"/>
  <path d="{DIVIDER}" stroke="url(#gSilverLine)" stroke-width="4" fill="none"/>
  <!-- decorative S-arc inside the dark zone -->
  <path d="{SARC}" stroke="url(#gSilverLine)" stroke-width="3" fill="none" opacity="0.9"/>
  <!-- sparkles on the gloss -->
  <g fill="#ffffff" opacity="0.9">
    <path d="{star4(708, 1233, 9)}"/>
    <path d="{star4(747, 1263, 6)}"/>
    <path d="{star4(768, 1286, 5)}"/>
  </g>
  <!-- corner vignette -->
  <rect x="0" y="0" width="1000" height="1425" fill="#02123a" opacity="0.08"
        style="mix-blend-mode:multiply"/>
</g>"""


def logo():
    # COSTA in Russo One squeezed to 90%, centre x=470, baseline 345, cap 103.
    # O centre x=380: amber drop sits inside the O.
    return """
<!-- ================= logo ================= -->
<g filter="url(#fTextShadow)">
  <g transform="scale(0.88 1)">
    <text x="531.8" y="370.5" text-anchor="middle" font-family="Russo" font-size="152"
          fill="#5a3d0e">COSTA</text>
    <text x="531.8" y="366" text-anchor="middle" font-family="Russo" font-size="152"
          fill="url(#gGold)" stroke="#7a5716" stroke-width="1.2">COSTA</text>
    <text x="531.8" y="364.6" text-anchor="middle" font-family="Russo" font-size="152"
          fill="none" stroke="#fff3cf" stroke-width="0.8" opacity="0.75">COSTA</text>
  </g>
</g>
<!-- amber drop inside the O -->
<path d="M 379 273 C 371 293 363 304 363 315 a 16 16 0 0 0 32 0 C 395 304 387 293 379 273 Z"
      fill="url(#gDropAmber)" stroke="#ffffff" stroke-width="2.5"/>
<ellipse cx="373" cy="310" rx="3.6" ry="5.5" fill="#fff6d8" opacity="0.85" transform="rotate(-14 373 302)"/>
<text x="468" y="404" text-anchor="middle" font-family="Montserrat" font-weight="500"
      font-size="25" letter-spacing="16" fill="#ebd9a8">LUBRICANT</text>
"""


def engine_oil():
    return """
<!-- ================= ENGINE OIL ================= -->
<g filter="url(#fTextShadow)">
  <g transform="scale(0.92 1)">
    <text x="402" y="584" text-anchor="middle" font-family="Russo" font-size="82"
          letter-spacing="2" fill="#ffffff">ENGINE OIL</text>
  </g>
</g>"""


def badge():
    cx, cy = 845, 735
    star_l = star4(cx - 56, cy - 46, 8)
    star_r = star4(cx + 56, cy - 46, 8)
    return f"""
<!-- ================= best quality medal (silver) ================= -->
<g filter="url(#fShadow)">
  <path d="{wavy_rosette(cx, cy, 100, 8, 13)}" fill="url(#gRing)" stroke="#63676e" stroke-width="1.5"/>
  <circle cx="{cx}" cy="{cy}" r="97" fill="url(#gDiscSilver)"/>
  <circle cx="{cx}" cy="{cy}" r="87" fill="none" stroke="#16264f" stroke-width="11"/>
  <circle cx="{cx}" cy="{cy}" r="81" fill="url(#gDiscSilver)"/>
  <circle cx="{cx}" cy="{cy}" r="81" fill="url(#gDiscSheen)"/>
  <g fill="#16264f">
    <path d="{star_l}"/><path d="{star_r}"/>
    <text x="{cx}" y="{cy - 35}" text-anchor="middle" font-family="Montserrat" font-weight="800"
          font-size="34">100%</text>
    <g transform="scale(0.68 1)">
      <text x="{cx / 0.68:.1f}" y="{cy + 20}" text-anchor="middle" font-family="Lora" font-weight="700"
            font-size="69">BEST</text>
    </g>
    <text x="{cx}" y="{cy + 45}" text-anchor="middle" font-family="Montserrat" font-weight="600"
          font-size="24" letter-spacing="4">QUALITY</text>
    <rect x="{cx - 44}" y="{cy + 51}" width="88" height="2.2"/>
    <rect x="{cx - 30}" y="{cy + 58}" width="60" height="2.2"/>
  </g>
</g>"""


def bands():
    x0, x1, tx = 400, 992, 465
    return f"""
<!-- ================= spec bands ================= -->
<g clip-path="url(#clipDie)">
  <rect x="{x0}" y="880" width="{x1 - x0}" height="4" fill="url(#gSilverLine)"/>
  <rect x="{x0}" y="884" width="{x1 - x0}" height="68" fill="url(#gNavyBand)"/>
  <rect x="{x0}" y="952" width="{x1 - x0}" height="16" fill="url(#gSilverBar)"/>
  <rect x="{x0}" y="968" width="{x1 - x0}" height="120" fill="#131417"/>
  <rect x="{x0}" y="968" width="{x1 - x0}" height="120" fill="url(#pCarbon)" opacity="0.9"/>
  <rect x="{x0}" y="1088" width="{x1 - x0}" height="16" fill="url(#gSilverBar)"/>
  <rect x="{x0}" y="1104" width="{x1 - x0}" height="72" fill="url(#gBlueBand)"/>
  <rect x="{x0}" y="1176" width="{x1 - x0}" height="4" fill="url(#gSilverLine)"/>

  <g transform="scale(0.85 1)">
    <text x="{tx / 0.85}" y="941" font-family="Russo" font-size="65" letter-spacing="4"
          fill="#f2e8c0">SYNTHETIC</text>
  </g>
  <g filter="url(#fTextShadow)">
    <text x="{tx}" y="1073" font-family="Russo" font-size="128" letter-spacing="2"
          fill="#ffffff">5W-30</text>
  </g>
  <text x="{tx}" y="1163" font-family="Russo" font-size="64" fill="#ffffff">API<tspan
        fill="#f2e8c0" dx="22">SP</tspan></text>
</g>"""


def engine_circle():
    img = b64("engine_crop.png")
    return f"""
<!-- ================= engine photo (extracted from reference) ============ -->
<g filter="url(#fShadow)">
  <circle cx="250" cy="1033" r="187" fill="url(#gRing)"/>
</g>
<g clip-path="url(#clipEngine)">
  <image x="63" y="846" width="374" height="374" preserveAspectRatio="none"
         href="data:image/png;base64,{img}"/>
</g>
<circle cx="250" cy="1033" r="176" fill="none" stroke="#71767d" stroke-width="1.5"/>
<circle cx="250" cy="1033" r="187" fill="none" stroke="#83878d" stroke-width="1.2"/>
"""


def splash():
    img = b64("splash_crop.png")
    return f"""
<!-- ================= oil splash (extracted from reference) ============= -->
<g clip-path="url(#clipDie)">
  <image x="325" y="1067" width="692" height="350" preserveAspectRatio="none"
         href="data:image/png;base64,{img}"/>
</g>"""


def five_l():
    return """
<!-- ================= 5L ================= -->
<g filter="url(#fTextShadow)">
  <text x="50" y="1405" font-family="Russo" font-size="139"
        fill="url(#gSilverText)">5<tspan font-size="93" dx="3">L</tspan></text>
</g>"""


def german():
    cx, cy = 720, 1338
    return f"""
<!-- ================= german technology ================= -->
<g filter="url(#fShadowS)">
  <path d="M 775 1303 H 910 L 950 1339 L 910 1375 H 775 Z" fill="url(#gPlate)"
        stroke="#8b8f96" stroke-width="1.5" stroke-linejoin="round"/>
  <text x="795" y="1333" font-family="Montserrat" font-weight="500" font-size="20"
        letter-spacing="9" fill="#e8ebef">GERMAN</text>
  <text x="795" y="1364" font-family="Montserrat" font-weight="800" font-size="20"
        letter-spacing="1" fill="#ffffff">TECHNOLOGY</text>
</g>
<g filter="url(#fShadowS)">
  <path d="{wavy_rosette(cx, cy, 52, 6, 10)}" fill="#17181c" stroke="#3a3d43" stroke-width="1.5"/>
  <circle cx="{cx}" cy="{cy}" r="47" fill="url(#gRing)"/>
  <g clip-path="url(#clipFlagC)">
    <rect x="{cx - 44}" y="{cy - 44}" width="88" height="30" fill="#161616"/>
    <rect x="{cx - 44}" y="{cy - 14}" width="88" height="29" fill="#d5121e"/>
    <rect x="{cx - 44}" y="{cy + 15}" width="88" height="29" fill="#f7c500"/>
    <circle cx="{cx}" cy="{cy}" r="44" fill="url(#gGlossFlag)"/>
  </g>
</g>"""


def frame():
    return f"""
<!-- ================= die-cut silver border ================= -->
<path d="{DIE}" fill="none" stroke="url(#gFrame)" stroke-width="9"/>
<path d="{DIE}" fill="none" stroke="#787c84" stroke-width="1.4" opacity="0.9"
      transform="translate(0,0)"/>"""


def html():
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
{defs()}
{background()}
{logo()}
{engine_oil()}
{badge()}
{bands()}
{engine_circle()}
{splash()}
{five_l()}
{german()}
{frame()}
</svg>"""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>COSTA 5W-30 Label</title>
<style>
@font-face {{ font-family:'Russo';      src:url('{FONT_DIR}/RussoOne-400.ttf'); }}
@font-face {{ font-family:'Montserrat'; font-weight:500; src:url('{FONT_DIR}/Montserrat-500.ttf'); }}
@font-face {{ font-family:'Montserrat'; font-weight:600; src:url('{FONT_DIR}/Montserrat-600.ttf'); }}
@font-face {{ font-family:'Montserrat'; font-weight:800; src:url('{FONT_DIR}/Montserrat-800.ttf'); }}
@font-face {{ font-family:'Lora';       font-weight:700; src:url('{FONT_DIR}/Lora-Bold.ttf'); }}
@page {{ size: 100mm 142.5mm; margin: 0; }}
html,body {{ margin:0; padding:0; }}
svg {{ display:block; width:100vw; height:100vh; }}
</style></head>
<body>{svg}</body></html>"""


open(OUT, "w").write(html())
print("wrote", OUT)
