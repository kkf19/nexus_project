"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createSubmission, friendlyErrorMessage, retrySubmission } from "@/lib/api";
import { DEMO_ORGANIZATIONS, DEMO_USER_ID } from "@/lib/config";
import NexusMark from "@/components/NexusMark";

// Exemples cliquables (brief p. 4, "si le temps le permet") : uniquement du
// texte à préremplir dans la zone de saisie, jamais une donnée réelle --
// ils n'entrent dans aucun chiffre tant que la personne n'a pas envoyé.
const EXAMPLES = [
  "Le 15 mars, nous avons organisé une collecte de sang avec la Croix-Rouge locale. 60 personnes ont donné leur sang, 8 bénévoles JCI ont participé pendant 5 heures.",
  "Formation en leadership pour 30 jeunes professionnels sur 2 jours, animée par 4 formateurs bénévoles de notre OL.",
  "Distribution de kits scolaires à 120 enfants dans 3 écoles primaires, avec l'aide de 15 membres JCI mobilisés pendant une journée.",
];

// Étapes affichées pendant l'analyse (brief p. 4). Elles décrivent l'ordre
// réel du pipeline (extraction puis mapping taxonomie, cf. §21 du prompt
// produit) -- ce ne sont pas des pourcentages inventés : les 4 premières
// avancent à un rythme fixe pour donner un signe de vie pendant l'appel
// réseau, mais la dernière ("Vérification") reste active jusqu'à la vraie
// réponse de l'API, jamais marquée "terminée" avant qu'elle n'arrive.
const ANALYSIS_STEPS = [
  { label: "Lecture du texte", detail: "NEXUS lit votre activité, dans votre langue." },
  { label: "Repérage des activités", detail: "Ce qui a été fait, où et quand." },
  { label: "Domaines et ODD", detail: "Les domaines JCI concernés et les ODD touchés." },
  { label: "Chiffres et ressources", detail: "Participants, bénévoles, heures, résultats." },
  { label: "Vérification", detail: "Ce que vous devrez confirmer ou compléter." },
];

