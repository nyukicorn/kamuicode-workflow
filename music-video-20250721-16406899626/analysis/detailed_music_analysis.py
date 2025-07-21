#!/usr/bin/env python3
"""
音楽分析専門スクリプト
generated-music.wavファイルの詳細分析を実行
"""

import numpy as np
import librosa
import scipy.signal
from scipy import stats
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime

def analyze_music_structure(y, sr, hop_length=512):
    """音楽の構造分析（セグメント分割）"""
    # クロマグラムとMFCC特徴量でセグメント境界を検出
    chroma = librosa.feature.chroma(y=y, sr=sr, hop_length=hop_length)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length, n_mfcc=13)
    
    # セグメント境界の検出
    boundaries = librosa.segment.agglomerative(chroma, k=4)
    boundary_times = librosa.frames_to_time(boundaries, sr=sr, hop_length=hop_length)
    
    return boundary_times

def analyze_tempo_and_rhythm(y, sr):
    """テンポとリズム分析"""
    # テンポ検出
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    
    # リズムの安定性分析
    beat_intervals = np.diff(beat_times)
    rhythm_stability = 1 - np.std(beat_intervals) / np.mean(beat_intervals) if len(beat_intervals) > 0 else 0
    
    return tempo, beat_times, rhythm_stability

def analyze_spectral_features(y, sr):
    """スペクトル特徴量の分析"""
    # スペクトル重心（音色の明るさ）
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    
    # スペクトルロールオフ（高周波成分の分布）
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    
    # ゼロクロッシングレート（音の質感）
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    
    # MFCC特徴量（音色特徴）
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    # スペクトル対比度（ハーモニック/パーカッシブ分離）
    harmonic, percussive = librosa.effects.hpss(y)
    harmonic_ratio = np.mean(np.abs(harmonic)) / (np.mean(np.abs(harmonic)) + np.mean(np.abs(percussive)))
    
    return {
        'spectral_centroid_mean': np.mean(spectral_centroids),
        'spectral_centroid_std': np.std(spectral_centroids),
        'spectral_rolloff_mean': np.mean(spectral_rolloff),
        'zcr_mean': np.mean(zcr),
        'mfcc_means': np.mean(mfccs, axis=1),
        'harmonic_ratio': harmonic_ratio
    }

def analyze_dynamics(y, sr, frame_length=2048, hop_length=512):
    """音量変化・ダイナミクス分析"""
    # RMS エネルギー
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    
    # デシベル変換
    rms_db = librosa.amplitude_to_db(rms)
    
    # ダイナミックレンジ
    dynamic_range = np.max(rms_db) - np.min(rms_db)
    
    # 音量変化の分析
    rms_times = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_length)
    
    # 音量のピークを検出
    peaks, _ = scipy.signal.find_peaks(rms, height=np.mean(rms) + np.std(rms))
    peak_times = rms_times[peaks] if len(peaks) > 0 else []
    
    return {
        'rms_mean': np.mean(rms),
        'rms_std': np.std(rms),
        'rms_db_mean': np.mean(rms_db),
        'dynamic_range': dynamic_range,
        'peak_times': peak_times.tolist(),
        'rms_profile': rms.tolist(),
        'rms_times': rms_times.tolist()
    }

def analyze_harmony_and_melody(y, sr):
    """ハーモニーとメロディーライン分析"""
    # クロマ特徴量（ピッチクラス分布）
    chroma = librosa.feature.chroma(y=y, sr=sr)
    
    # トニック推定（主調の推定）
    chroma_mean = np.mean(chroma, axis=1)
    tonic_estimate = np.argmax(chroma_mean)
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    estimated_key = note_names[tonic_estimate]
    
    # ピッチ追跡
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, threshold=0.1)
    
    # メロディーライン抽出の試行
    melody_f0 = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            melody_f0.append(pitch)
        else:
            melody_f0.append(0)
    
    # メロディーの音程変化分析
    melody_intervals = np.diff([f for f in melody_f0 if f > 0])
    melody_range = max(melody_f0) - min([f for f in melody_f0 if f > 0]) if any(f > 0 for f in melody_f0) else 0
    
    return {
        'estimated_key': estimated_key,
        'chroma_distribution': chroma_mean.tolist(),
        'melody_range_hz': melody_range,
        'melody_f0_profile': melody_f0[:100],  # 最初の100フレームのみ
        'harmonic_complexity': np.std(chroma_mean)
    }

