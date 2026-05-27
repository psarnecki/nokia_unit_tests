# ---------------------------------------------------------------------------
# TC1 — POST /ues bez pola ue_id → 422
# ---------------------------------------------------------------------------

def test_attach_ue_missing_ue_id_returns_422(client):
    response = client.post("/ues", json={})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC2 — POST /ues z ue_id poniżej zakresu → 422
# ---------------------------------------------------------------------------

def test_attach_ue_below_min_returns_422(client):
    response = client.post("/ues", json={"ue_id": 0})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC3 — POST /ues z ue_id powyżej zakresu → 422
# ---------------------------------------------------------------------------

def test_attach_ue_above_max_returns_422(client):
    response = client.post("/ues", json={"ue_id": 101})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC4 — POST /ues z ue_id zlego typu → 422
# ---------------------------------------------------------------------------

def test_attach_ue_wrong_type_returns_422(client):
    response = client.post("/ues", json={"ue_id": "abc"})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC5 — POST /ues/{ue_id}/bearers bez pola bearer_id → 422
# ---------------------------------------------------------------------------

def test_add_bearer_missing_bearer_id_returns_422(client):
    response = client.post("/ues/1/bearers", json={})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC6 — POST /ues/{ue_id}/bearers z bearer_id poniżej zakresu → 422
# ---------------------------------------------------------------------------

def test_add_bearer_below_min_returns_422(client):
    response = client.post("/ues/1/bearers", json={"bearer_id": 0})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC7 — POST /ues/{ue_id}/bearers z bearer_id powyżej zakresu → 422
# ---------------------------------------------------------------------------

def test_add_bearer_above_max_returns_422(client):
    response = client.post("/ues/1/bearers", json={"bearer_id": 10})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC8 — POST .../traffic bez pola protocol → 422
# ---------------------------------------------------------------------------

def test_start_traffic_missing_protocol_returns_422(client):
    response = client.post(
        "/ues/1/bearers/9/traffic",
        json={"bps": 1000},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC9 — POST .../traffic z niezgodnym z wzorcem protokołem → 422
# ---------------------------------------------------------------------------

def test_start_traffic_invalid_protocol_returns_422(client):
    response = client.post(
        "/ues/1/bearers/9/traffic",
        json={"protocol": "sctp", "bps": 1000},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC10 — POST .../traffic bez żadnej wartości throughput → 422
# ---------------------------------------------------------------------------

def test_start_traffic_no_throughput_returns_422(client):
    response = client.post(
        "/ues/1/bearers/9/traffic",
        json={"protocol": "tcp"},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC11 — POST .../traffic z dwoma wartościami throughput → 422
# ---------------------------------------------------------------------------

def test_start_traffic_two_throughputs_returns_422(client):
    response = client.post(
        "/ues/1/bearers/9/traffic",
        json={"protocol": "tcp", "bps": 1000, "Mbps": 1},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC12 — POST .../traffic ze wszystkimi trzema wartościami throughput→  422
# ---------------------------------------------------------------------------

def test_start_traffic_three_throughputs_returns_422(client):
    response = client.post(
        "/ues/1/bearers/9/traffic",
        json={"protocol": "tcp", "bps": 1000, "Mbps": 1, "kbps": 1},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC13 — POST .../traffic z ujemnym throughput (np. -40 Mbps) → 422
# ---------------------------------------------------------------------------

def test_start_traffic_negative_throughput_returns_422(client):
    client.post("/ues", json={"ue_id": 1})
    response = client.post(
        "/ues/1/bearers/9/traffic",
        json={"protocol": "tcp", "Mbps": -40},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TC14 — POST .../traffic z zerowym throughput (0 Mbps) → 200
# ---------------------------------------------------------------------------

def test_start_traffic_zero_throughput_returns_200(client):
    client.post("/ues", json={"ue_id": 1})
    response = client.post(
        "/ues/1/bearers/9/traffic",
        json={"protocol": "tcp", "Mbps": 0},
    )

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# TC15 — POST .../traffic z throughput > 100 Mbps (np. 180 Mbps) → 422
# ---------------------------------------------------------------------------

def test_start_traffic_above_max_throughput_returns_422(client):
    client.post("/ues", json={"ue_id": 1})
    response = client.post(
        "/ues/1/bearers/9/traffic",
        json={"protocol": "tcp", "Mbps": 180},
    )

    assert response.status_code == 422
