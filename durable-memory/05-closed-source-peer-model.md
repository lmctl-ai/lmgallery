# Closed-source peer repository model

**Status: planning only.** The owner has not confirmed the product list or
authorized any repository creation, transfer, visibility change, secret
creation, or release publication. No product repository or GitHub setting was
changed while preparing this plan.

## Repository roles

Each confirmed product uses two peer repositories with the same name:

| Repository | Visibility and role | Contents |
| --- | --- | --- |
| `lmctlhq/<name>` | Private source/build repository | Implementation source, schemas, tests, build scripts, CI, dependency pins, private development history, and the release publisher workflow. |
| `lmctl-ai/<name>` | Public demo, docs, and release repository | README demo page, docs and images, runnable `examples/*.lms` plus any data they require, `LICENSE-binaries`, `THIRD_PARTY_NOTICES*`, required full license texts, and GitHub Releases with the five binaries and `SHA256SUMS`. |

The public repository is the source of truth for README, docs, example scripts,
and their images. Preserve their repository-relative paths. In particular,
`https://raw.githubusercontent.com/lmctl-ai/<name>/main/examples/<file>.lms`
must continue to resolve to the same example so README `lmctl autorun` captions
and existing links stay valid. Keep the existing public `LICENSE` only with a
clear scope for the public docs/examples and historical MIT content; the new
`LICENSE-binaries` is a separate, owner-approved binary license. Do not
implicitly apply an old MIT license to newly built proprietary binaries.

The private source repository may contain its own source license and all build
inputs. Public release notice bundles must be curated from the product's actual
link/runtime closure; copying only `THIRD_PARTY_NOTICES` is insufficient where
the product's license audit requires additional text, source, or relinking
material.

## Private CI and release publication

The private workflow runs only on trusted `main` pushes or an explicitly
authorized manual run; do not expose `RELEASE_TOKEN` to `pull_request` jobs.
It builds and tests a five-platform matrix: Linux x64/arm64, macOS x64/arm64,
and Windows x64. The product adapter must stage exactly:

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

Use `VERSION_SERIES=MAJOR.MINOR` from a private repository variable and set
`VERSION=MAJOR.MINOR.<github.run_number>` after validating the series. Once all
five matrix jobs pass, a separate publish job creates a public tag/release
`v<VERSION>`, uploads all five assets and `SHA256SUMS`, and writes release
notes containing the version, source commit, platform list, and license/notices
links. A rerun that collides with an existing version must fail closed rather
than overwrite a release.

The private source repository stores `RELEASE_TOKEN` as an organization or
repository Actions secret. Use a fine-grained PAT or GitHub App installation
token scoped only to the selected `lmctl-ai/<name>` public repository with
`contents:write`; expose it only to the release job. `GITHUB_TOKEN` from the
private repository does not publish to its peer. The token must not be printed,
put in release assets, or supplied to example execution.

## Public CI and support policy

The public repository has a small, read-only workflow on pushes and
documentation/example pull requests. It checks local README links and image
paths, verifies every raw `lmctl autorun` target exists at the public path, and
runs `lmscript --check` on every `examples/**/*.lms`. It does not build source
or receive the release token.

Enable Issues on the public repository so users have a stable support route.
Do not accept implementation/source pull requests there. Documentation and
example contributions may be accepted if the owner wants them; updates to the
same files in `lmctlhq` should be forwarded into the public repository because
the public copy is authoritative. Triage source-revealing reports into the
private tracker without making private implementation details public.

## History, tags, redirects, and the recommended repository choice

Old MIT releases and tags remain public indefinitely. Do not rewrite or delete
their history. New releases are proprietary and use new tags; their public tag
points at the public docs/examples tree while the release assets come from the
private CI build. A source commit hash in the release notes connects that
binary to the private source history. Existing `@TAG` installs continue to use
the old public release assets; `@latest` continues to resolve at
`lmctl-ai/<name>` when new releases are published there.

Two transition choices have different consequences:

