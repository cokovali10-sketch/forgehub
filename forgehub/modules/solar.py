from forgehub.registry import Module

MODULE = Module(
    id="solar",
    name="SOLAR",
    tagline="Token optimization layer for LLM workflows",
    purpose="Reduce token usage without losing correctness: compress prompts, "
            "select relevant context, cache answers, route models, enforce budgets.",
    when_to_use=[
        "You need to send a long prompt or large context to an LLM",
        "You want to cache repeated questions",
        "You need to pick the cheapest model for a task",
        "You need to enforce a token budget",
        "You want to compress verbose instructions or logs",
    ],
    when_not_to_use=[
        "The prompt is already short and code-heavy (compression won't help)",
        "You need exact token counts (use tiktoken directly)",
    ],
    cli="solar",
    env_vars=["SOLAR_DB", "SOLAR_MODEL", "OPENAI_BASE_URL", "SOLAR_ROUTER"],
    tools=["solar.compress", "solar.context", "solar.cache", "solar.optimize"],
    knowledge=["prompt-compression", "context-optimization", "semantic-cache"],
    docs_url="https://github.com/cokovali10-sketch/solar",
    status="active",
    tags=["tokens", "compression", "cache", "routing", "budget"],
)
