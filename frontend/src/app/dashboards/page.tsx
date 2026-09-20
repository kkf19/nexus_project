"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import { friendlyErrorMessage, getDashboardOverview, getTrace } from "@/lib/api";
import { DEMO_ORGANIZATIONS } from "@/lib/config";
import { BUCKET_LABEL, BUCKET_STYLE, classifyIaooi, sumDirectPeople, type DisplayBucket } from "@/lib/classify";
import { SDG_LABELS } from "@/lib/sdgs";
import AggregateTable from "@/components/AggregateTable";
import TracePanel from "@/components/TracePanel";
import type {
  Aggregate,
  AreaBlock,
  DashboardOverviewResponse,
  SdgBlock,
  TraceResponse,
} from "@/lib/types";

type View = "ol" | "national" | "global";
type Screen = "overview" | "areas" | "sdgs";

const VIEWS: { key: View; label: string }[] = [
  { key: "ol", label: "Mon OL" },
  { key: "national", label: "Nationale" },
  { key: "global", label: "Mondiale" },
];

// Decision (2026-09-20, remplace le detour du meme jour vers un onglet dedie
// -- voir historique git) : cette page est une surface de LECTURE D'IMPACT
// pour un public externe (President JCI, board national/mondial, eventuel
// investisseur), jamais un outil de diagnostic interne. Regle : tout ce qui
// n'aide pas directement a lire l'impact (refus d'agregation, codes bruts,
// conflits documentaires) est retire de cet affichage. Ces signaux restent
// calcules par le moteur (backend/engine/aggregation_engine.py, jamais
// modifie) et exposes par l'API pour l'equipe et les tests -- ils ne sont
// simplement plus render ici. Voir aussi la suppression du bloc "26
// conflits" du meme jour, meme logique.
const SCREENS: { key: Screen; label: string }[] = [
  { key: "overview", label: "Vue d'ensemble" },
  { key: "areas", label: "Par domaine (Area)" },
  { key: "sdgs", label: "Par ODD" },
];

const BUCKET_ORDER: DisplayBucket[] = ["resource", "activity", "impact", "reach", "other"];

function metricValue(aggregates: Aggregate[], metricCode: string): Aggregate | undefined {
  return aggregates.find((a) => a.metric_code === metricCode);
}

function fmt(value: number | null | undefined): string {
  if (value === null || value === undefined) return "inconnu";
  return value.toLocaleString("fr-FR");
}

