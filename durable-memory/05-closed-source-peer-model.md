# Closed-source peer repository model

**Status: lmaudio pilot approved; nine-product scope.** Final owner scope is lmdraw,
lmvideo, lmaudio, lmoffice, lmcad, lmmagnum, lmfilament, lmimg, and lmpdf.
The generated public-only trees are under `/home/mma/staging/closed-source/`.
`lmplot`, `lmphysics`, all other hosts, `lmcode-*`, and `lmgallery` remain open
source and are not migration targets. A future OR-tools host starts private
with a public peer from day one.

## Repository roles

Each included product uses two repositories with the same name:

| Repository | Visibility and role | Contents |
| --- | --- | --- |
| `lmctlhq/<name>` | Private source/build repository | Implementation source, schemas, tests, build scripts, CI, dependency pins, private development history, and the release publisher workflow. |
| `lmctl-ai/<name>` | Fresh public demo, docs, and release repository | One orphan main commit containing README, docs/images, examples plus required inputs, `THIRD_PARTY_NOTICES*`, root `LICENSE` (binary terms), `LICENSE-examples` (MIT), and minimal public CI. Private CI publishes five release assets and `SHA256SUMS` here. |

The public repository is the source of truth for README, docs, example scripts,
and their images. Preserve README links and example repository-relative paths.
In particular,
`https://raw.githubusercontent.com/lmctl-ai/<name>/main/examples/<file>.lms`
must continue to resolve to the same example so README `lmctl autorun` captions
and install commands stay valid. The README/docs/images/examples use MIT under
`LICENSE-examples`; root `LICENSE` is copied from the final-for-now text in
`templates/LICENSE-binaries.md` and governs binaries.
`templates/LICENSE-examples-MIT` supplies the examples/docs MIT text. Full
license texts move under `docs/third-party-licenses/` and notices remain
`THIRD_PARTY_NOTICES*`.

The private source repository may contain its own source license and all build
inputs. Public release notice bundles must be curated from the product's actual
link/runtime closure; copying only `THIRD_PARTY_NOTICES` is insufficient where
the product's license audit requires additional text, source, or relinking
material.

## Private CI and release publication

On each main push, private CI runs a Linux-only fast job. The full five-platform
build/package matrix runs only on `workflow_dispatch` or a version tag: Linux
x64/arm64, macOS x64/arm64, and Windows x64. Do not expose `RELEASE_TOKEN` to
pull-request jobs. The product adapter stages exactly:

```text
<name>-linux-x64
<name>-linux-arm64
<name>-macos-x64
<name>-macos-arm64
<name>-windows-x64.exe
SHA256SUMS
```

The private CI checks out the public repository's `main` beside the source
checkout, puts the freshly built host first on `PATH`, runs the product's own
tests, then runs `lmscript --check` and executes every public example against
that fresh host. This prevents publishing a binary that only works with the
previous release. Any example data, images, fonts, or other runtime inputs must
also be present at the same public paths used by the scripts.

Once all five matrix jobs pass, the publish job creates the approved first
public tag/release, uploads the five binaries and `SHA256SUMS`, and writes
release notes containing the version, source commit, platform list, and
license/notices links. A rerun that collides with an existing version must
fail closed rather than overwrite a release. The chosen first tag is recorded
per product during the coordinated flip.

The owner will provide `RELEASE_TOKEN` as a private repository Actions secret
before the coordinated flip. Use a fine-grained PAT or GitHub App installation token
scoped only to the selected `lmctl-ai/<name>` public repo with `contents:write`;
expose it only to the release job. `GITHUB_TOKEN` from the private repository
does not publish to its peer. The flip runner refuses apply without the token,
the product entry in `~/tools/closed-source-approved.txt`, and the first
release tag. Never print or include the token in artifacts.

## Public CI and support policy

The public repository has a small, read-only workflow on pushes and
documentation/example pull requests. It checks local README links and image
paths, verifies every same-repo raw `lmctl autorun` target exists at the public
path, and runs `lmscript --check` on every `examples/**/*.lms`. On the orphan
push it waits for the private CI to publish the first release before checking
examples that use `install="github:...@latest"`. It does not build source or
receive the release token.

Enable Issues on the public repository so users have a stable support route.
Do not accept implementation/source pull requests there. Documentation and
example contributions may be accepted if the owner wants them; updates to the
same files in `lmctlhq` should be forwarded into the public repository because
the public copy is authoritative. Triage source-revealing reports into the
private tracker without making private implementation details public.

