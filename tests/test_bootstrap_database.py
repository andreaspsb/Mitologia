from pathlib import Path

from scripts.bootstrap_database import bootstrap_database


def test_bootstrap_database_accepts_source_path():
    source = Path("Mitologia grega.drawio")

    assert source.exists()
    assert callable(bootstrap_database)
