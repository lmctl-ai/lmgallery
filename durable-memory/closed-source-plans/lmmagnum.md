# Closed-source split dry-run: lmmagnum

- Source repo: `/home/mma/repos/dsl/lmmagnum`
- Source revision: `a821053d15c394021b67f979159fc0d1263d9f83`
- Private peer target: `lmctlhq/lmmagnum` (create/copy only after owner approval)
- Public peer target: `lmctl-ai/lmmagnum` (preserve the existing public URL)

## Exact tracked-file plan

### Public peer (`lmctl-ai/lmmagnum`): 88 tracked files
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
- `LICENSE`
- `README.md`
- `THIRD_PARTY_NOTICES.md`
- `LICENSE-binaries` (new owner-approved binary license text; not present in this source checkout unless listed above)

### Private peer (`lmctlhq/lmmagnum`): 34 tracked files
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
- `schema/lmmagnum.dsl.json`
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
- Licensing: Ship LICENSE, THIRD_PARTY_NOTICES.md, Magnum and Corrade MIT COPYING files, stb notice, lmcode-cpp notice, and platform runtime license texts; Linux static glibc remains LGPL-2.1+.

## Verification result

- Autorun path check: PASS
- Public docs source-reference check: REVIEW REQUIRED
- Public-plan secret scan: PASS

This is a read-only plan. No files were copied or changed, no GitHub operation was performed, and no visibility was changed.
