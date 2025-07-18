# kamuicode Creative Workshop

Claude Code SDK と kamuicode MCP を活用したAI駆動クリエイティブ工房

## 🚨 重要：既存ワークフロー保護ルール

### 絶対に変更・削除してはいけないワークフロー
- `video-workflow-template/create-video-from-prompt.yml` - 画像→動画生成（実績あり）
- `music-video-workflow/create-music-video.yml` - 音楽→動画生成（実績あり）
- `.claude/mcp-kamuicode.json` - MCP設定（全ワークフローで使用）

### 新規ワークフロー追加時のルール
1. **新しいディレクトリを作成**して既存を分離
2. **既存ワークフローは絶対に触らない**
3. **テスト完了後**に正式運用開始

⚠️ **このルールを破ると既存の動作が停止する可能性があります**

## 概要

このリポジトリは、GitHub ActionsでClaude Code SDKとkamuicode MCPを使用してAIコンテンツを生成するクリエイティブ工房システムです。新しいAI技術の迅速な実験から高品質なアート作品の制作まで、包括的なクリエイティブフローを提供します。

## 🏭 クリエイティブ工房システム

### 🧪 Creative Test Lab（クリエイティブテスト工房）
**目的**: 新しいMCPやAI技術の迅速な実験と検証

**特徴**:
- 新MCP発見から24時間以内のテスト実行
- 失敗を恐れない実験環境  
- 自動結果記録とアーカイブ
- 気軽に試せる軽量設計

**使用場面**:
- 新しいMCPサーバーのテスト
- 技術的可能性の探索
- アイデアの検証
- 組み合わせ実験

### 🎨 Creative Art Studio（クリエイティブアート工房）
**目的**: 展示レベルの高品質アート作品制作

**特徴**:
- 詳細なビジョン分析
- 段階的品質向上プロセス
- 複数回の改善イテレーション
- 完成品としての仕上げ

**使用場面**:
- 本格的なアート作品制作
- ポートフォリオ用作品
- 展示用高品質作品
- 商用レベルの制作

### 📹 Music Video Workflow（既存）
**目的**: 音楽付きビデオの自動生成

**特徴**:
- 画像→音楽→動画の統合制作
- 30-40秒の完成動画
- 自動プルリクエスト作成

## 🔧 含まれるワークフロー

### 1. **Creative Test Lab** (`creative-test-lab.yml`)
新しいMCPの実験用ワークフロー

#### 主な機能:
- 自動MCP検出・インストール
- 実験内容の分析と実行
- 結果の自動パッケージング
- 実験履歴の記録

#### 実行例:
```yaml
experiment_description: "新しい音楽MCP + 画像で動画作成"
mcp_to_test: "new-music-generator"
output_type: "video"
```

### 2. **Creative Art Studio** (`creative-art-studio.yml`)
高品質アート作品制作用ワークフロー（開発中）

#### 計画された機能:
- 詳細ビジョン分析
- 段階的制作プロセス
- 品質向上イテレーション
- 最終作品の完成

#### 実行例:
```yaml
art_vision: "桜の季節の京都庭園で、着物女性が茶を点てる幻想的な映像作品..."
proven_mcps: "imagen4-fast,google-lyria,hailuo-02-pro"
quality_level: "exhibition"
```

### 3. **Create Music Video** (`create-music-video.yml`)
音楽ビデオ生成ワークフロー

#### 機能:
- 音楽コンセプトから動画生成
- 画像→音楽→動画の統合
- 自動ブランチ作成とPR

## 🚀 クイックスタート

### 1. 最初の実験を実行
```bash
# GitHub Actionsで "Creative Test Lab" を実行
experiment_description: "Imagen4で美しいバラ園の画像を生成"
mcp_to_test: "imagen4-fast"
output_type: "image"
```

### 2. 実験結果を確認
- `experiment-results/` ディレクトリで結果を確認
- Actionsの Artifacts からダウンロード可能
- 成功したら次の実験を計画

### 3. 組み合わせ実験
```bash
# 音楽と画像を組み合わせた実験
experiment_description: "バラ園画像 + クラシック音楽で動画作成"
output_type: "video"
```

### 4. アート作品制作（準備中）
実験で成功パターンを確立後、Creative Art Studio で本格制作

## 📁 ディレクトリ構造

```
kamuicode-workflow/
├── .github/workflows/
│   ├── creative-test-lab.yml       # 実験工房
│   ├── creative-art-studio.yml     # アート工房（開発中）
│   ├── create-music-video.yml      # 音楽ビデオ（既存）
│   └── update-experiment-index.yml # 実験インデックス更新
├── .claude/
│   ├── mcp-kamuicode.json          # MCP設定
│   └── mcp-experimental.json       # 実験用MCP設定
├── experiments/                    # 実験ログ
├── experiment-results/             # 実験結果アーカイブ
├── art-studio-works/              # アート作品（準備中）
├── temp-configs/                  # 一時設定
└── creative-outputs/              # 統合出力
```

## 🔧 必要な環境

### 必須要件
- GitHub Actions
- Claude Code SDK
- kamuicode MCP
- Anthropic API Key

### GitHub Secrets設定
```bash
CLAUDE_ACCESS_TOKEN=your_access_token
CLAUDE_REFRESH_TOKEN=your_refresh_token  
CLAUDE_EXPIRES_AT=your_expires_at
```

### MCP設定
`.claude/mcp-kamuicode.json` に利用可能なMCPサーバーを設定

## 🎯 使用方法

### Creative Test Lab での実験
1. **新MCP追加時**: JSON設定更新で自動検出
2. **手動実験**: GitHub Actionsで実行
3. **結果確認**: Artifacts ダウンロード
4. **次の実験**: 成功パターンを発展

### Creative Art Studio での制作
1. **十分な実験**: Test Lab で基礎確立
2. **詳細ビジョン**: 長文での作品構想
3. **段階的制作**: 複数イテレーション
4. **最終完成**: 展示レベルの品質

## 📊 実験追跡

### 自動記録
- 実験回数と成功率
- MCP使用頻度
- 出力タイプ別統計
- 実験履歴の詳細

### 手動確認
- `experiment-results/index.md` で全体確認
- 各実験の詳細レポート
- 成功パターンの分析

## 🔄 ワークフロー

```
新MCP発見 → 実験 → 評価 → 採用/不採用
    ↓
成功パターン蓄積 → アート制作 → 高品質作品
```

## ライセンス

MIT License

## 貢献

新しいワークフローテンプレートの追加やバグ修正のPRを歓迎します。

---

🤖 Powered by [Claude Code SDK](https://github.com/anthropics/claude-code) & [kamuicode MCP](https://www.kamui.ai/ja)