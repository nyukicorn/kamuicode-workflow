# Three.js Experience: Panorama Test with Custom Model

## Overview
A beautiful interactive 3D experience featuring a Rose Bouquet System with dynamic controls and animations. This immersive web application showcases animated roses with realistic petals, particle effects, and panoramic backgrounds.

## Features
- **Interactive Rose Bouquet**: 5 roses arranged in a natural bouquet formation
- **Dynamic Petal System**: Procedurally generated rose petals with gradient textures
- **Particle Effects**: Ambient and floating particles for atmospheric enhancement
- **Real-time Controls**: Adjustable animation speed, petal properties, and opacity settings
- **Camera System**: Mouse/touch controls with auto-rotation capability

## Controls
- **Mouse drag**: Rotate camera around the bouquet
- **Mouse wheel**: Zoom in/out
- **Double-click**: Toggle automatic rotation
- **Touch support**: Mobile-friendly touch controls

## Control Panel
- Animation Speed: Control overall animation timing
- Rotation Speed: Adjust auto-rotation speed
- Petal Width: Modify petal size
- Petal Curl: Adjust petal curvature
- Rose/Stem/Ambient Opacity: Fine-tune transparency levels

## Technical Requirements
- **WebGL**: Required for 3D rendering
- **Three.js**: r128 (loaded via CDN)
- **Modern Browser**: Supports ES6+ features
- **Hardware Acceleration**: Recommended for optimal performance

## Usage
Simply open `src/index.html` in a modern web browser. The experience will load automatically and begin rendering the interactive rose bouquet scene.

## Performance
Optimized for real-time rendering with:
- 3000 ambient particles
- 1000 floating particles  
- 20 petals per rose (100 total)
- Efficient geometry updates
- Smooth 60fps animation

## Browser Compatibility
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+