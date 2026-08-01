<p align="center">
  <img src="./assets/brand-avatar.png" width="220" height="220" alt="Git 监控">
</p>

<h1 align="center">Git 监控 git_watch</h1>

<p align="center">定时轮询 GitHub，向指定群或好友推送仓库 Commit / Release 更新。</p>

<p align="center">
  <img alt="社区插件" src="https://img.shields.io/badge/%E7%A4%BE%E5%8C%BA%E6%8F%92%E4%BB%B6-4B5563">
  <img alt="版本" src="https://img.shields.io/badge/%E7%89%88%E6%9C%AC-v0.1.0-2563EB">
  <img alt="Pallas" src="https://img.shields.io/badge/Pallas-%3E%3D4.0-2563EB">
</p>

## 安装方式

可在控制台插件商店安装，也可按社区插件目录放入 `local/plugins/git_watch/`（目录名须与插件 ID `git_watch` 一致，与仓库名无关）。

```bash
git clone https://github.com/Blackish-Red/pallas-plugin-git-watch.git local/plugins/git_watch
```

装好后重启 Bot（或热加载社区插件）。未启用时不会注册定时任务，也不会推送。

包内 `assets/icon.png`、`assets/cover.png` 供商店卡片展示；`assets/brand-avatar.png` 仅 README 用。作者角标由索引 `author`（GitHub 头像）解析，**不要**在索引里填插件封面到 `avatar`。

**最低要求**：Pallas-Bot **4.0** 及以上；定时任务依赖 `nonebot_plugin_apscheduler`（主仓通常已带）。

## 怎么使用

1. 控制台 **插件 → Git 监控**：打开启用，填写推送群号 / QQ。
2. 可选填写本插件 Token；**留空则复用**控制台「GitHub 下载令牌」（`PALLAS_PROTOCOL_GITHUB_TOKEN`）。
3. 维护者命令：
   - `git 检查`：立即轮询一轮；有更新则按配置推送。
   - `git 状态`：查看开关、目标、仓库游标与上次结果。

预置仓默认开启：`PallasBot/Pallas-Bot`、`PallasBot/Pallas-Bot-WebUI`；也可在配置里追加自定义仓库。

> 详细用法与可用范围以帮助为主；命令默认仅超级用户。

## 命令权限

| 功能 | 默认等级 |
| --- | --- |
| `git 检查` | 超级用户 |
| `git 状态` | 超级用户 |

## 配置项

> 可在控制台 **插件 → Git 监控** 中修改。

### 基础

| 配置项 | 说明 |
| --- | --- |
| `git_watch_enabled` | 是否启用定时轮询与推送 |
| `git_watch_interval_minutes` | 轮询间隔（分钟），范围 5–1440，建议 5–60 |
| `git_watch_github_token` | 可选 GitHub PAT；留空复用 `PALLAS_PROTOCOL_GITHUB_TOKEN` |

### 推送目标

| 配置项 | 说明 |
| --- | --- |
| `git_watch_notify_group_ids` | 推送群号列表 |
| `git_watch_notify_user_ids` | 推送 QQ 列表 |
| `git_watch_notify_bot_id` | 发送用牛牛 QQ；`0` 表示任意在线账号 |

### 监控项与预置仓

| 配置项 | 说明 |
| --- | --- |
| `git_watch_watch_commits` | 是否监控新 Commit |
| `git_watch_watch_releases` | 是否监控新 Release |
| `git_watch_preset_pallas_bot` | 预置监控 `PallasBot/Pallas-Bot` |
| `git_watch_preset_pallas_webui` | 预置监控 `PallasBot/Pallas-Bot-WebUI` |
| `git_watch_preset_branch` | 预置仓盯的分支（默认 `main`） |

### 自定义仓库

| 配置项 | 说明 |
| --- | --- |
| `git_watch_custom_repos_json` | 自定义仓库 JSON 数组 |

示例：

```json
[
  {
    "owner": "org",
    "repo": "name",
    "branch": "main",
    "commits": true,
    "releases": true
  }
]
```

未写 `commits` / `releases` 时跟随全局开关；与预置仓同名时以预置为准（不重复监控）。

## 行为说明

- 首次启用或新加仓：只写入当前 tip，**不**把历史一次性刷进群。
- 漏更或多条未推送：Commit / Release **各最多推送当前最新一条**。
- 推送失败：不积压队列；同一 tip 可重试，tip 已前进则只推新 tip。
- 游标与状态落在 `data/git_watch/state.json`。
- 分片 worker 进程不注册调度，避免多发。

## 排障

| 现象 | 处理 |
| --- | --- |
| 完全没有推送 | 检查是否启用、群号/QQ 是否填写、Bot 是否在线。 |
| `git 状态` 显示 Token 未配置且频繁限流 | 在本插件或控制台填写 GitHub Token。 |
| 启用后突然刷很多历史 | 不应发生；若游标文件被删会重新初始化且不推历史。可删 `data/git_watch/state.json` 后重启再观察。 |
| 定时不跑 | 确认已安装 `nonebot_plugin_apscheduler`；分片 worker 上不会调度。 |
| 自定义仓不生效 | 检查 JSON 是否合法，以及 `owner` / `repo` 是否非空。 |

## 实现

源码位置：

- 插件入口：[`__init__.py`](./__init__.py)
- 配置定义：[`config.py`](./config.py)
- 命令处理：[`handlers.py`](./handlers.py)
- 启动调度：[`startup.py`](./startup.py)
- 轮询与推送：[`watcher.py`](./watcher.py)、[`github.py`](./github.py)、[`notify.py`](./notify.py)
- 游标存储：[`store.py`](./store.py)、[`cursor_logic.py`](./cursor_logic.py)

实现要点：

- 仅使用 `pallas.api.*`（社区插件 L1）。
- GitHub 鉴权走 `github_auth_headers`；Release 列表可复用 `fetch_github_releases`。
- WebUI 保存配置后会重调度 interval job。

## 更新日志

版本变更见 [`CHANGELOG.md`](./CHANGELOG.md)；也可在控制台插件商店弹窗的「更新日志」分栏查看。

## 相关链接

- [社区插件索引](https://github.com/PallasBot/community-plugin-index)
- [社区插件商店说明](https://github.com/PallasBot/Pallas-Bot/blob/dev/docs/guide/community-plugin-store.md)
- [仓库主页](https://github.com/Blackish-Red/pallas-plugin-git-watch)
