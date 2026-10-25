# Closed-source split dry-run: lmimg

**Staging status (2026-10-25): staged and verified — ready to flip pending owner
approval, RELEASE_TOKEN, first-tag choice, and quiescence preflight.**

- Source repo: `/home/mma/repos/dsl/lmimg`
- Source revision: `49186552658accc063eb5e7af9b33715523a3d6e`
- Private peer target: `lmctlhq/lmimg` (transfer this repository, then set it private, only after owner approval)
- Public peer target: `lmctl-ai/lmimg` (recreate at the old slug after transfer; preserve README/example paths)

## Exact tracked-file plan

### Public peer (`lmctl-ai/lmimg`): 65 tracked files
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
- `README.md`
- `THIRD_PARTY_NOTICES`
- `LICENSE` (new binary-license draft from templates/LICENSE-binaries.md)
- `LICENSE-examples` (MIT text from templates/LICENSE-examples-MIT; source repo LICENSE stays private)

### Private peer (`lmctlhq/lmimg`): 48 tracked files
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
- `cpp/std/lmcode-std.schema.json`
- `cpp/stdlib/collections.hpp`
- `cpp/stdlib/file.hpp`
- `cpp/stdlib/math.hpp`
- `cpp/stdlib/std.hpp`
- `cpp/stdlib/string.hpp`
- `cpp/stdlib/testing.hpp`
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
- `LICENSE`
- `schema/lmimg.dsl.json`
- `scripts/check-gallery.py`
- `scripts/gen-schema.py`
- `scripts/merge-std.py`
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
- Licensing: Carry ImageMagick NOTICE, IJG attribution, selected stb, Apache Roboto, SDK and runtime texts; optional GPL delegates remain disabled.

## Verification result

- Autorun path check: PASS
- Public docs source-reference check: PASS
- Public-plan secret scan: PASS

This is a read-only plan. No files were copied or changed, no GitHub operation was performed, and no visibility was changed.

## Staging verification pass (2026-10-25)

### Freshness

- `origin/main` re-fetched: `49186552658accc063eb5e7af9b33715523a3d6e` — identical to the
  staged SHA; no re-stage needed.
- CI run `40206014996` (staged SHA) was `in_progress` at staging time; it now
  reports `conclusion: success`. Staged tree is fresh and green.

### Staged public tree (`/home/mma/staging/closed-source/lmimg-public/`, 68 files)

- All 30 unique raw autorun URLs (62 README occurrences) resolve to staged files
  at the same paths; all 32 README images (30 PNG, 2 GIF) exist.
- No `/home/` paths, no source-file links, no `lmctlhq`/private references beyond
  the README's intentional "maintained privately in `lmctlhq/lmimg`" statement,
  no secret patterns.
