# ---------------------------------------------------------------------------
# TC1 — GET / zwraca 200 (root)
# ---------------------------------------------------------------------------

def test_root_returns_200(client):
    response = client.get("/")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC2 — GET /ues zwraca 200
# ---------------------------------------------------------------------------

def test_get_ues_returns_200(client):
    response = client.get("/ues")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC3 — POST /ues zwraca 200
# ---------------------------------------------------------------------------

def test_post_ues_returns_200(client):
    response = client.post("/ues", json={"ue_id": 1})

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC4 — GET /ues/{ue_id} po attach zwraca 200
# ---------------------------------------------------------------------------

def test_get_ue_returns_200(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.get("/ues/1")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC5 — DELETE /ues/{ue_id} po attach zwraca 200
# ---------------------------------------------------------------------------

def test_delete_ue_returns_200(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.delete("/ues/1")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC6 — POST /ues/{ue_id}/bearers zwraca 200
# ---------------------------------------------------------------------------

def test_post_bearer_returns_200(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.post("/ues/1/bearers", json={"bearer_id": 3})

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC7 — DELETE /ues/{ue_id}/bearers/{bearer_id} zwraca 200
# ---------------------------------------------------------------------------

def test_delete_bearer_returns_200(client):
    client.post("/ues", json={"ue_id": 1})
    client.post("/ues/1/bearers", json={"bearer_id": 3})

    response = client.delete("/ues/1/bearers/3")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC8 — POST /ues/{ue_id}/bearers/{bearer_id}/traffic zwraca 200
# ---------------------------------------------------------------------------

def test_post_traffic_returns_200(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.post(
        "/ues/1/bearers/9/traffic",
        json={"protocol": "tcp", "bps": 8000},
    )

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC9 — DELETE /ues/{ue_id}/bearers/{bearer_id}/traffic zwraca 200
# ---------------------------------------------------------------------------

def test_delete_traffic_returns_200(client):
    client.post("/ues", json={"ue_id": 1})
    client.post(
        "/ues/1/bearers/9/traffic",
        json={"protocol": "tcp", "bps": 8000},
    )

    response = client.delete("/ues/1/bearers/9/traffic")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC10 — GET /ues/{ue_id}/bearers/{bearer_id}/traffic zwraca 200
# ---------------------------------------------------------------------------

def test_get_traffic_stats_returns_200(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.get("/ues/1/bearers/9/traffic")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC11 — GET /ues/stats zwraca 200
# ---------------------------------------------------------------------------

def test_get_ues_stats_returns_200(client):
    response = client.get("/ues/stats")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC12 — POST /reset zwraca 200
# ---------------------------------------------------------------------------

def test_post_reset_returns_200(client):
    response = client.post("/reset")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC13 — zła metoda HTTP na istniejącej ścieżce zwraca 405
# ---------------------------------------------------------------------------

def test_wrong_method_returns_405(client):
    response = client.put("/ues", json={"ue_id": 1})

    assert response.status_code == 405


# ---------------------------------------------------------------------------
# TC14 — zły typ path param (string zamiast int) zwraca 422
# ---------------------------------------------------------------------------

def test_path_param_wrong_type_returns_422(client):
    response = client.get("/ues/abc")

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC15 — nieznana ścieżka zwraca 404
# ---------------------------------------------------------------------------

def test_unknown_path_returns_404(client):
    response = client.get("/does-not-exist")

    assert response.status_code == 404
