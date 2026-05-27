# ---------------------------------------------------------------------------
# TC1 — POST /ues z ue_id już dołączonego UE → 400
# ---------------------------------------------------------------------------

def test_attach_ue_duplicate_returns_400(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.post("/ues", json={"ue_id": 1})

    assert response.status_code == 400
    assert response.json()["detail"] == "UE already attached"


# ---------------------------------------------------------------------------
# TC2 — GET /ues/{ue_id} dla nieistniejącego UE → 400
# ---------------------------------------------------------------------------

def test_get_ue_not_found_returns_400(client):
    response = client.get("/ues/99")

    assert response.status_code == 400
    assert response.json()["detail"] == "UE not found"


# ---------------------------------------------------------------------------
# TC3 — DELETE /ues/{ue_id} dla nieistniejącego UE → 400
# ---------------------------------------------------------------------------

def test_detach_ue_not_found_returns_400(client):
    response = client.delete("/ues/99")

    assert response.status_code == 400
    assert response.json()["detail"] == "UE not found"


# ---------------------------------------------------------------------------
# TC4 — POST /ues/{ue_id}/bearers z bearer_id default → 400
# ---------------------------------------------------------------------------

def test_add_bearer_duplicate_default_returns_400(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.post("/ues/1/bearers", json={"bearer_id": 9})

    assert response.status_code == 400
    assert response.json()["detail"] == "Bearer already exists"


# ---------------------------------------------------------------------------
# TC5 — POST /ues/{ue_id}/bearers z bearer_id już dodanego → 400
# ---------------------------------------------------------------------------

def test_add_bearer_duplicate_returns_400(client):
    client.post("/ues", json={"ue_id": 1})
    client.post("/ues/1/bearers", json={"bearer_id": 3})

    response = client.post("/ues/1/bearers", json={"bearer_id": 3})

    assert response.status_code == 400
    assert response.json()["detail"] == "Bearer already exists"


# ---------------------------------------------------------------------------
# TC6 — POST /ues/{ue_id}/bearers dla nieistniejącego UE → 400
# ---------------------------------------------------------------------------

def test_add_bearer_ue_not_found_returns_400(client):
    response = client.post("/ues/99/bearers", json={"bearer_id": 3})

    assert response.status_code == 400
    assert response.json()["detail"] == "UE not found"


# ---------------------------------------------------------------------------
# TC7 — DELETE /ues/{ue_id}/bearers/9 (usunięcie default berara) → 400
# ---------------------------------------------------------------------------

def test_delete_default_bearer_returns_400(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.delete("/ues/1/bearers/9")

    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot remove default bearer"


# ---------------------------------------------------------------------------
# TC8 — DELETE /ues/{ue_id}/bearers/{bearer_id} dla nieistniejącego bearera → 400
# ---------------------------------------------------------------------------

def test_delete_bearer_not_found_returns_400(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.delete("/ues/1/bearers/3")

    assert response.status_code == 400
    assert response.json()["detail"] == "Bearer not found"


# ---------------------------------------------------------------------------
# TC9 — POST .../traffic dla nieistniejącego UE → 400
# ---------------------------------------------------------------------------

def test_start_traffic_ue_not_found_returns_400(client):
    response = client.post(
        "/ues/99/bearers/9/traffic",
        json={"protocol": "tcp", "bps": 1000},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "UE not found"


# ---------------------------------------------------------------------------
# TC10 — POST .../traffic dla nieistniejącego bearera w UE → 400
# ---------------------------------------------------------------------------

def test_start_traffic_bearer_not_found_returns_400(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.post(
        "/ues/1/bearers/5/traffic",
        json={"protocol": "tcp", "bps": 1000},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Bearer not found"


# ---------------------------------------------------------------------------
# TC11 — POST .../traffic gdy ruch już aktywny → 400
# ---------------------------------------------------------------------------

def test_start_traffic_already_running_returns_400(client, mock_tm):
    mock_tm.start.side_effect = ValueError("Traffic already running")
    client.post("/ues", json={"ue_id": 1})

    response = client.post(
        "/ues/1/bearers/9/traffic",
        json={"protocol": "tcp", "bps": 1000},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Traffic already running"


# ---------------------------------------------------------------------------
# TC12 — GET .../traffic dla nieistniejącego UE → 400
# ---------------------------------------------------------------------------

def test_get_traffic_stats_ue_not_found_returns_400(client):
    response = client.get("/ues/99/bearers/9/traffic")

    assert response.status_code == 400
    assert response.json()["detail"] == "UE not found"


# ---------------------------------------------------------------------------
# TC12b — GET .../traffic dla bearera, który nie należy do UE → 400
# ---------------------------------------------------------------------------

def test_get_traffic_stats_bearer_not_found_returns_400(client):
    client.post("/ues", json={"ue_id": 1})
    response = client.get("/ues/1/bearers/3/traffic")

    assert response.status_code == 400
    assert response.json()["detail"] == "Bearer not found"


# ---------------------------------------------------------------------------
# TC13 — GET /ues/stats?ue_id={nieistniejący} → 200
# ---------------------------------------------------------------------------

def test_get_ues_stats_unknown_ue_returns_200(client):
    response = client.get("/ues/stats", params={"ue_id": 99})

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC14 — DELETE /ues/{ue_id}/traffic (bez bearer_id) → 200
# ---------------------------------------------------------------------------

def test_stop_ue_traffic_without_bearer_id_returns_200(client):
    client.post("/ues", json={"ue_id": 1})
    response = client.delete("/ues/1/traffic")

    assert response.status_code == 200