## History, tags, redirects, and selected transition

The owner selected a fresh public history. The flip transfers today's public
repository to `lmctlhq/<name>` (so source history, releases, tags, issues, stars,
and watchers move into the private peer), immediately makes it private, and
creates a new public `lmctl-ai/<name>` with one orphan public-content commit.
The owner states there are no outsider users yet and accepts the loss of public
stars/issues/history. The new public repository begins with no tags/releases;
private CI publishes the first new release after the flip.

Raw README autorun URLs and `install="github:lmctl-ai/<name>@latest"` retain
their path because the new public repo reuses the same owner/name and example
paths. Old `@TAG` pins do not work after history is moved; the consumer
inventory must be updated to the first new release tag. The current inventory
includes lmgallery and other local repositories; see
[`closed-source-pin-inventory.md`](closed-source-pin-inventory.md).

The staged script uses GitHub's transfer endpoint to preserve the old repository
and its full history under `lmctlhq/<name>`, immediately makes it private, then
creates a fresh public repo at the original slug. The new public repo has no old
tags, releases, stars, issues, or source history; the old repository's records
remain in the private peer. Creating the public repo permanently replaces the
transfer redirect. Before the fresh public repo is created, a transfer can be
rolled back by moving the private repo back and restoring visibility. After the
new public repo occupies the slug, a full rollback is unavailable without
delete permissions; use forward recovery and publish a corrected public tree.
GitHub documents the transfer of issues, PRs, releases, stars, watchers and
redirect behavior in [Transferring a repository — GitHub Docs](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository).

## Migration sequence and rollback

Every live step is gated by the product name in
`~/tools/closed-source-approved.txt`, `--apply --i-have-owner-approval`, a
configured `RELEASE_TOKEN`, and an explicit first release tag. The current
instruction is to stage only; no apply is authorized in this pass.

| Step | Action after approval | Rollback |
| --- | --- | --- |
| 1. Inventory and stage | Grep tag pins and record active teams; stage `origin/main` to `/home/mma/staging/closed-source/<name>-public/`; validate docs links, autorun URLs, notices, license files, and secret scans. | Remove only the generated staging tree/manifest; no repository or GitHub state changed. |
| 2. Quiesce and preflight | Require clean/pushed source and consumer trees, green current-main CI, no active pusher, and a staged SHA equal to current `origin/main`. Resolve all consumer pins against the planned first tag. | Stop before transfer; refresh the staged tree and inventory after teams finish their pushes. |
| 3. Approve the coordinated flip | Owner adds the product to `~/tools/closed-source-approved.txt`, provides `RELEASE_TOKEN`, and selects the first release tag. | Do not change GitHub; keep the staged tree ready for review. |
| 4. Transfer and privatize source | Transfer the old public repo to `lmctlhq`, wait for it to appear, set it private immediately, and verify the private flag. | Before creating the replacement public repo, transfer back and restore public visibility. |
| 5. Recreate public peer | Create fresh public `lmctl-ai/<name>` with matching metadata, Issues enabled, Wiki/Projects disabled; push exactly one orphan commit from the staged tree. | After the old slug is reused, the redirect is gone. Without `delete_repo`, use forward recovery; do not try to delete the new repo. |
| 6. Install private CI and first release | Point local source origin to `lmctlhq`; install Linux-fast push CI plus manual/tag five-platform CI; check out public examples; trigger the full workflow and publish the first release through private CI. | Revert the private workflow commit/revoke the secret; repair the public tree and cut a corrected release forward. |
| 7. Verify and update consumers | Download the public binary, check its hash and `--version`, check two raw examples, then update old `@TAG` consumer pins to the first new tag. Update private memory and public README. | Repair consumer pins to an existing public tag and publish a fixed version; preserve the fresh public repo. |
| 8. Repoint checkouts | Set `~/repos/dsl/<name>` origin to private source and clone the public peer as `~/repos/dsl/<name>-public`. | Correct local remotes only; do not rewrite either repository history. |

## Two-checkout sync discipline

Use `~/repos/dsl/<name>` for private source/tests/build/CI and
`~/repos/dsl/<name>-public` for the public README/docs/images/examples/notices.
The public checkout is the only place to author user-facing examples and demo
content; private CI checks out its `main` next to source. Do not copy later
public edits back into the private repo as a competing source of truth.

