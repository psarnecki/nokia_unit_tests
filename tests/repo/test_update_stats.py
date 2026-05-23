import pytest

from epc.models import ThroughputStats


# ---------------------------------------------------------------------------
# TC1 — update_stats zapisuje statystyki do state.stats[bearer_id]
# ---------------------------------------------------------------------------

def test_update_stats_appears_in_state(repo):
    repo.attach_ue(1)

    repo.update_stats(1, ThroughputStats(bearer_id=9, ue_id=1, bytes_tx=100, bytes_rx=200))

    state = repo.get_ue(1)
    assert 9 in state.stats


# ---------------------------------------------------------------------------
# TC2 — wszystkie pola ThroughputStats są wiernie zachowane
# ---------------------------------------------------------------------------

def test_update_stats_preserves_all_fields(repo):
    repo.attach_ue(1)

    repo.update_stats(
        1,
        ThroughputStats(
            bearer_id=9,
            ue_id=1,
            bytes_tx=1024,
            bytes_rx=2048,
            start_ts=100.0,
            last_update_ts=105.5,
            protocol="tcp",
            target_bps=1_000_000,
        ),
    )

    stats = repo.get_ue(1).stats[9]
    assert stats.bytes_tx == 1024
    assert stats.bytes_rx == 2048
    assert stats.start_ts == 100.0
    assert stats.last_update_ts == 105.5
    assert stats.protocol == "tcp"
    assert stats.target_bps == 1_000_000


# ---------------------------------------------------------------------------
# TC3 — ponowny update_stats z tym samym bearer_id nadpisuje wartości (upsert)
# ---------------------------------------------------------------------------

def test_update_stats_overwrites_existing_entry(repo):
    repo.attach_ue(1)
    repo.update_stats(1, ThroughputStats(bearer_id=9, ue_id=1, bytes_tx=100))

    repo.update_stats(1, ThroughputStats(bearer_id=9, ue_id=1, bytes_tx=999))

    assert repo.get_ue(1).stats[9].bytes_tx == 999


# ---------------------------------------------------------------------------
# TC4 — różne bearer_id koegzystują niezależnie w stats
# ---------------------------------------------------------------------------

def test_update_stats_distinct_bearers_coexist(repo):
    repo.attach_ue(1)
    repo.add_bearer(1, 2)

    repo.update_stats(1, ThroughputStats(bearer_id=2, ue_id=1, bytes_tx=10))
    repo.update_stats(1, ThroughputStats(bearer_id=9, ue_id=1, bytes_tx=20))

    stats = repo.get_ue(1).stats
    assert stats[2].bytes_tx == 10
    assert stats[9].bytes_tx == 20


# ---------------------------------------------------------------------------
# TC5 — update_stats dla nieistniejącego UE → ValueError("UE not found")
# ---------------------------------------------------------------------------

def test_update_stats_ue_not_found_raises_value_error(repo):
    with pytest.raises(ValueError, match="UE not found"):
        repo.update_stats(99, ThroughputStats(bearer_id=9, ue_id=99))


# ---------------------------------------------------------------------------
# TC6 — update_stats nie waliduje istnienia bearera (można zapisać stats
#       dla bearera, którego nie ma w state.bearers)
# ---------------------------------------------------------------------------

def test_update_stats_does_not_validate_bearer_existence(repo):
    repo.attach_ue(1)

    repo.update_stats(1, ThroughputStats(bearer_id=7, ue_id=1, bytes_tx=50))

    state = repo.get_ue(1)
    assert 7 in state.stats
    assert 7 not in state.bearers


# ---------------------------------------------------------------------------
# TC7 — update_stats jest izolowane między UE
# ---------------------------------------------------------------------------

def test_update_stats_isolated_between_ues(repo):
    repo.attach_ue(1)
    repo.attach_ue(2)

    repo.update_stats(1, ThroughputStats(bearer_id=9, ue_id=1, bytes_tx=42))

    assert 9 in repo.get_ue(1).stats
    assert 9 not in repo.get_ue(2).stats
