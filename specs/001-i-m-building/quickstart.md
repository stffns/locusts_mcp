# Quickstart: Dynamic Multi-App Simulation Runner

## Prerequisites

- Python 3.11+
- Install dependencies: locust (and pyyaml if YAML later)

## Basic Run (headless)

```bash
export CONFIG_PATH=data/config.example.json
locust -f locustfile.py --headless
```

## Override Parameters

```bash
locust -f locustfile.py --headless --users 50 --spawn-rate 5 --run-time 10m --host https://example.com
```

## Validate Config

```bash
python locustfile.py --check-config
```

## Reports

- HTML report default path: data/results/report.html (or via --html)
