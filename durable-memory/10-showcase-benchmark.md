# 10 — `lmvideo` Visual Showcase Benchmark: 32 Target Scenes from Blender Demo Files & three.js Examples

**Status**: Benchmark & backlog expansion plan (`docs/plan only`; no product code or asset uploads performed).  
**Companion docs**: [09-lmvideo-backlog.md](09-lmvideo-backlog.md) (Phases 0–7 & Platform Primitives `P.*`), [08-consolidation-ResearchArgon.md](08-consolidation-ResearchArgon.md), [08-consolidation-ResearchOpus.md](08-consolidation-ResearchOpus.md), [08-consolidation-ResearchSol.md](08-consolidation-ResearchSol.md).

---

## 1. Purpose, Catalogue Survey, and Asset Licence Rule

The practical proof that the consolidated `lmvideo` product (`Image`/`Frame`, `Canvas`, `Scene`, `Layout`, `Timeline` with CPU rasterizer + built-in CPU Cycles) has reached visual maturity is its ability to reproduce the iconic classes of imagery demonstrated in:
1. **Blender Demo Files & Splash Gallery** ([official catalogue](https://www.blender.org/download/demo-files/)): surveyed across all 12 upstream categories (*Asset Bundles*, *Blender Splash Artwork* 2.74–5.2, *Hair*, *Simulation*, *Geometry Nodes*, *Grease Pencil*, *EEVEE*, *Rendering*, *Cycles*, *Modeling*, *Animation*, *Physics*).
2. **three.js Official Examples** ([official catalogue](https://threejs.org/examples/), upstream `examples/files.json`): surveyed across `webgl` (221 scenes in the fetched snapshot: animation, camera, clipping, geometry, instancing, lights, loaders, materials,pmrem, points, shadowmap), `webgl / postprocessing` (26 passes: 3DLUT, DoF, GTAO/SSAO, outline, Sobel, bloom), `webgl / advanced`, and `webgpu` (238 examples in the fetched snapshot, used only as visual references; no GPU implementation is scheduled).

The Blender HTML catalogue was fetched directly (the browser reader returned an error),
and three.js's dynamic index was supplemented by its actual
[examples/files.json](https://github.com/mrdoob/three.js/blob/dev/examples/files.json).
Both catalogues change: record the final reference URL/source revision in each scene
manifest. A three.js WebGL/WebGPU implementation is a **visual archetype**, not an
instruction to implement its GPU API, realtime frame rate or browser interaction.

### Strict Asset & Reference Licence Policy

Per the owner's licence gate ([09-lmvideo-backlog.md](09-lmvideo-backlog.md) §Phase P & §6.0):
- **Allowed for direct redistribution / `lmctl.com/assets/v1/` caching**: `CC0-1.0`, `MIT`, `BSD-2-Clause`, `BSD-3-Clause`, `Apache-2.0`, `OFL-1.1`, `Bitstream-Vera`, and **`CC-BY-4.0`** (provided exact creator attribution, source URL, SHA-256, and licence text are recorded in the `P.A2`/`P.3` provenance manifest and emitted by `--notices-used`).
- **Excluded by this benchmark's conservative default asset policy (`CC-BY-NC`, unapproved ShareAlike/GPL assets, or unverified model licences)**:
  - Many Blender splash files (e.g., *3.5 Cozy Kitchen*, *3.3 Scanlands*, *3.1 Secret Deer*, *2.92 Sinosauropteryx*, *2.77 Racing Car*, *Repeat Zone Flower*) are **`CC-BY-SA`** (ShareAlike copyleft on derivatives), and several `three.js` `examples/models/` assets carry mixed or non-standard notices.
  - **Rule**: We do not vendor ShareAlike/GPL data without a separately approved, fulfilled asset-licence plan; default to original replacements, and we **never** copy copyrighted reference renders from `blender.org` or `threejs.org` into our repositories. Where a reference scene is `CC-BY-SA`, too large (e.g., 280 MB–1.4 GB open-movie packs), or relies on Blender-internal node graphs, we **author an original procedural `.lms` scene of the same visual archetype** (or use `CC0` / `CC-BY-4.0` assets) and compare against a written visual specification and reference URL.

**Do not inherit asset rights from the renderer/library licence.** Three.js code is
MIT, but its actual [DamagedHelmet asset README](https://github.com/mrdoob/three.js/blob/dev/examples/models/gltf/DamagedHelmet/README.md)
states **CC-BY-NC**, not the draft's assumed CC-BY-4.0. B06 therefore uses an original
helmet analogue and must not publish those model bytes under a new label. A separately
sourced model with a verified different grant would need its own exact hash/notice.
Likewise, do not call Suzanne, Utah teapot variants, fonts, HDRIs or a whole asset
bundle CC0 without tracing the actual file's grant. The catalogue's CC0/CC-BY labels
are preliminary evidence: record the archive/readme's exact version, author, changes,
licence text and hashes before shipping derived files. CC-BY-SA is not inherently
noncommercial or universally illegal to distribute; excluding it here is a scope
choice. Blender's GPL code licence does not automatically license its demo art.
Unknown/NC/disallowed rights -> original independently designed scene of that kind.
No third-party reference renders are committed, downloaded into our tracked gallery,
or embedded as the comparison column; that column is text plus an external link.
A GPL Blender file also cannot be relabelled Apache because Cycles has that licence.

---

## 2. The 32 Target Benchmark Scenes (Easy $\rightarrow$ Hard)

### Legend
- **Backend**: `raster` = in-core CPU Z-buffer + shadow-map + GGX rasterizer (`Phase 3–5`); `cycles` = in-core permissive CPU Cycles + Embree + OIDN (`Phase 6`); `raster+img` = CPU 3D rasterizer piped through `Phase 2` `Image` post-processing filters; `cad+raster/cycles` = `lmcad` STL/OBJ handoff into `lmvideo`.
- **CPU Budget**: **Provisional acceptance ceilings, not measured capabilities.** Use a named reference CPU with exactly four render threads, pinned build/ISA/denoiser/settings, **900×560** stills or **1280×720** video, and a recorded memory limit. Linux x64 and arm64 get separate baselines; core count alone does not normalize performance. Table times are cold-job wall-clock targets with assets already present locally; report procedural bake/import, render/denoise and encode time separately. Exclude network transfer, never missing computation. Measure uncached frames and report cache hits separately; do not use cached output to claim renderer speed. Tier-3 clips are slow opt-in runs, not PR smoke tests.
- **Current status**: all 32 are **PLANNED**, none passed by this document. Completing phases 3–6 does not imply every G.* extension or imported model feature already exists.

| ID | Target Scene & Archetype | Reference Source (Blender Demo / three.js) | Ref Licence & Asset Strategy | Required Features (Primitives, Shading, Post, Layout) | Backend | CPU Time Budget | Delivering Backlog Phase / Items (`09` + Gaps `G.*`) | Tier |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| **B01** | **PBR Metallic/Roughness Sphere Matrix** | three.js [webgl_materials_physical_clearcoat](https://threejs.org/examples/#webgl_materials_physical_clearcoat) & `lmblender` `pbr-spheres.lms` | **Original `.lms`** (100% procedural) | 5×5 UV/icosphere grid varying `metallic` (0..1) and `roughness` (0.05..1), directional key + fill + rim lights, sky/ground gradient, linear-light 2×2 SSAA | `raster` | ≤5 s | `3.1`, `3.2`, `4.1` (+ `G.4` IBL reflection) | **Tier 1** |
| **B02** | **PCF Soft-Shadow Architectural Pedestal** | three.js [webgl_shadowmap](https://threejs.org/examples/#webgl_shadowmap) & [webgl_lights_spotlights](https://threejs.org/examples/#webgl_lights_spotlights) | **Original `.lms`** (procedural meshes) | Box/cylinder/torus on ground, one 2048² directional shadow map, 3×3 PCF/bias and spotlight fill (not a claim of spotlight shadows) | `raster` | ≤8 s | `3.1`, `3.2`, `4.3` | **Tier 1** |
| **B03** | **Cube Diorama Low-Poly Isometric Cutaway** | Blender Asset Bundle: *Cube Diorama* (`asset-demo-bundle-3.0-cube-diorama.zip`) | **Ref: `CC0` (11 MB)**; build clean procedural isometric room in `.lms` | Orthographic camera (`set_camera_ortho`), hierarchical `Node3D` room walls/props, flat + smooth PBR shading, directional sun shadow, warm palette | `raster` | ≤5 s | `3.1`, `3.2`, `4.1`, `4.3` | **Tier 1** |
| **B04** | **Procedural Tiled PBR Material Swatches** | Blender Rendering: *Radial Tiling* (`CC0`) + three.js [webgl_materials_texture_filters](https://threejs.org/examples/#webgl_materials_texture_filters) | **Ref: `CC0`**; procedural `.lmmat` textures (`P.M2`/`4.5`) | Seeded Perlin/Worley noise, brick/checker/radial ramp baked to `albedo` + `orm` + `normal` (from height), trilinear mipmap sampling, `.lmmat` pack | `raster` | Cold bake + render ≤30 s; warm render ≤8 s | `P.M1`–`P.M3`, `4.2`, `4.5`, `4.6`, `G.3` | **Tier 1** |
| **B05** | **Tangent-Space Normal & Bump Mapped Relief** | three.js [webgl_materials_normalmap](https://threejs.org/examples/#webgl_materials_normalmap) & [webgl_materials_bumpmap](https://threejs.org/examples/#webgl_materials_bumpmap) | **Original `.lms`** + procedural height-to-normal map | Analytic tangent/bitangent basis (`TBN`), height-to-normal conversion (`4.6`), grazing-angle point light moving across a relief medallion | `raster` | ≤8 s | `4.2`, `4.6`, **`G.3` (CPU normal map)** | **Tier 1** |
| **B06** | **Original glTF Helmet Analogue with Studio IBL** | three.js [webgl_loader_gltf](https://threejs.org/examples/#webgl_loader_gltf) (`DamagedHelmet.glb` + Royal Esplanade HDR) | Reference three.js model README: **CC-BY-NC** -> **do not ship**. Original mesh/textures; generated studio environment or separately approved HDRI | `.glb` mesh/material loader (`5.3`), `albedo` + `orm` + `normal` + `emissive` textures, equirectangular HDR environment reflection & skybox (`G.4`) | `raster` (and `cycles` parity) | ≤15 s raster / ≤120 s Cycles | `P.6`, `4.2`, `4.6`, `5.3`, `G.3`, `G.4`, **`G.13` (verified glTF profile)** | **Tier 1** |
| **B07** | **3D Extruded Bevel Typography & Logo Stage** | three.js [webgl_geometry_text](https://threejs.org/examples/#webgl_geometry_text) + Blender *Curve Bevel Profile* | **Bundled `OFL-1.1` / `Apache-2.0` fonts** (`P.2`/`P.5`) | Skia glyph outline extraction (`P.5`), winding/hole resolution (`A, B, O, 8, &`), 3D depth extrusion + bevel chamfer, metallic gold/chrome material | `raster` | Cold font/mesh + render ≤30 s; warm ≤10 s | `P.2`, `P.5`, `P.F4`, `4.1`, `4.3` | **Tier 1** |
| **B08** | **Spline Tubes & Lathe Ceramic Vessels (Opaque)** | three.js [webgl_geometry_extrude_splines](https://threejs.org/examples/#webgl_geometry_extrude_splines) + Blender *Curve Bevel Profile* | Reference asset rights unverified -> original profiles/curves; no third-party file shipped | Revolution surface (`mesh_lathe`) for vase/goblet profiles + Frenet-frame closed spline tube (`mesh_tube_spline`) for knot/coil geometry | `raster` | ≤10 s | `3.1`, **`G.2` (lathe & spline extrude)** | **Tier 1** |
| **B09** | **Procedural Terrain Heightfield & Contour Map** | three.js [webgl_geometry_terrain](https://threejs.org/examples/#webgl_geometry_terrain) + `lmvideo` `Heatmap` contours | **Original `.lms`** (seeded FBM noise heightfield) | 128×128 `mesh_heightfield` colored by elevation/slope (`G.6`), paired in a `Layout` split panel with a 2D top-down marching-squares contour `Plot` | `raster` | ≤15 s including terrain/contours | `3.1`, `3.3`, `4.5`, **`G.2`**, **`G.6` (vertex colors)** | **Tier 1** |
| **B10** | **FEM Stress Colormap & 2D Callout Dashboard** | three.js [webgl_geometry_colors_lookuptable](https://threejs.org/examples/#webgl_geometry_colors_lookuptable) + Blender *Geometric Surface Patterns* (`CC-BY`) | **Original `.lms`** (analytic cantilever/plate stress field) | Per-vertex scalar mapped through `viridis`/`coolwarm` LUT (`G.6`), wireframe overlay (`G.5`), 3D-to-2D projected callout arrows (`4.4`), 2D colorbar & FRF `Plot` | `raster` | ≤15 s | `3.3`, `4.4`, **`G.5`**, **`G.6` (mesh LUT)** | **Tier 1** |
| **B11** | **Dynamic Matrix Instancing (1,000+ Cubes/Hexes)** | three.js [webgl_instancing_dynamic](https://threejs.org/examples/#webgl_instancing_dynamic) & Blender *Gizmo Array* (`CC0`) | **Ref: `CC0`**; procedural 32×32 wave-modulated instance grid | `Scene3D.add_instances` (`G.1`) sharing 1 beveled box mesh across 1,024 per-instance transforms + per-instance color/phase modulation | `raster` | ≤15 s including instance setup | `3.1`, `3.4`, **`G.1` (instancing)** | **Tier 1** |
| **B12** | **Animated Particle Wave & Point Sprites** | three.js [webgl_points_waves](https://threejs.org/examples/#webgl_points_waves) & Blender *Particle Simulation* (`CC0`) | **Ref: `CC0`**; procedural 2,500-particle sine/vortex field | Depth-sorted circular/gaussian point sprites with distance attenuation (`G.5`) + sphere-instanced hero particles, rendered as 4 s 720p30 MP4 | `raster` | ≤1.5 s/frame; ≤240 s for 120 frames including encode | `3.4`, **`G.5` (point sprites)** | **Tier 1** |
| **B13** | **3D Render + 3D Hald CLUT & Post-Processing** | three.js [webgl_postprocessing_3dlut](https://threejs.org/examples/#webgl_postprocessing_3dlut), `dof`, `outline` | **Original `.lms`** (uses Phase 2 `Image` pipeline on Phase 3 render) | `s3d.render_image()` + depth/normal pass (`G.8`) $\rightarrow$ Phase 2 `Image.clut(hald)`, `tilt_shift`, `vignette`, and Sobel edge/outline composite in a 2×2 comparison grid | `raster+img` | ≤20 s including AOV/post passes | `2.4`, `2.5`, `2.7`, `3.3`, **`G.8` (depth/normal pass)** | **Tier 1** |
| **B14** | **Four-View CAD Engineering Quad & Uncapped Section View** | three.js [webgl_multiple_views](https://threejs.org/examples/#webgl_multiple_views) & [webgl_clipping](https://threejs.org/examples/#webgl_clipping) + `lmcad` STL | **Original `.lms`** (`lmcad` B-Rep housing exported to `.stl`) | Four Layout viewports, explicit ortho/perspective cameras, plane-clipped open cutaway and 2D dimensions. Capped sections require actual cut geometry/tessellation, not fragment discard | `cad+raster` | ≤30 s including import/four views | `3.3`, `4.4`, `5.1`, `5.2`, **`G.7` (multi-view & clip plane)** | **Tier 1** |
| **B15** | **Molecular Trajectory Video with Live 2D Plot** | `lmblender` `caffeine-molecule.lms` + `kepler-orbit.lms` + three.js [webgl_loader_pdb](https://threejs.org/examples/#webgl_loader_pdb) | **Original `.lms`** (procedural coordinates) | 120-frame 720p30 timeline (`3.4`), ball-and-stick molecule + orbital path on left, `4.4` projected atom labels, synchronized live 2D potential-energy `Plot` on right, `P.7` frame cache | `raster` | ≤1.5 s/frame; ≤240 s for 120 frames including encode | `P.7`, `3.3`, `3.4`, `4.4` | **Tier 1** |
| **B16** | **Cornell Box Global Illumination & Color Bleed** | Classic Cornell Box & `lmblender` `cornell-box.lms` | Original project-authored geometry/scripts; do not infer a CC0 grant merely from procedural generation | Diffuse red/green walls, ceiling area light (`G.10`), rotated tall/short blocks + mirror/glass spheres, multi-bounce diffuse color bleeding, OIDN denoise (`6.2`) | `cycles` | ≤90 s, 64 spp + CPU OIDN | `5.4`, `6.0`–`6.3`, **`G.10` (area lights)** | **Tier 2** |
| **B17** | **Refractive Glass Goblet, IOR & Absorption** | three.js [webgl_materials_physical_transmission](https://threejs.org/examples/#webgl_materials_physical_transmission) (spectral dispersion is not baseline acceptance) | **Original `.lms`** (`mesh_lathe` goblet + HDRI studio lighting) | Dielectric transmission (`transmission=1.0`, `ior=1.52`, `roughness=0.02`), volume absorption tint (amber/emerald glass), internal total reflection | `cycles` | ≤180 s, 96 spp + CPU OIDN | `6.2`, `6.3`, **`G.2`**, **`G.9` (transmission/volume)** | **Tier 2** |
| **B18** | **Caustic Ball Lens & Focused Photon Pattern** | three.js [webgpu_caustics](https://threejs.org/examples/#webgpu_caustics) & `lmblender` `caustic-ball-lens.lms` | **Original `.lms`** (glass sphere over checker/wood floor) | Emissive mesh illuminating a dielectric sphere and receiver; sufficient bounce/sample controls and measurable focused light. Bind selected Cycles caustic features explicitly; no obsolete branched-path API or assumption that existing analytic lamps create caustics | `cycles` | ≤600 s, initially 512–1024 spp; quality/convergence gate | `6.2`, `6.3`, **`G.9`** | **Tier 2** |
| **B19** | **Subsurface Scattering (SSS) Jade & Rim-Lit Skin** | Blender Cycles: *Monster Under The Bed* (`CC-BY`) + three.js [webgl_materials_subsurface_scattering](https://threejs.org/examples/#webgl_materials_subsurface_scattering) | **Original `.lms` sculpture** or **`CC0`** *Human Base Meshes v1.4.1* bust (`blender.org`) | Random-walk subsurface scattering (`subsurface_weight`, `subsurface_radius` RGB per-channel scatter distance), strong warm backlight showing ear/thin-edge translucency | `cycles` | ≤180 s, 96 spp + CPU OIDN | `5.3`, `6.2`, `6.3`, **`G.9` (SSS)** | **Tier 2** |
| **B20** | **Automotive Clearcoat, Metallic Flake & Anisotropy** | three.js [webgl_materials_car](https://threejs.org/examples/#webgl_materials_car) & [webgl_loader_gltf_anisotropy](https://threejs.org/examples/#webgl_loader_gltf_anisotropy) | **Original `.lms`** (curved speed-form hood/fender + brushed brake rotor) | Dual-lobe car paint (`base_color` + metallic undercoat + `clearcoat=1.0`, `clearcoat_roughness=0.03`) and anisotropic brushed aluminum (`anisotropy=0.8`) under studio softboxes | `cycles` | ≤180 s, 64 spp + CPU OIDN | `6.2`, `6.3`, **`G.9` (clearcoat & anisotropy)**, **`G.10`** | **Tier 2** |
| **B21** | **Volumetric Fog & Window God-Rays** | Blender Cycles: *Lone Monk* (`lone-monk_cycles_and_exposure-node_demo.blend`) + `god-rays-window.lms` | Reference-file licence not verified -> original chamber/medium; no Lone Monk file shipped | Homogeneous participating medium (`volume_scatter` density + Henyey-Greenstein anisotropy $g=0.6$), collimated sun beam casting crepuscular rays, exposure + Filmic/AgX tone map | `cycles` | ≤300 s, 128 spp + CPU OIDN | `6.0`, `6.2`, `6.3`, **`G.11` (volumetric fog)** | **Tier 2** |
| **B22** | **Physical Sky Atmosphere (Sun Elevation Sweep)** | Blender Cycles: *Single Scattering (Nishita) Sky Demo* (`CC-BY`) + `sunset-long-shadows.lms` | Reference art licence not verified -> original composition; engine sky-code licences audited separately | Physical hosek/nishita sky texture driven by sun elevation ($2^\circ$ golden hour vs $45^\circ$ noon), long soft shadows across terrain/monoliths | `cycles` | ≤120 s, 64 spp + CPU OIDN | `6.0`, `6.2`, `6.3` | **Tier 2** |
| **B23** | **Physical Camera Depth-of-Field (Bokeh Showcase)** | three.js [webgl_postprocessing_dof2](https://threejs.org/examples/#webgl_postprocessing_dof2) + `lmblender` `camera-dof.lms` + *Blender 2.77 Racing Car* DoF note | **Original `.lms`** (chess pieces / macro watch gears along Z axis + point-light bokeh background) | Thin-lens physical camera in Cycles (`aperture_fstop=1.4`, `focus_distance`, polygonal aperture `blades=6`), out-of-focus specular highlight bokeh | `cycles` | ≤180 s, 64 spp + CPU OIDN | `6.2`, `6.3`, **`G.10` (physical camera DoF)** | **Tier 2** |
| **B24** | **Hair & Fur Curve Strands Showcase** | Blender Hair: *Animal Fur Examples* (`CC0`, Simon Thommes) + `lmblender` `strands-showcase.lms` | **Ref: `CC0`**; procedural guide-curve + child-strand generator in `.lms` | Native Cycles curve/ribbon primitives (`ccl::Hair`), root-to-tip radius taper, melanin/roughness hair BSDF, rim lighting | `cycles` | ≤600 s, 64 spp + CPU OIDN | `6.2`, `6.3`, **`G.11` (curve/hair strands)** | **Tier 2** |
| **B25** | **Archviz Daylit Interior (Classroom / Pavilion)** | Blender Cycles: *Classroom* (`CC0`, 72 MB, Christophe Seux) & *Barcelona Pavilion* (`CC-BY`, 24 MB) | **Ref: `CC0` (*Classroom*)**; build compact archviz pavilion/studio room in `.lms` with `CC0` prop meshes | Compact original room with sunlight through windows and sky/environment illumination, indirect bounces and authored wood/concrete/plaster. Do not assume a portal-light API or full Classroom import | `cycles` | ≤600 s, 128 spp + CPU OIDN | `4.6`, `4.7`, `5.3`, `6.2`, `6.3`, **`G.9`**, **`G.10`** | **Tier 2** |
| **B26** | **Cozy Tabletop Still Life (Splash-Grade Composition)** | Blender Splash: *2.93 Still Life* (`CC-BY`, Erindale) & *3.5 Cozy Kitchen* (`CC-BY-SA`, rebuilt from scratch) | **100% Original `.lms` scene** (no `CC-BY-SA` assets used) | Combines ceramic/wood/glass/metal props (`mesh_lathe`, `mesh_extrude`, beveled boxes), warm window key light + candle emissive glow, shallow DoF, Phase 2 `Image.curves` + `vignette` | `cycles` + `img` | ≤600 s, 128 spp + CPU OIDN | `2.3`, `4.6`, `4.7`, `6.3`, **`G.2`**, **`G.9`**, **`G.10`** | **Tier 2** |
| **B27** | **CAD-to-Cycles Final Product Cutaway & Preview Twin** | `09` Item `6.5` + three.js [webgl_loader_stl](https://threejs.org/examples/#webgl_loader_stl) + Blender *Hard-Surface Product Render* | **Original `.lms`** (`lmcad` planetary gear / flanged valve $\rightarrow$ `lmvideo`) | One CAD mesh in CPU-preview/final-Cycles Layout panels with projected labels; report measured preview/final timing, not an assumed 0.25 s preview | `cad` + `raster` + `cycles` | ≤360 s including CAD/import/composition | `4.4`, `5.1`, `5.2`, `6.3`, `6.5`, **`G.9`** | **Tier 2** |
| **B28** | **Surface-Scattered Botanical Meadow (10k+ Instances)** | Blender Geometry Nodes: *Flower Scattering* (`CC0`) & *Scattering Pebbles* (`CC0`) + three.js [webgl_instancing_scatter](https://threejs.org/examples/#webgl_instancing_scatter) | **Ref: `CC0` (Blender Studio)**; procedural terrain + Poisson-disk surface scatter in `.lms` | Surface-normal-aligned Poisson scatter (`G.1`) placing 10,000 grass blades, pebbles, and flowers on a undulating terrain mesh with wind phase variation | `raster` & `cycles` | ≤30 s raster / ≤600 s Cycles; scene/instance limits recorded | `3.1`, `6.4`, **`G.1` (surface scatter & instancing)** | **Tier 3** |
| **B29** | **Procedural Fractals & Signed-Distance / CSG Boolean Sculpture** | Blender Repeat Zone Raymarch Fractal (catalogue CC0) and SDF Mixer (catalogue CC-BY); three.js [webgl_geometry_csg](https://threejs.org/examples/#webgl_geometry_csg) / [webgl_marchingcubes](https://threejs.org/examples/#webgl_marchingcubes) | **Ref: `CC0`**; procedural recursive Menger/Mandelbulb or CSG boolean lattice in `.lms` | Recursive instancing or marching-cubes / `Manifold` CSG boolean operations generating intricate self-shadowing mathematical sculpture | `cycles` (and `raster`) | ≤600 s including mesh generation | `3.1`, `6.3`, `G.1`, `G.2` (separate meshing/CSG queue) | **Tier 3** |
| **B30** | **Prescribed Fracture / Elastic Deformation Clip** | Blender Simulation: *Impact Fracture* (`CC0`), *Mesh Fracturing* (`CC0`), *Jiggly Pudding* (`CC0`) | **Ref: `CC0`**; deterministic procedural Voronoi fracture / elastic wave solver in `.lms` | 90 raster frames or 30 Cycles frames of bounded original prescribed/baked geometry states. A renderer is not a rigid/soft-body solver; actual simulation, if required, is a separate explicit task | `raster` (preview) / `cycles` (`6.4`) | ≤300 s / 90 raster frames; ≤2700 s / 30 Cycles frames | `3.4`, `6.4`, **`G.14` (deforming mesh/state path)** | **Tier 3** |
| **B31** | **Heterogeneous Smoke / Cloud Volume Plume** | Blender Simulation: *2D Puff Simulation* (`CC-BY`) + three.js [webgl_volume_perlin](https://threejs.org/examples/#webgl_volume_perlin) / [webgl_volume_cloud](https://threejs.org/examples/#webgl_volume_cloud) | **Original `.lms`** (procedural 3D Perlin/Worley density grid) | 3D density grid / procedural heterogeneous volume shader in Cycles (or ray-marched 3D noise volume) lit by internal fire emissive + external sun | `cycles` | ≤900 s, 96 spp + CPU OIDN | `6.2`, **`G.11` (3D noise / grid volume)** | **Tier 3** |
| **B32** | **Flagship Multi-Domain Scientific & 3D Video Story** | `lmgallery` Flagship + three.js [webgl_gpgpu_protoplanet](https://threejs.org/examples/#webgl_gpgpu_protoplanet) + Blender *5.1 Singularity* (`CC-BY`) | **100% Original `.lms`** | 150-frame 720p30 video combining a 3D accretion/orbital scene (`Scene3D`), Phase 2 `Image` bloom/LUT grading, 3D-to-2D projected telemetry HUD (`4.4`), and live 2D phase-space `Plot` + `VectorField` in one `Layout` | `raster+img` (with `cycles` hero still) | ≤300 s / 150 raster+post frames; ≤180 s hero still | `P.7`, `2.3`–`2.7`, `3.3`, `3.4`, `4.4`, `6.3`, **`G.1`**, **`G.5`** | **Tier 3** |

---

## 3. Tiered Scoreboard & Acceptance Criteria

### 3.1 Scoreboard Summary by Tier

| Tier | Scope & Target Count | Target IDs | Engine Path | Deliverable Gate & Wall-Time Envelope |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1 — CPU Rasterizer Core** | **15 targets** (Primitives, PBR, PCF shadows, `.lmmat` procedural textures, normal maps, glTF + HDRI IBL, 3D text extrusion, spline/lathe/heightfield, vertex colormaps, 1k instancing, particles, 3D LUT/DoF/outline post-processing, 4-view CAD clipping, animated 2D+3D video) | `B01`–`B15` | `renderer="raster"` (+ Phase 2 `Image` filters & `lmcad` STL/OBJ handoff) | Planned only after completing **Phases 2–5** + Gaps `G.1`–`G.8` and `G.13` as applicable. Timing is unmeasured: provisional 5–30 s still/bake ceilings and up to 240 s for the 120-frame clips; all listed G.* gaps must pass before claiming completion.  **Verified now: 0/15 (PLANNED).** |
| **Tier 2 — Built-in CPU Cycles** | **12 targets** (Cornell GI, glass refraction/dispersion, caustics, random-walk SSS, clearcoat/anisotropy car paint, volumetric god-rays, physical sky, thin-lens bokeh DoF, hair/fur strands, archviz interior GI, tabletop splash still-life, CAD preview-vs-Cycles twin) | `B16`–`B27` | `renderer="cycles"` (in-process permissive Cycles + Embree + OIDN, `Phase 6`) | Achievable upon completing **Phase 6 (`6.0`–`6.5`)** + Gaps `G.9`–`G.11`. Provisional 90–600 s still ceilings; samples, bounces, denoise and convergence recorded per target. Spectral dispersion is not implied by ordinary RGB glass.  **Verified now: 0/12 (PLANNED).** |
| **Tier 3 — Stretch & Complex Systems** | **5 targets** (10k+ surface-scattered botanical meadow, CSG/fractal sculpture, fracture/soft-body physics clip, heterogeneous cloud/smoke volume, flagship multi-domain 3D+2D+post video) | `B28`–`B32` | `raster` + `cycles` + procedural scatter / volume / multi-pass | Stretch targets validating high-instance scaling (`G.1`), CSG/isosurface generation (`G.2`), 3D volume density (`G.11`), and full-pipeline video caching (`P.7`).  **Verified now: 0/5 (PLANNED).** |

### 3.2 Benchmark Acceptance Contract (Web-First Showcase & No Copyrighted Renders in Repo)

`lmvideo`'s demos, examples, and benchmark gallery are **web pages under our control** (`https://lmctl.com/tools/lmvideo/showcase.html` and `https://lmctl.com/tools/lmvideo/examples/<slug>.html`), not bulky file galleries committed inside the GitHub repository. For each benchmark scene `B01`–`B32`, completion requires:
1. **Self-contained `.lms` script + manifest entry in the lean public peer** (`lmctl-ai/lmvideo`) under `examples/showcase/bench-NN-<slug>.lms` and `examples/showcase/manifest.json` (using only procedural generation or pinned `CC0` / `CC-BY-4.0` assets resolved through `P.1`/`P.6` with SHA-256 verification and `--offline` support). The manifest records `script_sha256`, expected output hashes (`image_sha256`, `poster_sha256`, or composited frame-hash digest for video), dimensions, captured stdout, required feature witnesses, and per-asset licence/hash provenance.
2. **Renders and videos produced into the website build / asset store (not bulk-committed to Git)**:
   - The public `lmctl-ai/lmvideo` repo stays lean: it tracks `examples/*.lms`, `examples/showcase/bench-NN-<slug>.lms`, `examples/manifest.json`, `examples/showcase/manifest.json`, and a short `README.md` with a few compact preview PNGs (`docs/images/*.png`, `< 30 KB`) and prominent links to `https://lmctl.com/tools/lmvideo/showcase.html` and `https://lmctl.com/tools/lmvideo/examples/`.
   - Full-resolution benchmark PNGs, side-by-side comparison renders (`B06`, `B10`, `B13`, `B27`), and `.mp4`/`.webm` video clips (`B13`–`B15`, `B26`–`B27`, `B30`–`B32`) are produced into the website build (`build/tools-media/lmvideo/`) and published to the website's content-addressed media store (`https://lmctl.com/tools/lmvideo/media/<slug>-<sha256>.{png,mp4,webm}`), verified against the expected hashes in the public repo's manifest.
3. **Rich Showcase & Example Web Pages on `lmctl.com/tools/lmvideo/`** generated by executable `lmhtml` programs (`scripts/tools/showcase-page.lms` and `scripts/tools/example-page.lms`) containing:
   - Our rendered still (`<img>`), side-by-side comparison `<figure>` (e.g., CPU `raster` vs `cycles` path-traced render, or wireframe/depth AOV vs final composite), or embedded `<video controls loop muted playsinline preload="metadata" poster="...">` (`<source type="video/mp4">` + `<source type="video/webm">`),
   - A structured technical description of the reference scene, its clickable upstream URL (`blender.org` or `threejs.org`), the visual phenomenon and feature witnesses verified, and measured CPU render time / peak RSS,
   - Per-example copyable "run it" command (`<pre><kbd>lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmvideo/<commit>/examples/showcase/bench-NN-<slug>.lms</kbd>\n<samp>...</samp></pre>`) hydrated with copy buttons by `/tools/lmctl-copy.js`, plus the escaped `.lms` script source and Tier 1–3 scoreboard table.
   - **Zero copied third-party reference JPEGs/PNGs** in the Git tree or website asset store. The comparison is our rendered media beside a reference description/link. Licence evidence is required for every input, even if a target otherwise renders correctly.
4. **Quantitative Regression Gate**:
   - Same pinned environment: record repeat hashes for both CPU paths; use explicitly justified numerical/image tolerances where the implementation is nondeterministic. Across ISA/denoiser builds use documented tolerances, not a universal byte claim; no SSIM comparison to an unlicensed copied render.
   - `raster` vs `cycles` handoff scenes (`B06`, `B27`) compare camera/projection, silhouette/depth and decoded material/channel values independently. A predeclared matte ROI may use SSIM ≥0.85 only with matched illumination/exposure and documented GI/specular differences; low whole-image similarity alone cannot diagnose a broken importer.

### 3.3 Lean public peer, private code repo, and `lmctl.com/tools/lmvideo/` web pipeline

The public peer (`lmctl-ai/lmvideo`) **owns the benchmark `.lms` sources, manifests, and expected-output hashes** while staying lean. The private peer (`lmctlhq/lmvideo`) owns implementation and source-coupled tests. The website (`lmctl-website` $\rightarrow$ `https://lmctl.com/tools/lmvideo/...`) owns the rich rendered demo pages, embedded videos, side-by-side comparisons, and interactive copyable scoreboard.

| Location | Authoritative tracked content | Not its responsibility |
|---|---|---|
| **Public `lmctl-ai/lmvideo`**, local `~/repos/dsl/lmvideo-public` | Short `README.md` with 3–6 compact preview PNGs (`< 30 KB`) and links to `https://lmctl.com/tools/lmvideo/showcase.html` and `/tools/lmvideo/examples/`; `examples/*.lms` and `examples/showcase/bench-NN-<slug>.lms`; `examples/manifest.json` and `examples/showcase/manifest.json` (expected output SHA-256s, stdout, feature witnesses, per-asset hashes/licences, measured scoreboard metadata); binary releases, notices and full licence texts | No bulk high-res PNGs or `.mp4`/`.webm` video files committed to Git; no proprietary renderer C++ source, build-only private fixtures, or copied third-party reference renders. `LICENSE-examples` (MIT) covers authored `.lms` scripts/docs. |
| **Private `lmctlhq/lmvideo`**, local `~/repos/lmctlhq/lmvideo` | `cpp/`, `schema/`, Makefile/build tooling, dependency pins, renderer/asset code, CI and release publisher; `tests/` source-coupled unit/failure/diagnostic tests and small synthetic fixtures/goldens requiring internal APIs; internal engineering notes | No second authoritative showcase `.lms` tree. Reads a pinned `lmctl-ai/lmvideo` checkout in mono/release verification to test the public `.lms` scripts with its freshly built candidate binary. |
| **Website `lmctl-website`**, published at `https://lmctl.com/tools/lmvideo/...` | `scripts/tools/pull-tools.py`, `scripts/tools/example-page.lms`, and `scripts/tools/showcase-page.lms` (`lmhtml` templates as code); `tools/lmvideo/showcase.html`, `tools/lmvideo/examples/*.html`, and `source-lock.json`; S3/CloudFront media store (`tools/lmvideo/media/<slug>-<sha256>.{png,mp4,webm}`) holding the rendered showcase images and videos | Does not hand-edit generated `.lms` examples or execute untrusted code during HTML lint/check; fetches pinned commits from `lmctl-ai/lmvideo` and verifies every render/video hash against the manifest before building pages. |

Public manifest/scoreboard records (`examples/showcase/manifest.json`) include scene ID/slug/status, required feature witnesses, allowed asset hashes/licences, expected output hashes (`image_sha256`, `poster_sha256`, `frame_hashes_sha256`, `mp4_sha256`, `webm_sha256`), CPU/build/ISA/thread/sample/denoise profile, phase timings/RSS, binary tag/hash/schema, and the tested public content SHA.

#### Book catalogue and representative README pictures

**README policy:** lmvideo's README is a short storefront with at most six representative pictures and links to the website books; this supersedes the earlier “README is the demo page” rule. The full collection lives under `/tools/lmvideo/` as structured multi-page volumes, with heavy renders/videos in the website asset store.

The planned content manifest has ordered `groups` (books), each with stable ID/title/summary, ordered chapters and ordered text/code/image/video blocks. Pinned executable lmhtml `book-index.lms` and `book-chapter.lms` templates render a per-book contents/index plus chapter pages, previous/next/contents navigation, and a tool-level list of available books. End chapters omit unavailable neighbours; navigation never jumps silently into another book. Group/chapter/block array order is authoritative. Example scripts/media can be referenced across authored chapters without source duplication.

Every tool gets an **Examples book** generated from its public `examples/` inventory at `/tools/<tool>/examples/`; optional authored **Getting started**, **Guide** and **Reference** books publish only when their chapter content exists. For lmvideo, the additional **Showcase book** at `/tools/lmvideo/showcase/` groups B01–B32 by tier/technique and includes the measured scoreboard, explanations, code/run transcripts, own pictures and captioned videos. Individual scene detail pages remain linkable. The previously proposed `/tools/lmvideo/showcase.html` becomes an optional landing/compatibility link to this volume rather than a single-page replacement for chapters. Preserve existing example URLs during migration and extend nested-book discovery/contract checks before publishing new paths.

Representative pictures are selected by an explicit `featured: true` on a chapter/example entry, with a verified compact `featured_image`, alt/caption and canonical chapter link. Default is false. Select in manifest group/chapter order, deduplicate picture digests, and reject more than six selections rather than dropping them silently. No featured entries means text book links, not an automatically filled gallery. README generation touches only its marked picture region, preserving installation/licence text. Non-featured entries remain in the full books. Choose distinct verified capabilities, not six near-identical renders or pictures of PLANNED scenes. Use one/two-column layouts and mobile/light/dark checks informed by website `durable-memory/tool-book-feedback`; bulk media remains untracked in the public product repository.

The book catalogue, featured flag and mixed-media templates are design work only. The existing three-PNG pilot and legacy example books are not migrated by this amendment. Acceptance must check two books with multiple chapters, per-book navigation boundaries, stable old links, zero/six featured selections, rejection of seven and the continued presence of all non-featured chapters.

#### Implementation status and media ownership

This section specifies the next website build, not features already shipped by w80. The current pilot at website commit `5039fa8` imports three tracked compact PNGs with manifest version 1 and renders plain example pages using `example-page.lms` pinned to lmhtml **v0.7.4**. It does not yet fetch an external media store, understand the showcase manifest, generate `showcase-page.lms`, allow video, upload media or render scenes. The planned render-harness command names below are interface sketches, not runnable commands today. Do not bulk-delete existing gallery media or rewrite public history as part of this docs amendment; migrate current references once verified web assets/pages exist.

The website asset store owns heavy media separately from the HTML deployment manifest. Its uploader is a separately invoked, scoped owner/mono operation, with long-lived read-only public URLs; no bucket credentials are needed by the page builder. The HTML publisher must never enumerate-and-delete the separately owned media prefix. Removing a page removes its HTML references, not its media objects: a distinct retention/garbage-collection pass may remove only blobs unreferenced by all retained page/release locks. Upload verified objects first, stage/check pages offline against a complete local media index, then promote pages. If a fetch or gate fails, keep the previous pages and media references intact.

#### Books and the README storefront (owner rule)

- **README policy:** `lmctl-ai/lmvideo/README.md` is the storefront, not the catalogue. It holds at most 6 representative compact pictures, chosen by `featured: true` in the content manifest (each a tracked `docs/images/*.png` < 30 KB), and links into the books. This supersedes the earlier "README is the demo page" rule for lmvideo.
- **Books:** the full material is published as books under `https://lmctl.com/tools/lmvideo/`. Each book is ordered chapters with one page per chapter, a per-book index, and prev/next/contents navigation, all generated by pinned lmhtml template programs (`book-index.lms`, `book-chapter.lms`). The model and layout are defined in the website's `durable-memory/tools-from-examples.md` ("Books per tool and the README storefront").
- **lmvideo's books:**
  - `examples/`, generated from `examples/manifest.json` groups;
  - `showcase/`, the B01–B32 benchmark as chapters per tier, with the scoreboard on its index page, under the scoped showcase allow-list;
  - optional authored `getting-started/` and `reference/` books.

  `showcase.html` in §3.2/§3.3 thereby becomes `showcase/index.html`, and the scene pages become chapters of that book.

#### Template as code (`lmhtml`) and the `showcase` role contract extension

Because we control `lmctl.com/tools/lmvideo/...`, the showcase and example pages can be richer than the plain prose `/tools/` pages while keeping `skill.html` (consumed by LLM agents via `lmhtml clean`) strictly minimal. Rather than weakening the `/tools/` contract globally, `lmctl-website` defines page templates as executable `lmhtml` programs and extends `scripts/tools/roles.lms` + `scripts/tools/check.lms` with an **explicit allow-list for the `showcase` role and importer-generated `examples/` pages**:

1. **Templates as `lmhtml` code (`scripts/tools/example-page.lms` and `scripts/tools/showcase-page.lms`)**:
   - The existing example generator pins lmhtml v0.7.4; the proposed showcase generator must also pin its reviewed release. Both are executable `_lmcode_ cli="lmhtml"` programs to be invoked by `scripts/tools/pull-tools.py` after the manifest-v2 extension. Python handles Git blob fetching, SHA-256 verification, and atomic directory staging; `lmhtml` owns all DOM construction (`html.parse`, `Doc.select`, `Node.replace_with`, `Node.insert_before`, `Node.remove`, `html.save`) with compile-time string escaping (`&`, `<`, `>`, `"`).
   - `example-page.lms` builds `tools/lmvideo/examples/<slug>.html` and `tools/lmvideo/examples/index.html` (with `<!-- generated: tools-from-examples -->`), emitting the `<h1>` title, task description, `<h2>Run this example</h2>` with `<pre><kbd>lmctl autorun https://raw.githubusercontent.com/lmctl-ai/lmvideo/<commit>/examples/...</kbd>\n<samp>...</samp></pre>`, media `<figure>` (still `<img>`, side-by-side comparison `<img>` pair, or `<video>`), pinned raw `.lms` link, and full escaped `<pre><code>...</code></pre>` script.
   - `showcase-page.lms` builds `tools/lmvideo/showcase.html` (and optional topic pages `showcase-raster.html`, `showcase-cycles.html` with `<!-- generated: tools-showcase -->`), emitting the Tier 1–3 scoreboard summary `<table>`, per-tier scene cards (`B01`–`B32`) with embedded `<video>` or side-by-side `<figure>` renders, reference scene attribution link, measured CPU time/RSS badge text, copyable `lmctl autorun` command, and link to the per-scene detail page.
2. **Coexistence with the plain-tag `/tools/` contract (`roles.lms`, `decorate.lms`, `check.lms`)**:
   - `scripts/tools/roles.lms` adds `showcase=Showcase` (`role_table = "skill=Skill|showcase=Showcase|tutorial=Tutorial|guide=Guide|recipes=Recipes|reference=Reference|faq=FAQ|changelog=Changelog|"`).
   - `skill.html` and standard prose roles (`tutorial`, `guide`, `recipes`, `reference`, `faq`, `changelog`) remain governed by the strict plain-tag contract (no `<video>` or authored `class`/`data-*`, and the existing `< 30 KB` PNG cap; the current checker already has one exact optional head copy-script exception).
   - Only when `page_role(file) == "showcase"` or a nested example page is explicitly classified as showcase by the validated local manifest/lock (never by an arbitrary HTML comment alone), `check.lms` enables the **scoped showcase/examples allow-list**:
     - **Copy buttons via `lmctl-copy.js`**: allows at most one `<script src="/tools/lmctl-copy.js" defer></script>` in `<head>` with empty body, injected by `decorate.lms` when the page contains a command in `<pre><kbd>`. Hydrates `<pre><kbd>...</kbd></pre>` (copying only the command, excluding `<samp>`) without source classes or data attributes; any later whole-script copy control requires a separately reviewed semantic marker.
     - **Embedded video**: allows `<video>` inside `<figure>` with attributes `controls`, `loop`, `muted`, `playsinline`, `preload="metadata"`, `poster`, `width`, `height`, containing 1–2 `<source>` elements (`src`, `type="video/mp4"` or `type="video/webm"`) and fallback text.
     - **Side-by-side comparison figures**: allows `<figure>` on `showcase` and `examples/` pages to contain either 1 `<img>`, 2 `<img>` elements (side-by-side comparison, e.g. `raster` vs `cycles` or wireframe vs shaded, styled via `figure > img + img` in `/tools/style.css` without `<div>` wrappers), or 1 `<video>`, plus exactly 1 `<figcaption>`.
     - **Scoped media paths & byte budgets**: allows media `src` / `poster` under `/tools/<tool>/examples/img/` (for compact `< 30 KB` thumbnails) and `/tools/<tool>/media/` (for full-resolution showcase PNGs up to `512,000` bytes and `.mp4`/`.webm` clips up to `5,242,880` bytes whose SHA-256 digests are locked in `source-lock.json` / `showcase-lock.json`).

#### Where renders are generated, where they are stored, how the page build fetches them, and cache/determinism

1. **Where renders are generated (`mono` / Actions / local staging)**:
   - **Never during website HTML lint/check**: `lmctl-website`'s `check:tools` and `decorate:tools` never execute `.lms` scene scripts or run Cycles.
   - **Fast 2D & Tier 1 raster examples (per-target provisional budgets in §2)**: generated in `mono.lmctl` (`lmctl-mono-test`) or local operator staging (`scripts/showcase/render-benchmark.py --tier 1`) using the pinned release binary (`lmvideo` + `lmscript`).
   - **Heavy 3D raster videos & Tier 2/3 Cycles scenes (`B13`–`B32`, `30–600 s` CPU)**: generated on `mono.lmctl` CPU batch workers or manual `workflow_dispatch` benchmark jobs in `lmctlhq/lmvideo` (checking out `lmctl-ai/lmvideo` at the exact target commit SHA), or locally via `scripts/showcase/render-benchmark.py --scene B17 --publish-media`.
2. **Where renders are stored**:
   - The render harness writes outputs into a local content-addressed staging directory (`build/tools-media/lmvideo/<slug>-<sha256>.{png,mp4,webm}`) and uploads verified blobs to the website S3 bucket under the `tools/lmvideo/media/` prefix (`s3://lmctl-website-prod/tools/lmvideo/media/<slug>-<sha256>.{png,mp4,webm}`, served at `https://lmctl.com/tools/lmvideo/media/...` with long-lived `Cache-Control: public, max-age=31536000, immutable` because the filename embeds the full content hash).
   - Compact `< 30 KB` thumbnails used by the 3–6 hero images in `lmctl-ai/lmvideo/README.md` may remain in `lmctl-ai/lmvideo/docs/images/` and `/tools/lmvideo/examples/img/`, while all 32 full-resolution benchmark PNGs, side-by-side pairs, and `.mp4`/`.webm` clips live in `tools/lmvideo/media/` (or S3) rather than bloating Git clones.
3. **How the website page build fetches and verifies them**:
   - `npm run pull:tools -- lmvideo --ref <40-char-sha>` (in `lmctl-website`) shallow-fetches the pinned commit from `https://github.com/lmctl-ai/lmvideo`, reads `examples/manifest.json` and `examples/showcase/manifest.json`, and verifies every `.lms` file's `script_sha256`.
   - For each example/showcase entry, `pull-tools.py` resolves the rendered media in priority order: (a) tracked blob in the public commit if `< 30 KB` (`docs/images/<slug>.png`), (b) local media staging cache (`build/tools-media/lmvideo/<slug>-<sha256>.<ext>`), or (c) HTTPS fetch from `https://lmctl.com/tools/lmvideo/media/<slug>-<sha256>.<ext>`.
   - `pull-tools.py` computes the SHA-256 of every fetched PNG/MP4/WebM (and verifies PNG header/dimensions or video container metadata) against the expected `image_sha256` / `mp4_sha256` / `webm_sha256` in `manifest.json`. Any missing blob or hash mismatch is a hard error that aborts staging before `example-page.lms` or `showcase-page.lms` runs.
   - `pull-tools.py` writes `tools/lmvideo/examples/source-lock.json` (recording the public repo commit SHA, `manifest_sha256`, `template_sha256`, and every input/media SHA-256), and the build driver must subsequently run `decorate:tools` and `check:tools`; the current pull command does not run those gates automatically.
4. **Cache and determinism rules**:
   - **Render cache key**: SHA-256 of a canonical record containing binary and compiler hashes, script/input-asset hashes, architecture/ISA, thread/seed/sample/denoise settings, fonts, codec binaries and canonical render preset stored under `build/showcase-cache/lmvideo/`. Re-running the render harness when the cache key matches skips re-rendering unless `--check` (force re-render + hash/SSIM verification) is passed.
   - **Still & frame determinism**: Require repeat-run hashes in the same pinned binary/ISA/thread/font/codec environment before marking a CPU rasterizer scene deterministic; no specific fixed-point or tile-reduction implementation is assumed. Cycles scenes use a fixed Sobol RNG seed, fixed sample/bounce counts, and pinned OIDN weights; repeat runs on the same machine/binary must match frame hashes (or stay within documented denoiser tolerance across `x86_64` vs `aarch64`).
   - **Video container determinism**: As in `homepage-videos.md`, reproducibility is gated on the **composited PNG frame sequence hashes** (`frame_hashes_sha256`) plus `ffprobe` codec/dimensions/duration/frame-count checks, while the final `.mp4` (H.264 `yuv420p`) and `.webm` (VP9) files uploaded to `tools/lmvideo/media/` are pinned by their exact published file SHA-256 in `manifest.json`.
   - **HTML build determinism acceptance**: Given the same `lmctl-ai/lmvideo` commit SHA, verified media blobs, and pinned `lmscript`/`lmhtml` binaries, running `pull:tools` + `decorate:tools` is a pure function that produces byte-identical HTML and `source-lock.json` with zero network dependence during `check:tools`.

#### What publish_tree.py actually does

Source selection and staging are separate from publication:

1. The historical split/staging path in
   [`peer-flip.py`](../scripts/closed-source/peer-flip.py) selects the reviewed tracked
   README/docs/examples and necessary inputs into a public tree, excludes private
   source/build/tests/engineering notes, and maps licence directories to public
   `docs/third-party-licenses/`. Its product staging plan is
   [closed-source-plans/lmvideo.md](closed-source-plans/lmvideo.md). This is initial
   boundary/bootstrap tooling, **not** an instruction to repeat a flip or rewrite
   public history for each new demo.
2. [`publish_tree.py`](../scripts/closed-source/publish_tree.py) **post-processes an
   existing staged tree**. It does not author showcase scripts, copy an arbitrary
   private examples tree by itself, render images, commit, push, deploy the website
   or upload releases. Its actual arguments are `STAGE SOURCE_REPO PRODUCT` plus
   optional `--notices`, `--boundary [--latest-tag ...]`, and `--private-ci OUT`.
3. `--notices` copies root `THIRD_PARTY_NOTICES*` byte-for-byte from source and
   rejects listed placeholder strings. Full licence directories/source/relink
   bundles, when applicable, are staged by the explicit product/release recipes;
   copying that root notice alone is not a complete compliance package.
4. `--private-ci OUT` writes a workflow file; it does not run CI or publish. The
   current generator renders a dispatch-only **Linux x64/arm64** prerelease workflow,
   not five automatic platform builds. Build recipes and notice staging are distinct
   from `scripts/release-to-public.sh` uploading the approved binary artifacts.
5. `--boundary` is historical licence-boundary tooling: it queries public latest
   unless given an explicit tag and its current implementation still writes the old
   Personal Use wording. **Do not run it to refresh demos or advance a historical
   cutoff.** Use the existing reviewed binary licence and preserved release-era
   statement; changing the helper/terms is a separate task. No boundary/flip/publish
   command is executed by this benchmark plan.

Illustrative staged-notice refresh only (not a command executed here):

```sh
python3 scripts/closed-source/publish_tree.py   /path/to/reviewed-public-stage /home/mma/repos/lmctlhq/lmvideo lmvideo --notices
```

A reviewed staged content change reaches the public peer through a normal public
branch/commit. For an already split product, new demos are instead authored
**directly in the public checkout**; do not regenerate or overwrite its README,
examples or images from a stale private copy.

#### Ongoing script/render/scoreboard flow

1. Author the `.lms`, visual specification, allowed-asset manifest and proposed
   manifest/scoreboard entry on a public branch (`lmctl-ai/lmvideo`). The benchmark is
   PLANNED until executed; no reference image is copied into the repo. Keep future-API
   examples off public main until a matching installable release exists.
2. Private source verification (`mono` / manual dispatch / local staging) checks out
   that **exact public branch commit SHA** beside the source commit, builds the
   candidate and puts that executable first on PATH. Run the public scripts from an
   empty directory and collect output, feature witnesses, licence validation,
   timings/RSS and CPU repeat checks. Never substitute a different private showcase
   script for the actual public one.
3. Publish verified full-resolution renders and `.mp4`/`.webm` clips into the website
   media store (`build/tools-media/lmvideo/` $\rightarrow$ `s3://lmctl-website-prod/tools/lmvideo/media/`)
   and commit only the `.lms` script, expected output hashes, and verified scoreboard
   metadata in `examples/showcase/manifest.json` on the public branch (keeping
   `lmctl-ai/lmvideo` lean). Source-coupled synthetic engine fixtures stay in private tests.
4. Stage/publish a matching versioned binary and complete notices through the product
   release path. Test fresh-cache install and pin the candidate tag in new demos
   before merging/promoting, avoiding a window where public main requires an API
   absent from latest. Keep old versioned examples/releases usable.
5. Explicitly triggered public checks validate links, manifest hashes, licence manifests,
   real raw URLs, source checking and selected executions against the pinned released
   binary; then `npm run pull:tools -- lmvideo --ref <full-sha>` in `lmctl-website`
   renders `/tools/lmvideo/showcase.html` and `/tools/lmvideo/examples/*.html` via
   `showcase-page.lms` and `example-page.lms`, followed by `decorate:tools` and `check:tools`.

The result is a clean three-way separation: **private code/tests/build/CI (`lmctlhq/lmvideo`);
lean public `.lms` examples, manifests, expected hashes, short README, and releases
(`lmctl-ai/lmvideo`); rich rendered showcase and example web pages (`lmctl.com/tools/lmvideo/...`)**.

---

## 4. Gap List Feeding `09-lmvideo-backlog.md` as New Backlog Items (`G.1`–`G.15`)

Mapping the 32 benchmark scenes against [09-lmvideo-backlog.md](09-lmvideo-backlog.md) identifies **15 capability/harness queues** that are not yet itemized in `09`. Each item below is an ordered capability queue to split into independently testable changes to Phases 2–6:

| Gap ID | Target Phase in `09` | Missing Capability Revealed by Benchmark | Proposed Small Backlog Item & API | Unlocks Benchmark Scenes |
| :---: | :---: | :--- | :--- | :--- |
| **`G.1`** | **Phase 3** (`3.5`) | Creating 1,000–10,000 separate `Node3D` handles for arrays or foliage (`webgl_instancing_*`, Blender *Flower/Pebble Scattering*) bloats scene memory and `.glb` export. | **First-class mesh instancing & deterministic surface scatter**: `Scene3D.add_instances(mesh, mat)` returning `InstancedNode3D` (`add_instance(tx,ty,tz, rx,ry,rz, sx,sy,sz, color_hex)`, `scatter_on_mesh(surface_mesh, count, seed, align_normal, min_dist)`). Exports via `EXT_mesh_gpu_instancing` / shared `ccl::Mesh` instances in Cycles. | `B11`, `B28`, `B29`, `B32` |
| **`G.2`** | **Phase 3** (`3.6`) | `09` `3.1` only lists basic primitives (`box`, `sphere`, `cylinder`, `cone`, `plane`, `torus`), missing spline tubes, lathe vessels, heightfields, and 2D polygon extrusion (`B08`, `B09`, `B17`, `B26`). | **Separate parametric/meshing tasks** (lathe, polygon extrusion/holes, spline tube, heightfield; optional CSG/isosurface generation is additional work): `mesh_lathe(profile_xy_csv, segs)`, `mesh_extrude(polygon_xy_csv, depth, bevel)`, `mesh_tube_spline(points_xyz_csv, radius, segs, closed)`, and `mesh_heightfield(sampled_image_or_grid, w, d, y_scale)` (choose concrete schema types; no assumed first-class DSL callback) (porting audited C++17 builders from `lmblender` `loft-outline.lms` and `lmfilament` `heightfield.lms`). | `B08`, `B09`, `B17`, `B26`, `B29` |
| **`G.3`** | **Phase 4** (`4.8`) | `09` `4.6` bakes tangent-space normal maps into `.lmmat`, but the CPU rasterizer (`4.1`/`4.2`) currently lacks vertex tangent generation and TBN fragment perturbation. | **Tangent-space normal mapping in CPU rasterizer**: compute MikkTSpace / UV-gradient tangent + bitangent + handedness `(tx, ty, tz, tw)` on `Mesh3D` and perturb shading normal `N` from `.lmmat` `normal` texture in the CPU fragment shader. | `B04`, `B05`, `B06` |
| **`G.4`** | **Phase 4** (`4.9`) | Metallic and clearcoat objects (`B01`, `B06`) look dark/flat in the CPU rasterizer under punctual lights alone without environment reflection. | **Equirectangular HDR/LDR environment map (IBL) in CPU rasterizer**: `Scene3D.set_environment(env_image, intensity, rotation_deg)` sampling prefiltered roughness mip levels along reflection vector `R` and diffuse irradiance along `N`, plus optional skybox background. | `B01`, `B06`, `B14` |
| **`G.5`** | **Phase 4** (`4.10`) | Particle waves (`B12`) and FEM wireframe overlays (`B10`) need screen-space point sprites and thick/wireframe line rendering in the CPU rasterizer. | **Point-cloud sprites & wireframe/line pass**: `Scene3D.add_points(xyz_color_radius_buffer, mat)` rendering depth-tested anti-aliased circular/gaussian sprites, plus `Material3D.set_wireframe_overlay(color_hex, width_px)` for mesh edge visualization. | `B10`, `B12`, `B32` |
| **`G.6`** | **Phase 4** (`4.11`) | Scientific meshes (`B09`, `B10`) and vertex-painted assets need per-vertex `COLOR_0` attributes and scalar-to-colormap lookup (`viridis`, `inferno`, `coolwarm`). | **Mesh vertex colors & scalar LUT mapper**: `Mesh3D.set_vertex_scalars(values, colormap_name, min_val, max_val)` populating `COLOR_0` and multiplying `COLOR_0` with `base_color` in both the CPU rasterizer and Cycles `Attribute` node. | `B09`, `B10` |
| **`G.7`** | **Phase 3** (`3.7`) | `B14` ([webgl_multiple_views](https://threejs.org/examples/#webgl_multiple_views) + [webgl_clipping](https://threejs.org/examples/#webgl_clipping)) needs 4 orthographic/perspective views of the *same* `Scene3D` and a cross-section cut plane without cloning the scene 4 times. | **Per-viewport camera and uncapped plane clipping**: `Canvas.scene3d_camera(scene, cam, x, y, w, h)` and `Scene3D.set_clip_plane(nx, ny, nz, d)` discarding fragments with $\mathbf{n}\cdot\mathbf{p} + d < 0$ in CPU raster; Cycles requires a separately validated geometric/visibility solution. A cap is new geometry requiring intersection contours and tessellation, not a `cap_color` argument on fragment discard. | `B14`, `B27` |
| **`G.8`** | **Phase 3 / 2** (`3.8`) | `B13` ([webgl_postprocessing_dof](https://threejs.org/examples/#webgl_postprocessing_dof), `outline`, `ssao`) needs depth and normal buffers from the CPU 3D rasterizer so Phase 2 `Image` filters can run depth-aware DoF blur and Sobel edge outlines. | **CPU raster AOV pass getters**: `s3d.render_depth_image(w, h, near_z, far_z) -> Image` and `s3d.render_normal_image(w, h) -> Image`, feeding directly into Phase 2 `Image` composite/blur/edge pipelines. | `B13`, `B32` |
| **`G.9`** | **Phase 4 / 6** (`6.6`) | `09` `4.1`/`4.7` only specify `base_color`, `metallic`, `roughness`, `normal`, `occlusion`, `emissive`. Tier 2 Cycles targets (`B17`–`B20`, `B25`, `B26`) require dielectric transmission, IOR, volume absorption, subsurface scattering, clearcoat, and anisotropy. | **Principled BSDF extension profile in `Material` & `.lmmat`/GLB**: add `set_transmission(w, ior)`, `set_volume_absorption(hex, density)`, `set_subsurface(w, rx, ry, rz)`, `set_clearcoat(w, rough)`, and `set_anisotropy(w, rot)` mapped to `KHR_materials_transmission`/`ior`/`volume`/`clearcoat`/`anisotropy` + Cycles `PrincipledBsdfNode`. | `B17`, `B18`, `B19`, `B20`, `B25`, `B26` |
| **`G.10`** | **Phase 5 / 6** (`6.7`) | `KHR_lights_punctual` only supports point/directional/spot lights (no rectangular/disk area lights for `B16`/`B20`/`B25`), and core glTF cameras lack physical aperture/focus distance (`B23`, `B26`). | **Area lights & physical camera DoF in `Scene3D` and `job.json` sidecar**: `Scene3D.add_area_light(w, h, color_hex, intensity)` and `Camera3D.set_dof(fstop, focus_dist, blades)` serialized in the Phase 5.4 `job.json` sidecar and mapped to `ccl::Light` (`LIGHT_AREA`) and `ccl::Camera` (`aperturesize`, `focaldistance`, `blades`). | `B16`, `B20`, `B23`, `B25`, `B26` |
| **`G.11`** | **Phase 6** (`6.8`) | `B21` (*Lone Monk* / god-rays), `B24` (*Animal Fur*), and `B31` (*Smoke Plume*) require curve/hair strands and homogeneous/procedural 3D volume media in the Cycles bridge (`09` `6.2` notes they need an explicit extension profile). | **Three separate Cycles extension tasks:** homogeneous medium (B21), native curve/hair geometry (B24), then heterogeneous density fields (B31): `Scene3D.add_hair_curves(roots_points_radii, mat)` $\rightarrow$ `ccl::Hair`, and `Scene3D.set_volume_fog(density, anisotropy_g, color_hex)` (plus 3D noise volume density) in `job.json` $\rightarrow$ the verified Cycles world/object volume shader and optional density-grid adapter. | `B21`, `B24`, `B31` |
| **`G.12`** | **Phase P** (`P.8`) | A curated mesh/environment pack needs per-file redistribution evidence, not inherited library licences | **Original or proven-permitted benchmark assets:** original helmet/knob/pawn/room meshes and generated studio panorama by default; optional verified Human Base Meshes/other CC0 or CC-BY-4.0 imports only after exact archive, author, licence-version and hash checks. **No assumed CC-BY-4.0 DamagedHelmet, no unproven CC0 Suzanne/teapot or invented HDRI grants.** Assets are proposed, not already hosted. | `B06`, `B19`, `B25`, `B27` |

| **`G.13`** | **Phase 5** (`5.5`) | Real GLB assets use embedded images and material/instancing extensions absent from the current importer | **Explicit glTF capability profile:** embedded bufferView/data-URI PNG/JPEG, core attributes, required-extension checks and declared instancing/material subsets; compressed formats only with separately audited codecs. Skinning/morph are not accepted silently as static geometry. | `B06`, `B19`, `B25`, `B28` |
| **`G.14`** | **Phase 3 / 6** (`3.9`) | B30 changes topology/vertex states; Transform keyframes alone do not simulate or deform a mesh | **CPU mesh-state/deformation input:** bounded authored/baked frame states, updated bounds/normals and per-frame geometry identity. Skin/morph evaluation, if later required, is its own tested profile. Prescribed motion does not claim a Blender physics/Geometry Nodes runtime. | `B30`; future rigged-model targets |
| **`G.15`** | **Phase 0** (`0.4`) | A visual name, fast cached frame or successful legacy-wrapper run cannot establish benchmark completion | **Benchmark manifest/harness:** pinned reference description, asset licences/hashes, required feature witnesses, CPU profile, cold/warm phase timings/RSS, repeat images and explicit PLANNED/PASS/BLOCKED results. Full slow clips are manual/owner-triggered; no GPU work scheduled. | all `B01`–`B32` |

## 5. Feasibility review against actual code (ResearchSol)

Reviewed the catalogues and current code, not just schemas or library marketing:
lmvideo source `4819dce669303546b14d67b0a6b64fb3cb2f58a9`, lmblender
`235ad015789c9b2ec94a52e05e02388cee243c8b`, lmfilament
`d592639922ed6c3fbdaab919420b419d18de322f`, lmmagnum
`aeeefcc9234b951cfeb8f0cd76e576e4704723ff` (moving branches; these are review
snapshots, not approved engine pins). lmvideo's 2D/typeface/Image work is advancing,
but its checked schema still has no Scene3D/scene3d constructor. Do not count an
old lmblender render as a passing built-in lmvideo Cycles benchmark.

- Current Filament backend is noop. `cpp/preview.cpp` samples albedo with CPU
  lighting/shadowing; uploading normal/metallic/roughness/AO maps does not implement
  shading from them. G.3/G.4 and the full portable-material path need new code/tests.
- `lmblender/cpp/gltf_import.hpp:206–218` rejects embedded texture images; it also
  rejects morph targets and unsupported material extensions (currently only the
  emissive-strength extension is accepted there). Its imported node transforms are
  baked; generic skinning/animation is not established. G.13 cannot be skipped.
- Native hair curves are not today's swept triangle-mesh hair helpers. Homogeneous
  volume support is not a heterogeneous smoke simulator. GPU particle demos become
  bounded CPU-authored particle states; no GPU backend or general simulation engine
  is scheduled by this benchmark.
- The existing wrapper documents that analytic lamps do not currently create its
  mirror/glass/caustic appearance; use an emissive mesh fixture or add/validate the
  correct Cycles light visibility/MIS/caustic bindings. A labelled bright spot or
  alpha-blended surface is not proof of refractive caustics or glass.
- Guardrails are not performance promises: current wrapper glTF caps include 10M
  accessor elements, 4096 meshes/materials, 64 MiB image files and a 64-megapixel
  decoded texture guard; global geometry caps are 10M vertices / 20M triangles.
  Benchmark scene/instance limits must be explicit and lower where appropriate;
  10k logical instances cannot simply inherit a 4096-object import path.
- The current CPU throughput note measured a simple 1280×720, 16-spp fast-denoise
  scene around 2 s/frame on its four-thread ARM host, with scene-dependent results.
  A previous 6.31 s OIDN measurement did not reproduce (controlled ~0.91 s rerun).
  None of this establishes 2.5–12 s at 64–128 spp for every glass/hair/interior scene,
  nor 0.08 s/frame for all 720p raster videos. Budgets above are revised provisional
  ceilings, to be baselined and quality-gated rather than presented as measurements.

For each target define a **feature witness**, not only an attractive final image:
shadow geometry/occlusion, material channels/normal orientation, glass checker-grid
refraction, caustic receiver contrast and sample convergence, volume attenuation,
instance geometry reuse, decoded asset identity, frame timing and text glyph/outline
integrity as applicable. Emit these checks in the script/manifest; overlay captions
cannot hide a missing feature. Every result is PLANNED until the actual lmvideo
script, output, licence manifest, CPU timing and feature witnesses pass together.

Licence checks used the directly fetched Blender HTML cards (e.g. Classroom CC0;
Cozy Kitchen/Scanlands/Secret Deer/Repeat Zone Flower carry ShareAlike notices) and
the actual three.js model README. A broad repository MIT notice or a catalogue
label alone is not the provenance of every extracted mesh/texture/font. No asset,
reference render, product implementation or website publication was added here.
