// Regroupement d'affichage des mesures/agrégats en blocs visuellement
// distincts. Contrainte non négociable (garde-fou produit, D-22) : le bloc
// "Impact" doit être visuellement séparé des ressources et de la portée de
// communication — jamais la même couleur, jamais le même bloc.
export type DisplayBucket = "resource" | "activity" | "impact" | "reach" | "other";

export function classifyIaooi(iaooiValue: string | undefined, metricCode: string | undefined): DisplayBucket {
  if (metricCode === "COMM_AUDIENCE") return "reach";
  switch (iaooiValue) {
    case "INPUT":
      return "resource";
    case "ACTIVITY":
    case "OUTPUT":
      return "activity";
    case "OUTCOME":
    case "IMPACT_CLAIM":
      return "impact";
    case "CONTEXT":
      return "reach";
    default:
      return "other";
  }
}

export const BUCKET_LABEL: Record<DisplayBucket, string> = {
  resource: "Ressources mobilisées (bénévoles, heures)",
  activity: "Activités et bénéficiaires",
  impact: "Impact",
  reach: "Portée de communication — non compté comme bénéficiaires",
  other: "Autres mesures",
};

// Styles délibérément différents (bordure + fond) pour qu'Impact ne soit
// jamais confondu visuellement avec les ressources ou la portée.
export const BUCKET_STYLE: Record<DisplayBucket, string> = {
  resource: "border-border bg-surface",
  activity: "border-border bg-surface",
  impact: "border-success/50 bg-success-bg",
  reach: "border-border bg-background",
  other: "border-border bg-surface",
};
