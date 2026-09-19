import type { ConfirmAreaInput, TaxonomyValue } from "@/lib/types";

// "Où" (D-26) : 1..n domaines d'intervention (Areas), EXACTEMENT un marqué
// "principal". Cocher/décocher change la liste ; le radio "principale" ne
// peut viser qu'une Area déjà cochée.
export default function AreaSelector({
  options,
  value,
  onChange,
}: {
  options: TaxonomyValue[];
  value: ConfirmAreaInput[];
  onChange: (areas: ConfirmAreaInput[]) => void;
}) {
  function isSelected(code: string) {
    return value.some((a) => a.code === code);
  }
  function isPrimary(code: string) {
    return value.some((a) => a.code === code && a.role === "primary");
  }

  function toggle(code: string) {
    if (isSelected(code)) {
      onChange(value.filter((a) => a.code !== code));
    } else {
      const hasPrimary = value.some((a) => a.role === "primary");
      onChange([...value, { code, role: hasPrimary ? "secondary" : "primary" }]);
    }
  }

  function makePrimary(code: string) {
    onChange(value.map((a) => ({ ...a, role: a.code === code ? "primary" : "secondary" })));
  }

  return (
    <div className="space-y-1">
      {options.map((opt) => {
        const selected = isSelected(opt.code);
        return (
          <div
            key={opt.code}
            className={`flex items-center justify-between rounded-md border px-3 py-1.5 text-sm ${
              selected ? "border-accent/40 bg-info-bg" : "border-border bg-surface"
            }`}
          >
            <label className="flex flex-1 items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={selected} onChange={() => toggle(opt.code)} />
              <span>{opt.label}</span>
            </label>
            {selected && (
              <label className="flex items-center gap-1 text-xs text-muted whitespace-nowrap pl-2">
                <input
                  type="radio"
                  name="area-primary"
                  checked={isPrimary(opt.code)}
                  onChange={() => makePrimary(opt.code)}
                />
                principale
              </label>
            )}
          </div>
        );
      })}
    </div>
  );
}
