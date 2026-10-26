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
| lmvideo | Skia m144 (JetBrains pack), external `ffmpeg` pipe | Skia raster, SVG DOM, PDF | 30.1 MB | 26 types, 205 methods (218 with free overloads) | 19+ README stories | proprietary freeware binary (private source + public peer) |
| lmdraw | LunaSVG 3.5 + PlutoVG 1.3 + FreeType, **not Skia** | PlutoVG vector rasterizer | 5.6 MB | 6 types, 46 declarations | 38 | proprietary freeware |
| lmmagnum | Magnum Math, Primitives, MeshTools, Trade (no GL) | **own CPU rasterizer** (`cpp/render.cpp`, ~200 lines: supersampling, shadow map, textures) | 4.0 MB | 7 types, 58 methods | 37 | proprietary freeware |
| lmfilament | Filament 1.78.1 on the **noop backend** (material compiler, engine, geometry tools) | **own CPU preview rasterizer** (`cpp/preview.cpp`, ~255 lines: 2048² shadow map, 3×3 PCF, linear-light SSAA) | 16.4 MB + glibc relink objects | 7 types, 62 methods | 38 | proprietary freeware; needs `~/toolchains/llvm19` to build |
| lmcad | OpenCASCADE B-rep (LGPL-2.1 + exception) | own CPU rasterizer (PNG, APNG, STL) | 30.5 MB + OCCT relink objects | 9 types, 62 methods | 38 | proprietary freeware with LGPL relink duties |
| lmblender | Blender Cycles (CPU, Embree, OIDN) **compiled into one static executable** | Cycles path tracing (GI, glass, emission) | 124 MB | 3 types, 96 methods | 99 example files | GPL-3.0-or-later binary, stays open source |

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
| **lmblender** | **Keep separate, shrunk to a render backend** (§3.5) | It is a GPL-3.0 binary, so it stays outside the proprietary product. It loses its modelling and drawing DSL and becomes the external `renderer="cycles"` backend: it receives the scene the product builds and returns frames. Its 96-method authoring schema is frozen behind the alias window, then retired. |

| **lmimg** | **Merge (owner addition 2, §3.0), then retire behind an alias** | Its `Image` becomes the one pixel type shared by drawing, 3D renders and video frames. ImageMagick's licence is permissive, so licence rules do not force it out. |

Out of scope and unchanged: lmplot (gnuplot charts; lmvideo's `Plot` overlaps, but lmplot stays open
source and separate).

## 3.0 One coherent product: a single model, not renamed hosts

Owner addition 2: one binary, one schema and one mental model. The compatibility subcommands in §5
exist only to run old scripts. They are hidden from the product documentation, and new examples use
only the single schema.

**The mental model in one sentence:** everything produces an `Image`, a `Timeline` turns time into
Images, and outputs write Images (or vector recordings) to files.

| Core type | What it is | Produced by | Consumed by |
|---|---|---|---|
| `Image` | RGBA pixels (8- or 16-bit, sRGB or linear tag), immutable value; ops return new Images | `open(file)`, `Canvas.snapshot()`, `Scene.render(camera, w, h)`, `Video.frame(t)`, `Layout.render()` | filters, composite, measure, `Canvas.image()`, 3D textures, outputs |
| `Canvas` | 2D drawing surface (Skia); records vectors when its target is SVG or PDF | `canvas(w, h)` or `image.edit()` | yields an `Image` or a vector `Picture` |
| `Scene` | 3D nodes, meshes, materials, lights, cameras | `scene()`, mesh import (lmcad STL/glTF) | `render() -> Image`; viewport layers |
| `Layout` | Panels, grids and layers (2D, 3D viewport, Image) | `panel(...)` | `render() -> Image` or `Picture` |
| `Timeline` | frame clock, keyframes and tracks; a function from t to an Image | `timeline(fps, duration)` | `Video`, GIF, APNG and WebP writers, contact sheets |

Image operations are first-class on `Image`, whatever produced it:
- geometry: resize, crop, rotate, flip, perspective, lens;
- tone and colour: levels, curves, LUT/CLUT, HSL, channel mix, grayscale, threshold, equalize;
- filters: blur, sharpen, unsharp, edges, morphology, median, vignette, tilt-shift, heal;
- composite: blend modes, masks, layers;
- measure: mean, stddev, histogram, SSIM, PSNR, pixel.

