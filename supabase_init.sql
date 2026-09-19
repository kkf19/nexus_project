-- NEXUS -- schema genere depuis backend/app/models.py (dev-brief.md section 2)
-- Ne pas editer a la main : regenerer avec backend/scripts/export_schema_sql.py

CREATE TABLE geo_mapping (
	country_iso2 TEXT NOT NULL, 
	mapping_version TEXT NOT NULL, 
	geographic_area TEXT NOT NULL, 
	confidence TEXT NOT NULL, 
	note TEXT, 
	PRIMARY KEY (country_iso2, mapping_version)
);

CREATE TABLE measurement_parent (
	id SERIAL NOT NULL, 
	measurement_id TEXT NOT NULL, 
	parent_measurement_id TEXT NOT NULL, 
	position INTEGER NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE organization (
	organization_id TEXT NOT NULL, 
	org_type TEXT NOT NULL, 
	name TEXT NOT NULL, 
	parent_organization_id TEXT, 
	country_iso2 TEXT, 
	PRIMARY KEY (organization_id), 
	FOREIGN KEY(parent_organization_id) REFERENCES organization (organization_id)
);

CREATE TABLE quality_issue (
	issue_id TEXT NOT NULL, 
	kind TEXT NOT NULL, 
	subject TEXT, 
	values JSON NOT NULL, 
	resolution_status TEXT NOT NULL, 
	displayed BOOLEAN NOT NULL, 
	PRIMARY KEY (issue_id)
);

CREATE TABLE taxonomy_release (
	version TEXT NOT NULL, 
	content JSON NOT NULL, 
	checksum TEXT NOT NULL, 
	loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	PRIMARY KEY (version)
);

CREATE TABLE app_user (
	user_id TEXT NOT NULL, 
	organization_id TEXT, 
	role TEXT NOT NULL, 
	PRIMARY KEY (user_id), 
	FOREIGN KEY(organization_id) REFERENCES organization (organization_id)
);

CREATE TABLE submission (
	submission_id TEXT NOT NULL, 
	organization_id TEXT NOT NULL, 
	user_id TEXT NOT NULL, 
	raw_text TEXT NOT NULL, 
	raw_text_sha256 TEXT NOT NULL, 
	language TEXT, 
	submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	pipeline_status TEXT NOT NULL, 
	pipeline_error TEXT, 
	PRIMARY KEY (submission_id), 
	FOREIGN KEY(organization_id) REFERENCES organization (organization_id), 
	FOREIGN KEY(user_id) REFERENCES app_user (user_id)
);

CREATE TABLE extraction_candidate (
	candidate_id TEXT NOT NULL, 
	submission_id TEXT NOT NULL, 
	stage TEXT NOT NULL, 
	payload JSON NOT NULL, 
	model_id TEXT NOT NULL, 
	validation_errors JSON, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (candidate_id), 
	FOREIGN KEY(submission_id) REFERENCES submission (submission_id)
);

CREATE TABLE project (
	project_id TEXT NOT NULL, 
	submission_id TEXT NOT NULL, 
	organization_id TEXT NOT NULL, 
	name TEXT, 
	reporting_year INTEGER NOT NULL, 
	period_start TEXT, 
	period_end TEXT, 
	outcome_status TEXT NOT NULL, 
	expected_outcome TEXT, 
	follow_up_date DATE, 
	programme_confirmed BOOLEAN NOT NULL, 
	taxonomy_version TEXT NOT NULL, 
	confirmed_by TEXT, 
	confirmed_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (project_id), 
	FOREIGN KEY(submission_id) REFERENCES submission (submission_id), 
	FOREIGN KEY(organization_id) REFERENCES organization (organization_id), 
	FOREIGN KEY(taxonomy_version) REFERENCES taxonomy_release (version)
);

CREATE TABLE measurement (
	measurement_id TEXT NOT NULL, 
	standard TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	submission_id TEXT, 
	project_id TEXT, 
	organization_id TEXT, 
	taxonomy_version TEXT, 
	metric_code TEXT NOT NULL, 
	metric_label_source TEXT NOT NULL, 
	definition_status TEXT, 
	definition_text TEXT, 
	definition_layer TEXT, 
	definition_source_ref TEXT, 
	iaooi_value TEXT, 
	iaooi_layer TEXT, 
	iaooi_standard TEXT, 
	iaooi_rule_id TEXT, 
	iaooi_confidence TEXT, 
	source_wording_class TEXT, 
	taxonomy_refs JSON, 
	value NUMERIC, 
	value_status TEXT, 
	value_qualifier TEXT, 
	value_range JSON, 
	unit_code TEXT, 
	unit_dimension TEXT, 
	unit_currency_code TEXT, 
	unit_sub_code TEXT, 
	unit_normalization JSON, 
	formula TEXT, 
	inputs JSON, 
	method TEXT, 
	assumptions TEXT, 
	conflicting_values JSON, 
	subject_type TEXT, 
	subject_id TEXT, 
	subject_name TEXT, 
	pop_internal_external TEXT, 
	pop_count_type TEXT, 
	pop_dedup_basis TEXT, 
	pop_target_group JSON, 
	pop_base_population JSON, 
	pop_attributes JSON, 
	period_type TEXT, 
	period_start TEXT, 
	period_end TEXT, 
	period_reporting_year INTEGER, 
	geography JSON, 
	layer TEXT NOT NULL, 
	source_origin TEXT, 
	source_document_id TEXT, 
	source_page TEXT, 
	source_section TEXT, 
	source_quote TEXT, 
	source_submitted_at TEXT, 
	source_language TEXT, 
	source_span JSON, 
	confidence TEXT, 
	verification_status TEXT NOT NULL, 
	evidence_refs JSON, 
	checks_passed JSON, 
	checks_failed JSON, 
	dq_refs JSON, 
	flag JSON, 
	validated_by TEXT, 
	validated_at TIMESTAMP WITH TIME ZONE, 
	agg_equivalence_key TEXT, 
	agg_aggregable TEXT, 
	agg_refusal_reason TEXT, 
	agg_dedup_key TEXT, 
	agg_suspected_duplicate_of JSON, 
	agg_coverage JSON, 
	PRIMARY KEY (measurement_id), 
	FOREIGN KEY(submission_id) REFERENCES submission (submission_id), 
	FOREIGN KEY(project_id) REFERENCES project (project_id), 
	FOREIGN KEY(organization_id) REFERENCES organization (organization_id), 
	FOREIGN KEY(taxonomy_version) REFERENCES taxonomy_release (version)
);

CREATE INDEX ix_measurement_metric_code ON measurement (metric_code);
CREATE INDEX ix_measurement_project_id ON measurement (project_id);
CREATE INDEX ix_measurement_verification_status ON measurement (verification_status);
CREATE INDEX ix_measurement_equivalence_key ON measurement (agg_equivalence_key);
CREATE INDEX ix_measurement_org_year ON measurement (organization_id, period_reporting_year);

CREATE TABLE project_area_of_opportunity (
	id SERIAL NOT NULL, 
	project_id TEXT NOT NULL, 
	code TEXT NOT NULL, 
	layer TEXT NOT NULL, 
	rule_id TEXT, 
	confidence TEXT, 
	proposed_by TEXT, 
	confirmed_by TEXT, 
	confirmed_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES project (project_id)
);

CREATE TABLE project_programme (
	id SERIAL NOT NULL, 
	project_id TEXT NOT NULL, 
	code TEXT NOT NULL, 
	layer TEXT NOT NULL, 
	rule_id TEXT, 
	confidence TEXT, 
	proposed_by TEXT, 
	confirmed_by TEXT, 
	confirmed_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES project (project_id)
);

CREATE TABLE project_rise_pillar (
	id SERIAL NOT NULL, 
	project_id TEXT NOT NULL, 
	code TEXT NOT NULL, 
	layer TEXT NOT NULL, 
	rule_id TEXT, 
	confidence TEXT, 
	proposed_by TEXT, 
	confirmed_by TEXT, 
	confirmed_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES project (project_id)
);

CREATE TABLE project_sdg (
	id SERIAL NOT NULL, 
	project_id TEXT NOT NULL, 
	goal INTEGER NOT NULL, 
	role TEXT NOT NULL, 
	layer TEXT NOT NULL, 
	rule_id TEXT, 
	confidence TEXT, 
	proposed_by TEXT, 
	confirmed_by TEXT, 
	confirmed_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES project (project_id)
);

CREATE TABLE aggregate (
	aggregate_run_id TEXT NOT NULL, 
	measurement_id TEXT NOT NULL, 
	view TEXT NOT NULL, 
	scope_organization_id TEXT, 
	group_by TEXT NOT NULL, 
	group_label TEXT, 
	filters JSON, 
	engine_version TEXT, 
	computed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (aggregate_run_id), 
	FOREIGN KEY(measurement_id) REFERENCES measurement (measurement_id)
);

CREATE TABLE derivation (
	id SERIAL NOT NULL, 
	measurement_id TEXT NOT NULL, 
	position INTEGER NOT NULL, 
	step TEXT NOT NULL, 
	rule_id TEXT, 
	agent TEXT, 
	input_refs JSON, 
	confidence TEXT, 
	timestamp TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(measurement_id) REFERENCES measurement (measurement_id)
);

CREATE TABLE measurement_relation (
	id SERIAL NOT NULL, 
	measurement_id TEXT NOT NULL, 
	relation_type TEXT NOT NULL, 
	target_measurement_id TEXT NOT NULL, 
	note TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(measurement_id) REFERENCES measurement (measurement_id)
);

CREATE TABLE measurement_version (
	id SERIAL NOT NULL, 
	measurement_id TEXT NOT NULL, 
	version_no INTEGER NOT NULL, 
	snapshot JSON NOT NULL, 
	changed_by TEXT, 
	changed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(measurement_id) REFERENCES measurement (measurement_id)
);

CREATE TABLE refusal (
	refusal_id TEXT NOT NULL, 
	aggregate_run_id TEXT, 
	reason TEXT NOT NULL, 
	measurement_ids JSON NOT NULL, 
	detail TEXT, 
	explanation_fr TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (refusal_id), 
	FOREIGN KEY(aggregate_run_id) REFERENCES aggregate (aggregate_run_id)
);

-- Charge le referentiel de taxonomie actif (dev-brief.md section 2.1), tel quel
INSERT INTO taxonomy_release (version, content, checksum, is_active)
VALUES ('0.2.2', $taxonomy_json${
  "meta": {
    "title": "NEXUS Taxonomy Configuration",
    "version": "0.2.2",
    "standard_version": "PROPOSED_STANDARD:NEXUS-TAXONOMY-v0",
    "status": "ACCEPTED — trois axes indépendants (2026-09-18) ; v0.2.1 : input_type (D-10) ; v0.2.2 : target_group simplifié (D-19), statut des résultats (D-20), zone géographique issue du profil OL (D-18)",
    "supersedes": "0.1.0-draft (structure hiérarchique L1→L8, où le programme était emboîté dans le domaine d'intervention)",
    "derived_from": [
      "Tier 1 §A (vocabulaire officiel JCI), §C (taxonomie), §P (modèle de provenance)",
      "Tier 2 §F (inventaire des 465 indicateurs), §M (modèle d'entités observé)",
      "DECISION NEXUS 2026-09-18 — pratique JCI de classement des projets (Product Owner, membre JCI)"
    ],
    "structural_principle": "JCI analyse un projet selon TROIS AXES INDÉPENDANTS : le domaine d'intervention (Area of Opportunity), le programme, et les ODD. Un même projet est classé sur chacun des trois, séparément. AUCUN de ces axes n'est emboîté dans un autre : un projet peut relever du domaine Individual Development, appartenir au programme JCI RISE, et viser l'ODD 8 — les trois en même temps, sans contradiction.",
    "why_this_changed": "La version 0.1.0 rattachait chaque programme à un domaine d'intervention et faisait hériter le projet du domaine de son programme (ancienne règle R3). Cette structure était contredite par les chiffres publiés : page 85, 53,47 % des projets déclarés 2025 sont des projets RISE ; page 86, 44,64 % de ces mêmes projets relèvent de Community Impact. Un sous-ensemble ne peut pas excéder l'ensemble qui le contient. L'emboîtement était donc faux. Ce n'est PAS une incohérence du rapport JCI : c'était une erreur de modélisation NEXUS, désormais corrigée. Aucun objet de conflit (DQC) n'a été ouvert à ce sujet.",
    "design_principle": "Les trois axes de classification sont OFFICIAL_JCI_FACT (JCI les publie). La couche de mesure (types d'activité, de groupe cible, de production, de résultat, d'impact) est PROPOSED_STANDARD : elle n'existe pas chez JCI, elle s'applique aux CHIFFRES et non au projet, et l'attribution d'un de ses codes à une donnée est toujours une SEMANTIC_INTERPRETATION.",
    "prohibited": [
      "Présenter un code de la couche de mesure comme du vocabulaire officiel JCI",
      "Faire hériter le domaine d'intervention d'un projet depuis son programme",
      "Utiliser la clé nue 'area' : toujours geographic_area ou area_of_opportunity"
    ],
    "changelog": [
      {
        "version": "0.2.0",
        "change": "Restructuration en trois axes indépendants (D-07)"
      },
      {
        "version": "0.2.1",
        "change": "Ajout de measurement_layer.input_type : VOLUNTEERS, VOLUNTEER_HOURS (D-10). Codes déjà employés dans les fixtures Tier 1 et les exemples du Measurement Object, jusqu'ici absents du référentiel."
      },
      {
        "version": "0.2.2",
        "change": "D-19 : target_group réduit à 6 familles + OTHER (libellé libre conservé), jamais bloquant, hors clé d'équivalence ; table de correspondance depuis les 12 anciens codes. D-20 : measurement_layer.outcome_status (measured / pending_follow_up / none). D-18 : geographic_area déclarée dans le profil de l'OL à la création du compte."
      }
    ]
  },
  "classification_axes": {
    "_note": "TROIS AXES INDÉPENDANTS. Un projet reçoit une valeur sur chacun, séparément. Aucun emboîtement.",
    "area_of_opportunity": {
      "axis": "A — Domaine d'intervention",
      "layer_values": "OFFICIAL_JCI_FACT",
      "layer_codes": "PROPOSED_STANDARD",
      "source": "p.2, 24-25",
      "cardinality": "1..n par projet",
      "cardinality_evidence": "« Some projects may fall under 2 or more Area of Opportunity » [p.86]",
      "published_distribution_2025": {
        "CI": 0.4464,
        "ID": 0.2721,
        "BE": 0.1849,
        "IC": 0.0966,
        "_source": "p.86 — « 2025 Projects Reported per Area of Opportunity »",
        "_note": "somme = 100,00 % : chaque projet compte une fois sur cet axe malgré la cardinalité 1..n"
      },
      "values": [
        {
          "code": "BE",
          "label": "Business & Entrepreneurship",
          "definition": "Programs fostering innovation, ethical business, and sustainable economic growth",
          "typical_sdgs": [
            8,
            9,
            12
          ]
        },
        {
          "code": "ID",
          "label": "Individual Development",
          "definition": "Skills, training, and experiences that build confidence and leadership capacity",
          "typical_sdgs": [
            4,
            5,
            10
          ]
        },
        {
          "code": "IC",
          "label": "International Cooperation",
          "definition": "Events, partnerships, and networks that connect young leaders across borders",
          "typical_sdgs": [
            16,
            17
          ]
        },
        {
          "code": "CI",
          "label": "Community Impact",
          "definition": "Grassroots projects addressing real needs in local societies",
          "typical_sdgs": [
            1,
            2,
            3,
            4,
            5,
            8,
            9,
            11,
            12,
            13
          ]
        }
      ],
      "notes": [
        "Aucun domaine « environnement » n'existe. Les projets environnementaux relèvent généralement de CI via les ODD 12/13 (SEMANTIC_INTERPRETATION).",
        "Les ODD 6, 7, 14 et 15 ne sont associés par défaut à aucun domaine dans la source.",
        "typical_sdgs est une association publiée p.24-25, PAS une règle de déduction automatique : les ODD d'un projet se déclarent sur l'axe C."
      ]
    },
    "programme": {
      "axis": "B — Programme",
      "layer_names": "OFFICIAL_JCI_FACT",
      "layer_codes": "PROPOSED_STANDARD",
      "cardinality": "0..n par projet",
      "cardinality_note": "Un projet local peut n'appartenir à aucun programme mondial. Le rapport oppose « RISE Projects » (53,47 %) à « Other Projects » (46,53 %) [p.85], ce qui atteste l'existence de projets hors programme.",
      "independence_rule": "Le programme NE DÉTERMINE PAS le domaine d'intervention du projet. Les deux axes se déclarent séparément.",
      "values": [
        {
          "code": "RISE",
          "label": "JCI RISE",
          "meaning": "Rebuild, Invest, Sustain, Evolve",
          "launched": 2020,
          "scope": "« addressing economic recovery, workforce empowerment, and mental health »",
          "cross_cutting": true,
          "components": "rise_pillars",
          "declared_sdgs": {
            "p26": [
              1,
              3,
              8,
              9,
              11,
              12,
              16,
              17
            ],
            "p85": [
              3,
              8,
              10
            ],
            "conflict": "DQC-16 — UNRESOLVED, les deux jeux conservés"
          },
          "pages": [
            85,
            92
          ],
          "published_share_2025": 0.5347
        },
        {
          "code": "CYE",
          "label": "Creative Young Entrepreneur",
          "subcomponents": [
            "CYE Accelerator (SDSN Youth)"
          ],
          "declared_sdgs": [
            8,
            9,
            12
          ],
          "pages": [
            28,
            115
          ]
        },
        {
          "code": "JIB",
          "label": "JCI in Business",
          "subcomponents": [
            "International Business Matching Session"
          ],
          "pages": [
            33
          ]
        },
        {
          "code": "SKILLS_DEV",
          "label": "Skills Development (Trainer certification)",
          "subcomponents": [
            "CNT",
            "CAT",
            "Global Trainers",
            "Training Mentors"
          ],
          "pages": [
            40,
            41
          ]
        },
        {
          "code": "EVENT_TRAINING",
          "label": "Trainings at Area Conferences & World Congress",
          "subcomponents": [
            "Leadership Training Sessions",
            "Skills Development Sessions"
          ],
          "pages": [
            42
          ]
        },
        {
          "code": "LEAD_MASTERCLASS",
          "label": "Leadership Masterclasses",
          "declared_sdgs": [
            4,
            5,
            10,
            16,
            17
          ],
          "pages": [
            26
          ]
        },
        {
          "code": "PUBLIC_SPEAKING",
          "label": "Public Speaking Competition",
          "pages": [
            43
          ]
        },
        {
          "code": "DEBATING",
          "label": "Debating Championship",
          "subcomponents": [
            "EN",
            "FR",
            "ES"
          ],
          "pages": [
            48
          ]
        },
        {
          "code": "TOYP",
          "label": "Ten Outstanding Young Persons of the World",
          "declared_sdgs": [
            3,
            4,
            10,
            11
          ],
          "label_variants_conflict": "DQC-20 — trois libellés différents dans la source",
          "pages": [
            26,
            54
          ]
        },
        {
          "code": "EVENTS",
          "label": "World Congress & Area Conferences",
          "subcomponents": [
            "4 Area Conferences",
            "World Congress"
          ],
          "pages": [
            59
          ]
        },
        {
          "code": "IHD",
          "label": "International Human Duties Initiative",
          "subcomponents": [
            "7 Duties for Leaders",
            "National Ambassadors",
            "Best Human Duties Project Award"
          ],
          "pages": [
            71
          ]
        },
        {
          "code": "TWINNING",
          "label": "JCI Twinning",
          "subcomponents": [
            "Buddy Project",
            "Mastery Month",
            "Training for Innovation"
          ],
          "pages": [
            78
          ]
        },
        {
          "code": "COMMUNITY_DEV",
          "label": "Community Development Projects",
          "pages": [
            84
          ]
        },
        {
          "code": "SUST_LEADERSHIP_COURSE",
          "label": "Mastering Sustainable Leadership (SDG Academy)",
          "pages": [
            124
          ]
        },
        {
          "code": "GLOBAL_CITIZEN_COURSE",
          "label": "Becoming Global Citizens for a Sustainable Society",
          "pages": [
            125
          ]
        },
        {
          "code": "GYD",
          "label": "Global Youth Dialogue",
          "pages": [
            122
          ]
        },
        {
          "code": "RISE_TO_THE_CHALLENGE",
          "label": "RISE to the Challenge (ECOSOC Youth Forum side event)",
          "pages": [
            117,
            118
          ]
        }
      ],
      "transversal_structures": {
        "_note": "Structures JCI qui ne sont pas des programmes de projet et ne se déclarent pas sur cet axe.",
        "layer": "OFFICIAL_JCI_FACT",
        "items": [
          "JCI Foundation / Development Grants",
          "JCI Senate",
          "JCI Awards Program",
          "Club100",
          "Alumni Clubs",
          "Junior Clubs",
          "Member-centric partnerships"
        ],
        "pages": [
          12,
          13,
          96,
          129
        ]
      },
      "chapter_placement_in_report": {
        "_warning": "STRUCTURE DOCUMENTAIRE UNIQUEMENT — ce n'est PAS une règle de classification. Indique seulement dans quel chapitre du rapport 2025 chaque programme a été imprimé. Ne jamais s'en servir pour déduire le domaine d'intervention d'un projet.",
        "BE": [
          "CYE",
          "JIB"
        ],
        "ID": [
          "SKILLS_DEV",
          "EVENT_TRAINING",
          "PUBLIC_SPEAKING",
          "DEBATING"
        ],
        "IC": [
          "TOYP",
          "EVENTS",
          "IHD",
          "TWINNING"
        ],
        "CI": [
          "COMMUNITY_DEV",
          "RISE"
        ],
        "unplaced": [
          "LEAD_MASTERCLASS",
          "SUST_LEADERSHIP_COURSE",
          "GLOBAL_CITIZEN_COURSE",
          "GYD",
          "RISE_TO_THE_CHALLENGE"
        ]
      }
    },
    "sdg": {
      "axis": "C — Objectifs de Développement Durable",
      "layer": "OFFICIAL_JCI_FACT",
      "count": 17,
      "source": "p.24-26, 84, 87-90",
      "cardinality": "1..n par projet, dont exactement 1 principal",
      "roles": [
        "primary",
        "secondary"
      ],
      "role_evidence": "« Primary SDGs Addressed / Secondary SDG » [p.84]",
      "commitment_2026": "« Every local project will align with one or more SDGs and report measurable results » [p.132 — Road Map for 2026]",
      "over_tagging_warning": "DQC-22 — le projet « SDGs Hunt » déclare les 17 ODD (l'ODD 11 deux fois) pour 4 heures de bénévolat et 5 bénévoles [p.89]. Un plafond sur le nombre d'ODD secondaires est un contrôle recommandé.",
      "label_note": "Libellés courts de l'ONU tels qu'employés par JCI. La casse varie dans la source (« Zero hunger », « Gender equality ») : ne pas traiter une différence de casse comme une valeur distincte."
    }
  },
  "rise_pillars": {
    "_note": "Composante du programme RISE. Se déclare uniquement si le projet est RISE.",
    "layer": "OFFICIAL_JCI_FACT",
    "source": "p.85",
    "cardinality": "1..n",
    "canonical_label_set": "graphique « RISE Pillars Covered » — retenu par DECISION NEXUS parce que ce sont les libellés attachés aux pourcentages publiés",
    "conflict": "DQC-17 — UNRESOLVED. La page 85 emploie deux jeux de libellés pour les mêmes trois piliers. NEXUS retient un jeu pour l'affichage ; cela ne résout pas le conflit côté JCI, qui reste ouvert.",
    "values": [
      {
        "code": "REBUILD_ECONOMIES",
        "label": "Sustaining and Rebuilding Economies",
        "variant_label": "Sustain and Rebuild Economies",
        "published_share_2025": 0.403
      },
      {
        "code": "WORKFORCE",
        "label": "Workforce Motivation",
        "variant_label": "Workforce Empowerment",
        "published_share_2025": 0.3167
      },
      {
        "code": "MENTAL_HEALTH",
        "label": "Preserving Mental Health",
        "variant_label": "Mental Health Awareness",
        "published_share_2025": 0.2804
      }
    ],
    "arithmetic_note": "La somme des trois parts vaut 100,01 % (DQC-18, arrondi)."
  },
  "geographic_area": {
    "_note": "Axe géographique, totalement distinct de area_of_opportunity malgré l'homonymie du mot « Area » dans la source.",
    "layer": "OFFICIAL_JCI_FACT",
    "source": "p.9",
    "codes_are": "PROPOSED_STANDARD, sauf ASPAC (abréviation attestée p.81, 106, 128)",
    "derivation": "Déclarée une fois dans le profil de l'OL à la création du compte (D-18) → LOCAL_REPORTED_FACT. Jamais extraite du texte, jamais demandée à la saisie d'un projet.",
    "values": [
      {
        "code": "AFME",
        "label": "Africa and the Middle East"
      },
      {
        "code": "AMERICA",
        "label": "America"
      },
      {
        "code": "ASPAC",
        "label": "Asia and the Pacific"
      },
      {
        "code": "EUROPE",
        "label": "Europe"
      }
    ],
    "disambiguation": "Si une source emploie « Area » sans contexte suffisant pour trancher, marquer AMBIGUOUS_AREA. Jamais tranché par le LLM (règle P7).",
    "known_gap": "La table organisation nationale / pays → geographic_area n'est pas publiée (VDX-01, carte p.9 illisible). Contournée pour le MVP par la déclaration du profil OL (D-18) ; la table reste utile pour contrôler la cohérence pays ↔ zone."
  },
  "measurement_layer": {
    "_note": "PROPOSITION NEXUS. Ces codes ne sont PAS du vocabulaire JCI. Ils s'appliquent aux CHIFFRES d'un projet, pas au projet lui-même. Attribuer un de ces codes à une donnée est toujours une SEMANTIC_INTERPRETATION.",
    "layer": "PROPOSED_STANDARD",
    "input_type": {
      "role": "Ressources mobilisées par le projet (classe IAOOI = INPUT). Jamais additionnées aux productions ni aux résultats : la clé d'équivalence les sépare.",
      "mvp": "actif — alimente les champs canoniques #7 resources.volunteers et #8 resources.volunteer_hours",
      "decision": "D-10 (2026-09-18)",
      "values": [
        {
          "code": "VOLUNTEERS",
          "unit": "person",
          "iaooi_class": "INPUT",
          "note": "La définition JCI de « volunteer » (membre ou non) est inconnue (UNK-DM-03) : definition.status reste unknown sauf si la saisie la précise."
        },
        {
          "code": "VOLUNTEER_HOURS",
          "unit": "hour",
          "iaooi_class": "INPUT",
          "note": "Total d'heures déclaré ; jamais recalculé à partir du nombre de bénévoles."
        }
      ]
    },
    "output_type": {
      "role": "CRITIQUE — c'est ce champ qui alimente la clé d'équivalence et rend possible le refus d'agrégation. Sans lui, deux nombres de même unité sont indistinguables.",
      "mvp": "actif, liste complète",
      "values": [
        {
          "code": "PARTICIPANTS",
          "unit": "person"
        },
        {
          "code": "PEOPLE_TRAINED",
          "unit": "person"
        },
        {
          "code": "PEOPLE_REACHED_DIRECT",
          "unit": "person"
        },
        {
          "code": "PEOPLE_REACHED_OUTREACH",
          "unit": "person",
          "never_sum_with": [
            "PEOPLE_REACHED_DIRECT",
            "BENEFICIARIES"
          ]
        },
        {
          "code": "REGISTRATIONS",
          "unit": "person"
        },
        {
          "code": "ATTENDEES",
          "unit": "person",
          "never_sum_with": [
            "REGISTRATIONS"
          ],
          "evidence": "DQC-06, DQC-14, DQC-15"
        },
        {
          "code": "COMPLETIONS",
          "unit": "person"
        },
        {
          "code": "APPLICATIONS_ENTRIES",
          "unit": "application"
        },
        {
          "code": "TEAMS",
          "unit": "team"
        },
        {
          "code": "ITEMS_DISTRIBUTED",
          "unit": "item"
        },
        {
          "code": "SIGNATURES",
          "unit": "signature"
        },
        {
          "code": "AGREEMENTS_SIGNED",
          "unit": "agreement"
        },
        {
          "code": "DOCUMENTS_PRODUCED",
          "unit": "document"
        },
        {
          "code": "PHYSICAL_OUTPUT",
          "unit": "variable",
          "requires": "sub_code"
        },
        {
          "code": "COMM_AUDIENCE",
          "unit": "view",
          "never_sum_with": [
            "BENEFICIARIES",
            "PEOPLE_REACHED_DIRECT"
          ],
          "evidence": "DQC-08"
        }
      ]
    },
    "outcome_type": {
      "role": "CRITIQUE — seul emplacement où un résultat peut être rangé. JCI n'a aucune catégorie équivalente, ce qui explique que 12 seulement de ses 465 indicateurs décrivent un changement.",
      "mvp": "actif, liste complète",
      "values": [
        {
          "code": "JOBS_CREATED"
        },
        {
          "code": "JOB_PLACEMENT",
          "requires": "base_population",
          "evidence": "DQC-12 — « 75% placed » sans base [p.91]"
        },
        {
          "code": "BUSINESS_CREATED"
        },
        {
          "code": "BUSINESS_GROWTH"
        },
        {
          "code": "ACCESS_TO_FINANCE_MARKETS"
        },
        {
          "code": "SKILLS_CONFIDENCE"
        },
        {
          "code": "AWARENESS_ATTITUDE"
        },
        {
          "code": "POLICY_INSTITUTIONAL_CHANGE"
        },
        {
          "code": "FOLLOW_UP_INITIATIVES"
        },
        {
          "code": "NEW_MEMBERS",
          "note": "résultat organisationnel, pas communautaire"
        },
        {
          "code": "PARTNERSHIPS_FORMED"
        }
      ]
    },
    "target_group": {
      "role": "Décrire à qui s'adresse le projet, pour lecture et filtrage. N'intervient JAMAIS dans l'agrégation.",
      "decision": "D-19 (2026-09-18) — il est impossible de prévoir tous les publics qu'une OL peut décrire ; la liste est donc courte, ouverte (OTHER) et non bloquante.",
      "layer": "PROPOSED_STANDARD (codes) · SEMANTIC_INTERPRETATION (attribution par l'IA)",
      "structure": {
        "internal_external": {
          "required": true,
          "values": [
            "internal",
            "external",
            "mixed"
          ],
          "rule": "Seule partie obligatoire (confirmation humaine, D-16). Porte la règle R7 et entre dans la clé d'équivalence."
        },
        "family": {
          "required": false,
          "proposed_by": "IA",
          "blocking": false,
          "cardinality": "0..n",
          "in_equivalence_key": false
        },
        "source_label": {
          "required": false,
          "rule": "Libellé exact employé par le SG (ex. « chercheurs d'emploi »), toujours conservé tel quel, jamais reformulé."
        }
      },
      "values": [
        {
          "code": "JCI_MEMBERS",
          "label": "Membres JCI",
          "axis": "internal"
        },
        {
          "code": "YOUTH_STUDENTS",
          "label": "Jeunes, étudiants, enfants",
          "axis": "external"
        },
        {
          "code": "ENTREPRENEURS_BUSINESSES",
          "label": "Entrepreneurs et entreprises",
          "axis": "external"
        },
        {
          "code": "EMPLOYMENT_PROFESSIONALS",
          "label": "Emploi et professionnels (dont chercheurs d'emploi)",
          "axis": "external"
        },
        {
          "code": "COMMUNITY_PUBLIC",
          "label": "Communauté et grand public (dont publics vulnérables)",
          "axis": "external"
        },
        {
          "code": "INSTITUTIONS_DECISION_MAKERS",
          "label": "Institutions et décideurs",
          "axis": "external"
        },
        {
          "code": "OTHER",
          "label": "Autre — le libellé libre du SG fait foi",
          "axis": "any",
          "requires": "source_label"
        }
      ],
      "fallback_rule": "Si aucune famille ne convient ou si l'IA hésite : OTHER + source_label. Ce n'est jamais une erreur ni un blocage.",
      "legacy_mapping_v0_2_1": {
        "JCI_MEMBERS": "JCI_MEMBERS",
        "JCI_JUNIOR": "JCI_MEMBERS",
        "YOUTH": "YOUTH_STUDENTS",
        "STUDENTS": "YOUTH_STUDENTS",
        "CHILDREN": "YOUTH_STUDENTS",
        "ENTREPRENEURS": "ENTREPRENEURS_BUSINESSES",
        "WOMEN_ENTREPRENEURS": "ENTREPRENEURS_BUSINESSES",
        "SMES_BUSINESSES": "ENTREPRENEURS_BUSINESSES",
        "PROFESSIONALS": "EMPLOYMENT_PROFESSIONALS",
        "VULNERABLE_COMMUNITIES": "COMMUNITY_PUBLIC",
        "GENERAL_PUBLIC": "COMMUNITY_PUBLIC",
        "DECISION_MAKERS": "INSTITUTIONS_DECISION_MAKERS"
      },
      "attributes_not_groups": [
        "gender",
        "age_band",
        "rural_urban",
        "vulnerability_flag"
      ],
      "critical_rule": "R7 — les membres JCI (interne) et les communautés externes ne s'additionnent jamais. Défaut documenté : S6."
    },
    "activity_type": {
      "role": "Utile pour comparer des projets entre eux, non vital pour l'agrégation.",
      "mvp": "déduit par l'IA, aucune liste imposée à la saisie, aucune question au SG",
      "values": [
        {
          "code": "TRAINING_WORKSHOP",
          "label": "Formation / atelier"
        },
        {
          "code": "MENTORING",
          "label": "Mentorat"
        },
        {
          "code": "COMPETITION",
          "label": "Compétition / concours"
        },
        {
          "code": "RECOGNITION_AWARD",
          "label": "Distinction / prix"
        },
        {
          "code": "CONFERENCE_EVENT",
          "label": "Congrès / conférence"
        },
        {
          "code": "PANEL_FORUM_DIALOGUE",
          "label": "Panel / forum / dialogue"
        },
        {
          "code": "ADVOCACY_CAMPAIGN",
          "label": "Plaidoyer / pétition / proclamation"
        },
        {
          "code": "AWARENESS_EDUCATION",
          "label": "Sensibilisation / éducation du public"
        },
        {
          "code": "COMMUNITY_SERVICE",
          "label": "Service direct"
        },
        {
          "code": "ENVIRONMENTAL_ACTION",
          "label": "Action environnementale"
        },
        {
          "code": "NETWORKING_MATCHING",
          "label": "Réseautage / mise en relation"
        },
        {
          "code": "PARTNERSHIP_AGREEMENT",
          "label": "Accord / jumelage"
        },
        {
          "code": "FUNDRAISING",
          "label": "Collecte de fonds"
        },
        {
          "code": "ONLINE_COURSE_WEBINAR",
          "label": "Cours / webinaire en ligne"
        },
        {
          "code": "INTERNAL_GOVERNANCE",
          "label": "Structuration interne"
        }
      ]
    },
    "impact_type": {
      "role": "Type une AFFIRMATION d'impact, jamais une mesure. Aucun impact n'est mesuré avec attribution dans le rapport (constat S3).",
      "mvp": "DÉSACTIVÉ — 1 seul cas sur 465 indicateurs, volume négligeable pour la démonstration",
      "values": [
        {
          "code": "ENVIRONMENTAL"
        },
        {
          "code": "ECONOMIC_RESILIENCE"
        },
        {
          "code": "HEALTH_WELLBEING"
        },
        {
          "code": "EDUCATION_ACCESS"
        },
        {
          "code": "SOCIAL_INCLUSION_EQUITY"
        },
        {
          "code": "GOVERNANCE_PEACE"
        }
      ],
      "attribution_levels": [
        "measured_attribution",
        "measured_contribution",
        "self_reported",
        "narrative_only"
      ]
    },
    "outcome_status": {
      "role": "État du champ canonique #12 (résultats) pour un projet. Remplace le booléen none_measured.",
      "decision": "D-20 (2026-09-18)",
      "layer": "PROPOSED_STANDARD",
      "required": true,
      "values": [
        {
          "code": "measured",
          "label": "Résultat constaté",
          "rule": "Le SG déclare ≥1 résultat concret chiffré (réponse à C7). La mesure garde sa propre iaooi_class (ex. 43 CV refaits = OUTPUT) : le statut dit qu'un résultat a été déclaré, il ne reclasse rien."
        },
        {
          "code": "pending_follow_up",
          "label": "Pas encore mesurable — suivi prévu",
          "rule": "Requiert expected_outcome_type (ou libellé libre) + follow_up_date. Aucune mesure créée, aucune valeur 0. La réponse au suivi crée une NOUVELLE mesure rattachée au projet."
        },
        {
          "code": "none",
          "label": "Aucun résultat mesurable attendu",
          "rule": "Activité réelle (comptée via ses outputs et inputs) sans effet mesurable visé, ex. partage d'expérience. Aucune mesure créée."
        }
      ],
      "mvp": "Les trois états sont stockés et affichés. La relance automatique à follow_up_date est post-MVP (démo : suivi simulé).",
      "invariant": "UNKNOWN ≠ ZERO : ni pending_follow_up ni none ne produisent de valeur 0."
    }
  },
  "rules": [
    {
      "id": "R1",
      "rule": "Un projet appartient à 1 organisation locale (ou 1 organisation nationale pour un projet national) ; une OL relève de 1 NO ; une NO relève de 1 geographic_area.",
      "layer": "OFFICIAL_JCI_FACT (structure p.8-10)"
    },
    {
      "id": "R2",
      "rule": "Un projet porte 1..n area_of_opportunity.",
      "layer": "OFFICIAL_JCI_FACT p.86"
    },
    {
      "id": "R3",
      "rule": "Les trois axes de classification sont INDÉPENDANTS. Le domaine d'intervention d'un projet ne se déduit jamais de son programme, ni l'inverse. Chaque axe se déclare séparément.",
      "layer": "DECISION NEXUS 2026-09-18",
      "supersedes": "R3 v0.1.0, qui faisait hériter le domaine depuis le programme — structure démentie par les distributions publiées p.85 et p.86"
    },
    {
      "id": "R4",
      "rule": "Un projet RISE porte 1..n piliers RISE. Un projet non-RISE n'en porte aucun.",
      "layer": "SEMANTIC_INTERPRETATION (le % par pilier suppose un étiquetage existant côté JCI)"
    },
    {
      "id": "R5",
      "rule": "ODD : exactement 1 principal, n secondaires.",
      "layer": "SEMANTIC_INTERPRETATION, libellés de rôle attestés p.84"
    },
    {
      "id": "R6",
      "rule": "Un jumelage relie ≥2 organisations de pays différents ; un même projet peut être déclaré par chaque partie.",
      "layer": "OFFICIAL_JCI_FACT p.78",
      "mvp_status": "DÉSACTIVÉ — décision D-03 : la déduplication est hors périmètre MVP, un projet déclaré deux fois est compté deux fois"
    },
    {
      "id": "R7",
      "rule": "Les métriques de membres JCI (interne) et de bénéficiaires externes ne s'additionnent jamais.",
      "layer": "PROPOSED_STANDARD",
      "evidence": "constat S6"
    },
    {
      "id": "R8",
      "rule": "Les métriques de contexte et les chiffres d'événements externes ne sont jamais agrégés comme productions NEXUS.",
      "layer": "PROPOSED_STANDARD",
      "evidence": "DQC-21"
    },
    {
      "id": "R9",
      "rule": "Un projet peut n'appartenir à aucun programme. L'absence de programme est une valeur légitime, pas une donnée manquante.",
      "layer": "OFFICIAL_JCI_FACT",
      "evidence": "« Other Projects 46.53% » [p.85]"
    }
  ],
  "cross_axis_analysis_enabled": {
    "_note": "Ce que la structure à trois axes rend possible et que le rapport JCI 2025 ne permet pas.",
    "examples": [
      "Comparer les résultats des projets RISE et non-RISE, à domaine d'intervention égal",
      "Mesurer la contribution réelle de chaque pilier RISE, au-delà du simple pourcentage de projets étiquetés",
      "Croiser un ODD avec un domaine d'intervention et un programme sans double comptage",
      "Répondre à « le programme RISE produit-il davantage ? », question aujourd'hui sans réponse dans la source"
    ]
  }
}$taxonomy_json$::json, '55dc93cae4a539f4b6af293cf6b20334980fab4e4c97bb05a0abd783aea2e810', true)
ON CONFLICT (version) DO NOTHING;

-- Charge le registre de qualite des donnees JCI (dev-brief.md section 2.11), tel quel

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-01', 'conflict', $qi_subject$Nombre de membres$qi_subject$, $qi_values$[{"label": "A", "value": 100000, "value_qualifier": "at_least", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "v", "section": "Executive Summary", "quote": "a global network of over 100,000 young leaders in more than 100 countries"}}, {"label": "B", "value": 100000, "value_qualifier": "at_least", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "vi", "section": "Message from JCI President", "quote": "More than 100,000 young leaders across four Areas came together"}}, {"label": "C", "value": 147000, "value_qualifier": "at_least", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "2", "section": "Organization Overview", "quote": "with over 147,000 members and 4,600 Local Organizations worldwide"}}, {"label": "D", "value": 147670, "value_qualifier": "exact", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "8", "section": "Membership Details", "quote": "powered by 147,670 members"}}]$qi_values$::json, 'UNRESOLVED', true)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-02', 'conflict', $qi_subject$Nombre de pays$qi_subject$, $qi_values$[{"label": "A", "value": 100, "value_qualifier": "at_least", "unit": "country", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "v", "section": "Executive Summary", "quote": "in more than 100 countries"}}, {"label": "B", "value": 100, "value_qualifier": "at_least", "unit": "country", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "24", "section": "Four Areas of Opportunity and SDG Alignment", "quote": "present in over 100 countries"}}, {"label": "C", "value": 114, "value_qualifier": "at_least", "unit": "country", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "2", "section": "Organization Overview", "quote": "Today, JCI is present in more than 114 countries"}}, {"label": "D", "value": 114, "value_qualifier": "exact", "unit": "country", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "9", "section": "International Presence \u2013 Operational Areas", "quote": "Global Presence (114 Countries)"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-03', 'conflict', $qi_subject$Nombre de projets$qi_subject$, $qi_values$[{"label": "A", "value": 1000, "value_qualifier": "at_least", "unit": "project", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "v", "section": "Executive Summary", "quote": "1,000+ projects implemented (2024\u20132025)"}}, {"label": "B", "value": 1000, "value_qualifier": "at_least", "unit": "project", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "84", "section": "Community Development Projects", "quote": "1,000+ Total Projects Executed (2024-25)"}}, {"label": "C", "value": 1000, "value_qualifier": "at_least", "unit": "project", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "85", "section": "JCI RISE Projects", "quote": "1000+ Total Projects Reported for 2025"}}, {"label": "D", "value": 10000, "value_qualifier": "at_least", "unit": "project", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "vii", "section": "Message from Interim Secretary General", "quote": "the collective energy of over 10,000 projects across more than 4,500 Local Organizations"}}]$qi_values$::json, 'UNRESOLVED', true)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-04', 'conflict', $qi_subject$Nombre de Local Organizations$qi_subject$, $qi_values$[{"label": "A", "value": 4500, "value_qualifier": "at_least", "unit": "local_organization", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "v", "section": "Executive Summary", "quote": "4,500+ Local Organizations mobilized across continents"}}, {"label": "B", "value": 4600, "value_qualifier": "approx", "unit": "local_organization", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "2", "section": "Organization Overview", "quote": "4,600 Local Organizations worldwide"}}, {"label": "C", "value": 4641, "value_qualifier": "exact", "unit": "local_organization", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "8", "section": "Membership Details", "quote": "4,641 Local Organizations provide the grassroots foundation"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-05', 'conflict', $qi_subject$Nombre de bénévoles$qi_subject$, $qi_values$[{"label": "A", "value": 40000, "value_qualifier": "at_least", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "v", "section": "Executive Summary", "quote": "40,000+ volunteers engaged"}}, {"label": "B", "value": 40000, "value_qualifier": "at_least", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "84", "section": "Community Development Projects", "quote": "40,000+ Total Number of Volunteers Engaged"}}, {"label": "C", "value": 42401, "value_qualifier": "exact", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "86", "section": "JCI RISE Projects", "quote": "42,401 Total Number of Volunteers Engaged"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-06', 'conflict', $qi_subject$Participation aux événements internationaux$qi_subject$, $qi_values$[{"label": "A", "value": 10000, "value_qualifier": "at_least", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "v", "section": "Executive Summary", "quote": "10,000+ attendees participating in international events"}}, {"label": "B", "value": 10000, "value_qualifier": "at_most", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "59", "section": "JCI Events Area Conferences and World Congress", "quote": "In 2024\u201325, JCI gathered nearly 10,000 participants across its global and Area events"}}, {"label": "C", "value": 10729, "value_qualifier": "exact", "unit": "registration", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "59", "section": "JCI Events Area Conferences and World Congress", "quote": "Total Registrations Across All Conferences 10,729 Registrations"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-07', 'conflict', $qi_subject$Followers réseaux sociaux$qi_subject$, $qi_values$[{"label": "A", "value": 260000, "value_qualifier": "at_least", "unit": "follower", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "v", "section": "Executive Summary", "quote": "260,000+ followers across JCI's digital platforms"}}, {"label": "B", "value": 229200, "value_qualifier": "exact", "unit": "follower_or_subscriber", "layer": "SEMANTIC_INTERPRETATION", "value_status": "calculated", "formula": "148000 + 41000 + 32000 + 8200", "inputs": [{"label": "Facebook", "value": 148000, "value_qualifier": "exact", "unit": "follower", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "17", "section": "Social Media Metrics", "quote": "Total Followers: 148,000"}}, {"label": "Instagram", "value": 41000, "value_qualifier": "exact", "unit": "follower", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "17", "section": "Social Media Metrics", "quote": "Total Followers: 41,000"}}, {"label": "LinkedIn", "value": 32000, "value_qualifier": "exact", "unit": "follower", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "17", "section": "Social Media Metrics", "quote": "Total Followers: 32,000"}}, {"label": "YouTube", "value": 8200, "value_qualifier": "exact", "unit": "subscriber", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "18", "section": "Social Media Metrics", "quote": "Subscribers: 8,200"}}], "rule_id": "CALC-ARITH"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-08', 'conflict', $qi_subject$Impressions vs reach$qi_subject$, $qi_values$[{"label": "A", "value": 2000000, "value_qualifier": "at_least", "unit": "impression", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "v", "section": "Executive Summary", "quote": "2 million+ impressions"}}, {"label": "B", "value": 2000000, "value_qualifier": "at_least", "unit": "reach", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "17", "section": "Social Media Metrics", "quote": "Reach: Over 2 million (76% organic)"}}, {"label": "C", "value": 318604, "value_qualifier": "exact", "unit": "impression", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "17", "section": "Social Media Metrics", "quote": "Impressions: 318,604"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-09', 'conflict', $qi_subject$Lecteurs du LEADER Magazine$qi_subject$, $qi_values$[{"label": "A", "value": 13800, "value_qualifier": "approx", "unit": "reader", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "v", "section": "Executive Summary", "quote": "The Leader Magazine: 13,800 readers across 70+ countries"}}, {"label": "B", "value": 13000, "value_qualifier": "at_most", "unit": "reader", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "19", "section": "The LEADER Magazine", "quote": "The Leader has reached nearly 13,000 total readers across seven issues"}}, {"label": "C", "value": 13872, "value_qualifier": "exact", "unit": "reader", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "20", "section": "The LEADER Magazine", "quote": "Total 13,872 15,423 0:48:56"}}, {"label": "D", "value": 12564, "value_qualifier": "exact", "unit": "reader_device", "layer": "SEMANTIC_INTERPRETATION", "value_status": "calculated", "formula": "8857 + 81 + 3626", "inputs": [{"label": "Mobile", "value": 8857, "value_qualifier": "exact", "unit": "reader", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "19", "section": "The LEADER Magazine", "quote": "Mobile Phone 8,857 (70.50%)"}}, {"label": "Tablet", "value": 81, "value_qualifier": "exact", "unit": "reader", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "19", "section": "The LEADER Magazine", "quote": "Tablet 81 (0.64%)"}}, {"label": "Computer", "value": 3626, "value_qualifier": "exact", "unit": "reader", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "19", "section": "The LEADER Magazine", "quote": "Computer or Laptop 3,626 (28.86%)"}}], "rule_id": "CALC-ARITH"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-10', 'conflict', $qi_subject$Genre des Senators$qi_subject$, $qi_values$[{"label": "A", "value": 0.67, "value_qualifier": "exact", "unit": "ratio", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "100", "section": "JCI Senate", "quote": "67% Senators are male"}}, {"label": "B", "value": 0.37, "value_qualifier": "exact", "unit": "ratio", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "100", "section": "JCI Senate", "quote": "and 37% are female as of 2025"}}, {"label": "C", "value": 1.04, "value_qualifier": "exact", "unit": "ratio", "layer": "SEMANTIC_INTERPRETATION", "value_status": "calculated", "formula": "0.67 + 0.37", "inputs": ["ref:same_conflict.values"], "rule_id": "CALC-ARITH"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-11', 'conflict', $qi_subject$Participants JCI Ankara '7x7'$qi_subject$, $qi_values$[{"label": "A", "value": 49, "value_qualifier": "exact", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "75", "section": "International Human Duties Impact Stories", "quote": "where 49 participants discussed the 7 duties at thematic roundtables"}}, {"label": "B", "value": 45, "value_qualifier": "exact", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "75", "section": "International Human Duties Impact Stories", "quote": "We engaged 45 participants"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-12', 'conflict', $qi_subject$Bridges Project : participants vs formés$qi_subject$, $qi_values$[{"label": "A", "value": 35, "value_qualifier": "exact", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "91", "section": "JCI RISE Impact Stories", "quote": "Over three weeks, 35 participants engaged in intensive sessions led by 20 volunteer trainers"}}, {"label": "B", "value": 200, "value_qualifier": "at_least", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "91", "section": "JCI RISE Impact Stories", "quote": "200+ youth trained"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-13', 'conflict', $qi_subject$Impulso NOA : 4 nouveaux membres = 20 %$qi_subject$, $qi_values$[{"label": "A", "value": 22, "value_qualifier": "exact", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "94", "section": "JCI RISE Impact Stories", "quote": "directly connecting 22 advanced students with leading companies"}}, {"label": "B", "value": 0.2, "value_qualifier": "exact", "unit": "ratio", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "94", "section": "JCI RISE Impact Stories", "quote": "four new JCI Salta members\u2014representing 20% of all participants"}}, {"label": "C", "value": 0.1818, "value_qualifier": "exact", "unit": "ratio", "layer": "SEMANTIC_INTERPRETATION", "value_status": "calculated", "formula": "4 / 22", "inputs": ["ref:same_conflict.values"], "rule_id": "CALC-ARITH"}]$qi_values$::json, 'UNRESOLVED', true)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-14', 'conflict', $qi_subject$Global Youth Dialogue : présents vs membres/non-membres$qi_subject$, $qi_values$[{"label": "A", "value": 662, "value_qualifier": "exact", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "122", "section": "Global Youth Dialogue 2025", "quote": "662 live attendees"}}, {"label": "B", "value": 679, "value_qualifier": "exact", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "123", "section": "Global Youth Dialogue 2025", "quote": "JCI Members 679 (79.6%)"}}, {"label": "C", "value": 174, "value_qualifier": "exact", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "123", "section": "Global Youth Dialogue 2025", "quote": "Non-Members 174 (20.4%)"}}, {"label": "D", "value": 853, "value_qualifier": "exact", "unit": "person", "layer": "SEMANTIC_INTERPRETATION", "value_status": "calculated", "formula": "679 + 174", "inputs": ["ref:same_conflict.values"], "rule_id": "CALC-ARITH"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-15', 'conflict', $qi_subject$ECOSOC side event : présents > inscrits$qi_subject$, $qi_values$[{"label": "A", "value": 1160, "value_qualifier": "at_least", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "117", "section": "Impact Through Hosted and Partner Events", "quote": "1,160+ registrants"}}, {"label": "B", "value": 1500, "value_qualifier": "at_least", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "117", "section": "Impact Through Hosted and Partner Events", "quote": "1,500+ live participants"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-16', 'conflict', $qi_subject$ODD du programme JCI RISE$qi_subject$, $qi_values$[{"label": "A", "value": [1, 3, 8, 9, 11, 12, 16, 17], "value_qualifier": "exact", "unit": "sdg_list", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "26", "section": "Programs and Initiatives with SDG Alignment", "quote": "JCI RISE \u2022 SDG 1: Addresses community challenges to reduce poverty through local initiatives."}}, {"label": "B", "value": [3, 8, 10], "value_qualifier": "exact", "unit": "sdg_list", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "85", "section": "JCI RISE Projects", "quote": "The initiative positions JCI as a key contributor to SDG 3 (Good Health & Well-being), SDG 8 (Decent Work & Economic Growth), and SDG 10 (Reduced Inequalities)."}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-17', 'conflict', $qi_subject$Libellés des piliers RISE$qi_subject$, $qi_values$[{"label": "A", "value": ["Sustain and Rebuild Economies", "Workforce Empowerment", "Mental Health Awareness"], "value_qualifier": "exact", "unit": "label_list", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "85", "section": "JCI RISE Projects", "quote": "Sustain and Rebuild Economies: Support businesses, entrepreneurs, and SMEs."}}, {"label": "B", "value": ["Sustaining and Rebuilding Economies", "Workforce Motivation", "Preserving Mental Health"], "value_qualifier": "exact", "unit": "label_list", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "85", "section": "JCI RISE Projects", "quote": "RISE Pillars Covered"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-18', 'conflict', $qi_subject$Pourcentages dont la somme vaut 100,01 %$qi_subject$, $qi_values$[{"label": "A", "value": [0.403, 0.2804, 0.3167], "value_qualifier": "exact", "unit": "ratio_list", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "85", "section": "JCI RISE Projects", "quote": "Sustaining and Rebuilding Economies 40.30% \u2026 Preserving Mental Health 28.04% \u2026 Workforce Motivation 31.67%"}}, {"label": "B", "value": [0.6704, 0.0915, 0.2191, 0.0191], "value_qualifier": "exact", "unit": "ratio_list", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "86", "section": "JCI RISE Projects", "quote": "2025 Projects Reported per Area"}}, {"label": "C", "value": 1.0001, "value_qualifier": "exact", "unit": "ratio", "layer": "SEMANTIC_INTERPRETATION", "value_status": "calculated", "formula": "sum(A) and sum(B)", "inputs": ["ref:same_conflict.values"], "rule_id": "CALC-ARITH"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-19', 'conflict', $qi_subject$Part des LO en Europe$qi_subject$, $qi_values$[{"label": "A", "value": 0.158, "value_qualifier": "exact", "unit": "ratio", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "8", "section": "Membership Details", "quote": "Europe 17,623 11.9% 736 15.8%"}}, {"label": "B", "value": 0.159, "value_qualifier": "exact", "unit": "ratio", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "11", "section": "Local Organizations", "quote": "Europe 736 (15.9%)"}}, {"label": "C", "value": 0.1586, "value_qualifier": "exact", "unit": "ratio", "layer": "SEMANTIC_INTERPRETATION", "value_status": "calculated", "formula": "736 / 4641", "inputs": ["ref:same_conflict.values"], "rule_id": "CALC-ARITH"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-20', 'conflict', $qi_subject$Nom officiel de TOYP$qi_subject$, $qi_values$[{"label": "A", "value": "Ten Outstanding Young Persons of the World", "value_qualifier": "exact", "unit": "label", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "54", "section": "Ten Outstanding Young Persons of the World (TOYP)", "quote": "Ten Outstanding Young Persons of the World (TOYP)"}}, {"label": "B", "value": "Ten Outstanding Young Persons", "value_qualifier": "exact", "unit": "label", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "26", "section": "Programs and Initiatives with SDG Alignment", "quote": "Ten Outstanding Young Persons (TOYP)"}}, {"label": "C", "value": "Ten Outstanding Persons of the Year", "value_qualifier": "exact", "unit": "label", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "113", "section": "Corporate Sponsors Driving Shared Impact", "quote": "the Ten Outstanding Persons of the Year programs"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-21', 'conflict', $qi_subject$Chiffres d'événements externes à proximité des chiffres JCI$qi_subject$, $qi_values$[{"label": "A", "value": 52000, "value_qualifier": "at_least", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "119", "section": "Impact Through Hosted and Partner Events", "quote": "which drew over 52,000 participants from 130+ countries"}}, {"label": "B", "value": 1000, "value_qualifier": "at_least", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "121", "section": "Impact Through Hosted and Partner Events", "quote": "which convened over 1,000 leaders from 100 countries"}}, {"label": "C", "value": 45, "value_qualifier": "exact", "unit": "person", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "121", "section": "Impact Through Hosted and Partner Events", "quote": "brought together 45 young human rights advocates from around the world"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-22', 'conflict', $qi_subject$ODD 11 cité deux fois (SDGs Hunt)$qi_subject$, $qi_values$[{"label": "A", "value": 11, "value_qualifier": "exact", "unit": "sdg", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "89", "section": "Community Impact Stories", "quote": "SDG 11: Sustainable Cities & Communities; SDG 1: No Poverty"}}, {"label": "B", "value": 11, "value_qualifier": "exact", "unit": "sdg", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "89", "section": "Community Impact Stories", "quote": "SDG 16: Peace,Justice & Strong Institutions,SDG 11: Sustainable Cities & Communities"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-23', 'conflict', $qi_subject$Pétitions IHD : pays par geographic_area$qi_subject$, $qi_values$[{"label": "A", "value": [35, 45, 63, 48], "value_qualifier": "exact", "unit": "country_list", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "73", "section": "International Human Duties Initiative", "quote": "Asia and the Pacific 54,921 (81.85%) from 35 Countries \u2026 America 3,656 (5.45%) from 45 Countries \u2026 Africa and the Middle East 6,867 (10.23%) from 63 Countries \u2026 Europe 1,657 (2.47%) from 48 Countries"}}, {"label": "B", "value": 191, "value_qualifier": "exact", "unit": "country", "layer": "SEMANTIC_INTERPRETATION", "value_status": "calculated", "formula": "35 + 45 + 63 + 48", "inputs": ["ref:same_conflict.values"], "rule_id": "CALC-ARITH"}, {"label": "C", "value": 22, "value_qualifier": "exact", "unit": "national_organization", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "10", "section": "National Organizations", "quote": "America 22 (19.3%)"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-24', 'conflict', $qi_subject$Hétérogénéité des périodes de reporting$qi_subject$, $qi_values$[{"label": "A", "value": "2024\u20132025", "value_qualifier": "exact", "unit": "period", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "v", "section": "Executive Summary", "quote": "1,000+ projects implemented (2024\u20132025)"}}, {"label": "B", "value": "2025", "value_qualifier": "exact", "unit": "period", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "85", "section": "JCI RISE Projects", "quote": "Total Projects Reported for 2025"}}, {"label": "C", "value": "January\u2013October 2025", "value_qualifier": "exact", "unit": "period", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "17", "section": "Social Media Metrics", "quote": "From January to October 2025"}}, {"label": "D", "value": "October 2024\u2013August 2025", "value_qualifier": "exact", "unit": "period", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "96", "section": "JCI Foundation", "quote": "Total Contributions Received (USD) since October 2024 to August 2025"}}, {"label": "E", "value": "since 2022", "value_qualifier": "exact", "unit": "period", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "96", "section": "JCI Foundation", "quote": "Total Contributions Received (USD) since 2022"}}, {"label": "F", "value": "since October 6, 2025", "value_qualifier": "exact", "unit": "period", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "21", "section": "The New Face of JCI Online", "quote": "Since the October 6, 2025 launch alone"}}]$qi_values$::json, 'UNRESOLVED', true)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-25', 'conflict', $qi_subject$Part des membres d'America (graphique)$qi_subject$, $qi_values$[{"label": "A", "value": 0.08, "value_qualifier": "exact", "unit": "ratio", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "8", "section": "Membership Details", "quote": "America 11,775 8.0% 492 10.6%"}}, {"label": "B", "value": 0.8, "value_qualifier": "exact", "unit": "ratio", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "8", "section": "Membership Details", "quote": "America 11,775 (80%)"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('DQC-26', 'conflict', $qi_subject$Utilisateurs actifs de jci.cc$qi_subject$, $qi_values$[{"label": "A", "value": 8700, "value_qualifier": "at_least", "unit": "user", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "21", "section": "The New Face of JCI Online", "quote": "the website attracted more than 8,700 active users since its redesign launch from over 50 countries"}}, {"label": "B", "value": 13351, "value_qualifier": "exact", "unit": "user", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "statement_published", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "22", "section": "The New Face of JCI Online", "quote": "13,351 Total Active Users"}}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('VDX-01', 'visual', $qi_subject$Global Presence (114 Countries)$qi_subject$, $qi_values$[{"page": "9", "section": "International Presence \u2013 Operational Areas", "chart": {"value": "Global Presence (114 Countries)", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "chart_exists", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "9", "section": "International Presence \u2013 Operational Areas", "quote": "Global Presence (114 Countries)"}}, "missing": "Liste des pays / National Organizations repr\u00e9sent\u00e9s sur la carte", "value": null, "value_status": "visual_data_not_extracted"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('VDX-02', 'visual', $qi_subject$Participation in Conferences$qi_subject$, $qi_values$[{"page": "42", "section": "Trainings at Area Conferences and World Congress", "chart": {"value": "Participation in Conferences", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "chart_exists", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "42", "section": "Trainings at Area Conferences and World Congress", "quote": "Participation in Conferences"}}, "missing": "R\u00e9partition des 1,969 participants par conf\u00e9rence (libell\u00e9s pr\u00e9sents, valeurs absentes)", "value": null, "value_status": "visual_data_not_extracted"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('VDX-03', 'visual', $qi_subject$National Organization Attendances per Area Conference (2025)$qi_subject$, $qi_values$[{"page": "60", "section": "JCI Events Area Conferences and World Congress", "chart": {"value": "National Organization Attendances per Area Conference (2025)", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "chart_exists", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "60", "section": "JCI Events Area Conferences and World Congress", "quote": "National Organization Attendances per Area Conference (2025)"}}, "missing": "Toutes les valeurs", "value": null, "value_status": "visual_data_not_extracted"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('VDX-04', 'visual', $qi_subject$Primary SDGs Addressed / Secondary SDG$qi_subject$, $qi_values$[{"page": "84", "section": "Community Development Projects", "chart": {"value": "Primary SDGs Addressed / Secondary SDG", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "chart_exists", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "84", "section": "Community Development Projects", "quote": "Primary SDGs Addressed / Secondary SDG"}}, "missing": "Toutes les valeurs (distribution des ODD principaux et secondaires)", "value": null, "value_status": "visual_data_not_extracted"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('VDX-05', 'visual', $qi_subject$Amount of Grants (USD) Received per Year$qi_subject$, $qi_values$[{"page": "97", "section": "JCI Foundation Development Grants", "chart": {"value": "Amount of Grants (USD) Received per Year", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "chart_exists", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "97", "section": "JCI Foundation Development Grants", "quote": "Amount of Grants (USD) Received per Year"}}, "missing": "Association valeur \u2194 ann\u00e9e \u2194 geographic_area", "value": null, "value_status": "visual_data_not_extracted"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('VDX-06', 'visual', $qi_subject$Amount of Grants (USD) Received per Year / Number of Projects per Year per Area$qi_subject$, $qi_values$[{"page": "98", "section": "JCI Foundation", "chart": {"value": "Amount of Grants (USD) Received per Year / Number of Projects per Year per Area", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "chart_exists", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "98", "section": "JCI Foundation", "quote": "Amount of Grants (USD) Received per Year / Number of Projects per Year per Area"}}, "missing": "Association valeur \u2194 ann\u00e9e \u2194 geographic_area", "value": null, "value_status": "visual_data_not_extracted"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('VDX-07', 'visual', $qi_subject$RISE to the Challenge Attendees per Area$qi_subject$, $qi_values$[{"page": "118", "section": "Impact Through Hosted and Partner Events", "chart": {"value": "RISE to the Challenge Attendees per Area", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "chart_exists", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "118", "section": "Impact Through Hosted and Partner Events", "quote": "RISE to the Challenge Attendees per Area"}}, "missing": "Toutes les valeurs par geographic_area", "value": null, "value_status": "visual_data_not_extracted"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('VDX-08', 'visual', $qi_subject$Languages per Area$qi_subject$, $qi_values$[{"page": "118", "section": "Impact Through Hosted and Partner Events", "chart": {"value": "Languages per Area", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "chart_exists", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "118", "section": "Impact Through Hosted and Partner Events", "quote": "Languages per Area"}}, "missing": "Toutes les valeurs (libell\u00e9s Spanish, French, Japanese, English pr\u00e9sents)", "value": null, "value_status": "visual_data_not_extracted"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)
VALUES ('VDX-09', 'visual', $qi_subject$Gobal Youth Dialogue Attendees per Area$qi_subject$, $qi_values$[{"page": "123", "section": "Global Youth Dialogue 2025", "chart": {"value": "Gobal Youth Dialogue Attendees per Area", "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "fact_scope": "chart_exists", "source": {"origin": "jci_report_2025", "document": "JCI Impact Report 2025", "page": "123", "section": "Global Youth Dialogue 2025", "quote": "Gobal Youth Dialogue Attendees per Area"}}, "missing": "Toutes les valeurs par geographic_area", "value": null, "value_status": "visual_data_not_extracted"}]$qi_values$::json, 'UNRESOLVED', false)
ON CONFLICT (issue_id) DO NOTHING;

