# lmvideo implementation backlog and open external products

Status: implementation/publication **plan only**, following the owner decisions.
This note supersedes the name candidates and fixed alias deadlines in the three
[08 consolidation notes](08-consolidation-ResearchSol.md). It changes no product
code, repository visibility, repository name, release or licence grant.

## Decisions and product boundaries

- **lmvideo is the product name and implementation focus.** One executable, one
  canonical authoring schema and one model: Image/Frame, Canvas, Scene, Layout,
  Timeline. No separately branded draw/img/Magnum/Filament modes or schema bundles.
- **lmcad** remains an external exact OCCT B-Rep product, suitable for public open
  source. It exports geometry; it is not linked into the closed lmvideo core.
- **lmcycles** is the new name for the reduced lmblender render engine. It takes
  a resolved scene job and returns rendered frames; it does not expose modelling,
  drawing or a parallel authoring/timeline DSL. It is a public open-source product.
- **lmdraw, lmmagnum, lmfilament and lmimg are maintenance-only:** critical fixes,
  no new features. Alias/retirement timing is **deferred to the owner**. There is no
  approved six-release, three-month or two-release deadline. Existing pins, raw
  example URLs and working downloads stay available while migration is incomplete.
- lmvideo keeps its private-source/public-demo-release peer arrangement. lmcad and
  lmcycles instead end with **one canonical public source repo each, containing
  CI and releases, and no active private source/build twin**. Other products are
  outside this change. lmblender already has this shape: `lmctl-ai/lmblender` is
  the only repo (`lmctlhq/lmblender` redirects to it), with its own `ci.yml`,
  `platforms.yml` and releases (v0.3.138), and no RELEASE_TOKEN or private
  checkout. So the peer-model cutover below applies only to **lmcad**. For
  lmcycles the work is the rename, removing the DSL and adding the render-job
  command.

The closed core's licence gate from [08, owner addition 3](08-consolidation-ResearchSol.md#owner-addition-3--licence-gated-core-and-external-components)
continues to apply: incompatible or unresolved components stay external. ImageMagick
is not inherently excluded: the currently pinned delegate-disabled permissive
build must pass the same exact-dependency audit as Skia and its codecs. No FFmpeg,
OCCT or GPL Blender helper is silently linked into lmvideo.

## Model and acceptance rules

Image is the shared pixel object, whether decoded, drawn, processed, rendered in
3D or evaluated at a timeline time. A frame adds index/time metadata to an Image;
it is not another backend-specific image class. Canvas edits an Image or records
vectors; Scene renders to Image; Layout composes these; Timeline evaluates them
and feeds one writer. A rasterized 3D viewport inside SVG/PDF remains raster.

First migration baseline: preserve lmimg's mutable fluent Image operations and
explicit `copy()`, RGBA8 editing/statistics and documented sRGB/alpha semantics.
Resolve premultiplied Skia buffers and linear-light 3D buffers at explicit boundaries.
Changing to immutable edits, HDR or colour-managed processing is additional scoped
work, not a claimed transparent migration. ImageMagick handles remain internal.

Every item below is intended as a small independently reviewable change. The table
names a concrete regression/example seed, **not an assertion that the new API exists**.
Prefixes `draw:`, `img:`, `magnum:`, `filament:`, `cad:` and `blender:` refer to the
existing public example files in those repos; new examples live in lmvideo. Keep
original raw URLs live, and update gallery manifests/committed pictures when a source
migration is accepted. Unit tests do not substitute for running the actual scripts.

For each implementation item: schema/compiler/registry parity; warnings-as-errors
build; source-located failure tests where relevant; same-pinned-environment repeat
hashes; a committed picture/caption and empty-directory `lmctl autorun` run. Cross-OS
images use documented tolerances/semantic checks; MP4 hashes require a pinned codec
and metadata policy. Baseline all current lmvideo examples before changing them.

## Phase 0 — baselines and shared contracts

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| 0.1 | Capture public example commits, output dimensions/hashes and current schemas; classify the 618 existing seven-host domain declarations | Inventory hashes agree with actual schemas; all 50 lmgallery compositions retain runnable historical pins; no missing API hidden by totals | Existing gallery 02, 14, 26, 34, 38 plus lmvideo `layout-workbench.lms` |
| 0.2 | Pin one compiler/SDK/std catalog and define canonical schema evolution/recompile policy | Compiler/registry exact signature match; valid new bytecode executes; old hash fails clearly or is run with its pinned historical binary, never another embedded registry | lmvideo `image.lms`, `quarterly-revenue.lms` |
| 0.3 | Define Image storage/alpha/colour/ownership and shared memory accounting | Alpha-zero, semitransparent edges, copy independence, allocation failure and bounded frame retention tests pass | img `blend_modes.lms`, `image_diff_heatmap.lms` |

No feature is added to a maintenance-only host while these baselines are captured.

## Phase P — platform primitives: fonts, assets and the cache (owner addition)

