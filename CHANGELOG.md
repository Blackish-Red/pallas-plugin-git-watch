# Changelog

## [Unreleased]

### Changed

- 统一 release 通知事件文案。

## [0.1.1] - 2026-08-11

### Added

- 补充 commit / release 通知推送业务事件日志

## [0.1.0] - 2026-08-01

### Added

- 定时轮询 GitHub Commit / Release，WebUI 配置推送群与好友
- 预置 Pallas-Bot、Pallas-Bot-WebUI；支持自定义仓库 JSON
- 游标防刷屏：首次不推历史，失败不积压，只推最新
- 维护者命令：`git 检查` / `git 状态`
- Token：插件自填优先，否则复用 `PALLAS_PROTOCOL_GITHUB_TOKEN`
