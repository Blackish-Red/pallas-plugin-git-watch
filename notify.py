from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nonebot import get_bots, logger

if TYPE_CHECKING:
    from .config import Config


def pick_bot(prefer_bot_id: int = 0) -> Any | None:
    bots = get_bots()
    if not bots:
        return None
    prefer = int(prefer_bot_id or 0)
    if prefer > 0:
        for candidate in bots.values():
            try:
                if int(candidate.self_id) == prefer:
                    return candidate
            except (TypeError, ValueError):
                continue
        logger.warning("git_watch: 指定 Bot {} 不在线", prefer)
        return None
    return next(iter(bots.values()))


async def send_notifications(config: Config, message: str) -> dict[str, Any]:
    text = (message or "").strip()
    if not text:
        return {"ok": False, "reason": "empty", "delivered": 0}

    groups = [int(x) for x in (config.git_watch_notify_group_ids or []) if int(x) > 0]
    users = [int(x) for x in (config.git_watch_notify_user_ids or []) if int(x) > 0]
    if not groups and not users:
        return {"ok": False, "reason": "no_targets", "delivered": 0}

    bot = pick_bot(config.git_watch_notify_bot_id)
    if bot is None:
        return {"ok": False, "reason": "no_bot", "delivered": 0}

    delivered = 0
    errors: list[str] = []
    for gid in groups:
        try:
            await bot.send_group_msg(group_id=gid, message=text)
            delivered += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f"group:{gid}:{exc}")
            logger.warning("git_watch: 群推送失败 group={} err={}", gid, exc)
    for uid in users:
        try:
            await bot.send_private_msg(user_id=uid, message=text)
            delivered += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f"user:{uid}:{exc}")
            logger.warning("git_watch: 私聊推送失败 user={} err={}", uid, exc)

    return {
        "ok": delivered > 0,
        "reason": "ok" if delivered > 0 else ("all_failed" if errors else "no_targets"),
        "delivered": delivered,
        "errors": errors,
        "bot_id": int(getattr(bot, "self_id", 0) or 0),
    }