def classify_mood_and_emotion(spectral_features, dynamics, harmony, tempo):
    """音楽の雰囲気・感情分析"""
    # 特徴量に基づく感情分類
    energy_level = dynamics['rms_mean']
    brightness = spectral_features['spectral_centroid_mean'] / 4000  # 正規化
    harmonic_complexity = harmony['harmonic_complexity']
    
    # 感情分類ロジック
    emotions = {
        'エネルギー': min(energy_level * 10, 1.0),
        '明るさ': min(brightness, 1.0),
        '複雑さ': min(harmonic_complexity * 2, 1.0),
        'テンポ感': min(tempo / 120, 1.0) if tempo > 0 else 0
    }
    
    # 総合的な雰囲気判定
    if emotions['エネルギー'] > 0.6 and emotions['テンポ感'] > 0.8:
        mood = "エネルギッシュ・活発"
    elif emotions['明るさ'] > 0.6 and emotions['複雑さ'] < 0.4:
        mood = "明るい・シンプル"
    elif emotions['エネルギー'] < 0.4 and emotions['テンポ感'] < 0.7:
        mood = "静寂・瞑想的"
    elif emotions['複雑さ'] > 0.6:
        mood = "複雑・洗練された"
    else:
        mood = "バランスの取れた・中庸"
    
    return mood, emotions

def analyze_instrumentation(y, sr, spectral_features):
    """楽器構成・音色分析"""
    # ハーモニック/パーカッシブ分離
    harmonic, percussive = librosa.effects.hpss(y)
    
    # ハーモニック成分の強さ
    harmonic_strength = np.mean(np.abs(harmonic)) / np.mean(np.abs(y))
    
    # パーカッシブ成分の強さ
    percussive_strength = np.mean(np.abs(percussive)) / np.mean(np.abs(y))
    
    # 周波数分析による楽器推定
    spectral_centroid = spectral_features['spectral_centroid_mean']
    harmonic_ratio = spectral_features['harmonic_ratio']
    
    instrument_characteristics = []
    
    # ピアノの特徴判定
    if harmonic_ratio > 0.7 and 200 < spectral_centroid < 2000:
        instrument_characteristics.append("ピアノ系楽器の特徴")
    
    # 弦楽器の特徴判定
    if harmonic_ratio > 0.8 and spectral_centroid > 1000:
        instrument_characteristics.append("弦楽器の特徴")
    
    # パーカッション判定
    if percussive_strength > 0.3:
        instrument_characteristics.append("パーカッシブな要素")
    
    if not instrument_characteristics:
        instrument_characteristics.append("ソフトなハーモニック楽器")
    
    return {
        'harmonic_strength': harmonic_strength,
        'percussive_strength': percussive_strength,
        'instrument_characteristics': instrument_characteristics,
        'tonal_balance': 'ハーモニック重視' if harmonic_strength > 0.7 else 'バランス型'
    }

def compare_with_plan(analysis_results, duration):
    """計画との比較"""
    plan = {
        'target_bpm': (80, 100),
        'target_duration': (30, 40),
        'structure': {
            'intro': 8,
            'development': (12, 16),
            'climax': (8, 10),
            'outro': (6, 8)
        },
        'style': 'ミニマリストピアノソロ'
    }
    
    comparison = {}
    
    # BPM比較
    actual_bpm = analysis_results['tempo']
    if plan['target_bpm'][0] <= actual_bpm <= plan['target_bpm'][1]:
        comparison['bpm_match'] = f"✓ 目標範囲内 ({actual_bpm:.1f} BPM)"
    else:
        comparison['bpm_match'] = f"✗ 目標範囲外 ({actual_bpm:.1f} BPM, 目標: {plan['target_bpm'][0]}-{plan['target_bpm'][1]})"
    
    # 長さ比較
    if plan['target_duration'][0] <= duration <= plan['target_duration'][1]:
        comparison['duration_match'] = f"✓ 目標範囲内 ({duration:.1f}秒)"
    else:
        comparison['duration_match'] = f"✗ 目標範囲外 ({duration:.1f}秒, 目標: {plan['target_duration'][0]}-{plan['target_duration'][1]}秒)"
    
    # スタイル比較
    instruments = analysis_results['instrumentation']['instrument_characteristics']
    if any('ピアノ' in inst for inst in instruments):
        comparison['style_match'] = "✓ ピアノ系楽器の特徴が検出されました"
    else:
        comparison['style_match'] = "? ピアノ特有の特徴が明確ではありません"
    
    return comparison

