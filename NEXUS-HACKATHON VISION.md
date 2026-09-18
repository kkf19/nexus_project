# NEXUS

### Fiche Vision du Projet — Hackathon d'innovation JCI 2026

Piste : Tableau de bord des données d'impact JCI Statut du document : en cours de construction, mis à jour au fil des décisions Dernière mise à jour : 18 septembre 2026

## 1\. Le problème tel qu'énoncé par JCI

JCI (Junior Chamber International) est un réseau mondial présent dans plus de 100 pays, organisé en organisations locales (OL) — des centaines, voire des milliers à travers le monde. Chaque OL organise ses propres activités sur le terrain toute l'année.  
JCI, au niveau mondial, formule le problème ainsi :  
« On a du mal à présenter notre impact global à nos sponsors et investisseurs. »

## 2\. La mauvaise lecture (celle que la plupart des équipes vont faire)

À première lecture, la conclusion évidente est : *« il manque un dashboard, il faut agréger les chiffres et les afficher joliment sur une carte du monde. »* C'est ce que la majorité des équipes en compétition vont construire — un pari risqué, car ça suppose que la donnée à afficher existe déjà sous une forme exploitable.

## 3\. Le vrai problème — en 4 niveaux

### 3.1 — Premier niveau : un problème de captation, pas d'affichage

Les données d'impact n'existent pas sous une forme exploitable. Elles existent sous forme de rapports texte libre (Word/PDF), rédigés différemment par chaque OL, sans structure commune, avec des chiffres parfois noyés dans une phrase, parfois absents.  
Exemple illustratif : JCI Cotonou organise une collecte de sang (80 donneurs, 15 membres mobilisés) → rapport narratif libre. JCI Comé fait une formation entrepreneuriat (25 jeunes formés) → rapport dans un style totalement différent. Résultat : impossible pour le board mondial de répondre à une question simple comme *« combien de personnes JCI a-t-elle touchées cette année ? »*

### 3.2 — Deuxième niveau : un problème de sens, pas seulement de structure

Même une fois les rapports structurés, un problème plus profond demeure : des chiffres structurés ne sont pas automatiquement comparables entre eux.  
Quatre OL décrivant la même activité d'entrepreneuriat, formulée différemment :

* OL A : *« bootcamp de 3 jours pour 45 jeunes, 12 ont créé leur entreprise »*  
* OL B : *« formation de 50 jeunes entrepreneurs, 8 nouvelles entreprises lancées »*  
* OL C : *« entrepreneurship workshop — 60 attendees — 15 businesses supported »*  
* OL D : *« une trentaine de jeunes accompagnés pendant deux mois »*

Additionner naïvement ces chiffres produit un total qui a l'air propre mais qui est trompeur : « attendees » \= « participants » ? « businesses supported » \= « businesses launched » ? Une même personne comptée deux fois ?  
Un système naïf additionne des mots qui se ressemblent. Un système fiable comprend d'abord ce que chaque mot signifie, avant de décider s'il peut être additionné.

### 3.3 — Troisième niveau : un problème de finalité — output vs impact réel

L'énoncé JCI parle de présenter l'impact, pas ce qui a été fait. Distinction essentielle :

| Niveau | Exemple | Ce que ça dit |
| :---- | :---- | :---- |
| Activité | JCI Comé organise une plantation d'arbres | Ce qui a été fait |
| Output | 80 plants mis en terre | Un chiffre d'effort |
| Outcome | 80 plants encore vivants 6 mois après | Un résultat vérifiable |
| Impact | Hectares reboisés, CO2 séquestré à terme | Le changement réel dans le monde |

Compter des outputs et appeler ça un « dashboard d'impact » est le piège dans lequel la majorité des équipes vont tomber.  
Décision retenue : on capture rigoureusement les outputs (et outcomes quand ils sont mentionnés), on ne prétend pas mesurer un impact long terme impossible à observer en 48h — mais le modèle de données distingue explicitement ces niveaux, pour ne jamais confondre un effort avec un résultat.

### 3.4 — Quatrième niveau : ce que sponsors et investisseurs veulent réellement voir

