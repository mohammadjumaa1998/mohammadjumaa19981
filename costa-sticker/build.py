#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generates the COSTA Lubricant 5W-30 label as an HTML file with inline SVG.

ViewBox: 1000 x 1600  ->  printed at 100mm x 160mm.
All geometry was measured off the reference bottle photo (label region
mapped to relative coordinates, then scaled to the 1000x1600 viewBox).
"""
import math
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "fonts"  # relative to label.html
OUT = os.path.join(BASE, "label.html")

W, H = 1000, 1600


# ---------------------------------------------------------------- helpers
def rosette_path(cx, cy, r_out, r_in, n):
    """Serrated (sunburst) circle edge."""
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def gear_path(cx, cy, r_out, r_in, r_hole, n):
    pts = []
    for i in range(n):
        a0 = 2 * math.pi * i / n
        step = 2 * math.pi / n
        for fr, rr in ((0.0, r_in), (0.18, r_in), (0.28, r_out), (0.62, r_out), (0.72, r_in), (0.9, r_in)):
            a = a0 + fr * step
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z "
    d += f"M {cx + r_hole:.1f} {cy:.1f} A {r_hole} {r_hole} 0 1 0 {cx - r_hole:.1f} {cy:.1f} A {r_hole} {r_hole} 0 1 0 {cx + r_hole:.1f} {cy:.1f} Z"
    return d


def star4(cx, cy, r, r2=None):
    """4-point sparkle star."""
    r2 = r2 or r * 0.28
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r2
        a = math.pi * i / 4 - math.pi / 2
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def blades(cx, cy, n, r0, r1):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        half0 = 2 * math.pi / n * 0.16
        half1 = 2 * math.pi / n * 0.30
        sweep = 0.30
        p0 = (cx + r0 * math.cos(a - half0), cy + r0 * math.sin(a - half0))
        p1 = (cx + r1 * math.cos(a - half1 + sweep), cy + r1 * math.sin(a - half1 + sweep))
        p2 = (cx + r1 * math.cos(a + half1 + sweep), cy + r1 * math.sin(a + half1 + sweep))
        p3 = (cx + r0 * math.cos(a + half0), cy + r0 * math.sin(a + half0))
        out.append(
            f'<path d="M {p0[0]:.1f} {p0[1]:.1f} L {p1[0]:.1f} {p1[1]:.1f} '
            f'A {r1} {r1} 0 0 1 {p2[0]:.1f} {p2[1]:.1f} L {p3[0]:.1f} {p3[1]:.1f} Z" '
            f'fill="url(#gBlade)" stroke="#171a1f" stroke-width="1.6"/>')
    return "\n".join(out)


def bolts(cx, cy, n, r, br, phase=0.3):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + phase
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{br}" fill="url(#gBoltM)" stroke="#101318" stroke-width="1.2"/>')
    return "\n".join(out)


def ribbed_disc(cx, cy, r, n, color="#9aa1a9"):
    """Radial ribs, like a stamped pulley face."""
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x0, y0 = cx + r * 0.35 * math.cos(a), cy + r * 0.35 * math.sin(a)
        x1, y1 = cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a)
        out.append(f'<path d="M {x0:.1f} {y0:.1f} L {x1:.1f} {y1:.1f}" stroke="{color}" stroke-width="3.4" opacity="0.85"/>')
    return "\n".join(out)


def streaks(seed, n_light, n_dark, alpha_lo, alpha_hi):
    """Diagonal brushed-metal streaks (drawn vertical, group is rotated)."""
    import random
    random.seed(seed)
    out = []
    for i in range(n_light):
        x = -700 + i * (2400 // max(n_light, 1)) + random.uniform(-20, 20)
        w = random.choice([3, 5, 8, 13, 20, 30, 46])
        op = random.uniform(alpha_lo, alpha_hi)
        out.append(f'<rect x="{x:.0f}" y="-400" width="{w}" height="2600" fill="#cfe4ff" opacity="{op:.3f}"/>')
    for i in range(n_dark):
        x = -650 + i * (2300 // max(n_dark, 1)) + random.uniform(-30, 30)
        w = random.choice([8, 14, 24, 40])
        op = random.uniform(alpha_lo * 0.8, alpha_hi * 0.8)
        out.append(f'<rect x="{x:.0f}" y="-400" width="{w}" height="2600" fill="#021030" opacity="{op:.3f}"/>')
    return "\n".join(out)


def droplet(cx, cy, r, rot=0):
    """Teardrop with glint."""
    return f"""
  <g transform="rotate({rot} {cx} {cy})">
    <path d="M {cx} {cy - 2.1 * r} C {cx - 0.55 * r} {cy - 0.7 * r} {cx - r} {cy - 0.35 * r} {cx - r} {cy}
             a {r} {r} 0 0 0 {2 * r} 0
             C {cx + r} {cy - 0.35 * r} {cx + 0.55 * r} {cy - 0.7 * r} {cx} {cy - 2.1 * r} Z"
          fill="url(#gAmberDrop)" stroke="#a3610a" stroke-width="0.8"/>
    <ellipse cx="{cx - 0.35 * r}" cy="{cy - 0.15 * r}" rx="{0.3 * r}" ry="{0.45 * r}" fill="#fff4cd" opacity="0.8"/>
  </g>"""


# Dark panel boundary: sweeps right of the logo then down-left to the left
# edge.  A straight silver spur leaves it near (540,546) for the right edge;
# the wedge above the spur (top-right corner) is a mid-tone blue.
CURVE = "M 730 -6 C 762 200 760 440 640 600 C 520 740 260 806 -6 858"
SPUR = "M 640 600 L 1006 524"


# ---------------------------------------------------------------- defs
def defs():
    return f"""
