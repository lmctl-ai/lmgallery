# 08 — Consolidating 2D, 3D, and Video Hosts into `lmvideo`: Language, Schema, and API Design (ResearchArgon)

**Scope**: Unified DSL schema and language ergonomics for merging 2D drawing (`lmdraw`), 3D scene rendering (`lmmagnum`, `lmfilament`), and frame-by-frame video/layout (`lmvideo`) into one product, while preserving strict technical and legal boundaries against `lmcad` (OCCT B-Rep) and `lmblender` (Blender/Cycles).  
**Companion docs**: [08-consolidation-ResearchOpus.md](08-consolidation-ResearchOpus.md) (product & engine architecture), [08-consolidation-ResearchSol.md](08-consolidation-ResearchSol.md) (feasibility, binary size, and CI inventory).

---

## 1. Verdict per Existing Repository & Critical Boundaries

| Repo | Today's Role & Stack | Types / Methods | Verdict | Rationale |
| :--- | :--- | :---: | :---: | :--- |
| **`lmvideo`** | 2D Skia canvas, retained `Plot`/`Heatmap`/`VectorField`, `Panel` layout managers, `lmdraw` diagram vocabulary, `Document`/`PdfDocument` vector export, and `Video` MP4/WebM/GIF encoder (`libskia.a` + `libsvg.a` + `ffmpeg`, 30.1 MB) | 26 / 205 | **BASE PRODUCT** | Already owns 100% of 2D Skia primitives, scientific plots, layout managers, vector recording, diagram primitives, and video encoding. |
| **`lmimg`** | Raster image processing, color grading (`curves`, `levels`, `hsl`, `clut`, `colormap`), convolution/retouch (`blur`, `unsharp`, `morphology`, `heal`, `perspective`, `lens`, `tilt_shift`), `Layers`, `Montage`, `Animation`, `ssim`/`psnr` (static ImageMagick + 1,626 LOC C++17) | 6 / 55 | **MERGE & RETIRE** | ~85% of `lmimg/cpp/image.cpp` is already our own pure C++17 pixel math over RGBA buffers; the remaining 4 MagickWand calls (`blur`, `sharpen`, `edges`, `resize`) are built into Skia (`SkImageFilters`, `SkPixmap::scalePixels`). Merging `lmimg` into `lmvideo`'s `Image`/`Surface` type eliminates ImageMagick (~8 MB) and makes filters/grading/compositing/SSIM first-class on every 2D canvas, 3D render, and video frame. |
| **`lmdraw`** | 2D vector canvas + diagram vocabulary (LunaSVG 3.5 + PlutoVG 1.3 + FreeType, 5.6 MB) | 6 / 46 | **MERGE & RETIRE** | 33 of 38 core methods already exist verbatim in `lmvideo` (ported in `lmvideo` v0.2.38). Adding the last 5 convenience helpers (`arrow`, `polyline`, `axes`, `log_axes`, `legend`) to `lmvideo`'s `Canvas` reaches 100% parity on a single Skia text/AA stack. |
| **`lmmagnum`** | 3D procedural primitives, hierarchical nodes, PBR-lite + shadow-map software rasterizer, STL/OBJ/PLY export (4.0 MB) | 7 / 58 | **MERGE API & RETIRE** | Despite the name, `lmmagnum` does **not** use Magnum's OpenGL/Vulkan renderer — `cpp/render.cpp` (200 LOC) is a pure C++17 CPU Z-buffer rasterizer (`#include "stb_image_write.h"`), using Magnum only for `MeshTools` primitive generators and `Matrix4`. |
| **`lmfilament`** | 3D procedural primitives (`box`, `sphere`, `icosphere`, `cylinder`, `cone`, `capsule`, `plane`, `triangle`, `tube_between`, `ring`, `text`), PBR materials, procedural textures, CPU preview rasterizer (16.4 MB) | 7 / 62 | **MERGE API & RETIRE** | Runs Google Filament 1.78.1 on `Backend::NOOP` (which renders **zero pixels**) and renders every PNG through `cpp/preview.cpp` (255 LOC pure C++17 CPU rasterizer). `cpp/mesh.cpp` (375 LOC) already generates all 11 procedural primitives in C++17 (only calling Filament's `SurfaceOrientation` for unused tangent quaternions). |
| **`lmcad`** | Parametric B-Rep solid modeling (`Sketch`, `Part`, `Assembly`), exact STEP/IGES/BREP/STL/DXF/SVG export on OpenCascade 7.8 (30.5 MB) | 9 / 62 | **KEEP SEPARATE** | Exact NURBS/B-Rep booleans, fillets, chamfers, shells, lofts, and HLR technical projections require 75 OCCT libraries and trigger **LGPL-2.1 §6a relink-archive obligations** (`lmcad-relink.tar.gz`). Merging OCCT into `lmvideo` would infect the core binary with LGPL relink duties. Interop is clean via STL/OBJ/glTF file handoff. |
| **`lmblender`** | In-process static Blender Cycles CPU path tracer, modifiers, metaballs, curves, `.blend`/`.glb` export (124 MB) | 3 / 96 | **KEEP SEPARATE** | Links Blender/Cycles (**GPL-3.0-or-later**, 124 MB). Cannot be linked into a closed-source binary, and its path-tracing latency is incompatible with high-FPS programmatic video loops. |

### Critical Architecture Refinement (Why to Drop *Both* Filament and Magnum/Corrade)

In [08-consolidation-ResearchOpus.md](08-consolidation-ResearchOpus.md) (§3.2 and §4), Opus rightly picks our own CPU rasterizer over Filament or Magnum GL, while retaining Magnum's `Math, Primitives, MeshTools, Trade (+ Corrade)` (+~3 MB) for primitive mesh generation. Inspecting the actual C++ implementations in `/home/mma/repos/dsl/lmfilament/cpp/` and `/home/mma/repos/dsl/lmmagnum/cpp/` reveals that we can drop Magnum and Corrade too (**Zero-Dependency C++17 3D Core**):

1. **`lmfilament/cpp/mesh.cpp` (375 LOC)** is already **100% dependency-free C++17** (`<cmath>`, `<vector>`, `<fstream>`). It implements `make_box`, `make_sphere`, `make_icosphere` (with midpoint subdivision), `make_cylinder`, `make_cone`, `make_capsule`, `make_plane`, `make_triangle`, `make_tube_between` (arbitrary 3D Frenet frame strut), `make_ring`, `load_obj`, and `save_obj`.
2. **`lmmagnum/cpp/render.cpp` (200 LOC)** and **`lmfilament/cpp/preview.cpp` (255 LOC)** are already standalone C++17 software rasterizers implementing perspective/orthographic projection, 2×2 SSAA, 1024×1024 directional shadow maps (`3×3` PCF), Cook-Torrance GGX / Blinn-Phong shading, procedural sky/ground gradients, bilinear/mipmapped texture sampling, and binary STL/OBJ/PLY export.
3. **Skia already provides `SkM44` / `SkV3` and glyph-path extraction (`SkFont::getPath`)**: instead of `lmfilament`/`lmmagnum`'s blocky 5×7 voxel bitmap cubes for `text3d`, `lmvideo` can extrude real TrueType outline contours from Skia's `SkPath` with Earcut triangulation in ~120 LOC.

**Conclusion**: Merging `lmfilament/cpp/mesh.cpp` + `preview.cpp` + `lmmagnum/cpp/render.cpp` into `lmvideo/src/scene3d.{hpp,cpp}` (~950 LOC total) gives `lmvideo` the union of `lmfilament` and `lmmagnum` with **zero new external libraries**, preserving `lmvideo`'s single `Makefile` build and keeping the static binary at **~18.5 MB**.

### 1.2 Component Licence Matrix & Core/External Boundary (Owner Licence Rule)

**Rule**: Any component with a licence or patent restriction incompatible with a closed-source single-file commercial/freeware binary (LGPL static-relink duties, GPL virality, H.264/HEVC distribution royalties, or GPL font exceptions) is **excluded from the core binary**, kept as an optional external piece (separate binary/repo or user-installed tool invoked via a documented interface), and paired with a **permissively licensed in-core replacement** (`MIT` / `BSD` / `Apache-2.0` / `Zlib` / `MPL-2.0` / `OFL-1.1`).

| Component / Capability | Candidate / Current Library | Licence | Problem for Closed Core Binary? | Disposition (`In-Core` / `External`) | Permissively Licensed In-Core Replacement & Documented External Interface |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2D Canvas, SVG DOM, PDF Writer, Text Shaping** | JetBrains Skia (`libskia.a` + `libsvg.a`: FreeType, HarfBuzz, libpng, libwebp, zlib, expat) | `BSD-3-Clause` / `MIT` / `FTL` / `Zlib` | **No** (attribution only in `THIRD-PARTY-NOTICES.txt`; FreeType used under BSD-style FTL without GPL) | **In-Core** | Already in `lmvideo` (`m144-e2e6623374-4`). Drops `lmdraw`'s redundant `LunaSVG`/`PlutoVG` (`MIT`). |
| **Raster Image Processing, Grading, Retouch & QA Metrics (`lmimg`)** | `lmimg/cpp/image.cpp` + `expr.hpp` (1,958 LOC) + static `ImageMagick` (`MagickCore`/`MagickWand`, `Apache-2.0`, ~8 MB) + `libtiff` (`libtiff` BSD-like) | `MIT` (own code) + `Apache-2.0` (ImageMagick) + `BSD` (`libtiff`) | **No licence blocker**, but static ImageMagick adds ~8 MB and security-policy overhead when 85% of `lmimg` is already pure C++17 pixel loops | **In-Core** (pure C++17 ops + Skia + `libtiff`; **drop ImageMagick**) | Port `lmimg/cpp/image.cpp` + `expr.hpp` (`MIT`) directly onto `Image`'s RGBA buffer; replace the 4 `MagickWand` filter calls (`blur`, `sharpen`, `edges`, `resize`) with Skia (`SkImageFilters`, `SkPixmap::scalePixels`) + 3×3 Sobel and `libtiff` (`BSD`). |
| **3D Scene Graph, Primitives, PBR + Shadow Rasterizer** | `lmvideo/src/scene3d.{hpp,cpp}` (consolidated from `lmfilament/cpp/mesh.cpp` + `preview.cpp` + `lmmagnum/cpp/render.cpp`) | `MIT` (own code) + `Unlicense`/`MIT` (`stb_image`, `stb_image_write`, `cgltf`) | **No** | **In-Core** | Replaces Google Filament (`Apache-2.0`, 16 MB noop stack) and Magnum/Corrade (`MIT`, 3 MB) with ~950 LOC of zero-dep `MIT` C++17. |
| **3D CSG Mesh Booleans & 2D-to-3D Extrusion** | `Manifold` (`elalish/manifold`) + `Clipper2` | `Apache-2.0` (`Manifold`) + `BSL-1.0` (`Clipper2`) | **No** | **In-Core** | Provides in-core 3D mesh `union` / `difference` / `intersection`, polygon extrusion, and lathe (~150 KB static) without OCCT. |
| **Exact NURBS / B-Rep CAD, Fillets, STEP / IGES / HLR** | OpenCascade (`OCCT 7.8`, 75 static archives in `lmcad`) | `LGPL-2.1` | **Yes** — static linking triggers **LGPL-2.1 §6a relink-archive duties** (`lmcad-relink.tar.gz`) + 32 MB size | **External** (`lmcad` repo/binary) | **In-Core**: `Manifold` (`Apache-2.0`) for mesh CSG/extrusion + `mesh_stl()`/`mesh_obj()`/`mesh_gltf()` loader. **External**: `lmcad` invoked as separate `_lmcode_ cli="lmcad"` block exporting `.stl`/`.obj`/`.glb`. |
| **Offline Ray-Traced Path Tracing & Modifiers** | Blender 4.x / Cycles (`lmblender`) | `GPL-3.0-or-later` | **Yes** — viral **GPL-3.0** + 124 MB external app | **External** (`lmblender` repo/binary) | **In-Core**: Cook-Torrance GGX + PCF shadow-map CPU rasterizer (`MIT`) + optional **`Intel Embree`** (`Apache-2.0`) / **`bvh`** (`MIT`) for ray-cast AO/shadows. **External**: `lmblender` via `.glb` scene handoff. |
| **Video Container Muxing & WebM / AV1 / VP9 Encoding** | FFmpeg (`libavcodec`, `libavformat`, `libswscale`) | `LGPL-2.1+` (or `GPL-2.0+` with `x264`/`x265`) | **Yes** — static `libav*` imposes **LGPL-2.1 §6a relink duties**; `x264`/`x265` are **GPL-2.0+** | **External** (`ffmpeg` CLI via stdin pipe) | **In-Core**: **`libvpx`** (`BSD-3-Clause` + Google VP8/VP9 patent grant) + **`SVT-AV1` / `libaom`** (`BSD-2-Clause` + AOMedia AV1 patent grant) + **`libwebm`** (`BSD-3-Clause` WebM/MKV muxer) + **`libopus`** (`BSD-3-Clause` audio) + **`msf_gif` / `libwebp` / `libpng`** (`MIT`/`BSD-3`/`Zlib` for GIF/WebP/APNG). **External**: user-installed `ffmpeg` spawned via `popen` (`video.backend("builtin" \| "ffmpeg")`). |
| **H.264 / HEVC Video Codecs** | `x264` (`GPL-2.0`), `OpenH264` (`BSD-2-Clause` source) | `GPL-2.0` / MPEG-LA patent pool | **Yes** — H.264/HEVC carry patent royalties when shipped as static binaries; Cisco's `OpenH264` patent umbrella covers **only** runtime-downloaded Cisco prebuilt `.so`/`.dll`/`.dylib` | **External** (system `ffmpeg`, OS hardware encoder, or runtime-dlopened Cisco plugin) | **In-Core**: Royalty-free **VP9 (`libvpx`, `BSD-3-Clause`)** and **AV1 (`libaom`/`SVT-AV1`, `BSD-2-Clause`)** in `.webm`/`.mp4` (`minimp4.h`, `MIT`), plus OS-native zero-royalty hardware APIs (`VideoToolbox` on macOS, `MediaFoundation` on Windows) and optional runtime `dlopen` of Cisco's official `libopenh264` binary. |
| **Bundled Fonts (2D Text & 3D Glyph Extrusion)** | System fonts or GPL fonts (e.g. legacy Liberation 1.x `GPLv2+font-exception`) | Varies | **Yes** if GPL font or non-redistributable system font (`Arial`/`Calibri`) | **In-Core** (permissive fonts only) | Bundle **Google Croscore (`Arimo`, `Tinos`, `Cousine` — `Apache-2.0`)** or **Liberation 2.1.5 / Carlito / Caladea / DejaVu (`OFL-1.1` / Bitstream Vera permissive)** for metric-compatible deterministic text. |

---

## 2. Unified Language & Schema Design (`schema/lmvideo.dsl.json` v3)

### 2.1 The Single Coherent Mental Model (Not a Bundle of Renamed Hosts)

The consolidated product is **one binary, one schema, and one mental model** built around **three core types** that every domain (image processing, 2D vector drawing/plotting, 3D rendering, and video) shares without temp-file round-trips:

1. **`Image` (Unified Pixel & Frame Buffer — merges `lmvideo.Image`, `lmvideo.Surface`, and `lmimg.Image`)**:
   - **One raster type everywhere**: `image("photo.jpg")`, `image_create(w, h, fill)`, `image_pattern(w, h, r, g, b, a)`, `image_hald(level)`, `canvas.to_image()`, `scene3d.render_image(w, h)`, and `doc.to_image(scale)` all return the **same `Image` type**.
   - **Bidirectional 2D/3D drawing on any `Image`**: calling `img.canvas() -> Canvas` opens a full Skia 2D `Canvas` backed by `img`'s pixels (replacing both `lmvideo.Surface` and `lmimg`'s crude 4-method `Image.rect/circle/line/text`).
   - **First-class `lmimg` filters, grading, warps, compositing, and QA metrics on every `Image` and video frame**: `.resize`, `.crop`, `.rotate`, `.flip`, `.perspective`, `.lens`, `.levels`, `.curves`, `.curves_rgb`, `.hsl`, `.channel_mix`, `.clut`, `.colormap`, `.grayscale`, `.sepia`, `.invert`, `.threshold`, `.normalize`, `.equalize`, `.blur`, `.sharpen`, `.unsharp`, `.edges`, `.morphology`, `.vignette`, `.tilt_shift`, `.heal`, `.blend`, `.mask`, `.selection`, `.ssim`, `.psnr`, `.mean`, `.stddev`, `.min`, `.max`, `.histogram`, `.save`.
