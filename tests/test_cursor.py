from __future__ import annotations

from git_watch.cursor_logic import apply_tip_decision, decide_tip
from git_watch.store import RepoCursor


def test_first_seen_seeds_without_notify():
    decision = decide_tip("", "", "abc123")
    assert decision.action == "seed"
    cursor = RepoCursor()
    apply_tip_decision(cursor, "commit", decision, notified_ok=True)
    assert cursor.last_seen_commit_sha == "abc123"
    assert cursor.last_notified_commit_sha == "abc123"


def test_same_tip_skips():
    decision = decide_tip("abc123", "abc123", "abc123")
    assert decision.action == "skip"


def test_new_tip_notifies_latest_only():
    decision = decide_tip("oldsha", "oldsha", "newsha")
    assert decision.action == "notify"
    assert decision.tip_id == "newsha"


def test_notify_failure_keeps_notified_for_retry_same_tip():
    cursor = RepoCursor(
        last_seen_commit_sha="old",
        last_notified_commit_sha="old",
    )
    decision = decide_tip(cursor.last_seen_commit_sha, cursor.last_notified_commit_sha, "mid")
    apply_tip_decision(cursor, "commit", decision, notified_ok=False)
    assert cursor.last_seen_commit_sha == "mid"
    assert cursor.last_notified_commit_sha == "old"
    decision2 = decide_tip(
        cursor.last_seen_commit_sha,
        cursor.last_notified_commit_sha,
        "latest",
    )
    assert decision2.action == "notify"
    assert decision2.tip_id == "latest"
    apply_tip_decision(cursor, "commit", decision2, notified_ok=True)
    assert cursor.last_notified_commit_sha == "latest"


def test_release_seed_and_notify():
    cursor = RepoCursor()
    seed = decide_tip("", "", "v1.0.0")
    apply_tip_decision(cursor, "release", seed, notified_ok=True)
    assert cursor.last_seen_release_tag == "v1.0.0"
    decision = decide_tip(
        cursor.last_seen_release_tag,
        cursor.last_notified_release_tag,
        "v1.1.0",
    )
    assert decision.action == "notify"
    apply_tip_decision(cursor, "release", decision, notified_ok=True)
    assert cursor.last_notified_release_tag == "v1.1.0"
