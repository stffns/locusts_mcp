#!/usr/bin/env python3
"""
Test the MCP server functionality
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

# Test the server import
from src.locusts_mcp.server import app, test_results


async def test_mcp_server():
    """Test basic MCP server functionality."""
    print("🧪 Testing MCP Server...")
    
    # Test 1: Create a basic config
    print("\n1. Testing create_basic_config...")
    
    from src.locusts_mcp.server import create_basic_config_tool
    
    result = await create_basic_config_tool({
        "host": "https://httpbin.org",
        "users": 5,
        "endpoints": ["/get", "/post", "/status/200"]
    })
    
    print(f"✅ Config creation result: {result[0].text[:100]}...")
    
    # Test 2: Validate config
    print("\n2. Testing validate_config...")
    
    # Find the created config file
    data_files = list(Path("data").glob("config_generated_*.json"))
    if data_files:
        config_path = str(data_files[0])
        print(f"Found config file: {config_path}")
        
        from src.locusts_mcp.server import validate_config_tool
        
        result = await validate_config_tool({
            "config_path": config_path
        })
        
        print(f"✅ Validation result: {result[0].text[:100]}...")
    else:
        print("❌ No config file found")
    
    # Test 3: Test server tools listing
    print("\n3. Testing list_tools...")
    
    from src.locusts_mcp.server import handle_list_tools
    
    tools = await handle_list_tools()
    print(f"✅ Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    print("\n🎉 MCP Server tests completed!")


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    asyncio.run(test_mcp_server())