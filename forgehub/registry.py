"""Central registry for ForgeHub.

Everything is a plugin:
- modules:  forgehub/modules/*.py  (each defines a `MODULE` object)
- tools:    tools/*.json           (JSON Schema + metadata)
- knowledge: knowledge/*.md       (markdown with YAML frontmatter)

ForgeHub discovers them at runtime. Adding a capability = adding a file.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


# ---------------------------------------------------------------------------
# Hashing embedder (stdlib-only, reused from SOLAR)
# ---------------------------------------------------------------------------

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for",
    "with", "is", "are", "was", "were", "be", "been", "this", "that", "it",
    "as", "at", "by", "from", "i", "you", "we", "they", "not", "no",
    "how", "what", "when", "where", "why", "which",
}


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}|[\u0430-\u044f\u0410-\u042f\u0401\u0451]{3,}", text.lower())
    return [t for t in tokens if t not in _STOPWORDS]


def _embed(text: str, dim: int = 256) -> list[float]:
    vec = [0.0] * dim
    tokens = _tokenize(text)
    shingles = tokens + [" ".join(tokens[i:i+3]) for i in range(len(tokens) - 2)]
    for feat in shingles:
        digest = hashlib.blake2b(feat.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if (digest[4] & 1) == 0 else -1.0
        weight = 1.0 + (0.5 if " " in feat else 0.0)
        vec[bucket] += sign * weight
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Tool:
    id: str
    name: str
    module: str
    description: str
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)
    safety: list[str] = field(default_factory=list)
    example: str = ""
    tags: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "module": self.module,
            "description": self.description, "input_schema": self.input_schema,
            "output_schema": self.output_schema, "safety": self.safety,
            "example": self.example, "tags": self.tags, "related": self.related,
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
    provenance: dict = field(default_factory=dict)
    body: str = ""
    tags: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    _embedding: list[float] = field(default_factory=list, repr=False)

    def embed(self) -> list[float]:
        if not self._embedding:
            text = " ".join([self.id, self.title, self.when, self.body] + self.tools + self.tags)
            self._embedding = _embed(text)
        return self._embedding

    def as_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title, "module": self.module,
            "when": self.when, "steps": self.steps, "tools": self.tools,
            "pitfalls": self.pitfalls, "verify": self.verify,
            "provenance": self.provenance, "body": self.body,
            "tags": self.tags, "related": self.related,
            "prerequisites": self.prerequisites,
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
    tools: list[str] = field(default_factory=list)
    knowledge: list[str] = field(default_factory=list)
    docs_url: str = ""
    status: str = "active"
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    version: str = "0.1.0"

    def as_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "tagline": self.tagline,
            "purpose": self.purpose, "when_to_use": self.when_to_use,
            "when_not_to_use": self.when_not_to_use, "cli": self.cli,
            "env_vars": self.env_vars, "tools": self.tools,
            "knowledge": self.knowledge, "docs_url": self.docs_url,
            "status": self.status, "tags": self.tags,
            "dependencies": self.dependencies, "version": self.version,
        }


# ---------------------------------------------------------------------------
# ForgeHub registry
# ---------------------------------------------------------------------------


class ForgeHub:
    """Central registry. Discovers plugins from disk."""

    def __init__(self, root=None, db_path=None):
        self.root = Path(root) if root else Path.cwd()
        self.modules: dict[str, Module] = {}
        self.tools: dict[str, Tool] = {}
        self.knowledge: dict[str, KnowledgeEntry] = {}
        self._usage_db = None
        self._usage_lock = threading.Lock()
        if db_path:
            self._init_usage_db(db_path)
        self._load()
        self._validate()

    def _init_usage_db(self, db_path):
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(path), check_same_thread=False)
        conn.execute("""CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL, kind TEXT, item_id TEXT, query TEXT
        )""")
        conn.commit()
        self._usage_db = conn

    def _track(self, kind: str, item_id: str, query: str = ""):
        if self._usage_db is None:
            return
        with self._usage_lock:
            self._usage_db.execute(
                "INSERT INTO usage (ts, kind, item_id, query) VALUES (?,?,?,?)",
                (time.time(), kind, item_id, query[:500]),
            )
            self._usage_db.commit()

    # ---------------------------------------------------------------- discovery
    def _load(self):
        self._load_modules()
        self._load_tools()
        self._load_knowledge()

    def _load_modules(self):
        modules_dir = self.root / "forgehub" / "modules"
        if not modules_dir.exists():
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

    def _load_tools(self):
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
                related=data.get("related", []),
            )
            self.tools[tool.id] = tool

    def _load_knowledge(self):
        knowledge_dir = self.root / "knowledge"
        if not knowledge_dir.exists():
            knowledge_dir = Path(__file__).parent.parent / "knowledge"
        if not knowledge_dir.exists():
            return
        for path in sorted(knowledge_dir.glob("*.md")):
            entry = self._parse_knowledge(path)
            if entry is not None:
                self.knowledge[entry.id] = entry

    def _parse_knowledge(self, path: Path):
        text = path.read_text(encoding="utf-8")
        frontmatter = {}
        body = text
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = _parse_frontmatter(parts[1])
                body = parts[2].strip()
        entry_id = frontmatter.get("id", path.stem)
        provenance = frontmatter.get("provenance", {}) or {}
        # normalize date objects to strings for JSON safety
        provenance = {k: (str(v) if not isinstance(v, (str, int, float, bool, list, dict)) else v) for k, v in provenance.items()}
        return KnowledgeEntry(
            id=entry_id,
            title=frontmatter.get("title", path.stem),
            module=frontmatter.get("module", ""),
            when=frontmatter.get("when", ""),
            steps=frontmatter.get("steps", []) or [],
            tools=frontmatter.get("tools", []) or [],
            pitfalls=frontmatter.get("pitfalls", []) or [],
            verify=frontmatter.get("verify", []) or [],
            provenance=provenance,
            body=body,
            tags=frontmatter.get("tags", []) or [],
            related=frontmatter.get("related", []) or [],
            prerequisites=frontmatter.get("prerequisites", []) or [],
        )

    def _validate(self):
        """Validate all loaded plugins. Report issues but don't crash."""
        self.validation_errors: list[str] = []
        for mid, m in self.modules.items():
            if not m.purpose:
                self.validation_errors.append(f"module {mid}: missing purpose")
            if not m.tagline:
                self.validation_errors.append(f"module {mid}: missing tagline")
        for tid, t in self.tools.items():
            if t.module and t.module not in self.modules:
                self.validation_errors.append(f"tool {tid}: unknown module {t.module}")
        for kid, k in self.knowledge.items():
            if k.module and k.module not in self.modules:
                self.validation_errors.append(f"knowledge {kid}: unknown module {k.module}")
            for tool_id in k.tools:
                if tool_id not in self.tools:
                    self.validation_errors.append(f"knowledge {kid}: unknown tool {tool_id}")

    # ---------------------------------------------------------------- query
    def list_modules(self) -> list[Module]:
        return sorted(self.modules.values(), key=lambda m: m.id)

    def get_module(self, module_id: str) -> Module | None:
        return self.modules.get(module_id)

    def search(self, query: str, limit: int = 10, semantic: bool = True) -> list[dict]:
        """Search modules, tools and knowledge. Keyword + semantic (cosine)."""
        terms = set(query.lower().split())
        scored: list[tuple[float, str, Any]] = []

        for m in self.modules.values():
            haystack = " ".join([m.id, m.name, m.tagline, m.purpose] + m.when_to_use + m.tags).lower()
            kw = sum(1 for t in terms if t in haystack)
            sem = _cosine(_embed(query), _embed(haystack)) if semantic else 0.0
            score = kw + sem * 3
            if score > 0:
                scored.append((score, "module", m))

        for t in self.tools.values():
            haystack = " ".join([t.id, t.name, t.description, t.module] + t.tags + t.related).lower()
            kw = sum(1 for term in terms if term in haystack)
            sem = _cosine(_embed(query), _embed(haystack)) if semantic else 0.0
            score = kw + sem * 3
            if score > 0:
                scored.append((score, "tool", t))

        for k in self.knowledge.values():
            haystack = " ".join([k.id, k.title, k.when, k.body] + k.tools + k.tags + k.related).lower()
            kw = sum(1 for term in terms if term in haystack)
            sem = _cosine(_embed(query), _embed(haystack)) if semantic else 0.0
            score = kw + sem * 3
            if score > 0:
                scored.append((score, "knowledge", k))

        scored.sort(key=lambda x: (-x[0], x[1]))
        results = []
        for score, kind, obj in scored[:limit]:
            results.append({"kind": kind, "score": round(score, 3), "item": obj.as_dict()})
            self._track(kind, obj.id if hasattr(obj, "id") else "", query)
        return results

    def describe(self, module_id: str) -> str:
        m = self.get_module(module_id)
        if m is None:
            return f"Unknown module: {module_id}"
        lines = [f"# {m.name} ({m.id})", f"**{m.tagline}**", "", m.purpose, ""]
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
        if m.dependencies:
            lines.append(f"**Dependencies:** {', '.join(m.dependencies)}")
        if m.docs_url:
            lines.append(f"**Docs:** {m.docs_url}")
        lines.append(f"**Status:** {m.status}  **Version:** {m.version}")
        return "\n".join(lines)

    def ai_context(self) -> str:
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
            if m.dependencies:
                lines.append(f"Depends on: {', '.join(m.dependencies)}")
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
        lines.append("2. Search: `forgehub search <query>` (semantic)")
        lines.append("3. Show: `forgehub show <id>`")
        lines.append("4. Describe a module: `forgehub describe <module>`")
        lines.append("5. Inject context for a task: `forgehub inject <task>`")
        lines.append("6. Validate: `forgehub validate`")
        lines.append("7. Stats: `forgehub stats`")
        lines.append("")
        lines.append("## Rules for AI agents")
        lines.append("")
        lines.append("- Prefer the right tool over reimplementing.")
        lines.append("- Study only the relevant playbooks, not all of them.")
        lines.append("- Verify results with tests (MATRIX eval loop).")
        lines.append("- Never trust stale knowledge: check provenance and TTL.")
        lines.append("- Compress context with SOLAR before sending to an LLM.")
        lines.append("- Use FORGE for code quality, SOLAR for efficiency, Helix for observability.")
        lines.append("- Use MATRIX tasks to measure whether you actually improved.")
        lines.append("- New modules: drop a file in forgehub/modules/, auto-discovered.")
        return "\n".join(lines)

    def inject(self, task: str, use_solar: bool = False, limit: int = 8) -> str:
        results = self.search(task, limit=limit)
        lines = [f"# ForgeHub context for: {task}", ""]
        modules_seen: set[str] = set()
        for r in results:
            item = r["item"]
            if r["kind"] == "knowledge":
                lines.append(f"## Playbook: {item['title']} (`{item['id']}`)")
                if item.get("when"):
                    lines.append(f"When: {item['when']}")
                if item.get("prerequisites"):
                    lines.append(f"Prerequisites: {', '.join(item['prerequisites'])}")
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
                if item.get("related"):
                    lines.append(f"Related: {', '.join(item['related'])}")
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
                if item.get("example"):
                    lines.append(f"Example: `{item['example']}`")
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

    def stats(self) -> dict:
        """Usage statistics."""
        if self._usage_db is None:
            return {"enabled": False}
        with self._usage_lock:
            rows = self._usage_db.execute(
                "SELECT kind, item_id, COUNT(*) as c FROM usage GROUP BY kind, item_id ORDER BY c DESC"
            ).fetchall()
            total = self._usage_db.execute("SELECT COUNT(*) FROM usage").fetchone()[0]
        return {
            "enabled": True,
            "total_queries": total,
            "by_item": [{"kind": r[0], "id": r[1], "count": r[2]} for r in rows],
        }

    def validate(self) -> list[str]:
        return list(getattr(self, "validation_errors", []))


def _parse_frontmatter(text: str) -> dict:
    try:
        import yaml
        return yaml.safe_load(text) or {}
    except ImportError:
        pass
    # minimal fallback
    result = {}
    current_key = None
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
