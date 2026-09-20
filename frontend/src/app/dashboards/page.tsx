"use client";

import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { friendlyErrorMessage, getDashboardOverview, getTrace } from "@/lib/api";
import { DEMO_ORGANIZATIONS } from "@/lib/config";
import { BUCKET_LABEL, BUCKET_STYLE, classifyIaooi, sumDirectPeople, type DisplayBucket } from "@/lib/classify";
import { SDG_LABELS } from "@/lib/sdgs";
import { domainColor } from "@/lib/domainColors";
import AggregateTable from "@/components/AggregateTable";
import ProjectListDisclosure from "@/components/ProjectListDisclosure";
import TracePanel from "@/components/TracePanel";
import { risePillarLabel } from "@/lib/metricLabels";
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
//
// Refonte visuelle 2026-09-20 (NEXUS_design_brief.pdf) : présentation
// uniquement -- aucune route, appel API, calcul ou schéma touché dans ce
// fichier. Seules la mise en forme de l'écran et deux mini-visualisations
// "Vue d'ensemble" (projets par domaine, personnes touchées par ODD) ont été
// ajoutées, entièrement rebranchées sur les agrégats déjà chargés par
// getDashboardOverview (data.areas / data.sdgs) -- aucune nouvelle donnée.
const SCREENS: { key: Screen; label: string }[] = [
  { key: "overview", label: "Vue d'ensemble" },
  { key: "areas", label: "Par domaine (Area)" },
  { key: "sdgs", label: "Par ODD" },
];

function metricValue(aggregates: Aggregate[], metricCode: string): Aggregate | undefined {
  return aggregates.find((a) => a.metric_code === metricCode);
}

function fmt(value: number | null | undefined): string {
  if (value === null || value === undefined) return "inconnu";
  return value.toLocaleString("fr-FR");
}

