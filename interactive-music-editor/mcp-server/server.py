#!/usr/bin/env python3
"""
🎵 Interactive Music Editor MCP Server
Web Audio API Integration for Real-time Music Creation

Features:
- Live coding music generation
- Real-time heatmap visualization  
- Natural language to music DSL conversion
- Audio analysis and effects
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# FastMCP for server implementation
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("interactive-music-mcp")

class InteractiveMusicMCP:
    """Interactive Music Editor MCP Server"""
    
    def __init__(self):
        self.app = FastMCP("Interactive Music Editor")
        self.project_root = Path(__file__).parent.parent
        self.output_dir = self.project_root / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        # Music state
        self.current_composition = None
        self.active_tracks = {}
        self.heatmap_data = {}
        self.tempo = 120
        self.key_signature = "C"
        self.time_signature = "4/4"
        
        # Audio engine state
        self.audio_context = None
        self.is_playing = False
        self.current_time = 0.0
        
        # Register tools
        self._register_tools()
        
        logger.info("🎵 Interactive Music Editor MCP Server initialized")
    
    def _register_tools(self):
        """Register all MCP tools"""
        
        @self.app.tool()
        def create_music_track(
            track_name: str,
            instrument: str = "piano",
            volume: float = 0.7,
            pan: float = 0.0
        ) -> Dict[str, Any]:
            """Create a new music track with specified parameters"""
            track = {
                "name": track_name,
                "instrument": instrument,
                "volume": volume,
                "pan": pan,
                "notes": [],
                "effects": [],
                "created_at": datetime.now().isoformat()
            }
            
            self.active_tracks[track_name] = track
            logger.info(f"🎼 Created track: {track_name} ({instrument})")
            
            return {
                "success": True,
                "track": track,
                "total_tracks": len(self.active_tracks)
            }
        
        @self.app.tool()
        def add_notes_to_track(
            track_name: str,
            notes: List[str],
            timing: List[float],
            durations: List[float],
            velocities: Optional[List[float]] = None
        ) -> Dict[str, Any]:
            """Add notes to an existing track"""
            if track_name not in self.active_tracks:
                return {"success": False, "error": f"Track '{track_name}' not found"}
            
            if velocities is None:
                velocities = [0.7] * len(notes)
            
            # Validate input lengths
            if not (len(notes) == len(timing) == len(durations) == len(velocities)):
                return {"success": False, "error": "All arrays must have same length"}
            
            track = self.active_tracks[track_name]
            for i, note in enumerate(notes):
                note_data = {
                    "note": note,
                    "start_time": timing[i],
                    "duration": durations[i],
                    "velocity": velocities[i]
                }
                track["notes"].append(note_data)
            
            logger.info(f"🎵 Added {len(notes)} notes to track: {track_name}")
            
            return {
                "success": True,
                "notes_added": len(notes),
                "total_notes": len(track["notes"])
            }
        
        @self.app.tool()
        def generate_heatmap_data(
            time_resolution: float = 0.1,
            duration: float = 30.0
        ) -> Dict[str, Any]:
            """Generate heatmap visualization data for all tracks"""
            
            time_points = int(duration / time_resolution)
            heatmap = {}
            
            for track_name, track in self.active_tracks.items():
                track_data = []
                
                for t in range(time_points):
                    current_time = t * time_resolution
                    volume = 0.0
                    is_playing = False
                    
                    # Check if any note is playing at this time
                    for note in track["notes"]:
                        start = note["start_time"]
                        end = start + note["duration"]
                        
                        if start <= current_time <= end:
                            volume = max(volume, note["velocity"] * track["volume"])
                            is_playing = True
                    
                    track_data.append({
                        "time": current_time,
                        "volume": volume,
                        "is_playing": is_playing,
                        "opacity": min(volume, 1.0)
                    })
                
                heatmap[track_name] = {
                    "instrument": track["instrument"],
                    "data": track_data
                }
            
            self.heatmap_data = heatmap
            logger.info(f"🔥 Generated heatmap data for {len(heatmap)} tracks")
            
            return {
                "success": True,
                "heatmap": heatmap,
                "duration": duration,
                "resolution": time_resolution,
                "time_points": time_points
            }
        
        @self.app.tool()
        def parse_music_dsl(
            dsl_code: str
        ) -> Dict[str, Any]:
            """Parse music DSL code into executable commands"""
            
            # Simple DSL parser (expandable)
            commands = []
            lines = dsl_code.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                    
                # Basic pattern matching
                if '.track(' in line:
                    # Extract track creation
                    try:
                        # Simple regex-like parsing
                        parts = line.split('.track(')[1].split(')')[0]
                        track_name = parts.strip('\'"')
                        commands.append({
                            "type": "create_track",
                            "params": {"track_name": track_name}
                        })
                    except:
                        pass
                
                elif '.play(' in line:
                    # Extract note playing
                    try:
                        parts = line.split('.play(')[1].split(')')[0]
                        notes = eval(parts)  # Careful with eval in production
                        commands.append({
                            "type": "play_notes", 
                            "params": {"notes": notes}
                        })
                    except:
                        pass
            
            logger.info(f"🔧 Parsed DSL: {len(commands)} commands")
            
            return {
                "success": True,
                "commands": commands,
                "original_code": dsl_code
            }
        
        @self.app.tool()
        def natural_language_to_dsl(
            instruction: str,
            context: Optional[str] = None
        ) -> Dict[str, Any]:
            """Convert natural language instruction to music DSL code"""
            
            # Simple rule-based conversion (expandable with AI)
            dsl_code = ""
            
            instruction_lower = instruction.lower()
            
            # Pattern matching for common instructions
            if "create" in instruction_lower and "piano" in instruction_lower:
                dsl_code += "track('piano').instrument('grand_piano')\n"
                
            if "add" in instruction_lower and "notes" in instruction_lower:
                dsl_code += ".play(['C4', 'E4', 'G4']).timing([0, 1, 2])\n"
                
            if "volume" in instruction_lower:
                if "louder" in instruction_lower or "up" in instruction_lower:
                    dsl_code += ".volume(0.9)\n"
                elif "quieter" in instruction_lower or "down" in instruction_lower:
                    dsl_code += ".volume(0.3)\n"
                    
            if "romantic" in instruction_lower:
                dsl_code += ".reverb(0.4).warmth(0.6)\n"
                
            if "dramatic" in instruction_lower:
                dsl_code += ".volume(0.9).crescendo(2.0)\n"
            
            logger.info(f"🤖 NL→DSL: '{instruction}' → DSL code")
            
            return {
                "success": True,
                "instruction": instruction,
                "dsl_code": dsl_code,
                "context": context
            }
        
        @self.app.tool()
        def export_composition(
            format: str = "json",
            include_heatmap: bool = True
        ) -> Dict[str, Any]:
            """Export current composition to specified format"""
            
            composition = {
                "metadata": {
                    "tempo": self.tempo,
                    "key_signature": self.key_signature,
                    "time_signature": self.time_signature,
                    "created_at": datetime.now().isoformat()
                },
                "tracks": self.active_tracks,
                "heatmap": self.heatmap_data if include_heatmap else None
            }
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"composition_{timestamp}.{format}"
            filepath = self.output_dir / filename
            
            if format == "json":
                with open(filepath, 'w') as f:
                    json.dump(composition, f, indent=2)
            
            logger.info(f"💾 Exported composition: {filename}")
            
            return {
                "success": True,
                "filepath": str(filepath),
                "format": format,
                "tracks_count": len(self.active_tracks),
                "composition": composition
            }
        
        @self.app.tool()
        def get_system_status() -> Dict[str, Any]:
            """Get current system status and statistics"""
            
            return {
                "server": "Interactive Music Editor MCP",
                "status": "running",
                "audio_context": {
                    "is_playing": self.is_playing,
                    "current_time": self.current_time,
                    "tempo": self.tempo
                },
                "tracks": {
                    "count": len(self.active_tracks),
                    "names": list(self.active_tracks.keys())
                },
                "heatmap": {
                    "available": bool(self.heatmap_data),
                    "tracks": len(self.heatmap_data)
                },
                "output_directory": str(self.output_dir),
                "timestamp": datetime.now().isoformat()
            }

def main():
    """Main entry point"""
    server = InteractiveMusicMCP()
    
    # Run the server
    logger.info("🚀 Starting Interactive Music Editor MCP Server...")
    server.app.run()

if __name__ == "__main__":
    main()