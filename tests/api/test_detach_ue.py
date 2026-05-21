import pytest
from fastapi import HTTPException

from epc.api import detach_ue


# ---------------------------------------------------------------------------
# TC1 — poprawne odpięcie istniejącego UE
# ---------------------------------------------------------------------------

def test_detach_ue_returns_detached_status(mock_repo):
    mock_repo.detach_ue.return_value = None

    result = detach_ue(ue_id=1, repo=mock_repo)

    assert result.status == "detached"
    assert result.ue_id == 1


# ---------------------------------------------------------------------------
# TC2 — repo.detach_ue wywołane z właściwym ue_id
# ---------------------------------------------------------------------------

def test_detach_ue_calls_repo_with_correct_ue_id(mock_repo):
    detach_ue(ue_id=42, repo=mock_repo)

    mock_repo.detach_ue.assert_called_once_with(42)


# ---------------------------------------------------------------------------
# TC3 — UE nie istnieje → repo rzuca ValueError → HTTP 400
# ---------------------------------------------------------------------------

def test_detach_ue_not_found_raises_http_400(mock_repo):
    mock_repo.detach_ue.side_effect = ValueError("UE not found")

    with pytest.raises(HTTPException) as exc_info:
        detach_ue(ue_id=99, repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "UE not found"
