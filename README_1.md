# 🏪 Cegid Lead Intelligence Platform — Guide d'installation complet

> Plateforme de sales intelligence retail : enrichissement de données, scoring McKinsey, prospection automatisée et génération de pitch IA.

---

## 📋 Table des matières

1. [Prérequis](#1-prérequis)
2. [Cloner le repository GitHub](#2-cloner-le-repository-github)
3. [Installation locale (Python)](#3-installation-locale-python)
4. [Configuration des clés API](#4-configuration-des-clés-api)
5. [Lancer l'application en local](#5-lancer-lapplication-en-local)
6. [Déployer sur Streamlit Cloud (recommandé)](#6-déployer-sur-streamlit-cloud-recommandé)
7. [Configurer les secrets sur Streamlit Cloud](#7-configurer-les-secrets-sur-streamlit-cloud)
8. [Vérification finale](#8-vérification-finale)
9. [Résolution des problèmes courants](#9-résolution-des-problèmes-courants)
10. [Récapitulatif des clés API](#10-récapitulatif-des-clés-api)

---

## 1. Prérequis

Avant de commencer, assurez-vous d'avoir installé sur votre machine :

| Outil | Version minimale | Lien de téléchargement |
|-------|-----------------|------------------------|
| **Python** | 3.10 ou supérieur | https://www.python.org/downloads/ |
| **Git** | Toute version récente | https://git-scm.com/downloads |
| **pip** | Inclus avec Python | — |

### Vérifier les installations

Ouvrez un terminal (PowerShell sur Windows, Terminal sur Mac/Linux) et tapez :

```bash
python --version
# Doit afficher : Python 3.10.x ou supérieur

git --version
# Doit afficher : git version 2.x.x

pip --version
# Doit afficher : pip 23.x.x
```

> ⚠️ **Windows** : si `python` ne fonctionne pas, essayez `python3` ou `py`.

---

## 2. Cloner le repository GitHub

### Option A — Via terminal (recommandé)

```bash
# Naviguez vers le dossier où vous voulez installer l'application
cd Documents  # ou n'importe quel dossier de votre choix

# Clonez le repository
git clone https://github.com/maxprr/cegid-lead-enricher.git

# Copie le repository en entier pour avoir le votre 
git fork https://github.com/maxprr/cegid-lead-enricher.git

# Entrez dans le dossier
cd cegid-lead-enricher
```

### Option B — Téléchargement manuel

1. Allez sur `https://github.com/maxprr/cegid-lead-enricher`
2. Cliquez sur le bouton vert **"Code"**
3. Cliquez sur **"Download ZIP"**
4. Décompressez le fichier ZIP
5. Ouvrez un terminal dans ce dossier

> 📝 Remplacez `VOTRE_ORG` par le nom de votre organisation ou compte GitHub.

---

## 3. Installation locale (Python)

### Étape 3.1 — Créer un environnement virtuel (recommandé)

Un environnement virtuel isole les dépendances de ce projet des autres projets Python sur votre machine.

```bash
# Créer l'environnement virtuel
python -m venv venv

# L'activer — macOS / Linux
source venv/bin/activate

# L'activer — Windows (PowerShell)
venv\Scripts\Activate.ps1

# L'activer — Windows (CMD)
venv\Scripts\activate.bat
```

Vous devriez voir `(venv)` apparaître au début de votre ligne de commande. C'est bon signe ✅

### Étape 3.2 — Installer les dépendances

```bash
pip install -r requirements.txt
```

Cette commande installe automatiquement tous les packages nécessaires :

| Package | Rôle |
|---------|------|
| `streamlit` | Interface web de l'application |
| `pandas` | Manipulation des données Excel/CSV |
| `numpy` | Calculs numériques |
| `requests` | Appels aux APIs (Sirene, Pappers, OSM) |
| `beautifulsoup4` | Scraping des store locators |
| `openpyxl` | Lecture/écriture des fichiers Excel |
| `anthropic` | API Claude pour la génération de pitch IA |
| `plotly` | Graphiques et carte territoire |

> ⏱️ L'installation prend environ 2-3 minutes selon votre connexion.

---

## 4. Configuration des clés API

L'application utilise plusieurs APIs externes. Voici comment obtenir et configurer chacune.

### Créer le fichier `.env`

À la racine du projet, créez un fichier nommé `.env` (sans extension) :

```bash
# macOS / Linux
touch .env

# Windows — ouvrez le Bloc-notes et sauvegardez sous ".env" dans le dossier du projet
```

Copiez-collez ce modèle dans le fichier `.env` :

```env
PAPPERS_API_KEY=votre_cle_pappers_ici
ANTHROPIC_API_KEY=votre_cle_anthropic_ici
GOOGLE_MAPS_API_KEY=votre_cle_google_maps_ici
SERPAPI_KEY=votre_cle_serpapi_ici
```

> ⚠️ Ne mettez jamais le fichier `.env` sur GitHub. Il est déjà listé dans le `.gitignore`.

---

### 4.1 Clé Pappers API ⭐ Recommandée

**Rôle** : Récupère le CA, les dirigeants et la forme juridique des entreprises françaises.  
**Tarif** : 1 000 requêtes/mois **gratuites**, puis payant.

**Étapes** :
1. Allez sur [https://www.pappers.fr/api](https://www.pappers.fr/api)
2. Cliquez sur **"Créer un compte"**
3. Renseignez votre email et créez un mot de passe
4. Validez votre email via le lien reçu
5. Allez dans **Mon compte → Clé API**
6. Copiez votre clé (format : `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
7. Collez-la dans `.env` :
   ```env
   PAPPERS_API_KEY=votre_cle_ici
   ```

---

### 4.2 Clé Anthropic (Claude) ⭐ Requise pour le Pitch IA

**Rôle** : Génère les kits de prospection personnalisés (Email J1, InMail, Pitch 30s).  
**Tarif** : ~0,025€ par kit généré. Minimum de recharge : 5$.

> ⚠️ **Important** : Votre abonnement Claude Pro (claude.ai) **ne donne pas accès** à l'API. Ce sont deux services séparés.

**Étapes** :
1. Allez sur [https://console.anthropic.com](https://console.anthropic.com)
2. Créez un compte ou connectez-vous
3. Dans le menu gauche, cliquez sur **"API Keys"**
4. Cliquez sur **"Create Key"**
5. Donnez un nom à votre clé (ex : `cegid-lead-platform`)
6. Copiez la clé immédiatement — elle n'est affichée qu'une seule fois (format : `sk-ant-api03-...`)
7. Collez-la dans `.env` :
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-votre_cle_ici
   ```
8. Allez dans **"Plans & Billing"** et ajoutez au minimum **5$** de crédits

---

### 4.3 Clé Google Maps Places API ⚙️ Optionnelle

**Rôle** : Améliore le comptage du nombre de magasins physiques.  
**Tarif** : 200$/mois de crédit gratuit (largement suffisant pour un usage normal).

**Étapes** :
1. Allez sur [https://console.cloud.google.com](https://console.cloud.google.com)
2. Créez un projet (ex : `cegid-lead-intelligence`)
3. Dans le menu, allez dans **"APIs & Services" → "Bibliothèque"**
4. Recherchez **"Places API"** et activez-la
5. Allez dans **"APIs & Services" → "Identifiants"**
6. Cliquez sur **"Créer des identifiants" → "Clé API"**
7. Copiez la clé et collez-la dans `.env` :
   ```env
   GOOGLE_MAPS_API_KEY=AIzaSy-votre_cle_ici
   ```

> 💡 Sans cette clé, l'application utilise OpenStreetMap (gratuit) — les résultats sont légèrement moins précis mais fonctionnels.

---

### 4.4 Clé SerpApi ⚙️ Optionnelle

**Rôle** : Fallback pour le comptage de magasins via Google Maps.  
**Tarif** : 100 requêtes/mois **gratuites**.

**Étapes** :
1. Allez sur [https://serpapi.com](https://serpapi.com)
2. Cliquez sur **"Register"**
3. Créez un compte gratuit
4. Dans votre dashboard, copiez votre **"API Key"**
5. Collez-la dans `.env` :
   ```env
   SERPAPI_KEY=votre_cle_ici
   ```

---

### Fichier `.env` complet

Votre fichier `.env` final doit ressembler à ceci :

```env
# Obligatoires
PAPPERS_API_KEY=abc123def456...
ANTHROPIC_API_KEY=sk-ant-api03-abc123...

# Optionnelles (améliore la qualité du comptage magasins)
GOOGLE_MAPS_API_KEY=AIzaSy-abc123...
SERPAPI_KEY=xyz789...
```

---

## 5. Lancer l'application en local

Assurez-vous que votre environnement virtuel est activé (`(venv)` visible dans le terminal), puis :

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur à l'adresse :
```
http://localhost:8501
```

> 💡 Pour arrêter l'application : `Ctrl + C` dans le terminal.

---

## 6. Déployer sur Streamlit Cloud (recommandé)

Streamlit Cloud permet de rendre l'application accessible depuis n'importe quel navigateur sans avoir Python installé, idéal pour toute l'équipe commerciale.

### Étape 6.1 — Préparer le repository GitHub

Assurez-vous que votre repository contient ces fichiers à la racine :

```
cegid-lead-enricher/
├── app.py                  ← fichier principal de l'application
├── requirements.txt        ← liste des dépendances Python
├── .gitignore              ← doit contenir ".env"
└── README.md               ← ce guide
```

Vérifiez que `.env` n'est **pas** sur GitHub :

```bash
cat .gitignore | grep .env
# Doit afficher : .env
```

Si `.env` n'y est pas, ajoutez-le :

```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
git push
```

### Étape 6.2 — Créer un compte Streamlit Cloud

1. Allez sur [https://share.streamlit.io](https://share.streamlit.io)
2. Cliquez sur **"Sign up"**
3. Connectez-vous avec votre compte **GitHub** (c'est la méthode la plus simple)
4. Autorisez Streamlit à accéder à vos repositories

### Étape 6.3 — Déployer l'application

1. Sur [https://share.streamlit.io](https://share.streamlit.io), cliquez sur **"New app"**
2. Renseignez les champs :
   - **Repository** : `VOTRE_ORG/cegid-lead-enricher`
   - **Branch** : `main`
   - **Main file path** : `app.py`
3. Cliquez sur **"Deploy!"**
4. Attendez 2-3 minutes que le déploiement se termine

Votre application est maintenant accessible via une URL du type :
```
https://cegid-lead-enricher-xxxx.streamlit.app
```

---

## 7. Configurer les secrets sur Streamlit Cloud

Sur Streamlit Cloud, le fichier `.env` n'existe pas — il faut configurer les clés directement dans l'interface.

### Étapes :

1. Allez sur [https://share.streamlit.io](https://share.streamlit.io)
2. Cliquez sur les **3 points** (⋮) à côté de votre application
3. Cliquez sur **"Settings"**
4. Allez dans l'onglet **"Secrets"**
5. Copiez-collez exactement ce contenu en remplaçant par vos vraies clés :

```toml
PAPPERS_API_KEY = "votre_cle_pappers"
ANTHROPIC_API_KEY = "sk-ant-api03-votre_cle_anthropic"
GOOGLE_MAPS_API_KEY = "AIzaSy-votre_cle_google"
SERPAPI_KEY = "votre_cle_serpapi"
```

6. Cliquez sur **"Save"**
7. L'application redémarre automatiquement avec les nouvelles clés

> ⚠️ **Format important** : sur Streamlit Cloud, les valeurs doivent être entre guillemets `"..."`.

---

## 8. Vérification finale

Une fois l'application lancée (en local ou sur Streamlit Cloud), vérifiez dans la **sidebar gauche** :

| Indicateur | Signification |
|------------|---------------|
| ✅ Pappers (active) | Clé Pappers correctement configurée |
| ✅ Anthropic/Claude (active) | Clé Anthropic correctement configurée |
| ✅ SerpApi (active) | Clé SerpApi correctement configurée |
| ⚠️ Google Maps (optionnel) | Normal si pas configurée |
| ❌ | Clé absente ou invalide — revérifiez |

### Test rapide de chaque fonctionnalité

**Page 2 — Prospection From Scratch**
1. Cliquez sur **"Tester la connexion API"**
2. Vous devez voir : `API Sirene accessible ✅`
3. Si erreur → vérifiez votre connexion internet

**Page 1 — Enrichissement**
1. Uploadez un fichier Excel avec des noms d'entreprises françaises
2. Lancez l'enrichissement sur 2-3 lignes
3. Si les colonnes Sirene se remplissent → API Sirene OK ✅
4. Si le CA apparaît → Pappers OK ✅

**Page 5 — Générateur de Pitch IA**
1. Chargez des prospects depuis la Page 2 ou 3
2. Sélectionnez un compte
3. Cliquez sur **"Générer le Kit"**
4. Si le kit s'affiche → Anthropic OK ✅
5. Si erreur "credit balance too low" → rechargez votre compte sur console.anthropic.com

---

## 9. Résolution des problèmes courants

### ❌ `ModuleNotFoundError: No module named 'streamlit'`
```bash
# Solution : vérifiez que l'environnement virtuel est activé
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate.bat  # Windows

# Puis réinstallez
pip install -r requirements.txt
```

### ❌ `Error code: 400 - credit balance is too low`
→ Allez sur [console.anthropic.com](https://console.anthropic.com) → **Plans & Billing** → ajoutez des crédits (minimum 5$).

### ❌ La carte territoire est vide
→ Normal si aucun prospect n'est chargé. Lancez d'abord une prospection (Page 2) ou un scoring (Page 3), puis revenez sur Dashboard Territoire.

### ❌ `Clé Anthropic absente` même après configuration sur Streamlit Cloud
→ Vérifiez que le format est exactement :
```toml
ANTHROPIC_API_KEY = "sk-ant-api03-..."
```
Pas de espaces autour du `=`, guillemets obligatoires.

### ❌ `Sirene API` ne retourne aucun résultat
→ L'API Sirene peut être temporairement indisponible. Attendez quelques minutes et réessayez. Vérifiez aussi votre connexion internet.

### ❌ `StreamlitAPIException` au démarrage
→ Vérifiez que vous lancez bien `streamlit run app.py` depuis le dossier du projet, et non depuis un sous-dossier.

### ❌ Les prospects disparaissent quand je change de page
→ Assurez-vous d'utiliser la version **v3.0** du fichier `app.py`. Les versions précédentes ne persistaient pas les données entre les pages.

---

## 10. Récapitulatif des clés API

| Clé | Obligatoire | Gratuit | Lien inscription | Usage |
|-----|-------------|---------|-----------------|-------|
| `PAPPERS_API_KEY` | ⭐ Recommandée | 1 000 req/mois | [pappers.fr/api](https://www.pappers.fr/api) | CA, dirigeants entreprises FR |
| `ANTHROPIC_API_KEY` | ⭐ Pitch IA | ~0,025€/kit | [console.anthropic.com](https://console.anthropic.com) | Génération kits prospection |
| `GOOGLE_MAPS_API_KEY` | Optionnelle | 200$/mois crédit | [console.cloud.google.com](https://console.cloud.google.com) | Comptage magasins physiques |
| `SERPAPI_KEY` | Optionnelle | 100 req/mois | [serpapi.com](https://serpapi.com) | Fallback comptage magasins |

> 💡 **Sans aucune clé API**, l'application fonctionne quand même pour la prospection Sirene et le scoring — mais sans enrichissement CA/dirigeants ni génération de pitch IA.

---

## Structure du projet

```
cegid-lead-enricher/
├── app.py                  ← Application principale Streamlit
├── requirements.txt        ← Dépendances Python
├── .env                    ← Clés API (LOCAL UNIQUEMENT - ne pas committer)
├── .gitignore              ← Fichiers à exclure de Git
└── README.md               ← Ce guide
```

---

## Support

Pour toute question technique, contactez l'équipe Albert School qui a développé cette plateforme dans le cadre du projet Cegid Retail — Lead Intelligence.

---

*Cegid Lead Intelligence Platform v3.0 — Mai 2026*
