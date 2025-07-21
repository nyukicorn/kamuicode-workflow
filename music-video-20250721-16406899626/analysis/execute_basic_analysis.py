#!/usr/bin/env python3
"""
基本音楽分析実行スクリプト
実際の測定データ取得
"""

import wave
import os
import struct
import math
import json
from datetime import datetime

def basic_wav_analysis(filepath):
    """WAVファイルの基本分析"""
    try:
        # ファイル存在確認
        if not os.path.exists(filepath):
            return {"error": f"ファイルが見つかりません: {filepath}"}
        
        # ファイルサイズ
        file_size = os.path.getsize(filepath)
        
        # WAVファイル読み込み
        with wave.open(filepath, 'rb') as wav_file:
            # 基本パラメータ
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            
            # 長さ計算
            duration = frames / sample_rate
            
            # 全フレーム読み込み
            raw_audio = wav_file.readframes(frames)
            
        # 音声データ解析
        if sample_width == 2:  # 16-bit
            audio_data = struct.unpack(f'<{frames * channels}h', raw_audio)
        elif sample_width == 1:  # 8-bit
            audio_data = struct.unpack(f'<{frames * channels}B', raw_audio)
        else:
            audio_data = []
        
        # 基本統計
        if audio_data:
            max_amplitude = max(abs(x) for x in audio_data)
            rms = math.sqrt(sum(x*x for x in audio_data) / len(audio_data))
            dynamic_range_approx = max_amplitude / (rms + 1) if rms > 0 else 0
        else:
            max_amplitude = 0
            rms = 0
            dynamic_range_approx = 0
        
        # 構造推定（簡易版）
        segment_length = sample_rate * 2  # 2秒ごとのセグメント
        segments = []
        
        for i in range(0, len(audio_data), segment_length):
            segment = audio_data[i:i+segment_length]
            if segment:
                segment_rms = math.sqrt(sum(x*x for x in segment) / len(segment))
                segments.append(segment_rms)
        
        # 簡単なBPM推定
        energy_peaks = []
        for i, rms in enumerate(segments):
            if i > 0 and i < len(segments) - 1:
                if rms > segments[i-1] and rms > segments[i+1]:
                    energy_peaks.append(i * 2)  # 時間（秒）
        
        estimated_bpm = 0
        if len(energy_peaks) > 1:
            avg_interval = sum(energy_peaks[i+1] - energy_peaks[i] for i in range(len(energy_peaks)-1)) / (len(energy_peaks)-1)
            if avg_interval > 0:
                estimated_bpm = 60 / avg_interval
        
        return {
            "file_info": {
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024*1024), 2),
                "duration_seconds": round(duration, 2),
                "sample_rate": sample_rate,
                "channels": channels,
                "sample_width_bytes": sample_width,
                "total_frames": frames
            },
            "audio_analysis": {
                "max_amplitude": max_amplitude,
                "rms_average": round(rms, 2),
                "dynamic_range_ratio": round(dynamic_range_approx, 2),
                "estimated_bpm": round(estimated_bpm, 1) if estimated_bpm > 0 else "推定不可",
                "energy_segments": len(segments),
                "energy_peaks_count": len(energy_peaks),
                "energy_peaks_times": energy_peaks
            },
            "structure_estimate": {
                "total_segments": len(segments),
                "peak_positions_seconds": energy_peaks,
                "estimated_intro_length": min(8, duration * 0.2),
                "estimated_outro_length": min(8, duration * 0.2),
                "segment_rms_values": segments
            }
        }
        
    except Exception as e:
        return {"error": f"分析エラー: {str(e)}"}

