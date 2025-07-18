# 360° Panorama + Music + 3JS Workflow

360度パノラマ画像と音楽を組み合わせたインタラクティブな3JS環境を生成するワークフロー

## 🌐 概要

このGitHub Actionsワークフローは、360度パノラマ画像と音楽を組み合わせて、インタラクティブな3D環境を自動生成します。

### 🎯 生成フロー

1. **360°パノラマ画像生成** - Imagen4 Ultraで360度パノラマ画像を生成
2. **音楽生成** - Google Lyriaで30-40秒の音楽を生成
3. **3JS環境構築** - Three.jsを使用してパノラマ画像+音楽の統合環境を構築
4. **HTMLパッケージ生成** - スタンドアロンで動作するHTMLファイルを生成

### 🔧 技術スタック

- **パノラマ画像生成**: Imagen4 Ultra（equirectangular形式）
- **音楽生成**: Google Lyria（30-40秒、高品質）
- **3D環境**: Three.js（パノラマ表示+音楽統合）
- **出力**: HTMLファイル+必要なアセット
- **AI統合**: Claude Code SDK + kamuicode MCP

## 🚀 使用方法

### 手動実行

1. リポジトリの**Actions**タブに移動
2. **Create 360° Panorama 3JS Experience**ワークフローを選択
3. **Run workflow**ボタンをクリック
4. パノラマシーンを入力（例: "桜満開の京都庭園、夕方の暖かい光"）
5. 音楽スタイルを入力（例: "穏やかなアンビエント音楽"）
6. **Run workflow**を実行

## 📁 出力構造

```
[シーン名]-[タイムスタンプ]/
├── panorama/
│   ├── generated-panorama.jpg      # 360度パノラマ画像
│   └── panorama-url.txt           # 画像ファイルのURL
├── music/
│   ├── generated-music.wav        # 生成された音楽
│   └── music-url.txt             # 音楽ファイルのURL
├── 3js-experience/
│   ├── index.html                # メインのHTMLファイル
│   ├── assets/
│   │   ├── panorama.jpg          # パノラマ画像
│   │   └── music.wav             # 音楽ファイル
│   └── js/
│       └── three.min.js          # Three.jsライブラリ
├── planning/
│   ├── panorama-strategy.md      # パノラマ戦略
│   └── music-strategy.md         # 音楽戦略
└── analysis/
    └── scene-analysis.md         # シーン分析結果
```

## 🔧 セットアップ要件

### 必要なSecrets

```yaml
ANTHROPIC_API_KEY: # Claude API Key
PAT_TOKEN: # GitHub Personal Access Token
```

### 必要なファイル

```
.claude/
└── mcp-kamuicode.json    # kamuicode MCP設定
```

### 権限設定

```yaml
permissions:
  contents: write
  pull-requests: write
  actions: read
```

## 🌅 パノラマシーン例

### 🏞️ 自然風景
```
"高原の朝日、雲海の上の山々、静寂な空気感"
"深い森の中、木漏れ日が差し込む神秘的な空間"
```

### 🏛️ 建築・都市
```
"モダンな美術館の中庭、幾何学的な建築美"
"夜のサイバーパンク都市、ネオンライトの世界"
```

### 🌊 海・水辺
```
"透明度の高い海底、カラフルな珊瑚礁の世界"
"夕暮れの海岸、波の音が聞こえる静寂"
```

## 🎵 音楽スタイル例

### 🎼 アンビエント系
```
"穏やかなアンビエント音楽、自然の音を含む"
"瞑想的な音楽、深いリラクゼーション"
```

### 🎹 クラシック系
```
"ピアノソロ、叙情的で美しいメロディー"
"弦楽四重奏、上品で落ち着いた雰囲気"
```

### 🎧 エレクトロニック系
```
"エレクトロニック、未来的で神秘的"
"チルアウト、都市的でクールな感じ"
```

## 🤖 技術的詳細

### AI Agent構成
- **パノラマ計画Agent**: シーン分析と戦略立案
- **パノラマ生成Agent**: Imagen4 Ultra実行
- **音楽生成Agent**: Google Lyria実行
- **3JS統合Agent**: Three.js環境構築
- **パッケージ生成Agent**: HTML+アセットの統合

### 3JS機能
- 360度パノラマ表示
- マウス/タッチでの視点操作
- 自動音楽再生
- フルスクリーン対応
- レスポンシブデザイン

## 📄 ライセンス

MIT License

## 👥 貢献

Issues、Pull Requests大歓迎です！

---

🌐 **AI-generated 360° Panorama 3JS Experience** - Powered by [Claude Code SDK](https://github.com/anthropics/claude-code) & [kamuicode MCP](https://www.kamui.ai/ja)