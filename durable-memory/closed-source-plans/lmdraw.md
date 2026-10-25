# Closed-source split dry-run: lmdraw

- Source repo: `/home/mma/repos/dsl/lmdraw`
- Source revision: `9452958efb8aceebb835daf7660a00d2f731dd9d`
- Private peer target: `lmctlhq/lmdraw` (transfer this repository, then set it private, only after owner approval)
- Public peer target: `lmctl-ai/lmdraw` (recreate at the old slug after transfer; preserve README/example paths)

## Exact tracked-file plan

### Public peer (`lmctl-ai/lmdraw`): 84 tracked files
- `assets/fonts/OFL.txt` → `docs/third-party-licenses/assets/fonts/OFL.txt`
- `docs/images/architecture-layers.png`
- `docs/images/carnot-cycle.png`
- `docs/images/damped-oscillator.png`
- `docs/images/decision-flowchart.png`
- `docs/images/decision-tree.png`
- `docs/images/entity-relationship.png`
- `docs/images/etl-pipeline.png`
- `docs/images/flowchart-order-approval.png`
- `docs/images/hohmann-transfer.png`
- `docs/images/hydrogen-spectrum.png`
- `docs/images/incline-free-body.png`
- `docs/images/kepler-second-law.gif`
- `docs/images/kepler-second-law.png`
- `docs/images/kleiber-allometry.png`
- `docs/images/lens-ray-diagram.png`
- `docs/images/lotka-volterra.png`
- `docs/images/mortgage-amortization.png`
- `docs/images/npv-irr-cashflow.png`
- `docs/images/org-chart-grid.png`
- `docs/images/punnett-square.png`
- `docs/images/rc-lowpass.png`
- `docs/images/relativity-lorentz.png`
- `docs/images/render-assets.png`
- `docs/images/sequence-oauth-refresh.png`
- `docs/images/state-machines.png`
- `docs/images/swimlane-process.png`
- `docs/images/timeline-gantt.png`
- `docs/images/truss-bridge.png`
- `docs/LLM_GUIDE.md`
- `docs/readme/architecture-light.lms`
- `docs/readme/architecture-light.png`
- `docs/readme/architecture.lms`
- `docs/readme/architecture.png`
- `docs/readme/render.sh`
- `examples/animated-ladder.lms`
- `examples/architecture-layers.lms`
- `examples/arrow-helper.lms`
- `examples/carnot-cycle.lms`
- `examples/chart-bars-lines.lms`
- `examples/damped-oscillator.lms`
- `examples/decision-flowchart.lms`
- `examples/decision-tree.lms`
- `examples/entity-relationship.lms`
- `examples/etl-pipeline.lms`
- `examples/flow-pipeline.lms`
- `examples/flowchart-order-approval.lms`
- `examples/geometry-ellipse.lms`
- `examples/heatmap-grid.lms`
- `examples/hohmann-transfer.lms`
- `examples/hydrogen-spectrum.lms`
- `examples/incline-free-body.lms`
- `examples/kepler-second-law.lms`
- `examples/kleiber-allometry.lms`
- `examples/lens-ray-diagram.lms`
- `examples/lotka-volterra.lms`
- `examples/mortgage-amortization.lms`
- `examples/node-tour.lms`
- `examples/npv-irr-cashflow.lms`
- `examples/org-chart-grid.lms`
- `examples/punnett-square.lms`
- `examples/rc-lowpass.lms`
- `examples/README.md`
- `examples/relativity-lorentz.lms`
- `examples/render-all.sh`
- `examples/render-assets.lms`
- `examples/sequence-oauth-refresh.lms`
- `examples/state-machines.lms`
- `examples/swimlane-process.lms`
- `examples/table-metrics.lms`
- `examples/timeline-gantt.lms`
- `examples/title-card.lms`
- `examples/tree-org.lms`
- `examples/truss-bridge.lms`
- `examples/tween-morph.lms`
- `licenses/FreeType-FTL.txt` → `docs/third-party-licenses/FreeType-FTL.txt`
- `licenses/GCC-RUNTIME-LIBRARY-EXCEPTION-3.1.txt` → `docs/third-party-licenses/GCC-RUNTIME-LIBRARY-EXCEPTION-3.1.txt`
- `licenses/GPL-3.txt` → `docs/third-party-licenses/GPL-3.txt`
- `licenses/LGPL-2.1.txt` → `docs/third-party-licenses/LGPL-2.1.txt`
- `licenses/LunaSVG-MIT.txt` → `docs/third-party-licenses/LunaSVG-MIT.txt`
- `licenses/Noto-OFL-1.1.txt` → `docs/third-party-licenses/Noto-OFL-1.1.txt`
- `licenses/PlutoVG-MIT.txt` → `docs/third-party-licenses/PlutoVG-MIT.txt`
- `README.md`
- `THIRD_PARTY_NOTICES`
- `LICENSE` (new binary-license draft from templates/LICENSE-binaries.md)
- `LICENSE-examples` (MIT text from templates/LICENSE-examples-MIT; source repo LICENSE stays private)

