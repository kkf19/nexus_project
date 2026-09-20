// Couleurs de domaine (Areas of Opportunity JCI) — constantes dans toute
// l'application, jamais l'émeraude de marque (réservée à NEXUS lui-même).
// Refonte visuelle 2026-09-20 (NEXUS_design_brief.pdf p.2). Les 4 Areas
// officielles JCI (décision produit actée) sont identifiées par leur
// libellé tel que renvoyé par l'API (`AreaBlock.label`), pas par un code
// deviné : le référentiel de taxonomie est externe et remplaçable, on ne
// suppose donc aucun code fixe ici.
export const DOMAIN_COLORS: Record<string, string> = {
  "Business & Entrepreneurship": "#5B8CFF",
  "Individual Development": "#A78BFA",
  "International Cooperation": "#FF8A5B",
  "Community Impact": "#F472B6",
};

const FALLBACK = "#9AA6A0"; // muted -- domaine non reconnu (ne devrait pas arriver, 4 Areas officielles fixes)

export function domainColor(label: string): string {
  return DOMAIN_COLORS[label] || FALLBACK;
}
