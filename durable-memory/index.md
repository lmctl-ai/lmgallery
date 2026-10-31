# lmgallery durable-memory

Technical documentation, design notes, and operational procedures for `lmgallery`.

| File | Contents |
| --- | --- |
| [README.md](README.md) | Gallery maintenance procedures, composition authoring guide, and catalog format |
| [01-lmcreator-idea-backlog.md](01-lmcreator-idea-backlog.md) | Multi-host composition ideas and backlog |
| [02-readme-health.md](02-readme-health.md) | Cross-repo demo-page health audit, image optimizations, and durable-memory status |
| [03-office-and-video-compositions.md](03-office-and-video-compositions.md) | Compositions 26–33 driving lmvideo and lmoffice, LibreOffice rasterization |
| [04-health-dashboard.md](04-health-dashboard.md) | Ecosystem-wide health dashboard script (`scripts/health.sh`), checks, and `--fix-pins` |
| [04-part2-host-compositions.md](04-part2-host-compositions.md) | Compositions 34–42 (part 2): hosts, pins, and host limits |
| [05-document-as-code.md](05-document-as-code.md) | Compositions 43–50: Markdown reports from computed results through lmoffice, heredocs, and office gotchas |
| [05-closed-source-peer-model.md](05-closed-source-peer-model.md) | Final private/public peer model, licensing obligations, staged-tree workflow, and gated flip process |
| [06-release-cycle.md](06-release-cycle.md) | Central registry-driven release cycle and preserved workflow facts |
| [07-licence-options.md](07-licence-options.md) | Binary licence comparison, owner intent, recommended draft and legal review priorities |
| [08-consolidation-ResearchOpus.md](08-consolidation-ResearchOpus.md) | Consolidating lmdraw/lmimg/lmmagnum/lmfilament into one product on lmvideo (Image/Canvas/Scene/Layout/Timeline): one scene model, own CPU 3D rasterizer, lmcad/lmblender kept separate, phased aliases |
| [08-consolidation-ResearchSol.md](08-consolidation-ResearchSol.md) | Exhaustive 546-declaration feasibility inventory, dependency/licence/size matrix, gallery/URL impact, and CI/release contracts |
| [08-consolidation-ResearchArgon.md](08-consolidation-ResearchArgon.md) | Unified all-in-one model (`Image`/`Scene`/`Timeline`), `lmimg` + 2D + 3D + video schema, component licence matrix, 6 examples, and migration shims |
| [09-lmvideo-backlog.md](09-lmvideo-backlog.md) | Owner-decided lmvideo backlog, acceptance/gallery items, and public lmcad/lmcycles transition plan |
| [10-showcase-benchmark.md](10-showcase-benchmark.md) | 32-scene visual benchmark from Blender Demo Files & three.js Examples (Tiers 1–3, asset licence rules, CPU budgets, and 12 gap items feeding 09) |
| [11-phase-7-2-gallery-migration.md](11-phase-7-2-gallery-migration.md) | Phase 7.2 gallery migration: 29 affected compositions (7 legacy-host ports + 22 lmvideo re-pins) on lmvideo v0.1.36, evidence and kept-picture boundaries |
| [closed-source-pin-inventory.md](closed-source-pin-inventory.md) | Local versioned install/release-tag consumers for the nine in-scope products |
| [closed-source-staging-inventory.md](closed-source-staging-inventory.md) | Staged public-tree SHAs, validation, active-team gates, and source sync status |

## Adding a new composition / example
1. Create `examples/showcase-NN-<name>.lms` using multi-host `_dsl_` blocks (`cli="..." install="github:lmctl-ai/<host>@latest"`).
2. Generate its preview image by running `examples/render-all.sh --only NN` into `images/showcase-NN-<name>.png`.
3. Add the composition to `showcases.json` and the CI autorun matrix in `.github/workflows/ci.yml`.
4. Run `python3 scripts/build-readme.py` to regenerate the root README gallery.
5. Verify `./test.sh` passes all signature, CRC, and size budget checks.

## Releases
Release publication is automatic on pushing a version tag `vX.Y.Z` or on push to `main` when CI workflows succeed.

## Open items
- 2026-10-24 `_dsl_` → `_lmcode_` spelling sweep (lmscript 0.2.419): 42 example files converted; 6 lines were left as `_dsl_` on purpose because the sweep tool flagged them ambiguous — prose mentions of the block spelling in `README.md`, `durable-memory/README.md`, `durable-memory/index.md` (this file), `durable-memory/03-office-and-video-compositions.md`, and a nested `p = _dsl_ cli="lmvideo" ...` block built inside a string literal in `examples/02-finance-cashflows-draw.lms` (lines 40 and 60 area). Both spellings remain accepted by the compiler, so nothing is broken; revisit only if the old spelling is ever dropped.
- `lmscript --check` on `examples/07-enzyme-response.lms` and `examples/40-bio-predator-prey-report.lms` needs an `lmbio` build that supports `--dsl-schema --json`; the released `~/.local/bin/lmbio` does not (pre-existing, unrelated to the spelling change). A schema-capable binary exists at `/home/mma/repos/dsl/lmbio/build/lmbio`.
