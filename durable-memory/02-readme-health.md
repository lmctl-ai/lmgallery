# README Health and Demo Page Audit

Date: 2026-10-24
Auditor: Gemini Flash (part-time worker)

## Overview
Comprehensive audit of demo-page health across all 31 `lmctl-ai` repositories (30 under `/home/mma/repos/dsl/lm*` and `/home/mma/repos/lmctlhq/lmvideo`).

## Audit Results

1. **Image References & Integrity**:
   - All referenced images (`![]()` and `<img src>`) exist as committed files across all 31 repositories.
   - Zero dead local image links.
   - Image recompression: `lmfilament/docs/images/texturedquad.png` (originally 1,149 KB) recompressed losslessly with PIL `optimize=True, compress_level=9` to 783 KB (saved 374 KB bit-identically).
   - Legitimate oversized multi-frame animation/simulation GIFs preserved:
     - `lmplot`: `docs/images/quantum_packet.gif` (960 KB) — quantum wave packet dispersion animation.
     - `lmweather`: `docs/images/rh_anim.gif` (926 KB), `docs/images/jet_rollup_anim.gif` (903 KB), `docs/images/kelvin_anim.gif` (650 KB) — atmospheric circulation and vortex simulations.
     - `lmfluid`: `docs/images/cylinder_wake.gif` (880 KB) — Navier-Stokes von Kármán vortex street simulation.
     - `lmmolecule`: `docs/images/argon-melt.gif` (812 KB) — molecular dynamics phase change animation.
     - `lmblender`: `docs/images/level-3-hands-off-lead.gif` (611 KB) — Blender Cycles procedural animation.

2. **Autorun URLs**:
   - 736 `lmctl autorun https://raw.githubusercontent.com/...` URLs audited across all READMEs.
   - 100% of autorun URLs resolve to committed files on default branch `main`.
   - Examples run cleanly when executed against released/built hosts. Note: `lmbio` requires local build on `PATH` over older system installation; `lmvideo/examples/terminal-shot.lms` requires three CLI arguments (`IN OUT TITLE`).

3. **SDK Naming, Dead Links, Badges, and Licenses**:
   - Stale names (`cpp-dsl-sdk`, `rust-dsl-sdk`): 0 occurrences found in any README.
   - Relative links `[text](path)`: All resolve to existing repository files/directories.
   - Workflow badges: All reference active GitHub Actions workflow definitions in `.github/workflows/`.
   - License statements: All match repository `LICENSE` files (MIT, Apache-2.0, MPL-2.0, GPL-3.0).

4. **Gallery Placement & First-Screen Visibility**:
   - All 31 repositories feature images within the first screen (all first images at or above line 43).
   - Galleries repositioned above prose and code blocks in: `lmcode-cpp` (moved to L30), `lmcode-go` (moved to L24), `lmcode-csharp` (moved to L16), `lmproxy` (moved to L17), `lmssh` (moved to L23), and `lmssl` (moved to L27).
