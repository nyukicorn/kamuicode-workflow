#!/usr/bin/env python3
"""
実際の音響データ分析
Pythonの標準ライブラリを使用
"""

import wave
import struct
import math
import os
import json
from datetime import datetime

def analyze_actual_wav(file_path):
    """実際のWAVファイル分析"""
    
    print("🎵 実際の音楽ファイル分析開始")
    print("=" * 50)
    print(f"ファイルパス: {file_path}")
    print(f"分析開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ファイル存在確認
    try:
        file_size = os.path.getsize(file_path)
        print(f"✓ ファイル検出成功")
        print(f"ファイルサイズ: {file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
    except Exception as e:
        print(f"✗ ファイルアクセスエラー: {e}")
        return None
    
    # WAV分析開始
    try:
        with wave.open(file_path, 'rb') as wav:
            # 基本パラメータ取得
            frames = wav.getnframes()
            sample_rate = wav.getframerate()
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            
            # 楽曲長計算
            duration = frames / sample_rate
            
            print()
            print("【1. 基本音響特性】")
            print(f"楽曲の長さ: {duration:.2f}秒 ({duration/60:.2f}分)")
            print(f"サンプリングレート: {sample_rate:,} Hz")
            print(f"チャンネル数: {channels} ({'ステレオ' if channels == 2 else 'モノラル'})")
            print(f"ビット深度: {sample_width * 8} bit")
            print(f"総フレーム数: {frames:,}")
            print(f"推定ビットレート: {sample_rate * channels * sample_width * 8:,} bps")
            
            # 戦略計画書との基本比較
            print()
            print("【2. 戦略計画書基本適合性】")
            duration_ok = 30 <= duration <= 40
            quality_ok = sample_rate >= 44100 and sample_width >= 2
            
            print(f"楽曲長さ（30-40秒目標）: {duration:.1f}秒 {'✓' if duration_ok else '✗'}")
            print(f"音質基準（44.1kHz+/16bit+）: {sample_rate}Hz/{sample_width*8}bit {'✓' if quality_ok else '✗'}")
            
            # 音声データ読み込み（サンプリング）
            max_samples = min(frames, sample_rate * 15)  # 最大15秒分
            raw_audio = wav.readframes(max_samples)
            
            # バイナリデータを数値に変換
            if sample_width == 2:  # 16-bit
                fmt = f'{max_samples * channels}h'
                audio_data = list(struct.unpack(fmt, raw_audio))
            elif sample_width == 4:  # 32-bit
                fmt = f'{max_samples * channels}i'
                audio_data = [x / (2**31) for x in struct.unpack(fmt, raw_audio)]
            else:
                print(f"サポート外のサンプル幅: {sample_width}")
                return None
            
            # ステレオ→モノラル変換
            if channels == 2:
                mono_data = []
                for i in range(0, len(audio_data), 2):
                    mono_data.append((audio_data[i] + audio_data[i+1]) / 2)
                audio_data = mono_data
            
            # 16-bit正規化
            if sample_width == 2:
                audio_data = [x / 32768.0 for x in audio_data]
            
            # 音量統計
            abs_audio = [abs(x) for x in audio_data]
            max_amp = max(abs_audio)
            avg_amp = sum(abs_audio) / len(abs_audio)
            rms = math.sqrt(sum(x*x for x in audio_data) / len(audio_data))
            
            print()
            print("【3. 音量レベル詳細分析】")
            print(f"最大振幅: {max_amp:.4f}")
            print(f"平均振幅: {avg_amp:.4f}")
            print(f"RMS エネルギー: {rms:.4f}")
            
            if avg_amp > 0:
                dynamic_range_db = 20 * math.log10(max_amp / avg_amp)
                print(f"ダイナミックレンジ: {dynamic_range_db:.1f} dB")
            
            # 音量特性判定
            if rms < 0.1:
                volume_char = "静寂・アンビエント（瞑想的特徴）"
            elif rms < 0.3:
                volume_char = "穏やか（落ち着いた音楽）"
            elif rms < 0.6:
                volume_char = "中程度"
            else:
                volume_char = "大音量"
            
            print(f"音量特性: {volume_char}")
            
            # テンポ分析
            print()
            print("【4. テンポ（BPM）分析】")
            
            # エネルギー変化検出
            window_size = int(sample_rate * 0.1)  # 100ms
            hop_size = window_size // 2
            energies = []
            
            for i in range(0, len(audio_data) - window_size, hop_size):
                window = audio_data[i:i + window_size]
                energy = sum(x*x for x in window)
                energies.append(energy)
            
            # ピーク検出
            if len(energies) > 10:
                threshold = sum(energies) / len(energies) * 1.3
                peaks = []
                
                for i in range(1, len(energies) - 1):
                    if (energies[i] > energies[i-1] and 
                        energies[i] > energies[i+1] and 
                        energies[i] > threshold):
                        time_pos = i * hop_size / sample_rate
                        peaks.append(time_pos)
                
                print(f"検出エネルギーピーク数: {len(peaks)}")
                
                if len(peaks) > 2:
                    # ピーク間隔→BPM計算
                    intervals = []
                    for i in range(1, len(peaks)):
                        interval = peaks[i] - peaks[i-1]
                        if 0.3 < interval < 3.0:  # 20-200 BPM範囲
                            intervals.append(interval)
                    
                    if intervals:
                        avg_interval = sum(intervals) / len(intervals)
                        estimated_bpm = 60 / avg_interval
                        
                        print(f"平均ピーク間隔: {avg_interval:.2f}秒")
                        print(f"推定BPM: {estimated_bpm:.1f}")
                        
                        # 戦略目標との比較
                        bpm_ok = 60 <= estimated_bpm <= 70
                        print(f"戦略目標（60-70 BPM）適合: {'✓' if bmp_ok else '✗'}")
                    else:
                        print("BPM測定不可（不規則リズム）")
                        estimated_bpm = None
                else:
                    print("BPM測定不可（ピーク不足）")
                    estimated_bpm = None
            else:
                print("BPM測定不可（データ不足）")
                estimated_bpm = None
            
            # 構造分析
            print()
            print("【5. 音楽構造・三部構成分析】")
            
            # 楽曲を複数セクションに分割
            num_sections = 8
            section_length = len(audio_data) / num_sections
            section_rms = []
            
            for i in range(num_sections):
                start = int(i * section_length)
                end = int((i + 1) * section_length)
                section_data = audio_data[start:end]
                
                section_rms_val = math.sqrt(sum(x*x for x in section_data) / len(section_data))
                section_rms.append(section_rms_val)
                
                time_start = start / sample_rate
                time_end = end / sample_rate
                print(f"セクション{i+1:2d} ({time_start:5.1f}-{time_end:5.1f}秒): RMS={section_rms_val:.4f}")
            
            # 三部構成分析
            print()
            print("【三部構成詳細評価】")
            
            # 楽曲を3つの主要部分に分類
            third_size = num_sections // 3
            intro_sections = section_rms[:third_size]
            dev_sections = section_rms[third_size:2*third_size]
            outro_sections = section_rms[2*third_size:]
            
            intro_avg = sum(intro_sections) / len(intro_sections)
            dev_avg = sum(dev_sections) / len(dev_sections)
            outro_avg = sum(outro_sections) / len(outro_sections)
            
            print(f"第1部（イントロ）平均エネルギー: {intro_avg:.4f}")
            print(f"第2部（展開部）平均エネルギー: {dev_avg:.4f}")
            print(f"第3部（終結部）平均エネルギー: {outro_avg:.4f}")
            
            # 三部構成特徴
            has_development = dev_avg > intro_avg * 1.15
            has_resolution = outro_avg < dev_avg * 0.85
            energy_variation = max(section_rms) - min(section_rms)
            
            print()
            print(f"展開部での盛り上がり: {'✓' if has_development else '✗'} ({dev_avg/intro_avg:.2f}倍)")
            print(f"終結部での静寂回帰: {'✓' if has_resolution else '✗'} ({outro_avg/dev_avg:.2f}倍)")
            print(f"全体エネルギー変動幅: {energy_variation:.4f}")
            
            three_part_confirmed = has_development and has_resolution
            print(f"三部構成確認: {'✓' if three_part_confirmed else '✗'}")
            
            # 楽器特徴推定
            print()
            print("【6. 楽器構成推定分析】")
            
            # 高周波数成分（雨音推定）
            high_freq_changes = 0
            for i in range(1, min(len(audio_data), 10000)):
                if abs(audio_data[i] - audio_data[i-1]) > 0.005:
                    high_freq_changes += 1
            
            high_freq_ratio = high_freq_changes / min(len(audio_data), 10000)
            print(f"高周波数変動比率: {high_freq_ratio:.6f}")
            
            # 楽器特徴判定
            guitar_score = 0
            rain_score = 0
            
            # ギター特徴
            if estimated_bpm and 50 <= estimated_bpm <= 100:
                guitar_score += 1
                print("✓ ギター適正テンポ範囲")
            
            if rms < 0.5:
                guitar_score += 1
                print("✓ アコースティック音量レベル")
            
            if energy_variation > 0.02:
                guitar_score += 1
                print("✓ 弦楽器的ダイナミクス変化")
            
            # 雨音特徴
            if high_freq_ratio > 0.001:
                rain_score += 1
                print("✓ 高周波数ノイズ（雨音的特徴）")
            
            background_consistency = 1 - (energy_variation / max(section_rms))
            if background_consistency > 0.6:
                rain_score += 1
                print("✓ 持続的背景音（雨音的特徴）")
            
            print(f"アコースティックギター適合度: {guitar_score}/3")
            print(f"雨音成分適合度: {rain_score}/2")
            
            # ループ性能
            print()
            print("【7. ループ性能分析】")
            
            loop_duration = min(1.0, duration/4)
            loop_samples = int(loop_duration * sample_rate)
            
            start_loop = audio_data[:loop_samples]
            end_loop = audio_data[-loop_samples:]
            
            start_rms = math.sqrt(sum(x*x for x in start_loop) / len(start_loop))
            end_rms = math.sqrt(sum(x*x for x in end_loop) / len(end_loop))
            rms_diff = abs(start_rms - end_rms)
            
            print(f"開始部RMS: {start_rms:.4f}")
            print(f"終了部RMS: {end_rms:.4f}")
            print(f"RMS差: {rms_diff:.4f}")
            
            # 相関計算
            if len(start_loop) == len(end_loop):
                correlation_num = sum(s * e for s, e in zip(start_loop, end_loop))
                start_energy = sum(s * s for s in start_loop)
                end_energy = sum(e * e for e in end_loop)
                
                if start_energy > 0 and end_energy > 0:
                    correlation = correlation_num / math.sqrt(start_energy * end_energy)
                    print(f"開始-終了相関係数: {correlation:.4f}")
                    
                    # ループ品質判定
                    if correlation > 0.8 and rms_diff < 0.05:
                        loop_quality = "優秀"
                    elif correlation > 0.6 and rms_diff < 0.1:
                        loop_quality = "良好"
                    elif correlation > 0.4:
                        loop_quality = "普通"
                    else:
                        loop_quality = "要改善"
                    
                    print(f"ループ適性評価: {loop_quality}")
            
            # 総合評価
            print()
            print("【8. 戦略計画書総合適合性評価】")
            
            total_score = 0
            max_score = 0
            
            # 各項目評価
            checks = [
                ("楽曲長さ（30-40秒）", duration_ok, 1),
                ("音質基準", quality_ok, 1),
                ("三部構成", three_part_confirmed, 1),
                ("アコースティックギター", guitar_score >= 2, 1),
                ("雨音成分", rain_score >= 1, 1)
            ]
            
            if estimated_bpm:
                checks.append(("BPM範囲（60-70）", 60 <= estimated_bpm <= 70, 1))
            
            for check_name, passed, weight in checks:
                max_score += weight
                if passed:
                    total_score += weight
                print(f"{check_name}: {'✓' if passed else '✗'}")
            
            compliance_rate = (total_score / max_score) * 100
            print()
            print(f"戦略適合率: {total_score}/{max_score} ({compliance_rate:.1f}%)")
            
            # 最終評価
            if compliance_rate >= 90:
                final_rating = "A+ (優秀) - 戦略計画書要求を完全満足"
            elif compliance_rate >= 75:
                final_rating = "A (良好) - 主要要求を十分満足"
            elif compliance_rate >= 60:
                final_rating = "B (普通) - 基本要求を満足"
            else:
                final_rating = "C (要改善) - 追加調整が必要"
            
            print(f"最終評価: {final_rating}")
            
            # 結果保存
            result = {
                "analysis_timestamp": datetime.now().isoformat(),
                "file_info": {
                    "path": file_path,
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
                    "max_amplitude": max_amp,
                    "avg_amplitude": avg_amp,
                    "rms_energy": rms,
                    "volume_character": volume_char
                },
                "tempo_analysis": {
                    "estimated_bpm": estimated_bpm,
                    "peaks_detected": len(peaks) if 'peaks' in locals() else 0
                },
                "structure_analysis": {
                    "intro_energy": intro_avg,
                    "development_energy": dev_avg,
                    "outro_energy": outro_avg,
                    "three_part_structure": three_part_confirmed,
                    "energy_variation": energy_variation
                },
                "instrument_analysis": {
                    "guitar_score": guitar_score,
                    "rain_score": rain_score,
                    "high_freq_ratio": high_freq_ratio
                },
                "loop_analysis": {
                    "start_rms": start_rms,
                    "end_rms": end_rms,
                    "rms_difference": rms_diff,
                    "quality": loop_quality if 'loop_quality' in locals() else "不明"
                },
                "strategy_compliance": {
                    "total_score": total_score,
                    "max_score": max_score,
                    "compliance_rate": compliance_rate,
                    "final_rating": final_rating
                }
            }
            
            return result
            
    except Exception as e:
        print(f"✗ WAV分析エラー: {e}")
        return None

# 実行
if __name__ == "__main__":
    music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16398936614/music/generated-music.wav"
    
    result = analyze_actual_wav(music_file)
    
    if result:
        # JSON保存
        output_dir = os.path.dirname(music_file).replace('/music', '/analysis')
        os.makedirs(output_dir, exist_ok=True)
        
        json_path = os.path.join(output_dir, 'actual_music_analysis.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print()
        print("=" * 50)
        print(f"詳細分析データ保存: {json_path}")
        print("音楽分析完了!")
        print("=" * 50)
    else:
        print("分析に失敗しました。")

# 基本ファイル情報取得
music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16398936614/music/generated-music.wav"

print("🎵 基本ファイル情報取得")
print("=" * 30)

try:
    file_size = os.path.getsize(music_file)
    print(f"ファイルサイズ: {file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
    
    with wave.open(music_file, 'rb') as wav:
        frames = wav.getnframes()
        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        duration = frames / sample_rate
        
        print(f"楽曲長: {duration:.2f}秒")
        print(f"サンプリングレート: {sample_rate:,} Hz")
        print(f"チャンネル: {channels}")
        print(f"ビット深度: {sample_width * 8} bit")
        print(f"総フレーム数: {frames:,}")
        
        # 戦略適合性チェック
        print()
        print("戦略計画書適合性:")
        duration_ok = 30 <= duration <= 40
        quality_ok = sample_rate >= 44100 and sample_width >= 2
        
        print(f"楽曲長（30-40秒目標）: {duration:.1f}秒 {'✓' if duration_ok else '✗'}")
        print(f"音質基準: {sample_rate}Hz/{sample_width*8}bit {'✓' if quality_ok else '✗'}")
        
        # 基本情報をJSONで保存
        basic_info = {
            "timestamp": datetime.now().isoformat(),
            "file_path": music_file,
            "file_size_bytes": file_size,
            "duration_seconds": duration,
            "sample_rate": sample_rate,
            "channels": channels,
            "bit_depth": sample_width * 8,
            "total_frames": frames,
            "strategy_compliance": {
                "duration_target_met": duration_ok,
                "quality_target_met": quality_ok
            }
        }
        
        output_dir = os.path.dirname(music_file).replace('/music', '/analysis')
        os.makedirs(output_dir, exist_ok=True)
        
        basic_json_path = os.path.join(output_dir, 'basic_file_info.json')
        with open(basic_json_path, 'w', encoding='utf-8') as f:
            json.dump(basic_info, f, indent=2, ensure_ascii=False)
        
        print(f"\n基本情報保存: {basic_json_path}")
        print("=" * 30)
        
except Exception as e:
    print(f"エラー: {e}")