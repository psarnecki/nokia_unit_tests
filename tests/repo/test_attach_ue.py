import pytest


# ---------------------------------------------------------------------------
# TC1 — attach nowego UE sprawia, że ue_exists zwraca True
# ---------------------------------------------------------------------------

def test_attach_ue_makes_ue_exist(repo):
    repo.attach_ue(1)

    assert repo.ue_exists(1) is True


# ---------------------------------------------------------------------------
# TC2 — attach automatycznie tworzy domyślny bearer 9
# ---------------------------------------------------------------------------

def test_attach_ue_creates_default_bearer_9(repo):
    repo.attach_ue(1)

    state = repo.get_ue(1)
    assert 9 in state.bearers
    assert state.bearers[9].bearer_id == 9


# ---------------------------------------------------------------------------
# TC3 — świeżo dołączone UE ma tylko bearer 9 i puste stats
# ---------------------------------------------------------------------------

def test_attach_ue_has_no_other_bearers_or_stats(repo):
    repo.attach_ue(1)

    state = repo.get_ue(1)
    assert list(state.bearers.keys()) == [9]
    assert state.stats == {}


# ---------------------------------------------------------------------------
# TC4 — ponowny attach tego samego UE → ValueError("UE already attached")
# ---------------------------------------------------------------------------

def test_attach_ue_duplicate_raises_value_error(repo):
    repo.attach_ue(1)

    with pytest.raises(ValueError, match="UE already attached"):
        repo.attach_ue(1)


# ---------------------------------------------------------------------------
# TC5 — attach wielu UE — każde istnieje niezależnie
# ---------------------------------------------------------------------------

def test_attach_ue_multiple_ues_are_independent(repo):
    repo.attach_ue(1)
    repo.attach_ue(2)
    repo.attach_ue(50)

    assert repo.ue_exists(1) is True
    assert repo.ue_exists(2) is True
    assert repo.ue_exists(50) is True
