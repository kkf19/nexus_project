// Les 17 Objectifs de Développement Durable (ONU) : liste fixe et
// universelle, indépendante de la taxonomie NEXUS (docs/technical/
// taxonomy.config.json ne fournit pas de libellé par ODD — seulement les
// métadonnées de l'axe C). Ce n'est pas une donnée métier NEXUS à charger
// dynamiquement, c'est un standard externe qui ne change pas.
export const SDG_LABELS: Record<number, string> = {
  1: "Pas de pauvreté",
  2: "Faim « zéro »",
  3: "Bonne santé et bien-être",
  4: "Éducation de qualité",
  5: "Égalité entre les sexes",
  6: "Eau propre et assainissement",
  7: "Énergie propre et d'un coût abordable",
  8: "Travail décent et croissance économique",
  9: "Industrie, innovation et infrastructure",
  10: "Inégalités réduites",
  11: "Villes et communautés durables",
  12: "Consommation et production responsables",
  13: "Mesures relatives à la lutte contre les changements climatiques",
  14: "Vie aquatique",
  15: "Vie terrestre",
  16: "Paix, justice et institutions efficaces",
  17: "Partenariats pour la réalisation des objectifs",
};

export const SDG_GOALS = Object.keys(SDG_LABELS).map(Number);
