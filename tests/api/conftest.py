import pytest
from unittest.mock import MagicMock

from epc.db import EPCRepository
from epc.traffic import TrafficGeneratorManager


@pytest.fixture
def mock_repo():
    return MagicMock(spec=EPCRepository)


@pytest.fixture
def mock_tm(monkeypatch):
    tm = MagicMock(spec=TrafficGeneratorManager)
    tm.is_running.return_value = False
    monkeypatch.setattr("epc.api.get_traffic_manager", lambda _: tm)
    return tm
