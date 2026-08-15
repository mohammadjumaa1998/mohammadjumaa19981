#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generates the COSTA Lubricant 5W-30 label as an HTML file with inline SVG.

ViewBox: 1000 x 1600  ->  printed at 100mm x 160mm.
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
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    return d


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


def bolts(cx, cy, n, r, br):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + 0.3
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{br}" fill="url(#gBoltM)" stroke="#101318" stroke-width="1.2"/>')
    return "\n".join(out)


def streaks():
    """Diagonal brushed-metal streaks across the blue field."""
    import random
    random.seed(7)
    out = []
    for i in range(26):
        x = -300 + i * 62 + random.uniform(-18, 18)
        w = random.choice([3, 5, 8, 14, 22])
        op = random.uniform(0.025, 0.085)
        out.append(f'<rect x="{x:.0f}" y="-200" width="{w}" height="2200" fill="#ffffff" opacity="{op:.3f}"/>')
    for i in range(12):
        x = -260 + i * 130 + random.uniform(-30, 30)
        w = random.choice([10, 18, 30])
        op = random.uniform(0.03, 0.07)
        out.append(f'<rect x="{x:.0f}" y="-200" width="{w}" height="2200" fill="#03102e" opacity="{op:.3f}"/>')
    return "\n".join(out)


# ---------------------------------------------------------------- pieces
def defs():
    return f"""
<defs>
  <!-- outer metallic frame -->
  <linearGradient id="gFrame" x1="0" y1="0" x2="0.25" y2="1">
    <stop offset="0" stop-color="#f4f5f7"/><stop offset="0.22" stop-color="#c7cad0"/>
    <stop offset="0.45" stop-color="#94989f"/><stop offset="0.62" stop-color="#e2e4e8"/>
    <stop offset="0.8" stop-color="#a4a8af"/><stop offset="1" stop-color="#eceef0"/>
  </linearGradient>
  <linearGradient id="gBlue" x1="0" y1="0" x2="0.55" y2="1">
    <stop offset="0" stop-color="#0a2166"/><stop offset="0.38" stop-color="#103586"/>
    <stop offset="0.7" stop-color="#2360b2"/><stop offset="1" stop-color="#3f86d4"/>
  </linearGradient>
  <radialGradient id="gGlow" cx="0.66" cy="0.62" r="0.5">
    <stop offset="0" stop-color="#8ec9f4" stop-opacity="0.95"/>
    <stop offset="0.55" stop-color="#5ea5e6" stop-opacity="0.5"/>
    <stop offset="1" stop-color="#5ea5e6" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="gDarkZone" x1="0" y1="0" x2="0.4" y2="1">
    <stop offset="0" stop-color="#071a52"/><stop offset="0.6" stop-color="#0d2d76"/>
    <stop offset="1" stop-color="#164094"/>
  </linearGradient>
  <linearGradient id="gSilverLine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.15"/>
    <stop offset="0.35" stop-color="#e9edf2" stop-opacity="0.95"/>
    <stop offset="0.65" stop-color="#aeb6c0" stop-opacity="0.9"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0.2"/>
  </linearGradient>
  <linearGradient id="gGold" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fdf3b0"/><stop offset="0.35" stop-color="#f1cf67"/>
    <stop offset="0.62" stop-color="#dca338"/><stop offset="0.85" stop-color="#a8721d"/>
    <stop offset="1" stop-color="#c6913a"/>
  </linearGradient>
  <linearGradient id="gGoldText" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffeD9a"/><stop offset="0.5" stop-color="#f4cf62"/>
    <stop offset="1" stop-color="#c98f24"/>
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
    <stop offset="0" stop-color="#1a3a80"/><stop offset="0.5" stop-color="#0e2358"/>
    <stop offset="1" stop-color="#0a1a44"/>
  </linearGradient>
  <linearGradient id="gBlackBand" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#33353a"/><stop offset="0.35" stop-color="#111215"/>
    <stop offset="1" stop-color="#020204"/>
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
  <radialGradient id="gEngineBg" cx="0.45" cy="0.4" r="0.85">
    <stop offset="0" stop-color="#4a5058"/><stop offset="0.6" stop-color="#23272d"/>
    <stop offset="1" stop-color="#0d1014"/>
  </radialGradient>
  <linearGradient id="gBlade" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#dfe3e8"/><stop offset="0.5" stop-color="#9aa1a9"/>
    <stop offset="1" stop-color="#565d66"/>
  </linearGradient>
  <radialGradient id="gBoltM" cx="0.35" cy="0.35" r="1">
    <stop offset="0" stop-color="#e8ebee"/><stop offset="1" stop-color="#5c636b"/>
  </radialGradient>
  <radialGradient id="gHub" cx="0.4" cy="0.35" r="1">
    <stop offset="0" stop-color="#c9ced4"/><stop offset="0.6" stop-color="#7d838c"/>
    <stop offset="1" stop-color="#3a4048"/>
  </radialGradient>
  <radialGradient id="gBadgeIn" cx="0.5" cy="0.42" r="0.75">
    <stop offset="0" stop-color="#20396e"/><stop offset="0.7" stop-color="#101f42"/>
    <stop offset="1" stop-color="#081227"/>
  </radialGradient>
  <linearGradient id="gAmber" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffe795"/><stop offset="0.35" stop-color="#f6c14e"/>
    <stop offset="0.7" stop-color="#dd9218"/><stop offset="1" stop-color="#a65f04"/>
  </linearGradient>
  <linearGradient id="gAmberDeep" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e8a92e"/><stop offset="1" stop-color="#8a4c02"/>
  </linearGradient>
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
  <clipPath id="clipInner"><rect x="26" y="26" width="948" height="1548" rx="26"/></clipPath>
  <clipPath id="clipEngine"><circle cx="300" cy="1067" r="163"/></clipPath>
</defs>"""


def background():
    return f"""
<!-- ================= background ================= -->
<g clip-path="url(#clipInner)">
  <rect x="0" y="0" width="1000" height="1600" fill="url(#gBlue)"/>
  <rect x="0" y="0" width="1000" height="1600" fill="url(#gGlow)"/>
  <!-- dark upper-left zone above the diagonal divider -->
  <path d="M 0 0 H 1000 V 545 Q 500 655 0 830 Z" fill="url(#gDarkZone)"/>
  <!-- brushed streaks -->
  <g transform="rotate(-58 500 800)">{streaks()}</g>
  <!-- diagonal silver divider -->
  <path d="M -10 833 Q 500 657 1010 547" stroke="url(#gSilverLine)" stroke-width="4" fill="none"/>
  <path d="M -10 846 Q 500 670 1010 560" stroke="#0a1c4a" stroke-width="3" fill="none" opacity="0.35"/>
  <!-- decorative silver arc top -->
  <path d="M 690 18 C 640 300 460 580 30 776" stroke="url(#gSilverLine)" stroke-width="3" fill="none" opacity="0.7"/>
  <!-- corner vignette -->
  <rect x="0" y="0" width="1000" height="1600" fill="#02123a" opacity="0.12"
        style="mix-blend-mode:multiply"/>
</g>"""


def logo():
    # COSTA centred at x=470; O centre ≈ 373
    return f"""
<!-- ================= logo ================= -->
<g filter="url(#fTextShadow)">
  <text x="470" y="352" text-anchor="middle" font-family="Cinzel" font-weight="900"
        font-size="122" letter-spacing="6" fill="url(#gGold)"
        stroke="#7a5312" stroke-width="1">COSTA</text>
</g>
<!-- red drop nestled into the O -->
<g filter="url(#fShadowS)" transform="translate(109,90) scale(0.75)">
  <path d="M 371.5 224 C 361 250 351 264 351 279 a 21 21 0 0 0 42 0 C 393 264 382 250 371.5 224 Z"
        fill="url(#gDrop)" stroke="#8f0d16" stroke-width="1.5"/>
  <ellipse cx="364" cy="272" rx="5" ry="8" fill="#ffd9d4" opacity="0.75" transform="rotate(-15 364 272)"/>
</g>
<text x="470" y="415" text-anchor="middle" font-family="Archivo" font-weight="600"
      font-size="33" letter-spacing="21" fill="#e9edf4">LUBRICANT</text>
"""


def engine_oil():
    return """
<!-- ================= ENGINE OIL ================= -->
<g filter="url(#fTextShadow)">
  <text x="355" y="682" text-anchor="middle" font-family="Archivo" font-weight="800"
        font-size="74" letter-spacing="2" fill="#ffffff">ENGINE OIL</text>
</g>"""


def badge():
    cx, cy = 830, 784
    sparkle_l = star4(cx - 62, cy - 52, 11)
    sparkle_r = star4(cx + 62, cy - 52, 11)
    return f"""
<!-- ================= best quality rosette ================= -->
<g filter="url(#fShadow)">
  <path d="{rosette_path(cx, cy, 114, 105, 40)}" fill="url(#gRing)"/>
  <circle cx="{cx}" cy="{cy}" r="103" fill="url(#gRing)" stroke="#6d727a" stroke-width="1"/>
  <circle cx="{cx}" cy="{cy}" r="90" fill="url(#gBadgeIn)" stroke="#d9dce1" stroke-width="2"/>
  <path d="{sparkle_l}" fill="#f2f4f7"/>
  <path d="{sparkle_r}" fill="#f2f4f7"/>
  <text x="{cx}" y="{cy - 44}" text-anchor="middle" font-family="Archivo" font-weight="800"
        font-size="27" fill="url(#gGoldText)">100%</text>
  <text x="{cx}" y="{cy + 12}" text-anchor="middle" font-family="Cinzel" font-weight="700"
        font-size="52" fill="#ffffff">BEST</text>
  <text x="{cx}" y="{cy + 52}" text-anchor="middle" font-family="Archivo" font-weight="600"
        font-size="21" letter-spacing="7" fill="#dfe4ea">QUALITY</text>
</g>"""


def engine_circle():
    cx, cy = 300, 1067
    return f"""
<!-- ================= engine photo circle ================= -->
<g filter="url(#fShadow)">
  <circle cx="{cx}" cy="{cy}" r="172" fill="url(#gRing)"/>
  <circle cx="{cx}" cy="{cy}" r="163" fill="url(#gEngineBg)"/>
</g>
<g clip-path="url(#clipEngine)">
  <!-- machinery backdrop -->
  <rect x="137" y="904" width="330" height="330" fill="url(#gEngineBg)"/>
  <!-- finned cylinder head, top-left -->
  <rect x="140" y="912" width="170" height="104" rx="12" fill="#343a41" stroke="#14171b" stroke-width="2"/>
  <g fill="#4d545c">
    <rect x="152" y="922" width="146" height="9" rx="4"/>
    <rect x="152" y="940" width="146" height="9" rx="4"/>
    <rect x="152" y="958" width="146" height="9" rx="4"/>
    <rect x="152" y="976" width="146" height="9" rx="4"/>
    <rect x="152" y="994" width="146" height="9" rx="4"/>
  </g>
  <!-- intake runner tubes -->
  <path d="M 300 930 q 50 6 78 44" stroke="#454c55" stroke-width="24" fill="none" stroke-linecap="round"/>
  <path d="M 300 962 q 42 10 60 44" stroke="#333941" stroke-width="20" fill="none" stroke-linecap="round"/>
  <!-- vertical pipes, left -->
  <path d="M 168 1030 q -6 60 8 118" stroke="#2b3037" stroke-width="20" fill="none" stroke-linecap="round"/>
  <path d="M 196 1040 q -2 56 10 104" stroke="#3a4149" stroke-width="12" fill="none" stroke-linecap="round"/>
  <!-- gears, right -->
  <path d="M 400 930 Q 445 990 428 1070" stroke="#20242a" stroke-width="22" fill="none"/>
  <path d="{gear_path(410, 974, 54, 43, 16, 12)}" fill="url(#gBlade)" fill-rule="evenodd" stroke="#15181d" stroke-width="2"/>
  <path d="{gear_path(458, 1064, 38, 29, 10, 10)}" fill="#7d838c" fill-rule="evenodd" stroke="#15181d" stroke-width="2"/>
  <!-- ribbed hoses across the bottom -->
  <path d="M 140 1190 Q 240 1136 330 1200 T 470 1176" stroke="#171b20" stroke-width="30" fill="none"/>
  <path d="M 140 1190 Q 240 1136 330 1200 T 470 1176" stroke="#3c424a" stroke-width="12" fill="none" opacity="0.85"/>
  <path d="M 150 1236 Q 260 1196 380 1240" stroke="#22262c" stroke-width="22" fill="none"/>
  <!-- alternator disc behind fan -->
  <circle cx="392" cy="1160" r="48" fill="#22262c" stroke="#0f1216" stroke-width="3"/>
  <circle cx="392" cy="1160" r="26" fill="#333941"/>
  {bolts(392, 1160, 5, 36, 3.5)}
  <!-- main fan / clutch -->
  <circle cx="278" cy="1090" r="98" fill="#1b1f24" stroke="#0b0e12" stroke-width="3"/>
  <circle cx="278" cy="1090" r="92" fill="none" stroke="#454c55" stroke-width="3" opacity="0.7"/>
  {blades(278, 1090, 13, 34, 86)}
  <circle cx="278" cy="1090" r="33" fill="url(#gHub)" stroke="#14171c" stroke-width="2"/>
  {bolts(278, 1090, 6, 22, 4.5)}
  <circle cx="278" cy="1090" r="9" fill="#22262c" stroke="#0d1014" stroke-width="2"/>
  <!-- glints -->
  <ellipse cx="225" cy="985" rx="60" ry="26" fill="#ffffff" opacity="0.07" transform="rotate(-24 225 985)"/>
  <ellipse cx="350" cy="1180" rx="50" ry="18" fill="#ffffff" opacity="0.05" transform="rotate(-18 350 1180)"/>
  <!-- cool blue tint + vignette -->
  <circle cx="300" cy="1067" r="163" fill="#2a5aa8" opacity="0.10"/>
  <circle cx="300" cy="1067" r="163" fill="none" stroke="#04070c" stroke-width="26" opacity="0.55"/>
</g>
<circle cx="{cx}" cy="{cy}" r="163" fill="none" stroke="#75797f" stroke-width="1.5"/>
"""


def bands():
    x0, x1 = 430, 974
    xc = (x0 + x1) / 2 + 40  # optical centre, right of the engine-circle overlap
    return f"""
<!-- ================= spec bands ================= -->
<g filter="url(#fShadowS)">
  <!-- SYNTHETIC row -->
  <path d="M {x0 + 26} 947 H {x1} V 1041 H {x0} V 973 A 26 26 0 0 1 {x0 + 26} 947 Z" fill="url(#gNavyBand)"/>
  <!-- 5W-30 row -->
  <rect x="{x0}" y="1041" width="{x1 - x0}" height="130" fill="url(#gBlackBand)"/>
  <!-- API row -->
  <path d="M {x0} 1171 H {x1} V 1256 H {x0 + 26} A 26 26 0 0 1 {x0} 1230 Z" fill="url(#gBlueBand)"/>
  <!-- separators -->
  <rect x="{x0}" y="1038" width="{x1 - x0}" height="4" fill="url(#gSilverLine)"/>
  <rect x="{x0}" y="1169" width="{x1 - x0}" height="4" fill="url(#gSilverLine)"/>
  <path d="M {x0 + 26} 945 H {x1}" stroke="url(#gSilverLine)" stroke-width="4" fill="none"/>
  <path d="M {x0 + 26} 1258 H {x1}" stroke="url(#gSilverLine)" stroke-width="4" fill="none"/>
</g>
<text x="{xc}" y="1010" text-anchor="middle" font-family="Archivo" font-weight="800"
      font-size="46" letter-spacing="10" fill="url(#gGoldText)">SYNTHETIC</text>
<g filter="url(#fTextShadow)">
  <text x="{xc}" y="1141" text-anchor="middle" font-family="Archivo" font-weight="900"
        font-size="100" letter-spacing="2" fill="#ffffff">5W-30</text>
</g>
<text x="{xc - 28}" y="1234" text-anchor="middle" font-family="Archivo" font-weight="900"
      font-size="54" letter-spacing="3" fill="#ffffff">API<tspan fill="url(#gGoldText)" dx="18">SP</tspan></text>
"""


def splash():
    return """
<!-- ================= oil splash ================= -->
<g filter="url(#fShadowS)">
  <!-- tongue rising over the API band's right corner -->
  <path d="M 974 1178 C 950 1192 934 1212 926 1238 C 919 1260 916 1274 916 1286
           L 974 1286 Z" fill="url(#gAmber)"/>
  <path d="M 974 1198
           C 930 1206 898 1220 872 1244
           C 844 1258 810 1260 764 1262
           C 706 1265 656 1270 622 1272
           C 566 1269 524 1284 508 1318
           C 496 1345 512 1372 548 1378
           C 528 1394 532 1420 558 1432
           C 610 1455 700 1436 760 1420
           C 838 1400 908 1402 974 1420 Z"
        fill="url(#gAmber)"/>
  <!-- curl -->
  <path d="M 622 1272 C 566 1269 524 1284 508 1318 C 498 1342 512 1366 544 1375
           C 522 1352 528 1322 556 1308 C 584 1294 616 1296 640 1312
           C 636 1290 630 1276 622 1272 Z" fill="url(#gAmberDeep)"/>
  <!-- underside shade -->
  <path d="M 974 1420 C 908 1402 838 1400 760 1420 C 700 1436 610 1455 558 1432
           C 596 1452 676 1454 748 1440 C 830 1424 900 1424 974 1442 Z"
        fill="#8a4c02" opacity="0.85"/>
  <!-- top highlight -->
  <path d="M 940 1212 C 900 1222 872 1236 848 1252 C 800 1262 720 1266 648 1274"
        stroke="#fff3bd" stroke-width="9" fill="none" opacity="0.65" stroke-linecap="round"/>
  <!-- droplets -->
  <circle cx="470" cy="1315" r="12" fill="url(#gAmber)"/>
  <circle cx="428" cy="1352" r="8" fill="url(#gAmber)"/>
  <circle cx="472" cy="1398" r="7" fill="url(#gAmber)"/>
  <path d="M 392 1380 c -6 14 -12 22 -12 30 a 12 12 0 0 0 24 0 c 0 -8 -6 -16 -12 -30 Z" fill="url(#gAmber)"/>
  <circle cx="360" cy="1320" r="5" fill="url(#gAmber)"/>
  <circle cx="520" cy="1408" r="9" fill="url(#gAmber)"/>
  <circle cx="588" cy="1300" r="6" fill="url(#gAmber)"/>
</g>"""


def five_l():
    return """
<!-- ================= 5L ================= -->
<g filter="url(#fTextShadow)">
  <text x="128" y="1508" font-family="Archivo" font-weight="900" font-size="185"
        fill="url(#gSilverText)" stroke="#9aa2ad" stroke-width="1.5">5<tspan font-size="135" dy="-4">L</tspan></text>
</g>"""


def german():
    return """
<!-- ================= german technology ================= -->
<g filter="url(#fShadowS)">
  <rect x="688" y="1414" width="284" height="84" rx="22" fill="url(#gPill)" stroke="#8b8f96" stroke-width="1.5"/>
  <text x="762" y="1450" font-family="Archivo" font-weight="600" font-size="24" letter-spacing="5"
        fill="#e8ebef">GERMAN</text>
  <text x="762" y="1485" font-family="Archivo" font-weight="900" font-size="26" letter-spacing="0.5"
        fill="#ffffff">TECHNOLOGY</text>
</g>
<g filter="url(#fShadowS)">
  <rect x="614" y="1388" width="136" height="136" rx="32" fill="#0c0d0f" stroke="#c8ccd1" stroke-width="5"/>
  <clipPath id="clipFlag"><rect x="620" y="1394" width="124" height="124" rx="27"/></clipPath>
  <g clip-path="url(#clipFlag)">
    <rect x="620" y="1394" width="124" height="42" fill="#141414"/>
    <rect x="620" y="1435" width="124" height="42" fill="#d5121e"/>
    <rect x="620" y="1476" width="124" height="42" fill="#f7c500"/>
    <rect x="620" y="1394" width="124" height="124" fill="url(#gGlossFlag)"/>
  </g>
</g>
<radialGradient id="gGlossFlag" cx="0.3" cy="0.2" r="1.1">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.35"/>
  <stop offset="0.4" stop-color="#ffffff" stop-opacity="0.05"/>
  <stop offset="1" stop-color="#000000" stop-opacity="0.25"/>
</radialGradient>"""


def frame():
    return """
<!-- ================= metallic frame (on top) ================= -->
<rect x="9" y="9" width="982" height="1582" rx="40" fill="none" stroke="url(#gFrame)" stroke-width="18"/>
<rect x="2.5" y="2.5" width="995" height="1595" rx="45" fill="none" stroke="#7e828a" stroke-width="3"/>
<rect x="19" y="19" width="962" height="1562" rx="33" fill="none" stroke="#5d6169" stroke-width="2" opacity="0.8"/>
<rect x="23" y="23" width="954" height="1554" rx="30" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.5"/>"""


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
