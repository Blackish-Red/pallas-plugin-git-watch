from nonebot.plugin import PluginMetadata

from pallas.api.commands import command_perm_list, command_perm_row
from pallas.api.metadata import (
    PLUGIN_HOMEPAGE,
    PLUGIN_MENU_TEMPLATE,
    SCENE_BOTH,
    join_usage,
    usage_line,
)

from . import handlers as handlers  # noqa: F401
from . import startup as startup  # noqa: F401
from .config import PLUGIN_ID

__plugin_meta__ = PluginMetadata(
    name="Git 监控",
    description="定时轮询 GitHub，向指定群或好友推送仓库 Commit / Release 更新。",
    usage=join_usage(
        usage_line("git 检查", "立即轮询一次并推送最新更新"),
        usage_line("git 状态", "查看开关、仓库与游标"),
    ),
    type="application",
    homepage=PLUGIN_HOMEPAGE,
    supported_adapters={"~onebot.v11"},
    extra={
        "help_tag": "tool",
        "help_audience": "superuser",
        "version": "0.1.0",
        "menu_template": PLUGIN_MENU_TEMPLATE,
        "command_permissions": command_perm_list(
            command_perm_row(f"{PLUGIN_ID}.check", "git 检查", "superuser"),
            command_perm_row(f"{PLUGIN_ID}.status", "git 状态", "superuser"),
        ),
        "menu_data": [
            {
                "func": "立即检查",
                "trigger_method": "on_command",
                "trigger_scene": SCENE_BOTH,
                "trigger_condition": "git 检查",
                "command_permission": f"{PLUGIN_ID}.check",
                "help_audience": "superuser",
                "brief_des": "立即轮询 GitHub",
                "detail_des": "按 WebUI 配置检查预置与自定义仓库；有更新则只推送最新一条。",
            },
            {
                "func": "查看状态",
                "trigger_method": "on_command",
                "trigger_scene": SCENE_BOTH,
                "trigger_condition": "git 状态",
                "command_permission": f"{PLUGIN_ID}.status",
                "help_audience": "superuser",
                "brief_des": "查看监控状态",
                "detail_des": "显示总开关、间隔、推送目标与各仓库游标。",
            },
        ],
        "reload_policy": "metadata",
    },
)
