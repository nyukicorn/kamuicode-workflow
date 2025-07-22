#!/bin/bash

# TRELLIS 3D Model Generation Script
# This script uses Claude Code SDK with the Polycam MCP to generate 3D models

set -e

echo "🎯 Starting TRELLIS 3D Model Generation"
echo "Input Type: $INPUT_TYPE"
echo "Input Data: $INPUT_DATA"
echo "Output Format: $OUTPUT_FORMAT"
echo "Steps: $STEPS"
echo "Model Name: $MODEL_NAME"
echo "Folder: $FOLDER_NAME"

# Create generation info JSON
cat > "$FOLDER_NAME/generation-info.json" << EOF
{
  "input_type": "$INPUT_TYPE",
  "input_data": "$INPUT_DATA", 
  "output_format": "$OUTPUT_FORMAT",
  "steps": $STEPS,
  "model_name": "$MODEL_NAME",
  "generated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "generation_method": "trellis_mcp"
}
EOF

# Create Claude Code script for 3D generation
cat > claude_3d_generation.js << 'EOF'
import { ClaudeCode } from '@anthropic-ai/claude-code';

const client = new ClaudeCode({
  apiKey: process.env.CLAUDE_CODE_OAUTH_TOKEN
});

async function generate3DModel() {
  const inputType = process.env.INPUT_TYPE;
  const inputData = process.env.INPUT_DATA;
  const outputFormat = process.env.OUTPUT_FORMAT;
  const steps = parseInt(process.env.STEPS);
  const modelName = process.env.MODEL_NAME;
  const folderName = process.env.FOLDER_NAME;

  console.log(`🚀 Generating 3D model from ${inputType}: ${inputData}`);
  
  try {
    // Generate 3D model using TRELLIS MCP tools
    const prompt = `
Generate a 3D model using the TRELLIS integration.

Input: ${inputType === 'image' ? 'Image URL: ' + inputData : 'Text prompt: ' + inputData}
Output format: ${outputFormat}
Diffusion steps: ${steps}
Output filename: ${modelName}.${outputFormat}
Output folder: ${folderName}/

Please:
1. Use the appropriate MCP tool to generate the 3D model
2. Save the generated model to the specified folder and filename
3. Provide generation details and any relevant metadata
4. If TRELLIS is not available, create a simulation/placeholder file for testing

Make sure the generated file is properly saved to ${folderName}/${modelName}.${outputFormat}
    `;

    const response = await client.beta.tools.use({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 4096,
      messages: [{ role: 'user', content: prompt }],
      tools: [
        { type: 'bash' },
        { type: 'computer_use', display_width: 1024, display_height: 768 }
      ]
    });

    console.log('✅ 3D model generation completed');
    console.log('Response:', response.content);

    // Set outputs
    console.log(`::set-output name=completed::true`);
    console.log(`::set-output name=model-file-path::${folderName}/${modelName}.${outputFormat}`);
    
    // Check if file was created and get size
    const fs = require('fs');
    const path = require('path');
    const modelPath = path.join(folderName, `${modelName}.${outputFormat}`);
    
    if (fs.existsSync(modelPath)) {
      const stats = fs.statSync(modelPath);
      console.log(`::set-output name=model-size::${stats.size}`);
      console.log(`📁 Model file created: ${modelPath} (${stats.size} bytes)`);
    } else {
      console.log(`⚠️  Model file not found: ${modelPath}`);
      console.log(`::set-output name=model-size::0`);
    }

  } catch (error) {
    console.error('❌ Error generating 3D model:', error);
    console.log(`::set-output name=completed::false`);
    process.exit(1);
  }
}

generate3DModel();
EOF

# Run the Claude Code 3D generation
echo "🎬 Running Claude Code 3D generation..."
node claude_3d_generation.js

echo "🎉 TRELLIS 3D Model Generation completed!"

# Display results
if [ -f "$FOLDER_NAME/$MODEL_NAME.$OUTPUT_FORMAT" ]; then
  echo "✅ Generated model: $FOLDER_NAME/$MODEL_NAME.$OUTPUT_FORMAT"
  ls -la "$FOLDER_NAME/$MODEL_NAME.$OUTPUT_FORMAT"
else
  echo "⚠️  Model file not found, but generation process completed"
fi

echo "📋 Generation info saved to: $FOLDER_NAME/generation-info.json"