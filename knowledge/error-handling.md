---
id: error-handling
title: "Handle errors properly"
module: forge
when: "you need to add or improve error handling"
steps:
  - "Fail fast with clear messages"
  - "Don't swallow exceptions silently"
  - "Use specific exception types"
  - "Log with context (what, where, why)"
  - "Return meaningful errors to users"
  - "Clean up resources (finally/with/defer)"
pitfalls:
  - "Bare except: hides bugs"
  - "Logging and re-raising is fine; swallowing is not"
  - "Don't leak internal details to users"
verify:
  - "errors are logged with context"
  - "users get actionable messages"
tags: [errors, forge]
related: [debugging, logging]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.95
  ttl_days: 365
---

# Error Handling

## When to use
When adding or improving error handling.

## How
1. Fail fast.
2. Specific exceptions.
3. Log with context.
4. Clean up resources.
