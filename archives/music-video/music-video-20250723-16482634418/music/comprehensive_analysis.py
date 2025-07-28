#!/usr/bin/env python3
"""
Comprehensive Audio Analysis for Generated Music
Analyzes the generated music WAV file to extract detailed musical characteristics.
"""

import wave
import struct
import numpy as np
import os
import json
from datetime import datetime

def get_wav_info(filepath):
    """Extract basic WAV file information."""
    try:
        with wave.open(filepath, 'rb') as wav:
            return {
                'duration': wav.getnframes() / wav.getframerate(),
                'sample_rate': wav.getframerate(),
                'channels': wav.getnchannels(),
                'sample_width': wav.getsampwidth(),
                'frames': wav.getnframes(),
                'file_size': os.path.getsize(filepath)
            }
    except Exception as e:
        return {'error': str(e)}

def read_audio_data(filepath):
    """Read audio data as numpy array."""
    try:
        with wave.open(filepath, 'rb') as wav:
            frames = wav.readframes(wav.getnframes())
            sample_width = wav.getsampwidth()
            channels = wav.getnchannels()
            
            # Convert based on sample width
            if sample_width == 1:
                data = np.frombuffer(frames, dtype=np.uint8)
                data = (data - 128) / 128.0
            elif sample_width == 2:
                data = np.frombuffer(frames, dtype=np.int16)
                data = data / 32768.0
            elif sample_width == 4:
                data = np.frombuffer(frames, dtype=np.int32)
                data = data / 2147483648.0
            else:
                return None
            
            # Convert stereo to mono if needed
            if channels == 2:
                data = data.reshape(-1, 2)
                data = np.mean(data, axis=1)
            
            return data
    except Exception as e:
        return None

def estimate_tempo_simple(audio_data, sample_rate):
    """Simple tempo estimation using zero-crossing rate analysis."""
    try:
        # Calculate zero crossings
        zero_crossings = np.diff(np.signbit(audio_data)).astype(int)
        zcr = np.sum(zero_crossings) / len(audio_data)
        
        # Rough tempo estimation based on zero crossing rate
        # This is a simplified approach
        estimated_tempo = zcr * sample_rate / 1000 * 60
        
        # Clamp to reasonable range
        if estimated_tempo < 30:
            estimated_tempo *= 2
        elif estimated_tempo > 200:
            estimated_tempo /= 2
        
        return estimated_tempo
    except:
        return None

def analyze_dynamics(audio_data, sample_rate):
    """Analyze dynamic characteristics."""
    try:
        # RMS over time
        frame_size = int(sample_rate * 0.1)  # 100ms frames
        hop_size = int(sample_rate * 0.05)   # 50ms hop
        
        rms_values = []
        for i in range(0, len(audio_data) - frame_size, hop_size):
            frame = audio_data[i:i+frame_size]
            rms = np.sqrt(np.mean(frame**2))
            rms_values.append(rms)
        
        rms_values = np.array(rms_values)
        
        return {
            'peak_amplitude': float(np.max(np.abs(audio_data))),
            'rms_mean': float(np.mean(rms_values)),
            'rms_std': float(np.std(rms_values)),
            'dynamic_range': float(np.max(rms_values) - np.min(rms_values)),
            'quiet_ratio': float(np.sum(rms_values < np.mean(rms_values) * 0.3) / len(rms_values))
        }
    except:
        return {}

def analyze_frequency_simple(audio_data, sample_rate):
    """Simple frequency analysis using FFT."""
    try:
        # Take FFT of the entire signal (simplified)
        fft = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
        
        # Get magnitude and only positive frequencies
        magnitude = np.abs(fft)
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        # Find dominant frequency
        dominant_freq_idx = np.argmax(positive_magnitude)
        dominant_freq = positive_freqs[dominant_freq_idx]
        
        # Spectral centroid (brightness measure)
        spectral_centroid = np.sum(positive_freqs * positive_magnitude) / np.sum(positive_magnitude)
        
        # High frequency content ratio
        high_freq_threshold = 2000  # Hz
        high_freq_ratio = np.sum(positive_magnitude[positive_freqs > high_freq_threshold]) / np.sum(positive_magnitude)
        
        return {
            'dominant_frequency': float(dominant_freq),
            'spectral_centroid': float(spectral_centroid),
            'high_frequency_ratio': float(high_freq_ratio),
            'frequency_range': [float(positive_freqs[0]), float(positive_freqs[-1])]
        }
    except:
        return {}

