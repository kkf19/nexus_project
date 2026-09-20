"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createSubmission, friendlyErrorMessage, retrySubmission } from "@/lib/api";
import { DEMO_ORGANIZATIONS, DEMO_USER_ID } from "@/lib/config";

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

  return (
    <div className="mx-auto max-w-xl">
      <h1 className="text-xl font-semibold">Racontez votre activité</h1>
      <p className="mt-1 text-sm text-muted">
        Comme à un collègue, dans votre langue. Pas de formulaire à remplir : NEXUS s&apos;occupe
        de comprendre ce que vous avez écrit.
      </p>
      <form onSubmit={handleSubmit} className="mt-6">
        <label className="mb-1 block text-xs font-medium text-muted">
          Vous soumettez en tant que (démo)
        </label>
        <select
          value={organizationId}
          onChange={(e) => setOrganizationId(e.target.value)}
          className="mb-3 w-full rounded-md border border-border bg-surface px-2 py-1.5 text-sm"
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
          className="w-full resize-y rounded-md border border-border bg-surface p-3 text-sm leading-6 outline-none focus:border-accent"
        />
        {clientError && <p className="mt-2 text-sm text-danger">{clientError}</p>}
        {serverError && <p className="mt-2 text-sm text-danger">{serverError}</p>}
        <button
          type="submit"
          disabled={loading}
          className="mt-4 rounded-md bg-accent px-5 py-2.5 text-sm font-medium text-accent-foreground disabled:opacity-50"
        >
          {loading ? "Analyse en cours…" : "Envoyer"}
        </button>
      </form>
    </div>
  );
}
