"use client";

import { useState } from "react";
import type { ConfirmActivityFamilyInput, TaxonomyValue } from "@/lib/types";

function isOtherCode(code: string): boolean {
  return code.endsWith("_OTHER") || code === "OTHER";
}

// "Quoi" (D-25) : 1..n familles d'activité (former, débattre, planter,
// jumeler...). Toute famille "Autre" impose un libellé libre non vide
// (AC-27) -- la case Confirmer reste désactivée tant qu'il manque.
//
// Progressive disclosure (revue Product Owner 2026-09-20) : le référentiel
// compte 32 familles d'activité -- les afficher toutes en permanence est
// exactement le "mur d'options" que la revue signale ("le front-end montre
// encore trop le moteur"). Par défaut, on affiche seulement ce que NEXUS a
// déjà détecté (les chips sélectionnées) ; le picker complet des 32 options
// ne s'ouvre que sur demande ("Modifier"), ou automatiquement si la
// sélection actuelle est incomplète (rien coché, ou un "Autre" sans
// libellé) -- une correction requise ne doit jamais être cachée.
function isComplete(value: ConfirmActivityFamilyInput[]): boolean {
  return value.length > 0 && value.every((f) => !isOtherCode(f.code) || !!f.other_label?.trim());
}

export default function ActivityFamilySelector({
  options,
  value,
  onChange,
}: {
  options: TaxonomyValue[];
  value: ConfirmActivityFamilyInput[];
  onChange: (families: ConfirmActivityFamilyInput[]) => void;
}) {
  const [mode, setMode] = useState<"view" | "edit">(() => (isComplete(value) ? "view" : "edit"));

  function labelFor(code: string): string {
    return options.find((o) => o.code === code)?.label || code;
  }

  function isSelected(code: string) {
    return value.some((f) => f.code === code);
  }

  function toggle(code: string) {
    if (isSelected(code)) {
      onChange(value.filter((f) => f.code !== code));
    } else {
      onChange([...value, { code, other_label: isOtherCode(code) ? "" : null }]);
    }
  }

  function setOtherLabel(code: string, label: string) {
    onChange(value.map((f) => (f.code === code ? { ...f, other_label: label } : f)));
  }

  if (mode === "view") {
    return (
      <div className="flex flex-wrap items-center gap-2">
        {value.map((f) => (
          <span
            key={f.code}
            className="rounded-full border border-accent bg-accent px-3 py-1 text-sm text-accent-foreground"
          >
            {labelFor(f.code)}
            {isOtherCode(f.code) && f.other_label ? ` — ${f.other_label}` : ""}
          </span>
        ))}
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
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => {
          const active = isSelected(opt.code);
          return (
            <button
              key={opt.code}
              type="button"
              onClick={() => toggle(opt.code)}
              className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                active
                  ? "border-accent bg-accent text-accent-foreground"
                  : "border-border bg-surface text-foreground hover:border-accent/50"
              }`}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
      {value.filter((f) => isOtherCode(f.code)).map((f) => (
        <div key={f.code} className="flex items-center gap-2">
          <span className="text-xs text-muted whitespace-nowrap">Libellé pour « {f.code} »</span>
          <input
            value={f.other_label ?? ""}
            onChange={(e) => setOtherLabel(f.code, e.target.value)}
            placeholder="Décrivez cette activité en quelques mots"
            className="w-full max-w-sm rounded-md border border-border bg-surface px-2 py-1 text-sm"
          />
          {!f.other_label?.trim() && <span className="text-xs text-danger whitespace-nowrap">obligatoire</span>}
        </div>
      ))}
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
