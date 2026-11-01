import pytest
from forgehub.registry import ForgeHub


def test_loads_modules():
    hub = ForgeHub(root=".")
    assert "solar" in hub.modules
    assert "forge" in hub.modules
    assert "matrix" in hub.modules
    assert "helix" in hub.modules
    assert "qorvex" in hub.modules


def test_loads_tools():
    hub = ForgeHub(root=".")
    assert "solar.compress" in hub.tools
    assert "forge.scan" in hub.tools
    assert len(hub.tools) >= 7


def test_loads_knowledge():
    hub = ForgeHub(root=".")
    assert "prompt-compression" in hub.knowledge
    assert "debugging" in hub.knowledge
    assert len(hub.knowledge) >= 8


def test_search():
    hub = ForgeHub(root=".")
    results = hub.search("compress token")
    assert len(results) > 0
    ids = [r["item"]["id"] for r in results]
    assert "solar" in ids or "prompt-compression" in ids


def test_describe():
    hub = ForgeHub(root=".")
    text = hub.describe("solar")
    assert "SOLAR" in text
    assert "When to use" in text


def test_ai_context():
    hub = ForgeHub(root=".")
    ctx = hub.ai_context()
    assert "ForgeHub" in ctx
    assert "SOLAR" in ctx
    assert "Rules for AI agents" in ctx


def test_inject():
    hub = ForgeHub(root=".")
    text = hub.inject("compress a prompt")
    assert "ForgeHub context" in text
    assert len(text) > 50


def test_module_as_dict():
    hub = ForgeHub(root=".")
    m = hub.get_module("solar")
    d = m.as_dict()
    assert d["id"] == "solar"
    assert "when_to_use" in d


def test_extensibility():
    # a future module can be added by dropping a file; verify discovery works
    hub = ForgeHub(root=".")
    # all 5 core modules present
    assert len(hub.modules) >= 5
