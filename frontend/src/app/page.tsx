import Link from "next/link";

export default function HomePage() {
  return (
    <>
      <section className="hero">
        <div className="eyebrow">Fonte única da verdade</div>
        <h1>Mitologia grega em dados navegáveis</h1>
        <p>
          O diagrama original passa a alimentar uma base estruturada com entidades, aliases,
          relações, fontes e visualizações geradas.
        </p>
        <form className="search-form" action="/search">
          <label className="sr-only" htmlFor="home-search">
            Buscar entidade
          </label>
          <input id="home-search" name="q" placeholder="Zeus, Hera, Troia..." type="search" />
          <button type="submit">Buscar</button>
        </form>
        <div className="actions">
          <Link className="button" href="/entities">
            Ver entidades
          </Link>
          <Link className="button secondary" href="/graph">
            Abrir grafo
          </Link>
          <Link className="button secondary" href="/audit">
            Ver auditoria
          </Link>
        </div>
      </section>

      <section className="section">
        <h2>Primeira versão</h2>
        <div className="grid">
          <article className="card">
            <h3>Parser draw.io</h3>
            <p>Extrai nós, arestas, estilos e geometria do arquivo original.</p>
          </article>
          <article className="card">
            <h3>Base Postgres</h3>
            <p>Guarda entidades, aliases e relações em um modelo evolutivo.</p>
          </article>
          <article className="card">
            <h3>API e site</h3>
            <p>Expõe dados para páginas navegáveis e visualizações interativas.</p>
          </article>
          <article className="card">
            <h3>Auditoria</h3>
            <p>Mostra tipos inferidos, relações ambíguas e entidades que ainda pedem revisão.</p>
          </article>
        </div>
      </section>
    </>
  );
}
