# Closed-source split dry-run: lmmagnum

- Source repo: `/home/mma/repos/dsl/lmmagnum`
- Source revision: `41a7d8504826d599aa9660b26329efb77ded6bee`
- Private peer target: `lmctlhq/lmmagnum` (transfer this repository, then set it private, only after owner approval)
- Public peer target: `lmctl-ai/lmmagnum` (recreate at the old slug after transfer; preserve README/example paths)

## Exact tracked-file plan

### Public peer (`lmctl-ai/lmmagnum`): 87 tracked files
- `docs/images/animated-gif.gif`
- `docs/images/area-lights.png`
- `docs/images/ball-stick.png`
- `docs/images/buckyball.png`
- `docs/images/bullet.png`
- `docs/images/caffeine-molecule.png`
- `docs/images/cornell-box.png`
- `docs/images/cubemap.png`
- `docs/images/depthtesting.png`
- `docs/images/dna-double-helix.png`
- `docs/images/fluidsimulation2d.png`
- `docs/images/fluidsimulation3d.png`
- `docs/images/level-1-sessions.gif`
- `docs/images/level-1-sessions.png`
- `docs/images/level-2-orchestration.gif`
- `docs/images/level-2-orchestration.png`
- `docs/images/level-3-hands-off-lead.gif`
- `docs/images/level-3-hands-off-lead.png`
- `docs/images/level-4-automation.gif`
- `docs/images/level-4-automation.png`
- `docs/images/lightbulb.png`
- `docs/images/material-sandbox.png`
- `docs/images/model-viewer.png`
- `docs/images/motionblur.png`
- `docs/images/multidraw.png`
- `docs/images/octree.png`
- `docs/images/pbr-spheres.png`
- `docs/images/primitives-scene-graph.png`
- `docs/images/primitives.png`
- `docs/images/raytracing.png`
- `docs/images/saturn-rings.png`
- `docs/images/shadows.png`
- `docs/images/text.png`
- `docs/images/texture-modes.png`
- `docs/images/textured-planet.gif`
- `docs/images/textured-planet.png`
- `docs/images/textured-primitives.png`
- `docs/images/textured-quad-texture.png`
- `docs/images/textured-quad.png`
- `docs/images/textured-triangle.png`
- `docs/images/triangle.png`
- `docs/images/truss-bridge.png`
- `docs/videos/level-1-sessions.mp4`
- `docs/videos/level-2-orchestration.mp4`
- `docs/videos/level-3-hands-off-lead.mp4`
- `docs/videos/level-4-automation.mp4`
- `examples/animated-gif.lms`
- `examples/arcball.lms`
- `examples/area-lights.lms`
- `examples/ball-stick.lms`
- `examples/buckyball.lms`
- `examples/bullet.lms`
- `examples/caffeine-molecule.lms`
- `examples/cornell-box.lms`
- `examples/cubemap.lms`
- `examples/depthtesting.lms`
- `examples/dna-double-helix.lms`
- `examples/fluidsimulation2d.lms`
- `examples/fluidsimulation3d.lms`
- `examples/level-1-sessions.lms`
- `examples/level-2-orchestration.lms`
- `examples/level-3-hands-off-lead.lms`
- `examples/level-4-automation.lms`
- `examples/lightbulb.lms`
- `examples/material-sandbox.lms`
- `examples/model-viewer.lms`
- `examples/motionblur.lms`
- `examples/multidraw.lms`
- `examples/octree.lms`
- `examples/pbr-spheres.lms`
- `examples/primitives-scene-graph.lms`
- `examples/primitives.lms`
- `examples/raytracing.lms`
- `examples/README.md`
- `examples/render-all.sh`
- `examples/saturn-rings.lms`
- `examples/shadows.lms`
- `examples/text.lms`
- `examples/texture-modes.lms`
- `examples/textured-planet.lms`
- `examples/textured-primitives.lms`
- `examples/textured-quad.lms`
- `examples/textured-triangle.lms`
- `examples/triangle.lms`
- `examples/truss-bridge.lms`
- `README.md`
- `THIRD_PARTY_NOTICES.md`
- `LICENSE` (new binary-license draft from templates/LICENSE-binaries.md)
- `LICENSE-examples` (MIT text from templates/LICENSE-examples-MIT; source repo LICENSE stays private)

### Private peer (`lmctlhq/lmmagnum`): 43 tracked files
- ``
- `.gitattributes`
- `.github/workflows/ci.yml`
- `.gitignore`
- `CMakeLists.txt`
- `cpp/atomic-file.cpp`
- `cpp/atomic-file.hpp`
- `cpp/deflate.hpp`
- `cpp/dslvm.hpp`
- `cpp/main.cpp`
- `cpp/render.cpp`
- `cpp/scene.cpp`
- `cpp/scene.hpp`
- `cpp/stb_image.h`
- `cpp/std/lmcode-std.schema.json`
- `cpp/stdlib/collections.hpp`
- `cpp/stdlib/file.hpp`
- `cpp/stdlib/math.hpp`
- `cpp/stdlib/std.hpp`
- `cpp/stdlib/string.hpp`
- `cpp/stdlib/testing.hpp`
- `cpp/texture.cpp`
- `deps.lock`
- `durable-memory/00-index.md`
- `durable-memory/01-build-static.md`
- `durable-memory/02-architecture.md`
- `durable-memory/03-dsl-reference.md`
- `durable-memory/04-examples.md`
- `durable-memory/05-extending.md`
- `durable-memory/06-release.md`
- `durable-memory/20-sibling-3d-hosts.md`
- `durable-memory/index.md`
- `LICENSE`
- `schema/lmmagnum.dsl.json`
- `scripts/merge-std.py`
- `scripts/select-compiler.sh`
- `scripts/stage-release-notices.sh`
- `scripts/stamp-version.sh`
- `scripts/sync-deps.sh`
- `scripts/sync-sdk.sh`
- `scripts/update-readme-images.sh`
- `sdk.lock`
- `test.sh`

