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
├── app.py                          Application Streamlit — 4 onglets (~1 900 lignes)
├── requirements.txt                streamlit · anthropic · pandas
├── personas_mobilite_200k.ipynb    Notebook Colab — génère les données avancées
└── README.md                       Ce fichier
```

**`.gitignore` recommandé :**
```
.streamlit/secrets.toml
distributions_nemotron.json
personas_mobilite_200k.csv
__pycache__/
```

---

## Déploiement

### 1. Forker et déployer sur Streamlit Cloud

```
GitHub → Fork → votre-pseudo/simulateur-velis

share.streamlit.io → New app
→ Repository : votre-pseudo/simulateur-velis
→ Main file  : app.py
→ Advanced settings → Secrets :
    ANTHROPIC_API_KEY = "sk-ant-XXXXXXXXXXXXXXXX"
```

### 2. Mettre à jour

Modifier `app.py` sur GitHub → Streamlit redéploie en ~30 secondes.

---

## L'application — 4 onglets

### 🏠 Accueil

Introduction au projet, présentation des 3 outils, sources de données avec leurs licences, et **explication détaillée du notebook Colab** avec le schéma du flux complet.

---

### 🎯 Onglet 1 — Optimiseur des aides

**Question :** quels véhicules électriques concevoir pour toucher le maximum de ménages modestes en rural/périurbain, à coût minimal ?

**5 types de véhicules** optimisés en parallèle. Pour chaque type, la catégorie et le mode de propulsion sont fixes ; l'autonomie et les places sont calculées automatiquement pour maximiser `personas atteints ÷ prix net`.

#### Les 5 types de véhicules

| Type | Catégorie | Vitesse | Mode | Batterie préconisée | Profil cible |
|---|---|---|---|---|---|
| 🚴 VAE cargo | VAE/L1e | ≤ 25 km/h | Actif | 40–60 km | Cyclistes périurbains |
| 🚲 L6e Actif | L6e | ≤ 45 km/h | Actif | 60–80 km | Périurbain solo + famille |
| 🚗 L6e Passif | L6e | ≤ 45 km/h | Passif | 60–80 km | Périurbain, seniors |
| 🚙 L7e Passif | L7e | ≤ 90 km/h | Passif | 80–100 km | Rural, routes nationales |
| 🛣️ L8e (hyp.) | L8e hypothétique | ≤ 110 km/h | Passif | 80–100 km | Rural isolé, voies rapides |

> La **batterie préconisée** est le standard industrie pour une autonomie commerciale confortable.
> Le **besoin estimé** (affiché dans les cartes) est calculé depuis les micro-données EMP 2019
> pour la population cible (trajets réels × 2 aller-retour × 1,15 de marge).

#### Le curseur unique : Aides publiques (sidebar, 0–20 %)

Toujours visible en scrollant. Partagé avec l'onglet 3. Recalcule en temps réel :
- Les specs optimales de chaque véhicule
- Le nombre de personas atteints par type
- Le coût public des aides (M€) et le CO₂ économisé (ktCO₂/an)

**Saut critique :** typiquement à 6–8 % d'aides, les profils ruraux qui nécessitent L7e deviennent accessibles → +100 000 personas d'un coup.

#### Résultats avec les données Nemotron réelles (200 000 ruraux)

| Profil | Personas Nemotron | Médiane autonomie | Médiane budget |
|---|---|---|---|
| Rural · famille | 144 948 (72 %) | 25 km | 8 500 € |
| Rural · navetteur | 49 808 (25 %) | 19 km | 7 650 € |
| Rural · longue dist. | 5 244 (3 %) | 79 km | 8 500 € |
| Périurbains (3 profils) | 0 * | — | — |

*\* Le filtre low-income Q1+Q2 de Nemotron ne capture que des ruraux dans l'échantillon actuel.
Les 3 profils périurbains utilisent les distributions EMP 2019 par défaut.*

**Rural · longue distance : profil structurellement non couvert.** Ces personas ont besoin de
80–140 km d'autonomie mais leur budget est ~9 000 €. Un L7e 80 km coûte ~11 800 € brut.
L'écart est structurel : il faudrait des aides ≥ 20 % ou une baisse du coût des batteries.

#### Transparence des données

| Donnée | Source | Statut |
|---|---|---|
| Distributions autonomie (`CUMUL_AUTO`) | EMP 2019 micro-données · ou Nemotron si JSON uploadé | ✅ Réelles |
| Courbes budget (`AFFORD_PROFILES`) | CGDD/INSEE 2022 · ou Nemotron si JSON uploadé | ⚠️ Estimées par défaut |
| Population cible (1,95M) | Extrapolation Nemotron × INSEE | ⚠️ Estimée |
| Parts des 6 profils archétypaux | Structure socio-démo France rurale | ⚠️ Estimées par défaut |

---

### 📊 Onglet 2 — Analyse par territoire

**Question :** pour chaque constructeur du catalogue Vélis, quels territoires et profils démographiques représentent les meilleures opportunités ?

30 archétypes (5 territoires × 3 âges × 2 profils sportif/standard) scorés sur les 60 véhicules. Score /120 = Budget(30) + Territoire/Vitesse(40) + Usages(30) + Affinité(+20).

---

### 🔍 Onglet 3 — Simulateur personas × véhicules

**Question :** pour un profil de personne donné, quels véhicules Vélis correspondent le mieux ?

15 personas de démonstration intégrés (Nemotron enrichis). Uploadez le CSV Colab pour travailler avec 200 000 personas réels. Score /120 avec barres détaillées et simulation de réaction IA (Claude).

---

## Le notebook Colab en détail

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/votre-pseudo/simulateur-velis/blob/main/personas_mobilite_200k.ipynb)

**Pré-requis :** compte Google uniquement. Durée : ~20 min. GPU non requis.

### Pourquoi l'utiliser ?

Par défaut, l'application utilise des estimations calibrées (EMP 2019 + CGDD/INSEE).
Le notebook permet de **remplacer ces estimations par des données calculées sur les 6M vrais personas Nemotron**.

Il produit deux fichiers :

```
personas_mobilite_200k.csv  → onglet 3 (Simulateur)
distributions_nemotron.json → sidebar onglet 1 (Optimiseur)
```

### Étapes 1–8 : génération du CSV (200 000 personas enrichis)

Le notebook scanne les personas Nemotron **en streaming** (sans télécharger les 6M d'un coup)
et applique deux filtres :

**Filtre 1 — Faibles revenus** : occupation de type ouvrier, employé, retraité, artisan,
agriculteur, aide-soignant, livreur… (professions modestes Q1+Q2).
Les cadres supérieurs, médecins, directeurs, associés sont exclus.

**Filtre 2 — Territoire rural ou périurbain** : département classé selon la densité communale INSEE.
*Note : dans l'échantillon actuel, le filtre low-income ne produit que des ruraux.*

Pour chaque persona retenu, le notebook attribue des statistiques de mobilité issues des
**micro-données EMP 2019** (35 segments territoire × CSP), avec un bruit log-normal calibré
pour reproduire la dispersion observée :

| Colonne | Méthode | Exemple (rural ouvrier 40 ans) |
|---|---|---|
| `km_jour` | EMP 2019 · distribution log-normale | 31 km/jour médian |
| `besoin_autonomie_km` | trajet max × 1,15 | 24 km P50 · 40 km P75 · 66 km P90 |
| `vitesse_min_kmh` | Logique routière par territoire | 90 km/h (rural) |
| `places_besoin` | Nemotron `household_type` | 3 (foyer avec enfants) |
| `budget_achat_eur` | CSP × âge × décile INSEE | 8 500 € médian |
| `co2_actuel_g_jour` | km_jour × ratio CO₂ EMP 2019 | 5 425 gCO₂/jour |

**Résultats observés (version actuelle) :**

```
200 000 personas collectés / 213 449 scannés

