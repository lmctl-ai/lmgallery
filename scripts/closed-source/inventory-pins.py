#!/usr/bin/env python3
"""Grep local repositories for versioned installs and release URLs."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

PRODUCTS = ("lmdraw", "lmvideo", "lmaudio", "lmoffice", "lmcad", "lmblender", "lmmagnum", "lmfilament", "lmimg", "lmpdf")
ROOTS = ("/home/mma/repos/dsl", "/home/mma/repos/lmctlhq")


def grep(product: str) -> list[str]:
    pattern = (
        rf"github:lmctl-ai/{re.escape(product)}@v[0-9]+\.[0-9]+\.[0-9]+"
        rf"|github\.com/lmctl-ai/{re.escape(product)}/releases/(download|tag)/v[0-9]+\.[0-9]+\.[0-9]+"
    )
    result = subprocess.run(
        ["rg", "--no-messages", "--hidden", "-n", "-g", "!**/.git/**", "-g", "!**/build/**",
         "-g", "!**/target/**", "-g", "!**/node_modules/**", "-g", "!**/.venv/**", "-g", "!**/.omx/**",
         "-g", "!**/closed-source-pin-inventory.md", pattern, *ROOTS],
        text=True, capture_output=True, check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip())
    return sorted(set(line for line in result.stdout.splitlines() if line.strip()))


def render() -> str:
    out = [
        "# Closed-source consumer tag-pin inventory",
        "",
        f"Grep snapshot: {date.today().isoformat()}. This is a local-repository inventory from `/home/mma/repos/dsl` and `/home/mma/repos/lmctlhq`, excluding `.git`, build, target, node_modules, and virtualenv trees. It includes versioned `install=github:lmctl-ai/<product>@vX.Y.Z` pins and release tag/download links; `@latest` references are intentionally excluded.",
        "",
        "| Product | Matches | Action before flip |",
        "| --- | ---: | --- |",
    ]
    sections: list[str] = []
    for product in PRODUCTS:
        matches = grep(product)
        action = "update to the first new public release tag" if matches else "none found in scanned local repos"
        out.append(f"| `{product}` | {len(matches)} | {action} |")
        sections.extend(["", f"## {product}", ""])
        if matches:
            for line in matches:
                match = re.match(r"(.+?):([0-9]+):(.*)$", line)
                if match:
                    sections.append(f"- `{match.group(1)}:{match.group(2)}` — `{match.group(3).strip()}`")
                else:
                    sections.append(f"- `{line}`")
        else:
            sections.append("- No versioned install or release URL found in the scanned local trees.")
    out.extend(["", "## Matches by product", *sections])
    out.extend(["", "A pin can be changed only after the first public release tag is known and published. The flip runner records this inventory during staging; before apply it must re-scan and ensure consumers can be updated without overwriting dirty or actively edited checkouts.", ""])
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    document = render()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(document, encoding="utf-8")
    else:
        sys.stdout.write(document)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
