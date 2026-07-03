from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.models import Entity, Relationship

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/summary")
def get_audit_summary(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> dict:
    entity_type_counts = dict(
        db.query(Entity.entity_type, func.count(Entity.id))
        .group_by(Entity.entity_type)
        .order_by(func.count(Entity.id).desc())
        .all()
    )
    relationship_type_counts = dict(
        db.query(Relationship.relationship_type, func.count(Relationship.id))
        .group_by(Relationship.relationship_type)
        .order_by(func.count(Relationship.id).desc())
        .all()
    )

    unknown_entities = (
        db.query(Entity)
        .filter(Entity.entity_type == "unknown")
        .order_by(Entity.name)
        .limit(limit)
        .all()
    )
    SourceEntity = aliased(Entity)
    TargetEntity = aliased(Entity)
    associated_relationships = (
        db.query(Relationship, SourceEntity, TargetEntity)
        .join(SourceEntity, Relationship.source_entity_id == SourceEntity.id)
        .join(TargetEntity, Relationship.target_entity_id == TargetEntity.id)
        .filter(Relationship.relationship_type == "associated_with")
        .order_by(Relationship.id)
        .limit(limit)
        .all()
    )

    relationship_items = []
    for relationship, source_entity, target_entity in associated_relationships:
        relationship_items.append(
            {
                "id": relationship.id,
                "source_entity_id": source_entity.id,
                "source_name": source_entity.name,
                "target_entity_id": target_entity.id,
                "target_name": target_entity.name,
                "relationship_type": relationship.relationship_type,
                "notes": relationship.notes,
            }
        )

    return {
        "totals": {
            "entities": db.query(Entity).count(),
            "relationships": db.query(Relationship).count(),
            "unknown_entities": entity_type_counts.get("unknown", 0),
            "associated_relationships": relationship_type_counts.get("associated_with", 0),
        },
        "entity_type_counts": entity_type_counts,
        "relationship_type_counts": relationship_type_counts,
        "unknown_entities": [
            {
                "id": entity.id,
                "name": entity.name,
                "entity_type": entity.entity_type,
            }
            for entity in unknown_entities
        ],
        "associated_relationships": relationship_items,
    }
