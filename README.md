<p align="center">
  <img src="./assets/icon.png" width="128" height="128" alt="Git 监控">
</p>

<h1 align="center">Git 监控 git_watch</h1>

<p align="center">定时轮询 GitHub，向指定群或好友推送仓库 Commit / Release 更新。</p>

<p align="center">
  <img alt="社区插件" src="https://img.shields.io/badge/%E7%A4%BE%E5%8C%BA%E6%8F%92%E4%BB%B6-4B5563">
  <img alt="版本" src="https://img.shields.io/badge/%E7%89%88%E6%9C%AC-v0.1.0-2563EB">
</p>

当前版本：**v0.1.0** · 作者：[Blackish-Red](https://github.com/Blackish-Red) · 需要 Pallas-Bot ≥ 4.0.0

## 安装方式

可在控制台插件商店安装（收录后），或：

```bash
git clone https://github.com/TogetsuDo/pallas-plugin-git-watch.git local/plugins/git_watch
```

目录名须为 `git_watch`。装好后重启 Bot。

## 怎么使用

1. 控制台 **插件 → Git 监控**：打开启用，填写推送群号 / QQ。
2. 可选填写本插件 Token；**留空则复用**控制台「GitHub 下载令牌」（`PALLAS_PROTOCOL_GITHUB_TOKEN`）。
3. 维护者命令：
   - `git 检查`：立即轮询一轮
   - `git 状态`：查看开关与游标

预置仓：`PallasBot/Pallas-Bot`、`PallasBot/Pallas-Bot-WebUI`；也可在配置里追加自定义仓库 JSON。

## 行为要点

- 首次启用只记当前 tip，不把历史刷进群。
- 漏更或多条未推送时，**只推最新** Commit / Release 各至多一条。
- 推送失败不积压；tip 前进后只推新 tip。

## 命令权限

| 功能 | 默认等级 |
| --- | --- |
| `git 检查` | 超级用户 |
| `git 状态` | 超级用户 |

## 配置摘要

| 项 | 说明 |
| --- | --- |
| 启用 / 间隔 | 总开关与分钟间隔（≥5） |
| GitHub Token | 可选；空则用内置协议令牌 |
| 推送群号 / QQ / Bot | 目标与发送账号 |
| 监控 Commit / Release | 全局开关 |
| 预置仓 | Pallas-Bot、WebUI + 分支 |
| 自定义仓库 JSON | `[{"owner","repo","branch","commits","releases"}]` |

## License

AGPL-3.0
