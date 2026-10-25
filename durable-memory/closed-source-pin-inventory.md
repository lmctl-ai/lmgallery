# Closed-source consumer tag-pin inventory

Grep snapshot: 2026-10-25. This is a local-repository inventory from `/home/mma/repos/dsl` and `/home/mma/repos/lmctlhq`, excluding `.git`, build, target, node_modules, and virtualenv trees. It includes versioned `install=github:lmctl-ai/<product>@vX.Y.Z` pins and release tag/download links; `@latest` references are intentionally excluded.

| Product | Matches | Action before flip |
| --- | ---: | --- |
| `lmdraw` | 1 | update to the first new public release tag |
| `lmvideo` | 50 | update to the first new public release tag |
| `lmaudio` | 2 | update to the first new public release tag |
| `lmoffice` | 26 | update to the first new public release tag |
| `lmcad` | 1 | update to the first new public release tag |
| `lmblender` | 1 | update to the first new public release tag |
| `lmmagnum` | 1 | update to the first new public release tag |
| `lmfilament` | 0 | none found in scanned local repos |
| `lmimg` | 7 | update to the first new public release tag |
| `lmpdf` | 1 | update to the first new public release tag |

## Matches by product

## lmdraw

- `/home/mma/repos/dsl/simulation/ROADMAP.md:62` — `| [lmdraw](https://github.com/lmctl-ai/lmdraw) | [v0.2.4](https://github.com/lmctl-ai/lmdraw/releases/tag/v0.2.4) | own 2D diagram renderer, PNG and numbered-frame GIF | MIT | 28 | 18 (17 PNG, 1 GIF) | v0.2.4: math/arrow glyph fallback, `Scene.log_axes`, `Scene.legend` |`

## lmvideo

- `/home/mma/repos/dsl/lmgallery/examples/26-qbr-deck-charts.lms:10` — `charts_1 = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/26-qbr-deck-charts.lms:31` — `charts_2 = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/26-qbr-deck-charts.lms:52` — `charts_3 = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/27-sales-report-docx.lms:12` — `charts_1 = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/27-sales-report-docx.lms:32` — `charts_2 = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/27-sales-report-docx.lms:51` — `charts_3 = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/28-forecast-workbook-chart.lms:45` — `chart_program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/29-invoice-logo-glyph.lms:18` — `art = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/29-invoice-logo-glyph.lms:30` — `glyph = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/29-invoice-logo-glyph.lms:60` — `sheet = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/30-resume-skills-bars.lms:9` — `skills = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/31-science-report-damping.lms:66` — `figure = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/33-wave-2d-animation.lms:56` — `film = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/dsl/lmgallery/examples/35-finance-curve-option-workbook.lms:55` — `chart = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/36-html-link-check-report.lms:51` — `term = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/37-cert-inventory-docx.lms:62` — `cards = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/39-audio-harmonics-slide.lms:51` — `chart = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/40-bio-predator-prey-report.lms:105` — `figure = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/41-weather-gravity-wave-speed.lms:91` — `figure = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/42-cell-growth-report.lms:55` — `figure = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/43-physics-lab-report.lms:75` — `chart = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/44-astronomy-observing-plan.lms:100` — `chart = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/45-finance-bond-memo.lms:113` — `chart = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/46-network-audit-report.lms:126` — `chart = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/47-weather-briefing-slides.lms:65` — `chart = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/48-bio-epidemic-workbook.lms:100` — `chart = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/49-cloud-plan-report.lms:96` — `chart = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/dsl/lmgallery/examples/50-data-quality-report.lms:124` — `chart = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.28";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/carnot-cycle.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.23";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/cavity-quiver.lms:4` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.26";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/chart-kinds-workbench.lms:3` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.26";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/confusion-matrix.lms:6` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.26";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/damped-oscillator.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.23";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/dashboard-grid.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/forecast-area.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.23";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/hydrogen-spectrum.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.23";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/layout-workbench.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.25";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/lotka-volterra.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.23";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/poisson-contours.lms:3` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.26";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/pr-average-precision.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.26";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/quarterly-revenue.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.23";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/rc-lowpass.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.23";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/relativity-lorentz.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.23";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/residual-scatter.lms:9` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.26";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/roc-auc.lms:17` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.26";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/sensor-calibration.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.23";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/standing-wave-field.lms:3` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.26";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/symlog-outlier.lms:3` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.26";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/vector-outputs.lms:4` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.29";`
- `/home/mma/repos/lmctlhq/lmvideo/examples/waveform-sampling.lms:7` — `program = _lmcode_ cli="lmvideo" install="github:lmctl-ai/lmvideo@v0.1.23";`

