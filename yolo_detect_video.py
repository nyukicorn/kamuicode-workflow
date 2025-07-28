import cv2
from ultralytics import YOLO
import os
from pathlib import Path
import json
from collections import defaultdict

# 動画ファイルパス
video_path = "/Users/nukuiyuki/神威/20250727_ラグーナ/動画_シーン15-2025-07-27T16-47-06/output/rose_scene_video2.mp4"

# 出力ディレクトリ
output_dir = Path("/Users/nukuiyuki/dev/kamuicode-workflow/yolo_detection_results")
output_dir.mkdir(exist_ok=True)

# YOLOv11モデルをダウンロードして使用
# Note: YOLOv11は最新バージョンのultralyticsで自動的にサポートされています
print("Loading YOLO model...")
model = YOLO('yolo11m.pt')  # medium size model for better accuracy

# 動画を開く
print(f"Opening video: {video_path}")
cap = cv2.VideoCapture(video_path)

# 動画情報を取得
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"Video info: {width}x{height} @ {fps}fps, {total_frames} frames total")

# 検出結果を保存する辞書
detection_summary = defaultdict(int)
frame_detections = []

# 出力動画の設定
output_video_path = output_dir / "detected_rose_scene.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(str(output_video_path), fourcc, fps, (width, height))

# フレームごとに処理
frame_count = 0
process_every_n_frames = 5  # 5フレームごとに処理（処理速度向上のため）

print("Starting object detection...")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    if frame_count % process_every_n_frames == 0:
        # YOLOで物体検出
        results = model(frame)
        
        # フレームごとの検出結果を保存
        frame_detection = {
            'frame': frame_count,
            'time': frame_count / fps,
            'objects': []
        }
        
        # 検出結果を描画
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
                    
                    # 統計を更新
                    detection_summary[label] += 1
                    
                    # フレーム検出情報に追加
                    frame_detection['objects'].append({
                        'class': label,
                        'confidence': conf,
                        'bbox': [x1, y1, x2, y2]
                    })
                    
                    # バウンディングボックスを描画
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        frame_detections.append(frame_detection)
        
        # 進捗表示
        if frame_count % 100 == 0:
            print(f"Processed {frame_count}/{total_frames} frames ({frame_count/total_frames*100:.1f}%)")
    
    # 動画に書き込み
    out.write(frame)
    frame_count += 1

# リソースを解放
cap.release()
out.release()
cv2.destroyAllWindows()

# 検出結果をJSON形式で保存
results_data = {
    'video_info': {
        'path': video_path,
        'width': width,
        'height': height,
        'fps': fps,
        'total_frames': total_frames,
        'duration': total_frames / fps
    },
    'detection_summary': dict(detection_summary),
    'frame_detections': frame_detections[:100]  # 最初の100フレーム分のみ保存（ファイルサイズ削減のため）
}

results_file = output_dir / "detection_results.json"
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results_data, f, indent=2, ensure_ascii=False)

# サマリーレポートを作成
report_file = output_dir / "detection_report.txt"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("=== YOLO v11 Object Detection Report ===\n\n")
    f.write(f"Video: {video_path}\n")
    f.write(f"Duration: {total_frames/fps:.2f} seconds\n")
    f.write(f"Resolution: {width}x{height}\n")
    f.write(f"Total frames: {total_frames}\n\n")
    
    f.write("Detected Objects Summary:\n")
    f.write("-" * 40 + "\n")
    
    sorted_detections = sorted(detection_summary.items(), key=lambda x: x[1], reverse=True)
    for obj_class, count in sorted_detections:
        f.write(f"{obj_class}: {count} detections\n")
    
    f.write("\n" + "=" * 40 + "\n")

print(f"\nDetection complete!")
print(f"Output video: {output_video_path}")
print(f"Results saved to: {results_file}")
print(f"Report saved to: {report_file}")

# 検出サマリーを表示
print("\nDetection Summary:")
for obj_class, count in sorted(detection_summary.items(), key=lambda x: x[1], reverse=True):
    print(f"  {obj_class}: {count} detections")