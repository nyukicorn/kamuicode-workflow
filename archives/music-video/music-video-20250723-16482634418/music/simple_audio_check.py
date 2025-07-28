#!/usr/bin/env python3
"""
Simple audio file property checker
"""

import wave
import os
import struct

def check_wav_file(file_path):
    """Check basic properties of WAV file"""
    try:
        print(f"Checking file: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        print(f"File size: {os.path.getsize(file_path)} bytes")
        
        with wave.open(file_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            duration = frames / sample_rate
            
            print(f"\n=== BASIC AUDIO PROPERTIES ===")
            print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            print(f"Sample Rate: {sample_rate} Hz")
            print(f"Channels: {channels} ({'Mono' if channels == 1 else 'Stereo' if channels == 2 else f'{channels} channels'})")
            print(f"Sample Width: {sample_width} bytes ({sample_width * 8} bits)")
            print(f"Total Frames: {frames:,}")
            print(f"Bitrate: {sample_rate * channels * sample_width * 8 / 1000:.1f} kbps")
            
            # Read a small sample to check if file is valid
            wav_file.setpos(0)
            sample_data = wav_file.readframes(min(1000, frames))
            print(f"Successfully read {len(sample_data)} bytes of audio data")
            
            # Estimate if this matches music box characteristics
            print(f"\n=== MUSIC BOX ASSESSMENT ===")
            print(f"Expected tempo range: 60-70 BPM")
            print(f"Duration suggests: {'Short piece' if duration < 60 else 'Medium piece' if duration < 180 else 'Long piece'}")
            
            if sample_rate >= 44100:
                print("✓ High quality sample rate suitable for detailed analysis")
            else:
                print("⚠ Lower sample rate - may limit frequency analysis")
                
            if channels == 1:
                print("✓ Mono recording - typical for music box samples")
            else:
                print("• Stereo recording - may need to convert to mono for some analyses")
                
            return True
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    file_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250723-16482634418/music/generated-music.wav"
    check_wav_file(file_path)