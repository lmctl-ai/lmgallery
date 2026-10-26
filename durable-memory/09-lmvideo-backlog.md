# lmvideo implementation backlog and open external products

Status: implementation/publication **plan only**, following the owner decisions.
This note supersedes the name candidates and fixed alias deadlines in the three
[08 consolidation notes](08-consolidation-ResearchSol.md). It changes no product
code, repository visibility, repository name, release or licence grant.

## Decisions and product boundaries

- **CPU reference only for now:** Skia raster, our 3D rasterizer and Cycles CPU; no GPU implementation or GPU work is scheduled.
- **lmvideo is the product name and implementation focus.** One executable, one
  canonical authoring schema and one model: Image/Frame, Canvas, Scene, Layout,
  Timeline. No separately branded draw/img/Magnum/Filament modes or schema bundles.
- **lmcad** remains an external exact OCCT B-Rep product, suitable for public open
  source. It exports geometry; it is not linked into the closed lmvideo core.
- **Cycles is a built-in render backend of lmvideo (`renderer="cycles"`); there is
  no lmcycles repo** (owner follow-up w75d, analysis in phase 6). Cycles and its
  dependencies are built from pinned upstream sources inside the lmvideo repo,
  after the four GPL Blender helpers are replaced. **lmblender is frozen as a public
  legacy GPL product:** no new features, releases and source offers kept, and its
  authoring examples migrate to lmvideo. Archiving is an owner decision once
  migration is done.
- **Owner addition 2 (w75):** lmblender, lmfilament, lmmagnum, lmimg, lmcad and lmdraw return to
  **public open source as real standalone repos**, not aliases of lmvideo, with minimal maintenance;
  see "Six standalone open-source repos". lmvideo alone keeps the private/public peer model.
- **lmdraw, lmmagnum, lmfilament and lmimg are maintenance-only:** critical fixes,
  no new features. Alias/retirement timing is **deferred to the owner**. There is no
  approved six-release, three-month or two-release deadline. Existing pins, raw
  example URLs and working downloads stay available while migration is incomplete.
- lmvideo keeps its private-source/public-demo-release peer arrangement. lmcad
  instead ends with **one canonical public source repo, containing
  CI and releases, and no active private source/build twin**. Other products are
  outside this change. lmblender already has this shape: `lmctl-ai/lmblender` is
  the only repo (`lmctlhq/lmblender` redirects to it), with its own `ci.yml`,
  `platforms.yml` and releases (v0.3.138), and no RELEASE_TOKEN or private
  checkout. So the peer-model cutover below applies only to **lmcad**; lmblender
  needs no repo operation at all.

The closed core's licence gate from [08, owner addition 3](08-consolidation-ResearchSol.md#owner-addition-3--licence-gated-core-and-external-components)
continues to apply: incompatible or unresolved components stay external. ImageMagick
is not inherently excluded: the currently pinned delegate-disabled permissive
build must pass the same exact-dependency audit as Skia and its codecs. No FFmpeg,
OCCT or GPL Blender helper is silently linked into lmvideo.

**Owner decision: CPU only.** Skia uses its raster backend, the 3D rasterizer runs on the CPU,
and Cycles runs on the CPU. GPU is a possible later upgrade if a real need appears; it is not built
or scheduled.

*Interface note.* Every pixel producer sits behind two internal interfaces that the DSL and schema
never name:
- `Surface`: the 2D target (Skia raster today);
- `Renderer`: the 3D or path-traced engine (`raster` or `cycles` today, selected by
  `renderer=` / quality settings).

A future GPU backend is another implementation of the same interfaces, chosen by a build or runtime
option. It adds no new DSL calls. The CPU output stays the deterministic reference that golden
tests compare against (a GPU path would be gated by SSIM against it). The GPU notes in phase 6 are
background only.

## Model and acceptance rules

**Surface/Renderer interface:** keep backend storage, command submission and render
execution behind internal interfaces returning the same canonical Image/Frame and
using the same scene/material contracts. A later GPU backend must require no DSL
or schema change and must be justified by a real need; none is planned now. Pinned
CPU outputs remain the deterministic reference (same-environment hashes, documented
cross-CPU image tolerances), independent of future backend implementation details.

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
- No font catalog or tracked font files were found; existing homepage binary/video assets do not establish a font service. Font hosting is
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
  - Roboto 2 from its Apache-2.0-licensed repository, pinned by exact bytes (do not assume every later Roboto release has the same licence);
  - one Noto CJK subset, gated on size.
- The catalog is generated in CI from the font files plus their licence texts. A file without a
  licence entry fails the deploy.

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| P.1 | Shared asset resolver and cache: `file:`, `https:`, `lmctl:` (catalog name) and bundled; cache at `$XDG_CACHE_HOME/lmvideo/assets/<sha256>`; size caps; `--offline` and `LMVIDEO_OFFLINE` | Same bytes from URL, cache and file; a sha256 mismatch is an error, never silently used; offline with an empty cache fails with a clear message, or uses the declared fallback; redirects only to https; concurrent runs do not corrupt the cache | new lmvideo `asset-cache.lms` (local fixture server in the test; no live network in CI unit tests) |
| P.2 | `font_load(name_or_url_or_path, sha256?)` → `Typeface`, for 2D text, PDF/SVG embedding and video titles; family, weight and style lookup over the catalog; fallback chain ending in bundled DejaVu | Glyph coverage and metrics of a pinned font match its file; a missing glyph falls back and is reported; PDF embeds a subset (checked with `pdffonts`); an offline run with a warm cache is byte-identical to the online one | new lmvideo `font-specimen.lms` (one sheet of catalog families); draw `title-card.lms` migrated |
| P.3 | Font licence tracking: every output records the fonts it used (family, version, sha256, SPDX); `--notices-used` prints them; video and PDF metadata carry them | One output that uses two fonts lists exactly those two with licences; a font without a known licence (user file) is reported as `unknown`, not omitted | `font-specimen.lms` writes `fonts-used.json` beside the PNG |
| P.4 | Lift the publication to lmctl.com: `assets/` tree, catalog generator, licence gate and `deploy-assets.sh` in the `lmctl-ai/lmctl` repo | Catalog validates; every file has sha256 and a licence; uploads use immutable cache headers; old versions stay (never deleted) | the catalog itself, plus a specimen page |
| P.5 | 3D text from any loaded font: glyph outlines via Skia, flattened, holes and winding resolved, triangulated, extruded with optional bevel | Letters with holes (`A B O 8 e`), nested contours and a CJK glyph; watertight check; replaces the 5×7 voxel text of magnum and filament | magnum/filament `text.lms` examples migrated; new `logo-extrude.lms` |
| P.6 | Generalise the resolver to images, SVG icons, HDR environment maps, LUTs and meshes (`image_load`, `env_load`, `mesh_load` accept the same URL, catalog and checksum forms) | Each kind loads from file, URL and catalog with the same checksum and offline rules; licence tracking as in P.3 | new `icon-grid.lms` (Lucide ISC / Material Symbols Apache-2.0 subset); a CC0 HDRI in a 3D scene |
| P.7 | Content-addressed render cache for video: per-frame hash of resolved scene state → cached Image; rerendering a changed range reuses the rest | Changing frames 40–60 rerenders only those (counted); a cache hit is byte-identical to a fresh render; bounded disk, LRU | `kepler-orbit` video rerender test |

