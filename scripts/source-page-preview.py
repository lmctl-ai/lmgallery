#!/usr/bin/env python3
"""Pair a source excerpt with a rendered page: the 900 px gallery picture for document compositions.

The left panel is a monospace excerpt of the composition (lines START to END, wrapped to the panel);
the right panel is the rendered first page (or slide) scaled to fit. Output is a deterministic PNG
on a 900 px canvas. Pass the page from scripts/render-office.py.

usage: scripts/source-page-preview.py SOURCE.lms START END PAGE.png OUT.png
"""
import argparse
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 900
PANEL_W = 430
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
SIZE = 13
LINE = 18
PAD = 16
BG = (248, 250, 252)
CODE_BG = (30, 41, 59)
CODE_FG = (226, 232, 240)
RULE = (203, 213, 225)


def excerpt_lines(source, start, end):
    lines = Path(source).read_text(encoding="utf-8").splitlines()
    if not 1 <= start <= end <= len(lines):
        raise SystemExit(f"bad line range {start}:{end} for {len(lines)} lines")
    wrapped = []
    for line in lines[start - 1:end]:
        wrapped.extend(textwrap.wrap(line, 48, break_long_words=False, replace_whitespace=False,
                                     drop_whitespace=False) or [""])
    return wrapped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.add_argument("page")
    parser.add_argument("out")
    args = parser.parse_args()
    font = ImageFont.truetype(FONT, SIZE)
    code = excerpt_lines(args.source, args.start, args.end)
    code_h = PAD * 2 + LINE * len(code)
    page = Image.open(args.page).convert("RGB")
    room_w, room_h = WIDTH - PANEL_W - 3 * PAD, 560
    scale = min(room_w / page.width, room_h / page.height)
    page = page.resize((round(page.width * scale), round(page.height * scale)), Image.LANCZOS)
    height = max(code_h, page.height + 2 * PAD) + PAD
    canvas = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((PAD, PAD, PANEL_W, PAD + code_h), radius=10, fill=CODE_BG)
    y = PAD + PAD
    for line in code:
        draw.text((PAD + PAD, y), line, font=font, fill=CODE_FG)
        y += LINE
    x = PANEL_W + PAD + (room_w - page.width) // 2 + PAD
    draw.rectangle((x - 1, PAD - 1, x + page.width, PAD + page.height), outline=RULE)
    canvas.paste(page, (x, PAD))
    canvas.save(args.out, optimize=True)
    print(f"wrote {args.out} ({canvas.width}x{canvas.height})")


if __name__ == "__main__":
    main()
