from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from scripts.normalize_entities import normalize_file as normalize_entities_file
from scripts.normalize_relationships import normalize_file as normalize_relationships_file
from scripts.parse_drawio import parse_drawio_file, write_json
from scripts.seed_database import seed_database


def bootstrap_database(source_drawio: str | Path = "Mitologia grega.drawio") -> None:
    source = Path(source_drawio)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        parsed_path = tmp_path / "drawio_raw.json"
        entities_path = tmp_path / "entities.csv"
        aliases_path = tmp_path / "aliases.csv"
        relationships_path = tmp_path / "relationships.csv"

        write_json(parse_drawio_file(source), parsed_path)
        normalize_entities_file(parsed_path, entities_path, aliases_path)
        normalize_relationships_file(parsed_path, relationships_path)
        seed_database(entities_path, aliases_path, relationships_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse, normalize, and seed the database from the draw.io source.")
    parser.add_argument("--source", default="Mitologia grega.drawio")
    args = parser.parse_args()
    bootstrap_database(args.source)


if __name__ == "__main__":
    main()