So the same `blur` works on a photo, a rendered 3D frame or one video frame inside the timeline, for
example a depth-of-field-like pass or a grade applied per frame.

**Mapping lmimg (6 types, 48 Image methods; 8.9 MB; ImageMagick plus original MIT code; 4 gallery
compositions) onto that model:**

| lmimg | Unified product |
|---|---|
| `Image` (filters, tone, geometry, measure, `save`) | `Image`, one-to-one names |
| `Image.rect/circle/line/text` | `image.edit()` returns a `Canvas`, with Skia text instead of stb_truetype |
| `Img.open/canvas/pattern` | top-level `open`, `canvas`, `pattern` |
| `Curve`, `Img.curve/hald` | `Curve`, `lut(...)` |
| `Layers` (`add`, `masked`, `render`) | `Layout` layers with blend mode, opacity and mask (the same layer stack as 2D and 3D) |
| `Montage`, `Img.panel` | `Layout` grid panel |
| `Animation` (GIF frames) | `Timeline` + GIF/APNG/WebP writer |
| `Img.eval/assert_close/assert_true/print` | shared script helpers for all areas |

**Engine choice for Image operations:**
- P1 links ImageMagick statically, as lmimg does now with all delegates off. Its licence is
  permissive, it is about 5 MB, and it reproduces lmimg's pixels exactly for the alias.
- Operations that Skia already does identically (resize, blend modes, colour matrix, blur, morphology,
  perspective) then move to Skia one by one, gated on SSIM against lmimg's README pictures.
- ImageMagick is dropped only if nothing needs it any more (TIFF and the exotic codecs are the likely
  holdouts). This is an implementation choice, invisible in the schema.

**Name candidates:**
- Keep **`lmvideo`**: zero install churn, but it undersells stills and image editing.
- **`lmframe`**: matches the core model, an Image that a frame clock animates. It is short and free in
  the lm* family.
- **`lmvis`** or **`lmmedia`**: `lmmedia` invites confusion with lmaudio.
- Avoid **`lmstudio`**: it collides with the existing "LM Studio" LLM desktop application.

Recommendation: `lmframe` as the product name if the owner accepts one rename. lmvideo then becomes
an alias exactly like lmdraw, lmimg, lmmagnum and lmfilament, so the extra alias work is one more
entry in the same mechanism.

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
| Deterministic bytes | same-platform reruns: yes; cross-OS byte identity is unmeasured and is a P1 gate, not a fact | driver-dependent | driver-dependent |
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
| Path-traced still or clip | `renderer="cycles"` → external lmblender process (§3.5) | yes | no (CPU Cycles) | yes at fixed samples and seed |
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

### 3.5 lmblender as a render backend (owner addition)

The product owns all drawing, scene building and animation. lmblender keeps only final path-traced
rendering.

**Where the interface sits.** It sits at one seam in the core: a `Renderer` interface that the
scene, viewport and timeline call. The core does not call Cycles directly.

```
Scene.render(camera, w, h, renderer: "raster" | "cycles", quality...) -> Image
Viewport3D(scene, camera, renderer: ...)          // layer inside Layout
Timeline.render(..., renderer: "cycles")          // batches all frames into one job
```

- `raster` is the in-core CPU rasterizer (§3.2) and is the default.
- `cycles` serialises the scene snapshot into a render job and runs the user's `lmblender` as a
  separate process, located through PATH or `install=` like any host.
- The backend reads the returned frames back as `Image` values, so 2D overlays, image ops, layout
  and video encoding all happen in the product exactly as for raster frames.
- If `cycles` is not installed, the product fails with a clear message. It never silently falls back
  to `raster`.
- The process boundary with file exchange keeps the GPL binary at arm's length from the proprietary
  core (§4a).

**Job format.** A versioned job directory or archive:

