from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any

from pallas.api.paths import plugin_data_dir

from .config import PLUGIN_ID

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class RepoCursor:
    last_seen_commit_sha: str = ""
    last_notified_commit_sha: str = ""
    last_seen_release_tag: str = ""
    last_notified_release_tag: str = ""


@dataclass
class WatchState:
    repos: dict[str, RepoCursor] = field(default_factory=dict)
    last_error: str = ""
    last_tick_at: str = ""
    last_tick_summary: str = ""


def state_path() -> Path:
    return plugin_data_dir(PLUGIN_ID) / "state.json"


def _cursor_from_dict(raw: Any) -> RepoCursor:
    if not isinstance(raw, dict):
        return RepoCursor()
    return RepoCursor(
        last_seen_commit_sha=str(raw.get("last_seen_commit_sha") or ""),
        last_notified_commit_sha=str(raw.get("last_notified_commit_sha") or ""),
        last_seen_release_tag=str(raw.get("last_seen_release_tag") or ""),
        last_notified_release_tag=str(raw.get("last_notified_release_tag") or ""),
    )


def load_state() -> WatchState:
    path = state_path()
    if not path.is_file():
        return WatchState()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return WatchState()
    if not isinstance(data, dict):
        return WatchState()
    repos_raw = data.get("repos") or {}
    repos: dict[str, RepoCursor] = {}
    if isinstance(repos_raw, dict):
        for key, value in repos_raw.items():
            repos[str(key).lower()] = _cursor_from_dict(value)
    return WatchState(
        repos=repos,
        last_error=str(data.get("last_error") or ""),
        last_tick_at=str(data.get("last_tick_at") or ""),
        last_tick_summary=str(data.get("last_tick_summary") or ""),
    )


def save_state(state: WatchState) -> None:
    path = state_path()
    payload = {
        "repos": {key: asdict(cursor) for key, cursor in state.repos.items()},
        "last_error": state.last_error,
        "last_tick_at": state.last_tick_at,
        "last_tick_summary": state.last_tick_summary,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_cursor(state: WatchState, repo_key: str) -> RepoCursor:
    key = repo_key.lower()
    cursor = state.repos.get(key)
    if cursor is None:
        cursor = RepoCursor()
        state.repos[key] = cursor
    return cursor
