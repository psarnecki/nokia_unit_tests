import pytest
from unittest.mock import MagicMock
from starlette.testclient import TestClient

from main import app
from epc.api import get_repo
from epc.db import EPCRepository
from epc.traffic import TrafficGeneratorManager


@pytest.fixture
def mock_repo():
    return MagicMock(spec=EPCRepository)


@pytest.fixture
def mock_tm():
    tm = MagicMock(spec=TrafficGeneratorManager)
    tm.is_running.return_value = False
    return tm


@pytest.fixture
def client(mock_repo, mock_tm, monkeypatch):
    monkeypatch.setattr("epc.api.get_traffic_manager", lambda _: mock_tm)
    app.dependency_overrides[get_repo] = lambda: mock_repo
    yield TestClient(app)
    app.dependency_overrides.clear()
