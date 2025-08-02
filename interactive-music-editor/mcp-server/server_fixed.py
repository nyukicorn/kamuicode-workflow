#!/usr/bin/env python3
"""
🎵 Interactive Music Editor MCP Server (Fixed)
Correct FastMCP implementation for Claude Code
"""

import asyncio
import json
import logging
import websockets
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# FastMCP for server implementation
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("interactive-music-mcp")

# Create FastMCP instance (globally)
mcp = FastMCP("Interactive Music Editor")

# Global state
active_tracks = {}
heatmap_data = {}
tempo = 120
key_signature = "C"
time_signature = "4/4"
is_playing = False
current_time = 0.0

# WebSocket notification function
async def notify_websocket(message_type: str, data: Any):
    """外部WebSocketサーバーに通知を送信"""
    try:
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(message))
            logger.info(f"📡 Sent to WebSocket: {message_type}")
            
    except Exception as e:
        logger.warning(f"⚠️  WebSocket notification failed: {e}")

# Music creation tools
@mcp.tool()
def create_music_track(
    track_name: str,
    instrument: str = "piano",
    volume: float = 0.7,
    pan: float = 0.0
) -> Dict[str, Any]:
    """Create a new music track with specified parameters"""
    global active_tracks
    
    track = {
        "name": track_name,
        "instrument": instrument,
        "volume": volume,
        "pan": pan,
        "notes": [],
        "effects": [],
        "created_at": datetime.now().isoformat()
    }
    
    active_tracks[track_name] = track
    logger.info(f"🎼 Created track: {track_name} ({instrument})")
    
    # Notify WebSocket clients
    asyncio.create_task(notify_websocket("tracks_updated", active_tracks))
    
    return {
        "success": True,
        "track": track,
        "total_tracks": len(active_tracks)
    }

@mcp.tool()
def add_notes_to_track(
    track_name: str,
    notes: List[str],
    timing: List[float],
    durations: List[float],
    velocities: Optional[List[float]] = None
) -> Dict[str, Any]:
    """Add notes to an existing track"""
    global active_tracks
    
    if track_name not in active_tracks:
        return {"success": False, "error": f"Track '{track_name}' not found"}
    
    if velocities is None:
        velocities = [0.7] * len(notes)
    
    # Validate input lengths
    if not (len(notes) == len(timing) == len(durations) == len(velocities)):
        return {"success": False, "error": "All arrays must have same length"}
    
    track = active_tracks[track_name]
    for i, note in enumerate(notes):
        note_data = {
            "note": note,
            "start_time": timing[i],
            "duration": durations[i],
            "velocity": velocities[i]
        }
        track["notes"].append(note_data)
    
    logger.info(f"🎵 Added {len(notes)} notes to track: {track_name}")
    
    # Notify WebSocket clients
    asyncio.create_task(notify_websocket("tracks_updated", active_tracks))
    
    return {
        "success": True,
        "notes_added": len(notes),
        "total_notes": len(track["notes"])
    }

@mcp.tool()
def generate_heatmap_data(
    time_resolution: float = 0.1,
    duration: float = 30.0
) -> Dict[str, Any]:
    """Generate heatmap visualization data for all tracks"""
    global active_tracks, heatmap_data
    
    time_points = int(duration / time_resolution)
    heatmap = {}
    
    for track_name, track in active_tracks.items():
        track_data = []
        
        for t in range(time_points):
            current_time_point = t * time_resolution
            volume = 0.0
            is_playing = False
            
            # Check if any note is playing at this time
            for note in track["notes"]:
                start = note["start_time"]
                end = start + note["duration"]
                
                if start <= current_time_point <= end:
                    volume = max(volume, note["velocity"] * track["volume"])
                    is_playing = True
            
            track_data.append({
                "time": current_time_point,
                "volume": volume,
                "is_playing": is_playing,
                "opacity": min(volume, 1.0)
            })
        
        heatmap[track_name] = {
            "instrument": track["instrument"],
            "data": track_data
        }
    
    heatmap_data = heatmap
    logger.info(f"🔥 Generated heatmap data for {len(heatmap)} tracks")
    
    # Notify WebSocket clients
    asyncio.create_task(notify_websocket("heatmap_updated", heatmap))
    
    return {
        "success": True,
        "heatmap": heatmap,
        "duration": duration,
        "resolution": time_resolution,
        "time_points": time_points
    }

