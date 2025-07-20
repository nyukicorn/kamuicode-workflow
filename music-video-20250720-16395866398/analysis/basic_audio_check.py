#!/usr/bin/env python3
"""
Basic audio file analysis using only standard library
"""

import os
import wave
import struct

def basic_audio_analysis(file_path):
    """Basic analysis using Python's wave module"""
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    try:
        with wave.open(file_path, 'rb') as wav_file:
            # Get basic properties
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            duration = frames / sample_rate
            
            print("=== BASIC AUDIO ANALYSIS ===")
            print(f"File: {file_path}")
            print(f"Duration: {duration:.3f} seconds ({duration/60:.2f} minutes)")
            print(f"Sample Rate: {sample_rate} Hz")
            print(f"Channels: {channels} ({'Stereo' if channels == 2 else 'Mono'})")
            print(f"Bit Depth: {sample_width * 8} bits")
            print(f"Total Samples: {frames:,}")
            print(f"File Size: {os.path.getsize(file_path):,} bytes ({os.path.getsize(file_path)/(1024*1024):.2f} MB)")
            
            # Read a small sample to check if data exists
            wav_file.setpos(0)
            sample_data = wav_file.readframes(min(1024, frames))
            
            if sample_data:
                print("✓ Audio data detected")
                
                # Basic amplitude check
                if sample_width == 2:  # 16-bit
                    samples = struct.unpack(f'{len(sample_data)//2}h', sample_data)
                    max_amplitude = max(abs(s) for s in samples)
                    print(f"Sample amplitude range: ±{max_amplitude} (max: ±32767)")
                    
                    if max_amplitude > 1000:
                        print("✓ Significant audio signal detected")
                    else:
                        print("⚠ Low amplitude signal - might be very quiet")
                
            else:
                print("⚠ No audio data found")
                
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    file_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16395866398/music/generated-music.wav"
    basic_audio_analysis(file_path)