# N枚画像生成機能 要件定義書

**プロジェクト**: KamuiCode Workflow  
**対象モジュール**: image-generation → image-generation-multi  
**作成日**: 2025-07-22  
**作成者**: オーケストレーションチーム  

---

## 🎯 機能概要

現在の`image-generation`モジュールを拡張し、ユーザー指定枚数の画像を生成する機能を追加する。
複数のAIモデルを使用した比較生成にも対応する。

---

## 📋 現在の制限と拡張要件

### **現在の制限**
- 1回の実行で1枚の画像のみ生成
- 1つのモデルのみ使用
- モデル比較機能なし

### **拡張要件**
- **複数枚生成**: 1-10枚の画像を一度に生成
- **モデル比較**: 異なるAIモデルで同一プロンプトを実行
- **並列処理**: 効率的な生成時間の実現
- **結果比較**: 生成結果の自動比較レポート

---

## 🔧 技術仕様

### **新しい入力パラメータ**
```yaml
inputs:
  image-prompt: # 既存
    description: 'The image generation prompt'
    required: true
    
  image-count: # 新規
    description: 'Number of images to generate (1-10)'
    required: false
    default: '1'
    
  models: # 新規
    description: 'Comma-separated list of models to use'
    required: false
    default: 'auto'
    # 例: "imagen4-fast,flux-schnell,imagen3"
    
  enable-comparison: # 新規
    description: 'Enable model comparison mode'
    required: false
    default: 'false'
    
  # 既存パラメータは維持
  folder-name:
    required: true
  branch-name:
    required: true
  oauth-token:
    required: true
  mcp-config:
    required: true
```

### **新しい出力仕様**
```yaml
outputs:
  images-completed:
    description: 'Number of images successfully generated'
    
  image-urls:
    description: 'JSON array of generated image URLs'
    # 例: ["url1", "url2", "url3"]
    
  models-used:
    description: 'JSON array of models actually used'
    # 例: ["imagen4-fast", "flux-schnell"]
    
  comparison-report:
    description: 'Path to comparison report file (if enabled)'
    
  # 既存出力は1枚目の情報として維持
  google-image-url:
    description: 'First image URL (backward compatibility)'
```

---

## 📁 ファイル構造

### **生成ファイルの命名規則**
```
{folder-name}/images/
├── generated-image-1-imagen4-fast.png
├── generated-image-2-flux-schnell.png
├── generated-image-3-imagen3.png
├── comparison-report.md
└── image-urls.json
```

### **後方互換性**
- `generated-image.png` は1枚目の画像として生成維持
- 既存ワークフローは無修正で動作継続

---

## ⚡ 実行フロー

### **パターン1: 同一モデルでN枚生成**
```yaml
inputs:
  image-count: "3"
  models: "imagen4-fast"
  
処理:
  1. imagen4-fastで3回並列実行
  2. 各画像を異なるファイル名で保存
  3. URL配列を返却
```

### **パターン2: 複数モデル比較**
```yaml
inputs:
  image-count: "1" 
  models: "imagen4-fast,flux-schnell,imagen3"
  enable-comparison: "true"
  
処理:
  1. 同一プロンプトで3つのモデル実行
  2. 比較レポート自動生成
  3. 品質・スタイル比較分析
```

### **パターン3: 複数モデル × 複数枚**
```yaml
inputs:
  image-count: "2"
  models: "imagen4-fast,flux-schnell" 
  
処理:
  1. imagen4-fast で2枚
  2. flux-schnell で2枚
  3. 合計4枚の画像生成
```

---

## 🎨 比較レポート仕様

### **自動生成レポート内容**
```markdown
# 画像生成比較レポート

## 生成条件
- プロンプト: "{original-prompt}"
- 生成日時: 2025-07-22 15:30:00
- 使用モデル: imagen4-fast, flux-schnell, imagen3

## 結果一覧
| モデル | ファイル | 生成時間 | 品質評価 |
|--------|---------|---------|---------|
| imagen4-fast | image-1.png | 45秒 | 高品質 |
| flux-schnell | image-2.png | 23秒 | 高速 |
| imagen3 | image-3.png | 67秒 | 詳細 |

## AI分析コメント
{Claude Code SDKによる自動分析}
```

---

## 🚫 制約条件

### **技術制約**
- **最大枚数**: 10枚（GitHub Actions実行時間制限）
- **並列度**: 最大5並列（MCP レート制限考慮）
- **ファイルサイズ**: 1画像あたり50MB以下
- **実行時間**: 全体で15分以内

### **互換性制約**
- 既存の`image-generation`モジュール呼び出しは無修正で動作
- 出力フォーマットは既存ワークフローと互換性維持
- エラーハンドリングは既存パターンを踏襲

---

## 🧪 テストケース

### **基本テスト**
1. **1枚生成（後方互換性）**: 既存の動作と同一結果
2. **3枚生成**: 同一モデルで3枚の異なる画像
3. **モデル比較**: 3つのモデルで同一プロンプト実行

### **エラーテスト**
1. **不正な枚数**: 0枚、11枚以上での適切なエラー
2. **存在しないモデル**: 無効なモデル名での処理
3. **MCP エラー**: ネットワーク障害時の処理

### **パフォーマンステスト**
1. **並列処理効率**: 5枚生成が1枚×5回より高速
2. **メモリ使用量**: 大量画像生成時のリソース管理
3. **ファイル管理**: 同時書き込み時の競合回避

---

## 📊 成功指標

### **機能指標**
- ✅ 1-10枚の画像生成成功率 95%以上
- ✅ 比較レポート自動生成 100%
- ✅ 既存ワークフロー無修正動作 100%

### **パフォーマンス指標**
- ✅ 5枚並列生成が単体×5より30%高速
- ✅ メモリ使用量が単体生成の200%以内
- ✅ 全体実行時間15分以内

---

## 🎯 実装アプローチ

### **GitHub Actions自動実装の対象**
1. ✅ **action.yml構造の修正**: 新パラメータ追加
2. ✅ **並列実行ロジック**: matrix戦略の実装
3. ✅ **ファイル管理システム**: 命名規則・保存ロジック
4. ✅ **比較レポート生成**: テンプレート化された自動生成
5. ✅ **エラーハンドリング**: 既存パターンの拡張

### **人間の判断が必要な部分**
1. ⚠️ **UI/UX設計**: ユーザーが使いやすい入力方法
2. ⚠️ **品質評価ロジック**: 何をもって「良い画像」とするか
3. ⚠️ **リソース最適化**: 実際の負荷に応じた調整

---

## 🚀 次のステップ

この要件定義書を基に、GitHub Actions内のClaude Code SDKで以下を自動実行：

1. **設計書生成**: 技術的な実装詳細の設計
2. **action.yml実装**: 新機能の組み込み
3. **テスト実行**: 基本機能とエラーケースの検証
4. **ドキュメント生成**: 使用方法の説明書作成

---

## 📋 開発プロセス実験

この機能は「**開発プロセス自体のGitHub Actions移管**」の第1回実験として位置づけられています。

### **実験目標**
- ローカル対話型開発 → GitHub Actions自動開発への移行可能性検証
- Claude Code SDKによる要件定義書 → 実装の自動化
- 新しい開発パラダイムの確立

### **実験成功の指標**
- GitHub Actions内で完全自動実装が完了
- 生成されたコードが人間のレビュー基準を満たす
- 既存ワークフローとの互換性維持

**この要件定義書で十分な詳細が提供されていることを確認し、GitHub Actions自動実装フェーズに進む準備が整いました。**