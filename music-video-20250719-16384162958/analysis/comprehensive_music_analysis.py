#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音楽ファイル詳細分析スクリプト
Generated Music Analysis for Jazz Piano Ballad
"""

import os
import sys
import numpy as np
import json
from datetime import datetime

try:
    import librosa
    import scipy.signal
    import matplotlib.pyplot as plt
    LIBS_AVAILABLE = True
except ImportError as e:
    print(f"警告: 必要なライブラリが利用できません: {e}")
    LIBS_AVAILABLE = False

def analyze_audio_file(file_path):
    """音楽ファイルの包括的分析を実行"""
    
    if not os.path.exists(file_path):
        return {"error": f"ファイルが見つかりません: {file_path}"}
    
    if not LIBS_AVAILABLE:
        return {"error": "必要なライブラリ（librosa、scipy、numpy）が利用できません"}
    
    try:
        # 音楽ファイルの読み込み
        y, sr = librosa.load(file_path, sr=None)
        
        # 基本的な技術詳細
        duration = len(y) / sr
        channels = 1 if y.ndim == 1 else y.shape[0]
        file_size = os.path.getsize(file_path)
        
        # テンポ推定
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # スペクトル特徴
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
        
        # メル周波数ケプストラム係数（MFCC）
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # クロマ特徴（和音・調性分析）
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        
        # トーナル重心（音楽的調性分析）
        tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
        
        # エネルギー分析（音楽構造分析のため）
        frame_length = 2048
        hop_length = 512
        energy = np.array([
            sum(abs(y[i:i+frame_length]**2))
            for i in range(0, len(y), hop_length)
        ])
        
        # 音楽構造の分析（セグメント分析）
        # エネルギーの変化点を検出して構造を推定
        energy_smooth = scipy.signal.savgol_filter(energy, 21, 3)
        peaks, _ = scipy.signal.find_peaks(energy_smooth, height=np.mean(energy_smooth))
        valleys, _ = scipy.signal.find_peaks(-energy_smooth, height=-np.mean(energy_smooth))
        
        # 構造推定（時間配分）
        segment_times = []
        if len(peaks) > 0 and len(valleys) > 0:
            all_points = sorted(list(peaks) + list(valleys))
            for point in all_points:
                time_point = (point * hop_length) / sr
                segment_times.append(time_point)
        
        # 統計値計算
        analysis_result = {
            "file_info": {
                "file_path": file_path,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "analysis_time": datetime.now().isoformat()
            },
            "technical_details": {
                "duration_seconds": round(duration, 2),
                "duration_minutes": f"{int(duration // 60)}:{int(duration % 60):02d}",
                "sample_rate_hz": sr,
                "channels": channels,
                "total_samples": len(y)
            },
            "tempo_analysis": {
                "estimated_bpm": round(float(tempo), 1),
                "tempo_category": categorize_tempo(tempo),
                "beat_count": len(beats)
            },
            "spectral_features": {
                "spectral_centroid_mean": round(np.mean(spectral_centroids), 2),
                "spectral_centroid_std": round(np.std(spectral_centroids), 2),
                "spectral_rolloff_mean": round(np.mean(spectral_rolloff), 2),
                "spectral_bandwidth_mean": round(np.mean(spectral_bandwidth), 2),
                "zero_crossing_rate_mean": round(np.mean(zero_crossing_rate), 4)
            },
            "harmonic_analysis": {
                "mfcc_means": [round(float(np.mean(mfcc)), 3) for mfcc in mfccs],
                "chroma_energy_distribution": [round(float(np.mean(chroma[i])), 3) for i in range(12)],
                "dominant_pitch_class": int(np.argmax(np.mean(chroma, axis=1))),
                "tonnetz_features": [round(float(np.mean(tonnetz[i])), 3) for i in range(6)]
            },
            "structural_analysis": {
                "energy_peaks_count": len(peaks),
                "energy_valleys_count": len(valleys),
                "estimated_segments": len(segment_times) + 1,
                "segment_transition_times": [round(t, 2) for t in segment_times[:10]]  # 最初の10個まで
            },
            "musical_characteristics": analyze_musical_characteristics(
                tempo, spectral_centroids, chroma, mfccs, zero_crossing_rate
            )
        }
        
        return analysis_result
        
    except Exception as e:
        return {"error": f"音楽分析中にエラーが発生しました: {str(e)}"}

def categorize_tempo(bpm):
    """BPMによるテンポカテゴリ分類"""
    if bpm < 60:
        return "非常に遅い (Largo)"
    elif bpm < 80:
        return "遅い (Adagio/Andante)"
    elif bpm < 100:
        return "中程度 (Moderato)"
    elif bpm < 120:
        return "やや速い (Allegretto)"
    elif bpm < 140:
        return "速い (Allegro)"
    else:
        return "非常に速い (Presto)"

def analyze_musical_characteristics(tempo, spectral_centroids, chroma, mfccs, zcr):
    """音楽的特徴の分析"""
    
    # 明るさ/暗さ分析（スペクトル重心とクロマ特徴から）
    brightness = np.mean(spectral_centroids)
    brightness_category = "明るい" if brightness > 2000 else "暗い" if brightness < 1000 else "中程度"
    
    # 複雑さ分析（MFCCの分散から）
    complexity = np.mean([np.std(mfcc) for mfcc in mfccs])
    complexity_category = "複雑" if complexity > 0.5 else "シンプル" if complexity < 0.2 else "中程度"
    
    # 動的特性（ゼロ交差率から）
    dynamic_activity = np.mean(zcr)
    activity_category = "動的" if dynamic_activity > 0.1 else "静的" if dynamic_activity < 0.05 else "中程度"
    
    # ハーモニック特徴（クロマの分散から）
    harmonic_richness = np.std(np.mean(chroma, axis=1))
    harmonic_category = "豊か" if harmonic_richness > 0.1 else "シンプル" if harmonic_richness < 0.05 else "中程度"
    
    return {
        "brightness": {
            "value": round(brightness, 2),
            "category": brightness_category
        },
        "complexity": {
            "value": round(complexity, 3),
            "category": complexity_category
        },
        "dynamic_activity": {
            "value": round(dynamic_activity, 4),
            "category": activity_category
        },
        "harmonic_richness": {
            "value": round(harmonic_richness, 3),
            "category": harmonic_category
        },
        "tempo_category": categorize_tempo(tempo),
        "jazz_ballad_characteristics": evaluate_jazz_ballad_features(
            tempo, brightness, complexity, dynamic_activity, harmonic_richness
        )
    }

def evaluate_jazz_ballad_features(tempo, brightness, complexity, activity, harmony):
    """ジャズピアノバラードとしての特徴評価"""
    
    score = 0
    evaluation = {}
    
    # テンポ評価（60-80 BPM が理想）
    if 60 <= tempo <= 80:
        tempo_score = 10
        evaluation["tempo"] = "理想的なバラードテンポ"
    elif 55 <= tempo <= 90:
        tempo_score = 8
        evaluation["tempo"] = "適切なバラードテンポ範囲"
    else:
        tempo_score = 5
        evaluation["tempo"] = "バラードとしてはやや速い/遅い"
    
    # 明るさ評価（適度な暗さが好ましい）
    if 800 <= brightness <= 1500:
        brightness_score = 10
        evaluation["mood"] = "憂愁的で内省的"
    elif 1500 <= brightness <= 2500:
        brightness_score = 7
        evaluation["mood"] = "ロマンチックで優雅"
    else:
        brightness_score = 5
        evaluation["mood"] = "標準的な明るさ"
    
    # 複雑さ評価（ジャズは適度な複雑さが必要）
    if 0.3 <= complexity <= 0.7:
        complexity_score = 10
        evaluation["harmony"] = "ジャズらしい適度な複雑さ"
    elif 0.2 <= complexity <= 0.8:
        complexity_score = 8
        evaluation["harmony"] = "適切なハーモニック複雑さ"
    else:
        complexity_score = 6
        evaluation["harmony"] = "シンプルまたは過度に複雑"
    
    # 動的特性評価（バラードは静的であるべき）
    if activity <= 0.06:
        activity_score = 10
        evaluation["dynamics"] = "静的で落ち着いた"
    elif activity <= 0.09:
        activity_score = 8
        evaluation["dynamics"] = "適度に静的"
    else:
        activity_score = 6
        evaluation["dynamics"] = "やや動的すぎる"
    
    total_score = (tempo_score + brightness_score + complexity_score + activity_score) / 4
    
    evaluation["overall_score"] = round(total_score, 1)
    evaluation["overall_assessment"] = get_overall_assessment(total_score)
    
    return evaluation

def get_overall_assessment(score):
    """総合評価の文字列を返す"""
    if score >= 9:
        return "優秀なジャズピアノバラード"
    elif score >= 8:
        return "良質なジャズピアノバラード"
    elif score >= 7:
        return "適切なジャズピアノバラード"
    elif score >= 6:
        return "標準的なジャズピアノバラード"
    else:
        return "改善の余地があるジャズピアノバラード"

def generate_detailed_report(analysis_result):
    """詳細分析レポートの生成"""
    
    if "error" in analysis_result:
        return f"エラーレポート:\n{analysis_result['error']}"
    
    report = f"""
