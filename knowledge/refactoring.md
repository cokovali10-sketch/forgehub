---
id: refactoring
title: "Refactor code safely"
module: forge
when: "you need to improve code structure without changing behavior"
steps:
  - "Ensure tests exist and pass before starting"
  - "Make one small change at a time"
  - "Run tests after each change"
  - "Keep the diff minimal and focused"
  - "Don't mix refactoring with feature changes"
pitfalls:
  - "Big bang refactors break things - go incremental"
  - "Don't refactor code you don't understand"
  - "Preserve public API unless explicitly changing it"
verify:
  - "all tests still pass"
  - "behavior unchanged (no new features)"
  - "diff is reviewable"
tags: [refactoring, quality, forge]
related: [testing, code-review]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.95
  ttl_days: 365
---

# Refactoring

## When to use
When improving code structure without changing behavior.

## How
1. Tests first.
2. Small changes.
3. Run tests each time.
4. Minimal diff.
