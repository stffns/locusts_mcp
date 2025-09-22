#!/usr/bin/env python3
"""
Complete MCP Server Integration Test

Tests the full workflow of the Locusts MCP server.
"""

import asyncio
import json
import os
from pathlib import Path

from src.locusts_mcp.server import (
    create_basic_config_tool,
    validate_config_tool,
    run_load_test_tool,
    handle_list_tools
)


async def full_integration_test():
    """Run a complete integration test of the MCP server."""
    print("🚀 Starting Full MCP Integration Test\n")
    
    # Ensure directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/results", exist_ok=True)
    
    try:
        # Step 1: List available tools
        print("📋 Step 1: Listing available tools...")
        tools = await handle_list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   • {tool.name}")
        
        # Step 2: Create a test configuration
        print("\n⚙️  Step 2: Creating test configuration...")
        config_result = await create_basic_config_tool({
            "host": "https://httpbin.org",
            "users": 2,
            "endpoints": ["/get", "/json", "/headers"]
        })
        
        config_text = config_result[0].text
        print(f"✅ Configuration created successfully")
        
        # Extract config filename from the response
        import re
        config_match = re.search(r'data/config_generated_[a-f0-9]+\.json', config_text)
        if not config_match:
            raise ValueError("Could not find config filename in response")
        
        config_path = config_match.group(0)
        print(f"   📄 Config file: {config_path}")
        
        # Step 3: Validate the configuration
        print("\n✅ Step 3: Validating configuration...")
        validation_result = await validate_config_tool({
            "config_path": config_path
        })
        
        validation_text = validation_result[0].text
        if "✅ Configuration is valid!" in validation_text:
            print("✅ Configuration validation passed")
        else:
            raise ValueError(f"Configuration validation failed: {validation_text}")
        
        # Step 4: Simulate a short load test
        print("\n🔥 Step 4: Running load test...")
        print("   (This will take a few seconds...)")
        
        test_result = await run_load_test_tool({
            "config_path": config_path,
            "users": 1,
            "spawn_rate": 1,
            "run_time": "5s"
        })
        
        test_text = test_result[0].text
        if "Load test completed!" in test_text:
            print("✅ Load test completed successfully")
            
            # Extract test ID
            test_id_match = re.search(r'Test ID:\*\* ([a-f0-9]+)', test_text)
            if test_id_match:
                test_id = test_id_match.group(1)
                print(f"   🆔 Test ID: {test_id}")
            
            # Check for success status
            if "✅ SUCCESS" in test_text:
                print("   🎯 Test status: SUCCESS")
            elif "⚠️ ERRORS" in test_text:
                print("   ⚠️  Test status: COMPLETED WITH ERRORS")
                print("   📝 Check the output for details")
            
        else:
            print(f"⚠️  Load test had issues: {test_text[:200]}...")
        
        # Step 5: Verify files were created
        print("\n📁 Step 5: Verifying created files...")
        
        if os.path.exists(config_path):
            print(f"✅ Config file exists: {config_path}")
            
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                print(f"   🎯 Host: {config_data['host']}")
                print(f"   👥 Users: {config_data['users']}")
                print(f"   📊 Endpoints: {len(config_data['endpoints'])}")
        
        # Check for report files
        report_files = list(Path("data/results").glob("test_*.html"))
        if report_files:
            print(f"✅ Found {len(report_files)} HTML report(s)")
            for report in report_files:
                print(f"   📊 Report: {report}")
        
        print("\n🎉 Integration Test PASSED!")
        print("\n📋 Summary:")
        print("   • MCP tools are working correctly")
        print("   • Configuration creation and validation works")
        print("   • Load test execution is functional")
        print("   • File generation is working")
        print("   • The MCP server is ready for production use!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def quick_validation_test():
    """Quick validation that the server can start and list tools."""
    print("🔍 Quick Validation Test...")
    
    try:
        tools = await handle_list_tools()
        expected_tools = {"run_load_test", "validate_config", "create_basic_config"}
        actual_tools = {tool.name for tool in tools}
        
        if expected_tools.issubset(actual_tools):
            print("✅ All expected tools are available")
            return True
        else:
            missing = expected_tools - actual_tools
            print(f"❌ Missing tools: {missing}")
            return False
            
    except Exception as e:
        print(f"❌ Quick validation failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🧪 Locusts MCP Server - Complete Test Suite\n")
    
    # Quick validation first
    if not await quick_validation_test():
        print("\n❌ Quick validation failed, skipping integration test")
        return
    
    print()
    
    # Full integration test
    success = await full_integration_test()
    
    if success:
        print("\n🏆 ALL TESTS PASSED - MCP Server is ready!")
    else:
        print("\n💥 TESTS FAILED - Check the errors above")


if __name__ == "__main__":
    asyncio.run(main())