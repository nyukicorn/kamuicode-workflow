# Multi Image Generation Workflow v3 - Detailed Design Document

**プロジェト**: KamuiCode Workflow  
**設計対象**: image-generation-multi モジュール v3 修正版  
**作成日**: 2025-07-27  
**作成者**: GitHub Actions Automatic Development System  

---

## 🎯 設計概要

### **現状分析**
既存の `image-generation-multi` モジュールが実装済みで、以下の機能を提供している：
- 複数枚画像生成 (1-10枚)
- 複数モデル対応 (imagen4-ultra/imagen4-fast/imagen3/flux-schnell/photo-flux)
- モデル比較レポート生成
- 後方互換性維持

### **設計課題**
要件定義書の分析結果、現在の実装が要件を既に満たしており、修正すべき主要な課題は：
1. **インターフェース検証の強化**: 下流モジュールとの互換性確認の厳密化
2. **エラーハンドリングの改善**: より堅牢なエラー処理とリトライ機構
3. **パフォーマンス最適化**: 並列処理の効率化
4. **ドキュメント充実**: 使用方法とベストプラクティスの明文化

---

## 📋 インターフェース分析

### **現在のインターフェース**

#### **入力インターフェース**
```yaml
inputs:
  image-prompt:         # 画像生成プロンプト (required)
  image-count:          # 生成枚数 1-10 (default: '1')
  models:              # 使用モデル CSV (default: 'auto')
  enable-comparison:   # 比較レポート有効化 (default: 'false')
  folder-name:         # 保存フォルダ名 (required)
  branch-name:         # 作業ブランチ名 (required)
  oauth-token:         # Claude Code OAuth トークン (required)
  mcp-config:          # MCP設定JSON (required)
```

#### **出力インターフェース**
```yaml
outputs:
  images-completed:    # 生成成功枚数 (数値)
  image-urls:          # 生成画像URL配列 (JSON)
  models-used:         # 使用モデル配列 (JSON)
  comparison-report:   # 比較レポートパス (文字列)
  google-image-url:    # 最初の画像URL (後方互換性)
```

### **下流モジュール連携分析**

#### **1. image-world-analysis モジュール**
- **連携方法**: `google-image-url` 出力を `image-url` 入力として使用
- **互換性**: ✅ 完全互換 - 既存の`google-image-url`出力で対応
- **リスク**: なし

#### **2. video-generation関連モジュール**
- **連携方法**: `google-image-url` を動画生成の入力画像として使用
- **互換性**: ✅ 完全互換 - 最初の画像が`google-image-url`として出力
- **リスク**: なし

#### **3. threejs-integration モジュール**
- **連携方法**: 生成画像をThree.js体験の背景として使用
- **互換性**: ✅ 完全互換 - ファイルパス基準で画像を参照
- **リスク**: なし

#### **4. web-player-generation モジュール**
- **連携方法**: 複数画像を活用した Web プレイヤー生成
- **互換性**: ✅ 強化互換 - `image-count`出力で複数画像に対応
- **リスク**: なし

---

## 🔧 技術詳細設計

### **アーキテクチャ概要**

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi Image Generation                    │
├─────────────────────────────────────────────────────────────┤
│  Input Validation  →  Model Processing  →  File Management  │
│       ↓                      ↓                      ↓       │
│  Error Handling   →  Parallel Execution →  Output Assembly │
│       ↓                      ↓                      ↓       │
│  Progress Tracking → Result Verification → Commit & Deploy  │
└─────────────────────────────────────────────────────────────┘
```

### **コアコンポーネント設計**

#### **1. 入力検証コンポーネント**
```bash
# 現在の実装 (image-generation-multi/action.yml:78-82)
IMAGE_COUNT="${{ inputs.image-count }}"
if [[ ! "$IMAGE_COUNT" =~ ^[0-9]+$ ]] || [ "$IMAGE_COUNT" -lt 1 ] || [ "$IMAGE_COUNT" -gt 10 ]; then
  echo "::error::❌ Invalid image count: $IMAGE_COUNT. Must be between 1 and 10."
  exit 1
