---
id: debugging
title: "Debug a failure systematically"
module: forge
when: "something is broken and you need to find the root cause"
steps:
  - "Reproduce the failure reliably"
  - "Read the error message and stack trace carefully"
  - "Identify the smallest failing case"
  - "Add a test that reproduces it"
  - "Fix the root cause, not the symptom"
  - "Verify the test passes and no regressions"
pitfalls:
  - "Don't guess - reproduce first"
  - "Don't fix the symptom (e.g. catching the exception)"
  - "Check if the bug exists in tests too"
verify:
  - "failing case now passes"
  - "no regressions in existing tests"
tags: [debugging, forge]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.95
  ttl_days: 365
---

# Debugging

## When to use
When something is broken.

## How
1. Reproduce.
2. Read the error.
3. Minimize.
4. Add a test.
5. Fix root cause.
6. Verify.
