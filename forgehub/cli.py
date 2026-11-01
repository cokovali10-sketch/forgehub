"""CLI for ForgeHub."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .registry import ForgeHub


def _hub(args) -> ForgeHub:
    root = getattr(args, "root", None)
    db = getattr(args, "db", None)
    return ForgeHub(root, db_path=db)


def cmd_list(args) -> int:
    hub = _hub(args)
    print("Modules:")
    for m in hub.list_modules():
        print(f"  {m.id:<10} {m.name:<10} [{m.status}] {m.tagline}")
    print()
    print(f"Tools: {len(hub.tools)}  Knowledge: {len(hub.knowledge)}")
    if hub.validation_errors:
        print(f"Validation errors: {len(hub.validation_errors)}")
    return 0


def cmd_search(args) -> int:
    hub = _hub(args)
    results = hub.search(args.query, limit=args.limit, semantic=not args.keyword)
    if not results:
        print("No results.")
        return 0
    for r in results:
        item = r["item"]
        print(f"[{r['kind']}] {item['id']} (score {r['score']})")
        if r["kind"] == "knowledge":
            print(f"  {item['title']} - {item['when']}")
        elif r["kind"] == "tool":
            print(f"  {item['name']}: {item['description']}")
        elif r["kind"] == "module":
            print(f"  {item['name']}: {item['purpose'][:80]}")
    return 0


def cmd_show(args) -> int:
    hub = _hub(args)
    if args.id in hub.knowledge:
        k = hub.knowledge[args.id]
        print(f"# {k.title}")
        print(f"Module: {k.module}")
        if k.when:
            print(f"When: {k.when}")
        if k.prerequisites:
            print(f"Prerequisites: {', '.join(k.prerequisites)}")
        if k.steps:
            print("\nSteps:")
            for s in k.steps:
                print(f"  - {s}")
        if k.pitfalls:
            print("\nPitfalls:")
            for p in k.pitfalls:
                print(f"  - {p}")
        if k.verify:
            print("\nVerify:")
            for v in k.verify:
                print(f"  - {v}")
        if k.related:
            print(f"\nRelated: {', '.join(k.related)}")
        if k.body:
            print("\n" + k.body)
        return 0
    if args.id in hub.tools:
        t = hub.tools[args.id]
        print(json.dumps(t.as_dict(), indent=2, ensure_ascii=False))
        return 0
    if args.id in hub.modules:
        print(hub.describe(args.id))
        return 0
    print(f"Not found: {args.id}")
    return 1


def cmd_describe(args) -> int:
    hub = _hub(args)
    print(hub.describe(args.module))
    return 0


def cmd_context(args) -> int:
    hub = _hub(args)
    print(hub.ai_context())
    return 0


def cmd_inject(args) -> int:
    hub = _hub(args)
    task = " ".join(args.task_words)
    text = hub.inject(task, use_solar=args.solar, limit=args.limit)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {args.output} ({len(text)} chars)")
    else:
        print(text)
    return 0


def cmd_modules(args) -> int:
    hub = _hub(args)
    for m in hub.list_modules():
        print(hub.describe(m.id))
        print("-" * 60)
    return 0


def cmd_validate(args) -> int:
    hub = _hub(args)
    errors = hub.validate()
    if not errors:
        print(f"OK: {len(hub.modules)} modules, {len(hub.tools)} tools, {len(hub.knowledge)} playbooks validated.")
        return 0
    print(f"Found {len(errors)} issue(s):")
    for e in errors:
        print(f"  - {e}")
    return 1


def cmd_stats(args) -> int:
    hub = _hub(args)
    s = hub.stats()
    if not s.get("enabled"):
        print("Usage tracking disabled (no --db).")
        return 0
    print(f"Total queries: {s['total_queries']}")
    for row in s["by_item"]:
        print(f"  {row['kind']:<10} {row['id']:<25} {row['count']}")
    return 0


def cmd_export(args) -> int:
    hub = _hub(args)
    data = {
        "modules": [m.as_dict() for m in hub.list_modules()],
        "tools": [t.as_dict() for t in hub.tools.values()],
        "knowledge": [k.as_dict() for k in hub.knowledge.values()],
    }
    text = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"exported to {args.output}")
    else:
        print(text)
    return 0


def cmd_mcp(args) -> int:
    """Run ForgeHub as an MCP server (stdio JSON-RPC)."""
    hub = _hub(args)
    # Minimal MCP server over stdio
    import sys as _sys

    def send(obj):
        _sys.stdout.write(json.dumps(obj) + "\n")
        _sys.stdout.flush()

    # Tool definitions
    tools = [
        {
            "name": "forgehub_search",
            "description": "Search ForgeHub modules, tools and playbooks.",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}},
                "required": ["query"],
            },
        },
        {
            "name": "forgehub_show",
            "description": "Show a playbook, tool or module by id.",
            "inputSchema": {
                "type": "object",
                "properties": {"id": {"type": "string"}},
                "required": ["id"],
            },
        },
        {
            "name": "forgehub_describe",
            "description": "Describe a module.",
            "inputSchema": {
                "type": "object",
                "properties": {"module": {"type": "string"}},
                "required": ["module"],
            },
        },
        {
            "name": "forgehub_context",
            "description": "Get the full AI context map.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "forgehub_inject",
            "description": "Build a context bundle for a task.",
            "inputSchema": {
                "type": "object",
                "properties": {"task": {"type": "string"}, "use_solar": {"type": "boolean"}},
                "required": ["task"],
            },
        },
    ]

    for line in _sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        method = req.get("method")
        req_id = req.get("id")

        if method == "initialize":
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "forgehub", "version": "0.1.0"},
                },
            })
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}})
        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            try:
                if name == "forgehub_search":
                    res = hub.search(args.get("query", ""), limit=args.get("limit", 10))
                    text = json.dumps(res, indent=2, ensure_ascii=False)
                elif name == "forgehub_show":
                    # reuse show logic by capturing
                    import io
                    buf = io.StringIO()
                    # manually build
                    item_id = args.get("id", "")
                    if item_id in hub.knowledge:
                        k = hub.knowledge[item_id]
                        parts = [f"# {k.title}", f"Module: {k.module}"]
                        if k.when:
                            parts.append(f"When: {k.when}")
                        if k.steps:
                            parts.append("Steps: " + "; ".join(k.steps))
                        if k.pitfalls:
                            parts.append("Pitfalls: " + "; ".join(k.pitfalls))
                        if k.body:
                            parts.append(k.body[:2000])
                        text = "\n".join(parts)
                    elif item_id in hub.tools:
                        text = json.dumps(hub.tools[item_id].as_dict(), indent=2)
                    elif item_id in hub.modules:
                        text = hub.describe(item_id)
                    else:
                        text = f"Not found: {item_id}"
                elif name == "forgehub_describe":
                    text = hub.describe(args.get("module", ""))
                elif name == "forgehub_context":
                    text = hub.ai_context()
                elif name == "forgehub_inject":
                    text = hub.inject(args.get("task", ""), use_solar=args.get("use_solar", False))
                else:
                    text = f"Unknown tool: {name}"
                send({"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": text}]}})
            except Exception as e:
                send({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}})
        elif method == "notifications/initialized":
            pass
        else:
            if req_id is not None:
                send({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "method not found"}})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forgehub", description="ForgeHub - AI knowledge and tool registry")
    parser.add_argument("--root", "-r", default=None, help="project root (default: cwd)")
    parser.add_argument("--db", default=None, help="usage tracking db path")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="list modules, tools and knowledge")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("search", help="search modules/tools/knowledge")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--keyword", action="store_true", help="keyword-only search")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("show", help="show a knowledge entry, tool or module")
    p.add_argument("id")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("describe", help="describe a module")
    p.add_argument("module")
    p.set_defaults(func=cmd_describe)

    p = sub.add_parser("context", help="print the AI context map")
    p.set_defaults(func=cmd_context)

    p = sub.add_parser("inject", help="build a context bundle for a task")
    p.add_argument("task_words", nargs="+")
    p.add_argument("--solar", action="store_true", help="compress with SOLAR if available")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--output", "-o", default=None)
    p.set_defaults(func=cmd_inject)

    p = sub.add_parser("modules", help="describe all modules")
    p.set_defaults(func=cmd_modules)

    p = sub.add_parser("validate", help="validate all plugins")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("stats", help="usage statistics")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("export", help="export registry as JSON")
    p.add_argument("--output", "-o", default=None)
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("mcp", help="run as MCP server (stdio)")
    p.set_defaults(func=cmd_mcp)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
