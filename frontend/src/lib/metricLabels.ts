// Libellés lisibles pour les `metric_code` du catalogue NEXUS
// (measurement_layer.{input_type,output_type,outcome_type} de
// taxonomy.config.json). Ce référentiel donne un `label` par code pour
// activity_family / area_of_opportunity / rise_pillars (classification_axes),
// mais PAS pour les metric_code eux-mêmes (constaté en lisant taxonomy.config.json
// le 2026-09-20) : ils n'ont jamais été prévus pour être montrés tels quels à un
// utilisateur — d'où les codes bruts (DOCUMENTS_PRODUCED, PEOPLE_TRAINED...)
// vus sur l'écran de confirmation et le tableau de bord.
//
// Correctif d'affichage FRONTEND uniquement : la source de vérité du
// catalogue reste taxonomy.config.json (référentiel externe et remplaçable,
// décision produit actée) — si le projet continue après le hackathon, ces
// libellés devraient migrer dans un champ `label_fr` du référentiel lui-même
// (comme les autres axes), pas rester ici en dur. Suit le même principe que
// SDG_LABELS (lib/sdgs.ts) pour les libellés d'ODD.
export const METRIC_LABELS_FR: Record<string, string> = {
  // Ressources (INPUT)
  VOLUNTEERS: "Bénévoles",
  VOLUNTEER_HOURS: "Heures de bénévolat",
  // Productions (OUTPUT)
  PARTICIPANTS: "Participants",
  PEOPLE_TRAINED: "Personnes formées",
  PEOPLE_REACHED_DIRECT: "Personnes touchées directement",
  PEOPLE_REACHED_OUTREACH: "Personnes touchées indirectement",
  REGISTRATIONS: "Inscriptions",
  ATTENDEES: "Présents (jour J)",
  COMPLETIONS: "Personnes ayant terminé",
  APPLICATIONS_ENTRIES: "Candidatures reçues",
  TEAMS: "Équipes",
  ITEMS_DISTRIBUTED: "Objets distribués",
  SIGNATURES: "Signatures",
  AGREEMENTS_SIGNED: "Accords signés",
  DOCUMENTS_PRODUCED: "Documents produits",
  PHYSICAL_OUTPUT: "Production physique",
  COMM_AUDIENCE: "Portée de communication (vues / abonnés)",
  // Résultats (OUTCOME)
  JOBS_CREATED: "Emplois créés",
  JOB_PLACEMENT: "Personnes placées en emploi",
  BUSINESS_CREATED: "Entreprises créées",
  BUSINESS_GROWTH: "Croissance d'entreprise",
  ACCESS_TO_FINANCE_MARKETS: "Accès au financement / aux marchés",
  SKILLS_CONFIDENCE: "Compétences ou confiance acquises",
  AWARENESS_ATTITUDE: "Sensibilisation / changement d'attitude",
  POLICY_INSTITUTIONAL_CHANGE: "Changement politique ou institutionnel",
  FOLLOW_UP_INITIATIVES: "Initiatives de suivi",
  NEW_MEMBERS: "Nouveaux membres JCI",
  PARTNERSHIPS_FORMED: "Partenariats formés",
};

// Filet de sécurité si le référentiel gagne un nouveau code non encore
// listé ci-dessus : jamais un code brut à l'écran, au pire une version
// humanisée ("SOME_NEW_CODE" -> "Some new code") plutôt qu'un blocage.
function humanizeFallback(code: string): string {
  return code
    .toLowerCase()
    .split("_")
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export function metricLabel(code: string | null | undefined): string {
  if (!code) return "Non classé";
  return METRIC_LABELS_FR[code] || humanizeFallback(code);
}
