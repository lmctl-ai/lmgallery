# Linux release cycle: Actions staging, local verification, promotion

The nine closed products (`lmaudio`, `lmcad`, `lmdraw`, `lmfilament`, `lmimg`,
`lmmagnum`, `lmoffice`, `lmpdf`, and `lmvideo`) use a two-phase release. The
private repository's workflow builds and tests Linux x86_64 and arm64 on
`ubuntu-22.04` and `ubuntu-22.04-arm`, then creates a prerelease in the matching
public `lmctl-ai/<product>` repository. This box downloads that prerelease for
additional tests; only an explicit `--promote` changes it to the latest release.

This phase publishes exactly `<product>-linux-x64`, `<product>-linux-arm64`,
`SHA256SUMS`, `LICENSE`, `THIRD_PARTY_NOTICES`, and product-required compliance
files. macOS and Windows assets are outside this phase. The version is stamped
by the product workflow exactly as its current CI does, including
`MAJOR.MINOR.<run number>` where that is the established rule.

## Actions staging

The private workflow is `workflow_dispatch` only. Its `linux-x64` and
`linux-arm64` jobs retain each product's real current-CI build and `test.sh`
equivalent, including lmcad and lmfilament's architecture-specific relink
materials. A `stage` job assembles the allowlist, computes `SHA256SUMS`, and
uses `secrets.RELEASE_TOKEN` to create or update a public release with
`draft=false` and `prerelease=true`. Public-content CI remains separate and
must not receive the private token.

Private Actions are intentionally disabled while the organization budget is
exhausted (through November 1). Do not enable them or dispatch a workflow in
this state. If the owner later authorizes re-enabling a repository, the exact
administrative command is printed by the cycle runner:

```sh
gh api repos/lmctlhq/<product>/actions/permissions -X PUT -F enabled=true
```

The templates and generator are ready for deployment; this task did not replace
or run any private workflow. The runner also checks the installed workflow's
contents before dispatch, refusing an older stable-release publisher even when
Actions are enabled. The lightweight `version` job reads the current source's
version series once; both build jobs and staging consume that same run-number tag.

The cost estimate for a Linux-only full run is cents to about one dollar per
product: approximately `$0.006/min` on x64 and `$0.005/min` on arm64.

## Local verification and promotion

Run `scripts/closed-source/release-cycle.sh <product> --dry-run` to inspect the
planned workflow and all safety gates. Without `--dry-run`, the command dispatches
only after confirming that private Actions are enabled and available, waits with
gentle polling, and downloads the resulting prerelease. `--tag <tag>` selects an
existing prerelease for a manual rehearsal without dispatching a workflow.

Local verification then:

1. Verifies every downloaded asset against `SHA256SUMS` and rejects non-Linux
   assets or missing compliance files.
2. Runs the x64 binary's `--version` and `--dsl-schema` checks.
3. Installs the staged x64 hosts on `PATH` using the same public-example host
   installer as public CI, then runs every public example against the staged
   binary.
4. Inspects the arm64 file as an AArch64 ELF and confirms its required glibc
   symbol versions do not exceed 2.35. This local host does not build or run
   arm64 binaries under QEMU in this cycle.
5. Compares `THIRD_PARTY_NOTICES` with the previous release and rejects GPL- or
   AGPL-only dependencies introduced by the candidate.

The runner writes token-free JSON and human reports under
`~/.local/state/lmctl/closed-source-releases/`. Each failure records the phase,
command, log path, and its final 80 log lines. A failed local verification never
promotes the prerelease. Without `--promote`, the runner prints the exact
promotion command. With it, the final step is equivalent to:

```sh
gh release edit <tag> -R lmctl-ai/<product> --prerelease=false --latest
```

After promotion, verify that `install="github:lmctl-ai/<product>@latest"` resolves
to the promoted tag; prereleases must remain excluded from that resolution.
The runner performs this check using a fresh cache and a PATH containing no old
product binary. A failure after the promotion command records
`promotion_applied` and `restore_latest_command` for recovery; it does not hide
that the release was already promoted. Private API calls use the operator's gh
authentication, while the protected release token is restricted to public calls.
Gallery pins are updated only when an example requires a newer API, and then
the affected examples are rerun.

## Manual rehearsal

The rehearsal uses existing public lmaudio assets republished under a throwaway
prerelease tag. It runs the download, checksum, x64/schema, public-example,
arm64-ELF, and notice checks, exercises `--promote` against the throwaway tag,
then deletes the throwaway release and tag. No private workflow is dispatched,
and no private Actions permission is changed. Stub `gh`, `npm`, and compiler
commands under `tests/` cover dry-run, disabled-budget refusal, polling,
verification, and promotion paths without network mutation.

The completed rehearsal used `v0.2.1+rehearsal-20261026T011149`, republishing
the existing lmaudio `v0.2.1` Linux assets. The runner accepted the controlled
build-metadata version, and all 22 public examples passed along with x64 schema,
checksum, arm64 ELF/glibc, and notice-delta checks. Promotion made `@latest`
resolve to the throwaway tag in a fresh isolated cache; cleanup then removed the
release and tag and restored `v0.2.1`. Evidence is recorded at
`~/.local/state/lmctl/closed-source-releases/manual-lmaudio-20261026T011149/rehearsal.json`.
Earlier non-semver and slash-version tags were rejected and cleaned up.