Before staging, read `origin/main` and record its commit in the stage manifest.
Before apply, require clean and synchronized local branches, recheck `origin/main`
and CI, and refuse if the source hash changed since staging. Quiesce the team
working on the product and any consumer repo whose pinned tag must change.
After the public orphan push, switch the private source checkout's `origin` to
`lmctlhq/<name>` and clone the public peer to the `-public` sibling. For docs or
example changes, commit only in the public checkout; the private workflow then
tests those exact paths. For implementation changes, commit only in private
source and let the workflow validate the public examples against the new host.

## Active-team and stage snapshot

The current no-flip staging inventory is
[`closed-source-staging-inventory.md`](closed-source-staging-inventory.md),
including source SHAs, tree validation, pin counts, and local sync state.
At the current `lmctl running` snapshot, `lmfilament.lmctl:Lead` and one live
lmfilament Researcher session were active; lmplot Lead was active but lmplot is
excluded. The Meta-Lead separately reports lmvideo, lmoffice,
and lmpdf teams as active even though no product-named sessions appeared in
that command output. Those three stay quiescence-gated; lmoffice and lmpdf are
last in the flip order. Staging uses fetched `origin/main` even if a local
checkout is dirty or behind; apply requires the team to stop and local source
to catch up.

## Product licensing review

This table records technical facts from each product's committed licensing
record and notice/release staging files. Preserve those files and re-check the
actual binary link closure on dependency changes. It is not a legal opinion.

| Product | Current obligations to retain with binaries/source package |
| --- | --- |
| `lmdraw` | MIT project/SDK; LunaSVG and PlutoVG MIT; FreeType Project License; stb public-domain notices; bundled Noto Sans/Noto Sans Math SIL-OFL texts; Linux dynamic glibc LGPL-2.1 and static GCC runtime GPL + exception texts. Existing release staging includes `LICENSE`, `THIRD_PARTY_NOTICES`, `licenses/*.txt`, and a source archive; preserve that release checklist. Source: `lmdraw/durable-memory/06-licensing-and-release.md`. |
| `lmvideo` | MIT project; DejaVu font license; Skia BSD-3-Clause; exact linked-pack texts for ICU, Expat, libjpeg/IJG, libpng, zlib, HarfBuzz, libwebp, and FreeType FTL. `scripts/stage-release-notices.sh` copies these into each binary release. FFmpeg/ffprobe are separate user-selected executables, not bundled. The notice warns the Skia pack lacks some per-library texts; retain the staged exact notice bundle and audit every pack update. Source: `lmvideo/THIRD_PARTY_NOTICES.md`, `scripts/stage-release-notices.sh`. |
| `lmaudio` | MIT project; complete upstream notice text for DaisySP, selected Soundpipe modules, KissFFT BSD-3-Clause, MT19937 BSD-3-Clause, PaulStretch, FAUST/STK, lmcode-cpp, and platform runtimes. The build excludes Csound-derived LGPL and GPL `zitarev` modules; keep them excluded. Source: `lmaudio/THIRD_PARTY_NOTICES`. |
| `lmoffice` | MIT host; Open XML SDK and `System.IO.Packaging` MIT notice; .NET 8 runtime/class-library component notices; lmcode-csharp MIT. Keep the lock-file-matched component notices with binaries. Source: `lmoffice/THIRD_PARTY_NOTICES.md`. |
| `lmcad` | MIT host; build123d Apache-2.0 plus NOTICE; PyVista MIT. Linux static OCCT 8.0.1 requires the exact LGPL-2.1 text and Open CASCADE exception plus `lmcad-linux-<arch>-relink-objects.tar.gz`, `OCCT-RELINKING.md`, and `lmcad-occt-relinking-recipe.tar.gz`; static glibc also needs LGPL text, package copyright metadata, application objects, and link instructions. Retain GPL-3 and GCC Runtime Library Exception texts for static GCC runtimes. **Do not omit the OCCT relinking assets.** Source: `lmcad/durable-memory/13-licensing.md`. |
| `lmmagnum` | MIT project; Magnum and Corrade MIT `COPYING` files; stb public-domain/MIT notice; lmcode-cpp MIT; Linux static glibc LGPL-2.1+ and compiler runtime notices. Release staging copies `LICENSE`, `THIRD_PARTY_NOTICES`, and both upstream `COPYING` files. Audit any static-glibc relinking materials required by the exact distributed build. Source: `lmmagnum/THIRD_PARTY_NOTICES.md`, `scripts/stage-release-notices.sh`. |
| `lmfilament` | MIT host; Filament Apache-2.0 `FILAMENT-LICENSE`; notices for the pinned Filament third-party libraries (including SPIR-V, zstd, meshoptimizer, mikktspace, robin-map); LLVM Apache exceptions; Linux static glibc LGPL and GCC/runtime license texts. Preserve the full staged notice inventory with each binary. Source: `lmfilament/THIRD_PARTY_NOTICES.md`. |
| `lmimg` | MIT host; ImageMagick NOTICE, IJG README/license/attribution, selected stb license, Apache-2.0 Roboto, lmcode-cpp MIT, plus platform runtime texts. Linux dynamically links glibc (LGPL-2.1) and statically links image/codec dependencies and GCC runtimes. Keep optional GPL delegates disabled. Source: `lmimg/durable-memory/02-libraries-and-licenses.md`, `THIRD_PARTY_NOTICES`. |
| `lmpdf` | Preserve generated `THIRD_PARTY_NOTICES.md`, full licenses for every locked Rust crate and bundled font, font attribution/hash inventory, and Rust target-runtime notices. Current policy denies GPL/AGPL-only components. Historical Caladea bytes have an Apache-2.0 notice; do not infer font licenses from current upstream names. Source: `lmpdf/durable-memory/08-release.md`, `04-decision.md`. |

