import Link from "next/link";
import { getEntities } from "@/lib/api";

export const dynamic = "force-dynamic";

const ENTITY_TYPES = ["king", "olympian", "nymph", "place", "monster", "event", "object", "group", "unknown"];

type EntitiesPageProps = {
  searchParams: Promise<{ type?: string }>;
};

export default async function EntitiesPage({ searchParams }: EntitiesPageProps) {
  const { type } = await searchParams;
  const entities = await getEntities(type);

  return (
    <>
      <div className="eyebrow">Entidades</div>
      <h1>Índice mitológico</h1>
      <p>Lista inicial de entidades importadas e normalizadas a partir do diagrama.</p>

      <nav className="filters" aria-label="Filtros por tipo de entidade">
        <Link className={!type ? "filter active" : "filter"} href="/entities">
          todos
        </Link>
        {ENTITY_TYPES.map((entityType) => (
          <Link
            className={type === entityType ? "filter active" : "filter"}
            href={`/entities?type=${entityType}`}
            key={entityType}
          >
            {entityType}
          </Link>
        ))}
      </nav>

      <section className="section entity-list">
        {entities.map((entity) => (
          <Link className="entity-row" href={`/entities/${entity.id}`} key={entity.id}>
            <strong>{entity.name}</strong>
            <span className="meta">{entity.entity_type}</span>
          </Link>
        ))}
      </section>
    </>
  );
}
