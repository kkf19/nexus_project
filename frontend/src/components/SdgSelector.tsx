import { SDG_GOALS, SDG_LABELS } from "@/lib/sdgs";
import type { ConfirmSdgInput } from "@/lib/types";

// ODD (D-27) : de 1 à n, SANS PLAFOND, exactement 1 principal, une phrase de
// justification obligatoire pour CHAQUE ODD retenu (le garde-fou n'est plus
// un nombre maximum mais l'obligation de justifier -- un ODD non justifié
// n'est pas proposé par l'IA, et ne peut pas être confirmé vide).
export default function SdgSelector({
  value,
  onChange,
}: {
  value: ConfirmSdgInput[];
  onChange: (sdgs: ConfirmSdgInput[]) => void;
}) {
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

  return (
    <div className="space-y-1">
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
  );
}
