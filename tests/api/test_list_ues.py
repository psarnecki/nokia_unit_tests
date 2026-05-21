from epc.api import list_ues
from epc.models import UEListResponse


# ---------------------------------------------------------------------------
# TC1 — brak UE w systemie
# ---------------------------------------------------------------------------

def test_list_ues_returns_empty_list_when_no_ues(mock_repo):
    mock_repo.list_ues.return_value = []

    result = list_ues(repo=mock_repo)

    assert result == UEListResponse(ues=[])


# ---------------------------------------------------------------------------
# TC2 — pojedyncze UE
# ---------------------------------------------------------------------------

def test_list_ues_returns_single_ue(mock_repo):
    mock_repo.list_ues.return_value = [1]

    result = list_ues(repo=mock_repo)

    assert result.ues == [1]


# ---------------------------------------------------------------------------
# TC3 — wiele UE, kolejność zachowana
# ---------------------------------------------------------------------------

def test_list_ues_returns_multiple_ues_in_order(mock_repo):
    mock_repo.list_ues.return_value = [1, 3, 7, 42]

    result = list_ues(repo=mock_repo)

    assert result.ues == [1, 3, 7, 42]


# ---------------------------------------------------------------------------
# TC4 — repo.list_ues wywołane dokładnie raz
# ---------------------------------------------------------------------------

def test_list_ues_calls_repo_exactly_once(mock_repo):
    mock_repo.list_ues.return_value = []

    list_ues(repo=mock_repo)

    mock_repo.list_ues.assert_called_once()
