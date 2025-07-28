import cv2
from ultralytics import YOLO
import numpy as np
from pathlib import Path
from collections import defaultdict
import json

# 動画ファイルパス
video_path = "/Users/nukuiyuki/神威/20250727_ラグーナ/動画_シーン15-2025-07-27T16-47-06/output/rose_scene_video2.mp4"

# 出力ディレクトリ
output_dir = Path("/Users/nukuiyuki/dev/kamuicode-workflow/yolo_detection_results")
output_dir.mkdir(exist_ok=True)

# YOLOv11モデル
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

# 出力動画の設定
output_motion_path = output_dir / "motion_tracking_rose_scene.mp4"
output_trajectory_path = output_dir / "trajectory_rose_scene.mp4"
output_heatmap_path = output_dir / "motion_heatmap_rose_scene.mp4"

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_motion = cv2.VideoWriter(str(output_motion_path), fourcc, fps, (width, height))
out_trajectory = cv2.VideoWriter(str(output_trajectory_path), fourcc, fps, (width, height))
out_heatmap = cv2.VideoWriter(str(output_heatmap_path), fourcc, fps, (width, height))

# トラッキング用の変数
object_tracks = defaultdict(list)  # オブジェクトIDごとの軌跡
object_speeds = defaultdict(list)  # オブジェクトIDごとの速度
next_object_id = 0
previous_objects = {}
motion_heatmap = np.zeros((height, width), dtype=np.float32)

# カラーマップ
colors = {
    'person': (255, 0, 0),      # 赤
    'cup': (0, 255, 0),         # 緑
    'bowl': (0, 0, 255),        # 青
    'donut': (255, 255, 0),     # シアン
    'apple': (255, 0, 255),     # マゼンタ
    'spoon': (0, 255, 255),     # イエロー
}

def calculate_iou(box1, box2):
    """2つのボックス間のIoU（Intersection over Union）を計算"""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0

def match_objects(current_objects, previous_objects, threshold=0.5):
    """前フレームと現フレームのオブジェクトをマッチング"""
    global next_object_id
    matched_objects = {}
    used_previous = set()
    
    for curr_idx, curr_obj in enumerate(current_objects):
        best_match = None
        best_iou = threshold
        
        for prev_id, prev_obj in previous_objects.items():
            if prev_id in used_previous:
                continue
            
            # 同じクラスのオブジェクトのみマッチング
            if curr_obj['class'] != prev_obj['class']:
                continue
            
            iou = calculate_iou(curr_obj['bbox'], prev_obj['bbox'])
            if iou > best_iou:
                best_iou = iou
                best_match = prev_id
        
        if best_match is not None:
            matched_objects[best_match] = curr_obj
            used_previous.add(best_match)
        else:
            # 新しいオブジェクト
            matched_objects[next_object_id] = curr_obj
            next_object_id += 1
    
    return matched_objects

# フレームごとに処理
frame_count = 0
trajectory_canvas = np.zeros((height, width, 3), dtype=np.uint8)

print("Starting motion detection and tracking...")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # YOLOで物体検出
    results = model(frame)
    
    # 現在のフレームのオブジェクト
    current_objects = []
    
    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = model.names[cls]
                
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                current_objects.append({
                    'class': label,
                    'confidence': conf,
                    'bbox': [x1, y1, x2, y2],
                    'center': [center_x, center_y]
                })
    
    # オブジェクトマッチング
    matched_objects = match_objects(current_objects, previous_objects)
    
    # モーショントラッキングフレーム
    motion_frame = frame.copy()
    
    # 各オブジェクトの処理
    for obj_id, obj in matched_objects.items():
        color = colors.get(obj['class'], (128, 128, 128))
        
        # トラッキング履歴に追加
        object_tracks[obj_id].append(obj['center'])
        
        # 速度計算（前フレームとの比較）
        if obj_id in previous_objects:
            prev_center = previous_objects[obj_id]['center']
            speed = np.sqrt((obj['center'][0] - prev_center[0])**2 + 
                          (obj['center'][1] - prev_center[1])**2)
            object_speeds[obj_id].append(speed)
            
            # モーションベクトルを描画
            if speed > 2:  # 最小移動閾値
                cv2.arrowedLine(motion_frame, 
                              tuple(prev_center), 
                              tuple(obj['center']), 
                              color, 2, tipLength=0.3)
            
            # ヒートマップ更新
            cv2.line(motion_heatmap, 
                    tuple(prev_center), 
                    tuple(obj['center']), 
                    1, 3)
        
        # バウンディングボックスとID表示
        x1, y1, x2, y2 = obj['bbox']
        cv2.rectangle(motion_frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(motion_frame, f'ID:{obj_id} {obj["class"]}', 
                   (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # 軌跡の描画（最後の30フレーム）
        if len(object_tracks[obj_id]) > 1:
            points = np.array(object_tracks[obj_id][-30:], np.int32)
            cv2.polylines(trajectory_canvas, [points], False, color, 2)
            cv2.polylines(motion_frame, [points], False, color, 1)
    
    # ヒートマップの可視化
    heatmap_normalized = cv2.normalize(motion_heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_colored = cv2.applyColorMap(heatmap_normalized.astype(np.uint8), cv2.COLORMAP_JET)
    heatmap_frame = cv2.addWeighted(frame, 0.7, heatmap_colored, 0.3, 0)
    
    # 軌跡オーバーレイ
    trajectory_frame = cv2.addWeighted(frame, 0.7, trajectory_canvas, 0.3, 0)
    
    # 動画に書き込み
    out_motion.write(motion_frame)
    out_trajectory.write(trajectory_frame)
    out_heatmap.write(heatmap_frame)
    
    # 次フレームの準備
    previous_objects = matched_objects.copy()
    frame_count += 1
    
    # 進捗表示
    if frame_count % 30 == 0:
        print(f"Processed {frame_count}/{total_frames} frames ({frame_count/total_frames*100:.1f}%)")

# リソースを解放
cap.release()
out_motion.release()
out_trajectory.release()
out_heatmap.release()
cv2.destroyAllWindows()

# モーション統計を計算
motion_stats = {
    'total_tracked_objects': len(object_tracks),
    'object_motions': []
}

for obj_id, track in object_tracks.items():
    if len(track) > 1:
        total_distance = 0
        for i in range(1, len(track)):
            dist = np.sqrt((track[i][0] - track[i-1][0])**2 + 
                         (track[i][1] - track[i-1][1])**2)
            total_distance += dist
        
        avg_speed = np.mean(object_speeds[obj_id]) if obj_id in object_speeds else 0
        
        motion_stats['object_motions'].append({
            'object_id': obj_id,
            'total_frames': len(track),
            'total_distance': float(total_distance),
            'average_speed': float(avg_speed),
            'start_position': track[0],
            'end_position': track[-1]
        })

# 統計を保存
stats_file = output_dir / "motion_statistics.json"
with open(stats_file, 'w') as f:
    json.dump(motion_stats, f, indent=2)

print(f"\nMotion detection complete!")
print(f"Motion tracking video: {output_motion_path}")
print(f"Trajectory video: {output_trajectory_path}")
print(f"Motion heatmap video: {output_heatmap_path}")
print(f"Statistics saved to: {stats_file}")
print(f"\nTotal tracked objects: {len(object_tracks)}")
print(f"Objects with significant motion: {sum(1 for m in motion_stats['object_motions'] if m['total_distance'] > 50)}")