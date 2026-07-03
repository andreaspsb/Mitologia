import Link from "next/link";
import { getEntity, getEntityRelationships, type Relationship } from "@/lib/api";

export const dynamic = "force-dynamic";

type EntityPageProps = {
  params: Promise<{ id: string }>;
};

function relatedEntityId(relationship: Relationship, currentEntityId: string) {
  return relationship.source_entity_id === currentEntityId
    ? relationship.target_entity_id
    : relationship.source_entity_id;
}

function RelationshipList({
  currentEntityId,
  emptyText,
  relationships,
  title,
}: {
  currentEntityId: string;
  emptyText: string;
  relationships: Relationship[];
  title: string;
}) {
  return (
    <div>
      <h2>{title}</h2>
      {relationships.length ? (
        <div className="entity-list">
          {relationships.map((relationship) => {
            const relatedId = relatedEntityId(relationship, currentEntityId);
            const relatedName =
              relatedId === relationship.source_entity_id
                ? relationship.source_name
                : relationship.target_name;
            return (
              <Link className="entity-row" href={`/entities/${relatedId}`} key={relationship.id}>
                <strong>{relatedName ?? relatedId}</strong>
                <span className="meta">{relationship.relationship_type}</span>
              </Link>
            );
          })}
        </div>
      ) : (
        <p>{emptyText}</p>
      )}
    </div>
  );
}

export default async function EntityPage({ params }: EntityPageProps) {
  const { id } = await params;
  const [entity, relationships] = await Promise.all([
    getEntity(id),
    getEntityRelationships(id),
  ]);
  const parents = relationships.filter(
    (relationship) => relationship.relationship_type === "parent_of" && relationship.target_entity_id === id,
  );
  const children = relationships.filter(
    (relationship) => relationship.relationship_type === "parent_of" && relationship.source_entity_id === id,
  );
  const associations = relationships.filter((relationship) => relationship.relationship_type !== "parent_of");

  return (
    <>
      <div className="eyebrow">{entity.entity_type}</div>
      <h1>{entity.name}</h1>
      <p>{entity.description || "Descrição ainda não cadastrada."}</p>

      <section className="section">
        <h2>Nomes alternativos</h2>
        {entity.aliases.length ? (
          <div className="grid">
            {entity.aliases.map((alias) => (
              <article className="card" key={alias.id}>
                <h3>{alias.alias}</h3>
                <div className="meta">{alias.alias_type || "alias"}</div>
              </article>
            ))}
          </div>
        ) : (
          <p>Nenhum alias registrado.</p>
        )}
      </section>

      <section className="section">
        <div className="relationship-columns">
          <RelationshipList
            currentEntityId={id}
            emptyText="Nenhum pai ou mãe registrado."
            relationships={parents}
            title="Pais"
          />
          <RelationshipList
            currentEntityId={id}
            emptyText="Nenhum filho registrado."
            relationships={children}
            title="Filhos"
          />
          <RelationshipList
            currentEntityId={id}
            emptyText="Nenhuma associação registrada."
            relationships={associations}
            title="Associações"
          />
        </div>
      </section>
    </>
  );
}
