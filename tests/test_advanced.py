import json, subprocess, sys, os
from pathlib import Path

import pytest

from forgehub.registry import ForgeHub

ENV = dict(os.environ)
ENV["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])


def test_semantic_search():
    hub = ForgeHub(root=".")
    results = hub.search("reduce token usage", semantic=True)
    assert len(results) > 0
    ids = [r["item"]["id"] for r in results]
    assert "solar" in ids or "prompt-compression" in ids or "semantic-cache" in ids


def test_validate():
    hub = ForgeHub(root=".")
    errors = hub.validate()
    assert errors == [], f"validation errors: {errors}"


def test_stats_disabled():
    hub = ForgeHub(root=".")
    s = hub.stats()
    assert s.get("enabled") is False


def test_stats_enabled(tmp_path):
    db = str(tmp_path / "usage.db")
    hub = ForgeHub(root=".", db_path=db)
    hub.search("compress")
    s = hub.stats()
    assert s["enabled"] is True
    assert s["total_queries"] > 0


def test_export():
    hub = ForgeHub(root=".")
    data = {
        "modules": [m.as_dict() for m in hub.list_modules()],
        "tools": [t.as_dict() for t in hub.tools.values()],
        "knowledge": [k.as_dict() for k in hub.knowledge.values()],
    }
    assert len(data["modules"]) >= 5
    assert len(data["tools"]) >= 10
    assert len(data["knowledge"]) >= 8


def test_related_fields():
    hub = ForgeHub(root=".")
    k = hub.knowledge["prompt-compression"]
    assert isinstance(k.related, list)
    assert isinstance(k.prerequisites, list)


def test_module_dependencies():
    hub = ForgeHub(root=".")
    m = hub.get_module("solar")
    assert isinstance(m.dependencies, list)


def test_cli_validate():
    p = subprocess.run([sys.executable, "-m", "forgehub.cli", "validate"], capture_output=True, text=True, env=ENV)
    assert p.returncode == 0
    assert "OK" in p.stdout


def test_cli_stats():
    p = subprocess.run([sys.executable, "-m", "forgehub.cli", "stats"], capture_output=True, text=True, env=ENV)
    assert p.returncode == 0


def test_cli_export():
    p = subprocess.run([sys.executable, "-m", "forgehub.cli", "export"], capture_output=True, text=True, env=ENV)
    assert p.returncode == 0
    data = json.loads(p.stdout)
    assert "modules" in data
    assert "tools" in data
    assert "knowledge" in data


def test_cli_inject_solar():
    p = subprocess.run(
        [sys.executable, "-m", "forgehub.cli", "inject", "compress", "prompt", "--solar"],
        capture_output=True, text=True, env=ENV,
    )
    assert p.returncode == 0
