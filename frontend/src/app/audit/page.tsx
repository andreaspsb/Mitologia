import Link from "next/link";
import { getAuditSummary } from "@/lib/api";

export const dynamic = "force-dynamic";

function formatCount(value: number) {
  return new Intl.NumberFormat("pt-BR").format(value);
}

export default async function AuditPage() {
  const audit = await getAuditSummary();

  return (
    <>
      <div className="eyebrow">Auditoria</div>
      <h1>Qualidade dos dados</h1>
      <p>Resumo operacional para revisar entidades sem classificação e relações ainda ambíguas.</p>

      <section className="section">
        <div className="metric-grid">
          <article className="metric">
            <span>Entidades</span>
            <strong>{formatCount(audit.totals.entities)}</strong>
          </article>
          <article className="metric">
            <span>Relacionamentos</span>
            <strong>{formatCount(audit.totals.relationships)}</strong>
          </article>
          <article className="metric warning">
            <span>Unknown</span>
            <strong>{formatCount(audit.totals.unknown_entities)}</strong>
          </article>
          <article className="metric warning">
            <span>Associated</span>
            <strong>{formatCount(audit.totals.associated_relationships)}</strong>
          </article>
        </div>
      </section>

      <section className="section two-column">
        <div>
          <h2>Entidades por tipo</h2>
          <div className="audit-list">
            {Object.entries(audit.entity_type_counts).map(([type, count]) => (
              <div className="audit-row" key={type}>
                <span>{type}</span>
                <strong>{formatCount(count)}</strong>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h2>Relações por tipo</h2>
          <div className="audit-list">
            {Object.entries(audit.relationship_type_counts).map(([type, count]) => (
              <div className="audit-row" key={type}>
                <span>{type}</span>
                <strong>{formatCount(count)}</strong>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section two-column">
        <div>
          <h2>Unknown para revisar</h2>
          <div className="audit-list">
            {audit.unknown_entities.map((entity) => (
              <Link className="audit-row" href={`/entities/${entity.id}`} key={entity.id}>
                <span>{entity.name}</span>
                <strong>{entity.entity_type}</strong>
              </Link>
            ))}
          </div>
        </div>
        <div>
          <h2>Relações ambíguas</h2>
          <div className="audit-list">
            {audit.associated_relationships.map((relationship) => (
              <div className="audit-row stacked" key={relationship.id}>
                <span>
                  {relationship.source_name} → {relationship.target_name}
                </span>
                <strong>{relationship.relationship_type}</strong>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
