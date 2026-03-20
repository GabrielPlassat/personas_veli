# 🚲 Simulateur Vélis × Personas — Optimiseur de mobilité douce

> POC d'aide à la décision pour la mobilité intermédiaire en France rurale et périurbaine.  
> Croise le dataset NVIDIA Nemotron-Personas-France (6M profils synthétiques), le catalogue Vélis (60 véhicules), les micro-données EMP 2019 (SDES/INSEE) et une logique d'optimisation inverse pour définir les véhicules électriques idéaux selon les territoires.

---

## Fichiers du projet

```
simulateur-velis/
├── app.py                              ← Application Streamlit principale (3 onglets)
├── requirements.txt                    ← Dépendances Python
├── personas_mobilite_500k.ipynb        ← Notebook Colab : génère 500k personas enrichis
│                                          + calcule les distributions pour l'onglet 3
└── README.md                           ← Ce fichier
```

---

## Déploiement Streamlit Cloud

### 1. Créer le dépôt GitHub

```
GitHub → New repository → "simulateur-velis" → Create
Add file → Upload : app.py · requirements.txt
```

### 2. Déployer sur Streamlit Cloud

```
share.streamlit.io → New app
→ Repository : votre-pseudo/simulateur-velis
→ Branch     : main
→ Main file  : app.py
→ Advanced settings → Secrets
```

### 3. Ajouter la clé API Anthropic (Secrets)

```toml
ANTHROPIC_API_KEY = "sk-ant-XXXXXXXXXXXXXXXX"
```

> La clé est chiffrée par Streamlit — ne jamais la mettre dans `app.py`.

### 4. Mettre à jour l'app

Modifier `app.py` sur GitHub (bouton crayon) → Streamlit redéploie automatiquement en ~30 secondes.

---

## Les 3 onglets

### Onglet 1 — 🔍 Simulateur personas × véhicules

**Objectif** : pour un persona donné, quels véhicules Vélis sont les mieux adaptés ?

**Fonctionnement :**
- Sélectionner un persona dans la sidebar (15 intégrés, ou CSV uploadé depuis Colab)
- Ajuster le budget (1 000 – 40 000 €) et les aides publiques (0 – 20 %)
- Filtrer par vitesse, motorisation (Actif/Passif), financement
- Chaque véhicule reçoit un score /120 : Budget (30) + Territoire (40) + Usages (30) + Affinité profil (+20)
- Bouton **"Simuler la réaction"** → API Anthropic `claude-sonnet-4-20250514`, réaction à la 1ère personne

**Données :** 15 personas enrichis Nemotron + 60 véhicules Vélis (export Airtable).

---

### Onglet 2 — 📊 Analyse constructeurs × territoires

**Objectif** : pour un constructeur Vélis, quels territoires et profils représentent les meilleures opportunités ?

**Fonctionnement :**
- 30 archétypes (5 territoires × 3 âges × 2 profils) scorés sur 60 véhicules
- Heatmap globale constructeurs × territoires
- Top 5 véhicules par territoire
- Analyse par constructeur : heatmap · segments porteurs ≥65/100
- Top 5 / Flop 5 personas réels avec indicateurs explicatifs

---

### Onglet 3 — 🎯 Optimiseur véhicule (reverse engineering EMP 2019)

**Objectif** : quels véhicules électriques concevoir pour couvrir le maximum de personas à faibles revenus en rural/périurbain, à coût minimal ?

**Principe :** au lieu d'un véhicule universel, **5 types de véhicules distincts** sont optimisés en parallèle, chacun pour des cas d'usage différents. Pour chaque type, l'autonomie et le nombre de places sont optimisés librement.

#### Les 5 types de véhicules

