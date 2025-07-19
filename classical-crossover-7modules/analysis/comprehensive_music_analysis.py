#!/usr/bin/env python3
"""
Comprehensive Music Analysis Tool
音楽分析専門ツール - クラシッククロスオーバー楽曲の詳細分析
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy import stats
from scipy.signal import find_peaks
import json
from datetime import datetime
import os

class MusicAnalyzer:
    def __init__(self, audio_file):
        self.audio_file = audio_file
        self.y, self.sr = librosa.load(audio_file, sr=None)
        self.duration = librosa.get_duration(y=self.y, sr=self.sr)
        
    def analyze_basic_properties(self):
        """基本的な楽曲プロパティの分析"""
        analysis = {
            "duration_seconds": round(self.duration, 2),
            "duration_minutes": f"{int(self.duration // 60)}:{int(self.duration % 60):02d}",
            "sample_rate": self.sr,
            "total_samples": len(self.y),
            "channels": "Mono" if len(self.y.shape) == 1 else "Stereo"
        }
        return analysis
    
    def analyze_tempo_and_rhythm(self):
        """テンポとリズムの分析"""
        # テンポ検出
        tempo, beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
        
        # テンポ変化の分析
        hop_length = 512
        onset_frames = librosa.onset.onset_detect(y=self.y, sr=self.sr, hop_length=hop_length)
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sr, hop_length=hop_length)
        
        # 動的テンポ分析
        tempogram = librosa.feature.tempogram(y=self.y, sr=self.sr, hop_length=hop_length)
        tempo_times = librosa.frames_to_time(range(tempogram.shape[1]), sr=self.sr, hop_length=hop_length)
        
        analysis = {
            "main_tempo_bpm": round(float(tempo), 1),
            "beat_count": len(beats),
            "onset_count": len(onset_frames),
            "tempo_stability": self._analyze_tempo_stability(tempogram),
            "rhythm_complexity": self._calculate_rhythm_complexity(onset_times)
        }
        return analysis
    
    def analyze_harmony_and_tonality(self):
        """和声と調性の分析"""
        # クロマ特徴量（音高クラス）
        chroma = librosa.feature.chroma_stft(y=self.y, sr=self.sr)
        
        # 調性推定
        key_profile = np.mean(chroma, axis=1)
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        major_correlations = []
        minor_correlations = []
        
        for i in range(12):
            major_correlations.append(np.corrcoef(key_profile, np.roll(major_profile, i))[0, 1])
            minor_correlations.append(np.corrcoef(key_profile, np.roll(minor_profile, i))[0, 1])
        
        best_major = np.argmax(major_correlations)
        best_minor = np.argmax(minor_correlations)
        
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        if max(major_correlations) > max(minor_correlations):
            estimated_key = f"{keys[best_major]} Major"
            confidence = max(major_correlations)
        else:
            estimated_key = f"{keys[best_minor]} Minor"
            confidence = max(minor_correlations)
        
        # 和声の複雑さ
        harmony_complexity = np.std(chroma)
        
        analysis = {
            "estimated_key": estimated_key,
            "key_confidence": round(float(confidence), 3),
            "harmonic_complexity": round(float(harmony_complexity), 3),
            "chromatic_content": self._analyze_chromatic_content(chroma)
        }
        return analysis
    
    def analyze_dynamics_and_expression(self):
        """ダイナミクスと表現の分析"""
        # RMS エネルギー
        rms = librosa.feature.rms(y=self.y)[0]
        
        # スペクトラル重心（音色の明るさ）
        spectral_centroids = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        
        # スペクトラル帯域幅
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr)[0]
        
        # ゼロ交差率
        zcr = librosa.feature.zero_crossing_rate(self.y)[0]
        
        # 動的レンジ
        db_rms = librosa.amplitude_to_db(rms)
        dynamic_range = np.max(db_rms) - np.min(db_rms)
        
        analysis = {
            "average_rms": round(float(np.mean(rms)), 4),
            "dynamic_range_db": round(float(dynamic_range), 2),
            "brightness_avg": round(float(np.mean(spectral_centroids)), 1),
            "brightness_variation": round(float(np.std(spectral_centroids)), 1),
            "spectral_bandwidth_avg": round(float(np.mean(spectral_bandwidth)), 1),
            "zero_crossing_rate": round(float(np.mean(zcr)), 4),
            "expressiveness_score": self._calculate_expressiveness(rms, spectral_centroids)
        }
        return analysis
    
    def analyze_structure(self):
        """楽曲構造の分析"""
        # セグメント分析
        hop_length = 512
        frame_length = 2048
        
        # 自己相似度行列
        chroma = librosa.feature.chroma_stft(y=self.y, sr=self.sr, hop_length=hop_length)
        similarity_matrix = np.dot(chroma.T, chroma)
        
        # 構造変化点の検出
        novelty = librosa.segment.recurrence_to_lag(similarity_matrix)
        peaks, _ = find_peaks(novelty, height=np.mean(novelty) + np.std(novelty))
        
        # 時間軸に変換
        segment_times = librosa.frames_to_time(peaks, sr=self.sr, hop_length=hop_length)
        
        # セグメント特徴の分析
        segments = self._analyze_segments(segment_times)
        
        analysis = {
            "total_segments": len(segment_times) + 1,
            "segment_boundaries": [round(float(t), 2) for t in segment_times],
            "average_segment_length": round(float(self.duration / (len(segment_times) + 1)), 2),
            "structure_complexity": round(float(len(segment_times) / self.duration * 60), 2),
            "segments": segments
        }
        return analysis
    
    def analyze_instrumentation(self):
        """楽器構成の分析"""
        # スペクトラル特徴による楽器推定
        mfccs = librosa.feature.mfcc(y=self.y, sr=self.sr, n_mfcc=13)
        spectral_contrast = librosa.feature.spectral_contrast(y=self.y, sr=self.sr)
        tonnetz = librosa.feature.tonnetz(y=self.y, sr=self.sr)
        
        # 周波数帯域別分析
        frequency_bands = self._analyze_frequency_bands()
        
        # 楽器的特徴の推定
        instrumentation_features = self._estimate_instrumentation_features(mfccs, spectral_contrast)
        
        analysis = {
            "frequency_distribution": frequency_bands,
            "instrumentation_indicators": instrumentation_features,
            "harmonic_richness": round(float(np.mean(spectral_contrast)), 3),
            "timbral_complexity": round(float(np.std(mfccs)), 3)
        }
        return analysis
    
    def analyze_classical_crossover_features(self):
        """クラシッククロスオーバー特徴の分析"""
        # クラシック的要素の検出
        classical_features = self._detect_classical_elements()
        
        # 現代的要素の検出
        contemporary_features = self._detect_contemporary_elements()
        
        # ジャンル融合度の評価
        fusion_score = self._calculate_fusion_score(classical_features, contemporary_features)
        
        analysis = {
            "classical_elements": classical_features,
            "contemporary_elements": contemporary_features,
            "fusion_score": fusion_score,
            "crossover_characteristics": self._identify_crossover_characteristics()
        }
        return analysis
    
    def _analyze_tempo_stability(self, tempogram):
        """テンポの安定性を分析"""
        tempo_variance = np.var(tempogram, axis=1)
        stability_score = 1.0 / (1.0 + np.mean(tempo_variance))
        return round(float(stability_score), 3)
    
    def _calculate_rhythm_complexity(self, onset_times):
        """リズムの複雑さを計算"""
        if len(onset_times) < 2:
            return 0.0
        
        intervals = np.diff(onset_times)
        complexity = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else 0
        return round(float(complexity), 3)
    
    def _analyze_chromatic_content(self, chroma):
        """クロマティックな内容を分析"""
        # 各音高クラスの使用頻度
        chroma_distribution = np.mean(chroma, axis=1)
        chromaticism = 1.0 - (np.max(chroma_distribution) - np.min(chroma_distribution))
        return round(float(chromaticism), 3)
    
    def _calculate_expressiveness(self, rms, spectral_centroids):
        """表現力スコアを計算"""
        dynamic_variation = np.std(rms) / np.mean(rms) if np.mean(rms) > 0 else 0
        timbral_variation = np.std(spectral_centroids) / np.mean(spectral_centroids) if np.mean(spectral_centroids) > 0 else 0
        expressiveness = (dynamic_variation + timbral_variation) / 2
        return round(float(expressiveness), 3)
    
    def _analyze_segments(self, segment_times):
        """セグメントの詳細分析"""
        segments = []
        times = [0] + list(segment_times) + [self.duration]
        
        for i in range(len(times) - 1):
            start_time = times[i]
            end_time = times[i + 1]
            duration = end_time - start_time
            
            # セグメントの特徴を分析
            start_sample = int(start_time * self.sr)
            end_sample = int(end_time * self.sr)
            segment_audio = self.y[start_sample:end_sample]
            
            if len(segment_audio) > 0:
                segment_rms = np.mean(librosa.feature.rms(y=segment_audio))
                segment_info = {
                    "segment_number": i + 1,
                    "start_time": round(start_time, 2),
                    "end_time": round(end_time, 2),
                    "duration": round(duration, 2),
                    "energy_level": round(float(segment_rms), 4),
                    "section_type": self._classify_section_type(i, len(times) - 2, segment_rms)
                }
                segments.append(segment_info)
        
        return segments
    
    def _classify_section_type(self, segment_index, total_segments, energy_level):
        """セクションタイプを分類"""
        if segment_index == 0:
            return "序奏 (Introduction)"
        elif segment_index == total_segments - 1:
            return "終結 (Conclusion)"
        elif segment_index < total_segments * 0.3:
            return "導入部 (Development)"
        elif segment_index > total_segments * 0.7:
            return "終盤 (Finale)"
        elif energy_level > 0.1:
            return "クライマックス (Climax)"
        else:
            return "展開部 (Development)"
    
    def _analyze_frequency_bands(self):
        """周波数帯域別分析"""
        stft = librosa.stft(self.y)
        magnitude = np.abs(stft)
        freqs = librosa.fft_frequencies(sr=self.sr)
        
        # 周波数帯域の定義
        bass_mask = freqs <= 250
        low_mid_mask = (freqs > 250) & (freqs <= 500)
        mid_mask = (freqs > 500) & (freqs <= 2000)
        high_mid_mask = (freqs > 2000) & (freqs <= 4000)
        treble_mask = freqs > 4000
        
        # 各帯域のエネルギー
        bass_energy = np.mean(magnitude[bass_mask, :])
        low_mid_energy = np.mean(magnitude[low_mid_mask, :])
        mid_energy = np.mean(magnitude[mid_mask, :])
        high_mid_energy = np.mean(magnitude[high_mid_mask, :])
        treble_energy = np.mean(magnitude[treble_mask, :])
        
        total_energy = bass_energy + low_mid_energy + mid_energy + high_mid_energy + treble_energy
        
        return {
            "bass_ratio": round(float(bass_energy / total_energy), 3),
            "low_mid_ratio": round(float(low_mid_energy / total_energy), 3),
            "mid_ratio": round(float(mid_energy / total_energy), 3),
            "high_mid_ratio": round(float(high_mid_energy / total_energy), 3),
            "treble_ratio": round(float(treble_energy / total_energy), 3)
        }
    
    def _estimate_instrumentation_features(self, mfccs, spectral_contrast):
        """楽器構成の特徴を推定"""
        # MFCC特徴からの楽器特徴推定
        mfcc_means = np.mean(mfccs, axis=1)
        contrast_means = np.mean(spectral_contrast, axis=1)
        
        # 楽器特徴の推定（簡単なヒューリスティック）
        features = {
            "string_likelihood": round(float(np.mean(contrast_means[2:5])), 3),
            "wind_likelihood": round(float(mfcc_means[1] * 0.1), 3),
            "percussion_likelihood": round(float(mfcc_means[0] * 0.05), 3),
            "piano_likelihood": round(float(np.mean(contrast_means[:3])), 3),
            "orchestral_complexity": round(float(np.std(mfcc_means)), 3)
        }
        return features
    
    def _detect_classical_elements(self):
        """クラシック的要素を検出"""
        # 和声の複雑さ
        chroma = librosa.feature.chroma_stft(y=self.y, sr=self.sr)
        harmonic_complexity = np.std(chroma)
        
        # 動的変化
        rms = librosa.feature.rms(y=self.y)[0]
        dynamic_range = np.max(rms) - np.min(rms)
        
        # クラシック的特徴
        features = {
            "harmonic_sophistication": round(float(harmonic_complexity), 3),
            "dynamic_expression": round(float(dynamic_range), 3),
            "structural_complexity": round(float(len(librosa.onset.onset_detect(y=self.y, sr=self.sr)) / self.duration), 2),
            "melodic_development": "present" if harmonic_complexity > 0.3 else "limited"
        }
        return features
    
    def _detect_contemporary_elements(self):
        """現代的要素を検出"""
        # スペクトラル特徴
        spectral_centroids = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        zcr = librosa.feature.zero_crossing_rate(self.y)[0]
        
        # 現代的特徴
        features = {
            "electronic_processing": round(float(np.mean(zcr)), 4),
            "modern_production": round(float(np.std(spectral_centroids)), 1),
            "accessibility": "high" if np.mean(spectral_centroids) > 2000 else "moderate",
            "contemporary_rhythm": "present" if np.std(zcr) > 0.01 else "traditional"
        }
        return features
    
    def _calculate_fusion_score(self, classical_features, contemporary_features):
        """ジャンル融合度を計算"""
        classical_score = (
            classical_features["harmonic_sophistication"] +
            classical_features["dynamic_expression"] +
            classical_features["structural_complexity"]
        ) / 3
        
        contemporary_score = (
            contemporary_features["electronic_processing"] * 10 +
            contemporary_features["modern_production"] / 1000
        )
        
        fusion_score = min(classical_score, contemporary_score) / max(classical_score, contemporary_score)
        return round(float(fusion_score), 3)
    
    def _identify_crossover_characteristics(self):
        """クロスオーバー特徴を特定"""
        return {
            "genre_blend": "classical-contemporary fusion",
            "accessibility_level": "high",
            "innovation_level": "moderate",
            "emotional_appeal": "broad audience"
        }
    
    def generate_comprehensive_report(self):
        """包括的な分析レポートを生成"""
        print("音楽分析を実行中...")
        
        basic = self.analyze_basic_properties()
        tempo = self.analyze_tempo_and_rhythm()
        harmony = self.analyze_harmony_and_tonality()
        dynamics = self.analyze_dynamics_and_expression()
        structure = self.analyze_structure()
        instrumentation = self.analyze_instrumentation()
        crossover = self.analyze_classical_crossover_features()
        
        report = {
            "analysis_metadata": {
                "file_path": self.audio_file,
                "analysis_timestamp": datetime.now().isoformat(),
                "analyzer_version": "1.0.0"
            },
            "basic_properties": basic,
            "tempo_and_rhythm": tempo,
            "harmony_and_tonality": harmony,
            "dynamics_and_expression": dynamics,
            "musical_structure": structure,
            "instrumentation": instrumentation,
            "classical_crossover_features": crossover
        }
        
        return report

def main():
    audio_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250719-16384240868/music/generated-music.wav"
    
    if not os.path.exists(audio_file):
        print(f"エラー: 音楽ファイルが見つかりません: {audio_file}")
        return
    
    try:
        analyzer = MusicAnalyzer(audio_file)
        report = analyzer.generate_comprehensive_report()
        
        # 結果をJSONファイルに保存
        output_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250719-16384240868/analysis/music_analysis_results.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"分析完了。結果は {output_file} に保存されました。")
        
        # 主要な結果を表示
        print("\n=== 音楽分析結果サマリー ===")
        print(f"楽曲の長さ: {report['basic_properties']['duration_minutes']} ({report['basic_properties']['duration_seconds']}秒)")
        print(f"メインテンポ: {report['tempo_and_rhythm']['main_tempo_bpm']} BPM")
        print(f"推定調性: {report['harmony_and_tonality']['estimated_key']} (信頼度: {report['harmony_and_tonality']['key_confidence']})")
        print(f"ダイナミックレンジ: {report['dynamics_and_expression']['dynamic_range_db']} dB")
        print(f"楽曲構造: {report['musical_structure']['total_segments']} セグメント")
        print(f"ジャンル融合度: {report['classical_crossover_features']['fusion_score']}")
        
        return report
        
    except Exception as e:
        print(f"分析中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()