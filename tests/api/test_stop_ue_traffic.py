import pytest
from fastapi import HTTPException

from epc.api import stop_ue_traffic
from epc.models import BearerConfig, UEState


def _ue(ue_id: int, bearers: dict[int, bool]) -> UEState:
    # bearers: bearer_id -> active flag
    return UEState(
        ue_id=ue_id,
        bearers={
            b_id: BearerConfig(bearer_id=b_id, active=active) for b_id, active in bearers.items()
        },
        stats={},
    )


def test_stop_ue_traffic_without_bearer_id_stops_all_bearers(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(1, {2: True, 3: True})

    result = stop_ue_traffic(ue_id=1, bearer_id=None, repo=mock_repo)

    assert result.status == "traffic_stopped"
    mock_tm.stop_ue.assert_called_once_with(1)
    # Two bearers should be updated to active=False.
    assert mock_repo.update_bearer.call_count == 2


def test_stop_ue_traffic_with_bearer_id_stops_single_bearer(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(1, {2: True, 3: False})

    result = stop_ue_traffic(ue_id=1, bearer_id=2, repo=mock_repo)

    assert result.status == "traffic_stopped"
    mock_tm.stop.assert_called_once_with(1, 2)
    mock_repo.update_bearer.assert_called_once()


def test_stop_ue_traffic_ue_not_found_raises_http_400(mock_repo, mock_tm):
    mock_repo.get_ue.side_effect = ValueError("UE not found")

    with pytest.raises(HTTPException) as exc_info:
        stop_ue_traffic(ue_id=99, bearer_id=None, repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "UE not found"


def test_stop_ue_traffic_bearer_not_found_raises_http_400(mock_repo, mock_tm):
    mock_repo.get_ue.return_value = _ue(1, {2: True})

    with pytest.raises(HTTPException) as exc_info:
        stop_ue_traffic(ue_id=1, bearer_id=9, repo=mock_repo)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Bearer not found"

