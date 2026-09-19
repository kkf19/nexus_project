"use client";

import { useEffect, useMemo, useState } from "react";
import { friendlyErrorMessage, getDashboard, getTaxonomy, getTrace } from "@/lib/api";
import { DEMO_ORGANIZATION_ID } from "@/lib/config";
import { BUCKET_LABEL, BUCKET_STYLE, classifyIaooi, type DisplayBucket } from "@/lib/classify";
import AggregateTable from "@/components/AggregateTable";
import RefusalList from "@/components/RefusalList";
import TracePanel from "@/components/TracePanel";
import type { Aggregate, DashboardResponse, TaxonomyContent, TraceResponse } from "@/lib/types";

type View = "ol" | "national" | "global";

const VIEWS: { key: View; label: string }[] = [
  { key: "ol", label: "Mon OL" },
  { key: "national", label: "Nationale" },
  { key: "global", label: "Mondiale" },
];

const BUCKET_ORDER: DisplayBucket[] = ["resource", "activity", "impact", "reach", "other"];

export default function DashboardsPage() {
  const [view, setView] = useState<View>("ol");
  const [taxonomy, setTaxonomy] = useState<TaxonomyContent | null>(null);
  const [reportingYear, setReportingYear] = useState<string>("");
  const [areaFilter, setAreaFilter] = useState("");
  const [programmeFilter, setProgrammeFilter] = useState("");
  const [sdgFilter, setSdgFilter] = useState("");

  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [openTraceId, setOpenTraceId] = useState<string | null>(null);
  const [trace, setTrace] = useState<TraceResponse | null>(null);
  const [traceLoading, setTraceLoading] = useState(false);

  useEffect(() => {
    getTaxonomy()
      .then((t) => setTaxonomy(t.content))
      .catch(() => {
        /* les filtres par axe restent vides si la taxonomie ne charge pas ; pas bloquant */
      });
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      setOpenTraceId(null);
      try {
        const res = await getDashboard(view, {
          scope_organization_id: view === "global" ? undefined : DEMO_ORGANIZATION_ID,
          group_by: view === "ol" ? "subject" : "network",
          reporting_year: reportingYear ? Number(reportingYear) : undefined,
          area_of_opportunity: areaFilter || undefined,
          programme: programmeFilter || undefined,
          sdg: sdgFilter ? Number(sdgFilter) : undefined,
        });
        if (!cancelled) setData(res);
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
  }, [view, reportingYear, areaFilter, programmeFilter, sdgFilter]);

  const buckets = useMemo(() => {
    const grouped: Record<DisplayBucket, Aggregate[]> = {
      resource: [],
      activity: [],
      impact: [],
      reach: [],
      other: [],
    };
    data?.aggregates.forEach((a) => {
      const bucket = classifyIaooi(a.iaooi_class?.value, a.metric_code);
      grouped[bucket].push(a);
    });
    return grouped;
  }, [data]);

  async function handleSelect(a: Aggregate) {
    if (openTraceId === a.measurement_id) {
      setOpenTraceId(null);
      return;
    }
    setOpenTraceId(a.measurement_id);
    setTraceLoading(true);
    try {
      const t = await getTrace(a.measurement_id);
      setTrace(t);
    } catch {
      setTrace(null);
    } finally {
      setTraceLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Tableaux de bord</h1>
        <p className="mt-1 text-sm text-muted">
          Un seul moteur de calcul, trois vues. Une valeur inconnue s&apos;affiche « inconnu » — aucune
          cible ni jauge de progression.
        </p>
      </div>

      <div className="flex gap-2 border-b border-border">
        {VIEWS.map((v) => (
          <button
            key={v.key}
            onClick={() => setView(v.key)}
            className={`border-b-2 px-3 py-2 text-sm font-medium ${
              view === v.key ? "border-accent text-accent" : "border-transparent text-muted"
            }`}
          >
            {v.label}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap gap-3">
        <input
          type="number"
          placeholder="Année"
          value={reportingYear}
          onChange={(e) => setReportingYear(e.target.value)}
          className="w-28 rounded-md border border-border bg-surface px-2 py-1.5 text-sm"
        />
        {taxonomy && (
          <>
            <select
              value={areaFilter}
              onChange={(e) => setAreaFilter(e.target.value)}
              className="rounded-md border border-border bg-surface px-2 py-1.5 text-sm"
            >
              <option value="">Tous les domaines</option>
              {taxonomy.classification_axes.area_of_opportunity.values.map((v) => (
                <option key={v.code} value={v.code}>
                  {v.label}
                </option>
              ))}
            </select>
            <select
              value={programmeFilter}
              onChange={(e) => setProgrammeFilter(e.target.value)}
              className="rounded-md border border-border bg-surface px-2 py-1.5 text-sm"
            >
              <option value="">Tous les programmes</option>
              {taxonomy.classification_axes.programme.values.map((v) => (
                <option key={v.code} value={v.code}>
                  {v.label}
                </option>
              ))}
            </select>
          </>
        )}
        <input
          type="number"
          min={1}
          max={17}
          placeholder="ODD n°"
          value={sdgFilter}
          onChange={(e) => setSdgFilter(e.target.value)}
          className="w-24 rounded-md border border-border bg-surface px-2 py-1.5 text-sm"
        />
      </div>

      {loading && <p className="text-sm text-muted">Calcul en cours…</p>}
      {error && <p className="text-sm text-danger">{error}</p>}

      {data && !loading && (
        <>
          {data.stale && (
            <p className="rounded-md border border-warning/40 bg-warning-bg px-3 py-2 text-sm text-warning">
              Le dernier calcul a échoué : cette vue affiche la dernière exécution réussie
              ({new Date(data.computed_at).toLocaleString("fr-FR")}).
            </p>
          )}

          {BUCKET_ORDER.filter((b) => buckets[b].length > 0).map((bucket) => (
            <section key={bucket} className={`rounded-lg border p-4 ${BUCKET_STYLE[bucket]}`}>
              <h2 className="text-sm font-semibold uppercase tracking-wide">{BUCKET_LABEL[bucket]}</h2>
              <div className="mt-3">
                <AggregateTable aggregates={buckets[bucket]} onSelect={handleSelect} />
              </div>
              {buckets[bucket].some((a) => a.measurement_id === openTraceId) && (
                <>
                  {traceLoading && <p className="mt-2 text-xs text-muted">Chargement de la traçabilité…</p>}
                  {!traceLoading && trace && <TracePanel trace={trace} />}
                </>
              )}
            </section>
          ))}

          <section className="rounded-lg border border-border bg-surface p-4">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">
              Refus d&apos;agrégation
            </h2>
            <p className="mt-1 text-xs text-muted">
              Toujours affichés, jamais masqués ni repliés.
            </p>
            <div className="mt-3">
              <RefusalList refusals={data.refusals} />
            </div>
          </section>

          {view === "global" && data.quality_issues && data.quality_issues.length > 0 && (
            <section className="rounded-lg border border-border bg-surface p-4">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">
                Chiffres publiés par JCI — incohérences connues
              </h2>
              <p className="mt-1 text-xs text-muted">
                Affichés à côté du calcul NEXUS, jamais à sa place. NEXUS n&apos;arbitre pas entre ces
                valeurs.
              </p>
              <div className="mt-3 space-y-3">
                {data.quality_issues.map((issue) => (
                  <div key={issue.issue_id} className="rounded-md border border-border bg-background p-3 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{issue.subject}</span>
                      <span className="rounded-full bg-warning-bg px-2 py-0.5 text-xs text-warning">
                        {issue.resolution_status}
                      </span>
                    </div>
                    <ul className="mt-2 space-y-1 text-xs text-muted">
                      {issue.values.map((v, i) => (
                        <li key={i}>
                          <span className="font-medium text-foreground">
                            {v.value_qualifier === "at_least" ? "≥ " : ""}
                            {v.value.toLocaleString("fr-FR")} {v.unit}
                          </span>{" "}
                          — {v.source?.document} ({v.source?.section}
                          {v.source?.page ? `, p.${v.source.page}` : ""})
                          {v.source?.quote && <span> — « {v.source.quote} »</span>}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
