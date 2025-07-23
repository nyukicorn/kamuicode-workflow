#!/usr/bin/env python3
"""
Audio Analysis Script for Generated Music
Analyzes the generated music WAV file to extract musical characteristics.
"""

import sys
import os
import wave
import struct
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

def analyze_audio_basic(file_path):
    """Extract basic audio properties from WAV file."""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            duration = frames / sample_rate
            
            # Read audio data
            raw_audio = wav_file.readframes(frames)
            
            # Convert to numpy array
            if sample_width == 1:
                audio_data = np.frombuffer(raw_audio, dtype=np.uint8)
                audio_data = (audio_data - 128) / 128.0
            elif sample_width == 2:
                audio_data = np.frombuffer(raw_audio, dtype=np.int16)
                audio_data = audio_data / 32768.0
            elif sample_width == 4:
                audio_data = np.frombuffer(raw_audio, dtype=np.int32)
                audio_data = audio_data / 2147483648.0
            
            # Handle stereo
            if channels == 2:
                audio_data = audio_data.reshape(-1, 2)
                audio_data = np.mean(audio_data, axis=1)  # Convert to mono
            
            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': channels,
                'sample_width': sample_width,
                'frames': frames,
                'audio_data': audio_data
            }
    except Exception as e:
        print(f"Error reading audio file: {e}")
        return None

