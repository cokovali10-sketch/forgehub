"""Central registry for ForgeHub.

Everything is a plugin:
- modules:  forgehub/modules/*.py  (each defines a `MODULE` object)
- tools:    tools/*.json           (JSON Schema + metadata)
- knowledge: knowledge/*.md       (markdown with YAML frontmatter)

ForgeHub discovers them at runtime. Adding a capability = adding a file.
"""

from __future__ import annotations

import importlib.util
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


@dataclass
class Tool:
    id: str
    name: str
    module: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    safety: list[str] = field(default_factory=list)
    example: str = ""
    tags: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "module": self.module,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "safety": self.safety,
            "example": self.example,
            "tags": self.tags,
        }


@dataclass
class KnowledgeEntry:
    id: str
    title: str
    module: str = ""
    when: str = ""
    steps: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    pitfalls: list[str] = field(default_factory=list)
    verify: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    body: str = ""
    tags: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "module": self.module,
            "when": self.when,
            "steps": self.steps,
            "tools": self.tools,
            "pitfalls": self.pitfalls,
            "verify": self.verify,
            "provenance": self.provenance,
            "body": self.body,
            "tags": self.tags,
        }


@dataclass
class Module:
    id: str
    name: str
    tagline: str
    purpose: str
    when_to_use: list[str] = field(default_factory=list)
    when_not_to_use: list[str] = field(default_factory=list)
    cli: str = ""
    env_vars: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)  # tool ids
    knowledge: list[str] = field(default_factory=list)  # knowledge ids
    docs_url: str = ""
    status: str = "active"  # active | beta | planned
    tags: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "tagline": self.tagline,
            "purpose": self.purpose,
            "when_to_use": self.when_to_use,
            "when_not_to_use": self.when_not_to_use,
            "cli": self.cli,
            "env_vars": self.env_vars,
            "tools": self.tools,
            "knowledge": self.knowledge,
            "docs_url": self.docs_url,
            "status": self.status,
            "tags": self.tags,
        }


