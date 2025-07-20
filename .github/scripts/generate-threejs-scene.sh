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

PROMPT="Create a simple Three.js HTML file at $SRC_DIR/index.html with:
- Three.js CDN import
- Black background
- Green rotating cube
- Basic animation loop
Just one HTML file with inline JavaScript."

echo "🚀 Starting Three.js Scene Generation Agent..."
echo "📝 Prompt: $PROMPT"

# Claude Code CLIの実行
npx @anthropic-ai/claude-code \
  --allowedTools "Bash,Write" \
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