2. **`Scene` (Unified 2D + 3D + Layout Composition — merges `lmvideo`, `lmdraw`, `lmmagnum`, `lmfilament`, and `lmimg.Montage`/`Layers`)**:
   - **`Canvas`** is the active 2D drawing surface (still image, document page, or current video frame).
   - **`Scene3D`** is a retained 3D world (`Node3D`, `Mesh3D`, `Material3D`, `Texture3D`, `Light3D`, `Camera3D`) that renders directly into a `Canvas` viewport (`canvas.scene3d(s3d, x, y, w, h)`), embeds inside a `Panel` layout (`panel.add_scene3d()`), or snapshots to an `Image` (`s3d.render_image(w, h)`) for post-processing with `lmimg` filters (`s3d.render_image(1280, 720).tilt_shift(...).vignette(...)`).
   - **3D-to-2D Screen Projection (`s3d.project_x/y/depth/visible`)**: projects 3D world coordinates into 2D `Canvas` coordinates so crisp Skia typography, connectors, and callout cards attach to moving 3D objects.
   - **`Panel`** (`grid`, `pack`, `border`, `flow_h`, `flow_v`, `place`) layouts arrange 2D `Plot`s, `Scene3D` viewports, `Image`s, and diagrams — cleanly subsuming `lmimg.Montage`, `lmimg.Img.panel`, and `lmimg.Layers`.
