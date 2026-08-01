from __future__ import annotations

import sys
import types
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "git_watch"

if PKG_NAME not in sys.modules:
    module = types.ModuleType(PKG_NAME)
    module.__path__ = [str(PLUGIN_ROOT)]  # type: ignore[attr-defined]
    sys.modules[PKG_NAME] = module

if str(PLUGIN_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT.parent))