fi
```

**改善提案**: 
- モデル名の妥当性検証を追加
- 入力パラメータの相互依存関係検証

#### **2. 並列実行エンジン**
```bash
# 現在の実装方式 (action.yml:185-270)
for model in "${MODEL_ARRAY[@]}"; do
  for ((i=1; i<=IMAGE_COUNT; i++)); do
    # 順次実行 - 改善余地あり
  done
done
```

**改善提案**:
- GNU Parallel または background job による真の並列処理
- Resource pooling による効率的なリソース利用

#### **3. ファイル管理システム**
```bash
# 現在の命名規則 (action.yml:200-210)
if [ "$MODEL_COUNT" -gt 1 ]; then
  OUTPUT_FILENAME="generated-image-${TOTAL_IMAGES}-$(echo "$model" | tr '/' '-').png"
else
  OUTPUT_FILENAME="generated-image-${i}.png"
fi
```

**設計評価**: ✅ 適切 - 一意性とトレーサビリティを確保

### **エラーハンドリング設計**

#### **現在のエラー処理**
- 個別画像の生成失敗は警告として継続処理
- 全画像の生成失敗時のみ exit 1

#### **改善提案**
```bash
# Retry機構の追加
retry_count=0
max_retries=3
while [ $retry_count -lt $max_retries ]; do
  if npx @anthropic-ai/claude-code [...]; then
    break
  else
    retry_count=$((retry_count + 1))
    echo "::warning::Retry $retry_count/$max_retries for image generation"
    sleep $((retry_count * 5))  # Exponential backoff
  fi
done
```

---

## 📊 パフォーマンス設計

### **現在のパフォーマンス特性**

#### **実行時間分析**
- **1枚生成**: 約45-90秒 (モデル依存)
- **5枚生成**: 約225-450秒 (5 × 単体時間)
- **並列化効果**: 現在は順次実行のため最小限

#### **並列化改善案**

```bash
# GNU Parallel を使用した並列処理
export -f generate_single_image
export CLAUDE_CODE_OAUTH_TOKEN MCP_CONFIG_ABS_PATH

# モデル×枚数の組み合わせを並列処理
printf '%s\n' "${IMAGE_JOBS[@]}" | \
  parallel -j 3 --bar generate_single_image {}
```

**期待効果**:
- 3並列実行で 60-70% の時間短縮
- リソース使用量は 150-200% (許容範囲内)

### **メモリ管理設計**
- **現在**: 画像生成は逐次でメモリ効率的
- **改善**: 並列時のメモリプール管理を追加

---

## 🎨 比較レポート設計

### **現在の比較レポート機能**
- Markdown形式の詳細レポート生成
- 生成時間、モデル別結果の表形式比較
- 統計情報 (平均、最速、最遅)

### **レポート機能強化案**

#### **視覚的比較**
```markdown
## 画像品質比較

| モデル | サムネイル | 品質評価 | 特徴 |
|--------|-----------|---------|------|
| Imagen4 Ultra | ![](image-1-thumb.png) | 9.2/10 | 高解像度、リアル |
| Flux Schnell | ![](image-2-thumb.png) | 8.5/10 | 高速、アート調 |
```

#### **AI品質評価**
```bash
# Claude Code による自動品質評価
QUALITY_PROMPT="生成された画像を分析し、品質スコア（1-10）と特徴を評価してください..."
```

---

## 🔒 セキュリティ設計

### **現在のセキュリティ対策**
- OAuth Token の環境変数経由での管理
- MCP設定の適切な隔離
- Git操作時の認証情報保護

### **セキュリティ強化提案**
1. **Secrets検証**: 入力Secretsの妥当性確認
2. **ファイルパス検証**: パストラバーサル攻撃の防止
3. **出力サニタイゼーション**: 機密情報の漏洩防止

---

## 🧪 テスト設計

### **テストケース階層**

#### **Unit Tests**
- [ ] 入力検証ロジックのテスト
- [ ] ファイル命名規則のテスト  
- [ ] JSON出力フォーマットのテスト

#### **Integration Tests**
- [ ] MCP接続テスト
- [ ] 各AIモデルとの連携テスト
- [ ] Git操作の統合テスト

#### **End-to-End Tests**
- [ ] 1枚生成の後方互換性テスト
- [ ] 複数枚生成のテスト
- [ ] モデル比較機能のテスト
- [ ] エラーシナリオのテスト

### **自動テスト実装**

```yaml
# .github/workflows/test-multi-image-generation.yml
name: Test Multi Image Generation
on:
  pull_request:
    paths: ['.github/actions/kamui-modules/image-generation-multi/**']