# 音楽ファイル詳細分析レポート

## ファイル情報
- ファイルパス: {analysis_result['file_info']['file_path']}
- ファイルサイズ: {analysis_result['file_info']['file_size_mb']} MB
- 分析実行時刻: {analysis_result['file_info']['analysis_time']}

## 1. 技術的詳細
- 長さ: {analysis_result['technical_details']['duration_seconds']} 秒 ({analysis_result['technical_details']['duration_minutes']})
- サンプルレート: {analysis_result['technical_details']['sample_rate_hz']} Hz
- チャンネル数: {analysis_result['technical_details']['channels']} (モノラル)
- 総サンプル数: {analysis_result['technical_details']['total_samples']:,}

## 2. テンポ分析
- 推定BPM: {analysis_result['tempo_analysis']['estimated_bpm']}
- テンポカテゴリ: {analysis_result['tempo_analysis']['tempo_category']}
- 検出されたビート数: {analysis_result['tempo_analysis']['beat_count']}

## 3. 音楽構造分析
- エネルギーピーク数: {analysis_result['structural_analysis']['energy_peaks_count']}
- エネルギー谷数: {analysis_result['structural_analysis']['energy_valleys_count']}
- 推定セグメント数: {analysis_result['structural_analysis']['estimated_segments']}
- セグメント遷移時間: {analysis_result['structural_analysis']['segment_transition_times']}