### Private peer (`lmctlhq/lmdraw`): 142 tracked files
- ``
- `.gitattributes`
- `.github/workflows/ci.yml`
- `.gitignore`
- `assets/automation-ladder-mobile.svg`
- `assets/automation-ladder.svg`
- `assets/fonts/NotoSans-Bold.ttf`
- `assets/fonts/NotoSans-Regular.ttf`
- `assets/fonts/NotoSansMath-Regular.ttf`
- `assets/level-automation.svg`
- `assets/level-delegate.svg`
- `assets/level-sessions.svg`
- `assets/level-team.svg`
- `assets/refused-class.svg`
- `CMakeLists.txt`
- `cpp/dslvm.hpp`
- `cpp/luna_renderer.cpp`
- `cpp/main.cpp`
- `cpp/renderer.hpp`
- `cpp/std/lmcode-std.schema.json`
- `cpp/stdlib/collections.hpp`
- `cpp/stdlib/file.hpp`
- `cpp/stdlib/math.hpp`
- `cpp/stdlib/std.hpp`
- `cpp/stdlib/string.hpp`
- `cpp/stdlib/testing.hpp`
- `cpp/tick_format.hpp`
- `durable-memory/01-purpose.md`
- `durable-memory/02-schema-and-svg.md`
- `durable-memory/03-build-run-test.md`
- `durable-memory/04-gotchas.md`
- `durable-memory/05-open-items.md`
- `durable-memory/06-licensing-and-release.md`
- `durable-memory/07-examples-and-images.md`
- `durable-memory/index.md`
- `LICENSE`
- `schema/lmdraw.dsl.json`
- `scripts/embed-resources.py`
- `scripts/merge-std.py`
- `scripts/select-compiler.sh`
- `scripts/stage-release-notices.sh`
- `scripts/sync-sdk.sh`
- `scripts/test-std.sh`
- `sdk.lock`
- `test.sh`
- `tests/fixtures/automation-ladder-mobile.svg`
- `tests/fixtures/automation-ladder.svg`
- `tests/fixtures/level-automation.svg`
- `tests/fixtures/level-delegate.svg`
- `tests/fixtures/level-sessions.svg`
- `tests/fixtures/level-team.svg`
- `tests/fixtures/refused-class.svg`
- `tests/golden/schema-summary.txt`
- `tests/images-output.lms`
- `tests/math-glyphs.lms`
- `tests/refusals/images-subdir.lms`
- `tests/refusals/images-traversal.lms`
- `tests/refusals/invalid-anchor.lms`
- `tests/refusals/invalid-axes.lms`
- `tests/refusals/invalid-connector-label-t.lms`
- `tests/refusals/invalid-connector-routing.lms`
- `tests/refusals/invalid-dash.lms`
- `tests/refusals/invalid-ellipse-radius.lms`
- `tests/refusals/invalid-grid.lms`
- `tests/refusals/invalid-legend.lms`
- `tests/refusals/invalid-log-axes.lms`
- `tests/refusals/invalid-marker.lms`
- `tests/refusals/outside-output.lms`
- `tests/refusals/prevalidate.lms`
- `tests/refusals/refused-svg.lms`
- `tests/refusals/stale-node.lms`
- `tests/unit.cpp`
- `tests/zero-corner-radius.lms`
- `third_party.lock`
- `third_party/lunasvg/.github/FUNDING.yml`
- `third_party/lunasvg/.github/workflows/main.yml`
- `third_party/lunasvg/.gitignore`
- `third_party/lunasvg/cmake/lunasvgConfig.cmake.in`
- `third_party/lunasvg/CMakeLists.txt`
- `third_party/lunasvg/examples/CMakeLists.txt`
- `third_party/lunasvg/examples/meson.build`
- `third_party/lunasvg/examples/svg2png.cpp`
- `third_party/lunasvg/include/lunasvg.h`
- `third_party/lunasvg/LICENSE`
- `third_party/lunasvg/meson_options.txt`
- `third_party/lunasvg/meson.build`
- `third_party/lunasvg/plutovg/.github/FUNDING.yml`
- `third_party/lunasvg/plutovg/.github/workflows/main.yml`
- `third_party/lunasvg/plutovg/.gitignore`
- `third_party/lunasvg/plutovg/cmake/plutovgConfig.cmake.in`
- `third_party/lunasvg/plutovg/CMakeLists.txt`
- `third_party/lunasvg/plutovg/examples/CMakeLists.txt`
- `third_party/lunasvg/plutovg/examples/meson.build`
- `third_party/lunasvg/plutovg/examples/smiley.c`
- `third_party/lunasvg/plutovg/include/plutovg.h`
- `third_party/lunasvg/plutovg/LICENSE`
- `third_party/lunasvg/plutovg/meson_options.txt`
- `third_party/lunasvg/plutovg/meson.build`
- `third_party/lunasvg/plutovg/README.md`
- `third_party/lunasvg/plutovg/smiley.png`
- `third_party/lunasvg/plutovg/source/FTL.TXT`
- `third_party/lunasvg/plutovg/source/plutovg-blend.c`
- `third_party/lunasvg/plutovg/source/plutovg-canvas.c`
- `third_party/lunasvg/plutovg/source/plutovg-font.c`
- `third_party/lunasvg/plutovg/source/plutovg-ft-math.c`
- `third_party/lunasvg/plutovg/source/plutovg-ft-math.h`
- `third_party/lunasvg/plutovg/source/plutovg-ft-raster.c`
- `third_party/lunasvg/plutovg/source/plutovg-ft-raster.h`
- `third_party/lunasvg/plutovg/source/plutovg-ft-stroker.c`
- `third_party/lunasvg/plutovg/source/plutovg-ft-stroker.h`
- `third_party/lunasvg/plutovg/source/plutovg-ft-types.h`
- `third_party/lunasvg/plutovg/source/plutovg-matrix.c`
- `third_party/lunasvg/plutovg/source/plutovg-paint.c`
- `third_party/lunasvg/plutovg/source/plutovg-path.c`
- `third_party/lunasvg/plutovg/source/plutovg-private.h`
- `third_party/lunasvg/plutovg/source/plutovg-rasterize.c`
- `third_party/lunasvg/plutovg/source/plutovg-stb-image-write.h`
- `third_party/lunasvg/plutovg/source/plutovg-stb-image.h`
- `third_party/lunasvg/plutovg/source/plutovg-stb-truetype.h`
- `third_party/lunasvg/plutovg/source/plutovg-surface.c`
- `third_party/lunasvg/plutovg/source/plutovg-utils.h`
- `third_party/lunasvg/README.md`
- `third_party/lunasvg/source/graphics.cpp`
- `third_party/lunasvg/source/graphics.h`
- `third_party/lunasvg/source/lunasvg.cpp`
- `third_party/lunasvg/source/svgelement.cpp`
- `third_party/lunasvg/source/svgelement.h`
- `third_party/lunasvg/source/svggeometryelement.cpp`
- `third_party/lunasvg/source/svggeometryelement.h`
- `third_party/lunasvg/source/svglayoutstate.cpp`
- `third_party/lunasvg/source/svglayoutstate.h`
- `third_party/lunasvg/source/svgpaintelement.cpp`
- `third_party/lunasvg/source/svgpaintelement.h`
- `third_party/lunasvg/source/svgparser.cpp`
- `third_party/lunasvg/source/svgparserutils.h`
- `third_party/lunasvg/source/svgproperty.cpp`
- `third_party/lunasvg/source/svgproperty.h`
- `third_party/lunasvg/source/svgrenderstate.cpp`
- `third_party/lunasvg/source/svgrenderstate.h`
- `third_party/lunasvg/source/svgtextelement.cpp`
- `third_party/lunasvg/source/svgtextelement.h`
- `third_party/lunasvg/subprojects/plutovg.wrap`

