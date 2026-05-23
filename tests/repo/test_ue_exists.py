# ---------------------------------------------------------------------------
# TC1 — puste repo → False dla dowolnego ue_id
# ---------------------------------------------------------------------------

def test_ue_exists_returns_false_when_empty(repo):
    assert repo.ue_exists(1) is False


# ---------------------------------------------------------------------------
# TC2 — True dla dołączonego UE
# ---------------------------------------------------------------------------

def test_ue_exists_returns_true_after_attach(repo):
    repo.attach_ue(1)

    assert repo.ue_exists(1) is True


# ---------------------------------------------------------------------------
# TC3 — False po detach
# ---------------------------------------------------------------------------

def test_ue_exists_returns_false_after_detach(repo):
    repo.attach_ue(1)
    repo.detach_ue(1)

    assert repo.ue_exists(1) is False


# ---------------------------------------------------------------------------
# TC4 — ue_exists nie myli różnych ue_id
# ---------------------------------------------------------------------------

def test_ue_exists_distinguishes_between_ue_ids(repo):
    repo.attach_ue(1)

    assert repo.ue_exists(1) is True
    assert repo.ue_exists(2) is False
