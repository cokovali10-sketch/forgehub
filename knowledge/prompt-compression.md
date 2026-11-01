---
id: prompt-compression
title: "Compress prompts without breaking code"
module: solar
when: "you need to reduce token count of a long prompt or instructions"
steps:
  - "Identify protected spans: code fences, inline code, identifiers, paths, numbers, quotes"
  - "Split text into protected and prose parts"
  - "Compress only prose: remove filler, replace verbose phrases, dedup sentences"
  - "Verify integrity: every protected span must survive verbatim"
  - "If integrity fails or savings below threshold, keep original"
pitfalls:
  - "Never compress code, identifiers or paths - the model will invent APIs"
  - "Constraint sentences (must/never/only/limit) must survive"
  - "Log compression can lose error context if not careful"
verify:
  - "integrity_ok == true"
  - "protected spans present in output"
tags: [compression, tokens, solar]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.95
  ttl_days: 180
---

# Prompt Compression

## When to use
When a prompt is verbose and contains natural-language instructions alongside code.

## How
1. Protect code spans first (regex: fenced code, inline code, identifiers, paths, numbers, quotes).
2. Compress only the prose between them.
3. Verify every protected span survived.
4. If verification fails, return the original untouched.

## Key rule
**Code is never rewritten.** Only prose is compressible. This is what keeps token savings from turning into "the model invented an API".
