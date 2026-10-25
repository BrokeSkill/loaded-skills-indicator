"""Loaded Skills Indicator: agent-side entry point.

Blog-sized package, three halves:

- ``desktop/plugin.js`` (installed at ``<hermes home>/desktop-plugins/``): the
  status-bar chip, its popover and the ``/loaded-skills`` panel.
- ``dashboard/plugin_api.py``: backend router mounted at
  ``/api/plugins/loaded-skills-indicator/`` — reads the durable transcript and
  reports which skills are still fully in context.
- this module: inert by design, so the package is a well-formed Hermes plugin.

The agent side registers nothing: the plugin READMEs the conversation, it
never changes it.
"""


def register(ctx):
    """Inert by design: all functionality lives in the desktop and dashboard halves."""
    return None