Also counted as platform primitives, owned by existing items rather than new ones:
- colour management (sRGB/linear tags and ICC embedding in PNG/PDF), item 0.3;
- text shaping/bidi verified through the actual selected Skia shaping path in P.2 with Arabic/Hebrew; merely linking HarfBuzz/ICU is not proof that a primitive shaper uses them;
- deterministic seeds for procedural content, 0.2 and 4.5;
- an audio track muxed into video, through the existing external ffmpeg process (lmaudio output
  as input).

### Primitive implementation details and acceptance subitems

The P.F subitems refine P.2/P.3/P.5, P.M refines 4.5–4.7, and P.A refines P.1/P.6/P.7. They are not separate products or duplicate authoring APIs.
These are lmvideo core capabilities, not new features for the frozen sibling hosts.
Implement the common asset resolver early (with 0.3/1.4), font loading before unified
text/3D text, and portable texture/material compilation with phase 4 before finalizing
the phase-5 GLB/backend bridge. One resolver, cache and provenance record serves every
consumer; do not create separate font/image/3D/video download stacks.

### Website source findings and proposed font publication

Inspected public [lmctl-ai/lmctl](https://github.com/lmctl-ai/lmctl) main commit
`3eb6ed805062312f68c756640b27494e057faa77`: `DEPLOY.md`, `docusaurus.config.ts`,
`homepage/assets/style.css`, `src/css/custom.css`, `docs/license.md`,
`scripts/deploy-homepage.sh` and `scripts/tools/static-site.py`, plus the recursive
Git tree. This is the lmctl.com homepage/docs/static-content repository, not the
private compiler monorepo. It currently serves the root homepage, Docusaurus docs
under `/lmctl/`, and separately published `/tools/`, `/examples/`, `/skills/` and
other static prefixes through S3/CloudFront. The current tree contains **no tracked
TTF/OTF/WOFF font assets or font catalog**; homepage CSS uses a system-ui font stack.
Do not infer redistribution permission for installed Segoe UI/Arial/etc from that CSS.
The site's lmctl binary licence page is not a licence for future third-party fonts.

Proposed new, **not-yet-served** URL contract:

- `https://lmctl.com/assets/v1/index.json`: versioned catalog with stable face
  IDs/family aliases, style/weight/variation metadata, font URL, SHA-256, size,
  source/version, copyright, licence identifier, licence-text URL/hash and relevant
  reserved-name/embedding/redistribution conditions.
- `https://lmctl.com/assets/v1/fonts/<family>/<version>/<face>.ttf` (or `.otf`) plus
  version-pinned licence texts with recorded hashes. Prefer raw TTF/OTF for Skia portability; WOFF2
  support is an explicit decoder/build capability, not assumed from web-font usage.
- A future website change must add the font MIME types and managed inventory to
  the actual publisher: its current extension allowlist does not include font
  suffixes. Use exact-prefix asset publishing, immutable caching for version-pinned asset paths,
  revalidation/version pinning for the index, and the existing managed-manifest
  deletion discipline. Check live status, MIME, byte hash and licence links.
  Do not upload fonts or deploy the website as part of this documentation task.

Name resolution uses the pinned catalog's family/face IDs, never an implicit scan
of arbitrary OS fonts. Explicit file/URL sources remain possible. Resolve styles
and axes deterministically; record the resolved face hash in render provenance.
Use approved bundled fonts for an offline fallback and ship their exact licence
texts. A strict/pinned job fails on missing or corrupt required bytes; a requested
fallback policy may select the bundled face and must report which face was used.
A checksum mismatch is not silently accepted as another font. External-font licences
stay separate from the lmvideo binary licence; exact-byte provenance matters more
than a family name. Keep notices with exports where the applicable font terms require
it; embedding a font does not generally relicense an entire document.

### First-class font load backlog

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| P.F1 | Common Font resolver for catalog name, HTTPS URL and local file, returning the same Skia-backed Font used by Canvas and Timeline | Name/URL/file resolving to identical bytes produce equal metrics/glyph IDs; unknown face, unreadable file, invalid font and unsupported axes fail clearly | New lmvideo `font-source-triptych.lms`; draw `title-card.lms` as migration seed |
| P.F2 | Content-addressed font cache, checksum verification, pinned metadata and offline fallback | Cold/warm cache, offline verified hit, missing cache, bad hash, interrupted download and concurrent loads tested; default bundled fallback is recorded and strict mode rejects substitution | New lmvideo `font-offline-poster.lms` with test-local HTTP fixtures and network-disabled rerun |
| P.F3 | Website font catalog/assets and per-face licence ledger, coordinated with the website maintainer | Every catalog entry has matching font/licence hashes and permitted hosting/redistribution; live MIME/URL checks; no system font copied from CSS assumptions | New lmvideo `font-license-specimen.lms` with face/source/licence caption; website catalog example |
| P.F4 | Reuse loaded face/shaped glyph runs for 2D text, 3D outline extrusion and every video frame | Same face/axes and baseline metrics across consumers; holes/winding/flattening and glyph fallback tested; shaping/RTL coverage explicitly tested or reported unsupported | New lmvideo `font-2d-3d-turntable.lms`; magnum `text.lms` and img `poster_text.lms` as seeds |

Font cache blobs can share the generic asset store below; glyph/shape caches also
include face hash, size/axes, shaping configuration and relevant library version.
No per-frame font fetching or duplicate font loading inside the Cycles process.
Extruded geometry/texture-baked text travels as ordinary scene assets; backend text
rendering does not get a separate untracked font-resolution policy.

### First-class texturing/material compilation backlog

Current-source fact: lmfilament `cpp/main.cpp:116–138` parses Filament material
source through `matp::MaterialParser`/`filamat::MaterialBuilder`; `material_file`
reads source text, and `Material.save` writes the resulting package bytes. Its
texture/checker/file/pixel/filter/wrap/repeat operations are useful migration seeds.
Those `.filamat` bytes are Filament shader packages, **not** portable CPU texture/PBR
assets and not a format glTF/Cycles can consume directly.

Carry over the **first-class workflow** into the one lmvideo schema:
`material_file`/source construction -> compile/validate -> Material/texture asset ->
`Material.save` -> reload/reuse -> CPU rendering and GLB export. Use a versioned
renderer-neutral material description/IR and deterministic baking of supported
procedural/image graphs; reuse the canonical Image/filter operations. Keep normal
compilation in the one binary. Apache-licensed Filament parser/compiler pieces may
be reused where useful after a closure audit, but a noop Filament engine is not
required to generate CPU pixels. Do not claim arbitrary view-dependent GLSL can be
baked into an equivalent texture; support a declared subset and diagnose other nodes.

Define the versioned `.lmmat` logical pack in phase 4 (`material.json` plus PNG/mip resources and hashes; an optional single-file archive must preserve the same deterministic payload), containing a manifest, source/IR hash, compiler/profile version, scalar
PBR parameters, texture bindings/samplers, baked image/mip resources, channel/colour
metadata, checksums and source/licence provenance. Require deterministic ordering,
fixed metadata and resource limits. The pack remains renderer-neutral; no GPU shader-payload compiler is scheduled. Distinguish source-file loading
from loading a compiled pack by explicit API/format magic. Legacy `.filamat` gets an
explicit import/conversion capability or clear unsupported-format diagnostic; never
reinterpret its bytes as the new portable pack.

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| P.M1 | `material_file` and source constructor with one typed material/texture IR, validation and compiler diagnostics | File versus equivalent inline source compile to identical IR; missing textures, bad parameters, unsupported graph nodes and source locations tested | Migrate filament `compile-sample-materials.lms`, `material_sandbox.lms`; new lmvideo `material-compiler-workbench.lms` |
| P.M2 | Procedural/image texture compilation using shared Images: checker/gradient/seeded noise, colour transforms, mipmaps and samplers | Same seed/settings reproduce resources; changing an Image or graph input invalidates cache; UV origin/wrap/repeat and sRGB versus linear channels verified | Migrate filament `texture-modes.lms`, `textured-primitives.lms`; img `gradient_studio.lms` |
| P.M3 | Portable `Material.save` pack and loader, reusable by the CPU rasterizer | Byte-identical pack for identical inputs; round-trip render equals direct material; corrupt/version-incompatible pack rejected; one pack reused across instances/frames without recompile | New lmvideo `packed-material-turntable.lms` with a compile-once/offline-reload test |
| P.M4 | Export compiled PBR/textures to standard glTF plus the Cycles material profile | Base colour/emissive sRGB, linear occlusion/roughness/metallic channel packing, tangent-space normals and alpha verified; CPU and Cycles decode the same resource hashes; unsupported material features fail explicitly | New lmvideo `material-cpu-cycles-compare.lms`; blender `material-maps.lms`/`gltf-emission.lms` as asset fixtures |
| P.M5 | Dependency-keyed compiled-material cache and bounded bake scheduling | Changes in source, included file, image hash, profile/compiler, dimensions or seed invalidate results; warm loads avoid recompilation; atomic cache writes and bake-memory limits tested | New lmvideo `material-cache-proof.lms` with cold/warm/modified-input captions |

This addition replaces the earlier plan to leave all material-compilation operations
on a frozen host. The new portable compilation workflow is first-class lmvideo work;
unsupported **legacy binary/shader semantics** may remain on the old external tool
until an explicit converter/profile exists. Avoid a misleading success when a material
only carries uploaded maps that the CPU shader does not actually sample. Track feature
coverage through compile, CPU shading, GLB export and the selected Cycles backend capability profile. This does not undo the newer w75d decision above to keep Cycles in lmvideo after its permissive-only closure gate; glTF remains an interchange format for the same packed material data.

### Other shared platform primitives worth adding

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| P.A1 | Common file/URL/embedded asset loading and content-addressed byte cache for Images/SVG/meshes/fonts/material packs | Same verified asset resolves once across consumers; bounded redirects/download sizes/timeouts, atomic cache writes, path/base-URL rules and offline behaviour tested; no shell command construction | New lmvideo `asset-source-dashboard.lms`, combining loaded Image, SVG and textured Scene |
| P.A2 | Asset dependency graph, provenance and reproducible job lock | Export lists every resolved source/hash/licence, transitive texture/font/material input and backend profile; changing an input invalidates only dependents; clean offline rerender succeeds from the lock/cache | New lmvideo `locked-scene-offline.lms` with an asset/provenance panel |
| P.A3 | Shared decoded-resource pool and async prefetch/cancellation at job boundaries | Bounded Image/font/mesh/mipmap memory, eviction of unused resources, no eviction of live handles, cancellation cleanup and no per-frame network access | New lmvideo `cached-texture-animation.lms`, cold/warm timing and peak-memory assertions |

These items provide useful primitives without adding a second authoring model.
Choose pixel/colour conversion, URI/base-path resolution, capability/error reporting
and temporary-file lifecycle once across image processing, textures, exports and
external render jobs. No website asset, material-pack implementation or new dependency
has been published by this plan amendment.

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

Material compilation is first-class in lmvideo: canonical `material_file` reads the declared
portable material/texture source profile; `Material.save` writes the reusable `.lmmat` pack.
Legacy Filament `.mat` source is a different source language and `.filamat` contains GPU shader
package bytes. The CPU rasterizer cannot execute arbitrary Filament shader programs. Convert the
supported source subset explicitly; unsupported legacy semantics stay on the pinned external
release until a real converter exists. Do not fake compatibility by relabelling package bytes.

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

## Phase 6 — Cycles built into lmvideo

### Owner follow-up w75d: built-in vs flavour vs separate repo

Measured from lmblender v0.3.138, which is the same Cycles + Embree + OIDN + OIIO/OCIO/EXR + TBB
closure plus a small DSL:

| Question | Evidence | Assessment |
|---|---|---|
| Size added to lmvideo (30.1 MB x64 today) | lmblender binaries: linux-x64 124 MB, linux-arm64 91 MB, macOS 85–90 MB, Windows 71 MB | lmvideo becomes roughly 150 MB (x64) and 120 MB (arm64). **Not a blocker** (owner note w75e). |
| Build time / CI cost | lmblender `ci.yml`: about 41 min per run with the dependency-prefix cache; the cold cache build is allowed up to 330 min (`timeout-minutes: 330`) | The one real cost. It is handled by a separate cached SDK job (below), so ordinary lmvideo CI only links. |
| arm64 | lmblender ships linux-arm64 and macOS arm64; OIDN NEON kernels are audited (README THROUGHPUT) | Viable. |
| Windows | lmblender ships windows-x64; lmvideo has no Windows build today | Not a Cycles issue; it is lmvideo's existing platform gap. |
| Dependencies | all permissive after 6.0; static; no OCIO config or Python at runtime | Viable. lmvideo already links ICU, HarfBuzz, libpng and libjpeg-turbo; pin one copy of each shared library (OIIO wants PNG/JPEG/TIFF) and check for duplicate symbols at link time. |
| Startup | a static binary pages in lazily, and the Cycles session, kernels and OIDN are created only on the first `cycles` render. lmblender reports setup/BVH under 1 ms on small scenes | Raster-only runs should not slow down. Gate: `lmvideo --version` and a raster example take at most 1.1× the time of the pre-Cycles binary. |
| Determinism | fixed seed and samples give repeatable output per machine; Embree and OIDN pick ISA-specific kernels | Same-machine reruns are byte-identical; across CPUs compare by SSIM. Same policy as the raster renderer. |

**Recommendation: (a) built in, the default build.** No new repo, and no separate flavour by
default:
- Cycles and its dependencies build from pinned upstream tags in the lmvideo repo
  (`third_party/cycles/`, the lmblender scripts and patches carried over, minus the GPL parts).
- A separate `cycles-sdk` workflow in the same repo produces a cached static prefix per platform.
  It is keyed on pins and patches, like lmblender's `PREFIX_CACHE_VERSION`, and rebuilt only when
  those change.
- The normal lmvideo build downloads that prefix and links.

Option (b), an optional `lmvideo-cycles` build flavour in the same repo, is kept only as a fallback
for a platform where the Cycles build fails, for a real portability reason, never for size. It
would be the same source with `-DLMVIDEO_CYCLES=OFF`, and `renderer="cycles"` reports "not built
in". The interim external process goes away once 6.0 lands.

**Effect on lmblender (c):** freeze it as public legacy. Critical fixes only, no features. Keep its
releases, tags, source archives and GPL source offers (they are owed for released binaries). Its
examples migrate to lmvideo scripts with `renderer="cycles"`. No rename to lmcycles and no new repo.
Archiving is an owner decision after migration.


### Owner question: lmcycles as a new lean repo on standalone Cycles (github.com/blender/cycles)

**Key fact: lmblender already is standalone Cycles, not a Blender build.**
- Its `.github/cycles-flags.txt` says `WITH_BLENDER=OFF WITH_CYCLES_STANDALONE=ON WITH_PYTHON=OFF`.
- The sources are Blender v5.2.2's `intern/cycles`, CPU only, with OSL, LLVM, OpenVDB, OpenSubdiv,
  GPU, USD and Hydra off, and Embree, OIDN and TBB on.
- Its README measures the plain standalone `cycles` ELF at **88.4 MB** on arm64, against 90.9 MB
  for the released lmblender arm64 binary.

The DSL adds about 3 MB. A "lean" repo would therefore save almost nothing in size or build time.
What changes, if the source moves to the standalone `blender/cycles` repository, is the
**licence**.

**Licences in standalone `blender/cycles` (checked on main via the GitHub API, 2026-10-26):**

| Part | Licence | GPL? |
|---|---|---|
| repo `LICENSE`, `src/**` (Cycles) | Apache-2.0 (SPDX headers) | no |
| `third_party/sky` (Hosek–Wilkie, single and multiple scattering) | BSD-3-Clause, Apache-2.0, MIT | no; replaces Blender's GPL `intern/sky` |
| `third_party/libc_compat` | Apache-2.0 | no; replaces Blender's GPL `intern/libc_compat` |
| `util/guarded_allocator` | Apache-2.0; Blender's `MEM_guardedalloc` only `#ifdef WITH_BLENDER_GUARDEDALLOC` (off in standalone) | no |
| **`third_party/atomic/atomic_ops.h` + `intern/*.h`** | jemalloc BSD notice **plus a "GPL LICENSE BLOCK" (GPL-2.0-or-later)**, included by `src/util/atomic.h` | **yes, the only GPL left**. Replace with a small `std::atomic`/compiler-builtin shim of the same functions (our patch, MIT) |
| `third_party/mikktspace`, `cuew`, `hipew` | permissive (zlib-style, Apache-2.0) | no |
| Embree 4, OIDN 2, oneTBB | Apache-2.0 | no |
| OpenImageIO (Apache-2.0 since 2.5; BSD-3 before), OpenColorIO, OpenEXR/Imath | BSD-3 / Apache-2.0 | no |
| OSL, OpenVDB/NanoVDB, OpenSubdiv, Alembic, USD/Hydra (all optional, now OFF) | BSD-3 or Apache-2.0 (OSL, OpenVDB); OpenSubdiv and USD under Pixar's modified Apache-2.0 | no GPL; OSL also needs LLVM (Apache-2.0 + LLVM exception) and adds much build time, so keep it OFF |
| our `cpp/view_luts.h` (Blender OCIO-derived) | treated as GPL | yes: not carried over (see the table below) |

Conclusion: standalone Cycles plus our atomic shim plus no Blender LUT gives a **fully permissive**
closure. Upstream licences change across versions, so CI must check each pinned tag with the SBOM
licence gate in 6.0.

**Build size and time vs lmblender:**
- Size is about the same: 85–125 MB per platform, dominated by multi-ISA Cycles CPU kernels,
  Embree, OIDN weights and OIIO.
- Build time is the same per cold dependency build (hours), or about 40 min cached.
- `make update` in `blender/cycles` can fetch Blender's precompiled dependency libraries for linux
  x64, macOS arm64 and Windows x64/arm64. That cuts the cold build to a large Git LFS download,
  but there is **no linux-arm64 set**, so lmblender's own static dependency build stays needed for
  arm64. Keep one own-build path for all platforms, for reproducibility.

**Scene input: our own glTF importer to the Cycles C++ scene API, not Cycles XML.**
- lmblender's `cpp/gltf_import.hpp` and `cpp/obj_import.hpp` are project-authored (MIT SPDX). They
  already build `Scene`, `Mesh`, `Object`, `ShaderGraph`, camera and lights directly through the
  API, with bounded inputs and structured errors.
- Cycles XML (`app/cycles_xml.cpp`) is the standalone app's test format: unversioned, with no PBR
  importer and no bounds checks.
- Job extensions for Cycles-only features go in `job.json` (subsurface, volume, procedural nodes,
  hair curves, DOF, motion blur).

**What moves to lmvideo** (lmblender never had Blender modifiers, metaballs or geometry nodes; it
only had DSL helpers):

| lmblender DSL helper | Becomes |
|---|---|
| `cube`, `uv_sphere`, `cylinder`, `cone`, `capsule`, `torus`, `plane`, `ring_arc`, `tube_between`, `arrow_between`, `loft`, `checkmark`, `glow_orb` | lmvideo Scene mesh builders (phase 3.1), exported in the glTF |
| `hair_patch`, `hair_sphere`, `strand` | lmvideo curve primitive → job extension `lm_curves` → Cycles native curve geometry (glTF has no hair) |
| `checker/noise/ramp_material`, `bump`, `subsurface`, `volume`, `mix_with*`, `toon_outline` | lmvideo material compiler (4.5–4.7) for baked maps; Cycles-only shading as `job.json` material extensions |
| `label`, `studio_setup`, `fit_camera`, `ground_plane`, `wall_plane_y`, presets | lmvideo Scene and Canvas helpers (labels as 2D overlays on the returned Image) |
| keyframes (camera, lights, materials, visibility), `motion_blur`, `camera_dof` | lmvideo Timeline → per-frame resolved states in the job |

Features Blender has but lmblender never had (modifiers, subdivision, metaballs, curve bevel,
booleans) are new lmvideo work only if wanted:
- subdivision: Cycles with OpenSubdiv ON (Pixar's modified Apache-2.0), or our own Catmull–Clark;
- metaballs: marching cubes in lmvideo;
- booleans: lmcad, or Manifold (Apache-2.0).

**CPU / GPU / denoise:**
- CPU with Embree and OIDN CPU denoise is the default everywhere, and deterministic per machine.
- GPU backends all exist in standalone Cycles and are all OFF: CUDA/OptiX (NVIDIA toolkit to
  build, driver at runtime), HIP (AMD), Metal (Apple Silicon), oneAPI (Intel).
- No GPU platform is prioritized, built or scheduled. Hardware acceleration is only
  a possible later need, hidden behind Surface/Renderer without changing the DSL/schema.
- The OptiX denoiser is NVIDIA-only, so OIDN stays the denoiser.
- **arm64:** Cycles CPU (via sse2neon), Embree 4 and OIDN 2 (NEON) all support it; lmblender
  already ships linux-arm64 and macOS arm64.

**Recommendation: switch the Cycles *source* to standalone `blender/cycles`, but do not create
an lmcycles repo.**
- The switch to standalone is the cheapest way to a permissive closure: one atomic shim instead of
  replacing three Blender subsystems.
- A separate repo adds a product, release train and CI with no size or build-time gain.
- Build Cycles inside lmvideo as recommended above (w75d: `third_party/cycles` pinned to a
  `blender/cycles` tag, plus the cached `cycles-sdk` workflow).
- lmblender then stays **only as a frozen public legacy GPL repo**: releases, tags and source
  offers kept; critical fixes only.

If the owner wants the permissive Cycles build itself to be public open source for others, the
alternative is a build-only public `lmcycles` repo. It would hold scripts, patches, the atomic shim
and CI producing the static prefix and the `render --job` CLI, with no DSL, and lmvideo would
consume its artifacts. That is a valid choice for publishing reasons, not for size. It needs
owner-created repo identity.

**Migration steps:**
1. Pin a `blender/cycles` tag matching Blender 5.2's Cycles. Add the `std::atomic` shim patch. Port
   lmblender's dependency scripts into lmvideo `third_party/cycles/` (6.0).
2. CI SBOM licence gate on the linked closure: no GPL object; `view_luts.h` absent; Standard view
   transform only until a permissive AgX exists.
3. Port the glTF and OBJ importers and the Principled BSDF mapping (MIT) to the in-process job (6.2).
4. Parity: lmblender v0.3.138 vs lmvideo `renderer="cycles"` on its fixture scenes, SSIM ≥ 0.99
   except sky and view transform (6.3).
5. Migrate lmblender examples one family at a time to lmvideo Scene + `renderer="cycles"` (7.1).
6. Freeze lmblender: README notice "legacy; use lmvideo `renderer=\"cycles\"`", critical fixes only.
   Archiving is an owner decision later. **No repo is created or renamed.**

### Cycles in lmvideo: what blocks it and how it is removed

From lmblender `docs/LICENSE_AUDIT.md`, the link closure is:
- Cycles: Apache-2.0;
- Embree, OIDN and oneTBB: Apache-2.0;
- OpenImageIO, OpenColorIO, OpenEXR/Imath and OpenJPH: BSD-family;
- robin-map: MIT;
- plus four GPL items:
  - `bf_intern_sky` (sky model);
  - `bf_intern_guardedalloc` (allocator wrapper, with `intern/atomic`);
  - `bf_intern_libc_compat`;
  - `cpp/view_luts.h` (Filmic/AgX LUTs sampled from Blender's OCIO config).

| Item | Replacement (permissive) |
|---|---|
| `bf_intern_guardedalloc` + atomic | standalone `blender/cycles` builds without guardedalloc; its `third_party/atomic` headers are still GPL, so replace them with our `std::atomic` shim |
| `bf_intern_libc_compat` | standalone `third_party/libc_compat` (Apache-2.0), or drop it with dynamic glibc ≥ 2.35 or musl |
| `bf_intern_sky` | standalone `third_party/sky` (BSD-3/Apache-2.0/MIT); no rewrite needed |
| `view_luts.h` | AgX implemented from its published description, or LUTs generated by a separately licensed OCIO config; until then ship `Standard` (exact sRGB) only. Never move the existing GPL LUT into lmvideo |

With these replaced, the whole closure is permissive and can sit in the closed core,
with notices. The size of Cycles, Embree and OIDN (on the order of 100 MB) is
accepted, per the owner. The remaining real costs:
- **Build time.** Static Cycles, Embree, OIDN, OIIO, OCIO, EXR and TBB take hours cold. The
  `cycles-sdk` workflow in the lmvideo repo caches them as a pinned static prefix, so ordinary
  lmvideo CI only links.
- **Portability.** lmblender already ships Linux, macOS and Windows, so this is no blocker; lmvideo
  itself lacks Windows today.
- **Determinism.** Cycles is deterministic at a fixed seed and thread-independent sampling. Golden
  tests use SSIM, not bytes, across CPUs (Embree and OIDN use ISA-specific kernels).

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| 6.0 | Carry lmblender's Cycles build scripts and patches into lmvideo `third_party/cycles/` without the four GPL helpers; `cycles-sdk` workflow produces the cached permissive static prefix (headers + `.a` + NOTICE set + SBOM) per platform | Link-map audit shows no GPL object; `scripts/licence-gate` passes on the SDK SBOM; existing lmblender render tests reproduce within SSIM ≥ 0.99, except sky and view transforms (compared by eye and documented) | lmblender `cornell-box`, `sky-texture`, `denoise-quality` fixtures |


| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| 6.1 | Freeze version-1 capabilities/job/result schemas and frame/colour contracts | JSON schema fixtures accept/reject independently; required feature negotiation, status codes, atomic outputs and cancellation specified | Cornell-box job plus missing/unsupported-backend fixtures |
| 6.2 | glTF scene + job translation into Cycles inside lmvideo (port of lmblender's glTF/OBJ importers and Principled BSDF mapping); `lmvideo render-job DIR` debug subcommand for the on-disk job | A fixed GLB job renders to PNG in-process; lmblender v0.3.138 renders the same scene within SSIM ≥ 0.99 (excluding sky and view transforms) | Migrated blender `cornell-box.lms`, `denoise-quality.lms` |
| 6.3 | One renderer selection seam in lmvideo (`raster` or `cycles`), in-process | The in-memory job and `render-job` on the dumped job give the same image; no file round trip; raster-only startup gate (≤ 1.1×) holds; returned frame is an Image and receives 2D overlays/filters; cancellation and thread count honoured | new lmvideo `cycles-product-still.lms`, based on glass/metal fixtures |
| 6.4 | Batch resolved frames, geometry reuse and optional passes | Compare batch versus single-frame states; bounded memory, correct indices/seed, cancellation and partial results; EXR only with agreed precision/colour support | Migrated blender `animation-visibility-optics.lms`, `denoise-quality.lms` with an explicit pass request |
| 6.5 | Finish one multi-host CAD -> lmvideo (raster preview + Cycles final) gallery story | Actual lmcad geometry handoff, CPU preview, final Cycles Image, Canvas labels and Timeline movie all execute from an empty directory | New lmgallery `cad-final-render.lms` plus committed CPU/final comparison picture |

The backend receives **data**, not Python, arbitrary commands or a second modelling
program: `scene.glb`, referenced assets, versioned `job.json`, per-frame resolved
states and an output manifest. Keep Cycles/Embree/OIDN, rendering settings, BSDF
translation, image/pass output and one session per job. Drop mesh construction,
diagrams, layout, editing, fitted-camera authoring and independent keyframe/easing
logic. In-process, the same job structures are passed in memory; the on-disk job stays the
format for `render-job`, tests and bug reports. GPL duties exist only for old lmblender releases.

### Parallel track — Cycles can start now

6.0–6.2 do not depend on phases 1–5. The lmblender build scripts, glTF importer and
Cornell-box fixtures exist. The SDK workflow and the job translation can land in
lmvideo behind `renderer="cycles"` while phases 1–4 proceed. Only 6.3–6.5 wait for
5.3/5.4.

## Phase 7 — migrations and release gates

| ID | Small item | Acceptance test | Gallery example / fixture |
|---|---|---|---|
| 7.1 | Structured source migrations and diagnostics, one old API family per change | Review actual argument/unit/type transformations; all new aliases discover exactly the same schema; no claim that renaming a binary fixes old bytecode hashes | draw `etl-pipeline.lms`, img `pipeline_diagram.lms`, magnum `model-viewer.lms` |
| 7.2 | Migrate public manifests/autorun sources and retain old pins | All 50 gallery compositions execute; 31 currently affected compositions produce their declared outputs; raw URLs and historical tags still install | Existing galleries 02/05/11/13, 14/34, 38 and 22 lmvideo compositions |
| 7.3 | Stage/release lmvideo with the unified link closure and public examples | Linux x64/arm64 minimum staged checksums, version/schema, notice audit and fresh-cache install; desktop platform changes explicitly approved, not silently removed | lmvideo image, image-processing, CPU scene and optional-Cycles smoke examples |

Retirement/alias deadlines are not acceptance criteria yet. Maintain old host names
minimally for critical fixes until the owner supplies timing. No new features are
backported. Implement first-class portable material/texture compilation via P.M1–P.M5.
Unsupported legacy Filament binary/shader semantics remain explicitly external
until converted; never fabricate a successful portable material from opaque bytes.

## Open-source licensing: lmcad and lmcycles

> **Superseded for lmcycles by owner follow-up w75d (phase 6):** there is no lmcycles repo.
> Cycles is built into closed lmvideo after item 6.0, with the Apache, BSD and MIT notices in
> lmvideo's notice set. The lmcycles rows below remain only as the licence analysis behind 6.0;
> lmblender keeps its GPL licence as a frozen legacy product.

Licences apply to exact files and link closures. Opening a wrapper does not relicense
its dependencies or remove static-link source/relink requirements.

| Public repo / component | Recommended source licence | Binary/distribution facts and acceptance |
|---|---|---|
| **lmcad original wrapper code** | **Keep MIT**, matching current authored source. No need to switch original code to Apache-2.0 just because it links OCCT. Keep Apache-licensed reference examples and their notices separately identified. | OCCT is LGPL-2.1 with its Open CASCADE exception. Publish exact OCCT source/patches/build flags, app link objects or sufficient reproducible relink materials, instructions and required runtime notices for each architecture. An original MIT wrapper is compatible with these obligations; OCCT-derived modifications retain the required library licence. |
| **lmcycles original wrapper/job code** | **Keep existing per-file MIT** and use MIT for newly authored wrapper code; preserve attribution. **After 6.0 the combined lmcycles build is Apache-2.0/MIT/BSD (no GPL), which is what allows linking into lmvideo.** Package root/README must clearly describe the actual selected distribution licence, not imply every bundled input is MIT. | For the current audited Blender-derived closure, keep **GPL-3.0-or-later** as the combined package/binary licence, with MIT original-file notices and Apache dependency notices retained. Public GPL is acceptable for this external product; removing its authoring DSL alone does not make the link closure permissive. |
| **Standalone Cycles** | Upstream **Apache-2.0**; retain its licence/NOTICE and mark patches | Confirmed by [standalone Cycles LICENSE](https://github.com/blender/cycles/blob/main/LICENSE) and the [Cycles source SPDX header](https://github.com/blender/blender/blob/main/intern/cycles/kernel/types.h). It is not intrinsically the full Blender GPL application. |
| **Current lmblender GPL inputs** | Preserve GPL terms; do not relabel as Apache or MIT | Existing audit names `bf_intern_sky`, `bf_intern_libc_compat`, `bf_intern_guardedalloc`, related intern support and `cpp/view_luts.h`. [Blender guardedalloc SPDX](https://github.com/blender/blender/blob/main/intern/guardedalloc/MEM_guardedalloc.h) is GPL-2.0-or-later. Existing notice selects GPL-3.0-or-later for the combined build. |
| **Possible later permissive-only lmcycles build** | Original MIT wrapper + standalone Cycles Apache-2.0 and an entirely audited compatible dependency closure | Remove/replace every GPL helper and LUT, inspect the actual link map and embedded assets, and reproduce the render tests. Only then advertise a permissive combined build. Per the owner note (w75e), this **is now the critical path**: item 6.0. It is what allows Cycles to be built into lmvideo. Releases before 6.0 stay GPL. |

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

> **Superseded (w75d):** no rename and no lmcycles repo. lmblender stays as is, frozen
> as public legacy; O5 below is dropped. The text is kept for the record.

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

## Six standalone open-source repos (owner addition 2, plan only)

Scope: lmblender, lmfilament, lmmagnum, lmimg, lmcad and lmdraw become ordinary public
open-source repos. Each has its own source, CI and releases, and is maintained minimally (critical
fixes, dependency security updates, no features). None is an lmvideo alias. lmvideo keeps its
private/public peer model and does not depend on them; the code it took over is copied into
lmvideo, not linked. **Nothing below has been flipped or pushed.**

### State on 2026-10-26

| Repo | Private source twin | Public `lmctl-ai/<name>` today | Saved pre-flip public history (`/home/mma/staging/closed-source/`) | Private commits since the flip |
|---|---|---|---|---|
| lmblender | none (`lmctlhq/lmblender` redirects) | full source, GPL-3.0-or-later, own CI and releases (v0.3.138) | n/a | n/a |
| lmfilament | `lmctlhq/lmfilament`, 26 commits, root LICENSE MIT | 4-commit orphan main: README, docs, examples; root LICENSE = binary licence after v0.3.20 | `lmfilament-public-history-*.git` (main c5f32a2, 22 commits) | 4 |
| lmmagnum | `lmctlhq/lmmagnum`, 20, MIT | orphan; binary licence after v0.2.14 | `lmmagnum-public-history-*.git` (41a7d85, 17) | 3 |
| lmimg | `lmctlhq/lmimg`, 69, MIT | orphan; binary licence after v0.1.3 | `lmimg-public-history-*.git` (656b23b, 66) | 3 |
| lmcad | `lmctlhq/lmcad`, 143, MIT | orphan; binary licence after v0.1.72 | `lmcad-public-history-*.git` (87cbb33, 140) | 3 |
| lmdraw | `lmctlhq/lmdraw`, 49, MIT | orphan; binary licence after v0.2.6 | `lmdraw-public-history-*.git` (9452958, 46) | 3 |

For all five private twins, the saved pre-flip public `main` **is an ancestor of the private
HEAD**. The private history is the old public history plus 3–4 commits made since the flip. Those
few commits are the only history that has never been public.

### Licence per repo

Our code stays **MIT**, matching every private root LICENSE and the pre-flip public grant.
Dependency notices and duties ship with each release.

| Repo | Our code | Dependencies and duties |
|---|---|---|
| lmblender | MIT per file | Combined binary **GPL-3.0-or-later** (Blender intern sky, guardedalloc, libc_compat, `view_luts.h`); source archive and source offer per release, as today. Cycles, Embree, OIDN and TBB: Apache-2.0; OIIO, OCIO and EXR: BSD. Optionally de-GPL it later by moving to standalone `blender/cycles` (phase 6 analysis); not required for open source. |
| lmfilament | MIT | Filament 1.78.1 Apache-2.0 (NOTICE); stb (public domain/MIT); static glibc → LGPL-2.1 text plus relink objects (as now); libc++ Apache-2.0 with LLVM exception |
| lmmagnum | MIT | Magnum and Corrade MIT; stb; static runtimes (glibc relink objects if static) |
| lmimg | MIT | ImageMagick licence (Apache-2.0 style) with all delegates off; zlib, libpng, libjpeg-turbo, libtiff, libwebp; stb_truetype; Roboto Apache-2.0; dynamic glibc (no relink duty) |
| lmcad | MIT | OCCT 8.0.1 **LGPL-2.1 + OCCT exception**: relink objects, `OCCT-RELINKING.md` and recipe per architecture (as now); build123d Apache-2.0 + NOTICE; PyVista MIT; static glibc LGPL |
| lmdraw | MIT | LunaSVG and PlutoVG MIT; FreeType FTL (credit); static runtimes |

With source public, the LGPL relink duty is easier to meet: the source and build scripts are
right there. The relink-object assets still ship for static builds.

### Restoring public source: history route

Recommended route: **restore the original lineage, not a new orphan.**
1. Audit the 3–4 post-flip private commits, plus the full current tree:
   - `gitleaks`/`trufflehog` over all private refs;
   - grep for tokens, internal hostnames and `lmctlhq` paths;
   - remove closed-only files: `scripts/release-to-public.sh`, private-CI publisher steps that use
     `RELEASE_TOKEN`, staging manifests, and binary-licence texts as root LICENSE.
2. The earlier history needs only a quick re-scan; it was public until 2026-10-25.
3. Add one "return to open source" commit on top of private HEAD:
   - root `LICENSE` MIT;
   - `LICENSE-examples` kept;
   - a README licence section explaining the release eras: MIT up to vA, binary licence vA+1…vB,
     MIT again from vB+1, or MIT for all if the owner relicenses the binary-era releases, which as
     sole copyright holder they can;
   - the public-only files of the 4 orphan commits (README and images), merged in.
4. Point public `main` at that commit, so the history is again pre-flip public history, then
   private, then the restore commit.
5. Keep the 4 orphan commits reachable as tag `binary-licence-era`, so nothing is lost.
6. Restore the saved pre-flip tags and branches from the backup mirrors.

Fallback: if the audit finds something unpublishable in the post-flip commits, squash only those
3–4 commits into the reviewed restore commit. The pre-flip history stays intact, and no full orphan
is needed. lmblender needs no history work.

### CI and release in a single public repo

- One `ci.yml`, built from the private twin's (all five have one):
  - build, test and `lmscript --check` examples on push and pull requests;
  - release job on `workflow_dispatch` or a version tag;
  - `permissions: contents: write` only in the release job, using `GITHUB_TOKEN`;
  - no `RELEASE_TOKEN`, no cross-repo checkout, no `release-to-public.sh`.
- Public repos get **free standard-runner minutes**, which removes the private Actions budget block
  for these six.
- Platforms: keep exactly the set each repo shipped last; lmdraw, lmmagnum and lmcad include
  Windows. Asset names stay unchanged (`<name>-<os>-<arch>`, `SHA256SUMS`) so `install=` pins and
  `@latest` keep working.
- Minimal maintenance: a monthly scheduled CI run to catch toolchain rot, Dependabot for Actions
  only, and releases only for fixes.
- Release registry (`lmctlhq/lmctl-mono-test/releases.json`): point these six at their own public
  workflows; remove them from the private publisher inventory and from `scripts/closed-source`
  split lists. The registry maintainer applies this after the owner approves.

### README and gallery state

- Each README keeps its picture gallery and autorun captions (raw paths unchanged) and adds:
  - "Status: maintained (critical fixes only). New 2D/3D/image work happens in lmvideo";
  - a link to the matching lmvideo examples;
  - a build-from-source section;
  - the licence table above.
- lmgallery: the showcase entries and pins keep working unchanged, because asset names and
  `@latest` are preserved. Update `closed-source-pin-inventory.md` and `05-closed-source-peer-model.md`
  to list only lmvideo (plus the products outside this change) as closed peers, and mark the six as
  open source.

### Ordered steps (owner-only actions in **bold**; nothing done here)

| # | Step | Who |
|---|---|---|
| 1 | Approve MIT for our code, the history route (restore lineage vs squash fallback) and the release-era wording; decide whether binary-era releases are relicensed MIT | **OWNER** |
| 2 | Secret and closed-only audit of each private twin; prepare the restore commit and the new public `ci.yml` on a branch; dry-run CI on a fork-free branch | agent |
| 3 | **Force-with-lease public `main` to the audited restore commit** (public history rewrite: reverses the 2026-10-25 orphan reset); push tag `binary-licence-era`; restore saved tags | **OWNER** authorizes, then runs or delegates |
| 4 | **Replace the root binary-licence text** (part of step 3's commit) and edit binary-era release notes with the licence statement | **OWNER** approves the wording |
| 5 | **Enable Actions / workflow permissions** on the public repo if disabled; first public CI run | **OWNER** |
| 6 | **Re-publish: first MIT release** from public CI under the same asset names; verify fresh-cache install, `SHA256SUMS`, notices and relink assets | **OWNER** approves promotion to latest |
| 7 | **Revoke `RELEASE_TOKEN`** and private publisher secrets; switch the registry entries | **OWNER** / registry maintainer |
| 8 | **Archive the private twin** `lmctlhq/<name>` (read-only, not deleted) once public CI rebuilds from source alone. No visibility flip of the twin is needed, since the public repo already exists | **OWNER** |
| 9 | lmblender: README "maintained (critical fixes)" note only; no repo operation (rename to lmcycles only if the owner still wants it) | agent; rename **OWNER** |

Order across repos: start with lmdraw (smallest, has Windows, 4 gallery compositions), then lmimg,
lmmagnum, lmfilament, and lmcad last (largest, with LGPL relink assets to verify).

## Review amendments (ResearchOpus)

Reviewed against the repos on 2026-10-26. The plan is accepted with these changes,
already folded in above:

- lmblender is already a single public repo; only lmcad needs the peer-model
  cutover (Decisions).
- Measured 3D baseline and a relative performance gate (phase 3).
- Cycles work (6.0–6.2) runs as a parallel early track (before phase 7).

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
  and cache), 1.1 (arrow and polyline) and 6.0 (`cycles-sdk` prefix without the GPL helpers). They are independent, small and unblock the
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
