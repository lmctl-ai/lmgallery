# README Health and Demo Page Audit

Date: 2026-10-24
Auditor: Gemini Flash (part-time worker)

## Overview
Comprehensive audit of demo-page health across all 31 `lmctl-ai` repositories (sibling checkouts under `.../dsl` and `.../lmvideo`).

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

## Post-Sweep Health Audit Findings (2026-10-25)

Comprehensive audit following the `_lmcode_` spelling rollout and `@lmctl-ai/lmctl@0.2.420` compiler upgrade across 39 repositories.

### 1. Compiler Upgrade & Standard Library Integration
- **Compiler Minimum Pin (0.2.420)**: Upgraded compiler pins across CI workflows and scripts from 0.2.419 (or older 0.2.369/0.2.401) to `@lmctl-ai/lmctl@0.2.420`.
- **Implicit Standard Library**: `lmscript 0.2.420` builds the standard library catalog into compiler invocations by default. Schema signature parity tests in hosts comparing their own registrations against compiler schemas (`lmcad`, `lmcell`, `lmdraw`, `lmfluid`, `lmmagnum`) were updated to invoke `lmscript --dsl-signatures <schema> --without-std` so checks test host-declared signatures without tripping on built-in standard library signatures.
- **SDK Parity Updates**: Core SDK runtimes (`lmcode-cpp`, `lmcode-rust`, `lmcode-go`, `lmcode-csharp`) adapted their signature parity suites for the compiler's implicit standard library.
- **Std Migration Status**:
  - `lmnet`: Migrated schema by stripping redundant standard library functions, updated CI pin to 0.2.420, and established `durable-memory/index.md`.
  - `lmaws` and `lmproxy`: Flagged as `std migration pending` (retaining legacy standard function declarations in host schema).
- **New Host Onboarding**:
  - `lmdb`: Published initial binary release `v0.1.1` with 5/5 platforms and `SHA256SUMS`.
  - `lmpdf`: Tracked as in-development host (Rust + Typst backend); unreleased state cleanly handled.
  - `lmcode-java`: Fully integrated and passing conformance checks.

### 2. Gallery & Demo Page Assets
- **Image Alt Attributes**: Added descriptive `alt` text to all gallery screenshot tables across `lmcloud` (20 images), `lmplot` (35 images), `lmfilament` (35 images), `lmcode-cpp` (4 images), `lmcode-rust` (4 images), `lmcode-go` (4 images), and `lmcode-csharp` (4 images).
- **Autorun and Image Links**: 100% of image references and `lmctl autorun` links resolve to committed files on default branch `main`. Zero dead links.

### 3. Block Spelling & Example Health
- `_lmcode_` spelling is standard; legacy `_dsl_` block spelling remains supported by the compiler and is audited at INFO severity (non-blocking) across pending suites (`lmaws`, `lmazure`, `lmcloud`, `lmoffice`).
