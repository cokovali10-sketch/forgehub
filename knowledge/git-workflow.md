---
id: git-workflow
title: "Git workflow best practices"
module: forge
when: "you need to manage branches, commits or PRs"
steps:
  - "Create a feature branch from main"
  - "Make small, focused commits"
  - "Write clear commit messages (conventional commits)"
  - "Open a PR with description and checklist"
  - "Review, then merge"
pitfalls:
  - "Don't commit directly to main"
  - "Don't mix unrelated changes in one commit"
  - "Don't force-push shared branches"
verify:
  - "CI passes"
  - "PR reviewed and approved"
tags: [git, workflow, forge]
related: [code-review, testing]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.95
  ttl_days: 365
---

# Git Workflow

## When to use
When managing branches, commits or PRs.

## How
1. Feature branch.
2. Small commits.
3. Conventional commit messages.
4. PR with checklist.
5. Review and merge.
