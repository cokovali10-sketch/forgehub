from forgehub.registry import Module

MODULE = Module(
    id="matrix",
    name="MATRIX",
    tagline="Artificial work environment for AI capability growth",
    purpose="Knowledge space, tool space, task space with tests, memory space, "
            "simulation space, evaluation space. Improves AI via retrieval, "
            "tools and feedback - not weight changes.",
    when_to_use=[
        "You want an AI to learn from curated tasks with tests",
        "You need a tool registry with JSON schemas",
        "You want to measure whether an AI improves on repeated tasks",
        "You need a sandboxed simulation environment",
    ],
    when_not_to_use=[
        "You expect the model weights to change (they won't - this is retrieval)",
        "You need a production code editor (use FORGE)",
    ],
    cli="matrix",
    env_vars=[],
    tools=["matrix.task", "matrix.eval", "matrix.memory"],
    knowledge=["task-design", "eval-harness", "tool-registry"],
    docs_url="https://github.com/cokovali10-sketch/matrix",
    status="planned",
    tags=["learning", "eval", "knowledge", "memory", "tasks"],
)
