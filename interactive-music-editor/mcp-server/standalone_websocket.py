#!/usr/bin/env python3
"""
🌐 Standalone WebSocket Server for Music Editor
Separate process for WebSocket communication
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Set, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("standalone-websocket")

class MusicWebSocketServer:
    """Standalone WebSocket server for music editor"""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.music_state = {
            "tracks": {},
            "heatmap": {},
            "playing": False,
            "current_time": 0
        }
        
    async def register(self, websocket):
        """Register new client"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        try:
            # Send welcome message first
            await websocket.send(json.dumps({
                "type": "welcome",
                "message": "🎵 Connected to Music Editor WebSocket!"
            }))
            
            # Send current state
            await websocket.send(json.dumps({
                "type": "state_sync",
                "data": self.music_state,
                "timestamp": datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error sending initial messages: {e}")
        
    async def unregister(self, websocket):
        """Remove client"""
        self.clients.remove(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
        
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast to all clients"""
        if self.clients:
            message["timestamp"] = datetime.now().isoformat()
            json_message = json.dumps(message)
            
            await asyncio.gather(
                *[client.send(json_message) for client in self.clients],
                return_exceptions=True
            )
            logger.info(f"Broadcasted to {len(self.clients)} clients: {message['type']}")
            
    async def handle_client(self, websocket, path):
        """Handle client connection"""
        try:
            await self.register(websocket)
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(data, websocket)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed normally")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            if websocket in self.clients:
                await self.unregister(websocket)
            
    async def process_message(self, data: Dict[str, Any], websocket):
        """Process incoming messages"""
        msg_type = data.get("type")
        
        if msg_type == "ping":
            await websocket.send(json.dumps({"type": "pong"}))
            
        elif msg_type == "update_tracks":
            # Update tracks from external source (MCP server)
            self.music_state["tracks"] = data.get("tracks", {})
            await self.broadcast({
                "type": "tracks_updated",
                "data": self.music_state["tracks"]
            })
            
        elif msg_type == "update_heatmap":
            # Update heatmap from external source
            self.music_state["heatmap"] = data.get("heatmap", {})
            await self.broadcast({
                "type": "heatmap_updated", 
                "data": self.music_state["heatmap"]
            })
            
        elif msg_type == "start_playback":
            # Start playback
            self.music_state["playing"] = True
            self.music_state["current_time"] = 0
            await self.broadcast({
                "type": "playback_updated",
                "data": {
                    "playing": True,
                    "current_time": 0
                }
            })
            
        elif msg_type == "demo_command":
            # Simulate CLI command for testing
            await self.broadcast({
                "type": "command_executed",
                "data": {
                    "command": data.get("command", "test"),
                    "result": "Demo command executed successfully"
                }
            })
            
    async def start_server(self):
        """Start WebSocket server"""
        logger.info(f"🚀 Starting WebSocket server on {self.host}:{self.port}")
        
        start_server = websockets.serve(
            self.handle_client, 
            self.host, 
            self.port
        )
        
        await start_server
        logger.info("✅ WebSocket server running!")
        await asyncio.Future()  # Run forever

async def main():
    """Main entry point"""
    server = MusicWebSocketServer()
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())