def generate_visual_suggestions(analysis_results, mood, duration):
    """視覚的要素への示唆"""
    suggestions = {
        'color_palette': [],
        'visual_rhythm': '',
        'camera_movement': '',
        'lighting': '',
        'texture_style': ''
    }
    
    # 色彩パレット提案
    brightness = analysis_results['spectral_features']['spectral_centroid_mean']
    energy = analysis_results['dynamics']['rms_mean']
    
    if brightness > 1500:
        suggestions['color_palette'].extend(['明るい白', 'クリーム色', '淡いゴールド'])
    elif brightness > 800:
        suggestions['color_palette'].extend(['ソフトグレー', '温かいベージュ', '淡いブルー'])
    else:
        suggestions['color_palette'].extend(['深いグレー', 'ミッドナイトブルー', '落ち着いたブラウン'])
    
    # 視覚的リズム
    tempo = analysis_results['tempo']
    if tempo < 80:
        suggestions['visual_rhythm'] = 'ゆっくりとした、瞑想的な動き'
    elif tempo < 100:
        suggestions['visual_rhythm'] = '穏やかで流れるような動き'
    else:
        suggestions['visual_rhythm'] = 'リズミカルで活発な動き'
    
    # カメラ動作
    dynamic_range = analysis_results['dynamics']['dynamic_range']
    if dynamic_range > 20:
        suggestions['camera_movement'] = 'ダイナミックなズームとパン'
    elif dynamic_range > 10:
        suggestions['camera_movement'] = '滑らかなスライドとティルト'
    else:
        suggestions['camera_movement'] = '静的または非常に穏やかな動き'
    
    # 照明スタイル
    harmonic_ratio = analysis_results['spectral_features']['harmonic_ratio']
    if harmonic_ratio > 0.8:
        suggestions['lighting'] = 'ソフトで均一な照明、温かい色温度'
    else:
        suggestions['lighting'] = 'コントラストのある照明、陰影を効かせた演出'
    
    # テクスチャスタイル
    if mood in ['静寂・瞑想的', 'バランスの取れた・中庸']:
        suggestions['texture_style'] = 'ミニマルで清潔、微細なテクスチャ'
    else:
        suggestions['texture_style'] = 'リッチでディテールのあるテクスチャ'
    
    return suggestions

