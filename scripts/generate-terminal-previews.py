#!/usr/bin/env python3
"""Render Nothing theme terminal preview PNGs using project palette."""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "assets"


def _hex(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


THEMES = {
    "nothing-dark-preview": {
        "bg": _hex("#090807"),
        "frame": _hex("#171412"),
        "shadow": _hex("#151311"),
        "titlebar_bg": _hex("#181614"),
        "titlebar_border": _hex("#3A3632"),
        "fg": _hex("#E5DDD0"),
        "muted": _hex("#5A5248"),
        "accent": _hex("#FF4719"),
        "blue": _hex("#4A8FD9"),
        "green": _hex("#5AB87A"),
        "cyan": _hex("#26C6C6"),
        "red": _hex("#D71921"),
        "yellow": _hex("#E8A030"),
        "magenta": _hex("#9575CD"),
        "bright": _hex("#FFFFFF"),
        "title": "nothing-dark · The Crucible",
    },
    "nothing-light-preview": {
        "bg": _hex("#FFFFFF"),
        "frame": _hex("#EDE9E5"),
        "shadow": _hex("#D9D5D1"),
        "titlebar_bg": _hex("#FFFFFF"),
        "titlebar_border": _hex("#E8E4DF"),
        "fg": _hex("#111111"),
        "muted": _hex("#6B6560"),
        "accent": _hex("#FF4719"),
        "blue": _hex("#1050A0"),
        "green": _hex("#1E6B3C"),
        "cyan": _hex("#006E6E"),
        "red": _hex("#C0000A"),
        "yellow": _hex("#7A4A00"),
        "magenta": _hex("#5A2D9A"),
        "bright": _hex("#000000"),
        "title": "nothing-light · The Steam",
    },
}


FONT_CANDIDATES = (
    os.environ.get("NOTHING_PREVIEW_FONT"),
    Path.home() / "Library/Fonts/JetBrainsMonoNerdFontMono-Regular.ttf",
    "/Library/Fonts/JetBrainsMonoNerdFontMono-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for cand in FONT_CANDIDATES:
        if not cand:
            continue
        p = Path(cand)
        if p.is_file():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def rounded_rect(
    draw: ImageDraw.ImageDraw,
    bbox: tuple[int, int, int, int],
    radius: int,
    fill,
    outline=None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)


def draw_terminal(pal: dict, font: ImageFont.FreeTypeFont, font_sm: ImageFont.FreeTypeFont) -> Image.Image:
    w, h = 1280, 720
    pad = 56
    ox, oy = pad + 22, pad + 16
    cw, ch = w - 2 * pad - 44, h - 2 * pad - 28
    rx = 18

    img = Image.new("RGB", (w, h), pal["frame"])
    draw = ImageDraw.Draw(img)

    shadow_off = 10
    rounded_rect(
        draw,
        (ox - shadow_off, oy + shadow_off, ox + cw + shadow_off, oy + ch + shadow_off),
        rx + 6,
        pal["shadow"],
        outline=None,
    )

    win_box = (ox, oy, ox + cw, oy + ch)
    rounded_rect(draw, win_box, rx, pal["bg"], outline=pal["titlebar_border"], width=2)

    title_h = 48
    rounded_rect(
        draw,
        (ox + 2, oy + 2, ox + cw - 2, oy + title_h - 2),
        max(10, rx - 4),
        pal["titlebar_bg"],
        outline=None,
    )

    dot_r = 6
    accent_x = ox + 20
    accent_y = oy + title_h // 2
    draw.ellipse(
        (accent_x - dot_r, accent_y - dot_r, accent_x + dot_r, accent_y + dot_r),
        fill=pal["accent"],
    )
    draw.text((accent_x + 22, oy + 12), pal["title"], font=font_sm, fill=pal["muted"])
    subtitle = "JetBrainsMono Nerd Font Mono · 24 pt"
    sub_w = int(draw.textlength(subtitle, font=font_sm))
    draw.text((ox + cw - sub_w - 18, oy + 12), subtitle, font=font_sm, fill=pal["muted"])

    body_x = ox + 36
    body_top = oy + title_h + 22
    lh = 30
    lh_code = 34
    cy = body_top

    def line(segments: list[tuple[str, tuple[int, int, int]]]) -> None:
        nonlocal cy
        x = body_x
        for text, rgb in segments:
            draw.text((x, cy), text, font=font, fill=rgb)
            x += int(draw.textlength(text, font=font))
        cy += lh

    def blank(extra: int = 8) -> None:
        nonlocal cy
        cy += extra

    m, fg = pal["muted"], pal["fg"]

    line(
        [
            ("~/Code/GH/nothing-theme", m),
            ("  ", fg),
            ("▌", pal["accent"]),
            ("  ", fg),
            ("make validate", fg),
        ]
    )
    line([("…  ", m), ("all theme checks passed", pal["green"])])

    blank(12)
    line(
        [
            ("drwxr-xr-x  ", m),
            ("nothing-theme", pal["blue"]),
            ("/", m),
        ]
    )
    line(
        [
            ("-rw-r--r--  ", m),
            ("Makefile", fg),
            ("    ", m),
            ("AGENTS.md", fg),
        ]
    )
    line(
        [
            ("lrwxr-xr-x  ", m),
            ("README.md", pal["cyan"]),
            ("  →  ", m),
            ("AGENTS.md", pal["cyan"]),
        ]
    )

    blank(14)
    line([("—" * 42, m)])
    blank(14)

    def code_line(segments: list[tuple[str, tuple[int, int, int]]]) -> None:
        nonlocal cy
        x = body_x
        for text, rgb in segments:
            draw.text((x, cy), text, font=font, fill=rgb)
            x += int(draw.textlength(text, font=font))
        cy += lh_code

    code_line(
        [
            ("import ", pal["cyan"]),
            ("{ ", m),
            ("Palette ", pal["magenta"]),
            ("} ", m),
            ("from ", m),
            ("'./warm-neutrals'", pal["green"]),
            (";", m),
        ]
    )
    comment = "// molten accent — sparingly"
    code_line(
        [
            ("const ", pal["red"]),
            ("ACCENT", fg),
            (" = ", m),
            ("0xFF4719", pal["yellow"]),
            (";  ", m),
            (comment, m),
        ]
    )

    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    font = load_font(22)
    font_sm = load_font(15)
    for slug, pal in THEMES.items():
        out = OUT_DIR / f"{slug}.png"
        img = draw_terminal(pal, font=font, font_sm=font_sm)
        img.save(out, format="PNG", optimize=True)
        print(f"wrote {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
