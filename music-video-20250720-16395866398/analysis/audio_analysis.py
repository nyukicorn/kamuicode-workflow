#!/usr/bin/env python3
"""
Comprehensive audio analysis script for generated-music.wav
This script analyzes various aspects of the audio file including:
- Basic properties (duration, sample rate, channels)
- Spectral analysis for tempo detection
- Dynamic range analysis
- Frequency analysis
- Structural analysis
"""

import os
import sys
import wave
import struct
import numpy as np
from scipy import signal
from scipy.fft import fft
import json

def analyze_wav_file(file_path):
    """Comprehensive analysis of a WAV file"""
    
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        # Open the WAV file
        with wave.open(file_path, 'rb') as wav_file:
            # Basic audio properties
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            duration = frames / sample_rate
            
            # Read audio data
            raw_audio = wav_file.readframes(frames)
            
        # Convert to numpy array
        if sample_width == 1:
            dtype = np.uint8
            audio_data = np.frombuffer(raw_audio, dtype=dtype).astype(np.float32) - 128
        elif sample_width == 2:
            dtype = np.int16
            audio_data = np.frombuffer(raw_audio, dtype=dtype).astype(np.float32)
        elif sample_width == 4:
            dtype = np.int32
            audio_data = np.frombuffer(raw_audio, dtype=dtype).astype(np.float32)
        else:
            return {"error": f"Unsupported sample width: {sample_width}"}
        
        # Normalize audio data
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Handle stereo files
        if channels == 2:
            audio_data = audio_data.reshape(-1, 2)
            # Convert to mono for analysis
            mono_audio = np.mean(audio_data, axis=1)
        else:
            mono_audio = audio_data
        
        # Basic analysis
        analysis = {
            "basic_properties": {
                "duration_seconds": round(duration, 3),
                "sample_rate_hz": sample_rate,
                "channels": channels,
                "bit_depth": sample_width * 8,
                "total_samples": frames,
                "file_size_bytes": os.path.getsize(file_path)
            }
        }
        
        # Dynamic range analysis
        rms = np.sqrt(np.mean(mono_audio**2))
        peak = np.max(np.abs(mono_audio))
        dynamic_range = 20 * np.log10(peak / (rms + 1e-10))
        
        analysis["dynamics"] = {
            "rms_level": round(float(rms), 4),
            "peak_level": round(float(peak), 4),
            "dynamic_range_db": round(float(dynamic_range), 2),
            "loudness_perception": "quiet" if peak < 0.3 else "moderate" if peak < 0.7 else "loud"
        }
        
        # Frequency analysis
        # Use a smaller chunk for FFT to avoid memory issues
        chunk_size = min(len(mono_audio), sample_rate * 10)  # Max 10 seconds
        fft_data = fft(mono_audio[:chunk_size])
        freqs = np.fft.fftfreq(chunk_size, 1/sample_rate)
        magnitude = np.abs(fft_data)
        
        # Find dominant frequency
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        dominant_freq_idx = np.argmax(positive_magnitude[1:]) + 1  # Skip DC component
        dominant_freq = positive_freqs[dominant_freq_idx]
        
        # Frequency band analysis
        bass_power = np.sum(positive_magnitude[(positive_freqs >= 20) & (positive_freqs <= 250)])
        mid_power = np.sum(positive_magnitude[(positive_freqs >= 250) & (positive_freqs <= 4000)])
        treble_power = np.sum(positive_magnitude[(positive_freqs >= 4000) & (positive_freqs <= 20000)])
        total_power = bass_power + mid_power + treble_power
        
        analysis["frequency_analysis"] = {
            "dominant_frequency_hz": round(float(dominant_freq), 2),
            "bass_percentage": round(float(bass_power / total_power * 100), 1),
            "mid_percentage": round(float(mid_power / total_power * 100), 1),
            "treble_percentage": round(float(treble_power / total_power * 100), 1),
            "frequency_character": "bass-heavy" if bass_power/total_power > 0.4 else "mid-heavy" if mid_power/total_power > 0.5 else "treble-heavy"
        }
        
        # Simple tempo estimation using autocorrelation
        # Downsample for tempo analysis to reduce computation
        downsample_factor = max(1, sample_rate // 1000)  # Target ~1kHz
        downsampled = mono_audio[::downsample_factor]
        effective_sr = sample_rate / downsample_factor
        
        # Use autocorrelation for tempo detection
        max_lag = int(effective_sr * 2)  # Max 2 seconds lag (30 BPM minimum)
        min_lag = int(effective_sr * 0.25)  # Min 0.25 seconds lag (240 BPM maximum)
        
        if len(downsampled) > max_lag * 2:
            autocorr = np.correlate(downsampled[:max_lag*4], downsampled[:max_lag*4], mode='full')
            autocorr = autocorr[len(autocorr)//2:]  # Take positive lags only
            
            # Find peaks in autocorrelation
            if len(autocorr) > max_lag:
                autocorr_segment = autocorr[min_lag:max_lag]
                if len(autocorr_segment) > 0:
                    peak_idx = np.argmax(autocorr_segment) + min_lag
                    tempo_period = peak_idx / effective_sr
                    estimated_bpm = 60 / tempo_period
                    
                    # Validate BPM range
                    if 30 <= estimated_bpm <= 240:
                        tempo_confidence = "medium"
                    else:
                        estimated_bpm = None
                        tempo_confidence = "low"
                else:
                    estimated_bpm = None
                    tempo_confidence = "low"
            else:
                estimated_bpm = None
                tempo_confidence = "low"
        else:
            estimated_bpm = None
            tempo_confidence = "low"
        
        analysis["tempo_analysis"] = {
            "estimated_bpm": round(estimated_bpm, 1) if estimated_bpm else None,
            "confidence": tempo_confidence,
            "tempo_description": get_tempo_description(estimated_bpm) if estimated_bpm else "unknown"
        }
        
        # Structural analysis - detect significant changes in energy
        # Analyze in 1-second windows
        window_size = sample_rate
        num_windows = len(mono_audio) // window_size
        energy_windows = []
        
        for i in range(num_windows):
            start = i * window_size
            end = start + window_size
            window_data = mono_audio[start:end]
            energy = np.sum(window_data**2)
            energy_windows.append(energy)
        
        if len(energy_windows) > 0:
            energy_windows = np.array(energy_windows)
            energy_mean = np.mean(energy_windows)
            energy_std = np.std(energy_windows)
            
            # Find significant energy changes
            significant_changes = []
            for i in range(1, len(energy_windows)):
                if abs(energy_windows[i] - energy_windows[i-1]) > energy_std:
                    significant_changes.append(i)
            
            # Classify sections
            low_energy_threshold = energy_mean - energy_std/2
            high_energy_threshold = energy_mean + energy_std/2
            
            low_energy_sections = np.sum(energy_windows < low_energy_threshold)
            high_energy_sections = np.sum(energy_windows > high_energy_threshold)
            
            analysis["structure_analysis"] = {
                "duration_windows": len(energy_windows),
                "significant_changes": len(significant_changes),
                "energy_variation": round(float(energy_std / energy_mean), 3),
                "low_energy_sections": int(low_energy_sections),
                "high_energy_sections": int(high_energy_sections),
                "structure_type": classify_structure(energy_windows, duration)
            }
        else:
            analysis["structure_analysis"] = {
                "error": "Track too short for structural analysis"
            }
        
        # Overall mood assessment
        analysis["mood_assessment"] = assess_mood(analysis)
        
        return analysis
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

def get_tempo_description(bpm):
    """Get descriptive tempo marking based on BPM"""
    if bpm is None:
        return "unknown"
    elif bpm < 60:
        return "very slow (Largo)"
    elif bpm < 76:
        return "slow (Adagio)"
    elif bpm < 108:
        return "moderate (Andante/Moderato)"
    elif bpm < 120:
        return "moderately fast (Allegretto)"
    elif bpm < 168:
        return "fast (Allegro)"
    else:
        return "very fast (Presto)"

def classify_structure(energy_windows, duration):
    """Classify the structural type of the track"""
    if len(energy_windows) < 3:
        return "too short to classify"
    
    # Calculate energy progression
    first_third = np.mean(energy_windows[:len(energy_windows)//3])
    middle_third = np.mean(energy_windows[len(energy_windows)//3:2*len(energy_windows)//3])
    last_third = np.mean(energy_windows[2*len(energy_windows)//3:])
    
    if middle_third > first_third * 1.2 and middle_third > last_third * 1.2:
        return "climactic (builds to middle)"
    elif last_third > first_third * 1.2:
        return "progressive (builds up)"
    elif first_third > last_third * 1.2:
        return "diminishing (fades out)"
    elif np.std([first_third, middle_third, last_third]) / np.mean([first_third, middle_third, last_third]) < 0.2:
        return "consistent energy"
    else:
        return "dynamic (varied energy)"

def assess_mood(analysis):
    """Assess the overall mood based on various factors"""
    mood = {}
    
    # Energy level
    if "dynamics" in analysis:
        peak = analysis["dynamics"]["peak_level"]
        dynamic_range = analysis["dynamics"]["dynamic_range_db"]
        
        if peak < 0.3:
            energy_level = "low"
        elif peak < 0.7:
            energy_level = "moderate"
        else:
            energy_level = "high"
        
        mood["energy_level"] = energy_level
    
    # Tempo feeling
    if "tempo_analysis" in analysis and analysis["tempo_analysis"]["estimated_bpm"]:
        bpm = analysis["tempo_analysis"]["estimated_bpm"]
        if bpm < 80:
            tempo_mood = "relaxed/contemplative"
        elif bpm < 120:
            tempo_mood = "moderate/walking pace"
        else:
            tempo_mood = "energetic/driving"
        
        mood["tempo_mood"] = tempo_mood
    
    # Frequency character
    if "frequency_analysis" in analysis:
        freq_char = analysis["frequency_analysis"]["frequency_character"]
        if freq_char == "bass-heavy":
            freq_mood = "warm/grounded"
        elif freq_char == "treble-heavy":
            freq_mood = "bright/airy"
        else:
            freq_mood = "balanced/natural"
        
        mood["frequency_mood"] = freq_mood
    
    # Overall assessment
    descriptors = []
    if mood.get("energy_level") == "low":
        descriptors.append("gentle")
    if mood.get("tempo_mood") == "relaxed/contemplative":
        descriptors.append("peaceful")
    if mood.get("frequency_mood") == "warm/grounded":
        descriptors.append("warm")
    
    mood["overall_descriptors"] = descriptors if descriptors else ["neutral"]
    
    return mood

if __name__ == "__main__":
    file_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16395866398/music/generated-music.wav"
    
    print("=== Audio Analysis Report ===")
    print(f"Analyzing: {file_path}")
    print()
    
    result = analyze_wav_file(file_path)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    # Print formatted results
    print("1. BASIC AUDIO PROPERTIES:")
    props = result["basic_properties"]
    print(f"   Duration: {props['duration_seconds']} seconds ({props['duration_seconds']/60:.2f} minutes)")
    print(f"   Sample Rate: {props['sample_rate_hz']} Hz")
    print(f"   Channels: {props['channels']} ({'Stereo' if props['channels'] == 2 else 'Mono'})")
    print(f"   Bit Depth: {props['bit_depth']} bits")
    print(f"   Total Samples: {props['total_samples']:,}")
    print(f"   File Size: {props['file_size_bytes']:,} bytes ({props['file_size_bytes']/(1024*1024):.2f} MB)")
    print()
    
    print("2. TEMPO/BPM ANALYSIS:")
    tempo = result["tempo_analysis"]
    if tempo["estimated_bpm"]:
        print(f"   Estimated BPM: {tempo['estimated_bpm']}")
        print(f"   Tempo Description: {tempo['tempo_description']}")
        print(f"   Confidence: {tempo['confidence']}")
    else:
        print(f"   BPM: Could not determine reliably (confidence: {tempo['confidence']})")
    print()
    
    print("3. DYNAMIC CHARACTERISTICS:")
    dynamics = result["dynamics"]
    print(f"   RMS Level: {dynamics['rms_level']}")
    print(f"   Peak Level: {dynamics['peak_level']}")
    print(f"   Dynamic Range: {dynamics['dynamic_range_db']} dB")
    print(f"   Loudness Perception: {dynamics['loudness_perception']}")
    print()
    
    print("4. FREQUENCY ANALYSIS:")
    freq = result["frequency_analysis"]
    print(f"   Dominant Frequency: {freq['dominant_frequency_hz']} Hz")
    print(f"   Bass Content: {freq['bass_percentage']}%")
    print(f"   Mid Content: {freq['mid_percentage']}%")
    print(f"   Treble Content: {freq['treble_percentage']}%")
    print(f"   Frequency Character: {freq['frequency_character']}")
    print()
    
    print("5. STRUCTURAL ANALYSIS:")
    if "structure_analysis" in result and "error" not in result["structure_analysis"]:
        struct = result["structure_analysis"]
        print(f"   Analysis Windows: {struct['duration_windows']} (1-second segments)")
        print(f"   Significant Changes: {struct['significant_changes']}")
        print(f"   Energy Variation: {struct['energy_variation']}")
        print(f"   Low Energy Sections: {struct['low_energy_sections']}")
        print(f"   High Energy Sections: {struct['high_energy_sections']}")
        print(f"   Structure Type: {struct['structure_type']}")
    else:
        print("   Could not perform structural analysis")
    print()
    
    print("6. MOOD AND CHARACTER ASSESSMENT:")
    mood = result["mood_assessment"]
    print(f"   Energy Level: {mood.get('energy_level', 'unknown')}")
    print(f"   Tempo Mood: {mood.get('tempo_mood', 'unknown')}")
    print(f"   Frequency Mood: {mood.get('frequency_mood', 'unknown')}")
    print(f"   Overall Descriptors: {', '.join(mood.get('overall_descriptors', ['unknown']))}")
    print()
    
    # Save detailed results as JSON
    output_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16395866398/analysis/detailed_audio_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Detailed analysis saved to: {output_file}")