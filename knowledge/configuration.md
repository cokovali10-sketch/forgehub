---
id: configuration
title: "Manage configuration properly"
module: forge
when: "you need to add or manage app configuration"
steps:
  - "Use env vars for secrets and deployment-specific values"
  - "Use config files for structured settings"
  - "Validate config at startup (fail fast)"
  - "Provide sensible defaults"
  - "Document all config options"
pitfalls:
  - "Don't hardcode secrets"
  - "Don't commit .env files"
  - "Validate early, not at runtime"
verify:
  - "app fails fast on bad config"
  - "all options documented"
tags: [config, forge]
related: [error-handling]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.95
  ttl_days: 365
---

# Configuration

## When to use
When managing app configuration.

## How
1. Env vars for secrets.
2. Config files for settings.
3. Validate at startup.
4. Sensible defaults.
