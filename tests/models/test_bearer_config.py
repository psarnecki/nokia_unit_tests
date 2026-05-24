from epc.models import BearerConfig

from tests.models.conftest import assert_validation_error


def test_bearer_config_valid_min_id():
    cfg = BearerConfig(bearer_id=1)
    assert cfg.bearer_id == 1
    assert cfg.protocol is None
    assert cfg.target_bps is None
    assert cfg.active is False


def test_bearer_config_valid_max_id():
    cfg = BearerConfig(bearer_id=9)
    assert cfg.bearer_id == 9


def test_bearer_config_accepts_tcp_and_udp_protocol():
    assert BearerConfig(bearer_id=1, protocol="tcp").protocol == "tcp"
    assert BearerConfig(bearer_id=1, protocol="udp").protocol == "udp"


def test_bearer_config_accepts_target_bps_and_active():
    cfg = BearerConfig(bearer_id=5, target_bps=1_000_000, active=True)
    assert cfg.target_bps == 1_000_000
    assert cfg.active is True


def test_bearer_config_rejects_bearer_id_below_1():
    assert_validation_error(lambda: BearerConfig(bearer_id=0), "bearer_id")


def test_bearer_config_rejects_bearer_id_above_9():
    assert_validation_error(lambda: BearerConfig(bearer_id=10), "bearer_id")


def test_bearer_config_rejects_invalid_protocol():
    assert_validation_error(lambda: BearerConfig(bearer_id=1, protocol="icmp"), "protocol")
