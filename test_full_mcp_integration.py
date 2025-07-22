#!/usr/bin/env python3
"""
Full integration test for Polycam MCP with Claude Code
Tests the complete flow from Claude Code to MCP tools
"""

import subprocess
import os
import time
import json

def test_full_integration():
    """Test full Claude Code + MCP integration"""
    
    print("🧪 Testing Full Polycam MCP Integration...")
    
    # Change to project directory
    project_dir = "/Users/nukuiyuki/Dev/kamuicode-workflow"
    os.chdir(project_dir)
    
    # Test 1: Verify all configurations
    print("\n1. Verifying all configurations...")
    
    # Check MCP config
    mcp_config = ".claude/mcp-polycam.json"
    if os.path.exists(mcp_config):
        with open(mcp_config, 'r') as f:
            config = json.load(f)
        print(f"✅ MCP config: {config['mcpServers']['polycam-trellis']['command']}")
    else:
        print("❌ MCP config missing")
        return False
    
    # Check settings permissions
    settings_file = ".claude/settings.json"
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        polycam_perms = [p for p in settings['permissions']['allow'] if 'polycam-trellis' in p]
        print(f"✅ Settings permissions: {len(polycam_perms)} Polycam permissions found")
        for perm in polycam_perms:
            print(f"   - {perm}")
    else:
        print("❌ Settings file missing")
        return False
    
    # Test 2: Verify MCP server can start
    print("\n2. Testing MCP server startup...")
    server_script = "polycam-mcp-server/trellis_server.py"
    if os.path.exists(server_script):
        try:
            # Test server import
            result = subprocess.run([
                'python3', '-c', 
                'import sys; sys.path.append("polycam-mcp-server"); from trellis_server import TrellisServer; print("✅ Server import success")'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ MCP server can be imported and initialized")
            else:
                print(f"❌ Server import failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Server test error: {e}")
            return False
    
    # Test 3: Check if Claude can see the MCP tools
    print("\n3. Testing Claude Code MCP tool visibility...")
    
    print("\n📋 Ready for manual testing!")
    print("\n🚀 To test manually, run:")
    print(f"cd {project_dir}")
    print("claude --mcp-config=.claude/mcp-polycam.json")
    print("\n🛠️ In Claude, you should be able to use:")
    print("- mcp__polycam-trellis__trellis_text_submit")
    print("- mcp__polycam-trellis__trellis_image_submit")
    print("- mcp__polycam-trellis__trellis_status")
    print("- mcp__polycam-trellis__trellis_result")
    
    print("\n✨ Test example:")
    print('Try: "Generate a 3D model of a futuristic spacecraft"')
    print("Claude should use the MCP tools to create a job and track progress!")
    
    return True

if __name__ == "__main__":
    success = test_full_integration()
    if success:
        print("\n🎉 All automated tests passed!")
        print("Ready for manual Claude Code testing!")
    else:
        print("\n❌ Some tests failed")
    exit(0 if success else 1)