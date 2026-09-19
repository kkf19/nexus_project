import type { TaxonomyValue } from "@/lib/types";

export default function ChipMultiSelect({
  options,
  selected,
  onChange,
}: {
  options: TaxonomyValue[];
  selected: string[];
  onChange: (codes: string[]) => void;
}) {
  function toggle(code: string) {
    if (selected.includes(code)) {
      onChange(selected.filter((c) => c !== code));
    } else {
      onChange([...selected, code]);
    }
  }
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => {
        const active = selected.includes(opt.code);
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
  );
}
