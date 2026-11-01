---
id: dependency-management
title: "Manage dependencies properly"
module: forge
when: "you need to add or update dependencies"
steps:
  - "Pin versions (lock files)"
  - "Audit for vulnerabilities"
  - "Keep dependencies minimal"
  - "Update regularly, not all at once"
  - "Test after updating"
pitfalls:
  - "Unpinned deps break builds"
  - "Unused deps bloat and add risk"
  - "Major version bumps need migration"
verify:
  - "lock file committed"
  - "no known vulnerabilities"
  - "tests pass after update"
tags: [dependencies, forge]
related: [security-scan, configuration]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.9
  ttl_days: 365
---

# Dependency Management

## When to use
When managing dependencies.

## How
1. Pin versions.
2. Audit vulnerabilities.
3. Minimal deps.
4. Update regularly.
5. Test after update.
