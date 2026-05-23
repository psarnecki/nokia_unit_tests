import pytest

from epc.models import ThroughputStats


# ---------------------------------------------------------------------------
# TC1 — reset_all na pustym repo nie rzuca i zostawia repo puste
# ---------------------------------------------------------------------------

def test_reset_all_on_empty_repo_is_noop(repo):
    repo.reset_all()

    assert list(repo.list_ues()) == []


# ---------------------------------------------------------------------------
# TC2 — po reset_all lista UE jest pusta
# ---------------------------------------------------------------------------

def test_reset_all_clears_all_ues(repo):
    repo.attach_ue(1)
    repo.attach_ue(2)
    repo.attach_ue(50)

    repo.reset_all()

    assert list(repo.list_ues()) == []


# ---------------------------------------------------------------------------
# TC3 — reset_all usuwa też bearery i statystyki (get_ue rzuca "UE not found")
# ---------------------------------------------------------------------------

def test_reset_all_removes_bearers_and_stats(repo):
    repo.attach_ue(1)
    repo.add_bearer(1, 2)
    repo.update_stats(1, ThroughputStats(bearer_id=2, ue_id=1, bytes_tx=100))

    repo.reset_all()

    with pytest.raises(ValueError, match="UE not found"):
        repo.get_ue(1)


# ---------------------------------------------------------------------------
# TC4 — po reset_all można ponownie attach_ue z tym samym ue_id
# ---------------------------------------------------------------------------

def test_reset_all_allows_reattach_with_same_id(repo):
    repo.attach_ue(1)
    repo.reset_all()

    repo.attach_ue(1)

    assert repo.ue_exists(1) is True


# ---------------------------------------------------------------------------
# TC5 — ue_exists zwraca False dla wszystkich wcześniej dołączonych UE
# ---------------------------------------------------------------------------

def test_reset_all_ue_exists_returns_false_for_all(repo):
    for uid in (1, 5, 10, 99):
        repo.attach_ue(uid)

    repo.reset_all()

    for uid in (1, 5, 10, 99):
        assert repo.ue_exists(uid) is False
