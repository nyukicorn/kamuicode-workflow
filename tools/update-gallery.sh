#!/bin/bash

# ギャラリーインデックス更新スクリプト

GALLERY_DIR="docs/gallery"
INDEX_FILE="$GALLERY_DIR/index.html"

echo "📸 ギャラリーインデックスを更新中..."

# HTMLファイル作成
cat > "$INDEX_FILE" << 'EOF'
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎨 Immersive Panorama Gallery</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            color: white;
            min-height: 100vh;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .gallery-item {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .gallery-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        .gallery-item h3 {
            margin-top: 0;
            color: #4ecdc4;
            font-size: 1.3em;
        }
        
        .gallery-item .info {
            margin: 10px 0;
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .gallery-item .actions {
            margin-top: 15px;
        }
        
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            margin-right: 10px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
        }
        
        .empty {
            text-align: center;
            opacity: 0.6;
            font-size: 1.2em;
            grid-column: 1 / -1;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 Immersive Panorama Gallery</h1>
        <p>お気に入りの360°パノラマポイントクラウド作品コレクション</p>
    </div>
    
    <div class="gallery">
EOF

# ギャラリーアイテムを追加
ITEM_COUNT=0
for dir in "$GALLERY_DIR"/*; do
    if [ -d "$dir" ] && [ "$(basename "$dir")" != "." ] && [ "$(basename "$dir")" != ".." ]; then
        ITEM_NAME=$(basename "$dir")
        if [ -f "$dir/index.html" ]; then
            # 作成日時を推定
            TIMESTAMP=$(echo "$ITEM_NAME" | grep -o '[0-9]\{8\}-[0-9]\{8\}' || echo "unknown")
            if [ "$TIMESTAMP" != "unknown" ]; then
                DATE_PART=$(echo "$TIMESTAMP" | cut -d'-' -f1)
                TIME_PART=$(echo "$TIMESTAMP" | cut -d'-' -f2)
                FORMATTED_DATE="${DATE_PART:0:4}-${DATE_PART:4:2}-${DATE_PART:6:2} ${TIME_PART:0:2}:${TIME_PART:2:2}:${TIME_PART:4:2}"
            else
                FORMATTED_DATE="不明"
            fi
            
            # ファイルサイズ取得
            SIZE=$(du -sh "$dir" 2>/dev/null | cut -f1 || echo "不明")
            
            cat >> "$INDEX_FILE" << EOF
        <div class="gallery-item">
            <h3>$ITEM_NAME</h3>
            <div class="info">
                <div>📅 作成日時: $FORMATTED_DATE</div>
                <div>💾 サイズ: $SIZE</div>
            </div>
            <div class="actions">
                <a href="$ITEM_NAME/" class="btn" target="_blank">🌐 開く</a>
                <a href="$ITEM_NAME/" class="btn" style="background: linear-gradient(45deg, #45b7d1, #96ceb4);">🎵 音楽と楽しむ</a>
            </div>
        </div>
EOF
            ITEM_COUNT=$((ITEM_COUNT + 1))
        fi
    fi
done

# アイテムがない場合
if [ $ITEM_COUNT -eq 0 ]; then
    cat >> "$INDEX_FILE" << 'EOF'
        <div class="empty">
            <p>まだお気に入りの作品がありません</p>
            <p>気に入った作品を保存するには:</p>
            <code>./tools/save-favorite.sh [作品ディレクトリ名] [新しい名前]</code>
        </div>
EOF
fi

cat >> "$INDEX_FILE" << 'EOF'
    </div>
    
    <div style="text-align: center; margin-top: 50px; opacity: 0.6;">
        <p>🚀 Generated by Kamuicode Workflow System</p>
    </div>
</body>
</html>
EOF

echo "✅ ギャラリーインデックス更新完了！"
echo "📊 保存済み作品数: $ITEM_COUNT"
echo "🌐 URL: https://nyukicorn.github.io/kamuicode-workflow/gallery/"