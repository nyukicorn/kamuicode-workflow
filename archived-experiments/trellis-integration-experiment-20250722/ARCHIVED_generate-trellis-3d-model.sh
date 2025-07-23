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

# Build the Claude Code prompt
PROMPT="Generate a 3D model using the TRELLIS MCP integration.

Input: $INPUT_TYPE - $INPUT_DATA
Output format: $OUTPUT_FORMAT
Diffusion steps: $STEPS
Output filename: $MODEL_NAME.$OUTPUT_FORMAT
Output folder: $FOLDER_NAME/

Please:
1. Use the appropriate MCP tool to generate the 3D model
2. Save the generated model to the specified folder and filename
3. Provide generation details and any relevant metadata
4. If TRELLIS is not available, create a simulation/placeholder file for testing

Make sure the generated file is properly saved to $FOLDER_NAME/$MODEL_NAME.$OUTPUT_FORMAT

CRITICAL REQUIREMENTS:
- Use polycam MCP tools for TRELLIS 3D generation
- Handle both image-to-3D and text-to-3D workflows
- Create proper $OUTPUT_FORMAT file format
- Save to exact path: $FOLDER_NAME/$MODEL_NAME.$OUTPUT_FORMAT"

echo "🚀 Starting TRELLIS 3D Model Generation Agent..."
echo "📝 Prompt length: ${#PROMPT} characters"

# Claude Code CLI (following existing pattern)
npx @anthropic-ai/claude-code \
  --allowedTools "Bash,Read,Write,LS" \
  --max-turns 10 \
  --permission-mode "acceptEdits" \
  -p "$PROMPT"

echo "🎉 TRELLIS 3D Model Generation completed!"

# Display results
if [ -f "$FOLDER_NAME/$MODEL_NAME.$OUTPUT_FORMAT" ]; then
  echo "✅ Generated model: $FOLDER_NAME/$MODEL_NAME.$OUTPUT_FORMAT"
  ls -la "$FOLDER_NAME/$MODEL_NAME.$OUTPUT_FORMAT"
else
  echo "⚠️  Model file not found, but generation process completed"
fi

echo "📋 Generation info saved to: $FOLDER_NAME/generation-info.json"