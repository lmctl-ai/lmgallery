# Release cycle: implementation notes

The single operator entrypoint now lives in `lmctlhq/lmctl-mono-test`:
`release-cycle.sh`, `releases.json`, and `adapters/{npm,github-release}.sh`.
Its short operator guide is `RELEASING.md`; mono.lmctl owns the cadence.
Adding a standard product requires one registry entry, with no code edits.

```sh
cd /home/mma/repos/lmctlhq/lmctl-mono-test
./release-cycle.sh --all --dry-run
./release-cycle.sh --all --promote
./release-cycle.sh --explain-last
```

The core owns locking, source-SHA selection, budget checks, dispatch intent,
75-second polling and reports in `~/.local/state/lmctl/release-cycle/`.
Adapters expose only `stage`, `test`, and `promote`; pinned candidate metadata
passes through a durable per-repo/per-SHA directory.

GitHub products stage published prereleases in their public lmctl-ai repos.
Only Linux x86_64 and arm64 are built, on Ubuntu 22.04 Actions runners.
The generator/template remains here in `scripts/closed-source/`; it preserves
product build/test recipes and stamps MAJOR.MINOR.GITHUB_RUN_NUMBER.
CMake-only products also update their hardcoded expected-version assertions.
OCCT/Filament relink objects must come from both architecture builds.

The adapter checks every asset checksum, x64 version/schema, all public
examples, arm64 ELF/glibc <=2.35, notices and prior relink requirements.
Promotion explicitly removes prerelease status, sets latest, and checks
fresh-cache lmscript resolution and binary hash. Public host installers use
GitHub's `/releases/latest`, never the first item of a release list.

Private Actions remain disabled during the budget hold. Do not enable or
actually dispatch them without owner authorization. There are no local builds.
Linux minutes cost cents to about $1 per product release; monthly budget $50.

The prior lmaudio rehearsal reused v0.2.1 assets under
`v0.2.1+rehearsal-20261026T011149`: 22 public examples and promotion passed.
Its throwaway release/tag were deleted and latest restored to v0.2.1.
Evidence: `~/.local/state/lmctl/closed-source-releases/manual-lmaudio-20261026T011149/rehearsal.json`.
The superseded lmgallery runner and its CLI-specific tests have been removed;
workflow-generation checks remain public and offline.

Owner update (2026-10-28): lmvideo v0.1.36 is explicitly authorized for native
local Linux release-build/testing and manual on-demand staging; this supersedes
the historical no-local-build statement above for lmvideo. Its registry entry
is manual-only, uses the versioned private runtime/101-example gate, and includes
the complete license archive. Meta-Lead runs `release-cycle.sh lmvideo` to stage
and test, then `release-cycle.sh lmvideo --promote` after staged review. The two
native Ubuntu22.04 jobs build Linux x64/arm64 with Cycles; no production-server
build or implicit daily publication of lmvideo is permitted. Technical evidence
is in lmvideo durable-memory/78-release-0136-local-gate.md.
