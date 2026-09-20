// Marque NEXUS : étoile à 4 branches concaves, sans carré, en émeraude
// (refonte visuelle 2026-09-20, cf. NEXUS_design_brief.pdf p.2 — aucun SVG
// officiel trouvé dans /public, seulement un logo-nexus.png ; redessinée ici
// d'après le dessin du deck plutôt que de garder un carré noir en fond).
// Présentation uniquement : composant purement décoratif, aucune logique.
export default function NexusMark({ size = 24, className = "" }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className={className}
    >
      <path
        d="M12 1.5C12 8.4 16.6 12 22.5 12 16.6 12 12 15.6 12 22.5 12 15.6 7.4 12 1.5 12 7.4 12 12 8.4 12 1.5Z"
        fill="currentColor"
      />
    </svg>
  );
}
