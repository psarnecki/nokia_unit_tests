import os

from epc.db import EPCRepository
from epc.models import BearerConfig, UEState


# ---------------------------------------------------------------------------
# TC1 — drugi EPCRepository na tym samym pliku widzi dane pierwszego
# ---------------------------------------------------------------------------

def test_data_persists_across_repo_instances(tmp_path):
    db_path = str(tmp_path / "shared.db")
    repo1 = EPCRepository(db_path=db_path)
    repo1.attach_ue(1)
    repo1.add_bearer(1, 2)

    repo2 = EPCRepository(db_path=db_path)

    assert repo2.ue_exists(1) is True
    state = repo2.get_ue(1)
    assert set(state.bearers.keys()) == {2, 9}


# ---------------------------------------------------------------------------
# TC2 — tworzenie instancji na nieistniejącym pliku tworzy plik bazy
# ---------------------------------------------------------------------------

def test_repo_creates_db_file_if_missing(tmp_path):
    db_path = tmp_path / "fresh.db"
    assert not db_path.exists()

    EPCRepository(db_path=str(db_path))

    assert db_path.exists()


# ---------------------------------------------------------------------------
# TC3 — wielokrotne tworzenie EPCRepository na tym samym pliku nie psuje schematu
# ---------------------------------------------------------------------------

def test_multiple_repos_on_same_file_keep_schema(tmp_path):
    db_path = str(tmp_path / "shared.db")
    repo1 = EPCRepository(db_path=db_path)
    repo1.attach_ue(1)

    EPCRepository(db_path=db_path)
    EPCRepository(db_path=db_path)
    repo_final = EPCRepository(db_path=db_path)

    assert repo_final.ue_exists(1) is True


# ---------------------------------------------------------------------------
# TC4 — save_ue używa INSERT OR REPLACE: nadpisuje istniejący wpis bez sprawdzenia czy UE było wcześniej "attached"
# ---------------------------------------------------------------------------

def test_save_ue_replaces_existing_state(repo):
    repo.attach_ue(1)

    new_state = UEState(ue_id=1)
    new_state.bearers[5] = BearerConfig(bearer_id=5)
    repo.save_ue(new_state)

    state = repo.get_ue(1)
    assert set(state.bearers.keys()) == {5}  # bearer 9 został nadpisany


# ---------------------------------------------------------------------------
# TC5 — save_ue wstawia nowe UE nawet bez wcześniejszego attach_ue
# ---------------------------------------------------------------------------

def test_save_ue_inserts_without_prior_attach(repo):
    state = UEState(ue_id=5)
    state.bearers[9] = BearerConfig(bearer_id=9)

    repo.save_ue(state)

    assert repo.ue_exists(5) is True
    assert 9 in repo.get_ue(5).bearers


# ---------------------------------------------------------------------------
# TC6 — gdy db_path nie jest podane, EPCRepository używa wartości EPC_DB_PATH
# ---------------------------------------------------------------------------

def test_default_db_path_from_module_constant(tmp_path, monkeypatch):
    custom_path = str(tmp_path / "from_env.db")
    monkeypatch.setattr("epc.db.EPC_DB_PATH", custom_path)

    repo = EPCRepository()  # bez argumentu db_path
    repo.attach_ue(1)

    assert os.path.exists(custom_path)
    assert repo.ue_exists(1) is True
