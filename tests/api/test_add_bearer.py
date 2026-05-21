import pytest
from fastapi import HTTPException

from epc.api import add_bearer
from epc.models import AddBearerRequest


def _req(bearer_id: int) -> AddBearerRequest:
    return AddBearerRequest(bearer_id=bearer_id)


# ---------------------------------------------------------------------------
# TC1 — poprawne dodanie bearera
# ---------------------------------------------------------------------------

def test_add_bearer_returns_bearer_added_status(mock_repo):
    result = add_bearer(ue_id=1, body=_req(2), repo=mock_repo)

    assert result.status == "bearer_added"
    assert result.ue_id == 1
    assert result.bearer_id == 2


# ---------------------------------------------------------------------------
# TC2 — repo.add_bearer wywołane z właściwym ue_id i bearer_id
# ---------------------------------------------------------------------------

def test_add_bearer_calls_repo_with_correct_ids(mock_repo):
    add_bearer(ue_id=5, body=_req(3), repo=mock_repo)

    mock_repo.add_bearer.assert_called_once_with(5, 3)


# ---------------------------------------------------------------------------
# TC3 — UE nie istnieje → repo rzuca ValueError → HTTP 400
# ---------------------------------------------------------------------------

def test_add_bearer_ue_not_found_raises_http_400(mock_repo):
    mock_repo.add_bearer.side_effect = ValueError("UE not found")

    with pytest.raises(HTTPException) as exc_info:
        add_bearer(ue_id=99, body=_req(1), repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "UE not found"


# ---------------------------------------------------------------------------
# TC4 — bearer już istnieje → repo rzuca ValueError → HTTP 400
# ---------------------------------------------------------------------------

def test_add_bearer_already_exists_raises_http_400(mock_repo):
    mock_repo.add_bearer.side_effect = ValueError("Bearer already exists")

    with pytest.raises(HTTPException) as exc_info:
        add_bearer(ue_id=1, body=_req(2), repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Bearer already exists"
