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

// A7 -- écran 1 (impact-science.md §7) : "Personnes touchées — public
// externe" et "Membres JCI mobilisés/formés" sont chacun UNE somme de
// mesures directes (jamais l'audience, jamais l'indirect), jamais mélangées
// entre interne et externe (R7). Restreint à l'unité "person" : ne somme
// jamais des heures ou une autre unité avec un décompte de personnes.
import type { Aggregate } from "./types";

export function sumDirectPeople(
  aggregates: Aggregate[],
  internalExternal: "internal" | "external"
): { value: number; hasUnknown: boolean; count: number } {
  const rows = aggregates.filter(
    (a) =>
      a.metric_code !== "COMM_AUDIENCE" &&
      a.unit?.code === "person" &&
      a.population?.count_type === "direct" &&
      a.population?.internal_external === internalExternal
  );
  const known = rows.filter((a) => a.value !== null && a.value !== undefined);
  return {
    value: known.reduce((sum, a) => sum + (a.value as number), 0),
    hasUnknown: known.length < rows.length,
    count: rows.length,
  };
}
