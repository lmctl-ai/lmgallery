# Health Dashboard (`scripts/health.sh`)

`scripts/health.sh` and `scripts/health.py` provide a single-command cross-repository health and status dashboard for the entire `lmctl-ai` ecosystem.

## Capabilities

The tool audits all repositories under the local checkouts tree and sibling `lmvideo` across both open-source and closed-source peer models:

1. **Closed-Source Peer Model Support**:
   - **Top PRODUCTS Table**: Displays a dedicated status section at the top of the output for closed products (`lmaudio`, `lmcad`, `lmdraw`, `lmfilament`, `lmimg`, `lmmagnum`, `lmoffice`, `lmpdf`, `lmvideo`), tracking:
     * Private repository URL (`https://github.com/lmctlhq/<name>`)
     * Public repository URL (`https://github.com/lmctl-ai/<name>`)
     * Latest release tag and age
     * Platform binary asset count and verification mark
     * Public-content CI status (`public-content` workflow on `lmctl-ai`)
     * Private source CI status (Linux fast CI on `lmctlhq`)
   - **Row Merging**: Merges `<name>` and `<name>-public` checkouts into a single canonical row in the main table.
   - **Public Repository Audits**:
     * Verifies release tag, platform binary assets (4 for `lmvideo`/`lmfilament`/`lmssh`, 5 for others), `SHA256SUMS`, `LICENSE`, and `THIRD_PARTY_NOTICES`.
     * Rejects debug/metrics extras (`*metrics*.json`, `*linkage*.json`, `*timings*.json`, `*minutes*.json`, `.pdb`, `.dSYM`).
     * Verifies platform binary naming adheres to `<name>-<os>-<arch>`.
     * Validates example syntax against installed released hosts with `lmscript --check`.
     * Audits README demo pictures, broken images, and broken autorun links.
     * Public side never flags missing durable-memory (`no dm/` is suppressed).
   - **Private Repository Audits**:
     * Monitors private push CI via `gh run list -R lmctlhq/<name>` (missing recent runs are allowed; failures flagged).
     * Confirms presence of `RELEASE_TOKEN` secret via `gh secret list -R lmctlhq/<name>`.
     * Confirms private/public repository visibility (`lmctlhq/<name>` is PRIVATE, `lmctl-ai/<name>` is PUBLIC).
     * Verifies latest private main HEAD matches commit SHA referenced in public release notes (if present).
     * Validates canonical `durable-memory/index.md` integrity.

2. **Open-Source Repository Audits**:
   - **Latest main CI status**: Queries default `main` branch CI; identifies failing job names (e.g. `FAIL [linux-x64, macos-arm64]`).
   - **Release status**: Queries latest published release tag, age, binary count, and `SHA256SUMS`. Recognizes SDK/composition repos where binary releases are not applicable.
   - **SDK pin freshness (`sdk.lock`)**: Measures commit distance behind SDK upstream (`lmcode-cpp`, `lmcode-csharp`, `lmcode-java`) and std catalog synchronization (`synced` vs `differs`).
   - **Compiler pin**: Audits workflows and scripts for `@lmctl-ai/lmctl` >= 0.2.420.
   - **README demo page health**: Counts images, detects broken image paths and broken `lmctl autorun` command targets, flags missing `alt` attributes and oversized assets (> 600 KB).
   - **Working tree and git state**: Identifies dirty trees and ahead/behind commit counts vs upstream remote branches.
   - **Durable memory integrity**: Confirms `durable-memory/index.md` exists and lists all notes.
   - **Stale names**: Scans for legacy identifiers (legacy SDK and tool names).

3. **Rate Limiting and Performance**:
   - Implements thread-safe in-memory caching of all GitHub CLI (`gh`) responses, eliminating duplicate queries across checks.

## Usage

```sh
# Run full human-readable table
scripts/health.sh

# Run for a specific repository or closed product
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
