from __future__ import annotations

from git_watch.config import Config, list_watched_repos, parse_custom_repos


def test_parse_custom_repos_respects_global_flags():
    repos = parse_custom_repos(
        '[{"owner":"Acme","repo":"Demo","branch":"dev","commits":true,"releases":false}]',
        global_commits=True,
        global_releases=True,
    )
    assert len(repos) == 1
    assert repos[0].full_name == "Acme/Demo"
    assert repos[0].branch == "dev"
    assert repos[0].watch_commits is True
    assert repos[0].watch_releases is False


def test_list_watched_repos_presets_and_dedupe():
    cfg = Config(
        git_watch_preset_pallas_bot=True,
        git_watch_preset_pallas_webui=True,
        git_watch_custom_repos_json='[{"owner":"PallasBot","repo":"Pallas-Bot","branch":"main"}]',
    )
    repos = list_watched_repos(cfg)
    names = [r.full_name for r in repos]
    assert names.count("PallasBot/Pallas-Bot") == 1
    assert "PallasBot/Pallas-Bot-WebUI" in names
