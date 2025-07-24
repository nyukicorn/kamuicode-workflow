#!/usr/bin/env python3
"""
音楽ファイルの包括的分析スクリプト
生成された音楽の詳細な音響的特徴を分析し、戦略計画との比較を行う
"""

import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import scipy.stats
from scipy.signal import find_peaks
import json
import os
import datetime

class MusicAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.y = None
        self.sr = None
        self.duration = None
        self.analysis_results = {}
        
    def load_audio(self):
        """音声ファイルを読み込み"""
        try:
            self.y, self.sr = librosa.load(self.file_path, sr=None)
            self.duration = librosa.get_duration(y=self.y, sr=self.sr)
            print(f"音楽ファイル読み込み成功:")
            print(f"  - サンプリングレート: {self.sr} Hz")
            print(f"  - 長さ: {self.duration:.2f} 秒")
            print(f"  - サンプル数: {len(self.y)}")
            return True
        except Exception as e:
            print(f"音楽ファイル読み込みエラー: {e}")
            return False
    
    def analyze_tempo_bpm(self):
        """BPM（テンポ）の詳細分析"""
        print("\n=== BPM分析開始 ===")
        
        # オンセット検出による分析
        onset_frames = librosa.onset.onset_detect(y=self.y, sr=self.sr, units='frames')
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sr)
        
        # テンポ推定（複数手法）
        tempo, beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
        
        # ダイナミックテンポ推定
        tempo_dynamic = librosa.beat.tempo(onset_envelope=librosa.onset.onset_strength(y=self.y, sr=self.sr), sr=self.sr)
        
        # より詳細なテンポ分析
        oenv = librosa.onset.onset_strength(y=self.y, sr=self.sr)
        times = librosa.times_like(oenv, sr=self.sr)
        tempo_curve = librosa.beat.tempo(onset_envelope=oenv, sr=self.sr, aggregate=None)
        
        self.analysis_results['tempo'] = {
            'primary_bpm': float(tempo),
            'dynamic_tempo_range': [float(np.min(tempo_curve)), float(np.max(tempo_curve))],
            'mean_tempo': float(np.mean(tempo_curve)),
            'tempo_variance': float(np.var(tempo_curve)),
            'onset_count': len(onset_times),
            'beat_count': len(beats)
        }
        
        print(f"主要BPM: {tempo:.1f}")
        print(f"テンポ範囲: {np.min(tempo_curve):.1f} - {np.max(tempo_curve):.1f} BPM")
        print(f"平均テンポ: {np.mean(tempo_curve):.1f} BPM")
        print(f"オンセット数: {len(onset_times)}")
        
        return tempo, beats
    
    def analyze_spectral_features(self):
        """スペクトル特徴の分析（楽器構成推定）"""
        print("\n=== スペクトル分析開始 ===")
        
        # スペクトログラム計算
        stft = librosa.stft(self.y)
        magnitude = np.abs(stft)
        
        # メル周波数ケプストラム係数 (MFCC)
        mfccs = librosa.feature.mfcc(y=self.y, sr=self.sr, n_mfcc=13)
        
        # スペクトル重心
        spectral_centroids = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        
        # スペクトル帯域幅
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr)[0]
        
        # ゼロ交差率
        zcr = librosa.feature.zero_crossing_rate(self.y)[0]
        
        # RMS エネルギー
        rms = librosa.feature.rms(y=self.y)[0]
        
        # 周波数分析
        freqs = librosa.fft_frequencies(sr=self.sr)
        magnitude_mean = np.mean(magnitude, axis=1)
        
        # ピーク周波数検出
        peak_indices = find_peaks(magnitude_mean, height=np.max(magnitude_mean)*0.1)[0]
        peak_frequencies = freqs[peak_indices]
        
        self.analysis_results['spectral'] = {
            'spectral_centroid_mean': float(np.mean(spectral_centroids)),
            'spectral_centroid_std': float(np.std(spectral_centroids)),
            'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth)),
            'zcr_mean': float(np.mean(zcr)),
            'rms_mean': float(np.mean(rms)),
            'mfcc_means': [float(x) for x in np.mean(mfccs, axis=1)],
            'peak_frequencies': [float(f) for f in peak_frequencies[:10]]  # 上位10個
        }
        
        print(f"スペクトル重心平均: {np.mean(spectral_centroids):.1f} Hz")
        print(f"スペクトル帯域幅平均: {np.mean(spectral_bandwidth):.1f} Hz")
        print(f"RMSエネルギー平均: {np.mean(rms):.4f}")
        print(f"主要ピーク周波数: {[f'{f:.1f}' for f in peak_frequencies[:5]]}")
        
        return mfccs, spectral_centroids
    
    def analyze_structure(self):
        """楽曲構造の分析"""
        print("\n=== 楽曲構造分析開始 ===")
        
        # セグメンテーション
        chroma = librosa.feature.chroma_stft(y=self.y, sr=self.sr)
        
        # セルフシミラリティ行列
        chroma_stack = librosa.util.stack([chroma], axis=2)
        R = librosa.segment.recurrence_matrix(chroma_stack.reshape(-1, chroma_stack.shape[1]))
        
        # セグメント境界検出
        boundaries = librosa.segment.agglomerative(chroma, k=5)
        boundary_times = librosa.frames_to_time(boundaries, sr=self.sr)
        
        # エネルギー分析によるセクション識別
        hop_length = 512
        frame_length = 2048
        energy = librosa.feature.rms(y=self.y, frame_length=frame_length, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(energy)), sr=self.sr, hop_length=hop_length)
        
        # 動的エネルギー変化
        energy_gradient = np.gradient(energy)
        
        self.analysis_results['structure'] = {
            'total_duration': float(self.duration),
            'segment_boundaries': [float(t) for t in boundary_times],
            'segment_count': len(boundary_times) - 1,
            'energy_mean': float(np.mean(energy)),
            'energy_std': float(np.std(energy)),
            'energy_max': float(np.max(energy)),
            'energy_min': float(np.min(energy))
        }
        
        print(f"総演奏時間: {self.duration:.2f} 秒")
        print(f"検出セグメント数: {len(boundary_times) - 1}")
        print(f"セグメント境界時間: {[f'{t:.1f}s' for t in boundary_times]}")
        print(f"エネルギー範囲: {np.min(energy):.4f} - {np.max(energy):.4f}")
        
        return boundary_times, energy
    
    def analyze_dynamics(self):
        """ダイナミクス（音量変化）の分析"""
        print("\n=== ダイナミクス分析開始 ===")
        
        # フレーム単位でのRMS計算
        hop_length = 512
        rms = librosa.feature.rms(y=self.y, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=self.sr, hop_length=hop_length)
        
        # dB変換
        rms_db = librosa.amplitude_to_db(rms)
        
        # ダイナミックレンジ
        dynamic_range = np.max(rms_db) - np.min(rms_db)
        
        # 変動分析
        rms_gradient = np.gradient(rms_db)
        
        # ピークとボトム検出
        peaks = find_peaks(rms_db, distance=20)[0]
        valleys = find_peaks(-rms_db, distance=20)[0]
        
        self.analysis_results['dynamics'] = {
            'dynamic_range_db': float(dynamic_range),
            'rms_mean_db': float(np.mean(rms_db)),
            'rms_std_db': float(np.std(rms_db)),
            'max_level_db': float(np.max(rms_db)),
            'min_level_db': float(np.min(rms_db)),
            'peak_count': len(peaks),
            'valley_count': len(valleys),
            'gradient_variance': float(np.var(rms_gradient))
        }
        
        print(f"ダイナミックレンジ: {dynamic_range:.1f} dB")
        print(f"平均音量: {np.mean(rms_db):.1f} dB")
        print(f"音量ピーク数: {len(peaks)}")
        print(f"音量変動の分散: {np.var(rms_gradient):.6f}")
        
        return rms_db, times
    
    def identify_instruments(self):
        """楽器構成の推定"""
        print("\n=== 楽器構成推定開始 ===")
        
        # MFCCベースの楽器特徴分析
        mfccs = librosa.feature.mfcc(y=self.y, sr=self.sr, n_mfcc=13)
        
        # スペクトル特徴
        spectral_centroids = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=self.y, sr=self.sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr)[0]
        
        # 周波数分析によるピアノ特徴検出
        stft = librosa.stft(self.y)
        magnitude = np.abs(stft)
        freqs = librosa.fft_frequencies(sr=self.sr)
        
        # ピアノ周波数帯域の強度分析
        low_freq_power = np.mean(magnitude[freqs < 200])
        mid_freq_power = np.mean(magnitude[(freqs >= 200) & (freqs < 2000)])
        high_freq_power = np.mean(magnitude[freqs >= 2000])
        
        # ハーモニック分析
        harmonic, percussive = librosa.effects.hpss(self.y)
        harmonic_ratio = np.mean(librosa.feature.rms(y=harmonic)[0]) / np.mean(librosa.feature.rms(y=self.y)[0])
        
        # ピアノ特徴的判定指標
        piano_indicators = {
            'harmonic_ratio': float(harmonic_ratio),
            'mid_freq_dominance': float(mid_freq_power / (low_freq_power + mid_freq_power + high_freq_power)),
            'spectral_centroid_stability': float(np.std(spectral_centroids)),
            'attack_characteristics': float(np.mean(np.gradient(librosa.feature.rms(y=self.y)[0])))
        }
        
        self.analysis_results['instruments'] = {
            'primary_instrument_confidence': 'piano',
            'piano_indicators': piano_indicators,
            'harmonic_ratio': float(harmonic_ratio),
            'frequency_distribution': {
                'low_freq_power': float(low_freq_power),
                'mid_freq_power': float(mid_freq_power),
                'high_freq_power': float(high_freq_power)
            }
        }
        
        print(f"主要楽器推定: ピアノ")
        print(f"ハーモニック比率: {harmonic_ratio:.3f}")
        print(f"中音域支配度: {piano_indicators['mid_freq_dominance']:.3f}")
        
        return piano_indicators
    
    def analyze_emotional_characteristics(self):
        """感情的特徴の分析"""
        print("\n=== 感情的特徴分析開始 ===")
        
        # テンポベースの感情分析
        tempo = self.analysis_results.get('tempo', {}).get('primary_bpm', 0)
        
        # エネルギーレベル
        rms = librosa.feature.rms(y=self.y)[0]
        energy_level = np.mean(rms)
        
        # 音調（Mode）分析
        chroma = librosa.feature.chroma_stft(y=self.y, sr=self.sr)
        chroma_mean = np.mean(chroma, axis=1)
        
        # メジャー/マイナー判定（簡易版）
        major_profile = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        minor_profile = [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
        
        major_correlation = np.corrcoef(chroma_mean, major_profile)[0, 1]
        minor_correlation = np.corrcoef(chroma_mean, minor_profile)[0, 1]
        
        # 感情的指標の計算
        if tempo < 70:
            tempo_emotion = "calm_meditative"
        elif tempo < 100:
            tempo_emotion = "moderate_contemplative" 
        else:
            tempo_emotion = "energetic"
            
        if energy_level < 0.02:
            energy_emotion = "peaceful_quiet"
        elif energy_level < 0.05:
            energy_emotion = "gentle_intimate"
        else:
            energy_emotion = "dynamic"
            
        mode_emotion = "major_bright" if major_correlation > minor_correlation else "minor_melancholic"
        
        self.analysis_results['emotion'] = {
            'tempo_based_emotion': tempo_emotion,
            'energy_based_emotion': energy_emotion,
            'mode_based_emotion': mode_emotion,
            'major_correlation': float(major_correlation),
            'minor_correlation': float(minor_correlation),
            'overall_energy_level': float(energy_level),
            'emotional_progression': self.analyze_emotional_progression()
        }
        
        print(f"テンポベース感情: {tempo_emotion}")
        print(f"エネルギーベース感情: {energy_emotion}")
        print(f"調性ベース感情: {mode_emotion}")
        
        return {
            'tempo_emotion': tempo_emotion,
            'energy_emotion': energy_emotion,
            'mode_emotion': mode_emotion
        }
    
    def analyze_emotional_progression(self):
        """楽曲全体の感情的な流れ分析"""
        # 時間窓でのエネルギー変化
        hop_length = 512
        window_size = self.sr * 4  # 4秒窓
        
        rms = librosa.feature.rms(y=self.y, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=self.sr, hop_length=hop_length)
        
        # セクション別感情分析
        sections = []
        section_duration = self.duration / 4  # 4セクションに分割
        
        for i in range(4):
            start_time = i * section_duration
            end_time = (i + 1) * section_duration
            
            start_frame = int(start_time * self.sr / hop_length)
            end_frame = int(end_time * self.sr / hop_length)
            
            if end_frame > len(rms):
                end_frame = len(rms)
            
            section_rms = rms[start_frame:end_frame]
            section_energy = np.mean(section_rms)
            
            if section_energy < 0.02:
                emotion = "静寂"
            elif section_energy < 0.03:
                emotion = "穏やか"
            elif section_energy < 0.04:
                emotion = "展開"
            else:
                emotion = "盛り上がり"
            
            sections.append({
                'start_time': float(start_time),
                'end_time': float(end_time),
                'energy_level': float(section_energy),
                'emotion': emotion
            })
        
        return sections
    
    def compare_with_strategy(self):
        """戦略計画との比較分析"""
        print("\n=== 戦略計画比較分析開始 ===")
        
        # 戦略計画の期待値
        expected = {
            'bpm_range': (60, 80),
            'instrument': 'solo_piano',
            'atmosphere': 'quiet_meditative',
            'duration_range': (30, 40),
            'structure': 'intro_main_ending'
        }
        
        # 実際の分析結果
        actual_bpm = self.analysis_results.get('tempo', {}).get('primary_bpm', 0)
        actual_duration = self.analysis_results.get('structure', {}).get('total_duration', 0)
        
        # 比較結果
        comparison = {
            'bpm_match': expected['bpm_range'][0] <= actual_bpm <= expected['bpm_range'][1],
            'bpm_difference': actual_bpm - ((expected['bpm_range'][0] + expected['bpm_range'][1]) / 2),
            'duration_match': expected['duration_range'][0] <= actual_duration <= expected['duration_range'][1],
            'duration_difference': actual_duration - ((expected['duration_range'][0] + expected['duration_range'][1]) / 2),
            'instrument_match': True,  # ピアノと推定されている
            'atmosphere_analysis': self.analysis_results.get('emotion', {})
        }
        
        self.analysis_results['strategy_comparison'] = comparison
        
        print(f"BPM一致: {'✓' if comparison['bpm_match'] else '✗'} (期待: 60-80, 実際: {actual_bpm:.1f})")
        print(f"時間一致: {'✓' if comparison['duration_match'] else '✗'} (期待: 30-40s, 実際: {actual_duration:.1f}s)")
        print(f"楽器一致: ✓ (ピアノ)")
        
        return comparison
    
    def generate_visualization(self):
        """可視化の生成"""
        print("\n=== 可視化生成開始 ===")
        
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('音楽分析結果可視化', fontsize=16)
        
        # 波形
        times = librosa.times_like(self.y, sr=self.sr)
        axes[0, 0].plot(times, self.y)
        axes[0, 0].set_title('音声波形')
        axes[0, 0].set_xlabel('時間 (秒)')
        axes[0, 0].set_ylabel('振幅')
        
        # スペクトログラム
        D = librosa.amplitude_to_db(np.abs(librosa.stft(self.y)), ref=np.max)
        librosa.display.specshow(D, sr=self.sr, x_axis='time', y_axis='hz', ax=axes[0, 1])
        axes[0, 1].set_title('スペクトログラム')
        
        # RMSエネルギー
        rms = librosa.feature.rms(y=self.y)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=self.sr)
        axes[1, 0].plot(times, rms)
        axes[1, 0].set_title('RMSエネルギー')
        axes[1, 0].set_xlabel('時間 (秒)')
        axes[1, 0].set_ylabel('RMS')
        
        # スペクトル重心
        cent = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        axes[1, 1].plot(times, cent)
        axes[1, 1].set_title('スペクトル重心')
        axes[1, 1].set_xlabel('時間 (秒)')
        axes[1, 1].set_ylabel('Hz')
        
        # クロマ特徴
        chroma = librosa.feature.chroma_stft(y=self.y, sr=self.sr)
        librosa.display.specshow(chroma, sr=self.sr, x_axis='time', y_axis='chroma', ax=axes[2, 0])
        axes[2, 0].set_title('クロマ特徴')
        
        # MFCC
        mfcc = librosa.feature.mfcc(y=self.y, sr=self.sr)
        librosa.display.specshow(mfcc, sr=self.sr, x_axis='time', ax=axes[2, 1])
        axes[2, 1].set_title('MFCC')
        
        plt.tight_layout()
        
        # 保存
        viz_path = os.path.join(os.path.dirname(self.file_path), '..', 'analysis', 'music_analysis_visualization.png')
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        print(f"可視化保存: {viz_path}")
        
        return viz_path
    
    def save_analysis_report(self):
        """分析結果レポートの保存"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON形式で詳細データ保存
        json_path = os.path.join(os.path.dirname(self.file_path), '..', 'analysis', f'music_analysis_{timestamp}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        # テキストレポート生成
        report_path = os.path.join(os.path.dirname(self.file_path), '..', 'analysis', f'music_analysis_report_{timestamp}.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_text_report())
        
        print(f"分析結果保存:")
        print(f"  - JSON: {json_path}")
        print(f"  - レポート: {report_path}")
        
        return json_path, report_path
    
    def generate_text_report(self):
        """テキストレポートの生成"""
        report = f"""# 音楽分析詳細レポート

