#!/usr/bin/env python3
"""
音楽ファイル詳細分析スクリプト
生成された音楽ファイルの基本情報、音楽的特徴、構造分析を実施
"""

import wave
import numpy as np
import os
import sys
from pathlib import Path

def analyze_wav_file(file_path):
    """WAVファイルの基本情報分析"""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            # 基本情報取得
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            
            # 時間計算
            duration = frames / sample_rate
            
            # 音声データ読み込み
            raw_audio = wav_file.readframes(frames)
            
            # numpy配列に変換
            if sample_width == 1:
                audio_data = np.frombuffer(raw_audio, dtype=np.uint8)
            elif sample_width == 2:
                audio_data = np.frombuffer(raw_audio, dtype=np.int16)
            elif sample_width == 4:
                audio_data = np.frombuffer(raw_audio, dtype=np.int32)
            else:
                audio_data = np.frombuffer(raw_audio, dtype=np.float32)
            
            # ステレオの場合、チャンネル分離
            if channels == 2:
                audio_data = audio_data.reshape(-1, 2)
            
            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': channels,
                'sample_width': sample_width,
                'frames': frames,
                'audio_data': audio_data
            }
    except Exception as e:
        return {'error': str(e)}

def analyze_amplitude_structure(audio_data, sample_rate, duration):
    """振幅分析による楽曲構造分析"""
    if len(audio_data.shape) == 2:  # ステレオの場合
        # モノラルに変換（左右平均）
        mono_audio = np.mean(audio_data, axis=1)
    else:
        mono_audio = audio_data
    
    # 正規化
    mono_audio = mono_audio.astype(np.float32) / np.max(np.abs(mono_audio))
    
    # 時間軸作成
    time_axis = np.linspace(0, duration, len(mono_audio))
    
    # セグメント分析（1秒ごと）
    segment_length = sample_rate  # 1秒分のサンプル数
    segments = []
    
    for i in range(0, len(mono_audio), segment_length):
        segment = mono_audio[i:i+segment_length]
        if len(segment) > 0:
            rms = np.sqrt(np.mean(segment**2))  # RMS（平均二乗平方根）
            peak = np.max(np.abs(segment))     # ピーク値
            segments.append({
                'start_time': i / sample_rate,
                'end_time': min((i + segment_length) / sample_rate, duration),
                'rms': rms,
                'peak': peak
            })
    
    return segments

def estimate_tempo_basic(audio_data, sample_rate):
    """基本的なテンポ推定（周波数分析）"""
    if len(audio_data.shape) == 2:
        mono_audio = np.mean(audio_data, axis=1)
    else:
        mono_audio = audio_data
    
    # 正規化
    mono_audio = mono_audio.astype(np.float32) / np.max(np.abs(mono_audio))
    
    # FFTによる周波数分析
    fft = np.fft.fft(mono_audio)
    freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
    
    # 低周波数帯域でのピーク検出（リズム成分）
    low_freq_mask = (freqs >= 0.5) & (freqs <= 8.0)  # 0.5-8 Hz (30-480 BPM範囲)
    low_freq_fft = np.abs(fft[low_freq_mask])
    low_freqs = freqs[low_freq_mask]
    
    if len(low_freq_fft) > 0:
        peak_idx = np.argmax(low_freq_fft)
        dominant_freq = low_freqs[peak_idx]
        estimated_bpm = dominant_freq * 60  # Hz to BPM
        return max(30, min(200, estimated_bpm))  # 30-200 BPMに制限
    
    return None

def detect_sections(segments):
    """楽曲セクション検出"""
    if not segments:
        return []
    
    # RMS値による動的変化検出
    rms_values = [seg['rms'] for seg in segments]
    rms_mean = np.mean(rms_values)
    rms_std = np.std(rms_values)
    
    sections = []
    current_section = {'start': 0, 'type': 'intro', 'intensity': 'low'}
    
    for i, segment in enumerate(segments):
        if segment['rms'] > rms_mean + rms_std:
            section_type = 'climax'
            intensity = 'high'
        elif segment['rms'] > rms_mean:
            section_type = 'development'
            intensity = 'medium'
        else:
            section_type = 'quiet'
            intensity = 'low'
        
        # セクション変化検出
        if current_section['type'] != section_type:
            current_section['end'] = segment['start_time']
            sections.append(current_section)
            current_section = {
                'start': segment['start_time'],
                'type': section_type,
                'intensity': intensity
            }
    
    # 最後のセクション終了
    current_section['end'] = segments[-1]['end_time']
    sections.append(current_section)
    
    return sections

def main():
    # ファイルパス設定
    music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16396927540/music/generated-music.wav"
    
    print("音楽ファイル詳細分析開始")
    print("=" * 50)
    
    # ファイル存在確認
    if not os.path.exists(music_file):
        print(f"エラー: ファイルが見つかりません - {music_file}")
        return
    
    # 基本情報分析
    print("1. 基本情報分析")
    basic_info = analyze_wav_file(music_file)
    
    if 'error' in basic_info:
        print(f"分析エラー: {basic_info['error']}")
        return
    
    print(f"  時間: {basic_info['duration']:.2f}秒")
    print(f"  サンプルレート: {basic_info['sample_rate']} Hz")
    print(f"  チャンネル数: {basic_info['channels']} ({'ステレオ' if basic_info['channels'] == 2 else 'モノラル'})")
    print(f"  ビット深度: {basic_info['sample_width'] * 8} bit")
    print(f"  フレーム数: {basic_info['frames']:,}")
    
    # 振幅構造分析
    print("\n2. 振幅構造分析")
    segments = analyze_amplitude_structure(
        basic_info['audio_data'], 
        basic_info['sample_rate'], 
        basic_info['duration']
    )
    
    for i, seg in enumerate(segments):
        print(f"  セグメント {i+1}: {seg['start_time']:.1f}-{seg['end_time']:.1f}秒 "
              f"RMS={seg['rms']:.4f} Peak={seg['peak']:.4f}")
    
    # テンポ推定
    print("\n3. テンポ推定")
    estimated_bpm = estimate_tempo_basic(basic_info['audio_data'], basic_info['sample_rate'])
    if estimated_bpm:
        print(f"  推定BPM: {estimated_bpm:.1f}")
    else:
        print("  テンポ推定不可")
    
    # セクション検出
    print("\n4. 楽曲構造分析")
    sections = detect_sections(segments)
    for i, section in enumerate(sections):
        print(f"  セクション {i+1}: {section['start']:.1f}-{section['end']:.1f}秒 "
              f"タイプ={section['type']} 強度={section['intensity']}")
    
    # 計画との比較
    print("\n5. 戦略計画との比較")
    print("  計画値:")
    print("    - 想定時間: 35秒")
    print("    - 想定BPM: 60-70")
    print("    - 想定キー: A minor")
    print("    - 想定構造: イントロ(8秒)→Aメロ(14秒)→Bメロ転換(8秒)→アウトロ(5秒)")
    
    print("  実測値:")
    print(f"    - 実際時間: {basic_info['duration']:.2f}秒 ({'✓' if 30 <= basic_info['duration'] <= 40 else '⚠️'})")
    if estimated_bpm:
        print(f"    - 実際BPM: {estimated_bpm:.1f} ({'✓' if 60 <= estimated_bpm <= 70 else '⚠️'})")
    print(f"    - 実際構造: {len(sections)}セクション検出")
    
    print("\n分析完了")

if __name__ == "__main__":
    main()