## 4. スペクトル特徴
- スペクトル重心平均: {analysis_result['spectral_features']['spectral_centroid_mean']} Hz
- スペクトルロールオフ平均: {analysis_result['spectral_features']['spectral_rolloff_mean']} Hz
- スペクトル帯域幅平均: {analysis_result['spectral_features']['spectral_bandwidth_mean']} Hz
- ゼロ交差率平均: {analysis_result['spectral_features']['zero_crossing_rate_mean']}

## 5. 音楽的特徴
- 明るさ: {analysis_result['musical_characteristics']['brightness']['category']} ({analysis_result['musical_characteristics']['brightness']['value']} Hz)
- 複雑さ: {analysis_result['musical_characteristics']['complexity']['category']} ({analysis_result['musical_characteristics']['complexity']['value']})
- 動的活動性: {analysis_result['musical_characteristics']['dynamic_activity']['category']} ({analysis_result['musical_characteristics']['dynamic_activity']['value']})
- ハーモニック豊かさ: {analysis_result['musical_characteristics']['harmonic_richness']['category']} ({analysis_result['musical_characteristics']['harmonic_richness']['value']})

## 6. ジャズピアノバラード特徴評価
"""
    
    jazz_eval = analysis_result['musical_characteristics']['jazz_ballad_characteristics']
    for key, value in jazz_eval.items():
        if key != 'overall_score' and key != 'overall_assessment':
            report += f"- {key.capitalize()}: {value}\n"
    
    report += f"\n**総合スコア: {jazz_eval['overall_score']}/10**\n"
    report += f"**総合評価: {jazz_eval['overall_assessment']}**\n"
    
    # 戦略計画書との整合性評価
    report += f"""

## 7. 戦略計画書との整合性評価

### テンポ適合性
- 計画: 60-80 BPM想定
- 実際: {analysis_result['tempo_analysis']['estimated_bpm']} BPM
- 評価: {'✓ 適合' if 60 <= analysis_result['tempo_analysis']['estimated_bpm'] <= 80 else '△ 部分適合' if 55 <= analysis_result['tempo_analysis']['estimated_bpm'] <= 90 else '✗ 不適合'}

### 感情的特徴適合性
計画: 内省的・ロマンチック・憂愁・優雅
実際の特徴:
- {analysis_result['musical_characteristics']['brightness']['category']}な音色
- {analysis_result['musical_characteristics']['dynamic_activity']['category']}な動き
- {analysis_result['musical_characteristics']['harmonic_richness']['category']}なハーモニー
"""

    return report

def main():
    """メイン実行関数"""
    
    # 音楽ファイルのパス
    music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250719-16384162958/music/generated-music.wav"
    
    print("音楽ファイル分析を開始します...")
    print(f"ファイル: {music_file}")
    
    # 分析実行
    result = analyze_audio_file(music_file)
    
    # JSON形式で結果を保存
    output_json = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250719-16384162958/analysis/music_analysis_result.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 詳細レポートを生成
    detailed_report = generate_detailed_report(result)
    
    # レポートをファイルに保存
    output_report = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250719-16384162958/analysis/detailed_music_analysis_report.md"
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write(detailed_report)
    
    print(f"\n分析完了!")
    print(f"JSON結果: {output_json}")
    print(f"詳細レポート: {output_report}")
    print("\n" + "="*60)
    print(detailed_report)

if __name__ == "__main__":
    main()