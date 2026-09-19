import type { TraceEntry, TraceResponse } from "@/lib/types";
import QuoteHighlight from "./QuoteHighlight";

// Cliquer sur un agrégat descend vers ses MO d'entrée, puis vers le projet,
// puis vers l'OL, puis vers le texte brut, citation surlignée (dev-brief §3.3).
export default function TracePanel({ trace }: { trace: TraceResponse }) {
  return (
    <div className="mt-2 space-y-2 rounded-md border border-border bg-background p-3">
      {!trace.chain_complete && (
        <p className="rounded-md bg-danger-bg px-2 py-1 text-xs text-danger">
          Chaîne de traçabilité incomplète — au moins un maillon n&apos;a pas pu être vérifié.
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
      <div className="rounded-md border border-danger/40 bg-danger-bg px-3 py-2 text-xs text-danger">
        {entry.measurement_id} — {entry.note || "mesure introuvable"}
      </div>
    );
  }

  const m = entry.measurement;
  return (
    <div className="rounded-md border border-border bg-surface px-3 py-2 text-xs">
      <div className="flex items-center justify-between">
        <span className="font-medium">
          {entry.kind === "aggregate" ? "Agrégat" : "Mesure source"} — {m?.metric_code} = {m?.value ?? "inconnu"}{" "}
          {m?.unit?.code}
        </span>
        <span className="text-muted">{entry.measurement_id}</span>
      </div>
      {entry.kind === "aggregate" && entry.parent_measurement_ids && (
        <p className="mt-1 text-muted">
          Calculé à partir de : {entry.parent_measurement_ids.join(", ")}
        </p>
      )}
      {entry.submission && (
        <div className="mt-2 rounded-md border border-border/60 bg-background p-2">
          <QuoteHighlight text={entry.submission.raw_text} span={entry.submission.highlight_span} />
          <p className="mt-1 text-muted">
            {entry.ctl_raw_ok ? "Intégrité du texte source vérifiée (CTL-RAW)." : "Intégrité du texte source non vérifiée."}
          </p>
        </div>
      )}
      {entry.note && <p className="mt-1 text-danger">{entry.note}</p>}
    </div>
  );
}
