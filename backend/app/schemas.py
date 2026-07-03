from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AliasRead(BaseModel):
    id: str
    entity_id: str
    alias: str
    language: str | None = None
    alias_type: str | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EntityRead(BaseModel):
    id: str
    external_id: str | None = None
    name: str
    canonical_name: str | None = None
    greek_name: str | None = None
    roman_name: str | None = None
    entity_type: str
    gender: str | None = None
    description: str | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    aliases: list[AliasRead] = []

    model_config = ConfigDict(from_attributes=True)


class RelationshipRead(BaseModel):
    id: str
    source_entity_id: str
    source_name: str | None = None
    target_entity_id: str
    target_name: str | None = None
    relationship_type: str
    certainty: str
    variant_group: str | None = None
    notes: str | None = None
    source_id: str | None = None

    model_config = ConfigDict(from_attributes=True)