3. **`Timeline` (`Video` — merges `lmvideo.Video` and `lmimg.Animation`)**:
   - Drives either procedural frame loops (`while (video.next_frame()) { ... }`, where `canvas` is the current frame and can be post-processed via `canvas.to_image().blur(...)`) or explicit frame assembly (`video.add_frame(img, delay_ms)`, replacing `lmimg.Animation`), outputting `.mp4`, `.webm`, `.gif`, `.apng`, or `.webp`.

**Product Name Candidates** (for the single all-in-one binary/host):
- **`lmstudio`** *(recommended if renaming)*: conveys an all-in-one visual studio for images, 2D graphics/plots, 3D scenes, and video (unlike `lmvideo`, which sounds video-only).
- **`lmcanvas`** / **`lmmedia`**: domain-neutral alternatives emphasizing the shared composition surface.
- **`lmvideo`** *(recommended if zero URL/pin churn is prioritized)*: keeps existing `lmgallery` pins and release workflows intact while expanding the product scope.

### 2.2 Context Variables & Top-Level Constructors

| Entry Point | Kind | Signature | Description |
| :--- | :--- | :--- | :--- |
| `canvas` | Context var | `Canvas` | Active 2D Skia drawing surface (frame buffer in video mode, image buffer in still mode) |
| `video` | Context var | `Video` | Frame timeline controller, easing/spring library, and FFmpeg pipe encoder |
| `out` | Context var | `Output` | Result emission (`out.emit_text(...)`, `out.set_metric(...)`) |
| `paint()` | Function | `() -> Paint` | Create a 2D Skia style/brush |
| `path()` | Function | `() -> Path` | Create a 2D vector path |
| `font()` / `font_Sub(...)` | Function | `(...) -> Font` | Create a 2D typeface/font handle |
| `surface(w, h)` | Function | `(int, int) -> Surface` | Offscreen 2D raster surface |
| `document(w, h)` | Function | `(float, float) -> Document` | Display-list vector recorder (`SkPicture`) for multi-DPI PNG, SVG, PDF, SKP |
| `pdf_document(path)` | Function | `(string) -> PdfDocument` | Multi-page vector PDF writer |
| `image(path)` / `svg(path)` | Function | `(string) -> Image / Svg` | Load raster image or vector SVG |
| **`scene3d()`** | Function | `() -> Scene3D` | **New**: Create a retained 3D scene |
| **`material3d()`** | Function | `() -> Material3D` | **New**: Create a PBR material (`color`, `metallic`, `roughness`, `emissive`, `opacity`, `wireframe`, `texture`) |
| **`texture3d(path)`** | Function | `(string) -> Texture3D` | **New**: Load PNG/JPEG texture with automatic mipmap chain |
| **`texture3d_checker(...)`** | Function | `(int, int, int, string, string) -> Texture3D` | **New**: Procedural checkerboard texture (`w, h, cell_px, hex_a, hex_b`) |
| **`texture3d_noise(...)`** | Function | `(int, int, float, int) -> Texture3D` | **New**: Procedural FBM Perlin noise texture (`w, h, scale, seed`) |
| **`texture3d_gradient(...)`** | Function | `(int, int, string, string, bool) -> Texture3D` | **New**: Procedural linear gradient texture (`w, h, hex_a, hex_b, vertical`) |
| **`mesh_box(sx, sy, sz)`** | Function | `(float, float, float) -> Mesh3D` | **New**: Axis-aligned box mesh centered at origin |
| **`mesh_sphere(r, rings, segs)`** | Function | `(float, int, int) -> Mesh3D` | **New**: UV sphere mesh |
| **`mesh_icosphere(r, subdiv)`** | Function | `(float, int) -> Mesh3D` | **New**: Geodesic icosphere mesh (`subdiv` 0..5) |
| **`mesh_cylinder(r, h, segs)`** | Function | `(float, float, int) -> Mesh3D` | **New**: Capped cylinder along Y axis |
| **`mesh_cone(r, h, segs)`** | Function | `(float, float, int) -> Mesh3D` | **New**: Capped cone along Y axis |
| **`mesh_capsule(r, h, segs)`** | Function | `(float, float, int) -> Mesh3D` | **New**: Hemisphere-capped cylinder along Y axis |
| **`mesh_plane(w, d, nx, nz)`** | Function | `(float, float, int, int) -> Mesh3D` | **New**: Subdivided ground/grid plane in XZ |
| **`mesh_torus(R, r, maj, min)`** | Function | `(float, float, int, int) -> Mesh3D` | **New**: Torus in XZ plane (`R` major, `r` minor radius) |
| **`mesh_ring(r_in, r_out, h, segs)`** | Function | `(float, float, float, int) -> Mesh3D` | **New**: Hollow cylindrical ring / washer (`lmfilament` parity) |
| **`mesh_tube(x0,y0,z0, x1,y1,z1, r, segs)`** | Function | `(float*7, int) -> Mesh3D` | **New**: Oriented cylindrical strut/bond between two 3D points (`lmfilament.tube_between` parity) |
| **`mesh_text3d(text, size, depth)`** | Function | `(string, float, float) -> Mesh3D` | **New**: Extruded 3D mesh from Skia TrueType glyph outlines (with voxel fallback option) |
| **`mesh_obj(path)` / `mesh_stl(path)`** | Function | `(string) -> Mesh3D` | **New**: Load Wavefront `.obj` or binary/ASCII `.stl` (e.g., exported from `lmcad`) |

### 2.3 Unified 3D Type & Method Reference

All 3D types use **one canonical convention** across the unified schema (while legacy `lmmagnum`/`lmfilament` compat shims adapt any differences automatically):
- **Coordinate system**: Right-handed, `+Y` up, `+X` right, `+Z` toward viewer.
- **Angles**: Degrees for Euler rotations (`rx, ry, rz` intrinsic Z-Y-X) and camera vertical `fov_deg` (matching `lmvideo`'s existing `Canvas.rotate(deg)` and `lmmagnum`'s `Node.rotate(rx, ry, rz)`).
- **Colors**: Standard `#RRGGBB` / `#RRGGBBAA` hex strings (matching all 201 existing `lmvideo` methods) **plus** `(r, g, b)` float overloads (`0.0..1.0`) for shader/math convenience.

```
Type: Scene3D
  # Environment & Background
  set_background(color: string) -> Scene3D                # Solid background ("transparent" / "#00000000" composites cleanly over 2D Canvas!)
  set_sky_gradient(zenith_hex: string, horizon_hex: string, ground_hex: string) -> Scene3D
  set_ambient(color_hex: string, intensity: float) -> Scene3D
  set_shadows(enabled: bool) -> Scene3D                   # 1024x1024 directional shadow map with 3x3 PCF
  set_ssaa(samples: int) -> Scene3D                       # 1 (fast), 2 (2x2 default), 4 (4x4 supersampling)
  set_exposure(aperture: float, shutter: float, iso: float) -> Scene3D
  set_tone_mapping(mode: string) -> Scene3D               # "aces" | "filmic" | "reinhard" | "linear"
  set_grid_floor(size: float, step: float, color_hex: string) -> Scene3D

  # Camera
  camera() -> Camera3D
  set_camera_look_at(ex: float, ey: float, ez: float, tx: float, ty: float, tz: float, ux: float, uy: float, uz: float) -> Scene3D
  set_camera_orbit(azimuth_deg: float, elevation_deg: float, distance: float, tx: float, ty: float, tz: float) -> Scene3D
  set_camera_perspective(fov_deg: float, near_z: float, far_z: float) -> Scene3D
  set_camera_ortho(half_width: float, near_z: float, far_z: float) -> Scene3D

  # Lights
  add_light(kind: string, color_hex: string, intensity: float) -> Light3D   # kind: "directional" | "point" | "spot"
  add_sun(dx: float, dy: float, dz: float, color_hex: string, intensity: float) -> Light3D
  add_point_light(x: float, y: float, z: float, color_hex: string, intensity: float, range: float) -> Light3D
  clear_lights() -> Scene3D

  # Scene Graph & One-Shot Primitive Builders
  add_node(name: string) -> Node3D
  add_mesh(mesh: Mesh3D, mat: Material3D) -> Node3D
  add_box(sx: float, sy: float, sz: float, mat: Material3D) -> Node3D
  add_sphere(r: float, mat: Material3D) -> Node3D
  add_cylinder(r: float, h: float, mat: Material3D) -> Node3D
  add_cone(r: float, h: float, mat: Material3D) -> Node3D
  add_capsule(r: float, h: float, mat: Material3D) -> Node3D
  add_plane(w: float, d: float, mat: Material3D) -> Node3D
  add_torus(major_r: float, minor_r: float, mat: Material3D) -> Node3D
  add_tube(x0: float, y0: float, z0: float, x1: float, y1: float, z1: float, r: float, mat: Material3D) -> Node3D
  add_text3d(text: string, size: float, depth: float, mat: Material3D) -> Node3D
  clear_nodes() -> Scene3D

  # 3D -> 2D Screen-Space Projection (relative to most recent viewport or explicit rect)
  project_x(x: float, y: float, z: float) -> float
  project_y(x: float, y: float, z: float) -> float
  project_depth(x: float, y: float, z: float) -> float
  project_visible(x: float, y: float, z: float) -> bool
  project_x_in(x: float, y: float, z: float, vx: float, vy: float, vw: float, vh: float) -> float
  project_y_in(x: float, y: float, z: float, vx: float, vy: float, vw: float, vh: float) -> float

  # Introspection & Standalone Outputs
  node_count() -> int
  vertex_count() -> int
  triangle_count() -> int
  render_image(w: int, h: int) -> Image                   # Rasterize to an in-memory Skia Image
  render_png(path: string, w: int, h: int) -> bool        # Standalone PNG output (lmmagnum/lmfilament parity)
  export_stl(path: string) -> bool                        # Binary STL export of transformed scene meshes
  export_obj(path: string) -> bool                        # Wavefront OBJ export
  export_ply(path: string) -> bool                        # Stanford PLY export
```

