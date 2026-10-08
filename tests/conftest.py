import pytest
from db import connection as db_connection
from db.schema import init_db

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """
    Points the app at a fresh, empty SQLite file for the duration of one test,
    then that file is deleted automatically by pytest afterward.
    """
    test_db_path = tmp_path / "test_snitch.db"
    monkeypatch.setattr(db_connection, "DB_PATH", test_db_path)
    init_db()
    yield test_db_path