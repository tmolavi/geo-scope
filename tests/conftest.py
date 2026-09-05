"""Keep test histories isolated from user data and repository samples."""

import pytest


@pytest.fixture(autouse=True)
def isolated_history(tmp_path, monkeypatch):
    from geo_scope.engine import history_tracker

    path = str(tmp_path / "history.json")
    monkeypatch.setattr(history_tracker, "HISTORY_FILE", path)
    monkeypatch.setenv("GEO_SCOPE_HISTORY_FILE", path)
