from epc.models import StartTrafficRequest

from tests.models.conftest import assert_validation_error


def _req(**kwargs) -> StartTrafficRequest:
    return StartTrafficRequest(**kwargs)


def test_start_traffic_request_accepts_tcp_and_udp():
    assert _req(protocol="tcp", bps=1).protocol == "tcp"
    assert _req(protocol="udp", bps=1).protocol == "udp"


def test_start_traffic_request_rejects_invalid_protocol():
    assert_validation_error(lambda: _req(protocol="http", bps=1), "protocol")


def test_start_traffic_request_rejects_none_of_throughput_fields():
    assert_validation_error(
        lambda: _req(protocol="tcp"),
        "Provide exactly one throughput value",
    )


def test_start_traffic_request_rejects_two_throughput_fields():
    assert_validation_error(
        lambda: _req(protocol="tcp", Mbps=1.0, kbps=1.0),
        "Provide exactly one throughput value",
    )


def test_start_traffic_request_rejects_all_three_throughput_fields():
    assert_validation_error(
        lambda: _req(protocol="tcp", Mbps=1.0, kbps=1.0, bps=1.0),
        "Provide exactly one throughput value",
    )


def test_start_traffic_request_rejects_negative_throughput_value():
    assert_validation_error(
        lambda: _req(protocol="tcp", Mbps=-40.0),
        "greater than or equal to 0",
    )


def test_start_traffic_request_accepts_zero_throughput_value():
    assert _req(protocol="tcp", Mbps=0).target_bps() == 0


def test_start_traffic_request_rejects_throughput_above_100_mbps():
    assert_validation_error(
        lambda: _req(protocol="tcp", Mbps=180),
        "Maximum supported throughput is 100 Mbps",
    )


def test_target_bps_from_mbps():
    assert _req(protocol="tcp", Mbps=10.0).target_bps() == 10_000_000


def test_target_bps_from_kbps():
    assert _req(protocol="tcp", kbps=512.0).target_bps() == 512_000


def test_target_bps_from_bps():
    assert _req(protocol="tcp", bps=8000).target_bps() == 8000


def test_target_bps_truncates_float_to_int():
    assert _req(protocol="tcp", Mbps=1.5).target_bps() == 1_500_000
