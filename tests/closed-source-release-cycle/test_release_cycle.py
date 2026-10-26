#!/usr/bin/env python3
"""Offline contract tests for scripts/closed-source/release-cycle.sh.

The command stubs deliberately fail if a real token or mutating GitHub call is
attempted.  The runner can be exercised locally with:

    python3 -m unittest discover -s tests/closed-source-release-cycle -v
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
import shutil


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts/closed-source/release-cycle.sh"


class ReleaseCycleContract(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="release-cycle-test-"))
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.state = self.tmp / "state"
        self.log = self.tmp / "commands.log"
        self._write_stub("gh", """#!/usr/bin/env bash
set -euo pipefail
printf 'gh %q\\n' "$@" >> "${STUB_LOG:?}"
case " $* " in
  *' actions/permissions '*) cat <<'JSON'
{"enabled":${STUB_ACTIONS:-false},"allowed_actions":"all"}
JSON
    ;;
  *' release view '*--json*) printf '%s\\n' '{"tagName":"v0.2.1","isPrerelease":true}' ;;
  *' release view '*) exit 0 ;;
  *' release list '*) printf '%s\\n' 'v0.2.1' ;;
  *' release download '*) : "${DOWNLOAD_DIR:?}"; printf '#!/bin/sh\\n[ "$1" = --version ] && echo "lmaudio 0.2.1"\\n[ "$1" = --dsl-schema ] && echo schema\\n' > "$DOWNLOAD_DIR/lmaudio-linux-x64"; chmod +x "$DOWNLOAD_DIR/lmaudio-linux-x64"; printf 'arm asset\\n' > "$DOWNLOAD_DIR/lmaudio-linux-arm64"; printf 'MIT\\n' > "$DOWNLOAD_DIR/LICENSE"; printf 'MIT\\n' > "$DOWNLOAD_DIR/THIRD_PARTY_NOTICES"; [ "${STUB_COPYLEFT:-false}" = true ] && printf 'GPL-3.0-only\\n' > "$DOWNLOAD_DIR/THIRD_PARTY_NOTICES"; sha256sum "$DOWNLOAD_DIR"/lmaudio-linux-* "$DOWNLOAD_DIR"/LICENSE "$DOWNLOAD_DIR"/THIRD_PARTY_NOTICES > "$DOWNLOAD_DIR/SHA256SUMS"; [ "${STUB_CORRUPT:-false}" = true ] && printf '%064d  lmaudio-linux-x64\\n' 0 > "$DOWNLOAD_DIR/SHA256SUMS" ;;
  *' release edit '*) printf '%s\\n' 'promoted' ;;
  *' release create '*) printf '%s\\n' 'created' ;;
esac
""")
        # Keep the fixture in a separately reviewable executable; the inline
        # fallback above is retained for easy diagnosis in older checkouts.
        fixture = Path(__file__).parent / "stubs/gh"
        shutil.copy2(fixture, self.bin / "gh")
        (self.bin / "gh").chmod((self.bin / "gh").stat().st_mode | stat.S_IXUSR)
        self._write_stub("npm", """#!/usr/bin/env bash
set -euo pipefail
printf 'npm %q\\n' "$@" >> "${STUB_LOG:?}"
""")
        self._write_stub("lmscript", """#!/usr/bin/env bash
set -euo pipefail
printf 'lmscript %q\\n' "$@" >> "${STUB_LOG:?}"
case "$*" in *'github:lmctl-ai/lmaudio@latest'*) echo 'tag: v0.2.1';; esac
if [ "${STUB_EXAMPLE_FAIL:-false}" = true ] && [[ "$*" == *"--check"* ]]; then exit 17; fi
exit 0
""")
        self._write_stub("readelf", """#!/usr/bin/env bash
set -euo pipefail
printf 'readelf %q\\n' "$@" >> "${STUB_LOG:?}"
case "$1" in
  -h) case "$*" in *arm64*) if [ "${STUB_ARM_WRONG:-false}" = true ]; then printf 'Class: ELF64\\nMachine: Advanced Micro Devices X86-64\\n'; else printf 'Class: ELF64\\nMachine: AArch64\\n'; fi ;; *) printf 'Class: ELF64\\nMachine: Advanced Micro Devices X86-64\\n' ;; esac ;;
  --version-info) if [ "${STUB_GLIBC_NEW:-false}" = true ]; then printf 'Name: GLIBC_2.36\\n'; else printf 'Name: GLIBC_2.35\\n'; fi ;;
