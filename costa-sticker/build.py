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
       "C 850 27 940 200 947 425 "
       "C 975 700 998 1150 999 1395 "
       "Q 999 1420 975 1420 "
       "L 32 1420 Q 8 1420 9 1396 "
       "C 30 1000 105 350 148 20 "
       "Q 152 3 168 3 Z")

# Diagonal divider between the dark navy zone (upper-left) and the light
# glow wedge (lower-right).
DIVIDER = "M 942 433 C 720 720 480 1030 292 1425"
DARKSIDE = "M 942 433 C 720 720 480 1030 292 1425 L -2 1427 L -2 -2 L 947 -2 Z"
WEDGE = "M 942 433 C 720 720 480 1030 292 1425 L 1004 1425 L 1004 420 Z"

# Decorative silver S-arc inside the dark zone (parallels the top-right
# corner, then sweeps left underneath the logo block).
SARC = "M 742 6 C 880 100 935 290 830 380 C 700 480 380 445 130 505"


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
  <clipPath id="clipEngine"><circle cx="250" cy="1023" r="165"/></clipPath>
  <clipPath id="clipFlagC"><circle cx="713" cy="1345" r="46"/></clipPath>

  <linearGradient id="gFrame" x1="0" y1="0" x2="0.25" y2="1">
    <stop offset="0" stop-color="#f4f5f7"/><stop offset="0.22" stop-color="#c7cad0"/>
    <stop offset="0.45" stop-color="#94989f"/><stop offset="0.62" stop-color="#e2e4e8"/>
    <stop offset="0.8" stop-color="#a4a8af"/><stop offset="1" stop-color="#eceef0"/>
  </linearGradient>
  <linearGradient id="gBase" x1="0" y1="0" x2="0.45" y2="1">
    <stop offset="0" stop-color="#14235f"/><stop offset="0.4" stop-color="#1d3a8c"/>
    <stop offset="0.75" stop-color="#2b53b0"/><stop offset="1" stop-color="#2e5fbf"/>
  </linearGradient>
  <linearGradient id="gWedge" x1="0.2" y1="0" x2="0.7" y2="1">
    <stop offset="0" stop-color="#3f7fd0"/><stop offset="0.45" stop-color="#4e97de"/>
    <stop offset="1" stop-color="#3b7ecb"/>
  </linearGradient>
  <radialGradient id="gGlow" cx="0.62" cy="0.42" r="0.55">
    <stop offset="0" stop-color="#b8def8" stop-opacity="0.9"/>
    <stop offset="0.5" stop-color="#8ec6f2" stop-opacity="0.5"/>
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
    <!-- glossy swirl arcs across the bottom -->
    <g fill="none" opacity="0.8">
      <circle cx="640" cy="1585" r="392" stroke="#9fd0f5" stroke-width="16" opacity="0.55"/>
      <circle cx="620" cy="1610" r="330" stroke="#bfe2fa" stroke-width="9" opacity="0.6"/>
      <circle cx="660" cy="1560" r="470" stroke="#7fbfef" stroke-width="26" opacity="0.3"/>
      <circle cx="600" cy="1655" r="270" stroke="#8ec6f2" stroke-width="12" opacity="0.4"/>
    </g>
    <g transform="rotate(-55 700 800)">{streaks(5, 22, 8, 0.02, 0.07)}</g>
  </g>
  <!-- divider piping -->
  <path d="{DIVIDER}" stroke="#0a1c4a" stroke-width="2.5" fill="none" opacity="0.4" transform="translate(3,3)"/>
  <path d="{DIVIDER}" stroke="url(#gSilverLine)" stroke-width="4" fill="none"/>
  <!-- decorative S-arc inside the dark zone -->
  <path d="{SARC}" stroke="url(#gSilverLine)" stroke-width="3" fill="none" opacity="0.9"/>
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
  <g transform="scale(0.9 1)">
    <text x="522" y="348" text-anchor="middle" font-family="Russo" font-size="143"
          fill="#6e4e14" opacity="0.9">COSTA</text>
    <text x="522" y="345" text-anchor="middle" font-family="Russo" font-size="143"
          fill="url(#gGold)" stroke="#6e4e14" stroke-width="1">COSTA</text>
  </g>
</g>
<!-- amber drop inside the O -->
<path d="M 384 266 C 376 285 368 296 368 306 a 16 16 0 0 0 32 0 C 400 296 392 285 384 266 Z"
      fill="url(#gDropAmber)" stroke="#ffffff" stroke-width="2.5"/>
<ellipse cx="378" cy="301" rx="3.6" ry="5.5" fill="#fff6d8" opacity="0.85" transform="rotate(-14 378 301)"/>
<text x="468" y="393" text-anchor="middle" font-family="Montserrat" font-weight="500"
      font-size="25" letter-spacing="13" fill="#ebd9a8">LUBRICANT</text>
"""


def engine_oil():
    return """
