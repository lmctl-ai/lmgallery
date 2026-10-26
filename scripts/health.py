#!/usr/bin/env python3
"""health.py: Cross-repository health dashboard for lmctl-ai ecosystem.

Audits:
- Closed-source peer model products:
  * Top PRODUCTS table: private URL, public URL, latest release tag, release age,
    asset count, public-content CI state, private CI state
  * Public repo: release tag, platform asset count (4-5), SHA256SUMS presence,
    LICENSE + THIRD_PARTY_NOTICES presence, no debug/metrics extras,
    asset naming (<name>-<os>-<arch>), public-content CI, README pictures & links,
    and example syntax via installed released hosts with `lmscript --check`
  * Private repo: Linux push CI (missing recent run is OK; failed is not),
    RELEASE_TOKEN secret presence, private main sha vs public release notes sha,
    private/public visibility (lmctlhq is PRIVATE, lmctl-ai is PUBLIC),
    durable-memory/index.md integrity, sdk.lock freshness, compiler pin
- Open-source repositories:
  * Latest main CI status (per-job failures listed)
  * Latest release tag, age, platform asset count (4-5), SHA256SUMS presence
  * sdk.lock commit vs SDK origin/main (commits behind, std fragment status)
  * Compiler pin (@lmctl-ai/lmctl >= 0.2.420)
  * README pictures, broken images, broken autorun links, missing alt text, oversized images
  * Git working-tree status (clean/dirty, ahead/behind counts)
  * durable-memory/index.md presence and complete indexing
  * Stale SDK names (cpp-dsl-sdk, rust-dsl-sdk, lmterraform)

Options:
  --json        Output results as machine-readable JSON
  --fix-pins    Automatically re-sync sdk.lock for hosts that are behind, run cheap tests, and push
  --repo <name> Audit a specific repo only
"""

import argparse
import concurrent.futures
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import urllib.parse
import urllib.request

# Ensure user local bin is on PATH for host binaries
local_bin = os.path.expanduser('~/.local/bin')
if local_bin not in os.environ.get('PATH', ''):
  os.environ['PATH'] = f"{local_bin}:{os.environ.get('PATH', '')}"

CLOSED_SOURCE_PRODUCTS = [
    'lmaudio',
    'lmcad',
    'lmdraw',
    'lmfilament',
    'lmimg',
    'lmmagnum',
    'lmoffice',
    'lmpdf',
    'lmvideo',
]

FOUR_PLATFORM_HOSTS = {
    'lmvideo',
    'lmfilament',
    'lmssh',
}

NON_BINARY_REPOS = {
    'lmgallery',
    'lmcode-cpp',
    'lmcode-go',
    'lmcode-rust',
    'lmcode-csharp',
    'lmcode-java',
}

UNRELEASED_HOSTS = {
    'lmproxy',
    'lmpdf',
    'lmawscli',
    'lmnet',
}

ALLOWED_OVERSIZED = {
    'quantum_packet.gif',
    'rh_anim.gif',
    'jet_rollup_anim.gif',
    'kelvin_anim.gif',
    'cylinder_wake.gif',
    'argon-melt.gif',
    'level-3-hands-off-lead.gif',
    'texturedquad.png',
}

STALE_WORDS = ['cpp-dsl-sdk', 'rust-dsl-sdk', 'lmterraform']

MIN_COMPILER_PIN = (0, 2, 420)

USE_COLOR = sys.stdout.isatty()

_GH_CACHE = {}
_GH_LOCK = threading.Lock()


def gh_cmd(args):
  key = tuple(args)
  with _GH_LOCK:
    if key in _GH_CACHE:
      return _GH_CACHE[key]
  res = subprocess.run(['gh'] + list(args), capture_output=True, text=True)
  with _GH_LOCK:
    _GH_CACHE[key] = res
  return res


def color(text, code):
  if not USE_COLOR:
    return text
  return f'\033[{code}m{text}\033[0m'


def green(text):
  return color(text, '32')


def red(text):
  return color(text, '31')


def yellow(text):
  return color(text, '33')


def bold(text):
  return color(text, '1')


def cyan(text):
  return color(text, '36')


def get_repos_root():
  return os.environ.get('LM_REPOS_ROOT') or os.path.dirname(
      os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  )


def discover_repos(target_repo=None):
  repos_root = get_repos_root()
  candidates = glob.glob(os.path.join(repos_root, 'lm*'))
  for alt in [
      os.path.join(repos_root, 'lmvideo'),
      os.path.join(os.path.dirname(repos_root), 'lmctlhq', 'lmvideo'),
  ]:
    if os.path.isdir(alt) and alt not in candidates:
      candidates.append(alt)

  # Map available directories
  dirs_by_name = {}
  for p in candidates:
    if not os.path.isdir(p) or not os.path.isdir(os.path.join(p, '.git')):
      continue
    bname = os.path.basename(p)
    if bname == 'lmctl-mono':
      continue
    dirs_by_name[bname] = os.path.abspath(p)

  # Collect base product / repo names
  base_names = set()
  for bname in dirs_by_name:
    if bname.endswith('-public'):
      base_names.add(bname[:-7])
    else:
      base_names.add(bname)

  # Normalize target_repo if specified (e.g. lmaudio-public -> lmaudio)
  target_norm = None
  if target_repo:
    target_norm = (
        target_repo[:-7] if target_repo.endswith('-public') else target_repo
    )

  repo_targets = []
  for name in sorted(base_names):
    if target_norm and name != target_norm:
      continue

    priv_path = dirs_by_name.get(name)
    pub_path = dirs_by_name.get(f'{name}-public')

    origin_url = ''
    if priv_path:
      p_rem = subprocess.run(
          ['git', '-C', priv_path, 'config', '--get', 'remote.origin.url'],
          capture_output=True,
          text=True,
      )
      origin_url = p_rem.stdout.strip()

    is_closed = False
    if name in CLOSED_SOURCE_PRODUCTS:
      if pub_path or 'lmctlhq' in origin_url:
        is_closed = True
      elif target_repo and target_repo in (name, f'{name}-public'):
        is_closed = True

    repo_targets.append({
        'name': name,
        'path': priv_path or pub_path,
        'private_path': priv_path,
        'public_path': pub_path,
        'is_closed': is_closed,
        'origin_url': origin_url,
    })

  return repo_targets


def check_ci(repo_name):
  res = gh_cmd([
      'run',
      'list',
      '-R',
      f'lmctl-ai/{repo_name}',
      '--branch',
      'main',
      '-L',
      '1',
      '--json',
      'databaseId,status,conclusion,url,headSha',
  ])
  if res.returncode != 0 or not res.stdout.strip():
    res = gh_cmd([
        'run',
        'list',
        '-R',
        f'lmctl-ai/{repo_name}',
        '-L',
        '1',
        '--json',
        'databaseId,status,conclusion,url,headSha',
    ])
    if res.returncode != 0 or not res.stdout.strip():
      return {
          'status': 'no_runs',
          'conclusion': 'unknown',
          'display': 'no runs',
          'failed_jobs': [],
          'run_url': '',
          'is_red': False,
      }

  try:
    runs = json.loads(res.stdout)
  except Exception:
    return {
        'status': 'error',
        'conclusion': 'unknown',
        'display': 'error',
        'failed_jobs': [],
        'run_url': '',
        'is_red': False,
    }

  if not runs:
    return {
        'status': 'no_runs',
        'conclusion': 'none',
        'display': 'no runs',
        'failed_jobs': [],
        'run_url': '',
        'is_red': False,
    }

  run = runs[0]
  status = run.get('status', '')
  conclusion = run.get('conclusion', '')
  run_id = run.get('databaseId')
  run_url = run.get('url', '')

  failed_jobs = []
  is_red = False

  if conclusion == 'success':
    display = 'PASS'
  elif status in ('queued', 'in_progress', 'waiting', 'requested'):
    display = status
  elif conclusion in ('failure', 'startup_failure', 'timed_out', 'cancelled'):
    is_red = conclusion != 'cancelled'
    if run_id:
      job_res = gh_cmd([
          'run',
          'view',
          str(run_id),
          '-R',
          f'lmctl-ai/{repo_name}',
          '--json',
          'jobs',
      ])
      if job_res.returncode == 0:
        try:
          job_data = json.loads(job_res.stdout)
          failed_jobs = [
              j.get('name', 'job')
              for j in job_data.get('jobs', [])
              if j.get('conclusion') in ('failure', 'startup_failure')
          ]
        except Exception:
          pass
    job_str = (
        f"[{', '.join(failed_jobs)}]"
        if failed_jobs
        else f'[{conclusion or status}]'
    )
    display = f'FAIL {job_str}'
  else:
    display = conclusion or status or 'unknown'

  return {
      'status': status,
      'conclusion': conclusion,
      'display': display,
      'failed_jobs': failed_jobs,
      'run_url': run_url,
      'is_red': is_red,
  }


