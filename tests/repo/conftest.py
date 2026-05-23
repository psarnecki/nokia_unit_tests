import pytest

from epc.db import EPCRepository


@pytest.fixture
def repo(tmp_path):
    return EPCRepository(db_path=str(tmp_path / "epc.db"))
