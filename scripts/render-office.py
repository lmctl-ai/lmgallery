#!/usr/bin/env python3
"""Render a generated Office document to one 900 px wide PNG (the gallery picture).

The document is converted to PDF by LibreOffice (headless), each page is rasterized by
PyMuPDF at a fixed DPI, the white margins are cropped, and the result is scaled to 900 px.
Slides and sheets can be tiled into a montage. Rendering is deterministic on one machine.

usage: scripts/render-office.py SOURCE OUT.png [--pages first|all] [--cols N] [--dpi N]
"""
import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pymupdf
from PIL import Image, ImageChops

WIDTH = 900
GAP = 14
TILE_BACKGROUND = (226, 232, 240)


def find_soffice():
    candidates = [
        os.environ.get("LMGALLERY_SOFFICE"),
        str(Path.home() / "tools/libreoffice/opt/libreoffice26.2/program/soffice"),
        shutil.which("soffice"),
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    raise SystemExit("LibreOffice soffice not found; set LMGALLERY_SOFFICE")


def convert_to_pdf(source, workdir):
    subprocess.run([find_soffice(), "--headless", "--norestore", "--convert-to", "pdf",
                    "--outdir", workdir, str(source)], check=True, timeout=600,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = Path(workdir) / (Path(source).stem + ".pdf")
    if not pdf.is_file():
        raise SystemExit(f"LibreOffice did not produce {pdf}")
    return pdf


def rasterize(pdf, dpi):
    pages = []
    with pymupdf.open(pdf) as document:
        for page in document:
            pixmap = page.get_pixmap(dpi=dpi, alpha=False)
            pages.append(Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples))
    return pages


def crop_margins(image, padding=18):
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, (255, 255, 255))
    box = ImageChops.difference(rgb, background).getbbox()
    if not box:
        return rgb
    left, top = max(0, box[0] - padding), max(0, box[1] - padding)
    right, bottom = min(rgb.width, box[2] + padding), min(rgb.height, box[3] + padding)
    return rgb.crop((left, top, right, bottom))


def montage(pages, columns):
    tiles = [crop_margins(page) for page in pages]
    tile_width = max(tile.width for tile in tiles)
    tile_height = max(tile.height for tile in tiles)
    rows = (len(tiles) + columns - 1) // columns
    width = columns * tile_width + (columns + 1) * GAP
    height = rows * tile_height + (rows + 1) * GAP
    canvas = Image.new("RGB", (width, height), TILE_BACKGROUND)
    for index, tile in enumerate(tiles):
        x = GAP + (index % columns) * (tile_width + GAP) + (tile_width - tile.width) // 2
        y = GAP + (index // columns) * (tile_height + GAP) + (tile_height - tile.height) // 2
        canvas.paste(tile, (x, y))
    return canvas


def to_gallery_width(image):
    height = round(image.height * WIDTH / image.width)
    return image.resize((WIDTH, height), Image.LANCZOS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--pages", choices=["first", "all"], default="first")
    parser.add_argument("--cols", type=int, default=3, help="columns for --pages all")
    parser.add_argument("--dpi", type=int, default=110)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="render-office-") as workdir:
        pages = rasterize(convert_to_pdf(args.source, workdir), args.dpi)
    if not pages:
        raise SystemExit(f"no pages rendered from {args.source}")
    if args.pages == "first":
        image = crop_margins(pages[0])
    else:
        image = montage(pages, args.cols)
    to_gallery_width(image).save(args.out, optimize=True)
    print(f"wrote {args.out} from {len(pages)} page(s)")


if __name__ == "__main__":
    main()
