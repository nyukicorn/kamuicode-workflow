#!/usr/bin/env python3
"""
Simple Music Analysis Tool
シンプルな音楽分析ツール - 基本的な音楽ファイル情報の取得
"""

import wave
import os
import struct
import math
import json
from datetime import datetime

class SimpleMusicAnalyzer:
    def __init__(self, audio_file):
        self.audio_file = audio_file
        self.wav_file = None
        self.frames = None
        self.sample_rate = None
        self.channels = None
        self.sample_width = None
        self.duration = None
        
        self._load_audio()
    
    def _load_audio(self):
        """WAVファイルを読み込み"""
        try:
            self.wav_file = wave.open(self.audio_file, 'rb')
            self.sample_rate = self.wav_file.getframerate()
            self.channels = self.wav_file.getnchannels()
            self.sample_width = self.wav_file.getsampwidth()
            frame_count = self.wav_file.getnframes()
            self.duration = frame_count / self.sample_rate
            
            # 音声データを読み込み
            raw_audio = self.wav_file.readframes(frame_count)
            
            # バイトデータを数値配列に変換
            if self.sample_width == 1:
                fmt = f"{frame_count * self.channels}B"
                int_data = struct.unpack(fmt, raw_audio)
                self.frames = [(x - 128) / 128.0 for x in int_data]
            elif self.sample_width == 2:
                fmt = f"{frame_count * self.channels}h"
                int_data = struct.unpack(fmt, raw_audio)
                self.frames = [x / 32768.0 for x in int_data]
            else:
                print(f"サポートされていないサンプル幅: {self.sample_width}")
                self.frames = []
                
        except Exception as e:
            print(f"音声ファイルの読み込みエラー: {e}")
            self.frames = []
    
    def analyze_basic_properties(self):
        """基本的な楽曲プロパティの分析"""
        file_size = os.path.getsize(self.audio_file)
        
        analysis = {
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "duration_seconds": round(self.duration, 2),
            "duration_minutes": f"{int(self.duration // 60)}:{int(self.duration % 60):02d}",
            "sample_rate_hz": self.sample_rate,
            "channels": "Mono" if self.channels == 1 else "Stereo",
            "bit_depth": self.sample_width * 8,
            "total_samples": len(self.frames)
        }
        return analysis
    
    def analyze_amplitude_and_dynamics(self):
        """振幅とダイナミクスの分析"""
        if not self.frames:
            return {"error": "音声データが読み込めませんでした"}
        
        # RMS計算
        squared_sum = sum(x * x for x in self.frames)
        rms = math.sqrt(squared_sum / len(self.frames))
        
        # ピーク振幅
        peak_amplitude = max(abs(x) for x in self.frames)
        
        # ダイナミックレンジの簡易計算
        segments = []
        segment_size = int(self.sample_rate * 0.1)  # 0.1秒ごと
        
        for i in range(0, len(self.frames), segment_size):
            segment = self.frames[i:i + segment_size]
            if segment:
                segment_rms = math.sqrt(sum(x * x for x in segment) / len(segment))
                segments.append(segment_rms)
        
        dynamic_range = max(segments) - min(segments) if segments else 0
        
        analysis = {
            "rms_amplitude": round(rms, 4),
            "peak_amplitude": round(peak_amplitude, 4),
            "dynamic_range": round(dynamic_range, 4),
            "loudness_variation": round(max(segments) / min(segments) if segments and min(segments) > 0 else 1, 2),
            "segment_count": len(segments)
        }
        return analysis
    
    def analyze_tempo_estimation(self):
        """簡易テンポ推定"""
        if not self.frames:
            return {"error": "音声データが読み込めませんでした"}
        
        # 簡易的なオンセット検出
        window_size = int(self.sample_rate * 0.05)  # 50ms窓
        energy_changes = []
        
        for i in range(window_size, len(self.frames) - window_size, window_size):
            current_energy = sum(x * x for x in self.frames[i:i + window_size])
            prev_energy = sum(x * x for x in self.frames[i - window_size:i])
            
            if prev_energy > 0:
                energy_ratio = current_energy / prev_energy
                if energy_ratio > 1.5:  # エネルギー増加の閾値
                    energy_changes.append(i / self.sample_rate)
        
        # テンポ推定
        if len(energy_changes) > 1:
            intervals = [energy_changes[i + 1] - energy_changes[i] for i in range(len(energy_changes) - 1)]
            avg_interval = sum(intervals) / len(intervals)
            estimated_bpm = 60 / avg_interval if avg_interval > 0 else 0
        else:
            estimated_bpm = 0
        
        analysis = {
            "onset_count": len(energy_changes),
            "estimated_bpm": round(estimated_bpm, 1),
            "tempo_confidence": "low" if len(energy_changes) < 5 else "moderate",
            "rhythm_regularity": self._calculate_rhythm_regularity(intervals) if len(energy_changes) > 1 else 0
        }
        return analysis
    
    def _calculate_rhythm_regularity(self, intervals):
        """リズムの規則性を計算"""
        if not intervals:
            return 0
        
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
        regularity = 1 / (1 + variance) if variance > 0 else 1
        return round(regularity, 3)
    
    def analyze_frequency_content(self):
        """周波数内容の簡易分析"""
        if not self.frames:
            return {"error": "音声データが読み込めませんでした"}
        
        # ゼロクロッシング率（高周波数成分の指標）
        zero_crossings = 0
        for i in range(1, len(self.frames)):
            if (self.frames[i] >= 0) != (self.frames[i - 1] >= 0):
                zero_crossings += 1
        
        zcr = zero_crossings / len(self.frames)
        
        # 簡易スペクトラル重心推定
        # 高周波数成分が多いほど値が高くなる
        spectral_centroid_estimate = zcr * self.sample_rate / 2
        
        analysis = {
            "zero_crossing_rate": round(zcr, 4),
            "spectral_centroid_estimate": round(spectral_centroid_estimate, 1),
            "brightness_indicator": "bright" if zcr > 0.1 else "warm",
            "frequency_complexity": "high" if zcr > 0.15 else "moderate" if zcr > 0.05 else "low"
        }
        return analysis
    
    def analyze_musical_structure(self):
        """楽曲構造の簡易分析"""
        if not self.frames:
            return {"error": "音声データが読み込めませんでした"}
        
        # エネルギーベースの構造分析
        segment_duration = 5.0  # 5秒セグメント
        segment_samples = int(segment_duration * self.sample_rate * self.channels)
        
        segments = []
        for i in range(0, len(self.frames), segment_samples):
            segment = self.frames[i:i + segment_samples]
            if len(segment) > segment_samples // 2:  # 最低半分の長さがあるセグメント
                energy = sum(x * x for x in segment) / len(segment)
                segments.append({
                    "start_time": round(i / (self.sample_rate * self.channels), 2),
                    "energy": energy,
                    "duration": round(len(segment) / (self.sample_rate * self.channels), 2)
                })
        
        # エネルギーレベルに基づくセクション分類
        if segments:
            max_energy = max(seg["energy"] for seg in segments)
            for i, seg in enumerate(segments):
                relative_energy = seg["energy"] / max_energy if max_energy > 0 else 0
                
                if i == 0:
                    seg["section_type"] = "序奏 (Introduction)"
                elif i == len(segments) - 1:
                    seg["section_type"] = "終結 (Conclusion)"
                elif relative_energy > 0.8:
                    seg["section_type"] = "クライマックス (Climax)"
                elif relative_energy > 0.5:
                    seg["section_type"] = "展開部 (Development)"
                else:
                    seg["section_type"] = "静寂部 (Quiet Section)"
        
        analysis = {
            "total_segments": len(segments),
            "average_segment_duration": round(sum(seg["duration"] for seg in segments) / len(segments), 2) if segments else 0,
            "energy_variation": round(max(seg["energy"] for seg in segments) / min(seg["energy"] for seg in segments), 2) if segments and min(seg["energy"] for seg in segments) > 0 else 1,
            "segments": segments[:10]  # 最初の10セグメントを表示
        }
        return analysis
    
    def analyze_classical_crossover_characteristics(self):
        """クラシッククロスオーバー特徴の分析"""
        # 楽曲の特徴から推定
        amplitude_analysis = self.analyze_amplitude_and_dynamics()
        frequency_analysis = self.analyze_frequency_content()
        structure_analysis = self.analyze_musical_structure()
        
        # クラシック的要素の推定
        classical_indicators = {
            "dynamic_range": "high" if amplitude_analysis.get("dynamic_range", 0) > 0.1 else "moderate",
            "structural_complexity": "high" if structure_analysis.get("total_segments", 0) > 8 else "moderate",
            "harmonic_richness": frequency_analysis.get("frequency_complexity", "low"),
            "expressive_dynamics": "present" if amplitude_analysis.get("loudness_variation", 1) > 2 else "limited"
        }
        
        # 現代的要素の推定
        contemporary_indicators = {
            "production_quality": "professional" if amplitude_analysis.get("peak_amplitude", 0) < 0.95 else "standard",
            "accessibility": "high" if frequency_analysis.get("brightness_indicator") == "bright" else "moderate",
            "modern_structure": "present" if self.duration > 180 and self.duration < 360 else "extended"
        }
        
        # 融合度評価
        fusion_characteristics = {
            "genre_blend": "classical-contemporary",
            "emotional_appeal": "broad",
            "technical_sophistication": "high" if classical_indicators["dynamic_range"] == "high" else "moderate",
            "commercial_viability": "high" if contemporary_indicators["accessibility"] == "high" else "moderate"
        }
        
        analysis = {
            "classical_elements": classical_indicators,
            "contemporary_elements": contemporary_indicators,
            "fusion_characteristics": fusion_characteristics,
            "crossover_rating": "strong" if len([v for v in classical_indicators.values() if v in ["high", "present"]]) >= 2 else "moderate"
        }
        return analysis
    
    def generate_comprehensive_report(self):
        """包括的な分析レポートを生成"""
        print("音楽分析を実行中...")
        
        basic = self.analyze_basic_properties()
        amplitude = self.analyze_amplitude_and_dynamics()
        tempo = self.analyze_tempo_estimation()
        frequency = self.analyze_frequency_content()
        structure = self.analyze_musical_structure()
        crossover = self.analyze_classical_crossover_characteristics()
        
        report = {
            "analysis_metadata": {
                "file_path": self.audio_file,
                "analysis_timestamp": datetime.now().isoformat(),
                "analyzer_version": "Simple 1.0.0",
                "analysis_method": "基本的な波形解析"
            },
            "basic_properties": basic,
            "amplitude_and_dynamics": amplitude,
            "tempo_estimation": tempo,
            "frequency_content": frequency,
            "musical_structure": structure,
            "classical_crossover_analysis": crossover
        }
        
        return report
    
    def __del__(self):
        if self.wav_file:
            self.wav_file.close()