def check_actions_permissions(product_name):
  res = gh_cmd(['api', f'repos/lmctlhq/{product_name}/actions/permissions'])
  if res.returncode == 0 and res.stdout.strip():
    try:
      data = json.loads(res.stdout)
      return data.get('enabled')
    except Exception:
      pass
  return None


def check_run_has_budget_annotation(product_name, run_id):
  res = gh_cmd([
      'api',
      f'repos/lmctlhq/{product_name}/actions/runs/{run_id}/jobs',
  ])
  if res.returncode == 0 and res.stdout.strip():
    try:
      data = json.loads(res.stdout)
      for j in data.get('jobs', []):
        if j.get('conclusion') in ('failure', 'startup_failure'):
          jid = j.get('id')
          if jid:
            ann_res = gh_cmd([
                'api',
                f'repos/lmctlhq/{product_name}/check-runs/{jid}/annotations',
            ])
            if ann_res.returncode == 0 and ann_res.stdout.strip():
              anns = json.loads(ann_res.stdout)
              for a in anns:
                msg = (a.get('message') or '').lower()
                if 'budget' in msg:
                  return True
    except Exception:
      pass
  return False


def check_private_ci(product_name):
  actions_enabled = check_actions_permissions(product_name)

  res = gh_cmd([
      'run',
      'list',
      '-R',
      f'lmctlhq/{product_name}',
      '--branch',
      'main',
      '-L',
      '1',
      '--json',
      'databaseId,status,conclusion,url,headSha',
  ])
  if res.returncode != 0 or not res.stdout.strip():
    res = gh_cmd([
        'run',
        'list',
        '-R',
        f'lmctlhq/{product_name}',
        '-L',
        '1',
        '--json',
        'databaseId,status,conclusion,url,headSha',
    ])
    if res.returncode != 0 or not res.stdout.strip():
      if actions_enabled is False:
        return {
            'status': 'hold',
            'conclusion': 'actions_disabled',
            'display': 'HOLD (actions disabled)',
            'failed_jobs': [],
            'run_url': '',
            'is_red': False,
        }
      return {
          'status': 'no_runs',
          'conclusion': 'none',
          'display': 'no runs (OK)',
          'failed_jobs': [],
          'run_url': '',
          'is_red': False,
      }

  try:
    runs = json.loads(res.stdout)
  except Exception:
    runs = []

  if not runs:
    if actions_enabled is False:
      return {
          'status': 'hold',
          'conclusion': 'actions_disabled',
          'display': 'HOLD (actions disabled)',
          'failed_jobs': [],
          'run_url': '',
          'is_red': False,
      }
    return {
        'status': 'no_runs',
        'conclusion': 'none',
        'display': 'no runs (OK)',
        'failed_jobs': [],
        'run_url': '',
        'is_red': False,
    }

  run = runs[0]
  status = run.get('status', '')
  conclusion = run.get('conclusion', '')
  run_id = run.get('databaseId')
  run_url = run.get('url', '')

  if actions_enabled is False:
    return {
        'status': 'hold',
        'conclusion': 'actions_disabled',
        'display': 'HOLD (actions disabled)',
        'failed_jobs': [],
        'run_url': run_url,
        'is_red': False,
    }

  failed_jobs = []
  is_red = False

  if conclusion == 'success':
    display = 'PASS'
  elif status in ('queued', 'in_progress', 'waiting', 'requested'):
    display = status
  elif conclusion in ('failure', 'startup_failure', 'timed_out', 'cancelled'):
    if conclusion != 'cancelled':
      if run_id and check_run_has_budget_annotation(product_name, run_id):
        return {
            'status': 'hold',
            'conclusion': 'budget',
            'display': 'HOLD (budget)',
            'failed_jobs': [],
            'run_url': run_url,
            'is_red': False,
        }

      is_red = True
      if run_id:
        job_res = gh_cmd([
            'run',
            'view',
            str(run_id),
            '-R',
            f'lmctlhq/{product_name}',
            '--json',
            'jobs',
        ])
        if job_res.returncode == 0:
          try:
            job_data = json.loads(job_res.stdout)
            failed_jobs = [
                j.get('name', 'job')
                for j in job_data.get('jobs', [])
                if j.get('conclusion') in ('failure', 'startup_failure')
            ]
          except Exception:
            pass
      job_str = (
          f"[{', '.join(failed_jobs)}]"
          if failed_jobs
          else f'[{conclusion or status}]'
      )
      display = f'FAIL {job_str}'
    else:
      display = 'cancelled'
  else:
    display = conclusion or status or 'unknown'

  return {
      'status': status,
      'conclusion': conclusion,
      'display': display,
      'failed_jobs': failed_jobs,
      'run_url': run_url,
      'is_red': is_red,
  }


def check_public_ci(product_name):
  res = gh_cmd([
      'run',
      'list',
      '-R',
      f'lmctl-ai/{product_name}',
      '--branch',
      'main',
      '-L',
      '1',
      '--json',
      'databaseId,status,conclusion,url,headSha,workflowName',
  ])
  if res.returncode != 0 or not res.stdout.strip():
    res = gh_cmd([
        'run',
        'list',
        '-R',
        f'lmctl-ai/{product_name}',
        '-L',
        '1',
        '--json',
        'databaseId,status,conclusion,url,headSha,workflowName',
    ])
    if res.returncode != 0 or not res.stdout.strip():
      return {
          'status': 'no_runs',
          'conclusion': 'unknown',
          'display': 'no runs',
          'failed_jobs': [],
          'run_url': '',
          'is_red': False,
      }

  try:
    runs = json.loads(res.stdout)
  except Exception:
    return {
        'status': 'error',
        'conclusion': 'unknown',
        'display': 'error',
        'failed_jobs': [],
        'run_url': '',
        'is_red': False,
    }

  if not runs:
    return {
        'status': 'no_runs',
        'conclusion': 'none',
        'display': 'no runs',
        'failed_jobs': [],
        'run_url': '',
        'is_red': False,
    }

  run = runs[0]
  status = run.get('status', '')
  conclusion = run.get('conclusion', '')
  run_id = run.get('databaseId')
  run_url = run.get('url', '')

  failed_jobs = []
  is_red = False

  if conclusion == 'success':
    display = 'PASS'
  elif status in ('queued', 'in_progress', 'waiting', 'requested'):
    display = status
  elif conclusion in ('failure', 'startup_failure', 'timed_out', 'cancelled'):
    is_red = conclusion != 'cancelled'
    if run_id:
      job_res = gh_cmd([
          'run',
          'view',
          str(run_id),
          '-R',
          f'lmctl-ai/{product_name}',
          '--json',
          'jobs',
      ])
      if job_res.returncode == 0:
        try:
          job_data = json.loads(job_res.stdout)
          failed_jobs = [
              j.get('name', 'job')
              for j in job_data.get('jobs', [])
              if j.get('conclusion') in ('failure', 'startup_failure')
          ]
        except Exception:
          pass
    job_str = (
        f"[{', '.join(failed_jobs)}]"
        if failed_jobs
        else f'[{conclusion or status}]'
    )
    display = f'FAIL {job_str}'
  else:
    display = conclusion or status or 'unknown'

  return {
      'status': status,
      'conclusion': conclusion,
      'display': display,
      'failed_jobs': failed_jobs,
      'run_url': run_url,
      'is_red': is_red,
  }


