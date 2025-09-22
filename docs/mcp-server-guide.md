# MCP Server Setup Guide

## Overview

The Locusts MCP Server provides Model Context Protocol integration for dynamic Locust performance testing. This allows AI agents to execute load tests, validate configurations, and generate test scenarios.

## Installation

Make sure you have the project installed with MCP dependencies:

```bash
# Install dependencies
uv add mcp locust

# Verify installation
uv run python -c "from src.locusts_mcp.server import main; print('✅ MCP Server ready')"
```

## Running the MCP Server

The MCP server communicates via stdin/stdout, so it's typically run by an MCP client:

```bash
# Run the server directly (for testing)
uv run python src/locusts_mcp/server.py

# Or use the entry point (if installed)
uv run locusts-mcp
```

## Available Tools

### 1. `create_basic_config`

Creates a basic load test configuration file.

**Parameters:**
- `host` (required): Target host URL
- `users` (optional): Number of concurrent users (default: 10)
- `endpoints` (optional): List of endpoint paths to test (default: ["/"])

**Example:**
```json
{
  "host": "https://httpbin.org",
  "users": 5,
  "endpoints": ["/get", "/post", "/status/200"]
}
```

### 2. `validate_config`

Validates a load test configuration without running the test.

**Parameters:**
- `config_path` (required): Path to configuration file

### 3. `run_load_test`

Executes a Locust load test with the specified configuration.

**Parameters:**
- `config_path` (required): Path to test configuration file
- `users` (optional): Override number of concurrent users
- `spawn_rate` (optional): Override users spawned per second
- `run_time` (optional): Override test duration
- `host` (optional): Override target host URL

## MCP Client Configuration

To use this server with an MCP client like Claude Desktop, add this to your MCP configuration:

```json
{
  "mcpServers": {
    "locusts-mcp": {
      "command": "uv",
      "args": [
        "run", 
        "--directory", 
        "/path/to/spec-test",
        "python", 
        "src/locusts_mcp/server.py"
      ],
      "env": {
        "UV_PROJECT_ENVIRONMENT": "/path/to/spec-test/.venv"
      }
    }
  }
}
```

## Testing the Server

Use the included test script:

```bash
uv run python test_mcp.py
```

This will test:
- Basic configuration creation
- Configuration validation
- Tool listing functionality

## Integration with Locust

The MCP server uses your existing `locustfile.py` and configuration system:

1. **Configurations**: Created in `data/` directory
2. **Results**: Stored in `data/results/` with HTML reports
3. **Environment**: Uses `CONFIG_PATH` environment variable
4. **CLI overrides**: Supports all Locust CLI parameters

## Example Workflow

1. **Create configuration:**
   ```json
   {
     "tool": "create_basic_config",
     "arguments": {
       "host": "https://api.example.com",
       "users": 20,
       "endpoints": ["/users", "/posts", "/comments"]
     }
   }
   ```

2. **Validate configuration:**
   ```json
   {
     "tool": "validate_config",
     "arguments": {
       "config_path": "data/config_generated_abc123.json"
     }
   }
   ```

3. **Run load test:**
   ```json
   {
     "tool": "run_load_test",
     "arguments": {
       "config_path": "data/config_generated_abc123.json",
       "run_time": "2m"
     }
   }
   ```

## Error Handling

The server handles common errors:
- Missing configuration files
- Invalid JSON configurations
- Locust execution failures
- Timeouts (5-minute limit)

All errors are returned as formatted text responses with appropriate emoji indicators.

## Development

To extend the server:

1. Add new tools to `handle_list_tools()`
2. Implement tool functions following the pattern
3. Add to `handle_call_tool()` dispatcher
4. Test with `test_mcp.py`

The server follows MCP protocol standards and returns `TextContent` responses for all operations.