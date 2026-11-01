from forgehub.registry import Module

MODULE = Module(
    id="agentmesh",
    name="AgentMesh",
    tagline="Multi-agent AI orchestration framework",
    purpose="Orchestrate multiple AI agents: planner, router, layered memory, "
            "MCP tools, web panel.",
    when_to_use=[
        "You need to coordinate multiple AI agents",
        "You need a planner/router/memory system",
        "You need MCP tool integration",
        "You need a web panel for agent management",
    ],
    when_not_to_use=[
        "You need a single agent (use SOLAR)",
        "You need a code editor",
    ],
    cli="agentmesh",
    env_vars=[],
    tools=["agentmesh.plan", "agentmesh.route", "agentmesh.memory"],
    knowledge=["multi-agent", "orchestration", "mcp"],
    docs_url="https://github.com/cokovali10-sketch/AgentMesh",
    status="active",
    tags=["ai", "agents", "orchestration", "mcp", "memory"],
)