## lmaudio

- `/home/mma/repos/dsl/lmgallery/examples/39-audio-harmonics-slide.lms:11` — `analysis = _lmcode_ cli="lmaudio" install="github:lmctl-ai/lmaudio@v0.2.1";`
- `/home/mma/repos/dsl/simulation/ROADMAP.md:36` — `| 8 | [lmaudio](https://github.com/lmctl-ai/lmaudio) | [v0.2.0](https://github.com/lmctl-ai/lmaudio/releases/tag/v0.2.0) | DaisySP (MIT), Soundpipe core (MIT), own FFT/STFT/biquad/pitch, RIFF/WAVE I/O | MIT only (KFR, libsndfile skipped) | 22 | 22 (21 PNG, 1 GIF) | preview (first release, smaller API) |`

## lmoffice

- `/home/mma/repos/dsl/lmgallery/examples/26-qbr-deck-charts.lms:74` — `deck_program = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.8";`
- `/home/mma/repos/dsl/lmgallery/examples/27-sales-report-docx.lms:87` — `report_program = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.8";`
- `/home/mma/repos/dsl/lmgallery/examples/28-forecast-workbook-chart.lms:74` — `book_program = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.8";`
- `/home/mma/repos/dsl/lmgallery/examples/29-invoice-logo-glyph.lms:78` — `book = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.8";`
- `/home/mma/repos/dsl/lmgallery/examples/30-resume-skills-bars.lms:35` — `resume_program = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.8";`
- `/home/mma/repos/dsl/lmgallery/examples/31-science-report-damping.lms:84` — `report = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.8";`
- `/home/mma/repos/dsl/lmgallery/examples/34-image-pipeline-contact-sheet.lms:48` — `deck = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.9";`
- `/home/mma/repos/dsl/lmgallery/examples/35-finance-curve-option-workbook.lms:71` — `book = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.9";`
- `/home/mma/repos/dsl/lmgallery/examples/36-html-link-check-report.lms:70` — `report_doc = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.9";`
- `/home/mma/repos/dsl/lmgallery/examples/37-cert-inventory-docx.lms:87` — `word = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.9";`
- `/home/mma/repos/dsl/lmgallery/examples/38-product-render-slide.lms:29` — `deck = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.9";`
- `/home/mma/repos/dsl/lmgallery/examples/39-audio-harmonics-slide.lms:67` — `deck = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.9";`
- `/home/mma/repos/dsl/lmgallery/examples/40-bio-predator-prey-report.lms:133` — `report = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.9";`
- `/home/mma/repos/dsl/lmgallery/examples/41-weather-gravity-wave-speed.lms:109` — `report = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.9";`
- `/home/mma/repos/dsl/lmgallery/examples/42-cell-growth-report.lms:76` — `report = _lmcode_ cli="lmoffice" install="github:lmctl-ai/lmoffice@v0.1.9";`
- `/home/mma/repos/dsl/lmgallery/examples/43-physics-lab-report.lms:59` — `report = _lmcode_ cli="lmoffice docx" install="github:lmctl-ai/lmoffice@v0.1.21";`
- `/home/mma/repos/dsl/lmgallery/examples/44-astronomy-observing-plan.lms:62` — `word = _lmcode_ cli="lmoffice docx" install="github:lmctl-ai/lmoffice@v0.1.21";`
- `/home/mma/repos/dsl/lmgallery/examples/44-astronomy-observing-plan.lms:91` — `deck = _lmcode_ cli="lmoffice pptx" install="github:lmctl-ai/lmoffice@v0.1.21";`
- `/home/mma/repos/dsl/lmgallery/examples/45-finance-bond-memo.lms:102` — `workbook = _lmcode_ cli="lmoffice xlsx" install="github:lmctl-ai/lmoffice@v0.1.21";`
- `/home/mma/repos/dsl/lmgallery/examples/45-finance-bond-memo.lms:86` — `memo = _lmcode_ cli="lmoffice docx" install="github:lmctl-ai/lmoffice@v0.1.21";`
- `/home/mma/repos/dsl/lmgallery/examples/46-network-audit-report.lms:102` — `audit = _lmcode_ cli="lmoffice docx" install="github:lmctl-ai/lmoffice@v0.1.21";`
- `/home/mma/repos/dsl/lmgallery/examples/47-weather-briefing-slides.lms:80` — `deck = _lmcode_ cli="lmoffice pptx" install="github:lmctl-ai/lmoffice@v0.1.21";`
- `/home/mma/repos/dsl/lmgallery/examples/48-bio-epidemic-workbook.lms:45` — `workbook = _lmcode_ cli="lmoffice xlsx" install="github:lmctl-ai/lmoffice@v0.1.21";`
- `/home/mma/repos/dsl/lmgallery/examples/48-bio-epidemic-workbook.lms:72` — `report = _lmcode_ cli="lmoffice docx" install="github:lmctl-ai/lmoffice@v0.1.21";`
- `/home/mma/repos/dsl/lmgallery/examples/49-cloud-plan-report.lms:87` — `report = _lmcode_ cli="lmoffice docx" install="github:lmctl-ai/lmoffice@v0.1.21";`
- `/home/mma/repos/dsl/lmgallery/examples/50-data-quality-report.lms:109` — `report = _lmcode_ cli="lmoffice docx" install="github:lmctl-ai/lmoffice@v0.1.21";`

