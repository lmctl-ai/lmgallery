# Closed-source split dry-run: lmcad

- Source repo: `/home/mma/repos/dsl/lmcad`
- Source revision: `87cbb33ee71c962e4ae4ff4b13ab92251bdc5e65`
- Private peer target: `lmctlhq/lmcad` (transfer this repository, then set it private, only after owner approval)
- Public peer target: `lmctl-ai/lmcad` (recreate at the old slug after transfer; preserve README/example paths)

## Exact tracked-file plan

### Public peer (`lmctl-ai/lmcad`): 87 tracked files
- `docs/images/beam-sections.png`
- `docs/images/brick.png`
- `docs/images/buckyball.png`
- `docs/images/bullet.png`
- `docs/images/caffeine-molecule.png`
- `docs/images/coil-spring.png`
- `docs/images/cornell-box.png`
- `docs/images/cubemap.png`
- `docs/images/dipole-field.png`
- `docs/images/dna-double-helix.png`
- `docs/images/fluidsimulation2d.png`
- `docs/images/fluidsimulation3d.png`
- `docs/images/gear-train.gif`
- `docs/images/heat-sink.png`
- `docs/images/level-1-sessions.gif`
- `docs/images/level-1-sessions.png`
- `docs/images/level-2-orchestration.gif`
- `docs/images/level-2-orchestration.png`
- `docs/images/level-3-hands-off-lead.gif`
- `docs/images/level-3-hands-off-lead.png`
- `docs/images/level-4-automation.gif`
- `docs/images/level-4-automation.png`
- `docs/images/material-sandbox.png`
- `docs/images/model-viewer.png`
- `docs/images/mug.png`
- `docs/images/multidraw.png`
- `docs/images/pbr-spheres.png`
- `docs/images/plate-with-holes.png`
- `docs/images/pressure-vessel.png`
- `docs/images/primitives.png`
- `docs/images/saturn-rings.png`
- `docs/images/textured-triangle.png`
- `docs/images/truss-bridge.png`
- `docs/images/vase.png`
- `docs/videos/level-1-sessions.mp4`
- `docs/videos/level-2-orchestration.mp4`
- `docs/videos/level-3-hands-off-lead.mp4`
- `docs/videos/level-4-automation.mp4`
- `examples/ball-stick.lms`
- `examples/beam-sections.lms`
- `examples/box-stl.lms`
- `examples/box-volume.lms`
- `examples/brick.lms`
- `examples/buckyball.lms`
- `examples/bullet.lms`
- `examples/caffeine-molecule.lms`
- `examples/coil-spring.lms`
- `examples/cornell-box.lms`
- `examples/cubemap.lms`
- `examples/dipole-field.lms`
- `examples/dna-double-helix.lms`
- `examples/fluidsimulation2d.lms`
- `examples/fluidsimulation3d.lms`
- `examples/gear-train.lms`
- `examples/heat-sink.lms`
- `examples/level-1-sessions.lms`
- `examples/level-2-orchestration.lms`
- `examples/level-3-hands-off-lead.lms`
- `examples/level-4-automation.lms`
- `examples/loop-row.lms`
- `examples/material-sandbox.lms`
- `examples/model-viewer.lms`
- `examples/mug.lms`
- `examples/multidraw.lms`
- `examples/pbr-spheres.lms`
- `examples/plate-with-holes.lms`
- `examples/pressure-vessel.lms`
- `examples/primitives.lms`
- `examples/README.md`
- `examples/render-all.sh`
- `examples/saturn-rings.lms`
- `examples/section-view.lms`
- `examples/still-life.lms`
- `examples/textured-triangle.lms`
- `examples/truss-bridge.lms`
- `examples/turntable.lms`
- `examples/tween.lms`
- `examples/vase.lms`
- `licenses/Apache-2.0.txt` → `docs/third-party-licenses/Apache-2.0.txt`
- `licenses/build123d-NOTICE.txt` → `docs/third-party-licenses/build123d-NOTICE.txt`
- `licenses/GCC-RUNTIME-LIBRARY-EXCEPTION-3.1.txt` → `docs/third-party-licenses/GCC-RUNTIME-LIBRARY-EXCEPTION-3.1.txt`
- `licenses/GPL-3.txt` → `docs/third-party-licenses/GPL-3.txt`
- `licenses/LGPL-2.1.txt` → `docs/third-party-licenses/LGPL-2.1.txt`
- `licenses/LINUX-RELINKING.md` → `docs/third-party-licenses/LINUX-RELINKING.md`
- `licenses/PyVista-MIT.txt` → `docs/third-party-licenses/PyVista-MIT.txt`
- `README.md`
- `THIRD_PARTY_NOTICES.md`
- `LICENSE` (new binary-license draft from templates/LICENSE-binaries.md)
- `LICENSE-examples` (MIT text from templates/LICENSE-examples-MIT; source repo LICENSE stays private)

