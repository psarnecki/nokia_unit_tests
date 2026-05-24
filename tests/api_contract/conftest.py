from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import epc.traffic
from epc.api import get_repo
from epc.db import EPCRepository
from main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    repo = EPCRepository(str(tmp_path / "epc.db"))
    app.dependency_overrides[get_repo] = lambda: repo

    tm = MagicMock()
    tm.is_running.return_value = False
    monkeypatch.setattr("epc.api.get_traffic_manager", lambda _: tm)
    monkeypatch.setattr(epc.traffic, "traffic_manager", None)

    yield TestClient(app)

    app.dependency_overrides.clear()
