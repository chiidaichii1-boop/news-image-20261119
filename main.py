"""The World, 19 November 2026.

A newspaper front page drawn in pure Python stdlib: a hand-rolled 5x7
bitmap font, a small vector canvas, and a hand-rolled PNG encoder.
Writes /output/entry.png (1024x1024, deterministic).

Stories (all reported on 19 November 2026):
 1. Trump, Xi and Putin meet in Shenzhen (Reuters)
 2. World Court rules on the Rohingya genocide case (Reuters)
 3. Grand Theft Auto VI launches worldwide (Reuters)
 4. Democrats complete the midterm sweep in the US (AP)
 5. EU proposes a 45 billion euro loan for Ukraine (Financial Times)
 6. Voyager 1 reaches one light-day from Earth (NASA / USA Today)
 7. Cyclone Akvan nears the Indian coast (IMD)
 8. Australia sanctions Israeli settlers (AP)
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 234)
INK = (22, 22, 22)
NAVY = (18, 38, 74)
NAVY2 = (28, 58, 108)
GOLD = (198, 158, 60)
RED = (178, 34, 34)
BLUE = (36, 84, 160)
SKY = (120, 170, 215)
LIGHT = (233, 228, 216)
WHITE = (255, 255, 255)
GREY = (120, 116, 106)
DARK = (10, 14, 26)

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, uppercase only. Each glyph is 7 rows of 5 chars.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap(text, scale, max_w):
    """Greedy word wrap; returns a list of lines."""
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        cand = w if not cur else cur + " " + w
        if text_width(cand, scale) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def _set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self._set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=False):
        if fill:
            for dy in range(-r, r + 1):
                half = int(math.sqrt(max(0, r * r - dy * dy)))
                self.fill_rect(cx - half, cy + dy, half * 2 + 1, 1, c)
            return
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self._set(px, py, c)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def arc(self, cx, cy, r, a0, a1, c):
        steps = max(8, int(abs(a1 - a0) * r / 4))
        for i in range(steps + 1):
            a = a0 + (a1 - a0) * i / steps
            self._set(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), c)

    def star(self, cx, cy, r, c):
        # 4-point star (diamond sparkle)
        self.line(cx - r, cy, cx + r, cy, c)
        self.line(cx, cy - r, cx, cy + r, c)
        self.line(cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2, c)
        self.line(cx - r // 2, cy + r // 2, cx + r // 2, cy - r // 2, c)

    def draw_text(self, text, x, y, scale, c):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def draw_text_center(self, text, cx, y, scale, c):
        self.draw_text(text, cx - text_width(text, scale) // 2, y, scale, c)

    def paragraph(self, text, x, y, max_w, scale, c, leading=None):
        lh = leading if leading is not None else 9 * scale
        for line in wrap(text, scale, max_w):
            self.draw_text(line, x, y, scale, c)
            y += lh
        return y


# ---------------------------------------------------------------- page ----
def draw():
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    cv.fill_rect(0, 0, W, 118, NAVY)
    cv.hline(0, 118, W, GOLD, 4)
    cv.draw_text_center("THE WORLD", W // 2, 16, 8, WHITE)
    cv.draw_text_center("THURSDAY, 19 NOVEMBER 2026", W // 2, 82, 2, GOLD)
    cv.draw_text("VOL. 1 - NO. 323", 16, 88, 1, (150, 170, 210))
    cv.draw_text("THE DAY IN ONE PAGE", W - 16 - text_width("THE DAY IN ONE PAGE", 1), 88, 1, (150, 170, 210))

    # ================= ROW 1 =================
    # ---- lead story: trilateral ----
    x0, y0, x1, y1 = 16, 126, 616, 452
    cv.rect(x0, y0, x1 - x0, y1 - y0, INK, 2)
    cv.draw_text("SHENZHEN, CHINA", x0 + 14, y0 + 12, 2, RED)
    cv.draw_text("TRUMP, XI AND PUTIN", x0 + 14, y0 + 38, 4, NAVY)
    cv.draw_text("MEET IN SHENZHEN", x0 + 14, y0 + 72, 4, NAVY)
    cv.hline(x0 + 14, y0 + 112, x1 - x0 - 28, GOLD, 3)
    # globe illustration, right side
    gx, gy, gr = 505, 318, 56
    cv.circle(gx, gy, gr, NAVY)
    cv.arc(gx, gy, gr, -1.2, 1.2, NAVY)
    cv.arc(gx, gy, gr, math.pi - 1.2, math.pi + 1.2, NAVY)
    cv.arc(gx, gy, int(gr * 0.55), -1.2, 1.2, NAVY)
    cv.arc(gx, gy, int(gr * 0.55), math.pi - 1.2, math.pi + 1.2, NAVY)
    cv.hline(gx - gr, gy, gr * 2, NAVY)
    half = int(math.sqrt(gr * gr - 28 * 28))
    cv.hline(gx - half, gy - 28, half * 2, NAVY)
    cv.hline(gx - half, gy + 28, half * 2, NAVY)
    # three leaders' markers
    for (mx, my, lab) in ((gx - 36, gy - 16, "USA"),
                          (gx + 28, gy - 26, "CHN"),
                          (gx + 6, gy + 28, "RUS")):
        cv.circle(mx, my, 7, RED, fill=True)
        cv.circle(mx, my, 7, WHITE)
        cv.draw_text(lab, mx - 12, my + 12, 1, INK)
    # summary, left of the globe
    cv.paragraph(
        "THE LEADERS OF THE WORLD'S THREE LARGEST NUCLEAR POWERS MEET FOR "
        "THE FIRST TIME, AT THE APEC SUMMIT. NUCLEAR ARMS CONTROL, UKRAINE "
        "AND TRADE TOP THE AGENDA.",
        x0 + 14, y0 + 126, 330, 2, INK)
    cv.paragraph(
        "TRUMP ALSO MEETS XI ONE ON ONE, AND PUTIN FOR THE FIRST TIME SINCE "
        "ALASKA IN 2025.",
        x0 + 14, y0 + 258, 560, 2, (70, 70, 70))

    # ---- ICJ ----
    x0, y0, x1, y1 = 632, 126, 1008, 300
    cv.rect(x0, y0, x1 - x0, y1 - y0, INK, 2)
    cv.draw_text("THE HAGUE", x0 + 12, y0 + 10, 2, RED)
    cv.draw_text("WORLD COURT RULES", x0 + 12, y0 + 34, 3, NAVY)
    cv.draw_text("ON ROHINGYA CASE", x0 + 12, y0 + 58, 3, NAVY)
    cv.paragraph(
        "THE WORLD COURT DELIVERS ITS FINAL JUDGMENT ON WHETHER MYANMAR "
        "COMMITTED GENOCIDE AGAINST THE ROHINGYA.",
        x0 + 12, y0 + 92, x1 - x0 - 24, 2, INK)

    # ---- GTA VI ----
    x0, y0, x1, y1 = 632, 310, 1008, 452
    cv.rect(x0, y0, x1 - x0, y1 - y0, INK, 2)
    cv.draw_text("VICE CITY", x0 + 12, y0 + 10, 2, RED)
    cv.draw_text("GTA VI IS HERE", x0 + 12, y0 + 34, 3, NAVY)
    cv.paragraph(
        "AFTER 13 YEARS, ROCKSTAR'S GTA VI ROLLS OUT WORLDWIDE.",
        x0 + 12, y0 + 62, x1 - x0 - 24, 2, INK)
    cv.draw_text("17M+ COPIES SOLD, $1.65BN IN PRE-ORDERS",
                 x0 + 12, y0 + 102, 1, (70, 70, 70))
    # neon skyline strip at the bottom
    bx, by, bw, bh = x0, y1 - 28, x1 - x0, 28
    cv.fill_rect(bx, by, bw, bh, DARK)
    cv.circle(bx + 52, by + 10, 7, GOLD, fill=True)
    heights = (16, 22, 12, 20, 26, 17, 24, 14, 21, 18)
    hx = bx + 8
    for hh in heights:
        cv.fill_rect(hx, by + bh - hh, 30, hh, NAVY2)
        hx += 36
    # 99 Metacritic badge, top-right: at its old spot (x1-40, y1-42) its
    # left edge (x 950) covered the end of "GTA VI ROLLS OUT WORLDWIDE."
    # (which ends at x 966); up here it clears every line of text
    cv.circle(x1 - 34, y0 + 40, 18, GOLD, fill=True)
    cv.circle(x1 - 34, y0 + 40, 18, NAVY)
    cv.draw_text("99", x1 - 45, y0 + 33, 2, NAVY)

    # ================= ROW 2 =================
    # ---- US midterms ----
    x0, y0, x1, y1 = 16, 462, 500, 688
    cv.rect(x0, y0, x1 - x0, y1 - y0, INK, 2)
    cv.draw_text("WASHINGTON", x0 + 12, y0 + 10, 2, RED)
    cv.draw_text("DEMOCRATS SWEEP", x0 + 12, y0 + 34, 3, NAVY)
    cv.draw_text("CONGRESS", x0 + 12, y0 + 58, 3, NAVY)
    cv.paragraph(
        "MARY PELTOLA WINS ALASKA. DEMOCRATS TAKE A 56-44 SENATE MAJORITY, "
        "FLIPPING NINE SEATS, THE MOST SINCE 1958.",
        x0 + 12, y0 + 92, x1 - x0 - 24, 2, INK)
    cv.draw_text("DEMOCRATS ALSO RETOOK THE HOUSE, UP 42 SEATS.",
                 x0 + 12, y0 + 150, 1, (70, 70, 70))
    # senate bar chart
    byy = y1 - 62
    cv.draw_text("DEM", x0 + 12, byy, 2, BLUE)
    cv.fill_rect(x0 + 72, byy, 200, 16, BLUE)
    cv.draw_text("56", x0 + 280, byy, 2, INK)
    cv.draw_text("REP", x0 + 12, byy + 24, 2, RED)
    cv.fill_rect(x0 + 72, byy + 24, 157, 16, RED)
    cv.draw_text("44", x0 + 237, byy + 24, 2, INK)

    # ---- EU Ukraine loan ----
    x0, y0, x1, y1 = 516, 462, 1008, 688
    cv.rect(x0, y0, x1 - x0, y1 - y0, INK, 2)
    cv.draw_text("BRUSSELS", x0 + 12, y0 + 10, 2, RED)
    cv.draw_text("EU PLANS 45 BN EURO", x0 + 12, y0 + 34, 3, NAVY)
    cv.draw_text("LOAN FOR KYIV", x0 + 12, y0 + 58, 3, NAVY)
    cv.paragraph(
        "THE EUROPEAN COMMISSION PROPOSES BORROWING 45 BILLION EUROS TO "
        "COVER UKRAINE'S 2027 BUDGET GAP, TO BE REPAID ONLY ONCE RUSSIA "
        "PAYS WAR REPARATIONS.",
        x0 + 12, y0 + 92, 330, 2, INK)
    # big coin
    cx, cy = x1 - 66, y1 - 58
    cv.circle(cx, cy, 34, GOLD, fill=True)
    cv.circle(cx, cy, 34, NAVY)
    cv.draw_text_center("45", cx, cy - 14, 3, NAVY)
    cv.draw_text_center("BN", cx, cy + 8, 2, NAVY)

    # ================= ROW 3 =================
    # ---- Voyager 1 ----
    x0, y0, x1, y1 = 16, 698, 340, 986
    cv.rect(x0, y0, x1 - x0, y1 - y0, INK, 2)
    cv.fill_rect(x0 + 2, y0 + 2, x1 - x0 - 4, 92, DARK)
    for (sx, sy) in ((x0 + 30, y0 + 20), (x0 + 90, y0 + 40), (x0 + 150, y0 + 14),
                     (x0 + 210, y0 + 60), (x0 + 260, y0 + 26), (x0 + 300, y0 + 70),
                     (x0 + 60, y0 + 74), (x0 + 180, y0 + 82), (x0 + 240, y0 + 12)):
        cv._set(sx, sy, WHITE)
        cv._set(sx + 1, sy, WHITE)
        cv._set(sx, sy + 1, WHITE)
    # probe: dish + body
    px, py = x0 + 160, y0 + 52
    cv.line(px - 40, py + 8, px + 30, py - 6, WHITE)
    cv.fill_rect(px - 6, py - 6, 26, 12, GOLD)
    cv.circle(px - 46, py + 10, 8, WHITE)
    cv.draw_text("VOYAGER 1", x0 + 12, y0 + 104, 3, NAVY)
    cv.draw_text("ONE LIGHT-DAY", x0 + 12, y0 + 128, 3, NAVY)
    cv.draw_text("FROM HOME", x0 + 12, y0 + 152, 3, NAVY)
    cv.paragraph(
        "AFTER 49 YEARS IN SPACE, NASA'S VOYAGER 1 IS THE FIRST HUMAN-MADE "
        "OBJECT ONE LIGHT-DAY FROM EARTH - 16 BILLION MILES AWAY.",
        x0 + 12, y0 + 184, x1 - x0 - 24, 2, INK)

    # ---- Cyclone Akvan ----
    x0, y0, x1, y1 = 356, 698, 668, 986
    cv.rect(x0, y0, x1 - x0, y1 - y0, INK, 2)
    cv.draw_text("BAY OF BENGAL", x0 + 12, y0 + 10, 2, RED)
    cv.draw_text("CYCLONE AKVAN", x0 + 12, y0 + 34, 3, NAVY)
    cv.draw_text("NEARS INDIA", x0 + 12, y0 + 58, 3, NAVY)
    # spiral
    cx, cy = x0 + 156, y0 + 146
    for r in (10, 18, 26, 34, 42):
        cv.arc(cx, cy, r, 0.6, 5.4, BLUE)
    cv.circle(cx, cy, 6, RED, fill=True)
    cv.draw_text("120-130 KM/H WINDS", x0 + 12, y0 + 206, 2, INK)
    cv.paragraph(
        "LANDFALL IS FORECAST AROUND NOON ON 20 NOVEMBER.",
        x0 + 12, y0 + 230, x1 - x0 - 24, 2, INK)

    # ---- Australia sanctions ----
    x0, y0, x1, y1 = 684, 698, 1008, 986
    cv.rect(x0, y0, x1 - x0, y1 - y0, INK, 2)
    cv.draw_text("CANBERRA", x0 + 12, y0 + 10, 2, RED)
    cv.draw_text("AUSTRALIA", x0 + 12, y0 + 34, 3, NAVY)
    # second line at size 2: at size 3 "SANCTIONS SETTLERS" is 321 px
    # wide and runs 9 px past the panel's right edge
    cv.draw_text("SANCTIONS SETTLERS", x0 + 12, y0 + 58, 2, NAVY)
    cv.paragraph(
        "AUSTRALIA SANCTIONS ISRAELI SETTLERS AND ORGANISATIONS OVER WEST "
        "BANK EXPANSION, STEPPING UP PRESSURE OVER THE OCCUPIED TERRITORY.",
        x0 + 12, y0 + 92, x1 - x0 - 24, 2, INK)
    # flag panel: blue field, southern cross stars
    fx, fy, fw, fh = x0 + 12, y1 - 92, x1 - x0 - 24, 80
    cv.fill_rect(fx, fy, fw, fh, NAVY2)
    for (sx, sy) in ((fx + 40, fy + 20), (fx + 90, fy + 44), (fx + 150, fy + 16),
                     (fx + 210, fy + 52), (fx + 260, fy + 28)):
        cv.star(sx, sy, 7, WHITE)
    cv.draw_text("WEST BANK", fx + 12, fy + fh - 22, 2, WHITE)

    # ---- footer ----
    cv.draw_text_center(
        "SOURCES: REUTERS, AP, NASA, FINANCIAL TIMES - THE WORLD, 19 NOVEMBER 2026",
        W // 2, 998, 1, GREY)

    return cv


# ------------------------------------------------------------------ png ----
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def save_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        i = (y * cv.w) * 3
        raw += cv.buf[i:i + cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    cv = draw()
    os.makedirs("/output", exist_ok=True)
    n = save_png(cv, "/output/entry.png")
    print("wrote /output/entry.png:", n, "bytes")


if __name__ == "__main__":
    main()