## Required path and release changes

- README-relative image/docs/example paths stay byte-for-byte at their current paths in the public peer.
- Raw autorun links checked: 37/37 map to public `.lms` files.
- Existing CI workflow paths move to the private peer; replace them with the private CI template and add public `.github/workflows/public-ci.yml`.
  - Private CI path: `.github/workflows/ci.yml`
- Expected public release assets: `lmmagnum-linux-x64`, `lmmagnum-linux-arm64`, `lmmagnum-macos-x64`, `lmmagnum-macos-arm64`, `lmmagnum-windows-x64.exe`, plus `SHA256SUMS`.
- README links to private source paths checked: 1 finding(s).
  - SOURCE REFERENCE TO REVIEW: `README.md:77 -> ](https://github.com/lmctl-ai/lmctl/tree/main/scripts/homepage/video)`
- Public-plan secret scan: 0 finding(s); values are never printed.
- Licensing: Carry Magnum/Corrade MIT COPYING files, stb/lmcode-cpp notices, runtime terms, and re-check static-glibc obligations.

## Verification result

- Autorun path check: PASS
- Public docs source-reference check: REVIEW REQUIRED
- Public-plan secret scan: PASS

This is a read-only plan. No files were copied or changed, no GitHub operation was performed, and no visibility was changed.


## Staging results (2026-10-25, STAGING only; nothing flipped)

- Staged from `origin/main` `41a7d8504826` (clean, pushed) into `/home/mma/staging/closed-source/lmmagnum-public/`: 90 files, public CI `.github/workflows/public-ci.yml` included.
- Release assets: latest `v0.2.14` (published 2026-10-25) downloaded to `lmmagnum-release/` with `SHA256SUMS`.
  - All 5 platform binaries (`lmmagnum-linux-arm64`, `lmmagnum-linux-x64`, `lmmagnum-macos-arm64`, `lmmagnum-macos-x64`, `lmmagnum-windows-x64.exe`) verify against `SHA256SUMS` (`sha256sum -c`).
  - Upstream notice files (`Magnum-COPYING`, `Corrade-COPYING`, `LICENSE`, `THIRD_PARTY_NOTICES`) verified.
- Staged release metadata and notes: `release-metadata.json` and `release-notes.md` generated with the MIT boundary up to and including `v0.2.14`.
- Verified: 37/37 README `lmctl autorun` targets exist in the staged tree; 41 local image/link refs resolve (37 README images present in `docs/images/`); no `/home/mma` path, no secret-like text, no private source links.
- Licensing notices: complete for binary (Magnum MIT `COPYING`, Corrade MIT `COPYING`, stb public-domain/MIT, lmcode-cpp MIT, static glibc LGPL-2.1+).
- Staged `LICENSE` and `README.md` carry the boundary sentence: "Releases up to and including v0.2.14 were published under the MIT License (see the LICENSE asset of that release). Releases after v0.2.14 are published under the Lattice Systems Personal Use License (this file)."

### Host execution and example check results

- Verified with published release binary `lmmagnum 0.2.14` on PATH:
  - **All 37/37 examples pass `lmscript --check`!**

### Technical assessment

No code or packaging blockers found. The repository is clean, origin/main CI is passing across all 5 platforms, and the latest published binary `v0.2.14` runs all 37 public examples without issues.

### Private CI

Staged at `/home/mma/staging/closed-source/lmmagnum-private-ci.yml`, adapted from the current `.github/workflows/ci.yml`:
- Fast Linux job on `push: branches: [main]` and `pull_request`: builds with Ninja, runs `./test.sh`, and tests public examples against the fresh Linux host.
- Full 5-platform matrix (`linux-x64`, `linux-arm64`, `macos-arm64`, `macos-x64`, `windows-x64`) on `workflow_dispatch` or `v*` tag.
- `publish-test` job verifies public write access with `secrets.RELEASE_TOKEN` without building.
- Gated publish job collects platform binaries and notice assets, calculates `SHA256SUMS`, and publishes to `lmctl-ai/lmmagnum` with `secrets.RELEASE_TOKEN`.

### Pin inventory (1 consumer)

- `/home/mma/repos/dsl/lmgallery/examples/38-product-render-slide.lms:10` — `render = _lmcode_ cli="lmmagnum" install="github:lmctl-ai/lmmagnum@v0.2.14";`

After the first new tag `<FIRST_TAG>` is published:

```bash
sed -i -E 's|(github:lmctl-ai/lmmagnum@)v[0-9]+\.[0-9]+\.[0-9]+|\1<FIRST_TAG>|g; s|(github\.com/lmctl-ai/lmmagnum/releases/(tag|download)/)v[0-9]+\.[0-9]+\.[0-9]+|\1<FIRST_TAG>|g' /home/mma/repos/dsl/lmgallery/examples/38-product-render-slide.lms
```

### Quiesce and decisions before flip

- No active `lmctl` team detected for `lmmagnum`; working tree is clean and synced with `origin/main`.
- Owner decisions:
  1. Approve `lmmagnum` in `~/tools/closed-source-approved.txt`.
  2. Provide `RELEASE_TOKEN` for the private CI workflow.
  3. Determine first new release tag or approve replay of `v0.2.14`.

### Ready to flip: YES (technically ready; pending owner approval & token)

Reasons: All 37 public examples pass `lmscript --check` against the fresh 5-platform `v0.2.14` release; clean and synchronized source tree; full notice closure; only 1 consumer pin; no active team; awaiting only owner sign-off and `RELEASE_TOKEN`.
