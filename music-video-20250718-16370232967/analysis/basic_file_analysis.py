#!/usr/bin/env python3
"""
基本的なファイル分析スクリプト
外部依存関係なしで実行可能な分析
"""

import os
import wave
import struct
import json
from datetime import datetime

def analyze_wav_file(file_path):
    """WAVファイルの基本情報を分析"""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            # 基本的なWAVファイル情報
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            
            # 楽曲長の計算
            duration = frames / float(sample_rate)
            
            # ファイルサイズ
            file_size = os.path.getsize(file_path)
            
            return {
                'file_path': file_path,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'duration_seconds': round(duration, 2),
                'duration_minutes_seconds': f"{int(duration // 60)}:{int(duration % 60):02d}",
                'sample_rate': sample_rate,
                'channels': channels,
                'sample_width': sample_width,
                'total_frames': frames,
                'bit_rate': sample_rate * channels * sample_width * 8,
                'analysis_timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        return {'error': str(e)}

def compare_with_strategy(file_info):
    """戦略計画との比較"""
    if 'error' in file_info:
        return {'error': 'ファイル分析エラーのため比較できません'}
    
    duration = file_info['duration_seconds']
    
    # 戦略計画の基準値
    strategy_duration_min = 30
    strategy_duration_max = 40
    strategy_bpm = 75
    
    comparison = {
        'duration_analysis': {
            'actual_duration': duration,
            'expected_range': f"{strategy_duration_min}-{strategy_duration_max}秒",
            'status': 'OK' if strategy_duration_min <= duration <= strategy_duration_max else 'NEEDS_ADJUSTMENT',
            'difference_from_ideal': round(duration - 35, 2)  # 35秒を理想値として
        },
        'file_quality': {
            'sample_rate': file_info['sample_rate'],
            'channels': file_info['channels'],
            'bit_depth': file_info['sample_width'] * 8,
            'quality_rating': 'HIGH' if file_info['sample_rate'] >= 44100 else 'MEDIUM'
        },
        'estimated_beats': {
            'total_beats_at_75bpm': round((duration * 75) / 60, 1),
            'beat_structure_fit': 'GOOD' if 30 <= duration <= 40 else 'NEEDS_ADJUSTMENT'
        }
    }
    
    return comparison

def generate_analysis_template():
    """分析テンプレートを生成"""
    template = {
        'manual_analysis_required': {
            'tempo_bpm': {
                'method': 'ビート検出またはマニュアル測定',
                'target': 75,
                'tolerance': '70-80',
                'actual_value': 'TBD'
            },
            'musical_structure': {
                'intro': {'start': 0, 'end': 'TBD', 'characteristics': 'TBD'},
                'theme_1': {'start': 'TBD', 'end': 'TBD', 'characteristics': 'TBD'},
                'theme_2': {'start': 'TBD', 'end': 'TBD', 'characteristics': 'TBD'},
                'climax': {'start': 'TBD', 'end': 'TBD', 'characteristics': 'TBD'},
                'outro': {'start': 'TBD', 'end': 'TBD', 'characteristics': 'TBD'}
            },
            'instruments': {
                'primary': 'オルゴール',
                'secondary': 'TBD',
                'analysis_notes': 'スペクトル分析または聴取による判定が必要'
            },
            'emotional_elements': {
                'cute_elements': 'TBD',
                'melancholy_elements': 'TBD',
                'transition_points': 'TBD'
            },
            'volume_dynamics': {
                'loudest_section': 'TBD',
                'quietest_section': 'TBD',
                'dynamic_range': 'TBD'
            }
        },
        'recommendations_framework': {
            'if_too_short': [
                '楽曲を延長',
                '動画速度を遅くする',
                'リピート部分を追加'
            ],
            'if_too_long': [
                '楽曲を短縮',
                '動画速度を上げる',
                '構造を再分割'
            ],
            'if_tempo_off': [
                '動画速度で調整',
                '編集リズムを変更',
                'エフェクトで補完'
            ]
        }
    }
    
    return template

def main():
    # 音楽ファイルのパス
    audio_file = "../music/generated-music.wav"
    
    print("=== 基本的な音楽ファイル分析 ===")
    
    if not os.path.exists(audio_file):
        print(f"エラー: 音楽ファイルが見つかりません: {audio_file}")
        return None
    
    # 基本的なファイル分析
    print("1. ファイル情報分析中...")
    file_info = analyze_wav_file(audio_file)
    
    if 'error' in file_info:
        print(f"エラー: {file_info['error']}")
        return None
    
    # 戦略計画との比較
    print("2. 戦略計画比較中...")
    comparison = compare_with_strategy(file_info)
    
    # 分析テンプレート生成
    print("3. 分析テンプレート生成中...")
    template = generate_analysis_template()
    
    # 結果の統合
    results = {
        'basic_file_info': file_info,
        'strategy_comparison': comparison,
        'analysis_template': template,
        'analysis_summary': {
            'file_readable': True,
            'duration_status': comparison['duration_analysis']['status'],
            'quality_status': comparison['file_quality']['quality_rating'],
            'next_steps': [
                'librosaを使用した詳細音響分析',
                'テンポ測定',
                '音楽構造の特定',
                '感情変化の分析',
                'プロンプト微調整案の作成'
            ]
        }
    }
    
    # 結果をJSONファイルに保存
    output_file = "basic_analysis_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"基本分析結果を保存しました: {output_file}")
    
    # 重要な結果を表示
    print("\n=== 基本分析結果 ===")
    print(f"ファイルサイズ: {file_info['file_size_mb']}MB")
    print(f"楽曲長: {file_info['duration_seconds']}秒")
    print(f"サンプルレート: {file_info['sample_rate']}Hz")
    print(f"チャンネル数: {file_info['channels']}")
    print(f"ビット深度: {file_info['sample_width'] * 8}bit")
    print(f"楽曲長ステータス: {comparison['duration_analysis']['status']}")
    print(f"理想値(35秒)との差: {comparison['duration_analysis']['difference_from_ideal']}秒")
    
    if comparison['duration_analysis']['status'] == 'NEEDS_ADJUSTMENT':
        print("\n⚠️  楽曲長が戦略計画の範囲外です。調整が必要です。")
    else:
        print("\n✅ 楽曲長は戦略計画の範囲内です。")
    
    print(f"\n次のステップ: 詳細分析のため comprehensive_music_analysis.py を実行してください")
    
    return results

if __name__ == "__main__":
    main()