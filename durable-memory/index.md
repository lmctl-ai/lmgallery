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

## Adding a new composition / example
1. Create `examples/showcase-NN-<name>.lms` using multi-host `_dsl_` blocks (`cli="..." install="github:lmctl-ai/<host>@latest"`).
2. Generate its preview image by running `examples/render-all.sh --only NN` into `images/showcase-NN-<name>.png`.
3. Add the composition to `showcases.json` and the CI autorun matrix in `.github/workflows/ci.yml`.
4. Run `python3 scripts/build-readme.py` to regenerate the root README gallery.
5. Verify `./test.sh` passes all signature, CRC, and size budget checks.

## Releases
Release publication is automatic on pushing a version tag `vX.Y.Z` or on push to `main` when CI workflows succeed.

## Open items
- 2026-10-24 `_dsl_` → `_lmcode_` spelling sweep (lmscript 0.2.419): 42 example files converted; 6 lines were left as `_dsl_` on purpose because the sweep tool flagged them ambiguous — prose mentions of the block spelling in `README.md`, `durable-memory/README.md`, `durable-memory/index.md` (this file), `durable-memory/03-office-and-video-compositions.md`, and a nested `p = _dsl_ cli="lmdraw" ...` block built inside a string literal in `examples/02-finance-cashflows-draw.lms` (lines 40 and 60 area). Both spellings remain accepted by the compiler, so nothing is broken; revisit only if the old spelling is ever dropped.
- `lmscript --check` on `examples/07-enzyme-response.lms` and `examples/40-bio-predator-prey-report.lms` needs an `lmbio` build that supports `--dsl-schema --json`; the released `~/.local/bin/lmbio` does not (pre-existing, unrelated to the spelling change). A schema-capable binary exists at `/home/mma/repos/dsl/lmbio/build/lmbio`.
