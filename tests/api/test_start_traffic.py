import pytest
from fastapi import HTTPException

from epc.api import start_traffic
from epc.models import BearerConfig, StartTrafficRequest, ThroughputStats, UEState


def _req(protocol: str = "tcp", **kwargs) -> StartTrafficRequest:
    """Build a StartTrafficRequest with exactly one throughput field."""
    if not kwargs:
        kwargs = {"bps": 8000}
    return StartTrafficRequest(protocol=protocol, **kwargs)


def _ue(ue_id: int, bearer_id: int, stats: dict | None = None) -> UEState:
    bearer = BearerConfig(bearer_id=bearer_id)
    return UEState(ue_id=ue_id, bearers={bearer_id: bearer}, stats=stats or {})


# ---------------------------------------------------------------------------
# TC1 — poprawne uruchomienie ruchu, odpowiedź
# ---------------------------------------------------------------------------

def test_start_traffic_returns_traffic_started_status(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(1, 2)

    result = start_traffic(ue_id=1, bearer_id=2, body=_req(bps=8000), repo=mock_repo)

    assert result.status == "traffic_started"
    assert result.ue_id == 1
    assert result.bearer_id == 2
    assert result.target_bps == 8000


# ---------------------------------------------------------------------------
# TC2 — przeliczanie jednostek: Mbps → bps
# ---------------------------------------------------------------------------

def test_start_traffic_converts_mbps_to_bps(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(1, 2)

    result = start_traffic(ue_id=1, bearer_id=2, body=_req(Mbps=10.0), repo=mock_repo)

    assert result.target_bps == 10_000_000


# ---------------------------------------------------------------------------
# TC3 — przeliczanie jednostek: kbps → bps
# ---------------------------------------------------------------------------

def test_start_traffic_converts_kbps_to_bps(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(1, 2)

    result = start_traffic(ue_id=1, bearer_id=2, body=_req(kbps=512.0), repo=mock_repo)

    assert result.target_bps == 512_000


# ---------------------------------------------------------------------------
# TC4 — konfiguracja bearera zaktualizowana przed przekazaniem do tm
# ---------------------------------------------------------------------------

def test_start_traffic_updates_bearer_config(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(1, 2)

    start_traffic(ue_id=1, bearer_id=2, body=_req(protocol="udp", kbps=100.0), repo=mock_repo)

    updated_bearer = mock_repo.update_bearer.call_args[0][1]
    assert updated_bearer.protocol == "udp"
    assert updated_bearer.target_bps == 100_000
    assert updated_bearer.active is True


# ---------------------------------------------------------------------------
# TC5 — repo.update_bearer wywołane z właściwym ue_id
# ---------------------------------------------------------------------------

def test_start_traffic_calls_update_bearer_with_correct_ue_id(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(7, 3)

    start_traffic(ue_id=7, bearer_id=3, body=_req(bps=1000), repo=mock_repo)

    assert mock_repo.update_bearer.call_args[0][0] == 7


# ---------------------------------------------------------------------------
# TC6 — inicjalne statystyki tworzone gdy bearer nie ma jeszcze statsów
# ---------------------------------------------------------------------------

def test_start_traffic_creates_initial_stats_when_none_exist(mock_repo, mock_tm, monkeypatch):
    monkeypatch.setattr("epc.api.time.time", lambda: 1000.0)
    mock_repo.get_ue.return_value = _ue(1, 2, stats={})   # brak statsów

    start_traffic(ue_id=1, bearer_id=2, body=_req(protocol="tcp", bps=8000), repo=mock_repo)

    mock_repo.update_stats.assert_called_once()
    created_stats: ThroughputStats = mock_repo.update_stats.call_args[0][1]
    assert created_stats.bearer_id == 2
    assert created_stats.ue_id == 1
    assert created_stats.start_ts == 1000.0
    assert created_stats.protocol == "tcp"
    assert created_stats.target_bps == 8000


# ---------------------------------------------------------------------------
# TC7 — inicjalne statystyki NIE są tworzone gdy już istnieją
# ---------------------------------------------------------------------------

def test_start_traffic_does_not_overwrite_existing_stats(mock_repo, mock_tm):
    existing_stats = ThroughputStats(bearer_id=2, ue_id=1, bytes_tx=500, start_ts=999.0)
    mock_repo.get_ue.return_value = _ue(1, 2, stats={2: existing_stats})

    start_traffic(ue_id=1, bearer_id=2, body=_req(bps=8000), repo=mock_repo)

    mock_repo.update_stats.assert_not_called()


# ---------------------------------------------------------------------------
# TC8 — tm.start wywołane z ue_id i zaktualizowanym bearerem
# ---------------------------------------------------------------------------

def test_start_traffic_calls_tm_start_with_updated_bearer(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(1, 2)

    start_traffic(ue_id=1, bearer_id=2, body=_req(bps=8000), repo=mock_repo)

    call_ue_id, call_bearer = mock_tm.start.call_args[0]
    assert call_ue_id == 1
    assert call_bearer.active is True


# ---------------------------------------------------------------------------
# TC9 — UE nie istnieje → repo.get_ue rzuca ValueError → HTTP 400
# ---------------------------------------------------------------------------

def test_start_traffic_ue_not_found_raises_http_400(mock_repo, mock_tm):
    mock_repo.get_ue.side_effect = ValueError("UE not found")

    with pytest.raises(HTTPException) as exc_info:
        start_traffic(ue_id=99, bearer_id=2, body=_req(bps=1000), repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "UE not found"


# ---------------------------------------------------------------------------
# TC10 — bearer nie istnieje w UE → HTTP 400
# ---------------------------------------------------------------------------

def test_start_traffic_bearer_not_found_raises_http_400(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = UEState(ue_id=1, bearers={})

    with pytest.raises(HTTPException) as exc_info:
        start_traffic(ue_id=1, bearer_id=9, body=_req(bps=1000), repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Bearer not found"


# ---------------------------------------------------------------------------
# TC11 — tm.start rzuca ValueError (np. ruch już aktywny) → HTTP 400
# ---------------------------------------------------------------------------

def test_start_traffic_already_running_raises_http_400(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(1, 2)
    mock_tm.start.side_effect = ValueError("Traffic already running")

    with pytest.raises(HTTPException) as exc_info:
        start_traffic(ue_id=1, bearer_id=2, body=_req(bps=1000), repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Traffic already running"
