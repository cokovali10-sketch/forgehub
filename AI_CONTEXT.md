# ForgeHub - AI Context Map

You are an AI agent with access to the ForgeHub ecosystem.
ForgeHub is a registry of modules, tools and playbooks. Before acting, study
the relevant entries. Use the right tool for the task.

## How to study ForgeHub

1. Run `forgehub context` to get the full map.
2. Run `forgehub search <query>` to find relevant playbooks and tools.
3. Run `forgehub show <id>` to read a playbook or tool schema.
4. Run `forgehub describe <module>` to understand a module.
5. Run `forgehub inject <task>` to get a compressed context bundle for a task.

## Available modules

### FORGE (forge) - Code quality and verification platform
Verify, audit and improve code: SAST/DAST/SBOM, policy enforcement, report export, pipeline orchestration.
Use when:
  - You need to scan code for vulnerabilities or quality issues
  - You need to generate an SBOM or SARIF report
  - You need policy enforcement on a codebase
  - You need to run a full verification pipeline
CLI: `qorvex`
Tools: forge.scan, forge.verify, forge.sbom, forge.report
Knowledge: code-review, security-scan, sbom-generation

### SOLAR (solar) - Token optimization layer for LLM workflows
Reduce token usage without losing correctness: compress prompts, select relevant context, cache answers, route models, enforce budgets.
Use when:
  - You need to send a long prompt or large context to an LLM
  - You want to cache repeated questions
  - You need to pick the cheapest model for a task
  - You need to enforce a token budget
  - You want to compress verbose instructions or logs
CLI: `solar`
Tools: solar.compress, solar.context, solar.cache, solar.optimize
Knowledge: prompt-compression, context-optimization, semantic-cache

### MATRIX (matrix) - Artificial work environment for AI capability growth
Knowledge space, tool space, task space with tests, memory space, simulation space, evaluation space.
Use when:
  - You want an AI to learn from curated tasks with tests
  - You need a tool registry with JSON schemas
  - You want to measure whether an AI improves on repeated tasks
  - You need a sandboxed simulation environment
CLI: `matrix`
Tools: matrix.task, matrix.eval, matrix.memory
Knowledge: task-design, eval-harness, tool-registry

### Helix (helix) - SOC observability platform with custom TSDB
Full observability: event collection, ingestion, storage (TSDB), query, alerting, dashboards, Kubernetes deployment.
Use when:
  - You need to collect and store time-series events at scale
  - You need multi-tenant observability
  - You need a Prometheus/ClickHouse replacement tuned for SOC
CLI: `helix`
Tools: helix.ingest, helix.query, helix.alert
Knowledge: tsdb-design, observability, multi-tenancy

### Qorvex (qorvex) - AI code verification platform
Verify AI-generated code with policy engine, audit trail, SBOM and report export.
Use when:
  - You need to verify code produced by an LLM
  - You need to run untrusted code in a sandbox
  - You need SBOM generation or SARIF reports
CLI: `qorvex`
Tools: qorvex.scan, qorvex.sandbox, qorvex.sbom, qorvex.report
Knowledge: code-verification, sandboxing, sast, dast

## Available tools

- `solar.compress` (solar): Compress a prompt or text, protecting code/ids/paths/numbers/quotes.
- `solar.context` (solar): Select relevant project files within a token budget.
- `solar.cache` (solar): Semantic cache lookup/store.
- `solar.optimize` (solar): Full optimization pipeline.
- `forge.scan` (forge): Security scan (SAST/DAST/SBOM).
- `forge.sandbox` (forge): Isolated execution (setrlimit/Job Objects).
- `qorvex.verify` (qorvex): Verify AI-generated code.

## Available playbooks (knowledge)

- `prompt-compression`: Compress prompts without breaking code
- `context-optimization`: Select relevant project context within a token budget
- `semantic-cache`: Cache LLM responses by semantic similarity
- `code-review`: Review code for quality and correctness
- `security-scan`: Scan a codebase for security issues
- `code-verification`: Verify AI-generated code before merging
- `debugging`: Debug a failure systematically
- `testing`: Write effective tests

## How to use ForgeHub

1. Read this map to understand what exists.
2. Search: `forgehub search <query>`
3. Show: `forgehub show <id>`
4. Describe a module: `forgehub describe <module>`
5. Inject context for a task: `forgehub inject <task>`

## Rules for AI agents

- Prefer the right tool over reimplementing.
- Study only the relevant playbooks, not all of them.
- Verify results with tests (MATRIX eval loop).
- Never trust stale knowledge: check provenance and TTL.
- Compress context with SOLAR before sending to an LLM.
- Use FORGE for code quality, SOLAR for efficiency, Helix for observability.
- Use MATRIX tasks to measure whether you actually improved.

## Extending ForgeHub

Adding a new module:
1. Create `forgehub/modules/<id>.py` with a `MODULE = Module(...)` object.
2. Add tool schemas in `tools/<module>.<tool>.json`.
3. Add playbooks in `knowledge/<id>.md`.
4. Restart ForgeHub - auto-discovered, no core changes needed.

This is how future modules plug in.