The owner approved the current binary-license text in `templates/LICENSE-binaries.md`
for now. The examples/docs MIT license template is `templates/LICENSE-examples-MIT`.
`lmblender` stays open source and is excluded because its Blender/Cycles-derived
binary is GPL-3.0-or-later and requires corresponding source.

For lmaudio, releases through `v0.2.1` remain MIT under the `LICENSE` asset
published with that release. The fresh public repo's root `LICENSE` is the
Lattice Systems Personal Use License for releases after `v0.2.1`; both the
public README and the `v0.2.1` release notes state this boundary. The old release
assets are republished byte-for-byte.

`lmplot` remains open source and is excluded. Its existing gnuplot patch and
runtime notices are unchanged by this plan.

## Candidate split planner and owner decisions

The read-only planner is [`scripts/closed-source/split.lms`](../scripts/closed-source/split.lms).
It generates exact tracked-file plans under
`durable-memory/closed-source-plans/`, checks README autorun mappings, scans
public docs for source links, and scans public text for high-confidence secret
patterns. The staged-tree builder is
[`scripts/closed-source/peer-flip.py`](../scripts/closed-source/peer-flip.py),
invoked by [`scripts/closed-source/flip.lms`](../scripts/closed-source/flip.lms).
`--dry-run` is the default; `--stage` writes only the public tree under
`/home/mma/staging/closed-source/`. `--apply` requires a product entry in
`~/tools/closed-source-approved.txt`, the release token, and a first release
tag. The current owner instruction is stage-only.

The final candidate list is lmdraw, lmvideo, lmaudio, lmoffice, lmcad,
lmmagnum, lmfilament, lmimg, and lmpdf. An OR-tools host is
future-only and has no existing repository plan. `lmplot` remains open source.

Generated tracked-file plans (each includes exact public/private path lists,
CI paths, autorun results, source-link findings, secret-scan status, and release
asset names):

- [lmdraw](closed-source-plans/lmdraw.md)
- [lmvideo](closed-source-plans/lmvideo.md)
- [lmaudio](closed-source-plans/lmaudio.md)
- [lmoffice](closed-source-plans/lmoffice.md)
- [lmcad](closed-source-plans/lmcad.md)
- [lmmagnum](closed-source-plans/lmmagnum.md)
- [lmfilament](closed-source-plans/lmfilament.md)
- [lmimg](closed-source-plans/lmimg.md)
- [lmpdf](closed-source-plans/lmpdf.md)

Owner decisions still required for later products:

1. Quiesce the reported active lmvideo/lmoffice/lmpdf teams and current active
   lmfilament work before each product's apply preflight.
2. Choose a first public release tag per product after confirming the private
   build version, then use the pin inventory to update every consumer.
3. Validate product-specific release packaging, especially lmcad OCCT relink
   materials, and static-glibc obligations.
4. Provide `RELEASE_TOKEN` only when the owner is ready to authorize coordinated
   flips and the private Actions workflow can publish to the matching public
   repo. The lmaudio flip is now owner-approved; do not flip another product without a separate approval.