Un sponsor ne cherche pas juste à savoir « combien JCI a fait de projets ». Il déroule un raisonnement en plusieurs questions : *Est-ce pertinent pour mes priorités ? JCI opère-t-elle à l'échelle ? Est-ce que ça marche vraiment ? Puis-je croire ces chiffres ? Qu'est-ce que mon argent spécifiquement permettrait ?*  
La question la plus critique, souvent négligée, est la crédibilité : peut-on remonter d'un chiffre agrégé mondial jusqu'à l'activité précise, dans l'OL précise, qui l'a produit ? C'est cette traçabilité (data lineage) qui transforme un dashboard décoratif en instrument de confiance.

## 4\. Conclusion — ce qu'on construit réellement

On ne construit pas un outil de visualisation en premier lieu. On construit une infrastructure de transformation de la donnée — de rapports locaux hétérogènes vers une donnée standardisée, traçable et agrégeable.  
Le dashboard est la surface visible ; le vrai produit est la couche qui le rend digne de confiance.

## 5\. Nom du projet

NEXUS

## 6\. Chaîne de valeur cible

Activité terminée par une OL  
        ↓  
Rapport saisi (texte libre ou semi-structuré)  
        ↓  
\[1\] EXTRACTION SÉMANTIQUE (IA — réelle)  
        ↓  
\[2\] MAPPING VERS TAXONOMIE JCI (IA — réelle)  
        ↓  
\[3\] NORMALISATION \+ VALIDATION (simplifiée pour le MVP)  
        ↓  
Donnée JCI structurée ("Measurement Object")  
        ↓  
Statut de revue (déclarée → validée / signalée)  
        ↓  
Agrégation  
        ↓  
Dashboards (par OL / national / mondial)

## 7\. Rôles et accès

| Rôle | Qui | Peut faire |
| :---- | :---- | :---- |
| Admin OL | Secrétaire Général (SG) et Président de l'OL — les deux ont accès admin | Saisir les activités de leur OL, voir leur propre dashboard |
| Admin National | La nationale JCI du pays | Voir les déclarations de toutes les OL du pays, les valider ou les signaler, voir le dashboard national |
|  |  |  |
| Board mondial | JCI monde | Voir le dashboard agrégé mondial |

## 8\. Modalités de saisie

