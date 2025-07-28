#!/usr/bin/env python3
"""
音楽分析専門ツール - 戦略計画書対応版
バラの花オルゴール音楽の詳細分析とレポート生成
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from datetime import datetime
import os
import sys

class MusicAnalyzer:
    def __init__(self, file_path):
        """音楽分析クラスの初期化"""
        self.file_path = file_path
        self.y = None
        self.sr = None
        self.duration = 0
        self.load_audio()
        
    def load_audio(self):
        """音楽ファイルの読み込み"""
        try:
            self.y, self.sr = librosa.load(self.file_path)
            self.duration = librosa.get_duration(y=self.y, sr=self.sr)
            print(f"音楽ファイル読み込み完了: {self.duration:.2f}秒")
        except Exception as e:
            print(f"エラー: 音楽ファイルの読み込みに失敗しました - {e}")
            sys.exit(1)
    
    def analyze_basic_properties(self):
        """基本的な音楽特性の分析"""
        # テンポ分析
        tempo, beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
        
        # 音量分析（RMS Energy）
        rms = librosa.feature.rms(y=self.y)[0]
        
        # スペクトル重心（音の明るさの指標）
        spectral_centroids = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        
        # ゼロクロッシング率（音の粗さの指標）
        zcr = librosa.feature.zero_crossing_rate(self.y)[0]
        
        return {
            'duration': self.duration,
            'tempo': tempo,
            'avg_rms': np.mean(rms),
            'std_rms': np.std(rms),
            'avg_spectral_centroid': np.mean(spectral_centroids),
            'avg_zcr': np.mean(zcr),
            'rms_values': rms,
            'spectral_centroids': spectral_centroids,
            'beats': beats
        }
    
    def analyze_structure(self):
        """音楽構造の分析（導入・展開・クライマックス・余韻）"""
        # 音楽を時系列で分割して分析
        segment_duration = self.duration / 4
        segments = []
        
        for i in range(4):
            start_time = i * segment_duration
            end_time = (i + 1) * segment_duration
            start_sample = int(start_time * self.sr)
            end_sample = int(end_time * self.sr)
            
            segment_audio = self.y[start_sample:end_sample]
            segment_rms = np.mean(librosa.feature.rms(y=segment_audio)[0])
            segment_spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=segment_audio, sr=self.sr)[0])
            
            segments.append({
                'section': ['導入部', '展開部', 'クライマックス部', '余韻部'][i],
                'time_range': f"{start_time:.1f}-{end_time:.1f}秒",
                'avg_volume': segment_rms,
                'avg_brightness': segment_spectral_centroid
            })
        
        return segments
    
    def analyze_instruments(self):
        """楽器構成の推定分析"""
        # STFT（Short-Time Fourier Transform）による周波数分析
        stft = librosa.stft(self.y)
        magnitude = np.abs(stft)
        
        # 周波数帯域別の分析
        freqs = librosa.fft_frequencies(sr=self.sr)
        
        # オルゴールの特徴的周波数帯域
        music_box_range = (200, 2000)  # オルゴールの主要周波数帯域
        bell_range = (1000, 4000)      # 鈴・ベルの周波数帯域
        strings_range = (80, 1200)     # 弦楽器の周波数帯域
        
        # 各楽器の推定存在度
        music_box_presence = np.mean(magnitude[(freqs >= music_box_range[0]) & (freqs <= music_box_range[1])])
        bell_presence = np.mean(magnitude[(freqs >= bell_range[0]) & (freqs <= bell_range[1])])
        strings_presence = np.mean(magnitude[(freqs >= strings_range[0]) & (freqs <= strings_range[1])])
        
        return {
            'estimated_music_box_presence': music_box_presence,
            'estimated_bell_presence': bell_presence,
            'estimated_strings_presence': strings_presence,
            'dominant_frequencies': freqs[np.argsort(np.mean(magnitude, axis=1))[-5:]]
        }
    
    def analyze_dynamics(self):
        """音量変化・ダイナミクスの分析"""
        # 時系列での音量変化
        hop_length = 512
        frame_duration = hop_length / self.sr
        
        rms = librosa.feature.rms(y=self.y, hop_length=hop_length)[0]
        time_frames = np.arange(len(rms)) * frame_duration
        
        # 音量の統計情報
        volume_stats = {
            'min_volume': np.min(rms),
            'max_volume': np.max(rms),
            'avg_volume': np.mean(rms),
            'volume_variance': np.var(rms),
            'dynamic_range': np.max(rms) - np.min(rms)
        }
        
        # 音量変化のパターン分析
        volume_gradient = np.gradient(rms)
        
        return {
            'volume_stats': volume_stats,
            'time_frames': time_frames,
            'rms_values': rms,
            'volume_changes': volume_gradient
        }
    
    def compare_with_strategy(self):
        """戦略計画書との比較分析"""
        target_duration_range = (35, 40)
        expected_structure = {
            '導入部': (0, 10),
            '展開部': (10, 20), 
            'クライマックス部': (20, 30),
            '余韻部': (30, 40)
        }
        
        basic_props = self.analyze_basic_properties()
        structure = self.analyze_structure()
        
        # 時間長の適合性
        duration_compliance = target_duration_range[0] <= self.duration <= target_duration_range[1]
        
        # テンポの適合性（60-70 BPM目標）
        tempo_compliance = 60 <= basic_props['tempo'] <= 70
        
        # 構造の分析結果
        structure_analysis = []
        for i, segment in enumerate(structure):
            expected_start, expected_end = list(expected_structure.values())[i]
            actual_start = i * (self.duration / 4)
            actual_end = (i + 1) * (self.duration / 4)
            
            structure_analysis.append({
                'section': segment['section'],
                'expected_time': f"{expected_start}-{expected_end}秒",
                'actual_time': segment['time_range'],
                'volume_level': segment['avg_volume'],
                'brightness_level': segment['avg_brightness']
            })
        
        return {
            'duration_compliance': duration_compliance,
            'duration_actual': self.duration,
            'duration_target': target_duration_range,
            'tempo_compliance': tempo_compliance, 
            'tempo_actual': basic_props['tempo'],
            'tempo_target': (60, 70),
            'structure_analysis': structure_analysis
        }
    
    def generate_detailed_report(self):
        """詳細分析レポートの生成"""
        print("🎵 音楽分析レポート - バラの花オルゴール")
        print("="*60)
        print(f"分析日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        print(f"ファイル: {os.path.basename(self.file_path)}")
        print()
        
        # 基本特性分析
        basic_props = self.analyze_basic_properties()
        print("📊 基本音楽特性")
        print("-"*30)
        print(f"長さ: {self.duration:.2f}秒")
        print(f"テンポ: {basic_props['tempo']:.1f} BPM")
        print(f"平均音量: {basic_props['avg_rms']:.4f}")
        print(f"音量変動: {basic_props['std_rms']:.4f}")
        print(f"平均音の明るさ: {basic_props['avg_spectral_centroid']:.1f} Hz")
        print()
        
        # 音楽構造分析
        structure = self.analyze_structure()
        print("🎼 音楽構造分析")
        print("-"*30)
        for segment in structure:
            print(f"{segment['section']} ({segment['time_range']})")
            print(f"  音量レベル: {segment['avg_volume']:.4f}")
            print(f"  明るさレベル: {segment['avg_brightness']:.1f} Hz")
        print()
        
        # 楽器構成推定
        instruments = self.analyze_instruments()
        print("🎹 楽器構成推定")
        print("-"*30)
        print(f"オルゴール推定度: {instruments['estimated_music_box_presence']:.4f}")
        print(f"鈴・ベル推定度: {instruments['estimated_bell_presence']:.4f}")
        print(f"弦楽器推定度: {instruments['estimated_strings_presence']:.4f}")
        print(f"主要周波数: {instruments['dominant_frequencies'][:3].astype(int)} Hz")
        print()
        
        # ダイナミクス分析
        dynamics = self.analyze_dynamics()
        print("📈 音量変化・ダイナミクス")
        print("-"*30)
        stats = dynamics['volume_stats']
        print(f"最小音量: {stats['min_volume']:.4f}")
        print(f"最大音量: {stats['max_volume']:.4f}")
        print(f"平均音量: {stats['avg_volume']:.4f}")
        print(f"音量変動幅: {stats['dynamic_range']:.4f}")
        print(f"音量変動の強さ: {stats['volume_variance']:.6f}")
        print()
        
        # 戦略計画書との比較
        strategy_comparison = self.compare_with_strategy()
        print("📋 戦略計画書との整合性分析")
        print("-"*40)
        print(f"時間長適合性: {'✓ 適合' if strategy_comparison['duration_compliance'] else '✗ 非適合'}")
        print(f"  実際: {strategy_comparison['duration_actual']:.2f}秒")
        print(f"  目標: {strategy_comparison['duration_target'][0]}-{strategy_comparison['duration_target'][1]}秒")
        print()
        print(f"テンポ適合性: {'✓ 適合' if strategy_comparison['tempo_compliance'] else '✗ 非適合'}")
        print(f"  実際: {strategy_comparison['tempo_actual']:.1f} BPM")
        print(f"  目標: {strategy_comparison['tempo_target'][0]}-{strategy_comparison['tempo_target'][1]} BPM")
        print()
        
        print("🎯 構造別詳細分析")
        print("-"*30)
        for analysis in strategy_comparison['structure_analysis']:
            print(f"{analysis['section']}")
            print(f"  予定: {analysis['expected_time']}")
            print(f"  実際: {analysis['actual_time']}")
            print(f"  音量: {analysis['volume_level']:.4f}")
            print(f"  明るさ: {analysis['brightness_level']:.1f} Hz")
            print()
        
        # 雰囲気・感情分析
        self.analyze_mood_emotion()
        
        # 微調整推奨事項
        self.generate_adjustment_recommendations(strategy_comparison, basic_props, structure)
    
    def analyze_mood_emotion(self):
        """雰囲気・感情の分析"""
        print("💫 雰囲気・感情分析")
        print("-"*30)
        
        basic_props = self.analyze_basic_properties()
        
        # テンポによる感情判定
        if basic_props['tempo'] < 70:
            tempo_mood = "優雅でゆったりとした"
        elif basic_props['tempo'] < 100:
            tempo_mood = "穏やかで心地よい"
        else:
            tempo_mood = "活発でエネルギッシュな"
        
        # 音量変動による情緒判定
        if basic_props['std_rms'] < 0.02:
            dynamic_mood = "安定した穏やかな"
        elif basic_props['std_rms'] < 0.05:
            dynamic_mood = "適度に変化のある"
        else:
            dynamic_mood = "劇的で感情豊かな"
        
        # スペクトル重心による明るさ判定
        if basic_props['avg_spectral_centroid'] < 1000:
            brightness_mood = "暖かく包み込むような"
        elif basic_props['avg_spectral_centroid'] < 2000:
            brightness_mood = "バランスの取れた自然な"
        else:
            brightness_mood = "明るく華やかな"
        
        print(f"テンポ感情: {tempo_mood}")
        print(f"動的感情: {dynamic_mood}")
        print(f"音色感情: {brightness_mood}")
        print()
        print("🎭 総合的雰囲気評価:")
        print(f"この音楽は{tempo_mood}雰囲気を持ち、{dynamic_mood}表現で、")
        print(f"{brightness_mood}音色特性を示しています。")
        print()
    
    def generate_adjustment_recommendations(self, strategy_comparison, basic_props, structure):
        """微調整推奨事項の生成"""
        print("🔧 微調整推奨事項")
        print("-"*30)
        
        recommendations = []
        
        # 時間長の調整
        if not strategy_comparison['duration_compliance']:
            if self.duration < 35:
                recommendations.append(f"⏱️ 音楽が短すぎます（{self.duration:.1f}秒）。35-40秒に延長を推奨。")
            elif self.duration > 40:
                recommendations.append(f"⏱️ 音楽が長すぎます（{self.duration:.1f}秒）。35-40秒に短縮を推奨。")
        
        # テンポの調整
        if not strategy_comparison['tempo_compliance']:
            if basic_props['tempo'] < 60:
                recommendations.append(f"🎵 テンポが遅すぎます（{basic_props['tempo']:.1f} BPM）。60-70 BPMに調整を推奨。")
            elif basic_props['tempo'] > 70:
                recommendations.append(f"🎵 テンポが速すぎます（{basic_props['tempo']:.1f} BPM）。60-70 BPMに調整を推奨。")
        
        # 音量バランスの調整
        volume_variation = basic_props['std_rms']
        if volume_variation < 0.01:
            recommendations.append("📈 音量変化が少なすぎます。表情豊かにするため音量の起伏を増加を推奨。")
        elif volume_variation > 0.06:
            recommendations.append("📉 音量変化が激しすぎます。オルゴールらしい繊細さのため変化を穏やかに調整を推奨。")
        
        # 構造的推奨事項
        climax_segment = structure[2]  # クライマックス部
        intro_segment = structure[0]   # 導入部
        
        if climax_segment['avg_volume'] <= intro_segment['avg_volume']:
            recommendations.append("🎼 クライマックス部の音量が導入部より低いです。感情の起伏を表現するため音量調整を推奨。")
        
        if len(recommendations) == 0:
            print("✅ 現在の音楽は戦略計画書の要件を満たしています。微調整は不要です。")
        else:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        
        print()
        print("📝 総合評価:")
        compliance_rate = sum([
            strategy_comparison['duration_compliance'],
            strategy_comparison['tempo_compliance'],
            volume_variation >= 0.01 and volume_variation <= 0.06
        ]) / 3 * 100
        
        print(f"戦略適合率: {compliance_rate:.1f}%")
        if compliance_rate >= 80:
            print("🏆 優秀: バラの花オルゴールコンセプトに高度に適合")
        elif compliance_rate >= 60:
            print("👍 良好: 軽微な調整で完璧になります")
        else:
            print("⚠️ 要改善: 戦略計画書に基づく大幅な調整が必要")


def main():
    """メイン実行関数"""
    if len(sys.argv) != 2:
        print("使用方法: python comprehensive_music_analysis.py <音楽ファイルパス>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"エラー: ファイルが見つかりません - {file_path}")
        sys.exit(1)
    
    # 音楽分析実行
    analyzer = MusicAnalyzer(file_path)
    analyzer.generate_detailed_report()


if __name__ == "__main__":
    main()