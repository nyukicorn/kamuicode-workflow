# image-generation-multi エラー分析

**Summary**: Auto Development V2生成モジュールの具体的エラー分析と修正方針  
**Tags**: #image-generation-multi #error-analysis #claude-code-cli #file-generation  
**Related**: [ai-driven-error-correction-strategy.md], [error-prevention-checklist.md]  
**AI Usage**: image-generation-multiモジュールの自動修正時の参考資料  
**Date**: 2025-01-27  
**Status**: active  

## 🚨 確認されたエラーパターン

### 前回実行 (16456742735) - 失敗
```bash
::error::❌ Claude Code CLI execution failed
::error::❌ Music prompt file not found  
::error::❌ Image prompt file not found
::error::❌ Video concept file not found
```

### 現在実行中 (16548131691)
- **Status**: in_progress (3分54秒経過)
- **入力**: simple red flower, 1画像, imagen4-fast
- **監視中**: 同様のエラーが発生するか確認

## 🔍 根本原因分析

### 1. Claude Code CLI実行失敗
**推測される原因**:
- NPXインストール問題
- MCP設定の不備
- OAuth トークンの問題
- プロンプト構文エラー

### 2. Planning段階の失敗連鎖
**エラーの流れ**:
```
music-planning失敗 → ファイル未生成 → music-generation失敗 → image-generation-multi失敗
```

## 🛠️ 修正方針

### Phase 1: 依存関係の問題
**image-generation-multi**は他のモジュールに依存:
- `music-planning` → `music-generation` → `music-analysis` → `image-generation-multi`

**修正アプローチ**:
1. **単体テスト**: image-generation-multiを独立実行
2. **依存関係修正**: 上流モジュールの問題解決
3. **統合テスト**: 全体フロー修正

### Phase 2: 単体テスト用ワークフロー作成
```yaml
name: Test Image Generation Multi (Standalone)

on:
  workflow_dispatch:
    inputs:
      image_prompt:
        description: '画像プロンプト'
        required: true
        default: 'simple red flower'
      image_count:
        description: '画像枚数'  
        required: false
        default: '1'
      models:
        description: 'モデル'
        required: false
        default: 'imagen4-fast'

jobs:
  test-standalone:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Setup Branch
        id: setup
        uses: ./.github/actions/kamui-modules/setup-branch
        
      - name: Test Image Generation Multi (Direct)
        uses: ./.github/actions/kamui-modules/image-generation-multi
        with:
          image-prompt: ${{ inputs.image_prompt }}
          image-count: ${{ inputs.image_count }}
          models: ${{ inputs.models }}
          enable-comparison: 'false'
          folder-name: ${{ steps.setup.outputs.folder-name }}
          branch-name: ${{ steps.setup.outputs.branch-name }}
          oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          mcp-config: ${{ secrets.MCP_CONFIG }}
```

### Phase 3: MCP設定の検証
**問題の可能性**:
```yaml
# image-generation-multi/action.yml の MCP設定フィルタリング
echo '${{ inputs.mcp-config }}' | jq '
  .mcpServers | 
  to_entries | 
  map(select(.key | startswith("t2i-"))) |
  from_entries |
  {"mcpServers": .}
' > "$MCP_CONFIG_ABS_PATH"
```

**修正案**:
1. **JQコマンドの検証**: 正しいフィルタリングか確認
2. **MCP設定の確認**: 実際の設定内容チェック
3. **エラーハンドリング**: JQ失敗時の対応

### Phase 4: Claude Code CLI実行の改善
**現在のコード**:
```bash
npx @anthropic-ai/claude-code \
  --mcp-config="$MCP_CONFIG_ABS_PATH" \
  --allowedTools "mcp__*,Bash" \
  --max-turns 25 \
  --verbose \
  --permission-mode "bypassPermissions" \
  -p "$PROMPT"
```

**改善案**:
1. **エラーハンドリング強化**: 詳細なログ出力
2. **段階的実行**: プロンプト分割
3. **フォールバック機構**: 失敗時の代替手段

## 🎯 AI駆動修正ワークフロー設計

### auto-fix-image-generation-multi.yml
```yaml
name: Auto Fix Image Generation Multi

on:
  workflow_dispatch:
    inputs:
      error_type:
        description: 'エラータイプ'
        type: choice
        options:
          - 'claude-code-cli-failure'
          - 'mcp-config-error'  
          - 'file-generation-failure'
          - 'dependency-failure'

jobs:
  auto-fix:
    runs-on: ubuntu-latest
    steps:
      - name: Analyze Error
        env:
          CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: |
          ERROR_TYPE="${{ inputs.error_type }}"
          
          # AI駆動エラー分析プロンプト
          ANALYSIS_PROMPT="image-generation-multiモジュールのエラー分析と修正。
          
          エラータイプ: $ERROR_TYPE
          
          参考資料:
          - ai-memory/error-prevention-checklist.md
          - ai-memory/debugging-lessons-from-agents.md
          - ai-memory/image-generation-multi-error-analysis.md
          
          修正手順:
          1. 根本原因の特定
          2. 修正コードの生成
          3. テストケースの作成
          4. 段階的検証"
          
          npx @anthropic-ai/claude-code \
            --allowedTools "Read,Write,Edit,Bash,Grep,Glob" \
            --max-turns 50 \
            --verbose \
            -p "$ANALYSIS_PROMPT"
            
      - name: Apply Fix and Test
        run: |
          # 修正適用後の自動テスト
          echo "修正適用とテスト実行"
```

## 📊 学習データとしての価値

### 失敗パターンの記録
```yaml
failure_pattern_1:
  module: "image-generation-multi"
  error: "Claude Code CLI execution failed"
  root_cause: "依存モジュール失敗による連鎖的エラー"
  solution: "単体テスト環境での検証"
  
failure_pattern_2:
  module: "upstream dependencies"  
  error: "File generation failure"
  root_cause: "music-planning段階の失敗"
  solution: "依存関係の分離・段階的テスト"
```

### Auto Development V2への改善提案
```yaml
v2_improvements:
  1: "依存関係分析の強化"
  2: "単体テスト自動生成"
  3: "エラーハンドリングの改善"
  4: "段階的統合テストの実装"
```

## 🔄 次のアクション

### 現在実行中テストの監視
1. **16548131691の結果確認**
2. **エラー詳細の特定**
3. **修正方針の決定**

### 修正実装
1. **単体テスト用ワークフロー作成**
2. **MCP設定の検証・修正**
3. **Claude Code CLI実行の改善**

### フィードバックループ
1. **Auto Development V2への学習データ提供**
2. **エラー予防チェックリストの更新**
3. **次回生成時の品質向上**

---

**この分析により、image-generation-multiの問題を体系的に解決し、Auto Development V2の改善につなげることができます。**