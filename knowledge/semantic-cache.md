---
id: semantic-cache
title: "Cache LLM responses by semantic similarity"
module: solar
when: "you want to avoid repeated LLM calls for similar questions"
steps:
  - "Normalize the prompt (lowercase, collapse whitespace)"
  - "Check exact hash match first"
  - "If miss, compute embedding and search by cosine similarity"
  - "In safe mode, only reuse if context fingerprint matches"
  - "Store new responses with verified=false; mark verified on reuse"
pitfalls:
  - "Bag-of-words embeddings have false positives on short prompts"
  - "Always check context fingerprint in safe mode"
  - "TTL and LRU eviction prevent unbounded growth"
verify:
  - "cache hit rate is measurable"
  - "no false positives on verified entries"
tags: [cache, tokens, solar]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.85
  ttl_days: 90
---

# Semantic Cache

## When to use
When the same or similar questions are asked repeatedly.

## How
1. Normalize prompt to a canonical form.
2. Exact hash lookup (O(1)).
3. Semantic fallback (cosine on hashing embedder).
4. Safe mode: require matching context fingerprint + verified flag.

## Key rule
**A cached answer is only as good as the context it was generated in.**
Always check the fingerprint.
