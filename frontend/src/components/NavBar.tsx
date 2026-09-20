"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import NexusMark from "./NexusMark";

// Nav collante translucide (refonte visuelle 2026-09-20) : logo redessiné en
// SVG (voir NexusMark, remplace le PNG à fond carré) + wordmark espacé, lien
// actif souligné en émeraude. Purement présentation -- aucune route ni appel
// API modifié.
const LINKS = [
  { href: "/", label: "Nouveau projet" },
  { href: "/dashboards", label: "Tableaux de bord" },
];

export default function NavBar() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2.5 text-lg font-normal tracking-[0.08em] text-foreground">
          <NexusMark size={22} className="text-accent" />
          NEXUS
        </Link>
        <nav className="flex gap-6 text-sm">
          {LINKS.map((link) => {
            const active = link.href === "/" ? pathname === "/" : pathname?.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`relative py-1 transition-colors ${
                  active ? "text-foreground" : "text-muted hover:text-foreground"
                }`}
              >
                {link.label}
                {active && <span className="absolute -bottom-[13px] left-0 right-0 h-0.5 rounded-full bg-accent" />}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
