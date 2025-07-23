#!/usr/bin/env python3
"""
基本的なオーディオファイル情報を取得するスクリプト
librosaが利用できない場合の代替手段
"""

import os
import struct
import sys

def get_wav_info(filename):
    """WAVファイルの基本情報を取得"""
    try:
        with open(filename, 'rb') as f:
            # WAVヘッダーを読み込み
            riff = f.read(4)
            if riff != b'RIFF':
                return None
            
            file_size = struct.unpack('<I', f.read(4))[0]
            wave = f.read(4)
            if wave != b'WAVE':
                return None
            
            # fmtチャンクを探す
            while True:
                chunk_id = f.read(4)
                if not chunk_id:
                    break
                    
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'fmt ':
                    fmt_data = f.read(chunk_size)
                    audio_format = struct.unpack('<H', fmt_data[0:2])[0]
                    num_channels = struct.unpack('<H', fmt_data[2:4])[0]
                    sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
                    byte_rate = struct.unpack('<I', fmt_data[8:12])[0]
                    block_align = struct.unpack('<H', fmt_data[12:14])[0]
                    bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
                elif chunk_id == b'data':
                    data_size = chunk_size
                    break
                else:
                    f.seek(chunk_size, 1)  # スキップ
            
            # 再生時間を計算
            duration = data_size / (sample_rate * num_channels * bits_per_sample // 8)
            
            return {
                'file_size': file_size,
                'sample_rate': sample_rate,
                'num_channels': num_channels,
                'bits_per_sample': bits_per_sample,
                'duration': duration,
                'data_size': data_size
            }
    except Exception as e:
        print(f"Error reading WAV file: {e}")
        return None

def analyze_file_properties(filename):
    """ファイルの基本プロパティを分析"""
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return
    
    file_size = os.path.getsize(filename)
    print(f"ファイルサイズ: {file_size / (1024*1024):.2f} MB")
    
    wav_info = get_wav_info(filename)
    if wav_info:
        print(f"サンプリングレート: {wav_info['sample_rate']} Hz")
        print(f"チャンネル数: {wav_info['num_channels']}")
        print(f"ビット深度: {wav_info['bits_per_sample']} bit")
        print(f"再生時間: {wav_info['duration']:.2f} 秒")
        print(f"データサイズ: {wav_info['data_size'] / (1024*1024):.2f} MB")
        
        # 戦略計画との比較
        target_min, target_max = 30, 40
        actual_duration = wav_info['duration']
        
        print(f"\n🎯 戦略計画との比較:")
        print(f"想定時間: {target_min}-{target_max}秒")
        print(f"実際時間: {actual_duration:.2f}秒")
        
        if target_min <= actual_duration <= target_max:
            print("✅ 時間長適合")
        elif actual_duration < target_min:
            print(f"⚠️ 短すぎます ({actual_duration - target_min:.1f}秒短い)")
        else:
            print(f"❌ 長すぎます (+{actual_duration - target_max:.1f}秒オーバー)")
        
        return wav_info
    else:
        print("WAVファイル情報の取得に失敗しました")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 basic_audio_info.py <wav_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    analyze_file_properties(filename)