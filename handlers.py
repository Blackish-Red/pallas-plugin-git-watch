from __future__ import annotations

from pallas.api.commands import PluginHandlerContext, bind_alias_handlers, message_command

from .watcher import run_watch_tick, status_text

check_cmd = message_command("git_watch.check", "git 检查", cd_sec=10)
status_cmd = message_command("git_watch.status", "git 状态", cd_sec=5)


async def handle_check(context: PluginHandlerContext) -> None:
    result = await run_watch_tick(force_enabled=True)
    await context.matcher.finish(result.summary_text())


async def handle_status(context: PluginHandlerContext) -> None:
    await context.matcher.finish(status_text())


bind_alias_handlers(check_cmd, handle_check)
bind_alias_handlers(status_cmd, handle_status)
