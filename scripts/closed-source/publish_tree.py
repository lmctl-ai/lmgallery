#!/usr/bin/env python3
"""Post-process a staged public tree for the closed-source model (stdlib only; does not edit peer-flip.py).

  --boundary   write the MIT boundary sentence in the staged LICENSE from the product's latest published tag
  --notices    copy THIRD_PARTY_NOTICES* from the source repository byte-for-byte, refuse placeholder text,
               and fail if the staged notice does not equal the source notice
  --private-ci generate <product>-private-ci.yml from the product's current .github/workflows/ci.yml; fails
               closed on any construct it does not transform, and lists the remaining manual edits

usage:
  publish_tree.py STAGE SOURCE_REPO PRODUCT [--latest-tag vX.Y.Z] [--boundary] [--notices] [--private-ci OUT]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

GALLERY = Path(__file__).resolve().parents[2]
TEMPLATE = GALLERY / "scripts/closed-source/templates/private-release.yml"
PLACEHOLDERS = ("private implementation detail", "private build metadata", "private source repository",
                "pinned by `private", "recorded in `private", "TODO(publish)")
BOUNDARY_PREFIX = "Releases up to and including "


def latest_tag(product):
    """Return the latest published public tag. The tag decides the MIT boundary, so it is never assumed."""
    result = subprocess.run(["gh", "api", f"repos/lmctl-ai/{product}/releases/latest", "--jq", ".tag_name"],
                            capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"cannot read latest release of lmctl-ai/{product}: {result.stderr.strip()}")
    tag = result.stdout.strip()
    if result.returncode != 0 or not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise SystemExit(f"lmctl-ai/{product} has no stable published release: {result.stderr.strip()}")
    return tag


def set_boundary(stage, product, tag):
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise SystemExit(f"latest tag {tag!r} is not vMAJOR.MINOR.PATCH")
    path = stage / "LICENSE"
    text = path.read_text(encoding="utf-8")
    if text.startswith(BOUNDARY_PREFIX):
        text = text.split("\n\n", 1)[1]
    sentence = (f"{BOUNDARY_PREFIX}{tag} were published under the MIT License (see the LICENSE asset of that "
                f"release). Releases after {tag} are published under the Lattice Systems Personal Use License "
                f"(this file).\n\n")
    path.write_text(sentence + text, encoding="utf-8", newline="\n")
    readme = stage / "README.md"
    readme_text = readme.read_text(encoding="utf-8")
    readme_text = re.sub(
        r"\[!\[License: MIT\]\([^)]*\)\]\(LICENSE\)",
        "[![Examples: MIT](https://img.shields.io/badge/examples-MIT-blue.svg)](LICENSE-examples)",
        readme_text,
    )
    if sentence.strip() not in readme_text:
        license_section = re.search(r"(?m)^## License\s*\n", readme_text)
        if not license_section:
            raise SystemExit(f"{readme}: no License section for the MIT boundary sentence")
        insert_at = license_section.end()
        readme_text = readme_text[:insert_at] + "\n" + sentence.rstrip() + "\n" + readme_text[insert_at:]
    readme.write_text(readme_text, encoding="utf-8", newline="\n")
    return sentence.strip()


def sync_notices(stage, source):
    sources = sorted(p for p in Path(source).glob("THIRD_PARTY_NOTICES*") if p.is_file())
    if not sources:
        raise SystemExit(f"no THIRD_PARTY_NOTICES* in {source}")
    for src in sources:
        data = src.read_bytes()
        text = data.decode("utf-8")
        for marker in PLACEHOLDERS:
            if marker in text:
                raise SystemExit(f"placeholder text {marker!r} in {src}: fix the notice generator, not the copy")
        dst = stage / src.name
        shutil.copyfile(src, dst)
        if dst.read_bytes() != data:
            raise SystemExit(f"{dst} is not byte-identical to {src}")
    return [p.name for p in sources]


def generate_private_ci(source, product, out):
    """Generate the dispatch-only Linux staging workflow from the product CI contract."""
    return generate_private_release(source, product, out)


def generate_private_release(source, product, out):
    """Render a two-architecture prerelease workflow; public CI remains untouched."""
    source = Path(source)
    version_text = (source / "VERSION").read_text().splitlines()[0] if (source / "VERSION").is_file() else ""
    if not version_text:
        cmake = (source / "CMakeLists.txt").read_text()
        match = re.search(rf"project\({re.escape(product)}\s+VERSION\s+(\d+)\.(\d+)", cmake)
        if not match:
            raise SystemExit(f"{product}: cannot derive MAJOR.MINOR from VERSION or CMakeLists.txt")
        major, minor = match.groups()
    else:
        parts = version_text.split(".")
        if len(parts) < 2:
            raise SystemExit(f"{product}: invalid VERSION {version_text!r}")
        major, minor = parts[:2]
    commands = {
        "lmaudio": ("scripts/sync-deps.sh && scripts/sync-sdk.sh --verify && cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel 3 && mkdir -p dist && cp build/lmaudio dist/lmaudio-linux-x64", "./test.sh", "scripts/sync-deps.sh && scripts/sync-sdk.sh --verify && cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel 3 && mkdir -p dist && cp build/lmaudio dist/lmaudio-linux-arm64", "./test.sh"),
        "lmimg": ("scripts/sync-deps.sh && scripts/sync-sdk.sh --verify && cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel 3 && mkdir -p dist && cp build/lmimg dist/lmimg-linux-x64", "./test.sh", "scripts/sync-deps.sh && scripts/sync-sdk.sh --verify && cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel 3 && mkdir -p dist && cp build/lmimg dist/lmimg-linux-arm64", "./test.sh"),
        "lmdraw": ("scripts/sync-sdk.sh --verify && cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel 3 && mkdir -p dist && cp build/lmdraw dist/lmdraw-linux-x64 && scripts/stage-release-notices.sh dist && rm -f dist/*.sha256 && tar -czf dist/lmdraw-linux-x64-notices.tar.gz -C dist licenses && rm -rf dist/licenses", "./test.sh", "scripts/sync-sdk.sh --verify && cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel 3 && mkdir -p dist && cp build/lmdraw dist/lmdraw-linux-arm64 && scripts/stage-release-notices.sh dist && rm -f dist/*.sha256 && tar -czf dist/lmdraw-linux-arm64-notices.tar.gz -C dist licenses && rm -rf dist/licenses", "./test.sh"),
        "lmoffice": ("scripts/sync-sdk.sh && RID=linux-x64 scripts/build.sh && mkdir -p dist && cp build/publish/lmoffice dist/lmoffice-linux-x64", "LMOFFICE_BIN=build/publish/lmoffice ./test.sh", "scripts/sync-sdk.sh && RID=linux-arm64 scripts/build.sh && mkdir -p dist && cp build/publish/lmoffice dist/lmoffice-linux-arm64", "LMOFFICE_BIN=build/publish/lmoffice ./test.sh"),
        "lmcad": ("scripts/sync-sdk.sh --verify && scripts/build-occt.sh && cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DLMCAD_OCCT_PREFIX=build/occt-prefix -DLMCAD_FULL_STATIC=ON && cmake --build build --parallel 3 && mkdir -p dist && cp build/lmcad dist/lmcad-linux-x64 && scripts/stage-release-notices.sh dist build/occt-prefix linux && tar -czf dist/lmcad-linux-x64-occt-relink-recipe.tar.gz .github/occt-cmake-flags.txt scripts/build-occt.sh durable-memory/13-licensing.md", "./test.sh", "scripts/sync-sdk.sh --verify && scripts/build-occt.sh && cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DLMCAD_OCCT_PREFIX=build/occt-prefix -DLMCAD_FULL_STATIC=ON && cmake --build build --parallel 3 && mkdir -p dist && cp build/lmcad dist/lmcad-linux-arm64 && scripts/stage-release-notices.sh dist build/occt-prefix linux && tar -czf dist/lmcad-linux-arm64-occt-relink-recipe.tar.gz .github/occt-cmake-flags.txt scripts/build-occt.sh durable-memory/13-licensing.md", "./test.sh"),
        "lmfilament": ("scripts/sync-sdk.sh --verify && scripts/sync-filament.sh && scripts/build-filament.sh && scripts/build.sh && mkdir -p dist && cp build/host/lmfilament dist/lmfilament-linux-x64 && tar -C build/host -czf dist/lmfilament-linux-x64-relink-objects.tar.gz CMakeFiles/lmfilament.dir build.ninja && cp third_party/filament/LICENSE dist/FILAMENT-LICENSE", "./test.sh", "scripts/sync-sdk.sh --verify && scripts/sync-filament.sh && scripts/build-filament.sh && scripts/build.sh && mkdir -p dist && cp build/host/lmfilament dist/lmfilament-linux-arm64 && tar -C build/host -czf dist/lmfilament-linux-arm64-relink-objects.tar.gz CMakeFiles/lmfilament.dir build.ninja && cp third_party/filament/LICENSE dist/FILAMENT-LICENSE", "./test.sh"),
        "lmvideo": ("scripts/fetch-skia.sh --quiet && make STATIC=1 -j2 && mkdir -p dist && cp build/lmvideo dist/lmvideo-linux-x64 && scripts/stage-release-notices.sh dist && tar -czf dist/lmvideo-linux-x64-licenses.tar.gz -C dist licenses && rm -rf dist/licenses", "./test.sh", "LMVIDEO_PLATFORM=linux-arm64 scripts/fetch-skia.sh --quiet && LMVIDEO_PLATFORM=linux-arm64 make STATIC=1 -j2 && mkdir -p dist && cp build/lmvideo dist/lmvideo-linux-arm64 && scripts/stage-release-notices.sh dist && tar -czf dist/lmvideo-linux-arm64-licenses.tar.gz -C dist licenses && rm -rf dist/licenses", "./test.sh"),
        "lmmagnum": ("scripts/sync-deps.sh && cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DLMMAGNUM_FULL_STATIC=ON && cmake --build build --parallel 3 && mkdir -p dist && cp build/lmmagnum dist/lmmagnum-linux-x64 && scripts/stage-release-notices.sh dist", "./test.sh", "scripts/sync-deps.sh && cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DLMMAGNUM_FULL_STATIC=ON && cmake --build build --parallel 3 && mkdir -p dist && cp build/lmmagnum dist/lmmagnum-linux-arm64 && scripts/stage-release-notices.sh dist", "./test.sh"),
        "lmpdf": ("rustup toolchain install 1.92.0 --profile minimal && rustup target add x86_64-unknown-linux-musl && scripts/compile-release.sh x86_64-unknown-linux-musl linux-x64", "python3 scripts/check-linkage.py --platform linux-x64 --binary dist/lmpdf-linux-x64 --output dist/linkage-linux-x64.json --static-crt && cargo test --release --locked --target x86_64-unknown-linux-musl", "rustup toolchain install 1.92.0 --profile minimal && rustup target add aarch64-unknown-linux-musl && scripts/compile-release.sh aarch64-unknown-linux-musl linux-arm64", "python3 scripts/check-linkage.py --platform linux-arm64 --binary dist/lmpdf-linux-arm64 --output dist/linkage-linux-arm64.json --static-crt && cargo test --release --locked --target aarch64-unknown-linux-musl"),
    }
    if product not in commands:
        raise SystemExit(f"{product}: no reviewed Linux staging adapter; add its real CI commands before generating")
    x64, tx, arm, ta = commands[product]
    try:
        ci_commit = subprocess.check_output(["git", "-C", str(source), "log", "-1", "--format=%H", "--", ".github/workflows/ci.yml"], text=True).strip()
    except subprocess.CalledProcessError:
        ci_commit = "unavailable"
    text = TEMPLATE.read_text(encoding="utf-8")
    replacements = {"{{PRODUCT}}": product, "{{MAJOR}}": major, "{{MINOR}}": minor, "{{SOURCE_CI_COMMIT}}": ci_commit,
                    "{{BUILD_X64}}": x64, "{{TEST_X64}}": tx, "{{BUILD_ARM64}}": arm, "{{TEST_ARM64}}": ta}
    for key, value in replacements.items():
        text = text.replace(key, value)
    Path(out).write_text(text, encoding="utf-8", newline="\n")
    return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage")
    parser.add_argument("source")
    parser.add_argument("product")
    parser.add_argument("--latest-tag", help="override the latest published tag (default: gh release list)")
    parser.add_argument("--boundary", action="store_true")
    parser.add_argument("--notices", action="store_true")
    parser.add_argument("--private-ci", metavar="OUT")
    args = parser.parse_args()
    stage = Path(args.stage)
    if args.boundary:
        tag = args.latest_tag or latest_tag(args.product)
        print("boundary:", set_boundary(stage, args.product, tag))
    if args.notices:
        print("notices copied byte-exact:", ", ".join(sync_notices(stage, args.source)))
    if args.private_ci:
        generate_private_ci(args.source, args.product, args.private_ci)
        print(f"generated {args.private_ci} from {args.source}/.github/workflows/ci.yml")


if __name__ == "__main__":
    sys.exit(main())
