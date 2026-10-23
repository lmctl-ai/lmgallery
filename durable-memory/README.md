# Gallery maintenance

- `catalog.json` is the 17-host inventory. Its host previews are exact copies of upstream `docs/images/` files, with SHA-256, producing script, attribution, and source commit where available. Read sibling repositories only; never edit them from this project.
- `showcases.json` lists nine original compositions. Each `.lms` binds at least two released hosts with `cli`/`install`, writes its own input data, executes its bytecode, and writes an `images/` PNG. Nothing depends on the checkout working directory.
- Update composition previews with `examples/render-all.sh`. This runs every program in a separate fresh temporary directory and retains execution logs. Use `--only 04` to regenerate one example.
- Regenerate README, attribution and the example index with `python3 scripts/build-readme.py`. CI rejects stale generated documents.
- `./test.sh` validates PNG signatures, CRCs, decoded size, preview size budgets, SHA-256 attribution, cross-host bindings, autorun captions and local links. `--network` also checks published HTTP links; planned upstream repository links are reported as skips, not advertised as verified. Remove the planned status once those repositories are public.
- `./test.sh --urls` is the publication acceptance check: it invokes every public raw URL with `lmctl autorun` from an empty directory. The runner reports retained `results.json` files and per-example logs outside the checkout.
- Scripts are MIT. Host binaries run as separate processes and are not redistributed. Retain the upstream attribution and license notice when refreshing copied artwork.
- Commit as Mike Ma <281311770+mike-lmctl@users.noreply.github.com>, with a model-specific `Co-Authored-By` trailer and the repository's decision-record trailers. Push to main and confirm CI after publication.
