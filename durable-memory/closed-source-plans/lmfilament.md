# Closed-source split dry-run: lmfilament

- Source repo: `/home/mma/repos/dsl/lmfilament`
- Source revision: `24a0c3e851336c05e9b149c56e113355982c4c89`
- Private peer target: `lmctlhq/lmfilament` (transfer this repository, then set it private, only after owner approval)
- Public peer target: `lmctl-ai/lmfilament` (recreate at the old slug after transfer; preserve README/example paths)

## Exact tracked-file plan

### Public peer (`lmctl-ai/lmfilament`): 85 tracked files
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
- `README.md`
- `THIRD_PARTY_NOTICES.md`
- `LICENSE` (new binary-license draft from templates/LICENSE-binaries.md)
- `LICENSE-examples` (MIT text from templates/LICENSE-examples-MIT; source repo LICENSE stays private)

### Private peer (`lmctlhq/lmfilament`): 44 tracked files
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
- `cpp/std/lmcode-std.schema.json`
- `cpp/stdlib/collections.hpp`
- `cpp/stdlib/file.hpp`
- `cpp/stdlib/math.hpp`
- `cpp/stdlib/std.hpp`
- `cpp/stdlib/string.hpp`
- `cpp/stdlib/testing.hpp`
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
- `LICENSE`
- `schema/lmfilament.dsl.json`
- `scripts/build-filament.sh`
- `scripts/build.sh`
- `scripts/merge-std.py`
- `scripts/select-compiler.sh`
- `scripts/stamp-version.sh`
- `scripts/sync-filament.sh`
- `scripts/sync-sdk.sh`
- `scripts/test-std.sh`
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
- Licensing: Carry FILAMENT-LICENSE, pinned Filament component notices, LLVM exceptions and Linux runtime terms.

## Verification result

- Autorun path check: PASS
- Public docs source-reference check: REVIEW REQUIRED
- Public-plan secret scan: PASS

This is a read-only plan. No files were copied or changed, no GitHub operation was performed, and no visibility was changed.

## Staging verification (2026-10-25 refresh)

- **Freshness: NOT STALE.** Staged SHA `24a0c3e851336c05e9b149c56e113355982c4c89`
  equals current `origin/main`; lmfilament team sessions were active but pushed
  nothing past the staged SHA between staging and this check. CI on that SHA is
  green (run 40204741784, conclusion success).
- **Staged tree**: `/home/mma/staging/closed-source/lmfilament-public/` (manifest
  `lmfilament-stage-manifest.json`, 88 files + 12 added license texts = 100 files).
  Independent re-verification: 38 unique raw autorun URLs all map to staged files
  at the same path (no rewrites); all 39 local README/`examples/README.md` image
  and doc references exist; no `/home/` paths, no secrets; the single `lmctlhq`
  hit is the intentional README line (same wording as the lmaudio pilot).