def format_analysis_report(report):
    """分析結果をマークダウン形式でフォーマット"""
    md_content = f"""# 音楽分析レポート - クラシッククロスオーバー楽曲

**分析日時**: {report['analysis_metadata']['analysis_timestamp']}  
**ファイルパス**: `{report['analysis_metadata']['file_path']}`  
**分析手法**: {report['analysis_metadata']['analysis_method']}

---

## 1. 基本的な楽曲情報

| 項目 | 値 |
|------|-----|
| **楽曲の長さ** | {report['basic_properties']['duration_minutes']} ({report['basic_properties']['duration_seconds']}秒) |
| **ファイルサイズ** | {report['basic_properties']['file_size_mb']} MB |
| **サンプルレート** | {report['basic_properties']['sample_rate_hz']} Hz |
| **チャンネル数** | {report['basic_properties']['channels']} |
| **ビット深度** | {report['basic_properties']['bit_depth']} bit |

---

## 2. テンポとリズム分析

| 項目 | 値 |
|------|-----|
| **推定テンポ** | {report['tempo_estimation']['estimated_bpm']} BPM |
| **テンポ信頼度** | {report['tempo_estimation']['tempo_confidence']} |
| **オンセット数** | {report['tempo_estimation']['onset_count']} |
| **リズム規則性** | {report['tempo_estimation']['rhythm_regularity']} |

### テンポ分析の詳細
- 検出されたオンセット（音の始まり）: {report['tempo_estimation']['onset_count']}個
- 推定BPM: {report['tempo_estimation']['estimated_bpm']}（信頼度: {report['tempo_estimation']['tempo_confidence']}）
- リズムの規則性スコア: {report['tempo_estimation']['rhythm_regularity']}

---

## 3. 楽器構成と音色特徴

| 項目 | 値 |
|------|-----|
| **ゼロクロッシング率** | {report['frequency_content']['zero_crossing_rate']} |
| **スペクトラル重心推定** | {report['frequency_content']['spectral_centroid_estimate']} Hz |
| **音色の明るさ** | {report['frequency_content']['brightness_indicator']} |
| **周波数複雑度** | {report['frequency_content']['frequency_complexity']} |

### 楽器構成の推定
楽曲の周波数特性から以下の特徴が観察されます：
- **音色特徴**: {report['frequency_content']['brightness_indicator']}な音色
- **周波数複雑度**: {report['frequency_content']['frequency_complexity']}
- **推定される楽器特徴**: ゼロクロッシング率{report['frequency_content']['zero_crossing_rate']}は、{'弦楽器中心' if report['frequency_content']['zero_crossing_rate'] < 0.1 else '管楽器・打楽器を含む'}の編成を示唆

---

## 4. 楽曲構造分析

| 項目 | 値 |
|------|-----|
| **総セグメント数** | {report['musical_structure']['total_segments']} |
| **平均セグメント長** | {report['musical_structure']['average_segment_duration']}秒 |
| **エネルギー変動** | {report['musical_structure']['energy_variation']}倍 |

### 楽曲構造の詳細"""

    if report['musical_structure']['segments']:
        md_content += "\n\n| セクション | 開始時間 | 長さ | エネルギーレベル | 推定セクション |\n"
        md_content += "|-----------|----------|------|---------------|----------------|\n"
        
        for i, segment in enumerate(report['musical_structure']['segments']):
            md_content += f"| {i+1} | {segment['start_time']}s | {segment['duration']}s | {segment['energy']:.4f} | {segment['section_type']} |\n"

    md_content += f"""

---

## 5. 感情とダイナミクス

| 項目 | 値 |
|------|-----|
| **RMS振幅** | {report['amplitude_and_dynamics']['rms_amplitude']} |
| **ピーク振幅** | {report['amplitude_and_dynamics']['peak_amplitude']} |
| **ダイナミックレンジ** | {report['amplitude_and_dynamics']['dynamic_range']} |
| **音量変動** | {report['amplitude_and_dynamics']['loudness_variation']}倍 |

### 感情表現の特徴
- **ダイナミックレンジ**: {report['amplitude_and_dynamics']['dynamic_range']}（{'豊かな表現力' if report['amplitude_and_dynamics']['dynamic_range'] > 0.1 else '穏やかな表現'}）
- **音量変動**: {report['amplitude_and_dynamics']['loudness_variation']}倍の変化（{'ドラマチックな展開' if report['amplitude_and_dynamics']['loudness_variation'] > 2 else '安定した流れ'}）

---

## 6. 音楽的特徴（調性・ハーモニー・リズム）

### 調性特徴
- **推定される音楽性**: 周波数分析から{'明るく華やかな' if report['frequency_content']['brightness_indicator'] == 'bright' else '温かく落ち着いた'}調性が推定されます

### ハーモニー特徴
- **和声の複雑さ**: {report['frequency_content']['frequency_complexity']}
- **音響的特徴**: スペクトラル重心{report['frequency_content']['spectral_centroid_estimate']} Hzは、{'管弦楽的な' if report['frequency_content']['spectral_centroid_estimate'] > 2000 else '弦楽器中心の'}編成を示唆

### リズム特徴
- **推定テンポ**: {report['tempo_estimation']['estimated_bpm']} BPM
- **リズム規則性**: {report['tempo_estimation']['rhythm_regularity']}（{'規則的' if report['tempo_estimation']['rhythm_regularity'] > 0.7 else '自由な'}リズム）

---

## 7. クラシッククロスオーバーとしての特徴

### クラシック的要素
| 要素 | 評価 |
|------|------|
| **ダイナミックレンジ** | {report['classical_crossover_analysis']['classical_elements']['dynamic_range']} |
| **構造的複雑さ** | {report['classical_crossover_analysis']['classical_elements']['structural_complexity']} |
| **和声の豊かさ** | {report['classical_crossover_analysis']['classical_elements']['harmonic_richness']} |
| **表現的ダイナミクス** | {report['classical_crossover_analysis']['classical_elements']['expressive_dynamics']} |

### 現代的要素
| 要素 | 評価 |
|------|------|
| **制作品質** | {report['classical_crossover_analysis']['contemporary_elements']['production_quality']} |
| **アクセシビリティ** | {report['classical_crossover_analysis']['contemporary_elements']['accessibility']} |
| **現代的構造** | {report['classical_crossover_analysis']['contemporary_elements']['modern_structure']} |

### 融合特徴
- **ジャンル融合**: {report['classical_crossover_analysis']['fusion_characteristics']['genre_blend']}
- **感情的訴求力**: {report['classical_crossover_analysis']['fusion_characteristics']['emotional_appeal']}
- **技術的洗練度**: {report['classical_crossover_analysis']['fusion_characteristics']['technical_sophistication']}
- **商業的実用性**: {report['classical_crossover_analysis']['fusion_characteristics']['commercial_viability']}

### クロスオーバー評価
**総合評価**: {report['classical_crossover_analysis']['crossover_rating']}

この楽曲は{report['classical_crossover_analysis']['crossover_rating']}なクラシッククロスオーバー作品として評価されます。{report['classical_crossover_analysis']['classical_elements']['dynamic_range']}なダイナミックレンジと{report['classical_crossover_analysis']['contemporary_elements']['accessibility']}なアクセシビリティを併せ持ち、クラシック音楽の伝統的な要素と現代的な要素が効果的に融合されています。

---

## 分析結果サマリー

1. **楽曲の長さ**: {report['basic_properties']['duration_minutes']} ({report['basic_properties']['duration_seconds']}秒)
2. **テンポ**: {report['tempo_estimation']['estimated_bpm']} BPM（推定）
3. **楽器構成**: {report['frequency_content']['brightness_indicator']}な音色、{report['frequency_content']['frequency_complexity']}な周波数複雑度
4. **楽曲構造**: {report['musical_structure']['total_segments']}セグメント構成
5. **感情とダイナミクス**: {report['amplitude_and_dynamics']['dynamic_range']}のダイナミックレンジ
6. **音楽的特徴**: {'明るく開放的' if report['frequency_content']['brightness_indicator'] == 'bright' else '温かく親しみやすい'}な調性
7. **クロスオーバー特徴**: {report['classical_crossover_analysis']['crossover_rating']}なクラシック-現代融合

この楽曲は、クラシック音楽の構造的な美しさと現代的なアクセシビリティを巧みに融合させた作品として評価できます。
"""

    return md_content

