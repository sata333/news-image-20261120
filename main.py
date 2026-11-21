#!/usr/bin/env python3
"""THE WORLD TODAY - one image summing up the world news of Friday 20 November 2026.

Draws a newspaper front page (masthead, date line, headline panels with small
drawn motifs, and an "also today" footer) using only the Python standard
library, and writes it as a 1024x1024 PNG to /output/entry.png
(or to $OUTPUT_DIR/entry.png when OUTPUT_DIR is set).

No network access. The drawing is pure integer arithmetic, so two runs
produce byte-identical output.
"""

import os
import struct
import zlib

W = H = 1024

# --------------------------------------------------------------------------
# 5x7 bitmap font (rows of 5 pixels). Only the characters used below.
# --------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "....#", "...#.", ".###.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "•": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
}

# --------------------------------------------------------------------------
# Colours
# --------------------------------------------------------------------------
PAPER = (247, 242, 228)
INK = (22, 19, 12)
RED = (163, 22, 33)
BLUE = (29, 78, 137)
GOLD = (176, 132, 10)
GREY = (107, 103, 92)
LIGHT = (226, 218, 196)
PINK = (233, 199, 199)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg) * (w * h)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                x0 = max(0, x)
                x1 = min(self.w, x + w)
                if x0 < x1:
                    i = (yy * self.w + x0) * 3
                    self.buf[i:i + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for t in range(thick):
                self.px(x0, y0 + t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, width=5):
        half = width / 2.0
        for yy in range(cy - r - width, cy + r + width + 1):
            for xx in range(cx - r - width, cx + r + width + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= half:
                    self.px(xx, yy, color)


# --------------------------------------------------------------------------
# Text
# --------------------------------------------------------------------------
def clean(s):
    return (s.upper()
             .replace("’", "'").replace("‘", "'")
             .replace("“", '"').replace("”", '"')
             .replace("–", "-").replace("—", "-")
             .replace("·", "•"))


def text_width(s, scale):
    return len(clean(s)) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color, bold=False):
    s = clean(s)
    cx = x
    extra = max(1, scale // 3) if bold else 0
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "#":
                    for dx in range(extra + 1):
                        cv.rect(cx + col * scale + dx, y + row * scale,
                                scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, cx, y, s, scale, color, bold=False):
    w = text_width(s, scale)
    return draw_text(cv, cx - w // 2, y, s, scale, color, bold)


def draw_text_right(cv, xr, y, s, scale, color, bold=False):
    w = text_width(s, scale)
    return draw_text(cv, xr - w, y, s, scale, color, bold)


def wrap(s, scale, max_w):
    words = clean(s).split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_paragraph(cv, x, y, s, scale, color, max_w, leading):
    lines = wrap(s, scale, max_w)
    for line in lines:
        draw_text(cv, x, y, line, scale, color)
        y += 7 * scale + leading
    return y


# --------------------------------------------------------------------------
# Motifs
# --------------------------------------------------------------------------
def motif_rings(cv, cx, cy):
    r = 44
    cv.circle(cx - 58, cy, r, BLUE, 6)
    cv.circle(cx, cy, r, RED, 6)
    cv.circle(cx + 58, cy, r, GOLD, 6)


def motif_scales(cv, cx, y):
    top = y
    cv.line(cx, top, cx, top + 40, INK, 4)
    cv.line(cx - 36, top + 6, cx + 36, top + 6, INK, 4)
    cv.circle(cx, top + 2, 5, RED, 5)
    for sgn in (-1, 1):
        px_ = cx + sgn * 36
        cv.line(px_, top + 6, px_ - 11, top + 26, INK, 2)
        cv.line(px_, top + 6, px_ + 11, top + 26, INK, 2)
        cv.line(px_ - 14, top + 26, px_ + 14, top + 26, INK, 3)
        cv.line(px_ - 14, top + 26, px_, top + 33, GOLD, 2)
        cv.line(px_ + 14, top + 26, px_, top + 33, GOLD, 2)
    cv.rect(cx - 20, top + 40, 40, 4, INK)


def motif_chart(cv, x, y, w, h):
    cv.line(x, y, x, y + h, GREY, 2)
    cv.line(x, y + h, x + w, y + h, GREY, 2)
    pts = [(0.02, 0.18), (0.16, 0.10), (0.30, 0.26), (0.44, 0.22),
           (0.58, 0.44), (0.72, 0.40), (0.86, 0.66), (0.99, 0.88)]
    prev = None
    for fx, fy in pts:
        px_ = int(x + fx * w)
        py_ = int(y + fy * h)
        if prev is not None:
            cv.line(prev[0], prev[1], px_, py_, RED, 4)
        prev = (px_, py_)
    ex, ey = prev
    cv.line(ex, ey, ex - 12, ey - 1, RED, 4)
    cv.line(ex, ey, ex - 3, ey - 12, RED, 4)


def motif_flags(cv, x, y):
    # EU: navy field, ring of gold stars. UK: white field, red cross, blue border.
    import math
    cv.rect(x, y, 84, 54, BLUE)
    for k in range(12):
        ang = 2 * math.pi * k / 12
        sx = int(x + 42 + 16 * math.cos(ang))
        sy = int(y + 27 + 16 * math.sin(ang))
        cv.rect(sx - 2, sy - 2, 5, 5, GOLD)
    ux = x + 58
    cv.rect(ux, y, 84, 54, PAPER)
    cv.rect(ux, y, 84, 3, BLUE)
    cv.rect(ux, y + 51, 84, 3, BLUE)
    cv.rect(ux, y, 3, 54, BLUE)
    cv.rect(ux + 81, y, 3, 54, BLUE)
    cv.rect(ux + 38, y, 9, 54, RED)
    cv.rect(ux, y + 23, 84, 9, RED)


# --------------------------------------------------------------------------
# Page composition
# --------------------------------------------------------------------------
def story(cv, x, y, w, kicker, headline_lines, body, body_w=None, motif=None):
    draw_text(cv, x, y, kicker, 2, RED, bold=True)
    y += 19
    for line in headline_lines:
        draw_text(cv, x, y, line, 4, INK, bold=True)
        y += 34
    y += 4
    yb = draw_paragraph(cv, x, y, body, 2, INK, body_w or w, 5)
    if motif == "scales":
        motif_scales(cv, x + w - 52, y + 2)
    elif motif == "chart":
        motif_chart(cv, x + w - 168, y + 2, 160, 46)
    elif motif == "flags":
        motif_flags(cv, x + w - 150, y + 2)
    return yb


def build():
    cv = Canvas(W, H, PAPER)
    M = 36
    CW = W - 2 * M

    # masthead
    cv.rect(M, 24, CW, 3, INK)
    draw_text_centered(cv, W // 2, 38, "THE WORLD TODAY", 10, INK, bold=True)
    cv.rect(M, 120, CW, 1, INK)
    cv.rect(M, 125, CW, 3, INK)

    # date bar
    cv.rect(M, 136, CW, 40, INK)
    draw_text(cv, M + 16, 145, "FRIDAY 20 NOVEMBER 2026", 3, PAPER, bold=True)
    draw_text_right(cv, W - M - 16, 145, "THE DAY IN ONE IMAGE", 3, PAPER)

    # lead story
    y = 192
    draw_text(cv, M, y, "SHENZHEN - APEC SUMMIT", 3, RED, bold=True)
    motif_rings(cv, W - M - 118, y + 62)
    y += 30
    for line in ("THREE POWERS", "SIGN A 'PEACE", "DECLARATION'"):
        draw_text(cv, M, y, line, 7, INK, bold=True)
        y += 58
    y += 4
    y = draw_paragraph(
        cv, M, y,
        "TRUMP, XI AND PUTIN END THE FIRST US-CHINA-RUSSIA SUMMIT WITH A "
        "JOINT VOW: NO NUCLEAR WAR, MORE FUEL, A REFORMED UN. UKRAINE IS "
        "NEVER MENTIONED.",
        3, INK, CW, 7)
    y += 10
    cv.rect(M, y, CW, 2, INK)
    y += 12

    # row of two: Ukraine war + ICJ
    colw = CW // 2 - 10
    x2 = M + CW // 2 + 10
    y_left = story(
        cv, M, y, colw, "UKRAINE WAR",
        ("MISSILES FALL ON", "NATO SOIL"),
        "RUSSIA'S BIGGEST STRIKE OF THE MONTH - 110+ MISSILES, 400 "
        "DRONES - HITS THREE KYIV BRIDGES AND EMBASSIES. TWO MISSILES "
        "AND A DRONE FALL IN POLAND.")
    y_right = story(
        cv, x2, y, colw, "THE HAGUE - WORLD COURT",
        ("ICJ: MYANMAR", "COMMITTED GENOCIDE"),
        "JUDGES RULE 9-6 IN THE GAMBIA'S CASE THAT THE 2017 CRACKDOWN "
        "WAS GENOCIDE - A FIRST FOR A STATE. REPARATIONS ARE ORDERED.",
        body_w=colw - 100, motif="scales")
    y = max(y_left, y_right) + 8
    cv.rect(M, y, CW, 2, INK)
    y += 12

    # row of two: markets + UK/EU
    y_left = story(
        cv, M, y, colw, "MARKETS",
        ("AI FEVER BREAKS -", "STOCKS TUMBLE"),
        "DOUBTS OVER AI SPENDING SINK STOCKS: THE S&P 500 FALLS 3.7% "
        "INTO CORRECTION, THE NIKKEI 5.06%. ANTHROPIC SLIDES AFTER "
        "ITS $81BN IPO.",
        body_w=colw - 178, motif="chart")
    y_right = story(
        cv, x2, y, colw, "BRUSSELS SUMMIT",
        ("UK AND EU SIGN", "NEW DEAL"),
        "FOOD TRADE, CARBON MARKETS AND A YOUTH MOBILITY SCHEME ARE "
        "AGREED. BURNHAM EYES EVEN CLOSER TIES.",
        body_w=colw - 160, motif="flags")
    y = max(y_left, y_right) + 10
    cv.rect(M, y, CW, 2, INK)
    y += 10

    # footer: black "also today" bar
    cv.rect(M, y, CW, 56, INK)
    draw_text(cv, M + 16, y + 6, "ALSO TODAY - HOUTHI MISSILE DAMAGES "
              "RIYADH'S TALLEST TOWER", 2, PAPER, bold=True)
    draw_text(cv, M + 16, y + 22, "UKRAINE HITS CRIMEA BRIDGE AGAIN • "
              "FOSSIL-FUEL PHASE-OUT", 2, PAPER)
    draw_text(cv, M + 16, y + 38, "DROPPED FROM COP31 DRAFT • VOYAGER 1 "
              "AT ONE LIGHT-DAY", 2, PAPER)
    y += 64
    draw_text_centered(cv, W // 2, y,
                       "COMPILED FROM THE DAY'S REPORTING - REUTERS, BBC, "
                       "AL JAZEERA, SCMP", 2, GREY)
    return cv


def save_png(cv, path):
    raw = bytearray()
    row_bytes = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.buf[yy * row_bytes:(yy + 1) * row_bytes]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = save_png(build(), path)
    print(f"wrote {path} ({size} bytes)")


if __name__ == "__main__":
    main()
