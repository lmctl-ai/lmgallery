# Consolidating the 2D/3D hosts on lmvideo: product and architecture (ResearchOpus)

Scope: lmvideo, lmdraw, lmmagnum, lmfilament, lmcad and lmblender. One product should draw 2D and
3D and produce images and video, with lmvideo as the base. This note covers the target
architecture, the 3D renderer choice, where CAD fits, a phased migration with compatibility aliases,
risks, open questions and a verdict per repository.

The facts below come from the repositories on 2026-10-26: READMEs, `schema/*.dsl.json`,
durable-memory, lmcad `durable-memory/20-sibling-3d-hosts.md`, release assets, and two timed runs.
The feasibility inventory (ResearchSol) and the API design (ResearchArgon) are separate notes.

## 1. What the six hosts are today

| Host | Engine | Pixels come from | Binary (linux-x64) | Schema | Examples | Distribution |
|---|---|---|---|---|---|---|
| lmvideo | Skia m144 (JetBrains pack), external `ffmpeg` pipe | Skia raster, SVG DOM, PDF | 30.1 MB | 26 types, 201 methods | 19+ README stories | proprietary freeware binary (private source + public peer) |
| lmdraw | LunaSVG 3.5 + PlutoVG 1.3 + FreeType, **not Skia** | PlutoVG vector rasterizer | 5.6 MB | 6 types, 38 methods | 38 | proprietary freeware |
| lmmagnum | Magnum Math, Primitives, MeshTools, Trade (no GL) | **own CPU rasterizer** (`cpp/render.cpp`, ~200 lines: supersampling, shadow map, textures) | 4.0 MB | 7 types, 58 methods | 37 | proprietary freeware |
| lmfilament | Filament 1.78.1 on the **noop backend** (material compiler, engine, geometry tools) | **own CPU preview rasterizer** (`cpp/preview.cpp`, ~255 lines: 2048² shadow map, 3×3 PCF, linear-light SSAA) | 16.4 MB + glibc relink objects | 7 types, 62 methods | 38 | proprietary freeware; needs `~/toolchains/llvm19` to build |
| lmcad | OpenCASCADE B-rep (LGPL-2.1 + exception) | own CPU rasterizer (PNG, APNG, STL) | 30.5 MB + OCCT relink objects | 9 types, 62 methods | 38 | proprietary freeware with LGPL relink duties |
| lmblender | Blender Cycles (CPU, Embree, OIDN) **compiled into one static executable** | Cycles path tracing (GI, glass, emission) | 124 MB | 3 types, 96 methods | 73 | GPL-3.0-or-later binary, stays open source |

Corrections to the premise:
- **lmdraw is not Skia.** It uses LunaSVG and PlutoVG. lmvideo already carries an
  "lmdraw-compatible diagram vocabulary" (labelled shapes, connectors, grids, sequences;
  `durable-memory/11-diagram-vocabulary.md`), so most of lmdraw has been re-implemented on Skia.
- **lmblender is not an external app.** It is Cycles linked into one 124 MB static GPL binary,
  with no Blender install and no Python. It is still the one host that must not be merged; see §4.
- **Filament draws nothing in lmfilament.** Filament runs on its noop backend; every PNG comes from
  lmfilament's own rasterizer. Filament contributes material compilation and validation, a 12 MB
  larger binary, an LLVM 19 toolchain requirement, and startup time. The same `shadows` scene
  (900×560, shadow map) takes **0.21 s** for a whole `lmscript` run with lmmagnum and **4.07 s**
  with lmfilament (79 MB vs 125 MB max RSS), and the pictures are equivalent.
- **The three 3D hosts already share one rendering idea.** Each has a few-hundred-line CPU
  rasterizer that differs in conventions (Y-up vs Z-up, radians vs degrees, horizontal vs vertical
  fov) rather than in capability. The library each one "wraps" mostly supplies maths, primitives
  and mesh export.

Gallery exposure (lmgallery `showcases.json`, 50 compositions): lmvideo appears in 22, lmdraw in 4,
lmcad in 2, lmmagnum in 1, and lmfilament and lmblender in none. Each host README has 11-19
`lmctl autorun` captions that must keep resolving.

## 2. Verdict

