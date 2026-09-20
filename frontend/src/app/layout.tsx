import type { Metadata } from "next";
import localFont from "next/font/local";
import NavBar from "@/components/NavBar";
import "./globals.css";

// Typo du deck NEXUS : géométrique, légère, très espacée (brief de refonte
// visuelle 2026-09-20). Auto-hébergée via next/font/local (fichier variable
// officiel Jost, licence OFL, sourcé du paquet @fontsource-variable/jost
// uniquement pour extraire le .woff2 -- aucune dépendance npm ajoutée,
// voir src/app/fonts/Jost-Variable.woff2) plutôt que next/font/google :
// le réseau de ce sandbox de vérification bloque fonts.googleapis.com/
// fonts.gstatic.com (politique d'organisation), ce qui aurait fait échouer
// `next build` ici sans qu'on puisse jamais vérifier le build avant de
// pousser -- next/font/local supprime toute dépendance réseau au build,
// sur ce sandbox comme sur Vercel.
const jost = localFont({
  src: "./fonts/Jost-Variable.woff2",
  weight: "100 900",
  variable: "--font-jost",
  display: "swap",
});

export const metadata: Metadata = {
  title: "NEXUS — Suivi d'impact JCI",
  description: "Racontez votre activité, NEXUS s'occupe du reste.",
  icons: { icon: "/logo-nexus.png" },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="fr" className={`h-full antialiased dark ${jost.variable}`} style={{ colorScheme: "dark" }}>
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <NavBar />
        <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
