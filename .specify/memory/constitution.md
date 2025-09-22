# Locust Performance App Constitution

## Core Principles

### I. Dynamic Template-Driven Configuration

- Single source of truth is a configuration template file at `data/<name>.{yaml|yml|json}`.
- Minimum required fields: `host` (string), `users` (int), `spawn_rate` (float), `run_time` (string, Locust duration format like "5m").
- Optional fields: `endpoints` (list of {`path`, `method`, `weight`, `headers?`, `payload?`}), `think_time_seconds` (float), `seed` (int), `report_html` (path).
- Precedence for values: CLI args > environment variables > template file defaults.
- Environment variables: `CONFIG_PATH` (path to template), `USERS`, `SPAWN_RATE`, `RUN_TIME`, `HOST`, `REPORT_HTML`.
- If `CONFIG_PATH` is unset, default to `data/config.yaml` if present, else `data/config.json`.

Example minimal template (YAML):

```yaml
host: https://example.com
users: 10
spawn_rate: 2
run_time: 2m
endpoints:
  - path: "/"
    method: GET
    weight: 1
```

### II. Minimal Viable Locust Implementation

- Provide a `locustfile.py` that:
  - Loads the configuration using the precedence above.
  - Defines a single `HttpUser` whose tasks are built dynamically from `endpoints` with weighted selection.
  - Sets wait time using `between(think_time_seconds, think_time_seconds)` if provided; otherwise Locust default.
  - Accepts headless execution using standard Locust flags (`--headless`, `--users`, `--spawn-rate`, `--run-time`, `--host`).
- Headless is the default execution mode for CI and non-interactive runs.

### III. CLI and Overrides

- Primary run command: `locust -f locustfile.py --headless` with optional overrides (`--users`, `--spawn-rate`, `--run-time`, `--host`).
- A lightweight wrapper is allowed but not required; configuration path is provided via `CONFIG_PATH` env var.
- On startup, print the resolved config (sanitized) and the precedence source per key.

### IV. Observability and Output

- Use Locust built-ins for summary stats. Support optional `--html <path>` or `REPORT_HTML` env var; default to `data/results/report.html` when not specified.
- Non-zero exit when configuration is invalid or required keys are missing.

### V. Simplicity First

- No external databases or custom UI. Keep dependencies minimal.
- Only `locust` and (if YAML templates are used) `pyyaml` are allowed.

## Additional Constraints

- Runtime: Python 3.11+.
- Dependencies: `locust>=2.23,<3.0`; `pyyaml>=6,<7` when using YAML; JSON requires no extra dependency.
- File layout: `locustfile.py` at repo root. Templates live under `data/`. Reports stored under `data/results/`.
- Determinism: when `seed` is set, initialize Python `random` and any weighted choices deterministically.
- Validation: fail fast with a clear message listing missing required keys.

## Workflow and Acceptance

- Provide one example template at `data/config.example.yaml` (or JSON equivalent) matching the schema.
- With only the example template and no CLI overrides, the following must execute successfully:
  - `CONFIG_PATH=data/config.example.yaml locust -f locustfile.py --headless`
- CLI overrides take precedence over template/env and are reflected in the printed resolved config.
- Optional HTML report path can be specified via `--html` or `REPORT_HTML`; file is created successfully.
- A `--check-config` mode (or equivalent code path) validates the template and exits without running traffic.

## Governance

- This constitution defines the minimum bar for the Locust app. Implementations must meet these requirements before extension.
- Amendments require updating this document alongside any code or template schema changes.

**Version**: 0.1.0 | **Ratified**: 2025-09-22 | **Last Amended**: 2025-09-22
