#!/usr/bin/env python3
"""
シンプルな音楽ファイル分析
Pythonの標準ライブラリのみを使用
"""

import wave
import os
import struct
import math

def main():
    audio_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250721-16406899626/music/generated-music.wav"
    
    print("🎵 音楽ファイル基本分析")
    print("=" * 50)
    
    try:
        # ファイル存在確認
        if not os.path.exists(audio_file):
            print(f"❌ ファイルが見つかりません: {audio_file}")
            return
        
        # ファイルサイズ
        file_size = os.path.getsize(audio_file)
        print(f"📁 ファイルサイズ: {file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
        
        # WAVファイル読み込み
        with wave.open(audio_file, 'rb') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            duration = frames / sample_rate
            
            print(f"⏱️ 長さ: {duration:.2f} 秒")
            print(f"🔊 サンプルレート: {sample_rate:,} Hz")
            print(f"📺 チャンネル数: {channels} ({'ステレオ' if channels == 2 else 'モノラル'})")
            print(f"🎚️ ビット深度: {sample_width * 8} bit")
            print(f"📊 総フレーム数: {frames:,}")
            
            # 計画との比較
            print(f"\n📋 計画との比較:")
            target_duration = (30, 40)
            if target_duration[0] <= duration <= target_duration[1]:
                print(f"✅ 長さ: {duration:.2f}秒 (目標: {target_duration[0]}-{target_duration[1]}秒) - 範囲内")
            else:
                print(f"⚠️ 長さ: {duration:.2f}秒 (目標: {target_duration[0]}-{target_duration[1]}秒) - 範囲外")
            
            # 技術品質チェック
            print(f"\n🔧 技術品質:")
            print(f"✅ サンプルレート: {sample_rate}Hz - {'高品質' if sample_rate >= 44100 else '標準品質'}")
            print(f"✅ ビット深度: {sample_width * 8}bit - {'高品質' if sample_width >= 2 else '標準品質'}")
            print(f"✅ ステレオ: {'対応' if channels == 2 else '非対応'}")
            
            # 基本的な音声データ読み込み
            raw_audio = wav_file.readframes(min(frames, sample_rate * 5))  # 最初の5秒分
            
        # 音声データの基本分析
        if sample_width == 2:  # 16-bit
            audio_data = struct.unpack(f'<{len(raw_audio)//2}h', raw_audio)
        else:
            audio_data = []
        
        if audio_data:
            max_amp = max(abs(x) for x in audio_data)
            rms = math.sqrt(sum(x*x for x in audio_data) / len(audio_data))
            
            print(f"\n📈 音声レベル分析（最初の5秒）:")
            print(f"📏 最大振幅: {max_amp}")
            print(f"🔊 RMS平均: {rms:.2f}")
            print(f"⚡ ダイナミクス比: {max_amp/rms:.2f}" if rms > 0 else "⚡ ダイナミクス比: N/A")
        
        # 視覚的要素への提案
        print(f"\n🎨 視覚的要素への基本提案:")
        
        # 長さベースの提案
        if duration < 35:
            print(f"📐 構成: コンパクトな3段構成推奨（イントロ→展開→アウトロ）")
        else:
            print(f"📐 構成: 標準4段構成推奨（イントロ→展開→クライマックス→アウトロ）")
        
        # サンプルレートベースの提案
        if sample_rate >= 48000:
            print(f"🎬 映像品質: 4K動画制作に最適")
        else:
            print(f"🎬 映像品質: HD動画制作に適合")
        
        # ミニマリストピアノソロ仮定での提案
        print(f"🎹 色彩パレット: クリーンホワイト、ソフトグレー、微細なゴールド")
        print(f"💡 照明: 柔らかく均一、ミニマルなコントラスト")
        print(f"📷 カメラ: 滑らかで穏やかな動き、静的カットメイン")
        
        # タイミング提案
        intro_length = min(8, duration * 0.2)
        outro_length = min(8, duration * 0.2)
        development_length = duration - intro_length - outro_length
        
        print(f"\n⏰ 推奨タイミング構造:")
        print(f"  イントロ: 0 - {intro_length:.1f}秒")
        print(f"  展開部: {intro_length:.1f} - {intro_length + development_length:.1f}秒")
        print(f"  アウトロ: {intro_length + development_length:.1f} - {duration:.1f}秒")
        
        # 総合評価
        print(f"\n📊 総合評価:")
        quality_score = 0
        total_checks = 3
        
        if target_duration[0] <= duration <= target_duration[1]:
            quality_score += 1
        if sample_rate >= 44100:
            quality_score += 1
        if channels == 2 and sample_width >= 2:
            quality_score += 1
            
        percentage = (quality_score / total_checks) * 100
        
        if percentage >= 80:
            print(f"🟢 品質スコア: {percentage:.0f}% - 優秀（そのまま動画制作可能）")
        elif percentage >= 60:
            print(f"🟡 品質スコア: {percentage:.0f}% - 良好（軽微な調整で使用可能）")
        else:
            print(f"🔴 品質スコア: {percentage:.0f}% - 要改善")
        
        print(f"\n🚀 推奨次ステップ:")
        if percentage >= 80:
            print(f"  1. 画像プロンプトに音楽の時間構造を反映")
            print(f"  2. 動画プロンプトに推奨カメラワークを適用")
            print(f"  3. ミニマリスト美学を視覚デザインに統合")
        else:
            print(f"  1. 音楽ファイルの詳細確認・調整検討")
            print(f"  2. 代替音楽制作の検討")
            print(f"  3. より柔軟な視覚デザイン戦略の立案")
        
        print("\n" + "=" * 50)
        print("✅ 基本分析完了")
        
    except Exception as e:
        print(f"❌ 分析エラー: {e}")

if __name__ == "__main__":
    main()