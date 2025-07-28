# 🌐 360° Panorama Point Cloud Generation

This module generates 3D point cloud data from 360-degree panorama images using MiDaS-style depth estimation and spherical coordinate transformation.

## 🎯 Overview

Converts equirectangular panorama images into spherical 3D point clouds with depth information:

```
[360° Panorama Image] → [MiDaS Depth Estimation] → [Spherical PLY Point Cloud]
```

## 📋 Features

- **MiDaS Depth Estimation**: Simulated depth analysis optimized for panoramic images
- **Spherical Coordinate System**: Proper equirectangular to sphere transformation  
- **Pole Compression**: Reduces distortion at panorama poles (top/bottom)
- **Seamline Continuity**: Ensures smooth 360° experience at left/right boundaries
- **Adaptive Particle Density**: Configurable quality levels (low/medium/high)
- **Depth Variation Control**: Adjustable depth-based radius modification

## 🔧 Usage

### Basic Usage
```yaml
- name: Generate Panorama Point Cloud
  uses: ./.github/actions/kamui-modules/pointcloud-panorama-generation
  with:
    panorama_image_path: 'assets/panorama.jpg'
    output_directory: 'generated'
```

### Advanced Configuration
```yaml
- name: Generate High-Quality Panorama Point Cloud
  uses: ./.github/actions/kamui-modules/pointcloud-panorama-generation
  with:
    panorama_image_path: 'assets/360_image.jpg'
    output_directory: 'assets'
    sphere_radius: '300'
    depth_resolution: '2048x1024'
    particle_density: 'high'
    depth_variation: '0.6'
    enable_pole_compression: 'true'
    depth_inversion: 'false'
```

## 📊 Input Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `panorama_image_path` | 360° panorama image (equirectangular) | - | ✅ |
| `output_directory` | Output directory for generated files | `assets` | ❌ |
| `sphere_radius` | Base sphere radius for particles | `200` | ❌ |
| `depth_resolution` | Depth analysis resolution (WxH) | `1024x512` | ❌ |
| `particle_density` | Density level (low/medium/high) | `medium` | ❌ |
| `depth_variation` | Depth-based radius variation (0.0-1.0) | `0.4` | ❌ |
| `enable_pole_compression` | Enable pole distortion reduction | `true` | ❌ |
| `depth_inversion` | Invert depth values | `false` | ❌ |

## 📤 Outputs

| Output | Description |
|--------|-------------|
| `panorama_ply_path` | Generated PLY point cloud file path |
| `depth_map_path` | Generated depth map PNG file path |
| `particle_count` | Number of generated particles |
| `processing_time` | Total processing time in seconds |
| `sphere_info` | JSON with sphere configuration details |

## 🏗️ Technical Architecture

### Depth Estimation Process
```python
# 1. Load equirectangular panorama
panorama = load_panorama_image(image_path)

# 2. Simulate MiDaS depth estimation
depth_map = simulate_midas_depth_estimation(panorama)

# 3. Apply panorama-specific corrections
depth_corrected = correct_panorama_distortion(depth_map)
```

### Spherical Transformation
```javascript
// Convert normalized coordinates to spherical with depth
function equirectangularToSphere(u, v, depthValue, baseRadius) {
    const phi = u * 2 * Math.PI;           // Longitude
    const theta = v * Math.PI;             // Latitude
    
    // Depth-based radius adjustment
    const depthFactor = depthValue / 255.0;
    const adjustedRadius = baseRadius + (depthFactor - 0.5) * radiusVariation;
    
    // Convert to Cartesian coordinates
    return {
        x: adjustedRadius * Math.sin(theta) * Math.cos(phi),
        y: adjustedRadius * Math.cos(theta),
        z: adjustedRadius * Math.sin(theta) * Math.sin(phi)
    };
}
```

## 🎨 Generated Files

### PLY Point Cloud
- **Format**: ASCII PLY with position (x,y,z) and color (r,g,b)
- **Coordinate System**: Centered sphere with depth-varied radius
- **Particle Count**: 15K-65K depending on density setting

### Depth Maps
- **Gray Depth**: `*_depth_gray.png` - Raw depth values (0-255)
- **Color Depth**: `*_depth.png` - Colorized visualization

### Processing Report
- **Report**: `panorama_generation_report.md` - Complete processing summary

## 🔍 Quality Optimization

### Particle Density Settings
```yaml
particle_density: 'low'    # 15,000 particles - Fast processing
particle_density: 'medium' # 35,000 particles - Balanced quality
particle_density: 'high'   # 65,000 particles - High detail
```

### Depth Variation Control
```yaml
depth_variation: '0.2'  # Subtle depth effects
depth_variation: '0.4'  # Moderate depth variation (default)
depth_variation: '0.8'  # Strong depth effects
```

## 🧪 Integration with Viewer

The generated PLY files are designed to work with the `threejs-panorama-viewer`:

```yaml
- name: Generate Panorama Point Cloud
  uses: ./.github/actions/kamui-modules/pointcloud-panorama-generation
  with:
    panorama_image_path: 'input/panorama.jpg'
  id: generate

- name: Create Interactive Viewer
  uses: ./.github/actions/kamui-modules/threejs-panorama-viewer
  with:
    ply_file_path: ${{ steps.generate.outputs.panorama_ply_path }}
    enable_depth_visualization: 'true'
```

## 📈 Performance Characteristics

| Density | Particles | Processing Time | Memory Usage | File Size |
|---------|-----------|----------------|--------------|-----------|
| Low | 15K | ~30s | ~50MB | ~2MB |
| Medium | 35K | ~60s | ~120MB | ~5MB |
| High | 65K | ~120s | ~200MB | ~10MB |

*Times measured on GitHub Actions standard runner*

## 🔧 Troubleshooting

### Common Issues

**❌ "Image aspect ratio not 2:1"**
- Ensure panorama is equirectangular projection
- Standard format is 2:1 aspect ratio (e.g., 4096x2048)

**❌ "Low particle count generated"**
- Increase `particle_density` setting
- Check image brightness (very dark areas are skipped)
- Verify `depth_resolution` is appropriate

**❌ "Distorted sphere visualization"**
- Enable `enable_pole_compression: 'true'`
- Adjust `depth_variation` to reduce extreme variations
- Check panorama image quality at poles

### Performance Optimization

```yaml
# For faster processing:
depth_resolution: '512x256'
particle_density: 'low'
depth_variation: '0.2'

# For maximum quality:
depth_resolution: '2048x1024'  
particle_density: 'high'
depth_variation: '0.6'
```

## 🔗 Related Modules

- **[threejs-panorama-viewer](../threejs-panorama-viewer/)**: Interactive 3D panorama viewer
- **[pointcloud-generation](../pointcloud-generation/)**: Original 2D→3D point cloud generation
- **[shared-viewer-components](../shared-viewer-components/)**: Shared Three.js components

---

*Generated by kamuicode Creative Workshop | Phase 2 Implementation*