### Private peer (`lmctlhq/lmcad`): 109 tracked files
- ``
- `.gitattributes`
- `.github/occt-cmake-flags.txt`
- `.github/workflows/ci.yml`
- `.gitignore`
- `CMakeLists.txt`
- `cpp/atomic-file.cpp`
- `cpp/atomic-file.hpp`
- `cpp/cad.cpp`
- `cpp/cad.hpp`
- `cpp/deflate.hpp`
- `cpp/dslvm.hpp`
- `cpp/export.cpp`
- `cpp/image.cpp`
- `cpp/keyframes.hpp`
- `cpp/main.cpp`
- `cpp/render.cpp`
- `cpp/render.hpp`
- `cpp/scene.cpp`
- `cpp/scene.hpp`
- `cpp/std/lmcode-std.schema.json`
- `cpp/stdlib/collections.hpp`
- `cpp/stdlib/file.hpp`
- `cpp/stdlib/math.hpp`
- `cpp/stdlib/std.hpp`
- `cpp/stdlib/string.hpp`
- `cpp/stdlib/testing.hpp`
- `durable-memory/00-index.md`
- `durable-memory/01-purpose-and-place.md`
- `durable-memory/02-render-stack-options.md`
- `durable-memory/03-build-run-test.md`
- `durable-memory/03-schema-v0.md`
- `durable-memory/04-gotchas.md`
- `durable-memory/04-loops-and-collections-notes.md`
- `durable-memory/05-open-items.md`
- `durable-memory/06-reference-examples.md`
- `durable-memory/07-occt-static-spike.md`
- `durable-memory/08-occt-integration.md`
- `durable-memory/13-licensing.md`
- `durable-memory/14-ci-macos-windows.md`
- `durable-memory/15-example-gallery.md`
- `durable-memory/20-sibling-3d-hosts.md`
- `durable-memory/index.md`
- `LICENSE`
- `reference/.gitignore`
- `reference/out/b3d_01_holes/b3d_01_holes.png`
- `reference/out/b3d_01_holes/b3d_01_holes.stl`
- `reference/out/b3d_02_lego/b3d_02_lego.png`
- `reference/out/b3d_02_lego/b3d_02_lego.stl`
- `reference/out/b3d_03_vase/b3d_03_vase.png`
- `reference/out/b3d_03_vase/b3d_03_vase.stl`
- `reference/out/b3d_05_tea_cup/b3d_05_tea_cup.png`
- `reference/out/b3d_05_tea_cup/b3d_05_tea_cup.stl`
- `reference/out/b3d_05_tea_cup/tea_cup.bin`
- `reference/out/b3d_05_tea_cup/tea_cup.glb`
- `reference/out/b3d_06_joints/b3d_06_joints.png`
- `reference/out/b3d_06_joints/b3d_06_joints.stl`
- `reference/out/pv_01_geometric_objects/pv_01_geometric_objects_1.png`
- `reference/out/pv_02_boolean_operations/pv_02_boolean_operations_1.png`
- `reference/out/pv_02_boolean_operations/pv_02_boolean_operations_2.png`
- `reference/out/pv_02_boolean_operations/pv_02_boolean_operations_3.png`
- `reference/out/pv_02_boolean_operations/pv_02_boolean_operations_4.png`
- `reference/out/pv_02_boolean_operations/pv_02_boolean_operations_5.png`
- `reference/out/pv_02_boolean_operations/pv_02_boolean_operations_6.png`
- `reference/out/pv_02_boolean_operations/pv_02_boolean_operations_7.png`
- `reference/out/pv_06_marching_cubes/pv_06_marching_cubes_1.png`
- `reference/out/pv_06_marching_cubes/pv_06_marching_cubes_2.png`
- `reference/python/b3d_01_holes.py`
- `reference/python/b3d_02_lego.py`
- `reference/python/b3d_03_vase.py`
- `reference/python/b3d_05_tea_cup.py`
- `reference/python/b3d_06_joints.py`
- `reference/python/pv_01_geometric_objects.py`
- `reference/python/pv_02_boolean_operations.py`
- `reference/python/pv_03_clip_with_plane_box.py`
- `reference/python/pv_04_light_types.py`
- `reference/python/pv_05_glyph.py`
- `reference/python/pv_06_marching_cubes.py`
- `reference/runners/run_b3d.py`
- `reference/runners/run_pv.py`
- `schema/lmcad.dsl.json`
- `scripts/build-occt.sh`
- `scripts/lmscript-source.mjs`
- `scripts/lmscript-source.sh`
- `scripts/merge-std.py`
- `scripts/npm-layout.sh`
- `scripts/select-compiler.sh`
- `scripts/stage-release-notices.sh`
- `scripts/stamp-version.sh`
- `scripts/sync-sdk.sh`
- `sdk.lock`
- `spikes/occt/.gitignore`
- `spikes/occt/cross_build123d.py`
- `spikes/occt/spike.cpp`
- `test.sh`
- `tests/adapter.py`
- `tests/apng-extract.cjs`
- `tests/cad-exports.py`
- `tests/cad.py`
- `tests/compiler-selection.py`
- `tests/data/keyframes.csv`
- `tests/inflate.hpp`
- `tests/multi-file.py`
- `tests/refusals.py`
- `tests/render-settings.py`
- `tests/schema-cli.py`
- `tests/tween.py`
- `tests/unit.cpp`
- `tools/apng-extract.cpp`

