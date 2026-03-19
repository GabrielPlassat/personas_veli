# 🚀 Guide de déploiement — Simulateur Vélis × Personas

## Ce dont tu as besoin
- Un compte GitHub (gratuit) → https://github.com
- Un compte Streamlit Cloud (gratuit) → https://streamlit.io
- Ta clé API Anthropic

---

## ÉTAPE 1 — Créer le dépôt GitHub

1. Va sur https://github.com/new
2. Nomme le dépôt : `simulateur-velis`
3. Coche "Add a README file"
4. Clique **Create repository**

---

## ÉTAPE 2 — Uploader les 2 fichiers

Dans ton nouveau dépôt GitHub :

1. Clique **Add file → Upload files**
2. Glisse-dépose les 2 fichiers :
   - `app.py`
   - `requirements.txt`
3. Clique **Commit changes**

Ton dépôt doit maintenant contenir :
```
simulateur-velis/
├── app.py
├── requirements.txt
└── README.md
```

---

## ÉTAPE 3 — Déployer sur Streamlit Cloud

1. Va sur https://share.streamlit.io
2. Connecte-toi avec ton compte GitHub
3. Clique **New app**
4. Remplis :
   - **Repository** : `ton-pseudo/simulateur-velis`
   - **Branch** : `main`
   - **Main file path** : `app.py`
5. Clique **Advanced settings**

---

## ÉTAPE 4 — Ajouter ta clé API (SECRET)

Dans **Advanced settings → Secrets**, colle exactement ceci :

```toml
ANTHROPIC_API_KEY = "sk-ant-XXXXXXXXXXXXXXXXXXXXX"
```

Remplace `sk-ant-XXX...` par ta vraie clé API Anthropic.

⚠️ Ne mets JAMAIS ta clé directement dans `app.py` — les secrets Streamlit sont chiffrés et invisibles dans le code.

---

## ÉTAPE 5 — Lancer l'app

1. Clique **Deploy!**
2. Attends 1-2 minutes (Streamlit installe les dépendances)
3. Ton app est en ligne à une URL du type :
   `https://ton-pseudo-simulateur-velis-app-XXXX.streamlit.app`

---

## 🔄 Mettre à jour l'app plus tard

Pour modifier l'app après déploiement :
1. Va dans ton dépôt GitHub
2. Clique sur `app.py` → icône crayon (éditer)
3. Fais tes modifications
4. Clique **Commit changes**

Streamlit Cloud se met à jour **automatiquement** en quelques secondes.

---

## ❓ Questions fréquentes

**L'app est lente au démarrage** → Normal, Streamlit "réveille" l'app après inactivité (version gratuite). Premier chargement = 30-60 secondes.

**Erreur "ANTHROPIC_API_KEY not found"** → Vérifie l'étape 4. La clé doit être dans Secrets, pas dans le code.

**Je veux changer les personas ou véhicules** → Modifie directement les listes `PERSONAS` et `VEHICLES` dans `app.py` sur GitHub.

**Je veux connecter le vrai dataset HuggingFace** → Dis-le-moi, on peut ajouter un onglet Colab qui charge les 1M de personas et exporte un CSV vers l'app.
