from epc.api import reset_all


# ---------------------------------------------------------------------------
# TC1 — poprawna odpowiedź
# ---------------------------------------------------------------------------

def test_reset_all_returns_reset_status(mock_repo, mock_tm):
    result = reset_all(repo=mock_repo)

    assert result.status == "reset"


# ---------------------------------------------------------------------------
# TC2 — tm.stop_all wywołane przed repo.reset_all
# ---------------------------------------------------------------------------

def test_reset_all_stops_all_traffic_then_clears_repo(mock_repo, mock_tm):
    call_order = []
    mock_tm.stop_all.side_effect = lambda: call_order.append("stop_all")
    mock_repo.reset_all.side_effect = lambda: call_order.append("reset_all")

    reset_all(repo=mock_repo)

    assert call_order == ["stop_all", "reset_all"]


# ---------------------------------------------------------------------------
# TC3 — repo.reset_all wywołane dokładnie raz
# ---------------------------------------------------------------------------

def test_reset_all_calls_repo_reset_once(mock_repo, mock_tm):
    reset_all(repo=mock_repo)

    mock_repo.reset_all.assert_called_once()


# ---------------------------------------------------------------------------
# TC4 — tm.stop_all wywołane dokładnie raz
# ---------------------------------------------------------------------------

def test_reset_all_calls_tm_stop_all_once(mock_repo, mock_tm):
    reset_all(repo=mock_repo)

    mock_tm.stop_all.assert_called_once()
