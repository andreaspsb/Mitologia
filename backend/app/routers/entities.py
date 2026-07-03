from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from backend.app.db import get_db
from backend.app.models import Alias, Entity, Relationship
from backend.app.schemas import EntityRead, RelationshipRead
from backend.app.routers.relationships import relationship_payload

router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("", response_model=list[EntityRead])
def list_entities(
    entity_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Entity]:
    query = db.query(Entity).options(selectinload(Entity.aliases)).order_by(Entity.name)
    if entity_type:
        query = query.filter(Entity.entity_type == entity_type)
    return query.offset(offset).limit(limit).all()


@router.get("/search/", response_model=list[EntityRead])
def search_entities(q: str, db: Session = Depends(get_db)) -> list[Entity]:
    pattern = f"%{q}%"
    return (
        db.query(Entity)
        .outerjoin(Alias)
        .options(selectinload(Entity.aliases))
        .filter(or_(Entity.name.ilike(pattern), Entity.canonical_name.ilike(pattern), Alias.alias.ilike(pattern)))
        .order_by(Entity.name)
        .limit(50)
        .all()
    )


@router.get("/{entity_id}", response_model=EntityRead)
def get_entity(entity_id: str, db: Session = Depends(get_db)) -> Entity:
    entity = (
        db.query(Entity)
        .options(selectinload(Entity.aliases))
        .filter(Entity.id == entity_id)
        .one_or_none()
    )
    if entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.get("/{entity_id}/relationships", response_model=list[RelationshipRead])
def list_entity_relationships(entity_id: str, db: Session = Depends(get_db)) -> list[dict]:
    relationships = (
        db.query(Relationship)
        .options(selectinload(Relationship.source_entity), selectinload(Relationship.target_entity))
        .filter(or_(Relationship.source_entity_id == entity_id, Relationship.target_entity_id == entity_id))
        .order_by(Relationship.relationship_type)
        .all()
    )
    return [
        relationship_payload(relationship, relationship.source_entity, relationship.target_entity)
        for relationship in relationships
    ]