## Required path and release changes

- README-relative image/docs/example paths stay byte-for-byte at their current paths in the public peer.
- Raw autorun links checked: 28/28 map to public `.lms` files.
- Existing CI workflow paths move to the private peer; replace them with the private CI template and add public `.github/workflows/public-ci.yml`.
  - Private CI path: `.github/workflows/ci.yml`
- Expected public release assets: `lmdraw-linux-x64`, `lmdraw-linux-arm64`, `lmdraw-macos-x64`, `lmdraw-macos-arm64`, `lmdraw-windows-x64.exe`, plus `SHA256SUMS`.
- README links to private source paths checked: 0 finding(s).
- Public-plan secret scan: 0 finding(s); values are never printed.
- Licensing: Carry THIRD_PARTY_NOTICES, Noto Sans/Noto Sans Math OFL texts, FreeType FTL, stb/runtime terms, and the release process's source archive; full license texts go beneath docs/third-party-licenses/.

## Verification result

- Autorun path check: PASS
- Public docs source-reference check: PASS
- Public-plan secret scan: PASS

This is a read-only plan. No files were copied or changed, no GitHub operation was performed, and no visibility was changed.


## Staging results (2026-10-25, STAGING only; nothing flipped)

- Staged from `origin/main` `9452958efb8a` (clean, pushed) into `/home/mma/staging/closed-source/lmdraw-public/`: 94 files, public CI `.github/workflows/public-ci.yml` included.
- Release assets: latest `v0.2.6` (published 2026-10-25 from tag `v0.2.6` on `9452958`) downloaded to `lmdraw-release/` with `SHA256SUMS`; all five binaries (`lmdraw-linux-arm64`, `lmdraw-linux-x64`, `lmdraw-macos-arm64`, `lmdraw-macos-x64`, `lmdraw-windows-x64.exe`), `lmdraw-notices.tar.gz`, `LICENSE`, and `THIRD_PARTY_NOTICES` verify against `SHA256SUMS` (`sha256sum -c`).
- Staged release metadata and notes: `release-metadata.json` and `release-notes.md` generated with the MIT boundary up to and including `v0.2.6`.
- Verified: 28/28 README `lmctl autorun` targets exist in the staged tree; 30 local image/link refs resolve (28 README images present in `docs/images/`); no `/home/mma` path, no secret-like text, no private source/blob links.
- Licensing notices: complete for binary (LunaSVG MIT, PlutoVG MIT, FreeType FTL, stb public-domain, bundled Noto Sans/Noto Sans Math SIL-OFL texts under `docs/third-party-licenses/assets/fonts/OFL.txt`, LGPL-2.1 dynamic glibc and static GCC runtime GPL+exception texts under `docs/third-party-licenses/`).
- Staged `LICENSE` and `README.md` carry the boundary sentence: "Releases up to and including v0.2.6 were published under the MIT License (see the LICENSE asset of that release). Releases after v0.2.6 are published under the Lattice Systems Personal Use License (this file)."