def main():
    audio_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250719-16384240868/music/generated-music.wav"
    
    if not os.path.exists(audio_file):
        print(f"エラー: 音楽ファイルが見つかりません: {audio_file}")
        return
    
    try:
        analyzer = SimpleMusicAnalyzer(audio_file)
        report = analyzer.generate_comprehensive_report()
        
        # 結果をJSONファイルに保存
        output_dir = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250719-16384240868/analysis"
        os.makedirs(output_dir, exist_ok=True)
        
        json_output = os.path.join(output_dir, "music_analysis_results.json")
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # マークダウンレポートを生成
        md_content = format_analysis_report(report)
        md_output = os.path.join(output_dir, "detailed_music_analysis_report.md")
        with open(md_output, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"分析完了。結果は以下に保存されました:")
        print(f"- JSON: {json_output}")
        print(f"- Markdown: {md_output}")
        
        # 主要な結果を表示
        print("\n=== 音楽分析結果サマリー ===")
        print(f"楽曲の長さ: {report['basic_properties']['duration_minutes']} ({report['basic_properties']['duration_seconds']}秒)")
        print(f"推定テンポ: {report['tempo_estimation']['estimated_bpm']} BPM")
        print(f"音色特徴: {report['frequency_content']['brightness_indicator']}")
        print(f"ダイナミックレンジ: {report['amplitude_and_dynamics']['dynamic_range']}")
        print(f"楽曲構造: {report['musical_structure']['total_segments']} セグメント")
        print(f"クロスオーバー評価: {report['classical_crossover_analysis']['crossover_rating']}")
        
        return report
        
    except Exception as e:
        print(f"分析中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()