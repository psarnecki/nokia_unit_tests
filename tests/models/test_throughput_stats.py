from epc.models import ThroughputStats

from tests.models.conftest import assert_validation_error


def test_throughput_stats_bytes_default_to_zero():
    stats = ThroughputStats(bearer_id=1, ue_id=1)
    assert stats.bytes_tx == 0
    assert stats.bytes_rx == 0


def test_throughput_stats_optional_timestamps_and_protocol_default_to_none():
    stats = ThroughputStats(bearer_id=1, ue_id=1)
    assert stats.start_ts is None
    assert stats.last_update_ts is None
    assert stats.protocol is None
    assert stats.target_bps is None


def test_throughput_stats_accepts_optional_fields():
    stats = ThroughputStats(
        bearer_id=2,
        ue_id=3,
        bytes_tx=100,
        bytes_rx=200,
        start_ts=1.0,
        last_update_ts=2.0,
        protocol="tcp",
        target_bps=1_000_000,
    )
    assert stats.bytes_tx == 100
    assert stats.bytes_rx == 200
    assert stats.protocol == "tcp"
    assert stats.target_bps == 1_000_000


def test_throughput_stats_requires_bearer_id_and_ue_id():
    assert_validation_error(lambda: ThroughputStats(), "bearer_id")
    assert_validation_error(lambda: ThroughputStats(bearer_id=1), "ue_id")
