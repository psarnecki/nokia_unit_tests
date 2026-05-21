import pytest
from fastapi import HTTPException

from epc.api import attach_ue
from epc.models import AttachUERequest


def _req(ue_id: int) -> AttachUERequest:
    return AttachUERequest(ue_id=ue_id)


# ---------------------------------------------------------------------------
# TC1 — poprawne dołączenie nowego UE
# ---------------------------------------------------------------------------

def test_attach_ue_returns_attached_status(mock_repo):
    mock_repo.attach_ue.return_value = None

    result = attach_ue(body=_req(1), repo=mock_repo)

    assert result.status == "attached"
    assert result.ue_id == 1


# ---------------------------------------------------------------------------
# TC2 — repo.attach_ue wywołane z właściwym ue_id
# ---------------------------------------------------------------------------

def test_attach_ue_calls_repo_with_correct_ue_id(mock_repo):
    attach_ue(body=_req(42), repo=mock_repo)

    mock_repo.attach_ue.assert_called_once_with(42)


# ---------------------------------------------------------------------------
# TC3 — UE już dołączone → repo rzuca ValueError → HTTP 400
# ---------------------------------------------------------------------------

def test_attach_ue_already_attached_raises_http_400(mock_repo):
    mock_repo.attach_ue.side_effect = ValueError("UE already attached")

    with pytest.raises(HTTPException) as exc_info:
        attach_ue(body=_req(1), repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "UE already attached"


# ---------------------------------------------------------------------------
# TC4 — komunikat błędu z repo trafia do odpowiedzi bez zmian
# ---------------------------------------------------------------------------

def test_attach_ue_error_detail_matches_repo_exception(mock_repo):
    mock_repo.attach_ue.side_effect = ValueError("custom error message")

    with pytest.raises(HTTPException) as exc_info:
        attach_ue(body=_req(1), repo=mock_repo)

    assert exc_info.value.detail == "custom error message"
