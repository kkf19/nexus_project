import type { TaxonomyValue } from "./types";

/** Retrouve le libellé humain d'un code dans une liste de valeurs de
 * taxonomie {code, label, ...}. Jamais recopié en dur (dev-brief §2.1) :
 * on part toujours du contenu chargé depuis GET /taxonomy. */
export function labelFor(values: TaxonomyValue[] | undefined, code: string): string {
  const found = values?.find((v) => v.code === code);
  return found?.label || code;
}

export function labelsFor(values: TaxonomyValue[] | undefined, codes: string[]): string {
  return codes.map((c) => labelFor(values, c)).join(", ");
}
