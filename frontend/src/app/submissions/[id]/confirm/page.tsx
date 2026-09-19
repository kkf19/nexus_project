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
import ChipMultiSelect from "@/components/ChipMultiSelect";
import CandidateCard from "@/components/CandidateCard";
import SdgSelector from "@/components/SdgSelector";
import OriginBadge from "@/components/OriginBadge";
import type {
  CandidateMapping,
  ConfirmCandidateInput,
  ConfirmErrorItem,
  ConfirmRequestBody,
  ConfirmResult,
  ConfirmSdgInput,
  ExtractionPayload,
  MappingPayload,
  TaxonomyContent,
} from "@/lib/types";

type Phase = "loading" | "ready" | "not_ready" | "error" | "already_confirmed" | "success";

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
  const [areaOfOpportunity, setAreaOfOpportunity] = useState<string[]>([]);
  const [programme, setProgramme] = useState<string[]>([]);
  const [risePillars, setRisePillars] = useState<string[]>([]);
  const [sdgs, setSdgs] = useState<ConfirmSdgInput[]>([]);
  const [overrides, setOverrides] = useState<Record<string, ConfirmCandidateInput>>({});

  const [outcomeChoice, setOutcomeChoice] = useState<"pending_follow_up" | "none" | null>(null);
  const [expectedOutcome, setExpectedOutcome] = useState("");
  const [followUpDate, setFollowUpDate] = useState("");

  const [confirmations, setConfirmations] = useState({ C1: false, C2: false, C3: false, C4: false });

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
            "Cette fiche n'a pas pu être analysée. Retournez à l'accueil pour relancer l'analyse."
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
          setErrorMsg("L'analyse n'a pas produit de fiche exploitable.");
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

        const pc = mappingPayload.project_classification;
        setAreaOfOpportunity(pc.area_of_opportunity.map((a) => a.code));
        setProgramme(pc.programme.map((p) => p.code));
        setRisePillars(pc.rise_pillars.map((r) => (typeof r === "string" ? r : r.code)));
        setSdgs(pc.sdgs.map((s) => ({ goal: s.goal, role: s.role })));

        const initialOverrides: Record<string, ConfirmCandidateInput> = {};
        for (const cand of extractionPayload.candidates) {
          if (!mappingPayload.candidate_mappings.some((m) => m.candidate_id === cand.candidate_id)) continue;
          initialOverrides[cand.candidate_id] = {
            candidate_id: cand.candidate_id,
            include: true,
            value: null,
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

  const hasOutcomeCandidate = candidateList.some(
    (c) => overrides[c.extraction.candidate_id]?.include && c.mapping.iaooi_value === "OUTCOME"
  );

  const c4Satisfied = hasOutcomeCandidate
    ? confirmations.C4
    : outcomeChoice === "none" ||
      (outcomeChoice === "pending_follow_up" && expectedOutcome.trim() !== "" && followUpDate !== "");

  const primaryCount = sdgs.filter((s) => s.role === "primary").length;
  const riseSelected = programme.includes("RISE");
  const includedCount = Object.values(overrides).filter((o) => o.include).length;

  const canSubmit =
    confirmations.C1 &&
    confirmations.C2 &&
    confirmations.C3 &&
    c4Satisfied &&
    areaOfOpportunity.length > 0 &&
    primaryCount === 1 &&
    (!riseSelected || risePillars.length > 0) &&
    includedCount > 0 &&
    !submitting;

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
      },
      axes: { area_of_opportunity: areaOfOpportunity, programme, rise_pillars: risePillars, sdgs },
      confirmations: { ...confirmations, C4: c4Satisfied },
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
        setGeneralErrors(nextGeneral.length ? nextGeneral : ["La fiche n'a pas pu être confirmée."]);
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
        <h1 className="text-lg font-semibold text-success">Fiche déjà confirmée</h1>
        <p className="mt-2 text-sm">Cette fiche a déjà été enregistrée.</p>
        <Link href="/dashboards" className="mt-4 inline-block text-sm font-medium text-accent">
          Voir les tableaux de bord →
        </Link>
      </div>
    );
  }
  if (phase === "error") {
    return (
      <div className="rounded-lg border border-danger/40 bg-danger-bg p-6">
        <h1 className="text-lg font-semibold text-danger">Impossible d&apos;afficher cette fiche</h1>
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
        <h1 className="text-lg font-semibold text-success">Fiche confirmée</h1>
        <p className="mt-2 text-sm">
          {result.measurement_ids.length} mesure(s) enregistrée(s) pour ce projet.
        </p>
        <div className="mt-4 flex gap-3">
          <Link
            href="/dashboards"
            className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-accent-foreground"
          >
            Voir les tableaux de bord
          </Link>
          <Link href="/" className="rounded-md border border-border px-4 py-2 text-sm font-medium">
            Nouveau témoignage
          </Link>
        </div>
      </div>
    );
  }

  const taxAxes = taxonomy!.classification_axes;

  return (
    <div className="space-y-8 pb-16">
      <div>
        <h1 className="text-xl font-semibold">Vérifiez la fiche</h1>
        <p className="mt-1 text-sm text-muted">
          Chaque case indique son origine. Corrigez ce qui doit l&apos;être, puis confirmez.
        </p>
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

      {/* Projet, période */}
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

      {/* Axe A */}
      <section className="rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">
            Domaine d&apos;intervention
          </h2>
          <OriginBadge origin="inferred" />
        </div>
        <div className="mt-3">
          <ChipMultiSelect
            options={taxAxes.area_of_opportunity.values}
            selected={areaOfOpportunity}
            onChange={setAreaOfOpportunity}
          />
        </div>
        {areaOfOpportunity.length === 0 && (
          <p className="mt-2 text-xs text-danger">Au moins un domaine est requis.</p>
        )}
      </section>

      {/* Axe B */}
      <section className="rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">Programme</h2>
          <OriginBadge origin="inferred" />
        </div>
        <p className="mt-1 text-xs text-muted">Laissez vide si le projet ne relève d&apos;aucun programme mondial.</p>
        <div className="mt-3">
          <ChipMultiSelect options={taxAxes.programme.values} selected={programme} onChange={setProgramme} />
        </div>
        {riseSelected && (
          <div className="mt-4 border-t border-border pt-3">
            <div className="flex items-center gap-2">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-muted">Piliers RISE</h3>
              <OriginBadge origin="inferred" />
            </div>
            <div className="mt-2">
              <ChipMultiSelect
                options={taxonomy!.rise_pillars.values}
                selected={risePillars}
                onChange={setRisePillars}
              />
            </div>
            {risePillars.length === 0 && (
              <p className="mt-2 text-xs text-danger">
                Au moins un pilier RISE est requis puisque RISE est coché.
              </p>
            )}
          </div>
        )}
      </section>

      {/* Axe C */}
      <section className="rounded-lg border border-border bg-surface p-4">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">
            Objectifs de développement durable
          </h2>
          <OriginBadge origin="inferred" />
        </div>
        <p className="mt-1 text-xs text-muted">Exactement un ODD principal.</p>
        <div className="mt-3 max-h-72 overflow-y-auto pr-1">
          <SdgSelector value={sdgs} onChange={setSdgs} />
        </div>
        {primaryCount !== 1 && (
          <p className="mt-2 text-xs text-danger">
            Exactement un ODD principal est requis (actuellement : {primaryCount}).
          </p>
        )}
      </section>

      {/* Chiffres */}
      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">Les chiffres</h2>
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
      </section>

      {/* Bloc à part : audience */}
      {audienceCandidates.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">
            Classé à part — non compté comme bénéficiaires
          </h2>
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
        </section>
      )}

      {/* Résultats mesurables (C4) */}
      <section className="rounded-lg border border-success/40 bg-success-bg p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-success">Résultats mesurables</h2>
        {hasOutcomeCandidate ? (
          <label className="mt-3 flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={confirmations.C4}
              onChange={(e) => setConfirmations((c) => ({ ...c, C4: e.target.checked }))}
            />
            Je confirme le(s) résultat(s) mesurable(s) ci-dessus (C4)
          </label>
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
              Aucun effet mesurable visé (C4)
            </label>
          </div>
        )}
      </section>

      {/* Confirmations C1-C3 */}
      <section className="rounded-lg border border-border bg-surface p-4 space-y-2 text-sm">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={confirmations.C1}
            onChange={(e) => setConfirmations((c) => ({ ...c, C1: e.target.checked }))}
          />
          Je confirme le mode de comptage de chaque chiffre ci-dessus (direct / indirect / audience) — C1
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={confirmations.C2}
            onChange={(e) => setConfirmations((c) => ({ ...c, C2: e.target.checked }))}
          />
          Je confirme, pour chaque chiffre, s&apos;il concerne des membres JCI ou du public externe — C2
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={confirmations.C3}
            onChange={(e) => setConfirmations((c) => ({ ...c, C3: e.target.checked }))}
          />
          Je confirme les ODD ci-dessus, avec exactement un objectif principal — C3
        </label>
      </section>

      <button
        onClick={handleConfirm}
        disabled={!canSubmit}
        className="rounded-md bg-accent px-5 py-2.5 text-sm font-medium text-accent-foreground disabled:opacity-40"
      >
        {submitting ? "Confirmation en cours…" : "Confirmer la fiche"}
      </button>
    </div>
  );
}
