#!/usr/bin/env python3
"""
🌐 WebSocket Server for Real-time Browser Updates
Bridges MCP tools and web interface
"""

import asyncio
import json
import logging
import websockets
from typing import Set, Dict, Any
from datetime import datetime

logger = logging.getLogger("websocket-server")

class MusicWebSocketServer:
    """WebSocket server for real-time music editor updates"""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.current_state = {
            "tracks": {},
            "heatmap": {},
            "playing": False,
            "current_time": 0
        }
        
    async def register(self, websocket):
        """Register new client and send current state"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        # Send current state to new client
        await websocket.send(json.dumps({
            "type": "state_sync",
            "data": self.current_state,
            "timestamp": datetime.now().isoformat()
        }))
        
    async def unregister(self, websocket):
        """Remove client on disconnect"""
        self.clients.remove(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
        
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if self.clients:
            message["timestamp"] = datetime.now().isoformat()
            json_message = json.dumps(message)
            
            # Send to all clients
            await asyncio.gather(
                *[client.send(json_message) for client in self.clients],
                return_exceptions=True
            )
            logger.info(f"Broadcasted to {len(self.clients)} clients: {message['type']}")
            
    async def handle_client(self, websocket, path):
        """Handle client connection"""
        await self.register(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process_message(data, websocket)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)
            
    async def process_message(self, data: Dict[str, Any], websocket):
        """Process incoming WebSocket messages"""
        msg_type = data.get("type")
        
        if msg_type == "ping":
            await websocket.send(json.dumps({"type": "pong"}))
            
        elif msg_type == "request_state":
            await websocket.send(json.dumps({
                "type": "state_sync",
                "data": self.current_state
            }))
            
    # MCP Integration Methods
    async def update_tracks(self, tracks: Dict[str, Any]):
        """Update tracks and broadcast to clients"""
        self.current_state["tracks"] = tracks
        await self.broadcast({
            "type": "tracks_updated",
            "data": tracks
        })
        
    async def update_heatmap(self, heatmap: Dict[str, Any]):
        """Update heatmap visualization"""
        self.current_state["heatmap"] = heatmap
        await self.broadcast({
            "type": "heatmap_updated",
            "data": heatmap
        })
        
    async def update_playback(self, is_playing: bool, current_time: float = 0):
        """Update playback state"""
        self.current_state["playing"] = is_playing
        self.current_state["current_time"] = current_time
        await self.broadcast({
            "type": "playback_updated",
            "data": {
                "playing": is_playing,
                "current_time": current_time
            }
        })
        
    async def send_command_result(self, command: str, result: Any):
        """Send CLI command execution result"""
        await self.broadcast({
            "type": "command_executed",
            "data": {
                "command": command,
                "result": result
            }
        })
        
    async def start_server(self):
        """Start WebSocket server"""
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever

# Global server instance
ws_server = None

def get_websocket_server():
    """Get or create WebSocket server instance"""
    global ws_server
    if ws_server is None:
        ws_server = MusicWebSocketServer()
    return ws_server

if __name__ == "__main__":
    # Standalone WebSocket server
    logging.basicConfig(level=logging.INFO)
    server = MusicWebSocketServer()
    asyncio.run(server.start_server())