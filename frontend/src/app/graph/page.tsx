import Link from "next/link";
import { getEntities, getRelationships } from "@/lib/api";
import { GraphView } from "./GraphView";

export const dynamic = "force-dynamic";

const ENTITY_TYPES = ["king", "olympian", "nymph", "place", "monster", "event", "object", "group", "unknown"];
const RELATIONSHIP_TYPES = ["parent_of", "associated_with"];

type GraphPageProps = {
  searchParams: Promise<{ entity_type?: string; relationship_type?: string }>;
};

function graphHref(entityType?: string, relationshipType?: string) {
  const params = new URLSearchParams();
  if (entityType) {
    params.set("entity_type", entityType);
  }
  if (relationshipType) {
    params.set("relationship_type", relationshipType);
  }
  const query = params.toString();
  return query ? `/graph?${query}` : "/graph";
}

export default async function GraphPage({ searchParams }: GraphPageProps) {
  const { entity_type, relationship_type } = await searchParams;
  const [entities, relationships] = await Promise.all([
    getEntities(entity_type, 1000),
    getRelationships(relationship_type, 1000),
  ]);
  const visibleEntityIds = new Set(entities.map((entity) => entity.id));
  const visibleRelationships = relationships.filter(
    (relationship) =>
      visibleEntityIds.has(relationship.source_entity_id) && visibleEntityIds.has(relationship.target_entity_id),
  );

  return (
    <>
      <div className="eyebrow">Grafo</div>
      <h1>Mapa interativo</h1>
      <p>Visualização das entidades e relações disponíveis na API, com filtros para reduzir o mapa.</p>

      <section className="section">
        <h2>Filtros</h2>
        <div className="filter-block">
          <span className="meta">Entidade</span>
          <div className="filters compact">
            <Link className={!entity_type ? "filter active" : "filter"} href={graphHref(undefined, relationship_type)}>
              todos
            </Link>
            {ENTITY_TYPES.map((type) => (
              <Link
                className={entity_type === type ? "filter active" : "filter"}
                href={graphHref(type, relationship_type)}
                key={type}
              >
                {type}
              </Link>
            ))}
          </div>
        </div>
        <div className="filter-block">
          <span className="meta">Relação</span>
          <div className="filters compact">
            <Link className={!relationship_type ? "filter active" : "filter"} href={graphHref(entity_type, undefined)}>
              todas
            </Link>
            {RELATIONSHIP_TYPES.map((type) => (
              <Link
                className={relationship_type === type ? "filter active" : "filter"}
                href={graphHref(entity_type, type)}
                key={type}
              >
                {type}
              </Link>
            ))}
          </div>
        </div>
        <p className="meta">
          {entities.length} entidades e {visibleRelationships.length} relações visíveis.
        </p>
      </section>

      <section className="section">
        <GraphView entities={entities} relationships={visibleRelationships} />
      </section>
    </>
  );
}