Répartition CSP :
  employés       113 873 (57 %)
  retraités       51 277 (26 %)
  ouvriers        25 858 (13 %)
  artisans         7 409  (4 %)
  agriculteurs     1 583  (1 %)

Stats mobilité (médiane) :
  km/jour          : 31 km
  Autonomie P50    : 24 km  · P75 : 40 km  · P90 : 66 km
  Vitesse min      : 90 km/h (100 % rural)
  Places besoin    : 3
  Budget médian    : 8 500 €
  CO₂ actuel/j     : 5 425 gCO₂/personne
```

### Étapes 9a–9d : calcul des distributions pour l'Optimiseur

Le notebook calcule pour chaque profil archétypal deux distributions cumulatives :

**`CUMUL_AUTO`** — P(besoin_autonomie ≤ X km) : quelle fraction du profil est couverte
par un véhicule d'autonomie X km ?

**`AFFORD_PROFILES`** — P(budget ≥ prix_net) : quelle fraction peut financer un véhicule
au prix net donné ?

| Profil | Autonomie P50 | Autonomie P75 | Budget P(≥8k€) |
|---|---|---|---|
| Rural · famille (72 %) | 25 km | 42 km | 77 % |
| Rural · navetteur (25 %) | 19 km | 30 km | 48 % |
| Rural · longue dist. (3 %) | 79 km | 104 km | 71 % |
| Périurbains (3 profils) | — (0 personas) | — | — |

**Si un profil est vide** (0 personas dans l'échantillon, typiquement les périurbains) :
l'app conserve automatiquement les valeurs EMP 2019 et affiche un avertissement.

### Schéma du flux complet

```
HuggingFace (6M personas Nemotron CC-BY-4.0)
        │
        ▼  Étapes 1–8 : stream 2M personas · filtre · enrichissement EMP 2019
        │
