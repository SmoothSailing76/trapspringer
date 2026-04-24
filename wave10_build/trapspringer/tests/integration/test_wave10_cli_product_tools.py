from pathlib import Path

from trapspringer.adapters.cli.main import main
from trapspringer.services.persistence_service import SessionPersistenceService


def test_cli_save_and_list(tmp_path: Path, capsys=None):
    rc = main(["--no-recap", "--save", "--save-dir", str(tmp_path), "--show-party", "--show-map"])
    assert rc == 0
    rows = SessionPersistenceService(tmp_path).list_saves()
    assert rows
    rc = main(["--list-saves", "--save-dir", str(tmp_path)])
    assert rc == 0


def test_cli_load_save(tmp_path: Path):
    main(["--no-recap", "--save", "--save-dir", str(tmp_path)])
    row = SessionPersistenceService(tmp_path).list_saves()[0]
    rc = main(["--load-save", row["save_id"], "--save-dir", str(tmp_path), "--show-party", "--show-log", "--public-log"])
    assert rc == 0