| Repository | Verdict | Why |
|---|---|---|
| **lmvideo** | **Base of the product; merge target** | It already owns the process, the Skia surface, layout managers, plots, SVG/PDF, video encode and a retained diagram model. |
| **lmmagnum** | **Merge, then retire** | The 3D core of the new product is its rasterizer plus Magnum Math, Primitives and MeshTools (MIT, about 3 MB). |
| **lmfilament** | **Merge its features, drop Filament, retire** | Keep the preview rasterizer's PBR shading, shadow map, textures and point lights. Drop the Filament dependency: no pixels, 4 s startup, 12 MB, LLVM 19. |
| **lmdraw** | **Merge (vocabulary already in lmvideo), then retire** | LunaSVG/PlutoVG duplicate Skia's SVG DOM and rasterizer. The 38 examples migrate to the Skia implementation behind the old schema. |
| **lmcad** | **Keep separate** | The OCCT B-rep kernel is the product: booleans, fillets, offsets, volumes. Merging it would put LGPL relink obligations and 25 MB on every image and video user. Interoperate through mesh files. |
| **lmblender** | **Keep separate** | GPL-3.0 binary: it cannot be linked into the proprietary product, and it is open source by owner decision. Its 124 MB size and hours-long CI do not fit a fast image/video host. Path-traced quality stays its niche. |

Out of scope and unchanged: lmplot (gnuplot charts; lmvideo's `Plot` overlaps but lmplot stays open
source) and lmimg (image processing).

## 3. Target architecture

### 3.1 One process, one document model

```
Document (size, background, colour space, fps, duration)
 └─ Timeline: frame clock t; Keyframes / Tracks bind any animatable property
     └─ Layout: Panels (pack, grid, place, border, flow, box), as in lmvideo today
         └─ Layers, composited in order onto the frame Canvas
             ├─ Canvas2D   recorded Skia picture: paths, text, shapes, diagrams, Plot/Series
             ├─ Viewport3D a Scene3D seen through a Camera, rasterized to RGBA, wrapped as an SkImage
             ├─ Image / Svg / Video-in   decoded inputs
             └─ Overlay    2D annotations anchored to 3D points (projected each frame)
Outputs: PNG/JPEG/WebP · SVG/PDF (2D vector; 3D layers embedded as raster) · GIF/APNG/MP4 (ffmpeg) · STL/OBJ/PLY/glTF (meshes)
```

- **Scene3D:** nodes with transform (translate, rotate in degrees, scale), mesh, material and
  visibility. It also holds cameras (look-at, vertical fov) and lights (directional, point, spot,
  ambient, image background).
- **Conventions:** Y-up, degrees, vertical fov everywhere. The compatibility adapters (§5) translate
  lmblender-style Z-up and lmmagnum's horizontal fov, following the porting table in lmcad 20 §3.
- **Two animation styles, kept side by side:**
  - immediate mode, today's lmvideo and 3D-host style: mutate objects, then emit a frame;
  - retained keyframes on any property, lmvideo `Keyframes` generalised to 3D node and material
    properties.

  Both feed the same per-frame evaluation, so a script can mix them.
- **2D and 3D compose in one place.** A Viewport3D is a layer inside a Panel. A dashboard can show a
  rotating molecule next to a Plot, with labels drawn by Skia (correct shaping and kerning, the same
  fonts as 2D) instead of the 3D hosts' bitmap or limited `label()` text.

### 3.2 3D renderer: one primary engine, our own CPU rasterizer

Choice: **consolidate the existing CPU rasterizers into one renderer**. Base it on lmfilament's
preview rasterizer (the most complete shading) and lmmagnum's structure (Magnum Math, Primitives,
MeshTools, Trade). Do not pick Filament or a Magnum GL renderer as the primary.

