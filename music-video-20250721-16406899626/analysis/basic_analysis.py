#!/usr/bin/env python3
"""
基本的な音楽ファイル分析
標準ライブラリとwaveモジュールを使用
"""

import wave
import os
import struct
import math

def basic_wav_analysis(filepath):
    """WAVファイルの基本分析"""
    try:
        # ファイル存在確認
        if not os.path.exists(filepath):
            return {"error": f"ファイルが見つかりません: {filepath}"}
        
        # ファイルサイズ
        file_size = os.path.getsize(filepath)
        
        # WAVファイル読み込み
        with wave.open(filepath, 'rb') as wav_file:
            # 基本パラメータ
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            
            # 長さ計算
            duration = frames / sample_rate
            
            # 全フレーム読み込み
            raw_audio = wav_file.readframes(frames)
            
        # 音声データ解析
        if sample_width == 2:  # 16-bit
            audio_data = struct.unpack(f'<{frames * channels}h', raw_audio)
        elif sample_width == 1:  # 8-bit
            audio_data = struct.unpack(f'<{frames * channels}B', raw_audio)
        else:
            audio_data = []
        
        # 基本統計
        if audio_data:
            max_amplitude = max(abs(x) for x in audio_data)
            rms = math.sqrt(sum(x*x for x in audio_data) / len(audio_data))
            dynamic_range_approx = max_amplitude / (rms + 1) if rms > 0 else 0
        else:
            max_amplitude = 0
            rms = 0
            dynamic_range_approx = 0
        
        # 構造推定（簡易版）
        # 音量レベルの変化を追跡して構造を推定
        segment_length = sample_rate * 2  # 2秒ごとのセグメント
        segments = []
        
        for i in range(0, len(audio_data), segment_length):
            segment = audio_data[i:i+segment_length]
            if segment:
                segment_rms = math.sqrt(sum(x*x for x in segment) / len(segment))
                segments.append(segment_rms)
        
        # 簡単なBPM推定（非常に粗い近似）
        # エネルギーピークの間隔を測定
        energy_peaks = []
        for i, rms in enumerate(segments):
            if i > 0 and i < len(segments) - 1:
                if rms > segments[i-1] and rms > segments[i+1]:
                    energy_peaks.append(i * 2)  # 時間（秒）
        
        estimated_bpm = 0
        if len(energy_peaks) > 1:
            avg_interval = sum(energy_peaks[i+1] - energy_peaks[i] for i in range(len(energy_peaks)-1)) / (len(energy_peaks)-1)
            if avg_interval > 0:
                estimated_bpm = 60 / avg_interval
        
        return {
            "file_info": {
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024*1024), 2),
                "duration_seconds": round(duration, 2),
                "sample_rate": sample_rate,
                "channels": channels,
                "sample_width_bytes": sample_width,
                "total_frames": frames
            },
            "audio_analysis": {
                "max_amplitude": max_amplitude,
                "rms_average": round(rms, 2),
                "dynamic_range_ratio": round(dynamic_range_approx, 2),
                "estimated_bpm": round(estimated_bpm, 1) if estimated_bpm > 0 else "推定不可",
                "energy_segments": len(segments),
                "energy_peaks_count": len(energy_peaks)
            },
            "structure_estimate": {
                "total_segments": len(segments),
                "peak_positions_seconds": energy_peaks,
                "estimated_intro_length": min(8, duration * 0.2),
                "estimated_outro_length": min(8, duration * 0.2)
            }
        }
        
    except Exception as e:
        return {"error": f"分析エラー: {str(e)}"}

