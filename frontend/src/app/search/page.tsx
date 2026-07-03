import Link from "next/link";
import { searchEntities } from "@/lib/api";

export const dynamic = "force-dynamic";

type SearchPageProps = {
  searchParams: Promise<{ q?: string }>;
};

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const { q } = await searchParams;
  const query = q?.trim() ?? "";
  const results = query ? await searchEntities(query) : [];

  return (
    <>
      <div className="eyebrow">Busca</div>
      <h1>Encontrar entidades</h1>
      <p>Pesquise por nome principal ou alias registrado.</p>

      <form className="search-form sectionless" action="/search">
        <label className="sr-only" htmlFor="search-page-input">
          Buscar entidade
        </label>
        <input
          autoFocus
          defaultValue={query}
          id="search-page-input"
          name="q"
          placeholder="Digite um nome ou alias"
          type="search"
        />
        <button type="submit">Buscar</button>
      </form>

      <section className="section entity-list">
        {!query ? (
          <p>Digite um termo para iniciar a busca.</p>
        ) : results.length ? (
          results.map((entity) => (
            <Link className="entity-row" href={`/entities/${entity.id}`} key={entity.id}>
              <span>
                <strong>{entity.name}</strong>
                {entity.aliases.length ? (
                  <span className="inline-meta">
                    {entity.aliases.map((alias) => alias.alias).join(", ")}
                  </span>
                ) : null}
              </span>
              <span className="meta">{entity.entity_type}</span>
            </Link>
          ))
        ) : (
          <p>Nenhum resultado encontrado.</p>
        )}
      </section>
    </>
  );
}