def estimate_tempo_autocorrelation(audio_data, sample_rate):
    """Estimate tempo using autocorrelation method."""
    try:
        # Apply envelope detection
        envelope = np.abs(signal.hilbert(audio_data))
        
        # Smooth the envelope
        window_size = int(sample_rate * 0.05)  # 50ms window
        envelope = np.convolve(envelope, np.ones(window_size)/window_size, mode='same')
        
        # Calculate autocorrelation
        autocorr = np.correlate(envelope, envelope, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find peaks in autocorrelation
        min_lag = int(sample_rate * 0.4)  # Minimum 0.4s (150 BPM max)
        max_lag = int(sample_rate * 2.0)  # Maximum 2.0s (30 BPM min)
        
        if max_lag > len(autocorr):
            max_lag = len(autocorr) - 1
        
        peaks, _ = signal.find_peaks(autocorr[min_lag:max_lag], height=np.max(autocorr) * 0.1)
        
        if len(peaks) > 0:
            # Get the most prominent peak
            peak_idx = peaks[np.argmax(autocorr[min_lag:max_lag][peaks])]
            lag_time = (min_lag + peak_idx) / sample_rate
            tempo = 60.0 / lag_time
            return tempo
        else:
            return None
    except Exception as e:
        print(f"Error in tempo estimation: {e}")
        return None

def analyze_frequency_content(audio_data, sample_rate):
    """Analyze frequency content and harmonic structure."""
    try:
        # Compute FFT
        n_fft = 2048
        hop_length = 512
        
        # Short-time Fourier transform
        f, t, Sxx = signal.spectrogram(audio_data, sample_rate, nperseg=n_fft, noverlap=n_fft-hop_length)
        
        # Average power spectrum
        avg_power = np.mean(Sxx, axis=1)
        
        # Find dominant frequencies
        peaks, properties = signal.find_peaks(avg_power, height=np.max(avg_power) * 0.1, distance=10)
        dominant_freqs = f[peaks]
        dominant_powers = avg_power[peaks]
        
        # Sort by power
        sorted_indices = np.argsort(dominant_powers)[::-1]
        dominant_freqs = dominant_freqs[sorted_indices][:10]  # Top 10 frequencies
        dominant_powers = dominant_powers[sorted_indices][:10]
        
        # Spectral centroid (brightness)
        spectral_centroid = np.sum(f * avg_power) / np.sum(avg_power)
        
        # Spectral rolloff (90% of energy)
        cumulative_power = np.cumsum(avg_power)
        rolloff_idx = np.where(cumulative_power >= 0.9 * cumulative_power[-1])[0][0]
        spectral_rolloff = f[rolloff_idx]
        
        return {
            'dominant_frequencies': dominant_freqs.tolist(),
            'dominant_powers': dominant_powers.tolist(),
            'spectral_centroid': spectral_centroid,
            'spectral_rolloff': spectral_rolloff,
            'frequency_range': [f[0], f[-1]]
        }
    except Exception as e:
        print(f"Error in frequency analysis: {e}")
        return None

def analyze_dynamics(audio_data, sample_rate):
    """Analyze dynamic characteristics of the audio."""
    try:
        # RMS energy over time
        frame_size = int(sample_rate * 0.1)  # 100ms frames
        hop_size = int(sample_rate * 0.05)   # 50ms hop
        
        rms_values = []
        for i in range(0, len(audio_data) - frame_size, hop_size):
            frame = audio_data[i:i+frame_size]
            rms = np.sqrt(np.mean(frame**2))
            rms_values.append(rms)
        
        rms_values = np.array(rms_values)
        
        # Dynamic range
        dynamic_range = np.max(rms_values) - np.min(rms_values)
        
        # Average RMS
        avg_rms = np.mean(rms_values)
        
        # Standard deviation (variability)
        rms_std = np.std(rms_values)
        
        return {
            'dynamic_range': dynamic_range,
            'average_rms': avg_rms,
            'rms_variability': rms_std,
            'peak_amplitude': np.max(np.abs(audio_data)),
            'rms_over_time': rms_values.tolist()
        }
    except Exception as e:
        print(f"Error in dynamics analysis: {e}")
        return None

def detect_rhythm_patterns(audio_data, sample_rate):
    """Detect rhythm patterns and beat structure."""
    try:
        # Onset detection using spectral flux
        n_fft = 1024
        hop_length = 512
        
        # Compute spectrogram
        f, t, Sxx = signal.spectrogram(audio_data, sample_rate, nperseg=n_fft, noverlap=n_fft-hop_length)
        
        # Spectral flux (difference between consecutive frames)
        spectral_flux = np.diff(Sxx, axis=1)
        spectral_flux = np.sum(np.maximum(spectral_flux, 0), axis=0)
        
        # Peak detection for onsets
        onset_peaks, _ = signal.find_peaks(spectral_flux, height=np.max(spectral_flux) * 0.3, distance=int(sample_rate/hop_length * 0.1))
        onset_times = onset_peaks * hop_length / sample_rate
        
        # Analyze beat intervals
        if len(onset_times) > 1:
            intervals = np.diff(onset_times)
            avg_interval = np.mean(intervals)
            interval_std = np.std(intervals)
            
            return {
                'onset_times': onset_times.tolist(),
                'num_onsets': len(onset_times),
                'average_beat_interval': avg_interval,
                'beat_interval_variability': interval_std,
                'estimated_tempo_from_onsets': 60.0 / avg_interval if avg_interval > 0 else None
            }
        else:
            return {
                'onset_times': [],
                'num_onsets': 0,
                'average_beat_interval': None,
                'beat_interval_variability': None,
                'estimated_tempo_from_onsets': None
            }
    except Exception as e:
        print(f"Error in rhythm analysis: {e}")
        return None

def main():
    file_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250723-16482634418/music/generated-music.wav"
    
    print("=== AUDIO ANALYSIS REPORT ===")
    print(f"File: {file_path}")
    print("\n" + "="*50)
    
    # Basic audio properties
    print("\n1. BASIC AUDIO PROPERTIES")
    print("-" * 30)
    
    basic_info = analyze_audio_basic(file_path)
    if basic_info:
        print(f"Duration: {basic_info['duration']:.2f} seconds")
        print(f"Sample Rate: {basic_info['sample_rate']} Hz")
        print(f"Channels: {basic_info['channels']}")
        print(f"Sample Width: {basic_info['sample_width']} bytes")
        print(f"Total Frames: {basic_info['frames']}")
        
        audio_data = basic_info['audio_data']
        sample_rate = basic_info['sample_rate']
        
        # Musical characteristics
        print("\n2. MUSICAL CHARACTERISTICS")
        print("-" * 30)
        
        # Tempo estimation
        tempo = estimate_tempo_autocorrelation(audio_data, sample_rate)
        if tempo:
            print(f"Estimated Tempo: {tempo:.1f} BPM")
            if 60 <= tempo <= 70:
                print("✓ Tempo matches expected range (60-70 BPM)")
            else:
                print(f"⚠ Tempo outside expected range (60-70 BPM)")
        else:
            print("Could not estimate tempo reliably")
        
        # Rhythm patterns
        rhythm_info = detect_rhythm_patterns(audio_data, sample_rate)
        if rhythm_info:
            print(f"Number of detected onsets: {rhythm_info['num_onsets']}")
            if rhythm_info['estimated_tempo_from_onsets']:
                print(f"Tempo from onsets: {rhythm_info['estimated_tempo_from_onsets']:.1f} BPM")
            if rhythm_info['average_beat_interval']:
                print(f"Average beat interval: {rhythm_info['average_beat_interval']:.3f} seconds")
                print(f"Beat timing variability: {rhythm_info['beat_interval_variability']:.3f}")
        
        # Dynamics
        dynamics_info = analyze_dynamics(audio_data, sample_rate)
        if dynamics_info:
            print(f"Dynamic range: {dynamics_info['dynamic_range']:.3f}")
            print(f"Average RMS level: {dynamics_info['average_rms']:.3f}")
            print(f"RMS variability: {dynamics_info['rms_variability']:.3f}")
            print(f"Peak amplitude: {dynamics_info['peak_amplitude']:.3f}")
        
        # Tonal qualities
        print("\n3. TONAL QUALITIES")
        print("-" * 30)
        
        freq_info = analyze_frequency_content(audio_data, sample_rate)
        if freq_info:
            print(f"Spectral centroid (brightness): {freq_info['spectral_centroid']:.1f} Hz")
            print(f"Spectral rolloff (90% energy): {freq_info['spectral_rolloff']:.1f} Hz")
            print("Top 5 dominant frequencies:")
            for i, (freq, power) in enumerate(zip(freq_info['dominant_frequencies'][:5], 
                                                freq_info['dominant_powers'][:5])):
                print(f"  {i+1}. {freq:.1f} Hz (power: {power:.3f})")
        
        # Musical box characteristics assessment
        print("\n4. MUSIC BOX CHARACTERISTICS ASSESSMENT")
        print("-" * 30)
        
        print("Expected characteristics for 'バラの花をイメージした美しいオルゴールの曲':")
        print("- Gentle, delicate tones (music box-like)")
        print("- Slow to moderate tempo (60-70 BPM)")
        print("- Simple, clear melody")
        print("- Limited frequency range (typical of music box)")
        print("- Consistent dynamics with subtle variations")
        
        print("\nAnalysis Results:")
        if tempo and 60 <= tempo <= 70:
            print("✓ Tempo appropriate for gentle music box song")
        elif tempo:
            print(f"⚠ Tempo ({tempo:.1f} BPM) may be outside ideal range")
        
        if freq_info and freq_info['spectral_rolloff'] < 4000:
            print("✓ Limited high-frequency content (music box characteristic)")
        elif freq_info:
            print("⚠ Broader frequency range than typical music box")
        
        if dynamics_info and dynamics_info['rms_variability'] < 0.1:
            print("✓ Gentle, consistent dynamics")
        elif dynamics_info:
            print("⚠ Higher dynamic variation than expected for gentle music box")
        
        # Recommendations for video prompts
        print("\n5. VIDEO PROMPT OPTIMIZATION RECOMMENDATIONS")
        print("-" * 30)
        
        print("Based on the audio analysis, consider these elements for video generation:")
        
        if tempo:
            if tempo < 65:
                print(f"• Slow, contemplative visuals (tempo: {tempo:.1f} BPM)")
                print("• Gentle camera movements, soft transitions")
            else:
                print(f"• Moderate-paced visuals (tempo: {tempo:.1f} BPM)")
                print("• Smooth, flowing camera movements")
        
        if dynamics_info:
            if dynamics_info['dynamic_range'] < 0.2:
                print("• Consistent lighting and soft visual dynamics")
                print("• Avoid dramatic visual changes")
            else:
                print("• Some visual dynamics to match audio variations")
        
        if freq_info:
            if freq_info['spectral_centroid'] < 1000:
                print("• Warm, soft color palette (low spectral centroid)")
                print("• Emphasize lower visual frequencies")
            else:
                print("• Brighter visual elements (higher spectral centroid)")
        
        print("• Rose-themed imagery (as per original concept)")
        print("• Delicate, ornate visual elements (music box aesthetic)")
        print("• Soft focus and gentle lighting")
        print("• Vintage or nostalgic visual style")
        
    else:
        print("Failed to analyze audio file")

if __name__ == "__main__":
    main()