| Choice | Consequences |
| --- | --- |
| Transfer the existing public repository to `lmctlhq/<name>` and make it private | GitHub transfers commit history, issues, pull requests, releases, stars, and watchers. But old repository URLs redirect to the private peer; that breaks public raw README URLs and public `@TAG` installation until a public peer is restored. If a new repository is created at the old `lmctl-ai/<name>` location, GitHub permanently deletes the transfer redirect. A new public repo does not automatically recreate its prior issue state, tags, or release assets. |
| Keep `lmctl-ai/<name>` public and create a private peer | Public stars, watchers, issues, releases, tags, raw URLs, and the canonical installer path stay with the public repo. A private peer can be initialized from a source-history copy, but GitHub does not automatically transfer issue/PR metadata or stars to that copy. Old source commits remain visible in the public repository's history, as required for historical MIT releases; new proprietary source commits stay private. |

**Recommendation:** keep the existing public repository at the existing
`lmctl-ai/<name>` path as the public demo/release peer, trim only its new
`main` tree to public content in an owner-approved migration, and create a
separate private peer by copying the source history into `lmctlhq/<name>`.
This preserves raw URLs, issue continuity, stars/watchers, old releases, and
`@TAG` pins without transferring a public repository into private visibility.
It does not make already-public MIT source history secret; old history and tags
remain public by design.

GitHub documents that transfers carry issues, pull requests, releases, stars,
and watchers, and that links redirect to the new location; it also warns that
creating a repo at the prior location permanently removes that redirect:
[Transferring a repository — GitHub Docs](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository).

## Migration sequence and rollback

Every live step is owner-gated. The sequence below is a runbook, not an
authorization to perform any step in this task.

| Step | Action after approval | Rollback |
| --- | --- | --- |
| 1. Confirm scope and license | Confirm exact products, binary license text, public support/PR policy, release version series, and each row in the licensing review below. Record the source commit and current tags/releases. | Stop before repository changes; retain the inventory and do not publish. |
| 2. Prepare private peer | Create `lmctlhq/<name>` privately and copy source history/branches/tags. Keep the source of truth explicitly named. | Delete/disable only the newly created empty or copied private peer after preserving any wanted work; the existing public repo remains untouched. |
| 3. Prepare public peer content | In a reviewed change, retain README/docs/images/examples/notices/licenses at their current public paths; remove new source/build/CI content from the public `main` tree. Preserve all prior commits and MIT tags. | Revert the public content commit; never force-push or delete old MIT tags/releases. |
| 4. Add support and CI policy | Keep public Issues enabled, prohibit source PRs, add public link/example CI, and install the private workflow without a release secret first. | Revert the workflow/policy files. Restore the prior public CI if needed. |
| 5. Add release credential | Create and scope `RELEASE_TOKEN` only after a successful no-secret dry-run; limit it to one public repo and release permissions. | Revoke the PAT/App installation immediately, delete the secret, and inspect audit logs if exposure is suspected. |
| 6. Prove a candidate release | Run the five builds, public examples against the fresh host, notice/license staging, hashes, asset names, `@TAG` and `@latest` install checks. Use a draft or nonproduction release if the owner chooses. | Stop publication; remove or mark the candidate release unavailable. Preserve old tags and do not overwrite a release. Revoke the token if needed. |
| 7. Cut over and announce | Publish the first approved proprietary version and document support/install changes. Confirm every README image/raw URL and public example works. | Disable the private publish workflow/secret; restore the last known-good public README/docs commit. Keep already-published historical MIT tags intact and communicate any withdrawn new release. |

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
| `lmblender` | The combined executable is GPL-3.0-or-later because it statically includes Blender GPL internals and GPL-derived LUT data. A proprietary closed-source binary is incompatible with this current closure. Releases already require `lmblender-source-vX.Y.Z.tar.gz` containing the corresponding repository, Blender/Cycles subset, patches, and third-party sources; retain `SOURCE_OFFER.md`, `SOURCES.json`, `docs/RELINKING.md`, GPL/Apache/BSD/MIT/license texts, and Windows relinking materials. Owner must decide whether to exclude this product or replace/relicense the GPL closure before calling its binary proprietary. Source: `lmblender/docs/LICENSE_AUDIT.md`, `THIRD_PARTY_NOTICES.md`. |
| `lmmagnum` | MIT project; Magnum and Corrade MIT `COPYING` files; stb public-domain/MIT notice; lmcode-cpp MIT; Linux static glibc LGPL-2.1+ and compiler runtime notices. Release staging copies `LICENSE`, `THIRD_PARTY_NOTICES`, and both upstream `COPYING` files. Audit any static-glibc relinking materials required by the exact distributed build. Source: `lmmagnum/THIRD_PARTY_NOTICES.md`, `scripts/stage-release-notices.sh`. |
| `lmfilament` | MIT host; Filament Apache-2.0 `FILAMENT-LICENSE`; notices for the pinned Filament third-party libraries (including SPIR-V, zstd, meshoptimizer, mikktspace, robin-map); LLVM Apache exceptions; Linux static glibc LGPL and GCC/runtime license texts. Preserve the full staged notice inventory with each binary. Source: `lmfilament/THIRD_PARTY_NOTICES.md`. |
| `lmplot` | MIT host; gnuplot's custom permissive terms require version/contact marking and shipping every modification as patches with binaries; retain `patches/*.patch` and gnuplot's exact `Copyright` text. Keep DejaVu/Bitstream/Arev font terms, glibc LGPL-2.1+ notice, and GCC runtime exception texts. Source: `lmplot/THIRD_PARTY_NOTICES`, `durable-memory/02-gnuplot-embedding.md`. |
| `lmimg` | MIT host; ImageMagick NOTICE, IJG README/license/attribution, selected stb license, Apache-2.0 Roboto, lmcode-cpp MIT, plus platform runtime texts. Linux dynamically links glibc (LGPL-2.1) and statically links image/codec dependencies and GCC runtimes. Keep optional GPL delegates disabled. Source: `lmimg/durable-memory/02-libraries-and-licenses.md`, `THIRD_PARTY_NOTICES`. |
| `lmpdf` | Preserve generated `THIRD_PARTY_NOTICES.md`, full licenses for every locked Rust crate and bundled font, font attribution/hash inventory, and Rust target-runtime notices. Current policy denies GPL/AGPL-only components. Historical Caladea bytes have an Apache-2.0 notice; do not infer font licenses from current upstream names. Source: `lmpdf/durable-memory/08-release.md`, `04-decision.md`. |

