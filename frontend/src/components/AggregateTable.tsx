import type { Aggregate } from "@/lib/types";
import { metricLabel } from "@/lib/metricLabels";

// Une valeur NULL s'affiche "inconnu". Aucune cible, objectif, jauge de
// progression ni pourcentage d'atteinte (D-09, garde-fou produit).
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
  return (
    <table className="w-full border-collapse text-sm">
      <thead>
        <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
          <th className="py-2 pr-3 font-medium">Indicateur</th>
          <th className="py-2 pr-3 font-medium">Valeur</th>
          <th className="py-2 pr-3 font-medium">Unité</th>
          <th className="py-2 pr-3 font-medium">Statut</th>
          <th className="py-2 pr-3 font-medium">Entrées</th>
        </tr>
      </thead>
      <tbody>
        {aggregates.map((a) => (
          <tr
            key={a.measurement_id}
            className={`border-b border-border/60 ${onSelect ? "cursor-pointer hover:bg-background" : ""}`}
            onClick={() => onSelect?.(a)}
          >
            <td className="py-2 pr-3 font-medium" title={`Code interne : ${a.metric_code}`}>
              {metricLabel(a.metric_code)}
            </td>
            <td className="py-2 pr-3">
              {a.value === null || a.value === undefined
                ? "inconnu"
                : `${a.value_qualifier === "approx" ? "≈ " : ""}${a.value.toLocaleString("fr-FR")}`}
            </td>
            <td className="py-2 pr-3 text-muted">{a.unit?.code || "—"}</td>
            <td className="py-2 pr-3">
              {a.value_status === "reported" && (
                <span className="rounded-full bg-warning-bg px-2 py-0.5 text-xs font-medium text-warning">
                  provisoire
                </span>
              )}
              {a.value_status === "calculated" && (
                <span className="rounded-full bg-info-bg px-2 py-0.5 text-xs font-medium text-info">
                  calculé
                </span>
              )}
              {a.value_status !== "reported" && a.value_status !== "calculated" && (
                <span className="text-xs text-muted">{a.value_status}</span>
              )}
            </td>
            <td className="py-2 pr-3 text-muted">{a.inputs?.length ?? 1}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