These features are small but used by every other phase. P.1–P.3 can start right after
phase 0, and 1.4 (font import) becomes P.2.

**Facts checked on 2026-10-26:**
- lmvideo today has only `font(float)`, using the one bundled `assets/fonts/DejaVuSans.ttf`
  (Bitstream Vera licence).
- lmctl.com is the public `lmctl-ai/lmctl` repo, deployed to S3 + CloudFront by
  `scripts/deploy*.sh`. Its prefixes are `/lmctl/` docs, `/tools/`, `/skills/`, `/examples/`,
  `/quickrun/`, `/autorun/`, `/templates/` and `/lmprobe/`.
- It serves **no fonts or binary assets** today; `static/` holds only four SVGs. Font hosting is
  therefore a new prefix and a new deploy script in that repo, not existing content.

**Proposed URL scheme.** Immutable and versioned; content-addressed files never change in place.

```
https://lmctl.com/assets/v1/index.json             # catalog: kind, name, version, files[], sha256, bytes, licence SPDX, licence URL, source URL
https://lmctl.com/assets/v1/fonts/<family>/<version>/<file>.ttf
https://lmctl.com/assets/v1/fonts/<family>/<version>/LICENSE.txt
https://lmctl.com/assets/v1/{icons,hdri,luts,textures}/...   # later kinds, same rules
```

- Only licences that permit embedding and redistribution are allowed: OFL-1.1, Apache-2.0,
  UFL-1.0, CC0, MIT and Bitstream Vera.
- Candidate first families:
  - Inter, Noto Sans, Noto Serif, Noto Sans Mono, JetBrains Mono and Source Serif 4 (OFL-1.1);
  - Roboto (Apache-2.0);
  - one Noto CJK subset, gated on size.
- The catalog is generated in CI from the font files plus their licence texts. A file without a
  licence entry fails the deploy.

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| P.1 | Shared asset resolver and cache: `file:`, `https:`, `lmctl:` (catalog name) and bundled; cache at `$XDG_CACHE_HOME/lmvideo/assets/<sha256>`; size caps; `--offline` and `LMVIDEO_OFFLINE` | Same bytes from URL, cache and file; a sha256 mismatch is an error, never silently used; offline with an empty cache fails with a clear message, or uses the declared fallback; redirects only to https; concurrent runs do not corrupt the cache | new lmvideo `asset-cache.lms` (local fixture server in the test; no live network in CI unit tests) |
| P.2 | `font_load(name_or_url_or_path, sha256?)` → `Typeface`, for 2D text, PDF/SVG embedding and video titles; family, weight and style lookup over the catalog; fallback chain ending in bundled DejaVu | Glyph coverage and metrics of a pinned font match its file; a missing glyph falls back and is reported; PDF embeds a subset (checked with `pdffonts`); an offline run with a warm cache is byte-identical to the online one | new lmvideo `font-specimen.lms` (one sheet of catalog families); draw `title-card.lms` migrated |
| P.3 | Font licence tracking: every output records the fonts it used (family, version, sha256, SPDX); `--notices-used` prints them; video and PDF metadata carry them | One output that uses two fonts lists exactly those two with licences; a font without a known licence (user file) is reported as `unknown`, not omitted | `font-specimen.lms` writes `fonts-used.json` beside the PNG |
| P.4 | Lift the publication to lmctl.com: `assets/` tree, catalog generator, licence gate and `deploy-assets.sh` in the `lmctl-ai/lmctl` repo | Catalog validates; every file has sha256 and a licence; uploads use immutable cache headers; old versions stay (never deleted) | the catalog itself, plus a specimen page |
| P.5 | 3D text from any loaded font: glyph outlines via Skia, flattened, holes and winding resolved, triangulated, extruded with optional bevel | Letters with holes (`A B O 8 e`), nested contours and a CJK glyph; watertight check; replaces the 5×7 voxel text of magnum and filament | magnum/filament `text3d` examples migrated; new `logo-extrude.lms` |
| P.6 | Generalise the resolver to images, SVG icons, HDR environment maps, LUTs and meshes (`image_load`, `env_load`, `mesh_load` accept the same URL, catalog and checksum forms) | Each kind loads from file, URL and catalog with the same checksum and offline rules; licence tracking as in P.3 | new `icon-grid.lms` (Lucide ISC / Material Symbols Apache-2.0 subset); a CC0 HDRI in a 3D scene |
| P.7 | Content-addressed render cache for video: per-frame hash of resolved scene state → cached Image; rerendering a changed range reuses the rest | Changing frames 40–60 rerenders only those (counted); a cache hit is byte-identical to a fresh render; bounded disk, LRU | `kepler-orbit` video rerender test |

Also counted as platform primitives, owned by existing items rather than new ones:
- colour management (sRGB/linear tags and ICC embedding in PNG/PDF), item 0.3;
- text shaping and bidi through HarfBuzz/ICU, already linked, verified in P.2 with an Arabic and a
  Hebrew line;
