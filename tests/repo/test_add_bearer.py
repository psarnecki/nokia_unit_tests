import pytest

from epc.models import BearerConfig


# ---------------------------------------------------------------------------
# TC1 — add_bearer dodaje bearer do state.bearers
# ---------------------------------------------------------------------------

def test_add_bearer_appears_in_state(repo):
    repo.attach_ue(1)

    repo.add_bearer(1, 2)

    state = repo.get_ue(1)
    assert 2 in state.bearers


# ---------------------------------------------------------------------------
# TC2 — dodany bearer to BearerConfig z poprawnym bearer_id i domyślnymi polami
# ---------------------------------------------------------------------------

def test_add_bearer_has_correct_default_config(repo):
    repo.attach_ue(1)

    repo.add_bearer(1, 3)

    state = repo.get_ue(1)
    bearer = state.bearers[3]
    assert isinstance(bearer, BearerConfig)
    assert bearer.bearer_id == 3
    assert bearer.protocol is None
    assert bearer.target_bps is None
    assert bearer.active is False


# ---------------------------------------------------------------------------
# TC3 — duplikat bearer_id → ValueError("Bearer already exists")
# ---------------------------------------------------------------------------

def test_add_bearer_duplicate_raises_value_error(repo):
    repo.attach_ue(1)
    repo.add_bearer(1, 2)

    with pytest.raises(ValueError, match="Bearer already exists"):
        repo.add_bearer(1, 2)


# ---------------------------------------------------------------------------
# TC4 — domyślny bearer 9 zajęty od razu po attach → add_bearer(_, 9) duplikat
# ---------------------------------------------------------------------------

def test_add_bearer_default_bearer_9_already_exists(repo):
    repo.attach_ue(1)

    with pytest.raises(ValueError, match="Bearer already exists"):
        repo.add_bearer(1, 9)


# ---------------------------------------------------------------------------
# TC5 — add_bearer dla nieistniejącego UE → ValueError("UE not found")
# ---------------------------------------------------------------------------

def test_add_bearer_ue_not_found_raises_value_error(repo):
    with pytest.raises(ValueError, match="UE not found"):
        repo.add_bearer(99, 1)


# ---------------------------------------------------------------------------
# TC6 — add_bearer nie wpływa na bearer 9
# ---------------------------------------------------------------------------

def test_add_bearer_preserves_default_bearer_9(repo):
    repo.attach_ue(1)

    repo.add_bearer(1, 2)

    state = repo.get_ue(1)
    assert 9 in state.bearers
    assert state.bearers[9].bearer_id == 9


# ---------------------------------------------------------------------------
# TC7 — kilka bearerów dodanych pod jedno UE
# ---------------------------------------------------------------------------

def test_add_bearer_multiple_bearers_coexist(repo):
    repo.attach_ue(1)

    repo.add_bearer(1, 1)
    repo.add_bearer(1, 5)
    repo.add_bearer(1, 8)

    state = repo.get_ue(1)
    assert set(state.bearers.keys()) == {1, 5, 8, 9}


# ---------------------------------------------------------------------------
# TC8 — add_bearer pod jedno UE nie wpływa na bearery innego UE
# ---------------------------------------------------------------------------

def test_add_bearer_isolated_between_ues(repo):
    repo.attach_ue(1)
    repo.attach_ue(2)

    repo.add_bearer(1, 3)

    assert 3 in repo.get_ue(1).bearers
    assert 3 not in repo.get_ue(2).bearers
