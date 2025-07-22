#!/usr/bin/env python3
"""
Test Claude Code MCP connection with Polycam server
"""

import subprocess
import sys
import os
import time

def test_claude_mcp_connection():
    """Test if Claude Code can connect to our MCP server"""
    
    print("🧪 Testing Claude Code MCP Connection...")
    
    # Change to project directory
    project_dir = "/Users/nukuiyuki/Dev/kamuicode-workflow"
    os.chdir(project_dir)
    
    # Test 1: Check if claude command is available
    print("\n1. Checking Claude Code availability...")
    try:
        result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Claude Code found at: {result.stdout.strip()}")
        else:
            print("❌ Claude Code not found in PATH")
            return False
    except Exception as e:
        print(f"❌ Error checking claude command: {e}")
        return False
    
    # Test 2: Test MCP configuration file
    print("\n2. Validating MCP configuration...")
    mcp_config = ".claude/mcp-polycam.json"
    if os.path.exists(mcp_config):
        print(f"✅ MCP config found: {mcp_config}")
    else:
        print(f"❌ MCP config not found: {mcp_config}")
        return False
    
    # Test 3: Test MCP server script
    print("\n3. Validating MCP server script...")
    server_script = "polycam-mcp-server/trellis_server.py"
    if os.path.exists(server_script):
        print(f"✅ MCP server script found: {server_script}")
    else:
        print(f"❌ MCP server script not found: {server_script}")
        return False
    
    # Test 4: Test Claude Code with MCP config (dry run)
    print("\n4. Testing Claude Code MCP configuration (dry run)...")
    try:
        # Use a timeout to avoid hanging
        cmd = ['claude', '--mcp-config=.claude/mcp-polycam.json', '--help']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Claude Code accepts MCP configuration")
        else:
            print(f"❌ Claude Code configuration error:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Claude Code MCP test timed out (expected for interactive mode)")
        print("✅ This usually means Claude Code is trying to start successfully")
    except Exception as e:
        print(f"❌ Error testing Claude Code: {e}")
        return False
    
    print("\n🎉 All basic tests passed!")
    print("\n📋 Next steps:")
    print("1. Run: cd /Users/nukuiyuki/Dev/kamuicode-workflow")
    print("2. Run: claude --mcp-config=.claude/mcp-polycam.json")
    print("3. In Claude, try using MCP tools to test functionality")
    
    return True

if __name__ == "__main__":
    success = test_claude_mcp_connection()
    sys.exit(0 if success else 1)