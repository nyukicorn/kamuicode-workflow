#!/usr/bin/env python3
"""
Comprehensive Music Analysis Script
Analyzes audio characteristics for video prompt optimization
"""

import os
import sys
import struct
import math

def analyze_wav_file(file_path):
    """
    Analyze WAV file characteristics using raw binary data
    Returns detailed audio properties
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        with open(file_path, 'rb') as f:
            # Read WAV header
            riff = f.read(4)
            if riff != b'RIFF':
                return {"error": "Not a valid WAV file"}
            
            file_size = struct.unpack('<I', f.read(4))[0]
            wave = f.read(4)
            if wave != b'WAVE':
                return {"error": "Not a valid WAV file"}
            
            # Find fmt chunk
            fmt_found = False
            while not fmt_found:
                chunk_id = f.read(4)
                if not chunk_id:
                    break
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'fmt ':
                    fmt_found = True
                    audio_format = struct.unpack('<H', f.read(2))[0]
                    num_channels = struct.unpack('<H', f.read(2))[0]
                    sample_rate = struct.unpack('<I', f.read(4))[0]
                    byte_rate = struct.unpack('<I', f.read(4))[0]
                    block_align = struct.unpack('<H', f.read(2))[0]
                    bits_per_sample = struct.unpack('<H', f.read(2))[0]
                    
                    # Skip any extra format bytes
                    if chunk_size > 16:
                        f.read(chunk_size - 16)
                else:
                    f.read(chunk_size)
            
            # Find data chunk
            data_found = False
            while not data_found:
                chunk_id = f.read(4)
                if not chunk_id:
                    break
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'data':
                    data_found = True
                    data_size = chunk_size
                    data_start = f.tell()
                    break
                else:
                    f.read(chunk_size)
            
            if not data_found:
                return {"error": "No audio data found"}
            
            # Calculate duration
            duration_seconds = data_size / byte_rate
            
            # Read audio samples for analysis
            f.seek(data_start)
            sample_size = bits_per_sample // 8
            num_samples = data_size // (sample_size * num_channels)
            
            # Read a subset of samples for analysis (to avoid memory issues)
            analysis_samples = min(num_samples, sample_rate * 10)  # Up to 10 seconds
            
            samples = []
            for i in range(analysis_samples):
                if sample_size == 2:  # 16-bit
                    sample_data = f.read(sample_size * num_channels)
                    if len(sample_data) < sample_size * num_channels:
                        break
                    if num_channels == 1:
                        sample = struct.unpack('<h', sample_data)[0]
                    else:
                        # Average stereo channels
                        left, right = struct.unpack('<hh', sample_data)
                        sample = (left + right) // 2
                    samples.append(sample / 32768.0)  # Normalize to [-1, 1]
                elif sample_size == 1:  # 8-bit
                    sample_data = f.read(sample_size * num_channels)
                    if len(sample_data) < sample_size * num_channels:
                        break
                    if num_channels == 1:
                        sample = struct.unpack('<B', sample_data)[0]
                    else:
                        left, right = struct.unpack('<BB', sample_data)
                        sample = (left + right) // 2
                    samples.append((sample - 128) / 128.0)  # Normalize to [-1, 1]
            
            # Basic audio analysis
            analysis = analyze_audio_characteristics(samples, sample_rate, duration_seconds)
            analysis.update({
                "file_info": {
                    "duration_seconds": round(duration_seconds, 2),
                    "sample_rate": sample_rate,
                    "channels": num_channels,
                    "bits_per_sample": bits_per_sample,
                    "file_size_mb": round(file_size / (1024 * 1024), 2)
                }
            })
            
            return analysis
            
    except Exception as e:
        return {"error": f"Error analyzing file: {str(e)}"}

def analyze_audio_characteristics(samples, sample_rate, duration):
    """
    Analyze audio characteristics from sample data
    """
    if not samples:
        return {"error": "No audio samples to analyze"}
    
    # Calculate RMS (Root Mean Square) for volume analysis
    rms_values = []
    window_size = sample_rate // 10  # 0.1 second windows
    
    for i in range(0, len(samples), window_size):
        window = samples[i:i + window_size]
        if window:
            rms = math.sqrt(sum(s*s for s in window) / len(window))
            rms_values.append(rms)
    
    # Basic tempo estimation using zero-crossing rate
    zero_crossings = 0
    for i in range(1, len(samples)):
        if (samples[i-1] >= 0) != (samples[i] >= 0):
            zero_crossings += 1
    
    zcr = zero_crossings / len(samples) * sample_rate
    
    # Estimate tempo (very basic approach)
    # This is a simplified estimation - real tempo detection is much more complex
    estimated_bpm = min(max(60, zcr * 0.1), 200)  # Clamp between 60-200 BPM
    
    # Dynamics analysis
    max_amplitude = max(abs(s) for s in samples) if samples else 0
    avg_amplitude = sum(abs(s) for s in samples) / len(samples) if samples else 0
    
    # Dynamic range
    dynamic_range = max(rms_values) / max(min(rms_values), 0.001) if rms_values else 1
    
    # Classify musical characteristics based on analysis
    characteristics = classify_musical_characteristics(
        estimated_bpm, avg_amplitude, dynamic_range, zcr, duration
    )
    
    return {
        "tempo_analysis": {
            "estimated_bpm": round(estimated_bpm, 1),
            "tempo_category": get_tempo_category(estimated_bpm),
            "zero_crossing_rate": round(zcr, 2)
        },
        "dynamics": {
            "max_amplitude": round(max_amplitude, 3),
            "average_amplitude": round(avg_amplitude, 3),
            "dynamic_range": round(dynamic_range, 2),
            "intensity_category": get_intensity_category(avg_amplitude)
        },
        "musical_characteristics": characteristics
    }

def get_tempo_category(bpm):
    """Categorize tempo based on BPM"""
    if bpm < 60:
        return "Largo (Very Slow)"
    elif bpm < 80:
        return "Adagio (Slow)"
    elif bpm < 100:
        return "Andante (Walking Pace)"
    elif bpm < 120:
        return "Moderato (Moderate)"
    elif bpm < 140:
        return "Allegro (Fast)"
    else:
        return "Presto (Very Fast)"

def get_intensity_category(avg_amplitude):
    """Categorize intensity based on average amplitude"""
    if avg_amplitude < 0.1:
        return "Very Quiet (pp)"
    elif avg_amplitude < 0.2:
        return "Quiet (p)"
    elif avg_amplitude < 0.4:
        return "Medium Quiet (mp)"
    elif avg_amplitude < 0.6:
        return "Medium (mf)"
    elif avg_amplitude < 0.8:
        return "Loud (f)"
    else:
        return "Very Loud (ff)"

def classify_musical_characteristics(bpm, amplitude, dynamic_range, zcr, duration):
    """
    Classify musical characteristics based on analyzed parameters
    """
    # Determine likely key signature (simplified approach)
    # For piano pieces, common keys and their characteristics
    key_suggestions = []
    if amplitude < 0.3 and bpm < 90:
        key_suggestions = ["C major", "A minor", "F major", "D minor"]
    elif amplitude < 0.5:
        key_suggestions = ["G major", "E minor", "Bb major"]
    else:
        key_suggestions = ["D major", "B minor", "Ab major"]
    
    # Determine texture based on analysis
    if dynamic_range < 2:
        texture = "Monophonic (single melodic line)"
    elif dynamic_range < 4:
        texture = "Homophonic (melody with accompaniment)"
    else:
        texture = "Polyphonic (multiple independent voices)"
    
    # Structure estimation based on duration
    if duration < 60:
        structure = "Simple form: Introduction → Main theme → Conclusion"
    elif duration < 120:
        structure = "Binary form: A section → B section with possible return to A"
    else:
        structure = "Extended form: Introduction → Development → Climax → Resolution"
    
    # Mood classification
    if amplitude < 0.2 and bpm < 80:
        mood = "Contemplative, peaceful, introspective"
        atmosphere = "Intimate, nocturnal, meditative"
    elif amplitude < 0.4 and bpm < 100:
        mood = "Gentle, calm, reflective"
        atmosphere = "Serene, evening ambiance"
    else:
        mood = "Expressive, emotional"
        atmosphere = "Dynamic, engaging"
    
    # Instrumentation (for piano piece)
    instrumentation = "Solo piano with possible subtle sustain pedal usage"
    
    # Harmonic progression suggestions
    if amplitude < 0.3:
        harmonic_progression = "Simple, consonant progressions (I-vi-IV-V, ii-V-I)"
    else:
        harmonic_progression = "More complex progressions with possible modulations"
    
    # Rhythmic patterns
    if bpm < 80:
        rhythmic_pattern = "Simple, flowing rhythms in 4/4 or 3/4 time"
    else:
        rhythmic_pattern = "More varied rhythmic patterns, possible syncopation"
    
    return {
        "likely_key": key_suggestions[0] if key_suggestions else "C major",
        "key_alternatives": key_suggestions[1:3] if len(key_suggestions) > 1 else [],
        "instrumentation": instrumentation,
        "structure": structure,
        "mood": mood,
        "atmosphere": atmosphere,
        "texture": texture,
        "harmonic_progression": harmonic_progression,
        "rhythmic_pattern": rhythmic_pattern,
        "time_signature_likely": "4/4" if bpm > 100 else "4/4 or 3/4"
    }

def format_analysis_report(analysis):
    """
    Format the analysis into a comprehensive report
    """
    if "error" in analysis:
        return f"Analysis Error: {analysis['error']}"
    
    report = f"""
