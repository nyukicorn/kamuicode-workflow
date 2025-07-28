#!/usr/bin/env python3
"""
Music Analysis for: バラの花をイメージした美しいオルゴールの曲
(Beautiful music box melody featuring rose flowers)
"""

import wave
import os
import numpy as np
import sys
from pathlib import Path

def analyze_music_box_audio(file_path):
    """Comprehensive analysis focused on music box characteristics"""
    
    print("=" * 80)
    print("🎵 MUSIC BOX AUDIO ANALYSIS")
    print("Target Concept: バラの花をイメージした美しいオルゴールの曲")
    print("(Beautiful music box melody featuring rose flowers)")
    print("=" * 80)
    
    # File existence check
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return
    
    # File basic information
    file_stats = os.stat(file_path)
    file_size_mb = file_stats.st_size / (1024 * 1024)
    
    print(f"📁 File Path: {file_path}")
    print(f"📊 File Size: {file_stats.st_size:,} bytes ({file_size_mb:.2f} MB)")
    print()
    
    try:
        # Open WAV file
        with wave.open(file_path, 'rb') as wav_file:
            # Get basic parameters
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            duration = frames / sample_rate
            
            print("🎼 BASIC AUDIO PROPERTIES")
            print("-" * 40)
            print(f"⏱️  Duration: {duration:.2f} seconds ({duration//60:.0f}m {duration%60:.1f}s)")
            print(f"🔊 Channels: {channels} ({'Stereo' if channels == 2 else 'Mono'})")
            print(f"📈 Sample Rate: {sample_rate:,} Hz")
            print(f"🎚️  Bit Depth: {sample_width * 8} bits")
            print(f"🎵 Total Frames: {frames:,}")
            print()
            
            # Read audio data
            wav_file.rewind()
            raw_audio = wav_file.readframes(frames)
            
            # Convert to NumPy array
            if sample_width == 1:
                audio_data = np.frombuffer(raw_audio, dtype=np.uint8)
                audio_data = audio_data.astype(np.float32) - 128
                max_amplitude = 127
            elif sample_width == 2:
                audio_data = np.frombuffer(raw_audio, dtype=np.int16)
                audio_data = audio_data.astype(np.float32)
                max_amplitude = 32767
            elif sample_width == 4:
                audio_data = np.frombuffer(raw_audio, dtype=np.int32)
                audio_data = audio_data.astype(np.float32)
                max_amplitude = 2147483647
            else:
                print(f"❌ Unsupported sample width: {sample_width}")
                return
            
            # Handle stereo/mono
            if channels == 2:
                audio_data = audio_data.reshape(-1, 2)
                # Create mono version for analysis
                mono_audio = np.mean(audio_data, axis=1)
            else:
                mono_audio = audio_data
            
            # Volume analysis
            print("🔊 VOLUME & DYNAMICS ANALYSIS")
            print("-" * 40)
            
            # RMS calculation
            rms = np.sqrt(np.mean(mono_audio**2))
            
            # Peak value
            peak = np.max(np.abs(mono_audio))
            
            # Convert to dB
            if rms > 0:
                rms_db = 20 * np.log10(rms / max_amplitude)
            else:
                rms_db = -float('inf')
            
            if peak > 0:
                peak_db = 20 * np.log10(peak / max_amplitude)
            else:
                peak_db = -float('inf')
            
            print(f"📊 RMS Level: {rms_db:.1f} dB")
            print(f"⚡ Peak Level: {peak_db:.1f} dB")
            print(f"📈 Dynamic Range: {peak_db - rms_db:.1f} dB")
            
            # Headroom calculation
            headroom = -peak_db
            print(f"🎚️  Headroom: {headroom:.1f} dB")
            print()
            
            # Tempo estimation
            print("🎵 TEMPO & RHYTHM ANALYSIS")
            print("-" * 40)
            
            # Energy-based tempo estimation
            window_size = int(0.1 * sample_rate)  # 0.1 second windows
            hop_size = int(0.05 * sample_rate)    # 0.05 second hops
            
            energy_profile = []
            for i in range(0, len(mono_audio) - window_size, hop_size):
                window = mono_audio[i:i + window_size]
                energy = np.sum(window**2)
                energy_profile.append(energy)
            
            energy_profile = np.array(energy_profile)
            
            # Beat detection
            energy_diff = np.diff(energy_profile)
            positive_diff = energy_diff[energy_diff > 0]
            
            if len(positive_diff) > 0:
                energy_std = np.std(energy_profile)
                time_step = hop_size / sample_rate
                beat_candidates = []
                
                for i in range(1, len(energy_profile) - 1):
                    if (energy_profile[i] > energy_profile[i-1] and 
                        energy_profile[i] > energy_profile[i+1] and
                        energy_profile[i] > np.mean(energy_profile) + 0.5 * energy_std):
                        beat_candidates.append(i * time_step)
                
                if len(beat_candidates) > 1:
                    intervals = np.diff(beat_candidates)
                    if len(intervals) > 0:
                        avg_interval = np.median(intervals)
                        estimated_bpm = 60 / avg_interval if avg_interval > 0 else 0
                        
                        print(f"🥁 Estimated BPM: {estimated_bpm:.0f}")
                        
                        # Tempo classification for music box
                        if 40 <= estimated_bpm <= 70:
                            tempo_assessment = "✅ Perfect for music box (slow & gentle)"
                        elif 70 < estimated_bpm <= 100:
                            tempo_assessment = "👍 Good for music box (moderate)"
                        elif estimated_bpm < 40:
                            tempo_assessment = "⬇️  Very slow (contemplative)"
                        else:
                            tempo_assessment = "⬆️  Too fast for typical music box"
                        
                        print(f"📊 Tempo Feel: {tempo_assessment}")
                    else:
                        print("🥁 Estimated BPM: Could not detect clear rhythm")
                else:
                    print("🥁 Estimated BPM: Beat pattern unclear")
            
            print()
            
            # Frequency analysis
            print("🎼 FREQUENCY ANALYSIS")
            print("-" * 40)
            
            # FFT analysis
            fft_size = min(8192, len(mono_audio))
            if fft_size > 0:
                # Analyze middle section
                start_idx = len(mono_audio) // 2 - fft_size // 2
                analysis_segment = mono_audio[start_idx:start_idx + fft_size]
                
                fft_result = np.fft.fft(analysis_segment)
                freqs = np.fft.fftfreq(fft_size, 1/sample_rate)
                magnitude = np.abs(fft_result[:fft_size//2])
                freqs = freqs[:fft_size//2]
                
                # Find dominant frequencies
                peak_indices = []
                for i in range(10, len(magnitude) - 1):  # Skip very low frequencies
                    if (magnitude[i] > magnitude[i-1] and 
                        magnitude[i] > magnitude[i+1] and
                        magnitude[i] > np.max(magnitude) * 0.1):
                        peak_indices.append(i)
                
                if peak_indices:
                    dominant_freqs = [(freqs[i], magnitude[i]) for i in peak_indices]
                    dominant_freqs.sort(key=lambda x: x[1], reverse=True)
                    
                    print("🎵 Dominant Frequencies:")
                    for i, (freq, mag) in enumerate(dominant_freqs[:5]):
                        print(f"   {freq:6.1f} Hz (magnitude: {mag:.0f})")
                
                # Frequency band energy distribution
                low_mask = (freqs >= 20) & (freqs <= 250)     # Bass
                mid_mask = (freqs > 250) & (freqs <= 4000)    # Midrange
                high_mask = (freqs > 4000) & (freqs <= 20000) # Treble
                
                low_energy = np.sum(magnitude[low_mask])
                mid_energy = np.sum(magnitude[mid_mask])
                high_energy = np.sum(magnitude[high_mask])
                total_energy = low_energy + mid_energy + high_energy
                
                if total_energy > 0:
                    low_percent = (low_energy / total_energy) * 100
                    mid_percent = (mid_energy / total_energy) * 100
                    high_percent = (high_energy / total_energy) * 100
                    
                    print(f"🔉 Low Frequencies (20-250 Hz): {low_percent:.1f}%")
                    print(f"🔊 Mid Frequencies (250-4000 Hz): {mid_percent:.1f}%")
                    print(f"✨ High Frequencies (4000+ Hz): {high_percent:.1f}%")
                    
                    print()
                    print("🎼 MUSIC BOX CHARACTERISTICS ANALYSIS")
                    print("-" * 40)
                    
                    # Music box specific analysis
                    music_box_score = 0
                    total_criteria = 6
                    
                    # 1. High frequency content (music boxes have bright, metallic tones)
                    if high_percent > 25:
                        print("✅ High frequency content: Strong (typical of music box)")
                        music_box_score += 1
                    elif high_percent > 15:
                        print("👍 High frequency content: Moderate")
                        music_box_score += 0.5
                    else:
                        print("❌ High frequency content: Low (not typical of music box)")
                    
                    # 2. Mid-range clarity (melodies are usually in mid frequencies)
                    if mid_percent > 40:
                        print("✅ Mid-range presence: Strong (good for melody)")
                        music_box_score += 1
                    else:
                        print("👍 Mid-range presence: Moderate")
                        music_box_score += 0.5
                    
                    # 3. Low frequency content (music boxes typically have less bass)
                    if low_percent < 30:
                        print("✅ Bass content: Low (typical of music box)")
                        music_box_score += 1
                    else:
                        print("❌ Bass content: High (not typical of music box)")
                    
                    # 4. Dynamic range (music boxes often have consistent volume)
                    dynamic_range = peak_db - rms_db
                    if 5 <= dynamic_range <= 15:
                        print("✅ Dynamic range: Good for music box")
                        music_box_score += 1
                    elif dynamic_range < 5:
                        print("⚠️  Dynamic range: Very limited")
                        music_box_score += 0.5
                    else:
                        print("⚠️  Dynamic range: Very wide (unusual for music box)")
                        music_box_score += 0.5
                    
                    # 5. Audio quality
                    if headroom > 3 and rms_db > -50:
                        print("✅ Audio quality: Good (no clipping, adequate level)")
                        music_box_score += 1
                    else:
                        print("⚠️  Audio quality: Issues detected")
                    
                    # 6. Duration appropriateness
                    if 30 <= duration <= 180:  # 30 seconds to 3 minutes
                        print("✅ Duration: Appropriate for music box piece")
                        music_box_score += 1
                    elif duration < 30:
                        print("⚠️  Duration: Short (may feel incomplete)")
                        music_box_score += 0.5
                    else:
                        print("⚠️  Duration: Long (may be too extended)")
                        music_box_score += 0.5
                    
                    print()
                    print("🌹 ROSE FLOWER CONCEPT ALIGNMENT")
                    print("-" * 40)
                    
                    concept_score = 0
                    concept_criteria = 5
                    
                    # Gentleness (soft dynamics and tempo)
                    if ('estimated_bpm' in locals() and estimated_bpm <= 80) or rms_db < -20:
                        print("✅ Gentleness: Suitable for delicate rose imagery")
                        concept_score += 1
                    else:
                        print("⚠️  Gentleness: May be too intense for rose concept")
                    
                    # Beauty (harmonic content and clarity)
                    if mid_percent > 35 and dynamic_range > 8:
                        print("✅ Musical beauty: Clear harmonic structure")
                        concept_score += 1
                    else:
                        print("⚠️  Musical beauty: Limited harmonic clarity")
                    
                    # Elegance (balanced frequency response)
                    if 15 <= high_percent <= 35 and 35 <= mid_percent <= 65:
                        print("✅ Elegance: Well-balanced frequency distribution")
                        concept_score += 1
                    else:
                        print("⚠️  Elegance: Frequency balance could be improved")
                    
                    # Delicacy (not too aggressive or loud)
                    if rms_db < -15 and headroom > 5:
                        print("✅ Delicacy: Appropriate volume and dynamics")
                        concept_score += 1
                    else:
                        print("⚠️  Delicacy: Volume/dynamics may be too strong")
                    
                    # Music box authenticity
                    if music_box_score >= 4:
                        print("✅ Music box authenticity: Strong characteristics")
                        concept_score += 1
                    else:
                        print("⚠️  Music box authenticity: Characteristics need enhancement")
                    
                    print()
                    print("📊 OVERALL ASSESSMENT")
                    print("-" * 40)
                    
                    music_box_percentage = (music_box_score / total_criteria) * 100
                    concept_percentage = (concept_score / concept_criteria) * 100
                    
                    print(f"🎵 Music Box Characteristics: {music_box_score:.1f}/{total_criteria} ({music_box_percentage:.0f}%)")
                    print(f"🌹 Rose Concept Alignment: {concept_score}/{concept_criteria} ({concept_percentage:.0f}%)")
                    
                    overall_score = (music_box_percentage + concept_percentage) / 2
                    print(f"🎯 Overall Score: {overall_score:.0f}%")
                    
                    if overall_score >= 80:
                        assessment = "🎉 Excellent - Perfect for the concept"
                    elif overall_score >= 60:
                        assessment = "👍 Good - Well-suited for the concept"
                    elif overall_score >= 40:
                        assessment = "⚠️  Fair - Some adjustments recommended"
                    else:
                        assessment = "❌ Poor - Significant improvements needed"
                    
                    print(f"📝 Assessment: {assessment}")
                    
                    print()
                    print("💡 RECOMMENDATIONS FOR VIDEO CREATION")
                    print("-" * 40)
                    
                    if high_percent > 20:
                        print("• Visual: Use bright, sparkling effects to match high frequencies")
                    
                    if 'estimated_bpm' in locals() and estimated_bpm <= 80:
                        print("• Pacing: Use slow, gentle camera movements and transitions")
                    
                    if mid_percent > 40:
                        print("• Focus: Emphasize melodic visual elements (flowing lines, curves)")
                    
                    if duration < 60:
                        print("• Structure: Create a simple, focused visual narrative")
                    elif duration > 120:
                        print("• Structure: Plan multiple visual sections to maintain interest")
                    
                    if music_box_percentage > 60:
                        print("• Theme: Incorporate music box-style mechanical movements")
                        print("• Colors: Use soft pastels and metallic accents")
                    
                    if concept_percentage > 60:
                        print("• Subject: Rose imagery will work well with this audio")
                        print("• Mood: Focus on beauty, elegance, and delicacy")
                    
            print()
            
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print("=" * 80)
    print("✅ Analysis Complete")
    print("=" * 80)

if __name__ == "__main__":
    # Music file path
    music_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250724-16486050103/music/generated-music.wav"
    
    analyze_music_box_audio(music_file)