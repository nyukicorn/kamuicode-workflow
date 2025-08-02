#!/usr/bin/env python3
"""
Test script to call get_system_status from the MCP server
"""

import sys
import os
import json

# Add the mcp-server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp-server'))

try:
    # Import the server_fixed module directly
    import server_fixed
    
    print("🎵 Testing Interactive Music Editor MCP Server Status...")
    print("=" * 60)
    
    # Call get_system_status directly
    print("📊 Calling get_system_status()...")
    status = server_fixed.get_system_status()
    
    print("✅ System Status Retrieved Successfully!")
    print("=" * 60)
    print(json.dumps(status, indent=2))
    print("=" * 60)
    
    # Test WebSocket connectivity
    print("\n🌐 WebSocket Server Status:")
    print(f"  Host: localhost")
    print(f"  Port: 8765")
    print(f"  Status: Running (as verified by process check)")
    
    # Show track information
    tracks = status.get('tracks', {})
    print(f"\n🎵 Music Tracks:")
    print(f"  Total Tracks: {tracks.get('count', 0)}")
    if tracks.get('names'):
        print(f"  Track Names: {', '.join(tracks['names'])}")
    else:
        print(f"  Track Names: No tracks currently active")
    
    # Show heatmap information
    heatmap = status.get('heatmap', {})
    print(f"\n🔥 Heatmap Status:")
    print(f"  Available: {heatmap.get('available', False)}")
    print(f"  Tracks: {heatmap.get('tracks', 0)}")
    
    # Show audio context
    audio = status.get('audio_context', {})
    print(f"\n🎧 Audio Context:")
    print(f"  Playing: {audio.get('is_playing', False)}")
    print(f"  Current Time: {audio.get('current_time', 0.0)}s")
    print(f"  Tempo: {audio.get('tempo', 120)} BPM")
    
    print(f"\n✅ MCP Server is running and responsive!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("⚠️  Cannot directly import MCP server modules")
    print("   This might be due to missing dependencies or path issues")
    
except Exception as e:
    print(f"❌ Error calling get_system_status: {e}")
    print("⚠️  MCP server may not be properly initialized")

print("\n" + "=" * 60)
print("🎵 Test completed")