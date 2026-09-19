// Chaque case de la fiche de confirmation porte son origine (impact-science.md
// §6, A6) : "tu l'as écrit" (extrait, avec citation), "déduit — à confirmer"
// (proposé par l'IA), "calculé" (bénévoles × durée, D-30) ou "à remplir"
// (aucune valeur disponible, la responsable doit la saisir).
export type Origin = "written" | "inferred" | "calculated" | "to_fill";

const STYLES: Record<Origin, string> = {
  written: "bg-info-bg text-info border-info/30",
  inferred: "bg-warning-bg text-warning border-warning/30",
  calculated: "bg-border/60 text-muted border-border",
  to_fill: "bg-danger-bg text-danger border-danger/30",
};

const LABELS: Record<Origin, string> = {
  written: "tu l'as écrit",
  inferred: "déduit — à confirmer",
  calculated: "calculé",
  to_fill: "à remplir",
};

export default function OriginBadge({ origin, className = "" }: { origin: Origin; className?: string }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium whitespace-nowrap ${STYLES[origin]} ${className}`}
    >
      {LABELS[origin]}
    </span>
  );
}
