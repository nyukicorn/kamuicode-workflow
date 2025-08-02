# 🎵 CLI操作デモ - Interactive Music Editor

## 🚀 セットアップ

1. **MCPサーバー起動**
```bash
cd mcp-server
pip install -r requirements.txt
python server.py
```

2. **Webインターフェース開く**
```bash
open web-interface/index.html
# または
python -m http.server 8000 --directory web-interface
```

## 🎯 CLI操作例

### 基本的な音楽作成
```bash
# Claude Codeから
> create_music_from_prompt("ピアノで優しい曲を作って")
# → ブラウザにピアノトラック + ヒートマップが表示される

> create_music_from_prompt("ロマンチックなバイオリンとピアノ")
# → ブラウザに2トラック表示

> create_music_from_prompt("激しいドラマチックな音楽")  
# → 音量大きめの楽曲が生成される
```

### 音量調整
```bash
> adjust_volume_cli("ピアノをもっと大きくして")
# → ブラウザでピアノトラックの音量が上がる

> adjust_volume_cli("バイオリンを小さくして")
# → バイオリンの音量が下がる

> adjust_volume_cli("全体的に音を下げて")
# → 全トラックの音量が下がる
```

### 再生制御
```bash
> start_playback_cli()
# → ブラウザで音楽再生開始、タイムラインマーカー動作

> start_playback_cli(["piano", "violin"])
# → 特定トラックのみ再生
```

## 🌐 WebSocket連携の仕組み

```
Claude Code (CLI)
    ↓ MCP Tool呼び出し
MCP Server (Python)
    ↓ WebSocket送信
Web Browser (JavaScript)
    ↓ 画面更新
ユーザーがビジュアル確認
```

## ✅ 確認ポイント

1. **WebSocket接続**
   - ブラウザのコンソールで「🌐 WebSocket connected」表示
   - 右上に「🌐 Connected to real-time server!」通知

2. **CLI操作の反映**
   - CLIコマンド実行後、即座にブラウザ更新
   - 「✅ CLI: [コマンド] → [結果]」通知表示

3. **音楽再生**
   - ヒートマップ表示
   - タイムラインマーカー同期
   - 実際の音声再生

## 🎨 カスタマイズ例

```python
# cli_tools.pyに追加
@self.mcp_server.app.tool()
def add_echo_effect(track_name: str, delay: float = 0.3):
    """エコー効果を追加"""
    # 実装...
```

```bash
# Claude Codeから使用
> add_echo_effect("piano", 0.5)
```

これで**CLI操作 → リアルタイムWeb表示**の完全な連携が実現されています！