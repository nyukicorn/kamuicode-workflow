# YAML Syntax Fix Requirements

## 概要
オーケストレーションワークフロー `.github/workflows/create-music-video-orchestrated-improved.yml` のYAML構文エラーを修正する。

## エラーの詳細
- **場所**: 67行目 `MUSIC_CONCEPT="${{ inputs.music_concept }}"`
- **エラー**: `concept:: command not found`
- **原因**: YAML構文の引用符の問題

## 修正要件

### 1. 問題の特定と修正
- 67行目のYAML構文エラーを修正
- 適切な引用符の使用を確保
- Bashスクリプト内での変数代入の正確性を保証

### 2. 保護すべきファイル
- **ポリコムチームの最新変更を保護**
- 特に `polycam-mcp-server/` ディレクトリ配下のファイル
- `trellis-3d-*` 関連のファイル
- 最新のThree.js experienceファイル

### 3. 修正範囲
- `.github/workflows/create-music-video-orchestrated-improved.yml` のみ
- 他のワークフローファイルは変更しない
- 既存の機能を維持

### 4. テスト要件
- YAML構文が正しいことを確認
- ワークフロー実行時にエラーが発生しないこと
- 既存の音楽ビデオ生成機能が正常に動作すること

### 5. 成果物
- 修正済みの `.github/workflows/create-music-video-orchestrated-improved.yml`
- YAML構文エラーの解決
- ポリコムチームの変更を保護した状態

## 注意事項
- ポリコムチームが最近リリースを行ったため、それらの変更を上書きしないよう注意
- 最小限の変更で問題を解決する
- 既存のワークフロー機能を損なわないようにする