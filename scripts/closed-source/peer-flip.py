#!/usr/bin/env python3
"""Inventory and stage source repos as public docs/examples peers."""

from __future__ import annotations

import argparse
import datetime
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


AUDIT_LOG: Path | None = None


def audit(message: str) -> None:
    if AUDIT_LOG is None:
        return
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with AUDIT_LOG.open("a", encoding="utf-8") as stream:
        stream.write(f"{stamp} {message}\n")


def _redact_for_log(value):
    if isinstance(value, dict):
        return {key: ("[REDACTED]" if re.search(r"token|secret|password|credential", str(key), re.I) else _redact_for_log(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_for_log(item) for item in value]
    if not isinstance(value, str):
        return value
    value = re.sub(r"(?i)github_pat_[a-z0-9_]{20,}|gh[pousr]_[a-z0-9]{20,}", "[REDACTED]", value)
    value = re.sub(r'(?i)("(?:temp_clone_token|access_token|refresh_token|release_token|client_secret|password)"\s*:\s*")[^"]*(")', r"\1[REDACTED]\2", value)
    return re.sub(r"(?i)(authorization\s*:\s*bearer\s+)[^\s]+", r"\1[REDACTED]", value)


def public_repo(product: str) -> str:
    return f"lmctl-ai/{product}"


def private_repo(product: str) -> str:
    return f"lmctlhq/{product}"


def _version_contains_release(output: str, product: str, tag: str) -> bool:
    return tag.removeprefix("v") in output


def _install_example_hosts(product: str, stage: Path) -> tuple[dict[str, str], Path]:
    script = stage / "scripts/install-hosts.sh"
    if not script.is_file():
        raise FlipError(f"public example host installer is missing: {script}")
    scratch_base = Path("/tmp/claude-1000/scratch-workers")
    scratch_base.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=f"{product}-example-hosts-", dir=scratch_base))
    host_bin = scratch / "bin"
    env = os.environ.copy()
    env["LMCTL_HOST_BIN_DIR"] = str(host_bin)
    env["RUNNER_TEMP"] = str(scratch)
    command(["bash", str(script)], cwd=stage, timeout=900, env=env)
    env["PATH"] = str(host_bin) + os.pathsep + env.get("PATH", "")
    audit(f"LOCAL_EXAMPLE_HOSTS_INSTALLED product={product} bin={host_bin}")
    return env, scratch


def _delete_public_ref(product: str, stage: Path, url: str, ref: str) -> None:
    expected_url = f"https://github.com/{public_repo(product)}.git"
    if url != expected_url:
        raise FlipError(f"ref deletion target is not the public remote URL for {product}: {url}")
    origin = command(["git", "-C", str(stage), "remote", "get-url", "origin"]).stdout.strip()
    if origin != expected_url:
        raise FlipError(f"public staging remote mismatch before ref deletion: {origin}")
    argv = ["git", "-C", str(stage), "push", expected_url, "--delete", ref]
    if argv[4] != expected_url or str(stage) == str(PRODUCT_ROOTS[product]):
        raise FlipError(f"ref deletion command is not explicitly scoped to the public remote: {argv!r}")
    audit(f"PUBLIC_REF_DELETE_ASSERTED url={expected_url} ref={ref}")
    command(argv, timeout=300)


def _delete_public_release(product: str, tag: str) -> None:
    repo = public_repo(product)
    if repo != f"lmctl-ai/{product}":
        raise FlipError(f"release deletion target is not the public repository: {repo}")
    argv = ["gh", "release", "delete", tag, "-R", repo, "--cleanup-tag", "--yes"]
    if argv[5] != repo:
        raise FlipError(f"release and tag deletion is not scoped to the public repository: {argv!r}")
    audit(f"PUBLIC_RELEASE_DELETE_ASSERTED repo={repo} tag={tag}")
    command(argv, timeout=300)


def command(argv: list[str], *, cwd: Path | None = None, check: bool = True,
            timeout: int = 300, input_text: str | None = None,
            env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=timeout, input=input_text, env=env)
    if AUDIT_LOG is not None:
        audit(f"COMMAND {argv!r} cwd={str(cwd) if cwd else ''} exit={proc.returncode} stdin={'[REDACTED]' if input_text is not None else '[none]'}")
        if proc.stdout.strip():
            try:
                logged = json.dumps(_redact_for_log(json.loads(proc.stdout)), sort_keys=True)
            except json.JSONDecodeError:
                logged = str(_redact_for_log(proc.stdout.strip()))
            audit(f"STDOUT {logged}")
        if proc.stderr.strip():
            audit(f"STDERR {_redact_for_log(proc.stderr.strip())}")
    if check and proc.returncode:
        raise FlipError(f"command failed ({proc.returncode}): {' '.join(argv)}\n{proc.stderr.strip()}")
    return proc


def gh_api_logged(api_args: list[str], *, timeout: int = 300) -> dict:
    argv = ["gh", "api", "-i", *api_args]
    proc = subprocess.run(argv, text=True, capture_output=True, timeout=timeout)
    raw = proc.stdout
    status_line = next((line.strip() for line in raw.splitlines() if line.startswith("HTTP/")), "HTTP status unavailable")
    body_parts = re.split(r"\r?\n\r?\n", raw, maxsplit=1)
    body_text = body_parts[1] if len(body_parts) == 2 else ""
    try:
        body = json.loads(body_text) if body_text.strip() else {}
    except json.JSONDecodeError:
        body = {"raw": body_text}
    audit(f"HTTP_COMMAND {argv!r} exit={proc.returncode}")
    audit(f"HTTP_STATUS {status_line}")
    audit("HTTP_RESPONSE_BODY " + json.dumps(_redact_for_log(body), sort_keys=True))
    status_match = re.match(r"HTTP/\S+\s+(\d+)", status_line)
    status_code = int(status_match.group(1)) if status_match else 0
    if proc.returncode or status_code >= 400:
        raise FlipError(f"GitHub API request failed: {status_line}; response body: {json.dumps(_redact_for_log(body), sort_keys=True)}")
    return body


def git_snapshot(product: str, *, fetch: bool = False) -> dict:
    root = PRODUCT_ROOTS[product]
    if not root.is_dir():
        raise FlipError(f"source checkout is missing: {root}")
    if fetch:
        command(["git", "-C", str(root), "fetch", "-q", "--prune", "--prune-tags", "origin"], timeout=300)
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


def ci_latest(product: str, sha: str, repository: str | None = None) -> dict:
    result = command(["gh", "run", "list", "-R", repository or f"lmctl-ai/{product}", "-L", "20", "--json", "status,conclusion,displayTitle,headSha,url"], check=False, timeout=120)
    if result.returncode != 0:
        return {"ok": False, "error": result.stderr.strip(), "status": "unknown", "conclusion": ""}
    try:
        rows = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid gh run list JSON", "status": "unknown", "conclusion": ""}
    if not rows:
        return {"ok": False, "error": "no Actions run found", "status": "unknown", "conclusion": ""}
    row = next((item for item in rows if item.get("headSha") == sha), None)
    if row is None:
        return {"ok": False, "error": f"no Actions run found for {sha}", "status": "unknown", "conclusion": ""}
    row["ok"] = row.get("status") == "completed" and row.get("conclusion") == "success"
    return row


