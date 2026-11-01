from forgehub.registry import Module

MODULE = Module(
    id="aegisx",
    name="AegisX",
    tagline="Autonomous XDR/SOAR platform",
    purpose="Autonomous extended detection and response: honeypots, eBPF, "
            "AI threat scoring, automated response playbooks.",
    when_to_use=[
        "You need XDR/SOAR capabilities",
        "You need honeypots and deception",
        "You need AI threat scoring",
        "You need automated incident response",
    ],
    when_not_to_use=[
        "You need a simple log viewer",
        "You need a single-purpose scanner",
    ],
    cli="aegisx",
    env_vars=[],
    tools=["aegisx.detect", "aegisx.respond", "aegisx.honeypot"],
    knowledge=["xdr", "soar", "threat-scoring", "honeypots"],
    docs_url="https://github.com/cokovali10-sketch/AegisX-",
    status="active",
    tags=["security", "xdr", "soar", "honeypots", "ai"],
)