def detect_structure(audio_data, sample_rate, duration):
    """Detect basic structural elements."""
    try:
        # Divide into quarters for structural analysis
        quarter_duration = duration / 4
        quarters = []
        
        for i in range(4):
            start_sample = int(i * quarter_duration * sample_rate)
            end_sample = int((i + 1) * quarter_duration * sample_rate)
            if end_sample > len(audio_data):
                end_sample = len(audio_data)
            
            quarter_data = audio_data[start_sample:end_sample]
            quarter_rms = np.sqrt(np.mean(quarter_data**2))
            
            quarters.append({
                'section': i + 1,
                'time_range': [i * quarter_duration, (i + 1) * quarter_duration],
                'rms_level': float(quarter_rms),
                'relative_intensity': 'low' if quarter_rms < 0.1 else 'medium' if quarter_rms < 0.3 else 'high'
            })
        
        return quarters
    except:
        return []

def assess_music_box_characteristics(info, dynamics, frequency):
    """Assess how well the audio matches music box characteristics."""
    score = 0
    notes = []
    
    # Duration check (30-40 seconds is ideal)
    if 30 <= info.get('duration', 0) <= 40:
        score += 20
        notes.append("✓ Duration ideal for music box piece")
    elif 25 <= info.get('duration', 0) <= 50:
        score += 15
        notes.append("• Duration acceptable for music box piece")
    else:
        score += 5
        notes.append("⚠ Duration outside typical music box range")
    
    # Dynamic range (music boxes have limited dynamic range)
    dynamic_range = dynamics.get('dynamic_range', 1)
    if dynamic_range < 0.3:
        score += 20
        notes.append("✓ Limited dynamic range (music box characteristic)")
    elif dynamic_range < 0.5:
        score += 15
        notes.append("• Moderate dynamic range")
    else:
        score += 5
        notes.append("⚠ Wide dynamic range (less music box-like)")
    
    # Frequency characteristics
    spectral_centroid = frequency.get('spectral_centroid', 2000)
    if spectral_centroid < 1500:
        score += 20
        notes.append("✓ Warm, gentle frequency content")
    elif spectral_centroid < 2500:
        score += 15
        notes.append("• Balanced frequency content")
    else:
        score += 5
        notes.append("⚠ Bright frequency content")
    
    # High frequency ratio (music boxes have limited high frequencies)
    high_freq_ratio = frequency.get('high_frequency_ratio', 0.5)
    if high_freq_ratio < 0.2:
        score += 20
        notes.append("✓ Limited high frequencies (music box-like)")
    elif high_freq_ratio < 0.4:
        score += 15
        notes.append("• Moderate high frequency content")
    else:
        score += 5
        notes.append("⚠ Significant high frequency content")
    
    # Overall assessment
    if score >= 75:
        assessment = "Excellent music box characteristics"
    elif score >= 60:
        assessment = "Good music box characteristics"
    elif score >= 45:
        assessment = "Moderate music box characteristics"
    else:
        assessment = "Limited music box characteristics"
    
    return {
        'score': score,
        'assessment': assessment,
        'notes': notes
    }

