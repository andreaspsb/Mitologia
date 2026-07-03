import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mitologia",
  description: "Base de conhecimento estruturada sobre mitologia grega.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body>
        <div className="shell">
          <header className="topbar">
            <Link className="brand" href="/">
              Mitologia
            </Link>
            <nav className="nav" aria-label="Navegação principal">
              <Link href="/search">Busca</Link>
              <Link href="/entities">Entidades</Link>
              <Link href="/graph">Grafo</Link>
              <Link href="/audit">Auditoria</Link>
            </nav>
          </header>
          <main className="main">{children}</main>
        </div>
      </body>
    </html>
  );
}
