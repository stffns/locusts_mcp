# Tasks: Dynamic Multi-App Simulation Runner

## Conventions

- Numbered tasks T001+, grouped by phase
- [P] indicates tasks that can run in parallel
- Use repo root paths; macOS zsh shell

## Phase A: Environment + Scaffolding

- T001: Create Python environment and deps [P]
  - Command:

    ```zsh
    python3 -m venv .venv && source .venv/bin/activate
    pip install --upgrade pip
    pip install "locust>=2.23,<3"
    ```

- T002: Prepare folders for data and results [P]
  - Paths: `/Users/jaysonsteffens/Documents/spec-test/data`, `/Users/jaysonsteffens/Documents/spec-test/data/results`
  - Command:

    ```zsh
    mkdir -p data/results
    ```

- T003: Add example JSON config [P]
  - Path: `/Users/jaysonsteffens/Documents/spec-test/data/config.example.json`
  - Content (example):

    ```json
    {
      "host": "https://example.com",
      "users": 10,
      "spawn_rate": 2,
      "run_time": "2m",
      "seed": 42,
      "think_time_seconds": 0,
      "endpoints": [
        {"path": "/", "method": "GET", "weight": 1}
      ]
    }
    ```

## Phase B: Locust Implementation

- T010: Implement config loader with precedence [required]
  - Path: `/Users/jaysonsteffens/Documents/spec-test/locustfile.py`
  - Must support: JSON template (via CONFIG_PATH), ENV overrides, CLI overrides; print resolved config/source; `--check-config` mode; non-zero exit on invalid keys

- T011: Build dynamic HttpUser tasks from endpoints [required]
  - Weighting from `endpoints[].weight`; deterministic when `seed` present; optional headers/payload per step

- T012: Support wait time and headless defaults [required]
  - Use think_time_seconds for between(a,a) if provided; default Locust wait otherwise; run supports `--html` path

- T013: Deterministic run seeding [required]
  - Seed Python random when `seed` provided; document in logs

- T014: CLI and env injection validation [required]
  - Validate `USERS`, `SPAWN_RATE`, `RUN_TIME`, `HOST`, `REPORT_HTML`; precedence CLI > ENV > template

## Phase C: Validation + Quickstart

- T020: Write quickstart verification steps [P]
  - Follow `specs/001-i-m-building/quickstart.md`; ensure commands succeed with example config

- T021: Add `--check-config` verification [P]
  - Ensure validation-only mode exits 0 on valid, non-zero on invalid

- T022: Generate HTML report check [P]
  - Verify `--html data/results/report.html` produces file

## Phase D: Contracts + MCP Readiness

- T030: Validate OpenAPI stubs [P]
  - Path: `specs/001-i-m-building/contracts/openapi.yaml`; run a linter (if available) and ensure schemas compile

- T031: Draft CLI-to-contract mapping doc [P]
  - Add notes in `contracts/` about mapping validate/run to CLI/env/Locust flags for future MCP

## Phase E: Governance + Housekeeping

- T040: Align with constitution checklist [required]
  - Ensure all constitution gates in `.specify/memory/constitution.md` met by implementation

- T041: Commit and push branch [required]
  - Command:

    ```zsh
    git add .
    git commit -m "feat(locust): dynamic JSON-config runner with validation and reports"
    git push -u origin 001-i-m-building
    ```
