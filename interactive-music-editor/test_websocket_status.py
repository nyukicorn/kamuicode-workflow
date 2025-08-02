#!/usr/bin/env python3
"""
Test WebSocket connection and try to get status from the MCP server
"""

import asyncio
import json
import websockets
from datetime import datetime

async def test_mcp_websocket():
    """Test WebSocket connection and try to get system status"""
    
    print("🎵 Testing Interactive Music Editor WebSocket Connection...")
    print("=" * 60)
    
    try:
        uri = "ws://localhost:8765"
        print(f"🌐 Connecting to: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Test 1: Send a basic test message
            print("\n📤 Test 1: Sending basic test message...")
            test_message = {
                "type": "test",
                "data": "connection_test",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(test_message))
            
            # Receive response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                print(f"📥 Response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received (timeout)")
            
            # Test 2: Try to request system status
            print("\n📤 Test 2: Requesting system status...")
            status_request = {
                "type": "get_system_status",
                "data": {},
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(status_request))
            
            # Receive response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                print(f"📥 Status Response: {response}")
                
                # Try to parse as JSON
                try:
                    status_data = json.loads(response)
                    print("\n📊 Parsed Status Data:")
                    print(json.dumps(status_data, indent=2))
                except json.JSONDecodeError:
                    print("⚠️  Response is not valid JSON")
                    
            except asyncio.TimeoutError:
                print("⏰ No status response received (timeout)")
            
            # Test 3: Try MCP-style tool call
            print("\n📤 Test 3: Trying MCP-style tool call...")
            mcp_request = {
                "type": "tool_call",
                "tool": "get_system_status",
                "args": {},
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(mcp_request))
            
            # Receive response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                print(f"📥 MCP Response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No MCP response received (timeout)")
            
            # Test 4: Send demo command
            print("\n📤 Test 4: Sending demo music creation command...")
            demo_request = {
                "type": "create_music",
                "data": {
                    "prompt": "Create a simple piano melody",
                    "style": "gentle"
                },
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(demo_request))
            
            # Receive response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                print(f"📥 Music Creation Response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No music creation response received (timeout)")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused - WebSocket server is not running")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    
    print("\n" + "=" * 60)
    print("🌐 WebSocket test completed")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_mcp_websocket())