| Criterion | Own CPU rasterizer | Filament (real GPU backend) | Magnum GL |
|---|---|---|---|
| Runs headless in CI, containers, any machine | yes | needs a Vulkan/Metal/GL device, or SwiftShader (+ size, slow) | needs GL context or EGL/OSMesa |
| Deterministic bytes across runs and platforms | yes (proven by the current hosts' golden tests) | driver-dependent | driver-dependent |
| Static single binary | yes (+~3 MB) | GPU loader and ICDs are dynamic | GL/EGL dynamic |
| What the gallery needs (Lambert/PBR-lite, shadows, textures, SSAA, ≤1080p) | already implemented three times | far more than needed | more than needed |
| Speed | 0.21 s per 900×560 scene with shadows (whole run); video at 720p fits CI minutes | fastest with a GPU | fast with a GPU |
| Build cost | C++17, no extra toolchain | LLVM 19, material compiler, large SDK | moderate |

Shading for v1:
- metallic/roughness BRDF (GGX, Smith, Schlick, re-implemented from the published formulas);
- directional, point and spot lights;
- one shadow map with PCF on the key light;
- albedo textures with mips (stb_image);
- linear-light supersampling, then a single sRGB encode, as lmfilament's preview does now.

Not in v1: global illumination, reflections, refraction and area lights (lmblender's job), and
order-independent transparency (sorted alpha only).

A GPU backend can come later behind the same scene model, as an optional build flavour, if video
volume demands it. It is not part of the merge.

### 3.3 CPU / headless / GPU matrix

| Output | Path | Headless | GPU needed | Deterministic |
|---|---|---|---|---|
| 2D still (PNG, JPEG, WebP) | Skia raster | yes | no | yes |
| 2D vector (SVG, PDF) | Skia SVG/PDF backends | yes | no | yes (fixed metadata) |
| 3D still | CPU rasterizer → SkImage layer | yes | no | yes |
| Mixed 2D+3D still | layers composited by Skia | yes | no | yes |
| Video (MP4, GIF, APNG) | per-frame raster → ffmpeg pipe (in-process libav evaluated in lmvideo 06; LGPL policy pending) | yes | no | yes (frames); container bytes depend on the ffmpeg version |
| Path-traced still or clip | **lmblender** (separate host) | yes | no (CPU Cycles) | yes at fixed samples and seed |
| Exact B-rep geometry | **lmcad** (separate host), exported as mesh | yes | no | yes |

### 3.4 Where CAD fits

lmcad stays the geometry kernel: B-rep modelling, booleans, fillets, sections and volumes, with
STL/APNG output and its own preview renderer. It joins the product by data, not by linking:
- lmcad exports a mesh (`STL` today; add `glTF` with materials);
- the unified host imports it (`scene.load_mesh("part.glb")`) and composes it with 2D annotation,
  dimension labels, plots and video.

The lmscript outer script already sequences hosts (`_dsl_` block per host). A CAD-to-video
composition is two blocks: lmcad builds and exports, the unified host renders and animates.

This keeps OCCT's LGPL relink duties and 25 MB inside lmcad. lmcad may later delegate its own
render calls to the shared renderer source (MIT, our code) to share look and conventions; that is
code reuse, not a merged binary.

lmblender uses the same pattern: the unified host can export a scene (glTF + camera JSON) for
path tracing. Whether lmblender gains an import is an owner decision (open question 3).

## 4. What not to merge, and what to drop

| Item | Decision | Reason |
|---|---|---|
| OCCT kernel (lmcad) | **Do not merge** | LGPL-2.1 static relinking duties and 25 MB for every user; a different product (engineering geometry). |
| Cycles (lmblender) | **Do not merge** | GPL-3.0 cannot be linked into the proprietary binary; 124 MB; CI takes hours. |
| Filament | **Drop** | Produces no pixels here; 4 s startup per run, 12 MB, LLVM 19 toolchain. Its material model survives as formulas in our shader. |
| LunaSVG + PlutoVG (lmdraw) | **Drop** | Skia's SVG DOM and rasterizer already serve lmvideo; two vector stacks would mean two text and AA behaviours. |
| Magnum GL, plugins, scene importers | **Do not add** | Keep only Math, Primitives, MeshTools, Trade (+ Corrade PluginManager), as lmmagnum does today. |
| lmblender-only features in the merged schema (GI, glass, emission materials) | **Do not fake** | The merged host draws what its rasterizer can draw; captions point to lmblender for path-traced looks. |
| Per-host conventions (Z-up, radians, horizontal fov) | **Drop from the new schema; keep only in compatibility adapters** | One convention set (Y-up, degrees, vertical fov) in the new schema. |

## 5. Migration in phases, with compatibility aliases

Rule: no gallery composition or README `lmctl autorun` URL breaks at any phase. Old host names stay
as thin aliases for at least **6 releases and 3 months**, whichever is longer, after the phase that
introduces them.

**P1 — 3D core inside lmvideo (new schema types only).**
- Add `Scene3D`, `Node`, `Mesh`, `Material`, `Light`, `Camera`, `Viewport3D`, `Texture` and
  mesh I/O.
- Port the merged rasterizer from lmfilament's preview and lmmagnum's render, with the shared
  conventions.
- Acceptance:
  - the 25 scenes shared by the 3D hosts (lmcad 20 §4) render to within SSIM ≥ 0.97 of the current
    lmmagnum/lmfilament pictures after convention mapping;
  - frame time ≤ 0.5 s at 1280×720 with shadows on the CI runner;
  - outputs are byte-identical across two runs on all four release platforms;
  - binary growth ≤ 4 MB.

**P2 — compatibility subcommands.**
- The one executable embeds the old schemas unchanged: `lmvideo magnum`, `lmvideo filament` and
  `lmvideo draw`, the same multi-schema pattern as `lmoffice docx|xlsx|pptx`.
- Bytecode compiled against an old schema keeps its schema hash, so existing `.dslb` files and
  scripts load.
- Each subcommand is an adapter: old methods map onto the new engine, with axis, fov, unit, light
  intensity (lmfilament lux to normalised) and material-model mapping.
- Acceptance: every example in the lmmagnum, lmfilament and lmdraw repositories runs through the
  adapter and matches its committed README picture within SSIM ≥ 0.97. Known deviations are listed
  per example.

**P3 — old repositories publish the alias binary.**
- The private peers of lmmagnum, lmfilament and lmdraw stop building their own engines. Their
  release workflow republishes the unified binary under the old asset names (`lmmagnum-linux-x64`,
  ...). The binary dispatches on `argv[0]`, or on a default subcommand baked in at link time.
- `cli="lmmagnum" install="github:lmctl-ai/lmmagnum@latest"` therefore keeps resolving, and README
  autorun URLs keep working unchanged, because examples stay at their paths in the public repos.

**P4 — migrate content mechanically.**
- A rewriter script (kept in the product repo) converts old-API scripts to the new schema using the
  convention table, for the 1 lmmagnum and 4 lmdraw gallery compositions and the repos' examples.
- Gallery compositions switch `cli=` to the product host in one commit each, with before/after
  pictures.
- lmvideo's own 22 compositions are unaffected.

**P5 — retire.**
- After the alias window, the lmmagnum, lmfilament and lmdraw public repos keep a README redirect, a
  pinned last alias release and their examples (so old URLs still run against the pinned release).
- Their private repos are archived.
- lmcad and lmblender continue unchanged, apart from the glTF exchange in §3.4.

## 6. Risks

| Risk | Mitigation |
|---|---|
| Visual regressions when one rasterizer replaces three | SSIM gates per example in P1 and P2, and per-example deviation notes instead of silent drift. |
| CPU 3D too slow for long 1080p videos | Measure in P1 (budget ≤ 0.5 s per 720p frame). Tile and thread the rasterizer (it is embarrassingly parallel). An optional GPU flavour is the escape hatch, not v1. |
| Schema bloat (201 + ~100 methods) makes the API hard to learn and compile | Namespaced types (`canvas`, `scene`, `timeline`, `layout`); the API design note (ResearchArgon) owns the surface. Old schemas live only in compatibility subcommands. |
| Floating-point differences across platforms break byte determinism | The existing hosts already pin it (no fast-math, fixed SSAA order). Keep golden-image tests on all four platforms; macOS links Skia with system frameworks, so check text rendering there first. |
| Licence contamination | No OCCT, Cycles or libav in the product binary. FFmpeg stays an external process until the LGPL policy in lmvideo 06 is decided. |
| One larger product, one release pipeline: a 3D change can block 2D releases | One repository with per-area tests and the existing automatic release per push. Area ownership is in module directories (as lmpdf does), not separate products. |
| Gallery and URL breakage | P3 alias binaries under old asset names; examples keep their paths; CI keeps running the old repos' examples against the alias until P5. |

## 7. Open questions for the owner

1. **Name.** Keep `lmvideo` (continuity; 22 gallery compositions, existing users), or rename to a
   neutral product name with `lmvideo` itself as an alias? A rename doubles the alias work in P3.
2. **Alias window.** Is "6 releases and 3 months" acceptable for lmmagnum, lmfilament and lmdraw,
   or must old host names live indefinitely as subcommands?
3. **lmblender interop.** Should lmblender gain a glTF + camera import so product scenes can be path
   traced, or does it stay a fully separate authoring host?
4. **lmcad rendering.** Should lmcad keep its own preview renderer, or adopt the shared renderer
   source for one look across the family? It stays a separate binary either way.
5. **GPU.** Is a GPU flavour ever wanted (long 4K video, interactive preview), or is CPU-only an
   explicit product promise ("runs anywhere, same bytes")?
