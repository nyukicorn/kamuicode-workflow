# 音楽付きパーティクル花園 (Particle Garden with Music)

An interactive Three.js experience featuring floating particles in a beautiful animated garden environment with synchronized background music.

## Experience Concept

音楽付きパーティクル花園 creates an immersive particle-based visual experience where colorful particles float and dance in 3D space. The particles move organically with gentle wave motions while users can interact with the scene through mouse controls. Background music enhances the meditative and artistic atmosphere.

## Controls

- **Mouse Drag**: Rotate the particle garden view
- **Mouse Wheel**: Zoom in and out 
- **Double-click**: Toggle automatic rotation mode
- **Play Button**: Start/pause background music
- **Volume Slider**: Adjust music volume

## Technical Requirements

- **Three.js**: WebGL-based 3D graphics library
- **WebGL**: Required for hardware-accelerated rendering
- **Modern Browser**: Chrome, Firefox, Safari, Edge (latest versions)
- **Audio Support**: WAV format playback capability

## Features

- 1000+ animated particles with dynamic colors
- Shader-based background with gradient effects
- Interactive camera controls
- Audio integration with volume control
- Responsive design for mobile devices
- Smooth 60fps animation performance

## Files Structure

```
threejs-experience-20250720-16402343270/
├── README.md
├── src/
│   └── index.html          # Main application file
├── music/
│   └── generated-music.wav # Background music
└── final/
    └── threejs-experience.zip # Packaged experience
```

## Usage

1. Open `src/index.html` in a modern web browser
2. Click the play button to start background music
3. Interact with the particle garden using mouse controls
4. Enjoy the immersive visual and audio experience