esac
""")
        self.env = os.environ.copy()
        isolated_home = self.tmp / 'home'
        isolated_home.mkdir()
        self.env.update({"PATH": f"{self.bin}:{self.env['PATH']}", "STUB_LOG": str(self.log),
                         "HOME": str(isolated_home),
                         "RELEASE_CYCLE_STATE_DIR": str(self.state), "DOWNLOAD_DIR": str(self.tmp / "download")})
        (self.tmp / "download").mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_stub(self, name, body):
        path = self.bin / name
        path.write_text(body)
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def run_cycle(self, *args):
        return subprocess.run([str(RUNNER), "lmaudio", *args], env=self.env,
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def test_dry_run_is_read_only_and_token_free(self):
        result = self.run_cycle("--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("dry-run", result.stdout.lower())
        calls = self.log.read_text() if self.log.exists() else ""
        self.assertNotIn("release create", calls)
        self.assertNotIn("release edit", calls)
        self.assertNotIn("RELEASE_TOKEN", result.stdout)

    def test_disabled_actions_refuses_dispatch_with_reenable_hint(self):
        result = self.run_cycle()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Private Actions are disabled", result.stdout)
        self.assertIn("repos/lmctlhq/lmaudio/actions/permissions", result.stdout)
        self.assertIn("enabled=true", result.stdout)
        calls = self.log.read_text() if self.log.exists() else ""
        self.assertNotIn("workflow_dispatch", calls)
        self.assertNotIn("release create", calls)

    def test_promotion_uses_explicit_latest_and_no_rebuild(self):
        # A pre-existing staged release is verified and promoted; no workflow
        # dispatch, npm install, or source build is allowed in this path.
        self.env["STUB_ACTIONS"] = "true"
        result = self.run_cycle("--tag", "v0.2.1", "--promote")
        self.assertEqual(result.returncode, 0, result.stdout)
        calls = self.log.read_text() if self.log.exists() else ""
        self.assertIn("release download", calls)
        self.assertIn("release edit", calls)
        self.assertNotIn("npm", calls)
        self.assertNotIn("workflow run", calls)

    def test_corrupt_checksum_is_rejected(self):
        self.env["STUB_ACTIONS"] = "true"
        self.env["STUB_CORRUPT"] = "true"
        result = self.run_cycle("--tag", "v0.2.1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum", result.stdout.lower())

    def test_new_glibc_and_copyleft_are_rejected(self):
        for key in ("STUB_GLIBC_NEW", "STUB_COPYLEFT"):
            with self.subTest(key=key):
                self.env["STUB_ACTIONS"] = "true"
                self.env[key] = "true"
                result = self.run_cycle("--tag", "v0.2.1")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("glibc" if key == "STUB_GLIBC_NEW" else "GPL/AGPL", result.stdout)
                self.env.pop(key)

    def test_dispatch_waits_and_finds_prerelease(self):
        self.env["STUB_ACTIONS"] = "true"
        result = self.run_cycle("--poll-seconds", "0.01")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Promote with:", result.stdout)
        self.assertIn("workflow run", self.log.read_text())

    def test_old_private_workflow_is_refused_before_dispatch(self):
        self.env["STUB_ACTIONS"] = "true"
        self.env["STUB_OLD_WORKFLOW"] = "true"
        result = self.run_cycle("--poll-seconds", "0.01")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("workflow", result.stdout.lower())
        self.assertNotIn("workflow run", self.log.read_text())

    def test_budget_annotation_refuses_dispatch(self):
        self.env["STUB_ACTIONS"] = "true"
        self.env["STUB_BUDGET"] = "true"
        result = self.run_cycle()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("budget", result.stdout.lower())

    def test_wrong_arm_architecture_is_rejected(self):
        self.env["STUB_ACTIONS"] = "true"
        self.env["STUB_ARM_WRONG"] = "true"
        result = self.run_cycle("--tag", "v0.2.1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("aarch64", result.stdout.lower())

    def test_public_example_failure_is_reported(self):
        self.env["STUB_ACTIONS"] = "true"
        self.env["STUB_EXAMPLE_FAIL"] = "true"
        result = self.run_cycle("--tag", "v0.2.1")
        self.assertNotEqual(result.returncode, 0)
        reports = list(self.state.rglob("report.json"))
        self.assertTrue(reports)
        self.assertEqual(json.loads(reports[0].read_text())["phase"], "public-examples")

    def test_token_is_redacted_from_report(self):
        self.env["STUB_ACTIONS"] = "true"
        self.env["GH_TOKEN"] = "sentinel-secret-token"
        result = self.run_cycle("--tag", "v0.2.1")
        report_files = list(self.state.rglob("report.json"))
        self.assertTrue(report_files)
        self.assertNotIn("sentinel-secret-token", report_files[0].read_text())

    def test_failure_report_has_phase_command_log_tail_and_no_token(self):
        self._write_stub("gh", """#!/usr/bin/env bash
set -eu
printf 'gh %q\\n' "$@" >> "${STUB_LOG:?}"
echo 'simulated failure' >&2
exit 42
""")
        result = self.run_cycle("--tag", "v0.2.1")
        self.assertNotEqual(result.returncode, 0)
        reports = list(self.state.rglob("*.json"))
        self.assertTrue(reports, result.stdout)
        report = json.loads(reports[0].read_text())
        self.assertIn("phase", report)
        self.assertIn("command", report)
        self.assertIn("last_lines", report)
        self.assertLessEqual(len(report["last_lines"]), 80)
        serialized = json.dumps(report)
        self.assertNotIn("RELEASE_TOKEN", serialized)


if __name__ == "__main__":
    unittest.main()
