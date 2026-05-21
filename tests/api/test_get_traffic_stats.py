import pytest
from fastapi import HTTPException

from epc.api import get_traffic_stats
from epc.models import ThroughputStats, UEState


def _ue_with_stats(stats: ThroughputStats) -> UEState:
    return UEState(ue_id=stats.ue_id, stats={stats.bearer_id: stats})


# ---------------------------------------------------------------------------
# TC1 — brak statsów dla bearera → zerowa odpowiedź
# ---------------------------------------------------------------------------

def test_get_traffic_stats_returns_zeros_when_no_stats(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = UEState(ue_id=1, stats={})

    result = get_traffic_stats(ue_id=1, bearer_id=9, repo=mock_repo)

    assert result.ue_id == 1
    assert result.bearer_id == 9
    assert result.tx_bps == 0
    assert result.rx_bps == 0
    assert result.duration == 0
    assert result.protocol is None
    assert result.target_bps is None


# ---------------------------------------------------------------------------
# TC2 — statsy istnieją, ruch nieaktywny → obliczenia z last_update_ts
# ---------------------------------------------------------------------------
# bytes_tx=800, bytes_rx=400, start_ts=1000.0, last_update_ts=1002.0
# duration = 2.0 s
# tx_bps = 800 * 8 / 2.0 = 3200
# rx_bps = 400 * 8 / 2.0 = 1600

def test_get_traffic_stats_calculates_bps_when_traffic_stopped(mock_repo, mock_tm):
    stats = ThroughputStats(
        bearer_id=9, ue_id=1,
        bytes_tx=800, bytes_rx=400,
        start_ts=1000.0, last_update_ts=1002.0,
        protocol="tcp", target_bps=8000,
    )
    mock_repo.get_ue.return_value = _ue_with_stats(stats)
    mock_tm.is_running.return_value = False

    result = get_traffic_stats(ue_id=1, bearer_id=9, repo=mock_repo)

    assert result.tx_bps == 3200
    assert result.rx_bps == 1600
    assert result.duration == 2.0
    assert result.protocol == "tcp"
    assert result.target_bps == 8000


# ---------------------------------------------------------------------------
# TC3 — ruch aktywny → end_ts = time.time()
# ---------------------------------------------------------------------------
# bytes_tx=1600, start_ts=1000.0, time.time()=1004.0
# duration = 4.0 s
# tx_bps = 1600 * 8 / 4.0 = 3200
# rx_bps = 800  * 8 / 4.0 = 1600

def test_get_traffic_stats_uses_current_time_when_traffic_running(mock_repo, mock_tm, monkeypatch):
    monkeypatch.setattr("epc.api.time.time", lambda: 1004.0)
    stats = ThroughputStats(
        bearer_id=9, ue_id=1,
        bytes_tx=1600, bytes_rx=800,
        start_ts=1000.0, last_update_ts=1002.0,
    )
    mock_repo.get_ue.return_value = _ue_with_stats(stats)
    mock_tm.is_running.return_value = True

    result = get_traffic_stats(ue_id=1, bearer_id=9, repo=mock_repo)

    assert result.tx_bps == 3200
    assert result.rx_bps == 1600
    assert result.duration == 4.0


# ---------------------------------------------------------------------------
# TC4 — start_ts=None → duration=0, bps=0
# ---------------------------------------------------------------------------

def test_get_traffic_stats_returns_zero_bps_when_no_start_ts(mock_repo, mock_tm):
    stats = ThroughputStats(
        bearer_id=9, ue_id=1,
        bytes_tx=9999, bytes_rx=9999,
        start_ts=None, last_update_ts=None,
    )
    mock_repo.get_ue.return_value = _ue_with_stats(stats)

    result = get_traffic_stats(ue_id=1, bearer_id=9, repo=mock_repo)

    assert result.tx_bps == 0
    assert result.rx_bps == 0
    assert result.duration == 0


# ---------------------------------------------------------------------------
# TC5 — UE nie istnieje → HTTP 400
# ---------------------------------------------------------------------------

def test_get_traffic_stats_ue_not_found_raises_http_400(mock_repo, mock_tm):
    mock_repo.get_ue.side_effect = ValueError("UE not found")

    with pytest.raises(HTTPException) as exc_info:
        get_traffic_stats(ue_id=99, bearer_id=9, repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "UE not found"
