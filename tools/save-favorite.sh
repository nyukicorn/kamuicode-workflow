#!/bin/bash

# お気に入り作品保存スクリプト
# Usage: ./tools/save-favorite.sh <作品ディレクトリ名> [新しい名前]

if [ $# -lt 1 ]; then
    echo "❌ Usage: $0 <作品ディレクトリ名> [新しい名前]"
    echo "例: $0 create-immersive-panorama-pointcloud-experience-20250801-16679534066"
    echo "例: $0 create-immersive-panorama-pointcloud-experience-20250801-16679534066 beautiful-aurora"
    exit 1
fi

SOURCE_DIR="docs/$1"
FAVORITE_NAME="${2:-$1}"
TARGET_DIR="docs/gallery/$FAVORITE_NAME"

# ソースディレクトリの存在確認
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ ソースディレクトリが見つかりません: $SOURCE_DIR"
    echo "📁 利用可能な作品:"
    find docs/ -maxdepth 1 -name "*immersive*" -type d | head -10
    exit 1
fi

# ターゲットディレクトリの重複確認
if [ -d "$TARGET_DIR" ]; then
    echo "❌ お気に入りが既に存在します: $TARGET_DIR"
    exit 1
fi

# コピー実行
echo "🎨 お気に入りに保存中..."
echo "   From: $SOURCE_DIR"
echo "   To: $TARGET_DIR"

cp -r "$SOURCE_DIR" "$TARGET_DIR"

if [ $? -eq 0 ]; then
    echo "✅ お気に入りに保存完了！"
    echo "🌐 URL: https://nyukicorn.github.io/kamuicode-workflow/gallery/$FAVORITE_NAME/"
    
    # ファイルサイズ情報
    SIZE=$(du -sh "$TARGET_DIR" | cut -f1)
    echo "💾 サイズ: $SIZE"
    
    # ギャラリーインデックス更新のメッセージ
    echo "📝 ギャラリーインデックスを更新するには:"
    echo "   ./tools/update-gallery.sh"
else
    echo "❌ コピーに失敗しました"
    exit 1
fi