def _reuse_lmfilament_publish_test(current_sha: str, root: Path) -> dict:
    run_id = "40234775880"
    details = json.loads(command(["gh", "run", "view", run_id, "-R", "lmctlhq/lmfilament",
                                  "--json", "status,conclusion,headSha,jobs,url"]).stdout)
    jobs = {job.get("name"): job for job in details.get("jobs", [])}
    if (details.get("status") != "completed" or details.get("conclusion") != "success"
            or jobs.get("publish-test", {}).get("conclusion") != "success"):
        raise FlipError(f"recorded lmfilament publish-test {run_id} is not successful: {details.get('url', '')}")
    tested_sha = details.get("headSha", "")
    if not tested_sha or command(["git", "-C", str(root), "merge-base", "--is-ancestor", tested_sha, current_sha], check=False).returncode:
        raise FlipError(f"recorded lmfilament publish-test {run_id} does not apply to current private main")
    workflows_unchanged = command(["git", "-C", str(root), "diff", "--quiet", f"{tested_sha}..{current_sha}",
                                  "--", ".github/workflows/ci.yml", "scripts/release-to-public.sh"], check=False)
    if workflows_unchanged.returncode:
        raise FlipError(f"lmfilament private publisher changed since publish-test {run_id}")
    details["ok"] = True
    audit(f"PRIVATE_PUBLISH_TEST_REUSED run={run_id} tested_sha={tested_sha} current_sha={current_sha}")
    return details


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
    manifest_path = STAGING / f"{product}-stage-manifest.json"
    if not manifest_path.is_file():
        raise FlipError(f"stage manifest missing for generated private CI: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    generated = Path(manifest.get("generated_private_ci_path", ""))
    if not generated.is_file():
        raise FlipError(f"generated product private CI is missing: {generated}")
    digest = hashlib.sha256(generated.read_bytes()).hexdigest()
    if digest != manifest.get("generated_private_ci_sha256"):
        raise FlipError(f"generated private CI differs from the reviewed stage manifest: {generated}")
    return generated


def postprocess_stage(product: str, snapshot: dict, stage: Path, manifest: dict) -> tuple[Path, str]:
    private_ci = STAGING / f"{product}-private-ci-{snapshot['ref'][:12]}.yml"
    script = GALLERY / "scripts/closed-source/publish_tree.py"
    command(["python3", str(script), str(stage), str(snapshot["root"]), product,
             "--boundary", "--notices", "--private-ci", str(private_ci)], timeout=300)
    if not private_ci.is_file():
        raise FlipError(f"publish_tree.py did not generate private CI: {private_ci}")
    actionlint = shutil.which("actionlint")
    fallback = Path("/tmp/claude-1000/scratch-workers/bin/actionlint")
    if not actionlint and fallback.is_file():
        actionlint = str(fallback)
    if actionlint:
        command([actionlint, str(private_ci)], timeout=120)
    manifest["generated_private_ci_path"] = str(private_ci)
    manifest["generated_private_ci_sha256"] = hashlib.sha256(private_ci.read_bytes()).hexdigest()
    return private_ci, manifest["generated_private_ci_sha256"]


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
        # Notices preserve upstream source citations byte-for-byte; their
        # relative paths are citations, not links in the public documentation.
        if path.name.startswith("THIRD_PARTY_NOTICES"):
            continue
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
        # Notices are copied byte-for-byte from the source by publish_tree.py;
        # upstream component paths inside them are compliance citations, not
        # links to private host implementation files.
        if path.name.startswith("THIRD_PARTY_NOTICES"):
            continue
        if path.suffix.lower() not in {".md", ".html", ".svg"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        scan_text = re.sub(r"https?://[^\s<>]+", "", text)
        for match in PRIVATE_TOKEN.finditer(scan_text):
            private_refs.append(f"{path.relative_to(stage).as_posix()}:{scan_text.count(chr(10), 0, match.start()) + 1}:{match.group(0)}")
    secrets = scan_secrets(stage, files)
    allowed = {"README.md", "docs", "examples", ".github", "scripts", "LICENSE", "LICENSE-examples"}
    allowed.update(name for name in {p.name for p in files} if name.startswith("THIRD_PARTY_NOTICES"))
    unapproved_top = sorted(p.name for p in stage.iterdir() if p.name not in allowed)
    public_scripts = sorted(p.relative_to(stage).as_posix() for p in files if p.is_relative_to(stage / "scripts"))
    if public_scripts and public_scripts != ["scripts/install-hosts.sh"]:
        unapproved_top.append("scripts (only scripts/install-hosts.sh is permitted)")
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
        previous_ci = Path(previous.get("generated_private_ci_path", ""))
        if previous_ci.is_file() and hashlib.sha256(previous_ci.read_bytes()).hexdigest() != previous.get("generated_private_ci_sha256"):
            raise FlipError(f"generated private CI changed since the manifest; inspect before refresh: {previous_ci}")
        shutil.rmtree(stage)
        manifest_path.unlink()
    STAGING.mkdir(parents=True, exist_ok=True)
    mapping = {path: mapped for path in snapshot["files"] if (mapped := map_public_path(path)) is not None}
    inputs = discover_inputs(product, snapshot["ref"], set(snapshot["files"]), mapping)
    mapping.update(inputs)
    selected = sorted(mapping)
    generated_private_ci = STAGING / f"{product}-private-ci-{snapshot['ref'][:12]}.yml"
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
        public_script = stage / "scripts/install-hosts.sh"
        public_script.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(GALLERY / "scripts/closed-source/templates/install-hosts.sh", public_script)
        public_script.chmod(0o755)
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
        postprocess_stage(product, snapshot, stage, manifest)
        report = validate_stage(product, stage, mapping)
        manifest["validation"] = report
        manifest["staged_file_sha256"] = {
            p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in stage.rglob("*") if p.is_file()
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return manifest
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        generated_private_ci.unlink(missing_ok=True)
        raise


def run_dry_or_stage(product: str, stage: bool, refresh: bool = False) -> int:
    snap = git_snapshot(product, fetch=True)
    members = active_lmctl_members()
    agents = agents_for(product, members)
    source_repo = private_repo(product) if snap["origin"].rstrip("/") in {
        f"https://github.com/{private_repo(product)}.git", f"https://github.com/{private_repo(product)}"
    } else public_repo(product)
    ci = ci_latest(product, snap["ref"], source_repo)
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


def _repo_view_private(product: str) -> dict:
    result = command(["gh", "api", f"repos/{private_repo(product)}"], check=False)
    if result.returncode:
        return {"exists": False}
    data = json.loads(result.stdout)
    data["exists"] = True
    return data


def _wait_for_repo_identity(product: str, *, private: bool | None = None, attempts: int = 30) -> dict:
    last = "repo not visible yet"
    for attempt in range(1, attempts + 1):
        result = command(["gh", "api", f"repos/{private_repo(product)}"], check=False, timeout=60)
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if data.get("full_name", "").lower() == private_repo(product).lower() and (private is None or data.get("private") is private):
                    audit(f"PRIVATE_REPO_VISIBLE attempt={attempt} private={data.get('private')} default_branch={data.get('default_branch')}")
                    return data
                last = f"resolved full_name={data.get('full_name')} private={data.get('private')}"
            except json.JSONDecodeError:
                last = "invalid repo JSON"
        else:
            last = result.stderr.strip()
        audit(f"PRIVATE_REPO_VISIBILITY_WAIT attempt={attempt}/{attempts} state={_redact_for_log(last)}")
        time.sleep(2)
    raise FlipError(f"{private_repo(product)} did not reach the expected private repo state: {last}")


def _check_private_target_free(product: str) -> bool:
    repos = json.loads(command(["gh", "repo", "list", "lmctlhq", "--limit", "1000", "--json", "name"]).stdout)
    if not any(repo.get("name", "").lower() == product.lower() for repo in repos):
        return False
    data = _wait_for_repo_identity(product, private=True)
    if data.get("disabled") or data.get("default_branch") not in (None, "main"):
        raise FlipError(f"existing private target {private_repo(product)} has unexpected repo settings")
    branches = json.loads(command(["gh", "api", f"repos/{private_repo(product)}/branches"]).stdout)
    releases = json.loads(command(["gh", "api", f"repos/{private_repo(product)}/releases?per_page=100"]).stdout)
    secrets = json.loads(command(["gh", "secret", "list", "-R", private_repo(product), "--json", "name,updatedAt"]).stdout)
    git_refs = command(["git", "ls-remote", "--heads", "--tags", f"https://github.com/{private_repo(product)}.git"], check=False)
    if branches or releases or secrets or (git_refs.returncode == 0 and git_refs.stdout.strip()):
        raise FlipError(f"existing private target {private_repo(product)} is not the reviewed empty scaffold")
    if git_refs.returncode != 0:
        raise FlipError(f"cannot verify the existing private scaffold refs: {git_refs.stderr.strip()}")
    actions = json.loads(command(["gh", "api", f"repos/{private_repo(product)}/actions/permissions"]).stdout)
    if actions.get("enabled") is not False:
        _set_repo_actions_enabled(product, False)
    audit(f"PRIVATE_EMPTY_SCAFFOLD_REUSED repo={private_repo(product)}")
    return True


def _update_local_checkouts(product: str, root: Path) -> None:
    command(["git", "-C", str(root), "remote", "set-url", "origin", f"https://github.com/{private_repo(product)}.git"])
    command(["git", "-C", str(root), "pull", "--rebase"], timeout=600)
    public_checkout = Path("/home/mma/repos/dsl") / f"{product}-public"
    if public_checkout.exists():
        public_origin = command(["git", "-C", str(public_checkout), "remote", "get-url", "origin"], check=False).stdout.strip().rstrip("/")
        if public_origin not in {f"https://github.com/{public_repo(product)}.git", f"https://github.com/{public_repo(product)}"}:
            raise FlipError(f"existing public checkout has an unexpected origin: {public_checkout}")
        if command(["git", "-C", str(public_checkout), "status", "--porcelain", "--untracked-files=all"]).stdout.strip():
            raise FlipError(f"existing public checkout is dirty: {public_checkout}")
        command(["git", "-C", str(public_checkout), "fetch", "-q", "origin"], timeout=600)
        command(["git", "-C", str(public_checkout), "reset", "--hard", "origin/main"], timeout=300)
        return
    public_checkout.parent.mkdir(parents=True, exist_ok=True)
    command(["git", "clone", f"https://github.com/{public_repo(product)}.git", str(public_checkout)], timeout=900)


def _install_private_ci(product: str, root: Path, first_tag: str) -> str:
    adapter = private_ci_adapter(product)
    command(["git", "-C", str(root), "pull", "--rebase", "origin", "main"], timeout=600)
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
        f"# Public/private peer deployment\n\nThe source repository is private at `{private_repo(product)}`. The public peer `{public_repo(product)}` owns README, docs/images, examples/inputs, notices, and binary releases. The first public release tag is `{first_tag}`. Public source history was replaced by one orphan docs/examples commit; old source history remains private. CI checks public examples against this source build. Private CI runs the Linux x64 fast job on pushes; the full platform matrix and publisher run only on workflow_dispatch or version tags (four platforms for lmvideo, five for other products). Releases through `{first_tag}` remain MIT under that release's LICENSE asset; later releases use the Personal Use License in the public root LICENSE.\n",
        encoding="utf-8",
    )
    command(["git", "-C", str(root), "add", ".github/workflows/ci.yml", "scripts/release-to-public.sh", "durable-memory/20-public-private-peers.md"])
    command([
        "git", "-C", str(root), "-c", "user.name=mike-lmctl", "-c", "user.email=281311770+mike-lmctl@users.noreply.github.com",
        "commit", "-m", "Install private peer publishing workflow [skip ci]",
        "-m", f"Use Linux-fast default checks, full tagged/manual matrix builds, public example tests, and publish {first_tag} through the public peer.",
        "-m", "Constraint: Public examples and binary releases stay in the public peer\nConfidence: high\nScope-risk: moderate\nTested: Private publish_test workflow\nNot-tested: Full platform build matrix\nCo-Authored-By: OpenAI Codex <noreply@anthropic.com>",
    ])
    command(["git", "-C", str(root), "push", f"https://github.com/{private_repo(product)}.git", "main:main"], timeout=900)
    return command(["git", "-C", str(root), "rev-parse", "HEAD"]).stdout.strip()


def _wait_for_private_workflow(product: str, attempts: int = 30) -> None:
    for attempt in range(1, attempts + 1):
        result = command(["gh", "api", f"repos/{private_repo(product)}/actions/workflows"], check=False, timeout=60)
        if result.returncode == 0:
            try:
                workflows = json.loads(result.stdout).get("workflows", [])
            except json.JSONDecodeError:
                workflows = []
            workflow = next((item for item in workflows if item.get("path") == ".github/workflows/ci.yml"), None)
            if workflow and workflow.get("state") == "active":
                audit(f"PRIVATE_WORKFLOW_ACTIVE attempt={attempt} id={workflow.get('id')}")
                return
            state = workflow.get("state") if workflow else "not-listed"
        else:
            state = result.stderr.strip()
        audit(f"PRIVATE_WORKFLOW_WAIT attempt={attempt}/{attempts} state={_redact_for_log(state)}")
        time.sleep(2)
    raise FlipError("private ci.yml workflow did not become active after enabling Actions")


def _run_publish_test(product: str, private_sha: str) -> dict:
    _wait_for_private_workflow(product)
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
    for name, job in jobs.items():
        if name not in {"publish-test", "version", "audit"} and job.get("conclusion") != "skipped":
            raise FlipError(f"publish-test unexpectedly ran non-test job {name}: {details.get('url','')}")
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
        repo_result = command(["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"], check=False)
        if repo_result.returncode:
            continue
        root = Path(repo_result.stdout.strip()).resolve()
        if root == source_root.resolve():
            continue
        file_map.setdefault(root, set()).add(path.resolve().relative_to(root).as_posix())
    updated: list[str] = []
    version = first_tag
    install_re = re.compile(rf"(github:lmctl-ai/{re.escape(product)}@)v[0-9]+\.[0-9]+\.[0-9]+")
    release_download_re = re.compile(rf"(github\.com/lmctl-ai/{re.escape(product)}/releases/download/)v[0-9]+\.[0-9]+\.[0-9]+")
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
                line = install_re.sub(rf"\g<1>{version}", line)
                line = release_download_re.sub(rf"\g<1>{version}", line)
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
                "-m", f"Update versioned public install and release references after the history reset for {product}.",
                "-m", "Constraint: Only the surviving first public release tag remains available\nConfidence: high\nScope-risk: narrow\nTested: Updated consumer references and pushed main\nNot-tested: Consumer-specific runtime behavior\nCo-Authored-By: OpenAI Codex <noreply@anthropic.com>",
            ])
            command(["git", "-C", str(root), "pull", "--rebase"], timeout=600)
            command(["git", "-C", str(root), "push", "origin", "main"], timeout=900)
            updated.append(str(root))
    return updated