| Type | Catégorie | Vitesse max | Pédalage | Profils cibles |
|---|---|---|---|---|
| 🚴 VAE cargo | VAE / L1e | ≤ 25 km/h | Actif | Périurbain cycliste (trajets ≤ 20 km) |
| 🚲 L6e Actif | L6e | ≤ 45 km/h | Actif | Périurbain solo + famille |
| 🚗 L6e Passif | L6e | ≤ 45 km/h | Passif | Périurbain, seniors, sans permis |
| 🚙 L7e Passif | L7e | ≤ 90 km/h | Passif | Rural navetteur + famille |
| 🛣️ L8e (hyp.) | L8e hypothétique | ≤ 110 km/h | Passif | Rural isolé, voies rapides |

#### Résultats à 0 % d'aides (EMP 2019 + CGDD/INSEE)

| Type | Autonomie | Places | Prix net | Personas | % cibles |
|---|---|---|---|---|---|
| 🚴 VAE cargo | 20 km | 1 adulte | 4 400 € | ~97 000 | 5 % |
| 🚲 L6e Actif | 20 km | 1+2 enfants | 7 500 € | ~238 000 | 12 % |
| 🚗 L6e Passif | 20 km | 1+2 enfants | 7 500 € | ~238 000 | 12 % |
| 🚙 L7e Passif | 40 km | 1+2 enfants | 10 800 € | ~278 000 | 14 % |
| 🛣️ L8e hyp. | 30 km | 1+2 enfants | 11 800 € | ~184 000 | 9 % |

#### L'unique curseur : Aides publiques (sidebar, 0–20 %)

Toujours visible en scrollant. Recalcule en temps réel :
- Les specs optimales de chaque véhicule (autonomie + places)
- Le nombre de personas atteints par type
- Le **coût public des aides** (tableau avec taux de pénétration de marché)

#### Calcul du coût public des aides

Quand les aides > 0 %, un 2ème curseur "Taux de pénétration du marché" (1–10 %) apparaît. Le tableau affiche pour chaque type :

| Colonne | Description |
|---|---|
| Aide/véhicule | Prix brut − prix net |
| Nb véhicules | Personas atteints × taux de pénétration |
| Coût public | Aide/veh × nb véhicules (en M€) |
| CO₂ économisé/an | Personas × CO₂ actuel EMP 2019 × 250j/an |

Et les métriques synthétiques : **coût total M€**, **CO₂ économisé ktCO₂/an**, **coût/tCO₂ évité**, **nb véhicules aidés**.

#### ⚠️ Transparence sur les données

| Source | Statut |
|---|---|
| Distributions autonomie (CUMUL_AUTO) | ✅ **Réelles** — EMP 2019 micro-données, 50–900 individus/profil |
| Courbes budgétaires (AFFORD_PROFILES) | ⚠️ **Estimées** — CGDD/INSEE 2022, calibration par CSP |
| Population cible (1,95M) | ⚠️ **Estimée** — 6M × fraction low-income × fraction rural+périurbain |
| Parts des 6 profils | ⚠️ **Estimées** — 8/12/25/28/20/7 % |
| Profil cycliste (VAE) | ⚠️ **Hardcodé** — profil futur, pas mesuré dans EMP 2019 |

**Pour remplacer les estimations par les vraies valeurs Nemotron** → voir la section Colab ci-dessous.

---

## Flux Colab → Onglet 3 : les vraies distributions Nemotron

### Pourquoi c'est important

Par défaut, l'optimiseur utilise des estimations calibrées. Le notebook Colab permet de calculer les distributions depuis les **6M vrais personas Nemotron** enrichis des données EMP 2019.

### Étape 1 — Ouvrir le notebook dans Colab

```
Google Colab → Fichier → Importer → Upload → personas_mobilite_500k.ipynb
```

Paramètres en cellule 2 :
```python
N_TARGET  = 500_000   # personas à générer (max recommandé)
SCAN_MAX  = 4_000_000 # lignes Nemotron à scanner (~40 min)
```

Lancer : **Runtime → Run all**

### Ce que fait le notebook

**Cellules 1–8 : génération des 500k personas enrichis**

