-- Remise a zero des donnees de demo/test AVANT l'enregistrement final de la
-- video (2026-09-20). A coller tel quel dans l'editeur SQL de Supabase
-- (Project -> SQL Editor -> New query -> Run), comme pour migration_v0_3_0.sql.
--
-- Objectif : que le tableau de bord mondial parte de zero pile avant
-- l'enregistrement, pour que les compteurs "montent" visiblement pendant que
-- les projets de demo sont soumis en direct devant la camera.
--
-- NE SUPPRIME QUE ce que le pipeline de soumission produit (submissions,
-- extractions, projets, mesures, agregats, refus). NE TOUCHE PAS :
--   - organization / app_user           (comptes de demo + les 3 pays
--                                         fictifs de seed_demo_countries.py)
--   - taxonomy_release / geo_mapping    (referentiels)
--   - quality_issue                     (les 26 conflits documentaires du
--                                         VRAI rapport JCI 2025, pas des
--                                         donnees de test -- a NE JAMAIS
--                                         effacer, cf. section 26 de la
--                                         gouvernance produit)
--
-- A executer une seule fois, juste avant la prise definitive -- pas avant,
-- sinon il faudra le relancer si d'autres tests de soumission ont lieu
-- entre-temps. Reversible seulement au sens ou aucune de ces lignes n'a de
-- valeur hors demo : ce sont exactement les 8 projets T1-T8 + les anciens
-- projets de test des Phases 1-3, tous recreables en resoumettant les
-- memes textes.

TRUNCATE TABLE
    refusal,
    aggregate,
    measurement_version,
    measurement_parent,
    measurement_relation,
    derivation,
    measurement,
    project_sdg,
    project_activity_family,
    project_rise_pillar,
    project_programme,
    project_area_of_opportunity,
    project,
    extraction_candidate,
    submission
RESTART IDENTITY CASCADE;
