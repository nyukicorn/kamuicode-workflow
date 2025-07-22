#!/usr/bin/env python3
"""
包括的音楽分析スクリプト - 美しいバラの花束
音響特性、楽器分析、構造分析、戦略比較を実行
"""

import numpy as np
import librosa
import librosa.display
import soundfile as sf
from scipy import signal
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime

class ComprehensiveMusicAnalyzer:
    def __init__(self, audio_file_path):
        self.audio_file_path = audio_file_path
        self.y, self.sr = librosa.load(audio_file_path)
        self.duration = len(self.y) / self.sr
        self.analysis_results = {}
        
    def analyze_basic_characteristics(self):
        """基本音響特性の分析"""
        print("=== 基本音響特性分析 ===")
        
        # 曲の長さ
        duration_seconds = self.duration
        print(f"楽曲の長さ: {duration_seconds:.2f}秒")
        
        # テンポ測定
        tempo, beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
        print(f"推定テンポ: {tempo:.1f} BPM")
        
        # キー/調性の判定
        chroma = librosa.feature.chroma_stft(y=self.y, sr=self.sr)
        key_profile = np.mean(chroma, axis=1)
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        estimated_key = key_names[np.argmax(key_profile)]
        print(f"推定キー: {estimated_key}")
        
        # 音量レベルと動的レンジ
        rms = librosa.feature.rms(y=self.y)[0]
        avg_rms = np.mean(rms)
        max_rms = np.max(rms)
        min_rms = np.min(rms)
        dynamic_range = 20 * np.log10(max_rms / (min_rms + 1e-10))
        
        print(f"平均RMS: {avg_rms:.4f}")
        print(f"最大RMS: {max_rms:.4f}")
        print(f"最小RMS: {min_rms:.4f}")
        print(f"動的レンジ: {dynamic_range:.1f} dB")
        
        self.analysis_results['basic'] = {
            'duration': duration_seconds,
            'tempo': float(tempo),
            'estimated_key': estimated_key,
            'average_rms': float(avg_rms),
            'max_rms': float(max_rms),
            'min_rms': float(min_rms),
            'dynamic_range': float(dynamic_range)
        }
        
    def analyze_instruments_and_timbre(self):
        """楽器・音色分析"""
        print("\n=== 楽器・音色分析 ===")
        
        # スペクトラム解析
        stft = librosa.stft(self.y)
        magnitude = np.abs(stft)
        
        # 周波数帯域別エネルギー分析
        freqs = librosa.fft_frequencies(sr=self.sr)
        
        # 低域 (20-250Hz) - 低音楽器
        low_freq_mask = (freqs >= 20) & (freqs <= 250)
        low_energy = np.mean(magnitude[low_freq_mask])
        
        # 中域 (250-4000Hz) - メロディ楽器
        mid_freq_mask = (freqs >= 250) & (freqs <= 4000)
        mid_energy = np.mean(magnitude[mid_freq_mask])
        
        # 高域 (4000-20000Hz) - 高音楽器、倍音
        high_freq_mask = (freqs >= 4000) & (freqs <= 20000)
        high_energy = np.mean(magnitude[high_freq_mask])
        
        print(f"低域エネルギー (20-250Hz): {low_energy:.4f}")
        print(f"中域エネルギー (250-4000Hz): {mid_energy:.4f}")
        print(f"高域エネルギー (4000-20000Hz): {high_energy:.4f}")
        
        # 楽器推定
        total_energy = low_energy + mid_energy + high_energy
        low_ratio = low_energy / total_energy
        mid_ratio = mid_energy / total_energy
        high_ratio = high_energy / total_energy
        
        print(f"低域比率: {low_ratio:.1%}")
        print(f"中域比率: {mid_ratio:.1%}")
        print(f"高域比率: {high_ratio:.1%}")
        
        # 楽器特定ロジック
        instruments = []
        if mid_ratio > 0.5:
            instruments.append("ピアノ (中域優勢)")
        if low_ratio > 0.2:
            instruments.append("ストリングス/チェロ (低域支持)")
        if high_ratio > 0.3:
            instruments.append("フルート/高音楽器 (高域アクセント)")
            
        print(f"推定楽器: {', '.join(instruments)}")
        
        # スペクトラル特徴
        spectral_centroid = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=self.y, sr=self.sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr)[0]
        
        avg_centroid = np.mean(spectral_centroid)
        avg_rolloff = np.mean(spectral_rolloff)
        avg_bandwidth = np.mean(spectral_bandwidth)
        
        print(f"スペクトラル重心: {avg_centroid:.1f} Hz")
        print(f"スペクトラルロールオフ: {avg_rolloff:.1f} Hz")
        print(f"スペクトラル帯域幅: {avg_bandwidth:.1f} Hz")
        
        # 音色特徴判定
        timbre_characteristics = []
        if avg_centroid < 2000:
            timbre_characteristics.append("暖かい音色")
        else:
            timbre_characteristics.append("明るい音色")
            
        if avg_bandwidth < 1500:
            timbre_characteristics.append("柔らかい質感")
        else:
            timbre_characteristics.append("鮮明な質感")
            
        print(f"音色特徴: {', '.join(timbre_characteristics)}")
        
        self.analysis_results['instruments'] = {
            'frequency_distribution': {
                'low_energy': float(low_energy),
                'mid_energy': float(mid_energy),
                'high_energy': float(high_energy),
                'low_ratio': float(low_ratio),
                'mid_ratio': float(mid_ratio),
                'high_ratio': float(high_ratio)
            },
            'estimated_instruments': instruments,
            'spectral_features': {
                'centroid': float(avg_centroid),
                'rolloff': float(avg_rolloff),
                'bandwidth': float(avg_bandwidth)
            },
            'timbre_characteristics': timbre_characteristics
        }
        
    def analyze_structure(self):
        """構造分析"""
        print("\n=== 構造分析 ===")
        
        # RMSエネルギーの時間変化
        rms = librosa.feature.rms(y=self.y, frame_length=2048, hop_length=512)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=self.sr, hop_length=512)
        
        # エネルギー変化の分析
        rms_smooth = signal.savgol_filter(rms, window_length=21, polyorder=3)
        
        # ピーク検出
        peaks, _ = signal.find_peaks(rms_smooth, height=np.mean(rms_smooth))
        peak_times = times[peaks]
        
        print(f"エネルギーピーク数: {len(peaks)}")
        print(f"ピーク時刻: {peak_times}")
        
        # 楽曲セクション推定
        duration = self.duration
        sections = []
        
        if duration > 30:
            # 標準的な構造 (>30秒)
            intro_end = min(8, duration * 0.2)
            development_end = min(20, duration * 0.6)
            climax_end = min(30, duration * 0.8)
            
            sections = [
                {'name': 'イントロ', 'start': 0, 'end': intro_end},
                {'name': '展開部', 'start': intro_end, 'end': development_end},
                {'name': 'クライマックス', 'start': development_end, 'end': climax_end},
                {'name': 'アウトロ', 'start': climax_end, 'end': duration}
            ]
        else:
            # 短い構造 (<30秒)
            intro_end = duration * 0.25
            development_end = duration * 0.7
            
            sections = [
                {'name': 'イントロ', 'start': 0, 'end': intro_end},
                {'name': '展開部', 'start': intro_end, 'end': development_end},
                {'name': 'アウトロ', 'start': development_end, 'end': duration}
            ]
        
        print("\n楽曲構造:")
        for section in sections:
            duration_sec = section['end'] - section['start']
            print(f"  {section['name']}: {section['start']:.1f}-{section['end']:.1f}秒 ({duration_sec:.1f}秒)")
        
        # 感情曲線の分析
        emotion_curve = rms_smooth / np.max(rms_smooth)  # 正規化
        
        # 感情的高揚ポイント
        high_emotion_threshold = np.percentile(emotion_curve, 80)
        high_emotion_indices = np.where(emotion_curve > high_emotion_threshold)[0]
        high_emotion_times = times[high_emotion_indices]
        
        print(f"\n感情的高揚ポイント (上位20%): {len(high_emotion_indices)}ポイント")
        if len(high_emotion_times) > 0:
            print(f"主要高揚時刻: {high_emotion_times[0]:.1f}秒 - {high_emotion_times[-1]:.1f}秒")
        
        self.analysis_results['structure'] = {
            'total_duration': float(duration),
            'energy_peaks': len(peaks),
            'peak_times': [float(t) for t in peak_times],
            'sections': sections,
            'emotion_curve_stats': {
                'max_emotion_time': float(times[np.argmax(emotion_curve)]),
                'min_emotion_time': float(times[np.argmin(emotion_curve)]),
                'high_emotion_duration': float(len(high_emotion_indices) * 512 / self.sr)
            }
        }
        
    def compare_with_strategy(self):
        """戦略計画との比較"""
        print("\n=== 戦略計画との比較分析 ===")
        
        # 計画された仕様
        planned_specs = {
            'tempo_range': (60, 70),
            'duration_range': (30, 40),
            'key': 'C Major',
            'instruments': ['ピアノ', 'ストリングス', 'フルート'],
            'structure': ['静寂', '優雅な開花', 'クライマックス', '余韻']
        }
        
        actual_specs = self.analysis_results
        
        print("=== テンポ比較 ===")
        actual_tempo = actual_specs['basic']['tempo']
        planned_min, planned_max = planned_specs['tempo_range']
        tempo_match = planned_min <= actual_tempo <= planned_max
        print(f"計画テンポ: {planned_min}-{planned_max} BPM")
        print(f"実際テンポ: {actual_tempo:.1f} BPM")
        print(f"テンポ一致: {'✓' if tempo_match else '✗'}")
        
        print("\n=== 楽曲長比較 ===")
        actual_duration = actual_specs['basic']['duration']
        planned_min_dur, planned_max_dur = planned_specs['duration_range']
        duration_match = planned_min_dur <= actual_duration <= planned_max_dur
        print(f"計画長さ: {planned_min_dur}-{planned_max_dur}秒")
        print(f"実際長さ: {actual_duration:.1f}秒")
        print(f"長さ一致: {'✓' if duration_match else '✗'}")
        
        print("\n=== キー比較 ===")
        actual_key = actual_specs['basic']['estimated_key']
        planned_key = planned_specs['key'].split()[0]  # 'C Major' -> 'C'
        key_match = actual_key == planned_key
        print(f"計画キー: {planned_specs['key']}")
        print(f"推定キー: {actual_key}")
        print(f"キー一致: {'✓' if key_match else '✗'}")
        
        print("\n=== 楽器構成比較 ===")
        planned_instruments = planned_specs['instruments']
        actual_instruments = actual_specs['instruments']['estimated_instruments']
        print(f"計画楽器: {', '.join(planned_instruments)}")
        print(f"推定楽器: {', '.join(actual_instruments)}")
        
        # 楽器マッチング分析
        instrument_matches = []
        for planned in planned_instruments:
            for actual in actual_instruments:
                if planned in actual or any(word in actual for word in planned.split()):
                    instrument_matches.append(planned)
                    break
        
        instrument_match_rate = len(instrument_matches) / len(planned_instruments)
        print(f"楽器一致率: {instrument_match_rate:.1%}")
        
        print("\n=== 構造比較 ===")
        planned_structure = planned_specs['structure']
        actual_sections = [s['name'] for s in actual_specs['structure']['sections']]
        print(f"計画構造: {' → '.join(planned_structure)}")
        print(f"実際構造: {' → '.join(actual_sections)}")
        
        # 総合一致率
        matches = [tempo_match, duration_match, key_match, instrument_match_rate > 0.5]
        overall_match_rate = sum(matches) / len(matches)
        
        print(f"\n=== 総合評価 ===")
        print(f"戦略実現度: {overall_match_rate:.1%}")
        
        self.analysis_results['strategy_comparison'] = {
            'tempo_match': tempo_match,
            'duration_match': duration_match,
            'key_match': key_match,
            'instrument_match_rate': float(instrument_match_rate),
            'overall_match_rate': float(overall_match_rate),
            'recommendations': []
        }
        
    def generate_prompt_recommendations(self):
        """プロンプト微調整のための推奨事項"""
        print("\n=== プロンプト微調整推奨事項 ===")
        
        recommendations = []
        actual = self.analysis_results
        
        # テンポに基づく推奨
        actual_tempo = actual['basic']['tempo']
        if actual_tempo < 60:
            recommendations.append({
                'category': 'テンポ調整',
                'issue': f'実際のテンポ({actual_tempo:.1f} BPM)が計画より遅い',
                'recommendation': '画像・動画プロンプトでより静的で瞑想的な表現を強調',
                'video_prompt_adjustment': 'ゆっくりとした花びらの動き、静寂な美しさを重視'
            })
        elif actual_tempo > 70:
            recommendations.append({
                'category': 'テンポ調整',
                'issue': f'実際のテンポ({actual_tempo:.1f} BPM)が計画より速い',
                'recommendation': '画像・動画プロンプトでより動的で活気のある表現を追加',
                'video_prompt_adjustment': '花びらの躍動感、光の動的変化を強調'
            })
        
        # 楽器構成に基づく推奨
        mid_ratio = actual['instruments']['frequency_distribution']['mid_ratio']
        high_ratio = actual['instruments']['frequency_distribution']['high_ratio']
        
        if mid_ratio > 0.6:
            recommendations.append({
                'category': '楽器バランス',
                'issue': 'ピアノ（中域）が支配的',
                'recommendation': '画像でピアノの優雅さを強調、キーボードや音符のビジュアル要素',
                'video_prompt_adjustment': 'エレガントな指の動き、鍵盤の反射を想起させる光の表現'
            })
        
        if high_ratio > 0.3:
            recommendations.append({
                'category': 'フルートアクセント',
                'issue': '高域楽器（フルート）が明確に存在',
                'recommendation': '軽やかで透明感のある視覚要素を追加',
                'video_prompt_adjustment': '風に舞う花びら、透明な光の粒子、空気感のある動き'
            })
        
        # 動的レンジに基づく推奨
        dynamic_range = actual['basic']['dynamic_range']
        if dynamic_range < 10:
            recommendations.append({
                'category': '動的表現',
                'issue': f'動的レンジが小さい({dynamic_range:.1f} dB)',
                'recommendation': '一定の美しさを保つ静的な美しさを重視',
                'video_prompt_adjustment': '安定した照明、穏やかな色彩変化'
            })
        elif dynamic_range > 20:
            recommendations.append({
                'category': '動的表現',
                'issue': f'動的レンジが大きい({dynamic_range:.1f} dB)',
                'recommendation': '劇的な明暗コントラスト、ダイナミックな視覚変化',
                'video_prompt_adjustment': '劇的な照明変化、影と光のコントラスト'
            })
        
        # 構造に基づく推奨
        sections = actual['structure']['sections']
        if len(sections) == 3:  # 短い構造
            recommendations.append({
                'category': '構造適応',
                'issue': '楽曲が短い構造（3セクション）',
                'recommendation': '各動画セグメントをより集中的に使用',
                'video_prompt_adjustment': '各5秒動画の要素を最大限活用、重複使用の効果的活用'
            })
        
        # 戦略計画の役割分担調整
        role_adjustments = {
            'メイン動画(60%)': 'ピアノ中心の優雅な表現に焦点、安定した美しさ',
            'アクセント動画(25%)': '高域楽器に合わせた軽やかで透明な表現',
            'トランジション動画(15%)': '動的レンジに合わせた繋ぎの強弱調整'
        }
        
        print("\n=== 役割分担調整推奨 ===")
        for role, adjustment in role_adjustments.items():
            print(f"{role}: {adjustment}")
            recommendations.append({
                'category': '役割分担',
                'issue': role,
                'recommendation': adjustment,
                'video_prompt_adjustment': adjustment
            })
        
        print(f"\n総推奨事項数: {len(recommendations)}")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. [{rec['category']}] {rec['recommendation']}")
        
        self.analysis_results['recommendations'] = recommendations
        
    def save_analysis_results(self, output_dir):
        """分析結果の保存"""
        os.makedirs(output_dir, exist_ok=True)
        
        # JSON形式で保存
        json_path = os.path.join(output_dir, 'music_analysis_results.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        # マークダウンレポートの生成
        report_path = os.path.join(output_dir, 'detailed-music-analysis-report.md')
        self._generate_markdown_report(report_path)
        
        print(f"\n=== 分析結果保存完了 ===")
        print(f"JSON: {json_path}")
        print(f"レポート: {report_path}")
        
    def _generate_markdown_report(self, report_path):
        """詳細マークダウンレポートの生成"""
        basic = self.analysis_results['basic']
        instruments = self.analysis_results['instruments']
        structure = self.analysis_results['structure']
        comparison = self.analysis_results['strategy_comparison']
        recommendations = self.analysis_results['recommendations']
        
        report = f"""# 音楽詳細分析レポート - 美しいバラの花束

## 分析概要
- **分析日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
- **音楽ファイル**: {os.path.basename(self.audio_file_path)}
- **総合戦略実現度**: {comparison['overall_match_rate']:.1%}

## 1. 基本音響特性

### 楽曲基本情報
- **楽曲の長さ**: {basic['duration']:.2f}秒
- **推定テンポ**: {basic['tempo']:.1f} BPM
- **推定キー**: {basic['estimated_key']}

### 音響レベル分析
- **平均RMSレベル**: {basic['average_rms']:.4f}
- **最大RMSレベル**: {basic['max_rms']:.4f}
- **最小RMSレベル**: {basic['min_rms']:.4f}
- **動的レンジ**: {basic['dynamic_range']:.1f} dB

## 2. 楽器・音色分析

### 周波数帯域別分析
- **低域 (20-250Hz)**: {instruments['frequency_distribution']['low_energy']:.4f} ({instruments['frequency_distribution']['low_ratio']:.1%})
- **中域 (250-4000Hz)**: {instruments['frequency_distribution']['mid_energy']:.4f} ({instruments['frequency_distribution']['mid_ratio']:.1%})
- **高域 (4000-20000Hz)**: {instruments['frequency_distribution']['high_energy']:.4f} ({instruments['frequency_distribution']['high_ratio']:.1%})

### 推定楽器
{chr(10).join(f'- {instrument}' for instrument in instruments['estimated_instruments'])}

### スペクトラル特徴
- **スペクトラル重心**: {instruments['spectral_features']['centroid']:.1f} Hz
- **スペクトラルロールオフ**: {instruments['spectral_features']['rolloff']:.1f} Hz
- **スペクトラル帯域幅**: {instruments['spectral_features']['bandwidth']:.1f} Hz

### 音色特徴
{chr(10).join(f'- {char}' for char in instruments['timbre_characteristics'])}

## 3. 構造分析

### 楽曲構造
{chr(10).join(f'- **{section["name"]}**: {section["start"]:.1f}-{section["end"]:.1f}秒 ({section["end"]-section["start"]:.1f}秒)' for section in structure['sections'])}

### 感情曲線分析
- **最大感情ポイント**: {structure['emotion_curve_stats']['max_emotion_time']:.1f}秒
- **最小感情ポイント**: {structure['emotion_curve_stats']['min_emotion_time']:.1f}秒
- **高揚継続時間**: {structure['emotion_curve_stats']['high_emotion_duration']:.1f}秒
- **エネルギーピーク数**: {structure['energy_peaks']}

## 4. 戦略計画との比較

### 仕様一致度
- **テンポ一致**: {'✓ 合致' if comparison['tempo_match'] else '✗ 不一致'}
- **楽曲長一致**: {'✓ 合致' if comparison['duration_match'] else '✗ 不一致'}
- **キー一致**: {'✓ 合致' if comparison['key_match'] else '✗ 不一致'}
- **楽器構成一致率**: {comparison['instrument_match_rate']:.1%}

### 総合評価
**戦略実現度: {comparison['overall_match_rate']:.1%}**

## 5. プロンプト微調整推奨事項

### 画像・動画プロンプト調整提案
"""
        
        for i, rec in enumerate(recommendations, 1):
            report += f"""
#### {i}. {rec['category']}
- **問題**: {rec['issue']}
- **推奨**: {rec['recommendation']}
- **動画プロンプト調整**: {rec['video_prompt_adjustment']}
"""
        
        report += f"""

## 6. 役割分担維持のための微調整案

### メイン動画 (60% 使用率) 
- 現在の音楽特性に基づき、{instruments['frequency_distribution']['mid_ratio']:.1%}の中域エネルギーを活かした優雅なピアノ表現に焦点
- 安定した美しさを表現する静的要素を重視

### アクセント動画 (25% 使用率)
- {instruments['frequency_distribution']['high_ratio']:.1%}の高域エネルギーを活かした軽やかな表現
- 透明感と躍動感のバランス

### トランジション動画 (15% 使用率)  
- {basic['dynamic_range']:.1f}dBの動的レンジに合わせた繋ぎの強弱
- 感情の橋渡し効果の最適化

## 7. 技術的考慮事項

- **実際BPM ({basic['tempo']:.1f})** に基づく動画速度調整推奨
- **動的レンジ ({basic['dynamic_range']:.1f}dB)** に合わせた視覚的コントラスト調整
- **楽曲長 ({basic['duration']:.1f}秒)** での3動画最適配分戦略

---
*この分析は楽曲の実際の特性に基づき、戦略計画との整合性を保ちつつ最適化を図ることを目的としています。*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def run_full_analysis(self):
        """完全分析の実行"""
        print("🎵 包括的音楽分析開始 🎵\n")
        
        self.analyze_basic_characteristics()
        self.analyze_instruments_and_timbre()
        self.analyze_structure()
        self.compare_with_strategy()
        self.generate_prompt_recommendations()
        
        print("\n✅ 分析完了 ✅")
        
        return self.analysis_results

def main():
    # 音楽ファイルのパス
    audio_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250722-16448947063/music/generated-music.wav"
    output_dir = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250722-16448947063/analysis"
    
    # 分析実行
    analyzer = ComprehensiveMusicAnalyzer(audio_file)
    results = analyzer.run_full_analysis()
    
    # 結果保存
    analyzer.save_analysis_results(output_dir)
    
    print(f"\n📊 詳細分析完了!")
    print(f"📁 結果保存先: {output_dir}")

if __name__ == "__main__":
    main()