def generate_plan_comparison(result, target_specs):
    """計画との詳細比較"""
    if "error" in result:
        return {"error": result["error"]}
    
    file_info = result["file_info"]
    audio_info = result["audio_analysis"]
    
    comparison = {}
    
    # 長さ比較
    duration = file_info["duration_seconds"]
    target_duration = target_specs["duration"]
    if target_duration[0] <= duration <= target_duration[1]:
        comparison["duration"] = {
            "status": "✅ 適合",
            "actual": f"{duration}秒",
            "target": f"{target_duration[0]}-{target_duration[1]}秒",
            "deviation": "範囲内"
        }
    else:
        deviation = min(abs(duration - target_duration[0]), abs(duration - target_duration[1]))
        comparison["duration"] = {
            "status": "⚠️ 範囲外",
            "actual": f"{duration}秒",
            "target": f"{target_duration[0]}-{target_duration[1]}秒",
            "deviation": f"{deviation:.1f}秒差"
        }
    
    # BPM比較
    estimated_bpm = audio_info["estimated_bpm"]
    target_bpm = target_specs["bpm"]
    if isinstance(estimated_bpm, (int, float)):
        if target_bpm[0] <= estimated_bpm <= target_bpm[1]:
            comparison["bpm"] = {
                "status": "✅ 適合",
                "actual": f"{estimated_bpm} BPM",
                "target": f"{target_bpm[0]}-{target_bpm[1]} BPM",
                "deviation": "範囲内"
            }
        else:
            deviation = min(abs(estimated_bpm - target_bpm[0]), abs(estimated_bpm - target_bpm[1]))
            comparison["bpm"] = {
                "status": "⚠️ 範囲外",
                "actual": f"{estimated_bpm} BPM",
                "target": f"{target_bpm[0]}-{target_bpm[1]} BPM",
                "deviation": f"{deviation:.1f} BPM差"
            }
    else:
        comparison["bpm"] = {
            "status": "❓ 推定不可",
            "actual": str(estimated_bpm),
            "target": f"{target_bpm[0]}-{target_bpm[1]} BPM",
            "deviation": "測定困難"
        }
    
    return comparison

def analyze_structure_sections(result, target_structure):
    """構造分析の詳細"""
    if "error" in result:
        return {"error": result["error"]}
    
    duration = result["file_info"]["duration_seconds"]
    peaks = result["structure_estimate"]["peak_positions_seconds"]
    
    # 理想的な構造との比較
    ideal_intro_end = target_structure["intro"]
    ideal_development_end = ideal_intro_end + target_structure["development"][1]
    ideal_climax_end = ideal_development_end + target_structure["climax"][1]
    
    analysis = {
        "actual_structure": {
            "total_duration": duration,
            "peak_count": len(peaks),
            "peak_times": peaks
        },
        "target_structure": target_structure,
        "section_analysis": {}
    }
    
    # セクション推定
    if duration > 0:
        intro_ratio = min(8, duration * 0.2) / duration
        outro_ratio = min(8, duration * 0.2) / duration
        development_ratio = 1 - intro_ratio - outro_ratio
        
        analysis["section_analysis"] = {
            "estimated_intro": f"0-{min(8, duration * 0.2):.1f}秒",
            "estimated_development": f"{min(8, duration * 0.2):.1f}-{duration - min(8, duration * 0.2):.1f}秒",
            "estimated_outro": f"{duration - min(8, duration * 0.2):.1f}-{duration:.1f}秒",
            "intro_ratio": f"{intro_ratio:.1%}",
            "development_ratio": f"{development_ratio:.1%}",
            "outro_ratio": f"{outro_ratio:.1%}"
        }
    
    return analysis

