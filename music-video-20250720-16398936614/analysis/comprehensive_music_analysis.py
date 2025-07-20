#!/usr/bin/env python3
"""
包括的音楽分析スクリプト
生成された音楽ファイルの詳細分析を実行します
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import os
import json
from datetime import datetime

def analyze_music_file(file_path):
    """音楽ファイルの包括的分析"""
    print(f"音楽ファイル分析開始: {file_path}")
    print("=" * 60)
    
    # 音楽ファイルの読み込み
    try:
        y, sr = librosa.load(file_path, sr=None)
        print(f"✓ ファイル読み込み成功")
    except Exception as e:
        print(f"✗ ファイル読み込みエラー: {e}")
        return None
    
    # 基本的な音響特性
    duration = len(y) / sr
    print(f"楽曲の長さ: {duration:.2f}秒 ({duration/60:.1f}分)")
    print(f"サンプリングレート: {sr} Hz")
    print(f"チャンネル: モノラル")
    print(f"総サンプル数: {len(y):,}")
    
    # 音量統計
    rms_energy = librosa.feature.rms(y=y)[0]
    avg_rms = np.mean(rms_energy)
    max_rms = np.max(rms_energy)
    min_rms = np.min(rms_energy)
    
    print(f"\n音量統計:")
    print(f"平均RMSエネルギー: {avg_rms:.4f}")
    print(f"最大RMSエネルギー: {max_rms:.4f}")
    print(f"最小RMSエネルギー: {min_rms:.4f}")
    print(f"ダイナミックレンジ: {20 * np.log10(max_rms/min_rms):.1f} dB")
    
    # テンポ分析
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    print(f"\nテンポ分析:")
    print(f"推定BPM: {tempo:.1f}")
    print(f"検出されたビート数: {len(beats)}")
    
    # より詳細なテンポ分析
    onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
    tempo_histogram = librosa.beat.tempo(onset_envelope=onset_envelope, sr=sr, max_tempo=200)
    print(f"テンポヒストグラム（上位3つ）: {tempo_histogram[:3]}")
    
    # 音楽構造分析
    print(f"\n音楽構造分析:")
    
    # セグメント分析（構造境界の検出）
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    boundaries = librosa.segment.agglomerative(chroma, k=4)
    segment_times = librosa.frames_to_time(boundaries, sr=sr)
    
    print(f"検出された構造境界: {len(boundaries)-1}個")
    for i, time in enumerate(segment_times):
        if i == 0:
            print(f"  セグメント {i+1}: 0.00 - {time:.1f}秒")
        elif i < len(segment_times)-1:
            print(f"  セグメント {i+1}: {segment_times[i-1]:.1f} - {time:.1f}秒")
        else:
            print(f"  セグメント {i+1}: {segment_times[i-1]:.1f} - {duration:.1f}秒")
    
    # 推測される楽曲構造
    if len(segment_times) >= 3:
        intro_end = segment_times[0]
        development_end = segment_times[-2] if len(segment_times) > 2 else segment_times[-1]
        
        print(f"\n推測される三部構成:")
        print(f"  イントロ部: 0.00 - {intro_end:.1f}秒 ({intro_end:.1f}秒間)")
        print(f"  展開部: {intro_end:.1f} - {development_end:.1f}秒 ({development_end-intro_end:.1f}秒間)")
        print(f"  終結部: {development_end:.1f} - {duration:.1f}秒 ({duration-development_end:.1f}秒間)")
    
    # スペクトル分析
    print(f"\nスペクトル分析:")
    
    # メル周波数ケプストラム係数
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    print(f"MFCC特徴量形状: {mfcc.shape}")
    
    # スペクトログラム
    stft = librosa.stft(y)
    magnitude = np.abs(stft)
    
    # 周波数帯域分析
    freqs = librosa.fft_frequencies(sr=sr)
    avg_magnitude = np.mean(magnitude, axis=1)
    
    # 低域(20-250Hz)、中域(250-4000Hz)、高域(4000-20000Hz)
    low_freq_mask = (freqs >= 20) & (freqs <= 250)
    mid_freq_mask = (freqs >= 250) & (freqs <= 4000)
    high_freq_mask = (freqs >= 4000) & (freqs <= sr/2)
    
    low_energy = np.mean(avg_magnitude[low_freq_mask])
    mid_energy = np.mean(avg_magnitude[mid_freq_mask])
    high_energy = np.mean(avg_magnitude[high_freq_mask])
    
    total_energy = low_energy + mid_energy + high_energy
    
    print(f"低域エネルギー (20-250Hz): {low_energy:.4f} ({low_energy/total_energy*100:.1f}%)")
    print(f"中域エネルギー (250-4000Hz): {mid_energy:.4f} ({mid_energy/total_energy*100:.1f}%)")
    print(f"高域エネルギー (4000Hz以上): {high_energy:.4f} ({high_energy/total_energy*100:.1f}%)")
    
    # 楽器成分分析
    print(f"\n楽器成分分析:")
    
    # ハーモニック・パーカッシブ分離
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    
    harmonic_energy = np.mean(librosa.feature.rms(y=y_harmonic)[0])
    percussive_energy = np.mean(librosa.feature.rms(y=y_percussive)[0])
    
    print(f"ハーモニック成分エネルギー: {harmonic_energy:.4f}")
    print(f"パーカッシブ成分エネルギー: {percussive_energy:.4f}")
    print(f"ハーモニック比率: {harmonic_energy/(harmonic_energy+percussive_energy)*100:.1f}%")
    
    # 音響特徴による楽器推定
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
    
    avg_centroid = np.mean(spectral_centroid)
    avg_rolloff = np.mean(spectral_rolloff)
    avg_zcr = np.mean(zero_crossing_rate)
    
    print(f"スペクトル重心: {avg_centroid:.1f} Hz")
    print(f"スペクトルロールオフ: {avg_rolloff:.1f} Hz")
    print(f"ゼロ交差率: {avg_zcr:.4f}")
    
    # アコースティックギターの特徴判定
    guitar_indicators = []
    if 200 <= avg_centroid <= 2000:
        guitar_indicators.append("スペクトル重心がギター範囲")
    if avg_zcr < 0.1:
        guitar_indicators.append("低いゼロ交差率（弦楽器的）")
    if harmonic_energy > percussive_energy * 2:
        guitar_indicators.append("ハーモニック成分が支配的")
    
    if guitar_indicators:
        print(f"アコースティックギター特徴: {', '.join(guitar_indicators)}")
    
    # 雨音成分分析
    print(f"\n雨音成分分析:")
    
    # 高周波数ノイズ成分の分析（雨音特徴）
    high_freq_noise = y_percussive[np.abs(y_percussive) > np.std(y_percussive) * 0.5]
    if len(high_freq_noise) > 0:
        noise_density = len(high_freq_noise) / len(y)
        print(f"高周波数ノイズ密度: {noise_density:.4f}")
        
        if noise_density > 0.1:
            print("雨音様の持続的なノイズ成分を検出")
        else:
            print("雨音成分は少ない")
    
    # ループ性能分析
    print(f"\nループ性能分析:")
    
    # 開始部と終了部の比較（各1秒）
    loop_duration = min(1.0, duration/4)  # 最大1秒、または楽曲の1/4
    loop_samples = int(loop_duration * sr)
    
    start_segment = y[:loop_samples]
    end_segment = y[-loop_samples:]
    
    # クロス相関によるループ適性評価
    correlation = np.correlate(start_segment, end_segment, mode='full')
    max_correlation = np.max(correlation) / (np.linalg.norm(start_segment) * np.linalg.norm(end_segment))
    
    print(f"開始-終了相関係数: {max_correlation:.4f}")
    
    # RMS差
    start_rms = np.sqrt(np.mean(start_segment**2))
    end_rms = np.sqrt(np.mean(end_segment**2))
    rms_difference = abs(start_rms - end_rms)
    
    print(f"開始部RMS: {start_rms:.4f}")
    print(f"終了部RMS: {end_rms:.4f}")
    print(f"RMS差: {rms_difference:.4f}")
    
    # ループ適性判定
    if max_correlation > 0.7 and rms_difference < 0.1:
        loop_quality = "優秀"
    elif max_correlation > 0.5 and rms_difference < 0.2:
        loop_quality = "良好"
    elif max_correlation > 0.3:
        loop_quality = "普通"
    else:
        loop_quality = "要改善"
    
    print(f"ループ適性: {loop_quality}")
    
    # 戦略計画書との整合性チェック
    print(f"\n戦略計画書との整合性:")
    print(f"BPM目標（60-70）vs 実測値（{tempo:.1f}）: {'✓' if 60 <= tempo <= 70 else '✗'}")
    print(f"三部構成: {'✓' if len(segment_times) >= 3 else '✗'}")
    print(f"アコースティックギター: {'✓' if guitar_indicators else '?'}")
    print(f"雨音成分: {'✓' if 'noise_density' in locals() and noise_density > 0.05 else '?'}")
    
    # 結果をJSONで保存
    analysis_result = {
        "timestamp": datetime.now().isoformat(),
        "file_path": file_path,
        "basic_properties": {
            "duration_seconds": float(duration),
            "sample_rate": int(sr),
            "total_samples": int(len(y))
        },
        "volume_analysis": {
            "avg_rms": float(avg_rms),
            "max_rms": float(max_rms),
            "min_rms": float(min_rms),
            "dynamic_range_db": float(20 * np.log10(max_rms/min_rms))
        },
        "tempo_analysis": {
            "bpm": float(tempo),
            "beats_detected": int(len(beats))
        },
        "structure_analysis": {
            "segments": len(boundaries)-1,
            "boundaries": [float(t) for t in segment_times]
        },
        "spectral_analysis": {
            "low_freq_energy_pct": float(low_energy/total_energy*100),
            "mid_freq_energy_pct": float(mid_energy/total_energy*100),
            "high_freq_energy_pct": float(high_energy/total_energy*100),
            "spectral_centroid": float(avg_centroid),
            "spectral_rolloff": float(avg_rolloff),
            "zero_crossing_rate": float(avg_zcr)
        },
        "instrument_analysis": {
            "harmonic_energy": float(harmonic_energy),
            "percussive_energy": float(percussive_energy),
            "harmonic_ratio": float(harmonic_energy/(harmonic_energy+percussive_energy)*100),
            "guitar_indicators": guitar_indicators
        },
        "loop_analysis": {
            "correlation": float(max_correlation),
            "start_rms": float(start_rms),
            "end_rms": float(end_rms),
            "rms_difference": float(rms_difference),
            "quality": loop_quality
        },
        "strategy_compliance": {
            "bpm_target_met": 60 <= tempo <= 70,
            "three_part_structure": len(segment_times) >= 3,
            "acoustic_guitar_detected": bool(guitar_indicators),
            "rain_sound_detected": 'noise_density' in locals() and noise_density > 0.05
        }
    }
    
    return analysis_result

def create_visualizations(file_path, analysis_result):
    """分析結果の視覚化"""
    y, sr = librosa.load(file_path, sr=None)
    
    # 図の作成
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('音楽分析結果', fontsize=16, fontweight='bold')
    
    # 1. 波形
    time = np.linspace(0, len(y) / sr, len(y))
    axes[0, 0].plot(time, y, alpha=0.7)
    axes[0, 0].set_title('波形')
    axes[0, 0].set_xlabel('時間 (秒)')
    axes[0, 0].set_ylabel('振幅')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. スペクトログラム
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    img = librosa.display.specshow(D, y_axis='hz', x_axis='time', sr=sr, ax=axes[0, 1])
    axes[0, 1].set_title('スペクトログラム')
    plt.colorbar(img, ax=axes[0, 1], format='%+2.0f dB')
    
    # 3. RMSエネルギー
    rms = librosa.feature.rms(y=y)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
    axes[1, 0].plot(times, rms)
    axes[1, 0].set_title('RMSエネルギー推移')
    axes[1, 0].set_xlabel('時間 (秒)')
    axes[1, 0].set_ylabel('RMSエネルギー')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. 周波数成分分布
    freqs = ['低域\n(20-250Hz)', '中域\n(250-4000Hz)', '高域\n(4000Hz+)']
    energies = [
        analysis_result['spectral_analysis']['low_freq_energy_pct'],
        analysis_result['spectral_analysis']['mid_freq_energy_pct'],
        analysis_result['spectral_analysis']['high_freq_energy_pct']
    ]
    axes[1, 1].bar(freqs, energies, color=['red', 'green', 'blue'], alpha=0.7)
    axes[1, 1].set_title('周波数帯域別エネルギー分布')
    axes[1, 1].set_ylabel('エネルギー (%)')
    
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.dirname(file_path).replace('/music', '/analysis')
    os.makedirs(output_dir, exist_ok=True)
    
    plt.savefig(os.path.join(output_dir, 'music_analysis_visualization.png'), dpi=300, bbox_inches='tight')
    print(f"\n視覚化結果を保存: {os.path.join(output_dir, 'music_analysis_visualization.png')}")
    
    return fig

if __name__ == "__main__":
    # 音楽ファイルのパス
    music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16398936614/music/generated-music.wav"
    
    # 分析実行
    result = analyze_music_file(music_file)
    
    if result:
        # JSON結果保存
        output_dir = os.path.dirname(music_file).replace('/music', '/analysis')
        os.makedirs(output_dir, exist_ok=True)
        
        json_path = os.path.join(output_dir, 'detailed_music_analysis.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n詳細分析結果をJSONで保存: {json_path}")
        
        # 視覚化作成
        try:
            create_visualizations(music_file, result)
        except Exception as e:
            print(f"視覚化作成エラー: {e}")
        
        print("\n" + "="*60)
        print("分析完了!")
        print("="*60)
    else:
        print("分析に失敗しました。")