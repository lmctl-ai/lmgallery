# Consolidation feasibility inventory — ResearchSol

Snapshot: 2026-10-26. Design only; no renderer, schema, example, release, repository
visibility or product code is changed by this note. Scope now includes the original six hosts plus lmimg (owner addition 2).
Counts and the complete API appendix come from checked-out **host-only** schemas;
release sizes come from public GitHub release asset metadata queried for this note.
These are inventories, not measured performance predictions for a merged build.

## Recommendation and repository verdicts

Consolidate on **lmvideo**, as the implementation/distribution base, with one canonical product schema and model.
Use Skia for 2D, an **own CPU triangle renderer** for the primary 3D path, and the
existing external FFmpeg encoder pipe. Reuse audited Magnum/Corrade geometry/math
and the two CPU renderers selectively; Magnum remains an implementation dependency,
not a second user-facing scene product. The primary renderer is not Filament's noop
backend. A real GPU implementation is a later, separately measured product decision.

| Repository | Verdict | Concrete boundary |
|---|---|---|
| lmvideo | **Merge target / keep** | Owns image/document output, frame clock, plots, diagrams, panels and encoder process. Add scene/viewports behind that output pipeline. |
| lmdraw | **Merge, then retire independent engine after compatibility gates** | Port 46 declarations, migrating its sources to the canonical schema; frozen old binaries cover old contracts. Do not remove LunaSVG/PlutoVG until SVG attributes, fonts and PNG comparisons pass; Skia is a replacement, not today's lmdraw dependency. |
| lmmagnum | **Merge selected renderer/geometry, then retire host implementation** | Reuse mesh primitives, transforms, textures, shadows, accumulation and exporters. Keep one canonical scene API; retain old releases and adapters. |
| lmfilament | **Merge preview features, retire standalone product conditionally** | Reuse CPU preview work. Drop Filament from the ordinary rendering path. Its material compiler/package APIs need a separate compatibility decision; dropping that library cannot preserve all 62 declarations automatically. |
| lmcad | **Keep separate** | Exact B-Rep/OCCT, booleans, fillets, chamfers, hollowing and volumes remain CAD. Exchange tessellated meshes; do not burden every chart/movie user with OCCT. |
| lmimg | **Merge image processing, then retire standalone authoring host** | One Image/Frame type owns filters, geometry, compositing and measurements for every producer; no separate img context in the target schema. |
| lmblender | **Shrink to an optional external render engine** | Keep Cycles path tracing/denoising/passes; remove modelling/drawing authoring from its target interface. The unified product builds one Scene and receives backend frames as the same Image type. Historical authoring binaries remain pinned for migration. |

lmimg is explicitly in scope by owner addition 2. lmplot remains outside this decision. Do not add OCCT, Cycles, a second public scene model or an in-process
FFmpeg distribution to the first consolidation milestone.

## Corrections that change the estimate

1. **lmdraw is LunaSVG/PlutoVG, not Skia.** Its CMake links those libraries and its
   README explicitly says PNG only. SVG is its internal retained representation.
2. **lmvideo SVG uses SkSVGDOM**, not LunaSVG: `cpp/lmvideo.cpp` includes SkSVGDOM
   and uses `SkShapers::Primitive::Factory()`. A Skia pack containing HarfBuzz/ICU
   does not prove this particular text path implements full complex shaping/RTL.
3. **lmfilament PNGs are CPU preview pixels.** `scripts/build-filament.sh` disables
   Vulkan, Metal, OpenGL, XCB and Xlib; `render_frames` drives noop rendering without
   image output. Roughness/metallic/normal/AO texture uploads do not imply preview
   shading uses those maps. Its README says Windows is unsupported.
4. **lmblender links Cycles/Embree/OIDN and Blender helpers into the executable.**
   `THIRD_PARTY_NOTICES.md` and `docs/LICENSE_AUDIT.md` identify the GPL closure.
   Cycles' own Apache licence does not remove the linked helpers/LUT obligations.
5. **Compatibility is not renaming a binary.** The original six schemas contain 546 domain declarations
   (618 with lmimg added below), different root contexts and only six identical declarations
   between lmvideo and lmdraw. The common diagram vocabulary is useful code reuse,
   not proof that every old script is already API-compatible.
6. **Release policy changed after the older sibling note.** The newer
   [release-cycle note](06-release-cycle.md) specifies staged Linux x64/arm64 releases
   and promotion; older five-platform/every-main-release prose is historical.

## Owner addition 2 — one product, one schema, one image/frame model

This addition **supersedes the earlier multiple-registry compatibility proposal**.
The delivered core is one executable and one canonical schema, not `lmvideo draw`,
`lmvideo magnum`, `lmvideo filament` and `lmvideo img` products hidden in one file.
Old names can be thin executable aliases, but every new alias must discover the
**same canonical schema**. Source migration and frozen old releases provide the
legacy bridge; aliases cannot make differently hashed old bytecode load by magic.

Name candidates: **lmframe** (shared image/frame vocabulary), **lmcanvas** (visual
composition), or **lmvideo** (least installer churn). No name availability is claimed.
Recommendation: retain lmvideo's existing distribution coordinate through migration;
use lmframe as the preferred neutral product name if the owner accepts a later rename.
A new name does not justify separate authoring schemas or another processing service.

| Core concept | Meaning and ownership | Shared operation path |
|---|---|---|
| **Image** | The one pixel object: dimensions, format, alpha/colour convention and owned storage. A video frame is this same Image plus timestamp/index metadata, not another pixel type. | Image decode, Canvas snapshot, Scene render and Layout render all return Image. The same resize/filter/composite/measure/save operations accept every producer. |
| **Canvas** | Drawing/editor for an Image or a vector command recording, using Skia. | Draw text/paths/shapes or an Image; snapshot to Image. Processing a vector recording first rasterizes explicitly; filtering cannot preserve arbitrary vector structure. |
| **Scene** | Meshes, transforms, camera, lights and materials, independent of output file type. | `Scene.render(...) -> Image`; a Layout viewport consumes the result directly, including in a Timeline. |
| **Layout** | Panels/layers that arrange Images, Canvas recordings, plots and Scene views. | Composition produces Image, or a Picture when all required parts retain vector commands. |
| **Timeline** | Frame clock/tracks and time-indexed evaluation of the same scene/layout/image operations. | Each evaluated frame is an Image; writers consume a stream of these Images. No separate lmimg Animation processing representation. |

**Editing semantics:** preserve lmimg's documented mutable receiver + fluent return,
with explicit `copy()` when the original must survive; snapshots from drawing or
3D rendering return fresh Images. The immutable-Image proposal in the companion note
is an alternative requiring a dataflow migration, because today's scripts often ignore
a filter's return value. Do not describe immutable edits as mechanically identical.
A Canvas edit view and its Image share ownership deliberately; unrelated scene/frame
snapshots must not alias a reused renderer buffer. Timeline writers need bounded
frame retention/backpressure, not the whole clip resident in memory.

**Pixel semantics:** current lmimg is RGBA8, straight-alpha, gamma-encoded sRGB for
its editing/statistics contract; it has no colour management. Use that documented
logical default for migrated operations. Skia's premultiplied buffers and linear-light
3D shading need explicit conversions at the adapter boundary. Convert once at a
well-defined boundary, with defined rounding and alpha-zero RGB behaviour; do not
silently run old levels/mean/SSIM in a new linear/HDR space. Higher precision and ICC
are separately scoped extensions of the same Image, not existing lmimg capabilities.

### lmimg inventory and mapping

Source HEAD `5364c868768b7aaf95ba3e977b1141062f305a5b`, schema
`schema/lmimg.dsl.json`, SHA-256
`e59212275e3cec0df67cd1e4a932c79d52045a113ef6675fc0d2c874c02c0ac9`.
Context `img: Img`; zero free functions; six types and **72 method declarations**:
Image 49, Img 14, Curve 1, Layers 3, Montage 2, Animation 3. These are not standard
catalog methods. Appendix C lists every declaration, taking the seven-host total to 618.

| Existing lmimg capability | Mapping into the canonical product | Behaviour to preserve / new work |
|---|---|---|
| `Img.open/canvas/pattern/hald` | Image decode/create/procedural factories | Same Image as drawing, mesh renders and frames; preserve normalized pattern coordinates, seeded hash/noise and Hald dimensions. |
| `Image.resize/crop/rotate/flip/perspective/lens` | Image geometry operations | Preserve crop/extent, interpolation, transparent borders and ImageMagick's non-right-angle rotation extent before changing engines. |
| `curves/curves_rgb/levels/threshold/invert/normalize/equalize/colormap/clut/hsl/channelmix` | Image tone/colour/filter operations; Curve/LUT are parameter assets | Preserve RGBA8 rounding, gamma-space arithmetic and trilinear CLUT sampling. They operate equally on a loaded photo or a rendered frame. |
| `blur/sharpen/edges/unsharp/vignette/tilt_shift/morphology/heal` | Image filters/retouching | Preserve premultiplied-alpha blur, RGB-only sharpening, radius limits and healing-lite semantics. A Skia blur does not implement this entire group. |
| `mask/selection/blend`, `Layers.add/masked/render` | Image masking/composite plus Layout layers | Retain the ten blend modes, offsets, opacity and mask conventions. Layer rendering returns the canonical Image, not another backend image wrapper. |
| `Image.rect/circle/line/text`, `Img.text_width` | Canvas drawing/edit view on Image | Share typography with every other output. ASCII stb text versus Skia font metrics requires image/caption review; not guaranteed byte-identical replacement. |
| `copy/width/height/pixel/set_pixel`, `property/metadata` | Image ownership, pixel access and metadata | Define read/write metadata and mutation lifetime once for all producers; no raw ImageMagick handle escapes. |
| `mean/stddev/min/max/ssim/psnr/histogram` | Image measurements and histogram export | Equal-dimension checks, normalized RGBA PSNR, identical-image infinity, and global-window luma SSIM remain explicit contracts. |
| `Img.panel/montage`, `Montage.add/render` | Layout/contact-sheet operations | Reuse panel sizing/spacing; intermediate thumbnails remain Images and can be filtered/drawn without disk round trips. |
| `Img.animation`, `Animation.add/size/save` | Timeline frames with per-frame durations and output writer | Preserve GIF centisecond delays. Current open reads only an animated input's first frame; full video/animation decode is new work. |
| `Image.save` and format conversion | One Image writer; conversion is decode -> optional Image ops -> encode | Current formats: PNG/JPEG/TIFF/WebP/GIF/BMP/PNM (PPM/PGM/PBM). Keep a capability list; restricted delegates remain external under addition 3. |
| `Img.eval/assert_close/assert_true/print` | Shared expression utility/testing/output contracts | Do not carry a parallel img service/root context just for helpers; map assertions/output to the common testing/Output surface. |