def generate_visual_recommendations(result):
    """視覚的要素への具体的提案"""
    if "error" in result:
        return {"error": result["error"]}
    
    file_info = result["file_info"]
    audio_info = result["audio_analysis"]
    
    duration = file_info["duration_seconds"]
    estimated_bpm = audio_info["estimated_bpm"]
    dynamic_range = audio_info["dynamic_range_ratio"]
    
    recommendations = {
        "color_palette": [],
        "visual_rhythm": "",
        "camera_movement": "",
        "lighting_style": "",
        "composition_style": "",
        "timing_suggestions": {}
    }
    
    # BPMベースの視覚リズム
    if isinstance(estimated_bpm, (int, float)):
        beat_interval = 60 / estimated_bpm
        recommendations["timing_suggestions"]["beat_interval"] = f"{beat_interval:.2f}秒"
        
        if estimated_bpm < 80:
            recommendations["visual_rhythm"] = "ゆっくりとした瞑想的な動き、長いトランジション"
            recommendations["camera_movement"] = "非常に滑らかなスローモーション、静的カットメイン"
        elif estimated_bpm <= 100:
            recommendations["visual_rhythm"] = "穏やかで流れるような動き、安定したペース"
            recommendations["camera_movement"] = "滑らかなパン・ティルト、緩やかなズーム"
        else:
            recommendations["visual_rhythm"] = "リズミカルで活発な動き、定期的な変化"
            recommendations["camera_movement"] = "ダイナミックなカメラワーク、リズムに同期"
    else:
        recommendations["visual_rhythm"] = "一定で落ち着いた動き、ミニマルな変化"
        recommendations["camera_movement"] = "静的または非常にゆっくりとした動き"
    
    # ダイナミックレンジベースの提案
    if dynamic_range > 3:
        recommendations["lighting_style"] = "コントラストの強い照明、ドラマチックな陰影"
        recommendations["color_palette"] = ["深いブルー", "鮮やかなホワイト", "アクセントゴールド"]
    elif dynamic_range > 2:
        recommendations["lighting_style"] = "バランスの取れた照明、適度なコントラスト"
        recommendations["color_palette"] = ["ソフトグレー", "温かいホワイト", "淡いブルー"]
    else:
        recommendations["lighting_style"] = "柔らかく均一な照明、ミニマルなコントラスト"
        recommendations["color_palette"] = ["クリームホワイト", "ライトグレー", "微細なゴールド"]
    
    # 長さベースの構成提案
    if duration < 30:
        recommendations["composition_style"] = "コンパクトで集中的、シンプルな3段構成"
    elif duration <= 40:
        recommendations["composition_style"] = "バランスの取れた4段構成、十分な展開時間"
    else:
        recommendations["composition_style"] = "ゆったりとした5段構成、十分な余白"
    
    return recommendations

