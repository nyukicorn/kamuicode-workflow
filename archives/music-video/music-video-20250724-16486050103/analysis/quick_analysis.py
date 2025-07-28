import wave
import numpy as np
import os

# Analyze the music file
file_path = '/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250724-16486050103/music/generated-music.wav'

print("MUSIC ANALYSIS REPORT")
print("=" * 50)
print("Target: バラの花をイメージした美しいオルゴールの曲")
print("(Beautiful music box melody featuring rose flowers)")
print("=" * 50)

try:
    # Basic file info
    size = os.path.getsize(file_path)
    print(f"File size: {size:,} bytes ({size/(1024*1024):.1f} MB)")
    
    # Wave file analysis
    with wave.open(file_path, 'rb') as wav:
        frames = wav.getnframes()
        rate = wav.getframerate()
        channels = wav.getnchannels()
        width = wav.getsampwidth()
        duration = frames / rate
        
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"Sample Rate: {rate} Hz")
        print(f"Channels: {channels} ({'Stereo' if channels == 2 else 'Mono'})")
        print(f"Bit Depth: {width*8} bits")
        print(f"Audio Quality: {'High' if rate >= 44100 and width >= 2 else 'Standard'}")
        
        # Read and analyze audio data
        audio_bytes = wav.readframes(frames)
        
        if width == 2:
            audio = np.frombuffer(audio_bytes, dtype=np.int16)
            max_val = 32767
        elif width == 1:
            audio = np.frombuffer(audio_bytes, dtype=np.uint8)
            max_val = 255
        else:
            audio = np.frombuffer(audio_bytes, dtype=np.int32)
            max_val = 2147483647
        
        if channels == 2:
            audio = audio.reshape(-1, 2)
            audio = audio[:, 0]  # Use left channel
        
        # Normalize
        audio_norm = audio.astype(np.float32) / max_val
        
        # Basic audio characteristics
        rms = np.sqrt(np.mean(audio_norm**2))
        peak = np.max(np.abs(audio_norm))
        
        print(f"RMS Level: {rms:.3f}")
        print(f"Peak Level: {peak:.3f}")
        
        # Dynamic range in dB
        if rms > 0 and peak > 0:
            dynamic_range_db = 20 * np.log10(peak/rms)
            print(f"Dynamic Range: {dynamic_range_db:.1f} dB")
        
        # Simple tempo estimation
        chunk_size = max(rate // 4, 1024)  # 0.25 second chunks
        chunks = len(audio_norm) // chunk_size
        
        if chunks > 4:
            energies = []
            for i in range(chunks):
                chunk = audio_norm[i*chunk_size:(i+1)*chunk_size]
                energy = np.mean(chunk**2)
                energies.append(energy)
            
            # Simple beat detection
            avg_energy = np.mean(energies)
            beats = sum(1 for e in energies if e > avg_energy * 1.2)
            
            if beats > 0 and duration > 0:
                estimated_bpm = (beats / (duration/60))
                print(f"Estimated BPM: {estimated_bpm:.0f}")
                
                if estimated_bpm < 60:
                    tempo_feel = "Very Slow (Perfect for music box)"
                elif estimated_bpm < 80:
                    tempo_feel = "Slow (Ideal for music box)"
                elif estimated_bpm < 120:
                    tempo_feel = "Medium (Good for music box)"
                else:
                    tempo_feel = "Fast (May be too quick for music box)"
                
                print(f"Tempo Feel: {tempo_feel}")
        
        # Frequency analysis (simplified)
        if len(audio_norm) > 1024:
            fft_size = min(4096, len(audio_norm))
            start_idx = len(audio_norm) // 2 - fft_size // 2
            segment = audio_norm[start_idx:start_idx + fft_size]
            
            fft = np.fft.fft(segment)
            freqs = np.fft.fftfreq(fft_size, 1/rate)
            magnitude = np.abs(fft[:fft_size//2])
            freqs_pos = freqs[:fft_size//2]
            
            # Find dominant frequency
            if len(magnitude) > 10:
                dominant_idx = np.argmax(magnitude[10:]) + 10
                dominant_freq = freqs_pos[dominant_idx]
                print(f"Dominant Frequency: {dominant_freq:.0f} Hz")
            
            # Frequency distribution
            low_energy = np.sum(magnitude[freqs_pos < 500])
            mid_energy = np.sum(magnitude[(freqs_pos >= 500) & (freqs_pos < 4000)])
            high_energy = np.sum(magnitude[freqs_pos >= 4000])
            total_energy = low_energy + mid_energy + high_energy
            
            if total_energy > 0:
                low_pct = (low_energy / total_energy) * 100
                mid_pct = (mid_energy / total_energy) * 100
                high_pct = (high_energy / total_energy) * 100
                
                print(f"Frequency Distribution:")
                print(f"  Low (< 500Hz): {low_pct:.0f}%")
                print(f"  Mid (500-4000Hz): {mid_pct:.0f}%")
                print(f"  High (> 4000Hz): {high_pct:.0f}%")
        
        print()
        print("MUSIC BOX ANALYSIS:")
        print("-" * 30)
        
        # Music box characteristics assessment
        music_box_score = 0
        total_criteria = 5
        
        # 1. High frequency content (music boxes are bright)
        if 'high_pct' in locals() and high_pct > 20:
            print("✓ High frequencies: Strong (typical music box)")
            music_box_score += 1
        elif 'high_pct' in locals() and high_pct > 10:
            print("~ High frequencies: Moderate")
            music_box_score += 0.5
        else:
            print("✗ High frequencies: Low")
        
        # 2. Gentle tempo
        if 'estimated_bpm' in locals() and estimated_bpm <= 80:
            print("✓ Tempo: Gentle (perfect for music box)")
            music_box_score += 1
        elif 'estimated_bpm' in locals() and estimated_bpm <= 120:
            print("~ Tempo: Moderate")
            music_box_score += 0.5
        else:
            print("✗ Tempo: Too fast for music box")
        
        # 3. Appropriate duration
        if 30 <= duration <= 180:
            print("✓ Duration: Good for music box piece")
            music_box_score += 1
        else:
            print("~ Duration: Could be optimized")
            music_box_score += 0.5
        
        # 4. Dynamic range
        if 'dynamic_range_db' in locals() and 8 <= dynamic_range_db <= 20:
            print("✓ Dynamics: Good range for music box")
            music_box_score += 1
        else:
            print("~ Dynamics: Could be improved")
            music_box_score += 0.5
        
        # 5. Audio quality
        if peak < 0.95 and rms > 0.01:
            print("✓ Quality: No distortion, good level")
            music_box_score += 1
        else:
            print("~ Quality: May have issues")
        
        music_box_percentage = (music_box_score / total_criteria) * 100
        print(f"Music Box Score: {music_box_score:.1f}/{total_criteria} ({music_box_percentage:.0f}%)")
        
        print()
        print("ROSE CONCEPT ALIGNMENT:")
        print("-" * 30)
        
        if music_box_percentage >= 70:
            print("✓ Excellent alignment with music box concept")
        elif music_box_percentage >= 50:
            print("✓ Good alignment with music box concept")
        else:
            print("~ Limited alignment with music box concept")
        
        if duration < 90:
            print("✓ Duration suitable for focused rose imagery")
        else:
            print("~ Consider shorter segments for rose focus")
        
        if 'estimated_bpm' in locals() and estimated_bpm <= 70:
            print("✓ Tempo perfect for delicate rose imagery")
        else:
            print("~ Tempo may be fast for delicate concept")
        
        print()
        print("RECOMMENDATIONS FOR VIDEO:")
        print("-" * 30)
        
        if 'high_pct' in locals() and high_pct > 15:
            print("• Use sparkling, bright visual effects")
        
        if 'estimated_bpm' in locals() and estimated_bpm <= 80:
            print("• Slow, gentle camera movements")
            print("• Gradual transitions between scenes")
        
        if duration < 60:
            print("• Simple, focused visual narrative")
        else:
            print("• Multiple visual movements/sections")
        
        print("• Soft lighting with warm tones")
        print("• Close-ups of rose details")
        print("• Mechanical music box movements")
        
        print()
        overall_rating = "Excellent" if music_box_percentage >= 80 else "Good" if music_box_percentage >= 60 else "Fair"
        print(f"OVERALL RATING: {overall_rating} for music box rose concept")
        
except Exception as e:
    print(f"Error analyzing audio: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)
print("Analysis complete")