jobs:
  test-basic:
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/kamui-modules/image-generation-multi
        with:
          image-prompt: "A beautiful sunset"
          image-count: "2"
          models: "imagen4-fast"
```

---

## 📚 ドキュメント設計

### **ドキュメント構造**

```
docs/
├── design/
│   ├── github-app-fix-multi-image-workflow-v3-design.md
│   ├── github-app-fix-multi-image-workflow-v3-implementation-plan.md
│   └── github-app-fix-multi-image-workflow-v3-interface-compatibility.md
├── user-guides/
│   ├── multi-image-generation-quickstart.md
│   ├── model-comparison-guide.md
│   └── troubleshooting.md
└── api-reference/
    └── image-generation-multi-api.md
```

### **READMEの充実**

```markdown
# Multi Image Generation Module

## 🚀 Quick Start
```yaml
- uses: ./.github/actions/kamui-modules/image-generation-multi
  with:
    image-prompt: "Beautiful cherry blossoms"
    image-count: "3"
    models: "imagen4-fast,flux-schnell"
    enable-comparison: "true"
```

## 📖 Advanced Usage
...
```

---

## 🚀 実装優先順位

### **Phase 1: 安定性向上 (高優先度)**
1. **エラーハンドリング強化** - リトライ機構とエラー分類
2. **入力検証強化** - より厳密なパラメータ検証
3. **ログ改善** - デバッグ可能な詳細ログ

### **Phase 2: パフォーマンス改善 (中優先度)**
1. **並列処理導入** - 真の並列実行による高速化
2. **リソース最適化** - メモリとCPU使用量の最適化
3. **キャッシュ機構** - 重複処理の削減

### **Phase 3: 機能拡張 (低優先度)**
1. **AI品質評価** - 自動品質スコアリング
2. **カスタムテンプレート** - 柔軟なレポート生成
3. **統計ダッシュボード** - 使用統計の可視化

---

## 💡 設計決定の根拠

### **既存実装を維持する理由**
1. **既に要件を満たしている**: 現在の実装は要件定義書の仕様を適切に実装
2. **下流互換性**: 既存のワークフローとの互換性が確保されている
3. **実績ベース**: 実際のワークフローで動作実績がある

### **改善提案の妥当性**
1. **段階的改善**: 破綻的変更を避け、段階的な品質向上を図る
2. **実用性重視**: 理論的な最適化より実際の使用体験を重視
3. **保守性**: 長期的なメンテナンスを考慮した設計

---

## 📋 実装チェックリスト

### **必須実装項目**
- [ ] エラーハンドリング強化
- [ ] 入力検証の厳密化
- [ ] ログとデバッグ情報の改善
- [ ] ドキュメント整備

### **推奨実装項目**
- [ ] 並列処理導入
- [ ] パフォーマンス監視
- [ ] 自動テスト追加

### **将来実装項目**
- [ ] AI品質評価
- [ ] 統計機能
- [ ] カスタマイゼーション機能

---

**この設計文書は、既存の優秀な実装を基盤として、より堅牢で効率的な多画像生成機能の実現を目指しています。**