#!/usr/bin/env python3
import struct
import sys

def get_wav_duration(filename):
    """WAVファイルの再生時間を取得"""
    try:
        with open(filename, 'rb') as f:
            # WAVヘッダー読み込み
            f.seek(0)
            riff = f.read(4)
            if riff != b'RIFF':
                return "Not a valid WAV file"
            
            f.read(4)  # file size
            wave = f.read(4)
            if wave != b'WAVE':
                return "Not a valid WAV file"
            
            # fmtチャンクとdataチャンクを探す
            sample_rate = None
            num_channels = None
            bits_per_sample = None
            data_size = None
            
            while True:
                chunk_id = f.read(4)
                if not chunk_id:
                    break
                
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'fmt ':
                    fmt_data = f.read(chunk_size)
                    num_channels = struct.unpack('<H', fmt_data[2:4])[0]
                    sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
                    bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
                elif chunk_id == b'data':
                    data_size = chunk_size
                    break
                else:
                    f.seek(chunk_size, 1)
            
            if sample_rate and num_channels and bits_per_sample and data_size:
                duration = data_size / (sample_rate * num_channels * bits_per_sample // 8)
                return f"{duration:.2f}"
            else:
                return "Could not determine duration"
                
    except Exception as e:
        return f"Error: {e}"

if len(sys.argv) != 2:
    print("Usage: python3 get_duration.py <wav_file>")
    sys.exit(1)

print(get_wav_duration(sys.argv[1]))