### Host execution and example check results

- Verified with published release binary `lmdraw 0.2.6` on PATH:
  - **All 38/38 examples pass `lmscript --check`!**
  - Release `v0.2.6` includes the host diagram API building blocks (`Scene.box`, `Scene.cluster`, `Scene.cylinder`, `Scene.diamond`, `Scene.note`, `Scene.connector`, and `Shape` type from commit `e6c71c1`), successfully resolving the previous check failures seen on `v0.2.5`.

### Private CI

Staged at `/home/mma/staging/closed-source/lmdraw-private-ci.yml`, adapted from the current `.github/workflows/ci.yml`:
- Fast Linux job on `push: branches: [main]` and `pull_request`: builds with Ninja, runs `./test.sh`, and tests public examples against the fresh Linux host.
- Full 5-platform matrix (`linux-x64`, `linux-arm64`, `macos-arm64`, `macos-x64`, `windows-x64`) on `workflow_dispatch` or `v*` tag.
- Link audit steps preserved for Linux, macOS, and Windows.
- `publish-test` job verifies public write access with `secrets.RELEASE_TOKEN` without building.
- Gated publish job packages `lmdraw-notices.tar.gz`, calculates `SHA256SUMS`, and publishes to `lmctl-ai/lmdraw` with `secrets.RELEASE_TOKEN`.

### Pin inventory (1 consumer)

- `/home/mma/repos/dsl/simulation/ROADMAP.md:62` — `| [lmdraw](https://github.com/lmctl-ai/lmdraw) | [v0.2.4](https://github.com/lmctl-ai/lmdraw/releases/tag/v0.2.4) | own 2D diagram renderer, PNG and numbered-frame GIF | MIT | 28 | 18 (17 PNG, 1 GIF) | v0.2.4: math/arrow glyph fallback, Scene.log_axes, Scene.legend |`

After the flip:

```bash
sed -i -E 's|(github\.com/lmctl-ai/lmdraw/releases/tag/)v[0-9]+\.[0-9]+\.[0-9]+|\1v0.2.6|g; s|(github:lmctl-ai/lmdraw@)v[0-9]+\.[0-9]+\.[0-9]+|\1v0.2.6|g' /home/mma/repos/dsl/simulation/ROADMAP.md
```

### Preflight before flip

- No active `lmctl` team detected for `lmdraw`; working tree is clean and synced with `origin/main` at `9452958`.
- Published `v0.2.6` release is verified across all 5 platforms.
- Owner decisions:
  1. Approve `lmdraw` in `~/tools/closed-source-approved.txt`.
  2. Provide `RELEASE_TOKEN` for the private CI workflow.

### Ready to flip: YES (technically ready; pending owner approval & token)

Reasons: All 38 public examples pass `lmscript --check` against published `v0.2.6`; full 5-platform binary release verified with SHA256SUMS; clean/synced tree; complete notice closure; 1 consumer pin and sed command ready; awaiting only owner approval in `closed-source-approved.txt` and `RELEASE_TOKEN`.
