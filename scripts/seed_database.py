from __future__ import annotations

import argparse
import csv
from pathlib import Path

from backend.app.db import SessionLocal
from backend.app.models import Alias, Entity, Relationship


def _load_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def seed_database(
    entities_path: str | Path = "data/seed/entities.csv",
    aliases_path: str | Path = "data/seed/aliases.csv",
    relationships_path: str | Path = "data/seed/relationships.csv",
) -> None:
    session = SessionLocal()
    try:
        for row in _load_csv(entities_path):
            session.merge(Entity(**{key: value or None for key, value in row.items()}))
        for row in _load_csv(aliases_path):
            session.merge(Alias(**{key: value or None for key, value in row.items()}))
        if Path(relationships_path).exists():
            for row in _load_csv(relationships_path):
                session.merge(Relationship(**{key: value or None for key, value in row.items()}))
        session.commit()
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the database from generated CSV files.")
    parser.add_argument("--entities", default="data/seed/entities.csv")
    parser.add_argument("--aliases", default="data/seed/aliases.csv")
    parser.add_argument("--relationships", default="data/seed/relationships.csv")
    args = parser.parse_args()
    seed_database(args.entities, args.aliases, args.relationships)


if __name__ == "__main__":
    main()