```
Type: Node3D
  set_position(x: float, y: float, z: float) -> Node3D
  translate(dx: float, dy: float, dz: float) -> Node3D
  set_rotation(rx_deg: float, ry_deg: float, rz_deg: float) -> Node3D
  rotate(drx_deg: float, dry_deg: float, drz_deg: float) -> Node3D
  set_scale(sx: float, sy: float, sz: float) -> Node3D
  set_uniform_scale(s: float) -> Node3D
  look_at(tx: float, ty: float, tz: float) -> Node3D
  set_material(mat: Material3D) -> Node3D
  set_visible(visible: bool) -> Node3D
  set_cast_shadows(cast: bool) -> Node3D
  set_receive_shadows(receive: bool) -> Node3D
  add_child(name: string) -> Node3D                       # Hierarchical parent-child transforms
  add_child_mesh(mesh: Mesh3D, mat: Material3D) -> Node3D
```

```
Type: Material3D
  set_color(hex: string) -> Material3D
  set_color_rgb(r: float, g: float, b: float) -> Material3D
  set_metallic(m: float) -> Material3D
  set_roughness(r: float) -> Material3D
  set_reflectance(refl: float) -> Material3D
  set_specular(s: float) -> Material3D
  set_emissive(hex: string, strength: float) -> Material3D
  set_opacity(alpha: float) -> Material3D
  set_wireframe(enabled: bool) -> Material3D
  set_flat_shading(flat: bool) -> Material3D
  set_double_sided(two_sided: bool) -> Material3D
  set_texture(tex: Texture3D) -> Material3D
  set_uv_scale(su: float, sv: float) -> Material3D
```

### 2.4 Additions to Existing `lmvideo` 2D Types (`Canvas`, `Panel`, `LayoutItem`)

Only **9 methods** need to be added to `lmvideo`'s existing 2D types to achieve both seamless 3D embedding and 100% `lmdraw` parity:

| Target Type | New Method | Signature | Purpose |
| :--- | :--- | :--- | :--- |
| `Canvas` | `scene3d` | `(scene: Scene3D, x: float, y: float, w: float, h: float) -> void` | Rasterize `scene` into `(x, y, w, h)` on the canvas (alpha-composited if background is `"transparent"`), recording `(x, y, w, h)` as the active projection viewport for `scene.project_x/y(...)`. |
| `Panel` | `add_scene3d` | `() -> LayoutItem` | Add a managed `Scene3D` viewport cell to a `pack` / `grid` / `border` / `flow` / `place` layout panel. |
| `LayoutItem` | `scene3d` | `() -> Scene3D` | Retrieve the `Scene3D` owned by a layout item (exactly parallel to `item.plot() -> Plot` and `item.panel() -> Panel`). |
| `Canvas` | `arrow` | `(x1: float, y1: float, x2: float, y2: float, head_size: float, paint: Paint) -> void` | Direct 2D arrow helper (`lmdraw` parity). |
| `Canvas` | `polyline` | `(points: string, paint: Paint) -> void` | Semicolon-separated `"x1,y1;x2,y2;..."` polyline helper (`lmdraw` parity). |
| `Canvas` | `axes` | `(x: float, y: float, w: float, h: float, xmin: float, xmax: float, ymin: float, ymax: float, paint: Paint, font: Font) -> void` | Immediate-mode linear axes box (`lmdraw` parity). |
| `Canvas` | `log_axes` | `(x: float, y: float, w: float, h: float, xmin: float, xmax: float, ymin: float, ymax: float, xlog: bool, ylog: bool, paint: Paint, font: Font) -> void` | Immediate-mode log/symlog axes box (`lmdraw` parity). |
| `Canvas` | `legend` | `(x: float, y: float, labels: string, colors: string, font: Font) -> void` | Immediate-mode legend box (`lmdraw` parity). |
| `Canvas` | `load_font` | `(path: string, size: float) -> Font` | Load TTF/OTF font directly from Canvas (`lmdraw` parity). |
| `Canvas` | `to_image` | `() -> Image` | Snapshot the current `Canvas` (or current video frame) into a mutable/filterable `Image`. |

### 2.5 Folding `lmimg` into the Unified Model (`Image`, `Curve`, `Canvas`, `Panel`, `Video`)

Every one of `lmimg`'s 6 types and 55 methods maps cleanly into the unified schema without keeping a separate `Img` context root (except inside the legacy `lmvideo img` / `argv[0] == "lmimg"` compatibility adapter):

| `lmimg` Type / Method Group | Methods in `lmimg` (55 total) | Target in Unified Schema | How It Works in the Single Coherent Model |
| :--- | :--- | :--- | :--- |
| **`Img` Constructors** (4) | `img.open(path)`, `img.canvas(w,h,r,g,b,a)`, `img.pattern(w,h,r,g,b,a)`, `img.hald(level)` | Top-level `image(path)`, `image_create(w,h,hex)`, `image_pattern(w,h,r,g,b,a)`, `image_hald(level)` | Any raster file, procedural expression, Hald CLUT, `canvas.to_image()`, or `s3d.render_image(w,h)` produces the same `Image` handle. |
| **`Image` Geometry & Warps** (7) | `width`, `height`, `copy`, `resize(w,h)`, `crop(x,y,w,h)`, `rotate(deg,r,g,b,a)`, `flip(horiz)`, `perspective(tlx..bly)`, `lens(k)` | **`Image`** methods (chainable, returning `Image`) | Operates in-place on `Image`'s RGBA buffer; usable on loaded photos, 3D renders, or video frames. |
| **`Image` Color & Tone Grading** (12) | `levels(b,g,w)`, `curves(c)`, `curves_rgb(r,g,b)`, `threshold(t)`, `invert()`, `normalize()`, `equalize()`, `colormap(name)`, `clut(hald)`, `hsl(h,s,l)`, `channelmix(m0..m8)`, `grayscale()`, `sepia(s)` | **`Image`** methods + **`Curve`** (`curve().point(x,y)`) | Pure C++17 pixel operators from `lmimg/cpp/image.cpp` (zero ImageMagick needed). Color-grade a `Scene3D` render or video frame with one chain: `s3d.render_image(w,h).clut(lut).vignette(r,s)`. |
| **`Image` Spatial Filters & Retouch** (8) | `blur(r,s)`, `sharpen(r,s)`, `edges(r)`, `unsharp(r,s,amt,th)`, `vignette(r,s)`, `tilt_shift(r,a,b)`, `morphology(op,r)`, `heal(x,y,w,h,r)` | **`Image`** methods | `blur`/`sharpen` use Skia `SkImageFilters` + premultiplied alpha; `unsharp`, `vignette`, `tilt_shift`, `morphology`, and least-squares plane `heal` port directly from `lmimg/cpp/image.cpp`. |
| **`Image` Masking, Blending & Layers** (6) | `Image.blend(over,mode,op,x,y)`, `Image.mask(m)`, `Image.selection(x,y,w,h)`, plus `Layers.add`, `Layers.masked`, `Layers.render` | **`Image.blend`**, **`Image.mask`**, **`Image.selection`** + **`Canvas`** blend modes | `Image.blend` supports all 10 `lmimg` modes (`over`, `multiply`, `screen`, `overlay`, `difference`, `darken`, `lighten`, `addition`, `subtract`, `divide`); `Layers` is subsumed by chaining `.blend(...)` or drawing onto `img.canvas()`. |
| **`Image` 2D Drawing & Text** (5) | `Image.rect`, `Image.circle`, `Image.line`, `Image.text`, `Img.text_width` | **`img.canvas() -> Canvas`** (`Canvas.rect`, `circle`, `line`, `text`, `Font.measure`) | Replaces `lmimg`'s single embedded-font ASCII drawer with the full Skia `Canvas` (anti-aliased vector paths, plots, diagrams, `Scene3D` viewports, and full Unicode shaping). |
| **`Montage` & `Img.panel`** (3) | `img.montage()`, `Montage.add(img)`, `Montage.render(...)`, `img.panel(a,b,gap)` | **`Panel.grid(cols, rows, gx, gy)`** + **`Panel.add_image(img)`** | `lmvideo`'s `Panel` layout manager already supports grid, border, flow, and pack layouts with titles and padding, plus a 1-liner `image_montage(cols, gap, bg)` helper. |
| **`Animation`** (3) | `img.animation()`, `Animation.add(img, delay_cs)`, `Animation.save(path)`, `Animation.size()` | **`Video`** (`video.add_frame(img, delay_ms)`, `video.save(path)`) | Unifies frame-by-frame `Animation` with `Video` so scripts can output GIF, APNG, WebP, WebM, or MP4 from the same timeline. |
| **`Image` Inspection, QA & I/O** (11) | `pixel`, `set_pixel`, `mean`, `stddev`, `min`, `max`, `ssim(other)`, `psnr(other)`, `histogram(path)`, `metadata`, `property`, `save(path)` | **`Image`** methods | Gives every 2D drawing, 3D render, and video frame built-in `ssim()` / `psnr()` regression metrics and multi-format export (`PNG`, `JPEG`, `WebP`, `GIF`, `BMP`, `TIFF`, `PNM`). |

