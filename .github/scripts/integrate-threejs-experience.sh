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

PROMPT="Three.js体験の最終統合とパッケージングを実行してください。

**体験コンセプト**: $EXPERIENCE_CONCEPT
**音楽統合**: $INCLUDE_MUSIC
$MUSIC_INFO

**実行手順**:
1. 生成されたファイルの品質チェック:
   - $SRC_DIR/index.htmlの構文確認
   - JavaScriptファイルの基本的な構文チェック
   - CSSファイルの妥当性確認
   - パノラマ画像のファイルサイズ確認

2. READMEファイル作成($FOLDER_NAME/README.md):
   - 体験コンセプトの説明
   - 操作方法（マウス/タッチ操作）
   - 技術仕様（Three.js, WebGL要件）
   - ローカル実行方法
   - 対応ブラウザ情報
   - トラブルシューティング

3. パフォーマンス最適化:
   - 画像ファイルサイズの確認
   - 不要なファイルの削除
   - HTMLのminification確認

4. 最終パッケージ作成（必須）:
   - **重要**: Bashツールを使用してzipパッケージを必ず作成
   - コマンド: cd $FOLDER_NAME/.. && zip -r $FINAL_DIR/threejs-experience.zip $(basename $FOLDER_NAME)/
   - 作成確認: $FINAL_DIR/threejs-experience.zip が存在することを確認
   - ファイルサイズの記録

**品質チェック項目**:
- WebGL対応チェックの実装確認
- レスポンシブデザインの実装確認
- エラーハンドリングの実装確認
- パフォーマンス最適化の実装確認
- ブラウザ互換性の確認

**最終成果物**:
- 完全動作するThree.js体験
- 詳細なREADME文書
- 配布用zipパッケージ
- 品質チェックレポート

**重要な注意点**:
- すべてのファイルパスが相対パスで正しく設定されているか確認
- 外部依存関係の確認（CDNリンクなど）
- モバイルデバイスでの動作確認要件の記載
- セキュリティベストプラクティスの確認"

echo "🚀 Starting Integration & Packaging Agent..."
echo "📝 Prompt length: ${#PROMPT}"

# Claude Code CLIの実行
npx @anthropic-ai/claude-code \
  --allowedTools "Bash" \
  --max-turns 25 \
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
