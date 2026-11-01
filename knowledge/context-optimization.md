---
id: context-optimization
title: "Select relevant project context within a token budget"
module: solar
when: "you need to send project files to an LLM but can't send everything"
steps:
  - "Rank files by relevance to the query (path + content overlap, changed bonus, test bonus)"
  - "Extract the best line window per file"
  - "Add dependency summaries (public defs of imported modules)"
  - "Include git diff and compact structure tree"
  - "Stop when token budget is reached"
pitfalls:
  - "Don't send the whole repo - pick the relevant subset"
  - "Changed files deserve a bonus in ranking"
  - "Budget should be conservative (1500 tokens default)"
verify:
  - "context_tokens <= budget_tokens"
  - "files selected have score > 0"
tags: [context, files, solar]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.9
  ttl_days: 180
---

# Context Optimization

## When to use
When an LLM needs project context but you can't afford to send everything.

## How
1. Walk the project, collect candidate files.
2. Score each by keyword overlap with the query.
3. Bonus for changed files, test files, manifests.
4. Extract best line window, add dependency summaries.
5. Stop at budget.

## Key rule
**Send the smallest set of snippets that lets the model answer correctly.**
