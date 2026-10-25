# Health Dashboard (`scripts/health.sh`)

`scripts/health.sh` and `scripts/health.py` provide a single-command cross-repository health and status dashboard for the entire `lmctl-ai` ecosystem.

## Capabilities

The tool audits all 33 repositories under the local checkouts tree and sibling `lmvideo`:

1. **Latest main CI status**:
   - Queries `gh run list` on the default `main` branch.
   - For failed runs, extracts and lists specific failed job names (e.g. `FAIL [linux-x64, macos-arm64]`).
   - Reports in-progress or queued states during active runs.

2. **Release status**:
   - Queries latest published GitHub release tag, age, and assets.
   - Verifies 4–5 platform binary assets (`linux-x64`, `linux-arm64`, `macos-x64`, `macos-arm64`, `windows-x64`).
   - Verifies presence of `SHA256SUMS`.
   - Categorizes SDK and composition repositories (`lmcode-*`, `lmgallery`) where binary releases are not applicable.

3. **SDK pin freshness (`sdk.lock`)**:
   - Checks pinned commit vs `origin/main` of the upstream SDK repo (`lmcode-cpp`, `lmcode-csharp`, or `lmcode-java`).
   - Reports exact commit distance behind HEAD.
   - Audits whether vendored `lmcode-std.schema.json` matches the upstream SDK standard catalog (`synced` vs `differs`).

4. **README demo page health**:
   - Counts embedded screenshots and diagram pictures.
   - Detects broken local image paths and broken `lmctl autorun` command targets.
   - Flags missing `alt` attributes and oversized assets (> 600 KB).

5. **Working tree and git state**:
   - Detects dirty working trees (modified and untracked files).
   - Tracks ahead/behind commit counts vs upstream remote branches.

6. **Durable memory integrity**:
   - Checks presence of canonical `durable-memory/index.md`.
   - Verifies that all files in `durable-memory/` are fully indexed.

7. **Stale names**:
   - Scans for legacy identifiers (legacy SDK and tool names).

## Usage

```sh
# Run full human-readable table
scripts/health.sh

# Run for a specific repository
scripts/health.sh --repo lmdraw

# Output machine-readable JSON
scripts/health.sh --json

# Automatically re-sync stale SDK pins across clean hosts
scripts/health.sh --fix-pins
```

## `--fix-pins` Safety Guarantees

When `--fix-pins` runs:
1. It skips any repository whose working tree is dirty (`git status --porcelain != ""` to prevent clobbering active worker edits).
2. It executes the host's native `scripts/sync-sdk.sh` or `scripts/sync-sdk.py`.
3. It validates the synced files using `scripts/sync-sdk.sh --verify` and cheap unit checks.
4. If checks fail, it reverts changes (`git checkout -- .`) and leaves the tree clean.
5. If checks pass, it commits with standard trailers, pulls with `--rebase`, and pushes one repo at a time.
