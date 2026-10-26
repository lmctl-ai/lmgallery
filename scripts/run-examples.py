#!/usr/bin/env python3
"""Run each showcase in a new empty directory, retaining output and logs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from check_gallery import preview_info, showcase_width_ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", action="store_true")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--only", help="script filename or leading two-digit number")
    args = parser.parse_args()
    assert shutil.which("lmctl"), "lmctl is required; npm install -g @lmctl-ai/lmctl"
    examples = json.loads((ROOT / "showcases.json").read_text())
    if args.only:
        examples = [e for e in examples if Path(e["file"]).name == args.only or Path(e["file"]).name.startswith(args.only + "-")]
        assert examples, f"no matching example: {args.only}"
    batch = Path(tempfile.mkdtemp(prefix="lmgallery-verify-"))
    records = []
    for e in examples:
        work = batch / Path(e["file"]).stem
        work.mkdir()
        assert not list(work.iterdir()), "verification directory is not empty"
        target = "https://raw.githubusercontent.com/lmctl-ai/lmgallery/main/" + e["file"] if args.urls else str(ROOT / e["file"])
        print(f"RUN {target}\n  empty directory: {work}", flush=True)
        result = subprocess.run(["lmctl", target], cwd=work, capture_output=True, text=True, timeout=900)
        (work / "autorun.log").write_text(result.stdout + result.stderr)
        if result.returncode:
            raise SystemExit(f"FAILED {e['file']} (exit {result.returncode}); log: {work / 'autorun.log'}\n{result.stdout[-1500:]}\n{result.stderr[-1500:]}")
        output = work / e["output"]
        assert output.is_file(), f"autorun did not render {e['output']}; log: {work / 'autorun.log'}"
        width, height = preview_info(output)
        assert showcase_width_ok(output), f"unexpected showcase width: {width}"
        if args.update:
            shutil.copyfile(output, ROOT / e["image"])
        records.append({"script": e["file"], "target": target, "workdir": str(work), "exit_code": result.returncode, "output": e["output"], "width": width, "height": height, "bytes": output.stat().st_size, "sha256": hashlib.sha256(output.read_bytes()).hexdigest()})
        print(f"PASS {e['file']}: {width}×{height}, {output.stat().st_size} bytes", flush=True)
    (batch / "results.json").write_text(json.dumps(records, indent=2) + "\n")
    print(f"PASS: {len(records)} empty-directory executions; evidence: {batch / 'results.json'}")


if __name__ == "__main__":
    main()

