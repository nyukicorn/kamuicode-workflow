#!/usr/bin/env python3
"""
手動音楽分析レポート - ライブラリ不要版
基本的な音楽ファイル情報の分析とレポート生成
"""

import wave
import os
import struct
import sys
from datetime import datetime

def analyze_wav_file(file_path):
    """WAVファイルの基本情報分析"""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            # 基本情報取得
            sample_rate = wav_file.getframerate()
            num_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            num_frames = wav_file.getnframes()
            duration = num_frames / sample_rate
            
            # 音声データ読み込み
            frames = wav_file.readframes(num_frames)
            
            # 16ビットステレオの場合の音量分析
            if sample_width == 2:
                samples = struct.unpack(f'<{num_frames * num_channels}h', frames)
                
                # 音量レベル分析（簡易版）
                max_amplitude = max(abs(sample) for sample in samples)
                avg_amplitude = sum(abs(sample) for sample in samples) / len(samples)
                
                # 簡易テンポ推定（波形の変化点を検出）
                window_size = sample_rate // 10  # 0.1秒間隔
                amplitude_changes = []
                
                for i in range(0, len(samples) - window_size, window_size):
                    window_avg = sum(abs(samples[i:i+window_size])) / window_size
                    amplitude_changes.append(window_avg)
                
                # 変化点の検出（簡易BPM推定）
                significant_changes = 0
                threshold = avg_amplitude * 1.2
                
                for i in range(1, len(amplitude_changes)):
                    if abs(amplitude_changes[i] - amplitude_changes[i-1]) > threshold * 0.1:
                        significant_changes += 1
                
                estimated_bpm = (significant_changes * 60) / duration if duration > 0 else 0
                
                return {
                    'duration': duration,
                    'sample_rate': sample_rate,
                    'channels': num_channels,
                    'bit_depth': sample_width * 8,
                    'file_size': os.path.getsize(file_path),
                    'max_amplitude': max_amplitude,
                    'avg_amplitude': avg_amplitude,
                    'estimated_bpm': estimated_bpm,
                    'amplitude_changes': amplitude_changes,
                    'dynamic_range': max_amplitude - min(abs(sample) for sample in samples[:1000])
                }
            else:
                return {
                    'duration': duration,
                    'sample_rate': sample_rate,
                    'channels': num_channels,
                    'bit_depth': sample_width * 8,
                    'file_size': os.path.getsize(file_path),
                    'estimated_bpm': 0,
                    'note': 'Basic analysis only - unsupported bit depth'
                }
                
    except Exception as e:
        return {'error': f'分析エラー: {e}'}

def generate_structure_analysis(duration, amplitude_changes):
    """音楽構造の推定分析"""
    if not amplitude_changes or duration <= 0:
        return []
    
    # 4つのセクションに分割
    section_duration = duration / 4
    sections = []
    samples_per_section = len(amplitude_changes) // 4
    
    section_names = ['導入部 (イントロ)', 'メイン展開部', 'クライマックス部', '余韻部 (アウトロ)']
    
    for i in range(4):
        start_idx = i * samples_per_section
        end_idx = (i + 1) * samples_per_section if i < 3 else len(amplitude_changes)
        
        if start_idx < len(amplitude_changes):
            section_samples = amplitude_changes[start_idx:end_idx]
            avg_amplitude = sum(section_samples) / len(section_samples) if section_samples else 0
            max_amplitude = max(section_samples) if section_samples else 0
            min_amplitude = min(section_samples) if section_samples else 0
            
            sections.append({
                'name': section_names[i],
                'time_range': f'{i * section_duration:.1f}-{(i + 1) * section_duration:.1f}秒',
                'avg_amplitude': avg_amplitude,
                'max_amplitude': max_amplitude,
                'dynamic_range': max_amplitude - min_amplitude,
                'intensity': 'high' if avg_amplitude > sum(amplitude_changes) / len(amplitude_changes) else 'low'
            })
    
    return sections

