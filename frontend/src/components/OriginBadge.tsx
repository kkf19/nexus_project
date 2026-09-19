// Chaque case de la fiche de confirmation porte son origine (dev-brief §3.2) :
// "tu l'as écrit" (extrait, avec citation), "déduit — à confirmer" (IA),
// "ton compte" (système) ou "manquant".
export type Origin = "written" | "inferred" | "account" | "missing";

const STYLES: Record<Origin, string> = {
  written: "bg-info-bg text-info border-info/30",
  inferred: "bg-warning-bg text-warning border-warning/30",
  account: "bg-border/60 text-muted border-border",
  missing: "bg-danger-bg text-danger border-danger/30",
};

const LABELS: Record<Origin, string> = {
  written: "tu l'as écrit",
  inferred: "déduit — à confirmer",
  account: "ton compte",
  missing: "manquant",
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
