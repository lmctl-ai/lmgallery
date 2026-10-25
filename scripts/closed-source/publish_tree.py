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
TEMPLATE = GALLERY / "scripts/closed-source/templates/private-ci/lmaudio.yml"
PLACEHOLDERS = ("private implementation detail", "private build metadata", "private source repository",
                "pinned by `private", "recorded in `private", "TODO(publish)")
BOUNDARY_PREFIX = "Releases up to and including "


def latest_tag(product):
    """Return the latest published public tag. The tag decides the MIT boundary, so it is never assumed."""
    result = subprocess.run(["gh", "release", "list", "-R", f"lmctl-ai/{product}", "-L", "1", "--json", "tagName"],
                            capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"cannot read latest release of lmctl-ai/{product}: {result.stderr.strip()}")
    rows = json.loads(result.stdout or "[]")
    if not rows:
        raise SystemExit(f"lmctl-ai/{product} has no published release")
    return rows[0]["tagName"]


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


def split_fast_path(body):
    """Clone the first job with a matrix include into a Linux-only push job; the original runs on dispatch or tag."""
    jobs = list(re.finditer(r"^  ([A-Za-z0-9_-]+):\n", body, re.M))
    for i, job in enumerate(jobs):
        end = jobs[i + 1].start() if i + 1 < len(jobs) else len(body)
        block = body[job.start():end]
        inc = re.search(r"^      matrix:\n        include:\n((?:          .*\n)+)", block, re.M)
        if not inc:
            continue
        entries = inc.group(1).splitlines(keepends=True)
        linux = [e for e in entries if "linux-x64" in e]
        if not linux:
            raise SystemExit(f"job {job.group(1)}: no linux-x64 matrix entry for the push-time fast path")
        name = job.group(1)
        gate = "    if: github.event_name != 'push' || github.ref != 'refs/heads/main'\n"
        # Full matrix (dispatch or tag): add the gate to the original job.
        full = re.sub(r"^(  [A-Za-z0-9_-]+:\n)", lambda m: m.group(1) + gate, block, count=1, flags=re.M)
        fast = block.replace(f"  {name}:\n", f"  {name}-fast:\n", 1)
        fast = fast.replace(inc.group(1), "".join(linux), 1)
        fast_gate = "    if: github.event_name == 'push' && github.ref == 'refs/heads/main'\n"
        fast = re.sub(r"^(  [A-Za-z0-9_-]+:\n)", lambda m: m.group(1) + fast_gate, fast, count=1, flags=re.M)
        return body[:job.start()] + fast + full + body[end:]
    raise SystemExit("no job with a matrix include was found for the push-time fast path")


def generate_private_ci(source, product, out):
    """Transform the product's current ci.yml into a private workflow; fail closed on what is not transformed."""
    text = (Path(source) / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    lines = text.split("\n")
    # 1. Replace the top-level trigger block.
    start = lines.index("on:") if "on:" in lines else next(i for i, l in enumerate(lines) if l.startswith("on:"))
    end = next(i for i in range(start + 1, len(lines)) if lines[i] and not lines[i].startswith((" ", "#")))
    triggers = [
        "on:",
        "  push:",
        "    branches: [main]",
        "    tags: [\"v*\"]",
        "  workflow_dispatch:",
        "    inputs:",
        "      release_tag:",
        "        description: First/new public tag, for example v0.2.0",
        "        required: false",
        "        type: string",
        "      publish_test:",
        "        description: Verify the publishing token with a temporary draft release, without building",
        "        required: false",
        "        default: false",
        "        type: boolean",
        "",
    ]
    lines = lines[:start] + [f"# Generated for lmctlhq/{product} from the current ci.yml by publish_tree.py."] + triggers + lines[end:]
    body = "\n".join(lines)
    # 2. Remove the public release job (it publishes with GITHUB_TOKEN on every push to main).
    job = re.search(r"^  release:\n(?:    .*\n|\n)*?(?=^  \S|\Z)", body, re.M)
    if not job:
        raise SystemExit(f"{product}: no release job found in ci.yml; add a transform before generating")
    needs_match = re.search(r"^    needs: \[(.*)\]", job.group(0), re.M)
    if not needs_match:
        raise SystemExit(f"{product}: the release job has no needs list to carry over")
    # The publish job waits for the same matrix jobs the public release waited for (never version or audit).
    publish_needs = [n.strip() for n in needs_match.group(1).split(",") if n.strip() not in ("version", "audit")]
    body = body[:job.start()] + body[job.end():]
    # 3. Append the publish jobs from the reviewed template (RELEASE_TOKEN only).
    template = TEMPLATE.read_text(encoding="utf-8")
    publish = template[template.index("  publish-test:"):]
    publish = publish.replace("lmctl-ai/lmaudio", f"lmctl-ai/{product}")
    publish = publish.replace("needs: [full-matrix]", "needs: [" + ", ".join(publish_needs) + "]")
    publish = publish.replace("pattern: binary-*", f"pattern: {product}-*")
    body = body.rstrip("\n") + "\n\n" + publish
    # 4. Version from the tag: the public tag decides the binary's version, never the run number.
    version_expr = r"\$\(scripts/stamp-version\.sh --base\)\.\$\{?GITHUB_RUN_NUMBER\}?"
    body, count = re.subn(version_expr, "${PRIVATE_VERSION#v}", body)
    if count:
        version_env = ("  PRIVATE_VERSION: ${{ inputs.release_tag || (startsWith(github.ref, 'refs/tags/v') && github.ref_name) "
                       "|| 'v0.0.0-private-ci' }}")
        if re.search(r"^env:\n", body, re.M):
            body = re.sub(r"^env:\n", "env:\n" + version_env + "\n", body, count=1, flags=re.M)
        else:
            body = re.sub(r"^permissions:", "env:\n" + version_env + "\npermissions:", body, count=1, flags=re.M)
    # 5. Push to main runs one Linux job; the full matrix runs only on dispatch or a version tag.
    body = split_fast_path(body)
    # 6. Fail closed on constructs that still need a human decision.
    remaining = []
    if "GITHUB_RUN_NUMBER" in body:
        remaining.append("version derived from GITHUB_RUN_NUMBER: derive it from the tag instead")
    if re.search(r"gh release (create|upload|edit)", body) and "RELEASE_TOKEN" not in body:
        remaining.append("a release write uses a token other than RELEASE_TOKEN")
    if "release-to-public.sh" not in body:
        remaining.append("publish does not call release-to-public.sh")
    if remaining:
        raise SystemExit(f"{product}: manual edits required before the private CI can be generated: " + "; ".join(remaining))
    Path(out).write_text(body, encoding="utf-8", newline="\n")
    return remaining


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
