# Closed-source split dry-run: lmimg

- Source repo: `/home/mma/repos/dsl/lmimg`
- Source revision: `1b386318f028bc7f94ca26af75bf6def34f5a334`
- Private peer target: `lmctlhq/lmimg` (transfer this repository, then set it private, only after owner approval)
- Public peer target: `lmctl-ai/lmimg` (recreate at the old slug after transfer; preserve README/example paths)

## Exact tracked-file plan

### Public peer (`lmctl-ai/lmimg`): 66 tracked files
- `docs/images/animation_wave.gif`
- `docs/images/animation_wave.png`
- `docs/images/barcode_label.png`
- `docs/images/batch_resize.png`
- `docs/images/before_after_panels.png`
- `docs/images/blend_modes.png`
- `docs/images/blur_reveal.png`
- `docs/images/color_grade_lut.png`
- `docs/images/contact_sheet_shoot.png`
- `docs/images/contact_sheet_story.png`
- `docs/images/document_scan_cleanup.png`
- `docs/images/edge_map.png`
- `docs/images/gradient_studio.png`
- `docs/images/graduated_nd_layers.png`
- `docs/images/hdr_tone_map.png`
- `docs/images/histogram_equalize_plot.png`
- `docs/images/image_diff_heatmap.png`
- `docs/images/lens_undistort.png`
- `docs/images/levels_lab.png`
- `docs/images/miniature_tilt_shift.png`
- `docs/images/perspective_whiteboard.png`
- `docs/images/pipeline_diagram.png`
- `docs/images/portrait_retouch.png`
- `docs/images/poster_text.png`
- `docs/images/procedural_photo.png`
- `docs/images/salt_pepper_denoise.png`
- `docs/images/sepia_poster.png`
- `docs/images/sprite_sheet.gif`
- `docs/images/sprite_sheet.png`
- `docs/images/thumbnail_grid.png`
- `docs/images/watermark_story.png`
- `docs/images/watermark_tiled.png`
- `examples/animation_wave.lms`
- `examples/barcode_label.lms`
- `examples/batch_resize.lms`
- `examples/before_after_panels.lms`
- `examples/blend_modes.lms`
- `examples/blur_reveal.lms`
- `examples/color_grade_lut.lms`
- `examples/contact_sheet_shoot.lms`
- `examples/contact_sheet_story.lms`
- `examples/document_scan_cleanup.lms`
- `examples/edge_map.lms`
- `examples/gradient_studio.lms`
- `examples/graduated_nd_layers.lms`
- `examples/hdr_tone_map.lms`
- `examples/histogram_equalize_plot.lms`
- `examples/image_diff_heatmap.lms`
- `examples/lens_undistort.lms`
- `examples/levels_lab.lms`
- `examples/miniature_tilt_shift.lms`
- `examples/perspective_whiteboard.lms`
- `examples/pipeline_diagram.lms`
- `examples/portrait_retouch.lms`
- `examples/poster_text.lms`
- `examples/procedural_photo.lms`
- `examples/render-all.sh`
- `examples/salt_pepper_denoise.lms`
- `examples/sepia_poster.lms`
- `examples/sprite_sheet.lms`
- `examples/thumbnail_grid.lms`
- `examples/watermark_story.lms`
- `examples/watermark_tiled.lms`
- `LICENSE`
- `README.md`
- `THIRD_PARTY_NOTICES`
- `LICENSE-binaries` (new owner-approved binary license text; not present in this source checkout unless listed above)

### Private peer (`lmctlhq/lmimg`): 39 tracked files
- ``
- `.gitattributes`
- `.github/workflows/ci.yml`
- `.gitignore`
- `CMakeLists.txt`
- `cpp/dslvm.hpp`
- `cpp/expr.hpp`
- `cpp/image.cpp`
- `cpp/image.hpp`
- `cpp/main.cpp`
- `cpp/memory_budget.cpp`
- `cpp/memory_budget.hpp`
- `deps.lock`
- `durable-memory/01-purpose.md`
- `durable-memory/02-libraries-and-licenses.md`
- `durable-memory/03-schema-and-numerics.md`
- `durable-memory/04-memory-budget.md`
- `durable-memory/05-build-and-tests.md`
- `durable-memory/06-ci-and-release.md`
- `durable-memory/07-examples.md`
- `durable-memory/08-limitations.md`
- `durable-memory/09-review-0.1.1.md`
- `durable-memory/10-review-0.1.2.md`
- `durable-memory/index.md`
- `schema/lmimg.dsl.json`
- `scripts/check-gallery.py`
- `scripts/gen-schema.py`
- `scripts/select-compiler.sh`
- `scripts/static-codec-pkg-config.sh.in`
- `scripts/sync-deps.sh`
- `scripts/sync-sdk.sh`
- `sdk.lock`
- `test.sh`
- `tests/check-vm-operands.py`
- `tests/editing.lms`
- `tests/oracles.lms`
- `tests/pixels.lms`
- `tests/review_image.lms`
- `tests/scientific.cpp`

## Required path and release changes

- README-relative image/docs/example paths stay byte-for-byte at their current paths in the public peer.
- Raw autorun links checked: 62/62 map to public `.lms` files.
- Existing CI workflow paths move to the private peer; replace them with the private CI template and add public `.github/workflows/public-ci.yml`.
  - Private CI path: `.github/workflows/ci.yml`
- Expected public release assets: `lmimg-linux-x64`, `lmimg-linux-arm64`, `lmimg-macos-x64`, `lmimg-macos-arm64`, `lmimg-windows-x64.exe`, plus `SHA256SUMS`.
- README links to private source paths checked: 0 finding(s).
- Public-plan secret scan: 0 finding(s); values are never printed.
- Licensing: Ship LICENSE, THIRD_PARTY_NOTICES, ImageMagick NOTICE, IJG README/license/attribution, chosen stb license, Apache-2.0 Roboto, SDK MIT and platform runtime texts; no GPL delegates are linked.

## Verification result

- Autorun path check: PASS
- Public docs source-reference check: PASS
- Public-plan secret scan: PASS

This is a read-only plan. No files were copied or changed, no GitHub operation was performed, and no visibility was changed.
