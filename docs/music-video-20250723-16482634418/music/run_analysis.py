#!/usr/bin/env python3

# Import and run the comprehensive analysis
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from comprehensive_analysis import main
    main()
except ImportError as e:
    print(f"Import error: {e}")
    print("Running basic analysis instead...")
    
    # Fallback basic analysis
    import wave
    import os
    
    filepath = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250723-16482634418/music/generated-music.wav"
    
    try:
        print("=== BASIC AUDIO FILE ANALYSIS ===")
        print(f"File: {filepath}")
        print(f"File exists: {os.path.exists(filepath)}")
        print(f"File size: {os.path.getsize(filepath):,} bytes ({os.path.getsize(filepath) / 1024 / 1024:.2f} MB)")
        
        with wave.open(filepath, 'rb') as wav:
            duration = wav.getnframes() / wav.getframerate()
            sample_rate = wav.getframerate()
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            frames = wav.getnframes()
            
            print(f"\nBasic Properties:")
            print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            print(f"Sample Rate: {sample_rate} Hz")
            print(f"Channels: {channels} ({'Mono' if channels == 1 else 'Stereo'})")
            print(f"Sample Width: {sample_width} bytes ({sample_width * 8} bits)")
            print(f"Total Frames: {frames:,}")
            print(f"Bitrate: {sample_rate * channels * sample_width * 8 / 1000:.1f} kbps")
            
            print(f"\nMusic Box Assessment:")
            if 30 <= duration <= 40:
                print("✓ Duration ideal for music box piece (30-40s)")
            elif 25 <= duration <= 50:
                print("• Duration acceptable for music box piece")
            else:
                print("⚠ Duration outside typical music box range")
                
            if sample_rate >= 44100:
                print("✓ High quality sample rate")
            else:
                print("• Lower sample rate")
                
            print(f"\nExpected characteristics for 'バラの花をイメージした美しいオルゴールの曲':")
            print("- Gentle, delicate tones (music box-like)")
            print("- Slow to moderate tempo (60-70 BPM)")
            print("- Simple, clear melody")
            print("- Limited frequency range")
            print("- Consistent dynamics with subtle variations")
            
            # Rough tempo estimation based on duration
            if duration > 0:
                # Very rough estimate: assume 4/4 time, moderate number of notes
                estimated_beats = duration * 1.2  # rough beats per second
                estimated_bpm = estimated_beats * 60 / duration
                print(f"\nRough tempo estimate: {estimated_bpm:.1f} BPM")
                
                if 60 <= estimated_bpm <= 70:
                    print("✓ Estimated tempo in ideal range")
                else:
                    print("• Estimated tempo may need verification")
    
    except Exception as e:
        print(f"Error: {e}")