<defs>
  <clipPath id="clipPanel"><path d="{CURVE} L -6 -6 Z"/></clipPath>
  <clipPath id="clipWedge"><path d="M 730 -6 H 1006 V 524 L 640 600 C 760 440 762 200 730 -6 Z"/></clipPath>
  <linearGradient id="gFrame" x1="0" y1="0" x2="0.25" y2="1">
    <stop offset="0" stop-color="#f4f5f7"/><stop offset="0.22" stop-color="#c7cad0"/>
    <stop offset="0.45" stop-color="#94989f"/><stop offset="0.62" stop-color="#e2e4e8"/>
    <stop offset="0.8" stop-color="#a4a8af"/><stop offset="1" stop-color="#eceef0"/>
  </linearGradient>
  <linearGradient id="gBlue" x1="0" y1="0" x2="0.55" y2="1">
    <stop offset="0" stop-color="#16408e"/><stop offset="0.45" stop-color="#2463b2"/>
    <stop offset="0.75" stop-color="#3c82cf"/><stop offset="1" stop-color="#2a62ae"/>
  </linearGradient>
  <radialGradient id="gGlow" cx="0.75" cy="0.52" r="0.48">
    <stop offset="0" stop-color="#a4d3f6" stop-opacity="0.85"/>
    <stop offset="0.55" stop-color="#74b5ec" stop-opacity="0.45"/>
    <stop offset="1" stop-color="#74b5ec" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="gMidZone" x1="0" y1="0" x2="0.3" y2="1">
    <stop offset="0" stop-color="#1a4392"/><stop offset="1" stop-color="#2b60b0"/>
  </linearGradient>
  <linearGradient id="gDarkZone" x1="0" y1="0" x2="0.35" y2="1">
    <stop offset="0" stop-color="#071b52"/><stop offset="0.55" stop-color="#0d2d76"/>
    <stop offset="1" stop-color="#143c8c"/>
  </linearGradient>
  <linearGradient id="gSilverLine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.25"/>
    <stop offset="0.35" stop-color="#eef1f5" stop-opacity="0.95"/>
    <stop offset="0.65" stop-color="#b3bac3" stop-opacity="0.9"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0.3"/>
  </linearGradient>
  <linearGradient id="gGold" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fdf3b0"/><stop offset="0.35" stop-color="#f1cf67"/>
    <stop offset="0.62" stop-color="#dca338"/><stop offset="0.85" stop-color="#a8721d"/>
    <stop offset="1" stop-color="#c6913a"/>
  </linearGradient>
  <linearGradient id="gGoldText" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffed9a"/><stop offset="0.5" stop-color="#f4cf62"/>
    <stop offset="1" stop-color="#c98f24"/>
  </linearGradient>
  <linearGradient id="gPaleYellow" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fdf6c0"/><stop offset="0.6" stop-color="#f2e17c"/>
    <stop offset="1" stop-color="#dcc157"/>
  </linearGradient>
  <radialGradient id="gDrop" cx="0.35" cy="0.3" r="0.9">
    <stop offset="0" stop-color="#ff7166"/><stop offset="0.45" stop-color="#e63a35"/>
    <stop offset="1" stop-color="#b30f1b"/>
  </radialGradient>
  <linearGradient id="gSilverText" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.55" stop-color="#e8ebef"/>
    <stop offset="0.8" stop-color="#b7bec7"/><stop offset="1" stop-color="#dfe3e8"/>
  </linearGradient>
  <linearGradient id="gNavyBand" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1c3d85"/><stop offset="0.5" stop-color="#0e2358"/>
    <stop offset="1" stop-color="#0a1a44"/>
  </linearGradient>
  <linearGradient id="gBlackBand" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3a3c40"/><stop offset="0.3" stop-color="#141518"/>
    <stop offset="1" stop-color="#000000"/>
  </linearGradient>
  <linearGradient id="gBlueBand" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3a70d4"/><stop offset="0.5" stop-color="#1f47a4"/>
    <stop offset="1" stop-color="#132f78"/>
  </linearGradient>
  <linearGradient id="gRing" x1="0" y1="0" x2="0.3" y2="1">
    <stop offset="0" stop-color="#fbfcfd"/><stop offset="0.3" stop-color="#c3c7cd"/>
    <stop offset="0.55" stop-color="#888d95"/><stop offset="0.75" stop-color="#dcdfe3"/>
    <stop offset="1" stop-color="#9599a1"/>
  </linearGradient>
  <radialGradient id="gEngineBg" cx="0.42" cy="0.38" r="0.9">
    <stop offset="0" stop-color="#787f88"/><stop offset="0.55" stop-color="#3d434b"/>
    <stop offset="1" stop-color="#181c22"/>
  </radialGradient>
  <linearGradient id="gBlade" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#e6eaee"/><stop offset="0.5" stop-color="#a6adb5"/>
    <stop offset="1" stop-color="#5e656e"/>
  </linearGradient>
  <radialGradient id="gBoltM" cx="0.35" cy="0.35" r="1">
    <stop offset="0" stop-color="#e8ebee"/><stop offset="1" stop-color="#5c636b"/>
  </radialGradient>
  <radialGradient id="gHub" cx="0.4" cy="0.35" r="1">
    <stop offset="0" stop-color="#d5dade"/><stop offset="0.6" stop-color="#868c94"/>
    <stop offset="1" stop-color="#42484f"/>
  </radialGradient>
  <radialGradient id="gBadgeIn" cx="0.5" cy="0.42" r="0.75">
    <stop offset="0" stop-color="#20396e"/><stop offset="0.7" stop-color="#101f42"/>
    <stop offset="1" stop-color="#081227"/>
  </radialGradient>
  <linearGradient id="gAmber" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fce9a2"/><stop offset="0.3" stop-color="#f3c455"/>
    <stop offset="0.65" stop-color="#e09a1d"/><stop offset="1" stop-color="#b26a06"/>
  </linearGradient>
  <linearGradient id="gAmberLight" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff7d6"/><stop offset="0.5" stop-color="#f9d778"/>
    <stop offset="1" stop-color="#e8ac33"/>
  </linearGradient>
  <linearGradient id="gAmberDeep" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e8a92e"/><stop offset="1" stop-color="#8a4c02"/>
  </linearGradient>
  <radialGradient id="gAmberDrop" cx="0.35" cy="0.3" r="1">
    <stop offset="0" stop-color="#fce9a2"/><stop offset="0.6" stop-color="#eeb33a"/>
    <stop offset="1" stop-color="#bf7708"/>
  </radialGradient>
  <linearGradient id="gPill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3a3d44"/><stop offset="0.5" stop-color="#17181d"/>
    <stop offset="1" stop-color="#060608"/>
  </linearGradient>
  <filter id="fShadow" x="-40%" y="-40%" width="180%" height="180%">
    <feDropShadow dx="0" dy="7" stdDeviation="9" flood-color="#02102e" flood-opacity="0.5"/>
  </filter>
  <filter id="fShadowS" x="-40%" y="-40%" width="180%" height="180%">
    <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#02102e" flood-opacity="0.45"/>
  </filter>
  <filter id="fTextShadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#01102c" flood-opacity="0.55"/>
  </filter>
  <clipPath id="clipInner"><rect x="14" y="14" width="972" height="1572" rx="26"/></clipPath>
  <clipPath id="clipEngine"><circle cx="302" cy="1067" r="168"/></clipPath>
  <clipPath id="clipBlack"><rect x="442" y="1056" width="532" height="144"/></clipPath>
  <radialGradient id="gGlossFlag" cx="0.3" cy="0.2" r="1.1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.35"/>
    <stop offset="0.4" stop-color="#ffffff" stop-opacity="0.05"/>
    <stop offset="1" stop-color="#000000" stop-opacity="0.25"/>
  </radialGradient>
