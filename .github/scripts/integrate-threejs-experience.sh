#!/bin/bash
set -e

echo "::group::📦 Three.js Integration & Packaging"
echo "Starting at: $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"

# 設定
EXPERIENCE_CONCEPT="$EXPERIENCE_CONCEPT"
INCLUDE_MUSIC="$INCLUDE_MUSIC"
FOLDER_NAME="$FOLDER_NAME"
SRC_DIR="$FOLDER_NAME/src"
ASSETS_DIR="$FOLDER_NAME/assets"
FINAL_DIR="$FOLDER_NAME/final"

echo "Experience concept: $EXPERIENCE_CONCEPT"
echo "Include music: $INCLUDE_MUSIC"
echo "Source folder: $FOLDER_NAME"

# finalディレクトリを作成
mkdir -p "$FINAL_DIR"
echo "📁 Created final directory: $FINAL_DIR"

# 生成されたファイルの存在確認
echo "🔍 Checking generated files..."
if [ ! -d "$SRC_DIR" ]; then
  echo "::error::❌ Source directory not found: $SRC_DIR"
  exit 1
fi

if [ ! -f "$SRC_DIR/index.html" ]; then
  echo "::error::❌ Main HTML file not found: $SRC_DIR/index.html"
  exit 1
fi

# ファイル統計
HTML_COUNT=$(find "$SRC_DIR" -name "*.html" | wc -l)
JS_COUNT=$(find "$SRC_DIR" -name "*.js" | wc -l)
CSS_COUNT=$(find "$SRC_DIR" -name "*.css" | wc -l)
ASSET_COUNT=$(find "$ASSETS_DIR" -type f 2>/dev/null | wc -l)

echo "📊 Generated files summary:"
echo "  HTML files: $HTML_COUNT"
echo "  JavaScript files: $JS_COUNT"  
echo "  CSS files: $CSS_COUNT"
echo "  Asset files: $ASSET_COUNT"

# プロンプトの構築
MUSIC_INFO=""
if [ "$INCLUDE_MUSIC" == "true" ]; then
  MUSIC_INFO="- 音楽統合機能付き（BGMオン/オフ制御）"
else
  MUSIC_INFO="- 音楽なし（パノラマ+パーティクルのみ）"
fi

PROMPT="Create final package for Three.js experience.

Tasks:
1. Copy music file if exists:
   - If $FOLDER_NAME/music/generated-music.wav exists, copy to $SRC_DIR/generated-music.wav
   - This ensures music works on GitHub Pages

2. Copy panorama image if exists:
   - If $FOLDER_NAME/assets/panorama.jpg exists, copy to $SRC_DIR/assets/panorama.jpg
   - Create assets directory: mkdir -p $SRC_DIR/assets
   - This fixes 404 error for panorama background

3. Create README.md in $FOLDER_NAME/ with:
   - Experience concept: $EXPERIENCE_CONCEPT
   - Controls: mouse drag, wheel zoom, double-click auto-rotate
   - Tech: Three.js, WebGL required
   
4. Create zip package:
   - Use bash: cd $FOLDER_NAME/.. && zip -r $FINAL_DIR/threejs-experience.zip $(basename $FOLDER_NAME)/
   - File must exist: $FINAL_DIR/threejs-experience.zip

CRITICAL: Ensure all asset files (music, panorama) are copied to correct locations."

echo "🚀 Starting Integration & Packaging Agent..."
echo "📝 Prompt length: ${#PROMPT}"

# Claude Code CLIの実行
npx @anthropic-ai/claude-code \
  --allowedTools "Bash" \
  --max-turns 60 \
  --verbose \
  --permission-mode "acceptEdits" \
  -p "$PROMPT"

# 最終結果の確認
echo ""
echo "📦 Checking final package..."

# READMEファイルの確認
if [ -f "$FOLDER_NAME/README.md" ]; then
  echo "✅ README file created: $FOLDER_NAME/README.md"
  README_SIZE=$(wc -c < "$FOLDER_NAME/README.md")
  echo "  README size: $README_SIZE bytes"
else
  echo "::warning::⚠️ README file not found"
fi

# 生成されたファイルの確認
echo ""
echo "📸 Checking generated Three.js files..."

# zipパッケージの確認
ZIP_PATH="$FINAL_DIR/threejs-experience.zip"
if [ -f "$ZIP_PATH" ]; then
  echo "✅ Final package created: $ZIP_PATH"
  PACKAGE_SIZE=$(wc -c < "$ZIP_PATH")
  PACKAGE_SIZE_MB=$((PACKAGE_SIZE / 1024 / 1024))
  echo "  Package size: $PACKAGE_SIZE bytes ($PACKAGE_SIZE_MB MB)"
  echo "final-package-path=$ZIP_PATH" >> $GITHUB_OUTPUT
  echo "package-size=${PACKAGE_SIZE_MB}MB" >> $GITHUB_OUTPUT
else
  echo "::error::❌ Final package not found"
  exit 1
fi

# 全体サマリー
TOTAL_FILES=$(find "$FOLDER_NAME" -type f | wc -l)
echo ""
echo "🎉 Integration completed successfully!"
echo "  Total files: $TOTAL_FILES"
echo "  Final package: $ZIP_PATH"
echo "  Package size: ${PACKAGE_SIZE_MB}MB"

echo "completed=true" >> $GITHUB_OUTPUT
echo "::endgroup::"
