#!/bin/bash

# Three.js 3D Model Viewer Integration Script
# This script creates a Three.js viewer for 3D models using Claude Code SDK

set -e

echo "🎯 Starting Three.js 3D Model Integration"
echo "Model Concept: $MODEL_CONCEPT"
echo "Model File: $MODEL_FILE_NAME.$MODEL_FORMAT"
echo "Viewer Style: $VIEWER_STYLE"
echo "Background: $BACKGROUND_TYPE"
echo "Lighting: $LIGHTING_PRESET"
echo "Camera: $CAMERA_CONTROLS"
echo "Folder: $FOLDER_NAME"

# Create viewer info JSON
cat > "$FOLDER_NAME/viewer-info.json" << EOF
{
  "model_concept": "$MODEL_CONCEPT",
  "model_file": "$MODEL_FILE_NAME.$MODEL_FORMAT",
  "viewer_style": "$VIEWER_STYLE",
  "background_type": "$BACKGROUND_TYPE",
  "lighting_preset": "$LIGHTING_PRESET",
  "camera_controls": "$CAMERA_CONTROLS",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "integration_method": "threejs_3d_viewer"
}
EOF

# Build the Claude Code prompt for 3D viewer
PROMPT="Create a professional Three.js 3D model viewer for the following specifications:

Model Details:
- Concept: $MODEL_CONCEPT  
- File: $MODEL_FILE_NAME.$MODEL_FORMAT
- Format: $MODEL_FORMAT

Viewer Configuration:
- Style: $VIEWER_STYLE
- Background: $BACKGROUND_TYPE
- Lighting: $LIGHTING_PRESET  
- Camera: $CAMERA_CONTROLS

Requirements:
1. Create an index.html file in the $FOLDER_NAME/ folder
2. Include complete Three.js viewer with proper $MODEL_FORMAT loader
3. Implement $CAMERA_CONTROLS camera controls
4. Set up $LIGHTING_PRESET lighting preset
5. Apply $BACKGROUND_TYPE background
6. Use $VIEWER_STYLE styling approach
7. Include loading screen and error handling
8. Make it responsive and mobile-friendly
9. Add model information display
10. Include performance optimizations

Technical Requirements:
- Use Three.js r128 (proven stable): https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js  
- OrbitControls: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/controls/OrbitControls.js
- GLTFLoader: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/loaders/GLTFLoader.js
- CRITICAL: These URLs are tested and working - DO NOT CHANGE
- CRITICAL: Load scripts IN ORDER with error handling
- Use THREE.OrbitControls constructor (not ES module import)
- Use renderer.outputEncoding (r128 compatible)
- Add proper error handling for failed script loads
- Include loading progress indication
- Add proper model loading with progress indication
- Implement appropriate lighting for the model type
- Handle GLB/PLY/OBJ formats appropriately
- Include model statistics display
- Add fullscreen capability
- Ensure cross-browser compatibility

Please create a complete, professional 3D viewer that works directly in GitHub Pages.
The model file $MODEL_FILE_NAME.$MODEL_FORMAT will be in the same directory as the index.html.

Make sure the viewer is:
- User-friendly with intuitive controls
- Visually appealing with proper styling
- Well-documented with inline comments
- Error-resistant with proper fallbacks

CRITICAL FEATURES:
1. GLB/PLY/OBJ loader support
2. Mouse orbit controls (drag to rotate, wheel to zoom)
3. Model centering and auto-scaling
4. Loading progress indicator
5. Error handling for missing/corrupt files
6. Mobile-responsive design
7. Model information panel showing file size, vertices, etc.
8. Proper lighting for 3D model visibility

WORKING SCRIPT TEMPLATE (COPY EXACTLY - TESTED CDNS):
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/controls/OrbitControls.js"></script>  
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/loaders/GLTFLoader.js"></script>
<script>
// Simple initialization after all scripts loaded
document.addEventListener('DOMContentLoaded', function() {
    if (typeof THREE !== 'undefined' && THREE.OrbitControls && THREE.GLTFLoader) {
        console.log('All Three.js components loaded successfully');
        initViewer(); // Start the 3D viewer
    } else {
        console.error('Three.js components failed to load');
        document.body.innerHTML = '<h1>Loading Error</h1><p>Please refresh the page to try again.</p>';
    }
});
</script>

CRITICAL SUCCESS FACTORS:
- Use the exact CDN URLs above (cdnjs.cloudflare.com r128)
- Load scripts with separate script tags, not dynamic loading  
- Check for THREE.OrbitControls and THREE.GLTFLoader availability
- Use DOMContentLoaded event for initialization"

echo "🚀 Starting Three.js 3D Viewer Integration Agent..."
echo "📝 Prompt length: ${#PROMPT} characters"

# Claude Code CLI (following existing pattern)
npx @anthropic-ai/claude-code \
  --allowedTools "Write,Read,LS" \
  --max-turns 8 \
  --permission-mode "acceptEdits" \
  -p "$PROMPT"

echo "🎉 Three.js 3D Model Integration completed!"

# Display results
if [ -f "$FOLDER_NAME/index.html" ]; then
  echo "✅ Generated 3D viewer: $FOLDER_NAME/index.html"
  ls -la "$FOLDER_NAME/index.html"
else
  echo "⚠️  Viewer file not found, but integration process completed"
fi

echo "📋 Viewer info saved to: $FOLDER_NAME/viewer-info.json"
echo "🌐 3D viewer will be deployed to GitHub Pages"