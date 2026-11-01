"""CLI for ForgeHub."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .registry import ForgeHub


def _hub(args) -> ForgeHub:
    root = getattr(args, "root", None)
    return ForgeHub(root)


def cmd_list(args) -> int:
    hub = _hub(args)
    print("Modules:")
    for m in hub.list_modules():
        print(f"  {m.id:<10} {m.name:<10} [{m.status}] {m.tagline}")
    print()
    print(f"Tools: {len(hub.tools)}  Knowledge: {len(hub.knowledge)}")
    return 0


def cmd_search(args) -> int:
    hub = _hub(args)
    results = hub.search(args.query, limit=args.limit)
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
    # try knowledge first, then tool, then module
    if args.id in hub.knowledge:
        k = hub.knowledge[args.id]
        print(f"# {k.title}")
        print(f"Module: {k.module}")
        if k.when:
            print(f"When: {k.when}")
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
    text = hub.ai_context()
    print(text)
    return 0


def cmd_inject(args) -> int:
    hub = _hub(args)
    task = args.task if hasattr(args, "task") else " ".join(args.task_words)
    text = hub.inject(task, use_solar=args.solar)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)
    return 0


def cmd_modules(args) -> int:
    hub = _hub(args)
    for m in hub.list_modules():
        print(hub.describe(m.id))
        print("-" * 60)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forgehub", description="ForgeHub - AI knowledge and tool registry")
    parser.add_argument("--root", "-r", default=None, help="project root (default: cwd)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="list modules, tools and knowledge")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("search", help="search modules/tools/knowledge")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)
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
    p.add_argument("--output", "-o", default=None)
    p.set_defaults(func=cmd_inject)

    p = sub.add_parser("modules", help="describe all modules")
    p.set_defaults(func=cmd_modules)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
