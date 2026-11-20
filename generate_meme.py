#!/usr/bin/env python3
"""GTA 6 meme renderer for make.fun competition gta6-meme-x-01.

Deterministic PIL render, 1200x675: Vice City neon sunset, the real
make.fun ghost mark large in the centre in a beach chair, sunglasses and
a game controller, two text lines with a thick black outline.
No randomness, no timestamps, no network. Running twice gives
byte-identical output.
"""
import glob
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
W, H = 1200, 675

SKY_TOP = (42, 10, 78)        # deep purple
SKY_MID = (142, 30, 99)       # magenta-purple
SKY_LOW = (214, 51, 108)      # magenta
HORIZON = (255, 126, 54)      # orange at the horizon
HORIZON_Y = 440
WATER_TOP = (255, 140, 80)
WATER_BOT = (120, 40, 110)
SAND_TOP = (242, 192, 120)
SAND_BOT = (222, 158, 87)
SILHOUETTE = (22, 10, 46)     # skyline / palms
WINDOW_LIT = (255, 209, 102)
WINDOW_LIT2 = (255, 158, 79)
SUN = (255, 209, 102)
SUN_CORE = (255, 236, 170)
CHAIR_MAGENTA = (224, 33, 138)
CHAIR_WHITE = (255, 255, 255)
CHAIR_FRAME = (30, 12, 40)
CTRL_BODY = (20, 20, 43)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gradient(img, y0, y1, stops):
    """Fill rows y0..y1 with a vertical multi-stop gradient."""
    d = ImageDraw.Draw(img)
    n = max(1, y1 - y0)
    for y in range(y0, y1):
        t = (y - y0) / n
        for i in range(len(stops) - 1):
            lo, hi = i / (len(stops) - 1), (i + 1) / (len(stops) - 1)
            if lo <= t <= hi:
                f = 0.0 if hi == lo else (t - lo) / (hi - lo)
                d.line([(0, y), (W, y)], fill=lerp(stops[i], stops[i + 1], f))
                break


def bezier(p0, p1, p2, steps=24):
    pts = []
    for s in range(steps + 1):
        t = s / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def find_bold_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    hits = sorted(glob.glob("/usr/share/fonts/**/*.ttf", recursive=True))
    for h in hits:
        name = h.lower()
        if "bold" in name and "dejavu" in name:
            return h
    for h in hits:
        if "bold" in name:
            return h
    return hits[0] if hits else None


def fit_font(text, max_width, start_size):
    path = find_bold_font()
    size = start_size
    while size > 10:
        font = ImageFont.truetype(path, size)
        if font.getlength(text) <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(path, 10)


def draw_text(d, text, y, start_size, max_width=1120):
    font = fit_font(text, max_width, start_size)
    w = font.getlength(text)
    x = (W - w) / 2
    d.text((x, y), text, font=font, fill=(255, 255, 255),
           stroke_width=4, stroke_fill=(0, 0, 0))
    return y + font.size


def draw_sun(d, overlay):
    # soft glow rings, then the disc; offset right so the ghost and chair
    # (centre) do not hide it -- it sets behind the skyline instead
    od = ImageDraw.Draw(overlay)
    cx, cy, r = 930, 392, 88
    for rad, alpha in ((160, 28), (132, 45), (110, 70)):
        od.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                   fill=(255, 170, 60, alpha))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN)
    d.ellipse([cx - r + 13, cy - r + 13, cx + r - 13, cy + r - 13],
              fill=SUN_CORE)
    # thin darker sun stripes (retro synthwave touch), clipped to the disc
    for dy, hh in ((32, 5), (50, 7), (70, 9)):
        yy = cy + dy
        half = int(math.sqrt(max(0, r * r - dy * dy)))
        d.rectangle([cx - half, yy, cx + half, yy + hh], fill=HORIZON)


