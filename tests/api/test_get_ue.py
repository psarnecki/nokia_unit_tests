import pytest
from fastapi import HTTPException

from epc.api import get_ue
from epc.models import BearerConfig, ThroughputStats, UEState


# ---------------------------------------------------------------------------
# TC1 — UE istnieje, brak bearerów i statystyk
# ---------------------------------------------------------------------------

def test_get_ue_returns_state_for_existing_ue(mock_repo):
    mock_repo.get_ue.return_value = UEState(ue_id=1)

    result = get_ue(ue_id=1, repo=mock_repo)

    assert result.ue_id == 1
    assert result.bearers == {}
    assert result.stats == {}


# ---------------------------------------------------------------------------
# TC2 — repo.get_ue wywołane z właściwym ue_id
# ---------------------------------------------------------------------------

def test_get_ue_calls_repo_with_correct_ue_id(mock_repo):
    mock_repo.get_ue.return_value = UEState(ue_id=7)

    get_ue(ue_id=7, repo=mock_repo)

    mock_repo.get_ue.assert_called_once_with(7)


# ---------------------------------------------------------------------------
# TC3 — UE z bearerami i statystykami — dane przepisane bez zmian
# ---------------------------------------------------------------------------

def test_get_ue_returns_full_state_with_bearers_and_stats(mock_repo):
    bearer = BearerConfig(bearer_id=9)
    stats = ThroughputStats(bearer_id=9, ue_id=1, bytes_tx=100, bytes_rx=50)
    mock_repo.get_ue.return_value = UEState(ue_id=1, bearers={9: bearer}, stats={9: stats})

    result = get_ue(ue_id=1, repo=mock_repo)

    assert 9 in result.bearers
    assert result.bearers[9].bearer_id == 9
    assert result.stats[9].bytes_tx == 100
    assert result.stats[9].bytes_rx == 50


# ---------------------------------------------------------------------------
# TC4 — UE nie istnieje → repo rzuca ValueError → HTTP 400
# ---------------------------------------------------------------------------

def test_get_ue_not_found_raises_http_400(mock_repo):
    mock_repo.get_ue.side_effect = ValueError("UE not found")

    with pytest.raises(HTTPException) as exc_info:
        get_ue(ue_id=99, repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "UE not found"
