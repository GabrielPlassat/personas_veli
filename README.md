# 🚲 Simulateur Vélis × Personas

**Outil open source d'aide à la décision pour la mobilité intermédiaire électrique en France rurale et périurbaine.**

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://simulateur-velis.streamlit.app)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/votre-pseudo/simulateur-velis/blob/main/personas_mobilite_500k.ipynb)
[![Dataset](https://img.shields.io/badge/Dataset-Nemotron--Personas--France-blue)](https://huggingface.co/datasets/nvidia/Nemotron-Personas-France)
[![License: CC BY 4.0](https://img.shields.io/badge/Personas-CC--BY--4.0-green)](https://creativecommons.org/licenses/by/4.0/)
[![EMP 2019](https://img.shields.io/badge/Mobilité-EMP%202019%20SDES%2FINSEE-orange)](https://www.statistiques.developpement-durable.gouv.fr/enquete-sur-la-mobilite-des-personnes-2018-2019)

---

## Présentation

Ce projet croise trois sources de données pour répondre à une question concrète : **quel véhicule électrique intermédiaire concevoir pour remplacer la voiture thermique des ménages modestes en zones rurales et périurbaines ?**

| Source | Contenu | Usage |
|---|---|---|
| [NVIDIA Nemotron-Personas-France](https://huggingface.co/datasets/nvidia/Nemotron-Personas-France) | 6M profils synthétiques · CC-BY-4.0 | Personas avec occupation, territoire, foyer |
| EMP 2019, SDES/INSEE | 45 169 déplacements individuels réels | Distributions de mobilité par CSP × territoire |
| Catalogue Vélis | 60 véhicules intermédiaires électriques | Scoring et comparaison des véhicules existants |

**Résultat** : une application Streamlit en 3 onglets + un notebook Colab pour générer les données d'entrée depuis les 6M personas.

---

## Démo rapide

> **Sans installation.** L'app tourne sur Streamlit Cloud, le notebook sur Google Colab.

| Outil | Accès |
|---|---|
| 🌐 Application Streamlit | [simulateur-velis.streamlit.app](https://simulateur-velis.streamlit.app) |
| 📓 Notebook Colab | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/votre-pseudo/simulateur-velis/blob/main/personas_mobilite_500k.ipynb) |

> Remplacer `votre-pseudo` par votre nom d'utilisateur GitHub après avoir forké le repo.

---

## Ce que fait l'application

### Onglet 1 — 🔍 Simulateur personas × véhicules

Pour un persona donné, quels véhicules Vélis correspondent le mieux à ses besoins ?

- **15 personas intégrés** extraits du dataset Nemotron, enrichis avec profils culturel, sportif, voyages, compétences
- **Score /120** par véhicule : Budget (30) + Territoire/vitesse (40) + Usages (30) + Affinité profil (+20)
- **Curseurs** budget (1k–40k €) et aides publiques (0–20 %) avec recalcul en temps réel
- **Simulation IA** : réaction à la 1ère personne via API Anthropic Claude
- **Upload CSV** : remplacer les 15 personas par un fichier généré depuis le notebook Colab

### Onglet 2 — 📊 Analyse constructeurs × territoires

Pour chaque constructeur du catalogue Vélis, quels segments géographiques et démographiques représentent les meilleures opportunités ?

- 30 archétypes (5 territoires × 3 âges × 2 profils) scorés sur les 60 véhicules
- Heatmap constructeurs × territoires, Top 5 véhicules par territoire
- Segments porteurs (score ≥ 65/120) par constructeur

### Onglet 3 — 🎯 Optimiseur véhicule *(reverse engineering EMP 2019)*

**Question** : quelles caractéristiques techniques minimales pour un véhicule électrique touchant le maximum de ménages modestes ruraux, à coût minimal ?

L'algorithme optimise **5 types de véhicules en parallèle**, chaque type ayant une catégorie et un mode de propulsion fixés, l'autonomie et les places étant librement optimisées :

| Type | Cat. | Vitesse | Mode | Profil cible principal |
|---|---|---|---|---|
| 🚴 VAE cargo | VAE/L1e | ≤ 25 km/h | Actif | Cyclistes périurbains, trajets ≤ 20 km |
| 🚲 L6e Actif | L6e | ≤ 45 km/h | Actif | Périurbain solo + famille |
| 🚗 L6e Passif | L6e | ≤ 45 km/h | Passif | Périurbain, seniors, sans permis |
| 🚙 L7e Passif | L7e | ≤ 90 km/h | Passif | Rural, routes nationales |
| 🛣️ L8e (hyp.) | L8e | ≤ 110 km/h | Passif | Rural isolé, voies rapides |

**Un seul curseur en entrée** : le taux d'aides publiques (0–20 %). Tout le reste est calculé.

**Résultats à 0 % d'aides :**

| Type | Specs optimales | Prix net | Personas touchés |
|---|---|---|---|
| 🚴 VAE cargo | 20 km · 1 adulte | 4 400 € | ~97 000 (5 %) |
| 🚲 L6e Actif | 20 km · 1+2 enfants | 7 500 € | ~238 000 (12 %) |
| 🚗 L6e Passif | 20 km · 1+2 enfants | 7 500 € | ~238 000 (12 %) |
| 🚙 L7e Passif | 40 km · 1+2 enfants | 10 800 € | ~278 000 (14 %) |
| 🛣️ L8e hyp. | 30 km · 1+2 enfants | 11 800 € | ~184 000 (9 %) |

Le tableau **coût public des aides** calcule en M€ le budget nécessaire selon un taux de pénétration marché (1–10 %), avec la CO₂ économisée et le coût par tonne évitée.

---

## Le notebook Colab — générer les vraies distributions depuis les 6M personas

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/votre-pseudo/simulateur-velis/blob/main/personas_mobilite_500k.ipynb)

Par défaut, l'onglet 3 utilise des **estimations** calibrées sur l'EMP 2019 et CGDD/INSEE. Le notebook permet de les remplacer par des distributions **calculées directement depuis les 6M personas Nemotron**.

### Prérequis

- Un compte Google (accès Colab gratuit)
- Pas d'installation, pas de téléchargement préalable
- Durée : ~40 min pour 4M personas scannés (GPU non requis)

### Ce que fait le notebook

```
HuggingFace (6M personas Nemotron CC-BY-4.0)
        ↓  Cellules 1–8 : stream + filtre low-income + enrichissement EMP 2019
personas_mobilite_500k.csv   (500k lignes · 20 colonnes de mobilité)
        ↓  Cellules 9a–9d : calcul des distributions cumulatives
distributions_nemotron.json  (6 profils · CUMUL_AUTO + AFFORD_PROFILES)
        ↓  Upload sidebar onglet 3 Streamlit
Optimiseur recalibré sur les vrais personas Nemotron
```

**Cellules 1–8** génèrent le CSV de 500k personas avec les colonnes :
`territoire · csp · km_jour · besoin_autonomie_km · vitesse_min_kmh · places_besoin · budget_achat_eur · co2_actuel_g_jour`

**Cellules 9a–9d** calculent les 6 profils archétypaux et exportent `distributions_nemotron.json` :

| Profil | Critère | Véhicule cible |
|---|---|---|
| `periurbain_cycliste` | Périurbain · solo · besoin ≤ 20 km | 🚴 VAE cargo |
| `periurbain_solo` | Périurbain · solo · besoin > 20 km | 🚲🚗 L6e |
| `periurbain_famille` | Périurbain · ≥ 3 places | 🚲🚗 L6e |
| `rural_navetteur` | Rural · ≤ 2 places · autonomie < 60 km | 🚙 L7e |
| `rural_famille` | Rural · ≥ 3 places | 🚙 L7e |
| `rural_longue_dist` | Rural · autonomie ≥ 60 km | 🛣️ L8e |

### Charger le JSON dans l'app

```
Onglet 🎯 Optimiseur → Sidebar → 📥 Distributions Nemotron → Browse → distributions_nemotron.json
```

L'app affiche `✅ Nemotron chargé · X personas` et recalibre immédiatement.

### Ce que le JSON améliore

| | Sans JSON | Avec JSON Nemotron |
|---|---|---|
| Distributions autonomie | EMP 2019, 50–900 individus/profil | Milliers de personas Nemotron réels |
| Courbes budget | Estimation CGDD/INSEE 2022 | Calculées par CSP × âge × décile INSEE |
| Population cible | 1,95M estimés | Décompte réel des personas filtrés |
| Parts des 6 profils | 8/12/25/28/20/7 % estimés | Calculées sur la vraie distribution |

> **Note** : le fichier `distributions_nemotron.json` est **à ne pas versionner** sur GitHub — il est généré localement par chaque utilisateur. Ajoutez-le à votre `.gitignore`.

---

## Installation locale (optionnel)

L'app est conçue pour Streamlit Cloud, mais elle fonctionne aussi en local.

```bash
git clone https://github.com/votre-pseudo/simulateur-velis.git
cd simulateur-velis
pip install -r requirements.txt

# Ajouter la clé API dans .streamlit/secrets.toml
echo 'ANTHROPIC_API_KEY = "sk-ant-XXXX"' > .streamlit/secrets.toml

streamlit run app.py
```

### `requirements.txt`

```
streamlit>=1.32
anthropic>=0.25
pandas>=2.0
```

---

## Déployer votre propre instance sur Streamlit Cloud

1. **Forker** ce dépôt sur GitHub
2. Aller sur [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Sélectionner votre fork · branch `main` · fichier `app.py`
4. Dans **Advanced settings → Secrets**, ajouter :
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-XXXXXXXXXXXXXXXX"
   ```
5. Cliquer **Deploy** — l'app est en ligne en ~2 minutes

> La clé API est chiffrée par Streamlit et n'apparaît jamais dans les logs. Ne jamais la mettre dans `app.py` ou dans un commit Git.

---

## Structure du projet

```
simulateur-velis/
├── app.py                          Application Streamlit (3 onglets, ~1 500 lignes)
├── requirements.txt                streamlit · anthropic · pandas
├── personas_mobilite_500k.ipynb    Notebook Colab (16 cellules)
└── README.md                       Ce fichier
```

**À ne pas versionner** (ajouter au `.gitignore`) :
```
.streamlit/secrets.toml
distributions_nemotron.json
personas_mobilite_500k.csv
__pycache__/
*.pyc
```

---

## Algorithmes

### Scoring véhicule (onglets 1 & 2) — /120 pts

```
Score = Budget(30) + Territoire(40) + Usages(30) + Affinité(+20)

Budget      → ratio prix_net / budget_persona → 0 à 30 pts
Territoire  → compatibilité vitesse véhicule × urbanité du persona → 0 à 40 pts
Usages      → fraction des besoins persona couverts par les usages du véhicule → 0 à 30 pts
Affinité    → signaux dans le profil (vélo → VAE, tourisme, bricolage) → 0 à +20 pts
```

### Optimisation (onglet 3)

```
Prix brut = (châssis + 40€/km × autonomie + coût_places) × 1,30

Personas atteints = Σ profil × N_cible
    × P(besoin_autonomie ≤ X km)   [EMP 2019 ou Nemotron]
    × P(vitesse suffisante)        [binaire]
    × P(places suffisantes)        [binaire]
    × P(budget ≥ prix_net)         [CGDD/INSEE ou Nemotron]

Optimisation : maximise personas_atteints ÷ prix_net
Variables libres : autonomie ∈ {10…120 km} · places ∈ {1…4}
Variables fixes  : catégorie et mode actif/passif du type de véhicule
```

---

## Transparence des données

| Donnée | Source | Statut |
|---|---|---|
| Distributions autonomie (`CUMUL_AUTO`) | EMP 2019, micro-données réelles | ✅ Réelles |
| Courbes budget (`AFFORD_PROFILES`) | CGDD/INSEE 2022, calibration | ⚠️ Estimées |
| Population cible 1,95M | Extrapolation sur Nemotron | ⚠️ Estimée |
| Parts des 6 profils | Structure socio-démo France rurale | ⚠️ Estimées |
| Profil cycliste VAE | Adoption future, non mesurée EMP 2019 | ⚠️ Hypothétique |

**Pour passer aux vraies valeurs** : exécuter le notebook Colab → uploader `distributions_nemotron.json`.

---

## Contribuer

Les contributions sont bienvenues, en particulier :

- **Nouvelles données mobilité** : intégration d'autres millésimes EMP ou enquêtes régionales
- **Nouveaux véhicules** : mise à jour du catalogue Vélis (export Airtable)
- **Amélioration du modèle de coût** : affiner les paramètres `BASE_CHASSIS` et `BATT_COST_KM` avec des données constructeurs
- **Loyer mensuel** : afficher le loyer équivalent (crédit 5 ans) en alternative au prix d'achat
- **Carte géographique** : visualiser les scores par département (plotly choropleth)

Ouvrir une issue ou une pull request directement sur ce dépôt.

---

## Licence et crédits

| Composant | Source | Licence |
|---|---|---|
| Personas synthétiques | [NVIDIA Nemotron-Personas-France](https://huggingface.co/datasets/nvidia/Nemotron-Personas-France) | CC-BY-4.0 |
| Données mobilité | [EMP 2019, SDES/INSEE](https://www.statistiques.developpement-durable.gouv.fr/enquete-sur-la-mobilite-des-personnes-2018-2019) | Open data (Etalab 2.0) |
| Données budget | CGDD/INSEE 2022 | Open data (Etalab 2.0) |
| Véhicules | [Catalogue Vélis / La Fabrique des Mobilités](https://wiki.lafabriquedesmobilites.fr/wiki/Catalogue_des_V%C3%A9hicules_Interm%C3%A9diaires) | — |
| LLM | Anthropic Claude `claude-sonnet-4-20250514` | API commerciale |
| Framework | [Streamlit](https://streamlit.io) | Apache 2.0 |

Développé dans le cadre d'un POC sur la mobilité douce avec l'aide de [Claude (Anthropic)](https://claude.ai).
