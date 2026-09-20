// Chaque case de la fiche de confirmation porte son origine (impact-science.md
// §6, A6) : "written" (extrait, avec citation), "inferred" (proposé par
// l'IA), "calculated" (bénévoles × durée, D-30) ou "to_fill" (aucune valeur
// disponible, la responsable doit la saisir).
export type Origin = "written" | "inferred" | "calculated" | "to_fill";

// Revue Product Owner (2026-09-20) : "L'utilisateur n'a pas besoin de savoir
// que NEXUS a fait une opération arithmétique [...] La mécanique reste
// interne." Règle retenue : un badge n'a sa place que si l'utilisateur doit
// prendre une décision à ce sujet.
// - "written" (ce que la personne a écrit elle-même) : rien à décider, rien
//   à afficher. Avant : "tu l'as écrit" — supprimé (§3B de la revue).
// - "calculated" (bénévoles × durée) : un calcul interne, pas une décision.
//   Avant : "calculé" — supprimé (§3C), la valeur reste éditable telle
//   quelle si une correction est nécessaire, sans exposer la mécanique.
// - "inferred" : NEXUS propose une valeur à partir du texte -- l'utilisateur
//   doit la confirmer ou la corriger, donc ça reste visible. Avant : "déduit
//   — à confirmer" (jargon de data governance) -> "Suggestion NEXUS" (§3A).
// - "to_fill" : une vraie action est requise (aucune valeur disponible),
//   reste visible.
const VISIBLE_ORIGINS: Origin[] = ["inferred", "to_fill"];

const STYLES: Record<Origin, string> = {
  written: "",
  inferred: "bg-warning-bg text-warning border-warning/30",
  calculated: "",
  to_fill: "bg-danger-bg text-danger border-danger/30",
};

const LABELS: Record<Origin, string> = {
  written: "",
  inferred: "Suggestion NEXUS",
  calculated: "",
  to_fill: "à compléter",
};

export default function OriginBadge({ origin, className = "" }: { origin: Origin; className?: string }) {
  if (!VISIBLE_ORIGINS.includes(origin)) return null;
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium whitespace-nowrap ${STYLES[origin]} ${className}`}
    >
      {LABELS[origin]}
    </span>
  );
}