def _set_release_secret_from_file(product: str) -> None:
    token_path = Path.home() / ".config/lmctl/release_token"
    if not token_path.is_file() or token_path.stat().st_mode & 0o777 != 0o600 or token_path.stat().st_size == 0:
        raise FlipError("release-token file is missing, empty, or not mode 600; no token value was read")
    audit(f"COMMAND gh secret set RELEASE_TOKEN -R {private_repo(product)} stdin=[REDACTED:{token_path}]")
    with token_path.open("rb") as stream:
        result = subprocess.run(["gh", "secret", "set", "RELEASE_TOKEN", "-R", private_repo(product)], stdin=stream, capture_output=True, text=True)
    audit(f"SECRET_SET exit={result.returncode} stdout={_redact_for_log(result.stdout.strip())} stderr={_redact_for_log(result.stderr.strip())}")
    if result.returncode:
        raise FlipError(f"could not set the private release secret: {result.stderr.strip()}")
    for attempt in range(1, 31):
        rows = json.loads(command(["gh", "secret", "list", "-R", private_repo(product), "--json", "name,updatedAt"]).stdout)
        if any(row.get("name") == "RELEASE_TOKEN" for row in rows):
            audit(f"PRIVATE_SECRET_VISIBLE attempt={attempt} name=RELEASE_TOKEN")
            return
        audit(f"PRIVATE_SECRET_WAIT attempt={attempt}/30 name=RELEASE_TOKEN")
        time.sleep(2)
    raise FlipError("RELEASE_TOKEN did not appear in the private repo secret list")


def _prepare_orphan_commit(stage: Path, product: str) -> None:
    if (stage / ".git").exists():
        raise FlipError("public stage already has Git history; refusing to reuse it")
    command(["git", "-C", str(stage), "init", "-b", "main"])
    command(["git", "-C", str(stage), "-c", "user.name=mike-lmctl", "-c", "user.email=281311770+mike-lmctl@users.noreply.github.com", "add", "-A"])
    command([
        "git", "-C", str(stage), "-c", "user.name=mike-lmctl", "-c", "user.email=281311770+mike-lmctl@users.noreply.github.com",
        "commit", "-m", f"Keep {product} public documentation and examples available",
        "-m", "The public peer serves MIT examples, documentation, and release entry points while private source and CI own future builds.",
        "-m", "Constraint: Existing raw example URLs must keep their paths\nConfidence: high\nScope-risk: broad\nReversibility: messy\nTested: Staged tree validation and public-content CI\nNot-tested: None\nCo-Authored-By: OpenAI Codex <noreply@anthropic.com>",
    ])
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


def _prepare_release_bundle(product: str, root: Path, first_tag: str, run_stamp: str) -> dict:
    release = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases/latest"]).stdout)
    if release.get("tag_name") != first_tag:
        raise FlipError(f"{first_tag} is not the latest published release of {public_repo(product)}")
    bundle = STAGING / f"{product}-release-replay-{run_stamp}"
    if bundle.exists():
        raise FlipError(f"release replay path already exists: {bundle}")
    bundle.mkdir(parents=True)
    if release.get("assets"):
        command(["gh", "release", "download", first_tag, "-R", public_repo(product), "--dir", str(bundle)], timeout=900)
    remote_assets = {item["name"]: item for item in release.get("assets", [])}
    downloaded = {path.name: path for path in bundle.iterdir() if path.is_file()}
    if set(remote_assets) != set(downloaded):
        raise FlipError(f"downloaded latest release asset set differs for {product}@{first_tag}")
    for name, path in downloaded.items():
        expected = remote_assets[name].get("digest")
        actual = f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"
        if expected and expected != actual:
            raise FlipError(f"latest release asset digest differs from GitHub for {product}@{first_tag}: {name}")

    def is_binary(name: str) -> bool:
        return bool(re.fullmatch(rf"{re.escape(product)}-(?:linux|macos|windows)-[A-Za-z0-9-]+(?:\.exe|\.sha256)?", name, re.I))

    def is_compliance(name: str) -> bool:
        lower = name.lower()
        return (name == "SHA256SUMS" or lower.endswith(".sha256") or any(
            part in lower for part in ("license", "copying", "copyright", "notice", "relink", "recipe", "occt", "gpl", "lgpl", "exception", "apache", "mit", "bsd", "zlib", "isc", "mpl", "bsl", "cc0")
        ))

    selected = []
    for name in sorted(downloaded):
        lower = name.lower()
        if "debug" in lower or "metric" in lower:
            continue
        if is_binary(name) or is_compliance(name):
            selected.append(name)
    if f"{product}-linux-x64" not in selected:
        raise FlipError(f"latest release has no {product}-linux-x64 binary")

    if "LICENSE" not in selected:
        source_license = root / "LICENSE"
        if not source_license.is_file() or not source_license.read_text(encoding="utf-8").startswith("MIT License"):
            raise FlipError(f"no published MIT LICENSE asset or MIT source LICENSE for {product}@{first_tag}")
        # The replay may add a license omitted by an older release; keep the
        # root bundle byte-exact as the rollback copy of published assets.
        replay = bundle / "replay"
        replay.mkdir(exist_ok=True)
        shutil.copyfile(source_license, replay / "LICENSE")
        selected.append("LICENSE")
    else:
        replay = bundle / "replay"
        replay.mkdir(exist_ok=True)
    notice_assets = [name for name in selected if name.lower().startswith("third_party_notices")]
    if not notice_assets:
        source_notices = sorted(path for path in root.glob("THIRD_PARTY_NOTICES*") if path.is_file())
        if not source_notices:
            raise FlipError(f"no THIRD_PARTY_NOTICES* asset or source file for {product}@{first_tag}")
        for path in source_notices:
            shutil.copyfile(path, replay / path.name)
            selected.append(path.name)

    if product == "lmcad":
        required = {
            "lmcad-linux-x64-relink-objects.tar.gz",
            "lmcad-occt-relinking-recipe.tar.gz",
            "OCCT-LGPL-EXCEPTION.txt",
            "OCCT-LICENSE_LGPL_21.txt",
            "OCCT-RELINKING.md",
        }
        missing = sorted(name for name in required if name not in selected)
        if missing:
            raise FlipError(f"lmcad release is missing required OCCT relinking materials: {', '.join(missing)}")

    selected = sorted(set(selected) - {"SHA256SUMS"})
    if not any(name.lower().startswith("third_party_notices") for name in selected):
        raise FlipError(f"prepared {product} release has no third-party notices")
    for name in selected:
        if not (replay / name).is_file():
            if name in downloaded:
                shutil.copyfile(bundle / name, replay / name)
        if not (replay / name).is_file():
            raise FlipError(f"required release compliance file is missing: {name}")
    sums = "".join(f"{hashlib.sha256((replay / name).read_bytes()).hexdigest()}  {name}\n" for name in selected)
    (replay / "SHA256SUMS").write_text(sums, encoding="ascii", newline="\n")
    selected.append("SHA256SUMS")
    boundary = (f"Releases up to and including {first_tag} were published under the MIT License (see the LICENSE asset of that "
                f"release). Releases after {first_tag} are published under the Lattice Systems Personal Use License (this file).")
    notes_path = replay / "release-notes-replay.md"
    notes_path.write_text((release.get("body") or "").rstrip() + "\n\n" + boundary + "\n", encoding="utf-8")
    linux = replay / f"{product}-linux-x64"
    command(["chmod", "+x", str(linux)])
    version = command([str(linux), "--version"], timeout=120).stdout.strip()
    if not _version_contains_release(version, product, first_tag):
        raise FlipError(f"staged {product} binary reports an unexpected version: {version}")
    stage_examples = STAGING / f"{product}-public" / "examples"
    examples = sorted(path.relative_to(stage_examples).as_posix() for path in stage_examples.rglob("*.lms"))
    if len(examples) < 2:
        raise FlipError(f"staged {product} tree has fewer than two examples for post-flip checks")
    return {"release": release, "bundle": bundle, "replay": replay, "asset_paths": [replay / name for name in selected],
            "notes_path": notes_path, "examples": examples[:2], "boundary": boundary}


