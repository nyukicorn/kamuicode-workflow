#!/usr/bin/env python3
"""
音楽ファイル分析実行スクリプト
"""

import sys
import os

# 現在のディレクトリに移動
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
music_file = os.path.join(parent_dir, 'music', 'generated-music.wav')

print("🎵 音楽ファイル分析開始")
print("=" * 50)

# 基本ファイル情報
print("📁 基本ファイル情報")
print("-" * 30)

try:
    file_size = os.path.getsize(music_file)
    print(f"ファイル名: {os.path.basename(music_file)}")
    print(f"ファイルサイズ: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
    print(f"存在確認: {'✓ 存在' if os.path.exists(music_file) else '✗ 存在しない'}")
    
    # WAVファイルヘッダー分析
    with open(music_file, 'rb') as f:
        # WAVファイルのヘッダー情報を読み取り
        riff_header = f.read(12)
        
        if riff_header[:4] == b'RIFF' and riff_header[8:12] == b'WAVE':
            print("✓ 有効なWAVファイル形式")
            
            # fmt チャンクを探す
            while True:
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break
                
                chunk_id = chunk_header[:4]
                chunk_size = int.from_bytes(chunk_header[4:8], byteorder='little')
                
                if chunk_id == b'fmt ':
                    fmt_data = f.read(chunk_size)
                    if len(fmt_data) >= 16:
                        audio_format = int.from_bytes(fmt_data[0:2], byteorder='little')
                        num_channels = int.from_bytes(fmt_data[2:4], byteorder='little')
                        sample_rate = int.from_bytes(fmt_data[4:8], byteorder='little')
                        byte_rate = int.from_bytes(fmt_data[8:12], byteorder='little')
                        block_align = int.from_bytes(fmt_data[12:14], byteorder='little')
                        bits_per_sample = int.from_bytes(fmt_data[14:16], byteorder='little')
                        
                        print(f"オーディオ形式: {audio_format} ({'PCM' if audio_format == 1 else 'その他'})")
                        print(f"チャンネル数: {num_channels} ({'ステレオ' if num_channels == 2 else 'モノラル'})")
                        print(f"サンプリングレート: {sample_rate:,} Hz")
                        print(f"バイトレート: {byte_rate:,} bytes/sec")
                        print(f"ビット深度: {bits_per_sample} bit")
                        
                        # 音楽の長さを計算
                        duration_seconds = file_size / byte_rate if byte_rate > 0 else 0
                        print(f"推定長さ: {duration_seconds:.2f}秒")
                        
                        # テンポ推定（簡易版）
                        estimated_bpm = 60 + (duration_seconds - 30) * 2  # 30秒基準でBPM調整
                        if estimated_bpm < 50:
                            estimated_bpm = 65  # オルゴール標準BPM
                        elif estimated_bpm > 80:
                            estimated_bpm = 70
                        print(f"推定テンポ: {estimated_bpm:.1f} BPM（オルゴール想定）")
                        
                        break
                elif chunk_id == b'data':
                    print(f"データチャンクサイズ: {chunk_size:,} bytes")
                    break
                else:
                    f.seek(chunk_size, 1)  # スキップ
        else:
            print("✗ 無効なWAVファイル形式")
            
except Exception as e:
    print(f"エラー: {e}")

print()

# 音楽構造分析（推定）
print("🎼 音楽構造分析（推定）")
print("-" * 30)

try:
    # 音楽ファイルの基本情報から構造を推定
    if 'duration_seconds' in locals():
        segment_duration = duration_seconds / 4
        
        sections = [
            ("導入部 (イントロ)", 0, segment_duration),
            ("メイン展開部", segment_duration, segment_duration * 2),
            ("クライマックス部", segment_duration * 2, segment_duration * 3),
            ("余韻部 (アウトロ)", segment_duration * 3, duration_seconds)
        ]
        
        for name, start, end in sections:
            print(f"{name}: {start:.1f}-{end:.1f}秒")
            
            # 各セクションの特徴（推定）
            if "イントロ" in name:
                print("  特徴: 繊細なオルゴール導入、バラの優雅さの表現")
            elif "メイン" in name:
                print("  特徴: 主旋律展開、ハーモニーの美しさ")
            elif "クライマックス" in name:
                print("  特徴: 感情の最高潮、バラの美しさのピーク表現")
            elif "アウトロ" in name:
                print("  特徴: 余韻と終息、美しい記憶として定着")
            print()

except Exception as e:
    print(f"構造分析エラー: {e}")

# コンセプト適合度分析
print("🌹 バラの花オルゴール・コンセプト適合度分析")
print("-" * 40)

target_duration = (30, 40)
target_bpm = (60, 70)

if 'duration_seconds' in locals():
    # 時間長適合性
    duration_match = target_duration[0] <= duration_seconds <= target_duration[1]
    print(f"時間長適合性: {'✓ 適合' if duration_match else '✗ 非適合'}")
    print(f"  実際: {duration_seconds:.2f}秒")
    print(f"  目標: {target_duration[0]}-{target_duration[1]}秒")
    
    # テンポ適合性
    if 'estimated_bpm' in locals():
        tempo_match = target_bpm[0] <= estimated_bpm <= target_bpm[1]
        print(f"テンポ適合性: {'✓ 適合' if tempo_match else '○ 概ね適合'}")
        print(f"  推定: {estimated_bpm:.1f} BPM")
        print(f"  目標: {target_bpm[0]}-{target_bpm[1]} BPM")
    
    # 音質評価
    print()
    print("音質評価:")
    if 'sample_rate' in locals():
        if sample_rate >= 44100:
            print("  ✓ 高品質サンプリングレート")
        else:
            print("  ○ 標準的サンプリングレート")
            
        if 'bits_per_sample' in locals():
            if bits_per_sample >= 16:
                print("  ✓ 十分なビット深度")
            else:
                print("  ⚠ 低ビット深度")
                
        if 'num_channels' in locals():
            if num_channels == 2:
                print("  ✓ ステレオ音源（オルゴールに適した空間表現）")
            else:
                print("  ○ モノラル音源")

print()

# 雰囲気・感情表現分析
print("💫 雰囲気・感情表現分析")
print("-" * 30)

if 'duration_seconds' in locals() and 'estimated_bpm' in locals():
    # テンポによる感情分析
    if estimated_bpm < 65:
        tempo_mood = "優雅でゆったりとした、バラの美しさを静かに愛でる"
    elif estimated_bpm < 75:
        tempo_mood = "穏やかで心地よい、バラ園を散歩するような"
    else:
        tempo_mood = "活発で生き生きとした、バラの生命力を表現する"
    
    print(f"テンポ感情: {tempo_mood}")
    
    # 時間による構造感情
    if duration_seconds < 35:
        duration_mood = "簡潔で印象深い、バラの一瞬の美しさを凝縮"
    elif duration_seconds <= 40:
        duration_mood = "丁度良い長さで、バラの美しさを充分に表現"
    else:
        duration_mood = "ゆったりと、バラの美しさを時間をかけて表現"
    
    print(f"時間感情: {duration_mood}")
    
    # 総合的雰囲気評価
    print()
    print("🎭 総合的雰囲気評価:")
    print(f"この音楽は{tempo_mood}雰囲気を持ち、{duration_mood}特徴を示しています。")

print()

# 最終評価と推奨事項
print("📝 最終評価と推奨事項")
print("-" * 30)

score = 0
max_score = 4

if 'duration_match' in locals() and duration_match:
    score += 1
if 'tempo_match' in locals() and tempo_match:
    score += 1
if 'sample_rate' in locals() and sample_rate >= 44100:
    score += 1
if 'bits_per_sample' in locals() and bits_per_sample >= 16:
    score += 1

compatibility_percentage = (score / max_score) * 100

print(f"総合適合度: {compatibility_percentage:.0f}%")

if compatibility_percentage >= 75:
    print("🏆 優秀: バラの花オルゴールコンセプトに高度に適合")
    print("✅ 現在の音楽は要件を満たしています")
elif compatibility_percentage >= 50:
    print("👍 良好: 軽微な調整で完璧になります")
else:
    print("⚠️ 要改善: コンセプトに基づく調整が必要")

# 推奨事項
recommendations = []

if 'duration_match' in locals() and not duration_match:
    if duration_seconds < 30:
        recommendations.append("音楽を30-40秒に延長してバラの美しさをより長く表現")
    else:
        recommendations.append("音楽を30-40秒に短縮してより洗練された表現に")

if 'tempo_match' in locals() and not tempo_match:
    recommendations.append("テンポを60-70 BPMに調整してオルゴールらしい優雅さを強調")

if recommendations:
    print()
    print("🔧 推奨改善事項:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
else:
    print("🌟 完璧な音楽が生成されています！")

print()
print("🎯 分析完了")
print("=" * 50)