- `THIRD_PARTY_NOTICES` (2873 lines) is the sanitized public variant of the
  source notice (private source paths replaced with "private implementation
  detail") and keeps every required text: ImageMagick license + required
  notices/NOTICE, IJG README/license/attribution (libjpeg-turbo), zlib, libpng,
  selected stb MIT, Apache-2.0 Roboto, lmcode-cpp MIT, glibc LGPL-2.1 statement,
  GCC Runtime Library Exception 3.1, and the "no GPL/LGPL delegates linked"
  statement. The staged layout keeps full texts inline in `THIRD_PARTY_NOTICES`;
  there is no `docs/third-party-licenses/` directory.

### Example checks against the released binary

- Downloaded released `lmimg-linux-x64` (`v0.1.3`) to scratch and put it first
  on `PATH`; `lmscript --check` passes on all 30 staged `examples/*.lms`
  (30/30, lmscript 0.2.420).
- No example needs external build artifacts or input data — all are procedural.
- Caveat: `examples/histogram_equalize_plot.lms` and
  `examples/pipeline_diagram.lms` contain secondary blocks binding
  `cli="lmdraw"` / `cli="lmplot"`. `--check` passes (syntax/schema only), but
  executing those two examples in private CI requires the lmdraw/lmplot CLIs
  installed (their `install=` attributes request them).

### Release mirror (`/home/mma/staging/closed-source/lmimg-release/`)

Latest release `v0.1.3` (published 2026-10-24), all 6 assets downloaded and
`sha256sum -c SHA256SUMS` verified OK:

| Asset | Size (bytes) | SHA256 |
| --- | --- | --- |
| `lmimg-linux-x64` | 8937672 | `25758fcb6a2521aa9a13be007f67cd09d4d0e1fba541f24d66bb18b1df0e2f36` |
| `lmimg-linux-arm64` | 8241136 | `2d85ff69d0b4e739317b95ada659f63d4c8d0ccb4a87a481f994b7224a5ef79f` |
| `lmimg-macos-x64` | 8248184 | `7da08fcfd71bca22e662c49198140ff5b47de3d6fcb77503bf1d6d99905d4c8a` |
| `lmimg-macos-arm64` | 7357912 | `98f477442ee6037241c89bbcee66bd6ca478943838c6f63f958a34c6e4dba6fe` |
| `lmimg-windows-x64.exe` | 8762880 | `4b556ae1c44c21eee26c56b13ffb42f1b2963786c615218c89fa1e748befbe24` |
| `SHA256SUMS` | 420 | — |

### Private CI draft (`/home/mma/staging/closed-source/lmimg-private-ci.yml`)

Adapted from lmimg's current `.github/workflows/ci.yml` into the pilot
(lmaudio) model shape; YAML validated:

- `linux-fast` job on every main push and PR (deps+sdk sync, `./test.sh` with
  `LMIMG_TEST_NETWORK=1`, fresh build first on `PATH`, public examples checked
  out anonymously from `lmctl-ai/lmimg` and checked + executed against it).
- `full-matrix` job (5 platforms incl. Windows msys2 ImageMagick Autoconf
  tooling, pinned actions) on `workflow_dispatch` or `v*` tags only; same
  public-examples step per platform; packages `build/lmimg[-.exe]` into
  `dist/lmimg-<platform>` artifacts.
- `publish-test` job (draft release create/delete with `RELEASE_TOKEN`).
- `publish` job, tag-gated, `needs: full-matrix`, `contents: read` everywhere
  except the token-scoped step: selects the tag, verifies all five assets,
  generates `SHA256SUMS`, **fails closed if the public release already exists**,
  refuses to run without `secrets.RELEASE_TOKEN`, then calls
  `scripts/release-to-public.sh` with `GH_TOKEN: ${{ secrets.RELEASE_TOKEN }}`.

### Pin inventory (inventory-pins.py + git grep across `/home/mma/repos/dsl/*` and `/home/mma/repos/lmctlhq/*`)

7 versioned lmimg references; lmctlhq repos have none. Only one actionable
consumer pin (others are lmimg's own historical durable-memory/review records
or simulation review docs):

- `/home/mma/repos/dsl/lmgallery/examples/34-image-pipeline-contact-sheet.lms:12`
  — `install="github:lmctl-ai/lmimg@v0.1.3"` (repo: lmgallery, owner: dsl).

Exact update line, parameterized on the future first tag (`<FIRST_TAG>`):

```sh
sed -i 's|github:lmctl-ai/lmimg@v0.1.3|github:lmctl-ai/lmimg@<FIRST_TAG>|' \
  /home/mma/repos/dsl/lmgallery/examples/34-image-pipeline-contact-sheet.lms
```

Remaining `@latest` references (lmimg README/tests/examples, lmcode-cpp memory,
simulation review) are self-healing and need no pin change.

### Flip readiness

- Staged SHA == current `origin/main` and CI is green; staged tree, notices,
  examples, release mirror, private CI, and pin inventory all verified above.
- Not flipped: owner approval, `RELEASE_TOKEN`, first-tag choice, and
  quiescence preflight are still required per the peer model.
