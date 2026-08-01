# AGENTS.md

## 项目

- **名称**：Git 监控 git_watch
- **类型**：Pallas-Bot 4.0 社区插件
- **插件 ID**：`git_watch`（安装目录 `local/plugins/git_watch/`）
- **作者**：Blackish-Red `<blackishred04@163.com>`
- **仓库**：https://github.com/Blackish-Red/pallas-plugin-git-watch
- **依赖**：Pallas-Bot `>=4.0`；调度依赖 `nonebot_plugin_apscheduler`

## 约定

- 仅 `pallas.api.*`（L1）
- GitHub 鉴权：`pallas.api.utils.github_auth_headers`；令牌优先插件配置，否则 `repo_env_raw_value("PALLAS_PROTOCOL_GITHUB_TOKEN")`
- 游标与状态：`data/git_watch/state.json`
- 发版：`CHANGELOG.md` 归档 + `community-index.entry.json` 的 `version` + git tag `vX.Y.Z`
- 改 `community-index.entry.json` 后，记得在 [community-plugin-index](https://github.com/PallasBot/community-plugin-index) 同步条目