| Cellule | Action |
|---|---|
| 1 | Installation des dépendances |
| 2 | Paramètres (N_TARGET, SCAN_MAX, SEED) |
| 3 | Référentiel mobilité EMP 2019 (35 segments territoire × CSP) |
| 4 | Mapping département → territoire + CSP Nemotron → CSP EMP |
| 5 | Fonctions d'attribution mobilité avec bruit log-normal calibré |
| 6 | Streaming Nemotron HuggingFace + filtre low-income + enrichissement |
| 7 | Validation des distributions (histogrammes) |
| 8 | Export `personas_mobilite_500k.csv` + téléchargement |

**Cellules 9a–9d : calcul des distributions pour l'onglet 3**

| Cellule | Action |
|---|---|
| 9a | Vérification des colonnes du DataFrame |
| 9b | Définition des **6 profils archétypaux** (dont le nouveau profil cycliste VAE) |
| 9c | Calcul des distributions cumulatives CUMUL_AUTO et AFFORD_PROFILES |
| 9d | Export `distributions_nemotron.json` + téléchargement |

### Les 6 profils calculés par le Colab

| Profil | Territoire | Critère de sélection | Véhicule cible |
|---|---|---|---|
| `periurbain_cycliste` | Périurbain | solo + besoin ≤ 20 km + vit ≤ 25 km/h | 🚴 VAE cargo |
| `periurbain_solo` | Périurbain | solo + besoin > 20 km | 🚲🚗 L6e |
| `periurbain_famille` | Périurbain | ≥ 3 places | 🚲🚗 L6e |
| `rural_navetteur` | Rural | ≤ 2 places + autonomie < 60 km | 🚙 L7e |
| `rural_famille` | Rural | ≥ 3 places | 🚙 L7e |
| `rural_longue_dist` | Rural | autonomie ≥ 60 km | 🛣️ L8e |

> **Si le profil cycliste est absent du JSON** (trop peu de personas correspondants) :
> l'app utilise automatiquement les valeurs hardcodées dans `app.py` — c'est normal,
> ce profil représente une adoption future pas encore mesurée dans EMP 2019.

### Étape 2 — Charger dans Streamlit

```
App Streamlit → Onglet 🎯 Optimiseur véhicule
→ Sidebar gauche → "📥 Distributions Nemotron"
→ Browse files → sélectionner distributions_nemotron.json
```

Statut affiché : `✅ Nemotron chargé · X personas`

### Ce que le JSON change

| Donnée | Sans JSON (défaut) | Avec JSON Nemotron |
|---|---|---|
| Distributions autonomie | EMP 2019, 50–900 individus/profil | Calculées sur des milliers de personas Nemotron |
| Courbes budget | Calibration CGDD/INSEE estimée | Budget calculé par CSP × âge × décile INSEE réel |
| Population cible | 1,95M (estimation) | Décompte réel des personas filtrés |
| Parts des profils | 8/12/25/28/20/7 % (estimées) | Calculées sur la vraie distribution Nemotron |
| Profil cycliste VAE | Hardcodé app.py | Remplacé par données Nemotron si présent |

### Flux complet en schéma

```
HuggingFace (6M personas Nemotron CC-BY-4.0)
        ↓  Cellules 1-8 (~40 min sur Colab)
personas_mobilite_500k.csv
  500k lignes · colonnes : territoire, csp, km_jour,
  besoin_autonomie_km, vitesse_min_kmh, places_besoin,
  budget_achat_eur, co2_actuel_g_jour
        ↓  Cellules 9a-9d (~5 min)
distributions_nemotron.json
  CUMUL_AUTO     : {profil → {km → P(besoin ≤ km)}}
  AFFORD_PROFILES: {profil → {prix → P(budget ≥ prix)}}
  n_cible_nemotron, profil_pct, profil_sizes
        ↓  Upload sidebar onglet 3
Optimiseur recalibré sur les 6M vrais personas Nemotron
```