| File | Content | Notes |
|---|---|---|
| `scene.glb` | glTF 2.0 binary: node hierarchy, triangle meshes with normals and UVs, metallic/roughness materials and textures, cameras, `KHR_lights_punctual` (point, spot, directional), `KHR_materials_emissive_strength`, `KHR_materials_transmission`, `KHR_materials_ior` | lmblender's glTF importer exists. P1 adds reading of cameras, punctual lights and those three material extensions. |
| `animation` inside the GLB | glTF animation channels for node TRS, camera and light parameters, sampled at the timeline's fps | Avoids one GLB per frame. Material animation goes in the job sidecar as per-frame overrides. |
| `job.json` | schema version; frame list; size; samples; seed; bounces; denoise quality; view transform (Standard/Filmic/AgX); world (colour, sky, environment map path); area lights (glTF has none); requested passes; output format (PNG 8/16-bit or EXR linear) | Everything glTF cannot say, and nothing else. |
| `out/` | `frame-%05d.{png,exr}`, optional passes `frame-%05d-{depth,normal,albedo}.exr`, and `result.json` (per-frame timings, structured errors) | The product imports the frames as Images. Scene-linear EXR lets the product do the grading. |

Not Cycles XML: it is Cycles' internal standalone format, unversioned, and needs a parallel exporter.
glTF is a standard that lmcad and outside tools also write, so the same `lmblender render` command
renders an lmcad export directly.

**CLI contract.**
- `lmblender render --job DIR [--threads N]` with exit codes: 0 ok, 2 job invalid, 3 unsupported
  feature (named in `result.json`), 4 render failure.
- `lmblender --render-capabilities` prints the job-schema version and supported extensions, so the
  product refuses an incompatible pair up front.

**What lmblender keeps:**
- static Cycles, Embree and OIDN;
- glTF, OBJ, STL and PLY importers;
- mapping onto the Principled BSDF;
- world colour, sky and environment maps;
- point, spot, sun and area lights;
- render settings, presets and view-transform LUTs;
- PNG/EXR, passes and sequence rendering, with one session per job (BVH reused across frames
  where only transforms change);
- the GPL source offer and relinking documentation.

**What it drops:**
- the lmscript authoring DSL as a product surface: mesh creation and transforms, instancing,
  ground/backdrop helpers, fitted camera, the diagram presets and the homepage diagram clips;
- its 99 example files as authoring examples. They migrate to product scripts with
  `renderer="cycles"`; examples that need Cycles-only material nodes (checker, noise, ramp, bump)
  carry those as job material extensions (`lm_cycles_procedural` in `job.json`), not as DSL calls;
- the BlenderCLI bridge example;
- the DSL schema itself, which stays only as a frozen compatibility alias for the alias window
  (§5, P3), then is removed.

The lmcad `compose` pipeline becomes lmcad → glTF → product scene → `cycles`.

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

## 4a. Licence table for the closed all-in-one core

Rule: a component whose licence or patents burden a closed static binary does not go into the core.
It becomes an optional external piece (own repo or binary with a documented interface, or
user-installed), and the core uses a permissive replacement.

