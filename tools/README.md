# 🎨 作品保存システム

気に入った360°パノラマポイントクラウド作品を永続的に保存し、404エラーを防ぐシステムです。

## 🚀 使用方法

### 1. お気に入り作品を保存
```bash
# 完全自動（プロンプトから特徴抽出 + タイムスタンプ）
./tools/save-favorite.sh create-immersive-panorama-pointcloud-experience-20250801-16679534066

# ユーザー指定名 + 自動タイムスタンプ（重複防止）
./tools/save-favorite.sh create-immersive-panorama-pointcloud-experience-20250801-16679534066 aurora
# → 結果: aurora-20250802-0155

# 強制自動命名
./tools/save-favorite.sh create-immersive-panorama-pointcloud-experience-20250801-16679534066 --auto-name
# → 結果: cosmic-20250802-0155 (プロンプトから「宇宙」を検出)
```

### 2. ギャラリーインデックスを更新
```bash
./tools/update-gallery.sh
```

### 3. 保存した作品にアクセス
- **ギャラリー**: https://nyukicorn.github.io/kamuicode-workflow/gallery/
- **直接アクセス**: https://nyukicorn.github.io/kamuicode-workflow/gallery/[作品名]/

## 📁 フォルダ構造

```
docs/
├── gallery/                    # 永続保存されたお気に入り作品
│   ├── index.html             # ギャラリー一覧ページ
│   ├── beautiful-aurora/      # お気に入り作品1
│   └── cosmic-nebula/         # お気に入り作品2
├── create-immersive-panorama-* # 一時的な作品（新しいデプロイで404になる可能性）
└── immersive-pointcloud-*     # 過去の作品
```

## ✨ 特徴

- **404エラー防止**: お気に入り作品は永続的に保存
- **わかりやすい名前**: 長いタイムスタンプ名を短縮可能
- **美しいギャラリー**: サムネイル付きの一覧表示
- **音楽撮影対応**: 保存した作品で安心して撮影可能

## 🎵 撮影での使用例

```bash
# 美しい作品を「撮影用オーロラ」として保存
./tools/save-favorite.sh create-immersive-panorama-pointcloud-experience-20250801-16679534066 recording-aurora

# ギャラリー更新
./tools/update-gallery.sh

# 撮影時はこのURLを使用（404になりません）
# https://nyukicorn.github.io/kamuicode-workflow/gallery/recording-aurora/
```

## 🔄 ワークフロー

1. 新しい作品を生成
2. 気に入ったら `save-favorite.sh` で保存
3. `update-gallery.sh` でギャラリー更新
4. 撮影や後日鑑賞に安心して使用

これで、次のデプロイで404エラーになる心配がありません！