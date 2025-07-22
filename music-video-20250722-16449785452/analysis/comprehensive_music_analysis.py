#!/usr/bin/env python3
"""
Comprehensive Music Analysis Tool
Analyzes WAV files for detailed audio characteristics
"""

import wave
import numpy as np
import json
import os
from datetime import datetime

def analyze_wav_file(file_path):
    """Comprehensive analysis of a WAV file"""
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    results = {}
    
    try:
        # Basic file information
        with wave.open(file_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            duration = frames / float(sample_rate)
            
            results["basic_info"] = {
                "file_size_bytes": os.path.getsize(file_path),
                "duration_seconds": round(duration, 2),
                "sample_rate_hz": sample_rate,
                "channels": channels,
                "bit_depth": sample_width * 8,
                "total_frames": frames,
                "format": "WAV"
            }
            
            # Read audio data for advanced analysis
            audio_data = wav_file.readframes(frames)
            
        # Convert to numpy array for analysis
        if sample_width == 1:
            dtype = np.uint8
        elif sample_width == 2:
            dtype = np.int16
        elif sample_width == 4:
            dtype = np.int32
        else:
            dtype = np.float32
            
        audio_array = np.frombuffer(audio_data, dtype=dtype)
        
        # Handle stereo vs mono
        if channels == 2:
            audio_array = audio_array.reshape(-1, 2)
            # Use left channel for analysis or mix to mono
            mono_audio = np.mean(audio_array.astype(np.float32), axis=1)
        else:
            mono_audio = audio_array.astype(np.float32)
        
        # Normalize audio data
        if sample_width <= 2:
            mono_audio = mono_audio / (2**(sample_width * 8 - 1))
        
        # Volume analysis
        rms = np.sqrt(np.mean(mono_audio**2))
        peak = np.max(np.abs(mono_audio))
        
        results["volume_analysis"] = {
            "rms_level": float(rms),
            "peak_level": float(peak),
            "dynamic_range": float(peak / (rms + 1e-10)),  # Avoid division by zero
            "rms_db": float(20 * np.log10(rms + 1e-10)),
            "peak_db": float(20 * np.log10(peak + 1e-10))
        }
        
        # Segment analysis (divide into 4 parts for structure analysis)
        segment_length = len(mono_audio) // 4
        segment_analysis = {}
        
        for i in range(4):
            start_idx = i * segment_length
            end_idx = (i + 1) * segment_length if i < 3 else len(mono_audio)
            segment = mono_audio[start_idx:end_idx]
            
            segment_rms = np.sqrt(np.mean(segment**2))
            segment_peak = np.max(np.abs(segment))
            
            segment_analysis[f"segment_{i+1}"] = {
                "time_range": f"{start_idx/sample_rate:.1f}-{end_idx/sample_rate:.1f}s",
                "rms_level": float(segment_rms),
                "peak_level": float(segment_peak),
                "relative_loudness": float(segment_rms / (rms + 1e-10))
            }
        
        results["structure_analysis"] = segment_analysis
        
        # Simple tempo estimation using zero crossings and energy variations
        # This is a basic approximation
        zero_crossings = np.where(np.diff(np.signbit(mono_audio)))[0]
        zcr = len(zero_crossings) / duration
        
        # Energy-based tempo estimation (very rough)
        window_size = int(0.1 * sample_rate)  # 100ms windows
        energy_windows = []
        
        for i in range(0, len(mono_audio) - window_size, window_size):
            window = mono_audio[i:i + window_size]
            energy = np.sum(window**2)
            energy_windows.append(energy)
        
        energy_windows = np.array(energy_windows)
        
        # Find peaks in energy to estimate tempo
        if len(energy_windows) > 1:
            energy_diff = np.diff(energy_windows)
            energy_peaks = np.where(energy_diff > np.std(energy_diff))[0]
            
            if len(energy_peaks) > 1:
                avg_peak_interval = np.mean(np.diff(energy_peaks)) * 0.1  # Convert to seconds
                estimated_bpm = 60 / (avg_peak_interval + 1e-10)
                # Clamp to reasonable range
                estimated_bpm = max(40, min(200, estimated_bpm))
            else:
                estimated_bpm = 0
        else:
            estimated_bpm = 0
        
        results["tempo_analysis"] = {
            "zero_crossing_rate": float(zcr),
            "estimated_bpm": float(estimated_bpm),
            "energy_variations": len(energy_peaks),
            "note": "BPM estimation is approximate and may not be accurate for ambient music"
        }
        
        # Frequency analysis (basic spectral centroid)
        fft = np.fft.fft(mono_audio[:min(len(mono_audio), sample_rate * 4)])  # First 4 seconds
        freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
        magnitude = np.abs(fft)
        
        # Spectral centroid (brightness indicator)
        spectral_centroid = np.sum(freqs[:len(freqs)//2] * magnitude[:len(magnitude)//2]) / np.sum(magnitude[:len(magnitude)//2])
        
        results["spectral_analysis"] = {
            "spectral_centroid_hz": float(spectral_centroid),
            "brightness_indicator": "high" if spectral_centroid > 2000 else "medium" if spectral_centroid > 1000 else "low"
        }
        
        # Musical characteristics inference
        characteristics = []
        
        if rms < 0.1:
            characteristics.append("quiet/ambient")
        elif rms > 0.5:
            characteristics.append("loud/energetic")
        else:
            characteristics.append("moderate volume")
            
        if peak / rms > 5:
            characteristics.append("high dynamic range")
        elif peak / rms < 2:
            characteristics.append("compressed/consistent")
        else:
            characteristics.append("moderate dynamics")
            
        if estimated_bpm > 0:
            if estimated_bpm < 80:
                characteristics.append("slow tempo")
            elif estimated_bpm > 120:
                characteristics.append("fast tempo")
            else:
                characteristics.append("moderate tempo")
        
        if spectral_centroid < 1000:
            characteristics.append("warm/dark timbre")
        elif spectral_centroid > 3000:
            characteristics.append("bright/clear timbre")
        else:
            characteristics.append("balanced timbre")
        
        results["musical_characteristics"] = characteristics
        
        # Analysis metadata
        results["analysis_metadata"] = {
            "analysis_timestamp": datetime.now().isoformat(),
            "analyzer_version": "1.0",
            "file_analyzed": os.path.basename(file_path)
        }
        
    except Exception as e:
        results["error"] = f"Analysis failed: {str(e)}"
    
    return results

def format_analysis_report(analysis_results):
    """Format analysis results into a readable report"""
    if "error" in analysis_results:
        return f"Error: {analysis_results['error']}"
    
    report = []
    report.append("# 音楽ファイル詳細分析レポート")
    report.append("")
    
    # Basic info
    basic = analysis_results.get("basic_info", {})
    report.append("## 1. 基本情報")
    report.append(f"- ファイルサイズ: {basic.get('file_size_bytes', 0):,} bytes ({basic.get('file_size_bytes', 0)/1024/1024:.1f} MB)")
    report.append(f"- 長さ: {basic.get('duration_seconds', 0)} 秒")
    report.append(f"- サンプルレート: {basic.get('sample_rate_hz', 0):,} Hz")
    report.append(f"- チャンネル数: {basic.get('channels', 0)} ({'ステレオ' if basic.get('channels') == 2 else 'モノラル'})")
    report.append(f"- ビット深度: {basic.get('bit_depth', 0)} bit")
    report.append(f"- 総フレーム数: {basic.get('total_frames', 0):,}")
    report.append("")
    
    # Volume analysis
    volume = analysis_results.get("volume_analysis", {})
    report.append("## 2. 音量分析")
    report.append(f"- RMSレベル: {volume.get('rms_level', 0):.4f} ({volume.get('rms_db', 0):.1f} dB)")
    report.append(f"- ピークレベル: {volume.get('peak_level', 0):.4f} ({volume.get('peak_db', 0):.1f} dB)")
    report.append(f"- ダイナミックレンジ: {volume.get('dynamic_range', 0):.2f}")
    report.append("")
    
    # Tempo analysis
    tempo = analysis_results.get("tempo_analysis", {})
    report.append("## 3. テンポ分析")
    report.append(f"- 推定BPM: {tempo.get('estimated_bpm', 0):.1f}")
    report.append(f"- ゼロクロッシング率: {tempo.get('zero_crossing_rate', 0):.1f} Hz")
    report.append(f"- エネルギー変動: {tempo.get('energy_variations', 0)} 個")
    report.append(f"- 注意: {tempo.get('note', '')}")
    report.append("")
    
    # Structure analysis
    structure = analysis_results.get("structure_analysis", {})
    report.append("## 4. 楽曲構造分析（4分割）")
    for segment_name, segment_data in structure.items():
        report.append(f"- {segment_name} ({segment_data.get('time_range', '')}):")
        report.append(f"  - RMSレベル: {segment_data.get('rms_level', 0):.4f}")
        report.append(f"  - 相対音量: {segment_data.get('relative_loudness', 0):.2f}")
    report.append("")
    
    # Spectral analysis
    spectral = analysis_results.get("spectral_analysis", {})
    report.append("## 5. スペクトル分析")
    report.append(f"- スペクトル重心: {spectral.get('spectral_centroid_hz', 0):.1f} Hz")
    report.append(f"- 音色の明るさ: {spectral.get('brightness_indicator', 'unknown')}")
    report.append("")
    
    # Musical characteristics
    characteristics = analysis_results.get("musical_characteristics", [])
    report.append("## 6. 音楽的特徴")
    for char in characteristics:
        report.append(f"- {char}")
    report.append("")
    
    # Strategy comparison
    report.append("## 7. 戦略計画との比較")
    report.append("### 想定された特徴:")
    report.append("- ジャンル: ネオクラシカル・アンビエント")
    report.append("- テンポ: 70-80 BPM")
    report.append("- 楽器構成: ピアノ、ストリングス、シンセパッド")
    report.append("- 想定時間: 35秒")
    report.append("- 感情アーク: 静寂→開花→頂点→余韻")
    report.append("")
    
    report.append("### 実際の分析結果との比較:")
    actual_duration = basic.get('duration_seconds', 0)
    actual_bpm = tempo.get('estimated_bpm', 0)
    
    report.append(f"- 実際の長さ: {actual_duration}秒 (想定35秒との差: {actual_duration-35:+.1f}秒)")
    
    if 70 <= actual_bpm <= 80:
        report.append(f"- 実際のBPM: {actual_bpm:.1f} ✓ (想定範囲70-80 BPMに適合)")
    else:
        report.append(f"- 実際のBPM: {actual_bpm:.1f} ⚠ (想定範囲70-80 BPMから逸脱)")
    
    # Volume pattern analysis
    segments = list(structure.values())
    if len(segments) >= 4:
        loudness_pattern = [s.get('relative_loudness', 0) for s in segments]
        if loudness_pattern[0] < loudness_pattern[1] < loudness_pattern[2] > loudness_pattern[3]:
            report.append("- 音量パターン: ✓ 静寂→展開→クライマックス→余韻の理想的パターン")
        else:
            report.append("- 音量パターン: ⚠ 想定された感情アークと異なるパターン")
    
    # Genre compatibility
    if "quiet/ambient" in characteristics and "slow tempo" in characteristics:
        report.append("- ジャンル適合性: ✓ ネオクラシカル・アンビエントの特徴と一致")
    else:
        report.append("- ジャンル適合性: ⚠ ネオクラシカル・アンビエント特徴との乖離")
    
    report.append("")
    
    # Analysis metadata
    metadata = analysis_results.get("analysis_metadata", {})
    report.append("## 8. 分析メタデータ")
    report.append(f"- 分析実行時刻: {metadata.get('analysis_timestamp', '')}")
    report.append(f"- 分析バージョン: {metadata.get('analyzer_version', '')}")
    report.append(f"- 分析対象ファイル: {metadata.get('file_analyzed', '')}")
    
    return "\n".join(report)

if __name__ == "__main__":
    file_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250722-16449785452/music/generated-music.wav"
    
    print("音楽ファイル分析を開始します...")
    results = analyze_wav_file(file_path)
    
    if "error" in results:
        print(f"エラー: {results['error']}")
    else:
        print("\n" + "="*60)
        print(format_analysis_report(results))
        print("="*60)
        
        # Save JSON results
        json_output_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250722-16449785452/analysis/analysis-results.json"
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n詳細結果をJSONファイルに保存しました: {json_output_path}")
        
        # Save formatted report
        report_output_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250722-16449785452/analysis/detailed-music-analysis-report.md"
        with open(report_output_path, 'w', encoding='utf-8') as f:
            f.write(format_analysis_report(results))
        
        print(f"フォーマット済みレポートをMarkdownファイルに保存しました: {report_output_path}")