#!/bin/bash
set -e

echo "::group::🎨 Three.js Scene Generation"
echo "Starting at: $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"

# 環境変数から設定を読み込み
SRC_DIR="$FOLDER_NAME/src"

echo "Target folders: $SRC_DIR"

# ディレクトリを事前に作成
mkdir -p "$SRC_DIR"
echo "📁 Created directory structure"

PROMPT="Please generate a single, self-contained HTML file named 'index.html' in the '$SRC_DIR' directory.\n\nThis file should create a simple Three.js scene with the following requirements:\n- Use the Three.js CDN: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js\n- The scene should have a black background.\n- Create a single BoxGeometry mesh (a cube).\n- The cube should have a basic material (MeshBasicMaterial) with a visible color (e.g., 0x00ff00).\n- Animate the cube to rotate on its Y-axis.\n- No user controls, no particles, no UI, and no other complex features are needed.\n- Ensure the final output is only one file: '$SRC_DIR/index.html'."

echo "🚀 Starting Three.js Scene Generation Agent..."
echo "📝 Prompt: $PROMPT"

# Claude Code CLIの実行
npx @anthropic-ai/claude-code \
  --allowedTools "Bash" \
  --max-turns 10 \
  --verbose \
  --permission-mode "acceptEdits" \
  -p "$PROMPT"

# 生成されたファイルの確認
echo ""
echo "📸 Checking generated Three.js files..."
if [ -f "$SRC_DIR/index.html" ]; then
  echo "✅ Main HTML file created: $SRC_DIR/index.html"
  HTML_SIZE=$(wc -c < "$SRC_DIR/index.html")
  echo "  HTML file size: $HTML_SIZE bytes"
else
  echo "::error::❌ Main HTML file not found at $SRC_DIR/index.html"
  exit 1
fi

TOTAL_FILES=$(find "$SRC_DIR" -type f | wc -l)
echo "scene-files-created=$TOTAL_FILES" >> $GITHUB_OUTPUT
echo "completed=true" >> $GITHUB_OUTPUT
echo "::endgroup::"