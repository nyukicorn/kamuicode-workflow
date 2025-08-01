#!/bin/bash

# お気に入り作品保存スクリプト（改良版）
# Usage: ./tools/save-favorite.sh <作品ディレクトリ名> [新しい名前] [--auto-name]

if [ $# -lt 1 ]; then
    echo "❌ Usage: $0 <作品ディレクトリ名> [新しい名前] [--auto-name]"
    echo "例: $0 create-immersive-panorama-pointcloud-experience-20250801-16679534066"
    echo "例: $0 create-immersive-panorama-pointcloud-experience-20250801-16679534066 aurora"
    echo "例: $0 create-immersive-panorama-pointcloud-experience-20250801-16679534066 --auto-name"
    exit 1
fi

SOURCE_DIR="docs/$1"

# 自動タイムスタンプ生成
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# 自動命名機能
if [ "$2" = "--auto-name" ] || [ -z "$2" ]; then
    # プロンプトファイルから特徴抽出を試行
    PROMPT_FILE=""
    if [ -f "$SOURCE_DIR/prompt.txt" ]; then
        PROMPT_FILE="$SOURCE_DIR/prompt.txt"
    elif [ -f "$SOURCE_DIR/config.txt" ]; then
        PROMPT_FILE="$SOURCE_DIR/config.txt"
    fi
    
    if [ -n "$PROMPT_FILE" ]; then
        # プロンプトから特徴的なキーワードを抽出
        AUTO_NAME=$(cat "$PROMPT_FILE" | grep -oE "(オーロラ|aurora|宇宙|cosmic|星|star|森|forest|海|ocean|山|mountain|花|flower|桜|sakura)" | head -1 | tr '[:upper:]' '[:lower:]')
        FAVORITE_NAME="${AUTO_NAME:-artwork}-$TIMESTAMP"
    else
        FAVORITE_NAME="artwork-$TIMESTAMP"
    fi
else
    # ユーザー指定名 + タイムスタンプ
    FAVORITE_NAME="$2-$TIMESTAMP"
fi

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
    echo "📛 作品名: $FAVORITE_NAME"
    echo "🌐 URL: https://nyukicorn.github.io/kamuicode-workflow/gallery/$FAVORITE_NAME/"
    
    # ファイルサイズ情報
    SIZE=$(du -sh "$TARGET_DIR" | cut -f1)
    echo "💾 サイズ: $SIZE"
    
    # メタデータファイル作成
    cat > "$TARGET_DIR/metadata.txt" << EOF
作品名: $FAVORITE_NAME
保存日時: $(date '+%Y-%m-%d %H:%M:%S')
元ディレクトリ: $1
ファイルサイズ: $SIZE
URL: https://nyukicorn.github.io/kamuicode-workflow/gallery/$FAVORITE_NAME/
EOF
    
    echo "📄 メタデータファイル作成完了"
    
    # ギャラリーインデックス更新のメッセージ
    echo "📝 ギャラリーインデックスを更新するには:"
    echo "   ./tools/update-gallery.sh"
else
    echo "❌ コピーに失敗しました"
    exit 1
fi