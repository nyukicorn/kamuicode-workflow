#!/usr/bin/env python3
"""
WAVファイルヘッダー直接解析
ファイルサイズと音楽長の正確な計算
"""

import struct
import os

def analyze_wav_header(file_path):
    """WAVファイルヘッダーを直接解析して詳細情報を取得"""
    try:
        # ファイルサイズ取得
        file_size = os.path.getsize(file_path)
        
        with open(file_path, 'rb') as f:
            # RIFFヘッダー読み取り (12 bytes)
            riff_header = f.read(12)
            if len(riff_header) < 12:
                return {'error': 'ファイルが小さすぎます'}
            
            # RIFF識別子確認
            riff_id = riff_header[:4]
            if riff_id != b'RIFF':
                return {'error': 'RIFFファイルではありません'}
            
            # ファイルサイズ（ヘッダー内）
            chunk_size = struct.unpack('<I', riff_header[4:8])[0]
            
            # WAVE識別子確認
            wave_id = riff_header[8:12]
            if wave_id != b'WAVE':
                return {'error': 'WAVEファイルではありません'}
            
            # fmtチャンク検索
            fmt_found = False
            data_found = False
            fmt_info = {}
            data_size = 0
            
            while True:
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break
                
                chunk_id = chunk_header[:4]
                chunk_data_size = struct.unpack('<I', chunk_header[4:8])[0]
                
                if chunk_id == b'fmt ':
                    # fmtチャンクデータ読み取り
                    fmt_data = f.read(chunk_data_size)
                    if len(fmt_data) >= 16:
                        # 基本fmt情報解析
                        audio_format = struct.unpack('<H', fmt_data[0:2])[0]
                        num_channels = struct.unpack('<H', fmt_data[2:4])[0]
                        sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
                        byte_rate = struct.unpack('<I', fmt_data[8:12])[0]
                        block_align = struct.unpack('<H', fmt_data[12:14])[0]
                        bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
                        
                        fmt_info = {
                            'audio_format': audio_format,
                            'num_channels': num_channels,
                            'sample_rate': sample_rate,
                            'byte_rate': byte_rate,
                            'block_align': block_align,
                            'bits_per_sample': bits_per_sample
                        }
                        fmt_found = True
                    
                    # 奇数サイズの場合のパディング調整
                    if chunk_data_size % 2 == 1:
                        f.read(1)
                
                elif chunk_id == b'data':
                    # dataチャンクサイズ記録
                    data_size = chunk_data_size
                    data_found = True
                    # dataの実際の内容はスキップ
                    f.seek(chunk_data_size, 1)
                    
                    # 奇数サイズの場合のパディング調整
                    if chunk_data_size % 2 == 1:
                        f.read(1)
                
                else:
                    # 他のチャンクはスキップ
                    f.seek(chunk_data_size, 1)
                    
                    # 奇数サイズの場合のパディング調整
                    if chunk_data_size % 2 == 1:
                        f.read(1)
            
            if not fmt_found or not data_found:
                return {'error': 'fmtまたはdataチャンクが見つかりません'}
            
            # 時間計算
            if fmt_info['byte_rate'] > 0:
                duration_seconds = data_size / fmt_info['byte_rate']
            else:
                # フォールバック計算
                bytes_per_sample = (fmt_info['bits_per_sample'] // 8) * fmt_info['num_channels']
                total_samples = data_size // bytes_per_sample
                duration_seconds = total_samples / fmt_info['sample_rate']
            
            return {
                'file_size': file_size,
                'chunk_size': chunk_size,
                'data_size': data_size,
                'duration_seconds': duration_seconds,
                'fmt_info': fmt_info,
                'audio_format_name': 'PCM' if fmt_info['audio_format'] == 1 else f'Format {fmt_info["audio_format"]}',
                'analysis_success': True
            }
            
    except Exception as e:
        return {'error': f'分析エラー: {str(e)}'}

def format_duration(seconds):
    """秒数を分:秒.ミリ秒形式でフォーマット"""
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:06.3f}"

def main():
    file_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16396927540/music/generated-music.wav"
    
    print("WAVファイルヘッダー解析")
    print("=" * 40)
    
    if not os.path.exists(file_path):
        print(f"エラー: ファイルが見つかりません - {file_path}")
        return
    
    result = analyze_wav_header(file_path)
    
    if 'error' in result:
        print(f"エラー: {result['error']}")
        return
    
    print("基本情報:")
    print(f"  ファイルサイズ: {result['file_size']:,} bytes ({result['file_size']/1024/1024:.2f} MB)")
    print(f"  音楽データサイズ: {result['data_size']:,} bytes")
    print(f"  楽曲時間: {result['duration_seconds']:.3f}秒 ({format_duration(result['duration_seconds'])})")
    
    print("\n音楽仕様:")
    fmt = result['fmt_info']
    print(f"  オーディオ形式: {result['audio_format_name']}")
    print(f"  チャンネル数: {fmt['num_channels']} ({'ステレオ' if fmt['num_channels'] == 2 else 'モノラル' if fmt['num_channels'] == 1 else f'{fmt[\"num_channels\"]}ch'})")
    print(f"  サンプルレート: {fmt['sample_rate']:,} Hz")
    print(f"  ビット深度: {fmt['bits_per_sample']} bit")
    print(f"  バイトレート: {fmt['byte_rate']:,} bytes/sec ({fmt['byte_rate']*8/1000:.1f} kbps)")
    print(f"  ブロックアライメント: {fmt['block_align']} bytes")
    
    print("\n戦略計画との比較:")
    print("  計画値: 35秒想定（30-40秒範囲）")
    print(f"  実測値: {result['duration_seconds']:.3f}秒")
    
    if 30 <= result['duration_seconds'] <= 40:
        status = "✅ 計画範囲内"
    elif 25 <= result['duration_seconds'] <= 45:
        status = "⚠️ 許容範囲内"
    else:
        status = "❌ 計画範囲外"
    
    print(f"  評価: {status}")
    
    # 差異計算
    diff = result['duration_seconds'] - 35
    print(f"  差異: {diff:+.3f}秒 ({diff/35*100:+.1f}%)")
    
    print("\n分析完了")

if __name__ == "__main__":
    main()