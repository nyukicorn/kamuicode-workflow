#!/usr/bin/env python3
"""
Comprehensive Music Analysis Script
音楽ファイルの詳細分析を行うスクリプト
"""

import wave
import os
import struct
import numpy as np
import sys
from pathlib import Path

def analyze_wav_file(file_path):
    """WAVファイルの詳細分析"""
    
    print("=" * 80)
    print("🎵 音楽ファイル詳細分析レポート")
    print("=" * 80)
    
    # ファイル存在確認
    if not os.path.exists(file_path):
        print(f"❌ エラー: ファイルが見つかりません: {file_path}")
        return
    
    # ファイル基本情報
    file_stats = os.stat(file_path)
    file_size_mb = file_stats.st_size / (1024 * 1024)
    
    print(f"📁 ファイルパス: {file_path}")
    print(f"📊 ファイルサイズ: {file_stats.st_size:,} バイト ({file_size_mb:.2f} MB)")
    print()
    
    try:
        # WAVファイルを開く
        with wave.open(file_path, 'rb') as wav_file:
            # 基本パラメータ取得
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            duration = frames / sample_rate
            
            print("🎼 基本音楽情報")
            print("-" * 40)
            print(f"⏱️  音楽の長さ: {duration:.2f} 秒 ({duration//60:.0f}分{duration%60:.1f}秒)")
            print(f"🔊 チャンネル数: {channels} ({'ステレオ' if channels == 2 else 'モノラル'})")
            print(f"📈 サンプリングレート: {sample_rate:,} Hz")
            print(f"🎚️  ビット深度: {sample_width * 8} ビット")
            print(f"🎵 総フレーム数: {frames:,}")
            print()
            
            # 音楽データ読み込み
            wav_file.rewind()
            raw_audio = wav_file.readframes(frames)
            
            # NumPy配列に変換
            if sample_width == 1:
                audio_data = np.frombuffer(raw_audio, dtype=np.uint8)
                audio_data = audio_data.astype(np.float32) - 128
            elif sample_width == 2:
                audio_data = np.frombuffer(raw_audio, dtype=np.int16)
                audio_data = audio_data.astype(np.float32)
            elif sample_width == 4:
                audio_data = np.frombuffer(raw_audio, dtype=np.int32)
                audio_data = audio_data.astype(np.float32)
            else:
                print(f"❌ サポートされていないサンプル幅: {sample_width}")
                return
            
            # ステレオの場合は2チャンネルに分離
            if channels == 2:
                audio_data = audio_data.reshape(-1, 2)
                left_channel = audio_data[:, 0]
                right_channel = audio_data[:, 1]
                # モノラル版を作成（分析用）
                mono_audio = np.mean(audio_data, axis=1)
            else:
                mono_audio = audio_data
                left_channel = audio_data
                right_channel = audio_data
            
            # 音量分析
            print("🔊 音量・ダイナミクス分析")
            print("-" * 40)
            
            # RMS（実効値）計算
            rms = np.sqrt(np.mean(mono_audio**2))
            
            # ピーク値
            peak = np.max(np.abs(mono_audio))
            
            # 動的範囲（dB）
            if sample_width == 2:
                max_amplitude = 32767
            elif sample_width == 1:
                max_amplitude = 127
            else:
                max_amplitude = 2147483647
            
            # dB変換
            if rms > 0:
                rms_db = 20 * np.log10(rms / max_amplitude)
            else:
                rms_db = -float('inf')
            
            if peak > 0:
                peak_db = 20 * np.log10(peak / max_amplitude)
            else:
                peak_db = -float('inf')
            
            print(f"📊 RMS レベル: {rms_db:.1f} dB")
            print(f"⚡ ピークレベル: {peak_db:.1f} dB")
            print(f"📈 ダイナミックレンジ: {peak_db - rms_db:.1f} dB")
            
            # ヘッドルーム計算
            headroom = -peak_db
            print(f"🎚️  ヘッドルーム: {headroom:.1f} dB")
            print()
            
            # 波形分析（セクション別）
            print("📈 波形構造分析")
            print("-" * 40)
            
            # 10秒単位でセクション分析
            section_length = 10 * sample_rate  # 10秒
            num_sections = int(np.ceil(len(mono_audio) / section_length))
            
            for i in range(min(num_sections, 5)):  # 最大5セクション
                start = i * section_length
                end = min((i + 1) * section_length, len(mono_audio))
                section = mono_audio[start:end]
                
                if len(section) > 0:
                    section_rms = np.sqrt(np.mean(section**2))
                    section_peak = np.max(np.abs(section))
                    
                    start_time = start / sample_rate
                    end_time = end / sample_rate
                    
                    if section_rms > 0:
                        section_rms_db = 20 * np.log10(section_rms / max_amplitude)
                    else:
                        section_rms_db = -float('inf')
                    
                    print(f"  {start_time:5.1f}s - {end_time:5.1f}s: RMS {section_rms_db:6.1f} dB")
            
            print()
            
            # テンポ推定（簡易版）
            print("🎵 音楽特性分析")
            print("-" * 40)
            
            # エネルギー変化によるテンポ推定
            # ウィンドウサイズ（0.1秒）
            window_size = int(0.1 * sample_rate)
            hop_size = int(0.05 * sample_rate)
            
            energy_profile = []
            for i in range(0, len(mono_audio) - window_size, hop_size):
                window = mono_audio[i:i + window_size]
                energy = np.sum(window**2)
                energy_profile.append(energy)
            
            energy_profile = np.array(energy_profile)
            
            # 差分を計算してビート検出
            energy_diff = np.diff(energy_profile)
            positive_diff = energy_diff[energy_diff > 0]
            
            if len(positive_diff) > 0:
                avg_energy_change = np.mean(positive_diff)
                energy_std = np.std(energy_profile)
                
                # 簡易テンポ推定
                # エネルギー変化の頻度から推定
                time_step = hop_size / sample_rate
                beat_candidates = []
                
                for i in range(1, len(energy_profile) - 1):
                    if (energy_profile[i] > energy_profile[i-1] and 
                        energy_profile[i] > energy_profile[i+1] and
                        energy_profile[i] > np.mean(energy_profile) + 0.5 * energy_std):
                        beat_candidates.append(i * time_step)
                
                if len(beat_candidates) > 1:
                    intervals = np.diff(beat_candidates)
                    if len(intervals) > 0:
                        avg_interval = np.median(intervals)
                        estimated_bpm = 60 / avg_interval if avg_interval > 0 else 0
                        
                        print(f"🥁 推定テンポ: {estimated_bpm:.0f} BPM")
                        
                        # テンポ範囲判定
                        if 60 <= estimated_bpm <= 80:
                            tempo_assessment = "✅ 想定範囲内（60-80 BPM）"
                        elif estimated_bpm < 60:
                            tempo_assessment = "⬇️  想定より遅い"
                        else:
                            tempo_assessment = "⬆️  想定より速い"
                        
                        print(f"📊 テンポ評価: {tempo_assessment}")
                    else:
                        print("🥁 推定テンポ: 検出できませんでした")
                else:
                    print("🥁 推定テンポ: ビートが不明瞭")
            
            print()
            
            # 周波数分析（簡易版）
            print("🎼 周波数特性分析")
            print("-" * 40)
            
            # FFTで周波数分析
            fft_size = min(8192, len(mono_audio))
            if fft_size > 0:
                # 中間部分を分析
                start_idx = len(mono_audio) // 2 - fft_size // 2
                analysis_segment = mono_audio[start_idx:start_idx + fft_size]
                
                fft_result = np.fft.fft(analysis_segment)
                freqs = np.fft.fftfreq(fft_size, 1/sample_rate)
                magnitude = np.abs(fft_result[:fft_size//2])
                freqs = freqs[:fft_size//2]
                
                # 周波数帯域別エネルギー
                bass_mask = (freqs >= 20) & (freqs <= 250)
                mid_mask = (freqs > 250) & (freqs <= 4000)
                treble_mask = (freqs > 4000) & (freqs <= 20000)
                
                bass_energy = np.sum(magnitude[bass_mask])
                mid_energy = np.sum(magnitude[mid_mask])
                treble_energy = np.sum(magnitude[treble_mask])
                total_energy = bass_energy + mid_energy + treble_energy
                
                if total_energy > 0:
                    bass_percent = (bass_energy / total_energy) * 100
                    mid_percent = (mid_energy / total_energy) * 100
                    treble_percent = (treble_energy / total_energy) * 100
                    
                    print(f"🎸 低域 (20-250 Hz): {bass_percent:.1f}%")
                    print(f"🎹 中域 (250-4000 Hz): {mid_percent:.1f}%")
                    print(f"✨ 高域 (4000-20000 Hz): {treble_percent:.1f}%")
                    
                    # 楽器構成推定
                    print()
                    print("🎼 推定楽器特性:")
                    if mid_percent > 50 and bass_percent < 30:
                        print("  ✅ アコースティックギター主体の特徴")
                    if treble_percent > 15 and mid_percent > 40:
                        print("  ✅ ピアノ系楽器の存在を示唆")
                    if bass_percent < 25:
                        print("  ✅ ソフトで穏やかな音響特性")
            
            print()
            
            # 音楽構造分析
            print("🏗️  音楽構造分析")
            print("-" * 40)
            
            # 1秒単位でRMSレベルの変化を分析
            section_duration = 1.0  # 1秒
            section_samples = int(section_duration * sample_rate)
            
            rms_timeline = []
            time_points = []
            
            for i in range(0, len(mono_audio), section_samples):
                section = mono_audio[i:i + section_samples]
                if len(section) > 0:
                    section_rms = np.sqrt(np.mean(section**2))
                    rms_timeline.append(section_rms)
                    time_points.append(i / sample_rate)
            
            rms_timeline = np.array(rms_timeline)
            
            if len(rms_timeline) > 2:
                # 構造の変化点を検出
                rms_diff = np.abs(np.diff(rms_timeline))
                threshold = np.std(rms_diff) * 1.5
                
                significant_changes = []
                for i, diff in enumerate(rms_diff):
                    if diff > threshold:
                        significant_changes.append(time_points[i + 1])
                
                print(f"⏱️  総時間: {duration:.1f}秒")
                
                # 構造推定
                if duration < 20:
                    print("📝 構造: ショートピース（イントロ的）")
                elif duration < 45:
                    print("📝 構造: 短編楽曲（イントロ-メイン構成推定）")
                else:
                    print("📝 構造: 標準楽曲構成")
                
                if len(significant_changes) > 0:
                    print("🔄 主要変化点:")
                    for i, change_time in enumerate(significant_changes[:3]):
                        print(f"   {change_time:.1f}秒")
                else:
                    print("🔄 構造: 安定した一様な構成")
            
            print()
            
            # 戦略計画との比較
            print("📋 戦略計画との比較検証")
            print("-" * 40)
            
            # 期待値
            expected_duration = (30, 40)  # 30-40秒
            expected_bpm = (60, 80)  # 60-80 BPM
            
            # 長さの比較
            if expected_duration[0] <= duration <= expected_duration[1]:
                duration_match = "✅ 想定範囲内"
            elif duration < expected_duration[0]:
                duration_match = f"⚠️  想定より短い ({expected_duration[0]-duration:.1f}秒不足)"
            else:
                duration_match = f"⚠️  想定より長い ({duration-expected_duration[1]:.1f}秒超過)"
            
            print(f"⏱️  長さ: {duration:.1f}秒 - {duration_match}")
            
            # 音響特性の評価
            if mid_percent > 45:
                instrument_match = "✅ アコースティックギター主体の特徴を確認"
            else:
                instrument_match = "⚠️  アコースティックギター特性が不明瞭"
            
            print(f"🎸 楽器構成: {instrument_match}")
            
            if rms_db > -20:
                volume_assessment = "⚠️  音量レベルが高め"
            elif rms_db < -40:
                volume_assessment = "⚠️  音量レベルが低め"
            else:
                volume_assessment = "✅ 適切な音量レベル"
            
            print(f"🔊 音量レベル: {volume_assessment}")
            
            # 総合評価
            print()
            print("🎯 総合評価")
            print("-" * 40)
            
            evaluation_score = 0
            total_criteria = 4
            
            if expected_duration[0] <= duration <= expected_duration[1]:
                evaluation_score += 1
                print("✅ 時間長: 適切")
            else:
                print("❌ 時間長: 調整必要")
            
            if mid_percent > 45:
                evaluation_score += 1
                print("✅ 音響特性: ギター主体を確認")
            else:
                print("❌ 音響特性: 楽器構成要確認")
            
            if -35 <= rms_db <= -15:
                evaluation_score += 1
                print("✅ 音量バランス: 適切")
            else:
                print("❌ 音量バランス: 調整推奨")
            
            if bass_percent < 30 and treble_percent < 40:
                evaluation_score += 1
                print("✅ 音色特性: ソフト・穏やか")
            else:
                print("❌ 音色特性: バランス要調整")
            
            match_percentage = (evaluation_score / total_criteria) * 100
            print()
            print(f"📊 戦略計画適合度: {evaluation_score}/{total_criteria} ({match_percentage:.0f}%)")
            
            if match_percentage >= 75:
                print("🎉 評価: 優秀 - 戦略計画に良く適合")
            elif match_percentage >= 50:
                print("👍 評価: 良好 - 概ね戦略計画に適合")
            else:
                print("⚠️  評価: 要改善 - 戦略計画との調整が必要")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        return
    
    print()
    print("=" * 80)
    print("✅ 分析完了")
    print("=" * 80)

if __name__ == "__main__":
    # 音楽ファイルのパス
    music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250722-16432802920/music/generated-music.wav"
    
    analyze_wav_file(music_file)