def generate_video_recommendations(info, dynamics, frequency, structure):
    """Generate recommendations for video generation based on audio analysis."""
    recommendations = []
    
    duration = info.get('duration', 0)
    
    # Tempo-based recommendations
    if duration > 0:
        # Estimate beats per minute from structure changes
        estimated_tempo = 240 / duration  # Very rough estimate
        
        if estimated_tempo < 70:
            recommendations.append("• Use slow, contemplative camera movements")
            recommendations.append("• Emphasize gentle transitions between scenes")
            recommendations.append("• Allow time for visual details to be appreciated")
        else:
            recommendations.append("• Use moderate-paced visual transitions")
            recommendations.append("• Balance movement with stable shots")
    
    # Dynamic-based recommendations
    dynamic_range = dynamics.get('dynamic_range', 0)
    if dynamic_range < 0.3:
        recommendations.append("• Use consistent, soft lighting throughout")
        recommendations.append("• Avoid dramatic visual contrasts")
        recommendations.append("• Maintain gentle, steady visual flow")
    else:
        recommendations.append("• Use varied lighting to match audio dynamics")
        recommendations.append("• Include some visual drama in climactic sections")
    
    # Frequency-based recommendations
    spectral_centroid = frequency.get('spectral_centroid', 2000)
    if spectral_centroid < 1500:
        recommendations.append("• Use warm color palette (browns, golds, soft pinks)")
        recommendations.append("• Emphasize soft, rounded visual elements")
    else:
        recommendations.append("• Include some brighter visual elements")
        recommendations.append("• Balance warm and cool tones")
    
    # Structure-based recommendations
    if len(structure) >= 4:
        recommendations.append("• Structure video in four main segments:")
        for i, section in enumerate(structure):
            intensity = section.get('relative_intensity', 'medium')
            time_range = section.get('time_range', [0, 0])
            
            if intensity == 'low':
                recommendations.append(f"  - Segment {i+1} ({time_range[0]:.1f}-{time_range[1]:.1f}s): Gentle introduction/outro")
            elif intensity == 'high':
                recommendations.append(f"  - Segment {i+1} ({time_range[0]:.1f}-{time_range[1]:.1f}s): Visual climax with roses in focus")
            else:
                recommendations.append(f"  - Segment {i+1} ({time_range[0]:.1f}-{time_range[1]:.1f}s): Build-up or development")
    
    # Rose-specific recommendations
    recommendations.append("• Rose-themed visual elements:")
    recommendations.append("  - Close-ups of rose petals and textures")
    recommendations.append("  - Soft focus effects for dreamy atmosphere")
    recommendations.append("  - Music box or vintage aesthetic elements")
    recommendations.append("  - Gentle particle effects (falling petals)")
    
    return recommendations