class ForgeHub:
    """The central registry. Discovers plugins from disk."""

    def __init__(self, root: str | os.PathLike[str] | None = None):
        self.root = Path(root) if root else Path.cwd()
        self.modules: dict[str, Module] = {}
        self.tools: dict[str, Tool] = {}
        self.knowledge: dict[str, KnowledgeEntry] = {}
        self._load()

    # ---------------------------------------------------------------- discovery
    def _load(self) -> None:
        self._load_modules()
        self._load_tools()
        self._load_knowledge()

    def _load_modules(self) -> None:
        modules_dir = self.root / "forgehub" / "modules"
        if not modules_dir.exists():
            # allow running from a different cwd: try package-relative
            modules_dir = Path(__file__).parent / "modules"
        if not modules_dir.exists():
            return
        for path in sorted(modules_dir.glob("*.py")):
            if path.name.startswith("_"):
                continue
            spec = importlib.util.spec_from_file_location(path.stem, path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception:
                continue
            obj = getattr(module, "MODULE", None)
            if isinstance(obj, Module):
                self.modules[obj.id] = obj

    def _load_tools(self) -> None:
        tools_dir = self.root / "tools"
        if not tools_dir.exists():
            tools_dir = Path(__file__).parent.parent / "tools"
        if not tools_dir.exists():
            return
        for path in sorted(tools_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            tool = Tool(
                id=data.get("id", path.stem),
                name=data.get("name", path.stem),
                module=data.get("module", ""),
                description=data.get("description", ""),
                input_schema=data.get("input_schema", {}),
                output_schema=data.get("output_schema", {}),
                safety=data.get("safety", []),
                example=data.get("example", ""),
                tags=data.get("tags", []),
            )
            self.tools[tool.id] = tool

    def _load_knowledge(self) -> None:
        knowledge_dir = self.root / "knowledge"
        if not knowledge_dir.exists():
            knowledge_dir = Path(__file__).parent.parent / "knowledge"
        if not knowledge_dir.exists():
            return
        for path in sorted(knowledge_dir.glob("*.md")):
            entry = self._parse_knowledge(path)
            if entry is not None:
                self.knowledge[entry.id] = entry

    def _parse_knowledge(self, path: Path) -> KnowledgeEntry | None:
        text = path.read_text(encoding="utf-8")
        # split frontmatter
        frontmatter: dict[str, Any] = {}
        body = text
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    import yaml
                except ImportError:
                    yaml = None
                if yaml is not None:
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                    except Exception:
                        frontmatter = {}
                else:
                    frontmatter = _parse_simple_frontmatter(parts[1])
                body = parts[2].strip()
        entry_id = frontmatter.get("id", path.stem)
        return KnowledgeEntry(
            id=entry_id,
            title=frontmatter.get("title", path.stem),
            module=frontmatter.get("module", ""),
            when=frontmatter.get("when", ""),
            steps=frontmatter.get("steps", []) or [],
            tools=frontmatter.get("tools", []) or [],
            pitfalls=frontmatter.get("pitfalls", []) or [],
            verify=frontmatter.get("verify", []) or [],
            provenance=frontmatter.get("provenance", {}) or {},
            body=body,
            tags=frontmatter.get("tags", []) or [],
        )

    # ---------------------------------------------------------------- query
    def list_modules(self) -> list[Module]:
        return sorted(self.modules.values(), key=lambda m: m.id)

    def get_module(self, module_id: str) -> Module | None:
        return self.modules.get(module_id)

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search modules, tools and knowledge by keyword overlap."""
        terms = set(query.lower().split())
        scored: list[tuple[float, str, Any]] = []

        for m in self.modules.values():
            haystack = " ".join(
                [m.id, m.name, m.tagline, m.purpose] + m.when_to_use + m.tags
            ).lower()
            score = sum(1 for t in terms if t in haystack)
            if score > 0:
                scored.append((score, "module", m))

        for t in self.tools.values():
            haystack = " ".join(
                [t.id, t.name, t.description, t.module] + t.tags
            ).lower()
            score = sum(1 for term in terms if term in haystack)
            if score > 0:
                scored.append((score, "tool", t))

        for k in self.knowledge.values():
            haystack = " ".join(
                [k.id, k.title, k.when, k.body] + k.tools + k.tags
            ).lower()
            score = sum(1 for term in terms if term in haystack)
            if score > 0:
                scored.append((score, "knowledge", k))

        scored.sort(key=lambda x: (-x[0], x[1]))
        results = []
        for score, kind, obj in scored[:limit]:
            results.append({"kind": kind, "score": score, "item": obj.as_dict()})
        return results

    def describe(self, module_id: str) -> str:
        m = self.get_module(module_id)
        if m is None:
            return f"Unknown module: {module_id}"
        lines = [
            f"# {m.name} ({m.id})",
            f"**{m.tagline}**",
            "",
            m.purpose,
            "",
        ]
        if m.when_to_use:
            lines.append("## When to use")
            for w in m.when_to_use:
                lines.append(f"- {w}")
            lines.append("")
        if m.when_not_to_use:
            lines.append("## When NOT to use")
            for w in m.when_not_to_use:
                lines.append(f"- {w}")
            lines.append("")
        if m.cli:
            lines.append(f"**CLI:** `{m.cli}`")
        if m.env_vars:
            lines.append(f"**Env:** {', '.join(m.env_vars)}")
        if m.tools:
            lines.append(f"**Tools:** {', '.join(m.tools)}")
        if m.knowledge:
            lines.append(f"**Knowledge:** {', '.join(m.knowledge)}")
        if m.docs_url:
            lines.append(f"**Docs:** {m.docs_url}")
        return "\n".join(lines)

    def ai_context(self) -> str:
        """Generate a machine-readable map of the whole ecosystem for an AI agent."""
        lines = [
            "# ForgeHub - AI Context Map",
            "",
            "You are an AI agent with access to the ForgeHub ecosystem.",
            "ForgeHub is a registry of modules, tools and playbooks. Before acting,",
            "study the relevant entries. Use the right tool for the task.",
            "",
            "## Available modules",
            "",
        ]
        for m in self.list_modules():
            lines.append(f"### {m.name} (`{m.id}`) — {m.tagline}")
            lines.append(m.purpose)
            if m.when_to_use:
                lines.append("Use when:")
                for w in m.when_to_use:
                    lines.append(f"  - {w}")
            if m.cli:
                lines.append(f"CLI: `{m.cli}`")
            lines.append("")
        lines.append("## Available tools")
        lines.append("")
        for t in sorted(self.tools.values(), key=lambda x: x.id):
            lines.append(f"- `{t.id}` ({t.module}): {t.description}")
        lines.append("")
        lines.append("## Available playbooks (knowledge)")
        lines.append("")
        for k in sorted(self.knowledge.values(), key=lambda x: x.id):
            lines.append(f"- `{k.id}`: {k.title} — {k.when}")
        lines.append("")
        lines.append("## How to use ForgeHub")
        lines.append("")
        lines.append("1. Read this map to understand what exists.")
        lines.append("2. Search: `forgehub search <query>`")
        lines.append("3. Show: `forgehub show <id>`")
        lines.append("4. Describe a module: `forgehub describe <module>`")
        lines.append("5. Inject context for a task: `forgehub inject <task>`")
        lines.append("")
        lines.append("## Rules for AI agents")
        lines.append("")
        lines.append("- Prefer the right tool over reimplementing.")
        lines.append("- Study only the relevant playbooks, not all of them.")
        lines.append("- Verify results with tests (MATRIX eval loop).")
        lines.append("- Never trust stale knowledge: check provenance and TTL.")
        lines.append("- Compress context with SOLAR before sending to an LLM.")
        return "\n".join(lines)

    def inject(self, task: str, use_solar: bool = False) -> str:
        """Build a context bundle for a task from relevant playbooks + tools."""
        results = self.search(task, limit=8)
        lines = [f"# ForgeHub context for: {task}", ""]
        modules_seen: set[str] = set()
        for r in results:
            item = r["item"]
            if r["kind"] == "knowledge":
                lines.append(f"## Playbook: {item['title']} (`{item['id']}`)")
                if item.get("when"):
                    lines.append(f"When: {item['when']}")
                if item.get("steps"):
                    lines.append("Steps:")
                    for s in item["steps"]:
                        lines.append(f"  - {s}")
                if item.get("pitfalls"):
                    lines.append("Pitfalls:")
                    for p in item["pitfalls"]:
                        lines.append(f"  - {p}")
                if item.get("verify"):
                    lines.append("Verify:")
                    for v in item["verify"]:
                        lines.append(f"  - {v}")
                if item.get("body"):
                    lines.append("")
                    lines.append(item["body"][:1500])
                lines.append("")
                if item.get("module"):
                    modules_seen.add(item["module"])
            elif r["kind"] == "tool":
                lines.append(f"## Tool: {item['name']} (`{item['id']}`)")
                lines.append(item["description"])
                if item.get("safety"):
                    lines.append("Safety: " + "; ".join(item["safety"]))
                lines.append("")
            elif r["kind"] == "module":
                lines.append(f"## Module: {item['name']} (`{item['id']}`)")
                lines.append(item["purpose"])
                if item.get("cli"):
                    lines.append(f"CLI: `{item['cli']}`")
                lines.append("")

        if modules_seen:
            lines.append("## Relevant modules")
            for mid in sorted(modules_seen):
                m = self.get_module(mid)
                if m:
                    lines.append(f"- {m.name}: {m.tagline} (CLI: `{m.cli}`)")
            lines.append("")

        text = "\n".join(lines)
        if use_solar:
            try:
                from solar.compress import compress_text
                from solar.config import CompressionConfig

                result = compress_text(text, level="balanced")
                return result.compressed
            except Exception:
                pass
        return text


def _parse_simple_frontmatter(text: str) -> dict[str, Any]:
    """Minimal YAML-ish frontmatter parser (no yaml dependency)."""
    result: dict[str, Any] = {}
    current_key: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped and not stripped.startswith("-"):
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "" or value == "[]":
                result[key] = []
                current_key = key
            elif value.startswith("[") and value.endswith("]"):
                items = [x.strip().strip("\"'") for x in value[1:-1].split(",") if x.strip()]
                result[key] = items
                current_key = None
            else:
                result[key] = value.strip("\"'")
                current_key = None
        elif stripped.startswith("-") and current_key is not None:
            item = stripped[1:].strip().strip("\"'")
            result.setdefault(current_key, [])
            if isinstance(result[current_key], list):
                result[current_key].append(item)
    return result
