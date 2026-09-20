"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ApiError,
  confirmSubmission,
  friendlyErrorMessage,
  getSubmission,
  getSubmissionDraft,
  getTaxonomy,
} from "@/lib/api";
import { DEMO_USER_ID } from "@/lib/config";
import ActivityFamilySelector from "@/components/ActivityFamilySelector";
import AreaSelector from "@/components/AreaSelector";
import RiseBlock from "@/components/RiseBlock";
import CandidateCard from "@/components/CandidateCard";
import SdgSelector from "@/components/SdgSelector";
import OriginBadge, { type Origin } from "@/components/OriginBadge";
import type {
  CandidateMapping,
  ConfirmActivityFamilyInput,
  ConfirmAreaInput,
  ConfirmCandidateInput,
  ConfirmErrorItem,
  ConfirmRequestBody,
  ConfirmResult,
  ConfirmRiseInput,
  ConfirmSdgInput,
  ExtractionPayload,
  MappingPayload,
  TaxonomyContent,
  ValueOriginQuote,
} from "@/lib/types";

type Phase = "loading" | "ready" | "not_ready" | "error" | "already_confirmed" | "success";

function isOtherCode(code: string): boolean {
  return code.endsWith("_OTHER") || code === "OTHER";
}

/** Origine d'un champ ressource {value,origin,quote} : "à remplir" si la
 * responsable n'a encore rien saisi, sinon l'origine de l'extraction
 * (impact-science.md §6, A6 : chaque champ porte son origine). */
function fieldOrigin(extracted: ValueOriginQuote<number> | undefined, currentStr: string): Origin {
  if (currentStr.trim() === "") return "to_fill";
  return extracted?.origin === "quoted" ? "written" : "inferred";
}

