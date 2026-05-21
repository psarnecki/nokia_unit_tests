import pytest
from fastapi import HTTPException

from epc.api import stop_traffic
from epc.models import BearerConfig, UEState


def _ue(ue_id: int, bearer_id: int) -> UEState:
    return UEState(ue_id=ue_id, bearers={bearer_id: BearerConfig(bearer_id=bearer_id)})


# ---------------------------------------------------------------------------
# TC1 — poprawne zatrzymanie ruchu, odpowiedź
# ---------------------------------------------------------------------------

def test_stop_traffic_returns_traffic_stopped_status(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(1, 2)

    result = stop_traffic(ue_id=1, bearer_id=2, repo=mock_repo)

    assert result.status == "traffic_stopped"
    assert result.ue_id == 1
    assert result.bearer_id == 2


# ---------------------------------------------------------------------------
# TC2 — tm.stop wywołane z właściwymi id
# ---------------------------------------------------------------------------

def test_stop_traffic_calls_tm_stop_with_correct_ids(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(3, 5)

    stop_traffic(ue_id=3, bearer_id=5, repo=mock_repo)

    mock_tm.stop.assert_called_once_with(3, 5)


# ---------------------------------------------------------------------------
# TC3 — bearer.active ustawione na False przed zapisem do repo
# ---------------------------------------------------------------------------

def test_stop_traffic_marks_bearer_inactive(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(1, 2)

    stop_traffic(ue_id=1, bearer_id=2, repo=mock_repo)

    updated_bearer = mock_repo.update_bearer.call_args[0][1]
    assert updated_bearer.active is False


# ---------------------------------------------------------------------------
# TC4 — repo.update_bearer wywołane z właściwym ue_id
# ---------------------------------------------------------------------------

def test_stop_traffic_calls_update_bearer_with_correct_ue_id(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(7, 3)

    stop_traffic(ue_id=7, bearer_id=3, repo=mock_repo)

    assert mock_repo.update_bearer.call_args[0][0] == 7


# ---------------------------------------------------------------------------
# TC5 — UE nie istnieje → repo.get_ue rzuca ValueError → HTTP 400
# ---------------------------------------------------------------------------

def test_stop_traffic_ue_not_found_raises_http_400(mock_repo, mock_tm):
    mock_repo.get_ue.side_effect = ValueError("UE not found")

    with pytest.raises(HTTPException) as exc_info:
        stop_traffic(ue_id=99, bearer_id=2, repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "UE not found"


# ---------------------------------------------------------------------------
# TC6 — bearer nie istnieje w UE → HTTP 400
# ---------------------------------------------------------------------------

def test_stop_traffic_bearer_not_found_raises_http_400(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = UEState(ue_id=1, bearers={})

    with pytest.raises(HTTPException) as exc_info:
        stop_traffic(ue_id=1, bearer_id=9, repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Bearer not found"