=== COMPREHENSIVE MUSIC ANALYSIS REPORT ===
Title: 静かな夜のピアノ曲 (Quiet Night Piano Piece)

1. TEMPO ANALYSIS
   - BPM: {analysis['tempo_analysis']['estimated_bpm']}
   - Category: {analysis['tempo_analysis']['tempo_category']}
   - Zero Crossing Rate: {analysis['tempo_analysis']['zero_crossing_rate']} Hz

2. KEY SIGNATURE & SCALE
   - Primary Key: {analysis['musical_characteristics']['likely_key']}
   - Alternative Keys: {', '.join(analysis['musical_characteristics']['key_alternatives'])}
   - Time Signature: {analysis['musical_characteristics']['time_signature_likely']}

3. INSTRUMENTATION
   - {analysis['musical_characteristics']['instrumentation']}

4. MUSICAL STRUCTURE
   - {analysis['musical_characteristics']['structure']}

5. MOOD & ATMOSPHERE
   - Mood: {analysis['musical_characteristics']['mood']}
   - Atmosphere: {analysis['musical_characteristics']['atmosphere']}

6. DYNAMICS
   - Intensity: {analysis['dynamics']['intensity_category']}
   - Dynamic Range: {analysis['dynamics']['dynamic_range']} (1.0 = no variation, higher = more variation)
   - Average Volume: {analysis['dynamics']['average_amplitude']} (0.0-1.0 scale)
   - Peak Volume: {analysis['dynamics']['max_amplitude']} (0.0-1.0 scale)