| Component | Licence | Problem for the closed core? | Placement / replacement |
|---|---|---|---|
| Skia (+ SVG module, PDF backend) | BSD-3-Clause | no | **in-core** |
| FreeType | FTL (BSD-style, credit clause) / GPL-2 dual | no (take FTL) | **in-core** |
| HarfBuzz, ICU, Expat, libpng, zlib, libjpeg-turbo, libwebp | MIT / Unicode / MIT / libpng / zlib / IJG+BSD / BSD-3 | no | **in-core** |
| DejaVu Sans (bundled font) | Bitstream Vera / public domain | no | **in-core** |
| Own 3D rasterizer, mesh primitives, exporters | own code | no | **in-core** |
| stb_image / stb_image_write, cgltf | public domain or MIT / MIT | no | **in-core** |
| Magnum Math, Primitives, MeshTools, Trade + Corrade | MIT | no | **in-core** for v1 (§8); later removable |
| Filament | Apache-2.0 | no licence problem | **dropped** for technical reasons (§4) |
| LunaSVG + PlutoVG (lmdraw) | MIT | no | **dropped**; Skia SVG replaces them |
| FFmpeg / libav* | LGPL-2.1+, or GPL with `--enable-gpl` | **yes**: static LGPL means relink duties; GPL builds are viral | **external**: user-installed `ffmpeg` process, as today. Core replacement for in-process encoding: libvpx (BSD-3) VP8/VP9 in a small own WebM muxer, libaom or SVT-AV1 (BSD-2 + AOM patent licence) for AV1, own GIF/APNG via libpng, libwebp for animated WebP |
| x264 / x265 | GPL-2.0+ | **yes** | **external** only (through the user's ffmpeg) |
| H.264 / HEVC / AAC codecs, any implementation | patent pools (MPEG LA / Access Advance / Via) | **yes** (patents, even with BSD code such as a self-built OpenH264) | **external** (user's ffmpeg). Core default video: VP9/AV1 in WebM, plus GIF/APNG/WebP |
| OpenCASCADE (lmcad) | LGPL-2.1 + OCCT exception | **yes**: static relink duties | **external**: lmcad stays its own binary, exchanging STL/OBJ/glTF meshes. Permissive core replacement if mesh-level CSG is ever wanted: Manifold (Apache-2.0); not B-rep |
| Blender sources and lmblender's combined binary | GPL-3.0-or-later | **yes** | **external**: lmblender stays its own GPL binary as the `cycles` render backend, invoked as a process with a glTF + `job.json` job (§3.5). Standalone Cycles + Embree + OIDN are Apache-2.0, so a permissive path-tracer plug-in is possible later, but its size (100+ MB) keeps it out of the core |
| glibc, linked statically (current Linux hosts) | LGPL-2.1+ | **yes**: relink objects shipped today | **replace**: link musl (MIT) statically, or link glibc dynamically. libstdc++/libgcc (GPL + runtime exception) and libc++ (Apache-2.0 + LLVM exception) have no problem |

The core binary therefore carries only permissive notices. Each external piece keeps its own
licence files, relink materials or source offer in its own release.

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
- The one executable embeds the old schemas unchanged: `magnum`, `filament`, `draw` and `img`
  subcommands (plus `video` if the product is renamed), the same multi-schema pattern as `lmoffice docx|xlsx|pptx`.
- Bytecode compiled against an old schema keeps its schema hash, so existing `.dslb` files and
  scripts load.
- Each subcommand is an adapter: old methods map onto the new engine, with axis, fov, unit, light
  intensity (lmfilament lux to normalised) and material-model mapping.
- Legacy contexts stay exactly as they are: `scene:Scene` for lmdraw and lmmagnum, `fil:Filament`
  for lmfilament.
- Adding types to the default lmvideo schema changes its raw hash. The binary therefore also keeps
  the fingerprints of previous lmvideo schemas and dispatches old `.dslb` files to them (or the
  owner accepts a recompile policy).
- lmfilament's material-compiler API (`material_file`, `Material.save`, compiled packages) cannot
  be emulated without Filament. Either those calls fail with a clear message in the alias, or
  lmfilament stays on its frozen last release (open question 2).
- Acceptance: every example in the lmmagnum, lmfilament and lmdraw repositories runs through the
  adapter and matches its committed README picture within SSIM ≥ 0.97. Known deviations are listed
  per example.

**P3 — old repositories publish the alias binary.**
- The private peers of lmmagnum, lmfilament and lmdraw stop building their own engines. Their
  release workflow republishes the unified binary under the old asset names (`lmmagnum-linux-x64`,
  ...). The binary dispatches on `argv[0]`, or on a default subcommand baked in at link time.
- `cli="lmmagnum" install="github:lmctl-ai/lmmagnum@latest"` therefore keeps resolving, and README
  autorun URLs keep working unchanged, because examples stay at their paths in the public repos.
- Platforms: lmdraw and lmmagnum ship Windows x64 today, but lmvideo and lmfilament do not. An alias
  replaces a Windows asset only after the unified Windows build passes. Until then the last native
  Windows release stays the `latest` for that platform.
- Releases follow the staged path in [06-release-cycle.md](06-release-cycle.md): Linux first, public
  prerelease verification, then explicit promotion of each alias. Promotion across peers is not
  atomic, so promote one peer at a time and keep rollback to the previous tag.

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
| Floating-point differences across platforms break byte determinism | Unmeasured today. Build without fast-math and with a fixed SSAA and tile order. Gate on SSIM across platforms and on byte identity per platform; promise cross-OS byte identity only if it is measured. |
| Licence contamination | Enforced by §4a: only permissive components in the core; a CI check fails on any non-allowlisted licence in the notices manifest. |
| One larger product, one release pipeline: a 3D change can block 2D releases | One repository with per-area tests and the existing automatic release per push. Area ownership is in module directories (as lmpdf does), not separate products. |
| Gallery and URL breakage | P3 alias binaries under old asset names; examples keep their paths; CI keeps running the old repos' examples against the alias until P5. |

## 7. Open questions for the owner

1. **Name.** Keep `lmvideo` (continuity; 22 gallery compositions), or rename to `lmframe` (§3.0),
   with lmvideo as one more alias in the same mechanism?
2. **Alias window.** Is "6 releases and 3 months" acceptable for lmmagnum, lmfilament, lmdraw and lmimg,
   or must old host names live indefinitely as subcommands? May lmfilament's material-compiler
   calls (`material_file`, `Material.save`) stay only on its frozen last release?
3. **Cycles install.** Should `renderer="cycles"` auto-install lmblender through lmctl on first use
   (124 MB download), or require an explicit user install, to keep the GPL piece clearly opt-in?
4. **lmcad rendering.** Should lmcad keep its own preview renderer, or adopt the shared renderer
   source for one look across the family? It stays a separate binary either way.
5. **GPU.** Is a GPU flavour ever wanted (long 4K video, interactive preview), or is CPU-only an
   explicit product promise ("runs anywhere, same bytes")?

## 8. Cross-review amendments

The two companion notes were read after this one was written:
[ResearchSol](08-consolidation-ResearchSol.md) (feasibility inventory) and
[ResearchArgon](08-consolidation-ResearchArgon.md) (API design). All three agree on the shape:
- lmvideo is the base;
- one CPU 3D renderer, rasterized into viewports inside 2D layout;
- Filament dropped;
- lmcad and lmblender kept separate;
- old host names kept as bounded aliases.

Accepted from ResearchSol (folded into §1, §3.3, §5 and §6 above):
- exact declaration counts;
- legacy contexts (`scene:Scene`, `fil:Filament`);
- schema-fingerprint dispatch for old lmvideo bytecode;
- the Windows asset contract of lmdraw and lmmagnum;
- the staged Linux-first release path;
- the Filament material-package APIs as a blocker for an unconditional alias;
- cross-OS byte identity treated as unmeasured.

Also from ResearchSol: WebP output, glTF export and video-input layers in §3.1 are proposed
additions, not current lmvideo outputs.

Where this note differs from ResearchArgon:
- **Magnum subset in v1.** ResearchArgon proposes a zero-dependency core with no Magnum or Corrade,
  built from lmfilament `cpp/mesh.cpp`. That file includes Filament's
  `geometry/SurfaceOrientation.h` (line 2) and uses its tangent builders, so it is not
  dependency-free today. P1 keeps the tested Magnum Math/Primitives/MeshTools subset (MIT,
  lmmagnum's 4.0 MB build). Removing it is a later size optimisation once primitives are extracted
  and the SSIM gates pass.
- **Size estimates.** ResearchArgon's "~18.5 MB total, <400 KB growth" estimate is not a baseline:
  released lmvideo linux-x64 is already 30.1 MB. Growth is measured in P1 against a ≤ 4 MB budget.
- **Premises corrected by ResearchSol and confirmed here from the repositories:**
  - lmdraw is LunaSVG/PlutoVG (5.55 MB), not Skia (15 MB);
  - lmblender is in-process static Cycles, not `blender -b -P`;
  - the gallery has 4 lmdraw compositions and 1 lmmagnum composition (`38-product-render-slide`),
    not 38 lmdraw compositions and no lmmagnum ones.

  So lmmagnum cannot be archived without an alias. ResearchArgon's 2-release lmdraw window is too
  short for the installer and Windows contracts; all three notes now leave the window to the owner,
  with 6 releases and 3 months as the proposal.
- **Frame times.** ResearchArgon's frame times (18 ms at 800×600, 3.4× from threading) are
  estimates. The only measured figure is the 0.21 s whole-run `shadows` scene in §1. The P1
  frame-time gate decides.

Agreed with ResearchArgon:
- degrees everywhere;
- Skia glyph outlines for 3D text, which needs real tessellation with holes and winding, so it is
  P1 work and not a one-liner;
- sorted alpha for transparency;
- `lmvideo draw|magnum|filament` subcommands with `argv[0]` dispatch.
