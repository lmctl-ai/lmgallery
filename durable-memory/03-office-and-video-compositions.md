# Office and video compositions (26-33)

Compositions 26-31 drive lmvideo (charts, PNG) and lmoffice (pptx, docx, xlsx) from one `.lms`
program. Their pictures are LibreOffice renders of the generated office file, made by
`scripts/render-office.py` (soffice headless to PDF, PyMuPDF rasterization, 900 px output).

Version pins (the cached `latest` binaries can be stale, so the compositions name a release tag):
- `lmvideo@v0.1.25` is the first release with the Plot layer (`canvas.panel`, `add_plot`, `series`).
  v0.1.23 has only the older canvas API.
- `lmoffice@v0.1.8` writes pictures as `pic:pic`. Release 0.1.1 wrote `a:pic`, and LibreOffice then
  renders the document without its images. v0.1.8 also has native Excel and PowerPoint charts
  (`Sheet.bar_chart`, `Slide.bar_chart`) and `Sheet.fit_to_page`.

Host limits found while building them:
- lmoffice cannot place an image in a worksheet, so composition 28 uses a native Excel chart beside
  its table. The lmvideo PNG is the gallery output, not part of the workbook.
- lmvideo charts have numeric category axes only. Category names are added with `Plot.annotate` under
  the axis, with the y-range extended below zero.
- lmvideo cannot read files. Series are fed with `${...}` scalars, so composition 31 plots the three
  measured damping ratios rather than whole time series.
- Inside `_dsl_`, a `fn` defined at top level is not visible; define it inside the block.
- The lmvideo DSL has `mix(a, b, t)` for colour interpolation and `image_file` / `image_rect` for
  placing PNGs on a canvas. Its `video.save_frame(path)` writes the current frame as a PNG.
- lmvideo encodes MP4 through ffmpeg on PATH; the CI matrix installs it for composition 33.

Deterministic outputs: every chart, document and frame is byte-stable on one machine. The
LibreOffice picture depends on the local font set, so regenerate it on the same machine as before.
