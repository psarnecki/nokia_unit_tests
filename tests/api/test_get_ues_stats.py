from unittest.mock import MagicMock

from epc.models import ThroughputStats, UEState


# ---------------------------------------------------------------------------
# TC1 — brak UE w systemie
# ---------------------------------------------------------------------------

def test_no_ues_returns_empty_aggregated_stats(client, mock_repo):
    mock_repo.list_ues.return_value = []

    response = client.get("/ues/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["scope"] == "all"
    assert body["ue_count"] == 0
    assert body["bearer_count"] == 0
    assert body["total_tx_bps"] == 0
    assert body["total_rx_bps"] == 0
    assert body["details"] is None


# ---------------------------------------------------------------------------
# TC2 — UE istnieje, ale nie ma statystyk
# ---------------------------------------------------------------------------

def test_ue_with_no_stats_returns_zero_bps(client, mock_repo):
    mock_repo.list_ues.return_value = [1]
    mock_repo.get_ue.return_value = UEState(ue_id=1, stats={})

    response = client.get("/ues/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["ue_count"] == 1
    assert body["bearer_count"] == 0
    assert body["total_tx_bps"] == 0
    assert body["total_rx_bps"] == 0


# ---------------------------------------------------------------------------
# TC3 — statystyki istnieją, ruch nieaktywny (is_running=False)
# ---------------------------------------------------------------------------
# bytes_tx=800, bytes_rx=400, start_ts=1000.0, last_update_ts=1001.0
# duration = 1001.0 - 1000.0 = 1.0 s
# tx_bps = 800 * 8 / 1.0 = 6400
# rx_bps = 400 * 8 / 1.0 = 3200
# Note: start_ts must be non-zero — the endpoint uses truthiness check `if stats.start_ts`,
# so 0.0 would be treated as "no start time" and duration would be 0.

def test_stats_with_traffic_stopped_calculates_bps_from_last_update_ts(client, mock_repo, mock_tm):
    stats = ThroughputStats(
        bearer_id=9,
        ue_id=1,
        bytes_tx=800,
        bytes_rx=400,
        start_ts=1000.0,
        last_update_ts=1001.0,
    )
    mock_repo.list_ues.return_value = [1]
    mock_repo.get_ue.return_value = UEState(ue_id=1, stats={9: stats})
    mock_tm.is_running.return_value = False

    response = client.get("/ues/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["bearer_count"] == 1
    assert body["total_tx_bps"] == 6400
    assert body["total_rx_bps"] == 3200


# ---------------------------------------------------------------------------
# TC4 — statystyki istnieją, ruch aktywny (is_running=True), time.time mockowany
# ---------------------------------------------------------------------------
# bytes_tx=1600, start_ts=1000.0, time.time()=1002.0  →  duration=2.0
# tx_bps = 1600 * 8 / 2.0 = 6400
# rx_bps = 800  * 8 / 2.0 = 3200

def test_stats_with_traffic_running_uses_current_time(client, mock_repo, mock_tm, monkeypatch):
    monkeypatch.setattr("epc.api.time.time", lambda: 1002.0)

    stats = ThroughputStats(
        bearer_id=9,
        ue_id=1,
        bytes_tx=1600,
        bytes_rx=800,
        start_ts=1000.0,
        last_update_ts=1001.0,
    )
    mock_repo.list_ues.return_value = [1]
    mock_repo.get_ue.return_value = UEState(ue_id=1, stats={9: stats})
    mock_tm.is_running.return_value = True

    response = client.get("/ues/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["total_tx_bps"] == 6400   # 1600 * 8 / 2.0
    assert body["total_rx_bps"] == 3200   # 800 * 8 / 2.0


# ---------------------------------------------------------------------------
# TC5 — start_ts=None → duration=0, bps=0
# ---------------------------------------------------------------------------

def test_stats_with_no_start_ts_returns_zero_bps(client, mock_repo):
    stats = ThroughputStats(
        bearer_id=9,
        ue_id=1,
        bytes_tx=9999,
        bytes_rx=9999,
        start_ts=None,
        last_update_ts=None,
    )
    mock_repo.list_ues.return_value = [1]
    mock_repo.get_ue.return_value = UEState(ue_id=1, stats={9: stats})

    response = client.get("/ues/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["total_tx_bps"] == 0
    assert body["total_rx_bps"] == 0


# ---------------------------------------------------------------------------
# TC6 — filtrowanie po istniejącym ue_id
# ---------------------------------------------------------------------------

def test_filter_by_existing_ue_id_returns_scoped_stats(client, mock_repo):
    mock_repo.ue_exists.return_value = True
    mock_repo.get_ue.return_value = UEState(ue_id=1, stats={})

    response = client.get("/ues/stats?ue_id=1")

    assert response.status_code == 200
    body = response.json()
    assert body["scope"] == "ue:1"
    assert body["ue_count"] == 1
    mock_repo.ue_exists.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# TC7 — filtrowanie po nieistniejącym ue_id
# ---------------------------------------------------------------------------

def test_filter_by_nonexistent_ue_id_returns_400(client, mock_repo):
    mock_repo.ue_exists.return_value = False

    response = client.get("/ues/stats?ue_id=99")

    assert response.status_code == 400
    assert response.json()["detail"] == "UE not found"


# ---------------------------------------------------------------------------
# TC8 — include_details=True
# ---------------------------------------------------------------------------

def test_include_details_populates_per_ue_per_bearer_dict(client, mock_repo, mock_tm):
    stats = ThroughputStats(
        bearer_id=9,
        ue_id=1,
        bytes_tx=800,
        bytes_rx=400,
        start_ts=1000.0,
        last_update_ts=1001.0,
    )
    mock_repo.list_ues.return_value = [1]
    mock_repo.get_ue.return_value = UEState(ue_id=1, stats={9: stats})
    mock_tm.is_running.return_value = False

    response = client.get("/ues/stats?include_details=true")

    assert response.status_code == 200
    body = response.json()
    assert body["details"] is not None
    assert "1" in body["details"]
    assert "9" in body["details"]["1"]
    assert body["details"]["1"]["9"] == 6400


# ---------------------------------------------------------------------------
# TC9 — race condition: list_ues zwraca id, ale get_ue rzuca ValueError
# ---------------------------------------------------------------------------

def test_get_ue_value_error_is_skipped_when_no_ue_id_filter(client, mock_repo):
    mock_repo.list_ues.return_value = [1]
    mock_repo.get_ue.side_effect = ValueError("UE not found")

    response = client.get("/ues/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["ue_count"] == 1
    assert body["bearer_count"] == 0


# ---------------------------------------------------------------------------
# TC10 — wiele UE, wiele bearerów — weryfikacja sumowania
# ---------------------------------------------------------------------------
# UE1: bearer 1 → tx=800, rx=400, duration=1.0  → tx_bps=6400, rx_bps=3200
#       bearer 2 → tx=400, rx=200, duration=2.0  → tx_bps=1600, rx_bps=800
# UE2: bearer 1 → tx=200, rx=100, duration=1.0  → tx_bps=1600, rx_bps=800
#       bearer 2 → tx=100, rx=50,  duration=1.0  → tx_bps=800,  rx_bps=400
# total_tx_bps = 6400+1600+1600+800 = 10400
# total_rx_bps = 3200+800+800+400   = 5200

def test_multiple_ues_and_bearers_sums_bps_correctly(client, mock_repo, mock_tm):
    ue1_stats = {
        1: ThroughputStats(bearer_id=1, ue_id=1, bytes_tx=800, bytes_rx=400, start_ts=1000.0, last_update_ts=1001.0),
        2: ThroughputStats(bearer_id=2, ue_id=1, bytes_tx=400, bytes_rx=200, start_ts=1000.0, last_update_ts=1002.0),
    }
    ue2_stats = {
        1: ThroughputStats(bearer_id=1, ue_id=2, bytes_tx=200, bytes_rx=100, start_ts=1000.0, last_update_ts=1001.0),
        2: ThroughputStats(bearer_id=2, ue_id=2, bytes_tx=100, bytes_rx=50,  start_ts=1000.0, last_update_ts=1001.0),
    }
    mock_repo.list_ues.return_value = [1, 2]
    mock_repo.get_ue.side_effect = [
        UEState(ue_id=1, stats=ue1_stats),
        UEState(ue_id=2, stats=ue2_stats),
    ]
    mock_tm.is_running.return_value = False

    response = client.get("/ues/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["ue_count"] == 2
    assert body["bearer_count"] == 4
    assert body["total_tx_bps"] == 10400
    assert body["total_rx_bps"] == 5200
