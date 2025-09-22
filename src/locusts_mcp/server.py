#!/usr/bin/env python3
"""
Locusts MCP Server

A Model Context Protocol server for dynamic Locust performance testing.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Server("locusts-mcp")

# Store for test results
test_results: Dict[str, Dict[str, Any]] = {}

@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available MCP tools for load testing."""
    return [
        Tool(
            name="run_load_test",
            description="Execute a Locust load test with specified configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "config_path": {
                        "type": "string",
                        "description": "Path to test configuration file"
                    },
                    "users": {
                        "type": "number",
                        "description": "Number of concurrent users"
                    },
                    "spawn_rate": {
                        "type": "number", 
                        "description": "Users spawned per second"
                    },
                    "run_time": {
                        "type": "string",
                        "description": "Test duration like '5m' or '30s'"
                    },
                    "host": {
                        "type": "string",
                        "description": "Target host URL"
                    }
                },
                "required": ["config_path"]
            }
        ),
        Tool(
            name="validate_config",
            description="Validate a load test configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "config_path": {
                        "type": "string",
                        "description": "Path to configuration file"
                    }
                },
                "required": ["config_path"]
            }
        ),
        Tool(
            name="create_basic_config",
            description="Create a basic load test configuration file",
            inputSchema={
                "type": "object",  
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "Target host URL"
                    },
                    "users": {
                        "type": "number",
                        "default": 10,
                        "description": "Number of concurrent users"
                    },
                    "endpoints": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of endpoint paths to test"
                    }
                },
                "required": ["host"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]):
    """Handle tool calls from the MCP client."""
    
    if name == "validate_config":
        return await validate_config_tool(arguments)
    elif name == "run_load_test":
        return await run_load_test_tool(arguments)
    elif name == "create_basic_config":
        return await create_basic_config_tool(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def validate_config_tool(arguments: Dict[str, Any]):
    """Validate a Locust configuration."""
    try:
        config_path = arguments["config_path"]
        
        if not os.path.exists(config_path):
            return [TextContent(
                type="text",
                text=f"❌ Configuration file not found: {config_path}"
            )]
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_fields = ["host", "users", "spawn_rate", "run_time"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            return [TextContent(
                type="text",
                text=f"❌ Missing required fields: {', '.join(missing_fields)}"
            )]
        
        return [TextContent(
            type="text",
            text=f"✅ Configuration is valid!\n\n```json\n{json.dumps(config, indent=2)}\n```"
        )]
        
    except Exception as e:
        return [TextContent(
            type="text", 
            text=f"❌ Validation failed: {str(e)}"
        )]


async def run_load_test_tool(arguments: Dict[str, Any]):
    """Execute a load test using Locust."""
    try:
        config_path = arguments["config_path"]
        
        if not os.path.exists(config_path):
            return [TextContent(
                type="text",
                text=f"❌ Configuration file not found: {config_path}"
            )]
        
        test_id = str(uuid.uuid4())[:8]
        report_path = f"data/results/test_{test_id}.html"
        
        locust_cmd = [
            sys.executable, "-m", "locust",
            "-f", "locustfile.py",
            "--headless",
            "--html", report_path
        ]
        
        # Add CLI overrides
        if "users" in arguments:
            locust_cmd.extend(["--users", str(arguments["users"])])
        if "spawn_rate" in arguments:
            locust_cmd.extend(["--spawn-rate", str(arguments["spawn_rate"])])
        if "run_time" in arguments:
            locust_cmd.extend(["--run-time", str(arguments["run_time"])])
        if "host" in arguments:
            locust_cmd.extend(["--host", arguments["host"]])
        
        env = os.environ.copy()
        env["CONFIG_PATH"] = config_path
        
        result = subprocess.run(
            locust_cmd,
            cwd=str(Path(__file__).parent.parent.parent),
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        test_results[test_id] = {
            "id": test_id,
            "config_path": config_path,
            "command": " ".join(locust_cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "report_path": report_path
        }
        
        response_text = f"🚀 Load test completed!\n\n"
        response_text += f"**Test ID:** {test_id}\n"
        response_text += f"**Status:** {'✅ SUCCESS' if result.returncode == 0 else '⚠️ ERRORS'}\n\n"
        
        # Extract stats
        output_lines = result.stdout.split('\n')
        for line in output_lines:
            if "Aggregated" in line and "req/s" in line:
                response_text += f"**Summary:** {line.strip()}\n"
                break
        
        if os.path.exists(report_path):
            response_text += f"\n📊 **HTML Report:** {report_path}\n"
        
        if result.stderr:
            response_text += f"\n**Errors:** {result.stderr[-300:]}\n"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        logger.exception("Error running load test")
        return [TextContent(
            type="text",
            text=f"❌ Load test failed: {str(e)}"
        )]


async def create_basic_config_tool(arguments: Dict[str, Any]):
    """Create a basic load test configuration file."""
    try:
        host = arguments["host"]
        users = arguments.get("users", 10)
        endpoints = arguments.get("endpoints", ["/"])
        
        config = {
            "host": host,
            "users": users,
            "spawn_rate": max(1, users // 5),
            "run_time": "5m",
            "endpoints": [
                {"path": endpoint, "method": "GET", "weight": 1}
                for endpoint in endpoints
            ]
        }
        
        config_filename = f"data/config_generated_{uuid.uuid4().hex[:8]}.json"
        os.makedirs("data", exist_ok=True)
        
        with open(config_filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        response_text = f"✅ **Created:** {config_filename}\n\n"
        response_text += f"```json\n{json.dumps(config, indent=2)}\n```\n\n"
        response_text += f"💡 Use with `run_load_test` tool."
        
        return [TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Failed to create configuration: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    os.makedirs("data/results", exist_ok=True)
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="locusts-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())