- deterministic seeds for procedural content, 0.2 and 4.5;
- an audio track muxed into video, through the existing external ffmpeg process (lmaudio output
  as input).

## Phase 1 — highest-value lmdraw parity helpers

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| 1.1 | Canvas arrow and polyline helpers using canonical Paint/Path | Horizontal/vertical/zero-length/bent geometry, arrowhead direction and clipping checks; migrate one source with unchanged diagram meaning | draw `arrow-helper.lms`; gallery 05 force diagram |
| 1.2 | Linear axes helper and data-to-pixel mapping | Tick positions, negative ranges, degenerate-range rejection and numeric labels verified independently | draw `chart-bars-lines.lms`, `incline-free-body.lms` |
| 1.3 | Log/semi-log axes and legend layout | Invalid log domains trap; decade ticks and measured legend boxes do not overlap | draw `kleiber-allometry.lms`, `rc-lowpass.lms` |
| 1.4 | Import SVG and map the retained attribute subset actually used by diagrams (font loading is P.2) | Font metrics/glyph coverage, group transforms, inherited attributes and SVG viewBox cases compared; unsupported attributes named explicitly | draw `title-card.lms`, `node-tour.lms`, `render-assets.lms` |
| 1.5 | Structured lmdraw source migration to the same canonical schema | All 38 public draw example files execute from empty dirs; nested generated source is rewritten structurally; reviewed visual deltas recorded | draw `etl-pipeline.lms`; gallery 02, 05, 11, 13 |

Do not estimate complete parity as five added methods: the old schema has 46
method declarations and arbitrary SVG-style state. Reuse current lmvideo diagram
work; retain an internal compatibility renderer only where measured parity needs it,
without exposing a second host schema.

## Phase 2 — Image and lmimg processing on every frame

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| 2.1 | Enrich the common Image and connect decode/create, Canvas snapshot and writer paths | A decoded Image and a drawn snapshot accept the same pixel/width/height/copy/save calls; no file round trip required | lmvideo `image.lms`, img `before_after_panels.lms` |
| 2.2 | Resize/crop/flip, then rotation as a separate reviewable patch | Exact dimensions and edge pixels; aspect policy explicit; preserve legacy non-right-angle rotation extent or document accepted change | img `batch_resize.lms`, `watermark_tiled.lms` |
| 2.3 | Levels/curves/HSL/channel-mix operations | Known pixel oracles, 8-bit rounding, copy independence and masked-alpha tests | img `levels_lab.lms`, `gradient_studio.lms` |
| 2.4 | Blur/sharpen/unsharp/edges | Premultiplied alpha blur does not halo; sharpen/edge alpha policy and parameter errors match documented contracts | img `blur_reveal.lms`, `edge_map.lms`, `procedural_photo.lms` |
| 2.5 | Image composite and layers/masks with one Layout bridge | Ten existing blend modes, offsets and opacity checked; changing a source after snapshot does not alter finished output | img `blend_modes.lms`, `graduated_nd_layers.lms` |
| 2.6 | Statistics, histogram, PSNR and global-window SSIM | Independently computed small-image values, equal-dimension errors and identical-image infinite PSNR; no silent metric redefinition | img `image_diff_heatmap.lms`, `histogram_equalize_plot.lms` |
| 2.7 | LUT/CLUT, threshold/equalize/morphology, then perspective/lens and healing-lite in separate patches | Per-family pixel oracles and limits; do not substitute a similarly named Skia filter for a different algorithm | img `color_grade_lut.lms`, `document_scan_cleanup.lms`, `perspective_whiteboard.lms`, `portrait_retouch.lms` |
| 2.8 | Contact sheets and variable-duration animation move to Layout/Timeline | Same Image input works as a sheet cell or animation frame; GIF centisecond delays and first-frame decode semantics tested | img `sprite_sheet.lms`, `contact_sheet_shoot.lms`; gallery 14 and 34 |
| 2.9 | Explicit decode/encode capability inventory and conversion | Round-trip supported PNG/JPEG/TIFF/WebP/GIF/BMP/PNM fixtures; restricted delegates rejected or external; no GPL/Ghostscript auto-discovery | img `batch_resize.lms`; new lmvideo `image-format-roundtrip.lms` |

For 2.7, accept one operation family at a time; it is an ordered queue, not one giant
change. TIFF and advanced editing may initially retain the vetted ImageMagick engine
behind Image. Processing must also work on the fresh Images returned in phase 3.

