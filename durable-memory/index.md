# lmgallery durable-memory

Technical documentation, design notes, and operational procedures for `lmgallery`.

| File | Contents |
| --- | --- |
| [README.md](README.md) | Gallery maintenance procedures, composition authoring guide, and catalog format |
| [01-lmcreator-idea-backlog.md](01-lmcreator-idea-backlog.md) | Multi-host composition ideas and backlog |
| [02-readme-health.md](02-readme-health.md) | Cross-repo demo-page health audit, image optimizations, and durable-memory status |

## Adding a new composition / example
1. Create `examples/showcase-NN-<name>.lms` using multi-host `_dsl_` blocks (`cli="..." install="github:lmctl-ai/<host>@latest"`).
2. Generate its preview image by running `examples/render-all.sh --only NN` into `images/showcase-NN-<name>.png`.
3. Add the composition to `showcases.json` and the CI autorun matrix in `.github/workflows/ci.yml`.
4. Run `python3 scripts/build-readme.py` to regenerate the root README gallery.
5. Verify `./test.sh` passes all signature, CRC, and size budget checks.

## Releases
Release publication is automatic on pushing a version tag `vX.Y.Z` or on push to `main` when CI workflows succeed.