## Required path and release changes

- README-relative image/docs/example paths stay byte-for-byte at their current paths in the public peer.
- Raw autorun links checked: 31/31 map to public `.lms` files.
- Existing CI workflow paths move to the private peer; replace them with the private CI template and add public `.github/workflows/public-ci.yml`.
  - Private CI path: `.github/workflows/ci.yml`
- Expected public release assets: `lmcad-linux-x64`, `lmcad-linux-arm64`, `lmcad-macos-x64`, `lmcad-macos-arm64`, `lmcad-windows-x64.exe`, plus `SHA256SUMS`.
- README links to private source paths checked: 1 finding(s).
  - SOURCE REFERENCE TO REVIEW: `README.md:66 -> ](https://github.com/lmctl-ai/lmctl/tree/main/scripts/homepage/video)`
- Public-plan secret scan: 0 finding(s); values are never printed.
- Licensing: Carry OCCT LGPL-2.1/Open CASCADE exception, OCCT relink objects/recipe/instructions, glibc/GCC runtime texts, build123d Apache NOTICE and PyVista MIT; do not omit OCCT relink assets.

## Verification result

- Autorun path check: PASS
- Public docs source-reference check: REVIEW REQUIRED
- Public-plan secret scan: PASS

This is a read-only plan. No files were copied or changed, no GitHub operation was performed, and no visibility was changed.

## Staging verification pass (2026-10-25, stage-only, no flip authorized)

### Freshness

- `origin/main` re-fetched: still `87cbb33ee71c962e4ae4ff4b13ab92251bdc5e65`; staged tree is fresh, no re-stage needed.
- Main CI run 40205702709 (head `87cbb33`) re-checked: **conclusion success** (was queued at staging time).

### Staged public tree verification (`/home/mma/staging/closed-source/lmcad-public/`)

- All 90 staged files present and byte-identical to the manifest SHA-256 inventory (0 missing, 0 mismatches).
- 38 raw `raw.githubusercontent.com/lmctl-ai/lmcad/main/...` URLs in staged README/docs all resolve to staged files at the same paths (includes the 31 autorun targets plus MP4/video links); 0 missing local images.
- Secret/`/home/` path scan of the staged tree: 0 findings.
- Public license/notices story per the lmcad licensing row:
  - `docs/third-party-licenses/` carries LGPL-2.1, GPL-3, GCC-RUNTIME-LIBRARY-EXCEPTION-3.1, Apache-2.0, build123d-NOTICE, PyVista-MIT, LINUX-RELINKING.md; each **byte-matches** `lmcad/licenses/`.
  - Staged `THIRD_PARTY_NOTICES.md` states the OCCT LGPL-2.1 + Open CASCADE exception obligation and explicitly names the relink assets shipped with releases (`lmcad-linux-<arch>-relink-objects.tar.gz`, `OCCT-RELINKING.md`, `lmcad-occt-relinking-recipe.tar.gz`), satisfying the "existence + instructions visible publicly" requirement.
  - **Where each obligation lives (recorded decision):** the OCCT exact texts (`OCCT-LICENSE_LGPL_21.txt`, `OCCT-LGPL-EXCEPTION.txt`), the per-arch relink-object archives, `OCCT-RELINKING.md`, GCC/glibc copyright metadata, and the recipe archive are **release-binary accompaniments** — produced by `scripts/stage-release-notices.sh` at package time and shipped as release assets; they are intentionally not in the public git tree. Their existence and purpose are documented in the public notices/license docs above.
  - Known cosmetic effect of the flip scrubber (same as the lmaudio pilot): private repo-relative paths inside the public copies of `THIRD_PARTY_NOTICES.md` and `LINUX-RELINKING.md` are replaced with `private implementation detail`. The authoritative unredacted OCCT-RELINKING instructions ship with each release as the `OCCT-RELINKING.md` asset.

