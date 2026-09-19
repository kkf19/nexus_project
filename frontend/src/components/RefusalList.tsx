import type { Refusal } from "@/lib/types";

// Règle non négociable du projet : un refus d'agrégation est stocké et
// affiché, jamais masqué ou replié par défaut (dev-brief §3.3, garde-fou
// produit). Ce composant n'a donc volontairement AUCUN état "replié" —
// toujours entièrement visible, sans bouton pour le cacher.
export default function RefusalList({ refusals }: { refusals: Refusal[] }) {
  if (!refusals || refusals.length === 0) {
    return (
      <p className="text-sm text-muted">Aucun refus d&apos;agrégation sur ce calcul.</p>
    );
  }
  return (
    <div className="space-y-2">
      {refusals.map((r, i) => (
        <div
          key={r.refusal_id || i}
          className="rounded-md border border-danger/40 bg-danger-bg px-3 py-2 text-sm text-danger"
        >
          <div className="font-medium">{r.explanation_fr || r.reason}</div>
          {r.measurement_ids?.length > 0 && (
            <div className="mt-1 text-xs opacity-80">
              Mesures concernées : {r.measurement_ids.join(", ")}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
