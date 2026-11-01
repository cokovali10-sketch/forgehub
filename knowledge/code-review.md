---
id: code-review
title: "Review code for quality and correctness"
module: forge
when: "you need to review a pull request or code change"
steps:
  - "Read the diff and understand the intent"
  - "Check for bugs, edge cases, off-by-one errors"
  - "Check for security issues (injection, auth, secrets)"
  - "Check for performance regressions"
  - "Verify tests exist and pass"
  - "Suggest improvements, not just problems"
pitfalls:
  - "Don't nitpick style if there's no formatter configured"
  - "Don't block on personal preference"
  - "Always check the tests, not just the code"
verify:
  - "all existing tests pass"
  - "no new security issues introduced"
tags: [review, quality, forge]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.9
  ttl_days: 365
---

# Code Review

## When to use
When reviewing a PR or code change.

## How
1. Understand intent from commit message + diff.
2. Check correctness, edge cases, security.
3. Verify tests.
4. Give actionable feedback.