export default function Home() {
  const router = useRouter();
  const [text, setText] = useState("");
  // Simulation multi-pays pour la démo (pas d'écran de connexion, voir
  // lib/config.ts) : "en tant que quelle OL" est un simple choix explicite
  // sur cet écran, pas une identité connectée.
  const [organizationId, setOrganizationId] = useState(DEMO_ORGANIZATIONS[0].id);
  const [clientError, setClientError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  // Le texte reste dans `text` (jamais effacé en cas d'échec) : on ne
  // redemande jamais de ressaisir (dev-brief §3.1).
  const [failedSubmissionId, setFailedSubmissionId] = useState<string | null>(null);
  const [retrying, setRetrying] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  // Progression de l'écran "Analyse en cours…" -- purement locale à l'écran,
  // aucun lien avec un score ou un pourcentage renvoyé par l'API (il n'en
  // existe pas). Repart de 0 à chaque nouvelle tentative d'envoi.
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (!loading) return;
    setActiveStep(0);
    const lastStep = ANALYSIS_STEPS.length - 1;
    let step = 0;
    const id = setInterval(() => {
      step += 1;
      setActiveStep(Math.min(step, lastStep));
      if (step >= lastStep) clearInterval(id);
    }, 850);
    return () => clearInterval(id);
  }, [loading]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setServerError(null);
    if (!text.trim()) {
      // Texte vide : refus côté client (dev-brief §3.1), pas d'appel API.
      setClientError("Écrivez quelques lignes avant d'envoyer.");
      return;
    }
    setClientError(null);
    setLoading(true);
    try {
      const submission = await createSubmission({
        organization_id: organizationId,
        user_id: DEMO_USER_ID,
        raw_text: text,
      });
      if (submission.pipeline_status === "failed") {
        setFailedSubmissionId(submission.submission_id);
        return;
      }
      // "awaiting_confirmation", ou tout autre statut : la fiche de
      // confirmation gère elle-même l'attente le cas échéant.
      router.push(`/submissions/${submission.submission_id}/confirm`);
    } catch (err) {
      setServerError(friendlyErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleRetry() {
    if (!failedSubmissionId) return;
    setRetrying(true);
    setServerError(null);
    try {
      const submission = await retrySubmission(failedSubmissionId);
      if (submission.pipeline_status === "failed") {
        setFailedSubmissionId(submission.submission_id);
        return;
      }
      router.push(`/submissions/${submission.submission_id}/confirm`);
    } catch (err) {
      setServerError(friendlyErrorMessage(err));
    } finally {
      setRetrying(false);
    }
  }

  if (failedSubmissionId) {
    return (
      <div className="mx-auto max-w-xl">
        <div className="rounded-lg border border-warning/40 bg-warning-bg p-6">
          <h1 className="text-lg font-semibold text-warning">Analyse impossible</h1>
          <p className="mt-2 text-sm text-foreground">
            Votre texte est conservé, rien n&apos;est perdu. Vous pouvez relancer l&apos;analyse
            maintenant, ou revenir plus tard — inutile de le ressaisir.
          </p>
          <div className="mt-4 rounded-md border border-border bg-surface p-3 text-sm text-muted">
            {text}
          </div>
          {serverError && <p className="mt-3 text-sm text-danger">{serverError}</p>}
          <div className="mt-4 flex gap-3">
            <button
              onClick={handleRetry}
              disabled={retrying}
              className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-accent-foreground disabled:opacity-50"
            >
              {retrying ? "Relance en cours…" : "Relancer l'analyse"}
            </button>
            <button
              onClick={() => setFailedSubmissionId(null)}
              className="rounded-md border border-border px-4 py-2 text-sm font-medium"
            >
              Revenir au texte
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return <AnalyzingScreen text={text} activeStep={activeStep} />;
  }

  return (
    <div className="mx-auto max-w-xl">
      <h1 className="nexus-hero-figure text-3xl sm:text-4xl">Racontez votre activité</h1>
      <p className="mt-3 text-sm text-muted">
        Comme à un collègue, dans votre langue. Pas de formulaire à remplir : NEXUS s&apos;occupe
        de comprendre ce que vous avez écrit.
      </p>
      <form onSubmit={handleSubmit} className="mt-8">
        <label className="nexus-label mb-2 block">Vous soumettez en tant que (démo)</label>
        <select
          value={organizationId}
          onChange={(e) => setOrganizationId(e.target.value)}
          className="nexus-focus-halo mb-4 w-full rounded-md border border-border bg-surface px-3 py-2 text-sm transition-colors"
        >
          {DEMO_ORGANIZATIONS.map((org) => (
            <option key={org.id} value={org.id}>
              {org.label}
            </option>
          ))}
        </select>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={10}
          placeholder="Par exemple : Du 3 au 5 septembre, on a organisé un bootcamp entrepreneuriat à Bouaké. 45 jeunes ont suivi les trois jours complets…"
          className="nexus-focus-halo w-full resize-y rounded-lg border border-border bg-surface p-4 text-sm leading-6 outline-none transition-all"
        />

        <div className="mt-3 flex flex-wrap gap-2">
          <span className="nexus-label self-center pr-1">Exemples :</span>
          {EXAMPLES.map((example, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setText(example)}
              className="rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted transition-colors hover:border-accent/40 hover:text-foreground"
            >
              Exemple {i + 1}
            </button>
          ))}
        </div>

        {clientError && <p className="mt-3 text-sm text-danger">{clientError}</p>}
        {serverError && <p className="mt-3 text-sm text-danger">{serverError}</p>}
        <button
          type="submit"
          disabled={loading}
          className="mt-5 rounded-md bg-accent px-5 py-2.5 text-sm font-medium text-accent-foreground transition-colors hover:bg-accent-hover disabled:opacity-50"
        >
          Envoyer
        </button>
      </form>
    </div>
  );
}

// Moment signature de la démo (brief p. 4) : pendant l'appel réseau réel
// (extraction + mapping taxonomie), on ne montre jamais un simple spinner.
// Le texte soumis reste lisible, parcouru par un balayage lumineux ; une
// liste d'étapes avance à un rythme fixe, sauf la dernière qui reste active
// jusqu'à la vraie réponse -- honnête, aucun faux pourcentage.
function AnalyzingScreen({ text, activeStep }: { text: string; activeStep: number }) {
  const lastStep = ANALYSIS_STEPS.length - 1;
  return (
    <div className="mx-auto max-w-3xl">
      <div className="grid gap-6 lg:grid-cols-[1.1fr_1fr] lg:items-start">
        <div>
          <div className="nexus-scan-box rounded-lg border border-border bg-surface p-4">
            <p className="max-h-64 overflow-hidden whitespace-pre-wrap text-sm leading-6 text-muted">
              {text}
            </p>
          </div>

          <div className="mt-8 flex flex-col items-center">
            <div className="flex flex-col items-center gap-1 text-muted-2">
              {[0, 1, 2].map((i) => (
                <span key={i} className="h-3 w-px bg-border-strong" />
              ))}
            </div>
            <div className="nexus-glow-bar mt-1 flex items-center gap-2 rounded-full bg-accent-deep px-5 py-2.5 text-accent">
              <NexusMark size={16} />
              <span className="nexus-label text-accent">NEXUS</span>
            </div>
            <DotField />
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-4">
          <p className="nexus-label">Ce que NEXUS cherche</p>
          <ul className="mt-4 space-y-4">
            {ANALYSIS_STEPS.map((step, i) => {
              const isDone = i < activeStep;
              const isActive = i === activeStep;
              return (
                <li key={step.label} className="flex items-start gap-3">
                  <span
                    className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[10px] ${
                      isDone
                        ? "border-accent/40 bg-accent/15 text-accent"
                        : isActive
                        ? "nexus-step-active border-accent/50 bg-accent/10 text-accent"
                        : "border-border text-muted-2"
                    }`}
                  >
                    {isDone ? "✓" : i + 1}
                  </span>
                  <div>
                    <p className={`text-sm font-medium ${isDone || isActive ? "text-foreground" : "text-muted-2"}`}>
                      {step.label}
                      {isActive && i === lastStep && (
                        <span className="ml-2 text-xs font-normal text-muted">en cours…</span>
                      )}
                    </p>
                    <p className="text-xs text-muted">{step.detail}</p>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </div>
  );
}

// Nuage de points épars, deux d'entre eux animés -- motif de marque du
// brief (§ "réseau de points reliés"), purement décoratif.
function DotField() {
  const dots = [
    [8, 8], [28, 4], [48, 10], [68, 4], [88, 8],
    [4, 24], [24, 26], [44, 22], [64, 26], [84, 24],
    [14, 40], [36, 38], [58, 40], [80, 38],
  ];
  const litIndices = new Set([2, 9]);
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 96 48"
      className="nexus-network-bg relative mt-1 h-16 w-40"
      style={{ position: "static", opacity: 1, mixBlendMode: "normal" }}
    >
      {dots.map(([x, y], i) => (
        <circle
          key={i}
          cx={x}
          cy={y}
          r={litIndices.has(i) ? 2 : 1.1}
          fill={litIndices.has(i) ? "var(--accent)" : "var(--border-strong)"}
          className={litIndices.has(i) ? "nexus-dot-pulse" : ""}
        />
      ))}
    </svg>
  );
}
