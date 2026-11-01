---
id: security-scan
title: "Scan a codebase for security issues"
module: forge
when: "you need to find vulnerabilities in code"
steps:
  - "Run SAST (semgrep, bandit, gosec)"
  - "Check dependencies (pip-audit, govulncheck)"
  - "Generate SBOM (CycloneDX)"
  - "Review findings, filter false positives"
  - "Export as SARIF for CI integration"
pitfalls:
  - "SAST has false positives - review before fixing"
  - "Don't ignore low-severity findings in auth/payment code"
  - "Keep SBOM updated on every release"
verify:
  - "no critical/high findings unaddressed"
  - "SBOM generated and stored"
tags: [security, sast, sbom, forge]
provenance:
  source: internal
  created: 2026-11-01
  confidence: 0.9
  ttl_days: 365
---

# Security Scan

## When to use
When you need to find and fix security issues.

## How
1. Run static analysis (SAST).
2. Audit dependencies.
3. Generate SBOM.
4. Triage findings.
5. Export report.
