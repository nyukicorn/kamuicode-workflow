import cv2
from ultralytics import YOLO
import numpy as np
from pathlib import Path

# 動画ファイルパス
video_path = "/Users/nukuiyuki/神威/20250727_ラグーナ/動画_シーン15-2025-07-27T16-47-06/output/rose_scene_video2.mp4"

# 出力ディレクトリ
output_dir = Path("/Users/nukuiyuki/dev/kamuicode-workflow/yolo_detection_results")
output_dir.mkdir(exist_ok=True)

# YOLOv11モデルを使用
print("Loading YOLO model...")
model = YOLO('yolo11m.pt')

# 動画を開く
print(f"Opening video: {video_path}")
cap = cv2.VideoCapture(video_path)

# 動画情報を取得
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"Video info: {width}x{height} @ {fps}fps, {total_frames} frames total")

# 出力動画の設定（ボックスのみ版）
output_boxes_only_path = output_dir / "boxes_only_rose_scene.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_boxes = cv2.VideoWriter(str(output_boxes_only_path), fourcc, fps, (width, height))

# 出力動画の設定（ボックス＋マスク版）
output_masked_path = output_dir / "masked_boxes_rose_scene.mp4"
out_masked = cv2.VideoWriter(str(output_masked_path), fourcc, fps, (width, height))

# 出力動画の設定（クロップされたオブジェクト版）
output_cropped_path = output_dir / "cropped_objects_rose_scene.mp4"
out_cropped = cv2.VideoWriter(str(output_cropped_path), fourcc, fps, (width, height))

# カラーマップ（クラスごとに異なる色）
colors = {
    'person': (255, 0, 0),      # 赤
    'cup': (0, 255, 0),         # 緑
    'bowl': (0, 0, 255),        # 青
    'donut': (255, 255, 0),     # シアン
    'apple': (255, 0, 255),     # マゼンタ
    'spoon': (0, 255, 255),     # イエロー
}

# フレームごとに処理
frame_count = 0
process_every_n_frames = 1  # 全フレーム処理

print("Starting box processing...")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 3つの出力フレームを準備
    boxes_only_frame = np.zeros_like(frame)  # 黒背景にボックスのみ
    masked_frame = frame.copy()  # 元画像にマスク適用
    cropped_frame = np.zeros_like(frame)  # クロップされたオブジェクト
    
    if frame_count % process_every_n_frames == 0:
        # YOLOで物体検出
        results = model(frame)
        
        # 検出結果を処理
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    # バウンディングボックスの座標
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # クラスと信頼度
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = model.names[cls]
                    
                    # クラスに応じた色を取得
                    color = colors.get(label, (128, 128, 128))
                    
                    # 1. ボックスのみ版：黒背景に色付きボックス
                    cv2.rectangle(boxes_only_frame, (x1, y1), (x2, y2), color, 3)
                    cv2.putText(boxes_only_frame, f'{label} {conf:.2f}', (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
                    # 2. マスク版：検出されたオブジェクト以外を暗くする
                    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
                    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
                    
                    # 3. クロップ版：検出されたオブジェクトのみを切り出して配置
                    if x2 > x1 and y2 > y1:  # 有効なボックスサイズをチェック
                        cropped_obj = frame[y1:y2, x1:x2]
                        cropped_frame[y1:y2, x1:x2] = cropped_obj
                        # ボックスの輪郭を追加
                        cv2.rectangle(cropped_frame, (x1, y1), (x2, y2), color, 2)
        
        # マスク処理：検出されたオブジェクト以外を暗くする
        if 'mask' in locals():
            # 全体的なマスクを作成（すべての検出オブジェクトを含む）
            full_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            for r in results:
                if r.boxes is not None:
                    for box in r.boxes:
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        cv2.rectangle(full_mask, (x1, y1), (x2, y2), 255, -1)
            
            # マスクを適用
            masked_frame = frame.copy()
            masked_frame[full_mask == 0] = masked_frame[full_mask == 0] * 0.3  # 背景を暗くする
    
    # 動画に書き込み
    out_boxes.write(boxes_only_frame)
    out_masked.write(masked_frame.astype(np.uint8))
    out_cropped.write(cropped_frame)
    
    frame_count += 1
    
    # 進捗表示
    if frame_count % 30 == 0:
        print(f"Processed {frame_count}/{total_frames} frames ({frame_count/total_frames*100:.1f}%)")

# リソースを解放
cap.release()
out_boxes.release()
out_masked.release()
out_cropped.release()
cv2.destroyAllWindows()

print(f"\nBox processing complete!")
print(f"Boxes only video: {output_boxes_only_path}")
print(f"Masked video: {output_masked_path}")
print(f"Cropped objects video: {output_cropped_path}")

# サムネイル画像も生成
print("\nGenerating preview images...")
cap = cv2.VideoCapture(video_path)
cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)  # 中間フレーム
ret, frame = cap.read()
if ret:
    results = model(frame)
    
    # プレビュー画像を作成
    preview_frame = np.zeros_like(frame)
    for r in results:
        if r.boxes is not None:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cls = int(box.cls[0])
                label = model.names[cls]
                color = colors.get(label, (128, 128, 128))
                cv2.rectangle(preview_frame, (x1, y1), (x2, y2), color, 3)
                cv2.putText(preview_frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    cv2.imwrite(str(output_dir / "preview_boxes_only.jpg"), preview_frame)
    print(f"Preview image saved: {output_dir / 'preview_boxes_only.jpg'}")

cap.release()