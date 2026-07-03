from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, aliased

from backend.app.db import get_db
from backend.app.models import Entity, Relationship
from backend.app.schemas import RelationshipRead

router = APIRouter(prefix="/relationships", tags=["relationships"])


def relationship_payload(relationship: Relationship, source: Entity, target: Entity) -> dict:
    return {
        "id": relationship.id,
        "source_entity_id": relationship.source_entity_id,
        "source_name": source.name,
        "target_entity_id": relationship.target_entity_id,
        "target_name": target.name,
        "relationship_type": relationship.relationship_type,
        "certainty": relationship.certainty,
        "variant_group": relationship.variant_group,
        "notes": relationship.notes,
        "source_id": relationship.source_id,
    }


@router.get("", response_model=list[RelationshipRead])
def list_relationships(
    relationship_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict]:
    SourceEntity = aliased(Entity)
    TargetEntity = aliased(Entity)
    query = (
        db.query(Relationship, SourceEntity, TargetEntity)
        .join(SourceEntity, Relationship.source_entity_id == SourceEntity.id)
        .join(TargetEntity, Relationship.target_entity_id == TargetEntity.id)
        .order_by(Relationship.relationship_type)
    )
    if relationship_type:
        query = query.filter(Relationship.relationship_type == relationship_type)
    return [
        relationship_payload(relationship, source, target)
        for relationship, source, target in query.offset(offset).limit(limit).all()
    ]
