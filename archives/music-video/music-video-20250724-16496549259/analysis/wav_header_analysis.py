#!/usr/bin/env python3
"""
WAVファイルヘッダー解析スクリプト
バイナリレベルでのWAVファイル詳細情報抽出
"""

import struct
import os

def analyze_wav_header(file_path):
    """WAVファイルヘッダーの詳細解析"""
    
    print(f"WAVファイル詳細解析: {os.path.basename(file_path)}")
    print("=" * 60)
    
    try:
        with open(file_path, 'rb') as f:
            # RIFFヘッダー読み込み
            riff_header = f.read(12)
            if len(riff_header) < 12:
                print("エラー: ファイルが小さすぎます")
                return None
            
            # RIFF署名確認
            riff_signature = riff_header[:4]
            file_size = struct.unpack('<I', riff_header[4:8])[0]
            wave_signature = riff_header[8:12]
            
            print(f"RIFF署名: {riff_signature.decode('ascii', errors='ignore')}")
            print(f"ファイルサイズ: {file_size:,} バイト")
            print(f"WAVE署名: {wave_signature.decode('ascii', errors='ignore')}")
            
            # fmtチャンク検索と解析
            while True:
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break
                
                chunk_id = chunk_header[:4]
                chunk_size = struct.unpack('<I', chunk_header[4:8])[0]
                
                if chunk_id == b'fmt ':
                    # フォーマットチャンク解析
                    fmt_data = f.read(chunk_size)
                    if len(fmt_data) >= 16:
                        audio_format = struct.unpack('<H', fmt_data[0:2])[0]
                        num_channels = struct.unpack('<H', fmt_data[2:4])[0]
                        sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
                        byte_rate = struct.unpack('<I', fmt_data[8:12])[0]
                        block_align = struct.unpack('<H', fmt_data[12:14])[0]
                        bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
                        
                        print("\n--- フォーマット情報 ---")
                        print(f"オーディオフォーマット: {audio_format} ({'PCM' if audio_format == 1 else 'その他'})")
                        print(f"チャンネル数: {num_channels} ({'モノラル' if num_channels == 1 else 'ステレオ' if num_channels == 2 else 'マルチチャンネル'})")
                        print(f"サンプリングレート: {sample_rate:,} Hz")
                        print(f"バイトレート: {byte_rate:,} バイト/秒")
                        print(f"ブロックアライン: {block_align} バイト")
                        print(f"ビット深度: {bits_per_sample} bit")
                        
                elif chunk_id == b'data':
                    # データチャンク情報
                    data_size = chunk_size
                    current_pos = f.tell()
                    
                    print(f"\n--- データ情報 ---")
                    print(f"音声データサイズ: {data_size:,} バイト")
                    
                    # 既に取得した情報から時間計算
                    if 'sample_rate' in locals() and 'num_channels' in locals() and 'bits_per_sample' in locals():
                        bytes_per_sample = bits_per_sample // 8
                        total_samples = data_size // (num_channels * bytes_per_sample)
                        duration_seconds = total_samples / sample_rate
                        
                        print(f"総サンプル数: {total_samples:,}")
                        print(f"再生時間: {duration_seconds:.3f} 秒")
                        print(f"再生時間: {int(duration_seconds//60)}:{int(duration_seconds%60):02d}.{int((duration_seconds%1)*1000):03d}")
                    
                    # 最初と最後のサンプル値確認（振幅解析の参考）
                    if data_size > 0:
                        # 最初の数サンプル
                        first_samples = f.read(min(100, data_size))
                        f.seek(current_pos + max(0, data_size - 100))
                        last_samples = f.read(100)
                        
                        if bits_per_sample == 16:
                            # 16bit PCMの場合
                            first_values = []
                            for i in range(0, min(20, len(first_samples)), 2):
                                if i + 1 < len(first_samples):
                                    value = struct.unpack('<h', first_samples[i:i+2])[0]
                                    first_values.append(value)
                            
                            last_values = []
                            for i in range(0, min(20, len(last_samples)), 2):
                                if i + 1 < len(last_samples):
                                    value = struct.unpack('<h', last_samples[i:i+2])[0]
                                    last_values.append(value)
                            
                            print(f"\n--- 振幅分析 ---")
                            print(f"開始部サンプル値 (最初10個): {first_values[:10]}")
                            print(f"終了部サンプル値 (最後10個): {last_values[:10]}")
                            
                            # 動的範囲推定
                            if first_values:
                                max_amplitude = max(abs(min(first_values + last_values)), abs(max(first_values + last_values)))
                                dynamic_range_estimate = max_amplitude / 32768.0 * 100
                                print(f"推定最大振幅: {max_amplitude}/32768 ({dynamic_range_estimate:.1f}%)")
                    
                    break
                else:
                    # その他のチャンクはスキップ
                    f.seek(chunk_size, 1)
            
            # ファイル全体の統計
            actual_file_size = os.path.getsize(file_path)
            print(f"\n--- ファイル統計 ---")
            print(f"実際のファイルサイズ: {actual_file_size:,} バイト")
            print(f"ヘッダー記載サイズ: {file_size + 8:,} バイト")
            print(f"サイズ一致: {'✓' if actual_file_size == file_size + 8 else '✗'}")
            
            # 品質評価
            if 'sample_rate' in locals():
                print(f"\n--- 品質評価 ---")
                if sample_rate >= 44100:
                    print("✓ サンプリングレート: 高品質 (CD品質以上)")
                else:
                    print("⚠ サンプリングレート: 標準以下")
                
                if bits_per_sample >= 16:
                    print("✓ ビット深度: 高品質 (CD品質以上)")
                else:
                    print("⚠ ビット深度: 標準以下")
                
                if num_channels >= 2:
                    print("✓ ステレオ録音: 空間表現対応")
                else:
                    print("- モノラル録音")
            
            return {
                'sample_rate': sample_rate if 'sample_rate' in locals() else None,
                'channels': num_channels if 'num_channels' in locals() else None,
                'bits_per_sample': bits_per_sample if 'bits_per_sample' in locals() else None,
                'duration': duration_seconds if 'duration_seconds' in locals() else None,
                'file_size': actual_file_size,
                'data_size': data_size if 'data_size' in locals() else None
            }
            
    except Exception as e:
        print(f"解析エラー: {e}")
        return None

def main():
    file_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250724-16496549259/music/generated-music.wav"
    
    if not os.path.exists(file_path):
        print(f"ファイルが見つかりません: {file_path}")
        return
    
    result = analyze_wav_header(file_path)
    
    if result:
        print("\nヘッダー解析完了")
    else:
        print("\nヘッダー解析失敗")

if __name__ == "__main__":
    main()