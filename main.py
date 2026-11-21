#!/usr/bin/env python3
"""Sum up the world news of Friday 20 November 2026 in one image.

A program that draws a newspaper front page using only the Python 3.13
standard library (no network, no third-party packages) and writes it to
/output/entry.png. Running it any number of times produces the same bytes.

Stories shown (all widely reported on 20 November 2026):
- Trump, Xi and Putin hold their first three-way summit in Shenzhen and
  issue a joint peace declaration.
- The International Court of Justice rules Myanmar committed genocide
  against the Rohingya.
- A Russian barrage damages embassies and St Volodymyr's Cathedral in Kyiv.
- Global stocks tumble on AI-valuation doubts after Anthropic's record
  Nasdaq debut; the Nikkei falls 4.8%.
- NASA's Voyager 1 phones home from one light-day away.
Footer: a Houthi missile damages a Riyadh tower; the COP31 draft drops the
call to phase out fossil fuels; Kenya discharges its last Ebola patient.
"""

import os
import struct
import zlib

# --------------------------------------------------------------------------
# Tiny RGB raster canvas with 2x supersampling for smooth edges.
# All drawing coordinates are in final-image pixels (1024 x 1024).
# --------------------------------------------------------------------------

W = 1024
H = 1024
SS = 2
DW = W * SS
DH = H * SS

_buf = bytearray(DW * DH * 3)


def _set(dx, dy, rgb):
    if 0 <= dx < DW and 0 <= dy < DH:
        i = (dy * DW + dx) * 3
        _buf[i] = rgb[0]
        _buf[i + 1] = rgb[1]
        _buf[i + 2] = rgb[2]


def rect(x, y, w, h, rgb):
    """Filled rectangle in final-image coordinates."""
    x0, y0 = int(x * SS), int(y * SS)
    x1, y1 = int((x + w) * SS), int((y + h) * SS)
    r, g, b = rgb
    row = bytes((r, g, b)) * (x1 - x0)
    for dy in range(max(0, y0), min(DH, y1)):
        i = (dy * DW + max(0, x0)) * 3
        _buf[i:i + len(row)] = row


def frame(x, y, w, h, t, rgb):
    rect(x, y, w, t, rgb)
    rect(x, y + h - t, w, t, rgb)
    rect(x, y, t, h, rgb)
    rect(x + w - t, y, t, h, rgb)


def circle(cx, cy, rad, rgb, fill=True):
    """Filled or outline circle."""
    r_out = rad * SS
    r_in = (rad - 2.2) * SS if not fill else -1
    cxd, cyd = cx * SS, cy * SS
    y0 = int(cyd - r_out - 1)
    y1 = int(cyd + r_out + 1)
    for dy in range(max(0, y0), min(DH, y1)):
        dyy = dy - cyd
        rem = r_out * r_out - dyy * dyy
        if rem < 0:
            continue
        half = int(rem ** 0.5)
        if fill:
            xa, xb = int(cxd - half), int(cxd + half)
            for dx in range(max(0, xa), min(DW, xb)):
                _set(dx, dy, rgb)
        else:
            rem_in = r_in * r_in - dyy * dyy
            half_in = int(rem_in ** 0.5) if rem_in > 0 else -1
            for dx in range(int(cxd - half), int(cxd + half)):
                if abs(dx - cxd) > half_in:
                    _set(dx, dy, rgb)


def line(x0, y0, x1, y1, t, rgb):
    """Thick line segment."""
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * SS) + 1
    rad = t / 2.0
    for s in range(steps + 1):
        f = s / steps
        cx = x0 + (x1 - x0) * f
        cy = y0 + (y1 - y0) * f
        # small filled disc at each step
        r = rad * SS
        for dy in range(int(cy * SS - r - 1), int(cy * SS + r + 1)):
            for dx in range(int(cx * SS - r - 1), int(cx * SS + r + 1)):
                if (dx - cx * SS) ** 2 + (dy - cy * SS) ** 2 <= r * r:
                    _set(dx, dy, rgb)


def tri(x0, y0, x1, y1, x2, y2, rgb):
    """Filled triangle (bounding-box barycentric fill)."""
    minx = int(min(x0, x1, x2) * SS)
    maxx = int(max(x0, x1, x2) * SS)
    miny = int(min(y0, y1, y2) * SS)
    maxy = int(max(y0, y1, y2) * SS)
    ax, ay, bx, by, cx, cy = x0 * SS, y0 * SS, x1 * SS, y1 * SS, x2 * SS, y2 * SS
    den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if den == 0:
        return
    for dy in range(max(0, miny), min(DH, maxy)):
        for dx in range(max(0, minx), min(DW, maxx)):
            w0 = ((by - cy) * (dx - cx) + (cx - bx) * (dy - cy)) / den
            w1 = ((cy - ay) * (dx - cx) + (ax - cx) * (dy - cy)) / den
            w2 = 1 - w0 - w1
            if w0 >= 0 and w1 >= 0 and w2 >= 0:
                _set(dx, dy, rgb)


