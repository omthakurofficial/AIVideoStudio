# Three.js & WebGL 3D Motion Graphics Rules

Distilled from CloudAI-X/threejs-skills and modern 3D WebGL motion graphic workflows.

## 1. 3D Scene Composition
- **Dark Spatial Canvas**: 3D infinite plane with subtle perspective grid lines and radial vignette falloff.
- **Hero 3D Meshes**:
  - `Rotating Wireframe Globe`: Central sphere with illuminated latitude/longitude rings, glowing coordinate pins, and curved orbital arcs.
  - `Spatial Node Network`: 3D nodes floating in space with dynamic connector splines and pulsing light vertices.
  - `3D Architecture Isometric Blocks`: Beveled 3D service cubes arranged on an isometric ground plane.
- **Lighting Model**: Dual light rig — key directional rim light (cyan/blue #38bdf8 or emerald #10b981) + soft ambient fill (#0f172a).

## 2. Camera Moves & Spatial Easing
- **Orbit Cam**: Continuous subtle 3D rotational drift around the hero mesh ($\Delta \theta \approx 4^\circ - 8^\circ$).
- **Dolly Push**: Controlled zoom along the Z-axis into the active node without clipping near planes.
- **Spatial Focus**: Dynamic framing that keeps all orbital nodes inside the viewport frustum.

## 3. Element Mapping & Synchronization
- Every 3D node or layer must have clear, human-readable labels and metrics.
- Timing: Entrances staggered to narration beats; glowing data packets travel along connector splines when communication is described.