def check_visibility(product_name):
  priv_res = gh_cmd(
      ['repo', 'view', f'lmctlhq/{product_name}', '--json', 'isPrivate']
  )
  pub_res = gh_cmd(
      ['repo', 'view', f'lmctl-ai/{product_name}', '--json', 'isPrivate']
  )

  priv_is_private = None
  if priv_res.returncode == 0:
    try:
      priv_is_private = json.loads(priv_res.stdout).get('isPrivate')
    except Exception:
      pass

  pub_is_private = None
  if pub_res.returncode == 0:
    try:
      pub_is_private = json.loads(pub_res.stdout).get('isPrivate')
    except Exception:
      pass

  issues = []
  if priv_is_private is False:
    issues.append(f'lmctlhq/{product_name} is PUBLIC (expected PRIVATE)')
  elif priv_is_private is None:
    issues.append(f'could not verify lmctlhq/{product_name} visibility')

  if pub_is_private is True:
    issues.append(f'lmctl-ai/{product_name} is PRIVATE (expected PUBLIC)')
  elif pub_is_private is None:
    issues.append(f'could not verify lmctl-ai/{product_name} visibility')

  return {
      'is_ok': len(issues) == 0,
      'issues': issues,
      'priv_is_private': priv_is_private,
      'pub_is_private': pub_is_private,
  }


def check_release_token(product_name):
  sec_res = gh_cmd(['secret', 'list', '-R', f'lmctlhq/{product_name}'])
  has_token = False
  if sec_res.returncode == 0:
    has_token = bool(re.search(r'\bRELEASE_TOKEN\b', sec_res.stdout))
  return has_token


def format_age(published_at):
  if not published_at:
    return ''
  try:
    dt = datetime.datetime.fromisoformat(published_at.replace('Z', '+00:00'))
    now = datetime.datetime.now(datetime.timezone.utc)
    diff = now - dt
    secs = int(diff.total_seconds())
    if secs < 3600:
      return f'{secs // 60}m'
    elif secs < 86400:
      return f'{secs // 3600}h'
    else:
      return f'{secs // 86400}d'
  except Exception:
    return ''


