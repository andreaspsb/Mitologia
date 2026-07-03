from __future__ import annotations

import argparse
from pathlib import Path

from backend.app.db import SessionLocal
from backend.app.models import Entity, Relationship


def export_dot(entity_type: str | None = None, relationship_type: str | None = None) -> str:
    session = SessionLocal()
    try:
        entity_query = session.query(Entity)
        if entity_type:
            entity_query = entity_query.filter(Entity.entity_type == entity_type)
        entities = {entity.id: entity for entity in entity_query.all()}

        relationship_query = session.query(Relationship)
        if relationship_type:
            relationship_query = relationship_query.filter(Relationship.relationship_type == relationship_type)

        lines = ["digraph Mitologia {", "  rankdir=LR;"]
        for entity in entities.values():
            lines.append(f'  "{entity.id}" [label="{entity.name}"];')
        for relationship in relationship_query.all():
            if relationship.source_entity_id in entities and relationship.target_entity_id in entities:
                lines.append(
                    f'  "{relationship.source_entity_id}" -> "{relationship.target_entity_id}" '
                    f'[label="{relationship.relationship_type}"];'
                )
        lines.append("}")
        return "\n".join(lines)
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export database relationships to Graphviz DOT.")
    parser.add_argument("--entity-type")
    parser.add_argument("--relationship-type")
    parser.add_argument("--output", default="exports/graphviz/mitologia.dot")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(export_dot(args.entity_type, args.relationship_type), encoding="utf-8")


if __name__ == "__main__":
    main()
