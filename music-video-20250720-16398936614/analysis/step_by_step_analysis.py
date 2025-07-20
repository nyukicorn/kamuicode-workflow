#!/usr/bin/env python3
"""
段階的音楽分析
"""
import wave
import os
from datetime import datetime

music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16398936614/music/generated-music.wav"

print("=== 音楽ファイル段階的分析 ===")
print(f"ファイルパス: {music_file}")
print(f"分析開始時刻: {datetime.now()}")

# ステップ1: ファイル存在確認
print("\n[ステップ1] ファイル存在確認")
try:
    if os.path.exists(music_file):
        file_size = os.path.getsize(music_file)
        print(f"✓ ファイル存在確認")
        print(f"  ファイルサイズ: {file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
    else:
        print("✗ ファイルが存在しません")
        exit(1)
except Exception as e:
    print(f"✗ ファイルアクセスエラー: {e}")
    exit(1)

# ステップ2: WAVファイル基本情報
print("\n[ステップ2] WAVファイル基本情報")
try:
    with wave.open(music_file, 'rb') as wav_file:
        frames = wav_file.getnframes()
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        duration = frames / sample_rate
        
        print(f"✓ WAVファイル読み込み成功")
        print(f"  楽曲の長さ: {duration:.2f}秒")
        print(f"  サンプリングレート: {sample_rate:,} Hz")
        print(f"  チャンネル数: {channels}")
        print(f"  サンプル幅: {sample_width} bytes ({sample_width*8} bit)")
        print(f"  総フレーム数: {frames:,}")
        
        # 戦略計画書との基本比較
        print(f"\n[基本適合性チェック]")
        duration_ok = 30 <= duration <= 40
        print(f"  楽曲長さ（30-40秒目標）: {duration:.1f}秒 {'✓' if duration_ok else '✗'}")
        print(f"  音質（44.1kHz以上）: {sample_rate}Hz {'✓' if sample_rate >= 44100 else '✗'}")
        print(f"  ビット深度（16bit以上）: {sample_width*8}bit {'✓' if sample_width >= 2 else '✗'}")
        
except Exception as e:
    print(f"✗ WAVファイル読み込みエラー: {e}")
    exit(1)

print(f"\n=== 基本分析完了 ===")

# 結果を簡易JSONとして保存
basic_result = {
    "timestamp": datetime.now().isoformat(),
    "file_path": music_file,
    "file_size_bytes": file_size,
    "duration_seconds": duration,
    "sample_rate": sample_rate,
    "channels": channels,
    "bit_depth": sample_width * 8,
    "total_frames": frames,
    "strategy_compliance_basic": {
        "duration_30_40_sec": duration_ok,
        "audio_quality_ok": sample_rate >= 44100 and sample_width >= 2
    }
}

import json
output_dir = os.path.dirname(music_file).replace('/music', '/analysis')
os.makedirs(output_dir, exist_ok=True)

basic_json_path = os.path.join(output_dir, 'basic_analysis_result.json')
with open(basic_json_path, 'w', encoding='utf-8') as f:
    json.dump(basic_result, f, indent=2, ensure_ascii=False)

print(f"基本分析結果保存: {basic_json_path}")

# 分析完了