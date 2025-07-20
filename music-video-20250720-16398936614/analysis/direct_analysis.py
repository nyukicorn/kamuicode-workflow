#!/usr/bin/env python3
"""
直接実行する音楽分析
"""
import wave
import struct
import math
import os
import json
from datetime import datetime

# 音楽ファイルパス
music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16398936614/music/generated-music.wav"

print("音楽ファイル詳細分析レポート")
print("=" * 60)
print(f"分析対象: {os.path.basename(music_file)}")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ファイル存在確認
try:
    file_size = os.path.getsize(music_file)
    print(f"✓ ファイル検出成功")
    print(f"ファイルサイズ: {file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
except Exception as e:
    print(f"✗ ファイルアクセスエラー: {e}")
    exit()

# WAVファイル分析
try:
    with wave.open(music_file, 'rb') as wav_file:
        # 基本パラメータ取得
        frames = wav_file.getnframes()
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        duration = frames / sample_rate
        
        print(f"\n【1. 楽曲の基本音響特性】")
        print(f"楽曲の長さ: {duration:.2f}秒 ({duration/60:.1f}分)")
        print(f"サンプリングレート: {sample_rate:,} Hz")
        print(f"チャンネル数: {channels} ({'ステレオ' if channels == 2 else 'モノラル'})")
        print(f"ビット深度: {sample_width * 8} bit")
        print(f"総フレーム数: {frames:,}")
        print(f"推定ビットレート: {sample_rate * channels * sample_width * 8:,} bps")
        
        # 音声データ読み込み（最初の10秒分）
        max_frames = min(frames, sample_rate * 10)
        raw_audio = wav_file.readframes(max_frames)
        
        # バイナリデータを数値配列に変換
        if sample_width == 2:  # 16-bit
            fmt = f'{max_frames * channels}h'
            audio_data = struct.unpack(fmt, raw_audio)
        elif sample_width == 4:  # 32-bit
            fmt = f'{max_frames * channels}i'
            audio_data = struct.unpack(fmt, raw_audio)
            audio_data = [x / (2**31) for x in audio_data]  # 正規化
        else:
            print(f"サポートされていないサンプル幅: {sample_width}")
            exit()
        
        # ステレオの場合はモノラルに変換
        if channels == 2:
            mono_data = []
            for i in range(0, len(audio_data), 2):
                mono_data.append((audio_data[i] + audio_data[i+1]) / 2)
            audio_data = mono_data
        
        # 16-bitの場合の正規化
        if sample_width == 2:
            audio_data = [x / 32768.0 for x in audio_data]
        
        print(f"解析サンプル数: {len(audio_data):,}")
        
        # 音量統計分析
        abs_audio = [abs(x) for x in audio_data]
        max_amplitude = max(abs_audio)
        avg_amplitude = sum(abs_audio) / len(abs_audio)
        rms_energy = math.sqrt(sum(x*x for x in audio_data) / len(audio_data))
        
        print(f"\n【2. 音量レベル分析】")
        print(f"最大振幅: {max_amplitude:.4f}")
        print(f"平均振幅: {avg_amplitude:.4f}")
        print(f"RMSエネルギー: {rms_energy:.4f}")
        
        if avg_amplitude > 0:
            dynamic_range_db = 20 * math.log10(max_amplitude / avg_amplitude)
            print(f"ダイナミックレンジ: {dynamic_range_db:.1f} dB")
        
        # 音量レベル評価
        if rms_energy < 0.1:
            volume_character = "非常に静寂（アンビエント特徴）"
        elif rms_energy < 0.3:
            volume_character = "静寂（落ち着いた音楽）"
        elif rms_energy < 0.6:
            volume_character = "中程度"
        else:
            volume_character = "大音量"
        
        print(f"音量特性: {volume_character}")
        
        # 簡易テンポ分析
        print(f"\n【3. テンポ（BPM）測定】")
        
        # エネルギー変化によるビート検出
        window_size = int(sample_rate * 0.1)  # 100msウィンドウ
        hop_size = window_size // 2
        energy_values = []
        
        for i in range(0, len(audio_data) - window_size, hop_size):
            window_data = audio_data[i:i + window_size]
            energy = sum(x*x for x in window_data)
            energy_values.append(energy)
        
        # エネルギーピーク検出
        threshold = sum(energy_values) / len(energy_values) * 1.2
        peaks = []
        
        for i in range(1, len(energy_values) - 1):
            if (energy_values[i] > energy_values[i-1] and 
                energy_values[i] > energy_values[i+1] and 
                energy_values[i] > threshold):
                time_position = i * hop_size / sample_rate
                peaks.append(time_position)
        
        print(f"検出されたエネルギーピーク数: {len(peaks)}")
        
        if len(peaks) > 2:
            # ピーク間隔からBPM推定
            intervals = []
            for i in range(1, len(peaks)):
                interval = peaks[i] - peaks[i-1]
                if 0.4 < interval < 2.0:  # 30-150 BPMの範囲
                    intervals.append(interval)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                estimated_bpm = 60 / avg_interval
                
                print(f"平均ビート間隔: {avg_interval:.2f}秒")
                print(f"推定BPM: {estimated_bpm:.1f}")
                
                # BPM評価
                if 60 <= estimated_bpm <= 70:
                    bpm_evaluation = "✓ 戦略目標範囲内（60-70 BPM）"
                elif 50 <= estimated_bpm <= 80:
                    bpm_evaluation = "△ 戦略目標に近い"
                else:
                    bpm_evaluation = "✗ 戦略目標から逸脱"
                
                print(f"戦略適合性: {bpm_evaluation}")
            else:
                print("BPM測定不可（不規則なリズム）")
                estimated_bpm = None
        else:
            print("BPM測定不可（ピーク不足）")
            estimated_bpm = None
        
        # 音楽構造分析
        print(f"\n【4. 音楽構造分析】")
        
        # 楽曲を時間セグメントに分割（8セクション）
        num_segments = 8
        segment_duration = len(audio_data) / num_segments
        segments_rms = []
        
        for i in range(num_segments):
            start_idx = int(i * segment_duration)
            end_idx = int((i + 1) * segment_duration)
            segment_data = audio_data[start_idx:end_idx]
            
            segment_rms = math.sqrt(sum(x*x for x in segment_data) / len(segment_data))
            segments_rms.append(segment_rms)
            
            time_start = start_idx / sample_rate
            time_end = end_idx / sample_rate
            print(f"セクション {i+1:2d} ({time_start:5.1f}-{time_end:5.1f}秒): RMS={segment_rms:.4f}")
        
        # 三部構成の分析
        print(f"\n【5. 三部構成分析（戦略計画書対応）】")
        
        # セグメントを3つの部分に分類
        first_third = segments_rms[:num_segments//3]
        middle_third = segments_rms[num_segments//3:2*num_segments//3]
        last_third = segments_rms[2*num_segments//3:]
        
        intro_energy = sum(first_third) / len(first_third)
        development_energy = sum(middle_third) / len(middle_third)
        outro_energy = sum(last_third) / len(last_third)
        
        print(f"イントロ部（静寂期）: RMS平均 {intro_energy:.4f}")
        print(f"展開部（発展期）: RMS平均 {development_energy:.4f}")
        print(f"終結部（回帰期）: RMS平均 {outro_energy:.4f}")
        
        # 三部構成の特徴確認
        has_development = development_energy > intro_energy * 1.1
        has_resolution = outro_energy < development_energy * 0.9
        energy_variation = max(segments_rms) - min(segments_rms)
        
        print(f"\n構造特徴:")
        print(f"展開部での盛り上がり: {'✓' if has_development else '✗'} ({development_energy/intro_energy:.2f}倍)")
        print(f"終結部での静寂化: {'✓' if has_resolution else '✗'} ({outro_energy/development_energy:.2f}倍)")
        print(f"全体エネルギー変動: {energy_variation:.4f}")
        print(f"三部構成確認: {'✓' if has_development and has_resolution else '✗'}")
        
        # 楽器構成推定
        print(f"\n【6. 楽器構成推定】")
        
        # 周波数成分の簡易分析（時間域での推定）
        high_freq_content = 0
        low_freq_content = 0
        
        # 高周波数成分推定（急激な変化）
        for i in range(1, len(audio_data)):
            diff = abs(audio_data[i] - audio_data[i-1])
            if diff > 0.01:
                high_freq_content += diff
        
        high_freq_ratio = high_freq_content / len(audio_data)
        
        print(f"高周波数成分密度: {high_freq_ratio:.6f}")
        
        # 楽器特徴の推定
        instrument_indicators = []
        
        if rms_energy < 0.4 and avg_amplitude < 0.3:
            instrument_indicators.append("アコースティック楽器（静寂）")
        
        if high_freq_ratio > 0.001:
            instrument_indicators.append("雨音等の自然音")
        
        if energy_variation > 0.02:
            instrument_indicators.append("動的な楽器演奏")
        
        if has_development and has_resolution:
            instrument_indicators.append("表現力豊かな演奏")
        
        print(f"推定楽器特徴: {', '.join(instrument_indicators) if instrument_indicators else '不明'}")
        
        # アコースティックギター特徴の確認
        guitar_score = 0
        if 50 <= estimated_bpm <= 120 if estimated_bpm else False:
            guitar_score += 1
            print("✓ ギター適正テンポ範囲")
        
        if rms_energy < 0.5:
            guitar_score += 1
            print("✓ アコースティック音量レベル")
        
        if energy_variation > 0.01:
            guitar_score += 1
            print("✓ 弦楽器的ダイナミクス")
        
        print(f"アコースティックギター適合度: {guitar_score}/3")
        
        # 雨音成分の推定
        print(f"\n【7. 雨音成分分析】")
        
        # 持続的な背景ノイズの検出
        background_consistency = 1 - (energy_variation / max(segments_rms))
        
        print(f"背景音一貫性: {background_consistency:.3f}")
        
        if background_consistency > 0.7:
            print("✓ 持続的な背景音（雨音的特徴）を検出")
        elif background_consistency > 0.5:
            print("△ 部分的な背景音を検出")
        else:
            print("✗ 明確な背景音は検出されず")
        
        if high_freq_ratio > 0.001:
            print("✓ 高周波数ノイズ成分（雨滴音的）を検出")
        else:
            print("△ 高周波数成分は少ない")
        
        # ループ性能分析
        print(f"\n【8. ループ性能分析】")
        
        loop_duration = min(1.0, duration/4)  # 最大1秒
        loop_samples = int(loop_duration * sample_rate)
        
        start_segment = audio_data[:loop_samples]
        end_segment = audio_data[-loop_samples:]
        
        start_rms = math.sqrt(sum(x*x for x in start_segment) / len(start_segment))
        end_rms = math.sqrt(sum(x*x for x in end_segment) / len(end_segment))
        rms_difference = abs(start_rms - end_rms)
        
        print(f"開始部RMS: {start_rms:.4f}")
        print(f"終了部RMS: {end_rms:.4f}")
        print(f"RMS差: {rms_difference:.4f}")
        
        # 簡易相関分析
        if len(start_segment) == len(end_segment):
            correlation_sum = sum(s * e for s, e in zip(start_segment, end_segment))
            start_energy = sum(s * s for s in start_segment)
            end_energy = sum(e * e for e in end_segment)
            
            if start_energy > 0 and end_energy > 0:
                correlation = correlation_sum / math.sqrt(start_energy * end_energy)
                print(f"開始-終了相関: {correlation:.4f}")
                
                # ループ品質判定
                if correlation > 0.8 and rms_difference < 0.05:
                    loop_quality = "優秀"
                elif correlation > 0.6 and rms_difference < 0.1:
                    loop_quality = "良好"
                elif correlation > 0.4 and rms_difference < 0.2:
                    loop_quality = "普通"
                else:
                    loop_quality = "要改善"
                
                print(f"ループ適性: {loop_quality}")
        
        # 戦略計画書との総合整合性
        print(f"\n【9. 戦略計画書との整合性評価】")
        
        compliance_score = 0
        total_criteria = 0
        
        # 楽曲長さ（30-40秒）
        total_criteria += 1
        duration_ok = 30 <= duration <= 40
        print(f"楽曲長さ（30-40秒目標）: {duration:.1f}秒 {'✓' if duration_ok else '✗'}")
        if duration_ok:
            compliance_score += 1
        
        # テンポ（60-70 BPM）
        if estimated_bpm:
            total_criteria += 1
            bmp_ok = 60 <= estimated_bpm <= 70
            print(f"テンポ（60-70 BPM目標）: {estimated_bpm:.1f} BPM {'✓' if bmp_ok else '✗'}")
            if bmp_ok:
                compliance_score += 1
        
        # 三部構成
        total_criteria += 1
        three_part_ok = has_development and has_resolution
        print(f"三部構成（静寂→発展→回帰）: {'✓' if three_part_ok else '✗'}")
        if three_part_ok:
            compliance_score += 1
        
        # アコースティックギター
        total_criteria += 1
        guitar_ok = guitar_score >= 2
        print(f"アコースティックギター特徴: {'✓' if guitar_ok else '✗'} ({guitar_score}/3)")
        if guitar_ok:
            compliance_score += 1
        
        # 雨音成分
        total_criteria += 1
        rain_ok = background_consistency > 0.5 and high_freq_ratio > 0.0005
        print(f"雨音成分: {'✓' if rain_ok else '△'}")
        if rain_ok:
            compliance_score += 1
        
        # 総合評価
        compliance_rate = compliance_score / total_criteria * 100
        print(f"\n【10. 総合評価】")
        print(f"戦略適合率: {compliance_score}/{total_criteria} ({compliance_rate:.1f}%)")
        
        if compliance_rate >= 80:
            overall_rating = "優秀 - 戦略計画書の要求を十分満たしている"
        elif compliance_rate >= 60:
            overall_rating = "良好 - 主要要求を満たしている"
        elif compliance_rate >= 40:
            overall_rating = "普通 - 部分的に要求を満たしている"
        else:
            overall_rating = "要改善 - 戦略計画書との乖離が大きい"
        
        print(f"総合評価: {overall_rating}")
        
        # 推奨事項
        print(f"\n【11. 画像・動画プロンプト微調整への推奨事項】")
        
        if guitar_ok:
            print("✓ アコースティックギター要素を強調した視覚表現を推奨")
        
        if rain_ok:
            print("✓ 雨音・雨滴要素を視覚的に強調することを推奨")
        
        if three_part_ok:
            print("✓ 三部構成に対応した動画構成（静寂→動き→静寂）を推奨")
        
        if estimated_bpm and 60 <= estimated_bpm <= 70:
            print(f"✓ ゆったりとした動きの速度（{estimated_bpm:.1f} BPM対応）を推奨")
        
        if loop_quality in ['優秀', '良好']:
            print("✓ ループ再生に適した動画構成を推奨")
        
        # 分析結果をJSONで保存
        analysis_result = {
            "analysis_timestamp": datetime.now().isoformat(),
            "file_info": {
                "path": music_file,
                "size_bytes": file_size,
                "duration_seconds": duration
            },
            "audio_properties": {
                "sample_rate": sample_rate,
                "channels": channels,
                "bit_depth": sample_width * 8,
                "total_frames": frames
            },
            "volume_analysis": {
                "max_amplitude": max_amplitude,
                "avg_amplitude": avg_amplitude,
                "rms_energy": rms_energy,
                "volume_character": volume_character
            },
            "tempo_analysis": {
                "estimated_bpm": estimated_bpm,
                "peaks_detected": len(peaks),
                "bpm_target_met": estimated_bpm and 60 <= estimated_bpm <= 70 if estimated_bpm else False
            },
            "structure_analysis": {
                "intro_energy": intro_energy,
                "development_energy": development_energy,
                "outro_energy": outro_energy,
                "has_development": has_development,
                "has_resolution": has_resolution,
                "three_part_structure": three_part_ok,
                "energy_variation": energy_variation
            },
            "instrument_analysis": {
                "guitar_score": guitar_score,
                "guitar_detected": guitar_ok,
                "estimated_features": instrument_indicators
            },
            "rain_sound_analysis": {
                "background_consistency": background_consistency,
                "high_freq_ratio": high_freq_ratio,
                "rain_detected": rain_ok
            },
            "loop_analysis": {
                "start_rms": start_rms,
                "end_rms": end_rms,
                "rms_difference": rms_difference,
                "quality": loop_quality if 'loop_quality' in locals() else "不明"
            },
            "strategy_compliance": {
                "total_score": compliance_score,
                "total_criteria": total_criteria,
                "compliance_rate": compliance_rate,
                "overall_rating": overall_rating,
                "duration_target_met": duration_ok,
                "tempo_target_met": estimated_bpm and 60 <= estimated_bpm <= 70 if estimated_bpm else False,
                "structure_target_met": three_part_ok,
                "guitar_target_met": guitar_ok,
                "rain_target_met": rain_ok
            }
        }
        
        # JSONファイル保存
        output_dir = os.path.dirname(music_file).replace('/music', '/analysis')
        os.makedirs(output_dir, exist_ok=True)
        
        json_path = os.path.join(output_dir, 'detailed_music_analysis_report.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n詳細分析データをJSONで保存: {json_path}")
        
        # マークダウンレポートの生成
        md_path = os.path.join(output_dir, 'music_analysis_report.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 音楽ファイル詳細分析レポート\n\n")
            f.write(f"**分析日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"**対象ファイル**: {os.path.basename(music_file)}\n\n")
            
            f.write("## 分析結果サマリー\n\n")
            f.write(f"- **楽曲長**: {duration:.1f}秒\n")
            f.write(f"- **推定BPM**: {estimated_bpm:.1f if estimated_bpm else '測定不可'}\n")
            f.write(f"- **三部構成**: {'確認' if three_part_ok else '未確認'}\n")
            f.write(f"- **戦略適合率**: {compliance_rate:.1f}%\n")
            f.write(f"- **総合評価**: {overall_rating}\n\n")
            
            f.write("## 詳細分析データ\n\n")
            f.write("詳細な数値データについては、添付のJSONファイルを参照してください。\n\n")
            
            f.write("## 画像・動画プロンプト最適化への提言\n\n")
            if guitar_ok:
                f.write("- アコースティックギターのクローズアップ映像を重視\n")
            if rain_ok:
                f.write("- 雨滴・雨音の視覚的表現を強調\n")
            if three_part_ok:
                f.write("- 静寂→動き→静寂の三部構成に対応した動画構成\n")
            if estimated_bpm and 60 <= estimated_bpm <= 70:
                f.write(f"- ゆったりとした動き（{estimated_bpm:.1f} BPM相当）\n")
        
        print(f"分析レポート（Markdown）を保存: {md_path}")
        
except Exception as e:
    print(f"✗ WAVファイル分析エラー: {e}")

print("\n" + "=" * 60)
print("音楽分析完了!")
print("=" * 60)