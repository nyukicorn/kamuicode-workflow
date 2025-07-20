#!/usr/bin/env python3
"""
音楽分析レポート生成
"""
import wave
import struct
import math
import os
import json
from datetime import datetime

def get_file_info(file_path):
    """ファイル基本情報の取得"""
    try:
        file_size = os.path.getsize(file_path)
        return {
            "exists": True,
            "size_bytes": file_size,
            "size_mb": file_size / (1024 * 1024)
        }
    except:
        return {"exists": False}

def analyze_wav_basic(file_path):
    """WAVファイルの基本分析"""
    result = {
        "file_info": get_file_info(file_path),
        "analysis_timestamp": datetime.now().isoformat(),
        "file_path": file_path
    }
    
    if not result["file_info"]["exists"]:
        result["error"] = "ファイルが存在しません"
        return result
    
    try:
        with wave.open(file_path, 'rb') as wav_file:
            # 基本パラメータ
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            duration = frames / sample_rate
            
            result["basic_properties"] = {
                "duration_seconds": round(duration, 2),
                "sample_rate": sample_rate,
                "channels": channels,
                "sample_width_bytes": sample_width,
                "total_frames": frames,
                "bitrate_estimate": sample_rate * channels * sample_width * 8
            }
            
            # 戦略計画書との比較
            result["strategy_compliance"] = {
                "duration_target_30_40_sec": 30 <= duration <= 40,
                "duration_status": f"{duration:.1f}秒 (目標: 30-40秒)",
                "format_suitable": sample_rate >= 44100 and sample_width >= 2
            }
            
            # 音声データの読み込み（制限付き）
            max_samples = min(frames, sample_rate * 10)  # 最大10秒分
            raw_audio = wav_file.readframes(max_samples)
            
            # 基本的な音量分析
            if sample_width == 2:
                fmt = f'{max_samples * channels}h'
                audio_data = struct.unpack(fmt, raw_audio)
                
                # モノラル変換
                if channels == 2:
                    mono_data = [audio_data[i] + audio_data[i+1] for i in range(0, len(audio_data), 2)]
                    audio_data = mono_data
                
                # 正規化
                normalized_data = [x / 32768.0 for x in audio_data]
                
                # 音量統計
                abs_values = [abs(x) for x in normalized_data]
                result["volume_analysis"] = {
                    "max_amplitude": round(max(abs_values), 4),
                    "avg_amplitude": round(sum(abs_values) / len(abs_values), 4),
                    "rms_energy": round(math.sqrt(sum(x*x for x in normalized_data) / len(normalized_data)), 4)
                }
                
                # 簡易構造分析
                segment_size = len(normalized_data) // 4
                segments = []
                for i in range(4):
                    start = i * segment_size
                    end = start + segment_size if i < 3 else len(normalized_data)
                    segment_data = normalized_data[start:end]
                    segment_rms = math.sqrt(sum(x*x for x in segment_data) / len(segment_data))
                    segments.append(round(segment_rms, 4))
                
                result["structure_analysis"] = {
                    "segment_energies": segments,
                    "energy_variation": round(max(segments) - min(segments), 4),
                    "has_dynamic_range": (max(segments) - min(segments)) > 0.05
                }
                
                # 三部構成の判定
                if len(segments) >= 3:
                    intro = segments[0]
                    development = max(segments[1:-1])
                    outro = segments[-1]
                    
                    has_development = development > intro * 1.1
                    has_resolution = outro < development * 0.9
                    
                    result["structure_analysis"]["three_part_structure"] = {
                        "intro_energy": intro,
                        "development_energy": development,
                        "outro_energy": outro,
                        "has_development": has_development,
                        "has_resolution": has_resolution,
                        "confirmed": has_development and has_resolution
                    }
                
                # ループ性能分析
                loop_samples = min(segment_size, int(sample_rate))  # 1秒分
                start_loop = normalized_data[:loop_samples]
                end_loop = normalized_data[-loop_samples:]
                
                start_rms = math.sqrt(sum(x*x for x in start_loop) / len(start_loop))
                end_rms = math.sqrt(sum(x*x for x in end_loop) / len(end_loop))
                
                result["loop_analysis"] = {
                    "start_rms": round(start_rms, 4),
                    "end_rms": round(end_rms, 4),
                    "rms_difference": round(abs(start_rms - end_rms), 4),
                    "loop_suitable": abs(start_rms - end_rms) < 0.1
                }
                
    except Exception as e:
        result["error"] = str(e)
    
    return result

# 分析実行
music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16398936614/music/generated-music.wav"
analysis = analyze_wav_basic(music_file)

# 結果出力
print("音楽ファイル分析レポート")
print("=" * 60)

# ファイル情報
if analysis["file_info"]["exists"]:
    print(f"✓ ファイル読み込み成功")
    print(f"ファイルサイズ: {analysis['file_info']['size_mb']:.2f} MB")
