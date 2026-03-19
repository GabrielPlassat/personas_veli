# 🚲 Simulateur Vélis × Personas

> **POC d'aide à la décision mobilité douce** — Croisement du dataset NVIDIA Nemotron-Personas-France (1 million de profils synthétiques français) avec le catalogue de 60 véhicules intermédiaires Vélis, pour simuler l'adéquation persona × véhicule et identifier les opportunités marché par territoire.

---

## Table des matières

- [Contexte](#contexte)
- [Architecture du projet](#architecture-du-projet)
- [Installation et déploiement](#installation-et-déploiement)
- [Fonctionnalités](#fonctionnalités)
- [Algorithme de scoring](#algorithme-de-scoring)
- [Données](#données)
- [Notebook Colab](#notebook-colab)
- [Structure des fichiers](#structure-des-fichiers)
- [Évolutions possibles](#évolutions-possibles)

---

## Contexte

Les **véhicules intermédiaires** (vélos cargos, quadricycles, triporteurs…) représentent une alternative crédible à la voiture pour de nombreux trajets du quotidien, mais leur adoption dépend fortement du profil de l'utilisateur, de son territoire, et de son budget.

Ce simulateur répond à deux questions :

1. **Pour un persona donné**, quels véhicules Vélis sont les plus adaptés, et pourquoi ?
2. **Pour un constructeur donné**, quels profils de personnes et quels territoires représentent les meilleures opportunités ?

Les personas synthétiques proviennent du dataset **NVIDIA Nemotron-Personas-France** (licence CC-BY-4.0), qui contient 1 million de profils fictifs représentatifs de la population française, avec des informations de culture, sport, voyages, compétences et hobbies.

---

## Architecture du projet

```
GitHub repo
├── app.py                        ← Application Streamlit principale
├── requirements.txt              ← Dépendances Python
├── velis_personas_sampler.ipynb  ← Notebook Google Colab (sampling Nemotron)
└── README.md                     ← Ce fichier
```

**Flux de données :**

```
HuggingFace (1M personas Nemotron)
        │
        ▼
Google Colab (filtre territoire + âge + profil)
        │  export CSV
        ▼
Streamlit (upload CSV dans la sidebar)
        │
        ├── Onglet 1 : Simulateur persona × véhicules
        └── Onglet 2 : Analyse constructeurs × territoires
```

---

## Installation et déploiement

### Prérequis

- Un compte **GitHub** (gratuit) — [github.com](https://github.com)
- Un compte **Streamlit Cloud** (gratuit) — [streamlit.io](https://streamlit.io)
- Une clé **API Anthropic** pour la fonctionnalité de réaction IA

### Étapes de déploiement

**1. Créer le dépôt GitHub**

```
GitHub → New repository → "simulateur-velis" → Create
```

**2. Uploader les fichiers**

Ajouter via `Add file → Upload files` :
- `app.py`
- `requirements.txt`
- `velis_personas_sampler.ipynb` *(optionnel, pour Colab)*

**3. Déployer sur Streamlit Cloud**

```
share.streamlit.io → New app
→ Repository : votre-pseudo/simulateur-velis
→ Branch : main
→ Main file : app.py
→ Advanced settings → Secrets
```

**4. Configurer le secret API**

Dans *Advanced settings → Secrets*, ajouter :

```toml
ANTHROPIC_API_KEY = "sk-ant-XXXXXXXXXXXXXXXX"
```

> ⚠️ Ne jamais mettre la clé directement dans `app.py`. Les secrets Streamlit sont chiffrés.

**5. Déployer**

Cliquer **Deploy!** — l'app sera disponible sous 2 minutes à l'URL :
`https://votre-pseudo-simulateur-velis-XXXX.streamlit.app`

### Mise à jour

Toute modification de `app.py` sur GitHub (bouton crayon → commit) déclenche un redéploiement automatique en moins de 30 secondes.

---

## Fonctionnalités

### Onglet 1 — Simulateur personas × véhicules

**Sélection du persona**

La sidebar liste 15 personas intégrés (extraits du dataset Nemotron) ou les personas chargés depuis un CSV Colab. Chaque persona est caractérisé par :

- Identité : prénom, âge, commune, département
- Profil socio-professionnel : occupation, revenus estimés
- Territoire : urbain / périurbain / rural / montagne / île
- Profil enrichi : culture, sport, voyages, compétences, hobbies
- Besoins de mobilité : trajets domicile-travail, courses, transport scolaire, tourisme, sport…

**Curseurs de simulation**

| Curseur | Plage | Effet |
|---|---|---|
| Budget d'achat | 1 000 € → 40 000 € (pas 500 €) | Recalcule le score budget de chaque véhicule |
| Aides publiques | 0 % → 20 % | Réduit le prix net affiché et recalcule le scoring |

Avec les aides actives, chaque carte affiche : ~~prix brut~~ **prix net** (-économie €)

**Filtres véhicules**

- **Vitesse maxi** : Tous / ≤ 25 km/h / ≤ 45 km/h / ≤ 90 km/h
- **Motorisation** : Tous / Actif (avec pédalage — VAE) / Passif (sans pédalage — quadricycle, L5e…)
- **Financement** : Tous / Prix connu (achat) / Location disponible

**Carte véhicule**

Chaque véhicule est affiché avec :
- Score total `/120` coloré (🟢 Excellent / 🔵 Bon match / 🟡 Partiel / 🟠 Faible / 🔴 Non adapté)
- 4 barres de détail : Budget /30, Territoire /40, Usages /30, Affinité +/20
- Badge 🚴 Actif ou 🛞 Passif (source : champ Airtable)
- Prix barré / net / économie réalisée
- Tags usages couverts (✓ vert) et non couverts (✗ rouge)
- Flags d'affinité détectés (cycliste, voyageur, bricoleur)
- Bouton **"Simuler la réaction"** → appel API Anthropic claude-sonnet

**Chargement CSV Colab**

Un expander en sidebar permet d'uploader un CSV généré par le notebook Colab pour remplacer les 15 personas intégrés par un échantillon personnalisé du dataset Nemotron (jusqu'à 2 000 personas).

---

### Onglet 2 — Analyse constructeurs × territoires

**Méthodologie**

30 archétypes représentatifs sont calculés automatiquement (5 territoires × 3 tranches d'âge × 2 profils sportif/standard) et scorés sur les 60 véhicules pour produire une cartographie des opportunités marché.

**Vue 1 — Carte des opportunités**

Heatmap rouge→vert : score moyen /100 de chaque constructeur sur les 5 territoires. Permet d'identifier d'un coup d'œil les zones géographiques où chaque constructeur est le mieux positionné.

**Vue 2 — Top 5 véhicules par territoire**

Pour chaque territoire (Urbain, Périurbain, Rural, Montagne, Île), les 5 meilleurs véhicules toutes marques confondues, avec leur badge Actif/Passif et leur score moyen.

**Vue 3 — Analyse détaillée par constructeur**

Sélectionner un constructeur pour voir :
- 4 métriques clés : nb véhicules, score moyen global, meilleur territoire, meilleur segment
- Heatmap territoire × segment (18-35/Sportif, 35-55/Standard, 55+/Voyageur…)
- Segments porteurs (score ≥ 65/100) affichés en badges verts
- Détail de chaque véhicule avec score moyen et meilleur territoire

**Meilleurs et pires personas (15 personas réels)**

En bas de l'analyse constructeur, deux colonnes :

| 🏆 Top 5 | ⚠️ Flop 5 |
|---|---|
| 🥇 Persona le mieux servi | 💀 Persona le moins bien servi |
| Score moyen /120 | Score moyen /120 |
| Meilleur véhicule du constructeur pour ce persona | Meilleur véhicule du constructeur pour ce persona |
| Indicateurs explicatifs (budget, territoire, usages, affinité) | Indicateurs explicatifs |

---

## Algorithme de scoring

Le score total est sur **120 points** = base 100 + bonus affinité 20.

### Base /100

**Budget (30 pts)**

| Ratio prix net / budget persona | Points |
|---|---|
| ≤ 1× (dans le budget) | 30 |
| ≤ 1,25× | 22 |
| ≤ 1,5× | 14 |
| ≤ 2× | 6 |
| > 2× | 0 |
| Prix inconnu (sur devis) | 12 (neutre) |

*Le prix net intègre la déduction des aides publiques.*

**Territoire / Vitesse (40 pts)**

| Urbanité persona \ Vitesse véhicule | ≤ 25 km/h | ≤ 45 km/h | > 45 km/h |
|---|---|---|---|
| Urbain | 40 | 35 | 28 |
| Périurbain | 8 | 38 | 40 |
| Rural | 0 | 22 | 40 |
| Montagne | 0 | 15 | 40 |
| Île | 8 | 28 | 40 |

**Usages (30 pts)**

Proportion des besoins du persona couverts par les usages déclarés du véhicule, sur 30 pts.

### Bonus affinité /20

| Signal détecté dans le profil | Condition véhicule | Bonus |
|---|---|---|
| Vélo / VTT dans sport ou hobbies | VAE ou L1eA (actif) | +8 pts |
| Tourisme / voyage dans travel | Usage "Tourisme Découverte" présent | +4 pts |
| Bricolage / mécanique dans skills ou hobbies | VAE (simple à entretenir soi-même) | +8 pts |

Le bonus est plafonné à 20 pts.

### Interprétation

| Score /120 | Label |
|---|---|
| ≥ 100 | 🟢 Excellent |
| ≥ 82 | 🔵 Bon match |
| ≥ 58 | 🟡 Partiel |
| ≥ 34 | 🟠 Faible |
| < 34 | 🔴 Non adapté |

---

## Données

### Véhicules — Catalogue Vélis (60 véhicules)

Source : export Airtable Vélis (vue `shrj4JvbxjN9yfz94`).

Colonnes utilisées :

| Colonne | Usage |
|---|---|
| Nom Véhicule | Identifiant |
| Nom Constructeur | Regroupement constructeur |
| Catégorie du véhicule | Affichage (VAE, L2e, L5e, L6e*, L7e*…) |
| Véhicule Actif (pédalage) ou Passif | Filtre motorisation + bonus affinité |
| Vitesse maxi (en km/h) | Score territoire |
| Cas d'usages détaillés | Score usages |
| Prix de vente (en € HT) | Score budget |
| Prix de location par mois | Filtre financement + affichage |

Répartition du catalogue : **47 Actifs** / **13 Passifs** sur 60 véhicules.

Constructeurs présents : BLUEMOOOV (13 modèles), Karbikes (4), E-ROE (4), HPR Solutions (3), Maillon Mobility (2), MOBILOW (2), Acticycle (2), VUF BIKES (2), Pelican (2), et 18 constructeurs mono-modèle.

### Personas — NVIDIA Nemotron-Personas-France

- **Source** : [huggingface.co/datasets/nvidia/Nemotron-Personas-France](https://huggingface.co/datasets/nvidia/Nemotron-Personas-France)
- **Licence** : CC-BY-4.0
- **Taille** : ~1 million de profils synthétiques
- **Champs utilisés** : uuid, persona, age, sex, commune, departement, occupation, household_type, marital_status, cultural_background, sports_persona, travel_persona, skills_and_expertise, hobbies_and_interests, professional_persona

**15 personas intégrés** (échantillon représentatif de la diversité territoriale française) :

| Avatar | Persona | Territoire | Budget |
|---|---|---|---|
| 👷‍♀️ | Epse Janiak, ouvrière maintenance, Bruay-la-Buissière | Périurbain | 9 000 € |
| 👩‍💼 | Nathalie Guillanton, assistante admin, Donges | Périurbain | 11 000 € |
| 🔧 | Olivier Carpentier, ouvrier métallurgie, Coise | Rural | 10 000 € |
| 🛒 | Pauline Poree, employée commerce, Saint-Égrève | Périurbain | 8 000 € |
| 🧑 | Ludovic Renard, employé supermarché, Corbère | Rural | 8 000 € |
| 👴 | Daniel Turpin, retraité, Quincieux | Périurbain | 9 000 € |
| 📦 | Hanaé Hamzaoui, technicienne logistique, Argenteuil | Urbain | 13 000 € |
| ⚓ | Romain Botherel, manutentionnaire, Mons-en-Barœul | Urbain | 3 500 € |
| 📋 | Corinne Monneret, assistante gestion, Orly | Urbain | 11 000 € |
| ⚙️ | Mehmet Kancel, technicien maintenance, Chambéry | Périurbain | 12 000 € |
| 🥛 | Audrey Poitiers, ouvrière laiterie, Périgueux | Périurbain | 7 000 € |
| 🏔️ | Paul Coubrun, employé mairie, Val-Cenis | Montagne | 11 000 € |
| 🥖 | Fabienne Assoun, boulangère artisane, Niffer | Rural | 16 000 € |
| 🏗️ | Antoine Zawada, technicien HLM, Paris 10e | Urbain | 8 000 € |
| 🌺 | Louis Proust, chargé de mission, Saint-Paul (Réunion) | Île | 15 000 € |

---

## Notebook Colab

Le fichier `velis_personas_sampler.ipynb` permet de sampler le dataset Nemotron complet (1M) pour générer un CSV personnalisé à charger dans Streamlit.

### Utilisation

1. Ouvrir dans Google Colab : `Fichier → Importer le notebook → Upload`
2. Configurer les paramètres dans la cellule 2 :

```python
TERRITOIRES = ['urbain', 'periurbain', 'rural']  # zones souhaitées
AGE_MIN     = 18      # âge minimum
AGE_MAX     = 65      # âge maximum
N_MAX       = 300     # personas à exporter (max 2000 pour Streamlit)
SCAN_MAX    = 150000  # lignes du dataset à scanner
OUTPUT_CSV  = 'personas_velis.csv'
```

3. Exécuter toutes les cellules (Runtime → Run all)
4. Le fichier CSV se télécharge automatiquement
5. Dans Streamlit → sidebar → "📥 Charger des personas depuis Colab" → uploader le CSV

### Mapping département → territoire

| Territoire | Départements types |
|---|---|
| Île | 971, 972, 973, 974, 976, 2A, 2B |
| Montagne | 04, 05, 07, 38, 63, 65, 73, 74… |
| Urbain | 06, 13, 31, 33, 69, 75, 92, 93, 94… |
| Périurbain | 77, 78, 91, 95, 29, 35, 44, 49… |
| Rural | Tous les autres |

### Budget estimé automatiquement

| Occupation | Budget estimé |
|---|---|
| Cadre, ingénieur, médecin | ~18 000 € |
| Artisan, commerçant | ~15 000 € |
| Technicien, enseignant, infirmier | ~11 000 € |
| Employé, vendeur, secrétaire | ~8 500 € |
| Ouvrier, manutentionnaire | ~7 000 € |
| Retraité | ~9 000 € |
| Étudiant | ~4 000 € |
| Sans emploi / RSA | ~3 500 € |

*Modulé par tranche d'âge : +10% entre 40-55 ans, -25% avant 25 ans.*

---

## Structure des fichiers

```
app.py
├── CSS custom (sidebar sombre, tags, reaction-box)
├── PERSONAS []               ← 15 profils enrichis (culture, sport, travel, skills, hobbies)
├── VEHICLES []               ← 60 véhicules Vélis
├── ACTIF_PASSIF {}           ← mapping nom → Actif/Passif (source Airtable)
├── Mots-clés affinité        ← KW_VELO, KW_TRAVEL, KW_BRICO
├── affinity_score()          ← calcul bonus 0-20 pts
├── compute_score()           ← score total /120
├── style_pivot()             ← coloration heatmap sans matplotlib
├── Sidebar
│   ├── Upload CSV Colab
│   └── Sélection persona (15 intégrés ou CSV)
├── Tab 1 — Simulateur
│   ├── Header persona (avatar, profil, besoins, expander détail)
│   ├── Curseur budget (1k-40k €)
│   ├── Curseur aides publiques (0-20%)
│   ├── Filtres (vitesse, motorisation, financement)
│   └── Cards véhicules (score, barres, tags, réaction IA)
└── Tab 2 — Analyse constructeurs
    ├── 30 archétypes (5 territoires × 3 âges × 2 profils)
    ├── Heatmap globale constructeurs × territoires
    ├── Top 5 véhicules par territoire
    └── Analyse détaillée par constructeur
        ├── 4 métriques + heatmap territoire×segment
        ├── Segments porteurs
        ├── Détail véhicules
        └── Top 5 / Flop 5 personas réels
```

---

## Évolutions possibles

- **Connexion Airtable en temps réel** via API Airtable (mise à jour automatique du catalogue sans re-export CSV)
- **Export CSV des résultats** — top matchs par persona ou par constructeur
- **Onglet 3 : comparateur de véhicules** — sélectionner 2-3 véhicules et les comparer face à face sur un persona donné
- **Carte géographique** — visualiser les scores par département sur une carte de France
- **Intégration données réelles** — remplacer les budgets estimés par des données INSEE (revenus médians par commune)
- **Scoring des aides territoriales** — certaines aides varient selon la région ou la commune (ADEME, régions, intercommunalités) ; les intégrer automatiquement selon le département du persona

---

## Licence et crédits

- Dataset personas : [NVIDIA Nemotron-Personas-France](https://huggingface.co/datasets/nvidia/Nemotron-Personas-France) — CC-BY-4.0
- Catalogue véhicules : Vélis / La Fabrique des Mobilités
- Application : Streamlit + Anthropic Claude API
- Développé avec Claude (Anthropic) dans le cadre d'un POC mobilité douce
