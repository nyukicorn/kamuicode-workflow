#!/usr/bin/env python3
"""
🎯 CLI-specific MCP Tools for Interactive Music Editor
Tools specifically designed for CLI/Claude Code integration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from server import InteractiveMusicMCP
    from websocket_server import MusicWebSocketServer

logger = logging.getLogger("cli-tools")

class CLIMusicTools:
    """CLI-specific tools that extend the base MCP server"""
    
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
        self.ws_server = mcp_server.ws_server
        
    def register_cli_tools(self):
        """Register CLI-specific tools"""
        
        @self.mcp_server.app.tool()
        def adjust_volume_cli(
            instruction: str,
            track_name: Optional[str] = None,
            volume: Optional[float] = None
        ) -> Dict[str, Any]:
            """CLI-friendly volume adjustment with natural language"""
            
            instruction_lower = instruction.lower()
            
            # Parse instruction for volume changes
            if "もっと大きく" in instruction or "上げて" in instruction or "louder" in instruction:
                target_volume = 0.9
            elif "小さく" in instruction or "下げて" in instruction or "quieter" in instruction:
                target_volume = 0.3
            elif volume is not None:
                target_volume = volume
            else:
                target_volume = 0.7  # Default
            
            # Parse track name from instruction if not provided
            if track_name is None:
                if "ピアノ" in instruction or "piano" in instruction:
                    track_name = "piano"
                elif "バイオリン" in instruction or "violin" in instruction:
                    track_name = "violin"
                elif "ドラム" in instruction or "drums" in instruction:
                    track_name = "drums"
                elif "ベース" in instruction or "bass" in instruction:
                    track_name = "bass"
                else:
                    # Apply to all tracks
                    for name in self.mcp_server.active_tracks.keys():
                        track = self.mcp_server.active_tracks[name]
                        track["volume"] = target_volume
                    
                    # Notify WebSocket clients
                    if self.ws_server:
                        asyncio.create_task(self.ws_server.update_tracks(self.mcp_server.active_tracks))
                        asyncio.create_task(self.ws_server.send_command_result(
                            instruction, f"All tracks volume set to {target_volume}"
                        ))
                    
                    return {
                        "success": True,
                        "instruction": instruction,
                        "tracks_updated": len(self.mcp_server.active_tracks),
                        "new_volume": target_volume
                    }
            
            # Update specific track
            if track_name in self.mcp_server.active_tracks:
                self.mcp_server.active_tracks[track_name]["volume"] = target_volume
                
                # Notify WebSocket clients
                if self.ws_server:
                    asyncio.create_task(self.ws_server.update_tracks(self.mcp_server.active_tracks))
                    asyncio.create_task(self.ws_server.send_command_result(
                        instruction, f"{track_name} volume set to {target_volume}"
                    ))
                
                return {
                    "success": True,
                    "instruction": instruction,
                    "track_name": track_name,
                    "new_volume": target_volume
                }
            else:
                return {
                    "success": False,
                    "error": f"Track '{track_name}' not found",
                    "available_tracks": list(self.mcp_server.active_tracks.keys())
                }
                
        @self.mcp_server.app.tool()
        def create_music_from_prompt(
            prompt: str,
            style: Optional[str] = None
        ) -> Dict[str, Any]:
            """Create complete music from natural language prompt"""
            
            prompt_lower = prompt.lower()
            
            # Clear existing tracks
            self.mcp_server.active_tracks = {}
            
            # Create tracks based on prompt
            tracks_created = []
            
            # Piano
            if "ピアノ" in prompt or "piano" in prompt or not any(instr in prompt for instr in ["violin", "drums", "bass"]):
                piano_track = {
                    "name": "piano",
                    "instrument": "piano",
                    "volume": 0.7,
                    "pan": 0.0,
                    "notes": [
                        {"note": "C4", "start_time": 0, "duration": 0.5, "velocity": 0.7},
                        {"note": "E4", "start_time": 0.5, "duration": 0.5, "velocity": 0.7},
                        {"note": "G4", "start_time": 1.0, "duration": 0.5, "velocity": 0.7},
                        {"note": "C5", "start_time": 1.5, "duration": 1.0, "velocity": 0.8}
                    ],
                    "effects": []
                }
                self.mcp_server.active_tracks["piano"] = piano_track
                tracks_created.append("piano")
            
            # Violin  
            if "バイオリン" in prompt or "violin" in prompt or "弦楽器" in prompt:
                violin_track = {
                    "name": "violin",
                    "instrument": "violin", 
                    "volume": 0.6,
                    "pan": 0.2,
                    "notes": [
                        {"note": "G4", "start_time": 0.2, "duration": 0.8, "velocity": 0.6},
                        {"note": "A4", "start_time": 1.0, "duration": 0.8, "velocity": 0.6},
                        {"note": "B4", "start_time": 1.8, "duration": 1.0, "velocity": 0.7}
                    ],
                    "effects": []
                }
                self.mcp_server.active_tracks["violin"] = violin_track
                tracks_created.append("violin")
            
            # Style adjustments
            if "ロマンチック" in prompt or "romantic" in prompt:
                for track in self.mcp_server.active_tracks.values():
                    track["volume"] *= 0.8  # Softer
                    
            elif "激しく" in prompt or "dramatic" in prompt:
                for track in self.mcp_server.active_tracks.values():
                    track["volume"] *= 1.2  # Louder
            
            # Generate heatmap
            heatmap = self._generate_heatmap_for_tracks()
            self.mcp_server.heatmap_data = heatmap
            
            # Notify WebSocket clients
            if self.ws_server:
                asyncio.create_task(self.ws_server.update_tracks(self.mcp_server.active_tracks))
                asyncio.create_task(self.ws_server.update_heatmap(heatmap))
                asyncio.create_task(self.ws_server.send_command_result(
                    prompt, f"Created {len(tracks_created)} tracks: {', '.join(tracks_created)}"
                ))
            
            return {
                "success": True,
                "prompt": prompt,
                "tracks_created": tracks_created,
                "track_count": len(tracks_created),
                "heatmap_generated": True
            }
            
        @self.mcp_server.app.tool()
        def start_playback_cli(
            track_names: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """Start music playback via CLI"""
            
            if not self.mcp_server.active_tracks:
                return {
                    "success": False,
                    "error": "No tracks available for playback"
                }
            
            tracks_to_play = track_names or list(self.mcp_server.active_tracks.keys())
            
            # Update playback state
            self.mcp_server.is_playing = True
            self.mcp_server.current_time = 0.0
            
            # Notify WebSocket clients
            if self.ws_server:
                asyncio.create_task(self.ws_server.update_playback(True, 0.0))
                asyncio.create_task(self.ws_server.send_command_result(
                    f"play {tracks_to_play}", "Playback started"
                ))
            
            return {
                "success": True,
                "playing": True,
                "tracks": tracks_to_play,
                "message": "Music playback started - check your web interface!"
            }
            
    def _generate_heatmap_for_tracks(self) -> Dict[str, Any]:
        """Generate heatmap data for current tracks"""
        heatmap = {}
        
        for track_name, track in self.mcp_server.active_tracks.items():
            track_data = []
            
            # Simple heatmap generation (simplified)
            for t in range(50):  # 5 seconds at 0.1s resolution
                current_time = t * 0.1
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
        
        return heatmap

# Function to add CLI tools to existing MCP server
def extend_mcp_with_cli_tools(mcp_server):
    """Add CLI-specific tools to existing MCP server"""
    cli_tools = CLIMusicTools(mcp_server)
    cli_tools.register_cli_tools()
    return cli_tools