from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from nonebot import logger

from pallas.api.logging import format_plugin_event

from .config import Config, WatchedRepo, get_config, list_watched_repos, resolve_github_token
from .cursor_logic import apply_tip_decision, decide_tip
from .github import (
    fetch_latest_commit,
    fetch_latest_release,
    format_commit_message,
    format_release_message,
)
from .notify import send_notifications
from .store import RepoCursor, WatchState, get_cursor, load_state, save_state


@dataclass
class TickResult:
    checked: int = 0
    seeded: int = 0
    notified: int = 0
    failed: int = 0
    messages: list[str] | None = None
    error: str = ""

    def summary_text(self) -> str:
        if self.error:
            return f"失败: {self.error}"
        return f"检查 {self.checked} 仓 · 初始化 {self.seeded} · 推送 {self.notified} · 失败 {self.failed}"


async def _maybe_notify(config: Config, message: str, *, dry_run: bool) -> bool:
    if dry_run:
        return True
    result = await send_notifications(config, message)
    return bool(result.get("ok"))


async def process_repo(
    config: Config,
    repo: WatchedRepo,
    state: WatchState,
    *,
    token: str,
    dry_run: bool = False,
) -> tuple[int, int, int, list[str]]:
    """返回 (seeded, notified, failed, messages)。"""
    cursor = get_cursor(state, repo.key)
    seeded = 0
    notified = 0
    failed = 0
    messages: list[str] = []

    if repo.watch_commits:
        tip = await fetch_latest_commit(repo.owner, repo.repo, repo.branch, token=token)
        if tip is not None:
            decision = decide_tip(
                cursor.last_seen_commit_sha,
                cursor.last_notified_commit_sha,
                tip.sha,
            )
            ok = True
            if decision.action == "seed":
                seeded += 1
            elif decision.action == "notify":
                text = format_commit_message(repo.full_name, repo.branch, tip)
                ok = await _maybe_notify(config, text, dry_run=dry_run)
                if ok:
                    notified += 1
                    messages.append(text)
                    if not dry_run:
                        logger.info(
                            format_plugin_event(
                                "git_commit_push",
                                f"Pushed a commit notification for [{repo.full_name}]@[{repo.branch}]",
                            )
                        )
                else:
                    failed += 1
            apply_tip_decision(cursor, "commit", decision, notified_ok=ok)

    if repo.watch_releases:
        release = await fetch_latest_release(repo.owner, repo.repo, token=token)
        if release is not None:
            decision = decide_tip(
                cursor.last_seen_release_tag,
                cursor.last_notified_release_tag,
                release.tag,
            )
            ok = True
            if decision.action == "seed":
                seeded += 1
            elif decision.action == "notify":
                text = format_release_message(repo.full_name, release)
                ok = await _maybe_notify(config, text, dry_run=dry_run)
                if ok:
                    notified += 1
                    messages.append(text)
                    if not dry_run:
                        logger.info(
                            format_plugin_event(
                                "git_release_push",
                                f"Pushed a release notification for [{repo.full_name}], tag [{release.tag}]",
                            )
                        )
                else:
                    failed += 1
            apply_tip_decision(cursor, "release", decision, notified_ok=ok)

    return seeded, notified, failed, messages


async def run_watch_tick(
    *,
    config: Config | None = None,
    dry_run: bool = False,
    force_enabled: bool = False,
) -> TickResult:
    cfg = config or get_config()
    result = TickResult(messages=[])
    if not force_enabled and not cfg.git_watch_enabled:
        result.error = "未启用"
        return result

    repos = list_watched_repos(cfg)
    if not repos:
        result.error = "无启用仓库"
        return result

    token = resolve_github_token(cfg)
    state = load_state()
    try:
        for repo in repos:
            result.checked += 1
            seeded, notified, failed, messages = await process_repo(cfg, repo, state, token=token, dry_run=dry_run)
            result.seeded += seeded
            result.notified += notified
            result.failed += failed
            if result.messages is not None:
                result.messages.extend(messages)
        state.last_error = ""
    except Exception as exc:  # noqa: BLE001
        logger.exception("git_watch: tick 失败")
        result.error = str(exc)
        state.last_error = str(exc)

    state.last_tick_at = datetime.now(UTC).isoformat()
    state.last_tick_summary = result.summary_text()
    save_state(state)
    return result


def status_text(config: Config | None = None) -> str:
    cfg = config or get_config()
    state = load_state()
    repos = list_watched_repos(cfg)
    token = resolve_github_token(cfg)
    lines = [
        "Git 监控状态",
        f"启用: {'是' if cfg.git_watch_enabled else '否'}",
        f"间隔: {cfg.git_watch_interval_minutes} 分钟",
        f"Commit: {'开' if cfg.git_watch_watch_commits else '关'} · "
        f"Release: {'开' if cfg.git_watch_watch_releases else '关'}",
        f"Token: {'已配置' if token else '未配置（匿名限流更紧）'}",
        f"群: {cfg.git_watch_notify_group_ids or []} · QQ: {cfg.git_watch_notify_user_ids or []}",
        f"上次: {state.last_tick_at or '-'} · {state.last_tick_summary or '-'}",
    ]
    if state.last_error:
        lines.append(f"上次错误: {state.last_error}")
    lines.append("仓库游标:")
    if not repos:
        lines.append("- （无）")
    else:
        for repo in repos:
            cursor = state.repos.get(repo.key) or RepoCursor()
            sha = cursor.last_seen_commit_sha
            sha_short = (sha[:7] + "…") if len(sha) > 7 else (sha or "-")
            tag = cursor.last_seen_release_tag or "-"
            flag = "预置" if repo.preset else "自定义"
            lines.append(f"- [{flag}] {repo.full_name}@{repo.branch}: {sha_short} / {tag}")
    return "\n".join(lines)
