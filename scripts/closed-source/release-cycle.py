#!/usr/bin/env python3
"""Stage in private Actions, verify public Linux assets locally, explicitly promote."""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time

PRODUCTS = ('lmaudio', 'lmcad', 'lmdraw', 'lmfilament', 'lmimg', 'lmmagnum', 'lmoffice', 'lmpdf', 'lmvideo')
HERE = Path(__file__).resolve().parent
FIELDS = 'tagName,isPrerelease,isDraft,assets,body,targetCommitish'


class CycleError(Exception):
    pass


class Cycle:
    def __init__(self, args):
        self.args = args
        self.product = args.product
        self.repo = f'lmctl-ai/{args.product}'
        self.private = f'lmctlhq/{args.product}'
        self.phase = 'preflight'
        self.command = []
        self.log = None
        self.counter = 0
        self.secrets = [os.environ[k] for k in ('GH_TOKEN', 'GITHUB_TOKEN') if os.environ.get(k)]
        token_file = Path.home() / '.config/lmctl/release_token'
        self.token = token_file.read_text().strip() if token_file.is_file() else ''
        if self.token:
            self.secrets.append(self.token)
        state = args.state_dir or Path(os.environ.get('RELEASE_CYCLE_STATE_DIR', Path.home() / '.local/state/lmctl/closed-source-releases'))
        self.root = state / f'{args.product}-{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%S}-{os.getpid()}'
        self.root.mkdir(parents=True)
        self.report = {'product': self.product, 'status': 'running', 'phase': self.phase, 'steps': []}

    def redact(self, value):
        text = str(value)
        for secret in self.secrets:
            text = text.replace(secret, '[redacted]')
        return re.sub(r'(?:github_pat_|gh[pousr]_)[A-Za-z0-9_]+', '[redacted]', text)

    def run(self, argv, *, cwd=None, env=None, check=True, timeout=900):
        self.command = list(map(str, argv))
        self.counter += 1
        self.log = self.root / f'{self.counter:03d}-{self.phase}.log'
        clean = os.environ.copy()
        clean.pop('GH_TOKEN', None)
        clean.pop('GITHUB_TOKEN', None)
        clean.pop('GH_DEBUG', None)
        private_call = any('lmctlhq/' in word for word in self.command)
        if self.command[0] == 'gh' and self.token and not private_call:
            clean['GH_TOKEN'] = self.token
        elif self.command[0] == 'gh' and not private_call:
            for key in ('GH_TOKEN', 'GITHUB_TOKEN'):
                if os.environ.get(key):
                    clean[key] = os.environ[key]
        clean.update(env or {})
        started = time.monotonic()
        try:
            p = subprocess.run(self.command, cwd=cwd, env=clean, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, timeout=timeout)
            output = self.redact(p.stdout)
            self.log.write_text(output)
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.log.write_text(self.redact(str(exc)))
            raise CycleError(self.redact(str(exc))) from exc
        self.report['steps'].append({'phase': self.phase, 'command': self.command, 'log_path': str(self.log),
                                     'exit_code': p.returncode, 'seconds': round(time.monotonic() - started, 2)})
        if check and p.returncode:
            if private_call and re.search(r'spending limit|payments? (?:have )?failed|budget.*(?:exhaust|exceed)', output, re.I):
                raise CycleError(f'Private Actions billing/budget is blocked. Resolve billing first; owner re-enable command: {self.reenable_hint()}')
            raise CycleError(f'Command exited {p.returncode}: {shlex.join(self.command)}')
        return p.returncode, output.strip()

    def gh_json(self, *args, check=True):
        code, text = self.run(['gh', *args], check=check)
        if code:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise CycleError(f'Invalid GitHub JSON: {exc}') from exc

    def require(self, value, message):
        if not value:
            raise CycleError(message)

    def reenable_hint(self):
        return f'gh api repos/{self.private}/actions/permissions -X PUT -F enabled=true'

    def dispatch(self):
        self.phase = 'actions-preflight'
        permissions = self.gh_json('api', f'repos/{self.private}/actions/permissions')
        self.require(permissions.get('enabled') is True,
                     f'Private Actions are disabled; no dispatch attempted. Owner re-enable command: {self.reenable_hint()}')
        # Stop proactively on GitHub's recent billing/account lock annotations.
        runs = self.gh_json('api', f'repos/{self.private}/actions/runs?per_page=5')
        for run in runs.get('workflow_runs', []):
            if run.get('created_at') and run['created_at'][:7] != dt.datetime.now(dt.timezone.utc).strftime('%Y-%m'):
                continue  # Historical monthly exhaustion must not block the next billing period.
            if run.get('conclusion') == 'failure':
                checks = self.gh_json('api', f'repos/{self.private}/check-suites/{run["check_suite_id"]}/check-runs') if run.get('check_suite_id') else {}
                for check in checks.get('check_runs', []):
                    output = json.dumps(check.get('output', {})).lower()
                    if check.get('output', {}).get('annotations_count'):
                        annotations = self.gh_json('api', f'repos/{self.private}/check-runs/{check["id"]}/annotations')
                        output += json.dumps(annotations).lower()
                    if re.search(r'spending limit|payments? (?:have )?failed|billing|budget.*(?:exhaust|exceed)', output):
                        raise CycleError(f'Actions budget/account is blocked; no dispatch attempted. Resolve billing first. Owner re-enable command: {self.reenable_hint()}')
        workflow = self.gh_json('api', f'repos/{self.private}/actions/workflows/{self.args.workflow}')
        self.require(workflow.get('state') == 'active', f'Workflow is disabled. {self.reenable_hint()}')
        installed = self.gh_json('api', f'repos/{self.private}/contents/.github/workflows/{self.args.workflow}?ref=main')
        try:
            text = base64.b64decode(installed['content'], validate=False).decode('utf-8')
        except (KeyError, ValueError, UnicodeError) as exc:
            raise CycleError('Cannot read the installed private staging workflow') from exc
        jobs = re.findall(r'^  ([a-z0-9-]+):\s*$', text.split('jobs:', 1)[-1], re.M)
        required_jobs = {'linux-x64', 'linux-arm64', 'stage'}
        self.require(required_jobs <= set(jobs) <= required_jobs | {'version'} and
                     all(value in text for value in ('workflow_dispatch:', 'ubuntu-22.04-arm',
                         'secrets.RELEASE_TOKEN', '--prerelease', '--latest=false', 'private-run-id')) and
                     not re.search(r'^  (?:push|pull_request|schedule):', text, re.M),
                     'Installed workflow is not the dispatch-only Linux prerelease pipeline. Deploy the generated private-release workflow before dispatching.')
        before = {r['id'] for r in runs.get('workflow_runs', [])}
        self.phase = 'dispatch'
        self.run(['gh', 'workflow', 'run', self.args.workflow, '-R', self.private, '--ref', 'main'])
        deadline = time.monotonic() + self.args.timeout
        selected = None
        while time.monotonic() < deadline:
            self.phase = 'wait'
            rows = self.gh_json('api', f'repos/{self.private}/actions/workflows/{self.args.workflow}/runs?event=workflow_dispatch&branch=main&per_page=20')
            candidates = [r for r in rows.get('workflow_runs', []) if r['id'] not in before]
            self.require(len(candidates) <= 1, 'Concurrent dispatches are ambiguous; select the staged tag explicitly with --tag')
            if candidates:
                selected = candidates[0]
                if selected.get('status') == 'completed':
                    if selected.get('conclusion') != 'success':
                        self.run(['gh', 'run', 'view', str(selected['id']), '-R', self.private, '--log-failed'], check=False)
                        raise CycleError(f'Private staging run {selected["id"]} failed. If budget exhausted, resolve billing; owner re-enable: {self.reenable_hint()}')
                    break
            print(f'Waiting for {self.private} staging workflow; next check in {self.args.poll_seconds:g}s', flush=True)
            time.sleep(self.args.poll_seconds)
        else:
            raise CycleError('Timed out waiting for the private staging workflow')
        self.report['workflow_run'] = selected['id']
        # The workflow stage notes bind the public tag to its exact private run.
        releases = self.gh_json('api', f'repos/{self.repo}/releases?per_page=100')
        marker = f'private-run-id: {selected["id"]}'
        matches = [r for r in releases if r.get('prerelease') and marker in r.get('body', '')]
        self.require(len(matches) == 1, 'Cannot uniquely identify the prerelease for the completed private run')
        return matches[0]['tag_name']

    def verify_checksums(self, assets):
        sums = assets / 'SHA256SUMS'
        self.require(sums.is_file(), 'Missing SHA256SUMS')
        listed = set()
        for line in sums.read_text().splitlines():
            m = re.fullmatch(r'([a-fA-F0-9]{64})\s+\*?(.+)', line)
            self.require(m, f'Invalid checksum entry: {line}')
            digest, name = m.groups()
            self.require(Path(name).name == name and name not in ('.', '..', 'SHA256SUMS'), 'Unsafe checksum asset path')
            self.require(name not in listed, 'Duplicate checksum entry')
            file = assets / name
            self.require(file.is_file() and not file.is_symlink(), f'Missing asset {name}')
            self.require(hashlib.sha256(file.read_bytes()).hexdigest() == digest.lower(), f'Checksum mismatch: {name}')
            listed.add(name)
        actual = {p.name for p in assets.iterdir()}
        self.require(actual == listed | {'SHA256SUMS'}, 'Every downloaded asset must be covered by SHA256SUMS')
        self.require({f'{self.product}-linux-x64', f'{self.product}-linux-arm64', 'LICENSE'} <= listed, 'Missing required Linux binary/license assets')
        self.require(any(n.startswith('THIRD_PARTY_NOTICES') for n in listed), 'Missing third-party notices')
        self.require(not any(re.search(r'-(?:macos|windows|osx|darwin)', n) for n in listed), 'Staged release contains a non-Linux platform asset')
        if self.product in ('lmcad', 'lmfilament'):
            self.require(all(f'{self.product}-linux-{a}-relink-objects.tar.gz' in listed for a in ('x64', 'arm64')), 'Both architectures require fresh compliance relink archives')
        self.report['sha256sums'] = sums.read_text()

    def check_notices(self, current, previous):
        old = '\n'.join(p.read_text() for p in sorted(previous.glob('THIRD_PARTY_NOTICES*')))
        new = '\n'.join(p.read_text() for p in sorted(current.glob('THIRD_PARTY_NOTICES*')))
        self.require(old and new, 'Both staged and previous release notices are required')
        diff = '\n'.join(difflib.unified_diff(old.splitlines(), new.splitlines(), fromfile='previous', tofile='staged'))
        (self.root / 'notices.diff').write_text(diff + '\n')
        dangerous = re.compile(r'(?<!L)\b(?:A?GPL(?:[- v]|v)?[123]?|GNU (?:Affero )?General Public License)\b', re.I)
        exceptions = re.compile(r'GCC[- ](?:runtime[- ]library[- ])?exception|GCC-exception|\bOR\s+(?:MIT|Apache|BSD)|dual[- ]licens', re.I)
        for line in diff.splitlines():
            if line.startswith('+') and not line.startswith('+++') and dangerous.search(line):
                self.require(exceptions.search(line), 'New GPL/AGPL-only or ambiguous copyleft dependency notice; inspect notices.diff before promotion')
        self.report['notices_changed'] = old != new

    def verify(self, tag, baseline):
        self.phase = 'release-metadata'
        metadata = self.gh_json('release', 'view', tag, '-R', self.repo, '--json', FIELDS)
        self.require(metadata.get('isPrerelease') is True and metadata.get('isDraft') is not True, 'Staging requires a published prerelease (draft=false, prerelease=true)')
        self.require(metadata.get('tagName') == tag, 'Staged release tag mismatch')
        version = self.args.rehearsal_version or tag.removeprefix('v')
        self.require(re.fullmatch(r'\d+\.\d+\.\d+', version), 'Version must be MAJOR.MINOR.PATCH; a throwaway rehearsal needs --rehearsal-version')
        self.phase = 'download'
        assets = self.root / 'assets'
        assets.mkdir()
        self.run(['gh', 'release', 'download', tag, '-R', self.repo, '--dir', assets])
        self.phase = 'checksums'
        self.verify_checksums(assets)
        self.phase = 'arm64-inspection'
        arm = assets / f'{self.product}-linux-arm64'
        _, header = self.run(['readelf', '-h', arm])
        self.require('AArch64' in header and 'ELF64' in header, 'arm64 asset is not an aarch64 ELF64')
        _, symbols = self.run(['readelf', '--version-info', arm])
        glibc = [tuple(map(int, x.split('.'))) for x in re.findall(r'GLIBC_(\d+\.\d+(?:\.\d+)?)', symbols)]
        self.require(not glibc or max(glibc) <= (2, 35), 'arm64 asset requires glibc newer than 2.35')
        self.phase = 'x64-smoke'
        binary = assets / f'{self.product}-linux-x64'
        binary.chmod(0o755)
        _, actual = self.run([binary, '--version'])
        self.require(actual == f'{self.product} {version}', f'Binary version does not match staged version: {actual}')
        _, schema = self.run([binary, '--dsl-schema', '--json'])
        self.require(isinstance(json.loads(schema), dict), 'Host schema is not a JSON object')
        self.phase = 'notices'
        previous = self.root / 'previous'
        previous.mkdir()
        self.run(['gh', 'release', 'download', baseline, '-R', self.repo, '--pattern', 'THIRD_PARTY_NOTICES*', '--dir', previous])
        self.check_notices(assets, previous)
        self.phase = 'public-examples'
        public = self.root / 'public'
        self.run(['gh', 'repo', 'clone', self.repo, public, '--', '--depth', '1'])
        compiler = shutil.which('lmscript')
        if not compiler:
            prefix = self.root / 'compiler'
            self.run(['npm', 'install', '--prefix', prefix, '@lmctl-ai/lmctl@0.2.420'])
            compiler = str(prefix / 'node_modules/.bin/lmscript')
        self.compiler = compiler
        deps, candidate = self.root / 'dependencies', self.root / 'candidate'
        deps.mkdir(); candidate.mkdir()
        shutil.copy2(binary, candidate / self.product)
        installer = public / 'scripts/install-hosts.sh'
        self.require(installer.is_file(), 'Public repo must contain its reviewed scripts/install-hosts.sh')
        env = {'LMCTL_HOST_BIN_DIR': str(deps), 'RUNNER_TEMP': str(self.root), 'GITHUB_ENV': '', 'GITHUB_PATH': ''}
        self.run(['bash', installer], cwd=public, env=env)
        skip = self.root / 'lmctl-unavailable-examples.tsv'
        self.require(not skip.exists() or not skip.read_text().strip(), 'Every public example must run; installer reported unavailable dependencies')
        env['PATH'] = f'{candidate}:{deps}:{Path(compiler).parent}:{os.environ.get("PATH", "")}'
        examples = sorted((public / 'examples').rglob('*.lms'))
        self.require(examples, 'No public examples found')
        for example in examples:
            print(f'Check/run {example.relative_to(public)}', flush=True)
            self.run([compiler, '--check', example], cwd=public, env=env)
            self.run([compiler, example], cwd=public, env=env)
        self.report['examples_passed'] = len(examples)
        self.report['verified_tag'] = tag
        self.report['baseline_tag'] = baseline

    def promote(self, tag):
        self.phase = 'promote'
        self.run(['gh', 'release', 'edit', tag, '-R', self.repo, '--prerelease=false', '--latest'])
        self.report['promotion_applied'] = tag
        self.report['restore_latest_command'] = ['gh', 'release', 'edit', self.report['baseline_tag'], '-R', self.repo, '--latest']
        latest = self.gh_json('api', f'repos/{self.repo}/releases/latest')
        self.require(latest.get('tag_name') == tag and not latest.get('prerelease'), 'GitHub latest did not resolve to the promoted tag')
        self.phase = 'latest-install'
        # Exclude all PATH host binaries and caches so install= cannot reuse an older binary.
        isolated = self.root / 'latest-bin'
        isolated.mkdir()
        node = shutil.which('node')
        self.require(node, 'Node is required for the actual lmscript @latest resolver check')
        (isolated / 'node').symlink_to(Path(node).resolve())
        env = {'PATH': f'{isolated}:/usr/local/bin:/usr/bin:/bin', 'LMSCRIPT_TOOL_CACHE': str(self.root / 'latest-cache')}
        _, output = self.run([self.compiler, 'install', f'github:{self.repo}@latest'], env=env)
        self.require(re.search(rf'^tag: {re.escape(tag)}$', output, re.M),
                     'lmscript install @latest did not report the promoted tag')
        self.report['promoted_tag'] = tag

    def finish(self, status, message):
        self.report.update({'status': status, 'phase': self.phase, 'command': self.command,
                            'log_path': str(self.log) if self.log else None, 'message': self.redact(message),
                            'last_lines': self.log.read_text().splitlines()[-80:] if self.log else []})
        serialized = self.redact(json.dumps(self.report, indent=2)) + '\n'
        (self.root / 'report.json').write_text(serialized)
        (self.root / 'report.txt').write_text(f'{status}: {self.redact(message)}\nPhase: {self.phase}\nCommand: {shlex.join(self.command)}\nLog: {self.log}\n\n' + '\n'.join(self.report['last_lines']) + '\n')
        print(f'{status}: {self.redact(message)}\nReport: {self.root / "report.json"}', flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('product', choices=PRODUCTS)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--promote', action='store_true')
    p.add_argument('--tag', help='verify an existing staged prerelease without dispatching Actions')
    p.add_argument('--rehearsal-version', help='existing binary version; only for a throwaway vVERSION+rehearsal-* tag')
    p.add_argument('--workflow', default='ci.yml')
    p.add_argument('--poll-seconds', type=float, default=45)
    p.add_argument('--timeout', type=float, default=14400)
    p.add_argument('--state-dir', type=Path)
    args = p.parse_args()
    if args.rehearsal_version and (not args.tag or not re.fullmatch(
            rf'v{re.escape(args.rehearsal_version)}\+rehearsal-[A-Za-z0-9.-]+', args.tag)):
        p.error('--rehearsal-version requires --tag vVERSION+rehearsal-SUFFIX matching the existing binary version')
    if args.poll_seconds < 0.01:
        p.error('--poll-seconds must be positive')
    cycle = Cycle(args)
    try:
        if args.dry_run:
            cycle.phase = 'dry-run'
            permissions = cycle.gh_json('api', f'repos/{cycle.private}/actions/permissions')
            message = (f'dry-run: would dispatch {cycle.private}/{args.workflow}, wait, download the public prerelease, '
                       'check hashes/x64 schema/all public examples/arm64 ELF/notices, then ' + ('promote.' if args.promote else 'print the promote command.'))
            if not permissions.get('enabled'):
                message += f' Actions disabled; real dispatch would refuse. Owner command: {cycle.reenable_hint()}'
            cycle.finish('PASS', message)
            return 0
        baseline_data = cycle.gh_json('api', f'repos/{cycle.repo}/releases/latest')
        baseline = baseline_data['tag_name']
        tag = args.tag or cycle.dispatch()
        cycle.verify(tag, baseline)
        if args.promote:
            cycle.promote(tag)
            message = f'Verified and promoted {cycle.repo}@{tag}'
        else:
            message = f'Local tests passed. Promote with: {HERE / "release-cycle.sh"} {args.product} --tag {shlex.quote(tag)} --promote'
        cycle.finish('PASS', message)
        return 0
    except (CycleError, KeyError, ValueError, OSError) as exc:
        cycle.finish('FAIL', str(exc))
        return 1


if __name__ == '__main__':
    sys.exit(main())
