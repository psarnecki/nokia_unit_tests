# ---------------------------------------------------------------------------
# TC1 — brak UE w systemie
# ---------------------------------------------------------------------------

def test_list_ues_returns_empty_list_when_no_ues(client, mock_repo):
    mock_repo.list_ues.return_value = []

    response = client.get("/ues")

    assert response.status_code == 200
    assert response.json() == {"ues": []}


# ---------------------------------------------------------------------------
# TC2 — pojedyncze UE
# ---------------------------------------------------------------------------

def test_list_ues_returns_single_ue(client, mock_repo):
    mock_repo.list_ues.return_value = [1]

    response = client.get("/ues")

    assert response.status_code == 200
    assert response.json() == {"ues": [1]}


# ---------------------------------------------------------------------------
# TC3 — wiele UE, kolejność zachowana
# ---------------------------------------------------------------------------

def test_list_ues_returns_multiple_ues_in_order(client, mock_repo):
    mock_repo.list_ues.return_value = [1, 3, 7, 42]

    response = client.get("/ues")

    assert response.status_code == 200
    body = response.json()
    assert body["ues"] == [1, 3, 7, 42]


# ---------------------------------------------------------------------------
# TC4 — repo.list_ues wywołane dokładnie raz
# ---------------------------------------------------------------------------

def test_list_ues_calls_repo_exactly_once(client, mock_repo):
    mock_repo.list_ues.return_value = []

    client.get("/ues")

    mock_repo.list_ues.assert_called_once()
