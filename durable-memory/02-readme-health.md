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
   - Stale names (legacy SDK identifiers): 0 occurrences found in any README.
   - Relative links `[text](path)`: All resolve to existing repository files/directories.
   - Workflow badges: All reference active GitHub Actions workflow definitions in `.github/workflows/`.
   - License statements: All match repository `LICENSE` files (MIT, Apache-2.0, MPL-2.0, GPL-3.0).

4. **Gallery Placement & First-Screen Visibility**:
   - All 31 repositories feature images within the first screen (all first images at or above line 43).
   - Galleries repositioned above prose and code blocks in: `lmcode-cpp` (moved to L30), `lmcode-go` (moved to L24), `lmcode-csharp` (moved to L16), `lmproxy` (moved to L17), `lmssh` (moved to L23), and `lmssl` (moved to L27).

## durable-memory audit

- `lmaudio`: index.md complete; 11 docs indexed; example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmbio`: index.md complete; 10 docs indexed; ODE/SSA benchmarks, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmblender`: index.md complete; 7 docs indexed; Cycles/EEVEE rendering, example & release procedures documented; SDK pinned to lmcode-cpp.
- `lmcad`: index.md complete; 14 docs indexed; OpenCASCADE integration, example & release procedures documented; SDK pinned to lmcode-cpp.
- `lmcell`: index.md complete; 11 docs indexed; next-release-version.md linked; example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmcloud`: index.md complete; 6 docs indexed; OpenTofu/Terraform engine, example & release workflows documented; Go SDK runtime.
- `lmcode-cpp`: index.md complete; 6 docs indexed; 51 conformance vectors, stdlib catalog, and host vendoring documented.
- `lmcode-csharp`: index.md complete; 5 docs indexed; NativeAOT builds, 51 conformance vectors, and SDK sync documented.
- `lmcode-go`: index.md complete; 5 docs indexed; zero-dependency Go runtime, 51 conformance vectors, and SDK sync documented.
- `lmcode-rust`: index.md complete; 6 docs indexed; Rust runtime, stdlib catalog, 51 conformance vectors, and SDK sync documented.
- `lmdraw`: index.md complete; 6 docs indexed; CPU rasterizer, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmfilament`: index.md complete; 9 docs indexed; Google Filament 1.78.1 preview rasterizer, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmfinance`: index.md complete; 11 docs indexed; portable-gallery.md linked; QuantLib models, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmfluid`: index.md complete; 11 docs indexed; next-release-version.md cleaned and linked; Navier-Stokes/LBM models, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmgallery`: index.md complete; 3 docs indexed; gallery catalog and health audit logs documented.
- `lmhtml`: index.md complete; 13 docs indexed; 15-sdk-catalog.md linked; Lexbor HTML5 engine, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmimg`: index.md complete; 11 docs indexed; stb/libspng image processing, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmmagnum`: index.md complete; 7 docs indexed; Magnum engine 3D preview renderer, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmmolecule`: index.md complete; 11 docs indexed; next-release-version.md cleaned and linked; OpenMM 8.2.0 dynamics, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmnum`: index.md complete; 12 docs indexed; autorun-v014.json and release-v014.json linked; Eigen/SUNDIALS solvers, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmoffice`: index.md complete; 8 docs indexed; Open XML Word/Excel/PowerPoint engine, NativeAOT builds, example & release workflows documented; SDK pinned to lmcode-csharp.
- `lmparticle`: index.md complete; 11 docs indexed; next-release-version.md linked; NIST XCOM photon/electron transport, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmphysics`: index.md complete; 11 docs indexed; Project Chrono physics engine, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmplot`: index.md complete; 10 docs indexed; gnuplot 6.0 embedding, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmproxy`: index.md complete; 1 doc indexed; reverse proxy and TLS interception engine, example & release workflows documented; Go SDK runtime.
- `lmshark`: index.md complete; 11 docs indexed; Wireshark/libpcap packet analysis, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmspace`: index.md complete; 11 docs indexed; astrodynamics and orbit propagation, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmssh`: index.md complete; 8 docs indexed; 07-sdk-catalog.md linked; OpenSSH client automation, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmssl`: index.md complete; 6 docs indexed; OpenSSL 3.3.2 cryptographic host, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmvideo`: index.md complete; 9 docs indexed; Skia 2D/video engine, Tk/Swing explicit layout managers, example & release workflows documented; SDK pinned to lmcode-cpp.
- `lmweather`: index.md complete; 11 docs indexed; NWP weather modeling, example & release workflows documented; SDK pinned to lmcode-cpp.

## Ecosystem Health Dashboard Findings (2026-10-24)

Automated audit executed via `scripts/health.sh` covering 33 checkouts:

1. **Clean/Green Status**:
   - 0 CI main failures across all repositories.
   - 0 broken images or broken autorun links.
   - 0 stale identifiers across all READMEs and durable-memory files.
   - 100% of repositories have canonical `durable-memory/index.md` indexing all documentation files.

2. **Open / Non-Actionable External Items**:
   - `lmnum`: Release `v0.1.4` has 5/5 platform binaries published on GitHub Releases, but lacks a separate `SHA256SUMS` text asset (asset digest hashes are present in GitHub release metadata).
   - `lmproxy` and `lmdb`: In-development hosts without published release tags yet (`none`).
   - SDK pins across standalone C++ hosts (`lmaudio`, `lmbio`, `lmblender`, `lmcad`, `lmcell`, `lmdraw`, `lmfinance`, `lmfluid`, `lmimg`, `lmmagnum`, `lmmolecule`, `lmnum`, `lmparticle`, `lmphysics`, `lmweather`, `lmvideo`): vendored single-file `dslvm.hpp` from stable milestone `a876646`; upstream `lmcode-cpp` added std catalog files which require coordinated std integration in those hosts.
