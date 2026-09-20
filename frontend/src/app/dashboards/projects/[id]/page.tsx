"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { friendlyErrorMessage, getProject, getTaxonomy, getTrace } from "@/lib/api";
import { BUCKET_LABEL, BUCKET_STYLE, classifyIaooi, type DisplayBucket } from "@/lib/classify";
import { metricLabel, risePillarLabel } from "@/lib/metricLabels";
import { SDG_LABELS } from "@/lib/sdgs";
import TracePanel from "@/components/TracePanel";
import type { MeasurementObject, ProjectDetail, TaxonomyContent, TraceResponse } from "@/lib/types";

// Niveau 4 du drill-down (revue Product Owner 2026-09-20, North Star :
// "Global metric -> country -> organization -> project -> source"). Cette
// page est la destination d'un clic "Voir les projets" depuis le tableau de
// bord (ProjectListDisclosure) : le détail d'UN projet, avec la preuve
// (texte source) accessible pour chaque mesure. Contrairement aux écrans du
// tableau de bord (D-34 : lecture d'impact seulement), on est ici sur un
// écran de PREUVE consulté volontairement -- montrer le détail complet est
// donc exactement ce que la personne est venue chercher, pas un excès de
// mécanique exposée.
const OUTCOME_LABELS: Record<string, string> = {
  measured: "Résultat mesuré",
  pending_follow_up: "Résultat attendu (suivi programmé)",
  none: "Pas de résultat mesuré pour l'instant",
};

const BUCKET_ORDER: DisplayBucket[] = ["impact", "activity", "resource", "reach", "other"];

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const projectId = params.id;

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [taxonomy, setTaxonomy] = useState<TaxonomyContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [openTraceId, setOpenTraceId] = useState<string | null>(null);
  const [trace, setTrace] = useState<TraceResponse | null>(null);
  const [traceLoading, setTraceLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [p, tax] = await Promise.all([getProject(projectId), getTaxonomy()]);
        if (!cancelled) {
          setProject(p);
          setTaxonomy(tax.content);
        }
      } catch (err) {
        if (!cancelled) setError(friendlyErrorMessage(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  const areaLabel = useMemo(() => {
    const values = taxonomy?.classification_axes.area_of_opportunity.values ?? [];
    const byCode = new Map(values.map((v) => [v.code, v.label]));
    return (code: string) => byCode.get(code) || code;
  }, [taxonomy]);

  const buckets = useMemo(() => {
    const grouped: Record<DisplayBucket, MeasurementObject[]> = {
      resource: [], activity: [], impact: [], reach: [], other: [],
    };
    project?.measurements.forEach((m) => {
      grouped[classifyIaooi(m.iaooi_class?.value, m.metric_code)].push(m);
    });
    return grouped;
  }, [project]);

  async function handleSelectMeasurement(measurementId: string) {
    if (openTraceId === measurementId) {
      setOpenTraceId(null);
      return;
    }
    setOpenTraceId(measurementId);
    setTraceLoading(true);
    try {
      const t = await getTrace(measurementId);
      setTrace(t);
    } catch {
      setTrace(null);
    } finally {
      setTraceLoading(false);
    }
  }

  if (loading) return <p className="text-sm text-muted">Chargement…</p>;

  if (error || !project) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-danger">{error || "Projet introuvable."}</p>
        <Link href="/dashboards" className="text-sm text-accent hover:underline">
          ← Retour aux tableaux de bord
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <Link href="/dashboards" className="text-xs text-muted hover:text-foreground">
          ← Retour aux tableaux de bord
        </Link>
        <h1 className="mt-1 text-xl font-semibold">{project.name || "(projet sans titre)"}</h1>
        <p className="mt-1 text-sm text-muted">
          {project.organization_name || project.organization_id}
          {project.country_iso2 ? ` (${project.country_iso2})` : ""} · {project.reporting_year}
        </p>
      </div>

      <section className="rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">Ce que NEXUS a compris</h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {project.axes.area_of_opportunity.map((code) => (
            <span key={code} className="rounded-full border border-border bg-background px-3 py-1 text-xs">
              {areaLabel(code)}
            </span>
          ))}
          {project.axes.rise_pillars.map((code) => (
            <span
              key={code}
              className="rounded-full border border-border bg-background px-3 py-1 text-xs"
              title={`Code interne : ${code}`}
            >
              RISE · {risePillarLabel(code)}
            </span>
          ))}
          {project.axes.sdgs.map((s) => (
            <span key={s.goal} className="rounded-full border border-border bg-background px-3 py-1 text-xs">
              ODD {s.goal} — {SDG_LABELS[s.goal]}
              {s.role === "primary" ? " · principal" : ""}
            </span>
          ))}
        </div>
        <p className="mt-3 text-sm">
          {OUTCOME_LABELS[project.outcome_status] || project.outcome_status}
          {project.expected_outcome && (
            <span className="text-muted"> — attendu : {project.expected_outcome}</span>
          )}
        </p>
      </section>

      {BUCKET_ORDER.map((bucket) => {
        const items = buckets[bucket];
        if (items.length === 0) return null;
        return (
          <section key={bucket} className={`rounded-lg border p-4 ${BUCKET_STYLE[bucket]}`}>
            <h2 className="text-sm font-semibold uppercase tracking-wide">{BUCKET_LABEL[bucket]}</h2>
            <div className="mt-3 space-y-2">
              {items.map((m) => (
                <div key={m.measurement_id} className="rounded-md border border-border/60 bg-surface p-2 text-sm">
                  <div className="flex items-center justify-between gap-2">
                    <span title={`Code interne : ${m.metric_code}`}>
                      {metricLabel(m.metric_code)} :{" "}
                      <span className="font-medium">
                        {m.value === null || m.value === undefined
                          ? "inconnu"
                          : `${m.value_qualifier === "approx" ? "≈ " : ""}${m.value.toLocaleString("fr-FR")}`}
                      </span>{" "}
                      {m.unit?.code}
                    </span>
                    <button
                      type="button"
                      onClick={() => handleSelectMeasurement(m.measurement_id)}
                      className="whitespace-nowrap text-xs font-medium text-accent underline underline-offset-2 hover:no-underline"
                    >
                      {openTraceId === m.measurement_id ? "Masquer la source" : "Voir la source"}
                    </button>
                  </div>
                  {openTraceId === m.measurement_id && (
                    <>
                      {traceLoading && <p className="mt-2 text-xs text-muted">Chargement…</p>}
                      {!traceLoading && trace && <TracePanel trace={trace} />}
                    </>
                  )}
                </div>
              ))}
            </div>
          </section>
        );
      })}

      {project.measurements.length === 0 && (
        <p className="text-sm text-muted">Aucune mesure enregistrée pour ce projet.</p>
      )}
    </div>
  );
}
