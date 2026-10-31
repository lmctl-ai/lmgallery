# Phase 7.2: gallery migration to lmvideo v0.1.36

Executed 2026-10-30 by KimiK3b. Implements row 7.2 of
[09-lmvideo-backlog.md](09-lmvideo-backlog.md): migrate the public gallery
compositions affected by the lmdraw/lmimg/lmmagnum/lmfilament → lmvideo
consolidation while keeping historical pins installable.

## Affected-composition count (verify of the "31 of 50" plan figure)

Inventory of every `cli=` binding in `examples/*.lms` against the consolidating
hosts (lmdraw, lmmagnum, lmfilament, lmimg, lmvideo):

- lmdraw: 02, 05, 11, 13 (4)
- lmimg: 14, 34 (2)
- lmmagnum: 38 (1)
- lmfilament: none (0)
- lmvideo: 26–31, 33, 35–37, 39–50 (22)

Total affected by the consolidation: **29**. The plan's "31" is reproduced only
if the two lmcad compositions (04, 10) are also counted; lmcad is a separate
product outside this migration, so 29 is the operative number.

## Baseline before migration

`scripts/run-examples.py --only NN` for NN = 01–50 on unmodified main:
**50/50 execute** and produce their declared outputs. Four compositions
(07, 13, 40, 48; all lmbio) fail *only* under this machine's ambient PATH, where
a stale `~/.local/bin/lmbio` 0.1.0 without `--lmcode-schema --json` shadows the
released host (pre-existing, see index.md open items). With a clean PATH the
released lmbio v0.1.3 installs and all four pass. All verification here used
`PATH=$HOME/work/KimiK3b/bin:/usr/bin:/bin` (shim dir with only lmctl/lmscript
symlinks). Hosts resolve to `~/.cache/lmscript/tools/github/lmctl-ai/<host>/<tag>/`.

The same baseline witnesses that every historical pin still installs and runs:
lmdraw@latest, lmimg@v0.1.3, lmmagnum@v0.2.14, lmvideo@v0.1.25 and @v0.1.28,
lmoffice@v0.1.29, lmpdf@v0.1.62, lmcad@latest, and the other `@latest` hosts.

## Migration decisions

All seven legacy-host compositions were **migrated to lmvideo v0.1.36**
(released; `gh api repos/lmctl-ai/lmvideo/releases/latest` → v0.1.36), reusing
KimiK3a's verified ports in `lmctlhq/lmvideo/examples/compositions/`
(hash-locked in `sources.json` / `image-sources.json` / `scene-sources.json`;
the gallery source hashes there match this repo's main). The only public-side
change to those ports is the explicit `install="github:lmctl-ai/lmvideo@v0.1.36"`
pin the gallery checker requires. lmvideo's Phase-3+ APIs (`scene3d`,
`camera3d`) make v0.1.36 the minimum usable pin for 38.

- 02, 05, 11, 13 (lmdraw → lmvideo Canvas), 14 (lmimg → lmvideo Layout): the
  script output **is** the gallery picture; pictures regenerated with the
  migrated scripts. Deltas vs the old pictures: mean abs pixel diff ≤ 2.5/255,
  same dimensions — the accepted font-metric/antialiasing deltas recorded in
  lmvideo durable-memory 18/21.
- 34 (lmimg → lmvideo): the declared script output (the 900×202 contact sheet)
  matches the old lmimg sheet at mean abs diff 0.016/255, max 1 (resampler
  rounding only). The **committed gallery picture is a LibreOffice render of
  the slide, not the script output** — pre-existing since commit ef10b98; kept
  unchanged because LibreOffice is not installed on the migration machine.
  Same situation for 38 (committed picture is the slide render, commit 312b0d5).
  Recorded consequence: `examples/render-all.sh` (`run-examples.py --update`)
  would replace those two pictures with the raw script outputs; that tooling
  inconsistency predates this migration.
- 38 (lmmagnum → lmvideo Scene3D): geometry is asserted in metres with bound
  checks; shading differs by design (lmvideo opaque CPU Lambert vs lmmagnum PBR
  specular; noted in the slide's speaker notes). Picture kept (see above).

The 22 lmvideo compositions were re-pinned v0.1.25/v0.1.28 → v0.1.36. Outputs
are **byte-identical** (SHA-256) to the old-pin runs for all 22, so no pictures
changed.

`showcases.json` host lists and descriptions now name lmvideo for the seven
migrated compositions; README.md and examples/README.md regenerated with
`scripts/build-readme.py`. catalog.json is unchanged (the 16 host previews and
the lmdraw/lmimg entries stay; those repos remain real maintenance-only
standalone hosts, not aliases).

## Acceptance evidence (7.2)

- All 50 gallery compositions execute: `./test.sh --run` →
  `PASS: 50 empty-directory executions` (clean PATH as above).
- The 29 affected compositions produce their declared outputs (7 migrated,
  22 re-pinned; run individually with per-composition PASS logs).
- Raw autorun URLs: `./test.sh --urls` after the push (50/50).
- `./test.sh` offline gate, `tests/closed-source-workflows` unittest,
  `bash -n test.sh examples/render-all.sh`, `git diff --check`: all green.
- Historical tags still install and run: baseline evidence above.

## Not done here (out of scope / follow-ups)

- lmcad compositions 04, 10: untouched (lmcad stays a separate product).
- The 34/38 slide-render pictures: regenerate with `scripts/render-office.py`
  on a machine with LibreOffice, or accept the raw script outputs, as a
  separate content decision.
- arm64 spot check on t4g1/t4g2 was not needed for a content/pin change.
