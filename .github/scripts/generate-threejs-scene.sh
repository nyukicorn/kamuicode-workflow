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
echo "  Art style: $ART_STYLE"
echo "  Arrangement: $ARRANGEMENT"
echo "  Color scheme: $COLOR_SCHEME"
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

# アートスタイルパーシング
case "$ART_STYLE" in
  "flower:sakura")
    PROMPT="$PROMPT
- Create 3D sakura (cherry blossom) art using particles:
  - Pink and white sakura petals arranged in 3D space
  - ${PARTICLE_COUNT:-1000} particles forming sakura shapes
  - Floating petals with gentle movement
  - Beautiful sakura tree or branch structure"
    ;;
  "flower:rose")
    PROMPT="$PROMPT
- Create 3D rose art using particles:
  - Red and pink rose petals in 3D formation
  - ${PARTICLE_COUNT:-1000} particles forming rose shapes
  - Elegant rose structure with layered petals"
    ;;
  "flower:lily")
    PROMPT="$PROMPT
- Create 3D lily art using particles:
  - White and yellow lily petals in elegant formation
  - ${PARTICLE_COUNT:-1000} particles forming lily shapes
  - Graceful lily structure with long stems"
    ;;
  "nature:tree")
    PROMPT="$PROMPT
- Create 3D tree art using particles:
  - Tree structure with branches and leaves
  - ${PARTICLE_COUNT:-1000} particles forming natural tree shape
  - Green and brown color scheme"
    ;;
  "nature:ocean")
    PROMPT="$PROMPT
- Create 3D ocean art using particles:
  - Wave-like formations and water droplets
  - ${PARTICLE_COUNT:-1000} particles forming ocean waves
  - Blue gradient color scheme"
    ;;
  "geometric:sphere")
    PROMPT="$PROMPT
- Create 3D geometric sphere art using particles:
  - Perfect sphere formation with ${PARTICLE_COUNT:-1000} particles
  - Mathematical precision in particle placement
  - Clean geometric lines"
    ;;
  "geometric:cube")
    PROMPT="$PROMPT
- Create 3D geometric cube art using particles:
  - Cubic formation with ${PARTICLE_COUNT:-1000} particles
  - Sharp edges and perfect symmetry
  - Modern geometric design"
    ;;
  "abstract:fluid")
    PROMPT="$PROMPT
- Create 3D abstract fluid art using particles:
  - Flowing, organic formations
  - ${PARTICLE_COUNT:-1000} particles in fluid motion
  - Smooth, curved shapes"
    ;;
  "simple:particles")
    PROMPT="$PROMPT
- Add simple particle system:
  - ${PARTICLE_COUNT:-1000} floating particles
  - Random positions and simple animation
  - Basic particle effects"
    ;;
  *)
    PROMPT="$PROMPT
- Create artistic particle formation:
  - ${PARTICLE_COUNT:-1000} particles in creative arrangement
  - Beautiful visual composition"
    ;;
esac

# 配置スタイル
case "$ARRANGEMENT" in
  "floating")
    PROMPT="$PROMPT
- Particles float freely in 3D space"
    ;;
  "grounded")
    PROMPT="$PROMPT
- Particles arranged with ground reference"
    ;;
  "scene")
    PROMPT="$PROMPT
- Particles form complete 3D scene"
    ;;
esac

# カラースキーム
if [ "$COLOR_SCHEME" != "auto" ]; then
  PROMPT="$PROMPT
- Color scheme: $COLOR_SCHEME colors"
fi

# エフェクト
if [ "$EFFECTS" != "none" ]; then
  PROMPT="$PROMPT
- Add $EFFECTS effects to particles"
fi

# 音楽設定
if [ "$INCLUDE_MUSIC" = "true" ] && [ -n "$MUSIC_URL" ]; then
  PROMPT="$PROMPT
- Add music controls:
  - HTML5 Audio element with muted autoplay initially
  - Prominent Play/Pause button in UI
  - NO automatic playback on page load
  - User must click Play button first (browser policy)
  - Loop playback when playing
  - Music file path: './generated-music.wav' (same directory as index.html)"
fi

# インタラクティブ機能
PROMPT="$PROMPT
- Mouse controls:
  - Drag to rotate view
  - Wheel to zoom
  - Double-click for auto-rotation
- Interactive controls (if particle_art):
  - Color adjustment controls
  - Size adjustment controls
  - Speed adjustment controls
- Responsive design for all screen sizes"

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