### Example checking against the released binary

- Downloaded `lmcad-linux-x64` v0.1.72 to a scratch PATH dir; `lmcad --version` → `lmcad 0.1.72`.
- `lmscript --check` against every staged `examples/*.lms`: **39/39 PASS** (cli="lmcad" blocks bind the released binary).
- Runtime dependencies to note for private CI: `beam-sections.lms`, `heat-sink.lms`, `truss-bridge.lms` also bind cli="lmplot" (`install="github:lmctl-ai/lmplot@latest"`), so CI needs the lmplot install token path as the current workflow does. `tween.lms` writes then reads `build/keyframes.csv` itself — no pre-existing example inputs are required beyond the public tree.

### Current published release audit (`/home/mma/staging/closed-source/lmcad-release/`, tag v0.1.72, published 2026-10-25)

- All 23 release assets downloaded; `sha256sum -c SHA256SUMS` PASS for the 5 platform binaries; every asset's local SHA-256 matches the GitHub API digest. Full name/size/hash inventory recorded in `release-metadata.json`.
- **OCCT relink-assets verdict: PRESENT — no blocker.** The current release already ships `lmcad-linux-x64-relink-objects.tar.gz` (313,894 B; 7 application objects + LICENSE + NOTICES + OCCT-RELINKING.md), `lmcad-linux-arm64-relink-objects.tar.gz` (313,948 B), `lmcad-occt-relinking-recipe.tar.gz` (722,507 B; both object archives + build-occt.sh + occt-cmake-flags.txt + CMakeLists + cpp sources + all license/copyright texts), `OCCT-RELINKING.md`, `OCCT-LICENSE_LGPL_21.txt`, and `OCCT-LGPL-EXCEPTION.txt`. The private-ci packaging in this plan preserves all of them.
- Note: `SHA256SUMS` covers only the 5 platform binaries (matches current workflow); consider extending it to the relink assets in the new publish job (not a blocker).

### Private CI draft

- `/home/mma/staging/closed-source/lmcad-private-ci.yml` — adapted from the current `.github/workflows/ci.yml` at SHA 87cbb33 into the peer-model shape: `linux-fast` job on push/PR (real OCCT cache/build, ninja, select-compiler, sync-sdk, `./test.sh`, static-executable assert, public-peer checkout, `lmscript --check` + run of all public examples); `full-matrix` job on workflow_dispatch/v* tag for all 5 platforms with the per-platform toolchain/audit quirks (ldd, otool, objdump) and `stage-release-notices.sh` staging; `publish` job gated on tag/dispatch, requires `secrets.RELEASE_TOKEN`, verifies the binary `--version` matches the tag, builds the OCCT relinking recipe archive, generates SHA256SUMS, and **fails closed** when the release already exists (replaces the old idempotent --clobber behavior). YAML validated.

### Pin inventory

- `inventory-pins.py` + repo grep: exactly one consumer pin —
  `/home/mma/repos/dsl/simulation/ROADMAP.md:63` (table row pinned to `v0.1.4`).
- Parameterized update line for the coordinated flip (run once the owner picks the first new tag):
  `FIRST_TAG=vX.Y.Z; sed -i "63s|v0.1.4|${FIRST_TAG}|g" /home/mma/repos/dsl/simulation/ROADMAP.md`
- The lmcad repo's own README/workflows reference its release asset names; those move to lmctlhq untouched.

### Verdict

Ready to flip from a staging/validation standpoint, pending the standing gates: owner approval entry in `~/tools/closed-source-approved.txt`, `RELEASE_TOKEN`, the chosen first release tag, and consumer-pin update above. The OCCT relink materials obligation is fully satisfied by the current release and preserved in the drafted private CI.
