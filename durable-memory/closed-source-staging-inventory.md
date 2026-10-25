# Closed-source public staging inventory

Snapshot: 2026-10-25. Public-only trees are staged under `/home/mma/staging/closed-source/<product>-public/` from each recorded `origin/main` SHA. They contain no Git metadata and were not pushed. The current public repositories and releases are intact. The earlier lmaudio transfer was reversed; no public history or release changed. The in-place pilot seeded `lmctlhq/lmaudio` with the full source mirror and generated private CI, enabled Actions, and set the release-token secret. Its publish-test failed during draft cleanup (HTTP 422, missing test tag); all build jobs were skipped, the draft is gone, and the public repo was not rewritten.

| Product | Source SHA | Public files | Raw autorun | Private refs | Secrets | Versioned consumer refs | Local checkout | Public CI at stage | Owner active report |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| lmdraw | 9452958efb8a | 94 | 28/28 | 0 | 0 | 1 | clean, synced | completed/success | no |
| lmvideo | 30494ec4691e | 138 | 41/41 | 0 | 0 | 50 | clean, synced | completed/success | yes, quiesce |
| lmaudio | 56b7a1952ac5 | 73 | 23/23 | 0 | 0 | 2 | clean, synced | completed/success | no |
| lmoffice | aa59d72ea09e | 186 | 90/90 | 0 | 0 | 26 | clean, synced | completed/success | yes, quiesce |
| lmcad | 87cbb33ee71c | 90 | 31/31 | 0 | 0 | 1 | clean, synced | queued/ | no |
| lmmagnum | 41a7d8504826 | 90 | 37/37 | 0 | 0 | 1 | clean, synced | completed/success | no |
| lmfilament | 24a0c3e85133 | 88 | 35/35 | 0 | 0 | 0 | dirty, synced | in_progress/ | lmfilament active |
| lmimg | 49186552658a | 68 | 62/62 | 0 | 0 | 7 | clean, synced | in_progress/ | no |
| lmpdf | 821ebcede14c | 69 | 0/0 | 0 | 0 | 1 | clean, synced | pending/ | yes, quiesce |

## Team/quiescence snapshot

The current `lmctl running` output lists active `lmfilament.lmctl:Lead` and a live lmfilament Researcher. The Meta-Lead separately reports active teams for lmvideo, lmoffice, and lmpdf; these are quiescence-gated, with lmoffice and lmpdf last. lmplot is active but excluded from the nine-product scope. Check all teams again immediately before any future flip.

The lmfilament local checkout was dirty when staged, although its branch matched `origin/main`; its public tree was built from fetched `origin/main`. Product source trees must be clean, pushed, quiesced, and current before any future apply.

## Consumer pins

See [closed-source-pin-inventory.md](closed-source-pin-inventory.md) for grep matches and paths. The staged inventory found versioned consumers for all listed products except lmfilament. Every old `@TAG` pin must be moved to the first new release tag during a separately approved coordinated flip.

## Apply status

The approval file lists lmaudio and the protected `RELEASE_TOKEN` file is available. A transfer-based attempt briefly moved lmaudio to `lmctlhq` and was reversed; its public `main`, `pushed_at`, v0.2.1 release, and assets are unchanged. The first in-place retry stopped before any mutation because the old-name API redirect was mistaken for an existing private target. The new method mirrors source into the empty private scaffold first and resets public refs in place only after its private publish test passes. The first seed run stopped after the Actions-disable PUT returned success but its immediate GET still reported enabled; a later GET showed disabled, so the runner now polls setting reads for propagation. Nine public trees remain staged; lmblender is excluded because its GPL corresponding-source obligation keeps it open source. lmplot, lmphysics, lmgallery, SDK repos, and all other products remain outside scope.
