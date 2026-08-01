from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from pallas.api.config import install_hot_reload_config, repo_env_raw_value

PLUGIN_ID = "git_watch"

PRESET_PALLAS_BOT = ("PallasBot", "Pallas-Bot")
PRESET_PALLAS_WEBUI = ("PallasBot", "Pallas-Bot-WebUI")


def _ui(
    label: str,
    *,
    group: str | None = None,
    secret: bool = False,
) -> dict[str, Any]:
    extra: dict[str, Any] = {"label": label}
    if group:
        extra["ui_group"] = group
    if secret:
        extra["secret"] = True
    return extra


class Config(BaseModel, extra="ignore"):
    git_watch_enabled: bool = Field(
        default=False,
        description="开启后按间隔轮询 GitHub，并向配置的群/好友推送更新。",
        json_schema_extra=_ui("启用 Git 监控", group="基础"),
    )
    git_watch_interval_minutes: int = Field(
        default=15,
        ge=5,
        le=1440,
        description="轮询间隔（分钟），建议 5–60。",
        json_schema_extra=_ui("轮询间隔（分钟）", group="基础"),
    )
    git_watch_github_token: str = Field(
        default="",
        description="可选 GitHub PAT；留空则复用控制台「GitHub 下载令牌」（PALLAS_PROTOCOL_GITHUB_TOKEN）。",
        json_schema_extra=_ui("GitHub Token（可选）", group="基础", secret=True),
    )
    git_watch_notify_group_ids: list[int] = Field(
        default_factory=list,
        description="推送目标群号列表。",
        json_schema_extra=_ui("推送群号", group="推送目标"),
    )
    git_watch_notify_user_ids: list[int] = Field(
        default_factory=list,
        description="推送目标 QQ 列表。",
        json_schema_extra=_ui("推送 QQ", group="推送目标"),
    )
    git_watch_notify_bot_id: int = Field(
        default=0,
        description="用哪个牛牛账号发送；0 表示任意在线账号。",
        json_schema_extra=_ui("发送用 Bot QQ", group="推送目标"),
    )
    git_watch_watch_commits: bool = Field(
        default=True,
        description="是否监控新提交。",
        json_schema_extra=_ui("监控 Commit", group="监控项"),
    )
    git_watch_watch_releases: bool = Field(
        default=True,
        description="是否监控新 Release。",
        json_schema_extra=_ui("监控 Release", group="监控项"),
    )
    git_watch_preset_pallas_bot: bool = Field(
        default=True,
        description="监控 PallasBot/Pallas-Bot。",
        json_schema_extra=_ui("预置：Pallas-Bot", group="预置仓库"),
    )
    git_watch_preset_pallas_webui: bool = Field(
        default=True,
        description="监控 PallasBot/Pallas-Bot-WebUI。",
        json_schema_extra=_ui("预置：Pallas-Bot-WebUI", group="预置仓库"),
    )
    git_watch_preset_branch: str = Field(
        default="main",
        description="预置仓库盯的分支名。",
        json_schema_extra=_ui("预置仓分支", group="预置仓库"),
    )
    git_watch_custom_repos_json: str = Field(
        default="[]",
        description=(
            "自定义仓库 JSON 数组，例如 "
            '[{"owner":"org","repo":"name","branch":"main","commits":true,"releases":true}]。'
        ),
        json_schema_extra=_ui("自定义仓库 JSON", group="自定义"),
    )


@dataclass(frozen=True)
class WatchedRepo:
    owner: str
    repo: str
    branch: str
    watch_commits: bool
    watch_releases: bool
    preset: bool = False

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repo}"

    @property
    def key(self) -> str:
        return self.full_name.lower()


def resolve_github_token(config: Config | None = None) -> str:
    """插件自填 token 优先，否则读内置 PALLAS_PROTOCOL_GITHUB_TOKEN。"""
    cfg = config or get_config()
    own = (cfg.git_watch_github_token or "").strip()
    if own:
        return own
    raw = repo_env_raw_value("PALLAS_PROTOCOL_GITHUB_TOKEN")
    return str(raw).strip() if raw is not None else ""


def parse_custom_repos(raw: str, *, global_commits: bool, global_releases: bool) -> list[WatchedRepo]:
    text = (raw or "").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    out: list[WatchedRepo] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        owner = str(item.get("owner") or "").strip()
        repo = str(item.get("repo") or "").strip()
        if not owner or not repo:
            continue
        branch = str(item.get("branch") or "main").strip() or "main"
        commits = bool(item["commits"]) if "commits" in item else global_commits
        releases = bool(item["releases"]) if "releases" in item else global_releases
        out.append(
            WatchedRepo(
                owner=owner,
                repo=repo,
                branch=branch,
                watch_commits=commits and global_commits,
                watch_releases=releases and global_releases,
                preset=False,
            )
        )
    return out


def list_watched_repos(config: Config | None = None) -> list[WatchedRepo]:
    cfg = config or get_config()
    branch = (cfg.git_watch_preset_branch or "main").strip() or "main"
    repos: list[WatchedRepo] = []
    if cfg.git_watch_preset_pallas_bot:
        owner, name = PRESET_PALLAS_BOT
        repos.append(
            WatchedRepo(
                owner=owner,
                repo=name,
                branch=branch,
                watch_commits=cfg.git_watch_watch_commits,
                watch_releases=cfg.git_watch_watch_releases,
                preset=True,
            )
        )
    if cfg.git_watch_preset_pallas_webui:
        owner, name = PRESET_PALLAS_WEBUI
        repos.append(
            WatchedRepo(
                owner=owner,
                repo=name,
                branch=branch,
                watch_commits=cfg.git_watch_watch_commits,
                watch_releases=cfg.git_watch_watch_releases,
                preset=True,
            )
        )
    custom = parse_custom_repos(
        cfg.git_watch_custom_repos_json,
        global_commits=cfg.git_watch_watch_commits,
        global_releases=cfg.git_watch_watch_releases,
    )
    seen = {r.key for r in repos}
    for item in custom:
        if item.key in seen:
            continue
        seen.add(item.key)
        repos.append(item)
    return repos


def on_git_watch_config_reload(_config: Config) -> None:
    from .startup import reschedule_git_watch_job

    reschedule_git_watch_job()


plugin_webui = install_hot_reload_config(
    Config,
    config_module=__name__,
    on_reload=on_git_watch_config_reload,
)
get_config = plugin_webui.get