export default function DashboardsPage() {
  const [view, setView] = useState<View>("ol");
  const [screen, setScreen] = useState<Screen>("overview");
  const [reportingYear, setReportingYear] = useState<string>("");
  // Simulation multi-pays pour la démo (voir lib/config.ts) : quelle OL
  // fictive regarder sur "Mon OL", quel pays sur "Nationale". Sans effet sur
  // la vue "Mondiale", qui reste sans restriction (scope_organization_id
  // undefined -- tous les pays confondus).
  const [selectedOrgId, setSelectedOrgId] = useState(DEMO_ORGANIZATIONS[0].id);
  const selectedOrg = DEMO_ORGANIZATIONS.find((o) => o.id === selectedOrgId) || DEMO_ORGANIZATIONS[0];
  const scopeOrganizationId =
    view === "global" ? undefined : view === "national" ? selectedOrg.nationalId : selectedOrg.id;

  const [data, setData] = useState<DashboardOverviewResponse | null>(null);
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
      setOpenTraceId(null);
      try {
        const res = await getDashboardOverview(view, {
          scope_organization_id: scopeOrganizationId,
          reporting_year: reportingYear ? Number(reportingYear) : undefined,
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
  }, [view, reportingYear, scopeOrganizationId]);

  const overviewBuckets = useMemo(() => {
    const grouped: Record<DisplayBucket, Aggregate[]> = {
      resource: [], activity: [], impact: [], reach: [], other: [],
    };
    data?.overview.aggregates.forEach((a) => {
      grouped[classifyIaooi(a.iaooi_class?.value, a.metric_code)].push(a);
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
          Un seul moteur de calcul, trois écrans. Une valeur inconnue s&apos;affiche « inconnu » — aucune
          cible ni jauge de progression.
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border">
        <div className="flex gap-2">
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
        {view !== "global" && (
          <label className="mb-2 flex items-center gap-2 text-xs text-muted">
            {view === "national" ? "Pays (démo)" : "OL (démo)"}
            <select
              value={selectedOrgId}
              onChange={(e) => setSelectedOrgId(e.target.value)}
              className="rounded-md border border-border bg-surface px-2 py-1 text-sm text-foreground"
            >
              {DEMO_ORGANIZATIONS.map((org) => (
                <option key={org.id} value={org.id}>
                  {view === "national" ? org.nationalLabel : org.label}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex gap-2">
          {SCREENS.map((s) => (
            <button
              key={s.key}
              onClick={() => setScreen(s.key)}
              className={`rounded-full border px-3 py-1.5 text-sm font-medium transition-colors ${
                screen === s.key
                  ? "border-accent bg-accent text-accent-foreground"
                  : "border-border bg-surface text-foreground hover:border-accent/50"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
        <input
          type="number"
          placeholder="Année"
          value={reportingYear}
          onChange={(e) => setReportingYear(e.target.value)}
          className="w-28 rounded-md border border-border bg-surface px-2 py-1.5 text-sm"
        />
      </div>

      {loading && <p className="text-sm text-muted">Calcul en cours…</p>}
      {error && <p className="text-sm text-danger">{error}</p>}

      {data && !loading && screen === "overview" && (
        <OverviewScreen
          data={data}
          buckets={overviewBuckets}
          openTraceId={openTraceId}
          trace={trace}
          traceLoading={traceLoading}
          onSelect={handleSelect}
        />
      )}

      {data && !loading && screen === "areas" && <AreasScreen areas={data.areas} />}

      {data && !loading && screen === "sdgs" && <SdgsScreen sdgs={data.sdgs} />}
    </div>
  );
}

function StatCard({ label, value, sub }: { label: string; value: string; sub?: ReactNode }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <div className="text-xs uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
      {sub && <div className="mt-1 text-xs text-muted">{sub}</div>}
    </div>
  );
}

function OverviewScreen({
  data,
  buckets,
  openTraceId,
  trace,
  traceLoading,
  onSelect,
}: {
  data: DashboardOverviewResponse;
  buckets: Record<DisplayBucket, Aggregate[]>;
  openTraceId: string | null;
  trace: TraceResponse | null;
  traceLoading: boolean;
  onSelect: (a: Aggregate) => void;
}) {
  const ov = data.overview;
  const external = sumDirectPeople(ov.aggregates, "external");
  const internal = sumDirectPeople(ov.aggregates, "internal");
  const hours = metricValue(ov.aggregates, "VOLUNTEER_HOURS");

  return (
    <>
      {/* Deux lectures jamais mélangées (impact-science.md §7) : "ce que JCI a
          fait" (Projets, ressources) d'un côté, "ce qui a changé" (Impact,
          bloc visuellement distinct, D-22) de l'autre. */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        <StatCard label="Projets" value={fmt(ov.total_projects)} sub="projets uniques" />
        <StatCard
          label="Personnes touchées — public externe"
          value={external.count === 0 ? "inconnu" : fmt(external.value)}
          sub="jamais l'audience, jamais l'indirect"
        />
        <StatCard
          label="Membres JCI mobilisés / formés"
          value={internal.count === 0 ? "inconnu" : fmt(internal.value)}
          sub="jamais additionné au public externe (R7)"
        />
        <StatCard label="Heures de bénévolat" value={hours ? fmt(hours.value) : "inconnu"} sub="somme, projets uniques" />
        <StatCard label="Projets avec résultat mesuré" value={fmt(ov.projects_measured)} />
        <StatCard
          label="Projets RISE"
          value={fmt(ov.rise_projects)}
          sub={
            // AC-31 : deux ratios, deux bases differentes, jamais confondues
            // (c'est precisement l'ecart 53,47% RISE vs 44,64% CI du rapport
            // JCI 2025, §1 du document de reference -- deux bases, pas une
            // incoherence).
            <>
              {ov.rise_pct_of_ci !== null
                ? `${ov.rise_pct_of_ci}% des projets Community Impact (base CI)`
                : "aucun projet Community Impact"}
              <br />
              {ov.rise_pct_of_all !== null
                ? `${ov.rise_pct_of_all}% de tous les projets (base tous projets)`
                : null}
            </>
          }
        />
        <StatCard label="Pays actifs" value={fmt(ov.countries_active)} />
        <StatCard label="OL actives" value={fmt(ov.ols_active)} />
      </div>

      <div className="space-y-4">
        {BUCKET_ORDER.filter((b) => buckets[b].length > 0).map((bucket) => (
          <section key={bucket} className={`rounded-lg border p-4 ${BUCKET_STYLE[bucket]}`}>
            <h2 className="text-sm font-semibold uppercase tracking-wide">{BUCKET_LABEL[bucket]}</h2>
            <div className="mt-3">
              <AggregateTable aggregates={buckets[bucket]} onSelect={onSelect} />
            </div>
            {buckets[bucket].some((a) => a.measurement_id === openTraceId) && (
              <>
                {traceLoading && <p className="mt-2 text-xs text-muted">Chargement de la traçabilité…</p>}
                {!traceLoading && trace && <TracePanel trace={trace} />}
              </>
            )}
          </section>
        ))}
      </div>
    </>
  );
}

function AreasScreen({ areas }: { areas: AreaBlock[] }) {
  return (
    <div className="space-y-4">
      <p className="text-xs text-muted">
        Un projet qui touche plusieurs domaines apparaît dans chaque bloc concerné, avec la mention
        « domaine secondaire » — la somme des blocs ci-dessous n&apos;est jamais un total (voir « Vue
        d&apos;ensemble » pour le nombre de projets uniques).
      </p>
      {areas.map((area) => {
        const volunteers = metricValue(area.aggregates, "VOLUNTEERS");
        const hours = metricValue(area.aggregates, "VOLUNTEER_HOURS");
        const external = sumDirectPeople(area.aggregates, "external");
        const internal = sumDirectPeople(area.aggregates, "internal");
        return (
          <section key={area.code} className="rounded-lg border border-border bg-surface p-4">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h2 className="text-base font-semibold uppercase tracking-wide">{area.label}</h2>
              <span className="text-sm text-muted">
                {fmt(area.total_projects)} projets
                {area.secondary_only_count > 0 && ` (dont ${area.secondary_only_count} en domaine secondaire)`}
              </span>
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-3">
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-muted">Ce qui a été fait</h3>
                {area.families.length === 0 ? (
                  <p className="mt-2 text-sm text-muted">Aucune famille d&apos;activité déclarée.</p>
                ) : (
                  <ul className="mt-2 space-y-1 text-sm">
                    {area.families.map((f) => (
                      <li key={f.code} className="flex justify-between border-b border-border/60 py-0.5">
                        <span>{f.label}</span>
                        <span className="font-medium">{f.project_count}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="rounded-md border border-border bg-background p-3">
                <h3 className="text-xs font-semibold uppercase tracking-wide text-muted">Ressources</h3>
                <p className="mt-2 text-sm">
                  Bénévoles {volunteers ? fmt(volunteers.value) : "inconnu"} · Heures {hours ? fmt(hours.value) : "inconnu"}
                </p>
              </div>

              {/* Bloc Impact visuellement distinct des ressources et de la portée
                  (garde-fou D-22) : couleur et bordure différentes, jamais le
                  même bloc. */}
              <div className="rounded-md border border-success/50 bg-success-bg p-3">
                <h3 className="text-xs font-semibold uppercase tracking-wide">Impact</h3>
                <p className="mt-2 text-sm">
                  Membres formés {internal.count === 0 ? "inconnu" : fmt(internal.value)} · Public externe
                  formé {external.count === 0 ? "inconnu" : fmt(external.value)} · Résultat mesuré{" "}
                  {fmt(area.projects_measured)}
                </p>
              </div>
            </div>

            {area.code === "CI" && area.rise && (
              <div className="mt-4 rounded-md border border-border bg-background p-3">
                <h3 className="text-xs font-semibold uppercase tracking-wide text-muted">RISE</h3>
                <p className="mt-2 text-sm">
                  Oui : {area.rise.yes} · Non : {area.rise.no}
                </p>
                {area.rise.pillars.length > 0 && (
                  <ul className="mt-2 flex flex-wrap gap-2 text-xs">
                    {area.rise.pillars.map((p) => (
                      <li key={p.code} className="rounded-full border border-border bg-surface px-2 py-1">
                        {p.code} — {p.project_count}
                      </li>
                    ))}
                  </ul>
                )}
                {area.top_sdgs.length > 0 && (
                  <p className="mt-2 text-xs text-muted">
                    ODD les plus cités :{" "}
                    {area.top_sdgs.map((s) => s.goal).join(" · ")}
                  </p>
                )}
              </div>
            )}
          </section>
        );
      })}
    </div>
  );
}

function SdgsScreen({ sdgs }: { sdgs: SdgBlock[] }) {
  if (sdgs.length === 0) {
    return <p className="text-sm text-muted">Aucun projet classé sur un ODD pour ce filtre.</p>;
  }
  return (
    <section className="rounded-lg border border-border bg-surface p-4">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
            <th className="py-2 pr-3 font-medium">ODD</th>
            <th className="py-2 pr-3 font-medium">Principal</th>
            <th className="py-2 pr-3 font-medium">Secondaire</th>
            <th className="py-2 pr-3 font-medium">Personnes touchées (externe)</th>
            <th className="py-2 pr-3 font-medium">Résultat mesuré</th>
          </tr>
        </thead>
        <tbody>
          {sdgs.map((s) => {
            const external = sumDirectPeople(s.aggregates, "external");
            return (
              <tr key={s.goal} className="border-b border-border/60">
                <td className="py-2 pr-3 font-medium">
                  ODD {s.goal} — {SDG_LABELS[s.goal]}
                </td>
                <td className="py-2 pr-3">{s.primary_count}</td>
                <td className="py-2 pr-3">{s.secondary_count}</td>
                <td className="py-2 pr-3">{external.count === 0 ? "inconnu" : fmt(external.value)}</td>
                <td className="py-2 pr-3">{s.projects_measured}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="mt-3 text-xs text-muted">
        Principal et secondaire ne sont jamais additionnés en un seul chiffre (D-27).
      </p>
    </section>
  );
}