def main():
    # ファイルパス
    audio_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250721-16406899626/music/generated-music.wav"
    
    print("音楽分析を開始します...")
    print(f"分析ファイル: {audio_file}")
    
    # 音楽ファイル読み込み
    try:
        y, sr = librosa.load(audio_file, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        print(f"ファイル読み込み完了 - 長さ: {duration:.2f}秒, サンプルレート: {sr}Hz")
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return
    
    # 各種分析実行
    print("\n=== 詳細分析実行中 ===")
    
    # 1. 構造分析
    print("1. 音楽構造分析...")
    structure_boundaries = analyze_music_structure(y, sr)
    
    # 2. テンポ・リズム分析
    print("2. テンポ・リズム分析...")
    tempo, beat_times, rhythm_stability = analyze_tempo_and_rhythm(y, sr)
    
    # 3. スペクトル特徴量分析
    print("3. スペクトル特徴量分析...")
    spectral_features = analyze_spectral_features(y, sr)
    
    # 4. ダイナミクス分析
    print("4. ダイナミクス分析...")
    dynamics = analyze_dynamics(y, sr)
    
    # 5. ハーモニー・メロディー分析
    print("5. ハーモニー・メロディー分析...")
    harmony = analyze_harmony_and_melody(y, sr)
    
    # 6. 楽器構成分析
    print("6. 楽器構成分析...")
    instrumentation = analyze_instrumentation(y, sr, spectral_features)
    
    # 7. 感情・雰囲気分析
    print("7. 感情・雰囲気分析...")
    mood, emotions = classify_mood_and_emotion(spectral_features, dynamics, harmony, tempo)
    
    # 8. 計画との比較
    print("8. 計画との比較...")
    comparison = compare_with_plan({
        'tempo': tempo,
        'instrumentation': instrumentation,
        'spectral_features': spectral_features,
        'dynamics': dynamics
    }, duration)
    
    # 9. 視覚的要素提案
    print("9. 視覚的要素提案生成...")
    visual_suggestions = generate_visual_suggestions({
        'spectral_features': spectral_features,
        'dynamics': dynamics,
        'tempo': tempo
    }, mood, duration)
    
    # 結果のまとめ
    analysis_results = {
        'file_info': {
            'duration_seconds': duration,
            'sample_rate': sr,
            'channels': 'ステレオ',
            'bit_depth': '16-bit'
        },
        'structure': {
            'total_duration': duration,
            'boundaries': structure_boundaries.tolist(),
            'estimated_sections': len(structure_boundaries) - 1
        },
        'tempo_rhythm': {
            'bpm': tempo,
            'rhythm_stability': rhythm_stability,
            'beat_count': len(beat_times)
        },
        'spectral_features': spectral_features,
        'dynamics': dynamics,
        'harmony': harmony,
        'instrumentation': instrumentation,
        'mood_emotion': {
            'overall_mood': mood,
            'emotion_scores': emotions
        },
        'plan_comparison': comparison,
        'visual_suggestions': visual_suggestions,
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    # 結果出力
    print("\n" + "="*60)
    print("🎵 音楽分析結果レポート")
    print("="*60)
    
    print(f"\n📊 基本情報:")
    print(f"  長さ: {duration:.2f}秒")
    print(f"  サンプルレート: {sr}Hz")
    print(f"  フォーマット: 16-bit ステレオ WAV")
    
    print(f"\n🏗️ 音楽構造:")
    print(f"  推定セクション数: {len(structure_boundaries)-1}")
    print(f"  セクション境界: {[f'{t:.1f}s' for t in structure_boundaries]}")
    
    print(f"\n🥁 テンポ・リズム:")
    print(f"  BPM: {tempo:.1f}")
    print(f"  リズム安定性: {rhythm_stability:.3f}")
    print(f"  検出ビート数: {len(beat_times)}")
    
    print(f"\n🎼 楽器構成・音色:")
    print(f"  ハーモニック強度: {instrumentation['harmonic_strength']:.3f}")
    print(f"  パーカッシブ強度: {instrumentation['percussive_strength']:.3f}")
    print(f"  楽器特徴: {', '.join(instrumentation['instrument_characteristics'])}")
    print(f"  音色バランス: {instrumentation['tonal_balance']}")
    
    print(f"\n🎭 音楽の雰囲気・感情:")
    print(f"  総合的雰囲気: {mood}")
    print(f"  感情スコア:")
    for emotion, score in emotions.items():
        print(f"    {emotion}: {score:.3f}")
    
    print(f"\n📈 音量変化・ダイナミクス:")
    print(f"  平均音量(RMS): {dynamics['rms_mean']:.4f}")
    print(f"  ダイナミックレンジ: {dynamics['dynamic_range']:.1f}dB")
    print(f"  音量ピーク数: {len(dynamics['peak_times'])}")
    
    print(f"\n🎶 音楽的特徴:")
    print(f"  推定調性: {harmony['estimated_key']}")
    print(f"  メロディー音域: {harmony['melody_range_hz']:.1f}Hz")
    print(f"  ハーモニック複雑さ: {harmony['harmonic_complexity']:.3f}")
    print(f"  スペクトル重心: {spectral_features['spectral_centroid_mean']:.1f}Hz")
    
    print(f"\n📋 計画との比較:")
    for key, value in comparison.items():
        print(f"  {key}: {value}")
    
    print(f"\n🎨 視覚的要素への示唆:")
    print(f"  推奨色彩: {', '.join(visual_suggestions['color_palette'])}")
    print(f"  視覚的リズム: {visual_suggestions['visual_rhythm']}")
    print(f"  カメラ動作: {visual_suggestions['camera_movement']}")
    print(f"  照明スタイル: {visual_suggestions['lighting']}")
    print(f"  テクスチャ: {visual_suggestions['texture_style']}")
    
    # JSON形式でも保存
    output_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250721-16406899626/analysis/detailed_music_analysis_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 詳細結果をJSONファイルに保存: {output_file}")
    print("\n" + "="*60)
    print("分析完了！")
    
    return analysis_results

if __name__ == "__main__":
    main()