@mcp.tool()
def natural_language_to_dsl(
    instruction: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """Convert natural language instruction to music DSL code"""
    
    # Simple rule-based conversion
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
    
    # Notify WebSocket clients
    asyncio.create_task(notify_websocket("command_executed", {
        "command": f"natural_language_to_dsl: {instruction}",
        "result": f"Generated DSL: {dsl_code[:50]}..."
    }))
    
    return {
        "success": True,
        "instruction": instruction,
        "dsl_code": dsl_code,
        "context": context
    }

@mcp.tool()
def create_music_from_prompt(
    prompt: str,
    style: Optional[str] = None
) -> Dict[str, Any]:
    """Create complete music from natural language prompt"""
    global active_tracks, heatmap_data
    
    prompt_lower = prompt.lower()
    
    # Clear existing tracks
    active_tracks = {}
    
    # Create tracks based on prompt
    tracks_created = []
    
    # Piano
    if "ピアノ" in prompt or "piano" in prompt:
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
        active_tracks["piano"] = piano_track
        tracks_created.append("piano")
    
    # Violin  
    if "バイオリン" in prompt or "violin" in prompt:
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
        active_tracks["violin"] = violin_track
        tracks_created.append("violin")
    
    # Style adjustments
    if "ロマンチック" in prompt or "romantic" in prompt:
        for track in active_tracks.values():
            track["volume"] *= 0.8  # Softer
            
    elif "激しく" in prompt or "dramatic" in prompt:
        for track in active_tracks.values():
            track["volume"] *= 1.2  # Louder
    
    # Generate heatmap
    heatmap = _generate_heatmap_for_tracks()
    heatmap_data = heatmap
    
    # Notify WebSocket clients
    asyncio.create_task(notify_websocket("tracks_updated", active_tracks))
    asyncio.create_task(notify_websocket("heatmap_updated", heatmap))
    asyncio.create_task(notify_websocket("command_executed", {
        "command": f"create_music_from_prompt: {prompt}",
        "result": f"Created {len(tracks_created)} tracks: {', '.join(tracks_created)}"
    }))
    
    return {
        "success": True,
        "prompt": prompt,
        "tracks_created": tracks_created,
        "track_count": len(tracks_created),
        "heatmap_generated": True
    }

@mcp.tool()
def get_system_status() -> Dict[str, Any]:
    """Get current system status and statistics"""
    global active_tracks, heatmap_data, is_playing, current_time, tempo
    
    return {
        "server": "Interactive Music Editor MCP",
        "status": "running",
        "audio_context": {
            "is_playing": is_playing,
            "current_time": current_time,
            "tempo": tempo
        },
        "tracks": {
            "count": len(active_tracks),
            "names": list(active_tracks.keys())
        },
        "heatmap": {
            "available": bool(heatmap_data),
            "tracks": len(heatmap_data)
        },
        "timestamp": datetime.now().isoformat()
    }

def _generate_heatmap_for_tracks() -> Dict[str, Any]:
    """Generate heatmap data for current tracks"""
    global active_tracks
    
    heatmap = {}
    
    for track_name, track in active_tracks.items():
        track_data = []
        
        # Simple heatmap generation
        for t in range(50):  # 5 seconds at 0.1s resolution
            current_time_point = t * 0.1
            volume = 0.0
            is_playing = False
            
            # Check if any note is playing at this time
            for note in track["notes"]:
                start = note["start_time"]
                end = start + note["duration"]
                
                if start <= current_time_point <= end:
                    volume = max(volume, note["velocity"] * track["volume"])
                    is_playing = True
            
            track_data.append({
                "time": current_time_point,
                "volume": volume,
                "is_playing": is_playing,
                "opacity": min(volume, 1.0)
            })
        
        heatmap[track_name] = {
            "instrument": track["instrument"],
            "data": track_data
        }
    
    return heatmap

if __name__ == "__main__":
    logger.info("🎵 Starting Interactive Music Editor MCP Server...")
    mcp.run()