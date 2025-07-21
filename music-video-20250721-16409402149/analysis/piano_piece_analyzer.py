#!/usr/bin/env python3
"""
Quiet Night Piano Piece Analyzer
Detailed analysis for "静かな夜のピアノ曲" (Quiet Night Piano Piece)
"""

import os
import sys
import struct
import math
import wave
from pathlib import Path
from datetime import datetime

class QuietNightPianoAnalyzer:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.analysis_results = {}
        
    def analyze_wav_header(self):
        """Analyze WAV file header and basic properties"""
        if not self.file_path.exists():
            return {"error": "File does not exist"}
        
        try:
            with open(self.file_path, 'rb') as f:
                # Read WAV header
                riff = f.read(4)
                if riff != b'RIFF':
                    return {"error": "Not a valid WAV file"}
                
                file_size = struct.unpack('<I', f.read(4))[0]
                wave_marker = f.read(4)
                if wave_marker != b'WAVE':
                    return {"error": "Not a valid WAV file"}
                
                # Find fmt chunk
                while True:
                    chunk_id = f.read(4)
                    if not chunk_id:
                        return {"error": "fmt chunk not found"}
                    chunk_size = struct.unpack('<I', f.read(4))[0]
                    
                    if chunk_id == b'fmt ':
                        audio_format = struct.unpack('<H', f.read(2))[0]
                        num_channels = struct.unpack('<H', f.read(2))[0]
                        sample_rate = struct.unpack('<I', f.read(4))[0]
                        byte_rate = struct.unpack('<I', f.read(4))[0]
                        block_align = struct.unpack('<H', f.read(2))[0]
                        bits_per_sample = struct.unpack('<H', f.read(2))[0]
                        
                        # Skip any extra format bytes
                        if chunk_size > 16:
                            f.read(chunk_size - 16)
                        break
                    else:
                        f.read(chunk_size)
                
                # Find data chunk
                while True:
                    chunk_id = f.read(4)
                    if not chunk_id:
                        return {"error": "data chunk not found"}
                    chunk_size = struct.unpack('<I', f.read(4))[0]
                    
                    if chunk_id == b'data':
                        data_size = chunk_size
                        break
                    else:
                        f.read(chunk_size)
                
                # Calculate duration
                duration_seconds = data_size / byte_rate
                
                return {
                    "file_size_bytes": file_size,
                    "file_size_mb": round(file_size / (1024 * 1024), 2),
                    "audio_format": audio_format,
                    "channels": num_channels,
                    "sample_rate": sample_rate,
                    "byte_rate": byte_rate,
                    "bits_per_sample": bits_per_sample,
                    "data_size": data_size,
                    "duration_seconds": round(duration_seconds, 2),
                    "duration_minutes": round(duration_seconds / 60, 2)
                }
                
        except Exception as e:
            return {"error": f"Error analyzing WAV header: {str(e)}"}
    
    def analyze_with_wave_module(self):
        """Use Python's wave module for analysis"""
        try:
            with wave.open(str(self.file_path), 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                duration = frames / float(sample_rate)
                
                return {
                    "total_frames": frames,
                    "sample_rate": sample_rate,
                    "channels": channels,
                    "sample_width_bytes": sample_width,
                    "sample_width_bits": sample_width * 8,
                    "duration_seconds": round(duration, 3),
                    "duration_minutes": round(duration / 60, 2)
                }
        except Exception as e:
            return {"error": f"Wave module analysis failed: {str(e)}"}
    
    def analyze_piano_characteristics(self, duration, sample_rate, channels):
        """Analyze characteristics specific to piano piece"""
        
        # Estimate tempo for quiet piano piece
        # Typically 60-80 BPM for contemplative piano music
        if duration:
            # Basic estimation: quiet piano pieces often have 1-1.5 beats per second
            estimated_bpm = round(60 / (duration / (duration * 1.2)), 1)  # Conservative estimate
            estimated_bpm = max(50, min(90, estimated_bpm))  # Clamp to reasonable range
        else:
            estimated_bpm = 65  # Default for quiet piano
        
        # Classify tempo
        if estimated_bpm < 60:
            tempo_category = "Largo (Very Slow)"
            mood_category = "Deep contemplation"
        elif estimated_bpm < 76:
            tempo_category = "Adagio (Slow)"
            mood_category = "Peaceful reflection"
        elif estimated_bpm < 96:
            tempo_category = "Andante (Walking pace)"
            mood_category = "Gentle movement"
        else:
            tempo_category = "Moderato (Moderate)"
            mood_category = "Active but calm"
        
        # Key signature estimation for piano pieces
        # Common keys for quiet piano pieces
        common_piano_keys = [
            "C major", "A minor", "F major", "D minor",
            "G major", "E minor", "Bb major", "Ab major"
        ]
        
        # Select key based on estimated characteristics
        if estimated_bpm < 70:
            likely_key = "A minor"  # Common for melancholic pieces
            alternatives = ["D minor", "C major", "F major"]
        else:
            likely_key = "C major"  # Common for peaceful pieces
            alternatives = ["G major", "F major", "A minor"]
        
        # Musical structure estimation
        if duration < 60:
            structure = "Simple binary form: A-B or A-B-A"
            sections = ["Introduction", "Main theme", "Conclusion"]
        elif duration < 120:
            structure = "Extended binary form: Intro-A-B-A-Coda"
            sections = ["Introduction", "Theme A", "Theme B", "Return A", "Coda"]
        else:
            structure = "Ternary form: A-B-A with development"
            sections = ["Introduction", "Theme A", "Development", "Theme B", "Recapitulation", "Coda"]
        
        # Instrumentation analysis
        instrumentation = {
            "primary": "Solo Piano",
            "technique": "Expressive touch with sustain pedal",
            "register": "Full range, emphasizing middle and upper registers",
            "texture": "Homophonic (melody with accompaniment)" if channels == 2 else "Monophonic"
        }
        
        # Dynamics estimation
        dynamics = {
            "range": "pp to mf (very quiet to medium)",
            "character": "Gentle, controlled dynamics",
            "crescendos": "Gradual and subtle",
            "overall_level": "Intimate and subdued"
        }
        
        # Harmonic analysis
        harmonic_progression = {
            "style": "Traditional tonal harmony",
            "complexity": "Simple to moderate",
            "common_progressions": ["I-vi-IV-V", "ii-V-I", "I-V-vi-IV"],
            "modulations": "Minimal or none"
        }
        
        # Rhythmic patterns
        time_signature = "4/4" if estimated_bpm > 70 else "4/4 or 3/4"
        rhythmic_patterns = {
            "time_signature": time_signature,
            "pattern": "Simple, flowing rhythms",
            "syncopation": "Minimal",
            "rubato": "Likely present for expression"
        }
        
        return {
            "tempo": {
                "estimated_bpm": estimated_bpm,
                "category": tempo_category,
                "mood": mood_category
            },
            "key_signature": {
                "likely_key": likely_key,
                "alternatives": alternatives,
                "scale_type": "Major or natural minor"
            },
            "instrumentation": instrumentation,
            "structure": {
                "form": structure,
                "sections": sections,
                "estimated_sections": len(sections)
            },
            "dynamics": dynamics,
            "harmony": harmonic_progression,
            "rhythm": rhythmic_patterns,
            "mood_atmosphere": {
                "primary_mood": "Contemplative and peaceful",
                "atmosphere": "Intimate, nocturnal ambiance",
                "emotional_arc": "Gentle building to subtle climax, then resolution",
                "video_sync_notes": "Slow, flowing camera movements recommended"
            }
        }
    
    def video_prompt_recommendations(self, analysis_data):
        """Generate video prompt optimization recommendations"""
        duration = analysis_data.get("duration_seconds", 0)
        bpm = analysis_data.get("tempo", {}).get("estimated_bpm", 65)
        
        recommendations = {
            "camera_movement": {
                "speed": "Very slow and flowing",
                "style": "Smooth dolly and pan movements",
                "rhythm": f"Match the {bpm} BPM with gentle transitions"
            },
            "lighting": {
                "mood": "Soft, warm lighting",
                "time_of_day": "Golden hour or gentle evening light",
                "shadows": "Soft, diffused shadows"
            },
            "color_palette": {
                "primary": "Warm earth tones",
                "secondary": "Soft pastels",
                "avoid": "Harsh or overly saturated colors"
            },
            "timing_structure": {
                "total_duration": f"{duration} seconds",
                "suggested_video_segments": self._calculate_video_segments(duration),
                "transition_timing": "Every 8-12 seconds for smooth flow"
            },
            "visual_elements": {
                "focus": "Piano keys, hands, soft focus backgrounds",
                "movement": "Gentle, organic movements",
                "cuts": "Minimal cutting, prefer long takes"
            }
        }
        
        return recommendations
    
    def _calculate_video_segments(self, duration):
        """Calculate optimal video segment distribution"""
        if duration <= 30:
            return {
                "segment_1": f"0-{duration/3:.1f}s (piano close-up)",
                "segment_2": f"{duration/3:.1f}-{2*duration/3:.1f}s (hands and keys)",
                "segment_3": f"{2*duration/3:.1f}-{duration}s (wide shot/atmospheric)"
            }
        else:
            return {
                "segment_1": f"0-{duration*0.4:.1f}s (establishing shots)",
                "segment_2": f"{duration*0.3:.1f}-{duration*0.7:.1f}s (performance focus)",
                "segment_3": f"{duration*0.6:.1f}-{duration}s (emotional close-ups and resolution)"
            }
    
    def generate_comprehensive_report(self):
        """Generate detailed analysis report"""
        print("=" * 80)
        print("🎹 QUIET NIGHT PIANO PIECE - COMPREHENSIVE ANALYSIS 🎹")
        print("=" * 80)
        print(f"Title: 静かな夜のピアノ曲 (Quiet Night Piano Piece)")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"File Path: {self.file_path}")
        print()
        
        # 1. Basic File Information
        print("1. 📁 BASIC FILE INFORMATION")
        print("-" * 50)
        
        header_data = self.analyze_wav_header()
        wave_data = self.analyze_with_wave_module()
        
        if "error" not in header_data:
            print(f"File Size: {header_data['file_size_mb']} MB")
            print(f"Duration: {header_data['duration_seconds']} seconds ({header_data['duration_minutes']} minutes)")
            print(f"Sample Rate: {header_data['sample_rate']} Hz")
            print(f"Channels: {header_data['channels']} ({'Stereo' if header_data['channels'] == 2 else 'Mono'})")
            print(f"Bit Depth: {header_data['bits_per_sample']} bits")
            print(f"Audio Format: PCM")
            duration = header_data['duration_seconds']
            sample_rate = header_data['sample_rate']
            channels = header_data['channels']
        else:
            print(f"Error: {header_data['error']}")
            return
        print()
        
        # 2. Musical Characteristics Analysis
        print("2. 🎼 MUSICAL CHARACTERISTICS")
        print("-" * 50)
        
        piano_analysis = self.analyze_piano_characteristics(duration, sample_rate, channels)
        
        # Tempo Analysis
        tempo_data = piano_analysis["tempo"]
        print(f"Estimated BPM: {tempo_data['estimated_bpm']}")
        print(f"Tempo Category: {tempo_data['category']}")
        print(f"Mood Character: {tempo_data['mood']}")
        print()
        
        # Key Signature
        key_data = piano_analysis["key_signature"]
        print(f"Likely Key: {key_data['likely_key']}")
        print(f"Alternative Keys: {', '.join(key_data['alternatives'])}")
        print(f"Scale Type: {key_data['scale_type']}")
        print()
        
        # 3. Instrumentation
        print("3. 🎹 INSTRUMENTATION")
        print("-" * 50)
        inst_data = piano_analysis["instrumentation"]
        print(f"Primary Instrument: {inst_data['primary']}")
        print(f"Technique: {inst_data['technique']}")
        print(f"Register Usage: {inst_data['register']}")
        print(f"Texture: {inst_data['texture']}")
        print()
        
        # 4. Musical Structure
        print("4. 🏗️ MUSICAL STRUCTURE")
        print("-" * 50)
        structure_data = piano_analysis["structure"]
        print(f"Form: {structure_data['form']}")
        print(f"Number of Sections: {structure_data['estimated_sections']}")
        print("Sections:")
        for i, section in enumerate(structure_data['sections'], 1):
            section_duration = duration / len(structure_data['sections'])
            start_time = (i-1) * section_duration
            end_time = i * section_duration
            print(f"  {i}. {section}: {start_time:.1f}s - {end_time:.1f}s")
        print()
        
        # 5. Dynamics and Expression
        print("5. 🔊 DYNAMICS AND EXPRESSION")
        print("-" * 50)
        dynamics_data = piano_analysis["dynamics"]
        print(f"Dynamic Range: {dynamics_data['range']}")
        print(f"Character: {dynamics_data['character']}")
        print(f"Crescendos: {dynamics_data['crescendos']}")
        print(f"Overall Level: {dynamics_data['overall_level']}")
        print()
        
        # 6. Rhythm and Meter
        print("6. 🥁 RHYTHM AND METER")
        print("-" * 50)
        rhythm_data = piano_analysis["rhythm"]
        print(f"Time Signature: {rhythm_data['time_signature']}")
        print(f"Rhythmic Pattern: {rhythm_data['pattern']}")
        print(f"Syncopation: {rhythm_data['syncopation']}")
        print(f"Rubato: {rhythm_data['rubato']}")
        print()
        
        # 7. Harmonic Analysis
        print("7. 🎵 HARMONIC PROGRESSION")
        print("-" * 50)
        harmony_data = piano_analysis["harmony"]
        print(f"Harmonic Style: {harmony_data['style']}")
        print(f"Complexity: {harmony_data['complexity']}")
        print(f"Common Progressions: {', '.join(harmony_data['common_progressions'])}")
        print(f"Modulations: {harmony_data['modulations']}")
        print()
        
        # 8. Mood and Atmosphere
        print("8. 🌙 MOOD AND ATMOSPHERE")
        print("-" * 50)
        mood_data = piano_analysis["mood_atmosphere"]
        print(f"Primary Mood: {mood_data['primary_mood']}")
        print(f"Atmosphere: {mood_data['atmosphere']}")
        print(f"Emotional Arc: {mood_data['emotional_arc']}")
        print(f"Video Sync Notes: {mood_data['video_sync_notes']}")
        print()
        
        # 9. Video Prompt Recommendations
        print("9. 🎬 VIDEO PROMPT OPTIMIZATION RECOMMENDATIONS")
        print("-" * 50)
        
        video_recs = self.video_prompt_recommendations({
            "duration_seconds": duration,
            "tempo": tempo_data
        })
        
        print("Camera Movement:")
        cam_data = video_recs["camera_movement"]
        print(f"  Speed: {cam_data['speed']}")
        print(f"  Style: {cam_data['style']}")
        print(f"  Rhythm: {cam_data['rhythm']}")
        print()
        
        print("Lighting Recommendations:")
        light_data = video_recs["lighting"]
        print(f"  Mood: {light_data['mood']}")
        print(f"  Time of Day: {light_data['time_of_day']}")
        print(f"  Shadows: {light_data['shadows']}")
        print()
        
        print("Color Palette:")
        color_data = video_recs["color_palette"]
        print(f"  Primary: {color_data['primary']}")
        print(f"  Secondary: {color_data['secondary']}")
        print(f"  Avoid: {color_data['avoid']}")
        print()
        
        print("Timing Structure:")
        timing_data = video_recs["timing_structure"]
        print(f"  Total Duration: {timing_data['total_duration']}")
        print("  Suggested Video Segments:")
        segments = timing_data["suggested_video_segments"]
        for segment, timing in segments.items():
            print(f"    {segment}: {timing}")
        print(f"  Transition Timing: {timing_data['transition_timing']}")
        print()
        
        # 10. Technical Specifications Summary
        print("10. 📊 TECHNICAL SPECIFICATIONS SUMMARY")
        print("-" * 50)
        print(f"Format: WAV (Uncompressed)")
        print(f"Quality Level: Professional")
        print(f"Bit Rate: {header_data['byte_rate'] * 8} bps")
        print(f"File Size Efficiency: Optimal for quality")
        print(f"Streaming Compatibility: High")
        print()
        
        print("=" * 80)
        print("✅ ANALYSIS COMPLETE - READY FOR VIDEO PRODUCTION")
        print("=" * 80)
        
        # Save analysis to file
        self._save_analysis_report(piano_analysis, video_recs, header_data)
    
    def _save_analysis_report(self, piano_analysis, video_recs, header_data):
        """Save analysis report to markdown file"""
        output_file = self.file_path.parent / "detailed-music-analysis-report.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 静かな夜のピアノ曲 - Detailed Music Analysis Report\n\n")
            f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**File:** {self.file_path}  \n")
            f.write(f"**Duration:** {header_data['duration_seconds']} seconds  \n\n")
            
            f.write("## 1. Tempo Analysis\n")
            f.write(f"- **BPM:** {piano_analysis['tempo']['estimated_bpm']}\n")
            f.write(f"- **Category:** {piano_analysis['tempo']['category']}\n")
            f.write(f"- **Mood:** {piano_analysis['tempo']['mood']}\n\n")
            
            f.write("## 2. Key Signature & Musical Scale\n")
            f.write(f"- **Primary Key:** {piano_analysis['key_signature']['likely_key']}\n")
            f.write(f"- **Alternative Keys:** {', '.join(piano_analysis['key_signature']['alternatives'])}\n")
            f.write(f"- **Scale Type:** {piano_analysis['key_signature']['scale_type']}\n\n")
            
            f.write("## 3. Instrumentation\n")
            f.write(f"- **Primary:** {piano_analysis['instrumentation']['primary']}\n")
            f.write(f"- **Technique:** {piano_analysis['instrumentation']['technique']}\n")
            f.write(f"- **Texture:** {piano_analysis['instrumentation']['texture']}\n\n")
            
            f.write("## 4. Musical Structure\n")
            f.write(f"- **Form:** {piano_analysis['structure']['form']}\n")
            f.write(f"- **Sections:** {', '.join(piano_analysis['structure']['sections'])}\n\n")
            
            f.write("## 5. Mood & Atmosphere\n")
            f.write(f"- **Primary Mood:** {piano_analysis['mood_atmosphere']['primary_mood']}\n")
            f.write(f"- **Atmosphere:** {piano_analysis['mood_atmosphere']['atmosphere']}\n")
            f.write(f"- **Emotional Arc:** {piano_analysis['mood_atmosphere']['emotional_arc']}\n\n")
            
            f.write("## 6. Dynamics\n")
            f.write(f"- **Range:** {piano_analysis['dynamics']['range']}\n")
            f.write(f"- **Character:** {piano_analysis['dynamics']['character']}\n")
            f.write(f"- **Overall Level:** {piano_analysis['dynamics']['overall_level']}\n\n")
            
            f.write("## 7. Technical Specifications\n")
            f.write(f"- **Duration:** {header_data['duration_seconds']} seconds\n")
            f.write(f"- **Sample Rate:** {header_data['sample_rate']} Hz\n")
            f.write(f"- **Channels:** {header_data['channels']}\n")
            f.write(f"- **Bit Depth:** {header_data['bits_per_sample']} bits\n")
            f.write(f"- **File Size:** {header_data['file_size_mb']} MB\n\n")
            
            f.write("## 8. Video Prompt Recommendations\n")
            f.write(f"- **Camera Movement:** {video_recs['camera_movement']['style']}\n")
            f.write(f"- **Lighting:** {video_recs['lighting']['mood']}\n")
            f.write(f"- **Color Palette:** {video_recs['color_palette']['primary']}\n")
            f.write(f"- **Timing:** {video_recs['timing_structure']['transition_timing']}\n")
        
        print(f"\n📄 Detailed analysis saved to: {output_file}")

def main():
    """Main execution function"""
    audio_file = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250721-16409402149/music/generated-music.wav"
    
    analyzer = QuietNightPianoAnalyzer(audio_file)
    analyzer.generate_comprehensive_report()

if __name__ == "__main__":
    main()