personas_mobilite_200k.csv  (200 000 lignes · 166 Mo · 25 colonnes)
   uuid · prenom · age · commune · occupation · csp · household_type
   km_jour · besoin_autonomie_km · vitesse_min_kmh · places_besoin
   budget_achat_eur · co2_actuel_g_jour · ...
        │
        ├─────────────────────────────────────────────────────────
        │                                                         │
        ▼  Upload onglet 3                    ▼  Étapes 9a–9d
        │                                                         │
🔍 Simulateur personas              distributions_nemotron.json
   Remplace les 15 personas          CUMUL_AUTO + AFFORD_PROFILES
   par 200 000 vrais personas        (distributions cumulatives réelles)
                                                  │
                                                  ▼  Upload sidebar
                                     🎯 Optimiseur recalibré
                                        sur les vrais personas Nemotron
```

### Comment utiliser les fichiers dans l'app

**`personas_mobilite_200k.csv` → Onglet 3 (Simulateur)**
```
Onglet 🔍 Simulateur personas
→ Expander "📥 Charger des personas depuis Colab"
→ Browse files → personas_mobilite_200k.csv
```

**`distributions_nemotron.json` → Sidebar (Onglet 1)**
```
Sidebar gauche → "📥 Données Nemotron avancées"
→ Browse files → distributions_nemotron.json
```
Un message indique quels profils sont actifs (Nemotron) et lesquels conservent EMP 2019.

### Description des 16 cellules

| Cellule | Titre | Action |
|---|---|---|
| 1 | Installation | `pip install datasets huggingface_hub pandas tqdm` |
| 2 | Paramètres | N_TARGET=200 000 · SCAN_MAX=2 000 000 · OUTPUT_FILE |
| 3 | Référentiel EMP 2019 | Table de 35 segments territoire × CSP (données réelles) |
| 4 | Mapping territoire + CSP | Département → rural/périurbain · occupation → CSP EMP |
| 5 | Fonctions mobilité | Attribution stats EMP 2019 avec bruit log-normal calibré |
| 6 | **Stream Nemotron** | Filtre low-income + rural · enrichissement · collecte |
| 7 | Validation | Histogrammes des distributions générées |
| 8 | Export CSV | `personas_mobilite_200k.csv` + téléchargement |
| 9a | Vérification | Contrôle des colonnes du DataFrame |
| 9b | 6 profils | Définition des filtres (territoire × places × autonomie) |
| 9c | Distributions | Calcul CUMUL_AUTO et AFFORD_PROFILES par profil |
| 9d | Export JSON | `distributions_nemotron.json` + téléchargement |

---

## Algorithme d'optimisation (Onglet 1)

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
Pour chaque profil p (6 profils archétypaux) :

  contribution =
    pct_pop
    × N_cible
    × P(besoin_autonomie ≤ X km)   ← EMP 2019 ou Nemotron (CUMUL_AUTO)
    × P(vitesse suffisante)         ← binaire : vit_véhicule ≥ vit_min_profil
    × P(places suffisantes)         ← binaire : places ≥ places_profil
    × P(budget ≥ prix_net)          ← CGDD/INSEE ou Nemotron (AFFORD_PROFILES)

Total = Σ contributions sur les 6 profils
```

