#!/usr/bin/env python3
"""
🌐 Minimal WebSocket Server for Music Editor  
Ultra-simple version to avoid compatibility issues
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("minimal-websocket")

connected_clients = set()

# 音楽状態管理
music_state = {
    "tracks": {},
    "heatmap": {},
    "playing": False
}

async def echo_server(websocket):
    """Minimal WebSocket echo server"""
    connected_clients.add(websocket)
    logger.info(f"🔗 Client connected. Total: {len(connected_clients)}")
    
    try:
        # Send welcome
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": "🎵 Minimal WebSocket Connected!"
        }))
        
        # Echo messages
        async for message in websocket:
            logger.info(f"📨 Received: {message}")
            
            # Parse and respond
            try:
                data = json.loads(message)
                msg_type = data.get('type')
                
                # 音楽機能の処理
                if msg_type == 'create_piano_track':
                    # ピアノトラック作成
                    music_state["tracks"]["piano"] = {
                        "instrument": "piano",
                        "notes": [
                            {"note": "C4", "start_time": 0, "duration": 0.5, "velocity": 0.7},
                            {"note": "E4", "start_time": 0.5, "duration": 0.5, "velocity": 0.7},
                            {"note": "G4", "start_time": 1.0, "duration": 0.5, "velocity": 0.7},
                            {"note": "C5", "start_time": 1.5, "duration": 1.0, "velocity": 0.8}
                        ],
                        "volume": 0.7
                    }
                    
                    # ヒートマップ生成
                    heatmap = generate_heatmap()
                    music_state["heatmap"] = heatmap
                    
                    # 全クライアントに送信
                    await broadcast_to_all({
                        "type": "tracks_updated",
                        "data": music_state["tracks"]
                    })
                    await broadcast_to_all({
                        "type": "heatmap_updated",
                        "data": heatmap
                    })
                    
                elif msg_type == 'adjust_volume':
                    # 音量調整
                    track_name = data.get('track', 'piano')
                    new_volume = data.get('volume', 0.7)
                    
                    if track_name in music_state["tracks"]:
                        music_state["tracks"][track_name]["volume"] = new_volume
                        
                        await broadcast_to_all({
                            "type": "tracks_updated",
                            "data": music_state["tracks"]
                        })
                        await broadcast_to_all({
                            "type": "command_executed",
                            "data": {
                                "command": f"adjust_volume {track_name} {new_volume}",
                                "result": f"Volume set to {new_volume}"
                            }
                        })
                
                elif msg_type == 'start_playback':
                    # 再生開始
                    music_state["playing"] = True
                    await broadcast_to_all({
                        "type": "playback_updated",
                        "data": {"playing": True, "current_time": 0}
                    })
                
                else:
                    # 既存のエコー処理
                    response = {
                        "type": "echo",
                        "original": data,
                        "message": f"Received {data.get('type', 'unknown')} command"
                    }
                    await websocket.send(json.dumps(response))
                    
                    # Broadcast to other clients
                    if len(connected_clients) > 1:
                        broadcast_msg = {
                            "type": "broadcast",
                            "data": data,
                            "message": "Message from another client"
                        }
                        for client in connected_clients:
                            if client != websocket:
                                try:
                                    await client.send(json.dumps(broadcast_msg))
                                except:
                                    pass
                                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON"
                }))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("🔌 Client disconnected")
    finally:
        connected_clients.discard(websocket)
        logger.info(f"👋 Client removed. Remaining: {len(connected_clients)}")

async def broadcast_to_all(message):
    """全クライアントにメッセージを送信"""
    if connected_clients:
        message_json = json.dumps(message)
        await asyncio.gather(
            *[client.send(message_json) for client in connected_clients.copy()],
            return_exceptions=True
        )
        logger.info(f"📢 Broadcasted to {len(connected_clients)} clients: {message['type']}")

def generate_heatmap():
    """ヒートマップデータ生成"""
    heatmap = {}
    for track_name, track in music_state["tracks"].items():
        track_data = []
        for t in range(50):  # 5秒間
            current_time = t * 0.1
            volume = 0.0
            
            # 音符の再生チェック
            for note in track["notes"]:
                start = note["start_time"]
                end = start + note["duration"]
                if start <= current_time <= end:
                    volume = max(volume, note["velocity"] * track["volume"])
            
            track_data.append({
                "time": current_time,
                "volume": volume,
                "opacity": min(volume, 1.0)
            })
        
        heatmap[track_name] = {
            "instrument": track["instrument"],
            "data": track_data
        }
    
    return heatmap

async def main():
    """Start minimal server"""
    logger.info("🚀 Starting minimal WebSocket server on localhost:8765")
    
    async with websockets.serve(echo_server, "localhost", 8765):
        logger.info("✅ Server running! Test with browser...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())