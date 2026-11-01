---
id: logging
title: "Add effective logging"
module: forge
when: "you need to add or improve logging"
steps:
  - "Use structured logging (JSON) in production"
  - "Log at appropriate levels (debug/info/warn/error)"
  - "Include context (request id, user, operation)"
  - "Don't log secrets or PII"
  - "Log errors with full stack traces"
pitfalls:
  - "Too much logging = noise and cost"
  - "Too little logging = blind debugging"
  - "Never log passwords, tokens, or keys"
verify:
  - "logs are structured and searchable"
  - "no secrets in logs"
tags: [logging, forge]
related: [error-handling, debugging]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.95
  ttl_days: 365
---

# Logging

## When to use
When adding or improving logging.

## How
1. Structured (JSON).
2. Appropriate levels.
3. Context included.
4. No secrets.