---

## Algorithme de scoring — Onglets 1 et 2

Score total **/120** = base /100 + bonus affinité /20.

### Budget — 30 pts

| Ratio prix net / budget persona | Points |
|---|---|
| ≤ 1× (dans le budget) | 30 |
| ≤ 1,25× | 22 |
| ≤ 1,5× | 14 |
| ≤ 2× | 6 |
| > 2× | 0 |
| Prix inconnu | 12 (neutre) |

### Territoire / Vitesse — 40 pts

| Urbanité \ Vitesse véhicule | ≤ 25 km/h | ≤ 45 km/h | > 45 km/h |
|---|---|---|---|
| Urbain | 40 | 35 | 28 |
| Périurbain | 8 | 38 | 40 |
| Rural | 0 | 22 | 40 |
| Montagne | 0 | 15 | 40 |
| Île | 8 | 28 | 40 |

### Usages — 30 pts

Fraction des besoins du persona couverts par les usages déclarés du véhicule.

### Bonus affinité — +20 pts max

| Signal dans le profil | Condition véhicule | Bonus |
|---|---|---|
| Vélo/VTT dans sport ou hobbies | VAE ou L1eA | +8 pts |
| Tourisme/voyage dans travel | Usage "Tourisme" déclaré | +4 pts |
| Bricolage/mécanique dans skills | VAE (entretien autonome) | +8 pts |

---

## Algorithme d'optimisation — Onglet 3

### Modèle de coût d'un véhicule théorique

```
Prix brut = (châssis + batterie + places) × marge
  Châssis  : VAE 2 600 € · L6e 3 500 € · L7e 5 200 € · L8e 6 400 €
  Batterie : 40 €/km d'autonomie (LFP 2025, pack complet)
  Places   : +0 € (1) · +650 € (2) · +1 500 € (3) · +2 700 € (4)
  Marge    : × 1,30 (industrielle + distribution + homologation)
```

Spécification constructeur recommandée = autonomie optimale × 1,20 (marge sécurité batterie).

### Calcul des personas atteints

```
Pour chaque profil p :
  contribution =
    pct_pop                           (part de la population cible)
    × N_cible                         (1 950 000 personas estimés)
    × P(autonomie couverte | EMP2019) (distribution cumulative réelle)
    × P(vitesse ok)                   (1 si vit_véhicule ≥ vit_min_profil, sinon 0)
    × P(places ok)                    (1 si places ≥ places_profil, sinon 0)
    × P(peut financer | CGDD2022)     (courbe accessibilité par CSP)

Total = Σ contributions sur les 6 profils
```

### Optimisation par type de véhicule

La vitesse et le mode actif/passif sont **fixes** pour chaque type.  
L'autonomie et les places sont **librement optimisées** pour maximiser `personas_atteints ÷ prix_net`.

Variables testées : autonomie ∈ {10, 20, 30, 40, 50, 60, 80, 100, 120 km} × places ∈ {1, 2, 3, 4} = 36 combinaisons par type.

---

## Données sources

### Personas — NVIDIA Nemotron-Personas-France

- **URL** : https://huggingface.co/datasets/nvidia/Nemotron-Personas-France
- **Licence** : CC-BY-4.0
- **Volume** : ~6 millions de profils synthétiques
- **Champs utilisés** : uuid · persona · age · sex · commune · departement · occupation · household_type · cultural_background · sports_persona · travel_persona · skills_and_expertise · hobbies_and_interests

### Véhicules — Catalogue Vélis

- **Source** : export Airtable (vue `shrj4JvbxjN9yfz94`)
- **60 véhicules** : 47 Actifs / 13 Passifs
- **Champ actif/passif** : `Véhicule Actif (pédalage) ou Passif` — valeur réelle Airtable

### Mobilité — EMP 2019 (SDES/INSEE)

