from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db import Base


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    canonical_name: Mapped[str | None] = mapped_column(String(255), index=True)
    greek_name: Mapped[str | None] = mapped_column(String(255))
    roman_name: Mapped[str | None] = mapped_column(String(255))
    entity_type: Mapped[str] = mapped_column(String(80), default="unknown", index=True)
    gender: Mapped[str | None] = mapped_column(String(40))
    description: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    aliases: Mapped[list["Alias"]] = relationship(back_populates="entity", cascade="all, delete-orphan")
    outgoing_relationships: Mapped[list["Relationship"]] = relationship(
        foreign_keys="Relationship.source_entity_id",
        back_populates="source_entity",
    )
    incoming_relationships: Mapped[list["Relationship"]] = relationship(
        foreign_keys="Relationship.target_entity_id",
        back_populates="target_entity",
    )


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    author: Mapped[str | None] = mapped_column(String(255))
    tradition: Mapped[str | None] = mapped_column(String(120))
    date_label: Mapped[str | None] = mapped_column(String(120))
    citation: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    source_entity_id: Mapped[str] = mapped_column(ForeignKey("entities.id"), index=True)
    target_entity_id: Mapped[str] = mapped_column(ForeignKey("entities.id"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(80), index=True)
    certainty: Mapped[str] = mapped_column(String(80), default="traditional")
    variant_group: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    source_id: Mapped[str | None] = mapped_column(ForeignKey("sources.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    source_entity: Mapped[Entity] = relationship(foreign_keys=[source_entity_id], back_populates="outgoing_relationships")
    target_entity: Mapped[Entity] = relationship(foreign_keys=[target_entity_id], back_populates="incoming_relationships")
    source: Mapped[Source | None] = relationship()


class Alias(Base):
    __tablename__ = "aliases"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    entity_id: Mapped[str] = mapped_column(ForeignKey("entities.id"), index=True)
    alias: Mapped[str] = mapped_column(String(255), index=True)
    language: Mapped[str | None] = mapped_column(String(80))
    alias_type: Mapped[str | None] = mapped_column(String(80))
    notes: Mapped[str | None] = mapped_column(Text)

    entity: Mapped[Entity] = relationship(back_populates="aliases")


class VisualLayout(Base):
    __tablename__ = "visual_layouts"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    layout_type: Mapped[str] = mapped_column(String(80))
    config_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
