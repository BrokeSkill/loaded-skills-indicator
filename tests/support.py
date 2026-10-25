"""Test support: import the backend router without a FastAPI install.

``dashboard/plugin_api.py`` is a FastAPI router because that is what the Hermes
dashboard mounts. The unit tests exercise the pure functions in it (transcript
analysis, SKILL.md scanning), so they stub the two FastAPI names the module
binds at import time instead of requiring the whole framework.
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_FILE = ROOT / "dashboard" / "plugin_api.py"

_cached = None


def _fake_fastapi() -> None:
    if "fastapi" in sys.modules:
        return
    fake = types.ModuleType("fastapi")

    class APIRouter:  # decorator-only surface: @router.get("/path")
        def get(self, *args, **kwargs):
            def decorator(fn):
                return fn

            return decorator

    fake.APIRouter = APIRouter
    fake.Query = lambda default=None, **kwargs: default
    sys.modules["fastapi"] = fake


def load_api():
    """The plugin_api module, loaded once per test session."""
    global _cached
    if _cached is not None:
        return _cached
    _fake_fastapi()
    spec = importlib.util.spec_from_file_location("lsi_plugin_api", API_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _cached = module
    return module


def row(**fields):
    """One transcript row with the columns ``analyse()`` reads."""
    base = {
        "id": 0,
        "role": "",
        "content": "",
        "tool_calls": None,
        "tool_call_id": None,
        "tool_name": None,
        "timestamp": 1.0,
        "display_kind": None,
    }
    base.update(fields)
    return base
