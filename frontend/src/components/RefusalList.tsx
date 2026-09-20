import type { Refusal } from "@/lib/types";

// Règle non négociable du projet : un refus d'agrégation est stocké et
// affiché, jamais masqué ou replié par défaut (dev-brief §3.3, garde-fou
// produit). Ce composant n'a donc volontairement AUCUN état "replié" —
// toujours entièrement visible, sans bouton pour le cacher.
//
// Correctif de présentation (2026-09-20) : `explanation_fr` est construit
// par Refusal.explain() dans backend/engine/aggregation_engine.py, un
// fichier réutilisé tel quel (jamais réécrit, cf. Étape 0) sous la forme
// "CODE_BRUT — explication en français" (ex. "MISSING_DEFINITION —
// définitions incompatibles ou absentes"). Montrer ce préfixe brut à un
// public non technique (jury, board) donne l'impression d'un message
// d'erreur système, alors que le principe produit ("le système doit savoir
// dire non", jamais caché) ne dit rien sur le FORMAT du texte. On retire
// donc ici le préfixe machine, sans toucher au moteur ni à la donnée
// stockée : le code brut reste consultable (attribut title + ligne
// technique repliée visuellement, jamais supprimée).
function humanExplanation(r: Refusal): string {
  const text = r.explanation_fr || r.reason;
  const prefix = `${r.reason} — `;
  return text.startsWith(prefix) ? text.slice(prefix.length) : text;
}

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
          <div className="font-medium" title={`Code interne : ${r.reason}`}>
            {humanExplanation(r)}
          </div>
          {r.measurement_ids?.length > 0 && (
            <div className="mt-1 text-xs text-danger/70">
              Détail technique ({r.reason}) : {r.measurement_ids.join(", ")}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
