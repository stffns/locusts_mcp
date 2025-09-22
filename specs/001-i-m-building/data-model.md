# Data Model: Dynamic Multi-App Simulation Runner

## Entities

### Simulation

- id (string)
- name (string)
- default_parameters (object)
- steps (array of Endpoint)
- supported_contexts (array of Context)
- criticality_rules (object)

### Context

- application (string)
- environment (string)
- country (string)

### Run

- id (string)
- simulation_id (string)
- context (Context)
- parameters (object)
- started_at (datetime)
- finished_at (datetime)
- status (enum: success, partial, failed, timed_out)
- step_results (array of StepResult)

### Catalog

- simulations (array of Simulation)
- compatibility (mapping of application->env->countries)

### Endpoint (Step)

- path (string)
- method (string)
- weight (number)
- headers (object, optional)
- payload (object, optional)
- timeout_seconds (number, optional)
- retries (number, optional)
- critical (boolean)

### StepResult

- step_ref (Endpoint)
- started_at (datetime)
- finished_at (datetime)
- status (enum: success, skipped, failed, retried)
- error (string, optional)

## Validation Rules

- Required config keys: host, users, spawn_rate, run_time
- Endpoints must have path, method, weight ≥ 1
- Context must be supported in catalog; unsupported combos disabled with explanation
- Critical steps abort run on failure; non-critical may continue
- Max run time default 30m; enforce timeout state