---

## 3. Six Complete Task-Oriented Example Scripts (Still Image & Video)

### Example 1 — Still Image: 3D Molecular Dimer with Projected 2D Skia Callouts & Bond Table

Demonstrates how `Scene3D` and 2D Skia typography work together on a single `Canvas`: the 3D engine renders shadowed spheres and covalent bond struts with a transparent background over a dark gradient card, and `s3d.project_x/y(...)` anchors crisp 2D callout connectors and Ångström bond labels directly to the 3D atom centers.

```lms
_lmcode_ cli="lmvideo" {
    canvas.resize(1280, 720);
    canvas.clear("#0B0F19");

    let f_title = font_Sub("Sans", 24.0, true, false);
    let f_body  = font("Sans", 14.0);
    let f_mono  = font("Mono", 13.0);
    let p_text  = paint().color("#E2E8F0");
    let p_muted = paint().color("#94A3B8");
    let p_cyan  = paint().color("#38BDF8").stroke(true).stroke_width(2.0);

    canvas.text("Cisplatin-DNA Guanine Crosslink (3D Structure + 2D Callouts)", 40.0, 44.0, f_title, p_text);
    canvas.text("3D PBR + shadow-mapped geometry with screen-projected 2D Skia typography", 40.0, 68.0, f_body, p_muted);

    # 1. Build the 3D molecular scene
    let s3d = scene3d()
        .set_background("transparent")
        .set_ambient("#1E293B", 0.35)
        .set_shadows(true)
        .set_camera_orbit(32.0, 22.0, 6.2, 0.0, 0.0, 0.0);
    s3d.add_sun(-0.6, -1.0, -0.5, "#FFFBEB", 1.3);
    s3d.add_point_light(2.5, 2.0, 2.0, "#38BDF8", 0.6, 10.0);

    let mat_pt   = material3d().set_color("#E2E8F0").set_metallic(0.85).set_roughness(0.18);
    let mat_n    = material3d().set_color("#3B82F6").set_metallic(0.15).set_roughness(0.35);
    let mat_cl   = material3d().set_color("#22C55E").set_metallic(0.10).set_roughness(0.40);
    let mat_bond = material3d().set_color("#64748B").set_metallic(0.50).set_roughness(0.30);

    # Platinum center at origin, two Cl ligands, two ammine N ligands (square planar)
    s3d.add_sphere(0.48, mat_pt).set_position(0.0, 0.0, 0.0);
    s3d.add_sphere(0.38, mat_cl).set_position(-1.45, 0.0,  1.10);
    s3d.add_sphere(0.38, mat_cl).set_position( 1.45, 0.0,  1.10);
    s3d.add_sphere(0.34, mat_n ).set_position(-1.25, 0.25, -1.05);
    s3d.add_sphere(0.34, mat_n ).set_position( 1.25, -0.20, -1.05);

    # Covalent coordination bonds
    s3d.add_tube(0.0, 0.0, 0.0, -1.45, 0.0,  1.10, 0.09, mat_bond);
    s3d.add_tube(0.0, 0.0, 0.0,  1.45, 0.0,  1.10, 0.09, mat_bond);
    s3d.add_tube(0.0, 0.0, 0.0, -1.25, 0.25, -1.05, 0.09, mat_bond);
    s3d.add_tube(0.0, 0.0, 0.0,  1.25, -0.20, -1.05, 0.09, mat_bond);

    # Render 3D viewport on the left (820x580)
    canvas.scene3d(s3d, 40.0, 96.0, 820.0, 580.0);

    # 2. Project 3D atom coordinates into 2D canvas space for sharp callout annotations
    let pt_x = s3d.project_x(0.0, 0.0, 0.0);
    let pt_y = s3d.project_y(0.0, 0.0, 0.0);
    let cl_x = s3d.project_x(1.45, 0.0, 1.10);
    let cl_y = s3d.project_y(1.45, 0.0, 1.10);
    let n_x  = s3d.project_x(-1.25, 0.25, -1.05);
    let n_y  = s3d.project_y(-1.25, 0.25, -1.05);

    canvas.arrow(pt_x + 70.0, pt_y - 80.0, pt_x + 12.0, pt_y - 12.0, 8.0, p_cyan);
    canvas.note(pt_x + 75.0, pt_y - 110.0, 210.0, 52.0, "Pt(II) d8 center\nd(Pt-N) = 2.01 A", "#1E293B", "#38BDF8", f_mono);

    canvas.arrow(cl_x + 65.0, cl_y + 55.0, cl_x + 14.0, cl_y + 10.0, 8.0, p_cyan);
    canvas.note(cl_x + 70.0, cl_y + 35.0, 215.0, 52.0, "Cl- leaving ligand\nd(Pt-Cl) = 2.31 A", "#1E293B", "#22C55E", f_mono);

    canvas.arrow(n_x - 60.0, n_y - 60.0, n_x - 10.0, n_y - 10.0, 8.0, p_cyan);
    canvas.note(n_x - 250.0, n_y - 95.0, 185.0, 52.0, "NH3 carrier ligand\nAngle N-Pt-N = 91.8 deg", "#1E293B", "#3B82F6", f_mono);

    # 3. Right-hand 2D bond energy plot in the same Canvas
    let plt = canvas.plot(890.0, 110.0, 350.0, 540.0);
    plt.set_title("Pt-Cl Hydrolysis Barrier")
       .set_xlabel("Reaction Coordinate (A)")
       .set_ylabel("Delta G (kcal/mol)")
       .set_theme("dark");
    let s_rxn = plt.add_series("Aquation Path");
    s_rxn.set_color("#38BDF8").set_width(2.5);
    s_rxn.add(0.0, 0.0); s_rxn.add(0.5, 8.4); s_rxn.add(1.0, 19.8);
    s_rxn.add(1.4, 24.1); s_rxn.add(1.9, 14.2); s_rxn.add(2.5, 3.6);
    plt.draw();

    canvas.save_png("build/01-molecule-3d-callouts.png");
}
```

---

### Example 2 — Still Image: 2×2 Engineering Dashboard (`Panel` Layout Mixing 3D Viewport, 2D Plot, Heatmap, and Architecture Diagram)

Demonstrates `Panel.add_scene3d()` inside `lmvideo`'s existing `grid(2, 2)` layout manager so 3D scenes participate in automatic padding, borders, titles, and aspect-ratio management alongside 2D `Plot`s and `Heatmap`s.

