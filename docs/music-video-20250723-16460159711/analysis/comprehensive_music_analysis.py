#!/usr/bin/env python3
"""
音楽分析専門ツール - バラのオルゴール版
バラの花オルゴール音楽の詳細分析とレポート生成
戦略計画書に基づく90 BPM想定での分析
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
        """音楽構造の分析（戦略計画に基づく3セクション）"""
        # 戦略計画に基づく構造分析
        # 0-12秒（導入）、12-28秒（展開・クライマックス）、28-40秒（余韻）
        segments = []
        
        # 実際の時間に基づいてセクションを調整
        if self.duration <= 40:
            # 3セクションに分割
            section_times = [
                (0, min(12, self.duration * 0.3)),
                (min(12, self.duration * 0.3), min(28, self.duration * 0.7)),
                (min(28, self.duration * 0.7), self.duration)
            ]
            section_names = ['導入部', '展開・クライマックス部', '余韻部']
        else:
            # 長い場合は4セクションに分割
            segment_duration = self.duration / 4
            section_times = [(i * segment_duration, (i + 1) * segment_duration) for i in range(4)]
            section_names = ['導入部', '展開部', 'クライマックス部', '余韻部']
        
        for i, (start_time, end_time) in enumerate(section_times):
            start_sample = int(start_time * self.sr)
            end_sample = int(end_time * self.sr)
            
            if start_sample >= len(self.y):
                break
                
            end_sample = min(end_sample, len(self.y))
            segment_audio = self.y[start_sample:end_sample]
            
            if len(segment_audio) > 0:
                segment_rms = np.mean(librosa.feature.rms(y=segment_audio)[0])
                segment_spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=segment_audio, sr=self.sr)[0])
            else:
                segment_rms = 0
                segment_spectral_centroid = 0
            
            segments.append({
                'section': section_names[i] if i < len(section_names) else f'セクション{i+1}',
                'time_range': f"{start_time:.1f}-{end_time:.1f}秒",
                'avg_volume': segment_rms,
                'avg_brightness': segment_spectral_centroid
            })
        
        return segments
    
    def analyze_instruments(self):
        """楽器構成の推定分析（オルゴール・チャイムベル特化）"""
        # STFT（Short-Time Fourier Transform）による周波数分析
        stft = librosa.stft(self.y)
        magnitude = np.abs(stft)
        
        # 周波数帯域別の分析
        freqs = librosa.fft_frequencies(sr=self.sr)
        
        # オルゴールとチャイムベルの特徴的周波数帯域
        music_box_range = (200, 2000)    # オルゴールの主要周波数帯域
        chime_bell_range = (800, 4000)   # チャイムベルの周波数帯域
        high_harmonics_range = (2000, 6000)  # 高次倍音（金属音の特徴）
        
        # 各楽器の推定存在度
        music_box_mask = (freqs >= music_box_range[0]) & (freqs <= music_box_range[1])
        chime_bell_mask = (freqs >= chime_bell_range[0]) & (freqs <= chime_bell_range[1])
        high_harmonics_mask = (freqs >= high_harmonics_range[0]) & (freqs <= high_harmonics_range[1])
        
        music_box_presence = np.mean(magnitude[music_box_mask]) if np.any(music_box_mask) else 0
        chime_bell_presence = np.mean(magnitude[chime_bell_mask]) if np.any(chime_bell_mask) else 0
        high_harmonics_presence = np.mean(magnitude[high_harmonics_mask]) if np.any(high_harmonics_mask) else 0
        
        return {
            'estimated_music_box_presence': music_box_presence,
            'estimated_chime_bell_presence': chime_bell_presence,
            'estimated_high_harmonics_presence': high_harmonics_presence,
            'dominant_frequencies': freqs[np.argsort(np.mean(magnitude, axis=1))[-5:]] if len(magnitude) > 0 else []
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
        """戦略計画書との比較分析（90 BPM・30-40秒想定）"""
        target_duration_range = (30, 40)
        target_tempo_range = (85, 95)  # 90 BPM ± 5
        
        expected_structure = {
            '導入部': (0, 12),
            '展開・クライマックス部': (12, 28), 
            '余韻部': (28, 40)
        }
        
        basic_props = self.analyze_basic_properties()
        structure = self.analyze_structure()
        
        # 時間長の適合性
        duration_compliance = target_duration_range[0] <= self.duration <= target_duration_range[1]
        
        # テンポの適合性（85-95 BPM目標）
        tempo_compliance = target_tempo_range[0] <= basic_props['tempo'] <= target_tempo_range[1]
        
        # 構造の分析結果
        structure_analysis = []
        for i, segment in enumerate(structure):
            if i < len(expected_structure):
                expected_start, expected_end = list(expected_structure.values())[i]
                structure_analysis.append({
                    'section': segment['section'],
                    'expected_time': f"{expected_start}-{expected_end}秒",
                    'actual_time': segment['time_range'],
                    'volume_level': segment['avg_volume'],
                    'brightness_level': segment['avg_brightness']
                })
            else:
                structure_analysis.append({
                    'section': segment['section'],
                    'expected_time': '想定外',
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
            'tempo_target': target_tempo_range,
            'structure_analysis': structure_analysis
        }
    
    def generate_detailed_report(self):
        """詳細分析レポートの生成"""
        print("🎵 バラのオルゴール音楽分析レポート")
        print("="*60)
        print(f"分析日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        print(f"ファイル: {os.path.basename(self.file_path)}")
        print()
        
        # 基本特性分析
        basic_props = self.analyze_basic_properties()
        print("📊 基本音楽特性")
        print("-"*30)
        print(f"楽曲の長さ: {self.duration:.2f}秒")
        print(f"推定テンポ: {basic_props['tempo']:.1f} BPM")
        print(f"平均音量レベル: {basic_props['avg_rms']:.4f}")
        print(f"音量変動幅: {basic_props['std_rms']:.4f}")
        print(f"平均音の明るさ: {basic_props['avg_spectral_centroid']:.1f} Hz")
        print(f"音の粗さ指標: {basic_props['avg_zcr']:.4f}")
        print()
        
        # 音楽構造分析
        structure = self.analyze_structure()
        print("🎼 楽曲構造分析")
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
        print(f"チャイムベル推定度: {instruments['estimated_chime_bell_presence']:.4f}")
        print(f"高次倍音（金属音）: {instruments['estimated_high_harmonics_presence']:.4f}")
        if len(instruments['dominant_frequencies']) > 0:
            print(f"主要周波数: {instruments['dominant_frequencies'][:3].astype(int)} Hz")
        print()
        
        # ダイナミクス分析
        dynamics = self.analyze_dynamics()
        print("📈 音量変化パターン・ダイナミクス")
        print("-"*30)
        stats = dynamics['volume_stats']
        print(f"最小音量: {stats['min_volume']:.4f}")
        print(f"最大音量: {stats['max_volume']:.4f}")
        print(f"平均音量: {stats['avg_volume']:.4f}")
        print(f"動的レンジ: {stats['dynamic_range']:.4f}")
        print(f"音量変動の強さ: {stats['volume_variance']:.6f}")
        print()
        
        # 戦略計画書との比較
        strategy_comparison = self.compare_with_strategy()
        print("📋 戦略計画書との整合性検証")
        print("-"*40)
        print(f"時間長適合性: {'✓ 適合' if strategy_comparison['duration_compliance'] else '✗ 非適合'}")
        print(f"  実際: {strategy_comparison['duration_actual']:.2f}秒")
        print(f"  想定: {strategy_comparison['duration_target'][0]}-{strategy_comparison['duration_target'][1]}秒")
        print()
        print(f"テンポ適合性: {'✓ 適合' if strategy_comparison['tempo_compliance'] else '✗ 非適合'}")
        print(f"  実際: {strategy_comparison['tempo_actual']:.1f} BPM")
        print(f"  想定: {strategy_comparison['tempo_target'][0]}-{strategy_comparison['tempo_target'][1]} BPM")
        print()
        
        print("🎯 構造別詳細分析")
        print("-"*30)
        for analysis in strategy_comparison['structure_analysis']:
            print(f"{analysis['section']}")
            print(f"  想定時間: {analysis['expected_time']}")
            print(f"  実際時間: {analysis['actual_time']}")
            print(f"  音量レベル: {analysis['volume_level']:.4f}")
            print(f"  明るさレベル: {analysis['brightness_level']:.1f} Hz")
            print()
        
        # 雰囲気・感情分析
        self.analyze_mood_emotion()
        
        # 戦略計画との差異分析
        self.analyze_strategy_differences(strategy_comparison, basic_props, structure, instruments)
    
    def analyze_mood_emotion(self):
        """雰囲気・感情の分析"""
        print("💫 全体的な雰囲気と特徴")
        print("-"*30)
        
        basic_props = self.analyze_basic_properties()
        
        # テンポによる感情判定
        if basic_props['tempo'] < 80:
            tempo_mood = "ゆったりとした穏やかな"
        elif basic_props['tempo'] < 100:
            tempo_mood = "優雅で品のある"
        else:
            tempo_mood = "活発でリズミカルな"
        
        # 音量変動による情緒判定
        if basic_props['std_rms'] < 0.02:
            dynamic_mood = "安定した静寂な"
        elif basic_props['std_rms'] < 0.05:
            dynamic_mood = "適度に表情豊かな"
        else:
            dynamic_mood = "劇的で感情的な"
        
        # スペクトル重心による明るさ判定
        if basic_props['avg_spectral_centroid'] < 1000:
            brightness_mood = "暖かく包み込むような"
        elif basic_props['avg_spectral_centroid'] < 2000:
            brightness_mood = "バランスの取れた自然な"
        else:
            brightness_mood = "明るくキラキラとした"
        
        print(f"テンポ感情: {tempo_mood}")
        print(f"動的感情: {dynamic_mood}")
        print(f"音色感情: {brightness_mood}")
        print()
        print("🎭 総合的雰囲気評価:")
        print(f"この楽曲は{tempo_mood}雰囲気を持ち、{dynamic_mood}表現で、")
        print(f"{brightness_mood}音色特性を示しています。")
        print("バラの花とオルゴールのイメージに", end="")
        
        # 戦略コンセプトとの適合度判定
        instruments = self.analyze_instruments()
        if (basic_props['tempo'] >= 85 and basic_props['tempo'] <= 95 and 
            instruments['estimated_music_box_presence'] > 0.1):
            print("非常によく適合していると評価されます。")
        elif basic_props['tempo'] >= 70 and basic_props['tempo'] <= 110:
            print("概ね適合していると評価されます。")
        else:
            print("一部調整が必要と評価されます。")
        print()
    
    def analyze_strategy_differences(self, strategy_comparison, basic_props, structure, instruments):
        """戦略計画との差異分析と評価"""
        print("🔍 戦略計画との差異分析")
        print("-"*40)
        
        differences = []
        
        # 時間長の差異
        if not strategy_comparison['duration_compliance']:
            if self.duration < 30:
                differences.append(f"⏱️ 楽曲が短すぎます（{self.duration:.1f}秒 vs 想定30-40秒）")
            elif self.duration > 40:
                differences.append(f"⏱️ 楽曲が長すぎます（{self.duration:.1f}秒 vs 想定30-40秒）")
        
        # テンポの差異
        if not strategy_comparison['tempo_compliance']:
            if basic_props['tempo'] < 85:
                differences.append(f"🎵 テンポが想定より遅いです（{basic_props['tempo']:.1f} BPM vs 想定90 BPM）")
            elif basic_props['tempo'] > 95:
                differences.append(f"🎵 テンポが想定より速いです（{basic_props['tempo']:.1f} BPM vs 想定90 BPM）")
        
        # 楽器構成の評価
        if instruments['estimated_music_box_presence'] < 0.1:
            differences.append("🎹 オルゴールの特徴が薄いです（想定：オルゴール主体）")
        
        if instruments['estimated_chime_bell_presence'] < 0.05:
            differences.append("🔔 チャイムベルの要素が不足しています（想定：ソフトチャイムベル）")
        
        # 音量変化パターンの評価
        volume_variation = basic_props['std_rms']
        if volume_variation < 0.01:
            differences.append("📈 音量変化が少なく、単調な印象です")
        elif volume_variation > 0.08:
            differences.append("📉 音量変化が激しく、オルゴールらしい繊細さが不足しています")
        
        if len(differences) == 0:
            print("✅ 戦略計画書の想定に高度に適合しています！")
            print("楽曲は「バラの花をイメージした美しいオルゴールの曲」の")
            print("コンセプトを十分に実現していると評価されます。")
        else:
            print("発見された差異:")
            for i, diff in enumerate(differences, 1):
                print(f"{i}. {diff}")
        
        print()
        print("📝 最終総合評価:")
        
        # 適合率計算
        compliance_factors = [
            strategy_comparison['duration_compliance'],
            strategy_comparison['tempo_compliance'],
            instruments['estimated_music_box_presence'] >= 0.1,
            0.01 <= volume_variation <= 0.08
        ]
        
        compliance_rate = sum(compliance_factors) / len(compliance_factors) * 100
        
        print(f"戦略適合率: {compliance_rate:.1f}%")
        if compliance_rate >= 90:
            print("🏆 卓越: 戦略計画を極めて高いレベルで実現")
        elif compliance_rate >= 75:
            print("🥇 優秀: バラのオルゴールコンセプトに高度に適合")
        elif compliance_rate >= 60:
            print("🥈 良好: 軽微な調整で完璧になります")
        else:
            print("🥉 要改善: 戦略計画に基づく調整が推奨されます")


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