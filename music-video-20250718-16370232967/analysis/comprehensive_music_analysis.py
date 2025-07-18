#!/usr/bin/env python3
"""
音楽分析専門スクリプト - 生成音楽ファイルの詳細分析
音楽コンセプト: 淡くピンク色の美しいポピーをイメージした可愛らしいオルゴールの曲。ただ少し切ない音色も入れて。
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import json
from datetime import datetime
import os
import sys

class MusicAnalyzer:
    def __init__(self, audio_file_path):
        self.audio_file_path = audio_file_path
        self.analysis_results = {}
        
    def load_audio(self):
        """音楽ファイルを読み込み"""
        try:
            self.y, self.sr = librosa.load(self.audio_file_path, sr=None)
            print(f"音楽ファイル読み込み成功: {self.audio_file_path}")
            print(f"サンプルレート: {self.sr} Hz")
            return True
        except Exception as e:
            print(f"音楽ファイル読み込み失敗: {e}")
            return False
    
    def analyze_duration(self):
        """楽曲の長さを分析"""
        duration = librosa.get_duration(y=self.y, sr=self.sr)
        self.analysis_results['duration'] = {
            'seconds': round(duration, 2),
            'minutes_seconds': f"{int(duration // 60)}:{int(duration % 60):02d}"
        }
        return duration
    
    def analyze_tempo(self):
        """テンポ（BPM）を詳細分析"""
        # 基本的なテンポ検出
        tempo, beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
        
        # より詳細なテンポ分析
        onset_frames = librosa.onset.onset_detect(y=self.y, sr=self.sr)
        onset_times = librosa.onset.onset_times(y=self.y, sr=self.sr)
        
        # テンポの変化を分析
        if len(onset_times) > 1:
            tempo_variations = []
            for i in range(1, len(onset_times)):
                interval = onset_times[i] - onset_times[i-1]
                if interval > 0:
                    bpm = 60 / interval
                    tempo_variations.append(bpm)
            
            if tempo_variations:
                avg_tempo = np.mean(tempo_variations)
                tempo_std = np.std(tempo_variations)
            else:
                avg_tempo = tempo
                tempo_std = 0
        else:
            avg_tempo = tempo
            tempo_std = 0
        
        self.analysis_results['tempo'] = {
            'main_bpm': round(float(tempo), 1),
            'average_bpm': round(float(avg_tempo), 1),
            'tempo_variation': round(float(tempo_std), 1),
            'onset_count': len(onset_times),
            'beat_frames': beats.tolist() if hasattr(beats, 'tolist') else []
        }
        return tempo
    
    def analyze_structure(self):
        """音楽構造を分析"""
        duration = self.analysis_results['duration']['seconds']
        
        # RMSエネルギーを計算
        rms = librosa.feature.rms(y=self.y)[0]
        rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=self.sr)
        
        # スペクトル重心を計算（音色の明るさ指標）
        spectral_centroids = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        
        # 音量レベルの変化を分析
        volume_changes = []
        for i in range(len(rms_times)):
            volume_changes.append({
                'time': round(rms_times[i], 2),
                'rms_energy': round(float(rms[i]), 4),
                'spectral_centroid': round(float(spectral_centroids[i]), 2)
            })
        
        # 構造の推定（エネルギーレベルに基づく）
        structure_points = self._estimate_structure_points(rms, rms_times, duration)
        
        self.analysis_results['structure'] = {
            'estimated_sections': structure_points,
            'volume_changes': volume_changes,
            'total_duration': duration
        }
        
        return structure_points
    
    def _estimate_structure_points(self, rms, rms_times, duration):
        """構造点を推定"""
        # RMSエネルギーの平均と標準偏差
        rms_mean = np.mean(rms)
        rms_std = np.std(rms)
        
        # エネルギーレベルに基づく構造推定
        sections = []
        
        # 戦略計画の構造と比較
        strategy_structure = [
            {"name": "イントロ", "start": 0, "end": 8},
            {"name": "第1テーマ", "start": 8, "end": 16},
            {"name": "第2テーマ", "start": 16, "end": 24},
            {"name": "クライマックス", "start": 24, "end": 32},
            {"name": "アウトロ", "start": 32, "end": 40}
        ]
        
        # 実際の楽曲長に基づく構造推定
        if duration <= 30:
            # 短い楽曲の場合
            sections = [
                {"name": "イントロ", "start": 0, "end": duration * 0.2},
                {"name": "メインテーマ", "start": duration * 0.2, "end": duration * 0.7},
                {"name": "アウトロ", "start": duration * 0.7, "end": duration}
            ]
        elif duration <= 45:
            # 中程度の楽曲の場合
            sections = [
                {"name": "イントロ", "start": 0, "end": duration * 0.15},
                {"name": "第1テーマ", "start": duration * 0.15, "end": duration * 0.4},
                {"name": "第2テーマ", "start": duration * 0.4, "end": duration * 0.7},
                {"name": "クライマックス", "start": duration * 0.7, "end": duration * 0.9},
                {"name": "アウトロ", "start": duration * 0.9, "end": duration}
            ]
        else:
            # 長い楽曲の場合
            sections = strategy_structure
        
        # 各セクションの実際の音響特性を分析
        for section in sections:
            start_time = section["start"]
            end_time = min(section["end"], duration)
            
            # 該当時間範囲のRMS値を取得
            start_frame = int(start_time * len(rms) / duration)
            end_frame = int(end_time * len(rms) / duration)
            
            if start_frame < len(rms) and end_frame <= len(rms):
                section_rms = rms[start_frame:end_frame]
                if len(section_rms) > 0:
                    section["avg_energy"] = round(float(np.mean(section_rms)), 4)
                    section["max_energy"] = round(float(np.max(section_rms)), 4)
                    section["energy_variation"] = round(float(np.std(section_rms)), 4)
        
        return sections
    
    def analyze_instruments(self):
        """楽器構成を分析"""
        # スペクトル特徴を分析
        spectral_features = {}
        
        # スペクトル重心（音色の明るさ）
        spectral_centroids = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        spectral_features['spectral_centroid'] = {
            'mean': round(float(np.mean(spectral_centroids)), 2),
            'std': round(float(np.std(spectral_centroids)), 2)
        }
        
        # スペクトル帯域幅（音色の豊かさ）
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr)[0]
        spectral_features['spectral_bandwidth'] = {
            'mean': round(float(np.mean(spectral_bandwidth)), 2),
            'std': round(float(np.std(spectral_bandwidth)), 2)
        }
        
        # ゼロ交差率（音色の性質）
        zcr = librosa.feature.zero_crossing_rate(self.y)[0]
        spectral_features['zero_crossing_rate'] = {
            'mean': round(float(np.mean(zcr)), 4),
            'std': round(float(np.std(zcr)), 4)
        }
        
        # MFCC（音色の特徴）
        mfccs = librosa.feature.mfcc(y=self.y, sr=self.sr, n_mfcc=13)
        spectral_features['mfcc'] = {
            'mean': [round(float(np.mean(mfcc)), 3) for mfcc in mfccs],
            'std': [round(float(np.std(mfcc)), 3) for mfcc in mfccs]
        }
        
        # 楽器推定（基本的な特徴量による）
        instrument_analysis = self._estimate_instruments(spectral_features)
        
        self.analysis_results['instruments'] = {
            'spectral_features': spectral_features,
            'estimated_instruments': instrument_analysis
        }
        
        return instrument_analysis
    
    def _estimate_instruments(self, spectral_features):
        """楽器を推定"""
        instruments = ["オルゴール（メイン）"]
        
        # スペクトル重心による分析
        centroid_mean = spectral_features['spectral_centroid']['mean']
        bandwidth_mean = spectral_features['spectral_bandwidth']['mean']
        
        # 高周波成分の分析
        if centroid_mean > 3000:
            instruments.append("高音域楽器（チャイム、ベル系）")
        
        # 帯域幅による楽器推定
        if bandwidth_mean > 2000:
            instruments.append("複合音色楽器（ストリングス、パッド系）")
        
        # MFCC特徴による分析
        mfcc_mean = spectral_features['mfcc']['mean']
        if len(mfcc_mean) > 2:
            if mfcc_mean[1] > 0.1:
                instruments.append("メロディック楽器（ピアノ、ハープ系）")
        
        return instruments
    
    def analyze_emotional_changes(self):
        """雰囲気・感情の変化を分析"""
        # 音響特徴量の時系列分析
        duration = self.analysis_results['duration']['seconds']
        
        # 短時間窓での特徴量計算
        hop_length = 512
        window_size = 2048
        
        # RMSエネルギー（音量・迫力）
        rms = librosa.feature.rms(y=self.y, hop_length=hop_length)[0]
        rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=self.sr, hop_length=hop_length)
        
        # スペクトル重心（明るさ）
        spectral_centroids = librosa.feature.spectral_centroid(y=self.y, sr=self.sr, hop_length=hop_length)[0]
        
        # スペクトル帯域幅（豊かさ）
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr, hop_length=hop_length)[0]
        
        # 感情的変化の分析
        emotional_timeline = []
        
        for i in range(len(rms_times)):
            if i < len(rms) and i < len(spectral_centroids) and i < len(spectral_bandwidth):
                # 切ない要素の検出（低いスペクトル重心 + 低いエネルギー）
                sadness_indicator = 0
                if spectral_centroids[i] < np.mean(spectral_centroids) * 0.9:
                    sadness_indicator += 1
                if rms[i] < np.mean(rms) * 0.8:
                    sadness_indicator += 1
                if spectral_bandwidth[i] < np.mean(spectral_bandwidth) * 0.9:
                    sadness_indicator += 1
                
                emotional_timeline.append({
                    'time': round(rms_times[i], 2),
                    'energy': round(float(rms[i]), 4),
                    'brightness': round(float(spectral_centroids[i]), 2),
                    'richness': round(float(spectral_bandwidth[i]), 2),
                    'sadness_level': sadness_indicator
                })
        
        # 切ない要素の出現タイミング
        sad_moments = [moment for moment in emotional_timeline if moment['sadness_level'] >= 2]
        
        self.analysis_results['emotional_changes'] = {
            'timeline': emotional_timeline,
            'sad_moments': sad_moments,
            'total_sad_moments': len(sad_moments)
        }
        
        return emotional_timeline
    
    def analyze_rhythm(self):
        """拍子・リズムパターンを分析"""
        # ビート検出
        tempo, beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
        beat_times = librosa.frames_to_time(beats, sr=self.sr)
        
        # 拍子推定
        if len(beat_times) > 1:
            beat_intervals = np.diff(beat_times)
            avg_beat_interval = np.mean(beat_intervals)
            beat_stability = 1 - (np.std(beat_intervals) / avg_beat_interval)
        else:
            avg_beat_interval = 0
            beat_stability = 0
        
        # リズムパターンの分析
        rhythm_analysis = {
            'tempo_bpm': round(float(tempo), 1),
            'beat_times': [round(float(bt), 2) for bt in beat_times],
            'average_beat_interval': round(float(avg_beat_interval), 3),
            'beat_stability': round(float(beat_stability), 3),
            'total_beats': len(beat_times),
            'estimated_time_signature': self._estimate_time_signature(beat_times)
        }
        
        self.analysis_results['rhythm'] = rhythm_analysis
        return rhythm_analysis
    
    def _estimate_time_signature(self, beat_times):
        """拍子を推定"""
        if len(beat_times) < 4:
            return "推定不可"
        
        # 4拍子パターンの検出
        beat_intervals = np.diff(beat_times)
        
        # 一定の間隔があるかチェック
        if np.std(beat_intervals) < 0.1:
            return "4/4拍子（推定）"
        else:
            return "変則拍子または3/4拍子（推定）"
    
    def compare_with_strategy(self):
        """戦略計画との比較"""
        strategy_comparison = {
            'expected_duration': '30-40秒',
            'actual_duration': f"{self.analysis_results['duration']['seconds']}秒",
            'expected_bpm': '75BPM',
            'actual_bpm': f"{self.analysis_results['tempo']['main_bpm']}BPM",
            'expected_structure': [
                {"name": "イントロ", "start": 0, "end": 8},
                {"name": "第1テーマ", "start": 8, "end": 16},
                {"name": "第2テーマ", "start": 16, "end": 24},
                {"name": "クライマックス", "start": 24, "end": 32},
                {"name": "アウトロ", "start": 32, "end": 40}
            ],
            'actual_structure': self.analysis_results['structure']['estimated_sections']
        }
        
        # 差異の分析
        duration_diff = self.analysis_results['duration']['seconds'] - 35  # 35秒を基準
        bpm_diff = self.analysis_results['tempo']['main_bpm'] - 75
        
        strategy_comparison['analysis'] = {
            'duration_difference': round(duration_diff, 2),
            'bpm_difference': round(bpm_diff, 1),
            'duration_status': 'OK' if 30 <= self.analysis_results['duration']['seconds'] <= 40 else 'NEEDS_ADJUSTMENT',
            'bpm_status': 'OK' if 70 <= self.analysis_results['tempo']['main_bpm'] <= 80 else 'NEEDS_ADJUSTMENT'
        }
        
        self.analysis_results['strategy_comparison'] = strategy_comparison
        return strategy_comparison
    
    def generate_recommendations(self):
        """微調整提案を生成"""
        recommendations = []
        
        # 楽曲長の推奨
        duration = self.analysis_results['duration']['seconds']
        if duration < 30:
            recommendations.append({
                'category': '楽曲長',
                'issue': f'楽曲長が短すぎます（{duration}秒）',
                'recommendation': '楽曲を30-40秒に延長するか、リピート部分を追加してください'
            })
        elif duration > 40:
            recommendations.append({
                'category': '楽曲長',
                'issue': f'楽曲長が長すぎます（{duration}秒）',
                'recommendation': '楽曲を30-40秒に短縮するか、構造を再調整してください'
            })
        
        # テンポの推奨
        bpm = self.analysis_results['tempo']['main_bpm']
        if bpm < 70:
            recommendations.append({
                'category': 'テンポ',
                'issue': f'テンポが遅すぎます（{bpm}BPM）',
                'recommendation': '75BPMに近づけるか、動画の速度を調整してください'
            })
        elif bpm > 80:
            recommendations.append({
                'category': 'テンポ',
                'issue': f'テンポが速すぎます（{bpm}BPM）',
                'recommendation': '75BPMに近づけるか、動画の速度を調整してください'
            })
        
        # 切ない要素の推奨
        sad_moments = self.analysis_results['emotional_changes']['total_sad_moments']
        if sad_moments < 3:
            recommendations.append({
                'category': '感情表現',
                'issue': '切ない要素が少なすぎます',
                'recommendation': '短調の要素やメランコリックな音色を追加してください'
            })
        
        # 構造の推奨
        sections = self.analysis_results['structure']['estimated_sections']
        if len(sections) < 3:
            recommendations.append({
                'category': '音楽構造',
                'issue': '構造が単純すぎます',
                'recommendation': 'より明確な構造分割を作成してください'
            })
        
        self.analysis_results['recommendations'] = recommendations
        return recommendations
    
    def run_full_analysis(self):
        """完全な分析を実行"""
        print("=== 音楽分析開始 ===")
        
        if not self.load_audio():
            return None
        
        print("1. 楽曲長分析中...")
        self.analyze_duration()
        
        print("2. テンポ分析中...")
        self.analyze_tempo()
        
        print("3. 音楽構造分析中...")
        self.analyze_structure()
        
        print("4. 楽器構成分析中...")
        self.analyze_instruments()
        
        print("5. 感情変化分析中...")
        self.analyze_emotional_changes()
        
        print("6. リズム分析中...")
        self.analyze_rhythm()
        
        print("7. 戦略計画比較中...")
        self.compare_with_strategy()
        
        print("8. 推奨事項生成中...")
        self.generate_recommendations()
        
        print("=== 分析完了 ===")
        return self.analysis_results

def main():
    # 音楽ファイルのパス
    audio_file = "../music/generated-music.wav"
    
    if not os.path.exists(audio_file):
        print(f"音楽ファイルが見つかりません: {audio_file}")
        sys.exit(1)
    
    # 分析実行
    analyzer = MusicAnalyzer(audio_file)
    results = analyzer.run_full_analysis()
    
    if results:
        # 結果をJSONファイルに保存
        output_file = "music_analysis_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n分析結果を保存しました: {output_file}")
        
        # 重要な結果を表示
        print("\n=== 主要分析結果 ===")
        print(f"楽曲長: {results['duration']['seconds']}秒")
        print(f"テンポ: {results['tempo']['main_bpm']}BPM")
        print(f"推定楽器: {', '.join(results['instruments']['estimated_instruments'])}")
        print(f"切ない要素: {results['emotional_changes']['total_sad_moments']}箇所")
        print(f"構造セクション数: {len(results['structure']['estimated_sections'])}")
        
        # 推奨事項
        if results['recommendations']:
            print(f"\n推奨事項: {len(results['recommendations'])}件")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"{i}. {rec['category']}: {rec['recommendation']}")
    
    return results

if __name__ == "__main__":
    main()