<!-- ================= ENGINE OIL ================= -->
<g filter="url(#fTextShadow)">
  <g transform="scale(0.92 1)">
    <text x="402" y="588" text-anchor="middle" font-family="Russo" font-size="76"
          letter-spacing="2" fill="#ffffff">ENGINE OIL</text>
  </g>
</g>"""


def badge():
    cx, cy = 853, 720
    star_l = star4(cx - 56, cy - 40, 9)
    star_r = star4(cx + 56, cy - 40, 9)
    return f"""
<!-- ================= best quality medal (silver) ================= -->
<g filter="url(#fShadow)">
  <path d="{wavy_rosette(cx, cy, 88, 8, 14)}" fill="url(#gRing)" stroke="#63676e" stroke-width="1.5"/>
  <circle cx="{cx}" cy="{cy}" r="76" fill="url(#gDiscSilver)" stroke="#787d85" stroke-width="1.5"/>
  <circle cx="{cx}" cy="{cy}" r="76" fill="url(#gDiscSheen)"/>
  <circle cx="{cx}" cy="{cy}" r="70" fill="none" stroke="#9ba0a8" stroke-width="1" opacity="0.7"/>
  <g fill="#1a2b5a">
    <path d="{star_l}"/><path d="{star_r}"/>
    <text x="{cx}" y="{cy - 31}" text-anchor="middle" font-family="Montserrat" font-weight="800"
          font-size="25">100%</text>
    <text x="{cx}" y="{cy + 17}" text-anchor="middle" font-family="Lora" font-weight="700"
          font-size="58">BEST</text>
    <text x="{cx}" y="{cy + 45}" text-anchor="middle" font-family="Montserrat" font-weight="600"
          font-size="17" letter-spacing="6">QUALITY</text>
  </g>
</g>"""


def bands():
    x0, x1, tx = 417, 992, 483
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
    <text x="{tx / 0.85}" y="940" font-family="Russo" font-size="60" letter-spacing="5"
          fill="#f2e8c0">SYNTHETIC</text>
  </g>
  <g filter="url(#fTextShadow)">
    <text x="{tx}" y="1073" font-family="Russo" font-size="128" letter-spacing="2"
          fill="#ffffff">5W-30</text>
  </g>
  <text x="{tx}" y="1168" font-family="Russo" font-size="81" fill="#ffffff">API<tspan
        fill="#f2e8c0" dx="26">SP</tspan></text>
</g>"""


def engine_circle():
    img = b64("engine_crop.png")
    return f"""
<!-- ================= engine photo (extracted from reference) ============ -->
<g filter="url(#fShadow)">
  <circle cx="250" cy="1023" r="178" fill="url(#gRing)"/>
</g>
<g clip-path="url(#clipEngine)">
  <image x="77" y="850" width="347" height="347" preserveAspectRatio="none"
         href="data:image/png;base64,{img}"/>
</g>
<circle cx="250" cy="1023" r="166" fill="none" stroke="#71767d" stroke-width="1.5"/>
<circle cx="250" cy="1023" r="178" fill="none" stroke="#83878d" stroke-width="1.2"/>
"""


def splash():
    img = b64("splash_crop.png")
    return f"""
<!-- ================= oil splash (extracted from reference) ============= -->
<g clip-path="url(#clipDie)">
  <image x="333" y="1067" width="683" height="333" preserveAspectRatio="none"
         href="data:image/png;base64,{img}"/>
</g>"""


def five_l():
    return """
<!-- ================= 5L ================= -->
<g filter="url(#fTextShadow)">
  <text x="87" y="1395" font-family="Russo" font-size="200"
        fill="url(#gSilverText)">5<tspan font-size="139" dx="4">L</tspan></text>
</g>"""


def german():
    cx, cy = 713, 1345
    return f"""
<!-- ================= german technology ================= -->
<g filter="url(#fShadowS)">
  <path d="M 772 1305 H 908 L 950 1341.5 L 908 1378 H 772 Z" fill="url(#gPlate)"
        stroke="#8b8f96" stroke-width="1.5" stroke-linejoin="round"/>
  <text x="782" y="1332" font-family="Montserrat" font-weight="500" font-size="20"
        letter-spacing="7" fill="#e8ebef">GERMAN</text>
  <text x="782" y="1363" font-family="Montserrat" font-weight="800" font-size="23"
        letter-spacing="1" fill="#ffffff">TECHNOLOGY</text>
</g>
<g filter="url(#fShadowS)">
  <path d="{wavy_rosette(cx, cy, 62, 7, 10)}" fill="#17181c" stroke="#3a3d43" stroke-width="1.5"/>
  <circle cx="{cx}" cy="{cy}" r="50" fill="url(#gRing)"/>
  <g clip-path="url(#clipFlagC)">
    <rect x="{cx - 46}" y="{cy - 46}" width="92" height="31" fill="#161616"/>
    <rect x="{cx - 46}" y="{cy - 15}" width="92" height="31" fill="#d5121e"/>
    <rect x="{cx - 46}" y="{cy + 16}" width="92" height="31" fill="#f7c500"/>
    <circle cx="{cx}" cy="{cy}" r="46" fill="url(#gGlossFlag)"/>
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
