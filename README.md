# Dynamic Locust Performance Testing App

A template-driven Locust performance testing application with dynamic configuration and MCP server readiness.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (tested with Python 3.13)
- Virtual environment support

### Installation

1. **Clone and setup the project:**
```bash
git clone <repository-url>
cd spec-test
```

2. **Create and activate virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install locust>=2.23,<3.0
```

### Basic Usage

**Run with example configuration:**
```bash
CONFIG_PATH=data/config.example.json locust -f locustfile.py --headless --run-time 30s
```

**With CLI overrides:**
```bash
CONFIG_PATH=data/config.example.json locust -f locustfile.py --headless \
  --users 5 --spawn-rate 1 --run-time 10s --host https://httpbin.org
```

**With environment variables:**
```bash
CONFIG_PATH=data/config.example.json HOST=https://httpbin.org USERS=3 \
  locust -f locustfile.py --headless --run-time 15s
```

## 📖 Configuration

### Configuration Files

Configuration templates are stored in the `data/` directory as JSON files:

- `data/config.example.json` - Basic example configuration
- `data/config.openapi.json` - Advanced OpenAPI-style configuration with multiple HTTP methods

### Configuration Schema

**Required fields:**
- `host` (string) - Target host URL
- `users` (integer) - Number of concurrent users
- `spawn_rate` (float) - Users spawned per second
- `run_time` (string) - Test duration in Locust format (e.g., "5m", "30s")

**Optional fields:**
- `endpoints` (array) - List of endpoint configurations
- `think_time_seconds` (float) - Wait time between requests
- `seed` (integer) - Random seed for deterministic results
- `report_html` (string) - HTML report output path

### Endpoint Configuration

Each endpoint in the `endpoints` array supports:

```json
{
  "path": "/api/users",
  "method": "GET",
  "weight": 2,
  "headers": {
    "Authorization": "Bearer token",
    "Content-Type": "application/json"
  },
  "payload": {
    "name": "Test User",
    "email": "test@example.com"
  }
}
```

- `path` (required) - API endpoint path
- `method` (optional) - HTTP method (GET, POST, PUT, DELETE), defaults to GET
- `weight` (optional) - Relative weight for selection probability, defaults to 1
- `headers` (optional) - Custom HTTP headers
- `payload` (optional) - JSON request body for POST/PUT requests

### Configuration Precedence

Values are resolved in this order (highest to lowest priority):

1. **CLI arguments** - `--users`, `--spawn-rate`, `--run-time`, `--host`
2. **Environment variables** - `USERS`, `SPAWN_RATE`, `RUN_TIME`, `HOST`, `REPORT_HTML`
3. **Template file** - JSON configuration file

## 🔧 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CONFIG_PATH` | Path to configuration template | `data/config.json` |
| `USERS` | Number of concurrent users | `10` |
| `SPAWN_RATE` | Users spawned per second | `2.0` |
| `RUN_TIME` | Test duration | `5m` |
| `HOST` | Target host URL | `https://api.example.com` |
| `REPORT_HTML` | HTML report output path | `reports/test.html` |

## 📊 Examples

### Simple GET Requests

```json
{
  "host": "https://httpbin.org",
  "users": 5,
  "spawn_rate": 1,
  "run_time": "1m",
  "endpoints": [
    {"path": "/get", "method": "GET", "weight": 1},
    {"path": "/status/200", "method": "GET", "weight": 2}
  ]
}
```

### CRUD API Testing

```json
{
  "host": "https://api.example.com",
  "users": 10,
  "spawn_rate": 2,
  "run_time": "5m",
  "think_time_seconds": 1.0,
  "endpoints": [
    {
      "path": "/api/v1/users",
      "method": "GET",
      "weight": 5,
      "headers": {"Authorization": "Bearer token"}
    },
    {
      "path": "/api/v1/users",
      "method": "POST",
      "weight": 2,
      "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer token"
      },
      "payload": {
        "name": "Test User",
        "email": "test@example.com"
      }
    },
    {
      "path": "/api/v1/users/123",
      "method": "PUT",
      "weight": 1,
      "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer token"
      },
      "payload": {
        "name": "Updated User"
      }
    },
    {
      "path": "/api/v1/users/123",
      "method": "DELETE",
      "weight": 1,
      "headers": {"Authorization": "Bearer token"}
    }
  ]
}
```

