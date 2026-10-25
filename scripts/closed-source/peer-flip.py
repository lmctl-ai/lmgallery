#!/usr/bin/env python3
"""Inventory and stage source repos as public docs/examples peers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

PRODUCTS = ("lmdraw", "lmvideo", "lmaudio", "lmoffice", "lmcad", "lmmagnum", "lmfilament", "lmimg", "lmpdf")
PRODUCT_ROOTS = {
    "lmdraw": Path("/home/mma/repos/dsl/lmdraw"),
    "lmvideo": Path("/home/mma/repos/lmctlhq/lmvideo"),
    "lmaudio": Path("/home/mma/repos/dsl/lmaudio"),
    "lmoffice": Path("/home/mma/repos/dsl/lmoffice"),
    "lmcad": Path("/home/mma/repos/dsl/lmcad"),
    "lmmagnum": Path("/home/mma/repos/dsl/lmmagnum"),
    "lmfilament": Path("/home/mma/repos/dsl/lmfilament"),
    "lmimg": Path("/home/mma/repos/dsl/lmimg"),
    "lmpdf": Path("/home/mma/repos/dsl/lmpdf"),
}
STAGING = Path("/home/mma/staging/closed-source")
GALLERY = Path("/home/mma/repos/dsl/lmgallery")
OWNER_REPORTED_ACTIVE = {"lmvideo", "lmoffice", "lmpdf"}
PRIVATE_ROOTS = {"cpp", "src", "schema", "tests", "scripts", "tools", "durable-memory", ".github", "build", "third_party", "target"}
PRIVATE_FILES = {"CMakeLists.txt", "Cargo.toml", "Makefile", "BUILD.md", "deps.lock", "sdk.lock", "package.json", "Cargo.lock"}
INPUT_SUFFIXES = {".csv", ".json", ".txt", ".wav", ".mp3", ".png", ".jpg", ".jpeg", ".svg", ".html", ".md", ".ttf", ".webp", ".zip", ".stl", ".obj", ".mtl", ".glb", ".gltf", ".mp4", ".gif", ".xml", ".pdf"}
PUBLIC_TEXT_SUFFIXES = {".md", ".lms", ".txt", ".json", ".svg", ".html", ".xml", ".yml", ".yaml", ".toml"}
DATA_LITERAL = re.compile(r"[\"']([^\"']+\.(?:csv|json|txt|wav|mp3|png|jpe?g|svg|html|md|ttf|webp|zip|stl|obj|mtl|glb|gltf|mp4|gif|xml|pdf))[\"']", re.I)
MD_LINK = re.compile(r"(?P<image>!)?\[(?P<label>[^\]]*)\]\((?P<target>[^)\s]+)(?P<tail>[^)]*)\)")
HTML_SRC = re.compile(r"(?P<left>\bsrc=[\"'])(?P<target>[^\"']+)(?P<right>[\"'])", re.I)
RAW_AUTORUN = re.compile(r"lmctl\s+autorun\s+(https?://[^\s`<>]+)", re.I)
PRIVATE_TOKEN = re.compile(r"(?<![A-Za-z0-9])(?:\.\.?/)*(?:cpp|src|schema|tests|scripts|durable-memory|\.github|build|third_party|target)/[A-Za-z0-9_.\-/]+", re.I)
TOKEN_PATTERNS = (
    re.compile(r"gh[pousr]_[a-z0-9]{30,}", re.I),
    re.compile(r"github_pat_[a-z0-9_]{30,}", re.I),
    re.compile(r"akia[a-z0-9]{16}", re.I),
    re.compile(r"-----begin [a-z ]*private key-----", re.I),
    re.compile(r"(api[_-]?key|access[_-]?token|client[_-]?secret|password)[\"']?\s*[:=]\s*[\"'][a-z0-9_./+=-]{20,}[\"']", re.I),
)


class FlipError(RuntimeError):
    pass


def public_repo(product: str) -> str:
    return f"lmctl-ai/{product}"


def private_repo(product: str) -> str:
    return f"lmctlhq/{product}"


def command(argv: list[str], *, cwd: Path | None = None, check: bool = True,
            timeout: int = 300, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=timeout, input=input_text)
    if check and proc.returncode:
        raise FlipError(f"command failed ({proc.returncode}): {' '.join(argv)}\n{proc.stderr.strip()}")
    return proc


def git_snapshot(product: str, *, fetch: bool = False) -> dict:
    root = PRODUCT_ROOTS[product]
    if not root.is_dir():
        raise FlipError(f"source checkout is missing: {root}")
    if fetch:
        command(["git", "-C", str(root), "fetch", "-q", "origin", "main"], timeout=300)
    origin = command(["git", "-C", str(root), "remote", "get-url", "origin"]).stdout.strip()
    local_head = command(["git", "-C", str(root), "rev-parse", "HEAD"]).stdout.strip()
    local_branch = command(["git", "-C", str(root), "branch", "--show-current"]).stdout.strip()
    status = command(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"]).stdout.strip()
    ref_result = command(["git", "-C", str(root), "rev-parse", "origin/main"], check=False)
    ref = ref_result.stdout.strip() if ref_result.returncode == 0 else ""
    if not ref:
        remote = command(["git", "ls-remote", origin, "refs/heads/main"], check=False)
        ref = remote.stdout.split()[0] if remote.stdout.strip() else ""
    if not ref:
        raise FlipError(f"cannot determine main revision for {product}")
    files = command(["git", "-C", str(root), "ls-tree", "-r", "--name-only", ref]).stdout.splitlines()
    return {
        "root": root,
        "origin": origin,
        "local_head": local_head,
        "local_branch": local_branch,
        "status": status,
        "ref": ref,
        "files": files,
        "clean": not status,
        "pushed": local_head == ref,
    }


def active_lmctl_members() -> list[str]:
    result = command(["lmctl", "running"], check=False, timeout=60)
    if result.returncode != 0:
        return ["lmctl running unavailable: " + result.stderr.strip()]
    members: list[str] = []
    running = True
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("idle,"):
            running = False
        if running and ".lmctl:" in stripped:
            members.append(stripped.split()[0])
    return members


def agents_for(product: str, members: list[str]) -> list[str]:
    return [member for member in members if member.lower().startswith(product.lower() + ".lmctl:")]


def ci_latest(product: str, sha: str) -> dict:
    result = command(["gh", "run", "list", "-R", f"lmctl-ai/{product}", "-L", "1", "--json", "status,conclusion,displayTitle,headSha,url"], check=False, timeout=120)
    if result.returncode != 0:
        return {"ok": False, "error": result.stderr.strip(), "status": "unknown", "conclusion": ""}
    try:
        rows = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid gh run list JSON", "status": "unknown", "conclusion": ""}
    if not rows:
        return {"ok": False, "error": "no Actions run found", "status": "unknown", "conclusion": ""}
    row = rows[0]
    row["ok"] = row.get("status") == "completed" and row.get("conclusion") == "success" and row.get("headSha") == sha
    return row


def pin_inventory(product: str) -> list[str]:
    pattern = rf"github:lmctl-ai/{re.escape(product)}@v[0-9]+\.[0-9]+\.[0-9]+|github\.com/lmctl-ai/{re.escape(product)}/releases/(download|tag)/v[0-9]+\.[0-9]+\.[0-9]+"
    result = command([
        "rg", "--no-messages", "--hidden", "-n", "-g", "!**/.git/**", "-g", "!**/build/**",
        "-g", "!**/target/**", "-g", "!**/node_modules/**", "-g", "!**/.venv/**", "-g", "!**/.omx/**",
        "-g", "!**/closed-source-pin-inventory.md", "-g", "!**/closed-source-staging-inventory.md",
        pattern, "/home/mma/repos/dsl", "/home/mma/repos/lmctlhq",
    ], check=False, timeout=180)
    if result.returncode not in (0, 1):
        raise FlipError(f"rg pin scan failed for {product}: {result.stderr.strip()}")
    return sorted(set(line for line in result.stdout.splitlines() if line.strip()))


def private_ci_adapter(product: str) -> Path:
    if product == "lmaudio":
        return GALLERY / "scripts/closed-source/templates/private-ci/lmaudio.yml"
    return GALLERY / "scripts/closed-source/adapters" / f"{product}-private-ci.yml"


def rewrite_product_tags(text: str, product: str, first_tag: str) -> str:
    install = re.compile(rf"(github:lmctl-ai/{re.escape(product)}@)v[0-9]+\.[0-9]+\.[0-9]+")
    release_url = re.compile(rf"(github\.com/lmctl-ai/{re.escape(product)}/releases/(?:download|tag)/)v[0-9]+\.[0-9]+\.[0-9]+")
    lines: list[str] = []
    for line in text.splitlines(keepends=True):
        line = install.sub(rf"\g<1>{first_tag}", line)
        if release_url.search(line):
            line = release_url.sub(rf"\g<1>{first_tag}", line)
            line = re.sub(r"\bv[0-9]+\.[0-9]+\.[0-9]+\b", first_tag, line)
        lines.append(line)
    return "".join(lines)


def rewrite_stage_product_tags(stage: Path, product: str, first_tag: str) -> None:
    for path in stage.rglob("*"):
        if path.is_file() and path.suffix.lower() in PUBLIC_TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="ignore")
            updated = rewrite_product_tags(text, product, first_tag)
            if updated != text:
                path.write_text(updated, encoding="utf-8")


def source_files(product: str, ref: str) -> list[str]:
    return command(["git", "-C", str(PRODUCT_ROOTS[product]), "ls-tree", "-r", "--name-only", ref]).stdout.splitlines()


def map_public_path(path: str) -> str | None:
    if path == "README.md" or path.startswith("docs/") or path.startswith("examples/"):
        return path
    if path.startswith("images/"):
        return "docs/" + path
    if path.startswith("img/"):
        return "docs/images/" + path[len("img/"):]
    if path.startswith("presets/"):
        return "docs/" + path
    if path.startswith("licenses/"):
        return "docs/third-party-licenses/" + path[len("licenses/"):]
    if path.startswith("THIRD_PARTY_NOTICES"):
        return path
    if path.startswith("assets/fonts/") and Path(path).name.lower().startswith(("license", "ofl", "copyright", "notice")):
        return "docs/third-party-licenses/assets/fonts/" + path[len("assets/fonts/"):]
    return None


def discover_inputs(product: str, ref: str, files: set[str], mapping: dict[str, str]) -> dict[str, str]:
    extra: dict[str, str] = {}
    root = PRODUCT_ROOTS[product]
    for script in sorted(p for p in files if p.startswith("examples/") and p.endswith(".lms")):
        content = command(["git", "-C", str(root), "show", f"{ref}:{script}"]).stdout
        for raw in DATA_LITERAL.findall(content):
            if "://" in raw or raw.startswith(("build/", "images/")):
                continue
            candidates = [posixpath.normpath(raw.lstrip("./"))]
            candidates.append(posixpath.normpath(posixpath.join(posixpath.dirname(script), raw)))
            for candidate in candidates:
                if candidate in files and candidate not in mapping and PurePosixPath(candidate).suffix.lower() in INPUT_SUFFIXES:
                    root_part = PurePosixPath(candidate).parts[0]
                    if root_part in PRIVATE_ROOTS:
                        continue
                    extra[candidate] = "examples/_inputs/" + candidate
                    break
    return extra


def safe_extract(tar_path: Path, stage: Path) -> None:
    with tarfile.open(tar_path, "r:") as tf:
        members = tf.getmembers()
        for member in members:
            p = PurePosixPath(member.name)
            if p.is_absolute() or ".." in p.parts:
                raise FlipError(f"unsafe archived path: {member.name}")
            resolved = (stage / Path(*p.parts)).resolve()
            if not resolved.is_relative_to(stage.resolve()):
                raise FlipError(f"archived path escapes staged tree: {member.name}")
            if member.issym() or member.islnk():
                target = (resolved.parent / member.linkname).resolve()
                if not target.is_relative_to(stage.resolve()):
                    raise FlipError(f"archive link escapes staged tree: {member.name}")
        for member in members:
            tf.extract(member, stage)


def archive_paths(mapping: dict[str, str], extra_inputs: dict[str, str]) -> list[str]:
    return sorted(set(mapping) | set(extra_inputs))


def move_mapped_files(stage: Path, mapping: dict[str, str], extra_inputs: dict[str, str]) -> None:
    all_mappings = {**mapping, **extra_inputs}
    for source, target in sorted(all_mappings.items()):
        if source == target or source == "README.md" or source.startswith("docs/") or source.startswith("examples/") or source.startswith("THIRD_PARTY_NOTICES"):
            continue
        src = stage / source
        if not src.exists():
            continue
        dst = stage / target
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            if dst.is_file() and src.is_file() and dst.read_bytes() == src.read_bytes():
                src.unlink()
                continue
            raise FlipError(f"public tree mapping collision: {source} -> {target}")
        shutil.move(str(src), str(dst))
    for directory in (stage / "images", stage / "licenses", stage / "assets"):
        if directory.exists():
            shutil.rmtree(directory)
    # Rewrite any staged example input paths that came from outside examples/.
    for source, target in extra_inputs.items():
        for example in (stage / "examples").rglob("*.lms"):
            text = example.read_text(encoding="utf-8")
            text = text.replace(f'"{source}"', f'"{target}"').replace(f"'{source}'", f"'{target}'")
            example.write_text(text, encoding="utf-8")


def _rewrite_target(markdown_path: str, raw_target: str, mapping: dict[str, str], public_paths: set[str], product: str) -> tuple[str | None, bool]:
    parsed = urlsplit(raw_target)
    if parsed.scheme or raw_target.startswith("//"):
        if parsed.netloc.lower() in {"github.com", "www.github.com", "raw.githubusercontent.com"}:
            parts = [p for p in parsed.path.split("/") if p]
            if len(parts) >= 2 and parts[0] in {"lmctl-ai", "lmctlhq"} and parts[1] in {product, "lmctl"}:
                if "raw.githubusercontent.com" in parsed.netloc:
                    parts = parts[3:]
                elif len(parts) >= 4 and parts[2] in {"blob", "tree"}:
                    parts = parts[4:]
                if parts and (parts[0] in PRIVATE_ROOTS or parts[0] == "reference"):
                    return None, True
        return raw_target, False
    path = unquote(parsed.path)
    if not path:
        return raw_target, False
    source_target = posixpath.normpath(posixpath.join(posixpath.dirname(markdown_path), path))
    if source_target == "LICENSE":
        dest = "LICENSE-examples"
    elif source_target in mapping:
        dest = mapping[source_target]
    elif source_target.startswith("licenses/"):
        dest = "docs/third-party-licenses/" + source_target[len("licenses/"):]
    elif source_target.startswith("images/"):
        dest = "docs/" + source_target
    elif source_target.split("/", 1)[0] in PRIVATE_ROOTS or PurePosixPath(source_target).name in PRIVATE_FILES:
        return None, True
    elif source_target not in public_paths:
        return None, True
    else:
        dest = source_target
    parent = posixpath.dirname(markdown_path) or "."
    relative = posixpath.relpath(dest, parent)
    suffix = ("?" + parsed.query if parsed.query else "") + ("#" + parsed.fragment if parsed.fragment else "")
    return relative + suffix, False


def sanitize_markdown(path: str, text: str, mapping: dict[str, str], public_paths: set[str], product: str) -> tuple[str, list[str]]:
    problems: list[str] = []
    text = text.replace("actions/workflows/ci.yml", "actions/workflows/public-ci.yml")

    def md_replace(match: re.Match[str]) -> str:
        image = match.group("image") or ""
        label = match.group("label")
        target, private = _rewrite_target(path, match.group("target"), mapping, public_paths, product)
        if private:
            problems.append(match.group("target"))
            return label
        if target is None:
            return label
        return f"{image}[{label}]({target}{match.group('tail')})"

    text = MD_LINK.sub(md_replace, text)

    def html_replace(match: re.Match[str]) -> str:
        target, private = _rewrite_target(path, match.group("target"), mapping, public_paths, product)
        if private or target is None:
            problems.append(match.group("target"))
            return ""
        return match.group("left") + target + match.group("right")

    text = HTML_SRC.sub(html_replace, text)
    private_repo_url = re.compile(
        rf"https?://github\.com/(?:lmctl-ai|lmctlhq)/(?:{re.escape(product)}|lmctl)/(?:blob|tree)/[^/]+/(?:cpp|src|schema|tests|scripts|durable-memory|\.github|build|third_party|target)/[^\s<>]+",
        re.I,
    )
    text = private_repo_url.sub("private implementation reference omitted", text)
    text = strip_private_paths_preserving_urls(text)
    text = re.sub(r"(?i)\bCMakeLists\.txt\b|\bCargo\.toml\b|\bCargo\.lock\b|\bdeps\.lock\b|\bsdk\.lock\b", "private build metadata", text)
    return text, problems


def strip_private_paths_preserving_urls(text: str) -> str:
    urls: list[str] = []

    def hold(match: re.Match[str]) -> str:
        urls.append(match.group(0))
        return f"\x00URL{len(urls) - 1}\x00"

    text = re.sub(r"https?://[^\s<>]+", hold, text)
    text = PRIVATE_TOKEN.sub("private implementation detail", text)
    for index, url in enumerate(urls):
        text = text.replace(f"\x00URL{index}\x00", url)
    return text


def replace_readme_sections(text: str, product: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    skip_level: int | None = None
    skip_heading = re.compile(r"^(build from source|source build|development|developer guide|tests and validation|known answers it is tested against)$", re.I)
    license_heading = re.compile(r"^(#{1,3})\s+licen[cs]e\b.*$", re.I)
    for line in lines:
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if skip_level is not None:
            if heading and len(heading.group(1)) <= skip_level:
                skip_level = None
            else:
                continue
        if heading:
            title = heading.group(2).strip()
            if skip_heading.fullmatch(title):
                skip_level = len(heading.group(1))
                continue
            if license_heading.match(line):
                skip_level = len(license_heading.match(line).group(1))
                out.extend([
                    "## License", "",
                    "The README, docs, images, and `examples/*.lms` are MIT-licensed under `LICENSE-examples`.",
                    "Binary releases are licensed under `LICENSE`. Third-party components remain under their own licenses and notices.",
                    "",
                ])
                continue
        out.append(line)
    result = "\n".join(out).rstrip()
    if not re.search(r"(?im)^##\s+License\b", result):
        result += "\n\n## License\n\nThe README, docs, images, and `examples/*.lms` are MIT-licensed under `LICENSE-examples`.\nBinary releases are licensed under `LICENSE`. Third-party components remain under their own licenses and notices."
    result += "\n"
    note = (
        f"\n> The public README, docs, images, and examples for `{product}` are MIT under `LICENSE-examples`. "
        f"Binary releases use `LICENSE`; implementation source and its history are maintained privately in `lmctlhq/{product}`.\n"
    )
    match = re.search(r"^#\s+[^\n]+\n", result, re.M)
    if match and "implementation source and its history" not in result:
        result = result[:match.end()] + note + result[match.end():]
    return result


def scan_secrets(stage: Path, files: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in files:
        name = path.name.lower()
        rel = path.relative_to(stage).as_posix()
        if name == ".env" or name.startswith(".env.") or name.endswith((".pem", ".p12", ".pfx")) or "credentials" in name or "private-key" in name:
            findings.append(rel + " (sensitive filename)")
            continue
        if path.suffix.lower() not in PUBLIC_TEXT_SUFFIXES and path.name not in {"LICENSE", "LICENSE-examples"} and not path.name.startswith("THIRD_PARTY_NOTICES"):
            continue
        try:
            data = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        if any(pattern.search(data) for pattern in TOKEN_PATTERNS):
            findings.append(rel)
    return findings


def validate_stage(product: str, stage: Path, mapping: dict[str, str]) -> dict:
    files = sorted(p for p in stage.rglob("*") if p.is_file())
    public_paths = {p.relative_to(stage).as_posix() for p in files}
    link_findings: list[str] = []
    for path in files:
        if path.suffix.lower() not in {".md", ".html", ".svg"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in MD_LINK.finditer(text):
            target = match.group("target")
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("//") or not parsed.path:
                continue
            local = posixpath.normpath(posixpath.join(posixpath.dirname(path.relative_to(stage).as_posix()), unquote(parsed.path)))
            if local not in public_paths and not (stage / local).exists() and not local.startswith("#"):
                link_findings.append(f"{path.relative_to(stage).as_posix()} -> {target}")
    readme = (stage / "README.md").read_text(encoding="utf-8")
    autorun_targets: list[str] = []
    missing_autorun: list[str] = []
    for raw_url in RAW_AUTORUN.findall(readme):
        parsed = urlsplit(raw_url.rstrip(",.;)"))
        parts = [part for part in parsed.path.split("/") if part]
        if parsed.netloc != "raw.githubusercontent.com" or len(parts) < 4:
            missing_autorun.append(raw_url)
            continue
        # Cross-product demo links remain at their own public hosts; only
        # this product's raw paths must exist in the staged tree.
        if parts[0] != "lmctl-ai" or parts[1] != product:
            continue
        target = "/".join(parts[3:])
        autorun_targets.append(target)
        if target not in public_paths:
            missing_autorun.append(target)
    private_refs: list[str] = []
    for path in files:
        if path.suffix.lower() not in {".md", ".html", ".svg"} and not path.name.startswith("THIRD_PARTY_NOTICES"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        scan_text = re.sub(r"https?://[^\s<>]+", "", text)
        for match in PRIVATE_TOKEN.finditer(scan_text):
            private_refs.append(f"{path.relative_to(stage).as_posix()}:{scan_text.count(chr(10), 0, match.start()) + 1}:{match.group(0)}")
    secrets = scan_secrets(stage, files)
    allowed = {"README.md", "docs", "examples", ".github", "LICENSE", "LICENSE-examples"}
    allowed.update(name for name in {p.name for p in files} if name.startswith("THIRD_PARTY_NOTICES"))
    unapproved_top = sorted(p.name for p in stage.iterdir() if p.name not in allowed)
    report = {
        "files": len(files),
        "top_level": sorted(p.name for p in stage.iterdir()),
        "raw_autorun_count": len(autorun_targets),
        "raw_autorun_ok": len(autorun_targets) - len(missing_autorun),
        "missing_autorun": missing_autorun,
        "broken_local_links": link_findings,
        "private_source_references": private_refs,
        "secret_findings": secrets,
        "unapproved_top_level": unapproved_top,
    }
    if missing_autorun or link_findings or private_refs or secrets or unapproved_top:
        raise FlipError("public tree validation failed: " + json.dumps(report, indent=2))
    return report


def stage_product(product: str, snapshot: dict, *, refresh: bool = False,
                  active_members: list[str] | None = None, ci: dict | None = None,
                  pins: list[str] | None = None) -> dict:
    stage = STAGING / f"{product}-public"
    manifest_path = STAGING / f"{product}-stage-manifest.json"
    if stage.exists() or manifest_path.exists():
        if not refresh or not stage.is_dir() or not manifest_path.is_file():
            raise FlipError(f"staging path already exists; inspect before overwrite: {stage}")
        try:
            previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise FlipError(f"cannot verify existing stage manifest: {manifest_path}") from exc
        if previous.get("product") != product or previous.get("staging_tree") != str(stage):
            raise FlipError(f"existing stage manifest does not own this path: {manifest_path}")
        if (stage / ".git").exists():
            raise FlipError(f"refusing to refresh a tree that has already been initialized for a public push: {stage}")
        expected_hashes = previous.get("staged_file_sha256")
        if not isinstance(expected_hashes, dict):
            raise FlipError(f"existing stage has no content-hash manifest; refusing to overwrite it: {stage}")
        actual_hashes = {p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in stage.rglob("*") if p.is_file()}
        if actual_hashes != expected_hashes:
            raise FlipError(f"staged files were changed since the manifest; inspect before refresh: {stage}")
        shutil.rmtree(stage)
        manifest_path.unlink()
    STAGING.mkdir(parents=True, exist_ok=True)
    mapping = {path: mapped for path in snapshot["files"] if (mapped := map_public_path(path)) is not None}
    inputs = discover_inputs(product, snapshot["ref"], set(snapshot["files"]), mapping)
    mapping.update(inputs)
    selected = sorted(mapping)
    stage.mkdir()
    try:
        with tempfile.TemporaryDirectory(prefix=f"{product}-archive-") as tmp:
            tar_path = Path(tmp) / "public.tar"
            command(["git", "-C", str(snapshot["root"]), "archive", "--format=tar", "-o", str(tar_path), snapshot["ref"], "--", *selected])
            with tarfile.open(tar_path, "r:") as archive:
                members = archive.getmembers()
                for member in members:
                    p = PurePosixPath(member.name)
                    if p.is_absolute() or ".." in p.parts:
                        raise FlipError(f"unsafe path in archive: {member.name}")
                for member in members:
                    archive.extract(member, stage)
        for source, target in sorted(mapping.items()):
            if source == target or source == "README.md" or source.startswith("docs/") or source.startswith("examples/") or source.startswith("THIRD_PARTY_NOTICES"):
                continue
            src = stage / source
            if not src.exists():
                continue
            dst = stage / target
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                if dst.is_file() and src.is_file() and dst.read_bytes() == src.read_bytes():
                    src.unlink()
                    continue
                raise FlipError(f"staged path collision: {source} -> {target}")
            shutil.move(str(src), str(dst))
        if product == "lmvideo":
            alias = stage / "examples/confusion_matrix.lms"
            canonical = stage / "examples/confusion-matrix.lms"
            if not alias.exists() and canonical.is_file():
                shutil.copyfile(canonical, alias)
        for directory in (stage / "images", stage / "img", stage / "licenses", stage / "assets", stage / "presets"):
            if directory.exists():
                shutil.rmtree(directory)
        files = sorted(p for p in stage.rglob("*") if p.is_file())
        for path in files:
            rel = path.relative_to(stage).as_posix()
            if path.suffix.lower() not in {".md", ".html", ".svg"} and not path.name.startswith("THIRD_PARTY_NOTICES"):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            text, _ = sanitize_markdown(rel, text, mapping, {p.relative_to(stage).as_posix() for p in files}, product)
            if rel == "README.md":
                text = replace_readme_sections(text, product)
            path.write_text(text, encoding="utf-8")
        # Notices may be extensionless; update links to relocated full license texts.
        for path in stage.glob("THIRD_PARTY_NOTICES*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="ignore")
                text = strip_private_paths_preserving_urls(text)
                text = re.sub(r"(?<!third-party-)licenses/", "docs/third-party-licenses/", text)
                text = text.replace("Source: LICENSE", "Source: LICENSE-examples")
                text = text.replace("see LICENSE.", "see LICENSE-examples.")
                path.write_text(text, encoding="utf-8")
        shutil.copyfile(GALLERY / "scripts/closed-source/templates/LICENSE-binaries.md", stage / "LICENSE")
        shutil.copyfile(GALLERY / "scripts/closed-source/templates/LICENSE-examples-MIT", stage / "LICENSE-examples")
        workflow = stage / ".github/workflows/public-ci.yml"
        workflow.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(GALLERY / "scripts/closed-source/templates/public-ci.yml", workflow)
        # Re-run the README sanitizer after inserting the standard license files.
        readme = stage / "README.md"
        text = readme.read_text(encoding="utf-8")
        text, _ = sanitize_markdown("README.md", text, mapping, {p.relative_to(stage).as_posix() for p in stage.rglob("*") if p.is_file()}, product)
        text = replace_readme_sections(text, product)
        readme.write_text(text, encoding="utf-8")
        report = validate_stage(product, stage, mapping)
        manifest = {
            "product": product,
            "source_root": str(snapshot["root"]),
            "source_origin": snapshot["origin"],
            "source_main_sha": snapshot["ref"],
            "local_head": snapshot["local_head"],
            "local_worktree_clean": snapshot["clean"],
            "local_branch_pushed": snapshot["pushed"],
            "active_lmctl_members": active_members or [],
            "owner_reported_active_team": product in OWNER_REPORTED_ACTIVE,
            "latest_main_ci": ci or {},
            "consumer_version_pins": pins or [],
            "staging_tree": str(stage),
            "public_file_map": mapping,
            "validation": report,
            "staged_file_sha256": {
                p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in stage.rglob("*") if p.is_file()
            },
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return manifest
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def run_dry_or_stage(product: str, stage: bool, refresh: bool = False) -> int:
    snap = git_snapshot(product, fetch=True)
    members = active_lmctl_members()
    agents = agents_for(product, members)
    ci = ci_latest(product, snap["ref"])
    pins = pin_inventory(product)
    mapping = {p: mapped for p in snap["files"] if (mapped := map_public_path(p)) is not None}
    inputs = discover_inputs(product, snap["ref"], set(snap["files"]), mapping)
    mapping.update(inputs)
    stage_path = STAGING / f"{product}-public"
    print(f"Product: {product}")
    print(f"Source repo: {snap['root']} ({snap['origin']})")
    print(f"Staging commit: {snap['ref']}")
    print(f"Local HEAD: {snap['local_head']} (clean={snap['clean']}, pushed={snap['pushed']})")
    print(f"Active lmctl sessions tagged for product: {', '.join(agents) if agents else 'none'}")
    if product in OWNER_REPORTED_ACTIVE:
        print("Owner-reported active team: quiesce and re-check before any flip.")
    print(f"Latest public-main CI: {ci.get('status','unavailable')}/{ci.get('conclusion','')} {ci.get('url','')}")
    print(f"Public tree path: {stage_path} ({len(mapping)} selected source files before generated license/CI templates)")
    print(f"External example inputs staged under examples/_inputs: {', '.join(inputs) if inputs else 'none detected by literal path scan'}")
    print(f"Pinned release consumers found: {len(pins)}")
    for pin in pins:
        print(f"  {pin}")
    if stage:
        manifest = stage_product(product, snap, refresh=refresh, active_members=agents, ci=ci, pins=pins)
        report = manifest["validation"]
        print(f"STAGED {report['files']} files at {stage_path} from {snap['ref']}")
        print(f"README raw autorun links: {report['raw_autorun_ok']}/{report['raw_autorun_count']}; private references: {len(report['private_source_references'])}; secret findings: {len(report['secret_findings'])}")
    else:
        if stage_path.exists():
            print("Stage directory already exists; refusing to overwrite it.")
        else:
            print("Dry-run only. Add --stage to write this tree locally; no GitHub operation or source checkout edit occurs.")
    return 0


def consumer_repositories(product: str) -> tuple[list[str], dict[str, list[str]]]:
    matches = pin_inventory(product)
    files: dict[str, list[str]] = {}
    source_root = PRODUCT_ROOTS[product].resolve()
    for line in matches:
        m = re.match(r"(.+?):[0-9]+:", line)
        if not m:
            continue
        path = Path(m.group(1))
        repo_result = command(["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"], check=False)
        if repo_result.returncode:
            continue
        root = Path(repo_result.stdout.strip()).resolve()
        rel = path.resolve().relative_to(root).as_posix()
        files.setdefault(str(root), []).append(rel)
    return matches, files


def validate_consumer_checkouts(product: str, roots: list[str], active_members: list[str]) -> None:
    for root_text in roots:
        root = Path(root_text)
        name = root.name
        if root.resolve() == PRODUCT_ROOTS[product].resolve():
            continue
        if agents_for(name, active_members):
            raise FlipError(f"consumer repo {name} has an active lmctl session; quiesce before flip")
        status = command(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"]).stdout.strip()
        if status:
            raise FlipError(f"consumer repo {root} is dirty; do not overwrite it")
        branch = command(["git", "-C", str(root), "branch", "--show-current"]).stdout.strip()
        if branch != "main":
            raise FlipError(f"consumer repo {root} is not on main")
        command(["git", "-C", str(root), "fetch", "-q", "origin", "main"], timeout=300)
        head = command(["git", "-C", str(root), "rev-parse", "HEAD"]).stdout.strip()
        remote = command(["git", "-C", str(root), "rev-parse", "origin/main"]).stdout.strip()
        if head != remote:
            raise FlipError(f"consumer repo {root} is not synchronized with origin/main")


def rewrite_consumer_file(path: Path, product: str, first_tag: str) -> bool:
    text = path.read_text(encoding="utf-8")
    changed = False
    install_re = re.compile(rf"(github:lmctl-ai/{re.escape(product)}@)v[0-9]+\.[0-9]+\.[0-9]+")
    release_re = re.compile(rf"(github\.com/lmctl-ai/{re.escape(product)}/releases/(?:download|tag)/)v[0-9]+\.[0-9]+\.[0-9]+")
    lines = []
    for line in text.splitlines(keepends=True):
        original = line
        line = install_re.sub(rf"\g<1>{first_tag}", line)
        if release_re.search(line):
            line = release_re.sub(rf"\g<1>{first_tag}", line)
            # Update the adjacent version label in release-link rows as well.
            line = re.sub(r"\bv[0-9]+\.[0-9]+\.[0-9]+\b", first_tag, line)
        if line != original:
            changed = True
        lines.append(line)
    if changed:
        path.write_text("".join(lines), encoding="utf-8")
    return changed


def update_consumer_pins(product: str, first_tag: str, pinned_files: dict[str, list[str]]) -> list[str]:
    updated_roots: list[str] = []
    for root_text, files in pinned_files.items():
        root = Path(root_text)
        changed: list[str] = []
        for rel in sorted(set(files)):
            path = root / rel
            if path.is_file() and rewrite_consumer_file(path, product, first_tag):
                changed.append(rel)
        if not changed:
            continue
        command(["git", "-C", str(root), "pull", "--rebase"], timeout=300)
        command(["git", "-C", str(root), "add", "--", *changed])
        command([
            "git", "-C", str(root), "-c", "user.name=mike-lmctl",
            "-c", "user.email=281311770+mike-lmctl@users.noreply.github.com",
            "commit", "-m", f"Point {product} consumers at the first public release",
            "-m", f"Update versioned install/release references to {first_tag} after the public history reset.",
        ])
        command(["git", "-C", str(root), "pull", "--rebase"], timeout=300)
        command(["git", "-C", str(root), "push", "origin", "main"], timeout=600)
        updated_roots.append(str(root))
    return updated_roots


def _repo_view(product: str) -> dict:
    return json.loads(command(["gh", "api", f"repos/{public_repo(product)}"]).stdout)


def _check_private_target_free(product: str) -> None:
    target = command(["gh", "api", f"repos/{private_repo(product)}"], check=False)
    if target.returncode == 0:
        raise FlipError(f"private target {private_repo(product)} already exists; stop for owner review")
    response = (target.stdout + target.stderr).lower()
    if "404" not in response and "not found" not in response:
        raise FlipError(f"cannot verify private target availability for {private_repo(product)}: {response.strip()}")


def _wait_for_private_transfer(product: str, attempts: int = 30) -> dict:
    last_error = ""
    for _ in range(attempts):
        result = command(["gh", "api", f"repos/{private_repo(product)}"], check=False, timeout=60)
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                last_error = "invalid repo JSON"
        else:
            last_error = result.stderr.strip()
        time.sleep(4)
    raise FlipError(f"transferred repo did not appear under {private_repo(product)}: {last_error}")


def _create_public_peer(product: str, metadata: dict, stage: Path) -> None:
    args = ["gh", "repo", "create", public_repo(product), "--public"]
    if metadata.get("description"):
        args.extend(["--description", metadata["description"]])
    if metadata.get("homepage"):
        args.extend(["--homepage", metadata["homepage"]])
    command(args)
    git_dir = stage / ".git"
    if git_dir.exists():
        raise FlipError(f"staging tree already contains Git history: {stage}")
    command(["git", "-C", str(stage), "init", "-b", "main"])
    command(["git", "-C", str(stage), "-c", "user.name=mike-lmctl", "-c", "user.email=281311770+mike-lmctl@users.noreply.github.com", "add", "-A"])
    command([
        "git", "-C", str(stage), "-c", "user.name=mike-lmctl",
        "-c", "user.email=281311770+mike-lmctl@users.noreply.github.com",
        "commit", "-m", f"Publish {product} docs, examples, and binary license",
    ])
    command(["git", "-C", str(stage), "remote", "add", "origin", f"https://github.com/{public_repo(product)}.git"])
    command(["git", "-C", str(stage), "push", "-u", "origin", "main"], timeout=900)
    edit = ["gh", "repo", "edit", public_repo(product), "--default-branch", "main", "--enable-issues", "--enable-wiki=false", "--enable-projects=false"]
    command(edit)
    for topic in metadata.get("topics", []):
        command(["gh", "repo", "edit", public_repo(product), "--add-topic", topic])


def _update_local_checkouts(product: str, root: Path) -> None:
    command(["git", "-C", str(root), "remote", "set-url", "origin", f"https://github.com/{private_repo(product)}.git"])
    command(["git", "-C", str(root), "pull", "--rebase"], timeout=600)
    public_checkout = Path("/home/mma/repos/dsl") / f"{product}-public"
    if public_checkout.exists():
        raise FlipError(f"public local checkout already exists: {public_checkout}")
    public_checkout.parent.mkdir(parents=True, exist_ok=True)
    command(["git", "clone", f"https://github.com/{public_repo(product)}.git", str(public_checkout)], timeout=900)


def _install_private_ci(product: str, root: Path, first_tag: str) -> str:
    adapter = GALLERY / "scripts/closed-source/adapters" / f"{product}-private-ci.yml"
    if product == "lmaudio":
        adapter = GALLERY / "scripts/closed-source/templates/private-ci/lmaudio.yml"
    if not adapter.is_file():
        raise FlipError(f"no tested product-specific private CI adapter exists yet: {adapter}; stage is ready but do not flip")
    command(["git", "-C", str(root), "pull", "--rebase"], timeout=600)
    workflow = root / ".github/workflows/ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(adapter, workflow)
    publisher_template = GALLERY / "scripts/closed-source/templates/release-to-public.sh"
    publisher = root / "scripts/release-to-public.sh"
    publisher.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(publisher_template, publisher)
    publisher.chmod(0o755)
    durable = root / "durable-memory/20-public-private-peers.md"
    durable.write_text(
        f"# Public/private peer deployment\n\nThe source repository is private at `{private_repo(product)}`. The public peer `{public_repo(product)}` owns README, docs/images, examples/inputs, notices, and binary releases. The first public release tag is `{first_tag}`. Public source history was replaced by one orphan docs/examples commit; old source history remains private. CI checks public examples against this source build. Releases through `v0.2.1` remain MIT under that release's LICENSE asset; later releases use the Personal Use License in the public root LICENSE.\n",
        encoding="utf-8",
    )
    command(["git", "-C", str(root), "add", ".github/workflows/ci.yml", "scripts/release-to-public.sh", "durable-memory/20-public-private-peers.md"])
    command([
        "git", "-C", str(root), "-c", "user.name=mike-lmctl", "-c", "user.email=281311770+mike-lmctl@users.noreply.github.com",
        "commit", "-m", "Install private peer publishing workflow [skip ci]",
        "-m", f"Use Linux-fast default checks, full tagged/manual matrix builds, public example tests, and publish {first_tag} through the public peer.",
    ])
    command(["git", "-C", str(root), "pull", "--rebase"], timeout=600)
    command(["git", "-C", str(root), "push", "origin", "main"], timeout=900)
    return command(["git", "-C", str(root), "rev-parse", "HEAD"]).stdout.strip()


def _run_publish_test(product: str, private_sha: str) -> dict:
    before = command(["gh", "run", "list", "-R", private_repo(product), "-L", "5", "--json", "databaseId,event,headSha"], timeout=120)
    previous_ids = {str(row.get("databaseId")) for row in json.loads(before.stdout)}
    command(["gh", "workflow", "run", "ci.yml", "-R", private_repo(product), "--ref", "main", "-f", "publish_test=true"], timeout=300)
    run: dict = {}
    for _ in range(24):
        result = command(["gh", "run", "list", "-R", private_repo(product), "-L", "5", "--json", "databaseId,event,status,conclusion,headSha,url"], check=False, timeout=120)
        if result.returncode == 0:
            try:
                rows = json.loads(result.stdout)
            except json.JSONDecodeError:
                rows = []
            run = next((row for row in rows if str(row.get("databaseId")) not in previous_ids and row.get("event") == "workflow_dispatch" and row.get("headSha") == private_sha), {})
            if run:
                break
        time.sleep(2)
    if not run:
        raise FlipError(f"publish-test workflow run was not found for {private_repo(product)}")
    watched = command(["gh", "run", "watch", str(run["databaseId"]), "-R", private_repo(product), "--exit-status"], check=False, timeout=1800)
    details = json.loads(command(["gh", "run", "view", str(run["databaseId"]), "-R", private_repo(product), "--json", "status,conclusion,jobs,url"]).stdout)
    jobs = {job.get("name"): job for job in details.get("jobs", [])}
    if watched.returncode != 0 or details.get("status") != "completed" or details.get("conclusion") != "success":
        raise FlipError(f"private publish-test failed: {details.get('url','')}")
    if jobs.get("publish-test", {}).get("conclusion") != "success":
        raise FlipError(f"private publish-test job did not succeed: {details.get('url','')}")
    for name in ("linux-fast", "full-matrix", "publish"):
        if name in jobs and jobs[name].get("conclusion") != "skipped":
            raise FlipError(f"publish-test unexpectedly ran build/publish job {name}: {details.get('url','')}")
    return details


def _update_consumer_pins(product: str, first_tag: str, inventory: list[str], source_root: Path) -> list[str]:
    file_map: dict[Path, set[str]] = {}
    for line in inventory:
        match = re.match(r"(.+?):([0-9]+):(.*)$", line)
        if not match:
            continue
        path = Path(match.group(1))
        if not path.is_file():
            continue
        root = Path(command(["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"]).stdout.strip()).resolve()
        if root == source_root.resolve():
            continue
        file_map.setdefault(root, set()).add(path.resolve().relative_to(root).as_posix())
    updated: list[str] = []
    version = first_tag
    install_re = re.compile(rf"(github:lmctl-ai/{re.escape(product)}@)v[0-9]+\.[0-9]+\.[0-9]+")
    release_re = re.compile(rf"(github\.com/lmctl-ai/{re.escape(product)}/releases/(?:download|tag)/)v[0-9]+\.[0-9]+\.[0-9]+")
    for root, files in file_map.items():
        status = command(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"]).stdout.strip()
        if status:
            raise FlipError(f"consumer repo is dirty after release; pin update needs review: {root}")
        command(["git", "-C", str(root), "pull", "--rebase"], timeout=600)
        status = command(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"]).stdout.strip()
        if status:
            raise FlipError(f"consumer repo became dirty while synchronizing: {root}")
        changed: list[str] = []
        for rel in sorted(files):
            path = root / rel
            text = path.read_text(encoding="utf-8")
            out_lines = []
            for line in text.splitlines(keepends=True):
                original = line
                line = install_re.sub(rf"\g<1>{version}", line)
                if release_re.search(line):
                    line = release_re.sub(rf"\g<1>{version}", line)
                    line = re.sub(r"\bv[0-9]+\.[0-9]+\.[0-9]+\b", version, line)
                out_lines.append(line)
            updated_text = "".join(out_lines)
            if updated_text != text:
                path.write_text(updated_text, encoding="utf-8")
                changed.append(rel)
        if changed:
            command(["git", "-C", str(root), "add", "--", *changed])
            command([
                "git", "-C", str(root), "-c", "user.name=mike-lmctl", "-c", "user.email=281311770+mike-lmctl@users.noreply.github.com",
                "commit", "-m", f"Point {product} consumers at {first_tag}",
            ])
            command(["git", "-C", str(root), "pull", "--rebase"], timeout=600)
            command(["git", "-C", str(root), "push", "origin", "main"], timeout=900)
            updated.append(str(root))
    return updated


def _set_release_secret_from_file(product: str) -> None:
    token_path = Path.home() / ".config/lmctl/release_token"
    if not token_path.is_file() or token_path.stat().st_mode & 0o777 != 0o600 or token_path.stat().st_size == 0:
        raise FlipError("release-token file is missing, empty, or not mode 600; no token value was read")
    with token_path.open("rb") as stream:
        result = subprocess.run(["gh", "secret", "set", "RELEASE_TOKEN", "-R", private_repo(product)], stdin=stream, capture_output=True, text=True)
    if result.returncode:
        raise FlipError(f"could not set the private release secret: {result.stderr.strip()}")


def _prepare_orphan_commit(stage: Path, product: str) -> None:
    if (stage / ".git").exists():
        raise FlipError("public stage already has Git history; refusing to reuse it")
    command(["git", "-C", str(stage), "init", "-b", "main"])
    command(["git", "-C", str(stage), "-c", "user.name=mike-lmctl", "-c", "user.email=281311770+mike-lmctl@users.noreply.github.com", "add", "-A"])
    command(["git", "-C", str(stage), "-c", "user.name=mike-lmctl", "-c", "user.email=281311770+mike-lmctl@users.noreply.github.com", "commit", "-m", f"Publish {product} public documentation and examples"])
    parents = command(["git", "-C", str(stage), "rev-list", "--parents", "-n", "1", "HEAD"]).stdout.strip().split()
    if len(parents) != 1:
        raise FlipError("staged public commit is not an orphan root commit")


def _release_files(product: str, release_dir: Path, first_tag: str) -> tuple[dict, list[Path]]:
    if product != "lmaudio" or first_tag != "v0.2.1":
        raise FlipError("the no-build release replay is only approved for lmaudio v0.2.1")
    release = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases/latest"]).stdout)
    if release.get("tag_name") != first_tag or release.get("name") != first_tag:
        raise FlipError(f"unexpected latest release metadata; expected {first_tag}")
    metadata_path = release_dir / "release-metadata.json"
    notes_path = release_dir / "release-notes.md"
    if not metadata_path.is_file() or not notes_path.is_file():
        raise FlipError(f"staged release notes or metadata are missing from {release_dir}")
    prior = json.loads(metadata_path.read_text(encoding="utf-8"))
    boundary = ("Releases up to and including v0.2.1 were published under the MIT License "
                "(see the LICENSE asset of that release). Releases after v0.2.1 are published "
                "under the Lattice Systems Personal Use License (this file).")
    expected_notes = prior.get("body", "").rstrip() + "\n\n" + boundary + "\n"
    if prior.get("tagName") != first_tag or prior.get("name") != first_tag or prior.get("body", "").rstrip() != release.get("body", "").rstrip():
        raise FlipError("staged release metadata no longer matches the published v0.2.1 release")
    if notes_path.read_text(encoding="utf-8") != expected_notes:
        raise FlipError("staged release body does not preserve the published notes plus the approved license boundary")
    remote_assets = {asset["name"]: asset for asset in release.get("assets", [])}
    local_assets = {path.name: path for path in release_dir.iterdir() if path.is_file() and path.name not in {"release-metadata.json", "release-notes.md"}}
    if set(local_assets) != set(remote_assets):
        raise FlipError("staged release asset names differ from the published release")
    for name, path in local_assets.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if remote_assets[name].get("digest") != f"sha256:{digest}":
            raise FlipError(f"staged release asset changed from the published bytes: {name}")
    if not (release_dir / "LICENSE").read_text(encoding="utf-8").startswith("MIT License"):
        raise FlipError("v0.2.1 LICENSE asset is not the published MIT license")
    command(["sha256sum", "-c", "SHA256SUMS"], cwd=release_dir)
    return release, [local_assets[name] for name in sorted(local_assets)]


def _publish_unchanged_release(product: str, first_tag: str, release: dict, assets: list[Path], notes: Path, verify_dir: Path) -> dict:
    if verify_dir.exists():
        raise FlipError(f"release verification path already exists: {verify_dir}")
    create = ["gh", "release", "create", first_tag, "-R", public_repo(product), "--target", "main", "--title", release["name"], "--notes-file", str(notes)]
    create.extend(str(path) for path in assets)
    command(create, timeout=900)
    published = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases/tags/{first_tag}"]).stdout)
    if published.get("tag_name") != first_tag or published.get("name") != release.get("name") or published.get("body", "").rstrip() != notes.read_text(encoding="utf-8").rstrip():
        raise FlipError("republished release metadata differs from the approved staged metadata")
    published_assets = {item["name"]: item for item in published.get("assets", [])}
    if set(published_assets) != {path.name for path in assets}:
        raise FlipError("republished release asset names differ from v0.2.1")
    for path in assets:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if published_assets[path.name].get("digest") != f"sha256:{digest}":
            raise FlipError(f"republished asset digest differs from staged v0.2.1: {path.name}")
    verify_dir.mkdir(parents=True)
    command(["gh", "release", "download", first_tag, "-R", public_repo(product), "--dir", str(verify_dir)], timeout=900)
    downloaded = {path.name: path for path in verify_dir.iterdir() if path.is_file()}
    if set(downloaded) != {path.name for path in assets}:
        raise FlipError("downloaded release asset names differ from v0.2.1")
    staged_by_name = {path.name: path for path in assets}
    for name, path in downloaded.items():
        if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(staged_by_name[name].read_bytes()).digest():
            raise FlipError(f"downloaded release asset bytes differ from v0.2.1: {name}")
    command(["sha256sum", "-c", "SHA256SUMS"], cwd=verify_dir)
    linux = verify_dir / f"{product}-linux-x64"
    command(["chmod", "+x", str(linux)])
    version = command([str(linux), "--version"]).stdout.strip()
    if version != f"{product} {first_tag[1:]}" :
        raise FlipError(f"republished binary returned an unexpected version: {version}")
    for example in ("eq_before_after.lms", "karplus_strong_harp.lms"):
        url = f"https://raw.githubusercontent.com/{public_repo(product)}/main/examples/{example}"
        path = verify_dir / example
        command(["curl", "-fsSL", url, "-o", str(path)], timeout=120)
        command(["lmscript", "--check", str(path)], timeout=300)
    return published


def _untracked_consumer_docs(product: str, pins: list[str]) -> dict[Path, str]:
    if product != "lmaudio":
        return {}
    known_local_doc = Path("/home/mma/repos/dsl/simulation/ROADMAP.md").resolve()
    result: dict[Path, str] = {}
    for line in pins:
        match = re.match(r"(.+?):[0-9]+:", line)
        if not match:
            continue
        path = Path(match.group(1)).resolve()
        probe = command(["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"], check=False)
        if probe.returncode == 0:
            continue
        if path != known_local_doc or not path.is_file():
            raise FlipError(f"versioned consumer is outside a Git checkout and is not an approved local doc: {path}")
        result[path] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _update_untracked_consumer_docs(product: str, first_tag: str, expected_hashes: dict[Path, str]) -> list[str]:
    updated: list[str] = []
    for path, expected_hash in expected_hashes.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            raise FlipError(f"untracked consumer doc changed after preflight; pin update needs review: {path}")
        if rewrite_consumer_file(path, product, first_tag):
            updated.append(str(path))
    return updated


def apply_lmaudio_pilot(first_tag: str) -> int:
    product = "lmaudio"
    if first_tag != "v0.2.1":
        raise FlipError("the approved lmaudio pilot must replay v0.2.1 unchanged")
    approval = Path.home() / "tools/closed-source-approved.txt"
    if not approval.is_file() or product not in {line.strip() for line in approval.read_text(encoding="utf-8").splitlines()}:
        raise FlipError("owner approval file must list lmaudio; no flip was started")
    token_path = Path.home() / ".config/lmctl/release_token"
    if not token_path.is_file() or token_path.stat().st_mode & 0o777 != 0o600 or token_path.stat().st_size == 0:
        raise FlipError("release-token file is missing, empty, or not mode 600; no flip was started")

    snapshot = git_snapshot(product, fetch=True)
    expected_origin = f"https://github.com/{public_repo(product)}.git"
    if snapshot["local_branch"] != "main" or not snapshot["clean"] or not snapshot["pushed"] or snapshot["origin"].rstrip("/") not in {expected_origin, expected_origin.removesuffix(".git")}:
        raise FlipError("lmaudio source checkout must be clean, on main, and synchronized to the public origin")
    if agents_for(product, active_lmctl_members()):
        raise FlipError("an active lmaudio session exists; stop before transfer")
    ci = ci_latest(product, snapshot["ref"])
    if not ci.get("ok"):
        raise FlipError(f"lmaudio main CI is not green: {ci.get('url','')} {ci.get('error','')}")
    root = snapshot["root"]
    stage = STAGING / f"{product}-public"
    manifest_path = STAGING / f"{product}-stage-manifest.json"
    release_dir = STAGING / f"{product}-release"
    verify_dir = STAGING / f"{product}-release-verify"
    if not stage.is_dir() or not manifest_path.is_file():
        raise FlipError(f"stage the public tree first: {stage}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("source_main_sha") != snapshot["ref"]:
        raise FlipError("lmaudio origin/main changed since staging; refresh the public tree")
    validation = validate_stage(product, stage, manifest.get("public_file_map", {}))
    if validation.get("private_source_references") or validation.get("secret_findings") or validation.get("missing_autorun"):
        raise FlipError("staged lmaudio tree failed validation")
    expected_hashes = manifest.get("staged_file_sha256", {})
    actual_hashes = {p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in stage.rglob("*") if p.is_file() and ".git" not in p.parts}
    if actual_hashes != expected_hashes:
        raise FlipError("staged lmaudio tree differs from its reviewed manifest")
    boundary = ("Releases up to and including v0.2.1 were published under the MIT License "
                "(see the LICENSE asset of that release). Releases after v0.2.1 are published "
                "under the Lattice Systems Personal Use License (this file).")
    if boundary not in (stage / "README.md").read_text(encoding="utf-8") or not (stage / "LICENSE").read_text(encoding="utf-8").startswith(boundary):
        raise FlipError("staged README/LICENSE omit the approved lmaudio license boundary")
    old_release, assets = _release_files(product, release_dir, first_tag)
    if stage.joinpath(".git").exists() or verify_dir.exists() or (Path("/home/mma/repos/dsl") / f"{product}-public").exists():
        raise FlipError("public stage, verification path, or public checkout already exists")

    pins, consumer_files = consumer_repositories(product)
    untracked_docs = _untracked_consumer_docs(product, pins)
    validate_consumer_checkouts(product, list(consumer_files), active_lmctl_members())
    metadata = _repo_view(product)
    _check_private_target_free(product)
    if metadata.get("private") or not metadata.get("default_branch") == "main":
        raise FlipError("public lmaudio repo metadata differs from the reviewed preflight")
    _prepare_orphan_commit(stage, product)

    transferred = False
    private_secret_set = False
    public_created = False
    try:
        command(["gh", "api", "-X", "POST", f"repos/{public_repo(product)}/transfer", "-f", "new_owner=lmctlhq"], timeout=300)
        transferred = True
        private_data = _wait_for_private_transfer(product, attempts=60)
        if private_data.get("private"):
            raise FlipError("transferred repo became private before the required immediate visibility step")
        command(["gh", "repo", "edit", private_repo(product), "--visibility", "private", "--accept-visibility-change-consequences"], timeout=300)
        private_data = json.loads(command(["gh", "api", f"repos/{private_repo(product)}"]).stdout)
        if not private_data.get("private"):
            raise FlipError("source repo did not become private")
        _set_release_secret_from_file(product)
        private_secret_set = True

        create = ["gh", "repo", "create", public_repo(product), "--public"]
        if metadata.get("description"):
            create.extend(["--description", metadata["description"]])
        if metadata.get("homepage"):
            create.extend(["--homepage", metadata["homepage"]])
        command(create, timeout=300)
        public_created = True
        command(["git", "-C", str(stage), "remote", "add", "origin", f"https://github.com/{public_repo(product)}.git"])
        command(["git", "-C", str(stage), "push", "-u", "origin", "main"], timeout=900)
        command(["gh", "repo", "edit", public_repo(product), "--default-branch", "main", "--enable-issues", "--enable-wiki=false", "--enable-projects=false"], timeout=300)
        for topic in metadata.get("topics", []):
            command(["gh", "repo", "edit", public_repo(product), "--add-topic", topic], timeout=300)
        public_data = json.loads(command(["gh", "api", f"repos/{public_repo(product)}"]).stdout)
        if public_data.get("private") or public_data.get("default_branch") != "main":
            raise FlipError("fresh public lmaudio repo visibility/default branch is unexpected")

        _install_private_ci(product, root, first_tag)
        private_sha = command(["git", "-C", str(root), "rev-parse", "HEAD"]).stdout.strip()
        private_ci = _run_publish_test(product, private_sha)
        notes = release_dir / "release-notes.md"
        published_release = _publish_unchanged_release(product, first_tag, old_release, assets, notes, verify_dir)
        _update_local_checkouts(product, root)
        update_consumer_pins(product, first_tag, consumer_files, root)
        updated_docs = _update_untracked_consumer_docs(product, first_tag, untracked_docs)
        print(f"FLIP COMPLETE: {product} source is private; fresh public peer and unchanged {first_tag} assets verified; private publish-test succeeded at {private_ci.get('url','')}; release={published_release.get('html_url','')}; local consumer docs updated={len(updated_docs)}")
        return 0
    except Exception as exc:
        if transferred and not public_created:
            try:
                if private_secret_set:
                    command(["gh", "secret", "delete", "RELEASE_TOKEN", "-R", private_repo(product)], timeout=120)
                command(["gh", "api", "-X", "POST", f"repos/{private_repo(product)}/transfer", "-f", "new_owner=lmctl-ai"], timeout=300)
                restored = _wait_for_transfer_back(product)
                if restored:
                    command(["gh", "repo", "edit", public_repo(product), "--visibility", "public", "--accept-visibility-change-consequences"], timeout=300)
                else:
                    raise FlipError("transferred repository did not return to lmctl-ai")
            except Exception as rollback_error:
                raise FlipError(f"flip failed before public recreation ({exc}); automatic rollback also failed ({rollback_error})") from exc
        elif public_created:
            raise FlipError(f"flip stopped after creating the fresh public repo; no delete_repo permission is available for rollback: {exc}") from exc
        raise


def _wait_for_transfer_back(product: str) -> bool:
    for _ in range(60):
        result = command(["gh", "api", f"repos/{public_repo(product)}"], check=False, timeout=60)
        if result.returncode == 0:
            return True
        time.sleep(3)
    return False


def apply_flip(product: str, first_tag: str) -> int:
    if product != "lmaudio":
        raise FlipError("only the owner-approved lmaudio pilot is enabled for apply")
    return apply_lmaudio_pilot(first_tag)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory, stage, and owner-gate a public/private peer repository flip")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true", help="read-only plan (default)")
    modes.add_argument("--stage", action="store_true", help="write a public-only tree under /home/mma/staging/closed-source")
    modes.add_argument("--apply", action="store_true", help="perform an approved transfer/recreate flip")
    parser.add_argument("--product", required=True, choices=PRODUCTS)
    parser.add_argument("--first-release-tag", default="")
    parser.add_argument("--refresh", action="store_true", help="replace only a staging tree with a matching peer-flip manifest")
    args = parser.parse_args()
    if args.apply:
        return apply_flip(args.product, args.first_release_tag)
    return run_dry_or_stage(args.product, args.stage, args.refresh)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FlipError as exc:
        print(f"peer-flip: {exc}", file=sys.stderr)
        raise SystemExit(2)
