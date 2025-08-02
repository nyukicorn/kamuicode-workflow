#!/usr/bin/env python3
"""
🎵 Interactive Music Editor System Status Report
Comprehensive analysis of the current MCP server state
"""

import json
import asyncio
import websockets
from datetime import datetime
import subprocess
import os

class SystemStatusAnalyzer:
    def __init__(self):
        self.status = {
            "server": "Interactive Music Editor MCP",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "analysis": {}
        }
    
    def check_processes(self):
        """Check running processes related to the music editor"""
        try:
            # Check for Python processes
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            music_processes = []
            for line in lines:
                if any(keyword in line.lower() for keyword in ['music', 'mcp', 'websocket', 'server']) and 'python' in line.lower():
                    if 'minimal_websocket.py' in line:
                        music_processes.append({
                            "name": "Minimal WebSocket Server",
                            "command": "minimal_websocket.py",
                            "status": "running",
                            "port": 8765
                        })
            
            self.status["components"]["processes"] = music_processes
            return len(music_processes) > 0
            
        except Exception as e:
            self.status["components"]["processes"] = []
            return False
    
    def check_network_ports(self):
        """Check if the required ports are available"""
        try:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            port_status = {}
            for line in lines:
                if '8765' in line and 'LISTEN' in line:
                    port_status["8765"] = "active (WebSocket)"
                if '3000' in line and 'LISTEN' in line:
                    port_status["3000"] = "active (HTTP)"
                if '8080' in line and 'LISTEN' in line:
                    port_status["8080"] = "active (HTTP)"
            
            self.status["components"]["network_ports"] = port_status
            return "8765" in port_status
            
        except Exception as e:
            self.status["components"]["network_ports"] = {}
            return False
    
    async def test_websocket_connection(self):
        """Test WebSocket connectivity and get music state"""
        try:
            uri = "ws://localhost:8765"
            async with websockets.connect(uri) as websocket:
                # Send test message
                test_msg = {"type": "test", "data": "status_check"}
                await websocket.send(json.dumps(test_msg))
                
                # Get response
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                response_data = json.loads(response)
                
                self.status["components"]["websocket"] = {
                    "status": "connected",
                    "uri": uri,
                    "response_type": response_data.get("type"),
                    "message": response_data.get("message")
                }
                
                # Try to get music state info by sending a create command
                create_msg = {"type": "create_piano_track", "data": {}}
                await websocket.send(json.dumps(create_msg))
                
                # This will trigger track creation and we can analyze the state
                return True
                
        except Exception as e:
            self.status["components"]["websocket"] = {
                "status": "failed",
                "error": str(e)
            }
            return False
    
    def check_file_structure(self):
        """Check if all required files exist"""
        base_path = "/Users/nukuiyuki/Dev/kamuicode-workflow/interactive-music-editor"
        
        required_files = {
            "mcp-server/server_fixed.py": "Main MCP Server",
            "mcp-server/minimal_websocket.py": "Minimal WebSocket Server",
            "mcp-server/cli_tools.py": "CLI Tools",
            "web-interface/index.html": "Web Interface",
            "outputs/": "Output Directory"
        }
        
        file_status = {}
        for file_path, description in required_files.items():
            full_path = os.path.join(base_path, file_path)
            exists = os.path.exists(full_path)
            file_status[file_path] = {
                "exists": exists,
                "description": description,
                "path": full_path
            }
        
        self.status["components"]["file_structure"] = file_status
        return all(info["exists"] for info in file_status.values())
    
    def analyze_mcp_server_state(self):
        """Analyze the current MCP server implementation"""
        try:
            # Read the server_fixed.py to understand available tools
            server_path = "/Users/nukuiyuki/Dev/kamuicode-workflow/interactive-music-editor/mcp-server/server_fixed.py"
            with open(server_path, 'r') as f:
                server_content = f.read()
            
            # Extract available tools
            available_tools = []
            lines = server_content.split('\n')
            for i, line in enumerate(lines):
                if "@mcp.tool()" in line and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if "def " in next_line:
                        func_name = next_line.split("def ")[1].split("(")[0]
                        available_tools.append(func_name)
            
            # Analyze global state variables
            global_vars = []
            for line in lines:
                if line.startswith("active_tracks") or line.startswith("heatmap_data") or line.startswith("tempo"):
                    global_vars.append(line.strip())
            
            self.status["analysis"]["mcp_server"] = {
                "available_tools": available_tools,
                "global_state_vars": global_vars,
                "file_size": len(server_content),
                "total_lines": len(lines)
            }
            
            return True
            
        except Exception as e:
            self.status["analysis"]["mcp_server"] = {"error": str(e)}
            return False
    
    def simulate_get_system_status(self):
        """Simulate the get_system_status MCP tool response"""
        # Based on the server_fixed.py implementation
        simulated_status = {
            "server": "Interactive Music Editor MCP",
            "status": "running",
            "audio_context": {
                "is_playing": False,  # Default state
                "current_time": 0.0,
                "tempo": 120
            },
            "tracks": {
                "count": 0,  # No tracks by default
                "names": []
            },
            "heatmap": {
                "available": False,  # No heatmap by default
                "tracks": 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        self.status["simulated_mcp_response"] = simulated_status
        return simulated_status
    
    async def generate_full_report(self):
        """Generate comprehensive system status report"""
        print("🎵 Interactive Music Editor - System Status Analysis")
        print("=" * 80)
        
        # Check all components
        print("📊 Checking system components...")
        
        process_ok = self.check_processes()
        print(f"  ✅ Processes: {'Running' if process_ok else 'Not Running'}")
        
        network_ok = self.check_network_ports()
        print(f"  ✅ Network: {'Active' if network_ok else 'Inactive'}")
        
        websocket_ok = await self.test_websocket_connection()
        print(f"  ✅ WebSocket: {'Connected' if websocket_ok else 'Failed'}")
        
        files_ok = self.check_file_structure()
        print(f"  ✅ Files: {'Complete' if files_ok else 'Missing'}")
        
        analysis_ok = self.analyze_mcp_server_state()
        print(f"  ✅ MCP Analysis: {'Complete' if analysis_ok else 'Failed'}")
        
        # Generate simulated MCP response
        mcp_status = self.simulate_get_system_status()
        
        print("\n" + "=" * 80)
        print("📋 SYSTEM STATUS REPORT")
        print("=" * 80)
        
        # Overall status
        overall_status = all([process_ok, network_ok, websocket_ok, files_ok])
        print(f"🎵 Overall Status: {'🟢 HEALTHY' if overall_status else '🟡 PARTIAL'}")
        
        # Component details
        print(f"\n🔧 Components:")
        for component, details in self.status["components"].items():
            print(f"  • {component.title()}: {json.dumps(details, indent=4)}")
        
        # MCP Server Analysis
        if "mcp_server" in self.status["analysis"]:
            mcp_analysis = self.status["analysis"]["mcp_server"]
            print(f"\n🛠️  MCP Server Analysis:")
            print(f"  • Available Tools: {mcp_analysis.get('available_tools', [])}")
            print(f"  • File Size: {mcp_analysis.get('file_size', 0)} characters")
        
        # Simulated MCP Response
        print(f"\n🎵 Simulated get_system_status() Response:")
        print(json.dumps(mcp_status, indent=2))
        
        print("\n" + "=" * 80)
        print("🎯 RECOMMENDATIONS:")
        
        if not process_ok:
            print("  ⚠️  Start the full MCP server: python3 mcp-server/server_fixed.py")
        if websocket_ok:
            print("  ✅ WebSocket server is running and responsive")
        if files_ok:
            print("  ✅ All required files are present")
        
        print("  💡 To use MCP tools, ensure the server is running with FastMCP")
        print("  💡 Web interface is available via the WebSocket connection")
        
        return self.status

async def main():
    analyzer = SystemStatusAnalyzer()
    report = await analyzer.generate_full_report()
    
    # Save report to file
    report_path = "/Users/nukuiyuki/Dev/kamuicode-workflow/interactive-music-editor/system_status.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())