def _snapshot_public_releases(product: str, backup_root: Path, stamp: str, latest_tag: str, latest_bundle: dict) -> list[dict]:
    if backup_root.exists():
        raise FlipError(f"release metadata backup path already exists: {backup_root}")
    backup_root.mkdir(parents=True)
    rows = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases?per_page=100"]).stdout)
    latest = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases/latest"]).stdout)
    tags = {row.get("tag_name") for row in rows}
    if latest.get("tag_name") != latest_tag or latest_tag not in tags:
        raise FlipError(f"{latest_tag} is not the latest public release")
    snapshots = []
    for row in rows:
        tag = row.get("tag_name", "")
        if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
            raise FlipError(f"unexpected release tag during snapshot: {tag}")
        directory = Path(latest_bundle["bundle"]) if tag == latest_tag else backup_root / tag
        directory.mkdir(parents=True, exist_ok=True)
        assets = row.get("assets", [])
        metadata = {
            "tagName": tag,
            "id": row.get("id"),
            "name": row.get("name") or tag,
            "body": row.get("body") or "",
            "isDraft": row.get("draft", False),
            "isPrerelease": row.get("prerelease", False),
            "assets": [{"name": item.get("name"), "digest": item.get("digest"), "size": item.get("size")} for item in sorted(assets, key=lambda item: item.get("name", ""))],
        }
        (directory / "release-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        (directory / "release-notes.md").write_text(metadata["body"], encoding="utf-8")
        snapshots.append({"tagName": tag, "path": str(directory), "assets": [item["name"] for item in metadata["assets"]], "assets_complete": tag == latest_tag})
    (backup_root / "manifest.json").write_text(json.dumps({"product": product, "createdAt": stamp, "latest": latest_tag, "releases": snapshots}, indent=2) + "\n", encoding="utf-8")
    return snapshots


def _backup_public_refs(product: str, expected_main: str, backup_git: Path, refs_path: Path) -> dict:
    url = f"https://github.com/{public_repo(product)}.git"
    if backup_git.exists() or refs_path.exists():
        raise FlipError("public history backup path already exists; refusing to overwrite it")
    command(["git", "clone", "--mirror", url, str(backup_git)], timeout=900)
    remote_lines = command(["git", "ls-remote", "--heads", "--tags", url], timeout=300).stdout.splitlines()
    remote_refs = {}
    for line in remote_lines:
        parts = line.split()
        if len(parts) == 2 and not parts[1].endswith("^{}"):
            remote_refs[parts[1]] = parts[0]
    local_lines = command(["git", "--git-dir", str(backup_git), "for-each-ref", "--format=%(objectname) %(refname)", "refs/heads", "refs/tags"]).stdout.splitlines()
    local_refs = {}
    for line in local_lines:
        parts = line.split()
        if len(parts) == 2:
            local_refs[parts[1]] = parts[0]
    if remote_refs != local_refs:
        raise FlipError("local mirror backup refs differ from the live public refs")
    if remote_refs.get("refs/heads/main") != expected_main:
        raise FlipError("public main changed before in-place replacement")
    refs_path.write_text("".join(f"{sha}\t{ref}\n" for ref, sha in sorted(remote_refs.items())), encoding="utf-8")
    audit(f"PUBLIC_REF_BACKUP old_main={expected_main} heads={sum(ref.startswith('refs/heads/') for ref in remote_refs)} tags={sum(ref.startswith('refs/tags/') for ref in remote_refs)} path={backup_git}")
    return {"refs": remote_refs, "main": expected_main}


def _backup_all_public_releases(product: str, backup_root: Path, stamp: str, expected_latest_tag: str = "v0.2.1") -> list[dict]:
    if backup_root.exists():
        raise FlipError(f"release backup path already exists: {backup_root}")
    backup_root.mkdir(parents=True)
    rows = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases?per_page=100"]).stdout)
    latest = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases/latest"]).stdout)
    if latest.get("tag_name") != expected_latest_tag or not any(row.get("tag_name") == expected_latest_tag for row in rows):
        raise FlipError(f"{expected_latest_tag} is not the latest public release")
    backed: list[dict] = []
    for row in rows:
        tag = row.get("tag_name", "")
        if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
            raise FlipError(f"unexpected release tag during backup: {tag}")
        release = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases/tags/{tag}"]).stdout)
        directory = backup_root / tag
        directory.mkdir()
        if release.get("assets"):
            command(["gh", "release", "download", tag, "-R", public_repo(product), "--dir", str(directory)], timeout=900)
        remote_assets = {asset["name"]: asset for asset in release.get("assets", [])}
        local_assets = {path.name: path for path in directory.iterdir() if path.is_file()}
        if set(remote_assets) != set(local_assets):
            raise FlipError(f"release {tag} asset names differ from the downloaded backup")
        for name, path in local_assets.items():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if remote_assets[name].get("digest") != f"sha256:{digest}":
                raise FlipError(f"release {tag} asset digest mismatch during backup: {name}")
        if "SHA256SUMS" in local_assets:
            command(["sha256sum", "-c", "SHA256SUMS"], cwd=directory)
        metadata = {
            "tagName": tag,
            "id": release.get("id"),
            "name": release.get("name") or tag,
            "body": release.get("body") or "",
            "isDraft": release.get("draft", False),
            "isPrerelease": release.get("prerelease", False),
            "createdAt": release.get("created_at"),
            "publishedAt": release.get("published_at"),
            "assets": [{"name": name, "digest": remote_assets[name].get("digest"), "size": remote_assets[name].get("size")} for name in sorted(remote_assets)],
        }
        (directory / "release-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        (directory / "release-notes.md").write_text(metadata["body"], encoding="utf-8")
        backed.append({"tagName": tag, "path": str(directory), "assets": sorted(remote_assets)})
        audit(f"RELEASE_BACKUP verified tag={tag} assets={len(remote_assets)} path={directory}")
    manifest = {"product": product, "createdAt": stamp, "releases": backed}
    (backup_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return backed


def _assert_private_mirror_refs(product: str, expected_refs: dict[str, str]) -> None:
    _wait_for_repo_identity(product, private=True)
    data = json.loads(command(["gh", "api", f"repos/{private_repo(product)}"]).stdout)
    if data.get("disabled"):
        raise FlipError("private source repo is disabled")
    if data.get("default_branch") != "main":
        command(["gh", "repo", "edit", private_repo(product), "--default-branch", "main"], timeout=300)
        for attempt in range(1, 31):
            data = json.loads(command(["gh", "api", f"repos/{private_repo(product)}"]).stdout)
            if data.get("default_branch") == "main":
                audit(f"PRIVATE_DEFAULT_BRANCH_CONVERGED attempt={attempt} branch=main")
                break
            audit(f"PRIVATE_DEFAULT_BRANCH_WAIT attempt={attempt}/30 observed={data.get('default_branch')}")
            time.sleep(2)
        else:
            raise FlipError("private repo default branch did not converge to main")
    for attempt in range(1, 31):
        remote_lines = command(["git", "ls-remote", "--heads", "--tags", f"https://github.com/{private_repo(product)}.git"], timeout=300).stdout.splitlines()
        actual = {parts[1]: parts[0] for line in remote_lines if len(parts := line.split()) == 2 and not parts[1].endswith("^{}")}
        if actual == expected_refs:
            private_main = command(["git", "ls-remote", f"https://github.com/{private_repo(product)}.git", "refs/heads/main"]).stdout.split()[0]
            if private_main == expected_refs.get("refs/heads/main"):
                audit(f"PRIVATE_MIRROR_VERIFIED attempt={attempt} refs={len(actual)} main={private_main}")
                return
        audit(f"PRIVATE_MIRROR_WAIT attempt={attempt}/30 refs_seen={len(actual)} expected={len(expected_refs)}")
        time.sleep(2)
    raise FlipError("private Git mirror refs/default-branch SHA did not converge to the reviewed public history")


def _set_repo_actions_enabled(product: str, enabled: bool) -> None:
    value = "true" if enabled else "false"
    state = json.loads(command(["gh", "api", f"repos/{private_repo(product)}/actions/permissions"]).stdout)
    if state.get("enabled") is enabled:
        audit(f"PRIVATE_ACTIONS_ALREADY value={value}")
        return
    command(["gh", "api", "--method", "PUT", f"repos/{private_repo(product)}/actions/permissions", "-F", f"enabled={value}"], timeout=300)
    for attempt in range(1, 31):
        data = json.loads(command(["gh", "api", f"repos/{private_repo(product)}/actions/permissions"]).stdout)
        if data.get("enabled") is enabled:
            audit(f"PRIVATE_ACTIONS_CONVERGED attempt={attempt} value={value}")
            break
        audit(f"PRIVATE_ACTIONS_WAIT attempt={attempt}/30 expected={value} observed={data.get('enabled')}")
        time.sleep(2)
    else:
        raise FlipError(f"private repo Actions enabled state did not converge to {value}")
    audit(f"PRIVATE_ACTIONS_ENABLED value={value}")


def _verify_public_release_snapshot(product: str, release_backups: list[dict]) -> None:
    current = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases?per_page=100"]).stdout)
    by_tag = {item.get("tag_name"): item for item in current}
    expected_tags = {item["tagName"] for item in release_backups}
    if set(by_tag) != expected_tags:
        raise FlipError("public release list changed after backup; refusing history reset")
    for backup in release_backups:
        saved = json.loads((Path(backup["path"]) / "release-metadata.json").read_text(encoding="utf-8"))
        live = by_tag[backup["tagName"]]
        live_assets = {asset["name"]: asset.get("digest") for asset in live.get("assets", [])}
        saved_assets = {asset["name"]: asset.get("digest") for asset in saved.get("assets", [])}
        if ((live.get("name") or backup["tagName"]) != saved.get("name")
                or (live.get("body") or "") != saved.get("body")
                or live.get("draft", False) != saved.get("isDraft", False)
                or live.get("prerelease", False) != saved.get("isPrerelease", False)
                or live_assets != saved_assets):
            raise FlipError(f"public release {backup['tagName']} changed after backup; refusing history reset")
    audit(f"PUBLIC_RELEASE_BACKUP_RECONFIRMED count={len(release_backups)}")


def _wait_for_no_public_releases(product: str, attempts: int = 30) -> None:
    for attempt in range(1, attempts + 1):
        releases = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases?per_page=100"]).stdout)
        if not releases:
            audit(f"PUBLIC_RELEASE_LIST_EMPTY attempt={attempt}")
            return
        audit(f"PUBLIC_RELEASE_DELETE_WAIT attempt={attempt}/{attempts} remaining={len(releases)}")
        time.sleep(2)
    raise FlipError("old public releases remained after deletion; public refs will be rolled back")


def _wait_for_public_latest_release(product: str, tag: str, expected_assets: dict[str, str], attempts: int = 30) -> dict:
    for attempt in range(1, attempts + 1):
        result = command(["gh", "api", f"repos/{public_repo(product)}/releases/tags/{tag}"], check=False, timeout=60)
        if result.returncode == 0:
            try:
                release = json.loads(result.stdout)
            except json.JSONDecodeError:
                release = {}
            assets = {item.get("name"): item.get("digest") for item in release.get("assets", [])}
            if release.get("tag_name") == tag and assets == expected_assets:
                audit(f"PUBLIC_RELEASE_ASSETS_CONVERGED attempt={attempt} tag={tag} assets={len(assets)}")
                return release
            state = f"tag={release.get('tag_name')} assets={len(assets)}/{len(expected_assets)}"
        else:
            state = _redact_for_log(result.stderr.strip())
        audit(f"PUBLIC_RELEASE_WAIT attempt={attempt}/{attempts} tag={tag} state={state}")
        time.sleep(2)
    raise FlipError(f"public release {tag} did not appear after upload")


def _wait_for_latest_release_tag(product: str, expected_tag: str, attempts: int = 30) -> None:
    for attempt in range(1, attempts + 1):
        result = command(["gh", "release", "view", "-R", public_repo(product), "--json", "tagName"], check=False, timeout=60)
        if result.returncode == 0:
            try:
                tag = json.loads(result.stdout).get("tagName")
            except json.JSONDecodeError:
                tag = None
            if tag == expected_tag:
                audit(f"PUBLIC_LATEST_RELEASE_CONVERGED attempt={attempt} tag={tag}")
                return
        else:
            tag = result.stderr.strip()
        audit(f"PUBLIC_LATEST_RELEASE_WAIT attempt={attempt}/{attempts} observed={_redact_for_log(tag)}")
        time.sleep(2)
    raise FlipError(f"public latest release did not converge to {expected_tag}")


def _wait_for_public_main(product: str, expected_sha: str, attempts: int = 30) -> None:
    url = f"https://github.com/{public_repo(product)}.git"
    for attempt in range(1, attempts + 1):
        result = command(["git", "ls-remote", url, "refs/heads/main"], check=False, timeout=60)
        observed = result.stdout.split()[0] if result.returncode == 0 and result.stdout.split() else ""
        if observed == expected_sha:
            audit(f"PUBLIC_MAIN_CONVERGED attempt={attempt} sha={observed}")
            return
        audit(f"PUBLIC_MAIN_WAIT attempt={attempt}/{attempts} expected={expected_sha} observed={observed or '[none]'}")
        time.sleep(2)
    raise FlipError(f"public main did not converge to expected SHA {expected_sha}")


def _wait_for_public_ci(product: str, expected_sha: str, timeout_seconds: int = 900) -> dict:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        result = command([
            "gh", "run", "list", "-R", public_repo(product), "-L", "50",
            "--json", "databaseId,status,conclusion,headSha,url,event",
        ], check=False, timeout=120)
        if result.returncode != 0:
            raise FlipError(f"cannot inspect public CI for orphan commit {expected_sha}: {result.stderr.strip()}")
        try:
            rows = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise FlipError("GitHub returned invalid JSON while waiting for public CI") from exc
        matching = [row for row in rows if row.get("headSha") == expected_sha and row.get("event") == "push"]
        if matching:
            run = matching[0]
            audit(f"PUBLIC_CI_WAIT sha={expected_sha} status={run.get('status')} conclusion={run.get('conclusion')}")
            if run.get("status") == "completed":
                if run.get("conclusion") == "success":
                    audit(f"PUBLIC_CI_SUCCESS sha={expected_sha} url={run.get('url','')}")
                    return run
                details = command([
                    "gh", "run", "view", str(run["databaseId"]), "-R", public_repo(product),
                    "--json", "jobs,url",
                ], timeout=120)
                view = json.loads(details.stdout)
                failed_jobs = [job.get("name", "unknown") for job in view.get("jobs", []) if job.get("conclusion") == "failure"]
                raise FlipError(
                    f"public CI failed for orphan commit {expected_sha}; job(s): "
                    f"{', '.join(failed_jobs) or 'unknown'}; run: {view.get('url', run.get('url',''))}"
                )
        else:
            audit(f"PUBLIC_CI_WAIT sha={expected_sha} status=not-visible")
        time.sleep(15)
    raise FlipError(f"public CI for orphan commit {expected_sha} did not finish successfully within {timeout_seconds // 60} minutes")


def _replace_public_history(product: str, stage: Path, old_refs: dict, backup_git: Path,
                            release_backups: list[dict], first_tag: str,
                            verify_dir: Path, release_bundle: dict | None = None,
                            preserve_release_tags: bool = False) -> dict:
    url = f"https://github.com/{public_repo(product)}.git"
    old_main = old_refs["main"]
    orphan_sha = command(["git", "-C", str(stage), "rev-parse", "HEAD"]).stdout.strip()
    public_mutated = False
    try:
        before_refs = command(["git", "ls-remote", "--heads", "--tags", url], timeout=300).stdout.splitlines()
        current_refs = {parts[1]: parts[0] for line in before_refs if len(parts := line.split()) == 2 and not parts[1].endswith("^{}")}
        if current_refs != old_refs["refs"]:
            raise FlipError("public refs changed after backup; refusing the in-place overwrite")
        _verify_public_release_snapshot(product, release_backups)
        audit(f"PUBLIC_REWRITE old_main={old_main} orphan_main={orphan_sha} lease_ref=refs/heads/main")
        command(["git", "-C", str(stage), "remote", "add", "origin", url])
        command(["git", "-C", str(stage), "push", f"--force-with-lease=refs/heads/main:{old_main}", "origin", f"{orphan_sha}:refs/heads/main"], timeout=900)
        public_mutated = True
        _wait_for_public_main(product, orphan_sha)
        public_ci = _wait_for_public_ci(product, orphan_sha)

        for ref in sorted(r for r in old_refs["refs"] if r.startswith("refs/heads/") and r != "refs/heads/main"):
            branch = ref.removeprefix("refs/heads/")
            _delete_public_ref(product, stage, url, branch)
            audit(f"PUBLIC_BRANCH_DELETED {branch}")
        if not preserve_release_tags:
            for item in release_backups:
                _delete_public_release(product, item["tagName"])
                audit(f"PUBLIC_RELEASE_DELETED tag={item['tagName']}")
        released_tags = {item["tagName"] for item in release_backups}
        if not preserve_release_tags:
            for ref in sorted(r for r in old_refs["refs"] if r.startswith("refs/tags/") and r.removeprefix("refs/tags/") not in released_tags):
                _delete_public_ref(product, stage, url, ref.removeprefix("refs/tags/"))
                audit(f"PUBLIC_TAG_DELETED {ref.removeprefix('refs/tags/')}")
            _wait_for_no_public_releases(product)
        for attempt in range(1, 31):
            residual = command(["git", "ls-remote", "--heads", "--tags", url], timeout=300).stdout.splitlines()
            residual_refs = [line for line in residual if not line.endswith("^{}") and (
                ("refs/heads/" in line and "refs/heads/main" not in line)
                or (not preserve_release_tags and "refs/tags/" in line)
            )]
            if not residual_refs:
                audit(f"PUBLIC_OLD_REFS_CLEARED attempt={attempt}")
                break
            audit(f"PUBLIC_OLD_REFS_WAIT attempt={attempt}/30 residual={';'.join(residual_refs)}")
            time.sleep(2)
        else:
            raise FlipError("public branches or tags remained after deletion")
        if preserve_release_tags:
            remaining = command(["git", "ls-remote", "--heads", "--tags", url], timeout=300).stdout.splitlines()
            actual_refs = {parts[1]: parts[0] for line in remaining if len(parts := line.split()) == 2 and not parts[1].endswith("^{}")}
            expected_tags = {ref: sha for ref, sha in old_refs["refs"].items() if ref.startswith("refs/tags/")}
            if {ref: sha for ref, sha in actual_refs.items() if ref.startswith("refs/tags/")} != expected_tags:
                raise FlipError("lmvideo public tags changed during the orphan main update")
            if set(ref for ref in actual_refs if ref.startswith("refs/heads/")) != {"refs/heads/main"}:
                raise FlipError("lmvideo public branch set differs from the single-main plan")

        latest = next((item for item in release_backups if item["tagName"] == first_tag), None)
        if latest is None:
            raise FlipError(f"latest release backup {first_tag} is missing")
        if release_bundle:
            release_dir = Path(release_bundle["bundle"])
            old_metadata = release_bundle["release"]
            notes = Path(release_bundle["notes_path"])
            asset_paths = release_bundle["asset_paths"]
            expected_asset_names = {path.name for path in asset_paths}
        else:
            release_dir = Path(latest["path"])
            old_metadata = json.loads((release_dir / "release-metadata.json").read_text(encoding="utf-8"))
            boundary = ("Releases up to and including v0.2.1 were published under the MIT License "
                        "(see the LICENSE asset of that release). Releases after v0.2.1 are published "
                        "under the Lattice Systems Personal Use License (this file).")
            notes = release_dir / "release-notes-replay.md"
            notes.write_text(old_metadata["body"].rstrip() + "\n\n" + boundary + "\n", encoding="utf-8")
            asset_paths = [release_dir / name for name in latest["assets"]]
            expected_asset_names = set(latest["assets"])
        release_name = old_metadata.get("name") or first_tag
        if preserve_release_tags:
            current_asset_names = {item.get("name") for item in old_metadata.get("assets", [])}
            replay_asset_names = {path.name for path in asset_paths}
            extra = sorted(replay_asset_names - current_asset_names)
            expected_extra = [] if "SHA256SUMS" in current_asset_names else ["SHA256SUMS"]
            if extra != expected_extra:
                raise FlipError(f"lmvideo replay is expected to add only a missing SHA256SUMS, got: {extra}")
            original_digests = {item.get("name"): item.get("digest") for item in old_metadata.get("assets", [])}
            replay_digests = {path.name: f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}" for path in asset_paths}
            for path in asset_paths:
                if path.name == "SHA256SUMS":
                    continue
                if original_digests.get(path.name) != replay_digests[path.name]:
                    raise FlipError(f"lmvideo existing tag asset changed during replay preparation: {path.name}")
            sums_asset = next(path for path in asset_paths if path.name == "SHA256SUMS")
            command(["gh", "release", "upload", first_tag, "-R", public_repo(product), "--clobber", str(sums_asset)], timeout=900)
            command(["gh", "release", "edit", first_tag, "-R", public_repo(product), "--title", release_name, "--notes-file", str(notes), "--latest"], timeout=300)
        else:
            create = ["gh", "release", "create", first_tag, "-R", public_repo(product), "--target", "main", "--title", release_name, "--notes-file", str(notes)]
            create.extend(str(path) for path in asset_paths)
            command(create, timeout=900)
        expected_asset_digests = {path.name: f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}" for path in asset_paths}
        published = _wait_for_public_latest_release(product, first_tag, expected_asset_digests)
        if published.get("tag_name") != first_tag or published.get("name") != release_name or published.get("body", "").rstrip() != notes.read_text(encoding="utf-8").rstrip():
            raise FlipError("re-published latest release metadata differs from the staged approved data")
        assets = {asset["name"]: asset for asset in published.get("assets", [])}
        if set(assets) != expected_asset_names:
            raise FlipError("re-published latest release asset names differ from the staged backup")
        for path in asset_paths:
            expected = hashlib.sha256(path.read_bytes()).hexdigest()
            if assets[path.name].get("digest") != f"sha256:{expected}":
                raise FlipError(f"re-published latest release asset changed: {path.name}")
        if verify_dir.exists():
            raise FlipError(f"release verification path already exists: {verify_dir}")
        verify_dir.mkdir(parents=True)
        command(["gh", "release", "download", first_tag, "-R", public_repo(product), "--dir", str(verify_dir)], timeout=900)
        downloaded = {path.name: path for path in verify_dir.iterdir() if path.is_file()}
        if set(downloaded) != expected_asset_names:
            raise FlipError("downloaded re-published release asset names do not match backup")
        staged_by_name = {path.name: path for path in asset_paths}
        for name, path in downloaded.items():
            if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(staged_by_name[name].read_bytes()).digest():
                raise FlipError(f"downloaded re-published release bytes differ: {name}")
        if "SHA256SUMS" in downloaded:
            command(["sha256sum", "-c", "SHA256SUMS"], cwd=verify_dir)
        if preserve_release_tags:
            live_release_tags = {item.get("tag_name") for item in json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases?per_page=100"]).stdout)}
            expected_release_tags = {item["tagName"] for item in release_backups}
            if live_release_tags != expected_release_tags:
                raise FlipError("lmvideo release tags changed while updating the latest SHA256SUMS")
        linux = verify_dir / f"{product}-linux-x64"
        command(["chmod", "+x", str(linux)])
        version = command([str(linux), "--version"]).stdout.strip()
        if not _version_contains_release(version, product, first_tag):
            raise FlipError(f"re-published binary returned an unexpected version: {version}")
        example_env, _example_host_scratch = _install_example_hosts(product, stage)
        examples_to_check = release_bundle["examples"] if release_bundle else ("eq_before_after.lms", "karplus_strong_harp.lms")
        for example in examples_to_check:
            url_example = f"https://raw.githubusercontent.com/{public_repo(product)}/main/examples/{example}"
            path = verify_dir / example
            command(["curl", "-fsSL", url_example, "-o", str(path)], timeout=120)
            command(["lmscript", "--check", str(path)], timeout=300, env=example_env)
            contents = path.read_text(encoding="utf-8")
            latest_copy = STAGING / f"{product}-{example}.latest.lms"
            updated, count = re.subn(rf"github:lmctl-ai/{re.escape(product)}@v[0-9]+\.[0-9]+\.[0-9]+", f"github:lmctl-ai/{product}@latest", contents, count=1)
            if count:
                latest_copy.write_text(updated, encoding="utf-8")
                command(["lmscript", "--check", str(latest_copy)], timeout=300, env=example_env)
        _wait_for_latest_release_tag(product, first_tag)
        audit(f"PUBLIC_RELEASE_REPUBLISHED tag={first_tag} url={published.get('html_url','')}")
        return {"release": published, "orphan_sha": orphan_sha, "public_ci": public_ci}
    except Exception as exc:
        if not public_mutated:
            main_result = command(["git", "ls-remote", url, "refs/heads/main"], check=False)
            observed = main_result.stdout.split()[0] if main_result.returncode == 0 and main_result.stdout.split() else ""
            public_mutated = observed == orphan_sha
        if public_mutated:
            try:
                if preserve_release_tags:
                    _rollback_public_tags_preserving_releases(product, backup_git, old_refs, release_backups, orphan_sha, first_tag, release_bundle)
                else:
                    _rollback_public_in_place(product, backup_git, old_refs, release_backups, orphan_sha)
                shutil.rmtree(stage / ".git", ignore_errors=True)
                audit("PUBLIC_ROLLBACK_COMPLETE public main/refs/releases restored")
            except Exception as rollback_error:
                raise FlipError(f"public replacement failed ({exc}); rollback also failed ({rollback_error})") from exc
        raise

def _rollback_public_in_place(product: str, backup_git: Path, old_refs: dict, release_backups: list[dict], orphan_sha: str) -> None:
    url = f"https://github.com/{public_repo(product)}.git"
    current = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases?per_page=100"]).stdout)
    for release in current:
        command(["gh", "api", "-X", "DELETE", f"repos/{public_repo(product)}/releases/{release['id']}"], timeout=300)
    old_main = old_refs["main"]
    command(["git", "--git-dir", str(backup_git), "push", f"--force-with-lease=refs/heads/main:{orphan_sha}", url, f"refs/heads/main:refs/heads/main"], timeout=900)
    command(["git", "--git-dir", str(backup_git), "push", "--mirror", url], timeout=900)
    restored = command(["git", "ls-remote", "--heads", "--tags", url], timeout=300).stdout.splitlines()
    actual = {parts[1]: parts[0] for line in restored if len(parts := line.split()) == 2 and not parts[1].endswith("^{}")}
    if actual != old_refs["refs"] or actual.get("refs/heads/main") != old_main:
        raise FlipError("rollback refs do not match the saved public history")
    _restore_public_releases(product, release_backups)


def _rollback_public_tags_preserving_releases(product: str, backup_git: Path, old_refs: dict,
                                              release_backups: list[dict], orphan_sha: str,
                                              latest_tag: str, release_bundle: dict) -> None:
    url = f"https://github.com/{public_repo(product)}.git"
    latest = next((item for item in release_backups if item["tagName"] == latest_tag), None)
    if latest is None:
        raise FlipError("cannot roll back lmvideo without its latest release snapshot")
    directory = Path(latest["path"])
    saved = json.loads((directory / "release-metadata.json").read_text(encoding="utf-8"))
    original_assets = {item.get("name"): item for item in saved.get("assets", [])}
    current = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases/tags/{latest_tag}"]).stdout)
    for asset in current.get("assets", []):
        old = original_assets.get(asset.get("name"))
        if old is None or old.get("digest") != asset.get("digest"):
            command(["gh", "api", "-X", "DELETE", f"repos/{public_repo(product)}/releases/assets/{asset['id']}"], timeout=300)
            if old is not None:
                original = directory / asset["name"]
                command(["gh", "release", "upload", latest_tag, "-R", public_repo(product), str(original)], timeout=900)
    command([
        "gh", "release", "edit", latest_tag, "-R", public_repo(product),
        "--title", saved.get("name") or latest_tag,
        "--notes-file", str(directory / "release-notes.md"),
        "--latest",
    ], timeout=300)
    command(["git", "--git-dir", str(backup_git), "push", f"--force-with-lease=refs/heads/main:{orphan_sha}", url,
             f"refs/heads/main:refs/heads/main"], timeout=900)
    command(["git", "--git-dir", str(backup_git), "push", "--mirror", url], timeout=900)
    restored = command(["git", "ls-remote", "--heads", "--tags", url], timeout=300).stdout.splitlines()
    actual = {parts[1]: parts[0] for line in restored if len(parts := line.split()) == 2 and not parts[1].endswith("^{}")}
    if actual != old_refs["refs"] or actual.get("refs/heads/main") != old_refs["main"]:
        raise FlipError("rollback refs do not match the saved lmvideo public history")
    audit("PUBLIC_ROLLBACK_COMPLETE lmvideo main/tags restored; existing releases retained")

def _restore_public_releases(product: str, release_backups: list[dict]) -> None:
    for item in release_backups:
        if not item.get("assets_complete", True):
            continue
        directory = Path(item["path"])
        metadata = json.loads((directory / "release-metadata.json").read_text(encoding="utf-8"))
        args = ["gh", "release", "create", metadata["tagName"], "-R", public_repo(product), "--title", metadata["name"], "--notes-file", str(directory / "release-notes.md")]
        if metadata.get("isDraft"):
            args.append("--draft")
        if metadata.get("isPrerelease"):
            args.append("--prerelease")
        args.extend(str(directory / name) for name in item["assets"])
        command(args, timeout=900)
        audit(f"ROLLBACK_RELEASE_RESTORED tag={metadata['tagName']} assets={len(item['assets'])}")


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
    if not _version_contains_release(version, product, first_tag):
        raise FlipError(f"republished binary returned an unexpected version: {version}")
    example_env, _example_host_scratch = _install_example_hosts(product, STAGING / f"{product}-public")
    for example in ("eq_before_after.lms", "karplus_strong_harp.lms"):
        url = f"https://raw.githubusercontent.com/{public_repo(product)}/main/examples/{example}"
        path = verify_dir / example
        command(["curl", "-fsSL", url, "-o", str(path)], timeout=120)
        command(["lmscript", "--check", str(path)], timeout=300, env=example_env)
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
    global AUDIT_LOG
    product = "lmaudio"
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    AUDIT_LOG = STAGING / f"lmaudio-inplace-flip-{stamp}.log"
    audit("METHOD in-place public history reset; no repository transfer; token values are never logged")
    audit("PREVIOUS_FAILURE git pull to lmctlhq returned 403 during transfer; previous transfer was reversed")
    audit("PREVIOUS_RETRY_STOPPED before mutation: lmctlhq API path redirected to lmctl-ai/lmaudio")
    if first_tag != "v0.2.1":
        raise FlipError("the approved lmaudio pilot must re-publish v0.2.1 unchanged")
    approval = Path.home() / "tools/closed-source-approved.txt"
    if not approval.is_file() or product not in {line.strip() for line in approval.read_text(encoding="utf-8").splitlines()}:
        raise FlipError("owner approval file must list lmaudio; no public changes started")
    token_path = Path.home() / ".config/lmctl/release_token"
    if not token_path.is_file() or token_path.stat().st_mode & 0o777 != 0o600 or token_path.stat().st_size == 0:
        raise FlipError("release-token file is missing, empty, or not mode 600; no token value was read")

    snapshot = git_snapshot(product, fetch=True)
    expected_origin = f"https://github.com/{public_repo(product)}.git"
    private_target = _repo_view_private(product)
    source_is_private = snapshot["origin"].rstrip("/") in {
        f"https://github.com/{private_repo(product)}.git", f"https://github.com/{private_repo(product)}"
    }
    valid_origins = {expected_origin, expected_origin.removesuffix(".git")}
    if source_is_private:
        valid_origins.update({f"https://github.com/{private_repo(product)}.git", f"https://github.com/{private_repo(product)}"})
    if snapshot["local_branch"] != "main" or not snapshot["clean"] or not snapshot["pushed"] or snapshot["origin"].rstrip("/") not in valid_origins:
        raise FlipError("lmaudio source checkout must be clean, on main, synchronized, and point at a known peer")
    if source_is_private and (not private_target.get("exists") or not private_target.get("private")):
        raise FlipError("local source points at lmctlhq/lmaudio, but that private peer is not verified")
    active = active_lmctl_members()
    if agents_for(product, active):
        raise FlipError("an active lmaudio session exists; stop before private mirror creation")
    ci = ci_latest(product, snapshot["ref"], private_repo(product) if source_is_private else public_repo(product))
    if not ci.get("ok"):
        raise FlipError(f"lmaudio main CI is not green: {ci.get('url','')} {ci.get('error','')}")

    root = snapshot["root"]
    stage = STAGING / f"{product}-public"
    manifest_path = STAGING / f"{product}-stage-manifest.json"
    if not stage.is_dir() or not manifest_path.is_file():
        raise FlipError(f"stage the public tree first: {stage}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("source_main_sha") != snapshot["ref"]:
        raise FlipError("lmaudio origin/main changed since staging; refresh the public tree")
    validation = validate_stage(product, stage, manifest.get("public_file_map", {}))
    if validation.get("private_source_references") or validation.get("secret_findings") or validation.get("missing_autorun"):
        raise FlipError("staged lmaudio public tree failed validation")
    expected_hashes = manifest.get("staged_file_sha256", {})
    actual_hashes = {p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in stage.rglob("*") if p.is_file() and ".git" not in p.parts}
    if actual_hashes != expected_hashes:
        raise FlipError("staged lmaudio tree differs from its reviewed manifest")
    boundary = ("Releases up to and including v0.2.1 were published under the MIT License "
                "(see the LICENSE asset of that release). Releases after v0.2.1 are published "
                "under the Lattice Systems Personal Use License (this file).")
    if boundary not in (stage / "README.md").read_text(encoding="utf-8") or not (stage / "LICENSE").read_text(encoding="utf-8").startswith(boundary):
        raise FlipError("staged README/LICENSE omit the approved lmaudio license boundary")
    if stage.joinpath(".git").exists():
        raise FlipError("public stage history already exists")

    metadata = _repo_view(product)
    if metadata.get("full_name", "").lower() != public_repo(product).lower() or metadata.get("private") or metadata.get("disabled") or metadata.get("default_branch") != "main":
        raise FlipError("public lmaudio identity/visibility/default branch is unexpected")
    private_scaffold = False if source_is_private else _check_private_target_free(product)
    pins, all_consumer_files = consumer_repositories(product)
    lmgallery_pin = GALLERY / "examples/39-audio-harmonics-slide.lms"
    if "github:lmctl-ai/lmaudio@v0.2.1" not in lmgallery_pin.read_text(encoding="utf-8"):
        raise FlipError("lmgallery lmaudio pin is not already v0.2.1; stop for review")
    command(["git", "-C", str(GALLERY), "diff", "--quiet", "HEAD", "--", "examples/39-audio-harmonics-slide.lms"])
    command(["git", "-C", str(GALLERY), "diff", "--cached", "--quiet", "HEAD", "--", "examples/39-audio-harmonics-slide.lms"])
    consumer_files = {consumer: paths for consumer, paths in all_consumer_files.items() if Path(consumer).resolve() != GALLERY.resolve()}
    untracked_docs = _untracked_consumer_docs(product, pins)
    validate_consumer_checkouts(product, list(consumer_files), active)

    run_stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_git = STAGING / f"lmaudio-public-history-{run_stamp}.git"
    refs_path = STAGING / f"lmaudio-public-refs-{run_stamp}.txt"
    release_backup_root = STAGING / f"lmaudio-release-set-{run_stamp}"
    verify_dir = STAGING / f"lmaudio-release-verify-{run_stamp}"
    public_main_result = command(["git", "ls-remote", f"https://github.com/{public_repo(product)}.git", "refs/heads/main"], timeout=300)
    if not public_main_result.stdout.split():
        raise FlipError("cannot resolve public main before backup")
    public_main = public_main_result.stdout.split()[0]
    old_refs = _backup_public_refs(product, public_main, backup_git, refs_path)
    release_backups = _backup_all_public_releases(product, release_backup_root, run_stamp)
    staged_latest, staged_latest_assets = _release_files(product, STAGING / f"{product}-release", first_tag)
    if not any(item["tagName"] == first_tag for item in release_backups) or len(staged_latest_assets) != 8:
        raise FlipError("latest release backup set does not match the reviewed v0.2.1 assets")
    local_ref_lines = command(["git", "-C", str(root), "for-each-ref", "--format=%(objectname) %(refname)", "refs/heads", "refs/tags"]).stdout.splitlines()
    local_refs = {parts[1]: parts[0] for line in local_ref_lines if len(parts := line.split()) == 2}
    if not source_is_private and local_refs != old_refs["refs"]:
        raise FlipError("local source clone refs do not include every public branch/tag; refusing an incomplete private mirror")
    audit(f"PREFLIGHT_PASS public_main={snapshot['ref']} ref_count={len(old_refs['refs'])} release_count={len(release_backups)} refs_backup={refs_path} release_backup={release_backup_root}")

    # Step 1: private source peer, with the existing history and tags mirrored in place.
    if not source_is_private and not private_scaffold:
        create = ["gh", "repo", "create", private_repo(product), "--private"]
        if metadata.get("description"):
            create.extend(["--description", metadata["description"]])
        if metadata.get("homepage"):
            create.extend(["--homepage", metadata["homepage"]])
        command(create, timeout=300)
        _wait_for_repo_identity(product, private=True)
    private_url = f"https://github.com/{private_repo(product)}.git"
    # The mirrored source contains push-triggered build workflows. Keep Actions
    # disabled until the private workflow is replaced and the test-only input exists.
    if not source_is_private:
        _set_repo_actions_enabled(product, False)
        command(["git", "-C", str(root), "push", "--mirror", private_url], timeout=900)
        command(["gh", "repo", "edit", private_repo(product), "--default-branch", "main"], timeout=300)
        for topic in metadata.get("topics", []):
            command(["gh", "repo", "edit", private_repo(product), "--add-topic", topic], timeout=300)
        _assert_private_mirror_refs(product, old_refs["refs"])
        audit(f"PRIVATE_MIRROR_COMPLETE repo={private_repo(product)} main={old_refs['main']} refs={len(old_refs['refs'])}")
    else:
        private_main = command(["git", "ls-remote", private_url, "refs/heads/main"], timeout=300).stdout.split()[0]
        if private_main != snapshot["ref"]:
            raise FlipError("existing private main no longer matches the clean local source checkout")
        secrets = json.loads(command(["gh", "secret", "list", "-R", private_repo(product), "--json", "name"]).stdout)
        if not any(item.get("name") == "RELEASE_TOKEN" for item in secrets):
            raise FlipError("existing private peer is missing RELEASE_TOKEN")
        audit(f"PRIVATE_RESUME_VERIFIED repo={private_repo(product)} main={private_main}")

    # Step 2: install the secret and test the private CI publishing path without building.
    if source_is_private:
        private_sha = snapshot["ref"]
        private_ci = ci
    else:
        _set_release_secret_from_file(product)
        private_sha = _install_private_ci(product, root, first_tag)
        _set_repo_actions_enabled(product, True)
        private_ci = _run_publish_test(product, private_sha)
    audit(f"PRIVATE_PUBLISH_TEST_SUCCESS url={private_ci.get('url','')}")

    # Step 3: update the existing public repo only after private mirror and token test pass.
    if "github:lmctl-ai/lmaudio@v0.2.1" not in lmgallery_pin.read_text(encoding="utf-8"):
        raise FlipError("lmgallery pin changed after preflight; stop before public rewrite")
    for path, expected_hash in untracked_docs.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            raise FlipError(f"untracked consumer doc changed after preflight; stop before public rewrite: {path}")
    try:
        _prepare_orphan_commit(stage, product)
    except Exception:
        shutil.rmtree(stage / ".git", ignore_errors=True)
        raise
    rewrite = _replace_public_history(product, stage, old_refs, backup_git, release_backups, first_tag, verify_dir)
    _update_local_checkouts(product, root)
    updated_docs = _update_untracked_consumer_docs(product, first_tag, untracked_docs)
    audit(f"PILOT_COMPLETE private_ci={private_ci.get('url','')} public_release={rewrite['release'].get('html_url','')} local_docs_updated={len(updated_docs)}")
    print(f"FLIP COMPLETE: private mirror and publish-test passed; public {first_tag} replayed in place with assets verified; source checkout private; public checkout cloned; log={AUDIT_LOG}")
    return 0


def apply_general_product(product: str, first_tag: str) -> int:
    global AUDIT_LOG
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    AUDIT_LOG = STAGING / f"{product}-inplace-flip-{stamp}.log"
    approval = Path.home() / "tools/closed-source-approved.txt"
    if not approval.is_file() or product not in {line.strip() for line in approval.read_text(encoding="utf-8").splitlines()}:
        raise FlipError(f"owner approval file must list {product}; no public changes started")
    token_path = Path.home() / ".config/lmctl/release_token"
    if not token_path.is_file() or token_path.stat().st_mode & 0o777 != 0o600 or token_path.stat().st_size == 0:
        raise FlipError("release-token file is missing, empty, or not mode 600; no token value was read")

    snapshot = git_snapshot(product, fetch=True)
    expected_origin = f"https://github.com/{public_repo(product)}.git"
    private_target = _repo_view_private(product)
    private_origin = f"https://github.com/{private_repo(product)}.git"
    source_is_private = snapshot["origin"].rstrip("/") in {private_origin, private_origin.removesuffix(".git")}
    valid_origins = {expected_origin, expected_origin.removesuffix(".git")}
    if source_is_private:
        valid_origins.update({private_origin, private_origin.removesuffix(".git")})
    if (snapshot["local_branch"] != "main" or not snapshot["clean"] or not snapshot["pushed"]
            or snapshot["origin"].rstrip("/") not in valid_origins):
        raise FlipError(f"{product} source checkout must be clean, on main, synchronized, and point at a known peer")
    if source_is_private and (not private_target.get("exists") or not private_target.get("private")):
        raise FlipError(f"local source points at {private_repo(product)}, but that private peer is not verified")
    active = active_lmctl_members()
    product_sessions = agents_for(product, active)
    if product == "lmfilament":
        # The active Lead session is the owner directing this authorized flip;
        # other lmfilament sessions still block it.
        product_sessions = [member for member in product_sessions if member.lower() != "lmfilament.lmctl:lead"]
    if product_sessions:
        raise FlipError(f"an active {product} session exists; stop before private peer creation")
    root = snapshot["root"]
    if product in {"lmoffice", "lmpdf"} and not source_is_private:
        recent = command(["git", "-C", str(snapshot["root"]), "log", "--since=30 minutes ago", "--format=%H", "origin/main"], timeout=120).stdout.strip()
        if recent:
            raise FlipError(f"{product} origin/main has a commit from the last 30 minutes; defer this product")
    ci = ci_latest(product, snapshot["ref"], private_repo(product) if source_is_private else public_repo(product))
    if product == "lmfilament" and source_is_private and not ci.get("ok"):
        ci = _reuse_lmfilament_publish_test(snapshot["ref"], snapshot["root"])
    current_private_workflow = root / ".github/workflows/ci.yml"
    current_private_text = current_private_workflow.read_text(encoding="utf-8") if current_private_workflow.is_file() else ""
    private_ci_ready = "  publish-test:" in current_private_text and "RELEASE_TOKEN" in current_private_text and (root / "scripts/release-to-public.sh").is_file()
    if not ci.get("ok") and not (source_is_private and not private_ci_ready):
        raise FlipError(f"{product} main CI is not green: {ci.get('url','')} {ci.get('error','')}")
    if source_is_private and not private_ci_ready:
        public_main_result = command(["git", "ls-remote", f"https://github.com/{public_repo(product)}.git", "refs/heads/main"], timeout=300)
        if not public_main_result.stdout.split():
            raise FlipError(f"cannot resolve original public {product} main during private mirror recovery")
        public_ci = ci_latest(product, public_main_result.stdout.split()[0], public_repo(product))
        if not public_ci.get("ok"):
            raise FlipError(f"original public {product} main CI is not green: {public_ci.get('url','')} {public_ci.get('error','')}")

    stage = STAGING / f"{product}-public"
    manifest_path = STAGING / f"{product}-stage-manifest.json"
    if not stage.is_dir() or not manifest_path.is_file():
        raise FlipError(f"stage the public tree first: {stage}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("source_main_sha") != snapshot["ref"]:
        raise FlipError(f"{product} origin/main changed since staging; refresh the public tree")
    validation = validate_stage(product, stage, manifest.get("public_file_map", {}))
    if validation.get("private_source_references") or validation.get("secret_findings") or validation.get("missing_autorun"):
        raise FlipError(f"staged {product} public tree failed validation")
    actual_hashes = {p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in stage.rglob("*") if p.is_file() and ".git" not in p.parts}
    if actual_hashes != manifest.get("staged_file_sha256", {}):
        raise FlipError(f"staged {product} tree differs from its reviewed manifest")
    boundary = (f"Releases up to and including {first_tag} were published under the MIT License "
                f"(see the LICENSE asset of that release). Releases after {first_tag} are published "
                "under the Lattice Systems Personal Use License (this file).")
    if boundary not in (stage / "README.md").read_text(encoding="utf-8") or not (stage / "LICENSE").read_text(encoding="utf-8").startswith(boundary):
        raise FlipError(f"staged {product} README/LICENSE omit the approved license boundary")
    if (stage / ".git").exists():
        raise FlipError(f"staged {product} public tree already has Git history")

    metadata = _repo_view(product)
    if metadata.get("full_name", "").lower() != public_repo(product).lower() or metadata.get("private") or metadata.get("disabled") or metadata.get("default_branch") != "main":
        raise FlipError(f"public {product} identity/visibility/default branch is unexpected")
    private_scaffold = False if source_is_private else _check_private_target_free(product)
    pins, consumers = consumer_repositories(product)
    validate_consumer_checkouts(product, list(consumers), active)
    latest = json.loads(command(["gh", "api", f"repos/{public_repo(product)}/releases/latest"]).stdout)
    if latest.get("tag_name") != first_tag:
        raise FlipError(f"{first_tag} is not the latest public release of {product}")

    backup_git = STAGING / f"{product}-public-history-{stamp}.git"
    refs_path = STAGING / f"{product}-public-refs-{stamp}.txt"
    release_backup_root = STAGING / f"{product}-release-set-{stamp}"
    verify_dir = STAGING / f"{product}-release-verify-{stamp}"
    public_main_result = command(["git", "ls-remote", f"https://github.com/{public_repo(product)}.git", "refs/heads/main"], timeout=300)
    if not public_main_result.stdout.split():
        raise FlipError(f"cannot resolve public {product} main before backup")
    old_refs = _backup_public_refs(product, public_main_result.stdout.split()[0], backup_git, refs_path)
    release_bundle = _prepare_release_bundle(product, root, first_tag, stamp)
    release_backups = _snapshot_public_releases(product, release_backup_root, stamp, first_tag, release_bundle)
    latest_backup = next((item for item in release_backups if item["tagName"] == first_tag), None)
    if latest_backup is None or not latest_backup.get("assets_complete"):
        raise FlipError(f"latest release backup {first_tag} is missing")
    local_ref_lines = command(["git", "-C", str(root), "for-each-ref", "--format=%(objectname) %(refname)", "refs/heads", "refs/tags"]).stdout.splitlines()
    source_refs = {parts[1]: parts[0] for line in local_ref_lines if len(parts := line.split()) == 2}
    public_refs_to_match = {ref: sha for ref, sha in old_refs["refs"].items()
                            if not (source_is_private and ref == "refs/heads/main")}
    missing_source_refs = sorted(ref for ref, sha in public_refs_to_match.items() if source_refs.get(ref) != sha)
    if missing_source_refs:
        raise FlipError(f"local source mirror is missing or differs from public refs: {', '.join(missing_source_refs)}")
    if source_is_private:
        ancestry = command(["git", "-C", str(root), "merge-base", "--is-ancestor", old_refs["main"], snapshot["ref"]], check=False)
        if ancestry.returncode:
            raise FlipError("existing private main is not descended from the original public main")
    if product == "lmvideo":
        release_tags = {item["tagName"] for item in release_backups}
        tag_refs = {ref.removeprefix("refs/tags/") for ref in old_refs["refs"] if ref.startswith("refs/tags/")}
        checked_pins = set()
        for line in pins:
            for pattern in (
                r"github:lmctl-ai/lmvideo@(v\d+\.\d+\.\d+)",
                r"github\.com/lmctl-ai/lmvideo/releases/download/(v\d+\.\d+\.\d+)",
            ):
                checked_pins.update(re.findall(pattern, line))
            checked_pins.update(re.findall(r"github\.com/lmctl-ai/lmvideo/releases/tag/(v\d+\.\d+\.\d+)", line))
        missing_pins = sorted(tag for tag in checked_pins if tag not in tag_refs or tag not in release_tags)
        if missing_pins:
            raise FlipError(f"lmvideo consumer pins reference missing release tags: {', '.join(missing_pins)}")
        audit(f"LMVIDEO_PIN_INVENTORY_VERIFIED pins={len(checked_pins)} preserved_tags={len(release_tags)}")
    audit(f"PREFLIGHT_PASS public_main={old_refs['main']} source_main={snapshot['ref']} release={first_tag} ref_count={len(old_refs['refs'])} pin_count={len(pins)}")

    # Preserve the full source tree privately before replacing public refs.
    if not source_is_private and not private_scaffold:
        create = ["gh", "repo", "create", private_repo(product), "--private"]
        if metadata.get("description"):
            create.extend(["--description", metadata["description"]])
        if metadata.get("homepage"):
            create.extend(["--homepage", metadata["homepage"]])
        command(create, timeout=300)
        _wait_for_repo_identity(product, private=True)
    private_url = f"https://github.com/{private_repo(product)}.git"
    if source_is_private:
        private_main = command(["git", "ls-remote", private_url, "refs/heads/main"], timeout=300).stdout.split()[0]
        if private_main != snapshot["ref"]:
            raise FlipError(f"existing private {product} main no longer matches the clean local source checkout")
        _assert_private_mirror_refs(product, source_refs)
        secrets = json.loads(command(["gh", "secret", "list", "-R", private_repo(product), "--json", "name"]).stdout)
        actions = json.loads(command(["gh", "api", f"repos/{private_repo(product)}/actions/permissions"]).stdout)
        workflow_path = root / ".github/workflows/ci.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8") if workflow_path.is_file() else ""
        private_ci_ready = "  publish-test:" in workflow_text and "RELEASE_TOKEN" in workflow_text and (root / "scripts/release-to-public.sh").is_file()
        has_secret = any(item.get("name") == "RELEASE_TOKEN" for item in secrets)
        if private_ci_ready:
            if not has_secret:
                _set_release_secret_from_file(product)
            private_sha = snapshot["ref"]
            if actions.get("enabled") is not True:
                if not ci.get("ok"):
                    raise FlipError(f"private Actions are disabled and no successful recorded publisher check exists for {product}")
                private_ci = ci
            else:
                private_ci = ci if ci.get("ok") else _run_publish_test(product, private_sha)
        else:
            _set_release_secret_from_file(product)
            private_sha = _install_private_ci(product, root, first_tag)
            _set_repo_actions_enabled(product, True)
            private_ci = _run_publish_test(product, private_sha)
        audit(f"PRIVATE_RESUME_VERIFIED repo={private_repo(product)} main={private_sha} publisher_ready={private_ci_ready}")
    else:
        _set_repo_actions_enabled(product, False)
        command(["git", "-C", str(root), "push", "--mirror", private_url], timeout=900)
        command(["gh", "repo", "edit", private_repo(product), "--default-branch", "main"], timeout=300)
        for topic in metadata.get("topics", []):
            command(["gh", "repo", "edit", private_repo(product), "--add-topic", topic], timeout=300)
        _assert_private_mirror_refs(product, source_refs)
        _set_release_secret_from_file(product)
        private_sha = _install_private_ci(product, root, first_tag)
        _set_repo_actions_enabled(product, True)
        private_ci = _run_publish_test(product, private_sha)
    audit(f"PRIVATE_PUBLISH_TEST_SUCCESS url={private_ci.get('url','')}")

    updated_consumers = [] if product == "lmvideo" else _update_consumer_pins(product, first_tag, pins, root)
    if updated_consumers:
        audit(f"CONSUMER_PINS_UPDATED repos={','.join(updated_consumers)}")

    _prepare_orphan_commit(stage, product)
    rewrite = _replace_public_history(
        product, stage, old_refs, backup_git, release_backups, first_tag, verify_dir, release_bundle,
        preserve_release_tags=product == "lmvideo",
    )
    _update_local_checkouts(product, root)
    audit(f"FLIP_COMPLETE product={product} private_ci={private_ci.get('url','')} public_ci={rewrite['public_ci'].get('url','')} release={rewrite['release'].get('html_url','')} consumer_repos_updated={len(updated_consumers)}")
    print(f"FLIP COMPLETE: {product} private mirror, publish-test, public-content CI, release replay, and local checkouts verified; log={AUDIT_LOG}")
    return 0

def apply_flip(product: str, first_tag: str) -> int:
    if product == "lmaudio":
        return apply_lmaudio_pilot(first_tag)
    if product in {"lmdraw", "lmvideo", "lmoffice", "lmpdf", "lmmagnum", "lmimg", "lmcad", "lmfilament"}:
        return apply_general_product(product, first_tag)
    raise FlipError(f"no flip implementation is enabled for {product}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory, stage, and owner-gate a public/private peer repository flip")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true", help="read-only plan (default)")
    modes.add_argument("--stage", action="store_true", help="write a public-only tree under /home/mma/staging/closed-source")
    modes.add_argument("--apply", action="store_true", help="mirror private source then reset public content in place under approval")
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
