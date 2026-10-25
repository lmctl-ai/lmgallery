# lmcreator idea backlog: what to port into the lmctl-ai public hosts

Survey of a private predecessor tool `lmcreator` (a multi-format render + lint engine
for LLM-authored visuals) mapped onto our public hosts (`lmctl-ai` organization).
Purpose: mine its examples and design docs for ports. The predecessor tool was NOT modified;
no secrets were copied.

Note on naming: the predecessor tool's binary/artifacts carried the legacy name `lmvideo`;
our public `lmvideo` repository (Skia 2D + SVG + video, currently growing a high-level
Plot layer, "Luna") is a different codebase.

Placement philosophy (owner refinement): NO hidden graph-layout engines (nothing like
Graphviz/mermaid auto-placement that computes geometry the author never sees). In their
place: EXPLICIT LAYOUT MANAGERS in the Tcl/Tk and Java Swing tradition — containers with
children and constraints that the script author chooses and controls. They are
predictable, composable, and visible in the script, and they replace hand-computed pixel
coordinates.

## 1. Capability map: lmcreator -> our repos

| lmcreator capability | lmcreator source | Status in our repos |
|---|---|---|
| `.chart` explicit chart DSL | examples/charts/*.chart | Partially covered: lmplot (lines/bars/scatter/errorbars/fillbetween/multiplot/date axes/polar), lmdraw hand-built charts (`chart-bars-lines.lms`). Missing: JSON spec surface, symlog scale, computed metric sidecars |
| `.mplchart` matplotlib-flavor JSON | examples/charts/*.mplchart | Partially covered (same as above); no matplotlib-like JSON input layer on any host |
| `.mplchartanim` keyframe chart animation | examples/charts/*.mplchartanim | Partially covered: lmplot video frame loops (video/*.lms), lmvideo tweened scenes; no fixed-structure keyframe tween spec |
| `.field` heatmap + contour + quiver + spacetime + frame animation | examples/field/*.field | Partially covered: lmplot heatmaps (matrix+XYZ), contours (`contours.lms`), vector field (`vector.lms`), pm3d surfaces; lmfluid/lmfinance heatmap examples. Missing: contour/quiver OVERLAID on a 2D heatmap image, 1D→x–t spacetime ranking, frame-column field→MP4 |
| `.confusion` confusion matrix | examples/field/ml-confusion.confusion | Not covered (a labeled matrix heatmap in lmplot is possible by hand, but there is no cell-text/contrast/normalize primitive) |
| `.mlplot` ROC / PR / pred-actual / residual | examples/field/*.mlplot | Not covered anywhere |
| mermaid flowchart | examples/mermaid/{pipeline-lr,decision-flow}.mmd | Covered: lmdraw `flow-pipeline.lms`, `decision-flowchart.lms` |
| mermaid sequence diagrams — SYNTAX IDEAS ONLY, no hidden layout | examples/mermaid/{api-call-chain,login,retry-timeout}.mmd | Not covered. Borrow vocabulary only (participants, lifelines, activations, sync/async messages). Placement = explicit layout managers (box/grid) or absolute place; lifeline/message helpers take coordinates inside a managed container |
| mermaid state diagrams — SYNTAX IDEAS ONLY, no hidden layout | examples/mermaid/{order-state,traffic-light-state,compare-state-*}.mmd | Not covered. Borrow notation only (states, transition labels, initial/final, composite states); placement via explicit layout managers |
| graphviz dot — SYNTAX/VOCABULARY IDEAS ONLY, no dot import, no autolayout | examples/dot/*.gv | Not covered. Borrow vocabulary only: node shapes (box/diamond/cylinder/note), clusters (grouped box with label), edge styles (solid/dashed/arrow/bidirectional), bezier edge curves. Placement via explicit layout managers or absolute coordinates in the script |
| diagram models: flow / graph / tree / number-line / panels | examples/*.model.json | Partially covered: lmdraw node-edge diagrams, org trees (manual). Missing: shape vocabulary, connector routing hints, lifeline/message helpers, layout managers (pack/grid/place/border/flow/box), number-line, diagram small-multiples. Trees/radials use author-chosen managers (grid/place) instead of hand-computed pixels |
| pseudo-3D `.scene3d` shapes/pages/animation | examples/scene3d/** | Covered — do NOT port: lmmagnum/lmfilament are real 3D (better quality, honest geometry) |
| storyboard -> narrated MP4 (scenes, transitions, keyframes) | examples/*.storyboard.json | Partially covered: lmvideo renders frames/MP4, lmmagnum/lmfilament storyboards level-*.lms. Missing: narration-driven scene timing, captions, crossfade/morph transitions |
| slides (SVG or HTML per slide -> MP4) | examples/slides.*.json | Partially covered: lmvideo video.lms; lmoffice writes PPTX but does not render video |
| `.pres` deck DSL -> MP4 / PPTX / composite lint | examples/presentations/*.pres | Partially covered: lmoffice 5slidedeck.lms (PPTX authoring). Missing: deck DSL, PPTX export from a deck, overlap/off-slide/clipped composite lint |
| compose (lmdoc Markdown -> self-contained HTML; figures, captions, auto-numbering, cross-refs, TOC, footnotes, GFM tables) | examples/compose/*.md | Not covered (nearest: host READMEs, lmoffice docx reports) |
| document export (docx/eml/html/pdf) | docs/export* | Partially covered: lmoffice (docx/xlsx/pptx). PDF not covered |
| keyframes / transcript / ASR reverse pipeline (MP4 -> storyboard) | docs/keyframes-DESIGN*.md | Not covered |
| video-lint (unique-frames-per-scene, audio-gap report) | durable-memory/v3-item5-video-lint.md | Not covered |
| HTML/URL capture | examples/html.anim.slide.html | Not covered (and should stay that way — see section 4) |
| lint engine (per-artifact diagnostics with remedy + alternative) | docs/lmvideodev-intro.md, lint-roadmap.md | Not covered — the single most valuable design idea; see section 3 |
| distill (lint-driven thumbnail remediation) | durable-memory/distill.md | Not covered (adopt after lint exists) |
| `convert pdf` (structural PDF read-out) | durable-memory/pdf-read.md | Not covered |
| `.lmv` shorthand compile | docs/compile* | Not applicable (input sugar; each host already has lmscript) |

## 2. Ranked backlog: 42 example candidates

Placement constraint (applies to every diagram/dashboard/figure candidate below):
mermaid and Graphviz are NOT to be ported — borrow only their syntax/vocabulary, and there
are NO hidden graph-layout engines (nothing computes geometry the author never sees).
What IS in scope: EXPLICIT LAYOUT MANAGERS, Tcl/Tk and Java Swing style — containers
(Frame/Panel) with an author-chosen manager and constraint set:

- `place` — absolute coordinates (the escape hatch, always available)
- `grid` — row/column/span, row/column weights, sticky N/S/E/W
- `pack` — side (top/bottom/left/right), fill, expand
- `border` — north/south/east/west/center
- `flow` — left-to-right wrapping with per-child gap
- `box` — horizontal/vertical stacks with glue and gaps
- maybe a small grid-bag-lite for the one weighted-cell case

plus container padding, inter-child gaps, alignment, and min/max sizes. The author picks
the manager and the constraints; nesting composes (a border-layout body cell holding a
grid of four plots). On top of managers we still want the diagram primitives: a shape
library (box/diamond/cylinder/note), connectors between two anchors with routing hints
(straight/elbow/curve) and edge styles (solid/dashed/arrow/bidirectional), label
placement relative to a connector, and lifeline/message helpers that take coordinates
inside a managed container.

Effort S = one example file with today's API, M = example needs one moderate feature,
L = example needs a major feature. "Source" paths reference example patterns in the predecessor tool.

| # | Source (lmcreator) | Target repo | What the picture shows | Missing API feature | Effort |
|---|---|---|---|---|---|
| 1 | examples/field/roc.mlplot (+ ml-binary-proba.csv) | lmplot (+lmnum) | ROC curve with AUC=0.98 from real probabilities | ROC sweep + trapezoidal AUC computation, diagonal reference line, metric sidecar | M |
| 2 | examples/field/ml-confusion.confusion (+ ml-confusion-multiclass.csv) | lmplot | 3-class random-forest confusion matrix, per-cell counts with black/white contrast text | Labeled-matrix heatmap: cell text, row-normalize, class-order control | M |
| 3 | examples/field/pr.mlplot | lmplot (+lmnum) | Precision-recall curve with average precision | PR sweep + AP computation, prevalence reference | M |
| 4 | examples/field/residual.mlplot (+ ml-regression-pred.csv) | lmnum gallery | Residual scatter vs predicted with y=0 reference | Reference-line helper + R²/RMSE sidecar | S |
| 5 | examples/field/pred_actual.mlplot | lmnum gallery | Predicted-vs-actual scatter with y=x reference | y=x reference line, metric sidecar | S |
| 6 | examples/field/poisson-phi-contour.field | lmplot | 2D potential heatmap with 8 marching-squares contour lines overlaid | Contour lines composited ON a 2D image heatmap (lmplot has both, separately; splot contour needs the surface path) | M |
| 7 | examples/field/cavity-quiver.field | lmplot (+lmfluid data) | Lid-driven cavity: streamfunction heatmap + auto-scaled velocity quiver arrows | Quiver/vector arrows overlaid on a heatmap image (vector.lms draws arrows alone) | M |
| 8 | examples/field/wave-2d-anim.field | lmplot | Animated standing-wave displacement field, 10 fps -> MP4 | Field-with-frame-column -> frame loop -> ffmpeg (today only splot surfaces animate) | M |
| 9 | examples/field/heat-1d-spacetime.field | lmplot | 1D heat equation as x–t spacetime band | Example-level only: rank 1D series into a matrix heatmap | S |
| 10 | examples/field/poisson-abs-error.field | lmfluid | Absolute-error field of a real FEM Poisson solve vs exact | Example-level: |error| heatmap variant of existing poisson.lms | S |
| 11 | examples/charts/{seasonal-decomposition,queue-combo,bars}.mplchart | lmplot | Dashboard: 2x2 grid of plots (decomposition panels + combo + bars) in one figure | Layout managers: grid manager (row/column/span/weights/sticky) + Frame/Panel containers with padding and gaps, plots as managed children | M |
| 12 | examples/presentations/demo.pres (deck chrome), examples/compose/page.md (page header) | lmplot / lmdraw | Composite figure with title bar + body + footer (page chrome around one or more panels) | Border layout manager (north/south/center) + text-block children + min-size constraints | M |
| 13 | examples/charts/outlier.chart | lmplot | Bar chart with one 63,000-commit outlier on a symlog y-scale | Symlog (linear around 0, log beyond threshold) y-axis | M |
| 14 | examples/charts/queue-combo.mplchart | lmplot | Queue length line (left axis) vs agents-busy bars (right axis) | Dual y-axis combo example (x1y2 exists; no combo demo) | S |
| 15 | examples/charts/forecast-ci-band.mplchart | lmplot | Revenue forecast line + shaded 95% CI band | Example-level: fillbetween with alpha (fillbetween.lms has the mechanics) | S |
| 16 | examples/charts/seasonal-decomposition.mplchart | lmplot | 3-panel sharex seasonal decomposition | Grid/row layout manager with shared-x alignment (multiplot today is hand-positioned) | S |
| 17 | examples/charts/bars.chart | lmplot | Annual revenue bars with $0–$300B currency ticks | Example-level: enhanced text + tick formatting | S |
| 18 | examples/charts/daily-signups-date-axis.mplchart | lmplot | 2024 monthly date-axis line chart | Example-level: timefmt date axis | S |
| 19 | examples/charts/queue-reveal-small.mplchartanim, queue-utilization-2series.mplchartanim | lmvideo (Luna Plot layer) | Animated queue-length "reveal" and 2-series demand-vs-staffing tween | Fixed-structure keyframe tweening of plotted series (points must match across keyframes) | M |
| 20 | examples/charts/physim-kepler-energy-conservation-check.mplchart | lmspace | 2-panel sharex energy conservation check, relative deviation | Example-level: deviation panel with % y-axis (layout manager for the 2-stack) | S |
| 21 | examples/mermaid/api-call-chain.mmd (+ login.mmd, retry-timeout.mmd) | lmdraw | Sequence diagram: participants, lifelines, activation bars, sync/async messages | Box/grid layout manager for the participant row + lifeline(x, y0, y1) and message(p1, p2, label, style) helpers taking coordinates inside the container | M |
| 22 | examples/mermaid/order-state.mmd, traffic-light-state.mmd, compare-state-*.mmd | lmdraw | State diagrams: order lifecycle, TCP connection, thermostat, door lock | Shape vocabulary (state rounded-box, initial/final dots) + transition connectors with labels; states placed via grid/place managers | M |
| 23 | examples/dot/pipeline-src.gv, shapes-and-cluster.gv | lmdraw | ETL digraph with cluster subgraph boxes, cylinder/database node, dashed edges — dot's visual vocabulary | Cylinder shape primitive, cluster = labeled group box (a Panel child), dashed/bidirectional edge styles (vocabulary only; NO dot import) | M |
| 24 | examples/dot/shapes-and-cluster.gv, cluster-selfloop-src.gv | lmdraw | Shape vocabulary showcase: box/diamond/cylinder/note, cluster box, self-loop connector | Self-loop connector + the shape library exercised in one tour example | S |
| 25 | examples/tree-diagram.model.json (dark tidy tree, weighted node sizes) | lmdraw | Tidy tree: levels as grid rows, siblings in a flow row, weighted node sizes | Flow manager (equal spacing per row) + grid rows for levels + named anchors — managers replace the hand-computed coordinates; no auto-layout | M |
| 26 | examples/conversion-tree.storyboard.json (+ assets) | lmvideo (Luna) | Narrated radial conversion tree (Joda-Time -> java.time), weighted node reveals, keep-out regions | Radial positions from author-written polar math feeding place()/grid-bag-lite + per-element reveal keyframes + narration-driven timing | L |
| 27 | examples/diagrams/lmmol-frontiers/*.mmd (5 DAGs) | lmbio (or lmgallery) | Frontier-review workflow DAGs (causal inference, PINNs, RAG, ...), author-arranged | Border/grid managers for the canvas regions + shapes + routing-hint connectors + labels | M |
| 28 | examples/diagrams/grepcent/sic-tree.dot | lmfinance | Real SIC finance-sector hierarchy tree | Grid rows + flow children per level + elbow connectors; the lmdraw org-tree pattern expressed with managers | S |
| 29 | examples/diagrams/grepcent/thread-map.mmd | lmfinance | FRED indicators -> theme -> SIC sectors -> companies flowchart, 1740x860 | Large flowchart via grid columns + box manager per column + labeled connectors | M |
| 30 | examples/graph-proof.model.json | lmdraw | 4-node DB precedence cycle proving edge labels clear their lines | Edge-label placement that offsets from its line (small connector/label gap fix) | S |
| 31 | diagram model number-line + panels layouts | lmdraw | Number-line figure and diagram small-multiples (main + margin panels) | Number-line primitive; border manager with main/margin roles (west/center cells) | M |
| 32 | examples/scene3d/label-legibility.scene3d | lmdraw | Labeled box with leader-line callout ("supply crate") | Leader-line callout helper (label + elbow leader + anchor point) | S |
| 33 | examples/scene3d/box-stack.scene | lmdraw | Two boxes stacked via named anchors | Named-anchor placement API (at/of/offset) for groups, composable with managers | S |
| 34 | examples/presentations/demo.pres (+ assets) | lmoffice | 4-slide quarterly-update deck: diagram + chart + thumbnail components | Deck DSL (slide size, positioned components, text blocks) -> PPTX | M |
| 35 | examples/presentations/demo-broken.pres, clipped-fixture.pres | lmoffice | Deliberately broken deck for composite lint (overlap, off-slide, tiny, clipped text) | Composite lint report on slide elements (overlap/off-slide/clipped) — pure geometry, no renderer needed | M |
| 36 | examples/known-good-narrated-deck.storyboard.json | lmvideo | Title + diagram + chart scenes rendered to crisp narrated MP4 | Narration-driven scene timing with OFFLINE synthetic audio only (no TTS API), captions in report | L |
| 37 | examples/compose/page.md (+ dau.chart) | lmoffice (docx) or new HTML-page surface | lmdoc page: prose + chart figure + mermaid figure, captions, auto figure numbers, [Figure @id] cross-refs, TOC | Compose surface: figure directives with caption/id, cross-reference resolution, TOC generation | L |
| 38 | examples/compose/tables.md | lmoffice | GFM table doc with alignment row, empty cells, inline formatting | Example-level: docx table alignment/format coverage | S |
| 39 | examples/compose/footnotes-multiline.md, code-and-footnotes.md | lmoffice | Multi-line footnote definitions, one footnote referenced twice (two back-links), fenced code | Footnote support in docx export (defs + multi-ref back-links) | M |
| 40 | durable-memory/v3-item5-video-lint.md | lmvideo | Report-only video lint: unique-frames-per-scene (luminance fingerprint) + audio-gap detection | Post-encode report: per-scene unique-frame count via ffmpeg scene sampling + silencedetect parse; report, never gate | S |
| 41 | docs/keyframes-DESIGN*.md | lmvideo | Reverse pipeline: MP4 -> estimated translate/scale keyframes -> editable storyboard -> re-render (proven round-trip) | Streaming decode + per-pair transform estimation (integral projections + NCC + scale search) + storyboard export | L |
| 42 | examples/viewbox-fills-frame.model.json | lmvideo (Luna) | 1280x720 scene-flow graph: presentation scenes as nodes with state classes, filling the frame | Storyboard scene-graph view: nodes laid out with a grid/border manager over the video canvas | M |

## 3. The 8 missing FEATURES that unlock the most candidates (ranked)

1. **Lint-as-output on every host.** Machine-readable diagnostics per render, each carrying a
   concrete `remedy` AND a different-lever `alternative`; never silently drop declared input
   (named `*_APPLIED`/`*_IGNORED` diagnostics instead). Unlocks candidates 35, 40 and
   improves every host's agent-friendliness. This is lmcreator's flagship idea ("lint is the
   LLM's vision").
2. **Explicit layout-manager family (Tk/Swing style) — the figure/diagram composition
   layer.** Containers (Frame/Panel) with an author-chosen manager: pack (side/fill/expand),
   grid (row/column/span/weights/sticky), place (absolute), border (north/south/east/west/
   center), flow (wrapping rows), box (horizontal/vertical with glue and gaps), maybe a
   grid-bag-lite; plus padding, gaps, alignment, min/max sizes. Predictable, composable,
   visible in the script — and explicitly NOT a hidden graph-layout engine: the author
   chooses and controls every manager and constraint. Land first in lmdraw (diagram
   arrangement) and lmplot (multiplot/dashboard composition), then in lmvideo's Luna layer
   as slice 2 (after the Plot layer) for multi-panel figures, dashboards, and title-bar +
   body + footer page chrome. Unlocks #11, #12, #16, #20, #21, #22, #25, #27–#29, #31, #42
   and cheapens #26.
3. **Labeled-matrix heatmap primitive in lmplot** (cell text with contrast-aware color,
   row/none normalization, class order). Unlocks #2 and every count-grid figure (migration
   matrices, contingency tables, correlation-labeled grids).
4. **Field overlays in lmplot: contour lines and quiver arrows composited on a 2D heatmap
   image.** Unlocks #6, #7 (and makes #8's frames much more useful). lmplot already has all
   three ingredients; the missing piece is compositing them in one 2D plot.
5. **Diagram vocabulary in lmdraw — mermaid/dot syntax ideas ONLY — composed WITH layout
   managers.** Shape library (box/diamond/cylinder/note/ellipse, initial/final dots);
   connector(anchorA, anchorB, routing: straight/elbow/curve, style: solid/dashed/arrow/
   bidirectional) with label offset placement; cluster = labeled group box (a Panel child);
   lifeline(x, y0, y1) and message(p1, p2, label, style) helpers taking coordinates inside
   a managed container. Unlocks #21–#25, #27–#30, #32, #33. Feature 2 does the placement;
   this does the notation.
6. **Frame/scene timeline primitives in lmvideo (Luna): clip splice + crossfade +
   per-element reveal keyframes.** Unlocks #19, #23, #26 (and feeds #36's narration timing
   and #40's lint report).
7. **Narration/timing model for lmvideo** (scene duration from narration audio, offline
   synthetic audio for tests, caption + onset/duration report.json). Unlocks #26, #36.
   Deliberately WITHOUT the lmsound network dependency — synthetic/silent only.
8. **Compose surface: lmdoc Markdown -> self-contained HTML (and DOCX via lmoffice)** with
   figure directives, captions, auto-numbering, [Figure @id] cross-refs, TOC, footnotes.
   Unlocks #37–#39. Biggest single new surface; start with figure+caption+TOC only.

Also valuable, just below the top 8: the **sidecar metadata contract** (.chartmeta/
.mlplotmeta-style JSON next to every figure: real values, ranges, and every inferred
transform). Unlocks #1–#5 properly and keeps all hosts honest; cheap to add once lint
(#1) exists.

## 4. What lmcreator does that we should NOT copy (and why)

1. **Network TTS narration (lmsound + LMCTL_KEY).** Quota, keys, nondeterminism in the test
   loop. Use offline synthetic audio; keep narration optional. (Never copy the key material.)
2. **Headless-Chrome HTML/CSS capture and WAAPI-seek slides.** Heavy, fragile dependency
   contradicting our one-static-executable model. Our hosts rasterize natively; if HTML
   slides are ever wanted, render from lmscript scene graphs instead.
3. **Pseudo-3D `.scene3d`.** Faceted, no curves, honest ceiling. lmmagnum/lmfilament already
   do real 3D with better quality — porting scene3d would be a downgrade.
4. **Naming debt.** lmcreator still ships `lmvideo`/`LMVIDEO_*` names in CLI, artifacts, and
   env vars years after renaming. Pick one name per repo at birth and enforce it in CI.
5. **Stale provenance docs mixed with live docs.** lmcreator keeps known-stale docs
   "for provenance" and records consumers being misled. Archive stale docs out of the live
   tree with a hard banner.
6. **Shipped silent-drop defects.** `.chart` single-color series, ignored xticks on bars,
   reserved-but-undrawn node text — logged in a backlog instead of fixed. Our rule: a declared
   input that is ignored is a build-time error, not a backlog entry.
7. **Placeholder visuals in a real schema.** The storyboard `screenshot` visual shipped as a
   visible placeholder + warning for a long time; semantic transitions silently degrade to a
   hard cut across HTML endpoints. Either implement a surface or reject the input; never
   render a placeholder as if it were output.
8. **Fixed-structure-only animation without on-surface documentation.** `.mplchartanim` /
   `.scene3danim` tweens require point-for-point identical keyframes; consumers had to learn
   the "reveal via fixed x-array" workaround by consulting. Our frame-loop model (lmplot
   video/, lmvideo) is strictly more general — if a tween spec is added, state the constraint
   where the spec is defined.
9. **Code-reuse-driven output constraints.** Confusion matrix inherited PNG-only output from
   the field rasterizer where the cell-count rationale does not apply. Keep vector output
   paths primary everywhere.
10. **Committed multi-MB `.bin` blobs + `file:`-linked sibling repos.** Six private sibling
    repos wired into one binary with committed native blobs made builds fragile. Our hosts
    vendor source with lockfiles (sdk.lock pattern) instead.
11. **Hidden automatic graph-layout (Graphviz, mermaid auto-placement).** Geometry the
    author never sees adds a heavy dependency, nondeterminism risk, and removes author
    control. The replacement is explicit layout managers (feature 2): Tk/Swing-style
    containers the author chooses and controls. Borrow mermaid/dot NOTATION and vocabulary
    only; never their layout.
