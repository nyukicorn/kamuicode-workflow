#!/usr/bin/env python3
"""
総合音楽分析スクリプト
音楽ファイルの詳細な特徴を分析し、視覚的要素との関連性を評価する
"""

import wave
import struct
import math
import os
import sys

def analyze_music_file(file_path):
    """音楽ファイルの包括的分析"""
    
    if not os.path.exists(file_path):
        print(f"エラー: ファイルが見つかりません: {file_path}")
        return None
    
    # WAVEファイルの基本情報を取得
    try:
        with wave.open(file_path, 'rb') as wav_file:
            # 基本パラメータ
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            frames = wav_file.getnframes()
            duration = frames / float(frame_rate)
            
            # 音響データを読み込み
            raw_audio = wav_file.readframes(frames)
            
        print("=== 音楽ファイル詳細分析レポート ===")
        print(f"ファイルパス: {file_path}")
        print()
        
        # 1. 基本情報
        print("1. 基本音響情報:")
        print(f"   - チャンネル数: {channels} ({'ステレオ' if channels == 2 else 'モノラル'})")
        print(f"   - サンプル幅: {sample_width} バイト ({sample_width * 8} bit)")
        print(f"   - サンプリングレート: {frame_rate} Hz")
        print(f"   - フレーム数: {frames:,}")
        print(f"   - 音楽の長さ: {duration:.2f} 秒 ({duration//60:.0f}分{duration%60:.1f}秒)")
        print()
        
        # 2. 音量分析
        if sample_width == 2:  # 16-bit
            audio_data = struct.unpack('<' + 'h' * (len(raw_audio) // 2), raw_audio)
        elif sample_width == 1:  # 8-bit
            audio_data = struct.unpack('<' + 'B' * len(raw_audio), raw_audio)
        else:
            print("   サポートされていないサンプル幅です")
            return None
        
        # ステレオの場合、チャンネルを分離
        if channels == 2:
            left_channel = audio_data[0::2]
            right_channel = audio_data[1::2]
            # 平均音量計算用にミックス
            audio_data = [(l + r) / 2 for l, r in zip(left_channel, right_channel)]
        
        # 音量統計
        max_amplitude = max(abs(sample) for sample in audio_data)
        avg_amplitude = sum(abs(sample) for sample in audio_data) / len(audio_data)
        rms_amplitude = math.sqrt(sum(sample**2 for sample in audio_data) / len(audio_data))
        
        # 正規化（16-bitの場合）
        max_possible = 2**(sample_width * 8 - 1) - 1
        max_amplitude_norm = max_amplitude / max_possible
        avg_amplitude_norm = avg_amplitude / max_possible
        rms_amplitude_norm = rms_amplitude / max_possible
        
        print("2. 音量・動的特徴:")
        print(f"   - 最大音量: {max_amplitude_norm:.3f} ({max_amplitude_norm*100:.1f}%)")
        print(f"   - 平均音量: {avg_amplitude_norm:.3f} ({avg_amplitude_norm*100:.1f}%)")
        print(f"   - RMS音量: {rms_amplitude_norm:.3f} ({rms_amplitude_norm*100:.1f}%)")
        
        # 動的レンジ
        dynamic_range = max_amplitude_norm / (avg_amplitude_norm + 0.001)  # ゼロ除算防止
        print(f"   - 動的レンジ: {dynamic_range:.2f} ({'高' if dynamic_range > 3 else '中' if dynamic_range > 2 else '低'})")
        
        # 3. 時間軸分析（セグメント別音量変化）
        segment_count = min(10, int(duration))  # 最大10セグメント
        segment_length = len(audio_data) // segment_count
        
        print()
        print("3. 音楽構造分析（時間軸での音量変化）:")
        segment_volumes = []
        for i in range(segment_count):
            start = i * segment_length
            end = start + segment_length
            segment_data = audio_data[start:end]
            segment_rms = math.sqrt(sum(sample**2 for sample in segment_data) / len(segment_data))
            segment_rms_norm = segment_rms / max_possible
            segment_volumes.append(segment_rms_norm)
            
            time_start = i * (duration / segment_count)
            time_end = (i + 1) * (duration / segment_count)
            print(f"   - セグメント {i+1} ({time_start:.1f}-{time_end:.1f}秒): 音量 {segment_rms_norm:.3f}")
        
        # 音楽構造の推定
        print()
        print("4. 推定される音楽構造:")
        
        # 音量変化パターンから構造を推定
        volume_changes = []
        for i in range(1, len(segment_volumes)):
            change = segment_volumes[i] - segment_volumes[i-1]
            volume_changes.append(change)
        
        # 開始部分の特徴
        if segment_volumes[0] < avg_amplitude_norm * 0.8:
            print("   - イントロ: 静かな開始（フェードイン的）")
        else:
            print("   - イントロ: 直接的な開始")
        
        # 中間部分の特徴
        max_volume_index = segment_volumes.index(max(segment_volumes))
        if max_volume_index > len(segment_volumes) * 0.3 and max_volume_index < len(segment_volumes) * 0.8:
            print(f"   - クライマックス: セグメント {max_volume_index + 1} 付近（{max_volume_index * (duration / segment_count):.1f}秒頃）")
        
        # 終了部分の特徴
        if segment_volumes[-1] < segment_volumes[-2]:
            print("   - アウトロ: フェードアウト的終了")
        else:
            print("   - アウトロ: 直接的な終了")
        
        # 5. 周波数分析（簡易版）
        print()
        print("5. 音色・周波数特徴（簡易分析）:")
        
        # 高周波・低周波成分の簡易推定
        # 音量の変動性から推定
        volume_variance = sum((vol - avg_amplitude_norm)**2 for vol in segment_volumes) / len(segment_volumes)
        
        if volume_variance < 0.001:
            texture = "非常に滑らか"
        elif volume_variance < 0.005:
            texture = "滑らか"
        elif volume_variance < 0.02:
            texture = "中程度の変化"
        else:
            texture = "動的・変化に富む"
        
        print(f"   - 音量変動: {texture}")
        print(f"   - 音量分散: {volume_variance:.6f}")
        
        # 6. テンポ推定（簡易版）
        print()
        print("6. テンポ分析（簡易推定）:")
        
        # 短時間フレームでの音量変化を分析してビート推定
        frame_size = frame_rate // 10  # 0.1秒フレーム
        frames_per_analysis = len(audio_data) // frame_size
        
        frame_energies = []
        for i in range(frames_per_analysis):
            start = i * frame_size
            end = start + frame_size
            frame_data = audio_data[start:end]
            frame_energy = sum(sample**2 for sample in frame_data) / len(frame_data)
            frame_energies.append(frame_energy)
        
        # エネルギー変化からテンポを推定
        energy_changes = []
        for i in range(1, len(frame_energies)):
            change = abs(frame_energies[i] - frame_energies[i-1])
            energy_changes.append(change)
        
        avg_energy_change = sum(energy_changes) / len(energy_changes) if energy_changes else 0
        
        # テンポカテゴリの推定
        if avg_energy_change < avg_amplitude_norm * 0.1:
            tempo_category = "非常にゆっくり (60-80 BPM推定)"
            tempo_description = "瞑想的・アンビエント"
        elif avg_energy_change < avg_amplitude_norm * 0.3:
            tempo_category = "ゆっくり (80-100 BPM推定)"
            tempo_description = "リラックス・バラード"
        elif avg_energy_change < avg_amplitude_norm * 0.6:
            tempo_category = "中程度 (100-120 BPM推定)"
            tempo_description = "中程度の動き"
        else:
            tempo_category = "速い (120+ BPM推定)"
            tempo_description = "活発・動的"
        
        print(f"   - 推定テンポ: {tempo_category}")
        print(f"   - 特徴: {tempo_description}")
        
        # 7. 感情・雰囲気分析
        print()
        print("7. 感情・雰囲気分析:")
        
        mood_indicators = []
        
        # 音量レベルから感情推定
        if avg_amplitude_norm < 0.3:
            mood_indicators.append("静寂・内省的")
        elif avg_amplitude_norm < 0.6:
            mood_indicators.append("穏やか・リラックス")
        else:
            mood_indicators.append("力強い・エネルギッシュ")
        
        # 動的レンジから感情推定
        if dynamic_range < 2:
            mood_indicators.append("安定・一様")
        elif dynamic_range < 4:
            mood_indicators.append("適度な変化・表現豊か")
        else:
            mood_indicators.append("劇的・ドラマチック")
        
        # 音量変動から感情推定
        if volume_variance < 0.005:
            mood_indicators.append("平和・瞑想的")
        elif volume_variance < 0.02:
            mood_indicators.append("感情的・表現力豊か")
        else:
            mood_indicators.append("激動・情熱的")
        
        print(f"   - 感情的特徴: {', '.join(mood_indicators)}")
        
        # 8. 「静かな夜のピアノ曲」との適合性評価
        print()
        print("8. コンセプト適合性評価:")
        print("   「静かな夜のピアノ曲」コンセプトとの整合性:")
        
        compliance_score = 0
        compliance_details = []
        
        # 時間長評価 (30-40秒が理想)
        if 25 <= duration <= 45:
            compliance_score += 2
            compliance_details.append(f"✓ 時間長: {duration:.1f}秒 (理想範囲内)")
        elif 20 <= duration <= 50:
            compliance_score += 1
            compliance_details.append(f"○ 時間長: {duration:.1f}秒 (許容範囲)")
        else:
            compliance_details.append(f"△ 時間長: {duration:.1f}秒 (理想範囲外)")
        
        # 静寂性評価
        if avg_amplitude_norm < 0.4:
            compliance_score += 2
            compliance_details.append("✓ 音量レベル: 静寂・内省的に適している")
        elif avg_amplitude_norm < 0.6:
            compliance_score += 1
            compliance_details.append("○ 音量レベル: やや静か")
        else:
            compliance_details.append("△ 音量レベル: 静寂性に欠ける")
        
        # 夜の雰囲気評価
        if "静寂・内省的" in mood_indicators or "平和・瞑想的" in mood_indicators:
            compliance_score += 2
            compliance_details.append("✓ 雰囲気: 夜の静寂・内省性に適している")
        elif "穏やか・リラックス" in mood_indicators:
            compliance_score += 1
            compliance_details.append("○ 雰囲気: リラックス系で適度に適している")
        else:
            compliance_details.append("△ 雰囲気: 夜の静寂性に欠ける")
        
        # テンポ評価
        if "非常にゆっくり" in tempo_category or "ゆっくり" in tempo_category:
            compliance_score += 2
            compliance_details.append("✓ テンポ: ピアノバラード・アンビエントに適している")
        elif "中程度" in tempo_category:
            compliance_score += 1
            compliance_details.append("○ テンポ: 中程度で許容範囲")
        else:
            compliance_details.append("△ テンポ: 静かなピアノ曲には速すぎる")
        
        for detail in compliance_details:
            print(f"   {detail}")
        
        total_possible = 8
        print(f"\n   総合適合スコア: {compliance_score}/{total_possible} ({compliance_score/total_possible*100:.1f}%)")
        
        if compliance_score >= 7:
            print("   評価: 非常に良くコンセプトに適合している")
        elif compliance_score >= 5:
            print("   評価: おおむねコンセプトに適合している")
        elif compliance_score >= 3:
            print("   評価: 部分的にコンセプトに適合している")
        else:
            print("   評価: コンセプトとの適合性が低い")
        
        # 9. 視覚的要素との関連性提案
        print()
        print("9. 視覚的要素との関連性・提案:")
        
        # 音楽特徴から視覚要素を提案
        visual_suggestions = []
        
        if "静寂・内省的" in mood_indicators:
            visual_suggestions.append("深い青・紫系の色調（夜空、深海）")
            visual_suggestions.append("ゆっくりとした動き・フェード効果")
            visual_suggestions.append("星空・月明かり・静かな水面")
        
        if avg_amplitude_norm < 0.4:
            visual_suggestions.append("低明度・高コントラストの画像")
            visual_suggestions.append("ソフトフォーカス・ボケ効果")
        
        if dynamic_range < 3:
            visual_suggestions.append("安定した構図・穏やかなカメラワーク")
            visual_suggestions.append("グラデーション・滑らかな色変化")
        
        if duration < 40:
            visual_suggestions.append("シンプルな構成・要素を絞った画面")
            visual_suggestions.append("ワンシーンでの表現・場面転換は最小限")
        
        print("   推奨視覚要素:")
        for suggestion in visual_suggestions:
            print(f"   - {suggestion}")
        
        # 10. 改善提案
        print()
        print("10. 音楽改善提案（必要に応じて）:")
        
        improvements = []
        
        if duration > 45:
            improvements.append(f"時間を短縮（現在{duration:.1f}秒 → 35-40秒推奨）")
        elif duration < 25:
            improvements.append(f"時間を延長（現在{duration:.1f}秒 → 30-35秒推奨）")
        
        if avg_amplitude_norm > 0.6:
            improvements.append("全体音量を下げて静寂性を向上")
        
        if dynamic_range > 4:
            improvements.append("音量変化を抑えて安定感を向上")
        
        if improvements:
            print("   提案される改善点:")
            for improvement in improvements:
                print(f"   - {improvement}")
        else:
            print("   現在の音楽は概ねコンセプトに適合しており、大きな改善は不要")
        
        print()
        print("=== 分析完了 ===")
        return {
            'duration': duration,
            'channels': channels,
            'sample_rate': frame_rate,
            'bit_depth': sample_width * 8,
            'avg_amplitude': avg_amplitude_norm,
            'max_amplitude': max_amplitude_norm,
            'dynamic_range': dynamic_range,
            'compliance_score': compliance_score,
            'mood_indicators': mood_indicators,
            'visual_suggestions': visual_suggestions
        }
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def main():
    """メイン実行関数"""
    
    # ファイルパスを指定
    music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16396202448/music/generated-music.wav"
    
    # 分析実行
    result = analyze_music_file(music_file)
    
    if result:
        print(f"\n音楽分析が正常に完了しました。")
        print(f"詳細は上記のレポートをご参照ください。")
    else:
        print("音楽分析に失敗しました。")

if __name__ == "__main__":
    main()