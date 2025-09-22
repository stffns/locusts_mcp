# Research: Dynamic Multi-App Simulation Runner

## Decisions

- JSON schema for configs with required keys: host, users, spawn_rate, run_time; optional: endpoints[], think_time_seconds, seed, report_html
- Precedence: CLI > ENV > template (CONFIG_PATH)
- Deterministic weighting with explicit seed
- Compatibility catalog for app/env/country with disabled-when-unsupported rules
- Reports to data/results/report.html by default

## Rationale

- Aligns with constitution simplicity and dynamic config requirements
- JSON first per user input; YAML can be added later with pyyaml
- Determinism aids reproducibility and debugging

## Alternatives Considered

- YAML-first (adds dependency now; deferred)
- CLI-only configuration (harder to reuse/share, verbose)