else:
    print("✗ ファイルが見つかりません")
    exit()

# エラーチェック
if "error" in analysis:
    print(f"✗ 分析エラー: {analysis['error']}")
    exit()

# 基本プロパティ
props = analysis["basic_properties"]
print(f"\n【基本音響特性】")
print(f"楽曲の長さ: {props['duration_seconds']}秒")
print(f"サンプリングレート: {props['sample_rate']} Hz")
print(f"チャンネル数: {props['channels']}")
print(f"ビット深度: {props['sample_width_bytes'] * 8} bit")
print(f"推定ビットレート: {props['bitrate_estimate']:,} bps")

# 音量分析
if "volume_analysis" in analysis:
    vol = analysis["volume_analysis"]
    print(f"\n【音量統計】")
    print(f"最大振幅: {vol['max_amplitude']}")
    print(f"平均振幅: {vol['avg_amplitude']}")
    print(f"RMSエネルギー: {vol['rms_energy']}")

# 構造分析
if "structure_analysis" in analysis:
    struct_data = analysis["structure_analysis"]
    print(f"\n【音楽構造分析】")
    print(f"セグメント別エネルギー: {struct_data['segment_energies']}")
    print(f"エネルギー変動幅: {struct_data['energy_variation']}")
    print(f"ダイナミックレンジ有: {'✓' if struct_data['has_dynamic_range'] else '✗'}")
    
    if "three_part_structure" in struct_data:
        tps = struct_data["three_part_structure"]
        print(f"\n【三部構成分析】")
        print(f"イントロ部エネルギー: {tps['intro_energy']}")
        print(f"展開部エネルギー: {tps['development_energy']}")
        print(f"終結部エネルギー: {tps['outro_energy']}")
        print(f"展開部の盛り上がり: {'✓' if tps['has_development'] else '✗'}")
        print(f"終結部の静寂化: {'✓' if tps['has_resolution'] else '✗'}")
        print(f"三部構成確認: {'✓' if tps['confirmed'] else '✗'}")

# ループ分析
if "loop_analysis" in analysis:
    loop = analysis["loop_analysis"]
    print(f"\n【ループ性能分析】")
    print(f"開始部RMS: {loop['start_rms']}")
    print(f"終了部RMS: {loop['end_rms']}")
    print(f"RMS差: {loop['rms_difference']}")
    print(f"ループ適性: {'✓' if loop['loop_suitable'] else '✗'}")

# 戦略計画書との整合性
compliance = analysis["strategy_compliance"]
print(f"\n【戦略計画書との整合性】")
print(f"楽曲長さ（30-40秒目標）: {compliance['duration_status']} {'✓' if compliance['duration_target_30_40_sec'] else '✗'}")
print(f"音質フォーマット: {'✓' if compliance['format_suitable'] else '✗'}")

# 推定楽器構成
print(f"\n【推定楽器構成分析】")
if "volume_analysis" in analysis:
    vol = analysis["volume_analysis"]
    # RMSエネルギーと振幅から楽器特性を推定
    if vol["rms_energy"] < 0.3 and vol["avg_amplitude"] < 0.2:
        print("✓ アンビエント系（静寂な環境音楽）特徴を確認")
    
    if vol["max_amplitude"] < 0.8:
        print("✓ 過度な音圧なし（自然な音楽特徴）")
    
    # 構造から楽器推定
    if "structure_analysis" in analysis and analysis["structure_analysis"]["has_dynamic_range"]:
        print("✓ 楽器演奏による自然なダイナミクス変化を検出")

print(f"\n【総合評価】")
total_checks = 0
passed_checks = 0

# チェック項目
checks = [
    ("楽曲長さ適正", compliance["duration_target_30_40_sec"]),
    ("音質フォーマット", compliance["format_suitable"]),
]

if "structure_analysis" in analysis:
    checks.append(("ダイナミックレンジ", analysis["structure_analysis"]["has_dynamic_range"]))
    if "three_part_structure" in analysis["structure_analysis"]:
        checks.append(("三部構成", analysis["structure_analysis"]["three_part_structure"]["confirmed"]))

if "loop_analysis" in analysis:
    checks.append(("ループ適性", analysis["loop_analysis"]["loop_suitable"]))

for check_name, passed in checks:
    total_checks += 1
    if passed:
        passed_checks += 1
    print(f"{check_name}: {'✓' if passed else '✗'}")

print(f"\n適合率: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.1f}%)")

# JSON保存
output_dir = os.path.dirname(music_file).replace('/music', '/analysis')
os.makedirs(output_dir, exist_ok=True)

json_path = os.path.join(output_dir, 'music_analysis_report.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(analysis, f, indent=2, ensure_ascii=False)

print(f"\n詳細分析結果をJSONで保存: {json_path}")
print("=" * 60)
print("音楽分析完了!")
print("=" * 60)