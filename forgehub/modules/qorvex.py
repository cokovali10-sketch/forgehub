from forgehub.registry import Module

MODULE = Module(
    id="qorvex",
    name="Qorvex",
    tagline="AI code verification platform",
    purpose="Verify AI-generated code: SAST/DAST/SBOM, policy enforcement, "
            "audit trails, isolated execution (Rust sandbox).",
    when_to_use=[
        "You need to verify code produced by an LLM",
        "You need to run untrusted code in a sandbox",
        "You need SBOM generation or SARIF reports",
        "You need policy enforcement on a codebase",
    ],
    when_not_to_use=[
        "You need a code editor or IDE",
        "You need runtime observability (use Helix)",
    ],
    cli="qorvex",
    env_vars=["QORVEX_PORT"],
    tools=["qorvex.scan", "qorvex.sandbox", "qorvex.sbom", "qorvex.report"],
    knowledge=["code-verification", "sandboxing", "sast", "dast"],
    docs_url="https://github.com/cokovali10-sketch/qorvex",
    status="active",
    tags=["security", "verification", "sandbox", "sast", "sbom"],
)