```lms
_lmcode_ cli="lmvideo" {
    canvas.resize(1400, 900);
    canvas.clear("#0F172A");

    let root = canvas.panel(20.0, 20.0, 1360.0, 860.0);
    root.grid(2, 2, 18.0, 18.0).set_padding(12.0);

    # Cell (0,0): 3D Cantilever Truss Viewport
    let cell_3d = root.add_scene3d();
    cell_3d.set_title("1. 3D Modal Deflection Mesh (Mode 1: 48.2 Hz)").set_bg("#1E293B");
    let s3d = cell_3d.scene3d()
        .set_background("#0B1120")
        .set_shadows(true)
        .set_grid_floor(8.0, 1.0, "#334155")
        .set_camera_orbit(38.0, 24.0, 7.5, 0.0, 0.6, 0.0);
    s3d.add_sun(-0.5, -1.0, -0.4, "#FFFFFF", 1.25);

    let m_steel  = material3d().set_color("#94A3B8").set_metallic(0.8).set_roughness(0.25);
    let m_stress = material3d().set_color("#F97316").set_metallic(0.4).set_roughness(0.35);
    for (let i = 0; i < 6; i = i + 1) {
        let x0 = -2.5 + float(i) * 1.0;
        let x1 = x0 + 1.0;
        let y0 = 0.05 * float(i * i);
        let y1 = 0.05 * float((i + 1) * (i + 1));
        let mat = m_steel;
        if (i >= 3) { mat = m_stress; }
        s3d.add_tube(x0, y0, -0.4, x1, y1, -0.4, 0.07, mat);
        s3d.add_tube(x0, y0,  0.4, x1, y1,  0.4, 0.07, mat);
        s3d.add_tube(x0, y0 + 0.8, -0.4, x1, y1 + 0.8, -0.4, 0.07, mat);
        s3d.add_tube(x0, y0 + 0.8,  0.4, x1, y1 + 0.8,  0.4, 0.07, mat);
        s3d.add_tube(x0, y0, -0.4, x1, y1 + 0.8, -0.4, 0.05, mat);
        s3d.add_tube(x0, y0,  0.4, x1, y1 + 0.8,  0.4, 0.05, mat);
    }

    # Cell (0,1): 2D Frequency-Response Plot
    let cell_frf = root.add_plot();
    let plt_frf = cell_frf.plot();
    plt_frf.set_title("2. Tip Accelerance FRF |H(f)|")
           .set_xlabel("Frequency (Hz)")
           .set_ylabel("Magnitude (dB)")
           .set_theme("dark");
    let s_frf = plt_frf.add_series("FEM Mode Superposition");
    s_frf.set_color("#38BDF8").set_width(2.2);
    for (let f = 10; f <= 120; f = f + 2) {
        let df1 = float(f) - 48.2;
        let df2 = float(f) - 96.5;
        let mag = 20.0 / sqrt(df1 * df1 + 4.0) + 12.0 / sqrt(df2 * df2 + 6.0);
        s_frf.add(float(f), 20.0 * log10(mag));
    }

    # Cell (1,0): 2D Von Mises Stress Heatmap with Marching-Squares Contours
    let cell_hm = root.add_plot();
    let plt_hm = cell_hm.plot();
    plt_hm.set_title("3. Root Flange Stress Distribution (MPa)")
          .set_xlabel("Width X (mm)")
          .set_ylabel("Thickness Y (mm)")
          .set_theme("dark");
    let hm = plt_hm.add_heatmap(24, 24, -50.0, 50.0, -20.0, 20.0);
    hm.set_colormap("inferno").set_contours(6, "#FFFFFF");
    for (let iy = 0; iy < 24; iy = iy + 1) {
        for (let ix = 0; ix < 24; ix = ix + 1) {
            let nx = (float(ix) - 11.5) / 11.5;
            let ny = (float(iy) - 11.5) / 11.5;
            let sigma = 180.0 * abs(ny) * (1.2 - 0.4 * nx) + 45.0 * exp(-4.0 * (nx * nx + ny * ny));
            hm.set_cell(ix, iy, sigma);
        }
    }

    # Cell (1,1): Summary Verification Table / Diagram Card
    let cell_info = root.add_text("4. Structural Margin Summary\n\nPeak Von Mises: 214.6 MPa\nYield Allow (Al-7075): 503.0 MPa\nSafety Factor: 2.34 (PASS)\nMode 1 Margin: +18.2% above 40 Hz spec");
    cell_info.set_bg("#1E293B").set_fg("#E2E8F0").set_font_size(16.0);

    root.draw();
    canvas.save_png("build/02-engineering-dashboard-2x2.png");
}
```

---

### Example 3 — Video: 3D Kepler Orbital Transfer with Synchronized Live 2D Phase/Energy Plot

Demonstrates a single `while (video.next_frame())` loop driving both a retained `Scene3D` (mutating spacecraft position, solar panel orientation, and orbit camera per frame) and a synchronized 2D `Plot` + telemetry HUD.

```lms
_lmcode_ cli="lmvideo" {
    canvas.resize(1280, 720);
    video.configure(180, 30, "build/03-orbital-transfer.mp4");

    # Retained 3D scene created once outside the frame loop
    let s3d = scene3d()
        .set_background("#050814")
        .set_ambient("#1E293B", 0.25)
        .set_shadows(true);
    s3d.add_sun(-0.8, -0.5, -0.6, "#FFF7ED", 1.6);

    let mat_earth = material3d().set_color("#2563EB").set_roughness(0.55).set_metallic(0.1);
    let mat_craft = material3d().set_color("#F59E0B").set_roughness(0.25).set_metallic(0.85);
    let mat_panel = material3d().set_color("#38BDF8").set_roughness(0.15).set_metallic(0.90);
    let mat_ring  = material3d().set_color("#334155").set_emissive("#38BDF8", 0.35);

    let earth = s3d.add_icosphere(1.15, 3, mat_earth);
    s3d.add_torus(2.2, 0.018, 64, 8, mat_ring);
    s3d.add_torus(3.6, 0.018, 64, 8, mat_ring);

    # Hierarchical spacecraft node with two child solar arrays
    let craft = s3d.add_box(0.22, 0.22, 0.32, mat_craft);
    craft.add_child_mesh(mesh_box(0.85, 0.02, 0.24), mat_panel).set_position(0.0, 0.0, 0.0);

    let f_hud = font_Sub("Mono", 14.0, true, false);
    let p_hud = paint().color("#38BDF8");

    while (video.next_frame()) {
        let u = video.progress();
        let theta = u * 3.14159265;
        # Hohmann transfer ellipse (r_p = 2.2, r_a = 3.6 -> a = 2.9, e = 0.2414)
        let a = 2.9;
        let e = 0.2414;
        let r = a * (1.0 - e * e) / (1.0 + e * cos(theta));
        let cx = r * cos(theta);
        let cz = r * sin(theta);

        earth.set_rotation(0.0, u * 120.0, 23.4);
        craft.set_position(cx, 0.0, cz).set_rotation(0.0, -theta * 57.2958, 0.0);
        s3d.set_camera_orbit(25.0 + u * 35.0, 28.0, 7.8, 0.0, 0.0, 0.0);

        canvas.clear("#050814");
        canvas.scene3d(s3d, 20.0, 20.0, 760.0, 680.0);

        # Project spacecraft 3D position to overlay a 2D tracking reticle & velocity readout
        let sx = s3d.project_x(cx, 0.0, cz);
        let sy = s3d.project_y(cx, 0.0, cz);
        canvas.circle(sx, sy, 14.0, paint().color("#F59E0B").stroke(true).stroke_width(2.0));
        canvas.text("SC-1 r=" + str(round(r * 100.0) / 100.0) + " Re", sx + 18.0, sy - 6.0, f_hud, p_hud);

        # Right side: Live 2D Specific Orbital Energy & Altitude Plot
        let plt = canvas.plot(800.0, 40.0, 450.0, 640.0);
        plt.set_title("Hohmann Transfer Trajectory (r vs True Anomaly)")
           .set_xlabel("True Anomaly (deg)")
           .set_ylabel("Orbital Radius (Re)")
           .set_xlim(0.0, 180.0)
           .set_ylim(1.8, 4.0)
           .set_theme("dark");
        let s_orb = plt.add_series("Radius r(theta)");
        s_orb.set_color("#F59E0B").set_width(2.5);
        let max_step = int(u * 90.0);
        for (let k = 0; k <= max_step; k = k + 1) {
            let ang = float(k) * 2.0 * 0.0174533;
            let rk  = a * (1.0 - e * e) / (1.0 + e * cos(ang));
            s_orb.add(float(k * 2), rk);
        }
        plt.draw();
    }
    video.save("build/03-orbital-transfer.mp4");
}
```

---

### Example 4 — Video: Animated Architecture Diagram with Live 3D Cluster Node Inspection

Demonstrates mixing `lmvideo`/`lmdraw`'s retained diagram vocabulary (`cluster`, `box`, `cylinder`, `connector`, `draw_diagram`) on the left with a live rotating 3D server rack / GPU torus topology (`Scene3D`) on the right.