## lmcad

- `/home/mma/repos/dsl/simulation/ROADMAP.md:63` — `| [lmcad](https://github.com/lmctl-ai/lmcad) | [v0.1.4](https://github.com/lmctl-ai/lmcad/releases/tag/v0.1.4) | OpenCASCADE B-rep + built-in software renderer (PNG, APNG, STL) | MIT host; OCCT LGPL-2.1 with exception: relink objects and recipe shipped per release | 20 | 12 (11 PNG, 1 GIF) | no GPU or display needed |`

## lmblender

- `/home/mma/repos/dsl/simulation/ROADMAP.md:64` — `| [lmblender](https://github.com/lmctl-ai/lmblender) | [v0.3.6](https://github.com/lmctl-ai/lmblender/releases/tag/v0.3.6) | Blender Cycles path tracer as one static executable | GPL-3.0-or-later; per-platform notices, source offer and relinking notes attached to each release | 82 | 12 (11 PNG, 1 GIF) | CI on push builds linux x64/arm64; macOS and Windows run in the `platforms` workflow; all 5 platforms on the release |`

## lmmagnum

- `/home/mma/repos/dsl/lmgallery/examples/38-product-render-slide.lms:10` — `render = _lmcode_ cli="lmmagnum" install="github:lmctl-ai/lmmagnum@v0.2.11";`

## lmfilament

- No versioned install or release URL found in the scanned local trees.

## lmimg

- `/home/mma/repos/dsl/lmgallery/examples/34-image-pipeline-contact-sheet.lms:12` — `pipeline = _lmcode_ cli="lmimg" install="github:lmctl-ai/lmimg@v0.1.3";`
- `/home/mma/repos/dsl/lmimg/durable-memory/06-ci-and-release.md:110` — `Released [v0.1.1](https://github.com/lmctl-ai/lmimg/releases/tag/v0.1.1) from`
- `/home/mma/repos/dsl/lmimg/durable-memory/06-ci-and-release.md:55` — `[v0.1.0](https://github.com/lmctl-ai/lmimg/releases/tag/v0.1.0), tag commit`
- `/home/mma/repos/dsl/lmimg/durable-memory/09-review-0.1.1.md:32` — `- Release: https://github.com/lmctl-ai/lmimg/releases/tag/v0.1.1 (exactly five executable assets).`
- `/home/mma/repos/dsl/simulation/REVIEW_lmimg.md:203` — `- Release: https://github.com/lmctl-ai/lmimg/releases/tag/v0.1.1 (exactly five executable assets).`
- `/home/mma/repos/dsl/simulation/REVIEW_lmimg.md:55` — `curl -sI https://github.com/lmctl-ai/lmimg/releases/tag/v0.1.0   # HTTP 404`
- `/home/mma/repos/dsl/simulation/ROADMAP.md:38` — `| 10 | [lmimg](https://github.com/lmctl-ai/lmimg) | [v0.1.1](https://github.com/lmctl-ai/lmimg/releases/tag/v0.1.1) | static ImageMagick MagickCore/Wand, zlib/libpng/libjpeg-turbo/libtiff/libwebp, stb_truetype/Roboto, own editing core | MIT host; permissive engine/codecs/font; no GIMP/GEGL | 30 | 32 (30 PNG, 2 GIF) | preview; independent review addressed |`

## lmpdf

- `/home/mma/repos/dsl/lmpdf/durable-memory/08-release.md:154` — `replays, and publication. [Release v0.1.54](https://github.com/lmctl-ai/lmpdf/releases/tag/v0.1.54)`

A pin can be changed only after the first public release tag is known and published. The flip runner records this inventory during staging; before apply it must re-scan and ensure consumers can be updated without overwriting dirty or actively edited checkouts.
