#!/bin/bash
set -e

echo "::group::🎨 Three.js Scene Generation"
echo "Starting at: $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"

# 環境変数から設定を読み込み
SRC_DIR="$FOLDER_NAME/src"
ASSETS_DIR="$FOLDER_NAME/assets"

echo "Configuration:"
echo "  Experience concept: $EXPERIENCE_CONCEPT"
echo "  Background type: $BACKGROUND_TYPE"
echo "  Particle enabled: $PARTICLE_ENABLED"
echo "  Target folders: $SRC_DIR"

# ディレクトリを事前に作成
mkdir -p "$SRC_DIR"
mkdir -p "$ASSETS_DIR"
echo "📁 Created directory structure"

# 基本的なプロンプト構築
PROMPT="Create a Three.js experience HTML file at $SRC_DIR/index.html.

Concept: $EXPERIENCE_CONCEPT

Requirements:
- Use Three.js CDN: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- Single HTML file with inline JavaScript
- No OrbitControls dependency"

# 背景タイプによる設定
if [ "$BACKGROUND_TYPE" = "solid_black" ]; then
  PROMPT="$PROMPT
- Black background (0x000000)"
elif [ "$BACKGROUND_TYPE" = "solid_white" ]; then
  PROMPT="$PROMPT
- White background (0xFFFFFF)"
elif [ "$BACKGROUND_TYPE" = "gradient" ]; then
  PROMPT="$PROMPT
- Gradient background using shaders"
elif [ "$BACKGROUND_TYPE" = "transparent" ]; then
  PROMPT="$PROMPT
- Transparent background (alpha: 0)"
else
  PROMPT="$PROMPT
- Default background"
fi

# パーティクル設定
if [ "$PARTICLE_ENABLED" = "true" ]; then
  PROMPT="$PROMPT
- Add particle system with:
  - Particle count: ${PARTICLE_COUNT:-1000}
  - Floating particles
  - Random positions
  - Simple animation"
fi

# 音楽設定
if [ "$INCLUDE_MUSIC" = "true" ] && [ -n "$MUSIC_URL" ]; then
  PROMPT="$PROMPT
- Add music controls:
  - HTML5 Audio element
  - Play/Pause button in UI
  - Loop playback
  - Music file from: $MUSIC_URL"
fi

# 基本機能
PROMPT="$PROMPT
- Mouse drag to rotate view
- Mouse wheel to zoom
- Double-click for auto-rotation
- Responsive design"

echo "🚀 Starting Three.js Scene Generation Agent..."
echo "📝 Prompt length: ${#PROMPT} characters"

# Claude Code CLIの実行
npx @anthropic-ai/claude-code \
  --allowedTools "Bash,Write" \
  --max-turns 15 \
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