import pytest

from epc.models import BearerConfig


# ---------------------------------------------------------------------------
# TC1 — update istniejącego bearera nadpisuje jego pola
# ---------------------------------------------------------------------------

def test_update_bearer_overwrites_existing(repo):
    repo.attach_ue(1)
    repo.add_bearer(1, 2)

    repo.update_bearer(
        1, BearerConfig(bearer_id=2, protocol="tcp", target_bps=1_000_000, active=True)
    )

    bearer = repo.get_ue(1).bearers[2]
    assert bearer.protocol == "tcp"
    assert bearer.target_bps == 1_000_000
    assert bearer.active is True


# ---------------------------------------------------------------------------
# TC2 — update bearera, którego jeszcze nie ma → upsert (zostaje dodany)
# ---------------------------------------------------------------------------

def test_update_bearer_inserts_when_missing(repo):
    repo.attach_ue(1)

    repo.update_bearer(1, BearerConfig(bearer_id=3, protocol="udp", target_bps=500))

    state = repo.get_ue(1)
    assert 3 in state.bearers
    assert state.bearers[3].protocol == "udp"
    assert state.bearers[3].target_bps == 500


# ---------------------------------------------------------------------------
# TC3 — update bearera 9 jest dozwolony (brak ochrony jak w delete_bearer)
# ---------------------------------------------------------------------------

def test_update_bearer_default_bearer_9_is_allowed(repo):
    repo.attach_ue(1)

    repo.update_bearer(1, BearerConfig(bearer_id=9, protocol="tcp", target_bps=2000, active=True))

    bearer = repo.get_ue(1).bearers[9]
    assert bearer.protocol == "tcp"
    assert bearer.target_bps == 2000
    assert bearer.active is True


# ---------------------------------------------------------------------------
# TC4 — update bearera w nieistniejącym UE → ValueError("UE not found")
# ---------------------------------------------------------------------------

def test_update_bearer_ue_not_found_raises_value_error(repo):
    with pytest.raises(ValueError, match="UE not found"):
        repo.update_bearer(99, BearerConfig(bearer_id=1))


# ---------------------------------------------------------------------------
# TC5 — update jednego bearera nie wpływa na inne
# ---------------------------------------------------------------------------

def test_update_bearer_does_not_touch_other_bearers(repo):
    repo.attach_ue(1)
    repo.add_bearer(1, 2)
    repo.add_bearer(1, 5)

    repo.update_bearer(1, BearerConfig(bearer_id=2, protocol="tcp", target_bps=100))

    state = repo.get_ue(1)
    assert state.bearers[5].protocol is None
    assert state.bearers[5].target_bps is None
    assert state.bearers[9].active is False


# ---------------------------------------------------------------------------
# TC6 — update jest izolowane między UE
# ---------------------------------------------------------------------------

def test_update_bearer_isolated_between_ues(repo):
    repo.attach_ue(1)
    repo.attach_ue(2)
    repo.add_bearer(1, 3)
    repo.add_bearer(2, 3)

    repo.update_bearer(1, BearerConfig(bearer_id=3, protocol="tcp", target_bps=100))

    assert repo.get_ue(1).bearers[3].protocol == "tcp"
    assert repo.get_ue(2).bearers[3].protocol is None