```lms
_lmcode_ cli="lmvideo" {
    canvas.resize(1280, 720);
    video.configure(120, 30, "build/04-diagram-and-3d-rack.mp4");

    let s3d = scene3d()
        .set_background("#0F172A")
        .set_shadows(true);
    s3d.add_sun(-0.6, -1.0, -0.5, "#FFFFFF", 1.3);

    let mat_chassis = material3d().set_color("#334155").set_metallic(0.75).set_roughness(0.30);
    let mat_active  = material3d().set_color("#22C55E").set_emissive("#22C55E", 0.55);
    let mat_link    = material3d().set_color("#38BDF8").set_metallic(0.50).set_roughness(0.20);

    # 4-blade 3D compute rack
    let b0 = s3d.add_box(1.8, 0.28, 1.2, mat_chassis).set_position(0.0, -0.9, 0.0);
    let b1 = s3d.add_box(1.8, 0.28, 1.2, mat_chassis).set_position(0.0, -0.3, 0.0);
    let b2 = s3d.add_box(1.8, 0.28, 1.2, mat_chassis).set_position(0.0,  0.3, 0.0);
    let b3 = s3d.add_box(1.8, 0.28, 1.2, mat_chassis).set_position(0.0,  0.9, 0.0);
    s3d.add_tube(-0.8, -0.9, 0.62, -0.8, 0.9, 0.62, 0.04, mat_link);
    s3d.add_tube( 0.8, -0.9, 0.62,  0.8, 0.9, 0.62, 0.04, mat_link);

    let f_lbl = font("Sans", 14.0);

    while (video.next_frame()) {
        let u = video.progress();
        let active_idx = int(u * 4.0) % 4;
        b0.set_material(mat_chassis); b1.set_material(mat_chassis);
        b2.set_material(mat_chassis); b3.set_material(mat_chassis);
        if (active_idx == 0) { b0.set_material(mat_active); }
        if (active_idx == 1) { b1.set_material(mat_active); }
        if (active_idx == 2) { b2.set_material(mat_active); }
        if (active_idx == 3) { b3.set_material(mat_active); }

        s3d.set_camera_orbit(30.0 + u * 90.0, 20.0, 4.8, 0.0, 0.0, 0.0);

        canvas.clear("#090D16");

        # Left side: 2D Architecture Diagram
        canvas.cluster("gw", 40.0, 60.0, 620.0, 600.0, "Inference Routing Fabric", "#1E293B", "#475569", f_lbl);
        canvas.box("ing", 80.0, 140.0, 180.0, 70.0, "API Gateway", "#0284C7", "#38BDF8", f_lbl);
        canvas.diamond("sched", 340.0, 135.0, 160.0, 80.0, "Ring Scheduler", "#4F46E5", "#818CF8", f_lbl);
        canvas.cylinder("kv", 340.0, 320.0, 160.0, 90.0, "Distributed KV", "#0D9488", "#2DD4BF", f_lbl);
        canvas.box("workers", 340.0, 490.0, 180.0, 75.0, "Active Blade #" + str(active_idx), "#15803D", "#4ADE80", f_lbl);
        canvas.connector("ing", "sched", "gRPC", "ortho", "#38BDF8", f_lbl);
        canvas.connector("sched", "kv", "prefix hit", "ortho", "#2DD4BF", f_lbl);
        canvas.connector("sched", "workers", "dispatch", "ortho", "#4ADE80", f_lbl);
        canvas.draw_diagram();

        # Right side: Live 3D Rack View highlighting the scheduled blade
        canvas.scene3d(s3d, 700.0, 60.0, 540.0, 600.0);
    }
    video.save("build/04-diagram-and-3d-rack.mp4");
}
```

---

### Example 5 — Multi-Host CAD-to-Video Composition (`lmcad` B-Rep -> `lmvideo` 3D Turntable + GD&T Spec Sheet)

Demonstrates why `lmcad` stays a separate B-Rep host while interoperating seamlessly with `lmvideo`: `lmcad` performs exact OpenCascade B-Rep boolean cuts and constant-radius fillets and exports `build/flange.stl`; `lmvideo` loads `mesh_stl("build/flange.stl")` and renders a shadowed PBR turntable video with 2D engineering callouts.

```lms
# Step 1: Exact B-Rep solid modeling & filleting in lmcad (OpenCascade kernel)
_lmcode_ cli="lmcad" {
    let base   = cylinder(45.0, 12.0);
    let hub    = cylinder(22.0, 34.0);
    let body   = base.fuse(hub).fillet(3.5);
    let bore   = cylinder(12.0, 40.0).translate(0.0, 0.0, -2.0);
    let flange = body.cut(bore).chamfer(1.0);

    # Subtract 6 bolt holes on a 33 mm pitch circle
    for (let i = 0; i < 6; i = i + 1) {
        let ang = float(i) * 60.0 * 0.01745329;
        let hole = cylinder(4.0, 20.0).translate(33.0 * cos(ang), 33.0 * sin(ang), -2.0);
        flange = flange.cut(hole);
    }
    flange.export_stl("build/flange.stl");
    flange.export_step("build/flange.step");
}

# Step 2: Lit PBR 3D turntable + 2D GD&T inspection card in lmvideo
_lmcode_ cli="lmvideo" {
    canvas.resize(1280, 720);
    video.configure(120, 30, "build/05-cad-flange-turntable.mp4");

    let cad_mesh = mesh_stl("build/flange.stl");
    let mat_ti   = material3d().set_color("#CBD5E1").set_metallic(0.88).set_roughness(0.22);

    let s3d = scene3d()
        .set_background("#0B0F17")
        .set_shadows(true)
        .set_grid_floor(140.0, 20.0, "#1E293B");
    s3d.add_sun(-0.6, -1.0, -0.5, "#FFFBEB", 1.35);
    s3d.add_point_light(60.0, 50.0, 60.0, "#38BDF8", 0.55, 250.0);

    let part_node = s3d.add_mesh(cad_mesh, mat_ti).set_rotation(-90.0, 0.0, 0.0);

    let f_hdr  = font_Sub("Sans", 22.0, true, false);
    let f_mono = font("Mono", 14.0);
    let p_wht  = paint().color("#F8FAFC");

    while (video.next_frame()) {
        let u = video.progress();
        part_node.set_rotation(-90.0, u * 360.0, 0.0);
        s3d.set_camera_orbit(35.0, 26.0, 135.0, 0.0, 12.0, 0.0);

        canvas.clear("#0B0F17");
        canvas.scene3d(s3d, 30.0, 30.0, 800.0, 660.0);

        canvas.text("ISO-2768-mM Titanium Drive Flange", 860.0, 64.0, f_hdr, p_wht);
        canvas.note(860.0, 96.0, 380.0, 220.0,
            "Source: lmcad OCCT 7.8 B-Rep\nSTEP: build/flange.step\nMesh: " + str(s3d.triangle_count()) + " triangles\n\nOD: 90.00 +/- 0.05 mm\nBore: 24.00 H7 (+0.021 / 0)\nFillet R: 3.50 mm constant\nBolt PCD: 6x M8 on 66.0 mm",
            "#1E293B", "#38BDF8", f_mono);
    }
    video.save("build/05-cad-flange-turntable.mp4");
}
```

---

### Example 6 — Multi-Format Vector + Raster Report (`Document` + `PdfDocument` from One Scene)

Demonstrates how `Document` (Skia `SkPicture` display-list recorder) combines a high-DPI rasterized 3D viewport (`s3d.render_image(1200, 900)`) with resolution-independent vector 2D plots and typography to produce 1× PNG, 2× Retina PNG, SVG, and PDF from one script.

```lms
_lmcode_ cli="lmvideo" {
    let doc = document(1200.0, 800.0);
    let c   = doc.canvas();
    c.clear("#FFFFFF");

    # 1. Render 3D scene at 2x supersampled resolution into an Image handle
    let s3d = scene3d()
        .set_background("#F8FAFC")
        .set_shadows(true)
        .set_camera_orbit(42.0, 25.0, 5.5, 0.0, 0.0, 0.0);
    s3d.add_sun(-0.5, -1.0, -0.6, "#FFFFFF", 1.3);
    let mat_copper = material3d().set_color("#D97706").set_metallic(0.85).set_roughness(0.20);
    s3d.add_torus(1.4, 0.42, 64, 32, mat_copper);
    let img_3d = s3d.render_image(1100, 1400);
    c.image_rect(img_3d, 30.0, 60.0, 550.0, 700.0);

    # 2. Vector 2D Plot recorded into the same SkPicture display list
    let plt = c.plot(610.0, 60.0, 560.0, 700.0);
    plt.set_title("Toroidal Inductance vs Aspect Ratio R/r")
       .set_xlabel("Major/Minor Ratio (R/r)")
       .set_ylabel("Normalized Inductance L/L0")
       .set_theme("light");
    let s_ind = plt.add_series("Exact Neumann Integral");
    s_ind.set_color("#0284C7").set_width(2.5);
    for (let i = 15; i <= 60; i = i + 3) {
        let ratio = float(i) / 10.0;
        let l_val = ratio - sqrt(ratio * ratio - 1.0);
        s_ind.add(ratio, l_val);
    }
    plt.draw();

    doc.finish();
    doc.save_png("build/06-report-1x.png");
    doc.save_png_scaled("build/06-report-2x.png", 2.0);
    doc.save_svg("build/06-report.svg");
    doc.save_pdf("build/06-report.pdf");
}
```

