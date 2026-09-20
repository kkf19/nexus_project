import Image from "next/image";
import Link from "next/link";

export default function NavBar() {
  return (
    <header className="border-b border-border bg-surface">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2 text-base font-semibold tracking-tight">
          <Image src="/logo-nexus.png" alt="" width={28} height={28} className="rounded-md" priority />
          NEXUS
        </Link>
        <nav className="flex gap-4 text-sm">
          <Link href="/" className="text-muted hover:text-foreground">
            Nouveau projet
          </Link>
          <Link href="/dashboards" className="text-muted hover:text-foreground">
            Tableaux de bord
          </Link>
        </nav>
      </div>
    </header>
  );
}