def analyze_concept_match(analysis_data):
    """バラの花オルゴールコンセプトとの適合度分析"""
    duration = analysis_data.get('duration', 0)
    estimated_bpm = analysis_data.get('estimated_bpm', 0)
    
    # 時間長の適合性
    target_duration_range = (30, 40)
    duration_match = target_duration_range[0] <= duration <= target_duration_range[1]
    
    # テンポの適合性（オルゴール想定: 60-80 BPM）
    target_bpm_range = (50, 90)  # オルゴールの一般的範囲を広めに設定
    bpm_match = target_bpm_range[0] <= estimated_bpm <= target_bpm_range[1] if estimated_bpm > 0 else None
    
    # 音質特性の評価
    sample_rate = analysis_data.get('sample_rate', 0)
    bit_depth = analysis_data.get('bit_depth', 0)
    
    quality_assessment = []
    if sample_rate >= 44100:
        quality_assessment.append('✓ 高品質サンプリングレート')
    else:
        quality_assessment.append('⚠ 低めのサンプリングレート')
    
    if bit_depth >= 16:
        quality_assessment.append('✓ 十分なビット深度')
    else:
        quality_assessment.append('⚠ 低ビット深度')
    
    return {
        'duration_match': duration_match,
        'duration_score': f'{duration:.2f}秒 (目標: {target_duration_range[0]}-{target_duration_range[1]}秒)',
        'bpm_match': bpm_match,
        'bpm_score': f'{estimated_bpm:.1f} BPM (推定)' if estimated_bpm > 0 else '推定不可',
        'quality_assessment': quality_assessment,
        'overall_compatibility': calculate_compatibility_score(duration_match, bpm_match, sample_rate, bit_depth)
    }

def calculate_compatibility_score(duration_match, bpm_match, sample_rate, bit_depth):
    """総合適合度スコア計算"""
    score = 0
    max_score = 4
    
    if duration_match:
        score += 1
    if bpm_match is not None and bpm_match:
        score += 1
    if sample_rate >= 44100:
        score += 1
    if bit_depth >= 16:
        score += 1
    
    percentage = (score / max_score) * 100
    
    if percentage >= 75:
        return f'{percentage:.0f}% - 優秀'
    elif percentage >= 50:
        return f'{percentage:.0f}% - 良好'
    else:
        return f'{percentage:.0f}% - 要改善'