def generate_comparison_report(analysis_result, target_specs):
    """分析結果と目標仕様の比較レポート"""
    report = []
    
    if "error" in analysis_result:
        return [f"❌ エラー: {analysis_result['error']}"]
    
    file_info = analysis_result["file_info"]
    audio_info = analysis_result["audio_analysis"]
    
    # 長さの比較
    duration = file_info["duration_seconds"]
    target_duration = target_specs.get("duration", (30, 40))
    if isinstance(target_duration, tuple):
        if target_duration[0] <= duration <= target_duration[1]:
            report.append(f"✅ 長さ: {duration}秒 (目標範囲: {target_duration[0]}-{target_duration[1]}秒)")
        else:
            report.append(f"⚠️ 長さ: {duration}秒 (目標範囲外: {target_duration[0]}-{target_duration[1]}秒)")
    else:
        report.append(f"📏 長さ: {duration}秒")
    
    # BPMの比較
    estimated_bpm = audio_info["estimated_bpm"]
    target_bpm = target_specs.get("bpm", (80, 100))
    if isinstance(estimated_bpm, (int, float)) and isinstance(target_bpm, tuple):
        if target_bpm[0] <= estimated_bpm <= target_bpm[1]:
            report.append(f"✅ BPM: {estimated_bpm} (目標範囲: {target_bpm[0]}-{target_bpm[1]})")
        else:
            report.append(f"⚠️ BPM: {estimated_bpm} (目標範囲外: {target_bpm[0]}-{target_bpm[1]})")
    else:
        report.append(f"🥁 BPM: {estimated_bpm}")
    
    # 品質指標
    report.append(f"🔊 音質: {file_info['sample_rate']}Hz, {file_info['sample_width_bytes']*8}bit, {'ステレオ' if file_info['channels']==2 else 'モノラル'}")
    report.append(f"📊 ダイナミクス比: {audio_info['dynamic_range_ratio']}")
    report.append(f"🎵 検出ピーク数: {audio_info['energy_peaks_count']}")
    
    return report

def main():
    # ファイルパス
    audio_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250721-16406899626/music/generated-music.wav"
    
    print("🎵 基本音楽分析実行中...")
    print(f"📁 ファイル: {audio_file}")
    print("-" * 60)
    
    # 分析実行
    result = basic_wav_analysis(audio_file)
    
    # 目標仕様
    target_specs = {
        "duration": (30, 40),  # 秒
        "bpm": (80, 100),      # BPM範囲
        "style": "ミニマリストピアノソロ"
    }
    
    # 結果表示
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    
    # 基本情報
    file_info = result["file_info"]
    audio_info = result["audio_analysis"]
    structure = result["structure_estimate"]
    
    print("📊 ファイル基本情報:")
    print(f"  ファイルサイズ: {file_info['file_size_mb']} MB")
    print(f"  長さ: {file_info['duration_seconds']} 秒")
    print(f"  サンプルレート: {file_info['sample_rate']} Hz")
    print(f"  チャンネル数: {file_info['channels']}")
    print(f"  ビット深度: {file_info['sample_width_bytes'] * 8} bit")
    
    print(f"\n🔍 音楽分析:")
    print(f"  最大振幅: {audio_info['max_amplitude']}")
    print(f"  RMS平均: {audio_info['rms_average']}")
    print(f"  ダイナミクス比: {audio_info['dynamic_range_ratio']}")
    print(f"  推定BPM: {audio_info['estimated_bpm']}")
    print(f"  エネルギーピーク数: {audio_info['energy_peaks_count']}")
    
    print(f"\n🏗️ 構造推定:")
    print(f"  分析セグメント数: {structure['total_segments']}")
    print(f"  ピーク位置: {structure['peak_positions_seconds']}")
    print(f"  推定イントロ長: {structure['estimated_intro_length']:.1f}秒")
    print(f"  推定アウトロ長: {structure['estimated_outro_length']:.1f}秒")
    
    print(f"\n📋 目標仕様との比較:")
    comparison = generate_comparison_report(result, target_specs)
    for item in comparison:
        print(f"  {item}")
    
    print(f"\n🎨 視覚的要素への示唆:")
    
    # 基本的な視覚提案
    duration = file_info['duration_seconds']
    estimated_bpm = audio_info.get('estimated_bpm', 90)
    
    if isinstance(estimated_bpm, (int, float)):
        if estimated_bpm < 80:
            visual_rhythm = "ゆっくりとした瞑想的な動き"
        elif estimated_bpm < 100:
            visual_rhythm = "穏やかで流れるような動き"
        else:
            visual_rhythm = "リズミカルな動き"
    else:
        visual_rhythm = "安定した穏やかな動き"
    
    print(f"  推奨視覚リズム: {visual_rhythm}")
    
    if duration < 35:
        print(f"  構成提案: コンパクトな3段構成（イントロ→展開→アウトロ）")
    else:
        print(f"  構成提案: 4段構成（イントロ→展開→クライマックス→アウトロ）")
    
    dynamic_ratio = audio_info.get('dynamic_range_ratio', 1)
    if dynamic_ratio > 3:
        print(f"  照明提案: ダイナミックな明暗変化")
    else:
        print(f"  照明提案: 柔らかく安定した照明")
    
    print(f"  色彩提案: ミニマルで清潔感のある色調")
    
    print("-" * 60)
    print("✅ 基本分析完了")

if __name__ == "__main__":
    main()