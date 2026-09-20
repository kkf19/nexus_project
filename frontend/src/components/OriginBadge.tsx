// Chaque case de la fiche de confirmation porte son origine (impact-science.md
// §6, A6) : "written" (extrait, avec citation), "inferred" (proposé par
// l'IA), "calculated" (bénévoles × durée, D-30) ou "to_fill" (aucune valeur
// disponible, la responsable doit la saisir).
export type Origin = "written" | "inferred" | "calculated" | "to_fill";

// Revue Product Owner (2026-09-20, P0) : "L'utilisateur n'a pas besoin de
// savoir que NEXUS a fait une opération arithmétique [...] La mécanique
// reste interne." Règle : un badge n'a sa place que si l'utilisateur doit
// prendre une décision à ce sujet.
// - "written" / "calculated" : rien à décider, jamais affiché (inchangé).
// - "to_fill" : une vraie action est requise (aucune valeur disponible),
//   reste visible -- seul badge encore affiché.
//
// CHALLENGE tranché par KKF (2026-09-20, correction de structure) : "inferred"
// ("Suggestion NEXUS") retiré de VISIBLE_ORIGINS -- décision P0 ci-dessus
// SUPERSEDED sur ce point précis, historique gardé plutôt que réécrit.
// Raison : répété sur presque chaque champ de l'écran de confirmation
// (nom du projet, type de comptage, pour qui, familles d'activité, ODD,
// RISE...), le badge n'apportait plus d'information -- tout le monde sait
// déjà que NEXUS a fait la proposition, la répétition alourdissait l'écran
// sans aider une décision. La distinction "à confirmer" reste réelle dans la
// donnée (chaque champ garde son statut d'origine, rien n'est supprimé côté
// data) ; seule sa mise en avant systématique par un badge disparaît. Si
// l'écran doit un jour redire "ces champs sont des suggestions", ce sera une
// seule mention, une fois, pas un badge par champ.
const VISIBLE_ORIGINS: Origin[] = ["to_fill"];

const STYLES: Record<Origin, string> = {
  written: "",
  inferred: "bg-accent/10 text-accent border-accent/30",
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
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium whitespace-nowrap ${STYLES[origin]} ${className}`}
    >
      {origin === "inferred" && (
        <svg width="9" height="9" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M12 1.5C12 8.4 16.6 12 22.5 12 16.6 12 12 15.6 12 22.5 12 15.6 7.4 12 1.5 12 7.4 12 12 8.4 12 1.5Z" />
        </svg>
      )}
      {LABELS[origin]}
    </span>
  );
}
