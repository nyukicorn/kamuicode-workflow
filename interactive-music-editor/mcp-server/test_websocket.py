#!/usr/bin/env python3
"""
🧪 Simple WebSocket Test Server
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-websocket")

async def handle_client(websocket, path):
    """Handle WebSocket client connections"""
    logger.info(f"New client connected: {websocket.remote_address}")
    
    try:
        # Send welcome message
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": "🎵 Test WebSocket Server Connected!"
        }))
        
        # Listen for messages
        async for message in websocket:
            data = json.loads(message)
            logger.info(f"Received: {data}")
            
            # Echo back
            await websocket.send(json.dumps({
                "type": "echo",
                "original": data,
                "response": "Message received!"
            }))
            
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")

async def main():
    """Start test WebSocket server"""
    logger.info("🚀 Starting test WebSocket server on localhost:8765...")
    
    async with websockets.serve(handle_client, "localhost", 8765):
        logger.info("✅ Test WebSocket server running!")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())