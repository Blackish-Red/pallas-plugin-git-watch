from __future__ import annotations

from nonebot import logger

from pallas.api.logging import format_plugin_event

from .config import get_config

JOB_ID = "git_watch.poll"


def _is_sharded_worker() -> bool:
    try:
        from pallas.api.platform import is_sharded_worker

        return bool(is_sharded_worker())
    except Exception:  # noqa: BLE001
        return False


async def _job() -> None:
    from .watcher import run_watch_tick

    try:
        result = await run_watch_tick()
        if result.error and result.error != "未启用":
            logger.warning("git_watch: 定时检查 {}", result.summary_text())
        else:
            logger.info("git_watch: 定时检查 {}", result.summary_text())
    except Exception:  # noqa: BLE001
        logger.exception("git_watch: 定时任务失败")


def reschedule_git_watch_job() -> None:
    if _is_sharded_worker():
        return
    try:
        from nonebot_plugin_apscheduler import scheduler
    except ImportError:
        logger.warning("git_watch: 未安装 nonebot_plugin_apscheduler，跳过调度")
        return

    if scheduler.get_job(JOB_ID):
        scheduler.remove_job(JOB_ID)

    cfg = get_config()
    if not cfg.git_watch_enabled:
        logger.info("git_watch: 已关闭（未注册调度）")
        return

    minutes = max(5, min(1440, int(cfg.git_watch_interval_minutes or 15)))
    scheduler.add_job(
        _job,
        trigger="interval",
        minutes=minutes,
        id=JOB_ID,
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=3600,
    )
    logger.info(
        format_plugin_event(
            "ready",
            f"Scheduled git watch polling every {minutes} minutes",
        )
    )


def setup_git_watch_runtime() -> None:
    reschedule_git_watch_job()


def _register_startup() -> None:
    try:
        from nonebot import get_driver
    except Exception:  # noqa: BLE001
        return
    try:
        get_driver().on_startup(setup_git_watch_runtime)
    except ValueError:
        return


_register_startup()
