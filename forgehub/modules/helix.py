from forgehub.registry import Module

MODULE = Module(
    id="helix",
    name="Helix",
    tagline="SOC observability platform with custom TSDB",
    purpose="Full observability: event collection, ingestion, storage (TSDB), "
            "query, alerting, dashboards, Kubernetes deployment.",
    when_to_use=[
        "You need to collect and store time-series events at scale",
        "You need multi-tenant observability",
        "You need a Prometheus/ClickHouse replacement tuned for SOC",
        "You need alerting and dashboards",
    ],
    when_not_to_use=[
        "You need a simple metrics library (use prometheus client)",
        "You need log aggregation only (use Loki)",
    ],
    cli="helix",
    env_vars=[],
    tools=["helix.ingest", "helix.query", "helix.alert"],
    knowledge=["tsdb-design", "observability", "multi-tenancy"],
    docs_url="https://github.com/cokovali10-sketch/helix",
    status="beta",
    tags=["observability", "tsdb", "soc", "kubernetes", "rust", "go"],
)
