# Closed-source split dry-run: lmfilament

- Source repo: `/home/mma/repos/dsl/lmfilament`
- Source revision: `8bd8b35cedd07ab376e6bc0054749b2386864187`
- Private peer target: `lmctlhq/lmfilament` (transfer this repository, then set it private, only after owner approval)
- Public peer target: `lmctl-ai/lmfilament` (recreate at the old slug after transfer; preserve README/example paths)

## Exact tracked-file plan

### Public peer (`lmctl-ai/lmfilament`): 86 tracked files
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
- `docs/images/heightfield.png`
- `docs/images/hellopbr.png`
- `docs/images/hellotriangle.png`
- `docs/images/level-1-sessions.gif`
- `docs/images/level-1-sessions.png`
- `docs/images/level-2-orchestration.gif`
- `docs/images/level-2-orchestration.png`
- `docs/images/level-3-hands-off-lead.gif`
- `docs/images/level-3-hands-off-lead.png`
- `docs/images/level-4-automation.gif`
- `docs/images/level-4-automation.png`
- `docs/images/lightbulb.png`
- `docs/images/material_sandbox.png`
- `docs/images/model-viewer.png`
- `docs/images/multidraw.png`
- `docs/images/primitives-scene-graph.png`
- `docs/images/primitives.png`
- `docs/images/saturn-rings.png`
- `docs/images/shadows.png`
- `docs/images/shadowtest.png`
- `docs/images/suzanne.png`
- `docs/images/text.png`
- `docs/images/texture-modes.png`
- `docs/images/textured-planet.gif`
- `docs/images/textured-primitives.png`
- `docs/images/texturedquad.png`
- `docs/images/truss-bridge.png`
- `docs/images/vbotest.png`
- `docs/images/viewtest.png`
- `docs/videos/level-1-sessions.mp4`
- `docs/videos/level-2-orchestration.mp4`
- `docs/videos/level-3-hands-off-lead.mp4`
- `docs/videos/level-4-automation.mp4`
- `examples/ball-stick.lms`
- `examples/buckyball.lms`
- `examples/bullet.lms`
- `examples/caffeine-molecule.lms`
- `examples/compile-sample-materials.lms`
- `examples/cornell-box.lms`
- `examples/cubemap.lms`
- `examples/depthtesting.lms`
- `examples/dna-double-helix.lms`
- `examples/fluidsimulation2d.lms`
- `examples/fluidsimulation3d.lms`
- `examples/heightfield.lms`
- `examples/hellopbr.lms`
- `examples/hellotriangle.lms`
- `examples/level-1-sessions.lms`
- `examples/level-2-orchestration.lms`
- `examples/level-3-hands-off-lead.lms`
- `examples/level-4-automation.lms`
- `examples/lightbulb.lms`
- `examples/material_sandbox.lms`
- `examples/model-viewer.lms`
- `examples/multidraw.lms`
- `examples/point_sprites.lms`
- `examples/primitives-scene-graph.lms`
- `examples/primitives.lms`
- `examples/README.md`
- `examples/render-all.sh`
- `examples/saturn-rings.lms`
- `examples/shadows.lms`
- `examples/shadowtest.lms`
- `examples/strobecolor.lms`
- `examples/suzanne.lms`
- `examples/text.lms`
- `examples/texture-modes.lms`
- `examples/textured-planet.lms`
- `examples/textured-primitives.lms`
- `examples/texturedquad.lms`
- `examples/truss-bridge.lms`
- `examples/vbotest.lms`
- `examples/viewtest.lms`
- `LICENSE`
- `README.md`
- `THIRD_PARTY_NOTICES.md`
- `LICENSE-binaries` (new owner-approved binary license text; not present in this source checkout unless listed above)

### Private peer (`lmctlhq/lmfilament`): 33 tracked files
- ``
- `.github/workflows/ci.yml`
- `.gitignore`
- `CMakeLists.txt`
- `cpp/deflate.hpp`
- `cpp/dslvm.hpp`
- `cpp/main.cpp`
- `cpp/mesh.cpp`
- `cpp/mesh.hpp`
- `cpp/preview.cpp`
- `cpp/preview.hpp`
- `cpp/stb_image.h`
- `cpp/texture.cpp`
- `cpp/texture.hpp`
- `durable-memory/00-index.md`
- `durable-memory/01-purpose-and-place.md`
- `durable-memory/02-build-run-test.md`
- `durable-memory/03-architecture-and-schema.md`
- `durable-memory/04-gotchas.md`
- `durable-memory/05-open-items.md`
- `durable-memory/06-upstream-sample-map.md`
- `durable-memory/07-ci-and-release.md`
- `durable-memory/20-sibling-3d-hosts.md`
- `durable-memory/index.md`
- `filament.lock`
- `schema/lmfilament.dsl.json`
- `scripts/build-filament.sh`
- `scripts/build.sh`
- `scripts/stamp-version.sh`
- `scripts/sync-filament.sh`
- `scripts/sync-sdk.sh`
- `sdk.lock`
- `test.sh`

## Required path and release changes

- README-relative image/docs/example paths stay byte-for-byte at their current paths in the public peer.
- Raw autorun links checked: 35/35 map to public `.lms` files.
- Existing CI workflow paths move to the private peer; replace them with the private CI template and add public `.github/workflows/public-ci.yml`.
  - Private CI path: `.github/workflows/ci.yml`
- Expected public release assets: `lmfilament-linux-x64`, `lmfilament-linux-arm64`, `lmfilament-macos-x64`, `lmfilament-macos-arm64`, `lmfilament-windows-x64.exe`, plus `SHA256SUMS`.
- README links to private source paths checked: 2 finding(s).
  - SOURCE REFERENCE TO REVIEW: `README.md:6 -> ](schema/lmfilament.dsl.json)`
  - SOURCE REFERENCE TO REVIEW: `README.md:93 -> ](https://github.com/lmctl-ai/lmctl/tree/main/scripts/homepage/video)`
- Public-plan secret scan: 0 finding(s); values are never printed.
- Licensing: Ship LICENSE, THIRD_PARTY_NOTICES.md, FILAMENT-LICENSE, all pinned Filament third-party notices, LLVM exception/runtime texts and Linux glibc LGPL materials.

## Verification result

- Autorun path check: PASS
- Public docs source-reference check: REVIEW REQUIRED
- Public-plan secret scan: PASS

This is a read-only plan. No files were copied or changed, no GitHub operation was performed, and no visibility was changed.
