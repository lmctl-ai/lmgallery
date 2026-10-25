# Closed-source peer repository model

**Status: in-place lmaudio pilot approved; nine-product scope.** No in-place public reset has run yet. Final owner scope is lmdraw,
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
| `lmctl-ai/<name>` | Existing public demo, docs, and release repository with its public history reset | One orphan `main` commit containing README, docs/images, examples plus required inputs, `THIRD_PARTY_NOTICES*`, root `LICENSE` (binary terms), `LICENSE-examples` (MIT), and minimal public CI. The repository identity, URL, settings, issues, and stars remain in place. Private CI publishes five release assets and `SHA256SUMS` here. |

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

Before each flip, put `RELEASE_TOKEN` in the private repository Actions secret
from the protected operator file. Use a fine-grained PAT or GitHub App installation token
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
main push it waits for the private CI to publish the first release before checking
examples that use `install="github:...@latest"`. It does not build source or
receive the release token.

Enable Issues on the public repository so users have a stable support route.
Do not accept implementation/source pull requests there. Documentation and
example contributions may be accepted if the owner wants them; updates to the
same files in `lmctlhq` should be forwarded into the public repository because
the public copy is authoritative. Triage source-revealing reports into the
private tracker without making private implementation details public.

## History, tags, redirects, and selected transition

The owner replaced the transfer plan. For each product, create a new private
`lmctlhq/<name>` repo, disable its Actions during seeding, and mirror all local
source branches and tags into it. This clears any stale redirect at the private
slug without moving the current public repo. Test the private release workflow
before changing the public refs.

Keep the existing public `lmctl-ai/<name>` repository in place. Its URL,
settings, issues, and stars remain. Before rewriting it, save the old main SHA,
all public branches and tags, and every release asset, note, tag, and name under
`/home/mma/staging/closed-source/`. Then force-with-lease the public `main` to
one orphan commit containing the reviewed public tree, remove old public
branches/tags/releases, and re-publish the latest release from the saved assets.
Earlier releases remain in the local backup and source tags remain in the
private mirror. The public `@latest` identity and raw README autorun paths stay
unchanged.

The lmaudio transition boundary is explicit: v0.2.1's five binaries,
`LICENSE` asset, `SHA256SUMS`, and notices are re-published byte-for-byte; the
release body, README, and public root `LICENSE` explain that releases through
v0.2.1 remain MIT and later releases use the Personal Use License. The public
root `LICENSE-examples` continues to cover examples and docs under MIT.

Versioned consumer pins must refer to a release that will still exist publicly.
The lmgallery example already pins lmaudio v0.2.1; the local simulation roadmap
pin at v0.2.0 needs to move to v0.2.1 because older public tags/releases are
removed. See [`closed-source-pin-inventory.md`](closed-source-pin-inventory.md).

Before the public reset, rollback is simply to stop; the private mirror may
remain. After the reset starts, restore the saved public `main` with
`--force-with-lease` against the known orphan SHA, restore every saved branch
and tag from the local mirror, and re-upload the saved release assets and
metadata. Never delete either repository. The public history rewrite is
explicitly owner-authorized only for the staged peer conversion.

## Migration sequence and rollback

Every live step is gated by the product name in
`~/tools/closed-source-approved.txt`, `--apply --i-have-owner-approval`, the
mode-600 `~/.config/lmctl/release_token` file, and the approved release tag.
The token is passed only through stdin to the private repo secret and is never
logged.

| Step | Action after approval | Rollback |
| --- | --- | --- |
| 1. Backup and preflight | Require clean/pushed product source, green current-main CI, no active product pusher, and current staged SHA. Save old public refs plus every release's metadata/assets; verify asset digests and `SHA256SUMS`. | No GitHub mutation has occurred; discard only the new backup/stage files if review stops. |
| 2. Seed private source | Create `lmctlhq/<name>` private with the existing description, disable Actions, `git push --mirror` the source history, and verify private `main` matches source `main`. | Public repo remains unchanged; the private repo can remain for review. |
| 3. Test private publisher | Set the repo secret from the protected file, install the private workflow with `[skip ci]`, enable Actions, and dispatch `publish_test=true`; require the draft release create/delete job to pass with build jobs skipped. | Public repo remains unchanged; leave private source for review and revoke the secret if requested. |
| 4. Rewrite public refs in place | `--force-with-lease` public `main` against its saved SHA, delete other heads and old release tags/releases, and re-publish the saved latest release. | Restore old `main` with a lease against the orphan SHA, mirror back saved refs, and re-upload all saved releases/assets/notes. Never delete the public repo. |
| 5. Verify and update consumers | Download the public latest assets, compare hashes, run the Linux binary, check two raw examples and `@latest`, then refresh consumer pins whose old tags disappeared. | Restore the saved public refs/releases and revert any consumer pin edits. |
| 6. Repoint checkouts | Set `~/repos/dsl/<name>` origin to private source and clone the public checkout as `~/repos/dsl/<name>-public`. | Restore only local remotes/clones; repository histories remain available. |

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

The lmaudio private workflow's `publish_test` dispatch creates and removes a
temporary draft release using `RELEASE_TOKEN` without starting a build. The
workflow-install commit uses `[skip ci]`, so the pilot waits until the next
source change to start its Linux build; later tagged/manual releases run the
five-platform matrix and publish with the cross-repo secret.

`lmplot` remains open source and is excluded. Its existing gnuplot patch and
runtime notices are unchanged by this plan.

## Candidate split planner and owner decisions

The read-only planner is [`scripts/closed-source/split.lms`](../scripts/closed-source/split.lms).
It generates exact tracked-file plans under
`durable-memory/closed-source-plans/`, checks README autorun mappings, scans
public docs for source links, and scans public text for high-confidence secret
patterns. The staging and in-place flip runner is
[`scripts/closed-source/peer-flip.py`](../scripts/closed-source/peer-flip.py),
invoked by [`scripts/closed-source/flip.lms`](../scripts/closed-source/flip.lms).
`--dry-run` is the default; `--stage` writes only the public tree under
`/home/mma/staging/closed-source/`. `--apply` requires a product entry in
`~/tools/closed-source-approved.txt`, the protected release-token file, and an
approved release tag. It creates a private mirror first, then resets public refs
in place after the private publish test.

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
