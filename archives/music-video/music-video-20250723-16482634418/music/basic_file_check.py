#!/usr/bin/env python3

import os
import wave

filepath = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250723-16482634418/music/generated-music.wav"

print("FILE EXISTENCE AND BASIC INFO")
print("=" * 40)
print(f"File exists: {os.path.exists(filepath)}")

if os.path.exists(filepath):
    file_size = os.path.getsize(filepath)
    print(f"File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    
    # Try to read with wave module
    try:
        with wave.open(filepath, 'rb') as wav:
            print(f"\nWAV FILE PROPERTIES")
            print("=" * 40)
            print(f"Sample rate: {wav.getframerate()} Hz")
            print(f"Channels: {wav.getnchannels()}")
            print(f"Sample width: {wav.getsampwidth()} bytes")
            print(f"Total frames: {wav.getnframes():,}")
            print(f"Duration: {wav.getnframes() / wav.getframerate():.2f} seconds")
            print(f"Compression type: {wav.getcomptype()}")
            print(f"Compression name: {wav.getcompname()}")
            
            duration = wav.getnframes() / wav.getframerate()
            
            print(f"\nMUSIC BOX ANALYSIS")
            print("=" * 40)
            print(f"Expected tempo range: 60-70 BPM")
            print(f"Expected duration: 35-40 seconds")
            print(f"Actual duration: {duration:.2f} seconds")
            
            if 35 <= duration <= 40:
                print("✓ Perfect duration for music box piece")
            elif 30 <= duration <= 45:
                print("• Good duration for music box piece")
            else:
                print("⚠ Duration outside typical range")
            
            # File size assessment
            expected_size = wav.getframerate() * wav.getnchannels() * wav.getsampwidth() * duration
            print(f"Expected file size: {expected_size:,.0f} bytes")
            print(f"Actual file size: {file_size:,} bytes")
            print(f"Size ratio: {file_size / expected_size:.2f}")
            
            if abs(file_size - expected_size) / expected_size < 0.1:
                print("✓ File size matches expected uncompressed WAV")
            else:
                print("• File size suggests possible compression or metadata")

    except Exception as e:
        print(f"Error reading WAV file: {str(e)}")
else:
    print("File does not exist!")

print(f"\nRECOMMENDATIONS FOR VIDEO OPTIMIZATION")
print("=" * 40)
print("Based on the concept 'バラの花をイメージした美しいオルゴールの曲':")
print("• Use gentle, slow camera movements")
print("• Emphasize rose imagery and soft textures")
print("• Apply warm, soft lighting")
print("• Use vintage/nostalgic visual effects")
print("• Include music box aesthetic elements")
print("• Maintain dreamy, romantic atmosphere")
print("• Consider particle effects (falling petals)")
print("• Use soft focus and gentle transitions")