</defs>"""


# ---------------------------------------------------------------- pieces
def background():
    return f"""
<!-- ================= background ================= -->
<g clip-path="url(#clipInner)">
  <rect x="0" y="0" width="1000" height="1600" fill="url(#gBlue)"/>
  <rect x="0" y="0" width="1000" height="1600" fill="url(#gGlow)"/>
  <!-- faint streaks over the whole field -->
  <g transform="rotate(-60 500 800)">{streaks(3, 22, 8, 0.015, 0.05)}</g>
  <!-- mid-tone wedge in the top-right corner -->
  <path d="M 730 -6 H 1006 V 524 L 640 600 C 760 440 762 200 730 -6 Z" fill="url(#gMidZone)"/>
  <g clip-path="url(#clipWedge)">
    <g transform="rotate(-60 780 300)">{streaks(5, 20, 8, 0.04, 0.10)}</g>
  </g>
  <!-- dark navy panel, top-left -->
  <path d="{CURVE} L -6 -6 Z" fill="url(#gDarkZone)"/>
  <g clip-path="url(#clipPanel)">
    <g transform="rotate(-60 300 400)">{streaks(7, 34, 12, 0.05, 0.14)}</g>
  </g>
  <!-- silver piping on the zone boundaries -->
  <path d="{CURVE}" stroke="#0a1c4a" stroke-width="2.5" fill="none" opacity="0.45" transform="translate(3,4)"/>
  <path d="{CURVE}" stroke="url(#gSilverLine)" stroke-width="4.5" fill="none"/>
  <path d="{SPUR}" stroke="url(#gSilverLine)" stroke-width="3.5" fill="none"/>
  <!-- corner vignette -->
  <rect x="0" y="0" width="1000" height="1600" fill="#02123a" opacity="0.10"
        style="mix-blend-mode:multiply"/>
