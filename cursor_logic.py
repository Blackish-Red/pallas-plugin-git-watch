from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .store import RepoCursor

Kind = Literal["commit", "release"]


@dataclass(frozen=True)
class TipDecision:
    """对单一 tip 的游标决策。"""

    action: Literal["seed", "skip", "notify"]
    tip_id: str


def decide_tip(seen: str, notified: str, tip_id: str) -> TipDecision:
    """首次写入不推送；tip 未变且已通知则跳过；否则只推当前 tip。"""
    tip = (tip_id or "").strip()
    if not tip:
        return TipDecision(action="skip", tip_id="")
    if not (seen or "").strip():
        return TipDecision(action="seed", tip_id=tip)
    if tip == (notified or "").strip():
        return TipDecision(action="skip", tip_id=tip)
    return TipDecision(action="notify", tip_id=tip)


def apply_tip_decision(
    cursor: RepoCursor,
    kind: Kind,
    decision: TipDecision,
    *,
    notified_ok: bool,
) -> None:
    tip = decision.tip_id
    if kind == "commit":
        cursor.last_seen_commit_sha = tip
        if decision.action == "seed" or (decision.action == "notify" and notified_ok):
            cursor.last_notified_commit_sha = tip
        return
    cursor.last_seen_release_tag = tip
    if decision.action == "seed" or (decision.action == "notify" and notified_ok):
        cursor.last_notified_release_tag = tip
