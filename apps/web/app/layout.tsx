import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Graph symmetrisation and inducibility",
  description: "Computational companion to arXiv:2012.10731",
};

const links = [
  { href: "/", label: "Symmetrisation" },
  { href: "/optimiser", label: "Optimiser" },
  { href: "/stability", label: "Near-extremal" },
  { href: "/results", label: "Paper results" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <header className="border-b border">
          <div className="mx-auto flex max-w-6xl flex-wrap items-end justify-between gap-4 px-6 py-5">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">arXiv:2012.10731</p>
              <p className="font-serif text-2xl">Graph symmetrisation explorer</p>
            </div>
            <nav className="flex gap-4 text-sm">
              {links.map((link) => (
                <Link key={link.href} href={link.href} className="underline-offset-4 hover:underline">
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
