from forgehub.registry import Module

MODULE = Module(
    id="apexguard",
    name="ApexGuard",
    tagline="Autonomous enterprise defense cluster",
    purpose="Enterprise defense: eBPF tracing, AI deception, threat detection, "
            "automated response.",
    when_to_use=[
        "You need endpoint detection and response (EDR)",
        "You need eBPF-based tracing",
        "You need AI-driven deception/honeypots",
        "You need automated threat response",
    ],
    when_not_to_use=[
        "You need a simple firewall",
        "You need log aggregation only",
    ],
    cli="apexguard",
    env_vars=[],
    tools=["apexguard.scan", "apexguard.defend"],
    knowledge=["threat-detection", "edr", "eBPF"],
    docs_url="https://github.com/cokovali10-sketch/ApexGuard",
    status="active",
    tags=["security", "edr", "ebpf", "defense"],
)
