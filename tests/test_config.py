from backend.app.config import Settings


def test_sqlalchemy_database_url_uses_psycopg_for_plain_postgres_url():
    settings = Settings(database_url="postgresql://user:pass@host:5432/db")

    assert settings.sqlalchemy_database_url == "postgresql+psycopg://user:pass@host:5432/db"


def test_sqlalchemy_database_url_preserves_explicit_driver():
    settings = Settings(database_url="postgresql+psycopg://user:pass@host:5432/db")

    assert settings.sqlalchemy_database_url == "postgresql+psycopg://user:pass@host:5432/db"
