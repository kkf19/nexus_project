// Simulation multi-pays pour la vidéo de démo (2026-09-20), SANS écran de
// connexion (décision du 2026-09-19 conservée à l'identique : toujours un
// seul compte utilisateur DEMO-USER, jamais d'auth). Plutôt que de rouvrir
// l'authentification à quelques heures de la deadline, on simule la
// diversité d'OL au niveau des DONNÉES seulement : plusieurs organisations
// locales fictives, chacune rattachée à une organisation nationale fictive
// (backend/scripts/seed_demo_countries.py), sélectionnables via un simple
// menu déroulant sur l'écran de saisie et sur le tableau de bord. Aucune
// notion de session/identité : n'importe qui peut soumettre "en tant que"
// n'importe laquelle de ces OL, exactement comme avant avec DEMO-OL seule.
export type DemoOrganization = {
  id: string; // organization_id de l'OL locale (soumissions + vue "Mon OL")
  label: string;
  nationalId: string; // organization_id du parent national (vue "Nationale")
  nationalLabel: string;
};

export const DEMO_ORGANIZATIONS: DemoOrganization[] = [
  { id: "DEMO-OL", label: "JCI Cotonou Étoile (Bénin)", nationalId: "NAT-BJ", nationalLabel: "JCI Bénin" },
  { id: "LOC-CA", label: "JCI Montréal (Canada)", nationalId: "NAT-CA", nationalLabel: "JCI Canada" },
  { id: "LOC-FR", label: "JCE de Paris (France)", nationalId: "NAT-FR", nationalLabel: "JCI France" },
];

// Conservés pour compat (compte utilisateur unique, et OL par défaut quand
// aucune sélection explicite n'est faite).
export const DEMO_ORGANIZATION_ID = DEMO_ORGANIZATIONS[0].id;
export const DEMO_USER_ID = "DEMO-USER";

// URL de base de l'API backend (Render). Définie via la variable
// d'environnement NEXT_PUBLIC_API_BASE_URL sur Vercel ; repli sur le lien de
// démo connu en local si elle est absente.
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
  "https://nexus-project-w4ux.onrender.com";