</g>"""


def logo():
    # COSTA condensed: Cinzel 900 @170px, squeezed to 75% width, centre x=467.
    # O centre lands at x~387.
    return """
<!-- ================= logo ================= -->
<g filter="url(#fTextShadow)">
  <g transform="scale(0.75 1)">
    <text x="622.7" y="377" text-anchor="middle" font-family="Cinzel" font-weight="900"
          font-size="170" fill="url(#gGold)" stroke="#7a5312" stroke-width="1.2">COSTA</text>
  </g>
</g>
<!-- red drop nestled into the O -->
<g filter="url(#fShadowS)" transform="translate(89,83) scale(0.8)">
  <path d="M 371.5 224 C 361 250 351 264 351 279 a 21 21 0 0 0 42 0 C 393 264 382 250 371.5 224 Z"
        fill="url(#gDrop)" stroke="#8f0d16" stroke-width="1.5"/>
  <ellipse cx="364" cy="272" rx="5" ry="8" fill="#ffd9d4" opacity="0.75" transform="rotate(-15 364 272)"/>
</g>
<text x="470" y="431" text-anchor="middle" font-family="Archivo" font-weight="600"
      font-size="27" letter-spacing="22" fill="#e9edf4">LUBRICANT</text>
"""


def engine_oil():
    return """
