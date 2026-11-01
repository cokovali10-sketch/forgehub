---
id: testing
title: "Write effective tests"
module: forge
when: "you need to add or improve tests"
steps:
  - "Test behavior, not implementation"
  - "Cover happy path, edge cases, error cases"
  - "Use descriptive test names"
  - "Keep tests fast and isolated"
  - "Don't test private internals"
pitfalls:
  - "Flaky tests are worse than no tests"
  - "Don't over-mock - test real behavior"
  - "100% coverage doesn't mean 100% correct"
verify:
  - "tests are deterministic"
  - "tests fail when behavior changes"
tags: [testing, forge]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.95
  ttl_days: 365
---

# Testing

## When to use
When adding or improving tests.

## How
1. Test behavior.
2. Cover edges.
3. Descriptive names.
4. Fast and isolated.