def draw_skyline(d):
    x = -10
    i = 0
    while x < W:
        w = 52 + ((i * 37) % 48)
        h = 62 + ((i * 53) % 128)
        top = HORIZON_Y - h
        d.rectangle([x, top, x + w, HORIZON_Y], fill=SILHOUETTE)
        # antenna on some towers
        if i % 4 == 1:
            d.line([(x + w // 2, top), (x + w // 2, top - 22)],
                   fill=SILHOUETTE, width=4)
            d.ellipse([x + w // 2 - 3, top - 28, x + w // 2 + 3, top - 22],
                      fill=(255, 80, 90))
        # tiny lit windows, deterministic pattern
        cols = max(1, w // 14)
        rows = max(1, h // 20)
        for r in range(rows):
            for c in range(cols):
                if (i * 7 + c * 3 + r * 5) % 4 == 0:
                    wx = x + 6 + c * 14
                    wy = top + 10 + r * 20
                    col = WINDOW_LIT if (i + c + r) % 3 else WINDOW_LIT2
                    d.rectangle([wx, wy, wx + 5, wy + 7], fill=col)
        x += w + 6 + ((i * 11) % 10)
        i += 1


def draw_palm(d, mirror=False):
    """Palm silhouette at one edge. mirror=True puts it on the right."""
    if not mirror:
        base = (48, H)
        top = (118, 296)
        lean = -1
    else:
        base = (1152, H)
        top = (1082, 296)
        lean = 1
    # trunk: curved, thick
    pts = bezier(base, ((base[0] + top[0]) / 2 + lean * 26, 480), top)
    d.line(pts, fill=SILHOUETTE, width=16, joint="curve")
    # fronds fanning out from the crown
    for k, (dx, dy, bend) in enumerate((
            (-150, -58, -46), (-110, -96, -70), (-52, -118, -88),
            (18, -122, -92), (88, -104, -72), (138, -62, -44),
            (-128, 6, 26), (128, 4, 28))):
        tip = (top[0] + dx, top[1] + dy)
        mid = (top[0] + dx * 0.55, top[1] + dy * 0.55 + bend)
        frond = bezier(top, mid, tip)
        d.line(frond, fill=SILHOUETTE, width=9, joint="curve")
        # leaflet ticks along the frond
        for s in range(2, 9):
            t = s / 10
            px = (1 - t) ** 2 * top[0] + 2 * (1 - t) * t * mid[0] + t ** 2 * tip[0]
            py = (1 - t) ** 2 * top[1] + 2 * (1 - t) * t * mid[1] + t ** 2 * tip[1]
            d.line([(px, py), (px - lean * 0 + (dx * 0.10), py + 16)],
                   fill=SILHOUETTE, width=4)
    # coconuts
    d.ellipse([top[0] - 16, top[1] + 2, top[0] - 2, top[1] + 16],
              fill=SILHOUETTE)
    d.ellipse([top[0] + 2, top[1] + 4, top[0] + 16, top[1] + 18],
              fill=SILHOUETTE)


def draw_chair(img, d):
    """Striped beach chair behind the ghost (peeks out at the sides).

    Stripes are painted on a layer and clipped to the backrest trapezoid
    with a mask, so they never cover the sky, sun or skyline.
    """
    top_y, bot_y = 196, 540
    poly = [(372, top_y), (828, top_y), (870, bot_y), (330, bot_y)]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    x, idx = 290, 0
    while x < 910:
        col = CHAIR_MAGENTA if idx % 2 == 0 else CHAIR_WHITE
        ld.rectangle([x, top_y, x + 42, bot_y], fill=col + (255,))
        x += 42
        idx += 1
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    # keep stripe alpha only inside the trapezoid, then composite
    layer.putalpha(Image.composite(layer.split()[3],
                                   Image.new("L", (W, H), 0), mask))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer)
              .convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    d.line(poly + [poly[0]], fill=CHAIR_FRAME, width=8, joint="curve")
    # horizontal slats
    for yy in (280, 360, 440, 510):
        f = (yy - top_y) / (bot_y - top_y)
        lx = 372 + (330 - 372) * f
        rx = 828 + (870 - 828) * f
        d.line([(lx, yy), (rx, yy)], fill=CHAIR_FRAME, width=5)
    # legs splaying out below
    d.line([(360, bot_y), (300, 640)], fill=CHAIR_FRAME, width=9)
    d.line([(840, bot_y), (900, 640)], fill=CHAIR_FRAME, width=9)


def draw_controller(d):
    """Small game controller held in front of the ghost, low centre."""
    x0, y0, x1, y1 = 538, 512, 662, 570
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=CTRL_BODY,
                        outline=(0, 0, 0), width=3)
    # grips
    d.ellipse([x0 + 4, y1 - 22, x0 + 34, y1 + 6], fill=CTRL_BODY,
              outline=(0, 0, 0), width=3)
    d.ellipse([x1 - 34, y1 - 22, x1 - 4, y1 + 6], fill=CTRL_BODY,
              outline=(0, 0, 0), width=3)
    # D-pad (left)
    d.rectangle([x0 + 22, y0 + 16, x0 + 30, y0 + 34], fill=(255, 255, 255))
    d.rectangle([x0 + 14, y0 + 22, x0 + 38, y0 + 28], fill=(255, 255, 255))
    # action buttons (right): magenta, cyan, yellow, green
    cx, cy = x1 - 26, y0 + 26
    for (dx, dy, col) in ((0, -9, (224, 33, 138)), (9, 0, (0, 200, 220)),
                          (0, 9, (255, 209, 102)), (-9, 0, (80, 220, 120))):
        d.ellipse([cx + dx - 5, cy + dy - 5, cx + dx + 5, cy + dy + 5],
                  fill=col, outline=(0, 0, 0), width=1)
    # sticks
    d.ellipse([x0 + 44, y0 + 32, x0 + 56, y0 + 44], fill=(60, 60, 90),
              outline=(0, 0, 0), width=2)
    d.ellipse([x1 - 56, y0 + 32, x1 - 44, y0 + 44], fill=(60, 60, 90),
              outline=(0, 0, 0), width=2)


def draw_sunglasses(d, ghost_xy, ghost_size):
    """Slim black shades over the ghost's sparkle eyes.

    Sparkle-eye centres in the 1024px source mark are about
    (452, 412) and (580, 405); scale them into the pasted position.
    """
    ox, oy = ghost_xy
    s = ghost_size / 1024.0
    le = (ox + 452 * s, oy + 412 * s)
    re = (ox + 580 * s, oy + 405 * s)
    lw, lh = 64 * s * 1.6, 42 * s * 1.6
    for (cx, cy) in (le, re):
        d.rounded_rectangle([cx - lw / 2, cy - lh / 2,
                             cx + lw / 2, cy + lh / 2],
                            radius=int(lh * 0.45), fill=(10, 10, 16),
                            outline=(0, 0, 0), width=2)
        # glint
        d.line([(cx - lw * 0.28, cy + lh * 0.18),
                (cx + lw * 0.05, cy - lh * 0.22)],
               fill=(255, 255, 255), width=3)
    # bridge + temple arms (level, so they read as shades not angry brows)
    d.line([(le[0] + lw / 2, le[1] - 2), (re[0] - lw / 2, re[1] - 2)],
           fill=(10, 10, 16), width=4)
    d.line([(le[0] - lw / 2, le[1]), (le[0] - lw / 2 - 22, le[1] - 2)],
           fill=(10, 10, 16), width=4)
    d.line([(re[0] + lw / 2, re[1]), (re[0] + lw / 2 + 22, re[1] - 2)],
           fill=(10, 10, 16), width=4)


def main():
    img = Image.new("RGB", (W, H), SKY_TOP)
    d = ImageDraw.Draw(img)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # 1. sky gradient
    gradient(img, 0, HORIZON_Y, [SKY_TOP, SKY_MID, SKY_LOW, HORIZON])
    # 2. sun low over the water
    draw_sun(d, overlay)
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay)
              .convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    # 3. water band + sun reflection (under the sun, right of centre)
    gradient(img, HORIZON_Y, 545, [WATER_TOP, WATER_BOT])
    for k, yy in enumerate(range(448, 540, 12)):
        wdt = 150 - k * 12
        d.rectangle([930 - wdt // 2, yy, 930 + wdt // 2, yy + 4],
                    fill=(255, 214, 130))
    # 4. skyline silhouette across the middle
    draw_skyline(d)
    # 5. sand strip at the bottom
    gradient(img, 545, H, [SAND_TOP, SAND_BOT])
    for k in range(40):
        sx = 30 + (k * 173) % 1140
        sy = 560 + (k * 47) % 100
        d.ellipse([sx, sy, sx + 4, sy + 3], fill=(190, 130, 70))
    # 6. beach chair (behind the ghost)
    draw_chair(img, d)
    d = ImageDraw.Draw(img)
    # 7. palms at the edges
    draw_palm(d, mirror=False)
    draw_palm(d, mirror=True)
    # 8. the real ghost mark, large in the centre
    ghost = Image.open(ASSETS / "ghost.png").convert("RGBA")
    ghost_size = 400
    ghost_xy = ((W - ghost_size) // 2, 118)
    ghost = ghost.resize((ghost_size, ghost_size), Image.LANCZOS)
    img.paste(ghost, ghost_xy, ghost)
    d = ImageDraw.Draw(img)
    # 9. sunglasses over the sparkle eyes + controller in front
    draw_sunglasses(d, ghost_xy, ghost_size)
    draw_controller(d)
    # 10. text, kept clear of the ghost's face (ghost spans y 118..518)
    draw_text(d, "WAITED 13 YEARS FOR GTA 6", 26, 56)
    draw_text(d, "MY AGENT GOT PAID ON MAKE.FUN", 596, 48)

    out = ASSETS / "meme.png"
    img.save(out, format="PNG")
    print(f"wrote {out} {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
