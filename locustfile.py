#!/usr/bin/env python3
"""
Dynamic Multi-App Simulation Runner using Locust
Follows constitution: template-driven config, precedence CLI > ENV > template
"""
import json
import os
import random
import sys
from typing import Dict, Any, List, Optional
from locust import HttpUser, task, between, events
from locust.env import Environment


class ConfigLoader:
    """Loads and validates configuration with precedence: CLI > ENV > template"""
    
    REQUIRED_KEYS = {'host', 'users', 'spawn_rate', 'run_time'}
    OPTIONAL_KEYS = {'endpoints', 'think_time_seconds', 'seed', 'report_html'}
    
    def __init__(self):
        self.config = {}
        self.sources = {}  # Track where each value came from
    
    def load(self) -> Dict[str, Any]:
        """Load config with precedence: CLI > ENV > template file"""
        # 1. Load template file
        self._load_template()
        
        # 2. Apply environment variable overrides
        self._apply_env_overrides()
        
        # 3. CLI overrides handled by Locust itself
        
        # 4. Validate required keys
        self._validate()
        
        # 5. Set defaults for optional keys
        self._set_defaults()
        
        return self.config
    
    def _load_template(self):
        """Load JSON template from CONFIG_PATH or default locations"""
        config_path = os.environ.get('CONFIG_PATH')
        
        if not config_path:
            # Try default locations
            for default_path in ['data/config.yaml', 'data/config.json']:
                if os.path.exists(default_path):
                    config_path = default_path
                    break
        
        if not config_path:
            # Use example config if no template found
            config_path = 'data/config.example.json'
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                template_config = json.load(f)
            
            for key, value in template_config.items():
                self.config[key] = value
                self.sources[key] = f"template:{config_path}"
        
        except (json.JSONDecodeError, IOError) as e:
            raise ValueError(f"Invalid config file {config_path}: {e}")
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        env_mappings = {
            'USERS': ('users', int),
            'SPAWN_RATE': ('spawn_rate', float),
            'RUN_TIME': ('run_time', str),
            'HOST': ('host', str),
            'REPORT_HTML': ('report_html', str)
        }
        
        for env_key, (config_key, type_func) in env_mappings.items():
            env_value = os.environ.get(env_key)
            if env_value is not None:
                try:
                    self.config[config_key] = type_func(env_value)
                    self.sources[config_key] = f"env:{env_key}"
                except ValueError as e:
                    raise ValueError(f"Invalid {env_key} environment variable: {e}")
    
    def _validate(self):
        """Validate required keys are present"""
        missing_keys = self.REQUIRED_KEYS - set(self.config.keys())
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {', '.join(sorted(missing_keys))}")
    
    def _set_defaults(self):
        """Set defaults for optional keys"""
        if 'endpoints' not in self.config:
            self.config['endpoints'] = [{"path": "/", "method": "GET", "weight": 1}]
            self.sources['endpoints'] = "default"
        
        if 'think_time_seconds' not in self.config:
            self.config['think_time_seconds'] = None
            self.sources['think_time_seconds'] = "default"
        
        if 'report_html' not in self.config:
            self.config['report_html'] = "data/results/report.html"
            self.sources['report_html'] = "default"
    
    def print_resolved_config(self):
        """Print resolved configuration with sources (sanitized)"""
        print("=== Resolved Configuration ===")
        for key, value in self.config.items():
            source = self.sources.get(key, "unknown")
            if key == 'seed' and value is not None:
                print(f"{key}: [REDACTED] (from {source})")
            else:
                print(f"{key}: {value} (from {source})")
        print("=" * 31)


class DynamicHttpUser(HttpUser):
    """HttpUser with dynamic tasks built from endpoints configuration"""
    
    def __init__(self, *args, **kwargs):
        self.config = GLOBAL_CONFIG
        super().__init__(*args, **kwargs)
        
        self._setup_wait_time()
        self._setup_tasks()
    
    def _setup_wait_time(self):
        """Configure wait time based on think_time_seconds"""
        think_time = self.config.get('think_time_seconds')
        if think_time is not None and think_time > 0:
            # Set as instance method that returns the think time
            self.wait_time = lambda: think_time
        # Otherwise, use Locust default wait time
    
    def _setup_tasks(self):
        """Build weighted tasks from endpoints configuration"""
        endpoints = self.config.get('endpoints', [])
        if not endpoints:
            return
        
        # Build weighted task list
        self.endpoint_tasks = []
        for endpoint in endpoints:
            weight = endpoint.get('weight', 1)
            for _ in range(weight):
                self.endpoint_tasks.append(endpoint)
    
    @task
    def dynamic_request(self):
        """Execute a randomly selected endpoint based on weights"""
        if not hasattr(self, 'endpoint_tasks') or not self.endpoint_tasks:
            # Fallback to root
            self.client.get("/")
            return
        
        # Select endpoint (deterministic if seed is set)
        endpoint = random.choice(self.endpoint_tasks)
        
        path = endpoint['path']
        method = endpoint.get('method', 'GET').upper()
        headers = endpoint.get('headers', {})
        payload = endpoint.get('payload')
        
        try:
            if method == 'GET':
                self.client.get(path, headers=headers)
            elif method == 'POST':
                self.client.post(path, json=payload, headers=headers)
            elif method == 'PUT':
                self.client.put(path, json=payload, headers=headers)
            elif method == 'DELETE':
                self.client.delete(path, headers=headers)
            else:
                # Unsupported method, skip
                pass
        except Exception as e:
            print(f"Request error for {method} {path}: {e}")


def setup_deterministic_seed(config: Dict[str, Any]):
    """Initialize random seed for deterministic runs"""
    seed = config.get('seed')
    if seed is not None:
        random.seed(seed)
        print(f"Initialized random seed: {seed}")


def check_config_mode():
    """Handle --check-config mode"""
    if '--check-config' in sys.argv:
        try:
            loader = ConfigLoader()
            config = loader.load()
            loader.print_resolved_config()
            print("✓ Configuration is valid")
            sys.exit(0)
        except Exception as e:
            print(f"✗ Configuration error: {e}")
            sys.exit(1)


# Global config storage for user classes
GLOBAL_CONFIG = {}

@events.init.add_listener
def on_locust_init(environment: Environment, **kwargs):
    """Initialize configuration when Locust starts up"""
    global GLOBAL_CONFIG
    try:
        loader = ConfigLoader()
        config = loader.load()
        
        # Store config globally for access by user classes
        GLOBAL_CONFIG = config
        
        # Set host as class attribute for Locust
        if config.get('host'):
            DynamicHttpUser.host = config['host']
        
        # Print resolved configuration
        loader.print_resolved_config()
        
        # Setup deterministic seeding
        setup_deterministic_seed(config)
        
    except Exception as e:
        print(f"Configuration error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Handle --check-config mode
    check_config_mode()
    
    # For direct execution, print usage
    print("Usage:")
    print("  locust -f locustfile.py --headless")
    print("  python locustfile.py --check-config")
    print("")
    print("Environment variables:")
    print("  CONFIG_PATH, USERS, SPAWN_RATE, RUN_TIME, HOST, REPORT_HTML")