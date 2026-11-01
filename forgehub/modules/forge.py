from forgehub.registry import Module

MODULE = Module(
    id="forge",
    name="FORGE",
    tagline="Code quality and verification platform",
    purpose="Verify, audit and improve code: SAST/DAST/SBOM, policy enforcement, "
            "report export, pipeline orchestration.",
    when_to_use=[
        "You need to scan code for vulnerabilities or quality issues",
        "You need to generate an SBOM or SARIF report",
        "You need policy enforcement on a codebase",
        "You need to run a full verification pipeline",
    ],
    when_not_to_use=[
        "You only need to edit a single file (use an editor directly)",
        "You need runtime observability (use Helix)",
    ],
    cli="qorvex",
    env_vars=["QORVEX_PORT"],
    tools=["forge.scan", "forge.verify", "forge.sbom", "forge.report"],
    knowledge=["code-review", "security-scan", "sbom-generation"],
    docs_url="https://github.com/cokovali10-sketch/qorvex",
    status="active",
    tags=["security", "sast", "dast", "sbom", "quality"],
)