<!-- ================= ENGINE OIL ================= -->
<g filter="url(#fTextShadow)">
  <text x="362" y="716" text-anchor="middle" font-family="BarlowC" font-weight="700"
        font-size="102" letter-spacing="2" fill="#ffffff">ENGINE OIL</text>
</g>"""


def badge():
    cx, cy = 832, 782
    sparkle_l = star4(cx - 60, cy - 50, 10)
    sparkle_r = star4(cx + 60, cy - 50, 10)
    return f"""
<!-- ================= best quality rosette ================= -->
<g filter="url(#fShadow)">
  <path d="{rosette_path(cx, cy, 113, 106, 52)}" fill="url(#gRing)"/>
  <circle cx="{cx}" cy="{cy}" r="104" fill="url(#gRing)" stroke="#6d727a" stroke-width="1"/>
  <circle cx="{cx}" cy="{cy}" r="91" fill="url(#gBadgeIn)" stroke="#d9dce1" stroke-width="2"/>
  <circle cx="{cx}" cy="{cy}" r="86" fill="none" stroke="#8fa2c8" stroke-width="0.8" opacity="0.6"/>
  <path d="{sparkle_l}" fill="#f2f4f7"/>
  <path d="{sparkle_r}" fill="#f2f4f7"/>
  <text x="{cx}" y="{cy - 42}" text-anchor="middle" font-family="Archivo" font-weight="800"
        font-size="27" fill="url(#gGoldText)">100%</text>
  <text x="{cx}" y="{cy + 14}" text-anchor="middle" font-family="Cinzel" font-weight="700"
        font-size="52" fill="#ffffff">BEST</text>
  <text x="{cx}" y="{cy + 54}" text-anchor="middle" font-family="Archivo" font-weight="600"
        font-size="20" letter-spacing="7" fill="#dfe4ea">QUALITY</text>
  <path d="M {cx - 34} {cy + 70} Q {cx} {cy + 82} {cx + 34} {cy + 70}"
        stroke="#c9cfd8" stroke-width="2.5" fill="none" opacity="0.8"/>
</g>"""


def bands():
    x0, x1 = 442, 976
    xc = (x0 + x1) / 2 + 34
    return f"""
<!-- ================= spec bands ================= -->
<g filter="url(#fShadowS)">
  <!-- SYNTHETIC row -->
  <path d="M {x0 + 40} 952 H {x1} V 1056 H {x0} V 992 A 40 40 0 0 1 {x0 + 40} 952 Z" fill="url(#gNavyBand)"/>
  <!-- 5W-30 row -->
  <rect x="{x0}" y="1056" width="{x1 - x0}" height="144" fill="url(#gBlackBand)"/>
  <g clip-path="url(#clipBlack)" opacity="0.5">
    <g transform="rotate(-60 700 1128)">{streaks(11, 16, 6, 0.04, 0.1)}</g>
  </g>
  <!-- API row -->
  <path d="M {x0} 1200 H {x1} V 1306 H {x0 + 40} A 40 40 0 0 1 {x0} 1266 Z" fill="url(#gBlueBand)"/>
  <!-- separators -->
  <rect x="{x0}" y="1053" width="{x1 - x0}" height="4" fill="url(#gSilverLine)"/>
  <rect x="{x0}" y="1198" width="{x1 - x0}" height="4" fill="url(#gSilverLine)"/>
  <path d="M {x0 + 40} 950 H {x1}" stroke="url(#gSilverLine)" stroke-width="4" fill="none"/>
  <path d="M {x0 + 40} 1308 H {x1}" stroke="url(#gSilverLine)" stroke-width="4" fill="none"/>