## Phase 3 — CPU 3D rasterizer and scene3d

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| 3.1 | Canonical Scene/Mesh/Node transforms, camera and primitive mesh builders | Winding, normals, bounds, hierarchy, units, Y-up/degrees/vertical FOV and invalid geometry verified; dependency closure audited | magnum `primitives.lms`, `primitives-scene-graph.lms` |
| 3.2 | Opaque CPU triangle rasterization and depth/clipping | Analytic overlapping triangles, near-plane clipping, culling and visibility tests pass; no GPU/display required | magnum `triangle.lms`, `depthtesting.lms` |
| 3.3 | Scene render -> Image and Canvas/Layout viewport composition | The same render can be resized, blurred, measured, drawn in a panel and written without a second image type; alpha edges match composition rules | new lmvideo `molecule-image-pipeline.lms`, based on `ball-stick.lms` |
| 3.4 | Retained scene mutation over the Timeline frame clock | Repeated/seeked frame evaluation agrees with sequential evaluation; bounded RSS and cancellation; measure representative 720p frame times | magnum `animated-gif.lms`, `saturn-rings.lms`; gallery 38 product slide |

Baseline before setting budgets (released hosts, linux-x64, the same `shadows` scene,
900×560, whole `lmscript` run): lmmagnum 0.21 s / 80 MB max RSS; lmfilament 4.07 s /
125 MB. Proposed gate for 3.4/4.3: the unified renderer is no slower than 1.5× the
lmmagnum figure on that scene. The 720p video budget is set after 3.4 measures it.

Use one own CPU renderer; selectively reuse audited math/geometry and preview work.
Removing Magnum or Filament helpers is a measured build task, not a zero-dependency
claim based on source line counts. Keep performance results by scene/triangle count,
resolution, supersampling, platform and revision; set budgets after baselining.

