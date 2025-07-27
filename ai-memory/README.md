# AI Memory - 知識ベース

**Summary**: AI駆動開発システムの学習・参照用知識データベース  
**Purpose**: AIが開発時に参照する実践知識とパターンの蓄積  
**Usage**: 新機能開発、エラー解決、テンプレート生成時の参考資料

## 📚 知識の種類

### 🎯 基本構想・ビジョン
- `ai-driven-development-complete-vision.md` - AI駆動開発の完全構想
- `development-principles-and-decisions.md` - 開発原則と重要決定事項
- `orchestration-architecture.md` - システム全体設計

### 🔧 技術フレームワーク
- `unified-media-analysis-framework.md` - 統一メディア分析フレームワーク
- その他の再利用可能な技術基盤

### 📈 実証済みパターン
- `integration-lessons-from-practice.md` - 統合作業の実践知識
- `multimodal-integration-success.md` - マルチモーダル統合成功事例
- その他の成功パターン

### ⚠️ トラブルシューティング
- `error-prevention-checklist.md` - エラー予防チェックリスト
- `debugging-lessons-from-agents.md` - AIエージェントのデバッグ教訓
- `github-actions-troubleshooting.md` - GitHub Actions問題解決

## 📂 重要なパス情報

### 開発モジュール
- **Kamuiモジュール**: `/Users/nukuiyuki/Dev/kamuicode-workflow/.github/actions/kamui-modules/`
- **GitHub Actions**: `/Users/nukuiyuki/Dev/kamuicode-workflow/.github/actions/`

### ワークフロー
- **ワークフロー**: `/Users/nukuiyuki/Dev/kamuicode-workflow/.github/workflows/`
- **自動駆動ワークフロー**: `auto-` で始まるファイル群

### 実行可能ツール
- **orchestrator**: `/Users/nukuiyuki/Dev/kamuicode-workflow/orchestrator/`
- **その他ツール**: `/Users/nukuiyuki/Dev/kamuicode-workflow/tools/`

### 要件定義・仕様
- **要件定義書**: `/Users/nukuiyuki/Dev/kamuicode-workflow/docs/requirements/`
- **AI知識ベース**: `/Users/nukuiyuki/Dev/kamuicode-workflow/ai-memory/`

## 🤖 AI利用ガイド

### ファイル作成時の構造
```markdown
# ファイルタイトル

**Summary**: 一行での要約（検索用）
**Tags**: #tag1 #tag2 #tag3
**Related**: [関連ファイル名]
**AI Usage**: このファイルをAIがどう活用すべきか
**Date**: 作成・更新日
**Status**: draft/active/archived

## 内容...
```

### 検索・参照方法
1. **内容検索重視**: ファイル名より内容で検索
2. **タグ活用**: 関連知識の横断検索
3. **関連ファイル**: 知識の連鎖的参照
4. **要約確認**: Summary部分で内容を素早く把握

### 新規知識追加時
- 自然な名前で命名（カテゴリプレフィックス不要）
- 必須構造（Summary、Tags、Related、AI Usage）を含める
- 既存知識との関連性を明記

## 🔄 更新・メンテナンス

### 定期的な整理
- 古い情報のアーカイブ化
- 関連ファイルのリンク更新
- 重複知識の統合

### 品質保持
- 実践で証明された知識のみ保存
- 推測や仮説は明確に区別
- 失敗事例も価値ある学習データとして記録

---

*この知識ベースは、AI駆動開発システムの実現に向けた実践知識の集積です。AIが自律的に開発を進める際の重要な参考資料として活用してください。*