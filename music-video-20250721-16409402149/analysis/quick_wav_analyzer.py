#!/usr/bin/env python3
"""
Quick WAV file analyzer - extracts basic audio properties
"""
import struct
import os

def quick_wav_analysis(file_path):
    """Quick analysis of WAV file properties"""
    try:
        with open(file_path, 'rb') as f:
            # Read WAV header
            riff = f.read(4)
            if riff != b'RIFF':
                return "ERROR: Not a valid WAV file"
            
            file_size = struct.unpack('<I', f.read(4))[0]
            wave = f.read(4)
            
            # Skip to fmt chunk
            f.read(4)  # fmt
            fmt_size = struct.unpack('<I', f.read(4))[0]
            audio_format = struct.unpack('<H', f.read(2))[0]
            channels = struct.unpack('<H', f.read(2))[0]
            sample_rate = struct.unpack('<I', f.read(4))[0]
            byte_rate = struct.unpack('<I', f.read(4))[0]
            block_align = struct.unpack('<H', f.read(2))[0]
            bits_per_sample = struct.unpack('<H', f.read(2))[0]
            
            # Calculate duration
            duration = file_size / byte_rate
            
            return f"""
BASIC AUDIO PROPERTIES:
- Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)
- Sample Rate: {sample_rate} Hz
- Channels: {channels} ({'Mono' if channels == 1 else 'Stereo'})
- Bit Depth: {bits_per_sample} bits
- File Size: {file_size / (1024*1024):.2f} MB
"""
    except Exception as e:
        return f"ERROR: {str(e)}"

# Run analysis
audio_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250721-16409402149/music/generated-music.wav"
result = quick_wav_analysis(audio_file)
print(result)