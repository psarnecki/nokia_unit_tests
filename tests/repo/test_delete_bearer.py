import pytest

from epc.models import ThroughputStats


# ---------------------------------------------------------------------------
# TC1 — delete_bearer usuwa bearera ze state.bearers
# ---------------------------------------------------------------------------

def test_delete_bearer_removes_bearer(repo):
    repo.attach_ue(1)
    repo.add_bearer(1, 2)

    repo.delete_bearer(1, 2)

    state = repo.get_ue(1)
    assert 2 not in state.bearers


# ---------------------------------------------------------------------------
# TC2 — bearer 9 jest chroniony → ValueError("Cannot remove default bearer")
# ---------------------------------------------------------------------------

def test_delete_bearer_default_bearer_9_raises_value_error(repo):
    repo.attach_ue(1)

    with pytest.raises(ValueError, match="Cannot remove default bearer"):
        repo.delete_bearer(1, 9)


# ---------------------------------------------------------------------------
# TC3 — sprawdzenie bearer_id == 9 wykonuje się przed get_ue
#       (nieistniejące UE + bearer 9 → "Cannot remove default bearer", nie "UE not found")
# ---------------------------------------------------------------------------

def test_delete_bearer_default_bearer_check_runs_before_ue_lookup(repo):
    with pytest.raises(ValueError, match="Cannot remove default bearer"):
        repo.delete_bearer(99, 9)


# ---------------------------------------------------------------------------
# TC4 — delete nieistniejącego bearera → ValueError("Bearer not found")
# ---------------------------------------------------------------------------

def test_delete_bearer_unknown_bearer_raises_value_error(repo):
    repo.attach_ue(1)

    with pytest.raises(ValueError, match="Bearer not found"):
        repo.delete_bearer(1, 3)


# ---------------------------------------------------------------------------
# TC5 — delete bearera w nieistniejącym UE → ValueError("UE not found")
# ---------------------------------------------------------------------------

def test_delete_bearer_ue_not_found_raises_value_error(repo):
    with pytest.raises(ValueError, match="UE not found"):
        repo.delete_bearer(99, 1)


# ---------------------------------------------------------------------------
# TC6 — delete czyści też stats[bearer_id]
# ---------------------------------------------------------------------------

def test_delete_bearer_also_removes_stats(repo):
    repo.attach_ue(1)
    repo.add_bearer(1, 2)
    repo.update_stats(1, ThroughputStats(bearer_id=2, ue_id=1, bytes_tx=100))
    assert 2 in repo.get_ue(1).stats  # sanity check

    repo.delete_bearer(1, 2)

    state = repo.get_ue(1)
    assert 2 not in state.stats


# ---------------------------------------------------------------------------
# TC7 — delete nie wpływa na inne bearery tego samego UE
# ---------------------------------------------------------------------------

def test_delete_bearer_preserves_other_bearers(repo):
    repo.attach_ue(1)
    repo.add_bearer(1, 2)
    repo.add_bearer(1, 5)

    repo.delete_bearer(1, 2)

    state = repo.get_ue(1)
    assert set(state.bearers.keys()) == {5, 9}


# ---------------------------------------------------------------------------
# TC8 — delete pod jedno UE nie wpływa na bearery innego UE
# ---------------------------------------------------------------------------

def test_delete_bearer_isolated_between_ues(repo):
    repo.attach_ue(1)
    repo.attach_ue(2)
    repo.add_bearer(1, 3)
    repo.add_bearer(2, 3)

    repo.delete_bearer(1, 3)

    assert 3 not in repo.get_ue(1).bearers
    assert 3 in repo.get_ue(2).bearers
