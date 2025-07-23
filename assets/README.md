# Assets Directory

このディレクトリには深度推定パイプライン用のテスト画像を配置します。

## ファイル構成
- `cover.jpg` - テスト用アルバムアート画像
- `depth.png` - MiDaSで生成された深度マップ  
- `pointcloud.ply` - 変換された点群ファイル

## 使用方法
1. `cover.jpg` に2D画像を配置
2. GitHub Actionsが自動で深度推定→点群変換→Web表示を実行