def check_release(repo_name, is_closed=False, private_path=None):
  res = gh_cmd([
      'release',
      'list',
      '-R',
      f'lmctl-ai/{repo_name}',
      '-L',
      '1',
      '--json',
      'tagName,publishedAt,name',
  ])
  if res.returncode != 0 or not res.stdout.strip():
    non_binary = repo_name in NON_BINARY_REPOS or repo_name.endswith('-sample')
    is_red = not non_binary and repo_name not in UNRELEASED_HOSTS
    return {
        'tag': None,
        'display': 'n/a (SDK/gallery)'
        if non_binary
        else 'none',
        'is_red': is_red,
        'assets': [],
        'has_sha256': False,
        'has_license': False,
        'has_notices': False,
        'extras': [],
        'misnamed': [],
        'platform_count': 0,
        'expected_platforms': 4 if repo_name in FOUR_PLATFORM_HOSTS else 5,
        'age_str': '',
        'issues': ['No release found'] if is_red else [],
    }

  try:
    rels = json.loads(res.stdout)
  except Exception:
    return {
        'tag': None,
        'display': 'error',
        'is_red': False,
        'assets': [],
        'has_sha256': False,
        'has_license': False,
        'has_notices': False,
        'extras': [],
        'misnamed': [],
        'platform_count': 0,
        'expected_platforms': 4 if repo_name in FOUR_PLATFORM_HOSTS else 5,
        'age_str': '',
        'issues': ['Failed to parse release list'],
    }

  if not rels:
    non_binary = repo_name in NON_BINARY_REPOS or repo_name.endswith('-sample')
    is_red = not non_binary and repo_name not in UNRELEASED_HOSTS
    return {
        'tag': None,
        'display': 'n/a (SDK/gallery)'
        if non_binary
        else 'none',
        'is_red': is_red,
        'assets': [],
        'has_sha256': False,
        'has_license': False,
        'has_notices': False,
        'extras': [],
        'misnamed': [],
        'platform_count': 0,
        'expected_platforms': 4 if repo_name in FOUR_PLATFORM_HOSTS else 5,
        'age_str': '',
        'issues': ['No release found'] if is_red else [],
    }

  rel = rels[0]
  tag = rel.get('tagName', '')
  published_at = rel.get('publishedAt', '')

  v_res = gh_cmd([
      'release',
      'view',
      tag,
      '-R',
      f'lmctl-ai/{repo_name}',
      '--json',
      'assets,body',
  ])
  assets = []
  body = ''
  if v_res.returncode == 0:
    try:
      v_data = json.loads(v_res.stdout)
      assets = [a.get('name', '') for a in v_data.get('assets', [])]
      body = v_data.get('body', '')
    except Exception:
      pass

  age_str = format_age(published_at)

  expected_platforms = 4 if repo_name in FOUR_PLATFORM_HOSTS else 5
  plat_targets = [
      'linux-x64',
      'linux-arm64',
      'macos-x64',
      'macos-arm64',
  ]
  if expected_platforms == 5:
    plat_targets.append('windows-x64')

  platform_count = 0
  misnamed = []
  for p in plat_targets:
    matching = [
        a
        for a in assets
        if p in a
        or (
            p == 'windows-x64'
            and (a.endswith('.exe') or 'windows' in a or 'win-x64' in a)
        )
    ]
    if matching:
      platform_count += 1
      if is_closed:
        for m in matching:
          if not m.startswith(f'{repo_name}-'):
            misnamed.append(m)

  has_sha256 = any('SHA256' in a.upper() for a in assets)
  has_license = any(a == 'LICENSE' or a.startswith('LICENSE.') for a in assets)
  has_notices = any('NOTICE' in a.upper() for a in assets)

  extras = []
  if is_closed:
    for a in assets:
      al = a.lower()
      if any(
          x in al
          for x in ['metrics', 'linkage', 'timings', 'minutes', '.pdb', '.dsym']
      ):
        extras.append(a)

  issues = []
  is_red = False

  if repo_name not in NON_BINARY_REPOS and repo_name not in UNRELEASED_HOSTS:
    if platform_count < expected_platforms:
      is_red = True
      issues.append(
          f'incomplete platform binaries ({platform_count}/{expected_platforms})'
      )
    if not has_sha256:
      is_red = True
      issues.append('missing SHA256SUMS')

    if is_closed:
      if not has_license:
        is_red = True
        issues.append('missing LICENSE asset')
      if not has_notices:
        is_red = True
        issues.append('missing THIRD_PARTY_NOTICES asset')
      if extras:
        is_red = True
        issues.append(f"debug/metrics extras present: {', '.join(extras)}")
      if misnamed:
        is_red = True
        issues.append(f"misnamed binary assets: {', '.join(misnamed)}")

      # Verify release notes commit SHA if present
      sha_match = re.search(r'\b(?:commit|sha)[:\s/]+([0-9a-f]{7,40})\b', body, re.I)
      if sha_match and private_path and os.path.isdir(private_path):
        rel_sha = sha_match.group(1).lower()
        p_head = subprocess.run(
            ['git', '-C', private_path, 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
        )
        priv_head = p_head.stdout.strip().lower()
        if not priv_head.startswith(rel_sha) and not rel_sha.startswith(priv_head):
          is_red = True
          issues.append(
              f'release notes SHA {rel_sha[:7]} does not match private HEAD'
              f' {priv_head[:7]}'
          )

  check_mark = '✓' if (has_sha256 and (not is_closed or (has_license and has_notices and not extras))) else '✗'
  display = f'{tag} ({age_str}, {platform_count}/{expected_platforms}, {check_mark})'

  return {
      'tag': tag,
      'published_at': published_at,
      'age_str': age_str,
      'assets': assets,
      'platform_count': platform_count,
      'expected_platforms': expected_platforms,
      'has_sha256': has_sha256,
      'has_license': has_license,
      'has_notices': has_notices,
      'extras': extras,
      'misnamed': misnamed,
      'display': display,
      'is_red': is_red,
      'issues': issues,
  }


def check_declares_std(repo_path, repo_name):
  if repo_name in NON_BINARY_REPOS or repo_name == 'lmvideo':
    return False
  repos_root = get_repos_root()
  cpp_std_path = os.path.join(
      repos_root, 'lmcode-cpp', 'std', 'lmcode-std.schema.json'
  )
  if not os.path.exists(cpp_std_path):
    return False
  try:
    with open(cpp_std_path, 'r') as f:
      std_data = json.load(f)
    std_funcs = set(std_data.get('functions', {}).keys())
    std_types = set(std_data.get('types', {}).keys())
  except Exception:
    return False

  schema_dir = os.path.join(repo_path, 'schema')
  if os.path.isdir(schema_dir):
    for sf in os.listdir(schema_dir):
      if sf.endswith('.json') and 'lmcode-std' not in sf:
        try:
          with open(os.path.join(schema_dir, sf), 'r') as f:
            data = json.load(f)
          funcs = set(data.get('functions', {}).keys())
          types = set(data.get('types', {}).keys())
          if funcs.intersection(std_funcs) or types.intersection(std_types):
            return True
        except Exception:
          pass
  return False


def check_sdk_pin(repo_path, repo_name):
  lock_path = os.path.join(repo_path, 'sdk.lock')
  declares_std = check_declares_std(repo_path, repo_name)
  if not os.path.exists(lock_path):
    disp = 'std migration pending' if declares_std else 'n/a'
    return {
        'has_lock': False,
        'pinned_repo': None,
        'commit': None,
        'behind': 0,
        'std_status': 'migration pending' if declares_std else 'n/a',
        'display': disp,
        'is_red': False,
        'is_stale': False,
        'declares_std': declares_std,
    }

  pinned_repo = None
  commit = None

  with open(lock_path, 'r', errors='ignore') as f:
    text = f.read().strip()

  if text.startswith('{'):
    try:
      d = json.loads(text)
      pinned_repo = d.get('repo') or d.get('repository')
      commit = d.get('commit')
    except Exception:
      pass
  else:
    for line in text.splitlines():
      line = line.strip()
      line_lower = line.lower()
      if (
          line_lower.startswith('repo=')
          or line_lower.startswith('repository=')
          or line_lower.startswith('sdk_repo=')
      ):
        pinned_repo = line.split('=', 1)[1].strip()
      elif line_lower.startswith('commit=') or line_lower.startswith(
          'sdk_commit='
      ):
        commit = line.split('=', 1)[1].strip()
      elif line and not line.startswith('#') and ' ' in line and '=' not in line:
        parts = line.split()
        if len(parts) >= 2:
          pinned_repo = parts[0]
          commit = parts[1]

  if not commit:
    return {
        'has_lock': True,
        'pinned_repo': pinned_repo,
        'commit': None,
        'behind': 0,
        'std_status': 'n/a',
        'display': 'no-commit',
        'is_red': True,
        'is_stale': False,
        'declares_std': declares_std,
    }

  repos_root = get_repos_root()
  if pinned_repo and 'lmcode-csharp' in pinned_repo:
    target_repo_path = os.path.join(repos_root, 'lmcode-csharp')
  elif pinned_repo and 'lmcode-java' in pinned_repo:
    target_repo_path = os.path.join(repos_root, 'lmcode-java')
  elif pinned_repo and 'lmcode-go' in pinned_repo:
    target_repo_path = os.path.join(repos_root, 'lmcode-go')
  elif pinned_repo and 'lmcode-rust' in pinned_repo:
    target_repo_path = os.path.join(repos_root, 'lmcode-rust')
  else:
    target_repo_path = os.path.join(repos_root, 'lmcode-cpp')

  behind = 0
  commit_exists = False
  if os.path.exists(target_repo_path):
    check_c = subprocess.run(
        ['git', '-C', target_repo_path, 'cat-file', '-e', commit],
        capture_output=True,
    )
    commit_exists = check_c.returncode == 0
    if commit_exists:
      rev_cnt = subprocess.run(
          [
              'git',
              '-C',
              target_repo_path,
              'rev-list',
              '--count',
              f'{commit}..origin/main',
          ],
          capture_output=True,
          text=True,
      )
      if rev_cnt.returncode == 0 and rev_cnt.stdout.strip().isdigit():
        behind = int(rev_cnt.stdout.strip())
    else:
      behind = 999

  std_status = '-'
  host_std_path = os.path.join(repo_path, 'cpp', 'std', 'lmcode-std.schema.json')
  cpp_std_path = os.path.join(
      repos_root, 'lmcode-cpp', 'std', 'lmcode-std.schema.json'
  )

  if os.path.exists(host_std_path):
    if os.path.exists(cpp_std_path):
      try:
        with (
            open(host_std_path, 'rb') as hf,
            open(cpp_std_path, 'rb') as cf,
        ):
          if (
              hashlib.sha256(hf.read()).hexdigest()
              == hashlib.sha256(cf.read()).hexdigest()
          ):
            std_status = 'synced'
          else:
            std_status = 'differs'
      except Exception:
        std_status = 'error'
    else:
      std_status = 'present'

  if declares_std:
    std_status = 'migration pending'

  is_stale = behind > 0
  if declares_std:
    if behind == 0:
      display = 'std migration pending'
    else:
      display = f'{behind} behind (std migration pending)'
  elif behind == 0:
    display = 'synced'
  else:
    std_part = f' (std:{std_status})' if std_status != '-' else ''
    display = f'{behind} behind{std_part}'

  return {
      'has_lock': True,
      'pinned_repo': pinned_repo,
      'commit': commit,
      'behind': behind,
      'std_status': std_status,
      'display': display,
      'is_red': False,
      'is_stale': is_stale,
      'commit_exists': commit_exists,
      'declares_std': declares_std,
  }


def check_compiler_pin(repo_path, repo_name):
  stale_pins = []
  found_versions = []
  targets = []
  wf_dir = os.path.join(repo_path, '.github', 'workflows')
  if os.path.isdir(wf_dir):
    for f in os.listdir(wf_dir):
      if f.endswith(('.yml', '.yaml')):
        targets.append(os.path.join(wf_dir, f))
  sp = os.path.join(repo_path, 'scripts', 'select-compiler.sh')
  if os.path.exists(sp):
    targets.append(sp)

  for t in targets:
    try:
      with open(t, 'r', errors='ignore') as fh:
        content = fh.read()
      for m in re.finditer(
          r'@lmctl-ai/lmctl@([0-9]+)\.([0-9]+)\.([0-9]+)', content
      ):
        ver_tuple = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        ver_str = f'{m.group(1)}.{m.group(2)}.{m.group(3)}'
        found_versions.append((ver_tuple, ver_str))
        if ver_tuple < MIN_COMPILER_PIN:
          rel = os.path.relpath(t, repo_path)
          stale_pins.append(f'{rel}@{ver_str}')
    except Exception:
      pass

  if not found_versions:
    return {
        'display': '-',
        'is_stale': False,
        'stale_pins': [],
        'version': None,
    }

  min_ver_tuple, min_ver_str = min(found_versions, key=lambda x: x[0])
  is_stale = min_ver_tuple < MIN_COMPILER_PIN
  display = min_ver_str
  return {
      'display': display,
      'is_stale': is_stale,
      'stale_pins': stale_pins,
      'version': min_ver_str,
  }


def check_examples(repo_path, repo_name, is_closed=False):
  examples_dir = os.path.join(repo_path, 'examples')
  if not os.path.isdir(examples_dir):
    return {
        'total': 0,
        'lmcode_count': 0,
        'dsl_count': 0,
        'dsl_files': [],
        'syntax_failures': [],
        'display': '-',
        'is_red': False,
    }

  lms_files = []
  for root, dirs, files in os.walk(examples_dir):
    for f in files:
      if f.endswith('.lms'):
        lms_files.append(os.path.join(root, f))

  total = len(lms_files)
  dsl_files = []
  lmcode_count = 0
  for fp in lms_files:
    try:
      with open(fp, 'r', errors='ignore') as fh:
        text = fh.read()
      has_dsl = bool(re.search(r'\b_dsl_\b', text))
      has_lmcode = bool(re.search(r'\b_lmcode_\b', text))
      if has_dsl:
        dsl_files.append(os.path.relpath(fp, repo_path))
      if has_lmcode:
        lmcode_count += 1
    except Exception:
      pass

  # If closed-source, test syntax with lmscript --check using installed host
  syntax_failures = []
  if is_closed and lms_files:
    host_bin = shutil.which(repo_name)
    if host_bin:
      # Batch run syntax check
      cmd = ['lmscript', '--check'] + lms_files
      res = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
      if res.returncode != 0:
        # One or more failed; pinpoint failing files individually
        for fp in lms_files:
          c_res = subprocess.run(
              ['lmscript', '--check', fp],
              cwd=repo_path,
              capture_output=True,
              text=True,
          )
          if c_res.returncode != 0:
            syntax_failures.append(os.path.relpath(fp, repo_path))

  is_red = bool(syntax_failures)
  display = (
      f'{len(dsl_files)} _dsl_ (info)'
      if dsl_files
      else ('OK' if total > 0 else '-')
  )
  if syntax_failures:
    display = f'FAIL ({len(syntax_failures)} syntax)'

  return {
      'total': total,
      'lmcode_count': lmcode_count,
      'dsl_count': len(dsl_files),
      'dsl_files': dsl_files,
      'syntax_failures': syntax_failures,
      'display': display,
      'is_red': is_red,
  }


def check_readme(repo_path, repo_name):
  readme_path = os.path.join(repo_path, 'README.md')
  if not os.path.exists(readme_path):
    is_red = repo_name not in UNRELEASED_HOSTS
    return {
        'exists': False,
        'pictures': 0,
        'broken_images': [],
        'broken_autorun': [],
        'missing_alt': 0,
        'oversized': [],
        'display': 'no README',
        'is_red': is_red,
    }

  with open(readme_path, 'r', errors='ignore') as f:
    text = f.read()

  img_matches = list(
      re.finditer(
          r'<img\s+([^>]*?)src=[\"\']([^\"\']+)[\"\']([^>]*?)>', text, re.I
      )
  )
  md_matches = list(re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', text))

  pictures = len(img_matches) + len(md_matches)
  broken_images = []
  missing_alt = 0
  oversized = []

  for m in img_matches:
    attrs = m.group(1) + ' ' + m.group(3)
    src = m.group(2).strip()
    alt_match = re.search(r'alt=[\"\']([^\"\']*)[\"\']', attrs, re.I)
    if not alt_match or not alt_match.group(1).strip():
      missing_alt += 1

    if not (src.startswith('http://') or src.startswith('https://')):
      local_file = os.path.join(repo_path, src.split('?')[0].split('#')[0])
      if not os.path.exists(local_file):
        broken_images.append(src)
      else:
        sz = os.path.getsize(local_file)
        fname = os.path.basename(local_file)
        if sz > 600 * 1024 and fname not in ALLOWED_OVERSIZED:
          oversized.append(f'{fname} ({sz // 1024}KB)')

  for m in md_matches:
    alt = m.group(1).strip()
    src = m.group(2).strip()
    if not alt:
      missing_alt += 1
    if not (src.startswith('http://') or src.startswith('https://')):
      local_file = os.path.join(repo_path, src.split('?')[0].split('#')[0])
      if not os.path.exists(local_file):
        broken_images.append(src)
      else:
        sz = os.path.getsize(local_file)
        fname = os.path.basename(local_file)
        if sz > 600 * 1024 and fname not in ALLOWED_OVERSIZED:
          oversized.append(f'{fname} ({sz // 1024}KB)')

  broken_autorun = []
  autorun_matches = re.findall(
      r'lmctl(?: autorun)?\s+(https://raw\.githubusercontent\.com/lmctl-ai/([^/]+)/([^/]+)/([^\s`\"\'\)<>]+))',
      text,
  )
  for url, rname, branch, file_path in autorun_matches:
    file_path = file_path.rstrip('.,;')
    if rname == repo_name:
      target_f = os.path.join(repo_path, file_path)
      if not os.path.exists(target_f):
        broken_autorun.append(file_path)

  is_red = bool(broken_images or broken_autorun)

  details = []
  if broken_images:
    details.append(f'{len(broken_images)} broken img')
  if broken_autorun:
    details.append(f'{len(broken_autorun)} bad autorun')
  if missing_alt:
    details.append(f'{missing_alt} no-alt')
  if oversized:
    details.append(f'{len(oversized)} oversized')

  detail_str = f" ({', '.join(details)})" if details else ''
  display = f'{pictures} pics{detail_str}'

  return {
      'exists': True,
      'pictures': pictures,
      'broken_images': broken_images,
      'broken_autorun': broken_autorun,
      'missing_alt': missing_alt,
      'oversized': oversized,
      'display': display,
      'is_red': is_red,
  }


def check_git(repo_path, public_path=None):
  p_status = subprocess.run(
      ['git', '-C', repo_path, 'status', '--porcelain'],
      capture_output=True,
      text=True,
  )
  dirty_lines = [l for l in p_status.stdout.splitlines() if l.strip()]
  is_dirty = len(dirty_lines) > 0

  p_ab = subprocess.run(
      ['git', '-C', repo_path, 'rev-list', '--left-right', '--count', 'HEAD...@{u}'],
      capture_output=True,
      text=True,
  )
  ahead = 0
  behind = 0
  if p_ab.returncode == 0 and p_ab.stdout.strip():
    parts = p_ab.stdout.strip().split()
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
      ahead = int(parts[0])
      behind = int(parts[1])
  else:
    p_ab_fb = subprocess.run(
        [
            'git',
            '-C',
            repo_path,
            'rev-list',
            '--left-right',
            '--count',
            'HEAD...origin/main',
        ],
        capture_output=True,
        text=True,
    )
    if p_ab_fb.returncode == 0 and p_ab_fb.stdout.strip():
      parts = p_ab_fb.stdout.strip().split()
      if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        ahead = int(parts[0])
        behind = int(parts[1])

  pub_dirty = 0
  if public_path and os.path.isdir(public_path):
    p_pub = subprocess.run(
        ['git', '-C', public_path, 'status', '--porcelain'],
        capture_output=True,
        text=True,
    )
    pub_lines = [l for l in p_pub.stdout.splitlines() if l.strip()]
    pub_dirty = len(pub_lines)
    if pub_dirty > 0:
      is_dirty = True

  if is_dirty:
    if pub_dirty > 0 and len(dirty_lines) > 0:
      status_str = f'dirty(priv:{len(dirty_lines)},pub:{pub_dirty})'
    elif pub_dirty > 0:
      status_str = f'dirty(pub:{pub_dirty})'
    else:
      status_str = f'dirty({len(dirty_lines)})'
  else:
    status_str = 'clean'

  ab_str = f'{ahead}↑ {behind}↓'
  display = f'{status_str}, {ab_str}'

  return {
      'is_dirty': is_dirty,
      'dirty_count': len(dirty_lines) + pub_dirty,
      'ahead': ahead,
      'behind': behind,
      'display': display,
      'is_red': False,
  }


def check_durable_memory(repo_path, is_closed=False):
  # In closed-source peer model, durable-memory is in private repo only
  dm = os.path.join(repo_path, 'durable-memory')
  if not os.path.exists(dm) and os.path.basename(repo_path.rstrip('/')).endswith('-sample'):
    # sample repos are teaching projects: their README is the documentation
    return {'exists': False, 'index_exists': False, 'unindexed': [], 'display': 'n/a (sample)', 'is_red': False}
  if not os.path.exists(dm):
    return {
        'exists': False,
        'index_exists': False,
        'unindexed': [],
        'display': 'no dm/',
        'is_red': True,
    }

  idx = os.path.join(dm, 'index.md')
  if not os.path.exists(idx):
    return {
        'exists': True,
        'index_exists': False,
        'unindexed': [],
        'display': 'no index.md',
        'is_red': True,
    }

  with open(idx, 'r', errors='ignore') as f:
    idx_text = f.read()

  dm_files = [f for f in os.listdir(dm) if os.path.isfile(os.path.join(dm, f))]
  unindexed = [f for f in dm_files if f != 'index.md' and f not in idx_text]

  if unindexed:
    return {
        'exists': True,
        'index_exists': True,
        'unindexed': unindexed,
        'display': f'unindexed({len(unindexed)})',
        'is_red': True,
    }

  return {
      'exists': True,
      'index_exists': True,
      'unindexed': [],
      'display': 'OK',
      'is_red': False,
  }


def check_stale_names(repo_path, public_path=None):
  stale_hits = []
  targets = [os.path.join(repo_path, 'README.md')]
  dm = os.path.join(repo_path, 'durable-memory')
  if os.path.exists(dm):
    for f in os.listdir(dm):
      fp = os.path.join(dm, f)
      if os.path.isfile(fp):
        targets.append(fp)

  if public_path and os.path.isdir(public_path):
    pub_readme = os.path.join(public_path, 'README.md')
    if os.path.exists(pub_readme) and pub_readme not in targets:
      targets.append(pub_readme)

  for t in targets:
    if os.path.exists(t):
      try:
        with open(t, 'r', errors='ignore') as fh:
          content = fh.read().lower()
        for w in STALE_WORDS:
          if w in content:
            stale_hits.append(f'{os.path.basename(t)}:{w}')
      except Exception:
        pass

  is_red = bool(stale_hits)
  display = f'stale({len(stale_hits)})' if stale_hits else '0'

  return {
      'stale_hits': stale_hits,
      'display': display,
      'is_red': is_red,
  }


def audit_repo(target):
  name = target['name']
  is_closed = target['is_closed']
  path = target['path']
  priv_path = target.get('private_path')
  pub_path = target.get('public_path')

  if not is_closed:
    ci = check_ci(name)
    rel = check_release(name)
    sdk = check_sdk_pin(path, name)
    compiler = check_compiler_pin(path, name)
    examples = check_examples(path, name)
    readme = check_readme(path, name)
    git_info = check_git(path)
    dm = check_durable_memory(path)
    stale = check_stale_names(path)

    is_red = (
        ci['is_red']
        or rel['is_red']
        or sdk['is_red']
        or compiler['is_stale']
        or readme['is_red']
        or dm['is_red']
        or stale['is_red']
    )

    return {
        'name': name,
        'path': path,
        'is_closed': False,
        'ci': ci,
        'release': rel,
        'sdk': sdk,
        'compiler': compiler,
        'examples': examples,
        'readme': readme,
        'git': git_info,
        'durable_memory': dm,
        'stale': stale,
        'is_red': is_red,
    }

  # --- Closed-source peer model audit ---
  actionable_issues = []

  # Visibility check
  vis = check_visibility(name)
  if not vis['is_ok']:
    actionable_issues.extend(vis['issues'])

  # Secret check
  has_token = check_release_token(name)
  if not has_token:
    actionable_issues.append(f'Missing RELEASE_TOKEN secret in lmctlhq/{name}')

  # Private and Public CI checks
  priv_ci = check_private_ci(name)
  pub_ci = check_public_ci(name)

  if priv_ci['is_red']:
    actionable_issues.append(
        f"Private CI {priv_ci['conclusion']} ({priv_ci.get('run_url', '')})"
    )
  if pub_ci['is_red']:
    actionable_issues.append(
        f"Public CI {pub_ci['conclusion']} ({pub_ci.get('run_url', '')})"
    )

  # Combined CI display for main table row
  if priv_ci['is_red']:
    ci_display = priv_ci['display']
  elif pub_ci['is_red']:
    ci_display = pub_ci['display']
  elif priv_ci['display'] in ('queued', 'in_progress'):
    ci_display = priv_ci['display']
  elif pub_ci['display'] in ('queued', 'in_progress'):
    ci_display = pub_ci['display']
  elif pub_ci['display'] == 'PASS':
    ci_display = 'PASS'
  elif priv_ci['display'] in ('PASS', 'no runs (OK)'):
    ci_display = 'PASS'
  else:
    ci_display = priv_ci['display']

  combined_ci = {
      'display': ci_display,
      'is_red': priv_ci['is_red'] or pub_ci['is_red'],
      'private_ci': priv_ci,
      'public_ci': pub_ci,
  }

  # Public release check
  rel = check_release(name, is_closed=True, private_path=priv_path)
  if rel['is_red']:
    actionable_issues.extend([f"Release: {i}" for i in rel.get('issues', [])])

  # Examples check in public repo (with lmscript --check)
  content_path = pub_path or priv_path
  examples = check_examples(content_path, name, is_closed=True)
  if examples['is_red']:
    actionable_issues.append(
        'Examples failed syntax check:'
        f" {', '.join(examples['syntax_failures'])}"
    )

  # README check on public repo
  readme = check_readme(content_path, name)
  if readme['broken_images']:
    actionable_issues.append(f"Broken images: {readme['broken_images']}")
  if readme['broken_autorun']:
    actionable_issues.append(
        f"Broken autorun files: {readme['broken_autorun']}"
    )

  # Git check (both private and public trees)
  git_info = check_git(priv_path or path, public_path=pub_path)

  # Durable memory check (checked on private checkout only)
  if priv_path and os.path.isdir(priv_path):
    dm = check_durable_memory(priv_path, is_closed=True)
  else:
    dm = {
        'exists': True,
        'index_exists': True,
        'unindexed': [],
        'display': 'OK',
        'is_red': False,
    }
  if dm['is_red']:
    actionable_issues.append(f"Durable memory: {dm['display']}")

  # SDK pin on private checkout
  sdk = check_sdk_pin(priv_path or path, name)
  if sdk['is_red']:
    actionable_issues.append(f"SDK lock: {sdk['display']}")

  # Compiler pin
  compiler = check_compiler_pin(priv_path or path, name)
  if compiler['is_stale']:
    actionable_issues.append(
        f"Stale compiler pin: {compiler['display']} < 0.2.420"
        f" ({', '.join(compiler['stale_pins'])})"
    )

  # Stale names
  stale = check_stale_names(priv_path or path, public_path=pub_path)
  if stale['is_red']:
    actionable_issues.append(f"Stale identifiers: {stale['stale_hits']}")

  is_red = bool(actionable_issues)

  return {
      'name': name,
      'path': priv_path or path,
      'is_closed': True,
      'private_path': priv_path,
      'public_path': pub_path,
      'private_url': f'https://github.com/lmctlhq/{name}',
      'public_url': f'https://github.com/lmctl-ai/{name}',
      'private_ci': priv_ci,
      'public_ci': pub_ci,
      'visibility': vis,
      'has_release_token': has_token,
      'ci': combined_ci,
      'release': rel,
      'sdk': sdk,
      'compiler': compiler,
      'examples': examples,
      'readme': readme,
      'git': git_info,
      'durable_memory': dm,
      'stale': stale,
      'is_red': is_red,
      'issues': actionable_issues,
  }


def pad(txt, w):
  raw_len = len(re.sub(r'\033\[[0-9;]*m', '', txt))
  return txt + ' ' * max(0, w - raw_len)


def print_products_table(results):
  closed_map = {r['name']: r for r in results if r.get('is_closed')}

  # If running for a single open repo, don't show products table
  if not closed_map and len(results) == 1:
    return

  col_widths = {
      'name': 11,
      'priv_url': 38,
      'pub_url': 39,
      'release': 10,
      'age': 7,
      'assets': 8,
      'pub_ci': 12,
      'priv_ci': 24,
  }

  header_line = (
      f"{'Product':<{col_widths['name']}} "
      f"{'Private Repo':<{col_widths['priv_url']}} "
      f"{'Public Repo':<{col_widths['pub_url']}} "
      f"{'Release':<{col_widths['release']}} "
      f"{'Age':<{col_widths['age']}} "
      f"{'Assets':<{col_widths['assets']}} "
      f"{'Public CI':<{col_widths['pub_ci']}} "
      f"{'Private CI':<{col_widths['priv_ci']}}"
  )

  sep_len = len(header_line) + 2
  print('=' * sep_len)
  print(bold('CLOSED-SOURCE PRODUCTS'))
  print('=' * sep_len)
  print(bold(header_line))
  print('-' * sep_len)

  # Show audited closed products first, or all 9 products if full dashboard
  display_names = [p for p in CLOSED_SOURCE_PRODUCTS if p in closed_map]
  if len(results) > 1:
    # Full dashboard: include all 9 products
    for p in CLOSED_SOURCE_PRODUCTS:
      if p not in display_names:
        display_names.append(p)

  for prod in sorted(display_names):
    r = closed_map.get(prod)
    if r:
      c_name = red(prod) if r['is_red'] else prod
      priv_url = r['private_url']
      pub_url = r['public_url']
      rel_tag = r['release']['tag'] or '-'
      c_rel = green(rel_tag) if r['release']['tag'] else rel_tag
      age = r['release'].get('age_str') or '-'
      exp_plat = r['release'].get('expected_platforms', 5)
      check_mark = (
          '✓'
          if (
              r['release']['has_sha256']
              and r['release'].get('has_license')
              and r['release'].get('has_notices')
              and not r['release'].get('extras')
          )
          else '✗'
      )
      assets_disp = (
          f"{r['release']['platform_count']}/{exp_plat} {check_mark}"
          if r['release']['tag']
          else '-'
      )
      if '✓' in assets_disp:
        c_assets = green(assets_disp)
      elif '✗' in assets_disp:
        c_assets = red(assets_disp)
      else:
        c_assets = assets_disp

      pub_ci_disp = r['public_ci']['display']
      if r['public_ci']['is_red']:
        c_pub_ci = red(pub_ci_disp)
      elif pub_ci_disp == 'PASS':
        c_pub_ci = green(pub_ci_disp)
      elif pub_ci_disp in ('queued', 'in_progress'):
        c_pub_ci = yellow(pub_ci_disp)
      else:
        c_pub_ci = pub_ci_disp

      priv_ci_disp = r['private_ci']['display']
      if r['private_ci']['is_red']:
        c_priv_ci = red(priv_ci_disp)
      elif 'HOLD' in priv_ci_disp:
        c_priv_ci = yellow(priv_ci_disp)
      elif priv_ci_disp in ('PASS', 'no runs (OK)'):
        c_priv_ci = green(priv_ci_disp)
      elif priv_ci_disp in ('queued', 'in_progress'):
        c_priv_ci = yellow(priv_ci_disp)
      else:
        c_priv_ci = priv_ci_disp
    else:
      # Product currently staging / unflipped
      c_name = prod
      priv_url = f'https://github.com/lmctlhq/{prod}'
      pub_url = f'https://github.com/lmctl-ai/{prod}'
      # Get release if present on lmctl-ai
      q_rel = check_release(prod)
      rel_tag = q_rel['tag'] or '-'
      c_rel = rel_tag
      age = q_rel.get('age_str') or '-'
      exp_plat = q_rel.get('expected_platforms', 5)
      check_mark = '✓' if q_rel['has_sha256'] else '✗'
      assets_disp = (
          f"{q_rel['platform_count']}/{exp_plat} {check_mark}"
          if q_rel['tag']
          else '-'
      )
      c_assets = assets_disp
      c_pub_ci = 'staging'
      q_priv_ci = check_private_ci(prod)
      priv_ci_disp = q_priv_ci['display']
      if q_priv_ci['is_red']:
        c_priv_ci = red(priv_ci_disp)
      elif 'HOLD' in priv_ci_disp:
        c_priv_ci = yellow(priv_ci_disp)
      elif priv_ci_disp in ('PASS', 'no runs (OK)'):
        c_priv_ci = green(priv_ci_disp)
      else:
        c_priv_ci = priv_ci_disp

    line = (
        f"{pad(c_name, col_widths['name'])} "
        f"{pad(priv_url, col_widths['priv_url'])} "
        f"{pad(pub_url, col_widths['pub_url'])} "
        f"{pad(c_rel, col_widths['release'])} "
        f"{pad(age, col_widths['age'])} "
        f"{pad(c_assets, col_widths['assets'])} "
        f"{pad(c_pub_ci, col_widths['pub_ci'])} "
        f"{pad(c_priv_ci, col_widths['priv_ci'])}"
    )
    print(line)

  print('=' * sep_len)
  print(
      cyan(
          'Legend: HOLD (actions disabled / budget) = private Actions paused on'
          ' budget hold (not a failure); FAIL = real failure.'
      )
  )
  print()


def print_table(results):
  # Print dedicated PRODUCTS table at top if closed products are present
  print_products_table(results)

  col_widths = {
      'name': 14,
      'ci': 24,
      'release': 23,
      'sdk': 22,
      'compiler': 10,
      'readme': 26,
      'git': 15,
      'dm': 10,
      'stale': 8,
  }

  header_line = (
      f"{'Repo':<{col_widths['name']}} "
      f"{'CI (main)':<{col_widths['ci']}} "
      f"{'Release':<{col_widths['release']}} "
      f"{'SDK Pin':<{col_widths['sdk']}} "
      f"{'Compiler':<{col_widths['compiler']}} "
      f"{'README':<{col_widths['readme']}} "
      f"{'Git Tree':<{col_widths['git']}} "
      f"{'Durable':<{col_widths['dm']}} "
      f"{'Stale':<{col_widths['stale']}}"
  )

  sep_len = len(header_line) + 2
  print('=' * sep_len)
  print(bold(header_line))
  print('-' * sep_len)

  total_repos = len(results)
  red_count = 0
  ci_failures = 0
  broken_links = 0
  missing_dm = 0
  stale_names_cnt = 0
  stale_pins_cnt = 0
  stale_compiler_cnt = 0
  dirty_trees_cnt = 0

  for r in results:
    if r['is_red']:
      red_count += 1
    if r['ci']['is_red']:
      ci_failures += 1
    if r['readme']['broken_images'] or r['readme']['broken_autorun']:
      broken_links += 1
    if r['durable_memory']['is_red']:
      missing_dm += 1
    if r['stale']['is_red']:
      stale_names_cnt += 1
    if r['sdk']['is_stale']:
      stale_pins_cnt += 1
    if r['compiler']['is_stale']:
      stale_compiler_cnt += 1
    if r['git']['is_dirty']:
      dirty_trees_cnt += 1

    # Format cells with color
    # Repo
    c_name = red(r['name']) if r['is_red'] else r['name']

    # CI
    ci_disp = r['ci']['display']
    if r['ci']['is_red']:
      c_ci = red(ci_disp)
    elif ci_disp == 'PASS':
      c_ci = green(ci_disp)
    elif ci_disp in ('queued', 'in_progress'):
      c_ci = yellow(ci_disp)
    else:
      c_ci = ci_disp

    # Release
    rel_disp = r['release']['display']
    if r['release']['is_red']:
      c_rel = red(rel_disp)
    elif '✓' in rel_disp:
      c_rel = green(rel_disp)
    else:
      c_rel = rel_disp

    # SDK
    sdk_disp = r['sdk']['display']
    if r['sdk']['is_red']:
      c_sdk = red(sdk_disp)
    elif r['sdk']['is_stale']:
      c_sdk = yellow(sdk_disp)
    elif sdk_disp == 'synced':
      c_sdk = green(sdk_disp)
    elif 'std migration pending' in sdk_disp:
      c_sdk = yellow(sdk_disp)
    else:
      c_sdk = sdk_disp

    # Compiler
    comp_disp = r['compiler']['display']
    if r['compiler']['is_stale']:
      c_comp = yellow(comp_disp)
    elif comp_disp == '0.2.420':
      c_comp = green(comp_disp)
    else:
      c_comp = comp_disp

    # README
    rdm_disp = r['readme']['display']
    if r['readme']['is_red']:
      c_rdm = red(rdm_disp)
    elif 'no-alt' in rdm_disp or 'oversized' in rdm_disp:
      c_rdm = yellow(rdm_disp)
    else:
      c_rdm = green(rdm_disp)

    # Git
    git_disp = r['git']['display']
    if r['git']['is_dirty']:
      c_git = yellow(git_disp)
    else:
      c_git = green(git_disp)

    # Durable
    dm_disp = r['durable_memory']['display']
    if r['durable_memory']['is_red']:
      c_dm = red(dm_disp)
    else:
      c_dm = green(dm_disp)

    # Stale
    stale_disp = r['stale']['display']
    if r['stale']['is_red']:
      c_stale = red(stale_disp)
    else:
      c_stale = green(stale_disp)

    line = (
        f"{pad(c_name, col_widths['name'])} "
        f"{pad(c_ci, col_widths['ci'])} "
        f"{pad(c_rel, col_widths['release'])} "
        f"{pad(c_sdk, col_widths['sdk'])} "
        f"{pad(c_comp, col_widths['compiler'])} "
        f"{pad(c_rdm, col_widths['readme'])} "
        f"{pad(c_git, col_widths['git'])} "
        f"{pad(c_dm, col_widths['dm'])} "
        f"{pad(c_stale, col_widths['stale'])}"
    )
    print(line)

  print('=' * sep_len)
  summary_text = (
      f'Summary: {total_repos} repos audited. '
      f'{ci_failures} CI failures, '
      f'{broken_links} broken link repos, '
      f'{missing_dm} missing index repos, '
      f'{stale_names_cnt} stale name repos, '
      f'{stale_pins_cnt} stale SDK pins, '
      f'{stale_compiler_cnt} stale compiler pins, '
      f'{dirty_trees_cnt} dirty trees.'
  )
  if red_count > 0:
    print(bold(red(summary_text)))
  else:
    print(bold(green(summary_text)))

  # Print details for any red items
  if red_count > 0:
    print('\n' + bold(red('Actionable Issues:')))
    for r in results:
      if r['is_red']:
        issues = r.get('issues', [])
        if not issues:
          # Fallback issue generation for standard repos
          if r['ci']['is_red']:
            issues.append(
                f"CI {r['ci']['conclusion']} ({r['ci'].get('run_url', '')})"
            )
          if r['release']['is_red']:
            issues.append(f"Release incomplete: {r['release']['display']}")
          if r['sdk']['is_red']:
            issues.append(f"SDK lock: {r['sdk']['display']}")
          if r['compiler']['is_stale']:
            issues.append(
                f"Stale compiler pin: {r['compiler']['display']} < 0.2.420"
                f" ({', '.join(r['compiler']['stale_pins'])})"
            )
          if r['readme']['broken_images']:
            issues.append(f"Broken images: {r['readme']['broken_images']}")
          if r['readme']['broken_autorun']:
            issues.append(
                f"Broken autorun files: {r['readme']['broken_autorun']}"
            )
          if r['durable_memory']['is_red']:
            issues.append(f"Durable memory: {r['durable_memory']['display']}")
          if r['stale']['is_red']:
            issues.append(f"Stale identifiers: {r['stale']['stale_hits']}")
        print(f"  * {bold(r['name'])}: {'; '.join(issues)}")

  info_repos = [r for r in results if r['examples']['dsl_count'] > 0]
  if info_repos:
    print(
        '\n'
        + bold(
            cyan(
                'Info Notes (examples with _dsl_ spelling; _lmcode_ expected):'
            )
        )
    )
    for r in info_repos:
      print(
          f"  * {bold(r['name'])}: {r['examples']['dsl_count']} file(s) use"
          f" _dsl_ ({r['examples']['lmcode_count']} use _lmcode_)"
      )


def fix_pins(results):
  print(
      bold(
          '\n--- Running --fix-pins: Synchronizing stale SDK pins one repo at'
          ' a time ---'
      )
  )

  repos_root = get_repos_root()
  cpp_dir = os.environ.get('LMCODE_CPP') or os.path.join(
      repos_root, 'lmcode-cpp'
  )

  # Fetch origin in lmcode-cpp first
  if os.path.exists(cpp_dir):
    subprocess.run(
        ['git', '-C', cpp_dir, 'fetch', 'origin'],
        check=False,
    )

  for r in results:
    sdk_info = r['sdk']
    if not sdk_info['has_lock'] or not sdk_info['is_stale']:
      continue

    repo_path = r['path']
    repo_name = r['name']

    # Check git status for dirtiness
    p_stat = subprocess.run(
        ['git', '-C', repo_path, 'status', '--porcelain'],
        capture_output=True,
        text=True,
    )
    if p_stat.stdout.strip():
      print(yellow(f'Skipping {repo_name}: working tree is dirty.'))
      continue

    # Look for sync script
    sync_script = None
    if os.path.exists(os.path.join(repo_path, 'scripts', 'sync-sdk.sh')):
      sync_script = ['bash', 'scripts/sync-sdk.sh']
    elif os.path.exists(os.path.join(repo_path, 'scripts', 'sync-sdk.py')):
      sync_script = ['python3', 'scripts/sync-sdk.py']

    if not sync_script:
      print(yellow(f'Skipping {repo_name}: no sync-sdk script found.'))
      continue

    print(
        f"Syncing {repo_name} (currently {sdk_info['behind']} commits"
        ' behind)...'
    )
    env = os.environ.copy()
    env['LMCODE_CPP'] = cpp_dir

    # Run sync
    p_sync = subprocess.run(
        sync_script, cwd=repo_path, env=env, capture_output=True, text=True
    )
    if p_sync.returncode != 0:
      print(red(f'Sync script failed for {repo_name}: {p_sync.stderr.strip()}'))
      subprocess.run(
          ['git', '-C', repo_path, 'checkout', '--', '.'], check=False
      )
      continue

    # Run cheap test / verification
    verify_cmd = None
    if sync_script[0] == 'bash':
      verify_cmd = sync_script + ['--verify']

    verified = True
    if verify_cmd:
      p_ver = subprocess.run(
          verify_cmd, cwd=repo_path, env=env, capture_output=True, text=True
      )
      if p_ver.returncode != 0:
        verified = False
        print(
            red(f'Verification failed for {repo_name}: {p_ver.stderr.strip()}')
        )

    if not verified:
      subprocess.run(
          ['git', '-C', repo_path, 'checkout', '--', '.'], check=False
      )
      continue

    # Check what changed
    p_after = subprocess.run(
        ['git', '-C', repo_path, 'status', '--porcelain'],
        capture_output=True,
        text=True,
    )
    if not p_after.stdout.strip():
      print(f'No files changed in {repo_name}.')
      continue

    # Get new commit from lock
    new_commit = 'latest'
    lock_file = os.path.join(repo_path, 'sdk.lock')
    if os.path.exists(lock_file):
      with open(lock_file) as lf:
        for line in lf:
          if line.startswith('commit='):
            new_commit = line.split('=', 1)[1].strip()[:7]
            break

    # Stage, commit and push
    subprocess.run(
        [
            'git',
            '-C',
            repo_path,
            'add',
            'sdk.lock',
            'cpp/',
            'sdk/',
            'scripts/merge-std.py',
        ],
        check=False,
    )
    subprocess.run(['git', '-C', repo_path, 'add', '-u'], check=False)

    commit_msg = (
        f'chore(sdk): sync SDK pin to lmcode-cpp {new_commit}\n\nCo-Authored-By:'
        ' GeminiFlash <noreply@anthropic.com>'
    )
    p_commit = subprocess.run(
        ['git', '-C', repo_path, 'commit', '-m', commit_msg],
        capture_output=True,
        text=True,
    )
    if p_commit.returncode != 0:
      print(red(f'Commit failed for {repo_name}: {p_commit.stderr.strip()}'))
      continue

    # Pull rebase and push
    p_pull = subprocess.run(
        ['git', '-C', repo_path, 'pull', '--rebase', 'origin', 'main'],
        capture_output=True,
        text=True,
    )
    if p_pull.returncode != 0:
      print(red(f'Pull rebase failed for {repo_name}: {p_pull.stderr.strip()}'))
      continue

    p_push = subprocess.run(
        ['git', '-C', repo_path, 'push', 'origin', 'main'],
        capture_output=True,
        text=True,
    )
    if p_push.returncode != 0:
      print(red(f'Push failed for {repo_name}: {p_push.stderr.strip()}'))
      continue

    print(green(f'Successfully synced, committed, and pushed {repo_name}.'))


def main():
  parser = argparse.ArgumentParser(
      description='Health dashboard for lmctl-ai ecosystem.'
  )
  parser.add_argument(
      '--json', action='store_true', help='Output in JSON format'
  )
  parser.add_argument(
      '--fix-pins', action='store_true', help='Re-sync stale SDK pins'
  )
  parser.add_argument('--repo', type=str, help='Check a single repository')
  args = parser.parse_args()

  repos = discover_repos(args.repo)
  if not repos:
    print(red('No repositories found.'), file=sys.stderr)
    sys.exit(1)

  # Fetch all repo audits concurrently
  with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(audit_repo, repos))

  # Sort by repo name
  results.sort(key=lambda r: r['name'])

  if args.fix_pins:
    fix_pins(results)
    # Clear cache before re-auditing
    with _GH_LOCK:
      _GH_CACHE.clear()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
      results = list(executor.map(audit_repo, repos))
    results.sort(key=lambda r: r['name'])

  if args.json:
    print(json.dumps(results, indent=2))
  else:
    print_table(results)

  # Exit non-zero if any repo is red
  any_red = any(r['is_red'] for r in results)
  sys.exit(1 if any_red else 0)


if __name__ == '__main__':
  main()
