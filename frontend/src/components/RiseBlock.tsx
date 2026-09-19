import type { ConfirmRiseInput, TaxonomyValue } from "@/lib/types";
import OriginBadge from "./OriginBadge";

// RISE (D-24) : visible SEULEMENT si Community Impact (CI) figure parmi les
// Areas retenues. yes/no obligatoire dans ce cas ; au moins un pilier si
// "yes" (AC-25). Décocher CI ailleurs sur la page doit ramener ce bloc à
// not_applicable -- géré par l'appelant (page de confirmation).
export default function RiseBlock({
  pillarOptions,
  value,
  onChange,
}: {
  pillarOptions: TaxonomyValue[];
  value: ConfirmRiseInput;
  onChange: (rise: ConfirmRiseInput) => void;
}) {
  function setStatus(status: "yes" | "no") {
    onChange({ status, pillars: status === "yes" ? value.pillars : [] });
  }

  function togglePillar(code: string) {
    const has = value.pillars.includes(code);
    onChange({ ...value, pillars: has ? value.pillars.filter((c) => c !== code) : [...value.pillars, code] });
  }

  return (
    <section className="rounded-lg border border-border bg-surface p-4">
      <div className="flex items-center gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">RISE</h2>
        <OriginBadge origin="inferred" />
      </div>
      <p className="mt-1 text-xs text-muted">
        JCI RISE (Rebuild, Invest, Sustain, Evolve) — sous-classification de Community Impact.
      </p>
      <div className="mt-3 flex items-center gap-4 text-sm">
        <label className="flex items-center gap-2">
          <input type="radio" name="rise-status" checked={value.status === "yes"} onChange={() => setStatus("yes")} />
          Oui, ce projet relève de RISE
        </label>
        <label className="flex items-center gap-2">
          <input type="radio" name="rise-status" checked={value.status === "no"} onChange={() => setStatus("no")} />
          Non
        </label>
      </div>
      {value.status === "yes" && (
        <div className="mt-3">
          <div className="flex flex-wrap gap-2">
            {pillarOptions.map((opt) => {
              const active = value.pillars.includes(opt.code);
              return (
                <button
                  key={opt.code}
                  type="button"
                  onClick={() => togglePillar(opt.code)}
                  className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                    active
                      ? "border-accent bg-accent text-accent-foreground"
                      : "border-border bg-background text-foreground hover:border-accent/50"
                  }`}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
          {value.pillars.length === 0 && (
            <p className="mt-2 text-xs text-danger">Au moins un pilier est requis quand RISE = oui.</p>
          )}
        </div>
      )}
    </section>
  );
}