def main():
    # ファイルパス
    audio_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250721-16406899626/music/generated-music.wav"
    
    print("🎵 音楽分析専門レポート実行中...")
    print(f"📁 対象ファイル: {audio_file}")
    print("=" * 80)
    
    # 分析実行
    result = basic_wav_analysis(audio_file)
    
    # 目標仕様
    target_specs = {
        "duration": (30, 40),  # 秒
        "bpm": (80, 100),      # BPM範囲
        "style": "ミニマリストピアノソロ",
        "structure": {
            "intro": 8,
            "development": (12, 16),
            "climax": (8, 10),
            "outro": (6, 8)
        }
    }
    
    if "error" in result:
        print(f"❌ エラー: {result['error']}")
        return
    
    # 詳細分析
    plan_comparison = generate_plan_comparison(result, target_specs)
    structure_analysis = analyze_structure_sections(result, target_specs["structure"])
    visual_recommendations = generate_visual_recommendations(result)
    
    # 1. 基本情報の報告
    print("📊 1. 基本ファイル情報")
    print("-" * 40)
    file_info = result["file_info"]
    print(f"  ファイルサイズ: {file_info['file_size_mb']} MB")
    print(f"  長さ: {file_info['duration_seconds']} 秒")
    print(f"  サンプルレート: {file_info['sample_rate']} Hz")
    print(f"  チャンネル数: {file_info['channels']}")
    print(f"  ビット深度: {file_info['sample_width_bytes'] * 8} bit")
    print()
    
    # 2. 聴覚的分析（推定）
    print("🎧 2. 聴覚的分析（推定ベース）")
    print("-" * 40)
    audio_info = result["audio_analysis"]
    print(f"  推定BPM: {audio_info['estimated_bpm']}")
    print(f"  最大振幅: {audio_info['max_amplitude']}")
    print(f"  RMS平均: {audio_info['rms_average']}")
    print(f"  ダイナミクス比: {audio_info['dynamic_range_ratio']}")
    print(f"  エネルギーピーク数: {audio_info['energy_peaks_count']}")
    
    if audio_info['energy_peaks_count'] > 0:
        print(f"  ピーク位置: {audio_info['energy_peaks_times']}")
    print()
    
    # 3. 構造分析
    print("🏗️ 3. 音楽構造分析")
    print("-" * 40)
    if "error" not in structure_analysis:
        actual = structure_analysis["actual_structure"]
        sections = structure_analysis["section_analysis"]
        print(f"  総長: {actual['total_duration']}秒")
        print(f"  検出ピーク数: {actual['peak_count']}")
        print(f"  推定イントロ: {sections['estimated_intro']}")
        print(f"  推定展開部: {sections['estimated_development']}")
        print(f"  推定アウトロ: {sections['estimated_outro']}")
    print()
    
    # 4. 計画との比較
    print("📋 4. 計画目標との比較")
    print("-" * 40)
    if "error" not in plan_comparison:
        duration_comp = plan_comparison["duration"]
        bpm_comp = plan_comparison["bpm"]
        
        print(f"  長さ: {duration_comp['status']}")
        print(f"    実際: {duration_comp['actual']}")
        print(f"    目標: {duration_comp['target']}")
        print(f"    差分: {duration_comp['deviation']}")
        print()
        print(f"  BPM: {bpm_comp['status']}")
        print(f"    実際: {bpm_comp['actual']}")
        print(f"    目標: {bpm_comp['target']}")
        print(f"    差分: {bpm_comp['deviation']}")
    print()
    
    # 5. 視覚的要素への示唆
    print("🎨 5. 画像・動画プロンプト微調整への示唆")
    print("-" * 40)
    if "error" not in visual_recommendations:
        vis_rec = visual_recommendations
        print(f"  推奨色彩: {', '.join(vis_rec['color_palette'])}")
        print(f"  視覚リズム: {vis_rec['visual_rhythm']}")
        print(f"  カメラ動作: {vis_rec['camera_movement']}")
        print(f"  照明スタイル: {vis_rec['lighting_style']}")
        print(f"  構成スタイル: {vis_rec['composition_style']}")
        
        if "beat_interval" in vis_rec["timing_suggestions"]:
            print(f"  ビート間隔: {vis_rec['timing_suggestions']['beat_interval']}")
    print()
    
    # 6. 総合評価
    print("📈 6. 総合評価・推奨事項")
    print("-" * 40)
    
    # 適合性スコア計算
    score = 0
    max_score = 2
    
    if "error" not in plan_comparison:
        if "✅" in plan_comparison["duration"]["status"]:
            score += 1
        if "✅" in plan_comparison["bpm"]["status"]:
            score += 1
    
    compatibility_percentage = (score / max_score) * 100
    print(f"  計画適合性: {compatibility_percentage:.0f}% ({score}/{max_score}項目適合)")
    
    if compatibility_percentage >= 80:
        print("  🟢 総合評価: 優秀 - そのまま動画制作に進行可能")
    elif compatibility_percentage >= 60:
        print("  🟡 総合評価: 良好 - 軽微な調整で動画制作可能")
    else:
        print("  🔴 総合評価: 要改善 - 大幅な調整または再生成推奨")
    
    print()
    print("📝 推奨次ステップ:")
    if compatibility_percentage >= 80:
        print("  1. 画像生成プロンプトに音楽特徴を反映")
        print("  2. 動画プロンプトに推奨カメラワークを組み込み")
        print("  3. 色彩パレットを視覚コンテンツに適用")
    else:
        print("  1. 音楽の再生成または調整を検討")
        print("  2. より柔軟な画像・動画プロンプト設計")
        print("  3. 音楽特徴に合わせた新規戦略立案")
    
    # 結果をJSONで保存
    analysis_summary = {
        "timestamp": datetime.now().isoformat(),
        "file_analysis": result,
        "plan_comparison": plan_comparison,
        "structure_analysis": structure_analysis,
        "visual_recommendations": visual_recommendations,
        "compatibility_score": compatibility_percentage,
        "next_steps": "画像・動画プロンプト微調整" if compatibility_percentage >= 80 else "音楽調整検討"
    }
    
    output_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250721-16406899626/analysis/music_analysis_report.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_summary, f, ensure_ascii=False, indent=2)
        print(f"\n💾 詳細結果を保存: {output_file}")
    except Exception as e:
        print(f"\n⚠️ ファイル保存エラー: {e}")
    
    print("\n" + "=" * 80)
    print("✅ 音楽分析専門レポート完了！")
    
    return analysis_summary

if __name__ == "__main__":
    main()