## Phase 4 — material/shadow/texture quality

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| 4.1 | Define supported metallic/roughness material and directional/point lights | Reference BRDF/energy/range cases; distinguish supported preview shading from GI/refraction; material snapshots/instances explicit | magnum `pbr-spheres.lms`, filament `hellopbr.lms` |
| 4.2 | Image textures, UV origin, wrap/filter/repeat and mipmaps | A processed Image can be a texture; oriented checker tests, sampling edge cases and mip selection checked | magnum `texture-modes.lms`, `textured-triangle.lms` |
| 4.3 | Shadow map, bias/PCF and supersampling; transparent pass separately | Contact/acne/peter-panning controls; repeat output; documented sorted-alpha limitations and no false order-independent transparency claim | magnum `shadows.lms`, filament `shadowtest.lms` |
| 4.4 | 3D projection anchors for 2D text/callouts | Offscreen/behind-camera/occluded anchors and viewport changes tested; reuse Canvas typography, not a second bitmap text engine | new lmvideo `molecule-callouts.lms`, based on `caffeine-molecule.lms` |
| 4.5 | Procedural texture graph compiled to images: checker, gradient, noise (value/Perlin/Worley, seeded), bricks, stripes, ramp, plus Image inputs (any phase 2 Image) combined by math nodes | Each generator matches an analytic or pinned-hash oracle at a fixed seed; tileable outputs wrap seamlessly (edge-difference check); resolution-independent definition, baked at a requested size | filament `texture_checker` examples; new lmvideo `material-swatches.lms` |
| 4.6 | Material compiler: `material(...)` description (base colour, metallic, roughness, normal or height, AO, emissive, opacity, each a constant, Image or texture graph) compiled into a packed asset with mips: `albedo` RGBA, `orm` (glTF occlusion/roughness/metallic packing), `normal` (from height when needed), `emissive`; `Material.save(path)` writes a `.lmmat` directory (`material.json` + PNGs + sha256) and `material_load` reads it back | Round trip save → load gives identical rasterizer output; the ORM packing matches the glTF spec; the height → normal conversion is checked on an analytic bump; mips are box-filtered in linear light; the CPU rasterizer samples all maps (fixing filament's albedo-only preview) | filament `hellopbr.lms`, `texture` examples migrated; new `material-library.lms` (sphere grid of saved materials) |
| 4.7 | Export compiled materials to glTF (`pbrMetallicRoughness`, `normalTexture`, `occlusionTexture`, `emissiveTexture`, `KHR_materials_emissive_strength`, `KHR_texture_transform`) for lmcycles and outside tools | The exported GLB passes the Khronos glTF validator; lmcycles renders the same material with base colour and roughness visibly consistent with the CPU preview (SSIM on a matte reference; glossy parts are compared by eye, as Cycles adds GI); lmblender's existing importer reads it | new `material-handoff.lms` (CPU preview vs lmcycles final, side by side) |

Filament compatibility: `material_file("*.mat")` and Filament `.filamat` packages are GPU shader
programs. The CPU rasterizer cannot execute them, and lmvideo does not compile them. The new
compiler covers the *texturing and material parameter* role. Scripts that need real Filament shader
packages stay on the pinned lmfilament release (maintenance only), as already stated in phase 7.

## Phase 5 — geometry and scene handoff

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| 5.1 | OBJ import/export with a declared subset | Round-trip geometry/normals/UVs, triangulation, relative textures and malformed input; units/material omissions explicit | cad `plate-with-holes.lms` -> new lmvideo `cad-preview.lms` |
| 5.2 | Binary/ASCII STL import/export | Independent bounds/triangle/normal tests; mm-to-world scale explicit; B-Rep volumes/topology not claimed preserved by tessellation | cad `box-stl.lms`, `heat-sink.lms` -> new lmvideo `cad-turntable.lms` |
| 5.3 | glTF 2.0 GLB meshes/materials/camera and punctual-light profile | Validate exported GLB; known asset round trips; required unsupported extensions fail before rendering; missing buffers/textures report paths | blender `gltf-import.lms`, `glb-import.lms` as asset fixtures, not future authoring APIs |
| 5.4 | Stable IDs, asset hashes and versioned render-job sidecar | Export the same canonical Scene to CPU and external job with matching transforms/camera/material states; test area-light/environment and animated-property sidecars | new lmvideo `scene-roundtrip.lms`, Cornell-box fixture |

lmcad already exports OBJ/STL, not glTF/STEP/IGES in its present schema. lmvideo
imports its mesh then owns the GLB export. Do not gate useful CAD composition on
adding an unrelated CAD exporter. glTF core animation does not generically encode
animated camera/light/material properties; the job sidecar carries resolved states.

## Phase 6 — lmcycles render engine and call from lmvideo

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| 6.1 | Freeze version-1 capabilities/job/result schemas and frame/colour contracts | JSON schema fixtures accept/reject independently; required feature negotiation, status codes, atomic outputs and cancellation specified | Cornell-box job plus missing/unsupported-backend fixtures |
| 6.2 | Reduce lmblender into `lmcycles render --job DIR` | Fresh public-source build renders a fixed GLB job to PNG; no modelling/drawing DSL in the new command; source/notices audit matches the binary | Migrated blender `cornell-box.lms`, `denoise-quality.lms` rendered through lmvideo |
| 6.3 | One renderer selection seam in lmvideo (`raster` or external `cycles`) | `cycles` starts argv without a shell; missing binary/timeouts/unsupported job fail clearly; returned frame is an Image and receives 2D overlays/filters | new lmvideo `cycles-product-still.lms`, based on glass/metal fixtures |
| 6.4 | Batch resolved frames, geometry reuse and optional passes | Compare batch versus single-frame states; bounded memory, correct indices/seed, cancellation and partial results; EXR only with agreed precision/colour support | Migrated blender `animation-visibility-optics.lms`, `denoise-quality.lms` with an explicit pass request |
| 6.5 | Finish one multi-host CAD -> lmvideo -> lmcycles gallery story | Actual lmcad geometry handoff, CPU preview, final Cycles Image, Canvas labels and Timeline movie all execute from an empty directory | New lmgallery `cad-final-render.lms` plus committed CPU/final comparison picture |

The backend receives **data**, not Python, arbitrary commands or a second modelling
program: `scene.glb`, referenced assets, versioned `job.json`, per-frame resolved
states and an output manifest. Keep Cycles/Embree/OIDN, rendering settings, BSDF
translation, image/pass output and one session per job. Drop mesh construction,
diagrams, layout, editing, fitted-camera authoring and independent keyframe/easing
logic. Existing GPL source/compliance duties remain with the external engine.

### Parallel track — lmcycles can start now

6.1 and 6.2 do not depend on phases 1–5. lmblender already imports glTF 2.0
(meshes, node transforms, metallic/roughness, external textures) and renders
Cornell-box fixtures, and its repo is public with working CI. Version 1 of the job
format can be frozen against hand-written GLB plus `job.json` fixtures, and
`lmcycles render --job` can ship while lmvideo phases 1–4 proceed. Only 6.3–6.5
wait for 5.3/5.4. This puts the external engine on its own public release cadence
without blocking lmvideo.

## Phase 7 — migrations and release gates

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| 7.1 | Structured source migrations and diagnostics, one old API family per change | Review actual argument/unit/type transformations; all new aliases discover exactly the same schema; no claim that renaming a binary fixes old bytecode hashes | draw `etl-pipeline.lms`, img `pipeline_diagram.lms`, magnum `model-viewer.lms` |
| 7.2 | Migrate public manifests/autorun sources and retain old pins | All 50 gallery compositions execute; 31 currently affected compositions produce their declared outputs; raw URLs and historical tags still install | Existing galleries 02/05/11/13, 14/34, 38 and 22 lmvideo compositions |
| 7.3 | Stage/release lmvideo with the unified link closure and public examples | Linux x64/arm64 minimum staged checksums, version/schema, notice audit and fresh-cache install; desktop platform changes explicitly approved, not silently removed | lmvideo image, image-processing, CPU scene and optional-Cycles smoke examples |

Retirement/alias deadlines are not acceptance criteria yet. Maintain old host names
minimally for critical fixes until the owner supplies timing. No new features are
backported. Keep unsupported legacy Filament material-package operations on their
old pinned release/external tool; do not fabricate successful compiled packages.

## Open-source licensing: lmcad and lmcycles

Licences apply to exact files and link closures. Opening a wrapper does not relicense
its dependencies or remove static-link source/relink requirements.

| Public repo / component | Recommended source licence | Binary/distribution facts and acceptance |
|---|---|---|
| **lmcad original wrapper code** | **Keep MIT**, matching current authored source. No need to switch original code to Apache-2.0 just because it links OCCT. Keep Apache-licensed reference examples and their notices separately identified. | OCCT is LGPL-2.1 with its Open CASCADE exception. Publish exact OCCT source/patches/build flags, app link objects or sufficient reproducible relink materials, instructions and required runtime notices for each architecture. An original MIT wrapper is compatible with these obligations; OCCT-derived modifications retain the required library licence. |
| **lmcycles original wrapper/job code** | **Keep existing per-file MIT** and use MIT for newly authored wrapper code; preserve attribution. Package root/README must clearly describe the actual selected distribution licence, not imply every bundled input is MIT. | For the current audited Blender-derived closure, keep **GPL-3.0-or-later** as the combined package/binary licence, with MIT original-file notices and Apache dependency notices retained. Public GPL is acceptable for this external product; removing its authoring DSL alone does not make the link closure permissive. |
| **Standalone Cycles** | Upstream **Apache-2.0**; retain its licence/NOTICE and mark patches | Confirmed by [standalone Cycles LICENSE](https://github.com/blender/cycles/blob/main/LICENSE) and the [Cycles source SPDX header](https://github.com/blender/blender/blob/main/intern/cycles/kernel/types.h). It is not intrinsically the full Blender GPL application. |
| **Current lmblender GPL inputs** | Preserve GPL terms; do not relabel as Apache or MIT | Existing audit names `bf_intern_sky`, `bf_intern_libc_compat`, `bf_intern_guardedalloc`, related intern support and `cpp/view_luts.h`. [Blender guardedalloc SPDX](https://github.com/blender/blender/blob/main/intern/guardedalloc/MEM_guardedalloc.h) is GPL-2.0-or-later. Existing notice selects GPL-3.0-or-later for the combined build. |
| **Possible later permissive-only lmcycles build** | Original MIT wrapper + standalone Cycles Apache-2.0 and an entirely audited compatible dependency closure | Remove/replace every GPL helper and LUT, inspect the actual link map and embedded assets, and reproduce the render tests. Only then advertise a permissive combined build. This is **not** the critical path for an external public GPL engine, and does not justify moving Cycles into closed lmvideo. |

[OCCT's LGPL text](https://github.com/Open-Cascade-SAS/OCCT/blob/master/LICENSE_LGPL_21.txt)
and [header-material exception](https://github.com/Open-Cascade-SAS/OCCT/blob/master/OCCT_LGPL_EXCEPTION.txt)
remain authoritative. The current lmcad audit pins OCCT **8.0.1**, not the older 7.8
assumption in an early design draft. Its source already describes architecture-specific
link-object archives and a relinking recipe. Publishing a GitHub source tree or its
automatic source ZIP alone does not prove that the exact released static executable
can be rebuilt/relinked with modified OCCT or libc. Test that operation explicitly.

Historical root LICENSE files, original-file licences and release asset licences must
remain distinguishable. Do not retroactively replace old MIT/GPL release grants or
rename a GPL-derived LUT into the MIT source area. No need to seek new licence terms
from contributors when preserving their original MIT/GPL/Apache notices and scope.

## Public history and the single-repo transition

### History to keep

- Keep the existing public lmcad repository identity, commits, tags, immutable
  releases/assets/checksums, Issues and raw example paths. Publish audited source
  **on top of** its current public main; do not repeat the earlier orphan/reset flip.
- Preserve the existing public lmblender source history, tags, source archives,
  released binaries and attribution when moving the product name to lmcycles.
  Historical commits can retain the old name/API; current main/README describe the
  render-only product. A rename does not require rewriting history.
- Inspect all candidate private lmcad history before publication: credentials,
  unrelated private products/data, third-party provenance, licences and obsolete
  publisher secrets/configuration. If the full relevant history is safe, merge the
  audited source history into public main without replacing existing history;
  explicitly namespace conflicting tag names. Never mirror all private refs blindly.
- If a private history cannot safely become public, publish a reviewed source
  snapshot commit plus AUTHORS/provenance/build records; retain its full audit
  backup offline. Do not publish secret-bearing history to preserve aesthetics.
  Every newly published source file still needs a valid licence/provenance record.

### Replace the peer-repo mechanics

| Today | Planned state for lmcad/lmcycles |
|---|---|
| Private implementation builds, public peer holds content/releases | One public source repo is authoritative for code, docs, images, examples, CI and releases |
| Private job checks out a separate public peer's content SHA | Public CI tests the source/examples from the same commit; external scene fixtures are pinned |
| Cross-repo `RELEASE_TOKEN` publishes to public peer | Same-repo release job uses appropriately scoped `GITHUB_TOKEN`; PR/build jobs never receive publish credentials |
| `scripts/closed-source/` generates the private/public split and publisher | Remove these two products from split/flip and private-publisher inventories after verified cutover; keep lmvideo and unrelated products unchanged |
| Release registry points to private workflow plus public target | Point each product's release entry at its public build/stage/promote workflows; remove cross-peer assumptions for these entries |
| Private source/build twin and disabled/budget-blocked Actions | Public standard-runner CI + releases; no active private twin or private Actions dependency after cutover |

The existing orchestrator registry lives in `lmctlhq/lmctl-mono-test/releases.json`.
Its updates are future scoped changes by its maintainer, not performed by this note.
Preserve stage/test/promote semantics; a public source repo does not require automatic
latest promotion on every push. Stamp versions, reject tag collisions and use a new
version boundary if resetting workflow run numbers would collide with old releases.

Public CI acceptance before latest promotion:

1. Pinned dependencies and compiler; Release build, unit/core/catalog/schema checks,
   public example/empty-directory runs, and meaningful per-job conclusions.
2. Linux x64/arm64 staged binaries with exact `<product>-linux-<arch>` names,
   SHA256SUMS and execution/schema checks; preserve existing macOS/Windows release
   assets. New desktop release coverage follows an explicit supported-platform plan.
3. lmcad: rebuild/relink against a modified OCCT fixture from shipped materials;
   lmcycles: source archive/build recipe corresponds to the actual linked closure,
   including GPL/runtime materials where applicable. Source and notices ship with
   binaries, not only in an inaccessible former private repo.
4. lmvideo/lmcad/lmcycles handoff test; bounded backend invocation, capability
   negotiation and missing-backend behaviour; fresh-cache install/checksum check.
5. Public README/image/raw-URL gates; untrusted pull requests run read-only checks.

No private Actions need to be enabled to prepare this documentation or transition.
Standard public runners are the intended CI baseline; large/specialized GPU runners
are a separate cost decision. Do not trigger them as a side effect of a repo rename.

## Naming and lmblender -> lmcycles

The target executable, documentation, install coordinate and new asset prefix are
`lmcycles`, `github:lmctl-ai/lmcycles@<version>`, and `lmcycles-<os>-<arch>[.exe]`.
The top-level example is a render job, not `scene.cube(...)` in a second authoring DSL.

Preferred history-preserving operation is an **owner-performed in-place rename** of
public `lmctl-ai/lmblender` to `lmctl-ai/lmcycles`, retaining Issues, history and
releases. Before it happens, test GitHub API/release/raw redirects and installer asset
selection from old coordinates against the proposed release layout. Existing
`lmblender-*` assets/tags must remain untouched; redirects do not change asset names
or fix old scripts' API assumptions. Do not immediately create a new repo at the old
slug: that can displace the redirect.

If those checks cannot preserve required legacy install/raw paths, the owner may
instead **create public lmcycles**, publish the audited renderer history there,
and retain lmblender as a frozen historical download/source archive. That is a
fallback for continuity, not a second developing product or private twin. Select the
route before changing any repository identity; no creation/rename is done here.

Update executable/banner/CMake/package names, current docs, asset names, install
scripts, health/catalog/release-registry entries, and backend discovery in reviewed
changes. First pin explicit lmcycles versions in handoff tests. Only switch examples
from old `@latest` installs after their source has actually migrated to lmvideo's
Scene plus Cycles selection. Saved old source/bytecode uses pinned old lmblender
binaries; a render-only engine cannot transparently execute its 96-method modelling
DSL. Publish this boundary and a migration guide rather than breaking it silently.

## Ordered cutover steps and actions reserved for the owner

The following is an ordered plan, **not authorization performed by this document**.
No visibility, creation, rename, deletion, Actions setting or release mutation occurs
as part of this task.

| Order | Work and evidence before advancing | Owner action, if required |
|---|---|---|
| O1 | Record source/public SHAs, refs/tags/releases/assets/checksums and raw URLs; back up history and source offers; choose rename versus new-repo fallback | **OWNER:** approve exact publication/history/licence scope and lmcycles identity route |
| O2 | Audit private lmcad source/history and current Cycles link closure; prepare source/licence/CI/README changes as a reviewable branch | **OWNER:** authorize any private source/history becoming public; approve removal of proprietary root terms from future open-source wrapper releases |
| O3 | Prepare and test public-source build workflows and same-repo release permissions; keep old release assets immutable | **OWNER:** approve repository Actions/workflow permission changes where needed; no private Actions enablement |
| O4 | Publish reviewed lmcad source into existing public `lmctl-ai/lmcad` preserving public history, tags and releases | No new repo or visibility change is necessary for this preferred route; if instead changing private repo visibility, **OWNER only**, after the full-history audit |
| O5 | Execute the chosen lmblender -> lmcycles identity operation after URL/install migration checks | **OWNER:** rename public lmblender, or explicitly create public lmcycles for the fallback; reserve the old slug/redirect policy |
| O6 | Build public staged releases with source/notices/relink assets, run clean installs and CAD/Cycles handoff tests; do not reuse old tags | **OWNER:** approve first cutover release/latest promotion and any explicit supported-platform change |
| O7 | Switch release registry, split inventories, install/catalog/health links and README/gallery references; verify no job still reads the private twin | Registry maintainer applies the reviewed changes; **OWNER** approves credential revocation and disabling the old publisher |
| O8 | Stop private-twin development, preserve an offline audited backup and verify public source suffices for a fresh rebuild | **OWNER:** decide final disposition of the existing private lmcad twin (retire/delete only after verification); it is not kept as an active source/build peer |
| O9 | Keep maintenance-only aliases and legacy downloads operational; migrate one authoring example at a time | **OWNER later:** set alias/retirement timing. No deadline or automatic repository deletion is implied now |

### README and gallery deliverables at cutover

- **lmvideo:** the sole authoring entry point and active feature backlog; show a
  processed Image, 2D/3D panel, CPU preview, CAD-imported turntable and optional
  Cycles final render, each with a committed picture and working autorun command.
- **lmcad:** public-source build instructions, exact B-Rep scope versus tessellation,
  MIT/OCCT/runtime licence table, tested relink/source materials, stable OBJ/STL
  handoff example and existing engineering galleries. Do not advertise absent STEP/
  IGES/glTF exporters as existing features.
- **lmcycles:** render-only command/capability/job reference; standalone Cycles versus
  actual combined-build licence explanation; public build/source archive instructions;
  fixed-scene preview/final/denoise/pass comparisons. No new modelling gallery.
- **Legacy lmblender examples:** migrate authoring into lmvideo while preserving raw
  paths or explicit pinned-history links; show which material features need the
  negotiated backend profile. Never delete source offers or GPL release archives.
- **lmdraw/lmimg/lmmagnum/lmfilament:** maintenance-only notice, migration link and
  stable old installs/examples. Critical fixes only; no promised alias deadline.
- **lmgallery:** edit catalog/showcase manifests and regenerate README/attribution;
  update install coordinates only after tested releases exist. Preserve public image
  attribution and source snapshots until deliberately replaced.

## Review amendments (ResearchOpus)

Reviewed against the repos on 2026-10-26. The plan is accepted with these changes,
already folded in above:

- lmblender is already a single public repo; only lmcad needs the peer-model
  cutover (Decisions).
- Measured 3D baseline and a relative performance gate (phase 3).
- lmcycles 6.1/6.2 run as a parallel early track (before phase 7).

Further points:

- **Image semantics.** Phase 2 keeps lmimg's mutable fluent Image with an explicit
  `copy()`. This supersedes the "immutable value" wording in 08-ResearchOpus §3.0.
  Migration fidelity outweighs purity here.
- **Old lmvideo bytecode.** Item 0.2 recompiles from source (the old hash fails
  clearly, or the pinned historical binary runs it). This replaces the
  schema-fingerprint dispatch proposed in 08-ResearchOpus §5 P2 and is consistent
  with "one schema, no modes". It assumes autorun URLs are source, which they are
  (`.lms`).
- **lmcad licence state today.** Public `lmctl-ai/lmcad` holds only README,
  examples, docs and binaries under "Lattice Systems Binary License 1.0; earlier
  releases stay MIT". The private `lmctlhq/lmcad` (143 commits) holds the source,
  with a root MIT LICENSE. Restoring MIT as the public root licence for new
  releases is the owner's licence decision in O2.
- **lmcad static glibc.** Relink duties come from both OCCT and static glibc.
  Consider linking glibc dynamically (≥ 2.35, as lmimg does). The LGPL duties
  would then shrink to OCCT alone, and the relink test in CI step 3 gets simpler.
- **Suggested first merged items:** 0.3 (Image contract), P.1 (asset resolver
  and cache), 1.1 (arrow and polyline) and 6.1 (job schema v1). They are independent, small and unblock the
  most work.

## Review and evidence

ResearchSol authored this plan; ResearchOpus reviewed and amended it (section above). Decisions
above override earlier brainstorm assumptions about renaming lmvideo, fixed alias
windows, private twins for the external wrappers, or keeping a second authoring
surface in lmcycles.

Evidence: [ResearchSol inventory](08-consolidation-ResearchSol.md),
[ResearchOpus architecture](08-consolidation-ResearchOpus.md),
[current peer model](05-closed-source-peer-model.md),
[release-cycle implementation](06-release-cycle.md), lmcad `THIRD_PARTY_NOTICES.md`,
and [lmblender's public link audit](https://github.com/lmctl-ai/lmblender/blob/main/docs/LICENSE_AUDIT.md).
The upstream Cycles/OCCT links above were checked for this plan. Original example
names were checked in the source/public content trees; all new APIs, example names,
workflow changes and identity operations remain proposed work until implemented.
