from __future__ import annotations

from dataclasses import dataclass

import httpx
from nonebot import logger

from pallas.api.utils import HTTPXClient, fetch_github_releases, github_auth_headers


@dataclass(frozen=True)
class CommitTip:
    sha: str
    message: str
    author: str
    html_url: str


@dataclass(frozen=True)
class ReleaseTip:
    tag: str
    title: str
    html_url: str


def _first_line(text: str) -> str:
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


async def fetch_latest_commit(
    owner: str,
    repo: str,
    branch: str,
    *,
    token: str = "",
) -> CommitTip | None:
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Pallas-Bot-git_watch/0.1",
    }
    headers.update(github_auth_headers(token))
    response = await HTTPXClient.get(
        url,
        headers=headers,
        params={"sha": branch, "per_page": 1},
        timeout=20.0,
    )
    if response is None:
        logger.warning("git_watch: 拉取 commit 失败 {}/{}@{}", owner, repo, branch)
        return None
    try:
        data = response.json()
    except Exception as exc:  # noqa: BLE001
        logger.warning("git_watch: commit JSON 解析失败 {}/{} err={}", owner, repo, exc)
        return None
    if not isinstance(data, list) or not data:
        return None
    item = data[0]
    if not isinstance(item, dict):
        return None
    sha = str(item.get("sha") or "").strip()
    if not sha:
        return None
    commit = item.get("commit") if isinstance(item.get("commit"), dict) else {}
    message = _first_line(str((commit or {}).get("message") or ""))
    author_obj = (commit or {}).get("author") if isinstance((commit or {}).get("author"), dict) else {}
    author = str((author_obj or {}).get("name") or "").strip()
    if not author:
        author_login = item.get("author") if isinstance(item.get("author"), dict) else {}
        author = str((author_login or {}).get("login") or "").strip() or "unknown"
    html_url = str(item.get("html_url") or "").strip()
    if not html_url:
        html_url = f"https://github.com/{owner}/{repo}/commit/{sha}"
    return CommitTip(sha=sha, message=message or sha[:7], author=author, html_url=html_url)


async def fetch_latest_release(
    owner: str,
    repo: str,
    *,
    token: str = "",
) -> ReleaseTip | None:
    async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
        releases = await fetch_github_releases(
            f"{owner}/{repo}",
            client=client,
            limit=5,
            token=token,
        )
    for item in releases:
        if not isinstance(item, dict):
            continue
        if bool(item.get("prerelease")):
            continue
        tag = str(item.get("tag") or item.get("tag_name") or "").strip()
        if not tag:
            continue
        title = str(item.get("name") or tag).strip() or tag
        html_url = str(item.get("html_url") or "").strip()
        if not html_url:
            html_url = f"https://github.com/{owner}/{repo}/releases/tag/{tag}"
        return ReleaseTip(tag=tag, title=title, html_url=html_url)
    # 若全是 pre-release，仍取第一条
    if releases:
        item = releases[0]
        tag = str(item.get("tag") or item.get("tag_name") or "").strip()
        if tag:
            title = str(item.get("name") or tag).strip() or tag
            html_url = str(item.get("html_url") or "").strip()
            if not html_url:
                html_url = f"https://github.com/{owner}/{repo}/releases/tag/{tag}"
            return ReleaseTip(tag=tag, title=title, html_url=html_url)
    return None


def format_commit_message(full_name: str, branch: str, tip: CommitTip) -> str:
    return f"[Git] {full_name} · 新提交\n分支: {branch}\n作者: {tip.author}\n摘要: {tip.message}\n{tip.html_url}"


def format_release_message(full_name: str, tip: ReleaseTip) -> str:
    return f"[Git] {full_name} · 新 Release\n标签: {tip.tag}\n标题: {tip.title}\n{tip.html_url}"