ImageMagick is currently a statically linked **permissive ImageMagick License** engine,
with loadable modules and delegates disabled; the notice explicitly excludes
GIMP/GEGL/Ghostscript and GPL/LGPL delegates. Its selected codecs include zlib,
libpng, libjpeg-turbo, libtiff and libwebp, plus stb_truetype/Roboto. It is not excluded
merely for being ImageMagick: audit exact selected inputs under addition 3. It can
remain an internal implementation of Image operations while Skia supplies drawing;
no second product, executable, public image type or file handoff is needed. If that
closure is rejected, use Skia/stb/libpng for core raster operations, port the original
MIT editing algorithms, and leave unsupported conversions as explicit external jobs.
Do not claim Skia already replaces healing, morphology, LUTs or every TIFF feature.

Latest observed public release [lmimg v0.1.3](https://github.com/lmctl-ai/lmimg/releases/tag/v0.1.3):
`lmimg-linux-x64` **8,937,672 bytes** (asset size, not incremental cost in a shared link).
This does not justify adding 8.94 MB to lmvideo's size prediction without a prototype.
The existing 4096 MiB default memory limit and native-allocation accounting are
requirements to re-evaluate for the shared Image pool, not to discard on migration.

Gallery additions: lmimg is in **two**, not four, of the current 50 showcase records:
`14-num-sweep-contact-sheet` and `34-image-pipeline-contact-sheet`. Both need a
source migration and before/after measurements/previews. The affected-host union
therefore grows from 29 to **31** compositions. Its own public examples include
lmplot/lmdraw compositions and relative assets; preserve those raw autorun paths.

**Revised verdict:** merge lmimg's capability into the single model, then retire its
independent authoring schema/engine pipeline after parity gates. Keep `lmimg` as a
canonical-schema alias for the proposed N=6-release/three-month transition; retain
old pinned binaries for old source/bytecode. No new distinct img schema is embedded.

## Owner addition — lmblender becomes a render engine only

This supersedes the original keep-separate-authoring verdict. The product owns all
2D drawing, mesh construction/import, scene modelling, cameras/lights/material
parameters, layout, image processing and timeline evaluation. lmblender is only
one selectable **external final-render backend**, with its current Cycles/GPL
closure outside the closed core. lmcad remains the optional exact B-Rep producer;
its tessellated result becomes an ordinary mesh in the product's Scene.

### Interface placement and ownership

One internal `Renderer` seam sits below the canonical Scene/Viewport and Timeline
APIs and above image composition. Conceptually, a future `Scene.render(...,
render="raster" | "cycles") -> Image` selects an implementation, not another
host/schema. `raster` is the in-core CPU renderer; `cycles` submits a render job to
an optional executable. This API notation is a design sketch, not current lmcode
syntax or an implemented method.

A Timeline evaluates animation once in the product and sends resolved per-frame
scene states to a batch job. The backend must not implement a second easing/model
or invent camera framing. It may reuse geometry/BVH and update transforms between
frames, but changing topology requires explicit versioned mesh references. Its
returned frame becomes the canonical Image; the product then performs 2D labels,
filters, compositing, layout and video encoding. lmblender does not encode the
final movie or duplicate the product's Canvas/Timeline engine.

### Scene/job export to Cycles

Use **glTF 2.0 GLB plus a versioned JSON job sidecar**, not generated Python,
arbitrary scripts or the old lmblender modelling DSL. The existing glTF mesh
importer is useful groundwork; full camera/light/material-extension fidelity and
the new job CLI remain implementation work, not capabilities inferred from it.

| Job entry | Required contract |
|---|---|
| `scene.glb` | Triangle meshes, stable node/mesh/material IDs, hierarchy/transforms, normals/UVs, embedded/referenced textures, metallic/roughness materials and cameras. Canonical units/axis convention is explicit; convert CAD units and camera angles in the product exporter. |
| Required extension list | Negotiate `KHR_lights_punctual` and any material extensions such as transmission/IOR/emissive strength before submission. Unsupported required features fail explicitly; they never become default grey materials. |
| `job.json` | Protocol version, scene/asset hashes, requested camera, width/height, frame indices/times, samples, seed, bounces, denoiser, CPU/device choice, output format, alpha/colour/view-transform contract, requested passes and resource/time budgets. Area lights, environment maps, procedural/material features not represented by the chosen GLB profile use documented typed sidecar fields. |
| Frame-state records | Product-evaluated node transforms/visibility, camera optics, lights and material changes, keyed by stable IDs. GLB core animation covers node TRS/morph weights; camera/light/material property animation is **not** a generic core glTF channel. Use these sidecar records or a separately negotiated extension. |
| Output manifest | One result entry per requested frame/pass with index, path, size, checksum, dimensions, channel/colour/alpha metadata, timing and structured error. Atomically publish completed files and distinguish partial/cancelled jobs. |
| Frames | Baseline PNG RGBA8 with defined sRGB/straight-alpha semantics, decoded to the same core Image. Scene-linear EXR is optional only when the core advertises a permissive decoder and matching Image precision/colour handling; current RGBA8 editing is not an implicit HDR pipeline. Apply display tone mapping exactly once. |

This follows the actual [glTF animation target contract](https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/schema/animation.channel.target.schema.json)
and [punctual-light extension](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_lights_punctual/README.md).
Area lights, environment/world state and arbitrary Cycles shader graphs are not
claimed to be fully portable core glTF. A versioned limited procedural/material
profile may preserve selected looks; unsupported features remain explicit errors.
lmcad currently exports STL/OBJ, not GLB: import those into the product and let
its one exporter generate the render job; adding CAD glTF export is optional.

Proposed backend CLI: `lmblender --render-capabilities` returns protocol versions,
formats, supported required extensions, passes and available devices;
`lmblender render --job DIR` consumes one bounded job and emits one final result
JSON. Proposed exits: 0 complete, 2 invalid job, 3 unsupported capability, 4 render
failure/cancelled job (with a distinct structured reason). The core resolves an
explicit backend path or user-installed tool, invokes argv without a shell, and
handles timeouts, cancellation and logs. Missing Cycles or an incompatible job
version is a clear failure; no silent preview fallback. The backend reports only
actual devices: selecting Cycles does not promise a GPU implementation.

### What lmblender keeps and drops

| Keep in the render engine | Drop from its target product surface / move into the unified product |
|---|---|
| Cycles session/integrator, Embree traversal, OIDN denoising, sampling/seed/bounce controls | Mesh primitives, tubes, labels, arrows, procedural modelling, instancing authoring and transform construction |
| Material-to-BSDF translation and supported texture/procedural decoding | A second public material-construction/model-building DSL; material authoring belongs to the one Scene model, with capability-checked backend parameters |
| Camera/light/world/environment rendering and explicitly supplied frame states | Fitted-camera helpers, user-authored camera/transform/light keyframes and a second timeline/easing evaluator |
| PNG/EXR/pass output, batch rendering and geometry/BVH reuse | 2D drawing, diagrams, image filters, montage/layout, final movie encoding and modelling/gallery authoring presets |
| Import/asset decoding needed by the declared job profile; source offers/notices/relink compliance for its actual binary | The 96-method lmscript schema as an active authoring interface. Its current inventory remains historical evidence, not a target API. |

Migrate the 99 current public lmblender example files into product-owned scripts
that construct a Scene and select Cycles where required; preserve raw URL paths by
updating their contents and keeping immutable old release pins. Do not claim all
99 need path tracing or that all current procedural looks fit the first job profile.
For the proposed N=6-release/three-month window, old authoring releases stay
available; any temporary source-migration launcher stays outside the one core
schema. The render engine remains a separately versioned optional dependency.

Acceptance: compare supported legacy scenes at fixed geometry/camera/material
states and render settings; test transparency/colour, passes, frame indices,
unsupported features, missing backend, cancellation and partial outputs. Verify
batch frame state versus individually rendered frames, and measure reuse/RSS.
Same-pinned-build reproducibility is a test, not a cross-device/Cycles-version
promise. The GPL source/notice obligations still apply to a separately shipped
backend; file exchange is not a waiver. The closed core's permissive CPU renderer
continues to work without downloading the external engine.

## Host/schema inventory

Exact source paths are `<source checkout>/schema/<host>.dsl.json`. There is one
host schema per product; all use schema version 2. Appendix A enumerates **every
free-function overload and method overload**, its types and return value. Standard
catalog declarations injected/merged at build time are excluded from these counts;
adding six standard catalogs together would falsely inflate the product API.

| Host | Source HEAD | Schema SHA-256 | Free overloads | Method overloads | Types | Root contexts |
|---|---|---|---:|---:|---:|---|
| lmvideo | `08929e247db6914420c45388ac8eafa4cba54754` | `b1427834727bd9730f556d392696a1a852ff4460d68ce6cd1c91a2cce0b0bf10` | 13 | 205 | 26 | `canvas: Canvas`, `video: Video`, `out: Output` |
| lmdraw | `927357fb00281c643429c85390dd02bedf0595e7` | `4f990a90530289bdac5747a0df5bed28b0d956b1f92393c7ec168612070bd6b0` | 0 | 46 | 6 | `scene: Scene` |
| lmcad | `65b893db229c881ae9662f8d933f1ddbf75f95bf` | `7b1bf8aa1356e8176cd144f0223601fb484197caa8e4b452e795d72aed5257a3` | 2 | 62 | 9 | `scene: Scene` |
| lmblender | `0ed644a7573eb123b0d476d88ec60b7d0b21c9fe` | `8bf12e704a32dd4238424f2757a36caf4397dd024c49f7097b29215414691f73` | 0 | 96 | 3 | `scene: Scene` |
| lmfilament | `b53b90fb72c604aa7005816ede2ad4179c93f93a` | `f769db9188e4a9ebfcc9573c62ca3ad068f51f976b41cfb86f83937fd40a83b6` | 0 | 62 | 7 | `fil: Filament` |
| lmmagnum | `f763ed7b8c96b0aaf2085ead34bcbdc90089418d` | `abb70b79df741b9ea5e91e793129d676193dd6716ce80bc533de6d71e1a44fd0` | 2 | 58 | 7 | `scene: Scene` |

The private source checkouts retain implementation schemas. Public peers are
`lmctl-ai/<host>`; local public content is under `<host>-public` when present.
lmvideo source is `~/repos/lmctlhq/lmvideo`; the other source checkouts are under
`~/repos/dsl/`. lmblender's origin remains public `lmctl-ai/lmblender`; the other
five origins are private peers. Public content, not stale private README copies,
is authoritative for examples and gallery images.

## Outputs: public DSL versus library/helper capability

| Host | Exposed output paths today | Important exclusions / exchange implications |
|---|---|---|
| lmvideo | `Surface.png/svg/pdf`; `Picture.png(path,scale)/svg/pdf/skp`; `PdfDocument.write`; `Video.output/save_frame` PNG/JPG/JPEG stills; MP4/WebM/MKV/GIF via external FFmpeg | `Document.finish` records a Picture; SKP is Skia-specific/version-sensitive. MP4 defaults libx264, WebM libvpx-vp9, MKV ffv1, GIF gif. No public 3D scene or mesh exporter today. |
| lmdraw | `Scene.render_png(path,w,h,scale)`; examples emit numbered PNGs and optionally call FFmpeg | No public SVG/PDF export despite internal SVG. Preserve scale/atomic-write/error behaviour and image filenames. |
| lmcad | PNG, PPM, STL, OBJ; `Animation` writes APNG | STL/OBJ exports are write-only; no current STEP/IGES/glTF exchange API. Mesh exchange loses exact B-Rep/topology/tolerances. |
| lmblender | PNG, EXR, render-pass outputs, PNG sequence, APNG | Existing OBJ/STL/ASCII PLY/glTF imports. It already imports glTF; shared-scene/camera/material fidelity is the missing contract, not the existence of a glTF importer. |
| lmfilament | Preview PNG, Texture PNG, Mesh OBJ, compiled Material package via `Material.save` | `render_frames` returns a count, not a movie/image. Filament binary material packages and shader compilation cannot be emulated by renaming a CPU material. |
| lmmagnum | PNG, PPM, accumulated PNG, Texture PNG, STL/OBJ/PLY | Animated GIF/MP4 in examples are external encoding of frames, not native scene-schema movie methods. |

Sources: each schema's output methods; lmvideo `cpp/host.cpp:122–142`,
`cpp/encoder.hpp` and `cpp/encoder.cpp:200–228`; lmdraw README restrictions;
lmcad/lmblender/lmfilament/lmmagnum rendering/export code and their READMEs.
WebP, glTF **export**, video-input layers and general property tracks may be useful
target features, but are not all current host-schema capabilities. SVG/PDF can
embed a rasterized 3D viewport; they do not become vector 3D/CAD exports.

## Overlap matrix

Feature overlap is broad; exact API equivalence is much smaller. The table below
counts identical owner-qualified declarations (owner/name/parameter types/return),
not interchangeable implementation, units, error behaviour or visual output.
Root contexts and standard functions are not included.

| | lmvideo | lmdraw | lmcad | lmblender | lmfilament | lmmagnum |
|---|---:|---:|---:|---:|---:|---:|
| lmvideo | 218 | 6 | 4 | 0 | 0 | 0 |
| lmdraw | 6 | 46 | 0 | 1 | 0 | 1 |
| lmcad | 4 | 0 | 64 | 0 | 1 | 25 |
| lmblender | 0 | 1 | 0 | 96 | 2 | 0 |
| lmfilament | 0 | 0 | 1 | 2 | 62 | 9 |
| lmmagnum | 0 | 1 | 25 | 0 | 9 | 60 |

| Capability | lmvideo | lmdraw | lmcad | lmblender | lmfilament | lmmagnum | Consolidation implication |
|---|---|---|---|---|---|---|---|
| 2D diagrams/text | Canvas/Plot/Panel | retained SVG nodes | limited scene annotations | mesh labels | mesh text | mesh text | Skia canonical; keep 3D text versus overlay labels explicit. |
| Scene transforms/primitives | absent 3D | 2D attributes | B-Rep shapes | triangle meshes, Z-up | meshes/nodes/parts | meshes/groups | One mesh scene, explicit units/camera adapters. |
| Lighting/materials | 2D paints | fills/gradients | CPU Blinn-Phong | Cycles GI/glass/volume | noop material compiler + CPU preview | CPU textures/shadows | Share preview features, do not promise path-traced parity. |
| Layout/plots | panels + plots | grids/diagram layout | no 2D layout | none | none | none | Preserve lmvideo's existing rich surface instead of replacing it with a 3D-first API. |
| Animation | streaming frame API, Keyframes | mutate then PNG | keyframes/APNG | transform/camera/material/light tracks | mutate parts, per-frame PNG | mutate, accumulation | General retained property tracks are new work, not an existing common timeline. |
| Engineering topology | none | none | exact OCCT operations | mesh operations/import | mesh only | mesh only | Separate CAD boundary. |

Nonmechanical mismatches: radians in lmcad versus degrees elsewhere; Blender Z-up
versus the other 3D hosts' Y-up; Magnum horizontal field of view versus CAD/Filament
vertical field of view; lux/material snapshots versus normalized CPU lighting;
texture origin, transform multiplication/pivot order and premultiplied alpha.
lmcad `cpp/render.cpp:33` uses image **height** for focal length, confirming vertical
FOV (one secondary inventory called it horizontal; the implementation wins).
Do not expose all existing unrelated `Scene`, `Shape`, `Material` and `Node` types
in one flat merged schema: the same names mean SVG, B-Rep, mesh or shader objects.

## Dependency, licence and released binary footprint

Metadata below is the uncompressed **linux-x64 executable asset** size, not a local
unstripped build, archive, whole download or incremental linked-library cost.
Queried public release metadata on the snapshot date; tag-specific links are stable.

| Host / latest observed release | Bytes (MiB) | Main link/runtime closure | Distribution consequence |
|---|---:|---|---|
| [lmvideo v0.1.35](https://github.com/lmctl-ai/lmvideo/releases/tag/v0.1.35) | 30,138,784 (28.74) | Skia m144 JetBrains pack, SkSVGDOM/SkShaper, ICU/HarfBuzz/FreeType, image codecs, embedded DejaVu; external FFmpeg/ffprobe | Skia BSD + component notices; DejaVu/Vera font terms; stage exact pack notices. FFmpeg is not shipped by this host. |
| [lmdraw v0.2.6](https://github.com/lmctl-ai/lmdraw/releases/tag/v0.2.6) | 5,554,776 (5.30) | LunaSVG 3.5, PlutoVG 1.3, FreeType-derived raster code, stb, embedded Noto Sans/Math; dynamic Linux glibc | MIT/FTL/stb notices, SIL-OFL font texts and runtime obligations. Rendering engine change affects fonts/SVG semantics. |
| [lmcad v0.1.72](https://github.com/lmctl-ai/lmcad/releases/tag/v0.1.72) | 30,500,280 (29.09) | OCCT static B-Rep + CPU preview; glibc/GCC runtime | LGPL-2.1 + OCCT exception, source/object/relink materials; release already has per-architecture relink archives and recipe. |
| [lmblender v0.3.138](https://github.com/lmctl-ai/lmblender/releases/tag/v0.3.138) | 124,185,032 (118.43) | Cycles, Blender GPL helper archives/LUT, Embree, OIDN, OIIO, OCIO, EXR, TBB, codecs, static runtimes | Audited combined binary GPL-3.0-or-later; 324,842,327-byte source archive also published. Keep separate from the proprietary core. |
| [lmfilament v0.3.20](https://github.com/lmctl-ai/lmfilament/releases/tag/v0.3.20) | 16,443,936 (15.68) | Filament 1.78.1 Apache-2.0, material compiler/noop backend, own CPU preview, stb, Linux runtimes | Preserve exact notices and shipped libc++/glibc relink materials. Removing Filament saves an unmeasured amount in a merged link; do not subtract whole host sizes. |
| [lmmagnum v0.2.14](https://github.com/lmctl-ai/lmmagnum/releases/tag/v0.2.14) | 4,043,264 (3.86) | Magnum Math/Primitives/MeshTools/Trade + Corrade, stb, CPU rasterizer, Linux runtimes | MIT dependency surface and runtime notices. Keep only measured required components. |

Linux-arm64 bytes respectively: 28,884,776; 5,438,280; 27,212,696; 90,894,344;
15,439,704; 3,831,352. These figures come from GitHub `/releases/latest` asset
`size` fields, not execution/latency/RSS measurements. All size predictions for the
unified binary remain estimates until a pinned prototype is linked and stripped.

Project-authored source notices, public-root binary terms and a historical release's
LICENSE are distinct. Preserve release-specific permissions (including earlier MIT
grants); the final freeware template cannot revoke component rights. An OCCT
integration is technically possible under LGPL compliance; separating it is an
architecture/distribution choice, not a claim that LGPL forbids commercial hosts.
[OCCT's exception](https://github.com/Open-Cascade-SAS/OCCT/blob/master/OCCT_LGPL_EXCEPTION.txt)
concerns header material and does not erase all static-link obligations.
[lmblender's public audit](https://github.com/lmctl-ai/lmblender/blob/main/docs/LICENSE_AUDIT.md)
identifies the actual GPL-derived link inputs; do not generalize that every use of
Apache-licensed Cycles is intrinsically GPL. Re-audit runtime and font closures after
link changes; do not assume a merged executable is obligation-free because wrappers
were MIT. A static ELF can still load external resources; noop rendering here is a
build choice, not proof that every static program is categorically unable to use a GPU.

## Owner addition 3 — licence-gated core and external components

The closed all-in-one **core must exclude any selected component whose licence or
unresolved patent conditions create the owner's stated problem**, including static
LGPL relinking obligations. Keep that functionality optional in a separately
licensed process/repo or user-installed tool with an explicit interface. The table
names concrete permissive alternatives; replacement means the stated core capability,
not a promise of identical B-Rep, shader or path-tracing behaviour. This rule changes
build selection; the historical size inventory above is not an approved link closure.

| Component | Licence / selected-build condition | Problem? | In-core / external / replacement |
|---|---|---|---|
| Skia 2D raster/SVG/PDF | BSD-3-Clause plus audited component notices | No inherent closed-source conflict; unverified pack contents are not approved automatically | **In-core**, after rebuilding/auditing the exact dependency/runtime closure. Replacement for LunaSVG is Skia's SVG DOM; retain legacy SVG behaviour only through accepted adapters or an optional external legacy host. |
| lmimg ImageMagick processing engine | Permissive ImageMagick License plus separately pinned codec/font notices | No inherent closed-source conflict in the current delegate-disabled closure; re-audit selected code | **In-core implementation of the same Image**, not a second host/schema. If that closure fails the licence gate, port original MIT processing algorithms onto Skia/stb/libpng and leave unsupported conversion delegates external. |
| Magnum / Corrade | MIT | No licence problem | **In-core** where required; optional replacement is extracted/reimplemented MIT-authored mesh primitives plus Skia math. Removing a dependency remains a build-tested optimization, not an assumed zero-cost edit. |
| Filament / material compiler | Apache-2.0 plus dependency notices | No inherent licence conflict; noop rendering/size is an architectural issue | Ordinary core uses own MIT CPU renderer. **External optional** legacy `lmfilament --dsl FILE` for real `.filamat` compilation/package operations if preserving that API; exchange material packages/OBJ/PNG, do not fake them. |
| OCCT B-Rep kernel | LGPL-2.1 + Open CASCADE exception | **Yes** under the owner's no-static-relink-duty rule | **External** `lmcad --dsl FILE`, exchanging OBJ/STL plus explicit units/appearance metadata. **Core replacement:** own MIT triangle scene and **Manifold (Apache-2.0)** for optional mesh booleans. Neither replaces exact OCCT B-Rep, fillets or topology; those remain external. |
| Current Blender/Cycles combined closure | GPL-3.0-or-later binary, including GPL Blender helpers/LUT; Cycles itself Apache-2.0 | **Yes** for the audited combined executable | **External render-only backend** `lmblender render --job DIR`, with a versioned scene job and PNG/EXR/frame outputs; the old authoring CLI remains only in frozen historical binaries. **Core replacement:** own MIT CPU preview plus permissive Magnum geometry, not GI/refraction. Any later standalone permissive Cycles build requires removing/replacing and re-auditing GPL inputs first. |
| FFmpeg/libav linked into core | Usually LGPL-2.1+; optional GPL components/configuration change the result | **Yes**, including LGPL relink duties even without GPL codecs | **External user-installed FFmpeg**, argv process accepting width/height/fps/pixel format and raw RGBA stdin, returning output files, status and stderr. **Core replacement:** **libvpx (BSD-3-Clause)** + **libwebm (BSD-3-Clause)** for an optional reviewed VP9/WebM encoder/muxer. Core can initially emit PNG sequences instead; this new codec path is not implemented today. |
| x264/x265, H.264/HEVC output | GPL-2.0+ implementations or separate commercial terms; patent questions are independent | **Yes / unresolved by a code licence alone** | **External**, explicitly selected user-installed encoder; no mandatory bundle or silent fallback. **Core replacement:** reviewed libvpx VP9/WebM as above, or PNG sequences. No H.264/HEVC-equivalent compatibility claim or royalty-free guarantee. |
| PNG/JPEG and image helpers | libpng/zlib; selected stb helpers MIT option; exact JPEG implementation notices vary | Normally no; inspect selected files/build | **In-core** PNG via libpng/zlib or stb's MIT option. Prefer PNG baseline; optional JPEG via a separately audited permissive implementation, not an assumed FFmpeg codec import. |
| Restricted/GPL or unlicensed system font files | GPL/exception or commercial font terms vary by exact bytes | **Yes** if the selected font fails the owner's rule or lacks redistribution rights; embedding exceptions are not family-wide guarantees | **External user-supplied font assets**, never silently redistributed. **Core replacement:** pinned **Roboto 2 (Apache-2.0)** font files from its Apache-licensed repository. Coverage/metrics differ; do not promise replacement of every math/CJK face. |
| Current Noto/DejaVu assets | SIL-OFL / Bitstream Vera-derived terms, depending on exact file | No automatic proprietary-software conflict; notices, naming and font redistribution rights remain separate | Keep only explicitly approved font bytes with full terms, or use the Apache Roboto 2 default above and make additional fonts **external assets**. Documents are not relicensed merely because OFL fonts are embedded. |
| FreeType/text shaping dependencies | FreeType FTL-or-GPL choice; HarfBuzz MIT-style; ICU Unicode terms | **Yes if a GPL-only selection**; permissive alternatives need attribution | Select FreeType's **permissive FTL** option and audited shaping dependencies. If that selected closure is rejected, use **stb_truetype (MIT)** for the limited core glyph path, keeping advanced font processing external; do not claim shaping/hinting equivalence. |
| Statically bundled glibc | LGPL-2.1+ | **Yes** under this owner rule, even with OCCT absent | **Replace in-core** with **musl (MIT)** on Linux and rebuild Skia/dependencies for that toolchain. A user-installed dynamic system libc is an **external OS dependency** alternative, with a clearly changed static-binary promise. The current prebuilt glibc-oriented Skia pack cannot be assumed musl-compatible. |
| GCC C++ runtime / LLVM replacement | libstdc++/libgcc GPL + GCC runtime exception; LLVM libc++/libc++abi/compiler-rt Apache-2.0 + LLVM exceptions | GCC runtime exception can permit closed distribution; not the same restriction as ordinary GPL; audit exact inputs | Prefer **in-core LLVM runtimes** for the permissive closure; retain applicable exception/notice texts. Exclude any runtime input that fails this audit rather than treating an exception as a blanket approval. |
| Later MPL-2.0 candidate | MPL file-level source duties, no blanket whole-product source release | Conditional; owner explicitly allows MPL | **In-core only if** the covered-file source/notice obligation is accepted and fulfilled; otherwise **external** or replace the specific functionality with the MIT/BSD/Apache alternatives above. Do not describe MPL as obligation-free. |

Primary licence evidence: [FFmpeg build-dependent licensing](https://github.com/FFmpeg/FFmpeg/blob/master/LICENSE.md),
[OCCT exception](https://github.com/Open-Cascade-SAS/OCCT/blob/master/OCCT_LGPL_EXCEPTION.txt),
[stb's MIT option](https://github.com/nothings/stb/blob/master/LICENSE),
[Roboto 2 Apache licence](https://github.com/googlefonts/roboto-2/blob/main/LICENSE),
[libvpx licence/patent files](https://github.com/webmproject/libvpx),
[libwebm BSD licence](https://github.com/webmproject/libwebm/blob/main/LICENSE.TXT),
[musl copyright](https://git.musl-libc.org/cgit/musl/tree/COPYRIGHT),
[LLVM runtime licence](https://github.com/llvm/llvm-project/blob/main/libcxx/LICENSE.TXT)
and the exact local/public host audits already cited. Pin versions and retain full
texts when implementing; these names are candidates, not a new shipped dependency set.

**Patent/closure gate:** a permissive copyright licence and a patent grant do not
establish universal patent clearance. If the chosen codec/font still has an unresolved
problem under the owner's rule, it stays external and the always-available core
outputs remain raw frames/PNG sequences. Out-of-process use does not erase licence,
patent, redistribution or source obligations of a separately shipped component.
Do not relabel an in-process plugin as an external process. Record executable/version,
input/output format, unit/colour conventions, timeouts, errors and independent notices
for each optional interface. Existing MP4 examples may continue to use user-installed
FFmpeg; no new core codec or musl build is claimed by this documentation amendment.

## Gallery, autorun and compatibility contracts

The checked-in gallery contains 50 showcase records. Impact from `showcases.json`:

| Host | Compositions | Leading IDs |
|---|---:|---|
| lmvideo | 22 | 26–31, 33, 35–37, 39–50 |
| lmdraw | 4 | 02, 05, 11, 13 |
| lmcad | 2 | 04, 10 |
| lmmagnum | 1 | 38 |
| lmfilament / lmblender | 0 / 0 | Their own public galleries still require preservation. |

Within gallery scripts, lmvideo has **28** install declarations: 13 pinned to
`v0.1.25` and 15 to `v0.1.28`; lmmagnum has one `v0.2.14` pin. lmdraw/lmcad
use latest, including a nested lmdraw program string. Never rewrite nested source
by a blind global substitution. The lmvideo public examples additionally pin
`v0.1.23`, `v0.1.25`, `v0.1.26` and `v0.1.29`; older preserved versions remain valid.

Public example-file counts observed: lmvideo 44, lmdraw 38, lmcad 38, lmblender 99,
lmfilament 38, lmmagnum 37. These are recursive `.lms` file counts, not README
caption counts or distinct runnable stories. Old private/source READMEs can differ.

Four independent contracts must survive:

1. **URL:** retain `lmctl-ai/<old>/main/examples/<path>.lms`, all relative inputs and
   committed pictures/captions. Renaming a product/repo does not redirect raw URLs.
2. **Installer:** retain `github:lmctl-ai/<old>@<tag>` and `@latest`; aliases must be
   real correctly named per-platform release assets, with SHA256SUMS and notices.
3. **Discovery/load:** retain the exact legacy schema bytes, signatures, contexts,
   CLI/result/error protocol and schema hash. The new product and all new aliases expose one canonical schema. Old hashes
   remain supported by frozen old binaries, not embedded legacy registries. Source
   migration must translate types/units and recompile; bytecode is not rewritten by
   text substitution.
4. **Visual/output:** preserve output filenames, dimensions, input resolution,
   alpha/colour handling, font metrics, frame order and encoding behaviour. A program
   that exits zero but changes the README picture is not an accepted migration.

`catalog.json` drives host cards, links, release badges and attributed source-image
snapshots; `showcases.json` drives composition hosts, captions and output paths.
`scripts/build-readme.py` regenerates README and attribution; `tests/check_gallery.py`
and `scripts/run-examples.py` validate picture bytes/dimensions and empty-directory
runs. Update manifests and regenerate, rather than hand-editing generated tables.
Keep original image attribution/source hashes until deliberately re-rendered.

## Target architecture and implementation feasibility

Retain lmvideo's C++ host, schema loader and output protocol. Add a typed mesh scene
and offscreen 3D viewport producing linear/premultiplied RGBA for Skia composition.
Retain useful Canvas/Plot/Panel/Document/Picture capabilities while normalizing
old Surface/Image and frame concepts onto the one Image model. Preserve signatures
where coherent; any changed signature requires an explicit source migration, not
a second legacy registry inside the core. Evaluate explicit frame state at frame
index/time before rendering; a still is a one-frame job. General transform/material
tracks, asset caching and random-access frame evaluation are new engineering tasks.

Choose one primary CPU 3D implementation, initially based on the existing Magnum
geometry/render structure and selected Filament-preview features. Keep GPU capability
out of baseline acceptance until an actual backend produces/readbacks pixels on both
Linux architectures and the supported desktop targets. Do not carry Filament noop
engine construction solely to render the CPU image.

A 3D viewport can become a raster Image in an otherwise vector SVG/PDF. Preserve
premultiplication, colour conversion and a defined depth/alpha contract. A geometry
layer does not automatically implement GI, refraction, image-based lighting, arbitrary
Filament shaders or all Cycles material modes. Long 1080p/4K videos need measured
frame-time/RSS budgets; one small still-scene run cannot establish throughput.

Use current OBJ/STL exchange from lmcad first, with explicit unit/appearance/camera
metadata alongside the mesh. Add glTF export only as a separate scoped feature;
CAD currently has none. The render-only lmblender backend consumes the product exporter's versioned GLB/job profile; its existing glTF import alone does not establish
complete camera/material fidelity.

**Hard compatibility limits:** lmdraw's arbitrary SVG-style attributes, gradients,
embedded fonts and imported SVG need adapters and image tests, not a CLI rename.
Filament's material source compilation, `material_file`, `Material.save`, package
size and material-package ABI either retain the real toolchain in an external
tool/old executable or are explicitly excluded from migrated examples. Do not
fake compiled packages or silently treat uploaded PBR maps as shaded maps. The old
public Filament release remains available if its exact contract cannot be reproduced.

## CI and peer-release impact

The checked-out [peer model](05-closed-source-peer-model.md) and newer
[release-cycle implementation](06-release-cycle.md) are complementary: private
implementation CI publishes to public demo/release peers; public content is authoritative.
The release-cycle registry lives in `lmctlhq/lmctl-mono-test/releases.json`, not here.
Its current staged release path is **Linux x64/arm64 on Ubuntu 22.04**, with public
prerelease verification followed by explicit latest promotion. Private Actions are
currently disabled for budget; this note neither enables nor dispatches them.

Observed latest-release platform assets:

| Host | Linux x64/arm64 | macOS x64/arm64 | Windows x64 |
|---|---|---|---|
| lmvideo | both | both | absent |
| lmdraw | both | both | present |
| lmcad | both | both | present |
| lmblender | both | both | present |
| lmfilament | both | both | absent |
| lmmagnum | both | both | present |

A merge onto lmvideo cannot silently remove the working Windows product from lmdraw
or lmmagnum. Keep their last Windows binaries usable until the unified Windows
Skia/3D/encoder path passes or the owner explicitly changes support policy. A Linux-only
new release cadence does not erase the installed historic macOS/Windows contract.

Build the core once per supported platform; test the one canonical registry, name
aliases and migrated examples against immutable **public peer commit SHAs**. Publish each alias to its own public
repo using properly scoped publisher credentials; the existing single-peer token
cannot be assumed to write all peers. Reuse signed/checksummed artifacts where bytes
are identical, but name them `<legacy>-<os>-<arch>[.exe]` and preserve each repo's
version banner/tag checks. Cross-peer latest promotion is not atomic: stage all aliases,
verify each fresh-cache installer/hash, then promote with rollback to previous releases.
Record one core source SHA plus canonical-schema/migration-tool versions in every release manifest.

Remove independent build/release entries for retired engines only after the common
pipeline publishes their tested compatibility assets. Keep CAD separate and lmblender as the optional render-only process.
A new product slug is optional; retaining lmvideo avoids a new repo identity and another
install-coordinate migration. No repository creation, visibility change, history rewrite
or force-push is part of this design.

## Phased migration with acceptance gates

| Phase | Work | Exit evidence |
|---|---|---|
| 0. Freeze inventory | Capture schemas and current public example SHA, release tags/hashes, platform support and outputs; maintain explicit material-package exceptions. | All 618 domain declarations classified as kept, adapted, separate or unsupported; no missing declaration hidden in totals. |
| 1. Compose a CPU viewport in lmvideo | One scene convention (Y-up, degrees, vertical FOV), primary CPU renderer, asset/material layer and Skia composition; preserve existing APIs. | Existing lmvideo examples unchanged; representative 3D scenes, frame time/RSS and stripped binary measured. Raw RGBA hashes repeat on the same pinned environment. |
| 2. Migrate sources and add name aliases | One canonical schema for lmvideo/lmdraw/lmimg/Magnum/Filament aliases; mechanically migrate supported source calls and units, then recompile. Frozen old releases cover unmigrated contracts; no compatibility subcommand selects a second schema. | Every affected public example runs from an empty directory. Pixel/geometry/alpha/measurement/error tests; old pins still install. Unsupported material packages remain external rather than faked. |
| 3. Stage peer releases | Common core, per-peer assets/checksums/notices, immutable public content snapshots; Linux x64/arm64 minimum, old desktop releases retained. | Fresh-cache `lmscript install` for every old name, pinned tags and latest; version/schema/checksum checks and per-job results. No private-billing dispatch during the hold. |
| 4. Migrate content mechanically where possible | Rewrite structured source/API call sites with reviewed unit/FOV conversions; update gallery manifests, captions and previews one composition at a time. | All 50 gallery compositions run; the affected 31 produce their declared outputs. All old raw autorun URLs still resolve. New compiler bytecode built from the new schema. |
| 5. Retire independent engines | Alias support for **N = 6 released compatibility versions and at least 3 months**, whichever is longer, starting only after platform acceptance. | Last compatibility assets, old example URLs and pinned tags retained indefinitely; ownership of security fixes and alias failure rollback recorded. Archive only implementation maintenance, not working download paths. |

Six releases is a proposed policy, not an existing promise. Keep compatibility
installation endpoints after active support ends. No exact CPU cross-OS pixel or
video-container byte guarantee is claimed: font libraries, Skia builds, compiler
floating-point choices, codec versions and metadata differ. Gate same-platform repeat
hashes separately from cross-platform image tolerance/semantic checks. PDF metadata
and FFmpeg configuration require explicit reproducibility controls.

## Risks and owner decisions

Main risks: the limited exact signature overlap; SVG/font/attribute differences;
material compiler ABI; Y-up/Z-up and degrees/radians/FOV errors; transparent/depth
composition and colour conversion; 3D frame throughput and memory; losing Windows;
legacy raw schema binding; partial cross-peer publication; font/runtime notices;
and a single large release blocking unchanged 2D users.

Owner questions (five):

1. Keep lmvideo's name/install coordinate, or budget an additional product rename and alias?
2. Accept a CPU-primary first release with explicit quality/performance limits, deferring real GPU?
3. Must all Filament material compiler/package APIs remain supported, or may they stay on the frozen legacy release while scene examples migrate?
4. Require the proposed six-release/three-month adapter window, and must new Windows/macOS compatibility builds continue alongside the Linux-only release cycle?
5. Approve mutable Image operations plus explicit copy (closest to current lmimg), or budget immutable-image dataflow rewrites and associated colour/alpha review?

## Cross-review with the other design notes

Read [ResearchOpus](08-consolidation-ResearchOpus.md) while preparing this note.
Agreement: lmvideo base, one own CPU renderer, CAD/Cycles separate, a bounded alias
window, one scene vocabulary and rasterized 3D viewports inside 2D layout.
Inventory amendments to that note's initial draft: lmvideo has **205 methods / 218
including free overloads**, lmdraw **46 methods**, lmblender **99 recursive public
example files**; the six exact schemas are indexed here. Skia's currently selected
primitive shaping path is not proof of full HarfBuzz/RTL layout. WebP/glTF-export/
video-input layers are proposed additions, not all current outputs. `import_gltf`
already exists in lmblender. Filament material-package APIs and Windows support
block an unconditional drop-in alias. The current release-cycle is staged Linux
x64/arm64, not automatic full-platform publication on every main push. Cross-OS
byte determinism and one-small-scene timing must remain unproven until measured.

Read [ResearchArgon](08-consolidation-ResearchArgon.md) after its first draft appeared.
Agreement: retain lmvideo's identity, additive Scene3D/viewports, explicit 3D names,
projected 2D annotations, separate CAD/Cycles and a CPU-primary first release.
The feasibility inventory requires these amendments to that draft's assumptions:

- Its lmdraw Skia premise, 15 MB footprint, 38-method total and 33 verbatim matches
  are not the checked-out contracts: LunaSVG/PlutoVG, 5.55 MB released x64 and 46
  declarations are measured above. Identical owner-qualified overlap is six;
  broader diagram vocabulary still needs parameter/type/attribute adapters.
- Current lmcad has Scene/Shape/Sketch/Animation, not Part/Assembly or public
  STEP/IGES/BREP/DXF export. Current lmblender is in-process Cycles with PNG/EXR,
  not a Blender Python launcher or a `.blend` exporter. Those example operations
  must remain labelled future work or be replaced with current STL/OBJ calls.
- Its 18–18.5 MB total and sub-400 KB growth projection are not measured: today's
  released lmvideo x64 alone is 30,138,784 bytes. The alleged dependency-free
  Filament mesh source includes `geometry/SurfaceOrientation.h` and uses Filament
  math/tangent builders (`cpp/mesh.cpp:346–349`). Extracting primitive algorithms
  may remove those dependencies, but this requires an actual build; retaining a
  tested Magnum subset is the conservative first implementation.
- Its unchanged-base examples propose replacements for existing calls:
  `font(float)`, `image_file(string)`, `pdf_document(float,float)`,
  `Plot.title/series`, `Paint.stroke()` and `Document.finish()->Picture` are the
  actual signatures. `font_Sub`, `Plot.set_title/add_series`, `canvas.resize`,
  `video.next_frame`, and `Document.save_png` are not existing API guarantees.
  The six task examples are design sketches until expressed in the supported
  block/range syntax and a concrete additive schema; they are not runnable demos.
- The legacy inventory contexts were **scene:Scene** for lmdraw/Magnum and
  **fil:Filament** for Filament. Addition 2 now chooses source migration and one
  canonical registry, rather than retaining those contexts as extra core schemas.
  Appending/changing declarations changes raw schema hashes: old bytecode uses
  pinned historical binaries; migrated source must be recompiled for the new core.
- Gallery exposure is 22 lmvideo, four lmdraw and one Magnum composition;
  Magnum/Filament are published products, not unreferenced/unpublished plans.
  A two-release shell-wrapper window does not cover their existing installer and
  Windows contracts. This note retains the longer proposed six-release/three-month
  window and frozen assets pending an owner decision.
- Reported 18 ms/frame, 3.4x threading speedup, tiny line-count estimates and
  cross-platform byte determinism are unverified estimates. Glyph extrusion
  also needs contour flattening, holes/winding, tessellation and failure limits;
  it is not supplied by merely calling `SkFont::getPath`.

These differences change migration cost and acceptance gates, rather than the
shared recommendation to consolidate the media product. Current-source evidence
above takes precedence over size, method-count or performance estimates.

## Appendix A — complete checked-out host API declarations

These are public contract declarations extracted from each host-only schema, not
implementation source. `self` is preserved as declared; the loader/registry normalizes
it to its owning type where required. Contexts are listed separately above. No std
function is omitted from a host API count by guesswork: these source schemas contain
only the domain surface and build-time standard merging remains a separate concern.

<details>
<summary>lmvideo: 218 declarations</summary>

```text
Canvas.activation(float, float, float, string, string) -> Group
Canvas.box(Shape, string, float, float, string, string, string, float, float) -> Shape
Canvas.box(float, float, float, float, string, string, string, float, float) -> Shape
Canvas.circle(float, float, float, Paint) -> void
Canvas.clear(string) -> void
Canvas.clip_rect(float, float, float, float) -> void
Canvas.cluster(float, float, float, float, string, string, string, float, float) -> Shape
Canvas.connector(Shape, string, Shape, string, string, string, string, string, string, float, string, float, float, float) -> Group
Canvas.connector(Shape, string, float, float, string, string, string, string, string, float, string, float, float, float) -> Group
Canvas.connector(float, float, Shape, string, string, string, string, string, string, float, string, float, float, float) -> Group
Canvas.connector(float, float, float, float, string, string, string, string, string, float, string, float, float, float) -> Group
Canvas.cylinder(float, float, float, float, string, string, string, float) -> Shape
Canvas.diamond(float, float, float, float, string, string, string, float) -> Shape
Canvas.draw_diagram() -> void
Canvas.grid(float, float, float, float, int, int, float, float) -> Grid
Canvas.group() -> Group
Canvas.image(Image, float, float) -> void
Canvas.image_rect(Image, float, float, float, float) -> void
Canvas.lifeline(float, float, float, string) -> Group
Canvas.line(float, float, float, float, Paint) -> void
Canvas.message(float, float, float, float, string, bool, string) -> Group
Canvas.note(float, float, float, float, string, string, string, float) -> Shape
Canvas.oval(float, float, float, float, Paint) -> void
Canvas.panel(float, float, float, float) -> Panel
Canvas.path(Path, Paint) -> void
Canvas.picture(Picture, float, float, float, float) -> void
Canvas.plot(float, float, float, float) -> Plot
Canvas.rect(float, float, float, float, Paint) -> void
Canvas.restore() -> void
Canvas.rotate(float) -> void
Canvas.round_rect(float, float, float, float, float, float, Paint) -> void
Canvas.save() -> void
Canvas.scale(float, float) -> void
Canvas.self_message(float, float, string, string) -> Group
Canvas.svg(Svg, float, float, float, float) -> void
Canvas.text(string, float, float, Font, Paint) -> void
Canvas.translate(float, float) -> void
Document.canvas() -> Canvas
Document.finish() -> Picture
Font.bold(bool) -> Font
Font.measure(string) -> float
Grid.cell(int, int) -> Shape
Group.add(Group) -> Group
Group.set_attr(string, string) -> Group
Heatmap.cell(int, int, float) -> Heatmap
Heatmap.clear() -> Heatmap
Heatmap.colorbar(bool) -> Heatmap
Heatmap.contours(int, string, float) -> Heatmap
Heatmap.draw() -> Heatmap
Heatmap.labels(bool) -> Heatmap
Heatmap.palette(string) -> Heatmap
Heatmap.range(float, float) -> Heatmap
Image.height() -> int
Image.width() -> int
ImageView.fit(string) -> ImageView
Keyframe.color() -> string
Keyframe.x() -> float
Keyframe.y() -> float
Keyframes.add(float, float, string) -> Keyframes
Keyframes.at(int) -> Keyframe
Keyframes.len() -> int
LayoutItem.align(string, string) -> LayoutItem
LayoutItem.border(string) -> LayoutItem
LayoutItem.fill(string) -> LayoutItem
LayoutItem.grid(int, int, int, int) -> LayoutItem
LayoutItem.image() -> ImageView
LayoutItem.max_size(float, float) -> LayoutItem
LayoutItem.min_size(float, float) -> LayoutItem
LayoutItem.pack(string, string, bool) -> LayoutItem
LayoutItem.panel() -> Panel
LayoutItem.place(float, float, float, float) -> LayoutItem
LayoutItem.plot() -> Plot
LayoutItem.preferred_size(float, float) -> LayoutItem
LayoutItem.shape() -> Shape
LayoutItem.sticky(string) -> LayoutItem
LayoutItem.text() -> Text
LayoutItem.weight(float) -> LayoutItem
Output.fail(string) -> void
Output.print(string) -> void
Paint.alpha(float) -> self
Paint.antialias(bool) -> self
Paint.blur(float) -> self
Paint.color(string) -> self
Paint.dash(float, float) -> self
Paint.fill() -> self
Paint.gradient(float, float, float, float, string, string) -> self
Paint.stroke() -> self
Paint.stroke_cap(string) -> self
Paint.stroke_join(string) -> self
Paint.stroke_width(float) -> self
Panel.add_glue() -> LayoutItem
Panel.add_image(Image) -> LayoutItem
Panel.add_panel() -> LayoutItem
Panel.add_plot() -> LayoutItem
Panel.add_shape(string) -> LayoutItem
Panel.add_text(string) -> LayoutItem
Panel.align(string, string) -> Panel
Panel.background(string) -> Panel
Panel.column_weight(int, float) -> Panel
Panel.columns(int) -> Panel
Panel.draw() -> Panel
Panel.edge(string, float) -> Panel
Panel.gap(float) -> Panel
Panel.manager(string) -> Panel
Panel.max_size(float, float) -> Panel
Panel.min_size(float, float) -> Panel
Panel.padding(float, float, float, float) -> Panel
Panel.row_weight(int, float) -> Panel
Path.circle(float, float, float) -> self
Path.close() -> self
Path.cubic_to(float, float, float, float, float, float) -> self
Path.line_to(float, float) -> self
Path.move_to(float, float) -> self
Path.oval(float, float, float, float) -> self
Path.quad_to(float, float, float, float) -> self
Path.rect(float, float, float, float) -> self
Path.round_rect(float, float, float, float, float, float) -> self
PdfDocument.add_page(Picture) -> PdfDocument
PdfDocument.pages() -> int
PdfDocument.write(string) -> void
Picture.draw(Canvas, float, float, float, float) -> void
Picture.height() -> int
Picture.pdf(string) -> void
Picture.png(string, int) -> void
Picture.skp(string) -> void
Picture.svg(string) -> void
Picture.width() -> int
Plot.annotate(float, float, string, string) -> Plot
Plot.background(string) -> Plot
Plot.draw() -> Plot
Plot.grid(bool) -> Plot
Plot.heatmap(string, int, int) -> Heatmap
Plot.hline(float, string, float) -> Plot
Plot.inset(float, float, float, float) -> Plot
Plot.legend(string) -> Plot
Plot.quiver(string) -> VectorField
Plot.series(string, string, string) -> Series
Plot.title(string) -> Plot
Plot.vline(float, string, float) -> Plot
Plot.x_date(string) -> Plot
Plot.x_range(float, float) -> Plot
Plot.x_scale(string) -> Plot
Plot.x_symlog(float) -> Plot
Plot.xlabel(string) -> Plot
Plot.y2_range(float, float) -> Plot
Plot.y2label(string) -> Plot
Plot.y_range(float, float) -> Plot
Plot.y_scale(string) -> Plot
Plot.y_symlog(float) -> Plot
Plot.ylabel(string) -> Plot
Series.add(float, float) -> Series
Series.add_band(float, float, float) -> Series
Series.add_error(float, float, float, float) -> Series
Series.axis(string) -> Series
Series.box(float, float, float, float, float) -> Series
Series.clear() -> Series
Series.color(string) -> Series
Series.dash(string) -> Series
Series.donut(float) -> Series
Series.group(string) -> Series
Series.histogram(int) -> Series
Series.marker(string) -> Series
Series.stack(string) -> Series
Series.width(float) -> Series
Shape.cx() -> float
Shape.cy() -> float
Shape.fill(string) -> Shape
Shape.label(string) -> Shape
Shape.radius(float) -> Shape
Shape.set_attr(string, string) -> Shape
Shape.stroke(string) -> Shape
Shape.stroke_width(float) -> Shape
Surface.canvas() -> Canvas
Surface.image() -> Image
Surface.pdf(string) -> void
Surface.png(string) -> void
Surface.svg(string) -> void
Svg.height() -> float
Svg.width() -> float
TemplateSvg.render(float, float, string) -> Svg
Text.align(string) -> Text
Text.bold(bool) -> Text
Text.color(string) -> Text
Text.size(float) -> Text
VectorField.add(float, float, float, float) -> VectorField
VectorField.clear() -> VectorField
VectorField.color(string) -> VectorField
VectorField.draw() -> VectorField
VectorField.scale(float) -> VectorField
VectorField.streamlines(bool) -> VectorField
Video.begin() -> void
Video.count() -> int
Video.crf(int) -> void
Video.end() -> void
Video.fps(int) -> void
Video.frame() -> void
Video.frames(int) -> void
Video.height() -> int
Video.index() -> int
Video.output(string) -> void
Video.save_frame(string) -> void
Video.size(int, int) -> void
Video.t() -> float
Video.time() -> float
Video.width() -> int
fn document(int, int) -> Document
fn font(float) -> Font
fn image_file(string) -> Image
fn keyframes() -> Keyframes
fn mix(string, string, float) -> string
fn paint() -> Paint
fn path() -> Path
fn pdf_document(float, float) -> PdfDocument
fn picture_file(string) -> Picture
fn surface(int, int) -> Surface
fn svg(string) -> Svg
fn svg_file(string) -> Svg
fn template_svg(string) -> TemplateSvg
```

</details>

<details>
<summary>lmdraw: 46 declarations</summary>

```text
Gradient.stop(float, string) -> Gradient
Grid.cell(int, int) -> Shape
Group.add(Group) -> Group
Group.add(Node) -> Group
Group.set_attr(string, string) -> Group
Node.set_attr(string, string) -> Node
Scene.activation(float, float, float, string, string) -> Group
Scene.arrow(float, float, float, float, string, float) -> Node
Scene.axes(float, float, float, float, float, float, float, float, int, string) -> Group
Scene.box(Shape, string, float, float, string, string, string, float, float) -> Shape
Scene.box(float, float, float, float, string, string, string, float, float) -> Shape
Scene.canvas(int, int, string) -> Scene
Scene.circle(float, float, float, string) -> Node
Scene.cluster(float, float, float, float, string, string, string, float, float) -> Shape
Scene.connector(Shape, string, Shape, string, string, string, string, string, string, float, string, float, float, float) -> Group
Scene.connector(Shape, string, float, float, string, string, string, string, string, float, string, float, float, float) -> Group
Scene.connector(float, float, Shape, string, string, string, string, string, string, float, string, float, float, float) -> Group
Scene.connector(float, float, float, float, string, string, string, string, string, float, string, float, float, float) -> Group
Scene.cylinder(float, float, float, float, string, string, string, float) -> Shape
Scene.diamond(float, float, float, float, string, string, string, float) -> Shape
Scene.ellipse(float, float, float, float, string) -> Node
Scene.grid(float, float, float, float, int, int, float, float) -> Grid
Scene.group() -> Group
Scene.image(string, float, float, float, float) -> Node
Scene.legend(float, float, string, string, string) -> Group
Scene.legend(float, float, string, string, string, string) -> Group
Scene.lifeline(float, float, float, string) -> Group
Scene.line(float, float, float, float, string, float) -> Node
Scene.linear_gradient(string, float, float, float, float) -> Gradient
Scene.load_font(string, string, bool) -> void
Scene.load_svg(string, string) -> Node
Scene.log_axes(float, float, float, float, float, float, float, float, bool, bool, int, string) -> Group
Scene.log_axes(float, float, float, float, float, float, float, float, int, string) -> Group
Scene.measure_text(string, float, bool) -> float
Scene.message(float, float, float, float, string, bool, string) -> Group
Scene.note(float, float, float, float, string, string, string, float) -> Shape
Scene.path(string, string, string, float) -> Node
Scene.polyline(string, string, float) -> Node
Scene.rect(float, float, float, float, string) -> Node
Scene.render_png(string, int, int, int) -> void
Scene.self_message(float, float, string, string) -> Group
Scene.text(float, float, float, string, string) -> Node
Scene.text(float, float, float, string, string, float) -> Node
Shape.cx() -> float
Shape.cy() -> float
Shape.set_attr(string, string) -> Shape
```

</details>

<details>
<summary>lmcad: 64 declarations</summary>

```text
Animation.add_frame() -> Animation
Animation.finish() -> void
Camera.clipping(float, float) -> Camera
Camera.look_at(float, float, float, float, float, float) -> Camera
Keyframe.b() -> float
Keyframe.g() -> float
Keyframe.r() -> float
Keyframe.time() -> float
Keyframe.x() -> float
Keyframe.y() -> float
Keyframe.z() -> float
Keyframes.at(int) -> Keyframe
Keyframes.len() -> int
Light.intensity(float) -> Light
Material.color(float, float, float) -> Material
Material.roughness(float) -> Material
Material.shininess(float) -> Material
Material.specular(float) -> Material
Scene.ambient(float) -> Scene
Scene.animation(string, int, int, int) -> Animation
Scene.assert_close(float, float, float) -> void
Scene.background(float, float, float) -> Scene
Scene.box(float, float, float, Material) -> Shape
Scene.camera(float, float, float, float, float, float, float) -> Camera
Scene.cylinder(float, float, Material) -> Shape
Scene.directional_light(float, float, float, float) -> Light
Scene.export_obj(string) -> void
Scene.export_stl(string) -> void
Scene.extrude(Sketch, float, Material) -> Shape
Scene.fill_light(float, float, float, float) -> Light
Scene.fit_camera(float, float) -> Camera
Scene.render_png(string, int, int) -> void
Scene.render_ppm(string, int, int) -> void
Scene.revolve_y(Sketch, Material) -> Shape
Scene.sketch() -> Sketch
Scene.sphere(float, Material) -> Shape
Scene.supersample(int) -> Scene
Scene.tube_between(float, float, float, float, float, float, float, Material) -> Shape
Shape.chamfer(float) -> Shape
Shape.color(float, float, float) -> Shape
Shape.cut(Shape) -> Shape
Shape.fillet(float) -> Shape
Shape.hollow(float) -> Shape
Shape.hollow_top(float) -> Shape
Shape.intersect(Shape) -> Shape
Shape.max_x() -> float
Shape.max_y() -> float
Shape.max_z() -> float
Shape.min_x() -> float
Shape.min_y() -> float
Shape.min_z() -> float
Shape.mirror(string) -> Shape
Shape.name(string) -> Shape
Shape.position(float, float, float) -> Shape
Shape.rotate(float, float, float) -> Shape
Shape.scale(float, float, float) -> Shape
Shape.translate(float, float, float) -> Shape
Shape.union(Shape) -> Shape
Shape.visible(bool) -> Shape
Shape.volume() -> float
Sketch.close() -> Sketch
Sketch.point(float, float) -> Sketch
fn material() -> Material
fn read_keyframes_csv(string) -> Keyframes
```

</details>

<details>
<summary>lmblender: 96 declarations</summary>

```text
Material.backface_culling(bool) -> void
Material.bump(float, float, float) -> void
Material.keyframe_color(int, float, float, float, string) -> void
Material.keyframe_emission_strength(int, float, string) -> void
Material.mix_with(Material, float) -> void
Material.mix_with_texture(Material, string) -> void
Material.subsurface(float, float, float, float, float) -> void
Material.texture_maps(string, string, string, string) -> void
Material.volume(string, float, float, float, float) -> void
Mesh.keyframe_transform(int, float, float, float, string) -> void
Mesh.keyframe_visible(int, bool, string) -> void
Mesh.material_count() -> int
Mesh.max_x() -> float
Mesh.max_y() -> float
Mesh.max_z() -> float
Mesh.min_x() -> float
Mesh.min_y() -> float
Mesh.min_z() -> float
Mesh.rotate_x(float) -> void
Mesh.rotate_y(float) -> void
Mesh.rotate_z(float) -> void
Mesh.scale(float, float, float) -> void
Mesh.set_material(Material) -> void
Mesh.set_smooth(bool) -> void
Mesh.translate(float, float, float) -> void
Mesh.triangle_count() -> int
Mesh.vertex_count() -> int
Scene.area_light(float, float, float, float, float, float, float, float, float, float, float) -> void
Scene.area_light_shape(float, float, float, float, float, float, float, float, float, float, float, float, string) -> void
Scene.arrow_between(float, float, float, float, float, float, float) -> Mesh
Scene.camera_dof(float, float) -> void
Scene.camera_keyframe(int, float, float, float, float, float, float, string) -> void
Scene.camera_look_at(float, float, float, float, float, float, float) -> void
Scene.camera_optics_keyframe(int, float, float, string) -> void
Scene.camera_orthographic(float, float, float, float, float, float, float) -> void
Scene.capsule(float, float, int, int) -> Mesh
Scene.checker_ground(float, float) -> void
Scene.checker_material(float, float, float, float, float, float, float, float) -> Material
Scene.checkmark(float, float, float, float, float) -> Mesh
Scene.cone(float, float, int, bool) -> Mesh
Scene.cube(float) -> Mesh
Scene.cylinder(float, float, int, bool) -> Mesh
Scene.denoise_quality(string) -> void
Scene.depth_range(float, float) -> void
Scene.environment_texture(string, float, float) -> void
Scene.expect_int(int, int) -> void
Scene.exposure(float) -> void
Scene.fit_camera(float) -> void
Scene.glow_orb(float, float, float, float, float, float, float, float) -> Mesh
Scene.ground_plane(float, float, float, float, float) -> void
Scene.hair_patch(float, float, float, float, int, float, float) -> Mesh
Scene.hair_sphere(float, float, float, float, int, float, float) -> Mesh
Scene.image_material(string, float) -> Material
Scene.import_gltf(string) -> Mesh
Scene.import_obj(string) -> Mesh
Scene.import_ply(string) -> Mesh
Scene.import_stl(string) -> Mesh
Scene.instance_mesh(Mesh, float, float, float, float, float, float) -> Mesh
Scene.label(string, float, float, float, float) -> Mesh
Scene.light_clamp(float, float) -> void
Scene.load_preset(string) -> void
Scene.loft(string, string, bool) -> Mesh
Scene.material(float, float, float, float, float, float, float, float, float, float) -> Material
Scene.material_from_palette(string) -> Material
Scene.motion_blur(bool, float) -> void
Scene.noise_material(float, float, float, float, float, float, float, float) -> Material
Scene.plane(float) -> Mesh
Scene.point_light(float, float, float, float, float, float, float) -> void
Scene.point_light_keyframe(int, int, float, string) -> void
Scene.preset_param(string, float) -> void
Scene.ramp_material(float, float, float, float, float, float, float, float) -> Material
Scene.render_apng(string, int, int, int, int, int, int) -> void
Scene.render_exr(string, int, int, int) -> void
Scene.render_passes(string, int, int, int) -> void
Scene.render_png(string, int, int, int) -> void
Scene.render_preset(string) -> void
Scene.render_sequence(string, int, int, int, int, int) -> void
Scene.render_settings(int, int, bool) -> void
Scene.render_timeout(int) -> void
Scene.ring_arc(float, float, float, float, float, float, float, int) -> Mesh
Scene.set_threads(int) -> void
Scene.set_view_transform(string) -> void
Scene.sky_texture(float, float, float) -> void
Scene.spot_light(float, float, float, float, float, float, float, float, float, float, float, float) -> void
Scene.strand(string, float, float, int) -> Mesh
Scene.studio_setup() -> void
Scene.sun_light(float, float, float, float, float, float, float, float) -> void
Scene.toon_outline(Mesh, float, float, float, float) -> Mesh
Scene.torus(float, float, int, int, bool) -> Mesh
Scene.transparent_background(bool) -> void
Scene.tube_between(float, float, float, float, float, float, float) -> Mesh
Scene.use_preset(string) -> void
Scene.uv_sphere(float, int, int, bool) -> Mesh
Scene.version() -> string
Scene.wall_plane_y(float, float, float, float, float) -> void
Scene.world_color(float, float, float, float) -> void
```

</details>

<details>
<summary>lmfilament: 62 declarations</summary>

```text
Filament.box(float, float, float) -> Mesh
Filament.capsule(float, float, int) -> Mesh
Filament.cone(float, float, int) -> Mesh
Filament.cylinder(float, float, int) -> Mesh
Filament.icosphere(float, int) -> Mesh
Filament.material(string, string) -> Material
Filament.material_file(string) -> Material
Filament.mesh_obj(string) -> Mesh
Filament.plane(float, float) -> Mesh
Filament.ring(float, float, int) -> Mesh
Filament.scene() -> Scene
Filament.sphere(float, int) -> Mesh
Filament.text(string, float) -> Mesh
Filament.texture(int, int) -> Texture
Filament.texture_checker(int, int, float, float, float, float, float, float) -> Texture
Filament.texture_file(string) -> Texture
Filament.triangle() -> Mesh
Filament.tube_between(float, float, float, float, float, float, float) -> Mesh
Filament.version() -> string
Material.name() -> string
Material.package_size() -> int
Material.save(string) -> void
Material.set_float(string, float) -> Material
Material.set_float3(string, float, float, float) -> Material
Material.set_float4(string, float, float, float, float) -> Material
Material.set_texture(string, Texture) -> Material
Mesh.compute_tangents() -> Mesh
Mesh.has_colors() -> bool
Mesh.has_tangents() -> bool
Mesh.save_obj(string) -> void
Mesh.triangle_count() -> int
Mesh.vertex_count() -> int
Node.parent(Node) -> Node
Node.rotate(float, float, float) -> Node
Node.scale(float, float, float) -> Node
Node.translate(float, float, float) -> Node
Part.parent(Node) -> Part
Part.rotate(float, float, float) -> Part
Part.scale(float, float, float) -> Part
Part.translate(float, float, float) -> Part
Part.visible(bool) -> Part
Scene.add(Mesh, Material) -> Scene
Scene.add_at(Mesh, Material, float, float, float) -> Scene
Scene.add_part(Mesh, Material) -> Part
Scene.camera(float, float, float, float, float, float, float) -> Scene
Scene.directional_light(float, float, float, float, float, float, float) -> Scene
Scene.light_count() -> int
Scene.node() -> Node
Scene.point_light(float, float, float, float, float) -> Scene
Scene.render_frames(int) -> int
Scene.render_png(string, int, int) -> void
Scene.renderable_count() -> int
Scene.shadows(bool) -> Scene
Scene.skybox(float, float, float) -> Scene
Scene.sun(float) -> Scene
Texture.filter(string) -> Texture
Texture.height() -> int
Texture.pixel(int, int, float, float, float) -> Texture
Texture.repeat(float, float) -> Texture
Texture.save_png(string) -> void
Texture.width() -> int
Texture.wrap(string) -> Texture
```

</details>

<details>
<summary>lmmagnum: 60 declarations</summary>

```text
Camera.look_at(float, float, float, float, float, float) -> Camera
Group.parent(Group) -> Group
Group.rotate(float, float, float) -> Group
Group.scale(float, float, float) -> Group
Group.translate(float, float, float) -> Group
Light.intensity(float) -> Light
Material.color(float, float, float) -> Material
Material.roughness(float) -> Material
Material.shininess(float) -> Material
Material.specular(float) -> Material
Material.texture(Texture) -> Material
Scene.accumulate(int, int) -> void
Scene.ambient(float) -> Scene
Scene.background(float, float, float) -> Scene
Scene.box(float, float, float, Material) -> Shape
Scene.camera(float, float, float, float, float, float, float) -> Camera
Scene.capsule(float, float, Material) -> Shape
Scene.cone(float, float, Material) -> Shape
Scene.cube(float, Material) -> Shape
Scene.cylinder(float, float, Material) -> Shape
Scene.directional_light(float, float, float, float) -> Light
Scene.export_obj(string) -> void
Scene.export_ply(string) -> void
Scene.export_stl(string) -> void
Scene.group() -> Group
Scene.icosphere(float, int, Material) -> Shape
Scene.plane(float, Material) -> Shape
Scene.render_png(string, int, int) -> void
Scene.render_ppm(string, int, int) -> void
Scene.reset_accumulation() -> void
Scene.ring(float, float, Material) -> Shape
Scene.save_accumulated_png(string) -> void
Scene.shadows(bool) -> Scene
Scene.shape_count() -> int
Scene.sphere(float, Material) -> Shape
Scene.text(string, float, Material) -> Shape
Scene.texture(int, int) -> Texture
Scene.texture_checker(int, int, float, float, float, float, float, float) -> Texture
Scene.texture_file(string) -> Texture
Scene.triangle(float, float, float, float, float, float, float, float, float, Material) -> Shape
Scene.triangle_count() -> int
Scene.tube_between(float, float, float, float, float, float, float, Material) -> Shape
Shape.color(float, float, float) -> Shape
Shape.name(string) -> Shape
Shape.parent(Group) -> Shape
Shape.rotate(float, float, float) -> Shape
Shape.scale(float, float, float) -> Shape
Shape.texture(Texture) -> Shape
Shape.translate(float, float, float) -> Shape
Shape.triangle_count() -> int
Shape.visible(bool) -> Shape
Texture.filter(string) -> Texture
Texture.height() -> int
Texture.pixel(int, int, float, float, float) -> Texture
Texture.repeat(float, float) -> Texture
Texture.save_png(string) -> void
Texture.width() -> int
Texture.wrap(string) -> Texture
fn magnum_version() -> string
fn material() -> Material
```

</details>

## Appendix B — evidence and reproduction

- Domain inventory: parse `schema/<host>.dsl.json`, expand every overload in
  `functions` and `types.*.methods`, retain the declaration's parameter and return
  types. SHA-256 and source HEAD are recorded above; no schema was modified.
- Release metadata: `gh api repos/lmctl-ai/<host>/releases/latest`, retaining
  `tag_name`, `published_at`, `assets[].name` and `assets[].size`. No private Actions
  were invoked; no release artifact or repository was changed.
- Gallery inventory: parse `catalog.json` and `showcases.json`; scan actual
  `examples/**/*.lms` install declarations, including generated/nested code.
- Renderer/library evidence: lmvideo `cpp/lmvideo.cpp`, `cpp/host.cpp`,
  `cpp/encoder.{hpp,cpp}`, `scripts/skia.lock` and notice staging; lmdraw CMake/README/
  notices; each 3D host's schema/CMake/README, actual rasterizer and license audit;
  lmcad `durable-memory/20-sibling-3d-hosts.md` for shared scene conventions.
- Distribution evidence: this repo's peer/release-cycle notes, registry in
  `lmctlhq/lmctl-mono-test/releases.json` and product publisher templates. Old workflow
  files and latest published asset sets are reported separately from newer policy.

No consolidation prototype was built or timed for this document. A summed standalone
binary size, a single rendered still, successful schema compilation or a green job
with skipped/continue-on-error steps cannot establish the merged product's size,
frame throughput, complete shader support, platform parity or reproducibility.

## Appendix C — lmimg host API declarations (owner addition 2)

Context `img: Img`; legacy inventory only, not an additional target schema.

```text
Animation.add(Image, int) -> Animation
Animation.save(string) -> void
Animation.size() -> int
Curve.point(float, float) -> Curve
Image.blend(Image, string, float, int, int) -> Image
Image.blur(float, float) -> Image
Image.channelmix(float, float, float, float, float, float, float, float, float) -> Image
Image.circle(float, float, float, float, float, float, float) -> Image
Image.clut(Image) -> Image
Image.colormap(string) -> Image
Image.copy() -> Image
Image.crop(int, int, int, int) -> Image
Image.curves(Curve) -> Image
Image.curves_rgb(Curve, Curve, Curve) -> Image
Image.edges(float) -> Image
Image.equalize() -> Image
Image.flip(bool) -> Image
Image.grayscale() -> Image
Image.heal(int, int, int, int, int) -> Image
Image.height() -> int
Image.histogram(string) -> void
Image.hsl(float, float, float) -> Image
Image.invert() -> Image
Image.lens(float) -> Image
Image.levels(float, float, float) -> Image
Image.line(float, float, float, float, float, float, float, float, float) -> Image
Image.mask(Image) -> Image
Image.max(int) -> float
Image.mean(int) -> float
Image.metadata(string, string) -> Image
Image.min(int) -> float
Image.morphology(string, int) -> Image
Image.normalize() -> Image
Image.perspective(float, float, float, float, float, float, float, float) -> Image
Image.pixel(int, int, int) -> float
Image.property(string) -> string
Image.psnr(Image) -> float
Image.rect(float, float, float, float, float, float, float, float) -> Image
Image.resize(int, int) -> Image
Image.rotate(float, float, float, float, float) -> Image
Image.save(string) -> void
Image.selection(int, int, int, int) -> Image
Image.sepia(float) -> Image
Image.set_pixel(int, int, float, float, float, float) -> Image
Image.sharpen(float, float) -> Image
Image.ssim(Image) -> float
Image.stddev(int) -> float
Image.text(float, float, string, float, float, float, float, float) -> Image
Image.threshold(float) -> Image
Image.tilt_shift(float, float, float) -> Image
Image.unsharp(float, float, float, float) -> Image
Image.vignette(float, float) -> Image
Image.width() -> int
Img.animation() -> Animation
Img.assert_close(float, float, float) -> void
Img.assert_true(bool) -> void
Img.canvas(int, int, float, float, float, float) -> Image
Img.curve() -> Curve
Img.eval(string) -> float
Img.hald(int) -> Image
Img.layers(int, int) -> Layers
Img.montage() -> Montage
Img.open(string) -> Image
Img.panel(Image, Image, int) -> Image
Img.pattern(int, int, string, string, string, string) -> Image
Img.print(string) -> void
Img.text_width(string, float) -> float
Layers.add(Image, string, float, int, int) -> Layers
Layers.masked(Image, Image, string, float, int, int) -> Layers
Layers.render() -> Image
Montage.add(Image) -> Montage
Montage.render(int, int, float, float, float, float) -> Image
```
