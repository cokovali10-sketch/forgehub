---
id: performance
title: "Optimize performance systematically"
module: forge
when: "you need to make code faster or use fewer resources"
steps:
  - "Measure first (profile, don't guess)"
  - "Identify the bottleneck (CPU, memory, I/O, network)"
  - "Optimize the hottest path"
  - "Measure again to confirm improvement"
  - "Don't optimize prematurely"
pitfalls:
  - "Premature optimization wastes time"
  - "Micro-benchmarks lie - measure in production-like conditions"
  - "Readability > micro-performance"
verify:
  - "measurable improvement confirmed"
  - "no regressions"
tags: [performance, forge]
related: [debugging, testing]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.9
  ttl_days: 365
---

# Performance

## When to use
When optimizing performance.

## How
1. Measure.
2. Find bottleneck.
3. Optimize hottest path.
4. Measure again.
5. Don't premature-optimize.