</g>
<text x="{xc}" y="1022" text-anchor="middle" font-family="Archivo" font-weight="700"
      font-size="47" letter-spacing="12" fill="url(#gPaleYellow)">SYNTHETIC</text>
<g filter="url(#fTextShadow)">
  <text x="{xc}" y="1168" text-anchor="middle" font-family="Archivo" font-weight="900"
        font-size="112" letter-spacing="2" fill="#ffffff">5W-30</text>
</g>
<text x="{xc - 30}" y="1274" text-anchor="middle" font-family="Archivo" font-weight="900"
      font-size="58" letter-spacing="3" fill="#ffffff">API<tspan fill="url(#gPaleYellow)" dx="20">SP</tspan></text>
"""


def engine_circle():
    cx, cy = 302, 1067
    return f"""
<!-- ================= engine photo circle ================= -->
<g filter="url(#fShadow)">
  <circle cx="{cx}" cy="{cy}" r="176" fill="url(#gRing)"/>
  <circle cx="{cx}" cy="{cy}" r="168" fill="url(#gEngineBg)"/>
</g>
<g clip-path="url(#clipEngine)">
  <rect x="134" y="899" width="336" height="336" fill="url(#gEngineBg)"/>
  <!-- finned block, top-left -->
  <rect x="136" y="905" width="180" height="112" rx="12" fill="#4b525a" stroke="#181c21" stroke-width="2"/>
  <g fill="#646c75">
    <rect x="148" y="916" width="156" height="10" rx="5"/>
    <rect x="148" y="936" width="156" height="10" rx="5"/>
    <rect x="148" y="956" width="156" height="10" rx="5"/>
    <rect x="148" y="976" width="156" height="10" rx="5"/>
    <rect x="148" y="996" width="156" height="10" rx="5"/>
  </g>
  <!-- intake runners -->
  <path d="M 306 928 q 54 8 84 48" stroke="#5a626b" stroke-width="26" fill="none" stroke-linecap="round"/>
  <path d="M 306 962 q 44 12 62 46" stroke="#464d56" stroke-width="20" fill="none" stroke-linecap="round"/>
  <!-- gears, upper right -->
  <path d="M 404 926 Q 452 990 434 1072" stroke="#272c33" stroke-width="22" fill="none"/>
  <path d="{gear_path(414, 972, 56, 44, 16, 12)}" fill="url(#gBlade)" fill-rule="evenodd" stroke="#15181d" stroke-width="2"/>
  <path d="{gear_path(462, 1066, 40, 30, 10, 10)}" fill="#8b929b" fill-rule="evenodd" stroke="#15181d" stroke-width="2"/>
  <!-- braided cables sweeping through -->
  <path d="M 150 950 C 240 1010 330 1120 452 1210" stroke="#20242a" stroke-width="17" fill="none"/>
  <path d="M 150 950 C 240 1010 330 1120 452 1210" stroke="#aab1b9" stroke-width="9" fill="none"
        stroke-dasharray="7 4" opacity="0.9"/>
  <path d="M 138 1024 C 210 1064 260 1130 320 1226" stroke="#1c2026" stroke-width="14" fill="none"/>
  <path d="M 138 1024 C 210 1064 260 1130 320 1226" stroke="#8f969e" stroke-width="7" fill="none"
        stroke-dasharray="6 4" opacity="0.85"/>
  <!-- pulleys bottom-right -->
  <circle cx="422" cy="1160" r="52" fill="#3a4048" stroke="#14171c" stroke-width="3"/>
  {ribbed_disc(422, 1160, 50, 18, "#79818a")}
  <circle cx="422" cy="1160" r="16" fill="url(#gHub)" stroke="#14171c" stroke-width="2"/>
  <circle cx="452" cy="1062" r="26" fill="#565d66" stroke="#171a1f" stroke-width="2"/>
  <!-- ribbed hoses, bottom -->
  <path d="M 138 1192 Q 240 1140 330 1204 T 470 1182" stroke="#171b20" stroke-width="30" fill="none"/>
  <path d="M 138 1192 Q 240 1140 330 1204 T 470 1182" stroke="#4a515a" stroke-width="13" fill="none" opacity="0.9"/>
  <path d="M 150 1240 Q 262 1200 382 1244" stroke="#262b31" stroke-width="22" fill="none"/>
  <!-- main ribbed fan / flywheel -->
  <circle cx="278" cy="1092" r="100" fill="#22262c" stroke="#0d1015" stroke-width="3"/>
  <circle cx="278" cy="1092" r="93" fill="none" stroke="#565d66" stroke-width="4" opacity="0.8"/>
  {blades(278, 1092, 15, 34, 87)}
  <circle cx="278" cy="1092" r="33" fill="url(#gHub)" stroke="#14171c" stroke-width="2"/>
  {bolts(278, 1092, 6, 22, 4.5)}
  <circle cx="278" cy="1092" r="9" fill="#22262c" stroke="#0d1014" stroke-width="2"/>
  <!-- small hardware -->
  {bolts(180, 1140, 3, 26, 5, 1.1)}
  <circle cx="368" cy="1010" r="12" fill="#767d86" stroke="#1a1e23" stroke-width="2"/>
  <!-- glints -->
  <ellipse cx="220" cy="975" rx="70" ry="28" fill="#ffffff" opacity="0.10" transform="rotate(-24 220 975)"/>
  <ellipse cx="360" cy="1190" rx="55" ry="20" fill="#ffffff" opacity="0.07" transform="rotate(-18 360 1190)"/>
  <!-- cool tint + vignette -->
  <circle cx="302" cy="1067" r="168" fill="#2a5aa8" opacity="0.08"/>
  <circle cx="302" cy="1067" r="168" fill="none" stroke="#04070c" stroke-width="22" opacity="0.5"/>
