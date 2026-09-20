"use client";

import { useState } from "react";
import Link from "next/link";
import { friendlyErrorMessage, listProjects } from "@/lib/api";
import type { ProjectListItem } from "@/lib/types";

// Niveau 3 du drill-down (revue Product Owner 2026-09-20, "le Board doit
// pouvoir descendre de la Area jusqu'au projet, puis jusqu'à la source") :
// un simple lien qui révèle, à la demande, les projets réels derrière un
// compte déjà affiché (Area, ODD). Chargement paresseux -- on ne demande la
// liste que si quelqu'un clique, jamais au chargement du tableau de bord.
export default function ProjectListDisclosure({
  label,
  view,
  scopeOrganizationId,
  areaOfOpportunity,
  sdg,
  reportingYear,
}: {
  label: string;
  view: "ol" | "national" | "global";
  scopeOrganizationId?: string;
  areaOfOpportunity?: string;
  sdg?: number;
  reportingYear?: number;
}) {
  const [open, setOpen] = useState(false);
  const [projects, setProjects] = useState<ProjectListItem[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function toggle() {
    if (open) {
      setOpen(false);
      return;
    }
    setOpen(true);
    if (projects !== null) return; // déjà chargé une fois
    setLoading(true);
    setError(null);
    try {
      const res = await listProjects({
        view,
        scope_organization_id: scopeOrganizationId,
        area_of_opportunity: areaOfOpportunity,
        sdg,
        reporting_year: reportingYear,
      });
      setProjects(res.projects);
    } catch (err) {
      setError(friendlyErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mt-2">
      {/* Bouton fantôme émeraude (brief étape 5, p. 5) : bordure et texte
          émeraude, jamais de remplissage plein -- ce n'est pas une action
          principale de l'écran, juste une porte vers le détail. */}
      <button
        type="button"
        onClick={toggle}
        className="inline-flex items-center gap-1 whitespace-nowrap rounded-full border border-accent/40 px-3 py-1 text-xs font-medium text-accent transition-colors hover:bg-accent/10"
      >
        {open ? "Masquer les projets" : label}
      </button>
      {open && (
        <div className="mt-2 rounded-md border border-border bg-background p-2">
          {loading && <p className="text-xs text-muted">Chargement…</p>}
          {error && <p className="text-xs text-danger">{error}</p>}
          {!loading && !error && projects && projects.length === 0 && (
            <p className="text-xs text-muted">Aucun projet pour ce filtre.</p>
          )}
          {!loading && !error && projects && projects.length > 0 && (
            <ul className="space-y-1.5 text-xs">
              {projects.map((p) => (
                <li key={p.project_id} className="flex items-baseline justify-between gap-2">
                  <Link href={`/dashboards/projects/${p.project_id}`} className="text-accent hover:underline">
                    {p.name}
                  </Link>
                  <span className="whitespace-nowrap text-muted">
                    {p.organization_name}
                    {p.reporting_year ? ` · ${p.reporting_year}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
