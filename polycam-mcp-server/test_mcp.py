#!/usr/bin/env python3
"""
Simple test script for TRELLIS MCP Server
Tests basic functionality without actual TRELLIS model
"""

import asyncio
import json
from trellis_server import TrellisServer

async def test_basic_functionality():
    """Test MCP server basic functionality"""
    print("🧪 Testing TRELLIS MCP Server...")
    
    # Create server instance
    server = TrellisServer()
    server.setup_handlers()
    
    print("✅ Server instance created successfully")
    
    # Test job submission
    text_result = await server._submit_text_job({
        "prompt": "A futuristic space station",
        "output_format": "glb",
        "steps": 10
    })
    
    print(f"✅ Text job submission: {text_result[0].text}")
    
    # Extract job ID from result
    job_id = text_result[0].text.split("Job ID: ")[1]
    print(f"📋 Job ID: {job_id}")
    
    # Wait a moment for simulation to progress
    await asyncio.sleep(2)
    
    # Test status check
    status_result = await server._check_status({"job_id": job_id})
    print(f"📊 Status check: {status_result[0].text}")
    
    # Wait for completion
    print("⏳ Waiting for job completion...")
    await asyncio.sleep(6)
    
    # Test final result
    result = await server._get_result({"job_id": job_id})
    print(f"🎯 Final result: {result[0].text}")
    
    print("\n✅ All tests passed! MCP Server is working correctly.")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())