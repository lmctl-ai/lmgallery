# Document-as-code reports (compositions 43–50)

Eight compositions compute results in a science, finance or data host, format them as Markdown in the outer
script, and hand the text to lmoffice. Each picture pairs the 13-line source excerpt with the rendered first
page or slide (`scripts/source-page-preview.py`, LibreOffice through `scripts/render-office.py`).

| Script | Compute host | Office output | Outer check |
| --- | --- | --- | --- |
| 43 physics lab report | lmphysics | docx (heredoc limitations) | measured mu within 0.01 of 0.3 |
| 44 observing plan | lmspace | docx and pptx from one body | perigee/apogee within 1 km |
| 45 finance memo | lmfinance | docx memo, xlsx workbook | bond price vs discount factors within 0.05 |
| 46 network audit | lmssl, lmhtml | docx (heredoc scope) | two self-signed certs, two broken links |
| 47 weather briefing | lmweather | pptx (Markdown slides, image slide) | speeds within 1 % of sqrt(g H) |
| 48 epidemic workbook | lmbio | xlsx (time series, summary) and docx | mass conserved; peak and final sizes |
| 49 cloud change report | lmcloud | docx | one changed, two unchanged, from state |
| 50 data-quality report | lmnum | docx | planted defects counted by csv_parse |

## Patterns

- **Heredoc in a block** (lmscript 0.2.420): `let limits = <<~MD;` then the body, then the tag alone on a line.
  The body is raw (no `${}`), and common indentation is stripped. Use it for static prose inside an lmoffice
  block, and join it with the dynamic text: `doc.markdown(body + "\n" + limits)`. The variable must be defined
  in the block, not referenced from an outer `${}` splice.
- **Outer Markdown**: build the body in outer variables from `"""` literals and `sprintf` rows. A `"""` literal
  cannot be concatenated with `+` inside a `${}` splice, and a triple-quoted string cannot appear inside a block
  splice (the block parser rejects it). Splice the finished variable: `doc.markdown(${body}).save();`.
- **Office calls** (lmoffice 0.1.21): `docx.create(path).markdown(text).save()`, `pptx.create(path).markdown(text).save()`,
  `xlsx.create(path).sheet_from_csv(name, csv)` then `save()`.
- **Slides**: each slide has exactly one heading. A `##` under a `#` slide title is an error ("each slide has one
  heading before its content"), so write deck text separately from the Word body.
- **Whole-number floats** splice as integer literals, which series and bar APIs reject. Add a small offset that
  keeps the repr short: `+ 0.0001` works, `+ 0.000000001` does not (`1e-09` has no exact literal). For tiny
  values, scale to percent and round with `num(sprintf("%.4f", x * 100.0 + 0.0001))`.
- **Host values**: lmcloud returns only `{"ok"...}` (its `result` is null) and has no print call. Read what it
  writes: `json_parse(read_file("build/infra/terraform.tfstate"))`. The input attribute is typed:
  `attributes.input.value`. Plan counts (`plan.add()` etc.) are not readable by the script in this host version.
- **Repeated-key checks**: `contains(array, x)` is not an exact membership test in this language. Use a delimited
  string (`"|" + key + "|"`).
- **Argument order**: lmfinance `instrument.bond(face, coupon, years, frequency)`; lmnum `load_csv` skips the header
  and `col(i)` is 0-based; lmweather `wave_speed()` on a `linear()` plane; lmssl `ssl.load_cert(path)`.

## Verification

- `lmscript --check` passes on every new script. Each composition runs with `lmctl autorun` from an empty directory.
- `scripts/run-examples.py --only NN` runs one composition and checks its PNG width.
- `python3 scripts/build-readme.py --check` and `tests/check_gallery.py` pass with 50 compositions.
- `tests/check_gallery.py` reads each `cli="..."` binding. A subcommand binding such as `cli="lmoffice docx"` is
  matched by its first word (`lmoffice`), so the host chain is checked for office blocks too.

## Local environment

`~/.local/bin/lmbio` (0.1.0) is on PATH and shadows the released lmbio; lmscript then rejects it because it has no
`--dsl-schema --json`. Run the compositions with the released hosts from the lmscript cache by keeping that
directory off PATH (`PATH=/usr/local/bin:/usr/bin:/bin lmctl autorun ...`). CI installs the released hosts and is
not affected.

## Open items

- lmcloud plan counts are not readable by lmscript (no return values, no print); composition 49 reports the applied
  state instead. Revisit when lmcloud exposes plan JSON or a print call.
- The source excerpts show the Markdown body as written, including `sprintf` calls, so they are long.
- Compositions 43–50 need lmscript 0.2.420 (heredoc). CI pins it already.

## PDF from the same block (lmpdf)

Compositions 43, 44, 45, 46, 49 and 50 also write a PDF. Directly after the `cli="lmoffice docx"` block
there is a copy of that block with exactly two changes:
- `cli="lmpdf docx" install="github:lmctl-ai/lmpdf@v0.1.62"`;
- `.pdf` instead of `.docx` in `docx.create(...)`.

The variable and the bytecode name get a `_pdf` / `-pdf` suffix. lmpdf exposes the same
`lmoffice_docx` schema, so the block compiles unchanged, Markdown body and heredoc included. The PDF is
PDF/A-2b + PDF/UA-1 tagged and byte-reproducible. Its layout parity with LibreOffice's render of the .docx is
measured in lmpdf's parity corpus (durable-memory/07-parity-report.md there).

`showcases.json` lists `lmpdf` in each of these host chains, because `tests/check_gallery.py` requires the
listed hosts to equal the `cli=` bindings. All six run with the released hosts from an empty directory and
write both `build/*.docx` and `build/*.pdf`.
