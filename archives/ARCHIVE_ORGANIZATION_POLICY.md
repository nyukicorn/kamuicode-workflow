# 📁 Archive Organization Policy

## 🎯 目的

kamuicode-workflow リポジトリの実験・プロジェクトフォルダを体系的に整理し、将来的な混乱を防ぐためのガイドライン。

## 📂 Archive構造

```
archives/
├── ARCHIVE_ORGANIZATION_POLICY.md (このファイル)
├── pointcloud/
│   ├── 2025-07-23/
│   ├── 2025-07-24/
│   └── 2025-07-27/
├── music-video/
│   ├── 2025-07-21/
│   └── 2025-07-22/
├── threejs-experience/
│   ├── 2025-07-19/
│   └── 2025-07-20/
├── trellis-3d/
│   └── 2025-07-xx/
└── integration-test/
    └── 2025-07-26/
```

## 🔄 整理ルール

### 1. プロジェクト分類

- **pointcloud**: `immersive-pointcloud-*`
- **music-video**: `music-video-*`
- **threejs-experience**: `threejs-experience-*`
- **trellis-3d**: `trellis-3d-*`
- **integration-test**: テスト・実験用

### 2. 各チーム責任範囲

- **Point Cloud チーム**: `pointcloud/` フォルダ
- **Music Video チーム**: `music-video/` フォルダ  
- **Three.js チーム**: `threejs-experience/` フォルダ
- **3D Generation チーム**: `trellis-3d/` フォルダ

### 3. 移動手順

1. **現在地確認**: 散乱フォルダの現在位置を特定
2. **日付別整理**: フォルダ名から日付抽出 → `archives/[project]/[date]/`
3. **GitHub Actions更新**: 出力先を `archives/[project]/latest/` に変更
4. **検証**: 新しい実行で正しい場所に出力されることを確認

### 4. 命名規則

- **アーカイブ先**: `archives/[project-type]/[YYYY-MM-DD]/[original-folder-name]/`
- **最新用**: `archives/[project-type]/latest/[timestamp-folder-name]/`

## ⚠️ 注意事項

- **各チーム責任**: 自分のプロジェクトタイプのみ整理
- **GitHub Actions更新必須**: 出力先変更を忘れずに
- **AI検索考慮**: フォルダ構造はAI検索に最適化済み

## 🔍 散乱フォルダの原因と対策

### 判明した原因
1. **docs/フォルダ散乱**: 複数のGitHub Actionsが `DOCS_DIR="docs/$FOLDER_NAME"` で出力
   - `threejs-3d-integration/action.yml:130`
   - `web-player-generation/action.yml:230` 
   - `threejs-integration/action.yml:96,207`

2. **ルート直下散乱**: 異なるActionsが異なる出力先を使用
   - 一部は `docs/` 配下に出力
   - 一部はリポジトリ直下に出力

### 対策
- **各チーム**: 自分のActionファイルで出力先を `archives/[project-type]/latest/` に統一
- **GitHub Pages**: `docs/` 以外のアプローチ（GitHub Actions Pages deploy）を使用

## 🤖 AI検索最適化

この構造により以下が実現される：
- プロジェクトタイプでの高速検索
- 日付範囲での絞り込み
- 最新実験への直接アクセス

---

**作成日**: 2025-07-27  
**対象**: 全チーム共通ガイドライン  
**次回更新**: 各チーム整理完了後