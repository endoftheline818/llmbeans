# llmbeans/recommenders/tools/__init__.py
# Auto-import all tool modules to register them with the engine.

import importlib
import os

_pkg_dir = os.path.dirname(__file__)
for _f in sorted(os.listdir(_pkg_dir)):
    if _f.endswith(".py") and not _f.startswith("_"):
        importlib.import_module(f"llmbeans.recommenders.tools.{_f[:-3]}")