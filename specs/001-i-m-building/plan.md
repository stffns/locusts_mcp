# Implementation Plan: Dynamic Multi-App Simulation Runner

**Branch**: `001-i-m-building` | **Date**: 2025-09-22 | **Spec**: /Users/jaysonsteffens/Documents/spec-test/specs/001-i-m-building/spec.md
**Input**: Feature specification from `/specs/001-i-m-building/spec.md`

## Execution Flow (/plan command scope)

```text
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:

- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

Enable a dynamic runner to execute simulations across different applications, environments, and countries, with strong validation and error handling that avoids non-critical fallbacks. Technical approach relies on a template-driven configuration to parameterize runs and a minimal Locust-based execution layer.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: Locust 2.x; JSON as primary config format (YAML optional later)
**Storage**: Files under `data/` for configs and `data/results/` for reports
**Testing**: Locust’s summary assertions + future pytest for validators
**Target Platform**: macOS/Linux runners
**Project Type**: single
**Performance Goals**: Handle small-to-medium simulations (tens of endpoints, up to 100-200 users initially)
**Constraints**: Headless runs by default; strong validation; no implicit critical fallbacks
**Scale/Scope**: Multi-app, multi-env, multi-country coverage in a single repo; future-ready to convert into an MCP

Technical Context (user input): "Voy a usar locust, por ahora para las configuracion archivos json que este listo para convertirse en un mcp"

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Dynamic Template-Driven Config: Use JSON under `data/`; required keys `host`, `users`, `spawn_rate`, `run_time`; optional `endpoints`, `think_time_seconds`, `seed`, `report_html` → PASS (planned)
- Precedence: CLI > ENV > template; use `CONFIG_PATH` env for template → PASS (planned)
- Minimal Locust Implementation: One `HttpUser`, dynamic tasks from `endpoints`, headless default, print resolved config → PASS (planned)
- Observability/Output: Support `--html` or `REPORT_HTML`, default `data/results/report.html`; non-zero exit on invalid config → PASS (planned)
- Simplicity: Only `locust` (+ optional `pyyaml` later); no extra DB/UI → PASS (planned)
- Constraints: Python 3.11+, dependencies pinned, deterministic `seed`, `--check-config` mode → PASS (planned)

No violations detected. Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/001-i-m-building/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```text
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: DEFAULT to Option 1 (single). No frontend/mobile detected.

## Phase 0: Outline & Research

1. Extract unknowns from Technical Context above:
   - Which JSON schema for simulations/endpoints? (fields, validation rules)
   - Strategy for dynamic task weighting and randomness seeding
   - Mapping for apps/environments/countries and compatibility catalog
   - Report format details for non-Locust artifacts (if any)

2. Generate and dispatch research agents:

```text
Task: "Research minimal JSON schema for Locust dynamic endpoints and validation rules"
Task: "Best practices for deterministic weighted task selection in Locust"
Task: "Design a compatibility catalog for app/env/country selection and validation"
Task: "Define report location conventions and naming under data/results/"
```

1. Consolidate findings in `research.md` using format:

- Decision: Chosen JSON schema and precedence rules
- Rationale: Simplicity, alignment with constitution
- Alternatives considered: YAML, CLI-only parameters

**Output**: research.md with all unknowns resolved

## Phase 1: Design & Contracts

Prerequisites: research.md complete

1. Extract entities from feature spec → `data-model.md`:
   - Entities: Simulation, Context, Run, Catalog (from spec)
   - Validation rules: required keys, compatibility checks, critical vs. recoverable

2. Generate API contracts from functional requirements:
   - Define CLI/contract surfaces to validate and run simulations (even if initial interface is CLI/Locust flags)
   - Output OpenAPI-style contract stubs for future MCP conversion to `/contracts/`

3. Generate contract tests from contracts:
   - One test file per contract endpoint or CLI command behavior
   - Assert request/response schemas (or CLI arg/env behaviors)

4. Extract test scenarios from user stories:
   - Quickstart walks through selecting a simulation, validating parameters, and executing headless

5. Update agent file incrementally (O(1)):
   - Run `.specify/scripts/bash/update-agent-context.sh copilot`

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach

This section describes what the /tasks command will do - DO NOT execute during /plan

**Task Generation Strategy**:

- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P]
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:

- TDD order: Tests before implementation
- Dependency order: Models before services before CLI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: ~25 tasks in tasks.md

## Phase 3+: Future Implementation

(Out of scope for /plan)

## Complexity Tracking

(No deviations – section intentionally left empty)

## Progress Tracking

**Phase Status**:

- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:

- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented
