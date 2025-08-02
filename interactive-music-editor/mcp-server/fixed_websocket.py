#!/usr/bin/env python3
"""
🌐 Fixed WebSocket Server for Music Editor
Compatible with newer websockets library
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fixed-websocket")

# Global state
connected_clients = set()
music_state = {
    "tracks": {},
    "heatmap": {},
    "playing": False,
    "current_time": 0
}

class MusicWebSocketHandler:
    """WebSocket handler class"""
    
    async def __call__(self, websocket):
        """Handle WebSocket connection - new websockets library style"""
        # Register client
        connected_clients.add(websocket)
        logger.info(f"Client connected. Total: {len(connected_clients)}")
        
        try:
            # Send welcome message
            welcome_msg = {
                "type": "welcome",
                "message": "🎵 Connected to Music Editor WebSocket!",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(welcome_msg))
            
            # Send initial state
            state_msg = {
                "type": "state_sync", 
                "data": music_state,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(state_msg))
            
            # Listen for messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"Received: {data}")
                    
                    # Process different message types
                    if data.get("type") == "demo_command":
                        # Broadcast demo response
                        response = {
                            "type": "command_executed",
                            "data": {
                                "command": data.get("command", "unknown"),
                                "result": "Demo command executed successfully!"
                            },
                            "timestamp": datetime.now().isoformat()
                        }
                        await self.broadcast_to_all(response)
                        
                    elif data.get("type") == "start_playback":
                        # Update music state and broadcast
                        music_state["playing"] = True
                        music_state["current_time"] = 0
                        
                        response = {
                            "type": "playback_updated",
                            "data": {
                                "playing": True,
                                "current_time": 0
                            },
                            "timestamp": datetime.now().isoformat()
                        }
                        await self.broadcast_to_all(response)
                        
                    elif data.get("type") == "ping":
                        # Respond to ping
                        await websocket.send(json.dumps({"type": "pong"}))
                        
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected normally")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            # Unregister client
            connected_clients.discard(websocket)
            logger.info(f"Client removed. Remaining: {len(connected_clients)}")

    async def broadcast_to_all(self, message):
        """Broadcast message to all connected clients"""
        if connected_clients:
            message_json = json.dumps(message)
            await asyncio.gather(
                *[client.send(message_json) for client in connected_clients.copy()],
                return_exceptions=True
            )
            logger.info(f"Broadcasted to {len(connected_clients)} clients: {message['type']}")

async def main():
    """Start the WebSocket server"""
    host = "localhost"
    port = 8765
    
    logger.info(f"🚀 Starting WebSocket server on {host}:{port}")
    
    # Create handler instance
    handler = MusicWebSocketHandler()
    
    # Start server with new style
    async with websockets.serve(handler, host, port):
        logger.info("✅ WebSocket server is running!")
        logger.info("Test with Ctrl+T (demo command) or Ctrl+P (playback) in browser")
        
        # Keep running
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")