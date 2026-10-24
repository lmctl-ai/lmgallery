#!/usr/bin/env python3
"""health.py: Cross-repository health dashboard for lmctl-ai ecosystem.

Audits:
- Latest main CI status (per-job failures listed)
- Latest release tag, age, platform asset count (4-5), SHA256SUMS presence
- sdk.lock commit vs SDK origin/main (commits behind, std fragment status)
- README pictures, broken images, broken autorun links, missing alt text, oversized images
- Git working-tree status (clean/dirty, ahead/behind counts)
- durable-memory/index.md presence and complete indexing
- Stale SDK names (cpp-dsl-sdk, rust-dsl-sdk, lmterraform)

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
import subprocess
import sys
import urllib.parse
import urllib.request

NON_BINARY_REPOS = {
    'lmgallery',
    'lmcode-cpp',
    'lmcode-go',
    'lmcode-rust',
    'lmcode-csharp',
    'lmcode-java',
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

USE_COLOR = sys.stdout.isatty()


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


def discover_repos(target_repo=None):
  candidates = glob.glob('/home/mma/repos/dsl/lm*') + [
      '/home/mma/repos/lmctlhq/lmvideo'
  ]
  repos = []
  for p in sorted(candidates):
    if not os.path.isdir(p):
      continue
    if not os.path.isdir(os.path.join(p, '.git')):
      continue
    name = os.path.basename(p)
    if name == 'lmctl-mono':
      continue
    if target_repo and name != target_repo:
      continue
    repos.append((name, os.path.abspath(p)))
  return repos


def check_ci(repo_name):
  cmd = [
      'gh',
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
  ]
  res = subprocess.run(cmd, capture_output=True, text=True)
  if res.returncode != 0 or not res.stdout.strip():
    cmd_fallback = [
        'gh',
        'run',
        'list',
        '-R',
        f'lmctl-ai/{repo_name}',
        '-L',
        '1',
        '--json',
        'databaseId,status,conclusion,url,headSha',
    ]
    res = subprocess.run(cmd_fallback, capture_output=True, text=True)
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
      job_res = subprocess.run(
          [
              'gh',
              'run',
              'view',
              str(run_id),
              '-R',
              f'lmctl-ai/{repo_name}',
              '--json',
              'jobs',
          ],
          capture_output=True,
          text=True,
      )
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


def check_release(repo_name):
  cmd = [
      'gh',
      'release',
      'list',
      '-R',
      f'lmctl-ai/{repo_name}',
      '-L',
      '1',
      '--json',
      'tagName,publishedAt,name',
  ]
  res = subprocess.run(cmd, capture_output=True, text=True)
  if res.returncode != 0 or not res.stdout.strip():
    is_red = repo_name not in NON_BINARY_REPOS
    return {
        'tag': None,
        'display': 'n/a (SDK/gallery)'
        if repo_name in NON_BINARY_REPOS
        else 'none',
        'is_red': is_red,
        'assets': [],
        'has_sha256': False,
        'platform_count': 0,
        'age_str': '',
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
        'platform_count': 0,
        'age_str': '',
    }

  if not rels:
    is_red = repo_name not in NON_BINARY_REPOS
    return {
        'tag': None,
        'display': 'n/a (SDK/gallery)'
        if repo_name in NON_BINARY_REPOS
        else 'none',
        'is_red': is_red,
        'assets': [],
        'has_sha256': False,
        'platform_count': 0,
        'age_str': '',
    }

  rel = rels[0]
  tag = rel.get('tagName', '')
  published_at = rel.get('publishedAt', '')

  view_cmd = [
      'gh',
      'release',
      'view',
      tag,
      '-R',
      f'lmctl-ai/{repo_name}',
      '--json',
      'assets',
  ]
  v_res = subprocess.run(view_cmd, capture_output=True, text=True)
  assets = []
  if v_res.returncode == 0:
    try:
      v_data = json.loads(v_res.stdout)
      assets = [a.get('name', '') for a in v_data.get('assets', [])]
    except Exception:
      pass

  age_str = ''
  if published_at:
    try:
      dt = datetime.datetime.fromisoformat(published_at.replace('Z', '+00:00'))
      now = datetime.datetime.now(datetime.timezone.utc)
      diff = now - dt
      secs = int(diff.total_seconds())
      if secs < 3600:
        age_str = f'{secs // 60}m'
      elif secs < 86400:
        age_str = f'{secs // 3600}h'
      else:
        age_str = f'{secs // 86400}d'
    except Exception:
      pass

  plat_targets = [
      'linux-x64',
      'linux-arm64',
      'macos-x64',
      'macos-arm64',
      'windows-x64',
  ]
  platform_count = 0
  for p in plat_targets:
    if any(
        p in a
        or (
            p == 'windows-x64'
            and (a.endswith('.exe') or 'windows' in a or 'win-x64' in a)
        )
        for a in assets
    ):
      platform_count += 1

  has_sha256 = any('SHA256' in a.upper() for a in assets)

  is_red = False
  if repo_name not in NON_BINARY_REPOS:
    if platform_count < 4 or not has_sha256:
      is_red = True

  display = (
      f"{tag} ({age_str}, {platform_count}/5, {'✓' if has_sha256 else '✗'})"
  )
  return {
      'tag': tag,
      'published_at': published_at,
      'age_str': age_str,
      'assets': assets,
      'platform_count': platform_count,
      'has_sha256': has_sha256,
      'display': display,
      'is_red': is_red,
  }


def check_sdk_pin(repo_path, repo_name):
  lock_path = os.path.join(repo_path, 'sdk.lock')
  if not os.path.exists(lock_path):
    return {
        'has_lock': False,
        'pinned_repo': None,
        'commit': None,
        'behind': 0,
        'std_status': 'n/a',
        'display': 'n/a',
        'is_red': False,
        'is_stale': False,
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
      if line.startswith('repo=') or line.startswith('repository='):
        pinned_repo = line.split('=', 1)[1].strip()
      elif line.startswith('commit='):
        commit = line.split('=', 1)[1].strip()

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
    }

  if pinned_repo and 'lmcode-csharp' in pinned_repo:
    target_repo_path = '/home/mma/repos/dsl/lmcode-csharp'
  elif pinned_repo and 'lmcode-java' in pinned_repo:
    target_repo_path = '/home/mma/repos/dsl/lmcode-java'
  else:
    target_repo_path = '/home/mma/repos/dsl/lmcode-cpp'

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
  host_std_path = os.path.join(
      repo_path, 'cpp', 'std', 'lmcode-std.schema.json'
  )
  cpp_std_path = '/home/mma/repos/dsl/lmcode-cpp/std/lmcode-std.schema.json'

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

  is_stale = behind > 0
  if behind == 0:
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
  }


def check_readme(repo_path, repo_name):
  readme_path = os.path.join(repo_path, 'README.md')
  if not os.path.exists(readme_path):
    return {
        'exists': False,
        'pictures': 0,
        'broken_images': [],
        'broken_autorun': [],
        'missing_alt': 0,
        'oversized': [],
        'display': 'no README',
        'is_red': True,
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
      r'lmctl autorun\s+(https://raw\.githubusercontent\.com/lmctl-ai/([^/]+)/([^/]+)/([^\s`\"\'\)<>]+))',
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


def check_git(repo_path):
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

  status_str = f'dirty({len(dirty_lines)})' if is_dirty else 'clean'
  ab_str = f'{ahead}↑ {behind}↓'
  display = f'{status_str}, {ab_str}'

  return {
      'is_dirty': is_dirty,
      'dirty_count': len(dirty_lines),
      'ahead': ahead,
      'behind': behind,
      'display': display,
      'is_red': False,
  }


def check_durable_memory(repo_path):
  dm = os.path.join(repo_path, 'durable-memory')
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


def check_stale_names(repo_path):
  stale_hits = []
  targets = [os.path.join(repo_path, 'README.md')]
  dm = os.path.join(repo_path, 'durable-memory')
  if os.path.exists(dm):
    for f in os.listdir(dm):
      fp = os.path.join(dm, f)
      if os.path.isfile(fp):
        targets.append(fp)

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


def audit_repo(repo_info):
  name, path = repo_info
  ci = check_ci(name)
  rel = check_release(name)
  sdk = check_sdk_pin(path, name)
  readme = check_readme(path, name)
  git_info = check_git(path)
  dm = check_durable_memory(path)
  stale = check_stale_names(path)

  is_red = (
      ci['is_red']
      or rel['is_red']
      or sdk['is_red']
      or readme['is_red']
      or dm['is_red']
      or stale['is_red']
  )

  return {
      'name': name,
      'path': path,
      'ci': ci,
      'release': rel,
      'sdk': sdk,
      'readme': readme,
      'git': git_info,
      'durable_memory': dm,
      'stale': stale,
      'is_red': is_red,
  }


def print_table(results):
  col_widths = {
      'name': 14,
      'ci': 18,
      'release': 23,
      'sdk': 22,
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
    else:
      c_sdk = sdk_disp

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

    # Print aligned line without color codes throwing off widths
    def pad(txt, w):
      raw_len = len(re.sub(r'\033\[[0-9;]*m', '', txt))
      return txt + ' ' * max(0, w - raw_len)

    line = (
        f"{pad(c_name, col_widths['name'])} "
        f"{pad(c_ci, col_widths['ci'])} "
        f"{pad(c_rel, col_widths['release'])} "
        f"{pad(c_sdk, col_widths['sdk'])} "
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
        issues = []
        if r['ci']['is_red']:
          issues.append(
              f"CI {r['ci']['conclusion']} ({r['ci'].get('run_url', '')})"
          )
        if r['release']['is_red']:
          issues.append(f"Release incomplete: {r['release']['display']}")
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


def fix_pins(results):
  print(
      bold(
          '\n--- Running --fix-pins: Synchronizing stale SDK pins one repo at'
          ' a time ---'
      )
  )

  # Fetch origin in lmcode-cpp first
  if os.path.exists('/home/mma/repos/dsl/lmcode-cpp'):
    subprocess.run(
        ['git', '-C', '/home/mma/repos/dsl/lmcode-cpp', 'fetch', 'origin'],
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
    env['LMCODE_CPP'] = '/home/mma/repos/dsl/lmcode-cpp'

    # Run sync
    p_sync = subprocess.run(
        sync_script, cwd=repo_path, env=env, capture_output=True, text=True
    )
    if p_sync.returncode != 0:
      print(red(f'Sync script failed for {repo_name}: {p_sync.stderr.strip()}'))
      subprocess.run(['git', '-C', repo_path, 'checkout', '--', '.'], check=False)
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
        print(red(f'Verification failed for {repo_name}: {p_ver.stderr.strip()}'))

    if not verified:
      subprocess.run(['git', '-C', repo_path, 'checkout', '--', '.'], check=False)
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
    # Also add any unstaged vendored files if touched
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
      print(
          red(f'Pull rebase failed for {repo_name}: {p_pull.stderr.strip()}')
      )
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
    # Re-audit after fixing pins
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