// Compteur animé (chiffre vedette + KPI) : anime UNIQUEMENT vers la valeur
// réelle déjà reçue de l'API -- jamais de fausse progression, jamais de
// pourcentage inventé (même règle que l'écran d'attente du brief). Respecte
// prefers-reduced-motion (saut direct à la valeur finale).
function useCountUp(target: number | null, durationMs = 900): number | null {
  const [display, setDisplay] = useState<number>(target ?? 0);
  const prevTarget = useRef<number | null>(null);

  useEffect(() => {
    if (target === null) return;
    const reduceMotion =
      typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const start = prevTarget.current ?? 0;
    if (reduceMotion || start === target) {
      setDisplay(target);
      prevTarget.current = target;
      return;
    }
    const startTime = performance.now();
    let raf = 0;
    function tick(now: number) {
      const progress = Math.min(1, (now - startTime) / durationMs);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(start + (target! - start) * eased));
      if (progress < 1) raf = requestAnimationFrame(tick);
    }
    raf = requestAnimationFrame(tick);
    prevTarget.current = target;
    return () => cancelAnimationFrame(raf);
  }, [target, durationMs]);

  return target === null ? null : display;
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
        <div className="nexus-label mb-1">NEXUS · Infrastructure d&apos;impact</div>
        <h1 className="text-3xl font-light tracking-tight text-foreground">Tableaux de bord</h1>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border">
        <div className="flex gap-6">
          {VIEWS.map((v) => (
            <button
              key={v.key}
              onClick={() => setView(v.key)}
              className={`relative px-0.5 py-2.5 text-sm transition-colors ${
                view === v.key ? "text-foreground" : "text-muted hover:text-foreground"
              }`}
            >
              {v.label}
              {view === v.key && <span className="absolute -bottom-px left-0 right-0 h-0.5 rounded-full bg-accent" />}
            </button>
          ))}
        </div>
        {view !== "global" && (
          <label className="mb-2 flex items-center gap-2 text-xs text-muted">
            {view === "national" ? "Pays (démo)" : "OL (démo)"}
            <select
              value={selectedOrgId}
              onChange={(e) => setSelectedOrgId(e.target.value)}
              className="rounded-lg border border-border bg-surface px-2.5 py-1.5 text-sm text-foreground outline-none transition-colors focus:border-accent/50"
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
              className={`rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors ${
                screen === s.key
                  ? "border-accent/40 bg-accent/10 text-accent"
                  : "border-border bg-surface text-muted hover:border-border-strong hover:text-foreground"
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
          className="w-28 rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-foreground outline-none transition-colors placeholder:text-muted-2 focus:border-accent/50"
        />
      </div>

      {error && <p className="text-sm text-danger">{error}</p>}

      {/* Premier chargement (aucune donnee precedente a montrer) : silhouette
          generique plutot qu'un texte ou un ecran vide. Un changement de vue
          ou d'annee APRES ce premier chargement garde au contraire l'ecran
          precedent affiche (voir .nexus-transition ci-dessous) -- correctif
          perf D-37 (2026-09-20) : ce rechargement prend ~10s au lieu de
          30-50s, mais on ne laisse plus jamais l'ecran paraitre vide ou
          fige pendant ce temps, et on ne nomme jamais "calcul"/"traitement"
          a l'ecran (regle d'or D-35 n3 : le moteur reste interne). */}
      {!data && loading && <OverviewSkeleton />}

      {data && (
        <div className={`nexus-transition${loading ? " nexus-transition-loading" : ""}`}>
          {screen === "overview" && (
            <OverviewScreen
              data={data}
              buckets={overviewBuckets}
              openTraceId={openTraceId}
              trace={trace}
              traceLoading={traceLoading}
              onSelect={handleSelect}
              onSeeByOdd={() => setScreen("sdgs")}
            />
          )}

          {screen === "areas" && (
            <AreasScreen
              areas={data.areas}
              view={view}
              scopeOrganizationId={scopeOrganizationId}
              reportingYear={reportingYear ? Number(reportingYear) : undefined}
            />
          )}

          {screen === "sdgs" && (
            <SdgsScreen
              sdgs={data.sdgs}
              view={view}
              scopeOrganizationId={scopeOrganizationId}
              reportingYear={reportingYear ? Number(reportingYear) : undefined}
            />
          )}
        </div>
      )}
    </div>
  );
}

// Silhouette du tout premier chargement (aucune donnee precedente a
// montrer) -- generique, pas un decalque exact de "Vue d'ensemble", puisque
// les 3 ecrans partagent le meme chargement de donnees et qu'on ne sait pas
// encore lequel l'utilisateur regardera. Volontairement discrete
// (animate-pulse natif Tailwind, aucune animation custom) ; jamais de texte
// "chargement"/"calcul" (D-38, meme principe que D-35 n3).
function OverviewSkeleton() {
  return (
    <div className="space-y-6" aria-hidden="true">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="animate-pulse rounded-lg border border-border bg-surface p-4">
            <div className="h-3 w-2/3 rounded bg-border/70" />
            <div className="mt-3 h-6 w-1/2 rounded bg-border/70" />
          </div>
        ))}
      </div>
      <div className="animate-pulse rounded-lg border border-border bg-surface p-4">
        <div className="h-3 w-1/4 rounded bg-border/70" />
        <div className="mt-4 space-y-2">
          <div className="h-4 w-full rounded bg-border/70" />
          <div className="h-4 w-5/6 rounded bg-border/70" />
          <div className="h-4 w-2/3 rounded bg-border/70" />
        </div>
      </div>
    </div>
  );
}

// Réseau de points reliés, motif de marque en basse opacité (brief p.2).
// Purement décoratif -- aria-hidden, jamais derrière du texte utile.
function NetworkDecoration({ className = "" }: { className?: string }) {
  return (
    <svg
      className={`nexus-network-bg ${className}`}
      viewBox="0 0 260 160"
      fill="none"
      aria-hidden="true"
      preserveAspectRatio="xMaxYMax slice"
    >
      <g stroke="var(--accent)" strokeOpacity="0.35" strokeWidth="1">
        <path d="M40 150 L90 100 L150 120 L210 60 L250 90" />
        <path d="M90 100 L120 40 L180 30 L210 60" />
        <path d="M150 120 L180 150" />
        <path d="M120 40 L60 20" />
      </g>
      <g fill="var(--accent)" fillOpacity="0.75">
        <circle cx="40" cy="150" r="2.4" />
        <circle cx="90" cy="100" r="2" />
        <circle cx="150" cy="120" r="2" />
        <circle cx="210" cy="60" r="3" />
        <circle cx="250" cy="90" r="2" />
        <circle cx="120" cy="40" r="2" />
        <circle cx="180" cy="30" r="2" />
        <circle cx="60" cy="20" r="2" />
        <circle cx="180" cy="150" r="2" />
      </g>
    </svg>
  );
}

function RuleChip({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border-strong bg-background/60 px-2.5 py-1 text-xs text-muted">
      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 8v5M12 16.5v.01" strokeLinecap="round" />
      </svg>
      {children}
    </span>
  );
}

function HeroStat({ value, note, isUnknown }: { value: number | null; note: string; isUnknown: boolean }) {
  const display = useCountUp(isUnknown ? null : value);
  return (
    <div className="relative overflow-hidden rounded-2xl border border-border bg-surface p-6 lg:row-span-2">
      <NetworkDecoration className="bottom-0 right-0 h-28 w-40" />
      <div className="relative">
        <div className="nexus-label">Personnes touchées — public externe</div>
        <div className="nexus-hero-figure mt-3 text-foreground">
          {isUnknown ? <span className="text-4xl italic text-muted-2">inconnu</span> : fmt(display)}
        </div>
        <div className="mt-5">
          <RuleChip>{note}</RuleChip>
        </div>
      </div>
    </div>
  );
}

function KpiCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-2xl border border-border bg-surface p-5 transition-colors hover:border-border-strong">
      <div className="nexus-label">{label}</div>
      <div className="nexus-figure mt-2 text-4xl text-foreground md:text-5xl">{value}</div>
      {sub && <div className="mt-1.5 text-xs text-muted">{sub}</div>}
    </div>
  );
}

function WideCard({ label, value, ruleNote, footNote }: { label: string; value: string; ruleNote: string; footNote?: string }) {
  return (
    <div className="rounded-2xl border border-border bg-surface p-5 lg:col-span-2">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="nexus-label">{label}</div>
        <RuleChip>{ruleNote}</RuleChip>
      </div>
      <div className="nexus-figure mt-2 text-4xl text-foreground md:text-5xl">{value}</div>
      {footNote && <div className="mt-1.5 text-xs text-muted">{footNote}</div>}
    </div>
  );
}

function RingStat({
  percent,
  color,
  size = 92,
  strokeWidth = 9,
}: {
  percent: number | null;
  color: string;
  size?: number;
  strokeWidth?: number;
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = percent ?? 0;
  const offset = circumference * (1 - Math.min(100, Math.max(0, pct)) / 100);
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="shrink-0">
      <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--border-strong)" strokeWidth={strokeWidth} />
      {percent !== null && (
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset 700ms ease" }}
        />
      )}
      <text
        x="50%"
        y="50%"
        dominantBaseline="middle"
        textAnchor="middle"
        fill="var(--foreground)"
        fontSize={size * 0.19}
        style={{ fontVariantNumeric: "tabular-nums" }}
      >
        {percent !== null ? `${percent}%` : "—"}
      </text>
    </svg>
  );
}

function RiseCard({ ov }: { ov: DashboardOverviewResponse["overview"] }) {
  // Base CI dérivée des deux nombres déjà renvoyés par l'API
  // (rise_projects et rise_pct_of_ci) -- pas une nouvelle donnée, juste
  // l'opération inverse du pourcentage déjà calculé côté moteur, affichée
  // pour donner le même contexte "base CI · N projets" que le brief.
  const ciBase = ov.rise_pct_of_ci ? Math.round((ov.rise_projects / ov.rise_pct_of_ci) * 100) : null;
  return (
    <div className="rounded-2xl border border-border bg-surface p-5 lg:col-span-2">
      <div className="flex flex-wrap items-center gap-6">
        <div>
          <div className="nexus-label">Projets RISE</div>
          <div className="nexus-figure mt-2 text-5xl text-foreground">{fmt(ov.rise_projects)}</div>
        </div>
        <div className="flex flex-1 flex-wrap items-center gap-6">
          <div className="flex items-center gap-3">
            <RingStat percent={ov.rise_pct_of_ci} color="var(--domain-community)" />
            <p className="max-w-[10rem] text-xs text-muted">
              {ov.rise_pct_of_ci !== null ? (
                <>des projets Community Impact</>
              ) : (
                <>aucun projet Community Impact</>
              )}
              <br />
              <span className="text-muted-2">base CI · {ciBase ?? "—"} projets</span>
            </p>
          </div>
          <div className="flex items-center gap-3">
            <RingStat percent={ov.rise_pct_of_all} color="var(--foreground)" />
            <p className="max-w-[10rem] text-xs text-muted">
              de tous les projets
              <br />
              <span className="text-muted-2">base tous projets · {fmt(ov.total_projects)}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatRow({ label, value, last }: { label: string; value: string; last?: boolean }) {
  return (
    <div className={`flex items-center justify-between py-2.5 ${last ? "" : "border-b border-border/60"}`}>
      <span className="text-sm text-muted">{label}</span>
      <span className="nexus-figure text-xl text-foreground">{value}</span>
    </div>
  );
}

function DomainBarList({ areas }: { areas: AreaBlock[] }) {
  const sorted = [...areas].sort((a, b) => b.total_projects - a.total_projects);
  const max = Math.max(1, ...sorted.map((a) => a.total_projects));
  return (
    <div className="rounded-2xl border border-border bg-surface p-5">
      <div className="nexus-label">Projets par domaine</div>
      <div className="mt-4 space-y-3">
        {sorted.map((area) => {
          const color = domainColor(area.label);
          const pct = (area.total_projects / max) * 100;
          return (
            <div key={area.code} className="flex items-center gap-3 text-sm">
              <span className="w-40 shrink-0 truncate text-foreground" title={area.label}>
                <span className="mr-2 inline-block h-2 w-2 rounded-full align-middle" style={{ background: color }} />
                {area.label}
              </span>
              <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-border">
                <span
                  className="block h-full rounded-full transition-all duration-500"
                  style={{ width: `${pct}%`, background: color }}
                />
              </span>
              <span className="nexus-figure w-8 text-right text-foreground">{area.total_projects}</span>
            </div>
          );
        })}
      </div>
      <p className="mt-4 text-xs text-muted-2">Un projet peut relever de plusieurs domaines : ne pas additionner.</p>
    </div>
  );
}

function OddReachList({ sdgs, onSeeByOdd }: { sdgs: SdgBlock[]; onSeeByOdd: () => void }) {
  const rows = sdgs.map((s) => ({ goal: s.goal, ...sumDirectPeople(s.aggregates, "external") }));
  const known = rows.filter((r) => r.count > 0).sort((a, b) => b.value - a.value).slice(0, 6);
  const unknownCount = rows.filter((r) => r.count === 0).length;
  const max = Math.max(1, ...known.map((r) => r.value));

  return (
    <div className="rounded-2xl border border-border bg-surface p-5">
      <div className="flex items-center justify-between">
        <div className="nexus-label">Personnes touchées par ODD · externe</div>
        <button onClick={onSeeByOdd} className="text-xs font-medium text-accent hover:text-accent-hover">
          Voir par ODD →
        </button>
      </div>
      {known.length === 0 ? (
        <p className="mt-4 text-sm text-muted">Aucune donnée pour ce filtre.</p>
      ) : (
        <div className="mt-4 space-y-3">
          {known.map((r) => (
            <div key={r.goal} className="flex items-center gap-3 text-sm">
              <span className="w-44 shrink-0 truncate text-foreground">
                <span className="mr-1.5 text-xs text-muted-2">ODD {r.goal}</span>
                {SDG_LABELS[r.goal]}
              </span>
              <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-border">
                <span
                  className="block h-full rounded-full bg-accent transition-all duration-500"
                  style={{ width: `${(r.value / max) * 100}%` }}
                />
              </span>
              <span className="nexus-figure w-12 text-right text-foreground">{fmt(r.value)}</span>
            </div>
          ))}
        </div>
      )}
      {unknownCount > 0 && (
        <p className="mt-4 text-xs italic text-muted-2">
          {unknownCount} ODD sans donnée : inconnu (non tracés)
        </p>
      )}
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
  onSeeByOdd,
}: {
  data: DashboardOverviewResponse;
  buckets: Record<DisplayBucket, Aggregate[]>;
  openTraceId: string | null;
  trace: TraceResponse | null;
  traceLoading: boolean;
  onSelect: (a: Aggregate) => void;
  onSeeByOdd: () => void;
}) {
  const ov = data.overview;
  const external = sumDirectPeople(ov.aggregates, "external");
  const internal = sumDirectPeople(ov.aggregates, "internal");
  const hours = metricValue(ov.aggregates, "VOLUNTEER_HOURS");

  // Decision KKF (2026-09-20) : sous les chiffres cles, ne montrer QUE le
  // detail qui est du vrai impact/resultat (bucket "impact" -- classe
  // IAOOI OUTCOME/IMPACT_CLAIM, classify.ts). Les buckets "resource"
  // (ressources mobilisees), "activity" (ce qui a ete fait), "reach"
  // (portee de communication, explicitement "non compte comme
  // beneficiaires") et "other" ne sont plus affiches ici : ce sont des
  // metriques de process/activite, pas de resultat, et un president/
  // investisseur qui vient lire l'impact n'a pas a les voir (meme principe
  // que D-34 : si ca n'aide pas a lire l'impact, ca sort de l'affichage).
  // La donnee n'est pas perdue -- toujours dans l'API et dans le detail par
  // domaine (ecran "Par domaine") -- seule cette vue la retire.
  const impactBucket = buckets.impact;

  return (
    <>
      {/* Deux lectures jamais mélangées (impact-science.md §7) : "ce que JCI a
          fait" (Projets, ressources) d'un côté, "ce qui a changé" (Impact,
          bloc visuellement distinct, D-22) de l'autre. */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <HeroStat value={external.value} isUnknown={external.count === 0} note="Jamais l'audience, jamais l'indirect" />
        <KpiCard label="Projets" value={fmt(ov.total_projects)} sub="projets uniques" />
        <KpiCard label="Heures de bénévolat" value={hours ? fmt(hours.value) : "inconnu"} sub="somme, projets uniques" />
        <WideCard
          label="Membres JCI mobilisés / formés"
          value={internal.count === 0 ? "inconnu" : fmt(internal.value)}
          ruleNote="Jamais additionné au public externe (R7)"
          footNote={
            external.count > 0 ? `Comptés séparément des ${fmt(external.value)} personnes touchées.` : undefined
          }
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <RiseCard ov={ov} />
        <div className="rounded-2xl border border-border bg-surface p-5">
          <StatRow label="Projets avec résultat mesuré" value={fmt(ov.projects_measured)} />
          <StatRow label="Pays actifs" value={fmt(ov.countries_active)} />
          <StatRow label="OL actives" value={fmt(ov.ols_active)} last />
        </div>
      </div>

      <section className={`rounded-2xl border p-5 ${BUCKET_STYLE.impact}`}>
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-foreground">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2.5" aria-hidden="true">
              <path d="M20 6 9 17l-5-5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            {BUCKET_LABEL.impact}
          </h2>
          {impactBucket.length > 0 && (
            <span className="text-xs text-muted">issus de {fmt(ov.projects_measured)} projet(s) avec résultat mesuré</span>
          )}
        </div>
        {impactBucket.length === 0 ? (
          <p className="mt-2 text-sm text-muted">
            Aucun résultat mesuré (par opposition à une simple activité) pour ce filtre pour l&apos;instant.
          </p>
        ) : (
          <>
            <div className="mt-4">
              <AggregateTable aggregates={impactBucket} onSelect={onSelect} />
            </div>
            {impactBucket.some((a) => a.measurement_id === openTraceId) && (
              <>
                {traceLoading && <p className="mt-2 text-xs text-muted">Chargement de la traçabilité…</p>}
                {!traceLoading && trace && <TracePanel trace={trace} />}
              </>
            )}
          </>
        )}
      </section>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <DomainBarList areas={data.areas} />
        <OddReachList sdgs={data.sdgs} onSeeByOdd={onSeeByOdd} />
      </div>
    </>
  );
}

function AreasScreen({
  areas,
  view,
  scopeOrganizationId,
  reportingYear,
}: {
  areas: AreaBlock[];
  view: View;
  scopeOrganizationId?: string;
  reportingYear?: number;
}) {
  return (
    <div className="space-y-4">
      {areas.map((area) => {
        const volunteers = metricValue(area.aggregates, "VOLUNTEERS");
        const hours = metricValue(area.aggregates, "VOLUNTEER_HOURS");
        const external = sumDirectPeople(area.aggregates, "external");
        const internal = sumDirectPeople(area.aggregates, "internal");
        const color = domainColor(area.label);
        return (
          <section
            key={area.code}
            className="rounded-2xl border border-border bg-surface p-4"
            style={{ borderLeftColor: color, borderLeftWidth: 3 }}
          >
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h2 className="flex items-center gap-2 text-base font-semibold uppercase tracking-wide text-foreground">
                <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: color }} />
                {area.label}
              </h2>
              <span
                className="text-sm text-muted"
                title={
                  area.secondary_only_count > 0
                    ? `Inclut ${area.secondary_only_count} projet(s) qui contribuent aussi à un autre domaine.`
                    : undefined
                }
              >
                {fmt(area.total_projects)} projets
              </span>
            </div>

            {area.total_projects > 0 && (
              <ProjectListDisclosure
                label={`Voir les ${fmt(area.total_projects)} projets →`}
                view={view}
                scopeOrganizationId={scopeOrganizationId}
                areaOfOpportunity={area.code}
                reportingYear={reportingYear}
              />
            )}

            <div className="mt-4 grid gap-4 md:grid-cols-3">
              <div>
                <h3 className="nexus-label">Ce qui a été fait</h3>
                {area.families.length === 0 ? (
                  <p className="mt-2 text-sm text-muted">Aucune famille d&apos;activité déclarée.</p>
                ) : (
                  <ul className="mt-2 space-y-1 text-sm">
                    {area.families.map((f) => (
                      <li key={f.code} className="flex justify-between border-b border-border/60 py-0.5">
                        <span className="text-foreground">{f.label}</span>
                        <span className="font-medium text-foreground">{f.project_count}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="rounded-xl border border-border bg-background p-3">
                <h3 className="nexus-label">Ressources</h3>
                <p className="mt-2 text-sm text-foreground">
                  Bénévoles {volunteers ? fmt(volunteers.value) : "inconnu"} · Heures {hours ? fmt(hours.value) : "inconnu"}
                </p>
                {/* Garde-fou anti double-comptage (revue PO 2026-09-20, §17) :
                    un projet actif dans plusieurs domaines apparaît dans
                    chacun de ses blocs -- sans cette phrase, les mêmes heures
                    pourraient sembler exister plusieurs fois. Affichée
                    seulement quand on sait, par le signal déjà disponible
                    (secondary_only_count), qu'un tel recouvrement existe pour
                    ce domaine précis -- jamais une mise en garde générique. */}
                {area.secondary_only_count > 0 && (
                  <p className="mt-1 text-xs text-muted-2">
                    Ressources partagées avec d&apos;autres domaines pour les projets multi-domaines.
                  </p>
                )}
              </div>

              {/* Bloc "Résultats mesurés" visuellement distinct des ressources
                  et de la portée (garde-fou D-22) : couleur et bordure
                  différentes, jamais le même bloc. Renommé depuis "Impact"
                  (revue PO 2026-09-20, §15) : "membres formés" n'est pas de
                  l'impact au sens de NEXUS (c'est justement la distinction
                  que le produit prétend faire respecter) -- ce sont des
                  résultats mesurés, pas encore un changement de long terme. */}
              <div className="rounded-xl border border-success/30 bg-success-bg p-3">
                <h3 className="text-xs font-semibold uppercase tracking-wide text-foreground">Résultats mesurés</h3>
                <p className="mt-2 text-sm text-foreground">
                  Membres formés {internal.count === 0 ? "inconnu" : fmt(internal.value)} · Public externe
                  formé {external.count === 0 ? "inconnu" : fmt(external.value)} · Résultat mesuré :{" "}
                  {fmt(area.projects_measured)} projet(s)
                </p>
              </div>
            </div>

            {area.code === "CI" && area.rise && (
              <div className="mt-4 rounded-xl border border-border bg-background p-3">
                <h3 className="nexus-label">RISE</h3>
                <p className="mt-2 text-sm text-foreground">
                  Oui : {area.rise.yes} · Non : {area.rise.no}
                </p>
                {area.rise.pillars.length > 0 && (
                  <ul className="mt-2 flex flex-wrap gap-2 text-xs">
                    {area.rise.pillars.map((p) => (
                      <li
                        key={p.code}
                        className="rounded-full border border-border bg-surface px-2 py-1 text-foreground"
                        title={`Code interne : ${p.code}`}
                      >
                        {risePillarLabel(p.code)} · {p.project_count}
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

function SdgsScreen({
  sdgs,
  view,
  scopeOrganizationId,
  reportingYear,
}: {
  sdgs: SdgBlock[];
  view: View;
  scopeOrganizationId?: string;
  reportingYear?: number;
}) {
  if (sdgs.length === 0) {
    return <p className="text-sm text-muted">Aucun projet classé sur un ODD pour ce filtre.</p>;
  }
  // Barres intégrées à la colonne "Personnes touchées" (brief étape 5, p. 5) :
  // largeur proportionnelle à la valeur, jamais dessinée pour un "inconnu"
  // (§13 du prompt produit -- unknown ≠ 0, aucune barre pour ce qu'on ne sait
  // pas). Le maximum se calcule uniquement sur les ODD dont la valeur est
  // connue, sur ce même écran.
  const maxExternal = Math.max(
    1,
    ...sdgs.map((s) => sumDirectPeople(s.aggregates, "external")).filter((r) => r.count > 0).map((r) => r.value)
  );
  return (
    <section className="rounded-2xl border border-border bg-surface p-5">
      {/* Finitions (brief étape 6) : à 390px, ce tableau à 6 colonnes ne
          peut pas tenir sans dégrader la lecture -- on isole le défilement
          horizontal à CE tableau plutôt que de laisser la page entière
          défiler horizontalement. Indice de défilement visible seulement
          sur petit écran (sur desktop, tout tient déjà). */}
      <p className="mb-2 text-xs text-muted-2 sm:hidden">Faites glisser pour voir toutes les colonnes →</p>
      <div className="overflow-x-auto">
      <table className="w-full min-w-[720px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
            <th className="py-2 pr-3 font-medium">ODD</th>
            <th className="py-2 pr-3 font-medium">Principal</th>
            <th className="py-2 pr-3 font-medium">Secondaire</th>
            <th className="py-2 pr-3 font-medium">Personnes touchées (externe)</th>
            <th className="py-2 pr-3 font-medium">Résultat mesuré</th>
            <th className="py-2 pr-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          {sdgs.map((s) => {
            const external = sumDirectPeople(s.aggregates, "external");
            return (
              <tr key={s.goal} className="border-b border-border/60 align-top">
                <td className="py-3 pr-3 font-medium text-foreground">
                  <span className="mr-2 inline-flex h-6 w-6 items-center justify-center rounded-full border border-accent/40 bg-accent/10 text-xs text-accent">
                    {s.goal}
                  </span>
                  {SDG_LABELS[s.goal]}
                </td>
                <td className="py-3 pr-3 text-foreground">
                  {s.primary_count > 0 ? (
                    <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-accent text-xs font-medium text-accent-foreground">
                      {s.primary_count}
                    </span>
                  ) : (
                    <span className="text-muted-2">0</span>
                  )}
                </td>
                <td className="py-3 pr-3 text-foreground">
                  {s.secondary_count > 0 ? (
                    <span className="inline-flex h-6 w-6 items-center justify-center rounded-full border border-border-strong text-xs text-foreground">
                      {s.secondary_count}
                    </span>
                  ) : (
                    <span className="text-muted-2">0</span>
                  )}
                </td>
                <td className="py-3 pr-3">
                  {external.count === 0 ? (
                    <span className="inline-flex items-center gap-2">
                      <span className="italic text-muted-2">inconnu</span>
                      <span
                        className="h-1.5 w-24 rounded-full opacity-50"
                        style={{
                          backgroundImage:
                            "repeating-linear-gradient(45deg, var(--border-strong) 0, var(--border-strong) 3px, transparent 3px, transparent 6px)",
                        }}
                      />
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-2">
                      <span className="nexus-figure text-foreground">{fmt(external.value)}</span>
                      <span className="h-1.5 w-24 overflow-hidden rounded-full bg-border">
                        <span
                          className="block h-full rounded-full bg-accent transition-all duration-500"
                          style={{ width: `${(external.value / maxExternal) * 100}%` }}
                        />
                      </span>
                    </span>
                  )}
                </td>
                <td className="py-3 pr-3 text-foreground">
                  {s.projects_measured > 0 && (
                    <span className="mr-1.5 inline-flex items-center gap-1 text-success">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" aria-hidden="true">
                        <path d="M20 6 9 17l-5-5" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </span>
                  )}
                  {s.projects_measured}
                </td>
                <td className="py-3 pr-3">
                  <ProjectListDisclosure
                    label="Voir les projets →"
                    view={view}
                    scopeOrganizationId={scopeOrganizationId}
                    sdg={s.goal}
                    reportingYear={reportingYear}
                  />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      </div>
      <p className="mt-3 text-xs text-muted-2">
        Principal et secondaire ne sont jamais additionnés en un seul chiffre (D-27).
      </p>
    </section>
  );
}