- **Staging fixes applied this pass** (staging only, product repo untouched):
  - `LICENSE` now carries the MIT boundary sentence: "Releases up to and including
    v0.3.19 were published under the MIT License (see the LICENSE asset of that
    release). Releases after v0.3.19 are published under the Lattice Systems
    Personal Use License (this file)." — lmfilament's actual latest tag is v0.3.19
    (not lmaudio's v0.2.1).
  - New `docs/third-party-licenses/` with the exact texts for the release binary's
    closure: `Filament-Apache-2.0.txt` (byte-identical to the v0.3.19
    FILAMENT-LICENSE asset), `glslang-BSD-3-Clause.txt`, `SPIRV-Tools-Apache-2.0.txt`,
    `SPIRV-Cross-Apache-2.0-MIT.txt`, `zstd-BSD-3-Clause.txt`, `smol-v-MIT.txt`,
    `meshoptimizer-MIT.txt`, `mikktspace-zlib.txt` (from Filament's vendored libz
    text; Filament ships mikktspace without its own license file), `robin-map-MIT.txt`,
    `LLVM-ReleaseLicense.txt`, `glibc-LGPL-2.1.txt`, `GCC-RUNTIME-LIBRARY-EXCEPTION-3.1.txt`.
    `THIRD_PARTY_NOTICES.md` now points at these files and keeps the Filament /
    third-party / glibc / relink-object texts verbatim.
- **`lmscript --check` against the RELEASED host**: downloaded
  `lmfilament-linux-x64` v0.3.19 to scratch, put it on PATH as `lmfilament`
  (reports `lmfilament 0.3.19 (filament 1.78.1)`); all 38 staged
  `examples/*.lms` pass. Examples whose *execution* (not check) needs extra
  inputs: `suzanne`, `hellopbr`, `texturedquad` read `third_party/filament/assets/...`
  relative to cwd; `level-*-sessions` shell out to ffmpeg for MP4/GIF. Private CI
  links the synced Filament checkout beside the public examples before running them.
- **Release asset inventory**: `/home/mma/staging/closed-source/lmfilament-release/`
  holds all 13 v0.3.19 assets, every one verified against the GitHub asset
  digests; the release ships per-asset `.sha256` sidecars but no aggregate
  SHA256SUMS, so one was computed and recorded in `SHA256SUMS`:

  | Asset | Size (bytes) | SHA-256 |
  | --- | ---: | --- |
  | lmfilament-linux-x64 | 16443936 | 047952741e1e8a63386154db757353139758fd5f4ae5ee148323c3e691132ef5 |
  | lmfilament-linux-arm64 | 15439704 | e11f6d26d70fb633136698765084410cb8cedb5afb21edb4aed4314bf9c604ff |
  | lmfilament-macos-x64 | 13544976 | df66d5b6508108a3a080b7b3f0b87b6986edf180778af76e03528f63a8d0c370 |
  | lmfilament-macos-arm64 | 12588968 | c956489053ab7f390f7e9a11a1733f7bdf7ee961d983c607b1f940eb61e19237 |
  | lmfilament-linux-x64-relink-objects.tar.gz | 426472 | 29bee4a3e246fd83a21239b5f44024d0f36aa93eee4d34ed4f538ee493c3127a |
  | lmfilament-linux-arm64-relink-objects.tar.gz | 429803 | c096898225c77293205dd2cd9b18e6b5ae6ad9150a2aa44b7c5a40ed5aefb7dd |
  | FILAMENT-LICENSE | 11362 | 02d70b593dd8e9355dd8e1ca8d13c303bee5bcaf3065b66ff6e4f534e1e6a2c1 |
  | LICENSE (MIT, pre-flip) | 1076 | 949eb9b711d9b64ae472b87b94916e8427575a75d0d218f6c4cbccf8c48d46f3 |
  | THIRD_PARTY_NOTICES.md | 2523 | baeaca058e375cca32af27c3ebd9e4254e01618cfc54620cf688c024b148c637 |

- **Private CI**: `/home/mma/staging/closed-source/lmfilament-private-ci.yml`,
  adapted from lmfilament's current `.github/workflows/ci.yml` into the model's
  shape (lmaudio staged yml + `templates/private-ci.yml` as skeleton): Linux-only
  fast job on push/PR (clang-18 + static libc++, filament.lock cache, sync-filament
  + sync-sdk verify, build-filament + build + test.sh, then public examples checked
  and run against the fresh host); 4-platform full matrix on tag/dispatch with
  per-platform packaging (binaries, `.sha256`, Linux relink-object tarballs,
  LICENSE/THIRD_PARTY_NOTICES/FILAMENT-LICENSE); publish-test draft job; publish
  job using only `secrets.RELEASE_TOKEN`, staging exactly the 4 platform binaries +
  2 relink archives + LICENSE + THIRD_PARTY_NOTICES.md + FILAMENT-LICENSE +
  SHA256SUMS, failing closed if the tag/release already exists. **Deviation from
  the model: 4 platforms, no windows-x64** — lmfilament's toolchain has no Windows
  build (public README states Windows is not supported yet); the old v0.3.19
  release likewise ships no Windows asset. Add the fifth matrix leg when Windows
  toolchain support lands.
- **Consumer pin inventory: 0 pins.** `inventory-pins.py` reports 0 lmfilament
  matches across `/home/mma/repos/dsl` and `/home/mma/repos/lmctlhq`; an
  independent sweep for `lmfilament@`, release download/tag URLs, and
  `cli="lmfilament"` found only one `@latest` reference
  (`lmcode-cpp/durable-memory/09-compiler-readiness-results.json:4006`), which
  keeps working after the flip. No sed updates required; when the first new tag
  is chosen, any future pin would move with
  `sed -i 's|github:lmctl-ai/lmfilament@<old>|github:lmctl-ai/lmfilament@vX.Y.Z|g' <file>`.
- **Blockers / open items before apply**:
  1. lmfilament team was live during staging; re-run the freshness check at
     apply preflight (quiesce + `origin/main` unchanged since `24a0c3e`).
  2. Windows platform absent (see private CI deviation); owner decision whether
     the first new release is 4-platform or waits for a Windows toolchain.
  3. `RELEASE_TOKEN` not yet configured; the model's publish gate requires it
     before the coordinated flip.
  4. First new release tag TBD at flip time; boundary sentence in the staged
     LICENSE is pinned to v0.3.19 (the last MIT release).