def downsample():
    """Box-downsample the device buffer to W x H RGB bytes."""
    out = bytearray(W * H * 3)
    for y in range(H):
        for x in range(W):
            i = ((y * SS) * DW + (x * SS)) * 3
            j = (y * W + x) * 3
            for c in range(3):
                s = (_buf[i + c] + _buf[i + 3 + c] +
                     _buf[i + DW * 3 + c] + _buf[i + DW * 3 + 3 + c])
                out[j + c] = s // 4
    return bytes(out)


def write_png(path, rgb_bytes):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += rgb_bytes[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


# --------------------------------------------------------------------------
# 5x7 bitmap font (uppercase). Each glyph is 7 rows of 5 pixels.
# --------------------------------------------------------------------------

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", ".#.#.", "..#..", ".#.#.", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "$": ("..#..", ".####", "#.#.#", ".###.", ".#.#.", "####.", "..#.."),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(x, y, text, scale, rgb):
    """Draw text with its top-left at (x, y); scale = font pixel size."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, px in enumerate(row):
                if px == "#":
                    rect(cx + col_i * scale, y + row_i * scale,
                         scale, scale, rgb)
        cx += 6 * scale
    return cx


def draw_text_center(cx, y, text, scale, rgb):
    w = text_width(text, scale)
    draw_text(cx - w / 2, y, text, scale, rgb)


def wrap(text, scale, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(x, y, lines, scale, rgb, line_gap=4):
    """Draw pre-broken lines of text; returns the y just past the block."""
    for i, ln in enumerate(lines):
        draw_text(x, y + i * (7 * scale + line_gap), ln, scale, rgb)
    return y + len(lines) * (7 * scale + line_gap)


def draw_text_block(x, y, text, scale, rgb, max_w, line_gap=4, center=False):
    lines = wrap(text, scale, max_w)
    for i, ln in enumerate(lines):
        yy = y + i * (7 * scale + line_gap)
        if center:
            draw_text_center(x + max_w / 2, yy, ln, scale, rgb)
        else:
            draw_text(x, yy, ln, scale, rgb)
    return y + len(lines) * (7 * scale + line_gap)


# --------------------------------------------------------------------------
# Colours
# --------------------------------------------------------------------------

PAPER = (246, 241, 229)
INK = (20, 22, 26)
WHITE = (255, 255, 255)
RED = (179, 58, 43)
BLUE = (36, 86, 166)
GOLD = (176, 124, 16)
NAVY = (23, 42, 74)
SPACE = (13, 24, 46)
SKY = (219, 232, 245)
GRAY = (110, 116, 124)
SMOKE = (154, 163, 173)
LIGHT = (196, 214, 240)


# --------------------------------------------------------------------------
# Pictograms
# --------------------------------------------------------------------------

def flag_us(x, y, w, h):
    rect(x, y, w, h, WHITE)
    band = h / 7.0
    for i in range(0, 7, 2):
        rect(x, y + i * band, w, band, (198, 42, 52))
    rect(x, y, w * 0.44, band * 4, (40, 52, 122))
    for r in range(4):
        for c in range(5):
            rect(x + 4 + c * (w * 0.44 - 6) / 4, y + 3 + r * (band * 4 - 5) / 3,
                 2.4, 2.4, WHITE)
    frame(x, y, w, h, 1.2, INK)


def flag_china(x, y, w, h):
    rect(x, y, w, h, (222, 41, 57))
    circle(x + w * 0.2, y + h * 0.3, 6, (255, 222, 0))
    for dx, dy in ((0.34, 0.14), (0.38, 0.3), (0.38, 0.48), (0.33, 0.62)):
        circle(x + w * dx, y + h * dy, 2.4, (255, 222, 0))
    frame(x, y, w, h, 1.2, INK)


def flag_russia(x, y, w, h):
    rect(x, y, w, h / 3, WHITE)
    rect(x, y + h / 3, w, h / 3, (0, 57, 166))
    rect(x, y + 2 * h / 3, w, h / 3 + 1, (213, 43, 30))
    frame(x, y, w, h, 1.2, INK)


def pict_flags(x, y, w, h):
    rect(x, y, w, h, SKY)
    rect(x, y + h - 14, w, 14, (178, 198, 214))
    fw, fh = 84, 56
    gap = (w - 3 * fw) / 4
    fy = y + 16
    for i, fn in enumerate((flag_us, flag_china, flag_russia)):
        fx = x + gap + i * (fw + gap)
        line(fx + fw / 2, fy + fh, fx + fw / 2, y + h - 14, 2.4, INK)
        fn(fx, fy, fw, fh)
    frame(x, y, w, h, 2, INK)


def pict_scales(cx, top):
    gold = GOLD
    line(cx, top, cx, top + 58, 4, gold)
    line(cx - 42, top + 8, cx + 42, top + 8, 4, gold)
    circle(cx, top + 3, 4.4, gold)
    for sx in (cx - 42, cx + 42):
        line(sx, top + 8, sx - 12, top + 36, 2, gold)
        line(sx, top + 8, sx + 12, top + 36, 2, gold)
        tri(sx - 19, top + 36, sx + 19, top + 36, sx, top + 50, gold)
    rect(cx - 20, top + 58, 40, 5, gold)
    rect(cx - 28, top + 64, 56, 5, gold)


def pict_cathedral(x, y, w, h):
    rect(x, y, w, h, (207, 220, 235))
    # smoke clouds
    for dx, dy, r in ((0.7, 0.18, 13), (0.82, 0.12, 16), (0.92, 0.2, 11)):
        circle(x + w * dx, y + h * dy, r, SMOKE)
    base = y + h - 8
    cx = x + w * 0.42
    # side towers
    for tx, tw, th in ((cx - 46, 22, 42), (cx + 24, 22, 42)):
        rect(tx, base - th, tw, th, NAVY)
        circle(tx + tw / 2, base - th - 4, 9, GOLD)
        line(tx + tw / 2, base - th - 18, tx + tw / 2, base - th - 9, 2.2, GOLD)
    # main tower and dome
    rect(cx - 14, base - 62, 28, 62, NAVY)
    circle(cx, base - 68, 15, GOLD)
    line(cx, base - 92, cx, base - 78, 2.6, GOLD)
    line(cx - 5, base - 87, cx + 5, base - 87, 2.6, GOLD)
    # windows
    for wx, wy in ((cx - 4, base - 44), (cx - 39, base - 28), (cx + 31, base - 28)):
        rect(wx, wy, 8, 13, (240, 200, 90))
    rect(x, base, w, 3, NAVY)
    frame(x, y, w, h, 2, INK)


def pict_chart(x, y, w, h):
    rect(x, y, w, h, WHITE)
    for i in range(1, 4):
        gy = y + h * i / 4
        line(x + 6, gy, x + w - 6, gy, 1.2, (205, 208, 212))
    line(x + 8, y + 6, x + 8, y + h - 8, 2, GRAY)
    line(x + 8, y + h - 8, x + w - 6, y + h - 8, 2, GRAY)
    pts = [(0.06, 0.3), (0.24, 0.22), (0.4, 0.42), (0.55, 0.36),
           (0.7, 0.6), (0.84, 0.55), (0.96, 0.82)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        line(x + w * ax, y + h * ay, x + w * bx, y + h * by, 4.4, RED)
    ex, ey = x + w * 0.96, y + h * 0.82
    tri(ex + 12, ey + 2, ex - 4, ey - 8, ex - 2, ey + 12, RED)
    frame(x, y, w, h, 2, INK)


def pict_voyager(x, y, w, h):
    rect(x, y, w, h, SPACE)
    # deterministic stars
    seed = 12345
    for _ in range(46):
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        sx = x + 6 + (seed % 1000) / 1000 * (w - 12)
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        sy = y + 6 + (seed % 1000) / 1000 * (h - 12)
        rect(sx, sy, 2.2, 2.2, WHITE)
    cx, cy = x + w * 0.6, y + h * 0.44
    # Earth, far away
    ex, ey = x + w * 0.14, y + h * 0.78
    circle(ex, ey, 11, (70, 130, 220))
    circle(ex - 3, ey - 3, 4, (90, 190, 120))
    # signal dots from probe to Earth
    for f in (0.25, 0.45, 0.65, 0.85):
        circle(cx + (ex - cx) * f, cy + (ey - cy) * f, 2.4, LIGHT)
    # probe: big dish, body, boom
    circle(cx, cy, 24, WHITE, fill=False)
    circle(cx, cy, 3.4, WHITE)
    line(cx, cy, cx + 16, cy - 14, 2.4, LIGHT)
    rect(cx + 12, cy + 8, 22, 13, GOLD)
    line(cx + 30, cy + 14, cx + 62, cy + 34, 3, LIGHT)
    rect(cx + 58, cy + 30, 10, 8, GRAY)
    line(cx + 14, cy + 21, cx - 8, cy + 44, 2.4, LIGHT)
    frame(x, y, w, h, 2, INK)


# --------------------------------------------------------------------------
# Page layout
# --------------------------------------------------------------------------

def panel(x, y, w, h, bg=WHITE):
    rect(x, y, w, h, bg)
    frame(x, y, w, h, 3, INK)


def kicker(x, y, text, rgb=RED):
    draw_text(x, y, text, 3, rgb)


def main():
    rect(0, 0, W, H, PAPER)
    frame(10, 10, W - 20, H - 20, 3, INK)
    frame(18, 18, W - 36, H - 36, 1.4, INK)

    # Masthead
    draw_text_center(W / 2, 30, "ALL THE DAY'S NEWS - ON ONE PAGE", 2, GRAY)
    draw_text_center(W / 2, 50, "THE WORLD TODAY", 10, INK)
    rect(36, 130, W - 72, 3, INK)
    rect(36, 138, W - 72, 42, INK)
    draw_text_center(W / 2, 142, "FRIDAY 20 NOVEMBER 2026", 5, WHITE)

    # Lead story: Shenzhen summit
    panel(36, 192, W - 72, 244)
    kicker(52, 206, "DIPLOMACY - SHENZHEN, CHINA")
    pict_flags(52, 240, 272, 150)
    draw_lines(348, 240,
               ["TRUMP, XI AND PUTIN", "HOLD FIRST THREE-WAY", "SUMMIT"],
               5, INK, line_gap=6)
    draw_text_block(348, 372,
                    "A JOINT PEACE DECLARATION - BUT NO MENTION OF A "
                    "UKRAINE CEASEFIRE.",
                    3, (52, 56, 62), 620, line_gap=5)

    # Row 2: ICJ and Kyiv
    panel(36, 452, 460, 282)
    kicker(52, 466, "INTERNATIONAL JUSTICE")
    pict_scales(266, 494)
    draw_text_block(52, 576,
                    "ICJ RULES MYANMAR COMMITTED GENOCIDE AGAINST "
                    "THE ROHINGYA",
                    4, INK, 432, line_gap=4)
    draw_text(52, 710, "FIRST GENOCIDE VERDICT ON A STATE", 2, RED)
    panel(528, 452, 460, 282)
    kicker(544, 466, "WAR IN UKRAINE - KYIV")
    pict_cathedral(544, 498, 190, 112)
    draw_lines(750, 498,
               ["RUSSIAN", "BARRAGE", "DAMAGES", "EMBASSIES", "IN KYIV"],
               4, INK, line_gap=4)
    draw_text_block(544, 654,
                    "THE CATHEDRAL IS HIT AS UKRAINE STRIKES THE "
                    "CRIMEA BRIDGE AGAIN.",
                    3, (52, 56, 62), 420, line_gap=5)

    # Row 3: markets and Voyager
    panel(36, 750, 460, 200)
    kicker(52, 764, "MARKETS - SELL-OFF")
    pict_chart(52, 796, 150, 118)
    draw_text(218, 800, "-4.8%", 7, RED)
    draw_lines(218, 858,
               ["NIKKEI FALLS", "AS AI DOUBTS", "HIT STOCKS"],
               3, INK, line_gap=4)
    panel(528, 750, 460, 200, SPACE)
    kicker(544, 764, "SPACE - THE LONG GOODBYE", LIGHT)
    pict_voyager(544, 796, 170, 118)
    draw_lines(730, 792,
               ["VOYAGER 1", "CALLS HOME", "FROM 1", "LIGHT-DAY", "AWAY"],
               4, WHITE, line_gap=3)

    # Footer: also in the news
    rect(36, 962, W - 72, 2.4, INK)
    draw_text_center(W / 2, 970,
                     "ALSO: COP31 DRAFT DROPS FOSSIL-FUEL EXIT - KENYA "
                     "SENDS LAST EBOLA PATIENT HOME", 2, INK)
    draw_text_center(W / 2, 988,
                     "ANTHROPIC'S RECORD DEBUT SPARKS AI DOUBTS - HOUTHI "
                     "MISSILE DAMAGES RIYADH TOWER", 2, INK)

    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "entry.png")
    except OSError:
        path = os.path.join("output", "entry.png")
        os.makedirs("output", exist_ok=True)
    write_png(path, downsample())


if __name__ == "__main__":
    main()