export default function ConfirmPage() {
  const params = useParams<{ id: string }>();
  const submissionId = params.id;

  const [phase, setPhase] = useState<Phase>("loading");
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [rawText, setRawText] = useState("");
  const [taxonomy, setTaxonomy] = useState<TaxonomyContent | null>(null);
  const [extraction, setExtraction] = useState<ExtractionPayload | null>(null);
  const [mapping, setMapping] = useState<MappingPayload | null>(null);

  const [projectName, setProjectName] = useState("");
  const [reportingYear, setReportingYear] = useState<number>(new Date().getFullYear());
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");

  const [activityFamilies, setActivityFamilies] = useState<ConfirmActivityFamilyInput[]>([]);
  const [areas, setAreas] = useState<ConfirmAreaInput[]>([]);
  const [rise, setRise] = useState<ConfirmRiseInput>({ status: "not_applicable", pillars: [] });
  const [sdgs, setSdgs] = useState<ConfirmSdgInput[]>([]);
  const [overrides, setOverrides] = useState<Record<string, ConfirmCandidateInput>>({});

  // Ressources (D-25/D-28/D-30) : bénévoles JCI, durée, heures pré-calculées.
  const [volunteersStr, setVolunteersStr] = useState("");
  const [durationStr, setDurationStr] = useState("");
  const [hoursStr, setHoursStr] = useState("");
  const [hoursCorrected, setHoursCorrected] = useState(false);

  const [outcomeChoice, setOutcomeChoice] = useState<"pending_follow_up" | "none" | null>(null);
  const [expectedOutcome, setExpectedOutcome] = useState("");
  const [followUpDate, setFollowUpDate] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [generalErrors, setGeneralErrors] = useState<string[]>([]);
  const [result, setResult] = useState<ConfirmResult | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setPhase("loading");
      try {
        const [submission, draft, tax] = await Promise.all([
          getSubmission(submissionId),
          getSubmissionDraft(submissionId),
          getTaxonomy(),
        ]);
        if (cancelled) return;

        if (submission.pipeline_status === "confirmed") {
          setPhase("already_confirmed");
          return;
        }
        if (submission.pipeline_status === "failed") {
          setErrorMsg(
            "Ce projet n'a pas pu être analysé. Retournez à l'accueil pour relancer l'analyse."
          );
          setPhase("error");
          return;
        }
        if (submission.pipeline_status !== "awaiting_confirmation") {
          setPhase("not_ready");
          return;
        }

        const structured = draft.candidates.find((c) => c.stage === "structured");
        const standardized = draft.candidates.find((c) => c.stage === "standardized");
        if (!structured || !standardized) {
          setErrorMsg("L'analyse n'a pas produit de résultat exploitable.");
          setPhase("error");
          return;
        }
        const extractionPayload = structured.payload as ExtractionPayload;
        const mappingPayload = standardized.payload as MappingPayload;

        setRawText(submission.raw_text);
        setTaxonomy(tax.content);
        setExtraction(extractionPayload);
        setMapping(mappingPayload);

        setProjectName(extractionPayload.project?.name?.value || "");
        setReportingYear(extractionPayload.project?.period?.reporting_year || new Date().getFullYear());
        setPeriodStart(extractionPayload.project?.period?.start || "");
        setPeriodEnd(extractionPayload.project?.period?.end || "");

        const volunteersValue = extractionPayload.project?.jci_volunteers_count?.value;
        const durationValue = extractionPayload.project?.activity_duration_hours?.value;
        setVolunteersStr(volunteersValue != null ? String(volunteersValue) : "");
        setDurationStr(durationValue != null ? String(durationValue) : "");
        setHoursCorrected(false);

        const pc = mappingPayload.project_classification;
        setActivityFamilies(pc.activity_families.map((f) => ({ code: f.code, other_label: f.other_label })));
        setAreas(pc.area_of_opportunity.map((a) => ({ code: a.code, role: a.role })));
        setRise({ status: pc.rise.status, pillars: pc.rise.pillars.map((p) => p.code) });
        setSdgs(pc.sdgs.map((s) => ({ goal: s.goal, role: s.role, justification: s.justification })));

        const initialOverrides: Record<string, ConfirmCandidateInput> = {};
        for (const cand of extractionPayload.candidates) {
          if (!mappingPayload.candidate_mappings.some((m) => m.candidate_id === cand.candidate_id)) continue;
          initialOverrides[cand.candidate_id] = {
            candidate_id: cand.candidate_id,
            include: true,
            value: null,
            value_internal: null,
            value_external: null,
            count_type: null,
            internal_external: null,
            corrected: false,
          };
        }
        setOverrides(initialOverrides);
        setPhase("ready");
      } catch (err) {
        if (cancelled) return;
        setErrorMsg(friendlyErrorMessage(err));
        setPhase("error");
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [submissionId]);

  // D-24/AC-17 : décocher Community Impact (CI) ramène RISE à not_applicable
  // et efface les piliers, sans attendre une action supplémentaire du SG.
  useEffect(() => {
    const ciPresent = areas.some((a) => a.code === "CI");
    if (!ciPresent && rise.status !== "not_applicable") {
      setRise({ status: "not_applicable", pillars: [] });
    }
  }, [areas, rise.status]);

  // D-30 : les heures se recalculent automatiquement (bénévoles × durée)
  // tant que le SG ne les a pas corrigées lui-même. Une fois corrigées,
  // elles ne sont plus jamais recalculées silencieusement à sa place.
  useEffect(() => {
    if (hoursCorrected) return;
    const v = Number(volunteersStr);
    const d = Number(durationStr);
    if (volunteersStr.trim() !== "" && durationStr.trim() !== "" && !Number.isNaN(v) && !Number.isNaN(d)) {
      setHoursStr(String(v * d));
    } else {
      setHoursStr("");
    }
  }, [volunteersStr, durationStr, hoursCorrected]);

  const mappingById = useMemo(() => {
    const map: Record<string, CandidateMapping> = {};
    mapping?.candidate_mappings.forEach((m) => (map[m.candidate_id] = m));
    return map;
  }, [mapping]);

  const candidateList = useMemo(() => {
    if (!extraction) return [];
    return extraction.candidates
      .filter((c) => mappingById[c.candidate_id])
      .map((c) => ({ extraction: c, mapping: mappingById[c.candidate_id] }));
  }, [extraction, mappingById]);

  const mainCandidates = candidateList.filter((c) => c.mapping.metric_code !== "COMM_AUDIENCE");
  const audienceCandidates = candidateList.filter((c) => c.mapping.metric_code === "COMM_AUDIENCE");

  // Bug de communication constaté en démo (2026-09-20) : le bandeau "Résultat"
  // affirmait qu'un résultat mesuré avait été identifié "dans les chiffres
  // ci-dessus (« Pour qui »)" — mais la vraie raison n'est pas le champ
  // "Pour qui" (internal_external), c'est la classification IAOOI = OUTCOME
  // d'un candidat retenu, qui n'est elle-même visible nulle part ailleurs sur
  // la fiche. Le SG n'avait donc aucun moyen de comprendre l'affirmation.
  // On nomme maintenant explicitement le(s) candidat(s) responsables.
  const outcomeCandidates = candidateList.filter(
    (c) => overrides[c.extraction.candidate_id]?.include && c.mapping.iaooi_value === "OUTCOME"
  );
  const hasOutcomeCandidate = outcomeCandidates.length > 0;

  const ciPresent = areas.some((a) => a.code === "CI");
  const primaryAreaCount = areas.filter((a) => a.role === "primary").length;
  const primarySdgCount = sdgs.filter((s) => s.role === "primary").length;

  const familiesOk =
    activityFamilies.length > 0 &&
    activityFamilies.every((f) => !isOtherCode(f.code) || (f.other_label ?? "").trim() !== "");
  const areasOk = areas.length > 0 && primaryAreaCount === 1;
  const riseOk = ciPresent
    ? rise.status !== "not_applicable" && (rise.status !== "yes" || rise.pillars.length > 0)
    : rise.status === "not_applicable";
  const sdgsOk = sdgs.length > 0 && primarySdgCount === 1 && sdgs.every((s) => s.justification.trim() !== "");
  const resourcesOk =
    volunteersStr.trim() !== "" &&
    durationStr.trim() !== "" &&
    hoursStr.trim() !== "" &&
    !Number.isNaN(Number(volunteersStr)) &&
    !Number.isNaN(Number(durationStr)) &&
    !Number.isNaN(Number(hoursStr));
  const mixedOk = Object.values(overrides).every((o) => {
    if (!o.include) return true;
    const ie = o.internal_external ?? mappingById[o.candidate_id]?.internal_external;
    if (ie !== "mixed") return true;
    return o.value_internal != null && o.value_external != null;
  });
  const outcomeOk =
    hasOutcomeCandidate ||
    outcomeChoice === "none" ||
    (outcomeChoice === "pending_follow_up" && expectedOutcome.trim() !== "" && followUpDate !== "");

  const canSubmit =
    familiesOk && areasOk && riseOk && sdgsOk && resourcesOk && mixedOk && outcomeOk && !submitting;

  // Barre d'action collante (brief de refonte visuelle, étape 4, p. 6) :
  // même logique de blocage que `canSubmit` ci-dessus (rien n'y change),
  // seulement rendue lisible -- la responsable doit savoir QUOI compléter
  // sans remonter chercher chaque message d'erreur un par un.
  const missingItems: string[] = [];
  if (!familiesOk) missingItems.push("au moins une famille d'activité");
  if (!areasOk) missingItems.push("un domaine principal");
  if (!riseOk) missingItems.push("RISE (Community Impact)");
  if (!sdgsOk) missingItems.push("un ODD principal justifié");
  if (!resourcesOk) missingItems.push("bénévoles, durée et heures");
  if (!mixedOk) missingItems.push("les chiffres du public mixte");
  if (!outcomeOk) missingItems.push("le résultat du projet");

  function updateOverride(candidateId: string, next: ConfirmCandidateInput) {
    setOverrides((prev) => ({ ...prev, [candidateId]: next }));
  }

  async function handleConfirm() {
    setSubmitting(true);
    setFieldErrors({});
    setGeneralErrors([]);
    const body: ConfirmRequestBody = {
      project: {
        name: projectName.trim() || null,
        reporting_year: reportingYear,
        period_start: periodStart || null,
        period_end: periodEnd || null,
        outcome_status: hasOutcomeCandidate ? "measured" : (outcomeChoice as "pending_follow_up" | "none"),
        expected_outcome: outcomeChoice === "pending_follow_up" ? expectedOutcome : null,
        follow_up_date: outcomeChoice === "pending_follow_up" ? followUpDate : null,
        jci_volunteers_count: Number(volunteersStr),
        activity_duration_hours: Number(durationStr),
        volunteer_hours: Number(hoursStr),
        volunteer_hours_corrected: hoursCorrected,
      },
      axes: {
        activity_families: activityFamilies,
        area_of_opportunity: areas,
        rise,
        sdgs,
      },
      candidates: Object.values(overrides),
      confirmed_by: DEMO_USER_ID,
    };
    try {
      const res = await confirmSubmission(submissionId, body);
      setResult(res);
      setPhase("success");
    } catch (err) {
      if (err instanceof ApiError && err.status === 422) {
        const detail = err.body?.detail;
        const errors: ConfirmErrorItem[] =
          typeof detail === "object" && detail && "errors" in detail
            ? ((detail as { errors: ConfirmErrorItem[] }).errors ?? [])
            : [];
        const nextFieldErrors: Record<string, string> = {};
        const nextGeneral: string[] = [];
        errors.forEach((e) => {
          if (e.candidate_id) nextFieldErrors[e.candidate_id] = e.message;
          else nextGeneral.push(e.message);
        });
        setFieldErrors(nextFieldErrors);
        setGeneralErrors(nextGeneral.length ? nextGeneral : ["Le projet n'a pas pu être confirmé."]);
      } else {
        setGeneralErrors([friendlyErrorMessage(err)]);
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (phase === "loading") {
    return <p className="text-sm text-muted">Chargement de la fiche…</p>;
  }
  if (phase === "not_ready") {
    return <p className="text-sm text-muted">Analyse en cours, réessayez dans un instant.</p>;
  }
  if (phase === "already_confirmed") {
    return (
      <div className="rounded-lg border border-success/40 bg-success-bg p-6">
        <h1 className="text-lg font-semibold text-success">Projet déjà confirmé</h1>
        <p className="mt-2 text-sm">Ce projet a déjà été enregistré dans NEXUS.</p>
        <Link href="/dashboards" className="mt-4 inline-block text-sm font-medium text-accent">
          Voir les tableaux de bord →
        </Link>
      </div>
    );
  }
  if (phase === "error") {
    return (
      <div className="rounded-lg border border-danger/40 bg-danger-bg p-6">
        <h1 className="text-lg font-semibold text-danger">Impossible d&apos;afficher ce projet</h1>
        <p className="mt-2 text-sm">{errorMsg}</p>
        <Link href="/" className="mt-4 inline-block text-sm font-medium text-accent">
          ← Retour à l&apos;accueil
        </Link>
      </div>
    );
  }
  if (phase === "success" && result) {
    return (
      <div className="rounded-lg border border-success/40 bg-success-bg p-6">
        <h1 className="text-lg font-semibold text-success">Projet ajouté à NEXUS</h1>
        <p className="mt-2 text-sm">
          {result.measurement_ids.length} mesure(s) enregistrée(s) — ce projet contribue maintenant aux
          tableaux de bord national et mondial.
        </p>
        <div className="mt-4 flex gap-3">
          <Link
            href="/dashboards"
            className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-accent-foreground"
          >
            Voir les tableaux de bord
          </Link>
          <Link href="/" className="rounded-md border border-border px-4 py-2 text-sm font-medium">
            Nouveau projet
          </Link>
        </div>
      </div>
    );
  }

  const taxAxes = taxonomy!.classification_axes;

  return (
    <div className="space-y-8 pb-28">
      <div>
        <h1 className="text-xl font-semibold">Vérifiez votre projet</h1>
        <p className="mt-1 text-sm text-muted">Corrigez ce qui doit l&apos;être, puis confirmez.</p>
      </div>

      {/* Sentiment de réussite (revue Product Owner 2026-09-20, §8) : annoncer
          immédiatement que NEXUS a compris le texte, sans jamais afficher de
          score de confiance interne ("96 %" ne veut rien dire pour l'OL). */}
      <div className="rounded-md border border-success/30 bg-success-bg px-4 py-3 text-sm text-success">
        NEXUS a compris votre projet. Vérifiez les points ci-dessous et corrigez si besoin.
      </div>

      {generalErrors.length > 0 && (
        <div className="rounded-md border border-danger/40 bg-danger-bg p-3 text-sm text-danger">
          <ul className="list-disc pl-5">
            {generalErrors.map((m, i) => (
              <li key={i}>{m}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 01 — Votre projet */}
      <div className="space-y-3">
      <SectionKicker n={1} label="Votre projet" />
      <section className="rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">Le projet</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-2">
          <div>
            <div className="mb-1 flex items-center gap-1">
              <label className="text-xs text-muted">Nom du projet</label>
              <OriginBadge origin="inferred" />
            </div>
            <input
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <div className="mb-1 flex items-center gap-1">
              <label className="text-xs text-muted">Année de référence</label>
              <OriginBadge origin="written" />
            </div>
            <input
              type="number"
              value={reportingYear}
              onChange={(e) => setReportingYear(Number(e.target.value))}
              className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <div className="mb-1 flex items-center gap-1">
              <label className="text-xs text-muted">Début</label>
              <OriginBadge origin="written" />
            </div>
            <input
              type="date"
              value={periodStart}
              onChange={(e) => setPeriodStart(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <div className="mb-1 flex items-center gap-1">
              <label className="text-xs text-muted">Fin</label>
              <OriginBadge origin="written" />
            </div>
            <input
              type="date"
              value={periodEnd}
              onChange={(e) => setPeriodEnd(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
            />
          </div>
        </div>
        {extraction?.project?.period?.quote && (
          <p className="mt-2 text-xs text-muted">« {extraction.project.period.quote} »</p>
        )}
      </section>
      </div>

      {/* 02 — Ce que NEXUS a compris : Quoi + Où + RISE + ODD */}
      <div className="space-y-3">
      <SectionKicker n={2} label="Ce que NEXUS a compris" />
      <section className="rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">Quoi</h2>
          <OriginBadge origin="inferred" />
        </div>
        <p className="mt-1 text-xs text-muted">La ou les familles d&apos;activité de ce projet.</p>
        <div className="mt-3">
          <ActivityFamilySelector
            options={taxAxes.activity_family.values}
            value={activityFamilies}
            onChange={setActivityFamilies}
          />
        </div>
        {activityFamilies.length === 0 && (
          <p className="mt-2 text-xs text-danger">Au moins une famille d&apos;activité est requise.</p>
        )}
      </section>

      {/* 2. Où */}
      <section className="rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">Où</h2>
          <OriginBadge origin="inferred" />
        </div>
        <p className="mt-1 text-xs text-muted">Domaine(s) d&apos;intervention JCI, avec exactement un principal.</p>
        <div className="mt-3">
          <AreaSelector options={taxAxes.area_of_opportunity.values} value={areas} onChange={setAreas} />
        </div>
        {!areasOk && (
          <p className="mt-2 text-xs text-danger">
            {areas.length === 0
              ? "Au moins un domaine est requis."
              : `Exactement un domaine « principal » est requis (actuellement : ${primaryAreaCount}).`}
          </p>
        )}
      </section>

      {/* 3. RISE (visible seulement si CI est coché) */}
      {ciPresent && (
        <RiseBlock pillarOptions={taxonomy!.rise_pillars.values} value={rise} onChange={setRise} />
      )}

      {/* 4. ODD */}
      <section className="rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">
            Objectifs de développement durable
          </h2>
          <OriginBadge origin="inferred" />
        </div>
        <p className="mt-1 text-xs text-muted">
          Aucun plafond : tout ODD réellement touché peut être coché, à condition d&apos;être justifié.
          Exactement un ODD principal.
        </p>
        <div className="mt-3">
          <SdgSelector value={sdgs} onChange={setSdgs} />
        </div>
        {!sdgsOk && (
          <p className="mt-2 text-xs text-danger">
            {sdgs.length === 0
              ? "Au moins un ODD est requis."
              : primarySdgCount !== 1
              ? `Exactement un ODD principal est requis (actuellement : ${primarySdgCount}).`
              : "Une justification est requise pour chaque ODD retenu."}
          </p>
        )}
      </section>
      </div>

      {/* 03 — Qui et quelles ressources */}
      <div className="space-y-3">
      <SectionKicker n={3} label="Qui et quelles ressources" />
      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">Pour qui</h2>
        <div className="mt-3 space-y-3">
          {mainCandidates.map(({ extraction: cand, mapping: map }) => (
            <CandidateCard
              key={cand.candidate_id}
              extraction={cand}
              mapping={map}
              rawText={rawText}
              override={overrides[cand.candidate_id]}
              onChange={(next) => updateOverride(cand.candidate_id, next)}
              errorMessage={fieldErrors[cand.candidate_id]}
            />
          ))}
        </div>
        {audienceCandidates.length > 0 && (
          <div className="mt-4">
            <h3 className="text-xs font-semibold uppercase tracking-wide text-muted">
              Classé à part — non compté comme bénéficiaires
            </h3>
            <div className="mt-3 space-y-3">
              {audienceCandidates.map(({ extraction: cand, mapping: map }) => (
                <CandidateCard
                  key={cand.candidate_id}
                  extraction={cand}
                  mapping={map}
                  rawText={rawText}
                  override={overrides[cand.candidate_id]}
                  onChange={(next) => updateOverride(cand.candidate_id, next)}
                  errorMessage={fieldErrors[cand.candidate_id]}
                  accent="border-border bg-background"
                />
              ))}
            </div>
          </div>
        )}
      </section>

      {/* 6. Ressources */}
      <section className="rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">Ressources</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-3">
          <div>
            <div className="mb-1 flex items-center gap-1">
              <label className="text-xs text-muted">Bénévoles JCI</label>
              <OriginBadge origin={fieldOrigin(extraction?.project?.jci_volunteers_count, volunteersStr)} />
            </div>
            <input
              type="number"
              min={0}
              value={volunteersStr}
              onChange={(e) => setVolunteersStr(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <div className="mb-1 flex items-center gap-1">
              <label className="text-xs text-muted">Durée de l&apos;activité (heures)</label>
              <OriginBadge origin={fieldOrigin(extraction?.project?.activity_duration_hours, durationStr)} />
            </div>
            <input
              type="number"
              min={0}
              value={durationStr}
              onChange={(e) => setDurationStr(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
            />
          </div>
          <div>
            <div className="mb-1 flex items-center gap-1">
              <label className="text-xs text-muted">Heures de bénévolat</label>
              <OriginBadge origin="calculated" />
            </div>
            <input
              type="number"
              min={0}
              value={hoursStr}
              onChange={(e) => {
                setHoursStr(e.target.value);
                setHoursCorrected(true);
              }}
              className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
            />
          </div>
        </div>
        {(extraction?.project?.jci_volunteers_count?.quote || extraction?.project?.activity_duration_hours?.quote) && (
          <p className="mt-2 text-xs text-muted">
            {extraction?.project?.jci_volunteers_count?.quote && (
              <>« {extraction.project.jci_volunteers_count.quote} » </>
            )}
            {extraction?.project?.activity_duration_hours?.quote && (
              <>« {extraction.project.activity_duration_hours.quote} »</>
            )}
          </p>
        )}
        {!resourcesOk && (
          <p className="mt-2 text-xs text-danger">
            Bénévoles JCI, durée et heures de bénévolat sont obligatoires (0 est accepté, un champ vide ne
            l&apos;est pas).
          </p>
        )}
      </section>
      </div>

      {/* 04 — Ce que le projet a produit */}
      <div className="space-y-3">
      <SectionKicker n={4} label="Ce que le projet a produit" />
      <section className="rounded-lg border border-success/40 bg-success-bg p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-success">Résultat</h2>
        {hasOutcomeCandidate ? (
          <div className="mt-3 space-y-1 text-sm">
            <p>
              NEXUS a identifié {outcomeCandidates.length > 1 ? "les résultats suivants" : "un résultat"}{" "}
              pour ce projet — un changement chez les bénéficiaires, pas seulement une activité :
            </p>
            <ul className="ml-4 list-disc">
              {outcomeCandidates.map((c) => (
                <li key={c.extraction.candidate_id}>
                  {c.mapping.source_wording_class || c.extraction.metric_label_source}
                </li>
              ))}
            </ul>
            <p className="text-xs text-muted">
              Ce projet est donc marqué automatiquement « résultat mesuré » — pas besoin de répondre à la
              question de suivi ci-dessous.
            </p>
          </div>
        ) : (
          <div className="mt-3 space-y-2 text-sm">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="outcome-choice"
                checked={outcomeChoice === "pending_follow_up"}
                onChange={() => setOutcomeChoice("pending_follow_up")}
              />
              Pas encore mesurable à ce stade
            </label>
            {outcomeChoice === "pending_follow_up" && (
              <div className="ml-6 grid gap-2 sm:grid-cols-2">
                <input
                  placeholder="Effet attendu"
                  value={expectedOutcome}
                  onChange={(e) => setExpectedOutcome(e.target.value)}
                  className="rounded-md border border-border bg-background px-2 py-1.5 text-sm"
                />
                <input
                  type="date"
                  value={followUpDate}
                  onChange={(e) => setFollowUpDate(e.target.value)}
                  className="rounded-md border border-border bg-background px-2 py-1.5 text-sm"
                />
              </div>
            )}
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="outcome-choice"
                checked={outcomeChoice === "none"}
                onChange={() => setOutcomeChoice("none")}
              />
              Aucun effet mesurable visé
            </label>
          </div>
        )}
      </section>
      </div>

      {/* Barre d'action collante (brief étape 4, p. 6) : reste visible au
          défilement pour que la personne sache, à tout moment, ce qu'il
          reste à compléter -- sans changer quand le bouton s'active
          (`canSubmit`, inchangé). */}
      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-background/95 backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm">
            {missingItems.length === 0 ? (
              <span className="text-success">Tout est prêt.</span>
            ) : (
              <>
                <span className="font-medium text-warning">
                  {missingItems.length} point{missingItems.length > 1 ? "s" : ""} à compléter
                </span>
                <span className="text-muted"> — {missingItems.join(", ")}</span>
              </>
            )}
          </p>
          <button
            onClick={handleConfirm}
            disabled={!canSubmit}
            className="shrink-0 rounded-md bg-accent px-5 py-2.5 text-sm font-medium text-accent-foreground transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-40"
          >
            {submitting ? "Confirmation en cours…" : "Confirmer le projet"}
          </button>
        </div>
      </div>
    </div>
  );
}

// Revue Product Owner (2026-09-20, §7) : "les sections devraient raconter une
// histoire". Un simple repère numéroté 01→05 au-dessus de chaque groupe,
// sans toucher aux composants existants ni à leurs règles de validation --
// juste rendre visible la progression Projet → Compréhension → Qui/Ressources
// → Résultat → Confirmer.
function SectionKicker({ n, label }: { n: number; label: string }) {
  return (
    <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted">
      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-accent/15 text-accent">
        {n}
      </span>
      {label}
    </div>
  );
}
