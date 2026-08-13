"""Waste Collection Schedule Component (Republic Services only)."""

import site
from pathlib import Path

# The bundled `waste_collection_schedule` package is imported as a top-level
# module by the source module and by config_flow, so its parent directory has
# to be on sys.path. Upstream did this in init_yaml.py, which no longer exists
# in this fork, so it happens here instead - before anything else is imported.
site.addsitedir(str(Path(__file__).resolve().parent))

from .init_ui import (  # noqa: F401  # isort:skip
    async_migrate_entry,
    async_setup_entry,
    async_unload_entry,
    async_update_listener,
)
