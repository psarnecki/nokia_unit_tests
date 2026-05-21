import pytest
from fastapi import HTTPException

from epc.api import delete_bearer
from epc.models import BearerConfig, UEState


def _ue_with_bearer(ue_id: int, bearer_id: int) -> UEState:
    return UEState(ue_id=ue_id, bearers={bearer_id: BearerConfig(bearer_id=bearer_id)})


# ---------------------------------------------------------------------------
# TC1 — poprawne usunięcie bearera, ruch nieaktywny
# ---------------------------------------------------------------------------

def test_delete_bearer_returns_bearer_deleted_status(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue_with_bearer(1, 2)
    mock_tm.is_running.return_value = False

    result = delete_bearer(ue_id=1, bearer_id=2, repo=mock_repo)

    assert result.status == "bearer_deleted"
    assert result.ue_id == 1
    assert result.bearer_id == 2


# ---------------------------------------------------------------------------
# TC2 — repo.delete_bearer wywołane z właściwymi id
# ---------------------------------------------------------------------------

def test_delete_bearer_calls_repo_with_correct_ids(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue_with_bearer(3, 5)
    mock_tm.is_running.return_value = False

    delete_bearer(ue_id=3, bearer_id=5, repo=mock_repo)

    mock_repo.delete_bearer.assert_called_once_with(3, 5)


# ---------------------------------------------------------------------------
# TC3 — ruch aktywny → tm.stop wywołane przed usunięciem
# ---------------------------------------------------------------------------

def test_delete_bearer_stops_traffic_before_deleting(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue_with_bearer(1, 2)
    mock_tm.is_running.return_value = True

    delete_bearer(ue_id=1, bearer_id=2, repo=mock_repo)

    mock_tm.stop.assert_called_once_with(1, 2)
    mock_repo.delete_bearer.assert_called_once_with(1, 2)


# ---------------------------------------------------------------------------
# TC4 — ruch nieaktywny → tm.stop NIE jest wywołane
# ---------------------------------------------------------------------------

def test_delete_bearer_does_not_stop_traffic_when_not_running(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue_with_bearer(1, 2)
    mock_tm.is_running.return_value = False

    delete_bearer(ue_id=1, bearer_id=2, repo=mock_repo)

    mock_tm.stop.assert_not_called()


# ---------------------------------------------------------------------------
# TC5 — UE nie istnieje → repo.get_ue rzuca ValueError → HTTP 400
# ---------------------------------------------------------------------------

def test_delete_bearer_ue_not_found_raises_http_400(mock_repo, mock_tm):
    mock_repo.get_ue.side_effect = ValueError("UE not found")

    with pytest.raises(HTTPException) as exc_info:
        delete_bearer(ue_id=99, bearer_id=2, repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "UE not found"


# ---------------------------------------------------------------------------
# TC6 — bearer nie istnieje w UE → HTTP 400
# ---------------------------------------------------------------------------

def test_delete_bearer_bearer_not_found_raises_http_400(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = UEState(ue_id=1, bearers={})

    with pytest.raises(HTTPException) as exc_info:
        delete_bearer(ue_id=1, bearer_id=9, repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Bearer not found"


# ---------------------------------------------------------------------------
# TC7 — repo.delete_bearer rzuca ValueError (np. próba usunięcia default bearera)
# ---------------------------------------------------------------------------

def test_delete_bearer_repo_error_raises_http_400(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue_with_bearer(1, 9)
    mock_tm.is_running.return_value = False
    mock_repo.delete_bearer.side_effect = ValueError("Cannot remove default bearer")

    with pytest.raises(HTTPException) as exc_info:
        delete_bearer(ue_id=1, bearer_id=9, repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Cannot remove default bearer"
