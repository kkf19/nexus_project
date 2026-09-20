import type { Aggregate } from "@/lib/types";
import { metricLabel, unitLabel } from "@/lib/metricLabels";

// Une valeur NULL s'affiche "inconnu". Aucune cible, objectif, jauge de
// progression ni pourcentage d'atteinte (D-09, garde-fou produit).
//
// Retrait des colonnes "Statut" et "Entrées" (2026-09-20, retour KKF : "je ne
// comprends pas ce que ça mesure, en quoi c'est utile ?") :
// - "Statut" affichait quasi toujours le même badge ("calculé") : c'est la
//   valeur que le moteur (aggregation_engine.py, to_measurement_object())
//   écrit littéralement en dur pour TOUT agrégat qu'il produit, qu'il
//   combine 1 ou 50 mesures. Elle ne distinguait donc jamais rien à l'écran
//   -- pas une donnée de lecture d'impact, un vestige technique.
// - "Entrées" (a.inputs.length) est une vraie donnée (nombre de mesures
//   effectivement additionnées dans cette ligne) mais n'apporte rien tant
//   qu'elle vaut 1 (le cas courant aujourd'hui, faute de mesures réellement
//   équivalentes entre plusieurs projets) : on ne l'affiche donc plus que
//   quand elle dit quelque chose (> 1), en note à côté de la valeur, jamais
//   comme colonne à part entière.
function distinguishingSuffix(a: Aggregate, siblings: Aggregate[]): string | null {
  if (siblings.length < 2) return null;
  const ieValues = new Set(siblings.map((s) => s.population?.internal_external || ""));
  const iaooiValues = new Set(siblings.map((s) => s.iaooi_class?.value || ""));
  const parts: string[] = [];
  // Le moteur ne fusionne jamais deux mesures dont la population (interne /
  // externe) ou la classification IAOOI diffèrent (equivalence_key()) --
  // même libellé humain, groupes réellement distincts. On ne l'affiche que
  // si ça diffère VRAIMENT entre les lignes de ce tableau (jamais un texte
  // ajouté par défaut).
  if (ieValues.size > 1 && a.population?.internal_external) {
    parts.push(a.population.internal_external === "internal" ? "interne" : "externe");
  }
  if (iaooiValues.size > 1 && a.iaooi_class?.value) {
    parts.push(a.iaooi_class.value.toLowerCase());
  }
  return parts.length > 0 ? parts.join(", ") : null;
}

// Refonte visuelle 2026-09-20 : le tableau devient une grille de tuiles
// "preuve" émeraude (NEXUS_design_brief.pdf p.3, bloc RÉSULTATS MESURÉS) --
// même donnée, même valeurs, même règle "inconnu ≠ 0" (D-13), seule la mise
// en forme change. Reste utilisé uniquement pour le bucket "impact" de la
// Vue d'ensemble (voir dashboards/page.tsx) ; même signature (aggregates,
// onSelect) qu'avant, pas de renommage.
export default function AggregateTable({
  aggregates,
  onSelect,
}: {
  aggregates: Aggregate[];
  onSelect?: (a: Aggregate) => void;
}) {
  if (aggregates.length === 0) {
    return <p className="text-sm text-muted">Aucun agrégat pour ce filtre.</p>;
  }

  const byMetric = new Map<string, Aggregate[]>();
  aggregates.forEach((a) => {
    const list = byMetric.get(a.metric_code) || [];
    list.push(a);
    byMetric.set(a.metric_code, list);
  });

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {aggregates.map((a) => {
        const suffix = distinguishingSuffix(a, byMetric.get(a.metric_code) || []);
        const sourceCount = a.inputs?.length ?? 1;
        const known = a.value !== null && a.value !== undefined;
        return (
          <button
            key={a.measurement_id}
            type="button"
            onClick={() => onSelect?.(a)}
            className={`rounded-xl border border-success/30 bg-success-bg p-4 text-left transition-colors ${
              onSelect ? "hover:border-success/60" : "cursor-default"
            }`}
          >
            <div className="nexus-figure text-4xl text-foreground">
              {known
                ? `${a.value_qualifier === "approx" ? "≈ " : ""}${a.value!.toLocaleString("fr-FR")}`
                : <span className="text-2xl italic text-muted-2">inconnu</span>}
            </div>
            <div className="mt-1.5 text-sm text-foreground" title={`Code interne : ${a.metric_code}`}>
              {metricLabel(a.metric_code)}
              {suffix && <span className="ml-1 text-muted">({suffix})</span>}
            </div>
            <div className="mt-0.5 text-xs text-muted" title={`Code interne : ${a.unit?.code || "—"}`}>
              {unitLabel(a.unit?.code)}
              {sourceCount > 1 && <span className="ml-1.5">· {sourceCount} projets combinés</span>}
            </div>
          </button>
        );
      })}
    </div>
  );
}
