"use client";

import { useState } from "react";
import { SDG_GOALS, SDG_LABELS } from "@/lib/sdgs";
import type { ConfirmSdgInput } from "@/lib/types";

// ODD (D-27) : de 1 à n, SANS PLAFOND, exactement 1 principal, une phrase de
// justification obligatoire pour CHAQUE ODD retenu (le garde-fou n'est plus
// un nombre maximum mais l'obligation de justifier -- un ODD non justifié
// n'est pas proposé par l'IA, et ne peut pas être confirmé vide).
//
// Progressive disclosure (revue Product Owner 2026-09-20) : les 17 ODD
// affichés en permanence, chacun avec sa propre case de justification, sont
// exactement le genre de "mur d'options" que la revue demande de retirer de
// l'écran par défaut. Par défaut, on affiche seulement les ODD que NEXUS a
// déjà proposés (chips, avec le principal marqué et la justification en
// infobulle) ; la liste complète des 17 ne s'ouvre que sur demande
// ("Modifier"), ou automatiquement si la sélection est incomplète (aucun
// ODD, plus d'un principal, ou une justification manquante).
function isComplete(value: ConfirmSdgInput[]): boolean {
  return (
    value.length > 0 &&
    value.filter((s) => s.role === "primary").length === 1 &&
    value.every((s) => s.justification.trim() !== "")
  );
}

export default function SdgSelector({
  value,
  onChange,
}: {
  value: ConfirmSdgInput[];
  onChange: (sdgs: ConfirmSdgInput[]) => void;
}) {
  const [mode, setMode] = useState<"view" | "edit">(() => (isComplete(value) ? "view" : "edit"));

  function isSelected(goal: number) {
    return value.some((s) => s.goal === goal);
  }
  function isPrimary(goal: number) {
    return value.some((s) => s.goal === goal && s.role === "primary");
  }
  function justificationOf(goal: number) {
    return value.find((s) => s.goal === goal)?.justification ?? "";
  }

  function toggle(goal: number) {
    if (isSelected(goal)) {
      onChange(value.filter((s) => s.goal !== goal));
    } else {
      const hasPrimary = value.some((s) => s.role === "primary");
      onChange([...value, { goal, role: hasPrimary ? "secondary" : "primary", justification: "" }]);
    }
  }

  function makePrimary(goal: number) {
    onChange(value.map((s) => ({ ...s, role: s.goal === goal ? "primary" : "secondary" })));
  }

  function setJustification(goal: number, justification: string) {
    onChange(value.map((s) => (s.goal === goal ? { ...s, justification } : s)));
  }

  if (mode === "view") {
    return (
      <div className="space-y-2">
        <div className="flex flex-wrap gap-2">
          {value
            .slice()
            .sort((a, b) => (a.role === "primary" ? -1 : b.role === "primary" ? 1 : a.goal - b.goal))
            .map((s) => (
              <span
                key={s.goal}
                title={s.justification}
                className="rounded-full border border-accent/40 bg-info-bg px-3 py-1 text-xs"
              >
                ODD {s.goal} — {SDG_LABELS[s.goal]}
                {s.role === "primary" ? " · principal" : ""}
              </span>
            ))}
        </div>
        <button
          type="button"
          onClick={() => setMode("edit")}
          className="text-xs font-medium text-accent underline underline-offset-2 hover:no-underline"
        >
          Modifier
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="max-h-96 space-y-1 overflow-y-auto pr-1">
        {SDG_GOALS.map((goal) => {
          const selected = isSelected(goal);
          return (
            <div
              key={goal}
              className={`rounded-md border px-3 py-1.5 text-sm ${
                selected ? "border-accent/40 bg-info-bg" : "border-border bg-surface"
              }`}
            >
              <div className="flex items-center justify-between">
                <label className="flex flex-1 items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={selected} onChange={() => toggle(goal)} />
                  <span>
                    ODD {goal} — {SDG_LABELS[goal]}
                  </span>
                </label>
                {selected && (
                  <label className="flex items-center gap-1 text-xs text-muted whitespace-nowrap pl-2">
                    <input
                      type="radio"
                      name="sdg-primary"
                      checked={isPrimary(goal)}
                      onChange={() => makePrimary(goal)}
                    />
                    principal
                  </label>
                )}
              </div>
              {selected && (
                <div className="mt-1.5 pl-6">
                  <input
                    value={justificationOf(goal)}
                    onChange={(e) => setJustification(goal, e.target.value)}
                    placeholder="Justification tirée du texte (obligatoire)"
                    className={`w-full rounded-md border bg-surface px-2 py-1 text-xs ${
                      justificationOf(goal).trim() ? "border-border" : "border-danger/50"
                    }`}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
      <button
        type="button"
        onClick={() => setMode("view")}
        className="text-xs font-medium text-accent underline underline-offset-2 hover:no-underline"
      >
        Terminé
      </button>
    </div>
  );
}
