from epc.models import BearerConfig, ThroughputStats, UEState

from tests.models.conftest import assert_validation_error


def test_ue_state_none_bearers_and_stats_become_empty_dicts():
    state = UEState(ue_id=1, bearers=None, stats=None)
    assert state.bearers == {}
    assert state.stats == {}


def test_ue_state_default_bearers_and_stats_are_empty_dicts():
    state = UEState(ue_id=1)
    assert state.bearers == {}
    assert state.stats == {}


def test_ue_state_valid_ue_id_boundaries():
    assert UEState(ue_id=1).ue_id == 1
    assert UEState(ue_id=100).ue_id == 100


def test_ue_state_rejects_ue_id_below_1():
    assert_validation_error(lambda: UEState(ue_id=0), "ue_id")


def test_ue_state_rejects_ue_id_above_100():
    assert_validation_error(lambda: UEState(ue_id=101), "ue_id")


def test_ue_state_holds_bearer_and_stats_dicts():
    state = UEState(
        ue_id=5,
        bearers={2: BearerConfig(bearer_id=2)},
        stats={2: ThroughputStats(bearer_id=2, ue_id=5)},
    )
    assert state.bearers[2].bearer_id == 2
    assert state.stats[2].ue_id == 5
