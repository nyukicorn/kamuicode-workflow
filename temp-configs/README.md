# 一時設定ファイル

このディレクトリには実験用の一時的な設定ファイルが保存されます。

## 用途

### 実験用 MCP 設定
- 新しい MCP サーバーのテスト設定
- 既存設定を壊さない一時的な設定
- 実験終了後は自動削除

### 設定ファイルの種類

#### experimental-mcp.json
```json
{
  "mcpServers": {
    "experimental-threejs": {
      "type": "http",
      "url": "http://localhost:3000/threejs",
      "status": "testing",
      "created": "2025-01-17T12:00:00Z"
    }
  }
}
```

#### mcp-test-config.json
```json
{
  "extends": "../.claude/mcp-kamuicode.json",
  "mcpServers": {
    "temp-server": {
      "type": "http",
      "url": "http://localhost:3001/test",
      "timeout": 30000
    }
  }
}
```

## 自動管理

### 作成
- 実験開始時に自動生成
- 既存設定との衝突回避
- 一意な名前での保存

### 削除
- 実験終了後 24 時間で自動削除
- 成功した設定は保持オプション
- 手動削除も可能

## 注意事項

- このディレクトリのファイルは一時的なものです
- 長期的な設定は `.claude/` ディレクトリに移動してください
- 実験中にのみ使用し、本番環境では使用しないでください
- 機密情報は含めないでください

## 設定の昇格

実験が成功し、継続的に使用したい場合：

1. `temp-configs/` から設定をコピー
2. `.claude/mcp-kamuicode.json` に統合
3. 実験用設定を削除
4. 本番ワークフローで使用開始