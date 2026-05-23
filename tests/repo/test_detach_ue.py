import pytest


# ---------------------------------------------------------------------------
# TC1 — detach istniejącego UE sprawia, że ue_exists zwraca False
# ---------------------------------------------------------------------------

def test_detach_ue_removes_ue(repo):
    repo.attach_ue(1)

    repo.detach_ue(1)

    assert repo.ue_exists(1) is False


# ---------------------------------------------------------------------------
# TC2 — detach nieistniejącego UE → ValueError("UE not found")
# ---------------------------------------------------------------------------

def test_detach_ue_not_found_raises_value_error(repo):
    with pytest.raises(ValueError, match="UE not found"):
        repo.detach_ue(99)


# ---------------------------------------------------------------------------
# TC3 — detach nie usuwa innych UE
# ---------------------------------------------------------------------------

def test_detach_ue_does_not_affect_other_ues(repo):
    repo.attach_ue(1)
    repo.attach_ue(2)

    repo.detach_ue(1)

    assert repo.ue_exists(1) is False
    assert repo.ue_exists(2) is True


# ---------------------------------------------------------------------------
# TC4 — po detach można ponownie dołączyć UE z tym samym id
# ---------------------------------------------------------------------------

def test_detach_ue_allows_reattach_with_same_id(repo):
    repo.attach_ue(1)
    repo.detach_ue(1)

    repo.attach_ue(1)

    assert repo.ue_exists(1) is True


# ---------------------------------------------------------------------------
# TC5 — drugi detach tego samego UE → ValueError("UE not found")
# ---------------------------------------------------------------------------

def test_detach_ue_twice_raises_value_error(repo):
    repo.attach_ue(1)
    repo.detach_ue(1)

    with pytest.raises(ValueError, match="UE not found"):
        repo.detach_ue(1)
