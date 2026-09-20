import type { TraceEntry, TraceResponse } from "@/lib/types";
import QuoteHighlight from "./QuoteHighlight";
import { metricLabel, unitLabel } from "@/lib/metricLabels";

// Preuve de traçabilité (North Star : "Global metric -> country ->
// organization -> project -> source") : cliquer un résultat mesuré descend
// jusqu'au texte original soumis par l'organisation.
//
// Revue Product Owner (2026-09-20) : "l'utilisateur n'a pas besoin de voir
// la mécanique du moteur." Règle appliquée ici, plus stricte que le reste
// de l'écran car cet écran affichait jusqu'ici des identifiants techniques
// bruts (measurement_id) et des noms de règles internes en toutes lettres
// (CTL-RAW, CTL-TRACE, dev-brief.md) directement dans l'interface :
// - aucun identifiant de mesure n'est affiché (rien à décider dessus) ;
// - le texte de statut vient UNIQUEMENT des drapeaux structurés renvoyés
//   par l'API (resolved, ctl_raw_ok, présence ou non de `submission`) --
//   jamais de `entry.note`, qui est un texte libre écrit pour les
//   développeurs (il peut nommer une règle interne) et ne doit donc jamais
//   atterrir tel quel dans une interface destinée à un board ou un
//   président JCI. Sa seule utilisation ici est sa PRÉSENCE (booléenne),
//   pour distinguer un vrai fait officiel JCI (pas de soumission attendue)
//   d'une chaîne cassée (soumission attendue mais introuvable).
export default function TracePanel({ trace }: { trace: TraceResponse }) {
  return (
    <div className="mt-2 space-y-2 rounded-md border border-border bg-background p-3">
      {!trace.chain_complete && (
        <p className="rounded-md bg-warning-bg px-2 py-1 text-xs text-warning">
          Une partie de cette chaîne de preuve n&apos;a pas pu être vérifiée.
        </p>
      )}
      {trace.entries.map((entry, i) => (
        <TraceEntryCard key={`${entry.measurement_id}-${i}`} entry={entry} />
      ))}
    </div>
  );
}

function TraceEntryCard({ entry }: { entry: TraceEntry }) {
  if (!entry.resolved) {
    return (
      <div className="rounded-md border border-warning/40 bg-warning-bg px-3 py-2 text-xs text-warning">
        Une mesure de cette chaîne est introuvable.
      </div>
    );
  }

  const m = entry.measurement;
  const isCombined = entry.kind === "aggregate";
  const sourceCount = entry.parent_measurement_ids?.length ?? 0;

  return (
    <div className="rounded-md border border-border bg-surface px-3 py-2 text-xs">
      <span className="font-medium" title={m?.metric_code ? `Code interne : ${m.metric_code}` : undefined}>
        {metricLabel(m?.metric_code)} : {m?.value ?? "inconnu"} {unitLabel(m?.unit?.code)}
      </span>
      {isCombined && sourceCount > 0 && (
        <p className="mt-1 text-muted">
          Combine {sourceCount} mesure{sourceCount > 1 ? "s" : ""} source{sourceCount > 1 ? "s" : ""}.
        </p>
      )}
      {entry.submission && (
        <div className="mt-2 rounded-md border border-border/60 bg-background p-2">
          <QuoteHighlight text={entry.submission.raw_text} span={entry.submission.highlight_span} />
          <p className="mt-1 text-muted">
            {entry.ctl_raw_ok
              ? "Le texte source n'a pas été modifié depuis sa soumission."
              : "Le texte source n'a pas pu être vérifié."}
          </p>
        </div>
      )}
      {!entry.submission && !isCombined && (
        <p className="mt-1 text-muted">
          {entry.note
            ? "Le document source de cette mesure n'est plus disponible."
            : "Donnée officielle JCI — aucune soumission individuelle associée."}
        </p>
      )}
    </div>
  );
}