- **Fichiers** :
  - `k_deploc_public_V4.csv` — 45 169 déplacements individuels semaine
  - `tcm_ind_kish_public_V3.csv` — socio-démo individus
  - `tcm_men_public_V3.csv` — ménages (densité, quartile revenu)
- **Filtre** : Q1+Q2 (faibles revenus) · DENSITECOM 2-3-4 (périurbain + rural)
- **Indicateur** : `besoin_autonomie = max_trajet × 2 (AR) × 1,15 (marge)`
- **Segments extraits** : 35 combinaisons territoire × CSP, de 8 à 629 individus

### Budget — CGDD/INSEE 2022

- *"Les ménages modestes et la mobilité"*, CGDD 2022
- Courbe P(budget ≥ prix) calibrée par CSP dominante de chaque profil

---

## Architecture `app.py`

```
app.py (~1 500 lignes)
│
├── Imports (streamlit, pandas, anthropic, json, math)
├── CSS global (classes card · lcard · ok · ko · badge)
│
├── DONNÉES ONGLETS 1 & 2
│   ├── PERSONAS[]              15 profils enrichis Nemotron
│   ├── VEHICLES[]              60 véhicules Vélis
│   ├── ACTIF_PASSIF{}          mapping nom → Actif/Passif (Airtable)
│   └── Fonctions scoring       affinity_score() · compute_score()
│
├── DONNÉES ONGLET 3
│   ├── _CUMUL_AUTO_DEFAULT{}   EMP 2019 — 5 profils originaux
│   ├── _AFFORD_PROFILES_DEFAULT{} CGDD/INSEE — 5 profils
│   ├── CUMUL_AUTO / AFFORD_PROFILES  (actifs, remplaçables par upload)
│   ├── PROFILES[]              6 profils archétypaux dont cycliste
│   └── Fonctions               prix_brut() · reach_t3() · optimize_type()
│
├── Sidebar                     persona selector · upload CSV Colab
│
├── Tab 1 — Simulateur
│   ├── Header persona
│   ├── Curseurs budget + aides
│   ├── Filtres véhicules
│   └── Cards score + réaction IA
│
├── Tab 2 — Analyse constructeurs
│   ├── Heatmap globale
│   ├── Top 5 par territoire
│   └── Analyse par constructeur
│
└── Tab 3 — Optimiseur
    ├── Sidebar propre          curseur aides · upload JSON Nemotron
    ├── Vue synthétique         5 cartes véhicules côte à côte
    ├── Barre cumulative        couverture par profil × type véhicule
    ├── Détail par véhicule     onglets · barres autonomie + budget
    ├── Coût public des aides   tableau M€ · CO₂ · coût/tCO₂
    └── Récapitulatif           cahiers des charges en ligne
```

---

## Évolutions possibles

- **Airtable temps réel** : connexion API → catalogue mis à jour sans re-export CSV
- **Carte géographique** : scores par département (plotly choropleth)
- **Loyer mensuel** : afficher le loyer mensuel équivalent (crédit 5 ans) en alternative au prix d'achat
- **Aides territoriales réelles** : intégrer les aides variables par région/commune selon le département du persona
- **Comparateur véhicules** : face à face 2-3 véhicules sur un profil
- **ENTD 2008** : comparer tendances mobilité 2008 vs 2019 (fichiers présents dans le projet)
- **Export résultats** : CSV des meilleurs matchs · PDF cahier des charges constructeur

---

## Licence et crédits

| Composant | Source | Licence |
|---|---|---|
| Personas synthétiques | NVIDIA Nemotron-Personas-France | CC-BY-4.0 |
| Données mobilité | EMP 2019, SDES/INSEE | Open data |
| Données budget | CGDD/INSEE 2022 | Open data |
| Véhicules | Catalogue Vélis / La Fabrique des Mobilités | — |
| LLM | Anthropic Claude `claude-sonnet-4-20250514` | API commerciale |
| Framework | Streamlit | Apache 2.0 |