* La saisie se fait après que l'activité a eu lieu (pas de saisie en temps réel pendant l'activité)  
* Les activités sont saisies une par une, même si plusieurs sont saisies dans la même session  
* Le format d'entrée est du texte (saisi ou collé), proche du langage naturel de l'OL — pas de PDF pour le MVP (source d'échec en démo, hors du chemin critique de la valeur démontrée)  
* C'est le pipeline d'extraction qui absorbe l'hétérogénéité, pas un formulaire rigide à 50 champs

## 9\. Mécanisme de confiance (le « gendarme »)

Pas d'audit terrain lourd (irréaliste à l'échelle de centaines d'OL). À la place : responsabilisation par la visibilité.  
Statuts d'une déclaration :

* Déclarée — saisie par l'OL, entre immédiatement dans les agrégats provisoires  
* Validée — la nationale a jeté un œil, cohérence plausible confirmée  
* Signalée — la nationale identifie une incohérence manifeste et demande une précision

Principe : ce n'est pas le contrôle en lui-même qui change le comportement, c'est le fait que l'OL sache qu'on regarde. Bonus : ça donne à la nationale un vrai outil de gouvernance qu'elle n'a pas aujourd'hui.

## 10\. Dashboards

Un seul moteur d'agrégation, décliné en trois vues filtrées :

* Vue OL — progression de sa propre organisation (levier d'adoption)  
* Vue Nationale — toutes les OL d'un pays, statuts de validation  
* Vue Mondiale — agrégat global (la cible principale de l'énoncé JCI, destinée au board mondial)

Principe de sécurité pour l'agrégation : le système doit parfois refuser d'agréger. « 100 reached » \+ « 100 trained » ne devient pas automatiquement « 200 impactés » si les deux métriques ne désignent pas la même chose. Mieux vaut afficher deux chiffres distincts et corrects qu'un total flatteur mais faux.

## 11\. Le pipeline sémantique (cœur du produit) — retenu pour le MVP hackathon

Décision : un vrai pipeline IA, limité aux 2 étapes qui démontrent la proposition de valeur. Le reste est simplifié mais architecturalement prévu.

| Étape | Statut MVP | Rôle |
| :---- | :---- | :---- |
| Extraction | RÉEL (appel LLM) | Lit un rapport en texte libre, en sort du JSON structuré (activité, participants, durée, résultats mentionnés...) |
| Mapping taxonomie JCI | RÉEL (appel LLM) | Mappe le vocabulaire local hétérogène vers un vocabulaire canonique JCI (Domaine → Type d'activité → Groupe cible → Métrique) |
| Normalisation d'unités | Simplifiée | Règles simples |
| Validation | Simplifiée | Détection basique de champs manquants ou valeurs suspectes |
| Déduplication | Simplifiée / mock | Non prioritaire pour la démo |
| Provenance | Réelle mais simple | Chaque donnée standardisée garde un lien vers le rapport source d'origine |

Pourquoi ce choix et pas un pipeline complet, ni un pipeline simulé :

* Un pipeline complet (entity resolution avancée, scoring de confiance sophistiqué, workflow multi-niveaux) prendrait trop de temps pour 48h et diluerait la démo  
* Un pipeline entièrement codé en dur (if/else) serait vulnérable à la question évidente d'un jury technique : *« et si le rapport dit autre chose ? »* — ça viderait la proposition de valeur de son sens

La démo qui doit convaincre : montrer deux rapports formulés de façon complètement différente, en direct, et prouver que le système les fait converger vers le même concept JCI standardisé — donc agrégeables ensemble.

## 14\. Stratégie de robustesse face aux consignes encore inconnues

Les consignes officielles du hackathon (types de données à insérer, format exact attendu) ne sont pas encore publiées — elles seront communiquées le vendredi 18 septembre à partir de 17h GMT.  
Ce qui tient, peu importe les consignes reçues : l'architecture en couches (données hétérogènes → transformation sémantique → donnée standardisée → agrégation) n'est pas dépendante d'un format précis. Le Measurement Object est pensé comme un contenant générique, pas un schéma figé.  
Risques identifiés :

* Le format d'entrée réel imposé peut différer de notre hypothèse (texte libre) — ex: dataset déjà structuré fourni  
* La taxonomie imposée par l'organisateur peut différer de celle de JCI qu'on a adoptée  
* Le temps de réaction est court une fois les consignes connues (hackathon démarre immédiatement après)

Mesures de robustesse retenues :

1. Le module d'extraction est isolé et remplaçable — si les données arrivent déjà structurées, on saute directement au mapping taxonomie  
2. La taxonomie est configurable (référentiel externe), pas codée en dur — remplaçable en quelques minutes si nécessaire  
3. Un créneau de triage est prévu dès réception des consignes (30-45 min) pour comparer aux hypothèses actuelles et n'ajuster que ce qui doit l'être  
4. Le scénario de démo (5 cas de test) reste indépendant du jeu de données officiel final — il prouve le concept quel que soit le contexte

---

## 15\. Livrables attendus pour la soumission

D'après le Q\&A de la page de présentation du hackathon :

* Une page de projet (problématique \+ description de la solution)  
* Un dépôt GitHub public  
* Une courte vidéo de présentation  
* Un diaporama

*Les exigences précises (format, durée, template) seront détaillées sur une page de soumission pas encore publiée.*

## 17\. Points encore ouverts

*  Intégrer les résultats de l'extraction du JCI Impact Report 2025 (vocabulaire, taxonomie fine, cas de test)  
*  Confirmer le noyau exact du schéma d'extraction (le "Measurement Object" appliqué concrètement)  
*  Choix du modèle LLM et méthode d'intégration (API, prompts d'extraction et de mapping)  
*  Stack technique définitive (proposition initiale : Node/Express \+ SQLite, React \+ Leaflet \+ Recharts — à revalider à la lumière du pipeline IA)  
*  Scénario précis de démo (les cas-exemples à préparer à l'avance)  
*  Attente des consignes officielles de l'hackathon (vendredi 18 septembre, 17h GMT)  
*  Exigences précises de soumission (page projet, vidéo, diaporama) — page de soumission pas encore publiée

---

*Document de travail — NEXUS, équipe hackathon JCI Innovation 2026*  
