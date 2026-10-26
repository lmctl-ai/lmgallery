#!/usr/bin/env python3
"""Dependency-free checks for the published gallery, its images and links."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import struct
import time
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
import zlib

ROOT = Path(__file__).resolve().parents[1]
HOSTS = set("lmplot lmnum lmfinance lmspace lmphysics lmbio lmfluid lmmolecule lmcell lmparticle lmweather lmdraw lmcad lmblender lmimg lmaudio".split())
RAW = "https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/"


def png_info(path):
    data = Path(path).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"not a PNG: {path}"
    assert len(data) <= 300_000, f"image exceeds 300 KB: {path}"
    pos, header, compressed, ended = 8, None, bytearray(), False
    while pos < len(data):
        assert pos + 12 <= len(data), f"truncated PNG: {path}"
        size = struct.unpack_from(">I", data, pos)[0]
        kind = data[pos + 4:pos + 8]
        end = pos + 8 + size
        assert end + 4 <= len(data), f"truncated chunk: {path}"
        body = data[pos + 8:end]
        assert zlib.crc32(kind + body) & 0xffffffff == struct.unpack_from(">I", data, end)[0], f"bad PNG CRC: {path}"
        if kind == b"IHDR":
            assert header is None and pos == 8 and size == 13, f"invalid IHDR: {path}"
            header = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            compressed.extend(body)
        elif kind == b"IEND":
            assert size == 0 and end + 4 == len(data), f"invalid IEND: {path}"
            ended = True
        pos = end + 4
    assert header and ended and compressed, f"incomplete PNG: {path}"
    width, height, depth, color, compression, filtering, interlace = header
    assert 600 <= width <= 1200 and 200 <= height <= 1200, f"unexpected preview dimensions: {path}"
    assert compression == filtering == interlace == 0, f"unsupported PNG encoding: {path}"
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    stride = (width * channels * depth + 7) // 8
    raw = zlib.decompress(compressed)
    assert len(raw) == height * (stride + 1), f"invalid decoded PNG length: {path}"
    assert all(raw[y * (stride + 1)] <= 4 for y in range(height)), f"invalid row filter: {path}"
    return width, height


def preview_info(path):
    if Path(path).suffix != ".gif":
        return png_info(path)
    data = Path(path).read_bytes()
    assert data[:6] in (b"GIF87a", b"GIF89a") and data[-1:] == b";", f"invalid GIF: {path}"
    assert len(data) <= 3_000_000, f"animation exceeds 3 MB: {path}"
    width, height = struct.unpack_from("<HH", data, 6)
    assert 600 <= width <= 1200 and 200 <= height <= 1200, f"unexpected GIF dimensions: {path}"
    return width, height


def showcase_width_ok(path):
    """Composition previews are 900 px wide; animated GIFs may be narrower to stay under the size budget."""
    width = preview_info(path)[0]
    return width == 900 if Path(path).suffix == ".png" else 600 <= width <= 900


class HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for name, value in attrs if name in ("href", "src") and value)


def document_links(path):
    text = path.read_text()
    parser = HTMLLinks()
    parser.feed(text)
    links = parser.links + re.findall(r"!?\[[^\]]*\]\(([^\s)]+)\)", text)
    links += re.findall(r"https://raw\.githubusercontent\.com/[^\s<`]+", text)
    return links


def local_target(path, link):
    target = (path.parent / unquote(urlsplit(link).path)).resolve()
    assert target.is_relative_to(ROOT), f"link escapes repository: {path}: {link}"
    assert target.exists(), f"broken local link: {path.relative_to(ROOT)}: {link}"


def check_http(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url, method="HEAD", headers={"User-Agent": "lmgallery-link-check/1.0"}), timeout=30) as response:
                assert 200 <= response.status < 400, (url, response.status)
            return
        except (HTTPError, URLError, TimeoutError) as error:
            if attempt == 2:
                raise AssertionError(f"HTTP link failed: {url}: {error}") from error
            time.sleep(2 ** (attempt + 1))


def check(network=False):
    hosts = json.loads((ROOT / "catalog.json").read_text())
    examples = json.loads((ROOT / "showcases.json").read_text())
    assert {h["name"] for h in hosts} == HOSTS and len(hosts) == len(HOSTS), "host catalog mismatch"
    assert len(examples) >= 14, "expected at least 14 cross-host examples"
    assert len({e["file"] for e in examples}) == len(examples), "duplicate script"
    assert {str(p.relative_to(ROOT)) for p in (ROOT / "examples").glob("*.lms")} == {e["file"] for e in examples}, "unlisted or missing script"
    images = []
    for h in hosts:
        image = ROOT / h["image"]
        preview_info(image)
        assert hashlib.sha256(image.read_bytes()).hexdigest() == h["sha256"], f"copied image changed: {image}"
        assert h["attribution"] and h["source_image"].startswith("docs/images/"), "missing attribution"
        images.append(h["image"])
    readme = (ROOT / "README.md").read_text()
    for e in examples:
        source = (ROOT / e["file"]).read_text()
        assert "SPDX-License-Identifier: MIT" in source, f"missing script license: {e['file']}"
        # One composition generates a second self-executing LMS program from
        # computed data. Its quoted bindings still belong in the host inventory.
        bindings = source.replace('\\"', '"')
        bound = set(re.findall(r'cli="([a-z]+)(?: [a-z]+)?"', bindings))
        assert len(bound) >= 2 and bound == set(e["hosts"]), f"host chain mismatch: {e['file']}"
        for host in bound:
            assert f'install="github:lmctl-ai/{host}@' in bindings, f"missing install binding: {host}"
        assert 'schema="' not in source and "../" not in source, f"checkout-dependent script: {e['file']}"
        assert "savedsl(" in source and "dsl_cli(" in source and "system" in source, f"compile-only script: {e['file']}"
        assert e["output"].startswith("images/") and e["output"] in source, f"invalid output: {e['file']}"
        assert Path(e["output"]).suffix == Path(e["image"]).suffix, f"preview format differs from output: {e['file']}"
        assert f'lmctl autorun {RAW}{e["file"]}' in readme, f"missing autorun caption: {e['file']}"
        assert showcase_width_ok(ROOT / e["image"]), f"showcase must be 900px wide (animations 600–900): {e['image']}"
        images.append(e["image"])
    assert len(set(images)) == len(images), "duplicate image destination"
    assert {str(p.relative_to(ROOT)) for p in (ROOT / "docs/images").iterdir() if p.suffix in (".png", ".gif")} == set(images), "unlisted or missing preview"
    remote = set()
    for path in [ROOT / "README.md", ROOT / "examples/README.md", ROOT / "docs/ATTRIBUTION.md", ROOT / "durable-memory/README.md"]:
        for link in document_links(path):
            if link.startswith("https://"):
                remote.add(link)
            elif not link.startswith("#"):
                local_target(path, link)
    print(f"PASS: {len(hosts)} attributed host previews, {len(examples)} cross-host scripts, {len(images)} valid PNG/GIF previews and all local links")
    if network:
        planned = [h["repo"] for h in hosts if not h["repo_available"]]
        checked, skipped = 0, 0
        for url in sorted(remote):
            if os.environ.get("GITHUB_EVENT_NAME") == "pull_request" and url.startswith(RAW):
                print(f"SKIP not-yet-published PR URL (local file checked): {url}")
                skipped += 1
                continue
            if any(url == prefix or url.startswith(prefix + "/") for prefix in planned):
                print(f"SKIP planned upstream publication: {url}")
                skipped += 1
                continue
            check_http(url)
            checked += 1
        print(f"PASS: {checked} published HTTP links; {skipped} explicitly reported skips")
    else:
        print("SKIP: HTTP availability checks; run ./test.sh --network")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", action="store_true")
    args = parser.parse_args()
    check(args.network)

