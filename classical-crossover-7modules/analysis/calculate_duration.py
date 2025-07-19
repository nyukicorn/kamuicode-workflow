#!/usr/bin/env python3
"""
音楽ファイルの長さ計算ツール
"""

import os

def calculate_wav_duration(file_path):
    """WAVファイルの長さを計算"""
    try:
        # ファイルサイズを取得
        file_size = os.path.getsize(file_path)
        
        # WAVファイルのヘッダー情報から推定
        # 16-bit stereo, 48000 Hz の場合
        # 1秒 = 48000 samples/sec * 2 channels * 2 bytes/sample = 192000 bytes/sec
        sample_rate = 48000  # Hz
        channels = 2  # stereo
        bit_depth = 16  # bits
        bytes_per_sample = bit_depth // 8  # 2 bytes
        
        bytes_per_second = sample_rate * channels * bytes_per_sample
        
        # WAVファイルのヘッダー（約44バイト）を差し引く
        audio_data_size = file_size - 44
        
        duration_seconds = audio_data_size / bytes_per_second
        
        return duration_seconds, file_size
    
    except Exception as e:
        print(f"エラー: {e}")
        return None, None

def main():
    file_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250719-16384240868/music/generated-music.wav"
    
    duration, size = calculate_wav_duration(file_path)
    
    if duration:
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        print(f"楽曲の長さ: {minutes}:{seconds:02d} ({duration:.2f}秒)")
        print(f"ファイルサイズ: {size / (1024*1024):.2f} MB")
        print(f"音質: 16-bit Stereo 48kHz")
        
        return {
            "duration_seconds": duration,
            "duration_minutes": f"{minutes}:{seconds:02d}",
            "file_size_mb": size / (1024*1024),
            "sample_rate": 48000,
            "bit_depth": 16,
            "channels": "Stereo"
        }
    else:
        print("音楽ファイルの分析に失敗しました。")
        return None

if __name__ == "__main__":
    main()