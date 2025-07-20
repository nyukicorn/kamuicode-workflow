#!/usr/bin/env python3
"""
基本的な音楽分析スクリプト
システムライブラリのみを使用した分析
"""

import wave
import struct
import math
import os
import json
from datetime import datetime

def analyze_wav_file(file_path):
    """WAVファイルの基本分析"""
    print(f"音楽ファイル基本分析: {file_path}")
    print("=" * 60)
    
    try:
        # WAVファイルを開く
        with wave.open(file_path, 'rb') as wav_file:
            # 基本パラメータを取得
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            
            # 楽曲の長さを計算
            duration = frames / sample_rate
            
            print(f"✓ ファイル読み込み成功")
            print(f"楽曲の長さ: {duration:.2f}秒 ({duration/60:.1f}分)")
            print(f"サンプリングレート: {sample_rate} Hz")
            print(f"チャンネル数: {channels}")
            print(f"サンプル幅: {sample_width} bytes")
            print(f"総フレーム数: {frames:,}")
            
            # 音声データを読み込む
            raw_audio = wav_file.readframes(frames)
            
            # バイナリデータを数値配列に変換
            if sample_width == 1:
                fmt = f'{frames * channels}B'
                audio_data = struct.unpack(fmt, raw_audio)
                audio_data = [(x - 128) / 128.0 for x in audio_data]  # -1.0 to 1.0に正規化
            elif sample_width == 2:
                fmt = f'{frames * channels}h'
                audio_data = struct.unpack(fmt, raw_audio)
                audio_data = [x / 32768.0 for x in audio_data]  # -1.0 to 1.0に正規化
            else:
                print(f"サポートされていないサンプル幅: {sample_width}")
                return None
            
            # モノラル変換（ステレオの場合）
            if channels == 2:
                mono_data = []
                for i in range(0, len(audio_data), 2):
                    mono_data.append((audio_data[i] + audio_data[i+1]) / 2)
                audio_data = mono_data
            
            print(f"処理されたサンプル数: {len(audio_data):,}")
            
            # 音量統計分析
            abs_audio = [abs(x) for x in audio_data]
            max_amplitude = max(abs_audio)
            avg_amplitude = sum(abs_audio) / len(abs_audio)
            
            # RMSエネルギー計算
            rms = math.sqrt(sum(x*x for x in audio_data) / len(audio_data))
            
            print(f"\n音量統計:")
            print(f"最大振幅: {max_amplitude:.4f}")
            print(f"平均振幅: {avg_amplitude:.4f}")
            print(f"RMSエネルギー: {rms:.4f}")
            
            # 動的レンジ推定
            if avg_amplitude > 0:
                dynamic_range_db = 20 * math.log10(max_amplitude / avg_amplitude)
                print(f"推定ダイナミックレンジ: {dynamic_range_db:.1f} dB")
            
            # 簡易テンポ分析（ピーク検出）
            print(f"\n簡易テンポ分析:")
            
            # 短時間エネルギー計算（100msウィンドウ）
            window_size = int(sample_rate * 0.1)  # 100ms
            energy_values = []
            
            for i in range(0, len(audio_data) - window_size, window_size // 2):
                window_data = audio_data[i:i + window_size]
                energy = sum(x*x for x in window_data) / len(window_data)
                energy_values.append(energy)
            
            # エネルギー変化からピークを検出
            peaks = []
            threshold = sum(energy_values) / len(energy_values) * 1.5  # 平均の1.5倍
            
            for i in range(1, len(energy_values) - 1):
                if (energy_values[i] > energy_values[i-1] and 
                    energy_values[i] > energy_values[i+1] and 
                    energy_values[i] > threshold):
                    peaks.append(i)
            
            if len(peaks) > 1:
                # ピーク間隔からテンポを推定
                peak_intervals = []
                for i in range(1, len(peaks)):
                    interval = (peaks[i] - peaks[i-1]) * (window_size // 2) / sample_rate
                    peak_intervals.append(interval)
                
                if peak_intervals:
                    avg_interval = sum(peak_intervals) / len(peak_intervals)
                    estimated_bpm = 60 / avg_interval if avg_interval > 0 else 0
                    print(f"検出されたピーク数: {len(peaks)}")
                    print(f"平均ピーク間隔: {avg_interval:.2f}秒")
                    print(f"推定BPM: {estimated_bpm:.1f}")
                else:
                    print("BPM推定不可（ピーク間隔が不規則）")
            else:
                print("BPM推定不可（十分なピークが検出されませんでした）")
            
            # 音楽構造の簡易分析
            print(f"\n音楽構造分析:")
            
            # 楽曲を時間セグメントに分割
            segment_duration = duration / 4  # 4つのセグメントに分割
            segments = []
            
            for i in range(4):
                start_sample = int(i * segment_duration * sample_rate)
                end_sample = int((i + 1) * segment_duration * sample_rate)
                if end_sample > len(audio_data):
                    end_sample = len(audio_data)
                
                segment_data = audio_data[start_sample:end_sample]
                segment_rms = math.sqrt(sum(x*x for x in segment_data) / len(segment_data))
                segments.append(segment_rms)
                
                print(f"セグメント {i+1} ({i*segment_duration:.1f}-{(i+1)*segment_duration:.1f}秒): RMS={segment_rms:.4f}")
            
            # 三部構成の評価
            if len(segments) >= 3:
                intro_energy = segments[0]
                development_energy = max(segments[1:-1]) if len(segments) > 2 else segments[1]
                outro_energy = segments[-1]
                
                print(f"\n三部構成分析:")
                print(f"イントロ部エネルギー: {intro_energy:.4f}")
                print(f"展開部最大エネルギー: {development_energy:.4f}")
                print(f"終結部エネルギー: {outro_energy:.4f}")
                
                # 三部構成の特徴判定
                has_development = development_energy > intro_energy * 1.2
                has_resolution = outro_energy < development_energy * 0.8
                
                print(f"展開部の盛り上がり: {'✓' if has_development else '✗'}")
                print(f"終結部の静寂化: {'✓' if has_resolution else '✗'}")
                
                three_part_structure = has_development and has_resolution
                print(f"三部構成の確認: {'✓' if three_part_structure else '✗'}")
            
            # ループ性能分析
            print(f"\nループ性能分析:")
            
            # 開始部と終了部の比較（各1秒）
            loop_duration = min(1.0, duration/4)
            loop_samples = int(loop_duration * sample_rate)
            
            start_segment = audio_data[:loop_samples]
            end_segment = audio_data[-loop_samples:]
            
            # RMS比較
            start_rms = math.sqrt(sum(x*x for x in start_segment) / len(start_segment))
            end_rms = math.sqrt(sum(x*x for x in end_segment) / len(end_segment))
            rms_difference = abs(start_rms - end_rms)
            
            print(f"開始部RMS: {start_rms:.4f}")
            print(f"終了部RMS: {end_rms:.4f}")
            print(f"RMS差: {rms_difference:.4f}")
            
            # 簡易相関計算
            if len(start_segment) == len(end_segment):
                correlation = sum(s * e for s, e in zip(start_segment, end_segment))
                correlation /= math.sqrt(sum(s*s for s in start_segment) * sum(e*e for e in end_segment))
                print(f"開始-終了相関係数: {correlation:.4f}")
                
                # ループ品質判定
                if correlation > 0.7 and rms_difference < 0.1:
                    loop_quality = "優秀"
                elif correlation > 0.5 and rms_difference < 0.2:
                    loop_quality = "良好"
                elif correlation > 0.3:
                    loop_quality = "普通"
                else:
                    loop_quality = "要改善"
                
                print(f"ループ適性: {loop_quality}")
            
            # 戦略計画書との整合性
            print(f"\n戦略計画書との整合性チェック:")
            
            # 長さチェック（30-40秒）
            duration_ok = 30 <= duration <= 40
            print(f"楽曲長さ（30-40秒目標）: {duration:.1f}秒 {'✓' if duration_ok else '✗'}")
            
            # BPMチェック（60-70）
            if 'estimated_bpm' in locals() and estimated_bpm > 0:
                bpm_ok = 60 <= estimated_bpm <= 70
                print(f"BPM（60-70目標）: {estimated_bpm:.1f} {'✓' if bpm_ok else '✗'}")
            else:
                print(f"BPM（60-70目標）: 測定不可 ✗")
            
            # 三部構成チェック
            if 'three_part_structure' in locals():
                print(f"三部構成: {'✓' if three_part_structure else '✗'}")
            
            # 結果をJSON形式で保存
            analysis_result = {
                "timestamp": datetime.now().isoformat(),
                "file_path": file_path,
                "basic_properties": {
                    "duration_seconds": duration,
                    "sample_rate": sample_rate,
                    "channels": channels,
                    "sample_width": sample_width,
                    "total_frames": frames
                },
                "volume_analysis": {
                    "max_amplitude": max_amplitude,
                    "avg_amplitude": avg_amplitude,
                    "rms_energy": rms,
                    "dynamic_range_db": dynamic_range_db if 'dynamic_range_db' in locals() else None
                },
                "tempo_analysis": {
                    "peaks_detected": len(peaks) if 'peaks' in locals() else 0,
                    "estimated_bpm": estimated_bpm if 'estimated_bpm' in locals() else None
                },
                "structure_analysis": {
                    "segments": len(segments),
                    "segment_energies": segments,
                    "three_part_structure": three_part_structure if 'three_part_structure' in locals() else False
                },
                "loop_analysis": {
                    "start_rms": start_rms,
                    "end_rms": end_rms,
                    "rms_difference": rms_difference,
                    "correlation": correlation if 'correlation' in locals() else None,
                    "quality": loop_quality if 'loop_quality' in locals() else "不明"
                },
                "strategy_compliance": {
                    "duration_target_met": duration_ok,
                    "bpm_target_met": bmp_ok if 'bpm_ok' in locals() else False,
                    "three_part_structure": three_part_structure if 'three_part_structure' in locals() else False
                }
            }
            
            return analysis_result
            
    except Exception as e:
        print(f"✗ ファイル分析エラー: {e}")
        return None

if __name__ == "__main__":
    # ファイルパス
    music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16398936614/music/generated-music.wav"
    
    # 分析実行
    result = analyze_wav_file(music_file)
    
    if result:
        # JSON結果を保存
        output_dir = os.path.dirname(music_file).replace('/music', '/analysis')
        os.makedirs(output_dir, exist_ok=True)
        
        json_path = os.path.join(output_dir, 'basic_music_analysis.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n分析結果をJSONで保存: {json_path}")
        print("="*60)
        print("基本分析完了!")
        print("="*60)
    else:
        print("分析に失敗しました。")