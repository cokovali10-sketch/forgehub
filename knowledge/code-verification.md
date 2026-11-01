---
id: code-verification
title: "Verify AI-generated code before merging"
module: qorvex
when: "you have code produced by an LLM and need to verify it"
steps:
  - "Run static analysis (lint, type check)"
  - "Run existing tests"
  - "Check policy rules (no hardcoded secrets, no unsafe calls)"
  - "Run in sandbox if untrusted"
  - "Generate SBOM for dependencies"
  - "Export report (SARIF/JSON/HTML)"
pitfalls:
  - "LLM code often looks correct but has subtle bugs"
  - "Always run tests, don't just read the code"
  - "Sandbox has limits: network isolation not enforced"
verify:
  - "all tests pass"
  - "no policy violations"
  - "sandbox execution succeeded"
tags: [verification, security, qorvex]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.9
  ttl_days: 365
---

# Code Verification

## When to use
When you have code produced by an LLM and need to verify it before merging.

## How
1. Static analysis.
2. Run tests.
3. Policy check.
4. Sandbox execution (if untrusted).
5. SBOM + report.
