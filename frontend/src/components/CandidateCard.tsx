import type { CandidateMapping, ConfirmCandidateInput, ExtractionCandidate } from "@/lib/types";
import QuoteHighlight from "./QuoteHighlight";
import OriginBadge from "./OriginBadge";
import { metricLabel } from "@/lib/metricLabels";

const COUNT_TYPES = [
  { value: "direct", label: "direct" },
  { value: "indirect", label: "indirect" },
  { value: "audience", label: "audience" },
  { value: "cumulative", label: "cumulatif" },
  { value: "unknown", label: "inconnu" },
];

// D-26 : la population "pour qui" peut être 100% membres JCI, 100% public
// externe, ou "mixte" -- dans ce dernier cas AC-30 impose deux chiffres
// distincts (jamais un seul chiffre additionné, R7).
const INTERNAL_EXTERNAL = [
  { value: "internal", label: "membres JCI" },
  { value: "external", label: "public externe" },
  { value: "mixed", label: "mixte (JCI + externe)" },
  { value: "unknown", label: "inconnu" },
];

export default function CandidateCard({
  extraction,
  mapping,
  rawText,
  override,
  onChange,
  errorMessage,
  accent = "border-border bg-surface",
}: {
  extraction: ExtractionCandidate;
  mapping: CandidateMapping;
  rawText: string;
  override: ConfirmCandidateInput;
  onChange: (next: ConfirmCandidateInput) => void;
  errorMessage?: string;
  accent?: string;
}) {
  const value = override.value ?? extraction.value;
  const countType = override.count_type ?? mapping.count_type;
  const internalExternal = override.internal_external ?? mapping.internal_external;
  const isMixed = internalExternal === "mixed";

  function markCorrected(patch: Partial<ConfirmCandidateInput>) {
    onChange({ ...override, ...patch, corrected: true });
  }

  function changeInternalExternal(next: string) {
    // En quittant "mixed" on efface les deux valeurs partielles pour ne pas
    // laisser une ancienne saisie invisible resurgir si l'on revient à mixte.
    if (next === "mixed") {
      markCorrected({ internal_external: next });
    } else {
      markCorrected({ internal_external: next, value_internal: null, value_external: null });
    }
  }

  return (
    <div className={`rounded-lg border p-4 ${accent} ${!override.include ? "opacity-60" : ""}`}>
      <div className="flex items-start justify-between gap-3">
        <label className="flex items-center gap-2 text-sm font-medium">
          <input
            type="checkbox"
            checked={override.include}
            onChange={(e) => onChange({ ...override, include: e.target.checked })}
          />
          {mapping.source_wording_class || extraction.metric_label_source}
        </label>
        <span
          className="rounded-full bg-border/60 px-2 py-0.5 text-xs text-muted whitespace-nowrap"
          title={mapping.metric_code ? `Code interne : ${mapping.metric_code}` : undefined}
        >
          {metricLabel(mapping.metric_code)}
        </span>
      </div>

      {errorMessage && (
        <p className="mt-2 rounded-md bg-danger-bg px-2 py-1 text-xs text-danger">{errorMessage}</p>
      )}

      <div className="mt-3 rounded-md border border-border/60 bg-background/60 p-2">
        <QuoteHighlight text={rawText} span={extraction.span} />
      </div>

      <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {!isMixed && (
          <div>
            <div className="mb-1 flex items-center gap-1">
              <span className="text-xs text-muted">Valeur</span>
              <OriginBadge origin={value === null ? "to_fill" : "written"} />
            </div>
            <input
              type="number"
              value={value ?? ""}
              onChange={(e) =>
                markCorrected({ value: e.target.value === "" ? null : Number(e.target.value) })
              }
              className="w-full rounded-md border border-border bg-surface px-2 py-1 text-sm"
            />
          </div>
        )}
        {isMixed && (
          <>
            <div>
              <div className="mb-1 flex items-center gap-1">
                <span className="text-xs text-muted">Membres JCI</span>
                <OriginBadge origin={override.value_internal == null ? "to_fill" : "written"} />
              </div>
              <input
                type="number"
                value={override.value_internal ?? ""}
                onChange={(e) =>
                  markCorrected({ value_internal: e.target.value === "" ? null : Number(e.target.value) })
                }
                className="w-full rounded-md border border-border bg-surface px-2 py-1 text-sm"
              />
            </div>
            <div>
              <div className="mb-1 flex items-center gap-1">
                <span className="text-xs text-muted">Public externe</span>
                <OriginBadge origin={override.value_external == null ? "to_fill" : "written"} />
              </div>
              <input
                type="number"
                value={override.value_external ?? ""}
                onChange={(e) =>
                  markCorrected({ value_external: e.target.value === "" ? null : Number(e.target.value) })
                }
                className="w-full rounded-md border border-border bg-surface px-2 py-1 text-sm"
              />
            </div>
          </>
        )}
        <div>
          <div className="mb-1 flex items-center gap-1">
            <span className="text-xs text-muted">Unité</span>
            <OriginBadge origin="inferred" />
          </div>
          <div className="rounded-md border border-border bg-background px-2 py-1 text-sm text-muted">
            {mapping.unit_code}
          </div>
        </div>
        <div>
          <div className="mb-1 flex items-center gap-1">
            <span className="text-xs text-muted">Type de comptage</span>
            <OriginBadge origin="inferred" />
          </div>
          <select
            value={countType}
            onChange={(e) => markCorrected({ count_type: e.target.value })}
            className="w-full rounded-md border border-border bg-surface px-2 py-1 text-sm"
          >
            {COUNT_TYPES.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <div className="mb-1 flex items-center gap-1">
            <span className="text-xs text-muted">Pour qui</span>
            <OriginBadge origin="inferred" />
          </div>
          <select
            value={internalExternal}
            onChange={(e) => changeInternalExternal(e.target.value)}
            className="w-full rounded-md border border-border bg-surface px-2 py-1 text-sm"
          >
            {INTERNAL_EXTERNAL.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isMixed && (
        <p className="mt-2 text-xs text-muted">
          Public mixte : les deux nombres sont enregistrés séparément et ne sont jamais additionnés (R7).
        </p>
      )}

      {extraction.definition_text && (
        <p className="mt-2 text-xs text-muted">Définition : {extraction.definition_text}</p>
      )}
    </div>
  );
}