## 🎯 Common Use Cases

### 1. Basic Health Check
```bash
# Quick health check with 1 user for 10 seconds
CONFIG_PATH=data/config.example.json locust -f locustfile.py --headless \
  --users 1 --spawn-rate 1 --run-time 10s
```

### 2. Load Testing
```bash
# Load test with 50 users, ramping up 5 per second for 5 minutes
CONFIG_PATH=data/config.example.json locust -f locustfile.py --headless \
  --users 50 --spawn-rate 5 --run-time 5m
```

### 3. Stress Testing
```bash
# Stress test with high user count
CONFIG_PATH=data/config.example.json locust -f locustfile.py --headless \
  --users 100 --spawn-rate 10 --run-time 10m --html data/results/stress-test.html
```

### 4. Development Testing
```bash
# Test against local development server
CONFIG_PATH=data/config.example.json HOST=http://localhost:8000 \
  locust -f locustfile.py --headless --users 5 --run-time 30s
```

## 📁 Project Structure

```
spec-test/
├── locustfile.py              # Main Locust implementation
├── data/
│   ├── config.example.json    # Example configuration
│   ├── config.openapi.json    # Advanced OpenAPI example
│   └── results/
│       └── README.md          # Generated reports directory
├── docs/
│   └── mcp-mapping.md         # MCP server conversion guide
└── specs/
    └── 001-i-m-building/      # Project specifications
```

## 🔍 Validation and Debugging

### Configuration Validation

The application validates configuration on startup and provides clear error messages:

```bash
# Test with invalid configuration
CONFIG_PATH=data/config.bad.json locust -f locustfile.py --headless
# Output: Configuration error: Missing required configuration keys: host
```

### Resolved Configuration

On startup, the application prints the resolved configuration showing the source of each value:

```
=== Resolved Configuration ===
host: https://httpbin.org (from env:HOST)
users: 5 (from env:USERS)
spawn_rate: 2 (from template:data/config.example.json)
run_time: 30s (from cli)
...
```

## 📊 Reporting

### HTML Reports

Generate detailed HTML reports with performance metrics:

```bash
# Generate HTML report
CONFIG_PATH=data/config.example.json locust -f locustfile.py --headless \
  --run-time 2m --html data/results/performance-report.html
```

Reports include:
- Request statistics (response times, throughput, error rates)
- Response time percentiles
- Error details
- Charts and graphs (in web UI mode)

### Web UI Mode

For interactive testing and real-time monitoring:

```bash
# Start web UI (remove --headless)
CONFIG_PATH=data/config.example.json locust -f locustfile.py
# Access at http://localhost:8089
```

## 🔧 Advanced Features

### Deterministic Testing

Use seeds for reproducible test results:

```json
{
  "seed": 42,
  "endpoints": [...]
}
```

### Custom Think Time

Add realistic delays between requests:

```json
{
  "think_time_seconds": 2.5,
  "endpoints": [...]
}
```

### Weighted Endpoint Selection

Control traffic distribution with weights:

```json
{
  "endpoints": [
    {"path": "/api/read", "weight": 8},   # 80% of requests
    {"path": "/api/write", "weight": 2}   # 20% of requests
  ]
}
```

## 🚀 MCP Server Readiness

This implementation is designed to be easily converted to a Model Context Protocol (MCP) server. See `docs/mcp-mapping.md` for detailed conversion guidance.

## 🐛 Troubleshooting

### Common Issues

**1. "You must specify the base host" error:**
- Ensure `host` is specified in configuration or via `--host` flag

**2. "Missing required configuration keys" error:**
- Check that all required fields are present in your configuration file

**3. JSON parsing errors:**
- Validate your JSON configuration file syntax

**4. Import errors:**
- Ensure Locust is installed: `pip install locust>=2.23,<3.0`
- Activate your virtual environment

### Debug Mode

Add verbose output for debugging:

```bash
# Run with verbose logging
CONFIG_PATH=data/config.example.json locust -f locustfile.py --headless \
  --run-time 30s -L DEBUG
```

## 📝 Contributing

This project follows the `.specify` methodology with constitutional development principles. See `.specify/memory/constitution.md` for implementation requirements.

## 📄 License

This project is part of a specification-driven development experiment following constitutional programming principles.

---

**Version**: 1.0.0 | **Last Updated**: September 22, 2025