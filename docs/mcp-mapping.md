# MCP Server Mapping Documentation

## Overview

This Locust performance testing application is designed to be MCP (Model Context Protocol) ready. It provides a foundation that can be easily converted into an MCP server for dynamic API load testing.

## Current Architecture

### Configuration System
- **Template-driven**: JSON configuration files define test scenarios
- **Precedence**: CLI > Environment Variables > Template files
- **Validation**: Required fields validation with clear error messages
- **Flexibility**: Support for complex endpoint configurations

### Request Generation  
- **Multi-method support**: GET, POST, PUT, DELETE
- **Headers**: Custom headers including Authentication, Content-Type
- **Payloads**: JSON request bodies for POST/PUT operations
- **Weighted selection**: Configurable endpoint weights for realistic traffic patterns

## MCP Server Conversion

### 1. Tools/Functions Mapping

The current Locust implementation can map to these MCP tools:

```typescript
// MCP Tool Definitions
{
  "run_load_test": {
    "description": "Execute a load test with specified configuration",
    "parameters": {
      "config_path": "string",  // Path to test configuration
      "users": "number",        // Override user count
      "spawn_rate": "number",   // Users per second spawn rate
      "run_time": "string",     // Test duration (e.g., "2m", "30s")
      "host": "string",         // Target host override
      "report_format": "string" // Output format (html, json)
    }
  },
  
  "validate_config": {
    "description": "Validate load test configuration without running test",
    "parameters": {
      "config_path": "string"
    }
  },
  
  "create_test_scenario": {
    "description": "Generate test configuration for API endpoints",
    "parameters": {
      "api_spec": "object",     // OpenAPI specification
      "test_strategy": "string", // Strategy: crud, read-heavy, write-heavy
      "target_rps": "number"    // Target requests per second
    }
  }
}
```

### 2. Resources Mapping

Current configuration files can become MCP resources:

```typescript
// MCP Resource Definitions
{
  "load_test_configs": {
    "uri": "config://load-tests/{config_name}",
    "mimeType": "application/json",
    "description": "Load test configuration templates"
  },
  
  "test_results": {
    "uri": "results://load-tests/{test_id}",
    "mimeType": "text/html",
    "description": "Load test execution reports"
  }
}
```

### 3. Prompts Integration

The load testing can be enhanced with LLM prompts:

```typescript
{
  "generate_api_test": {
    "description": "Generate load test configuration from API documentation",
    "arguments": [
      {
        "name": "api_documentation",
        "description": "API documentation or OpenAPI spec",
        "required": true
      },
      {
        "name": "performance_requirements", 
        "description": "Performance requirements and SLAs",
        "required": false
      }
    ]
  }
}
```

## Implementation Roadmap

### Phase 1: Basic MCP Server
1. Wrap current Locust functionality in MCP tool handlers
2. Add configuration resource management
3. Implement basic load test execution tools

### Phase 2: Enhanced Features  
1. OpenAPI spec parsing for automatic test generation
2. Performance analysis and recommendations
3. Integration with monitoring systems

### Phase 3: Advanced Capabilities
1. AI-driven test scenario generation
2. Performance regression detection
3. Multi-environment test orchestration

## Configuration Examples

### Simple CRUD API Test
```json
{
  "host": "https://api.example.com",
  "users": 10,
  "spawn_rate": 2,
  "run_time": "5m",
  "endpoints": [
    {
      "path": "/api/v1/users",
      "method": "GET",
      "weight": 5,
      "headers": {"Authorization": "Bearer {{token}}"}
    },
    {
      "path": "/api/v1/users",
      "method": "POST", 
      "weight": 2,
      "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer {{token}}"
      },
      "payload": {
        "name": "Test User",
        "email": "test@example.com"
      }
    }
  ]
}
```

### Performance Test Scenarios
```json
{
  "scenarios": {
    "read_heavy": {
      "description": "80% reads, 20% writes",
      "endpoints": [
        {"path": "/api/users", "method": "GET", "weight": 8},
        {"path": "/api/users", "method": "POST", "weight": 2}
      ]
    },
    "write_heavy": {
      "description": "30% reads, 70% writes", 
      "endpoints": [
        {"path": "/api/users", "method": "GET", "weight": 3},
        {"path": "/api/users", "method": "POST", "weight": 5},
        {"path": "/api/users/{id}", "method": "PUT", "weight": 2}
      ]
    }
  }
}
```

## Benefits for MCP Integration

1. **Template-driven flexibility**: Easy to create test scenarios for different APIs
2. **Configuration precedence**: Allows runtime customization via CLI/environment
3. **Multi-method support**: Handles full CRUD operations
4. **Realistic traffic patterns**: Weighted endpoint selection
5. **Comprehensive reporting**: HTML reports with detailed metrics
6. **Deterministic testing**: Seed-based reproducible results

## Next Steps

To convert this to an MCP server:

1. **Create MCP manifest**: Define tools, resources, and prompts
2. **Implement handlers**: Wrap existing functionality in MCP protocol handlers  
3. **Add AI integration**: Use LLM for test scenario generation and analysis
4. **Enhanced reporting**: Generate insights and recommendations
5. **Template library**: Build collection of common API test patterns

This foundation provides a solid base for building a comprehensive MCP-powered load testing solution.