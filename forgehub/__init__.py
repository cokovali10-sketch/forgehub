"""ForgeHub - knowledge and tool registry for AI agents.

ForgeHub is the "master workshop" for AI: a curated, machine-readable map of
the FORGE ecosystem (FORGE, SOLAR, MATRIX, Helix, Qorvex, ...) plus playbooks
and tool schemas. An AI agent studies ForgeHub, then picks the right tool for
the task.

Design principle: every module, tool and playbook is a *plugin*. Adding a new
capability means dropping a file in the right directory - no core code changes.
"""

__version__ = "0.1.0"

from .registry import ForgeHub, Module, Tool, KnowledgeEntry

__all__ = ["ForgeHub", "Module", "Tool", "KnowledgeEntry", "__version__"]