def generate_detailed_report(file_path):
    """詳細分析レポートの生成"""
    print("🎵 音楽分析レポート - バラの花オルゴール")
    print("=" * 60)
    print(f"分析日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    print(f"ファイル: {os.path.basename(file_path)}")
    print()
    
    # 基本分析
    analysis = analyze_wav_file(file_path)
    
    if 'error' in analysis:
        print(f"❌ {analysis['error']}")
        return
    
    # 基本音楽特性
    print("📊 基本音楽特性")
    print("-" * 30)
    print(f"長さ: {analysis['duration']:.2f}秒")
    print(f"サンプリングレート: {analysis['sample_rate']:,} Hz")
    print(f"チャンネル: {analysis['channels']} ({'ステレオ' if analysis['channels'] == 2 else 'モノラル'})")
    print(f"ビット深度: {analysis['bit_depth']} bit")
    print(f"ファイルサイズ: {analysis['file_size'] / 1024:.1f} KB")
    
    if 'estimated_bpm' in analysis and analysis['estimated_bpm'] > 0:
        print(f"推定テンポ: {analysis['estimated_bpm']:.1f} BPM")
    else:
        print("推定テンポ: 分析不可")
    
    if 'avg_amplitude' in analysis:
        print(f"平均音量レベル: {analysis['avg_amplitude']:.0f}")
        print(f"最大音量レベル: {analysis['max_amplitude']:.0f}")
        print(f"ダイナミックレンジ: {analysis['dynamic_range']:.0f}")
    
    print()
    
    # 音楽構造分析
    if 'amplitude_changes' in analysis:
        structure = generate_structure_analysis(analysis['duration'], analysis['amplitude_changes'])
        print("🎼 音楽構造分析")
        print("-" * 30)
        for section in structure:
            print(f"{section['name']} ({section['time_range']})")
            print(f"  平均強度: {section['avg_amplitude']:.1f}")
            print(f"  最大強度: {section['max_amplitude']:.1f}")
            print(f"  変化幅: {section['dynamic_range']:.1f}")
            print(f"  特徴: {section['intensity']} intensity")
            print()
    
    # コンセプト適合度分析
    concept_analysis = analyze_concept_match(analysis)
    print("🌹 バラの花オルゴール・コンセプト適合度")
    print("-" * 40)
    print(f"時間長適合性: {'✓ 適合' if concept_analysis['duration_match'] else '✗ 非適合'}")
    print(f"  {concept_analysis['duration_score']}")
    print()
    
    if concept_analysis['bpm_match'] is not None:
        print(f"テンポ適合性: {'✓ 適合' if concept_analysis['bpm_match'] else '✗ 非適合'}")
        print(f"  {concept_analysis['bpm_score']}")
    else:
        print(f"テンポ適合性: 分析不可")
        print(f"  {concept_analysis['bpm_score']}")
    print()
    
    print("音質評価:")
    for assessment in concept_analysis['quality_assessment']:
        print(f"  {assessment}")
    print()
    
    print(f"総合適合度: {concept_analysis['overall_compatibility']}")
    print()
    
    # 楽器・音色特徴推定
    print("🎹 推定音色特徴")
    print("-" * 30)
    
    if analysis['sample_rate'] >= 44100 and analysis['channels'] == 2:
        print("✓ オルゴール音源に適したステレオ高品質録音")
    
    if 'avg_amplitude' in analysis:
        if analysis['avg_amplitude'] < 10000:
            print("✓ 繊細で上品な音量レベル（オルゴール特性に適合）")
        elif analysis['avg_amplitude'] < 20000:
            print("○ 適度な音量レベル")
        else:
            print("⚠ やや音量が大きめ（オルゴールらしい繊細さには要調整）")
    
    # 雰囲気・感情表現評価
    print()
    print("💫 雰囲気・感情表現分析")
    print("-" * 30)
    
    duration = analysis['duration']
    if 30 <= duration <= 40:
        print("🎭 時間感: バラの美しさを十分に表現する適切な長さ")
    elif duration < 30:
        print("🎭 時間感: やや短め - バラの魅力をより長く表現できる余地あり")
    else:
        print("🎭 時間感: やや長め - より簡潔な美しさの表現が可能")
    
    estimated_bpm = analysis.get('estimated_bpm', 0)
    if 50 <= estimated_bpm <= 70:
        print("🎵 テンポ感: 優雅でゆったりとしたバラの花のような美しさ")
    elif 70 < estimated_bpm <= 90:
        print("🎵 テンポ感: 穏やかで心地よい、バラ園を歩くような心地よさ")
    elif estimated_bpm > 0:
        print("🎵 テンポ感: 活発で生き生きとした、バラの生命力を表現")
    else:
        print("🎵 テンポ感: 分析不可 - 手動確認が必要")
    
    if 'dynamic_range' in analysis:
        if analysis['dynamic_range'] > 5000:
            print("🎶 表現力: 感情豊かでダイナミックな表現")
        else:
            print("🎶 表現力: 穏やかで安定した、オルゴールらしい表現")
    
    print()
    print("📝 総合評価・推奨事項")
    print("-" * 30)
    
    recommendations = []
    
    if not concept_analysis['duration_match']:
        if duration < 30:
            recommendations.append("⏱️ 音楽を30-40秒に延長してバラの美しさをより長く表現")
        else:
            recommendations.append("⏱️ 音楽を30-40秒に短縮してより洗練された表現に")
    
    if concept_analysis['bpm_match'] is False:
        recommendations.append("🎵 テンポを60-80 BPMに調整してオルゴールらしい優雅さを強調")
    
    if analysis.get('sample_rate', 0) < 44100:
        recommendations.append("🔊 サンプリングレートを44.1kHz以上に向上して音質改善")
    
    if len(recommendations) == 0:
        print("✅ 現在の音楽は「バラの花オルゴール」コンセプトに適合しています")
        print("🏆 美しい音楽が生成されています")
    else:
        print("🔧 改善推奨事項:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    print()
    print(f"🎯 最終評価: {concept_analysis['overall_compatibility']}")

def main():
    """メイン実行関数"""
    if len(sys.argv) != 2:
        print("使用方法: python manual_music_analysis.py <音楽ファイルパス>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"エラー: ファイルが見つかりません - {file_path}")
        sys.exit(1)
    
    # 音楽分析実行
    generate_detailed_report(file_path)

if __name__ == "__main__":
    main()