</g>
<circle cx="{cx}" cy="{cy}" r="168" fill="none" stroke="#7d8187" stroke-width="1.5"/>
"""


def splash():
    drops = (
        droplet(455, 1330, 11, -18) + droplet(420, 1366, 8, -22) +
        droplet(383, 1398, 6, -15) + droplet(352, 1344, 5, -30) +
        droplet(470, 1412, 7, -10) + droplet(514, 1294, 6, -25)
    )
    return f"""
<!-- ================= oil splash ================= -->
<g filter="url(#fShadowS)">
  <!-- thin upper sheet over the API band corner -->
  <path d="M 976 1188 C 928 1198 890 1216 862 1244 C 900 1232 944 1224 976 1224 Z"
        fill="url(#gAmberLight)" opacity="0.95"/>
  <!-- main wave -->
  <path d="M 976 1214
           C 920 1224 880 1244 850 1272
           C 810 1306 770 1322 720 1330
           C 664 1338 620 1332 588 1322
           C 548 1310 516 1318 500 1344
           C 488 1368 500 1394 530 1402
           C 560 1408 588 1400 606 1384
           C 640 1410 690 1424 744 1424
           C 820 1424 900 1428 976 1436 Z"
        fill="url(#gAmber)"/>
  <!-- curl core -->
  <path d="M 588 1322 C 548 1310 516 1318 500 1344 C 490 1364 498 1386 522 1396
           C 506 1376 512 1350 536 1338 C 560 1326 584 1330 602 1344
           C 598 1334 594 1326 588 1322 Z" fill="url(#gAmberDeep)"/>
  <!-- translucent under-sheet -->
  <path d="M 976 1436 C 900 1428 820 1424 744 1424 C 690 1424 640 1410 606 1384
           C 648 1428 720 1444 790 1442 C 860 1440 926 1444 976 1452 Z"
        fill="#8a4c02" opacity="0.8"/>
  <!-- crest highlights -->
  <path d="M 952 1222 C 906 1232 872 1250 846 1274 C 810 1306 772 1320 724 1327"
        stroke="#fff3bd" stroke-width="9" fill="none" opacity="0.75" stroke-linecap="round"/>
  <path d="M 700 1332 C 664 1336 628 1332 600 1324" stroke="#ffedb0" stroke-width="6"
        fill="none" opacity="0.55" stroke-linecap="round"/>
  <path d="M 530 1398 C 510 1390 502 1372 508 1352" stroke="#fff3bd" stroke-width="5"
        fill="none" opacity="0.6" stroke-linecap="round"/>
  <!-- droplets -->
  {drops}
</g>"""


def five_l():
    return """
<!-- ================= 5L ================= -->
<g filter="url(#fTextShadow)">
  <text x="112" y="1545" font-family="BarlowC" font-weight="700" font-size="252"
        fill="url(#gSilverText)" stroke="#8f97a2" stroke-width="1.5">5<tspan font-size="178" dy="-3" dx="2">L</tspan></text>
</g>"""


def german():
    return """
<!-- ================= german technology ================= -->
<g filter="url(#fShadowS)">
  <rect x="700" y="1417" width="252" height="106" rx="26" fill="url(#gPill)" stroke="#8b8f96" stroke-width="1.5"/>
  <text x="758" y="1462" font-family="Archivo" font-weight="600" font-size="24" letter-spacing="6"
        fill="#e8ebef">GERMAN</text>
  <text x="758" y="1502" font-family="BarlowC" font-weight="700" font-size="34" letter-spacing="1"
        fill="#ffffff">TECHNOLOGY</text>
</g>
<g filter="url(#fShadowS)">
  <rect x="609" y="1403" width="134" height="134" rx="30" fill="#0c0d0f" stroke="#c8ccd1" stroke-width="5"/>
  <clipPath id="clipFlag"><rect x="615" y="1409" width="122" height="122" rx="25"/></clipPath>
  <g clip-path="url(#clipFlag)">
    <rect x="615" y="1409" width="122" height="41" fill="#141414"/>
    <rect x="615" y="1450" width="122" height="41" fill="#d5121e"/>
    <rect x="615" y="1491" width="122" height="41" fill="#f7c500"/>
    <rect x="615" y="1409" width="122" height="122" fill="url(#gGlossFlag)"/>
  </g>
</g>"""


def frame():
    return """
<!-- ================= metallic frame (thin, on top) ================= -->
<rect x="7" y="7" width="986" height="1586" rx="30" fill="none" stroke="url(#gFrame)" stroke-width="10"/>
<rect x="1.5" y="1.5" width="997" height="1597" rx="33" fill="none" stroke="#7e828a" stroke-width="2"/>
<rect x="13" y="13" width="974" height="1574" rx="25" fill="none" stroke="#5d6169" stroke-width="1.6" opacity="0.85"/>
<rect x="16" y="16" width="968" height="1568" rx="23" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.5"/>"""


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
@font-face {{ font-family:'Cinzel';  font-weight:700; src:url('{FONT_DIR}/Cinzel-700.ttf'); }}
@font-face {{ font-family:'Cinzel';  font-weight:900; src:url('{FONT_DIR}/Cinzel-900.ttf'); }}
@font-face {{ font-family:'Archivo'; font-weight:600; src:url('{FONT_DIR}/Archivo-600.ttf'); }}
@font-face {{ font-family:'Archivo'; font-weight:700; src:url('{FONT_DIR}/Archivo-600.ttf'); }}
@font-face {{ font-family:'Archivo'; font-weight:800; src:url('{FONT_DIR}/Archivo-800.ttf'); }}
@font-face {{ font-family:'Archivo'; font-weight:900; src:url('{FONT_DIR}/Archivo-900.ttf'); }}
@font-face {{ font-family:'BarlowC'; font-weight:700; src:url('{FONT_DIR}/BarlowCondensed-700.ttf'); }}
@page {{ size: 100mm 160mm; margin: 0; }}
html,body {{ margin:0; padding:0; }}
svg {{ display:block; width:100vw; height:100vh; }}
</style></head>
<body>{svg}</body></html>"""


open(OUT, "w").write(html())
print("wrote", OUT)
