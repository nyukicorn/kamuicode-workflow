# KamuiCode Workflow Orchestrator

AI駆動のワークフロー自動生成システム。自然言語の指示から最適なGitHub Actionsワークフローを動的に生成・実行します。

## 🎯 概要

このオーケストレーターは、自然言語コマンドを解析して既存のモジュールを柔軟に組み合わせ、カスタムワークフローを自動生成します。

### 特徴
- **自然言語解析**: 日本語の指示を構造化データに変換
- **動的モジュール組み合わせ**: 依存関係を自動解決
- **GitHub Actions統合**: 実行可能なYAMLワークフローを生成
- **拡張可能設計**: 新しいモジュールやプロバイダーに対応

## 🚀 クイックスタート

### インストール
```bash
cd orchestrator
npm install
```

### 基本的な使用方法
```bash
# 単一画像生成
node src/orchestrator.js "Imagen4で美しい桜の画像を1つ作って"

# 音楽ビデオ生成
node src/orchestrator.js "音楽付きのミュージックビデオを作成"

# 複合ワークフロー
node src/orchestrator.js "Imagen4で画像1つ、Hailuoで5秒動画1つ作って"

# デバッグ情報表示
node src/orchestrator.js --debug
```

## 📋 対応コマンド例

### 画像生成
- `"Imagen4で美しい風景画像を生成"`
- `"imagen4で画像1つ作って"`
- `"Imagen4を使って桜の画像を1つ生成して"`

### 音楽生成
- `"リラックスできる音楽を生成"`
- `"Google Lyriaで30秒の音楽"`
- `"音楽付きのミュージックビデオを作成"`

### 動画生成
- `"Hailuoで5秒動画を生成"`
- `"動画1本作って"`
- `"音楽と動画を組み合わせて"`

### 複合ワークフロー
- `"Imagen4で画像1つ、Hailuoで5秒動画1つ作って"`
- `"音楽とのミュージックビデオを作成"`
- `"Fluxで2つ、Imagen4で1つ画像作って、動画3本作成"`

## 🏗️ アーキテクチャ

### ディレクトリ構造
```
orchestrator/
├── src/
│   └── orchestrator.js          # メインエンジン
├── config/
│   ├── modules.json             # モジュール定義
│   └── templates.json           # ワークフローテンプレート
├── examples/
│   └── test-commands.txt        # テストコマンド例
└── README.md
```

### 処理フロー
1. **自然言語解析**: コマンドを構造化データに変換
2. **モジュール選択**: 必要なモジュールを特定
3. **依存関係解決**: 依存モジュールを自動追加
4. **ワークフロー生成**: GitHub Actions YAMLを生成
5. **実行**: ワークフローファイルを保存

## 🔧 設定

### モジュール追加
`config/modules.json`に新しいモジュールを定義:

```json
{
  "modules": {
    "new-module": {
      "path": "./.github/actions/kamui-modules/new-module",
      "inputs": ["param1", "param2"],
      "outputs": ["output1"],
      "dependencies": ["setup-branch"],
      "category": "content",
      "description": "新しいモジュール"
    }
  }
}
```

### プロバイダー追加
新しいAI APIプロバイダーを追加:

```json
{
  "providers": {
    "new-ai": {
      "type": "image",
      "module": "new-image-generation",
      "description": "新しい画像生成AI"
    }
  }
}
```

## 📊 使用可能なモジュール

| モジュール | 機能 | プロバイダー |
|-----------|------|------------|
| setup-branch | ブランチ・フォルダ作成 | - |
| music-planning | 音楽ビデオ戦略策定 | - |
| image-generation | 画像生成 | Imagen4 |
| music-generation | 音楽生成 | Google Lyria |
| music-analysis | 音楽分析 | - |
| video-generation | 動画生成 | Hailuo-02 |
| video-adjustment | 動画プロンプト調整 | - |
| video-concatenation | 動画統合 | - |

## 🧪 テスト

### Phase 1: 単一モジュール
```bash
node src/orchestrator.js "Imagen4で画像1つ"
```

### Phase 2: 複数モジュール
```bash
node src/orchestrator.js "音楽付きのミュージックビデオ"
```

### Phase 3: 複雑な組み合わせ
```bash
node src/orchestrator.js "Imagen4で画像、Hailuoで動画、音楽付きで統合"
```

## 🔄 拡張予定

### 短期（1-2週間）
- [ ] Fluxプロバイダー対応
- [ ] Baiduプロバイダー対応
- [ ] リトライ機構追加

### 中期（1ヶ月）
- [ ] GitHub Actions API直接実行
- [ ] 実行状況監視
- [ ] 品質評価システム

### 長期（2-3ヶ月）
- [ ] Three.js統合
- [ ] カスタムMCP対応
- [ ] Web UI開発

## 🛠️ トラブルシューティング

### よくある問題

**Q: ワークフローが生成されない**
A: `--debug`オプションでモジュール読み込み状況を確認してください。

**Q: 依存関係エラー**
A: `config/modules.json`の依存関係定義を確認してください。

**Q: 自然言語が認識されない**
A: より具体的なプロバイダー名（Imagen4、Hailuo等）を含めて指定してください。

## 📄 ライセンス

MIT License

## 🤝 貢献

プルリクエストやIssueをお待ちしています。

---

🎭 **KamuiCode Workflow Orchestrator** - Powered by Claude Code SDK