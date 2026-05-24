import pytest
from pydantic import ValidationError


def assert_validation_error(fn, *expected_in_message: str):
    with pytest.raises(ValidationError) as exc_info:
        fn()
    message = str(exc_info.value)
    for fragment in expected_in_message:
        assert fragment in message