`LICENSE-binaries` text and any additional product-specific source offer must be
reviewed and supplied by the owner; this plan does not draft proprietary legal
terms.

## Candidate split planner and owner decisions

The read-only planner is [`scripts/closed-source/split.lms`](../scripts/closed-source/split.lms).
It generates exact tracked-file plans under
`durable-memory/closed-source-plans/`, checks README autorun mappings, scans
public docs for source links, and scans public text for high-confidence secret
patterns. It is not a migration tool: `--apply` checks for both
`--i-have-owner-approval` and `~/tools/closed-source-approved.txt`, then still
refuses because mutation is intentionally not implemented here.

The current candidate list is provisional: lmdraw, lmvideo, lmaudio, lmoffice,
lmcad, lmblender, lmmagnum, lmfilament, lmplot, lmimg, and lmpdf. An OR-tools
host is future-only and has no plan because no product repository was named.

Generated tracked-file plans (each includes exact public/private path lists,
CI paths, autorun results, source-link findings, secret-scan status, and release
asset names):

- [lmdraw](closed-source-plans/lmdraw.md)
- [lmvideo](closed-source-plans/lmvideo.md)
- [lmaudio](closed-source-plans/lmaudio.md)
- [lmoffice](closed-source-plans/lmoffice.md)
- [lmcad](closed-source-plans/lmcad.md)
- [lmblender](closed-source-plans/lmblender.md)
- [lmmagnum](closed-source-plans/lmmagnum.md)
- [lmfilament](closed-source-plans/lmfilament.md)
- [lmplot](closed-source-plans/lmplot.md)
- [lmimg](closed-source-plans/lmimg.md)
- [lmpdf](closed-source-plans/lmpdf.md)

Owner decisions still required:

1. Confirm the exact product list; in particular, decide whether GPL-bound
   lmblender is excluded or gets a redesigned license-compatible build.
2. Approve the public binary license text and the scope/license for public
   docs/examples; decide whether documentation/example PRs are accepted.
3. Approve keeping existing `lmctl-ai/<name>` public and creating private peers
   by source-history copy, rather than transferring repositories.
4. Set each product's `MAJOR.MINOR` series, publication cadence, and the policy
   for withdrawing a bad new release without touching old MIT tags.
5. Validate per-product licensing/staging requirements against the actual
   release artifact, especially lmcad OCCT relinking assets, lmvideo's Skia
   notices, lmblender corresponding source, and static glibc products.
6. Decide issue routing/triage ownership, and who may create `RELEASE_TOKEN`
   secrets and approve first publication.