### Optimisation par type

```
Variables fixes  : vitesse max · mode actif/passif
Variables libres : autonomie ∈ {10…120 km} × places ∈ {1…4}
Critère          : maximise personas_atteints ÷ prix_net
```

---

## Algorithme de scoring (Onglet 3)

```
Score /120 = Budget(30) + Territoire/Vitesse(40) + Usages(30) + Affinité(+20)
```

| Composante | Critère |
|---|---|
| Budget (30 pts) | Ratio prix net / budget persona → 0 à 30 pts |
| Territoire/Vitesse (40 pts) | Compatibilité vitesse × urbanité |
| Usages (30 pts) | Fraction des besoins couverts par le véhicule |
| Affinité (+20 pts) | Vélo → +8 pts VAE · Tourisme → +4 pts · Bricolage → +8 pts |

---

## Architecture `app.py`

```
app.py (~1 900 lignes)
│
├── Imports + CSS (dark sidebar, badges, cards)
│
├── DONNÉES GLOBALES
│   ├── PERSONAS[]              15 profils enrichis Nemotron
│   ├── VEHICLES[]              60 véhicules Vélis
│   ├── ACTIF_PASSIF{}          source Airtable réelle
│   ├── Fonctions scoring       compute_score() · affinity_score()
│   ├── _CUMUL_AUTO_DEFAULT{}   EMP 2019 (portée globale)
│   ├── _AFFORD_PROFILES_DEFAULT{} CGDD/INSEE (portée globale)
│   ├── CUMUL_AUTO / AFFORD_PROFILES (remplaçables par JSON)
│   ├── VEHICLE_TYPES_T3[]      5 types (portée globale)
│   ├── PROFILES_T3[]           6 profils (portée globale)
│   └── Fonctions optimiseur    interp() · prix_brut() · reach_t3() · optimize_type()
│
├── SESSION STATE               personas_csv · personas_source · reactions
│
├── SIDEBAR (toujours visible)
│   ├── Curseur aides (0–20 %)  partagé onglets 1 et 3
│   └── Upload JSON Nemotron    validation anti-zéro · expander explicatif
│
├── tab_home — 🏠 Accueil
│   ├── Présentation 3 outils
│   ├── Sources de données
│   └── Explication Colab détaillée (tableau, schéma, flux)
│
├── tab1 — 🎯 Optimiseur des aides
│   ├── Expander méthode de calcul
│   ├── 5 cartes véhicules (batterie standard + besoin estimé)
│   ├── Couverture cumulée par profil (barres empilées)
│   ├── Analyse structurelle rural_longue_dist si non couvert
│   ├── Détail onglets par type de véhicule
│   ├── Coût public des aides (M€ · CO₂ · €/tCO₂)
│   └── Récapitulatif cahier des charges
│
├── tab2 — 📊 Analyse par territoire
│   ├── Heatmap constructeurs × territoires
│   ├── Top 5 véhicules par territoire
│   └── Analyse par constructeur
│
└── tab3 — 🔍 Simulateur personas
    ├── Expander "Qu'est-ce qu'un persona ?"
    ├── Upload CSV Colab (200k personas)
    ├── Col. gauche : sélecteur personas
    └── Col. droite : score véhicules · réaction IA
```

---

## Évolutions possibles

- **Périurbains dans Nemotron** : modifier `is_low_income()` pour inclure plus de profils périurbains (ex. intérimaires, contrats courts en banlieue)
- **Loyer mensuel** : afficher l'équivalent crédit 5 ans
- **Carte géographique** : scores par département (plotly choropleth)
- **Aides territoriales réelles** : ADEME, régions, communes
- **Comparateur véhicules** : face à face 2–3 véhicules

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

Développé avec [Claude (Anthropic)](https://claude.ai).