---

## 4. Naming & What the Gallery (`lmgallery`) Looks Like

### 4.1 Naming Recommendation: Keep `lmvideo` as Binary/Repo Name + Add Subcommand Aliases

Renaming `lmvideo` to `lmstudio` or `lmscene` would touch:
- Both `lmctl-ai/lmvideo` (public release repo) and `lmctlhq/lmvideo` (private source repo),
- All release tarballs (`lmvideo-linux-x86_64.tar.gz`, etc.) and installer URLs (`github:lmctl-ai/lmvideo@v0.2.38`),
- 8 compositions in `lmgallery` (`examples/26` through `29`, `30` through `33`) plus `showcases.json`, `scripts/health.sh`, and `closed-source-pin-inventory.md`.

**Recommended approach**:
1. **Keep `lmvideo` as the canonical binary and repository name** (`cli="lmvideo"`), described in the gallery as **"2D/3D scenes, scientific plots, diagrams, vector figures, and video (Skia + CPU 3D + FFmpeg)"**.
2. **Support explicit subcommands and `argv[0]` dispatch** inside the `lmvideo` binary:
   - `lmvideo` (no subcommand) or `lmvideo scene`: exposes the unified v3 schema (`canvas`, `video`, `scene3d()`, `out`).
   - `lmvideo draw` (or invoked via symlink/alias `lmdraw`): exposes `canvas` + `out` with `lmdraw` CLI flag compatibility (`--dsl-schema`, `--dsl-signatures`).
   - `lmvideo magnum` (or invoked via symlink/alias `lmmagnum`): exposes `scene: Scene` + `out: Output` matching `lmmagnum.dsl.json` v0.1.0 for 100% backward compatibility.
   - `lmvideo filament` (or invoked via symlink/alias `lmfilament`): exposes `scene: Scene` + `out: Output` matching `lmfilament.dsl.json` v0.1.0 for 100% backward compatibility.

### 4.2 Gallery Host Table Consolidation

In `lmgallery/README.md`, the **"Hosts in this gallery"** table simplifies from 16 hosts to **15 public hosts** (and prevents adding 2 more separate repos for `lmmagnum` and `lmfilament`):

| Before Consolidation | After Consolidation |
| :--- | :--- |
| `lmdraw` — 2D vector graphics, scientific plots, diagrams (Skia) | **Merged into `lmvideo`** (`lmdraw` binary remains a thin alias for 2 release cycles, then archived) |
| `lmvideo` — Programmatic 2D video & motion graphics (Skia + FFmpeg) | **`lmvideo` — Programmatic 2D/3D scenes, scientific plots, diagrams, vector PDF/SVG, and video (Skia + 3D PBR + FFmpeg)** |
| `lmmagnum` / `lmfilament` — (2 separate unpublished 3D repos) | **Merged into `lmvideo`** (`Scene3D` in unified schema; `lmvideo magnum` and `lmvideo filament` compat subcommands) |
| `lmcad` — Parametric 3D CAD & technical drawings (OpenCascade) | **Unchanged (`lmcad`)** — exact B-Rep solids, STEP/IGES/DXF, feeds `.stl` meshes into `lmvideo` |
| `lmblender` — Photorealistic 3D scenes & rendering (Blender Cycles) | **Unchanged (`lmblender`)** — offline ray-traced path tracing and `.blend`/`.glb` assets |

---

## 5. Phased Migration Path & Compatibility Shims

| Phase | Scope | Compatibility Guarantee |
| :--- | :--- | :--- |
| **Phase 1: Complete `lmdraw` Parity in `lmvideo` (~150 LOC)** | Add the 5 remaining `lmdraw` methods (`arrow`, `polyline`, `axes`, `log_axes`, `legend`, `load_font`) to `lmvideo`'s `Canvas`. Add `lmvideo draw` subcommand and `argv[0] == "lmdraw"` detection. | Every existing `cli="lmdraw"` script in `lmgallery` (`examples/01`–`25`, `34`–`42`) runs **unchanged** when `lmdraw` is symlinked to `lmvideo` or switched to `cli="lmvideo"`. |
| **Phase 2: Embed Zero-Dependency 3D Engine in `lmvideo` (~950 LOC)** | Port `lmfilament/cpp/mesh.cpp` (11 procedural primitives + OBJ/STL I/O) and the unified `preview.cpp` + `lmmagnum/cpp/render.cpp` software rasterizer (shadow map, Cook-Torrance GGX, mipmapped textures, `project_x/y`, Skia glyph extrusion for `mesh_text3d`) into `lmvideo/src/scene3d.{hpp,cpp}`. | Zero new third-party libraries; `lmvideo` Makefile stays self-contained; binary grows by < 400 KB (~18.4 MB total). |
| **Phase 3: Compat Shims (`lmvideo magnum` & `lmvideo filament`, ~300 LOC)** | Embed the legacy `lmmagnum` (`scene: Scene` root) and `lmfilament` (`scene: Scene` root) schema adapters inside `lmvideo` under `lmvideo magnum` and `lmvideo filament` (and `argv[0]` dispatch). | Existing 8 examples in `lmmagnum/examples/` and 8 examples in `lmfilament/examples/` pass `--check` and render identically through `lmvideo`. |
| **Phase 4: Gallery Migration & Repo Retirement** | Add 4 flagship 2D+3D+video compositions to `lmgallery`. Switch `lmgallery` `cli="lmdraw"` blocks to `cli="lmvideo"` (keeping a 1-MB shell/exec wrapper in `lmctl-ai/lmdraw` for 2 minor releases). Archive `lmdraw`, `lmmagnum`, and `lmfilament`. | All autorun URLs and pinned tags in `closed-source-pin-inventory.md` continue working during the 2-release deprecation window. |

---

## 6. Risks & Mitigations

1. **Software 3D rasterizer throughput at 1080p60 video**:
   - *Risk*: A 2×2 SSAA + 1024² shadow-map software rasterizer takes ~18 ms/frame at 800×600 (~55 fps), which is fast enough for 720p30/1080p30 but can bottleneck on >100k-triangle CAD meshes at 4×4 SSAA.
   - *Mitigation*: Default `set_ssaa(1)` during `video.next_frame()` loops and `set_ssaa(2)` for still images; parallelize scanline tile rasterization across 4 threads (`std::thread` pool in `scene3d.cpp`, zero external deps) for a 3.4× speedup.
2. **Coordinate-system & angle-unit mismatch between `lmmagnum` (degrees) and `lmfilament` (radians in camera FOV)**:
   - *Risk*: Scripts ported from `lmfilament` pass `fov_deg` in degrees (`set_perspective(45.0, ...)`) while `lmfilament`'s `rotate_node` took radians in some helpers and degrees in others.
   - *Mitigation*: Canonicalize all unified `Scene3D` angles to **degrees** (matching `lmvideo` 2D `Canvas.rotate(deg)` and `lmmagnum`), while the `lmvideo filament` compat subcommand preserves exact `lmfilament` parameter semantics.
3. **3D Depth Sorting & Transparency (`opacity < 1.0`)**:
   - *Risk*: A standard Z-buffer cannot blend multiple overlapping transparent triangles in arbitrary order.
   - *Mitigation*: Render opaque triangles first with Z-write enabled, then sort transparent triangles back-to-front by centroid view-Z with Z-test enabled and Z-write disabled (already partially implemented in `lmfilament/cpp/preview.cpp`).

---

## 7. Open Questions for the Owner (Max 5)

1. **Product Name**: Should we keep **`lmvideo`** as the binary and repo name (zero URL/pin churn across `lmgallery`, subcommands `lmvideo draw|magnum|filament`), or rename the consolidated binary to **`lmscene`** / **`lmstudio`** with `lmvideo` and `lmdraw` as compatibility aliases?
2. **Fate of `lmmagnum` and `lmfilament` repos**: Since neither `lmmagnum` nor `lmfilament` is referenced in `lmgallery/showcases.json` yet, can we archive both repos immediately once Phase 2–3 land in `lmvideo`, without publishing standalone compatibility binaries for them?
3. **`lmdraw` Deprecation Window**: When migrating `lmgallery`'s 38 `lmdraw` compositions to `cli="lmvideo"`, is a **2-release** shim window for `lmctl-ai/lmdraw` sufficient before archiving `lmdraw`?
4. **3D Text Default**: Should `mesh_text3d(text, size, depth)` default to smooth **extruded TrueType glyph outlines** via Skia `SkPath` (recommended), keeping the legacy 5×7 voxel-cube font only in the `lmvideo magnum`/`filament` compatibility shims?
5. **Headless GPU Backend Later?**: Is the **zero-dependency C++17 software rasterizer** (100% deterministic across Linux/macOS/Windows CI without X11/EGL/Vulkan drivers) sufficient as the permanent 3D engine for `lmvideo`, with `lmblender` remaining the escape hatch for heavy GPU/Cycles path tracing?
