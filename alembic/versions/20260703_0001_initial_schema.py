"""Initial schema

Revision ID: 20260703_0001
Revises:
Create Date: 2026-07-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260703_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "entities",
        sa.Column("id", sa.String(length=120), primary_key=True),
        sa.Column("external_id", sa.String(length=120), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("canonical_name", sa.String(length=255), nullable=True),
        sa.Column("greek_name", sa.String(length=255), nullable=True),
        sa.Column("roman_name", sa.String(length=255), nullable=True),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("gender", sa.String(length=40), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_entities_external_id", "entities", ["external_id"], unique=True)
    op.create_index("ix_entities_name", "entities", ["name"])
    op.create_index("ix_entities_canonical_name", "entities", ["canonical_name"])
    op.create_index("ix_entities_entity_type", "entities", ["entity_type"])

    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=120), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("tradition", sa.String(length=120), nullable=True),
        sa.Column("date_label", sa.String(length=120), nullable=True),
        sa.Column("citation", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_sources_title", "sources", ["title"])

    op.create_table(
        "aliases",
        sa.Column("id", sa.String(length=120), primary_key=True),
        sa.Column("entity_id", sa.String(length=120), sa.ForeignKey("entities.id"), nullable=False),
        sa.Column("alias", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=80), nullable=True),
        sa.Column("alias_type", sa.String(length=80), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_aliases_entity_id", "aliases", ["entity_id"])
    op.create_index("ix_aliases_alias", "aliases", ["alias"])

    op.create_table(
        "relationships",
        sa.Column("id", sa.String(length=120), primary_key=True),
        sa.Column("source_entity_id", sa.String(length=120), sa.ForeignKey("entities.id"), nullable=False),
        sa.Column("target_entity_id", sa.String(length=120), sa.ForeignKey("entities.id"), nullable=False),
        sa.Column("relationship_type", sa.String(length=80), nullable=False),
        sa.Column("certainty", sa.String(length=80), nullable=False, server_default="traditional"),
        sa.Column("variant_group", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source_id", sa.String(length=120), sa.ForeignKey("sources.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_relationships_source_entity_id", "relationships", ["source_entity_id"])
    op.create_index("ix_relationships_target_entity_id", "relationships", ["target_entity_id"])
    op.create_index("ix_relationships_relationship_type", "relationships", ["relationship_type"])

    op.create_table(
        "visual_layouts",
        sa.Column("id", sa.String(length=120), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("layout_type", sa.String(length=80), nullable=False),
        sa.Column("config_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_visual_layouts_name", "visual_layouts", ["name"])


def downgrade() -> None:
    op.drop_table("visual_layouts")
    op.drop_table("relationships")
    op.drop_table("aliases")
    op.drop_table("sources")
    op.drop_table("entities")
