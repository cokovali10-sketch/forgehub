---
id: api-design
title: "Design a REST API"
module: forge
when: "you need to design or review an API"
steps:
  - "Define resources and endpoints (nouns, not verbs)"
  - "Use standard HTTP methods (GET, POST, PUT, PATCH, DELETE)"
  - "Use consistent status codes"
  - "Version the API (/v1/)"
  - "Document with OpenAPI/Swagger"
  - "Handle errors consistently (error envelope)"
pitfalls:
  - "Don't use verbs in URLs"
  - "Don't break backward compatibility without versioning"
  - "Don't return 200 for errors"
verify:
  - "OpenAPI spec valid"
  - "All endpoints documented"
  - "Error responses consistent"
tags: [api, design, forge]
related: [code-review, testing]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.9
  ttl_days: 365
---

# API Design

## When to use
When designing or reviewing a REST API.

## How
1. Resources as nouns.
2. Standard HTTP methods.
3. Consistent status codes.
4. Version the API.
5. Document with OpenAPI.
