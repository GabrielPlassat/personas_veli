# 🚲 Simulateur Vélis × Personas

**Outil open source d'aide à la décision pour la mobilité intermédiaire électrique en France rurale et périurbaine.**

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://simulateur-velis.streamlit.app)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/votre-pseudo/simulateur-velis/blob/main/personas_mobilite_200k.ipynb)
[![Dataset Nemotron](https://img.shields.io/badge/Dataset-Nemotron--Personas--France-blue)](https://huggingface.co/datasets/nvidia/Nemotron-Personas-France)
[![License CC BY 4.0](https://img.shields.io/badge/Personas-CC--BY--4.0-green)](https://creativecommons.org/licenses/by/4.0/)
[![EMP 2019](https://img.shields.io/badge/Mobilité-EMP%202019%20SDES%2FINSEE-orange)](https://www.statistiques.developpement-durable.gouv.fr/enquete-sur-la-mobilite-des-personnes-2018-2019)

---

## Présentation

Ce projet répond à une question concrète : **quel véhicule électrique intermédiaire concevoir pour réduire la dépendance à la voiture thermique des ménages modestes en zones rurales et périurbaines ?**

Il croise trois sources de données :

| Source | Contenu | Licence |
|---|---|---|
| [NVIDIA Nemotron-Personas-France](https://huggingface.co/datasets/nvidia/Nemotron-Personas-France) | 6M profils synthétiques · occupation, territoire, foyer, sport, voyages | CC-BY-4.0 |
| [EMP 2019, SDES/INSEE](https://www.statistiques.developpement-durable.gouv.fr/enquete-sur-la-mobilite-des-personnes-2018-2019) | 45 169 déplacements individuels réels · Q1+Q2 · rural+périurbain | Open data Etalab 2.0 |
| [Catalogue Vélis](https://wiki.lafabriquedesmobilites.fr/wiki/Catalogue_des_V%C3%A9hicules_Interm%C3%A9diaires) | 60 véhicules intermédiaires électriques · 47 Actifs / 13 Passifs | — |

---

## Fichiers du projet

```
simulateur-velis/
├── app.py                          Application Streamlit — 4 onglets (~1 700 lignes)
├── requirements.txt                streamlit · anthropic · pandas
├── personas_mobilite_200k.ipynb    Notebook Colab — génère personas enrichis + distributions
└── README.md                       Ce fichier
```

**À ne pas versionner** — ajouter au `.gitignore` :
```
.streamlit/secrets.toml
distributions_nemotron.json
personas_mobilite_200k.csv
__pycache__/
```

---

## Déploiement en 4 étapes

### 1. Forker ce dépôt sur GitHub

```
GitHub → Fork → votre-pseudo/simulateur-velis
```

### 2. Déployer sur Streamlit Cloud

```
share.streamlit.io → New app
→ Repository : votre-pseudo/simulateur-velis
→ Branch     : main
→ Main file  : app.py
→ Advanced settings → Secrets
```

### 3. Ajouter la clé API Anthropic

```toml
ANTHROPIC_API_KEY = "sk-ant-XXXXXXXXXXXXXXXX"
```

> Chiffrée par Streamlit — ne jamais la mettre dans `app.py` ou dans un commit.

### 4. Mettre à jour l'app

Modifier `app.py` sur GitHub (bouton crayon) → Streamlit redéploie en ~30 secondes.

---

## L'application — 4 onglets

### 🏠 Accueil

Page d'introduction présentant les 3 outils, les sources de données avec leurs licences, et le guide pour utiliser le notebook Colab. Contient le badge "Open in Colab" pour lancer directement le notebook.

---

### 🎯 Onglet 1 — Optimiseur des aides

**Question :** quels véhicules électriques concevoir pour toucher le maximum de ménages modestes en rural/périurbain, à coût minimal ?

**Principe :** 5 types de véhicules optimisés en parallèle. Pour chaque type, la catégorie et le mode de propulsion sont fixes ; l'autonomie et les places sont librement optimisées pour maximiser `personas atteints ÷ prix net`.

#### Les 5 types de véhicules

| Type | Catégorie | Vitesse max | Mode | Batterie préconisée | Profil cible principal |
|---|---|---|---|---|---|
| 🚴 VAE cargo | VAE/L1e | ≤ 25 km/h | Actif (pédalage) | 40–60 km | Cyclistes périurbains, trajets ≤ 20 km |
| 🚲 L6e Actif | L6e | ≤ 45 km/h | Actif (pédalage) | 60–80 km | Périurbain solo + famille |
| 🚗 L6e Passif | L6e | ≤ 45 km/h | Passif (moteur seul) | 60–80 km | Périurbain, seniors, sans permis |
| 🚙 L7e Passif | L7e | ≤ 90 km/h | Passif (moteur seul) | 80–100 km | Rural, routes nationales |
| 🛣️ L8e (hyp.) | L8e hypothétique | ≤ 110 km/h | Passif (moteur seul) | 80–100 km | Rural isolé, voies rapides |

> **Batterie préconisée** : standard industrie pour une autonomie commerciale confortable.  
> **Besoin estimé** (affiché dans les cartes) : calculé depuis les micro-données EMP 2019 pour la population cible.

#### Résultats indicatifs à 0 % d'aides (données EMP 2019 + CGDD/INSEE)

| Type | Besoin estimé | Places optimales | Prix net estimé | Personas ciblés |
|---|---|---|---|---|
| 🚴 VAE cargo | 20 km | 1 adulte + 2 enfants | ~4 400 € | ~97 000 (5 %) |
| 🚲 L6e Actif | 20 km | 1 adulte + 2 enfants | ~7 500 € | ~238 000 (12 %) |
| 🚗 L6e Passif | 20 km | 1 adulte + 2 enfants | ~7 500 € | ~238 000 (12 %) |
| 🚙 L7e Passif | 40 km | 1 adulte + 2 enfants | ~10 800 € | ~278 000 (14 %) |
| 🛣️ L8e hyp. | 30 km | 1 adulte + 2 enfants | ~11 800 € | ~184 000 (9 %) |

#### Le curseur "Aides publiques" (sidebar gauche — 0 à 20 %)

Le **seul curseur d'entrée** de l'onglet 1. Toujours visible en scrollant. Partagé avec l'onglet 3.

- Réduit le prix net de tous les véhicules
- Recalcule en temps réel les specs optimales, le nombre de personas atteints et le coût public des aides
- **Saut critique** : typiquement à 6–8 % d'aides, les profils ruraux qui nécessitent L7e deviennent accessibles → +100 000 personas d'un coup

#### Calcul du coût public des aides

Quand les aides > 0 %, un tableau affiche pour chaque type :

| Indicateur | Calcul |
|---|---|
| Aide par véhicule | Prix brut − prix net |
| Nombre de véhicules aidés | Personas atteints × taux de pénétration marché (1–10 %, second curseur) |
| Coût public total | Aide/véhicule × nombre de véhicules (en M€) |
| CO₂ économisé/an | Personas × CO₂ moyen voiture thermique EMP 2019 × 250 j/an (en ktCO₂) |
| Coût par tonne CO₂ évitée | Coût total / CO₂ économisé (en €/tCO₂) |

#### Transparence des données

| Donnée | Source | Statut |
|---|---|---|
| Distributions autonomie (`CUMUL_AUTO`) | EMP 2019 micro-données réelles | ✅ Réelles |
| Courbes budget (`AFFORD_PROFILES`) | CGDD/INSEE 2022, calibration par CSP | ⚠️ Estimées |
| Population cible (1,95M) | Extrapolation Nemotron × INSEE | ⚠️ Estimée |
| Parts des 6 profils archétypaux | Structure socio-démo France rurale | ⚠️ Estimées |

**Pour remplacer les estimations par les vraies valeurs Nemotron** → uploader `distributions_nemotron.json` dans la sidebar (généré par le notebook Colab, cellule 9d).

---

### 📊 Onglet 2 — Analyse par territoire

**Question :** pour chaque constructeur du catalogue Vélis, quels territoires et profils démographiques représentent les meilleures opportunités ?

**Différence avec l'onglet 1 :** l'onglet 1 cible les ménages modestes spécifiquement. L'onglet 2 analyse tous les segments de revenus sur des archétypes plus larges.

**30 archétypes** (5 territoires × 3 tranches d'âge × 2 profils sportif/standard) sont scorés sur les 60 véhicules.

#### Score /120

| Composante | Points | Critère |
|---|---|---|
| Budget | 30 | Ratio prix net / budget moyen du profil |
| Territoire / Vitesse | 40 | Compatibilité vitesse véhicule × type de zone |
| Usages | 30 | Fraction des besoins du profil couverts par les usages déclarés |
| Affinité | +20 | Signaux profil : cycliste → +8 VAE · tourisme → +4 · bricoleur → +8 |

Score ≥ 65/120 = **segment porteur**.

#### Ce que l'onglet affiche

- Heatmap globale constructeurs × territoires (score moyen)
- Top 5 véhicules par territoire (Urbain / Périurbain / Rural / Montagne / Île)
- Analyse par constructeur : heatmap territoire × segment, segments porteurs, Top 5 / Flop 5 personas

---

### 🔍 Onglet 3 — Simulateur personas × véhicules

**Question :** pour un profil de personne donné, quels véhicules Vélis correspondent le mieux à ses besoins, son budget et ses affinités ?

#### Les 15 personas intégrés

15 personas de démonstration extraits du dataset Nemotron et enrichis manuellement :

- Profils variés : urbain·e, périurbain·e, rural·e
- CSP : ouvrier·e, employé·e, retraité·e, artisan, étudiant·e
- Âges : 22 à 71 ans
- Enrichissements : profil culturel, sport, voyages, compétences, hobbies

#### Charger vos propres personas

Le notebook Colab génère `personas_mobilite_200k.csv` avec 200 000 personas enrichis. Une fois uploadé dans l'expander "📥 Charger des personas depuis Colab", les 15 personas de démonstration sont remplacés.

#### Le curseur "Aides publiques"

Le curseur de la **sidebar gauche** (partagé avec l'onglet 1) s'applique ici au calcul du prix net de chaque véhicule dans le scoring. Pas de second curseur.

#### Simulation IA

Bouton "Simuler la réaction" sur chaque véhicule → appel API Anthropic `claude-sonnet-4-20250514` → réaction à la 1ère personne du persona face au véhicule.

---

## Le notebook Colab — générer des données enrichies

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/votre-pseudo/simulateur-velis/blob/main/personas_mobilite_200k.ipynb)

### Pré-requis

- Compte Google (Colab gratuit)
- Aucune installation, aucun téléchargement préalable
- Durée : ~20 min

### Ce que fait le notebook

```
HuggingFace (6M personas Nemotron CC-BY-4.0)
        │
        ▼  Cellules 1–8 (~15 min) : stream + filtre + enrichissement
        │
        │  Filtre : low-income (Q1+Q2) · rural + périurbain
        │  Attributs EMP 2019 : km/jour · besoin autonomie · vitesse min
        │                       places · budget · CO₂ actuel
        │
        ▼
personas_mobilite_200k.csv   (~160 Mo · 200 000 lignes · 20 colonnes)
        │
        ├──→ Uploader dans onglet 3 (Simulateur personas)
        │    pour remplacer les 15 personas de démonstration
        │
        ▼  Cellules 9a–9d (~5 min) : calcul distributions
        │
distributions_nemotron.json  (<1 Mo · 6 profils)
        │
        └──→ Uploader dans la sidebar
             pour recalibrer l'onglet 1 (Optimiseur)
```

### Description des cellules

| Cellule | Action |
|---|---|
| 1 | Installation des dépendances |
| 2 | Paramètres : N_TARGET=200 000 · SCAN_MAX=2 000 000 · SEED |
| 3 | Référentiel mobilité EMP 2019 — 35 segments territoire × CSP |
| 4 | Mapping département → territoire · CSP Nemotron → CSP EMP |
| 5 | Attribution mobilité avec bruit log-normal calibré sur EMP 2019 |
| 6 | **Stream Nemotron** · filtre low-income rural+périurbain · enrichissement |
| 7 | Validation des distributions (histogrammes) |
| 8 | Export `personas_mobilite_200k.csv` + téléchargement |
| 9a | Vérification des colonnes du DataFrame |
| 9b | Définition des 6 profils archétypaux (dont profil cycliste VAE) |
| 9c | Calcul des distributions cumulatives CUMUL_AUTO et AFFORD_PROFILES |
| 9d | Export `distributions_nemotron.json` + téléchargement |

### Les 6 profils calculés

| Profil | Territoire | Critère | Onglet cible |
|---|---|---|---|
| `periurbain_cycliste` | Périurbain | solo · besoin ≤ 20 km · vit ≤ 25 km/h | 🚴 VAE cargo |
| `periurbain_solo` | Périurbain | solo · besoin > 20 km | 🚲🚗 L6e |
| `periurbain_famille` | Périurbain | ≥ 3 places | 🚲🚗 L6e |
| `rural_navetteur` | Rural | ≤ 2 places · autonomie < 60 km | 🚙 L7e |
| `rural_famille` | Rural | ≥ 3 places | 🚙 L7e |
| `rural_longue_dist` | Rural | autonomie ≥ 60 km | 🛣️ L8e |

### Ce que les fichiers changent dans l'app

| | Sans fichiers (défaut) | Avec `distributions_nemotron.json` | Avec `personas_mobilite_200k.csv` |
|---|---|---|---|
| **Onglet concerné** | — | 🎯 Onglet 1 | 🔍 Onglet 3 |
| Distributions autonomie | EMP 2019, 50–900 individus/profil | Milliers de personas Nemotron réels | — |
| Courbes budget | Calibration CGDD/INSEE estimée | Budget calculé par CSP × âge × décile INSEE | — |
| Population cible | 1,95M (estimation) | Décompte réel Nemotron | — |
| Parts des 6 profils | 8/12/25/28/20/7 % estimés | Calculées sur vrais personas | — |
| Personas affichés | 15 de démonstration | — | 200 000 Nemotron enrichis |

---

## Algorithme d'optimisation — Onglet 1

### Modèle de coût d'un véhicule théorique

```
Prix brut = (châssis + batterie + places) × marge

  Châssis  :  VAE 2 600 €  ·  L6e 3 500 €  ·  L7e 5 200 €  ·  L8e 6 400 €
  Batterie :  40 €/km d'autonomie (LFP 2025, pack complet)
  Places   :  +0 €(1)  ·  +650 €(2)  ·  +1 500 €(3)  ·  +2 700 €(4)
  Marge    :  × 1,30 (industrielle + distribution + homologation)

Spécification constructeur = autonomie optimale × 1,20 (marge sécurité batterie)
```

### Calcul des personas atteints

```
Pour chaque profil p (sur 6 profils archétypaux) :

  contribution = pct_pop × N_cible
               × P(besoin autonomie ≤ X km)   ← EMP 2019 ou Nemotron
               × P(vitesse suffisante)         ← binaire : vit ≥ vit_min_profil
               × P(places suffisantes)         ← binaire : places ≥ places_profil
               × P(budget ≥ prix_net)          ← CGDD/INSEE 2022 ou Nemotron

Total personas = Σ contributions sur les 6 profils
```

### Optimisation par type de véhicule

```
Variables fixes  : vitesse max · mode actif/passif
Variables libres : autonomie ∈ {10, 20, 30, 40, 50, 60, 80, 100, 120 km}
                   places    ∈ {1, 2, 3, 4}
Critère          : maximise  personas_atteints ÷ prix_net
```

---

## Algorithme de scoring — Onglet 3

### Score /120

```
Score total = Budget(30) + Territoire(40) + Usages(30) + Affinité(+20)
```

**Budget (30 pts)**

| Ratio prix net / budget persona | Points |
|---|---|
| ≤ 1× — dans le budget | 30 |
| ≤ 1,25× | 22 |
| ≤ 1,5× | 14 |
| ≤ 2× | 6 |
| > 2× | 0 |
| Prix inconnu | 12 (neutre) |

**Territoire / Vitesse (40 pts)**

| Urbanité \ Vitesse | ≤ 25 km/h | ≤ 45 km/h | > 45 km/h |
|---|---|---|---|
| Urbain | 40 | 35 | 28 |
| Périurbain | 8 | 38 | 40 |
| Rural | 0 | 22 | 40 |
| Montagne | 0 | 15 | 40 |
| Île | 8 | 28 | 40 |

**Usages (30 pts)** — fraction des besoins du persona couverts par les usages déclarés du véhicule.

**Affinité (+20 pts max)**

| Signal dans le profil persona | Condition véhicule | Bonus |
|---|---|---|
| Vélo/VTT dans sport ou hobbies | VAE ou L1eA | +8 pts |
| Tourisme/voyage dans travel | Usage "Tourisme" déclaré | +4 pts |
| Bricolage/mécanique dans skills | VAE (entretien autonome) | +8 pts |

---

## Architecture `app.py`

```
app.py (~1 700 lignes)
│
├── Imports + CSS global (dark sidebar, badges, cards)
│
├── DONNÉES GLOBALES
│   ├── PERSONAS[]              15 profils enrichis Nemotron
│   ├── VEHICLES[]              60 véhicules Vélis
│   ├── ACTIF_PASSIF{}          mapping nom → Actif/Passif (source Airtable)
│   ├── Fonctions scoring       affinity_score() · compute_score() · badge_info()
│   ├── _CUMUL_AUTO_DEFAULT{}   distributions autonomie EMP 2019 (5 profils)
│   ├── _AFFORD_PROFILES_DEFAULT{} courbes budget CGDD/INSEE (5 profils)
│   ├── CUMUL_AUTO / AFFORD_PROFILES  (actifs, remplaçables par upload JSON)
│   ├── VEHICLE_TYPES_T3[]      5 types de véhicules (portée globale)
│   ├── PROFILES_T3[]           6 profils archétypaux (portée globale)
│   └── Fonctions optimiseur    interp() · prix_brut() · reach_t3() · optimize_type()
│
├── SESSION STATE               personas_csv · personas_source · reactions
│
├── SIDEBAR (toujours visible)
│   ├── Curseur aides (0–20 %)  partagé onglets 1 et 3 · clé aide_global
│   └── Upload JSON Nemotron    recalibre onglet 1 · expander explicatif
│
├── tab_home — 🏠 Accueil
│   ├── Présentation des 3 outils
│   ├── Sources de données + licences
│   └── Guide Colab + badge Open in Colab
│
├── tab1 — 🎯 Optimiseur des aides
│   ├── Expander méthode de calcul
│   ├── 5 cartes véhicules (batterie 80-100km + besoin estimé)
│   ├── Barre de couverture par profil
│   ├── Détail onglets par type de véhicule
│   ├── Tableau coût public des aides (M€ · CO₂ · €/tCO₂)
│   └── Récapitulatif cahier des charges
│
├── tab2 — 📊 Analyse par territoire
│   ├── Expander "Comment lire ces analyses"
│   ├── Heatmap constructeurs × territoires
│   ├── Top 5 véhicules par territoire
│   └── Analyse par constructeur (heatmap · Top5/Flop5)
│
└── tab3 — 🔍 Simulateur personas
    ├── Expander "Qu'est-ce qu'un persona ?"
    ├── Upload CSV Colab (200k personas)
    ├── Colonne gauche : sélecteur 15 personas (ou CSV)
    └── Colonne droite : score véhicules · réaction IA Claude
```

---

## Évolutions possibles

- **Airtable temps réel** : connexion API → catalogue mis à jour sans re-export CSV
- **Loyer mensuel** : afficher l'équivalent crédit 5 ans en alternative au prix d'achat
- **Carte géographique** : scores par département (plotly choropleth)
- **Aides territoriales réelles** : intégrer les aides variables par région/commune (ADEME, régions)
- **Comparateur véhicules** : face à face 2–3 véhicules pour un persona donné
- **ENTD 2008** : comparer les tendances mobilité 2008 vs 2019 (données présentes dans le projet)
- **Export résultats** : CSV des meilleurs matchs · PDF cahier des charges constructeur

---

## Contribuer

Les contributions sont bienvenues, notamment :

- Mise à jour du catalogue Vélis (nouveaux véhicules)
- Amélioration du modèle de coût (`BASE_CHASSIS`, `BATT_COST_KM`)
- Nouvelles données mobilité (enquêtes régionales, EMD)
- Traductions (EN, DE, ES)

Ouvrir une **issue** ou une **pull request** sur ce dépôt.

---

## Licence et crédits

| Composant | Source | Licence |
|---|---|---|
| Personas synthétiques | [NVIDIA Nemotron-Personas-France](https://huggingface.co/datasets/nvidia/Nemotron-Personas-France) | CC-BY-4.0 |
| Données mobilité | [EMP 2019, SDES/INSEE](https://www.statistiques.developpement-durable.gouv.fr) | Open data Etalab 2.0 |
| Données budget | CGDD/INSEE 2022 | Open data Etalab 2.0 |
| Véhicules | [Catalogue Vélis / La Fabrique des Mobilités](https://wiki.lafabriquedesmobilites.fr) | — |
| LLM | Anthropic Claude `claude-sonnet-4-20250514` | API commerciale |
| Framework | [Streamlit](https://streamlit.io) | Apache 2.0 |

Développé dans le cadre d'un POC mobilité douce avec [Claude (Anthropic)](https://claude.ai).
