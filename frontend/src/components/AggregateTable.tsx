import type { Aggregate } from "@/lib/types";
import { metricLabel } from "@/lib/metricLabels";

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
    <table className="w-full border-collapse text-sm">
      <thead>
        <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
          <th className="py-2 pr-3 font-medium">Indicateur</th>
          <th className="py-2 pr-3 font-medium">Valeur</th>
          <th className="py-2 pr-3 font-medium">Unité</th>
        </tr>
      </thead>
      <tbody>
        {aggregates.map((a) => {
          const suffix = distinguishingSuffix(a, byMetric.get(a.metric_code) || []);
          const sourceCount = a.inputs?.length ?? 1;
          return (
            <tr
              key={a.measurement_id}
              className={`border-b border-border/60 ${onSelect ? "cursor-pointer hover:bg-background" : ""}`}
              onClick={() => onSelect?.(a)}
            >
              <td className="py-2 pr-3 font-medium" title={`Code interne : ${a.metric_code}`}>
                {metricLabel(a.metric_code)}
                {suffix && <span className="ml-1 font-normal text-muted">({suffix})</span>}
              </td>
              <td className="py-2 pr-3">
                {a.value === null || a.value === undefined
                  ? "inconnu"
                  : `${a.value_qualifier === "approx" ? "≈ " : ""}${a.value.toLocaleString("fr-FR")}`}
                {sourceCount > 1 && (
                  <span className="ml-1.5 text-xs text-muted">· {sourceCount} projets combinés</span>
                )}
              </td>
              <td className="py-2 pr-3 text-muted">{a.unit?.code || "—"}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
