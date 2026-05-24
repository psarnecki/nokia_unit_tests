from epc.models import AttachUERequest

from tests.models.conftest import assert_validation_error


def test_attach_ue_request_valid_boundaries():
    assert AttachUERequest(ue_id=1).ue_id == 1
    assert AttachUERequest(ue_id=100).ue_id == 100


def test_attach_ue_request_rejects_ue_id_below_1():
    assert_validation_error(lambda: AttachUERequest(ue_id=0), "ue_id")


def test_attach_ue_request_rejects_ue_id_above_100():
    assert_validation_error(lambda: AttachUERequest(ue_id=101), "ue_id")
