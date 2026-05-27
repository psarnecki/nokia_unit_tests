# ---------------------------------------------------------------------------
# TC1 — POST /ues zwraca JSON {"status","ue_id"}, status="attached"
# ---------------------------------------------------------------------------

def test_attach_ue_response_shape(client):
    response = client.post("/ues", json={"ue_id": 1})

    data = response.json()
    assert set(data.keys()) == {"status", "ue_id"}
    assert data["status"] == "attached"
    assert data["ue_id"] == 1


# ---------------------------------------------------------------------------
# TC2 — DELETE /ues/{ue_id} zwraca JSON {"status","ue_id"}, status="detached"
# ---------------------------------------------------------------------------

def test_detach_ue_response_shape(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.delete("/ues/1")

    data = response.json()
    assert set(data.keys()) == {"status", "ue_id"}
    assert data["status"] == "detached"
    assert data["ue_id"] == 1


# ---------------------------------------------------------------------------
# TC3 — POST /ues/{ue_id}/bearers zwraca {"status","ue_id","bearer_id"}
# ---------------------------------------------------------------------------

def test_add_bearer_response_shape(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.post("/ues/1/bearers", json={"bearer_id": 3})

    data = response.json()
    assert set(data.keys()) == {"status", "ue_id", "bearer_id"}
    assert data["status"] == "bearer_added"
    assert data["ue_id"] == 1
    assert data["bearer_id"] == 3


# ---------------------------------------------------------------------------
# TC4 — DELETE /ues/{ue_id}/bearers/{bearer_id} zwraca {"status","ue_id","bearer_id"}
# ---------------------------------------------------------------------------

def test_delete_bearer_response_shape(client):
    client.post("/ues", json={"ue_id": 1})
    client.post("/ues/1/bearers", json={"bearer_id": 3})

    response = client.delete("/ues/1/bearers/3")

    data = response.json()
    assert set(data.keys()) == {"status", "ue_id", "bearer_id"}
    assert data["status"] == "bearer_deleted"
    assert data["bearer_id"] == 3


# ---------------------------------------------------------------------------
# TC5 — POST .../traffic zwraca {"status","ue_id","bearer_id","target_bps"}
# ---------------------------------------------------------------------------

def test_start_traffic_response_shape(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.post(
        "/ues/1/bearers/9/traffic",
        json={"protocol": "tcp", "Mbps": 10},
    )

    data = response.json()
    assert set(data.keys()) == {"status", "ue_id", "bearer_id", "target_bps"}
    assert data["status"] == "traffic_started"
    assert data["target_bps"] == 10_000_000


# ---------------------------------------------------------------------------
# TC6 — DELETE .../traffic zwraca {"status","ue_id","bearer_id"}
# ---------------------------------------------------------------------------

def test_stop_traffic_response_shape(client):
    client.post("/ues", json={"ue_id": 1})
    client.post("/ues/1/bearers/9/traffic", json={"protocol": "tcp", "bps": 1000})

    response = client.delete("/ues/1/bearers/9/traffic")

    data = response.json()
    assert set(data.keys()) == {"status", "ue_id", "bearer_id"}
    assert data["status"] == "traffic_stopped"


# ---------------------------------------------------------------------------
# TC7 — GET /ues zwraca {"ues": [...]} z lista intów
# ---------------------------------------------------------------------------

def test_list_ues_response_shape(client):
    client.post("/ues", json={"ue_id": 1})
    client.post("/ues", json={"ue_id": 2})

    response = client.get("/ues")

    data = response.json()
    assert set(data.keys()) == {"ues"}
    assert data["ues"] == [1, 2]


# ---------------------------------------------------------------------------
# TC8 — GET /ues/{ue_id} zwraca {"ue_id","bearers","stats"} z default bearerem
# ---------------------------------------------------------------------------

def test_get_ue_response_shape(client):
    client.post("/ues", json={"ue_id": 1})

    response = client.get("/ues/1")

    data = response.json()
    assert set(data.keys()) == {"ue_id", "bearers", "stats"}
    assert data["ue_id"] == 1
    assert "9" in data["bearers"]
    assert data["stats"] == {}


# ---------------------------------------------------------------------------
# TC9 — GET /ues/stats zwraca scope="all" przy braku filtra
# ---------------------------------------------------------------------------

def test_get_ues_stats_response_shape_scope_all(client):
    response = client.get("/ues/stats")

    data = response.json()
    assert set(data.keys()) == {
        "scope", "ue_count", "bearer_count",
        "total_tx_bps", "total_rx_bps", "details",
    }
    assert data["scope"] == "all"
    assert data["details"] is None

# ---------------------------------------------------------------------------
# TC10 — POST /reset zwraca {"status": "reset"}
# ---------------------------------------------------------------------------

def test_reset_response_shape(client):
    response = client.post("/reset")

    data = response.json()
    assert set(data.keys()) == {"status"}
    assert data["status"] == "reset"


# ---------------------------------------------------------------------------
# TC11 — DELETE /ues/traffic zwraca {"status"}
# ---------------------------------------------------------------------------

def test_stop_all_traffic_response_shape(client):
    response = client.delete("/ues/traffic")

    data = response.json()
    assert set(data.keys()) == {"status"}
    assert data["status"] == "traffic_stopped"


# ---------------------------------------------------------------------------
# TC11 — DELETE /ues/{ue_id}/traffic zwraca {"status"}
# ---------------------------------------------------------------------------

def test_stop_ue_traffic_without_bearer_id_response_shape(client):
    client.post("/ues", json={"ue_id": 1})
    response = client.delete("/ues/1/traffic")

    data = response.json()
    assert set(data.keys()) == {"status"}
    assert data["status"] == "traffic_stopped"


# ---------------------------------------------------------------------------
# TC12 — GET /ues/{ue_id}/traffic zwraca {"ue_id","unit","tx","rx","bearer_count"}
# ---------------------------------------------------------------------------

def test_get_ue_traffic_summary_response_shape(client):
    client.post("/ues", json={"ue_id": 2})
    response = client.get("/ues/2/traffic")

    data = response.json()
    assert set(data.keys()) == {"ue_id", "unit", "tx", "rx", "bearer_count"}
    assert data["ue_id"] == 2