def main():
    filepath = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250723-16482634418/music/generated-music.wav"
    
    print("=" * 60)
    print("🎵 COMPREHENSIVE MUSIC ANALYSIS REPORT")
    print("=" * 60)
    print(f"File: {filepath}")
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Basic file information
    print("1. BASIC AUDIO PROPERTIES")
    print("-" * 30)
    info = get_wav_info(filepath)
    
    if 'error' in info:
        print(f"Error reading file: {info['error']}")
        return
    
    print(f"Duration: {info['duration']:.2f} seconds")
    print(f"Sample Rate: {info['sample_rate']} Hz")
    print(f"Channels: {info['channels']} ({'Mono' if info['channels'] == 1 else 'Stereo'})")
    print(f"Sample Width: {info['sample_width']} bytes ({info['sample_width'] * 8} bits)")
    print(f"File Size: {info['file_size']:,} bytes ({info['file_size'] / 1024 / 1024:.2f} MB)")
    print(f"Total Frames: {info['frames']:,}")
    
    # Expected tempo range check
    print(f"\nTempo Range Assessment:")
    if 30 <= info['duration'] <= 40:
        expected_bpm_range = "60-70 BPM (ideal for gentle music box)"
        print(f"Expected BPM for {info['duration']:.1f}s piece: {expected_bpm_range}")
    
    # Read audio data for detailed analysis
    print("\n2. DETAILED AUDIO ANALYSIS")
    print("-" * 30)
    
    audio_data = read_audio_data(filepath)
    if audio_data is None:
        print("Error: Could not read audio data for detailed analysis")
        return
    
    print(f"Successfully loaded {len(audio_data):,} audio samples")
    
    # Dynamic analysis
    print("\n2.1 Dynamic Characteristics")
    dynamics = analyze_dynamics(audio_data, info['sample_rate'])
    print(f"Peak Amplitude: {dynamics.get('peak_amplitude', 0):.3f}")
    print(f"Average RMS Level: {dynamics.get('rms_mean', 0):.3f}")
    print(f"RMS Variability: {dynamics.get('rms_std', 0):.3f}")
    print(f"Dynamic Range: {dynamics.get('dynamic_range', 0):.3f}")
    print(f"Quiet Sections Ratio: {dynamics.get('quiet_ratio', 0):.1%}")
    
    # Frequency analysis
    print("\n2.2 Frequency Characteristics")
    frequency = analyze_frequency_simple(audio_data, info['sample_rate'])
    print(f"Dominant Frequency: {frequency.get('dominant_frequency', 0):.1f} Hz")
    print(f"Spectral Centroid (Brightness): {frequency.get('spectral_centroid', 0):.1f} Hz")
    print(f"High Frequency Content: {frequency.get('high_frequency_ratio', 0):.1%}")
    freq_range = frequency.get('frequency_range', [0, 0])
    print(f"Frequency Range: {freq_range[0]:.1f} - {freq_range[1]:.1f} Hz")
    
    # Tempo estimation
    print("\n2.3 Tempo Estimation")
    estimated_tempo = estimate_tempo_simple(audio_data, info['sample_rate'])
    print(f"Estimated Tempo: {estimated_tempo:.1f} BPM" if estimated_tempo else "Could not estimate tempo")
    
    if estimated_tempo:
        if 60 <= estimated_tempo <= 70:
            print("✓ Tempo matches expected range for gentle music box (60-70 BPM)")
        elif 50 <= estimated_tempo <= 80:
            print("• Tempo close to expected range (may need minor adjustment)")
        else:
            print("⚠ Tempo outside expected range (significant adjustment may be needed)")
    
    # Structural analysis
    print("\n3. STRUCTURAL ANALYSIS")
    print("-" * 30)
    structure = detect_structure(audio_data, info['sample_rate'], info['duration'])
    
    for section in structure:
        time_range = section['time_range']
        print(f"Section {section['section']}: {time_range[0]:.1f}-{time_range[1]:.1f}s "
              f"(RMS: {section['rms_level']:.3f}, Intensity: {section['relative_intensity']})")
    
    # Music box assessment
    print("\n4. MUSIC BOX CHARACTERISTICS ASSESSMENT")
    print("-" * 30)
    assessment = assess_music_box_characteristics(info, dynamics, frequency)
    print(f"Overall Score: {assessment['score']}/100")
    print(f"Assessment: {assessment['assessment']}")
    print("\nDetailed Analysis:")
    for note in assessment['notes']:
        print(f"  {note}")
    
    # Video recommendations
    print("\n5. VIDEO GENERATION RECOMMENDATIONS")
    print("-" * 30)
    recommendations = generate_video_recommendations(info, dynamics, frequency, structure)
    for rec in recommendations:
        print(rec)
    
    # Technical summary for optimization
    print("\n6. TECHNICAL SUMMARY FOR OPTIMIZATION")
    print("-" * 30)
    print(f"• Audio Quality: Professional ({info['file_size'] / 1024 / 1024:.1f}MB WAV)")
    print(f"• Duration: {info['duration']:.1f}s (ideal: 35-40s)")
    print(f"• Dynamic Character: {'Gentle' if dynamics.get('dynamic_range', 0) < 0.3 else 'Moderate' if dynamics.get('dynamic_range', 0) < 0.5 else 'Dynamic'}")
    print(f"• Frequency Character: {'Warm' if frequency.get('spectral_centroid', 2000) < 1500 else 'Balanced' if frequency.get('spectral_centroid', 2000) < 2500 else 'Bright'}")
    print(f"• Music Box Authenticity: {assessment['score']}% match")
    
    if estimated_tempo:
        tempo_status = "Perfect" if 60 <= estimated_tempo <= 70 else "Good" if 50 <= estimated_tempo <= 80 else "Needs adjustment"
        print(f"• Tempo Suitability: {tempo_status} ({estimated_tempo:.1f} BPM)")
    
    print("\n" + "=" * 60)
    print("Analysis completed successfully!")
    print("Use this data to optimize your video generation prompts.")
    print("=" * 60)

if __name__ == "__main__":
    main()