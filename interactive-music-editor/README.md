# 🎵 Interactive Music Editor

**次世代音楽創作プラットフォーム - モジュラー・クリエイティブ・ツールキット**

自然言語指示からリアルタイムライブコーディングまで、革新的な音楽制作体験を提供する実験的プロジェクトです。

## 🌟 プロジェクトビジョン

### 🎯 核心コンセプト
- **自然言語 → コード変換**: "ロマンチックな雰囲気に" → `track('violin').emotion('romantic')`
- **リアルタイムヒートマップ**: 楽器×時間軸のビジュアライゼーション  
- **双方向連携**: 音楽 ⇔ 3D ⇔ アート ⇔ 動画
- **モジュラー設計**: 機能単位での拡張・統合

### 🎨 革新的機能

#### 🔥 **ヒートマップビジュアル**
```
🎻 Violin │━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│ 連続音（線）
🎹 Piano  │████░░░░████░░░░████░░░░████│ 断続音（ブロック）
🥁 Drums  │▌ ▌ ▌ ▌ ▌ ▌ ▌ ▌ ▌ ▌ ▌ ▌ ▌ ▌│ パルス音（短バー）
          └─────────────────────────┘
           色の濃さ = 音量 | 色相 = 音高
```

#### 🤖 **自然言語音楽制作**
```javascript
// 自然言語入力例
"2分のところでピアノをもっと小さく" 
    ↓ AI変換
track('piano').at(120).volume(0.3)
    ↓ 実行・可視化
ヒートマップ更新 + リアルタイム演奏
```

#### 🎼 **ライブコーディング統合**
```javascript
// JavaScriptベース音楽DSL
pick("c#7 a#9 d#7").struct("x-x-").mux(supersaw)
  .gain(0.5).hpf(100).room(0.3)
  ._heatmap({ track: 'lead', width: 800 })
```

## 🏗️ プロジェクト構造

```
📂 interactive-music-editor/
├── 📄 README.md               # このファイル
├── 📄 package.json            # 依存関係管理
├── 🗂️ mcp-server/             # Web Audio API MCPサーバー
│   ├── server.py             # FastMCP音楽サーバー
│   ├── requirements.txt      # Python依存関係
│   └── tools/                # 音楽生成・解析ツール
├── 🗂️ web-interface/          # Webアプリケーション
│   ├── index.html            # メインインターface
│   ├── editor/               # Monaco Editor統合
│   ├── visualizer/           # ヒートマップ・ビジュアル
│   └── audio-engine/         # Web Audio API
├── 🗂️ prototypes/             # 実験・プロトタイプ
│   ├── heatmap-test/         # ヒートマップ実験
│   ├── dsl-parser/           # DSL構文解析実験
│   └── bridge-experiments/   # 音楽⇔ビジュアル連携実験
└── 🗂️ docs/                   # ドキュメント
    ├── architecture.md       # システム設計
    ├── dsl-specification.md  # DSL言語仕様
    └── api-reference.md      # API リファレンス
```

## 🚀 開発フェーズ

### 📍 **Phase 1: ローカル開発** (現在)
- ✅ プロジェクト構造設計
- 🔄 MCPサーバー構築
- 🔄 基本ヒートマップ実装
- 🔄 音楽DSL設計

### 📦 **Phase 2: モジュール化**
- kamuicode-workflow/kamui-modulesに移植
- GitHub Actions統合
- 独立モジュールパッケージ化

### 🌟 **Phase 3: エコシステム統合**
- 既存Three.js・画像生成モジュールとの連携
- 統合ワークフロー作成
- 自動音楽ビデオ生成

### 🔮 **Phase 4: 配布・コミュニティ**
- NPMパッケージ化 `@kamuicode/web-audio-mcp`
- オープンソース化
- SNS配信・コミュニティ形成

## 🛠️ 技術スタック

### **コア技術**
- **Web Audio API**: リアルタイム音響処理
- **FastMCP**: Claude Code統合
- **Monaco Editor**: ライブコーディング環境
- **Canvas/WebGL**: ビジュアライゼーション

### **統合技術**
- **Three.js**: 3D音楽体験
- **GitHub Actions**: 自動化パイプライン
- **MCPエコシステム**: 他ツールとの連携

## 🎭 使用例・ワークフロー

### 🎵 **基本的な音楽制作**
```bash
# 1. 自然言語で指示
"Create a gentle piano melody with strings"

# 2. AI変換・コード生成
track('piano').chord(['C4','E4','G4']).timing(4)
track('strings').harmony().volume(0.6)

# 3. リアルタイム実行・ビジュアル表示
ヒートマップ + ライブ演奏 + 3D反応
```

### 🎨 **クリエイティブ統合**
```bash
# 音楽から3D生成
music.beat → scene.lights.flash
music.frequency → mesh.morphTargets

# 3Dから音楽制御  
mouse.position → filter.cutoff
object.rotation → reverb.size
```

## 🎯 開発指針

### **試行錯誤 vs 記録**
- **MCPエージェント**: 実験・プロトタイプ・试行錯誤
- **GitHub Actions**: 動作確認・記録・自動化

### **モジュラー開発**
- 機能は独立モジュールとして開発
- 段階的統合・組み合わせ自由
- 将来の拡張・配布を考慮

### **ユーザー体験重視**
- 直感的な自然言語インターfェース
- リアルタイム・インタラクティブ
- 初心者からプロまで対応

## 📱 SNS配信戦略

- **実験過程**: 録画 → X(Twitter)配信
- **作品紹介**: ショート動画での魅力訴求
- **技術解説**: 開発過程の透明性

## 🤝 コントリビューション

このプロジェクトは実験的・探索的な性質を持ちます。
新しいアイデア・機能追加・改良提案を歓迎します。

## 📄 ライセンス

MIT License - 自由に使用・改変・配布可能

---

**🎶 "Where code meets creativity, music comes alive!" 🎶**

*KamuiCode Creative Platform - Interactive Music Editor*