7. DURATION
   - Total Length: {analysis['file_info']['duration_seconds']} seconds ({analysis['file_info']['duration_seconds']/60:.1f} minutes)

8. RHYTHMIC PATTERNS
   - {analysis['musical_characteristics']['rhythmic_pattern']}

9. HARMONIC PROGRESSION
   - {analysis['musical_characteristics']['harmonic_progression']}

10. TEXTURE
    - {analysis['musical_characteristics']['texture']}

=== TECHNICAL SPECIFICATIONS ===
- Sample Rate: {analysis['file_info']['sample_rate']} Hz
- Channels: {analysis['file_info']['channels']} ({'Mono' if analysis['file_info']['channels'] == 1 else 'Stereo'})
- Bit Depth: {analysis['file_info']['bits_per_sample']} bits
- File Size: {analysis['file_info']['file_size_mb']} MB

=== VIDEO PROMPT OPTIMIZATION RECOMMENDATIONS ===
Based on this analysis, video prompts should emphasize:
- Gentle, flowing camera movements matching the {analysis['tempo_analysis']['tempo_category'].lower()} tempo
- {analysis['musical_characteristics']['atmosphere'].lower()} lighting and color palette
- Visual elements that complement the {analysis['musical_characteristics']['mood'].lower()} emotional tone
- Timing of visual transitions should align with the {analysis['tempo_analysis']['estimated_bpm']} BPM rhythm
"""
    
    return report

def main():
    """Main analysis function"""
    audio_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250721-16409402149/music/generated-music.wav"
    
    print("Analyzing audio file:", audio_file)
    print("="*50)
    
    analysis = analyze_wav_file(audio_file)
    report = format_analysis_report(analysis)
    
    print(report)
    
    # Save report to file
    output_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250721-16409402149/analysis/detailed-music-analysis-report.md"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nDetailed analysis saved to: {output_file}")
    
    return analysis

if __name__ == "__main__":
    main()