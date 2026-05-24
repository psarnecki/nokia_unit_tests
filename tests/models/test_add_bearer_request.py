from epc.models import AddBearerRequest

from tests.models.conftest import assert_validation_error


def test_add_bearer_request_valid_boundaries():
    assert AddBearerRequest(bearer_id=1).bearer_id == 1
    assert AddBearerRequest(bearer_id=9).bearer_id == 9


def test_add_bearer_request_rejects_bearer_id_below_1():
    assert_validation_error(lambda: AddBearerRequest(bearer_id=0), "bearer_id")


def test_add_bearer_request_rejects_bearer_id_above_9():
    assert_validation_error(lambda: AddBearerRequest(bearer_id=10), "bearer_id")
