from epc.models import (
    AggregatedStatsResponse,
    AttachResponse,
    BearerAddResponse,
    BearerDeleteResponse,
    DetachResponse,
    StatusResponse,
    TrafficStartResponse,
    TrafficStatsResponse,
    TrafficStopResponse,
    UEDisplayResponse,
    UEListResponse,
    UEState,
)


def test_status_response_holds_status():
    resp = StatusResponse(status="ok")
    assert resp.status == "ok"


def test_attach_response_holds_fields():
    resp = AttachResponse(status="attached", ue_id=1)
    assert resp.status == "attached"
    assert resp.ue_id == 1


def test_detach_response_holds_fields():
    resp = DetachResponse(status="detached", ue_id=2)
    assert resp.status == "detached"
    assert resp.ue_id == 2


def test_bearer_add_response_holds_fields():
    resp = BearerAddResponse(status="added", ue_id=1, bearer_id=3)
    assert resp.status == "added"
    assert resp.ue_id == 1
    assert resp.bearer_id == 3


def test_bearer_delete_response_holds_fields():
    resp = BearerDeleteResponse(status="deleted", ue_id=1, bearer_id=3)
    assert resp.status == "deleted"
    assert resp.ue_id == 1
    assert resp.bearer_id == 3


def test_traffic_start_response_holds_fields():
    resp = TrafficStartResponse(
        status="started",
        ue_id=1,
        bearer_id=2,
        target_bps=1000,
    )
    assert resp.status == "started"
    assert resp.ue_id == 1
    assert resp.bearer_id == 2
    assert resp.target_bps == 1000


def test_traffic_stop_response_holds_fields():
    resp = TrafficStopResponse(status="stopped", ue_id=1, bearer_id=2)
    assert resp.status == "stopped"
    assert resp.ue_id == 1
    assert resp.bearer_id == 2


def test_traffic_stats_response_optional_fields_default_to_none():
    resp = TrafficStatsResponse(
        ue_id=1,
        bearer_id=2,
        tx_bps=100,
        rx_bps=200,
        duration=1.5,
    )
    assert resp.protocol is None
    assert resp.target_bps is None


def test_traffic_stats_response_holds_all_fields():
    resp = TrafficStatsResponse(
        ue_id=1,
        bearer_id=2,
        protocol="udp",
        target_bps=500,
        tx_bps=100,
        rx_bps=200,
        duration=1.5,
    )
    assert resp.ue_id == 1
    assert resp.bearer_id == 2
    assert resp.protocol == "udp"
    assert resp.target_bps == 500
    assert resp.tx_bps == 100
    assert resp.rx_bps == 200
    assert resp.duration == 1.5


def test_ue_list_response_holds_ues():
    resp = UEListResponse(ues=[1, 2, 3])
    assert resp.ues == [1, 2, 3]


def test_aggregated_stats_response_holds_fields_without_details():
    resp = AggregatedStatsResponse(
        scope="all",
        ue_count=1,
        bearer_count=1,
        total_tx_bps=0,
        total_rx_bps=0,
    )
    assert resp.scope == "all"
    assert resp.ue_count == 1
    assert resp.bearer_count == 1
    assert resp.total_tx_bps == 0
    assert resp.total_rx_bps == 0
    assert resp.details is None


def test_aggregated_stats_response_holds_fields_with_details():
    details = {"ue:1": {"tx": 100, "rx": 200}}
    resp = AggregatedStatsResponse(
        scope="ue:1",
        ue_count=1,
        bearer_count=1,
        total_tx_bps=100,
        total_rx_bps=200,
        details=details,
    )
    assert resp.scope == "ue:1"
    assert resp.ue_count == 1
    assert resp.bearer_count == 1
    assert resp.total_tx_bps == 100
    assert resp.total_rx_bps == 200
    assert resp.details == details


def test_ue_display_response_inherits_ue_state():
    display = UEDisplayResponse(ue_id=1)
    assert isinstance(display, UEState)
    assert display.ue_id == 1
    assert display.bearers == {}
    assert display.stats == {}