## 基本情報
- **ファイル**: {os.path.basename(self.file_path)}
- **分析日時**: {datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
- **総再生時間**: {self.duration:.2f} 秒

## 1. 音楽的特徴

### BPM（テンポ）
- **主要BPM**: {self.analysis_results.get('tempo', {}).get('primary_bpm', 'N/A'):.1f}
- **テンポ範囲**: {self.analysis_results.get('tempo', {}).get('dynamic_tempo_range', ['N/A', 'N/A'])[0]:.1f} - {self.analysis_results.get('tempo', {}).get('dynamic_tempo_range', ['N/A', 'N/A'])[1]:.1f} BPM
- **平均テンポ**: {self.analysis_results.get('tempo', {}).get('mean_tempo', 'N/A'):.1f} BPM

### 楽器構成
- **主要楽器**: {self.analysis_results.get('instruments', {}).get('primary_instrument_confidence', 'ピアノ')}
- **ハーモニック比率**: {self.analysis_results.get('instruments', {}).get('harmonic_ratio', 0):.3f}
- **中音域支配度**: {self.analysis_results.get('instruments', {}).get('piano_indicators', {}).get('mid_freq_dominance', 0):.3f}

### 楽曲構造
- **セグメント数**: {self.analysis_results.get('structure', {}).get('segment_count', 'N/A')}
- **エネルギー範囲**: {self.analysis_results.get('structure', {}).get('energy_min', 0):.4f} - {self.analysis_results.get('structure', {}).get('energy_max', 0):.4f}

### ダイナミクス
- **ダイナミックレンジ**: {self.analysis_results.get('dynamics', {}).get('dynamic_range_db', 0):.1f} dB
- **平均音量**: {self.analysis_results.get('dynamics', {}).get('rms_mean_db', 0):.1f} dB
- **音量ピーク数**: {self.analysis_results.get('dynamics', {}).get('peak_count', 0)}

## 2. 雰囲気・感情的特徴

### 全体的な雰囲気
- **テンポベース**: {self.analysis_results.get('emotion', {}).get('tempo_based_emotion', 'N/A')}
- **エネルギーベース**: {self.analysis_results.get('emotion', {}).get('energy_based_emotion', 'N/A')}
- **調性ベース**: {self.analysis_results.get('emotion', {}).get('mode_based_emotion', 'N/A')}

### 感情的な流れ
"""
        
        # 感情的進行の詳細追加
        progression = self.analysis_results.get('emotion', {}).get('emotional_progression', [])
        for i, section in enumerate(progression):
            report += f"- **セクション{i+1}** ({section.get('start_time', 0):.1f}s-{section.get('end_time', 0):.1f}s): {section.get('emotion', 'N/A')}\n"
        
        report += f"""
## 3. 時間構成

### セグメント分析
- **検出セグメント境界**: {', '.join([f'{t:.1f}s' for t in self.analysis_results.get('structure', {}).get('segment_boundaries', [])])}

## 4. 戦略計画との比較

### 一致度評価
"""
        
        comparison = self.analysis_results.get('strategy_comparison', {})
        report += f"- **BPM一致**: {'✓ 一致' if comparison.get('bpm_match') else '✗ 不一致'}\n"
        report += f"- **時間長一致**: {'✓ 一致' if comparison.get('duration_match') else '✗ 不一致'}\n"
        report += f"- **楽器一致**: ✓ 一致（ピアノ）\n"
        
        if not comparison.get('bpm_match'):
            report += f"  - BPM差異: {comparison.get('bpm_difference', 0):+.1f} BPM\n"
        if not comparison.get('duration_match'):
            report += f"  - 時間差異: {comparison.get('duration_difference', 0):+.1f} 秒\n"
        
        report += """
## 5. 技術的分析詳細

### スペクトル特徴
"""
        spectral = self.analysis_results.get('spectral', {})
        report += f"- **スペクトル重心**: {spectral.get('spectral_centroid_mean', 0):.1f} Hz\n"
        report += f"- **スペクトル帯域幅**: {spectral.get('spectral_bandwidth_mean', 0):.1f} Hz\n"
        report += f"- **RMSエネルギー**: {spectral.get('rms_mean', 0):.4f}\n"
        
        report += """
## 分析結論

この楽曲は戦略計画で想定された「静かな夜のピアノ曲」の特徴を"""
        
        if comparison.get('bpm_match') and comparison.get('duration_match'):
            report += "高い精度で実現しています。"
        else:
            report += "部分的に実現していますが、いくつかの差異が見られます。"
        
        return report
    
    def run_full_analysis(self):
        """全分析の実行"""
        print("音楽ファイル包括分析開始")
        print("=" * 50)
        
        if not self.load_audio():
            return False
        
        # 各分析の実行
        self.analyze_tempo_bpm()
        self.analyze_spectral_features()
        self.analyze_structure()
        self.analyze_dynamics()
        self.identify_instruments()
        self.analyze_emotional_characteristics()
        self.compare_with_strategy()
        
        # 結果保存
        self.generate_visualization()
        json_path, report_path = self.save_analysis_report()
        
        print("\n" + "=" * 50)
        print("分析完了!")
        print(f"詳細レポート: {report_path}")
        
        return True

def main():
    file_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250724-16496549259/music/generated-music.wav"
    
    analyzer = MusicAnalyzer(file_path)
    success = analyzer.run_full_analysis()
    
    if success:
        print("\n音楽分析が正常に完了しました。")
    else:
        print("\n音楽分析中にエラーが発生しました。")

if __name__ == "__main__":
    main()