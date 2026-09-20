-- Cree/complete les organisations fictives multi-pays pour la video de demo
-- (2026-09-20), SANS toucher a l'authentification (toujours DEMO-USER, D-04
-- inchangee). A coller tel quel dans l'editeur SQL de Supabase (Project ->
-- SQL Editor -> New query -> Run), comme pour migration_v0_3_0.sql --
-- equivalent SQL de seed_demo_countries.py, au cas ou executer le script
-- Python directement (nécessite DATABASE_URL en local) est moins pratique.
--
-- Ne cree AUCUN projet ni mesure -- seulement 6 lignes `organization`
-- (metadata) : sans effet sur les totaux du tableau de bord. Peut etre
-- lance a tout moment, y compris bien avant l'enregistrement (contrairement
-- a reset_demo_data.sql, a executer juste avant la prise finale).
--
-- Idempotent : peut etre relance sans risque (upsert par organization_id).
-- Complete aussi DEMO-OL (nom, pays, parent national) si elle existe deja
-- sans ces champs -- c'est ce qui rendait la vue "Nationale" vide pour ce
-- compte.

-- 1) Organisations nationales (doivent exister avant les OL locales, FK).
INSERT INTO organization (organization_id, org_type, name, parent_organization_id, country_iso2)
VALUES
  ('NAT-BJ', 'national', 'JCI Benin', NULL, 'BJ'),
  ('NAT-CA', 'national', 'JCI Canada', NULL, 'CA'),
  ('NAT-FR', 'national', 'JCI France', NULL, 'FR')
ON CONFLICT (organization_id) DO UPDATE SET
  name = EXCLUDED.name,
  country_iso2 = EXCLUDED.country_iso2;

-- 2) OL locales, une par pays (DEMO-OL existe deja -- on la complete plutot
-- que la recreer, pour ne pas perdre son historique de soumissions).
INSERT INTO organization (organization_id, org_type, name, parent_organization_id, country_iso2)
VALUES
  ('DEMO-OL', 'local', 'JCI Cotonou Etoile', 'NAT-BJ', 'BJ'),
  ('LOC-CA', 'local', 'JCI Montreal', 'NAT-CA', 'CA'),
  ('LOC-FR', 'local', 'JCE de Paris', 'NAT-FR', 'FR')
ON CONFLICT (organization_id) DO UPDATE SET
  name = EXCLUDED.name,
  parent_organization_id = EXCLUDED.parent_organization_id,
  country_iso2 = EXCLUDED.country_iso2;
