import { SDG_GOALS, SDG_LABELS } from "@/lib/sdgs";
import type { ConfirmSdgInput } from "@/lib/types";

// C3 : ODD avec exactement 1 principal (le sur-étiquetage est le défaut
// documenté de la source, DQC-22).
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

  function toggle(goal: number) {
    if (isSelected(goal)) {
      onChange(value.filter((s) => s.goal !== goal));
    } else {
      const hasPrimary = value.some((s) => s.role === "primary");
      onChange([...value, { goal, role: hasPrimary ? "secondary" : "primary" }]);
    }
  }

  function makePrimary(goal: number) {
    onChange(value.map((s) => ({ ...s, role: s.goal === goal ? "primary" : "secondary" })));
  }

  return (
    <div className="space-y-1">
      {SDG_GOALS.map((goal) => {
        const selected = isSelected(goal);
        return (
          <div
            key={goal}
            className={`flex items-center justify-between rounded-md border px-3 py-1.5 text-sm ${
              selected ? "border-accent/40 bg-info-bg" : "border-border bg-surface"
            }`}
          >
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
        );
      })}
    </div>
  );
}
