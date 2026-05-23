# ---------------------------------------------------------------------------
# TC1 — brak UE w repo → pusta lista
# ---------------------------------------------------------------------------

def test_list_ues_returns_empty_when_no_ues(repo):
    assert list(repo.list_ues()) == []


# ---------------------------------------------------------------------------
# TC2 — pojedyncze UE
# ---------------------------------------------------------------------------

def test_list_ues_returns_single_ue(repo):
    repo.attach_ue(1)

    assert list(repo.list_ues()) == [1]


# ---------------------------------------------------------------------------
# TC3 — wiele UE zwróconych rosnąco po ue_id
# ---------------------------------------------------------------------------

def test_list_ues_returns_ues_sorted_ascending(repo):
    repo.attach_ue(42)
    repo.attach_ue(3)
    repo.attach_ue(7)
    repo.attach_ue(1)

    assert list(repo.list_ues()) == [1, 3, 7, 42]


# ---------------------------------------------------------------------------
# TC4 — odłączone UE znika z listy
# ---------------------------------------------------------------------------

def test_list_ues_excludes_detached_ues(repo):
    repo.attach_ue(1)
    repo.attach_ue(2)
    repo.attach_ue(3)
    repo.detach_ue(2)

    assert list(repo.list_ues()) == [1, 3]


# ---------------------------------------------------------------------------
# TC5 — list_ues zwraca elementy typu int
# ---------------------------------------------------------------------------

def test_list_ues_returns_int_values(repo):
    repo.attach_ue(1)

    result = list(repo.list_ues())
    assert all(isinstance(x, int) for x in result)
