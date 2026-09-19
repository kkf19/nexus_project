// Compte de démo unique pour le MVP (pas d'écran de connexion — décision du
// 2026-09-19 : un seul compte DEMO-OL pour le hackathon, un vrai système de
// comptes pourra être ajouté plus tard si le temps le permet).
export const DEMO_ORGANIZATION_ID = "DEMO-OL";
export const DEMO_USER_ID = "DEMO-USER";

// URL de base de l'API backend (Render). Définie via la variable
// d'environnement NEXT_PUBLIC_API_BASE_URL sur Vercel ; repli sur le lien de
// démo connu en local si elle est absente.
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
  "https://nexus-project-w4ux.onrender.com";
