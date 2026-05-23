import pytest

from epc.models import UEState


# ---------------------------------------------------------------------------
# TC1 — get_ue zwraca UEState z poprawnym ue_id
# ---------------------------------------------------------------------------

def test_get_ue_returns_ue_state_with_correct_id(repo):
    repo.attach_ue(1)

    state = repo.get_ue(1)

    assert isinstance(state, UEState)
    assert state.ue_id == 1


# ---------------------------------------------------------------------------
# TC2 — get_ue zwraca UEState zawierający domyślny bearer 9
# ---------------------------------------------------------------------------

def test_get_ue_includes_default_bearer_9(repo):
    repo.attach_ue(1)

    state = repo.get_ue(1)

    assert 9 in state.bearers
    assert state.bearers[9].bearer_id == 9
    assert state.bearers[9].active is False


# ---------------------------------------------------------------------------
# TC3 — świeżo dołączone UE ma puste stats
# ---------------------------------------------------------------------------

def test_get_ue_has_empty_stats_after_attach(repo):
    repo.attach_ue(1)

    state = repo.get_ue(1)

    assert state.stats == {}


# ---------------------------------------------------------------------------
# TC4 — get_ue dla nieistniejącego UE → ValueError("UE not found")
# ---------------------------------------------------------------------------

def test_get_ue_not_found_raises_value_error(repo):
    with pytest.raises(ValueError, match="UE not found"):
        repo.get_ue(99)


# ---------------------------------------------------------------------------
# TC5 — get_ue po detach → ValueError("UE not found")
# ---------------------------------------------------------------------------

def test_get_ue_after_detach_raises_value_error(repo):
    repo.attach_ue(1)
    repo.detach_ue(1)

    with pytest.raises(ValueError, match="UE not found"):
        repo.get_ue(1)
