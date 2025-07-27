# 📁 Pointcloud Experiments Organization Plan

## 🎯 **整理目標**

リポジトリ直下に散乱している大量の`immersive-pointcloud-*`フォルダを整理し、将来的な混乱を防ぐ。

## 📊 **現状分析**

### 発見された散乱フォルダ
- **Immersive Pointcloud**: 約80個のフォルダ（2025-07-23～2025-07-27）
- **Music Video**: 約10個のフォルダ（2025-07-17～2025-07-21）  
- **Integration Test**: 2個のフォルダ（2025-07-26）

### 問題点
1. **ディレクトリ構造の汚染**: リポジトリルートの可読性低下
2. **ファイル検索の困難**: 重要ファイルが埋もれる
3. **Git履歴の複雑化**: 大量の自動生成フォルダでログが見にくい

## 🚀 **整理方針**

### 1. **アーカイブ構造**
```
archive-pointcloud-experiments/
├── ORGANIZATION_PLAN.md (このファイル)
├── by-date/
│   ├── 2025-07-23/
│   ├── 2025-07-24/
│   ├── 2025-07-25/
│   ├── 2025-07-26/
│   └── 2025-07-27/
├── by-type/
│   ├── immersive-pointcloud/
│   ├── music-video/
│   └── integration-test/
└── latest/ (最新テスト用の symlink)
```

### 2. **分類基準**

#### **メイン分類**
- `by-date/`: 日付別アーカイブ（履歴確認用）
- `by-type/`: 種類別アーカイブ（機能別検索用）
- `latest/`: 最新テスト結果へのショートカット

#### **保持基準**
- **完全なフォルダ**: すべてのファイル（depth.png, pointcloud.ply等）が揃っているもの
- **不完全なフォルダ**: URLファイルのみの場合は低優先度でアーカイブ

### 3. **将来の自動化方針**

#### **GitHub Actions修正**
- **出力先変更**: `immersive-pointcloud-*` → `archive-pointcloud-experiments/latest/`
- **自動アーカイブ**: 完了後に日付フォルダに移動
- **クリーンアップ**: 古いテストフォルダの定期削除

#### **ワークフロー修正箇所**
- `create-immersive-pointcloud-experience.yml`
- `threejs-pointcloud-viewer/action.yml`  
- `pointcloud-generation/action.yml`

## 📝 **実行手順**

### Phase 1: アーカイブ構造作成
1. `archive-pointcloud-experiments/` ディレクトリ作成
2. `by-date/`, `by-type/`, `latest/` サブディレクトリ作成

### Phase 2: 既存フォルダの移動
1. 日付別に既存フォルダをソート
2. `by-date/YYYY-MM-DD/` に移動
3. 種類別に `by-type/` にシンボリックリンク作成

### Phase 3: GitHub Actions修正
1. 出力先パスの変更
2. 自動アーカイブ機能の追加
3. クリーンアップ機能の追加

### Phase 4: 検証
1. 新しいテスト実行で正しい場所に出力されることを確認
2. GitHub Pages のパス更新
3. ドキュメント更新

## 🎯 **期待される効果**

### 即座の改善
- **リポジトリルートの整理**: 重要ファイルの可視性向上
- **検索性向上**: 日付・種類別の構造化アクセス
- **開発効率**: テストフォルダの迅速な特定

### 長期的メリット  
- **自動整理**: 新しいテストが自動的に適切な場所に配置
- **履歴管理**: 日付別アクセスで過去のテスト結果を簡単に追跡
- **スケーラビリティ**: 将来のテスト増加に対応可能な構造

---

**作成日**: 2025-07-27  
**対象**: Kamuicode Creative Workshop リポジトリ整理  
**優先度**: High - リポジトリの可読性とメンテナンス性向上