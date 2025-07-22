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

# Create Claude Code script for 3D viewer integration
cat > claude_3d_integration.js << 'EOF'
import { ClaudeCode } from '@anthropic-ai/claude-code';

const client = new ClaudeCode({
  apiKey: process.env.CLAUDE_CODE_OAUTH_TOKEN
});

async function integrate3DViewer() {
  const modelConcept = process.env.MODEL_CONCEPT;
  const modelFileName = process.env.MODEL_FILE_NAME;
  const modelFormat = process.env.MODEL_FORMAT;
  const viewerStyle = process.env.VIEWER_STYLE;
  const backgroundType = process.env.BACKGROUND_TYPE;
  const lightingPreset = process.env.LIGHTING_PRESET;
  const cameraControls = process.env.CAMERA_CONTROLS;
  const folderName = process.env.FOLDER_NAME;

  console.log(`🚀 Creating Three.js 3D viewer for: ${modelConcept}`);
  
  try {
    const prompt = `
Create a professional Three.js 3D model viewer for the following specifications:

Model Details:
- Concept: ${modelConcept}
- File: ${modelFileName}.${modelFormat}
- Format: ${modelFormat.toUpperCase()}

Viewer Configuration:
- Style: ${viewerStyle}
- Background: ${backgroundType}
- Lighting: ${lightingPreset}
- Camera: ${cameraControls}

Requirements:
1. Create an index.html file in the ${folderName}/ folder
2. Include complete Three.js viewer with proper ${modelFormat.toUpperCase()} loader
3. Implement ${cameraControls} camera controls
4. Set up ${lightingPreset} lighting preset
5. Apply ${backgroundType} background
6. Use ${viewerStyle} styling approach
7. Include loading screen and error handling
8. Make it responsive and mobile-friendly
9. Add model information display
10. Include performance optimizations

Technical Requirements:
- Use Three.js via CDN (latest stable version)
- Include OrbitControls for camera movement
- Add proper model loading with progress indication
- Implement appropriate lighting for the model type
- Handle different model formats appropriately
- Include model statistics display
- Add fullscreen capability
- Ensure cross-browser compatibility

Please create a complete, professional 3D viewer that works directly in GitHub Pages.
The model file ${modelFileName}.${modelFormat} will be in the same directory as the index.html.

Make sure the viewer is:
- User-friendly with intuitive controls
- Visually appealing with proper styling
- Well-documented with inline comments
- Error-resistant with proper fallbacks
    `;

    const response = await client.beta.tools.use({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 8192,
      messages: [{ role: 'user', content: prompt }],
      tools: [
        { type: 'bash' },
        { type: 'computer_use', display_width: 1024, display_height: 768 }
      ]
    });

    console.log('✅ 3D viewer integration completed');
    console.log('Response:', response.content);

    // Set outputs
    console.log(`::set-output name=completed::true`);

    // Check if viewer was created
    const fs = require('fs');
    const path = require('path');
    const viewerPath = path.join(folderName, 'index.html');
    
    if (fs.existsSync(viewerPath)) {
      const stats = fs.statSync(viewerPath);
      console.log(`📁 3D viewer created: ${viewerPath} (${stats.size} bytes)`);
      console.log(`🌐 Viewer will be available at GitHub Pages`);
    } else {
      console.log(`⚠️  Viewer file not found: ${viewerPath}`);
    }

  } catch (error) {
    console.error('❌ Error creating 3D viewer:', error);
    console.log(`::set-output name=completed::false`);
    process.exit(1);
  }
}

integrate3DViewer();
EOF

# Run the Claude Code 3D viewer integration
echo "🎬 Running Claude Code 3D viewer integration..."
node claude_3d_integration.js

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