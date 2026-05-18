"""
Cegid Retail - Lead Enricher v2.0
Application Streamlit - 4 pages :
  1. Enrichissement Dataset
  2. Prospection From Scratch
  3. Scoring & Top 100
  4. Analyse Business
"""

from __future__ import annotations
import os, re, io, time
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

# ==================================================================
# 0. CONFIG & STYLE
# ==================================================================

st.set_page_config(
    page_title="Cegid Retail - Lead Enricher",
    page_icon="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj4KICA8cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgcng9IjE2IiBmaWxsPSIjMDAzMDgyIi8+CiAgPHRleHQgeD0iNTAiIHk9IjcyIiBmb250LWZhbWlseT0iQXJpYWwgQmxhY2ssIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iNjgiIAogICAgICAgIGZvbnQtd2VpZ2h0PSI5MDAiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5DPC90ZXh0Pgo8L3N2Zz4=",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2_family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* -- Base : theme clair force ---------------------------------- */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, .block-container {
    background-color: #FFFFFF !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* -- Texte general : sombre sur fond clair --------------------- */
.stMarkdown, .stMarkdown p, .stMarkdown li,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: #0D1F3C !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* -- Sidebar : gradient bleu, texte blanc ---------------------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1f3c 0%, #003082 100%) !important;
}
[data-testid="stSidebar"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] a,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
    color: white !important;
}

/* -- Header principal (div.main-header) ------------------------ */
.main-header {
    background: linear-gradient(135deg, #003082, #1a4fa8);
    padding: 1.8rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -50%; right: -5%;
    width: 280px; height: 280px;
    background: rgba(255,107,53,.12);
    border-radius: 50%;
}
.main-header h1,
.main-header h2,
.main-header p,
.main-header span,
.main-header div {
    color: white !important;
}
.main-header .accent { color: #FF6B35 !important; }

/* -- Section titles -------------------------------------------- */
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #003082 !important;
    border-bottom: 2px solid #FF6B35;
    padding-bottom: .4rem;
    margin: 1.4rem 0 .9rem;
    display: inline-block;
}

/* -- Metric cards ---------------------------------------------- */
.metric-card {
    background: #ffffff !important;
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    box-shadow: 0 2px 8px rgba(0,48,130,.08);
    border-left: 4px solid #003082;
    margin-bottom: .8rem;
}
.metric-card .label { font-size:.72rem; color:#64748b !important; text-transform:uppercase; letter-spacing:.05em; font-weight:600; }
.metric-card .value { font-size:1.9rem; font-weight:700; color:#003082 !important; font-family:'DM Mono',monospace; }

/* -- Info / Warn boxes ----------------------------------------- */
.info-box {
    background: #eff6ff; border: 1px solid #bfdbfe;
    border-radius: 10px; padding: .9rem 1.1rem;
    margin: .8rem 0; font-size: .88rem; color: #1e40af !important;
}
.warn-box {
    background: #fffbeb; border: 1px solid #fde68a;
    border-radius: 10px; padding: .9rem 1.1rem;
    margin: .8rem 0; font-size: .88rem; color: #92400e !important;
}
.log-box {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: .7rem 1rem;
    font-family: 'DM Mono', monospace; font-size: .76rem;
    color: #475569 !important; max-height: 240px; overflow-y: auto; line-height: 1.6;
}

/* -- Boutons Cegid : UNIQUEMENT les stButton (pas upload, pas download) -- */
div[data-testid="stButton"] > button {
    background: #003082 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all .2s !important;
}
div[data-testid="stButton"] > button:hover {
    background: #FF6B35 !important;
    color: white !important;
    transform: translateY(-1px);
}
div[data-testid="stButton"] > button p,
div[data-testid="stButton"] > button span {
    color: white !important;
}

/* -- Progress bar ---------------------------------------------- */
.stProgress > div > div { background: #FF6B35 !important; }
</style>
""", unsafe_allow_html=True)

# ==================================================================
# 1. CHARGEMENT .ENV
# ==================================================================

def load_keys():
    """
    Charge les cles API :
    - Streamlit Cloud : st.secrets (Settings -> Secrets dans le dashboard)
    - Local           : fichier .env dans le meme dossier que app.py
    Priorite : st.secrets > .env
    """
    keys = {}

    # 1. .env en local
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                keys[k.strip()] = v.strip()

    # 2. st.secrets (Streamlit Cloud) - prioritaire
    try:
        secrets = st.secrets
        for k in ["PAPPERS_API_KEY", "GOOGLE_MAPS_API_KEY", "SERPAPI_KEY"]:
            val = secrets.get(k, "")
            if val:
                keys[k] = val
    except Exception:
        pass

    return keys

def is_streamlit_cloud():
    """Detecte si on tourne sur Streamlit Cloud."""
    import os
    return (
        os.environ.get("STREAMLIT_SHARING_MODE") == "1"
        or os.environ.get("HOME", "").startswith("/home/adminuser")
        or "/mount/src/" in str(Path(__file__))
    )

_KEYS       = load_keys()
PAPPERS_KEY = _KEYS.get("PAPPERS_API_KEY", "")
GMAPS_KEY   = _KEYS.get("GOOGLE_MAPS_API_KEY", "")
SERPAPI_KEY = _KEYS.get("SERPAPI_KEY", "")
ON_CLOUD    = is_streamlit_cloud()

# ==================================================================
# 2. CONSTANTES METIER
# ==================================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

NAF_RETAIL = {
    "4771Z":"Habillement","4772A":"Chaussures","4772B":"Maroquinerie",
    "4777Z":"Bijouterie/Horlogerie","4775Z":"Parfumerie/Cosmetiques",
    "4711A":"Superettes","4711B":"Supermarches","4711C":"Hypermarches",
    "4711D":"Hard discount","4711F":"Alimentation generale",
    "4719A":"Grands magasins","4719B":"Commerce detail non alimentaire",
    "4721Z":"Fruits et Legumes","4741Z":"Informatique/Telephonie",
    "4751Z":"Textiles","4759A":"Meubles/Decoration",
    "4778A":"Optique","4778C":"Commerce specialise",
    "4779Z":"Occasion","6420Z":"Holding commerce",
}

# Enseignes retail connues par secteur NAF
# L'API Sirene cherche par nom d'entreprise - on cherche les vraies enseignes
NAF_QUERIES = {
    "4771Z": [
        "ZARA","H&M","MANGO","UNIQLO","CACHE CACHE","CAMAIEU","KIABI","PROMOD",
        "BERSHKA","PULL AND BEAR","STRADIVARIUS","PIMKIE","JENNYFER","ETAM",
        "MORGAN","NANA","JACQUELINE","LA HALLE","GRAIN DE MALICE","BONOBO",
        "JULES","CELIO","JACK AND JONES","SCOTCH AND SODA","SANDRO","MAJE",
        "IRO","ISABEL MARANT","COMPTOIR DES COTONNIERS","CLAUDIE PIERLOT",
        "BA&SH","ZADIG","AMERICAN VINTAGE","MAISON SCOTCH","ROUJE",
    ],
    "4772A": [
        "ANDRE","ERAM","BATA","GEOX","CLARKS","TIMBERLAND","CONVERSE",
        "VANS","UGG","BIRKENSTOCK","MEPHISTO","FREE LANCE","MINELLI",
        "BOCAGE","TEXTO","COSMOPARIS","JONAK","KICKERS",
    ],
    "4772B": [
        "LONGCHAMP","LANCEL","LE TANNEUR","LACOSTE","FURLA","COCCINELLE",
        "MICHAEL KORS","COACH","KATE SPADE","TUMI","SAMSONITE","DELSEY",
    ],
    "4777Z": [
        "HISTOIRE D OR","PANDORA","SWAROVSKI","MATY","CLEOR","JULIEN D ORG",
        "AGATHA","LES BIJOUX DE LA LICORNE","YAM","CHAMPS ELYSEES",
        "FOSSIL","SWATCH","OMEGA","CARTIER","VAN CLEEF",
    ],
    "4775Z": [
        "SEPHORA","MARIONNAUD","NOCIBE","YVES ROCHER","SABON","RITUALS",
        "THE BODY SHOP","KIEHL","LUSH","NUXE","CLARINS","GUERLAIN",
        "LANC_ME","SISLEY","BIOTHERM","L OCCITANE","PARAPHARMACIE",
    ],
    "4719A": [
        "GALERIES LAFAYETTE","PRINTEMPS","LE BON MARCHE","BHV","MONOPRIX",
        "PRISUNIC","MAMMOUTH","CORA","AUCHAN","CARREFOUR",
    ],
    "4719B": [
        "FNAC","CULTURA","VIRGIN","NATURE ET DECOUVERTE","GAME","MICROMANIA",
        "FOOT LOCKER","COURIR","SPORT 2000","GO SPORT","DECIMAS",
    ],
    "4778A": [
        "ALAIN AFFLELOU","OPTIC 2000","KRYS","ATOL","GRAND OPTICAL",
        "OPTICAL CENTER","VISION PLUS","GIO OPTIQUE",
    ],
    "4759A": [
        "HABITAT","BUT","CONFORAMA","IKEA","MAISONS DU MONDE","JARDILAND",
        "CASTORAMA","LEROY MERLIN","BRICORAMA","BRICO DEPOT","BRICOMARCHE",
        "TRUFFAUT","BOTANIC","GAMM VERT",
    ],
    "4741Z": [
        "APPLE","SAMSUNG","ORANGE","SFR","BOUYGUES TELECOM","FREE",
        "DARTY","FNAC","BOULANGER","MEDIAMARKT",
    ],
    "4711B": [
        "CASINO","INTERMARCHE","SUPER U","LECLERC","SYSTEME U",
        "MATCH","SIMPLY MARKET","MONOPRIX","FRANPRIX","CARREFOUR MARKET",
    ],
    "4711C": [
        "CARREFOUR","AUCHAN","LECLERC","INTERMARCHE","GEANT CASINO",
        "HYPERMARCHE","HYPERU",
    ],
    "4778C": [
        "MAPED","BOULANGER","PICARD","POINT P","METRO","LIDL","ALDI",
        "ACTION","HEMA","TIGER","FLYING TIGER","CLAIRE",
    ],
    "6420Z": [
        "INDITEX","H AND M","FAST RETAILING","LVMH","KERING","HERMES",
        "CHANEL","DIOR","LOUIS VUITTON","RICHEMONT","TAPESTRY",
    ],
}

# Requete generique fallback si NAF non liste
NAF_QUERY_DEFAULT = {
    "4771Z": "vetements mode retail",
    "4775Z": "parfumerie beaute cosmetiques",
    "4772A": "chaussures retail",
    "4777Z": "bijouterie horlogerie",
    "4778A": "optique lunettes",
}

REGIONS_FR = [
    "Auvergne-Rhone-Alpes","Bourgogne-Franche-Comte","Bretagne",
    "Centre-Val de Loire","Corse","Grand Est","Hauts-de-France",
    "Ile-de-France","Normandie","Nouvelle-Aquitaine","Occitanie",
    "Pays de la Loire","Provence-Alpes-Cote d'Azur",
]

REGIONS_INSEE = {
    "Auvergne-Rhone-Alpes":"84","Bourgogne-Franche-Comte":"27","Bretagne":"53",
    "Centre-Val de Loire":"24","Corse":"94","Grand Est":"44","Hauts-de-France":"32",
    "Ile-de-France":"11","Normandie":"28","Nouvelle-Aquitaine":"75","Occitanie":"76",
    "Pays de la Loire":"52","Provence-Alpes-Cote d'Azur":"93",
}

DEPT_REGION = {
    "01":"Auvergne-Rhone-Alpes","03":"Auvergne-Rhone-Alpes","07":"Auvergne-Rhone-Alpes",
    "15":"Auvergne-Rhone-Alpes","26":"Auvergne-Rhone-Alpes","38":"Auvergne-Rhone-Alpes",
    "42":"Auvergne-Rhone-Alpes","43":"Auvergne-Rhone-Alpes","63":"Auvergne-Rhone-Alpes",
    "69":"Auvergne-Rhone-Alpes","73":"Auvergne-Rhone-Alpes","74":"Auvergne-Rhone-Alpes",
    "21":"Bourgogne-Franche-Comte","25":"Bourgogne-Franche-Comte","39":"Bourgogne-Franche-Comte",
    "58":"Bourgogne-Franche-Comte","70":"Bourgogne-Franche-Comte","71":"Bourgogne-Franche-Comte",
    "89":"Bourgogne-Franche-Comte","90":"Bourgogne-Franche-Comte",
    "22":"Bretagne","29":"Bretagne","35":"Bretagne","56":"Bretagne",
    "18":"Centre-Val de Loire","28":"Centre-Val de Loire","36":"Centre-Val de Loire",
    "37":"Centre-Val de Loire","41":"Centre-Val de Loire","45":"Centre-Val de Loire",
    "2A":"Corse","2B":"Corse",
    "08":"Grand Est","10":"Grand Est","51":"Grand Est","52":"Grand Est",
    "54":"Grand Est","55":"Grand Est","57":"Grand Est","67":"Grand Est",
    "68":"Grand Est","88":"Grand Est",
    "02":"Hauts-de-France","59":"Hauts-de-France","60":"Hauts-de-France",
    "62":"Hauts-de-France","80":"Hauts-de-France",
    "75":"Ile-de-France","77":"Ile-de-France","78":"Ile-de-France","91":"Ile-de-France",
    "92":"Ile-de-France","93":"Ile-de-France","94":"Ile-de-France","95":"Ile-de-France",
    "14":"Normandie","27":"Normandie","50":"Normandie","61":"Normandie","76":"Normandie",
    "16":"Nouvelle-Aquitaine","17":"Nouvelle-Aquitaine","19":"Nouvelle-Aquitaine",
    "23":"Nouvelle-Aquitaine","24":"Nouvelle-Aquitaine","33":"Nouvelle-Aquitaine",
    "40":"Nouvelle-Aquitaine","47":"Nouvelle-Aquitaine","64":"Nouvelle-Aquitaine",
    "79":"Nouvelle-Aquitaine","86":"Nouvelle-Aquitaine","87":"Nouvelle-Aquitaine",
    "09":"Occitanie","11":"Occitanie","12":"Occitanie","30":"Occitanie","31":"Occitanie",
    "32":"Occitanie","34":"Occitanie","46":"Occitanie","48":"Occitanie","65":"Occitanie",
    "66":"Occitanie","81":"Occitanie","82":"Occitanie",
    "44":"Pays de la Loire","49":"Pays de la Loire","53":"Pays de la Loire",
    "72":"Pays de la Loire","85":"Pays de la Loire",
    "04":"Provence-Alpes-Cote d'Azur","05":"Provence-Alpes-Cote d'Azur",
    "06":"Provence-Alpes-Cote d'Azur","13":"Provence-Alpes-Cote d'Azur",
    "83":"Provence-Alpes-Cote d'Azur","84":"Provence-Alpes-Cote d'Azur",
}

TRANCHES_EFF = {
    "00":"0 salarie","01":"1-2","02":"3-5","03":"6-9","11":"10-19","12":"20-49",
    "21":"50-99","22":"100-199","31":"200-249","32":"250-499","41":"500-999",
    "42":"1 000-1 999","51":"2 000-4 999","52":"5 000-9 999","53":"10 000+",
}

EXCLUSION_KW = [
    "corner","revendeur","galeries lafayette","printemps","bon marche",
    "wholesale","multimarques","pop-up","stand","e-shop uniquement",
    "pure player","marketplace","amazon",
]

# -- Segmentation officielle Cegid (document DEF_PROSPECT_CEGID_RETAIL) --------
CEGID_SEGMENTS = {
    "S":  {"stores_min":5,   "stores_max":19,  "ca_min_m":5,   "ca_max_m":19,   "label":"S - 5 a 19 magasins ou 5-19M EUR CA"},
    "M":  {"stores_min":20,  "stores_max":99,  "ca_min_m":20,  "ca_max_m":99,   "label":"M - 20 a 99 magasins ou 20-99M EUR CA"},
    "L":  {"stores_min":100, "stores_max":499, "ca_min_m":100, "ca_max_m":499,  "label":"L - 100 a 499 magasins ou 100-499M EUR CA"},
    "XL": {"stores_min":500, "stores_max":9999,"ca_min_m":500, "ca_max_m":99999,"label":"XL - 500+ magasins ou 500M+ EUR CA"},
}

# -- Secteurs prioritaires Y2 --------------------------------------------------
SECTORS_Y2_PRIORITY = [
    "fashion","luxury","ladieswear","menswear","childrenswear","footwear",
    "beauty","cosmetics","sportswear","accessories","lingerie",
]
SECTORS_Y2_SECONDARY = [
    "professional clothes","jewelry","watches","home linens","specialty food",
    "leather goods","gifts","diy","gardening","decoration","toys",
    "telephony","automotive","office supplies","clubs","hotel","museum","culture",
]

# -- Personas decisionnaires par produit (document DEF_PROSPECT) ---------------
PERSONAS = {
    "Cegid Retail Y2": {
        "S":  ["Directeur General","DSI","Directeur Retail"],
        "M":  ["Directeur Informatique","DSI","Directeur Retail","CTO"],
        "L":  ["DSI","Directeur Informatique","Directeur Retail","CTO"],
        "XL": ["DSI","CTO","VP Retail","Directeur Informatique"],
    },
    "Cegid Orli": {
        "all": ["DSI","Directeur General","Directeur Logistique","Supply Chain Manager","Directeur Production"],
    },
    "Cegid Store Excellence": {
        "all": ["Directeur Retail","Directeur Operations","VP Retail","Directeur Magasins"],
    },
}


# ==================================================================
# 3. FONCTIONS SCRAPING & ENRICHISSEMENT
# ==================================================================

def dept_to_region(cp):
    if not cp: return ""
    return DEPT_REGION.get(str(cp)[:2], "")

def is_empty(val):
    return val is None or str(val).strip() in ("", "nan", "None", "NaN")

def sirene_search(name, siren=None):
    """Recherche INSEE - retourne dict avec statut lisible."""
    r = {"siren":None,"naf":None,"naf_label":None,"adresse":None,
         "nb_etab":None,"effectifs":None,"statut":"Non appelee","ok":False}
    try:
        url    = "https://recherche-entreprises.api.gouv.fr/search"
        params = {"q": siren or name, "per_page": 1}
        resp   = requests.get(url, params=params, headers=HEADERS, timeout=8)
        if resp.status_code != 200:
            r["statut"] = "HTTP {} - verifie ta connexion internet".format(resp.status_code)
            return r
        data = resp.json()
        if not data.get("results"):
            r["statut"] = "Entreprise non trouvee dans la base Sirene"
            return r
        c = data["results"][0]; s = c.get("siege", {})
        r.update({
            "siren":    c.get("siren"),
            "naf":      s.get("activite_principale", ""),
            "naf_label":s.get("libelle_activite_principale", ""),
            "adresse":  s.get("adresse", ""),
            "nb_etab":  c.get("nombre_etablissements_ouverts", 0),
            "effectifs":TRANCHES_EFF.get(str(c.get("tranche_effectif_salarie") or ""), ""),
            "statut":   "OK - {} etablissements, effectifs: {}".format(
                c.get("nombre_etablissements_ouverts",0),
                TRANCHES_EFF.get(str(c.get("tranche_effectif_salarie") or ""),"inconnu")),
            "ok": True,
        })
    except Exception as e:
        r["statut"] = "Erreur reseau: {}".format(str(e)[:50])
    return r

def pappers_search(siren, key):
    """Pappers API - CA + dirigeant. Statut lisible et explicite."""
    r = {"ca":None,"dirigeant":None,"forme_jur":None,"creation":None,
         "statut":"Non appelee","ok":False}
    if not key or not key.strip():
        r["statut"] = "Cle absente - ajoutez PAPPERS_API_KEY=votre_cle dans le fichier .env"
        return r
    if is_empty(siren):
        r["statut"] = "SIREN manquant - enrichissement Sirene necessaire d'abord"
        return r
    try:
        siren_clean = re.sub(r"\D", "", str(siren))[:9]
        url    = "https://api.pappers.fr/v2/entreprise"
        params = {"api_token": key.strip(), "siren": siren_clean,
                  "comptes": "true", "dirigeants": "true"}
        resp   = requests.get(url, params=params, timeout=10)
        if resp.status_code == 401:
            r["statut"] = "Cle Pappers INVALIDE (401) - verifiez PAPPERS_API_KEY dans .env"
            return r
        if resp.status_code == 404:
            r["statut"] = "Entreprise non trouvee sur Pappers (SIREN: {})".format(siren_clean)
            return r
        if resp.status_code != 200:
            r["statut"] = "Pappers HTTP {} - {}".format(resp.status_code, resp.text[:80])
            return r
        data    = resp.json()
        comptes = data.get("comptes_sociaux", [])
        ca      = None
        ca_year = None
        if comptes:
            ca_raw  = comptes[0].get("chiffre_affaires")
            ca_year = comptes[0].get("annee")
            if ca_raw:
                ca = "{:,} EUR".format(int(ca_raw)).replace(",", " ")
        dirs = data.get("dirigeants", [])
        d_str = None
        if dirs:
            d     = dirs[0]
            d_str = "{} {} ({})".format(d.get("prenom",""), d.get("nom",""), d.get("fonction","")).strip()
        r.update({
            "ca":       ca,
            "dirigeant":d_str,
            "forme_jur":data.get("forme_juridique"),
            "creation": int(str(data.get("date_immatriculation_rcs",""))[:4]) if data.get("date_immatriculation_rcs") else None,
            "statut":   "OK - CA {}{} | Dirigeant: {}".format(
                ca or "non dispo", " ({})".format(ca_year) if ca_year else "",
                d_str or "non dispo"),
            "ok": True,
        })
    except requests.exceptions.Timeout:
        r["statut"] = "Timeout Pappers (>10s) - reessayer"
    except Exception as e:
        r["statut"] = "Erreur Pappers: {}".format(str(e)[:60])
    return r

# ------------------------------------------------------------------
# COMPTAGE MAGASINS - Cascade multi-sources sans Google Maps obligatoire
#
# Ordre de priorite :
#   1. Overpass API (OpenStreetMap) - Gratuit, illimite, aucune cle requise
#   2. Scraping store locator du site officiel de la marque - Gratuit
#   3. Google Maps Places API - Payant mais precis (si cle dispo)
#   4. SerpApi - Alternatif payant (si cle dispo)
#   5. Proxy Sirene (nb etablissements) - Toujours disponible
# ------------------------------------------------------------------

# Types OSM qui correspondent a des magasins physiques en propre
# Source : https://wiki.openstreetmap.org/wiki/Key:shop
OSM_SHOP_TYPES = {
    # Commerce physique confirme
    "shop": ["clothes","shoes","jewelry","accessories","cosmetics","beauty",
             "optician","sports","toys","books","electronics","department_store",
             "supermarket","convenience","variety_store","gift","stationery",
             "perfumery","bag","watches","fashion","boutique","general"],
    # Restauration / alimentaire
    "amenity": ["cafe","restaurant","fast_food","bakery","ice_cream"],
}

# Tags OSM qui indiquent un point NON physique ou non exclusif a exclure
OSM_EXCLUDE_TAGS = {
    "internet_sales": "yes",        # E-commerce pur
    "delivery_only":  "yes",        # Livraison uniquement
    "shop":           "online",     # Shop en ligne
    "office":         ["yes","company","retail"],  # Bureau, pas magasin
    "building":       "warehouse",  # Entrepot
    "landuse":        "industrial", # Zone industrielle
}

# Mots dans le "name" OSM qui indiquent un non-magasin-en-propre
OSM_NAME_EXCLUDE = [
    "corner", "outlet center", "galeries lafayette", "printemps",
    "le bon marche", "bhv", "revendeur", "wholesale", "entrepot",
    "logistique", "siege", "headquarters", "bureau",
]


def _is_physical_owned_store(element, brand_name):
    """
    Verifie si un element OSM est bien un magasin physique en propre.
    Retourne (bool, raison).
    """
    tags = element.get("tags", {})
    name = tags.get("name", "").lower()
    brand = tags.get("brand", "").lower()
    shop  = tags.get("shop", "").lower()
    amenity = tags.get("amenity", "").lower()

    brand_lower = brand_name.lower().strip()
    brand_word  = brand_lower.split()[0]  # Premier mot = identifiant principal

    # 1. Le nom doit contenir le nom de la marque (pas un revendeur anonyme)
    if brand_word not in name and brand_word not in brand:
        return False, "Nom '{}' ne contient pas la marque '{}'".format(name[:30], brand_word)

    # 2. Exclure les mots-cles non-exclusifs dans le nom
    for excl in OSM_NAME_EXCLUDE:
        if excl in name:
            return False, "Nom contient '{}' -> non exclusif".format(excl)

    # 3. Exclure les tags e-commerce / bureau / entrepot
    for tag_key, tag_val in OSM_EXCLUDE_TAGS.items():
        osm_val = tags.get(tag_key, "")
        if isinstance(tag_val, list):
            if osm_val in tag_val:
                return False, "Tag {}={} -> hors perimetre".format(tag_key, osm_val)
        else:
            if osm_val == tag_val:
                return False, "Tag {}={} -> hors perimetre".format(tag_key, osm_val)

    # 4. Valider que c'est bien un type de commerce physique
    shop_ok = any(shop in types for types in OSM_SHOP_TYPES.values()) or shop != ""
    amenity_ok = amenity in OSM_SHOP_TYPES.get("amenity", [])
    building_ok = tags.get("building") in ("retail", "commercial", "yes", "")

    # Si shop tag present et non exclu = magasin physique confirme
    if shop and shop not in ("online", "internet"):
        return True, "Magasin physique confirme (shop={})".format(shop)

    # Si pas de tag shop mais coordonnees et nom de marque = accepte prudemment
    if "lat" in element or element.get("type") in ("node", "way"):
        return True, "Point physique geolocalise avec nom de marque"

    return False, "Type inconnu - exclu par precaution"


def _overpass_count(brand_name):
    """
    Compte les magasins PHYSIQUES EN PROPRE d'une enseigne en France.
    Utilise OpenStreetMap / Overpass API - gratuit, sans cle.

    Filtres appliques :
    - Le nom du lieu doit contenir le nom de la marque (exclut corners/revendeurs)
    - Le type OSM doit etre un commerce physique (shop=clothes, shop=shoes, etc.)
    - Exclusion explicite : e-commerce, bureaux, entrepots, corners multimarques
    - Exclusion par nom : 'corner', 'galeries lafayette', 'printemps', etc.
    """
    r = {"nb_stores": None, "nb_exclu": 0, "methode": "OpenStreetMap Overpass",
         "statut": "", "ok": False, "details": []}

    brand = brand_name.strip()

    # Requete Overpass : recuperer les elements complets (pas juste le count)
    # pour pouvoir appliquer nos filtres cote client
    query = """
[out:json][timeout:30];
(
  node["brand"="{b}"]["addr:country"="FR"];
  way["brand"="{b}"]["addr:country"="FR"];
  node["name"~"{b}",i]["shop"]["addr:country"="FR"];
  way["name"~"{b}",i]["shop"]["addr:country"="FR"];
  node["operator"="{b}"]["shop"]["addr:country"="FR"];
);
out tags;
""".strip().format(b=brand.replace('"', '\"'))

    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    ]

    for endpoint in endpoints:
        try:
            resp = requests.post(
                endpoint,
                data={"data": query},
                headers={"User-Agent": "CegidRetailLeadEnricher/2.0"},
                timeout=25,
            )
            if resp.status_code != 200:
                continue

            data     = resp.json()
            elements = data.get("elements", [])

            if not elements:
                # Essayer avec juste le count pour savoir si OSM a des donnees
                query_count = '[out:json][timeout:15];node["brand"="{b}"]["addr:country"="FR"];out count;'.format(b=brand)
                resp2 = requests.post(endpoint, data={"data": query_count},
                                      headers={"User-Agent": "CegidRetailLeadEnricher/2.0"}, timeout=15)
                if resp2.status_code == 200:
                    el2 = resp2.json().get("elements", [])
                    if el2 and el2[0].get("type") == "count":
                        raw_total = int(el2[0].get("tags", {}).get("total", 0))
                        if raw_total == 0:
                            r["statut"] = "OSM: aucune donnee pour '{}' en France".format(brand)
                            return r
                continue

            # Filtrage cote client
            kept   = []
            exclu  = []
            for el in elements:
                valid, reason = _is_physical_owned_store(el, brand)
                name = el.get("tags", {}).get("name", "inconnu")
                if valid:
                    kept.append(name)
                else:
                    exclu.append("{} -> {}".format(name[:25], reason))

            r.update({
                "nb_stores": len(kept),
                "nb_exclu":  len(exclu),
                "statut": (
                    "OK - {total} elements OSM trouves : "
                    "{kept} magasins en propre conserves, "
                    "{exclu} exclus (corners/e-commerce/bureaux)"
                ).format(total=len(elements), kept=len(kept), exclu=len(exclu)),
                "details": exclu[:5],  # Garder les 5 premiers pour le log
                "ok": True,
            })
            return r

        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            continue

    r["statut"] = "Overpass indisponible (tous les endpoints) - passage au fallback"
    return r


def _scrape_store_locator(brand_name):
    """
    Extrait le nombre de MAGASINS PHYSIQUES EN PROPRE depuis les snippets web.

    Filtres appliques sur le texte extrait :
    - Patterns qui mentionnent explicitement 'boutiques en propre', 'magasins physiques'
    - Exclusion des mentions e-commerce : 'site', 'en ligne', 'web', 'livraison', 'click'
    - Exclusion des mentions de revendeurs : 'revendeurs', 'points de vente partenaires',
      'corners', 'distributeurs'
    - Plage realiste : entre 2 et 5000 magasins (filtre les chiffres aberrants)
    """
    r = {"nb_stores": None, "methode": "Scraping store locator", "statut": "", "ok": False}
    try:
        query = "{} boutiques magasins physiques France nombre".format(brand_name)
        url   = "https://html.duckduckgo.com/html/_q={}".format(
            requests.utils.quote(query))
        resp  = requests.get(url, headers=HEADERS, timeout=10)

        soup     = BeautifulSoup(resp.text, "html.parser")
        snippets = [el.get_text() for el in soup.find_all("a", class_="result__snippet")][:8]
        full_txt = " ".join(snippets).lower()

        # Mots qui invalident un resultat (mention e-commerce ou revendeur)
        ECOM_SIGNALS = [
            "site internet", "boutique en ligne", "e-commerce", "e commerce",
            "commande en ligne", "livraison a domicile", "click and collect uniquement",
            "revendeurs agrees", "points de vente partenaires", "distributeurs agrees",
            "corners", "galeries lafayette", "printemps",
        ]

        # Patterns specifiques magasins physiques en propre (du plus precis au moins precis)
        patterns_owned = [
            # Tres precis : mention explicite "en propre" ou "physique"
            (r"(\d+)\s+(_:boutiques_|magasins_|stores_)\s+(_:en\s+propre|physiques_|exclusifs_)", "magasins en propre mentionnes"),
            # Precis : magasins en France avec nombre
            (r"(\d+)\s+(_:boutiques_|magasins_|stores_)\s+en\s+france", "magasins en France"),
            (r"(\d+)\s+boutiques_\s+(_:a\s+travers|partout|dans)", "boutiques physiques"),
            # Moins precis : reseau de magasins
            (r"reseau\s+(_:de\s+)_(\d+)\s+(_:boutiques_|magasins_)", "reseau de magasins"),
            (r"(\d+)\s+points_\s+de\s+vente\s+(_:en\s+france|physiques_|exclusifs_)", "points de vente physiques"),
            # Fallback : nombre suivi de boutiques/magasins (sans mention e-com autour)
            (r"(\d+)\s+(_:boutiques_|magasins_|stores_)", "mention de boutiques"),
        ]

        for pat, label in patterns_owned:
            for m in re.finditer(pat, full_txt):
                nb = int(m.group(1))
                if not (2 <= nb <= 5000):
                    continue
                # Verifier contexte : pas de signal e-commerce dans les 100 chars autour
                start = max(0, m.start() - 100)
                end   = min(len(full_txt), m.end() + 100)
                context = full_txt[start:end]
                ecom_found = next((sig for sig in ECOM_SIGNALS if sig in context), None)
                if ecom_found:
                    continue  # Ce chiffre concerne le e-commerce ou des revendeurs
                r.update({
                    "nb_stores": nb,
                    "statut": "OK - {} magasins extraits (pattern: '{}', contexte verifie)".format(nb, label),
                    "ok": True,
                })
                return r

        r["statut"] = "Store locator : chiffre de magasins physiques non trouve (ou uniquement mentions e-commerce)"
    except Exception as e:
        r["statut"] = "Store locator erreur: {}".format(str(e)[:50])
    return r


def count_stores(name, gmaps_key=None, serpapi_key=None):
    """
    Cascade multi-sources pour compter les magasins en propre.
    Essaie chaque source dans l'ordre et retourne des qu'un resultat est trouve.
    """
    r = {"nb_stores": None, "methode": None, "statut": "Non appelee", "ok": False}

    if not name:
        r["statut"] = "Nom de marque manquant"
        return r

    # -- Source 1 : Overpass / OpenStreetMap (gratuit, sans cle) --------------
    res = _overpass_count(name)
    if res["ok"] and res["nb_stores"] is not None and res["nb_stores"] > 0:
        return res

    # -- Source 2 : Store locator scraping (gratuit) ---------------------------
    res2 = _scrape_store_locator(name)
    if res2["ok"] and res2["nb_stores"] is not None:
        return res2

    # -- Source 3 : Google Maps Places API (si cle dispo) ---------------------
    if gmaps_key and gmaps_key.strip():
        try:
            url    = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {"query": "{} boutique magasin France".format(name),
                      "language": "fr", "region": "fr", "key": gmaps_key.strip()}
            resp   = requests.get(url, params=params, timeout=10)
            data   = resp.json()
            status = data.get("status", "")
            if status == "REQUEST_DENIED":
                r["statut"] = "Google Maps REFUS - verifiez Places API dans Google Cloud Console: {}".format(
                    data.get("error_message", ""))
            elif status in ("OK", "ZERO_RESULTS"):
                places  = data.get("results", [])
                brand_w = name.lower().split()[0]
                owned   = [p for p in places
                           if brand_w in p.get("name", "").lower()
                           and not any(kw in p.get("name", "").lower() for kw in EXCLUSION_KW)]
                return {
                    "nb_stores": len(owned),
                    "methode":   "Google Places API",
                    "statut":    "OK - {} lieux, {} en propre apres filtrage".format(len(places), len(owned)),
                    "ok":        True,
                }
        except Exception as e:
            pass  # Fallback suivant

    # -- Source 4 : SerpApi (si cle dispo) ------------------------------------
    if serpapi_key and serpapi_key.strip():
        try:
            url    = "https://serpapi.com/search"
            params = {"engine": "google_maps", "q": "{} boutique".format(name),
                      "api_key": serpapi_key.strip(), "hl": "fr", "gl": "fr"}
            resp   = requests.get(url, params=params, timeout=10)
            places = resp.json().get("local_results", [])
            owned  = [p for p in places if name.lower().split()[0] in p.get("title","").lower()]
            return {
                "nb_stores": len(owned),
                "methode":   "SerpApi Google Maps",
                "statut":    "OK - {} magasins en propre".format(len(owned)),
                "ok":        True,
            }
        except Exception as e:
            pass

    # -- Aucune source n'a fonctionne ------------------------------------------
    r["statut"] = ("OpenStreetMap: {} | Store locator: {} | "
                   "Google Maps: {} | SerpApi: {}").format(
        res.get("statut","non tente")[:40],
        res2.get("statut","non tente")[:40],
        "cle absente" if not gmaps_key else "echec",
        "cle absente" if not serpapi_key else "echec",
    )
    return r


# Alias pour compatibilite avec enrich_row
def gmaps_stores(name, gmaps_key=None, serpapi_key=None):
    return count_stores(name, gmaps_key=gmaps_key, serpapi_key=serpapi_key)

def enrich_row(row):
    """Enrichit une ligne. Retourne (row, dict_logs) avec logs par source."""
    row   = row.copy()
    logs  = {"Sirene":"Non necessaire","Pappers":"Non necessaire","Magasins":"Non necessaire"}
    name  = str(row.get("Account Name") or row.get("Nom") or "")
    siren = str(row.get("National ID") or row.get("SIREN") or "")
    if siren in ("nan","None",""): siren = ""

    # Sirene
    needs_s = any(is_empty(row.get(c)) for c in ["National ID","Industry Code","Nb Etablissements"])
    if needs_s and name:
        res = sirene_search(name, siren or None)
        logs["Sirene"] = res["statut"]
        if res["ok"]:
            if is_empty(siren): row["National ID"] = res["siren"]; siren = str(res["siren"] or "")
            if is_empty(row.get("Industry Code")):
                row["Industry Code"] = res["naf"]
                row["Industry Label"] = res["naf_label"]
            if is_empty(row.get("Nb Etablissements")):
                row["Nb Etablissements"] = res["nb_etab"]
            if is_empty(row.get("Effectifs")):
                row["Effectifs"] = res["effectifs"]
            if is_empty(row.get("Adresse Siege")):
                row["Adresse Siege"] = res["adresse"]

    # Pappers
    needs_p = any(is_empty(row.get(c)) for c in ["Annual Revenue","Dirigeant"])
    if needs_p:
        res = pappers_search(siren, PAPPERS_KEY)
        logs["Pappers"] = res["statut"]
        if res["ok"]:
            if is_empty(row.get("Annual Revenue")): row["Annual Revenue"] = res["ca"]
            if is_empty(row.get("Dirigeant")):      row["Dirigeant"] = res["dirigeant"]
            if is_empty(row.get("Forme Juridique")):row["Forme Juridique"] = res["forme_jur"]

    # Magasins
    needs_m = is_empty(row.get("No. of Stores"))
    if needs_m and name:
        res = gmaps_stores(name, GMAPS_KEY or None, SERPAPI_KEY or None)
        # Log detaille : methode utilisee + nb exclus si Overpass
        detail = res["statut"]
        if res.get("nb_exclu", 0) > 0:
            detail += " | Exclus: {}".format(res.get("nb_exclu", 0))
        if res.get("details"):
            detail += " | Ex exclusions: {}".format("; ".join(res["details"][:2]))
        logs["Magasins"] = detail
        if res["ok"] and res["nb_stores"] is not None:
            row["No. of Stores"] = res["nb_stores"]
            row["Source Stores"] = res.get("methode", "")

    row["Date Enrichissement"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return row, logs

# ==================================================================
# 4. PROSPECTION API SIRENE
# ==================================================================

def prospect_by_naf(naf_codes, region=None, min_etab=3, max_results=100):
    """
    Prospection via API Sirene. 
    Strategie : collecter max_results * 3 resultats bruts avant deduplication
    pour compenser les pertes dues au filtrage et a la deduplication.
    """
    results, seen = [], set()
    # Collecter beaucoup plus que demande avant dedup
    collect_target = max_results * 4
    region_code    = REGIONS_INSEE.get(region) if region and region != "Toutes les regions" else None
    url            = "https://recherche-entreprises.api.gouv.fr/search"
    errors, prog   = [], st.empty()

    def fetch_one(query, naf, label=""):
        """Fait une requete et retourne les resultats filtres."""
        found = []
        for page in range(1, 4):
            try:
                params = {"q": query, "per_page": 25, "page": page}
                if region_code: params["region"] = region_code
                resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
                if resp.status_code == 429:
                    time.sleep(2)
                    resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
                if resp.status_code != 200: break
                data  = resp.json()
                items = data.get("results", [])
                if not items: break
                for c in items:
                    siren = c.get("siren","")
                    if not siren or siren in seen: continue
                    if c.get("etat_administratif") == "F": continue
                    nb = c.get("nombre_etablissements_ouverts") or 0
                    if nb < min_etab: continue
                    s  = c.get("siege", {}); cp = s.get("code_postal","")
                    seen.add(siren)
                    found.append({
                        "Account Name":     c.get("nom_complet") or c.get("nom_raison_sociale",""),
                        "National ID":      siren,
                        "SIRET Siege":      s.get("siret",""),
                        "Industry Code":    s.get("activite_principale","") or naf,
                        "Industry Label":   NAF_RETAIL.get(s.get("activite_principale","") or naf, NAF_RETAIL.get(naf, label)),
                        "Billing Country":  "France",
                        "Adresse Siege":    s.get("adresse",""),
                        "Code Postal":      cp,
                        "Ville":            s.get("libelle_commune",""),
                        "Region":           s.get("libelle_region","") or dept_to_region(cp) or (region if region and region != "Toutes les regions" else ""),
                        "Nb Etablissements":nb,
                        "No. of Stores":    None,
                        "Annual Revenue":   None,
                        "Effectifs":        TRANCHES_EFF.get(str(c.get("tranche_effectif_salarie") or ""),""),
                        "Dirigeant":        None,
                        "Source":           "API Sirene / data.gouv.fr",
                        "Date extraction":  datetime.now().strftime("%Y-%m-%d"),
                    })
                total = data.get("total_results", 0)
                if page * 25 >= min(total, 75): break
                time.sleep(0.2)
            except Exception as e:
                errors.append("{}: {}".format(query[:20], str(e)[:40])); break
        return found

    for i, naf in enumerate(naf_codes):
        if len(results) >= collect_target: break
        naf_label = NAF_RETAIL.get(naf, "")
        queries   = NAF_QUERIES.get(naf, [])

        # Strategie 1 : chercher par enseigne connue
        if isinstance(queries, list):
            for q_idx, enseigne in enumerate(queries):
                if len(results) >= collect_target: break
                prog.caption("NAF {} ({}/{}) - enseigne '{}' - {} prospects...".format(
                    naf, i+1, len(naf_codes), enseigne, len(results)))
                results.extend(fetch_one(enseigne, naf, naf_label))
                time.sleep(0.2)

        # Strategie 2 : requete generique en fallback
        generic = NAF_QUERY_DEFAULT.get(naf, "")
        if generic and len(results) < collect_target:
            prog.caption("NAF {} - recherche generique '{}' - {} prospects...".format(
                naf, generic, len(results)))
            results.extend(fetch_one(generic, naf, naf_label))

        if len(results) >= collect_target: break

    prog.empty()
    if errors:
        with st.expander("Erreurs API ({})".format(len(errors)), expanded=False):
            for e in errors[:10]: st.caption(e)

    if not results: return pd.DataFrame()

    df = pd.DataFrame(results)

    # -- Deduplication passe 1 : SIREN exact ----------------------------------
    n_avant = len(df)
    df = df.drop_duplicates(subset=["National ID"], keep="first")

    # -- Deduplication passe 2 : Nom normalise (groupes/filiales) -------------
    def normalize_name(name):
        if not name: return ""
        n = str(name).upper().strip()
        for suffix in [" SAS"," SA"," SARL"," SNC"," SASU"," GIE",
                       " FRANCE"," BOUTIQUES"," STORES"," SHOP"," RETAIL"," GROUP"," GROUPE"]:
            n = n.replace(suffix, "")
        SKIP = {"LES","LE","LA","DE","DU","DES","ET","THE","NEW","LTD","INC","STE","CIE"}
        words = [w for w in n.strip().split() if w and len(w) >= 2 and w not in SKIP]
        return " ".join(words[:2]).strip()

    df["_nom_norm"] = df["Account Name"].apply(normalize_name)
    # Trier par nb etablissements desc avant dedup : on garde la plus grande entite
    df = (df.sort_values("Nb Etablissements", ascending=False)
            .drop_duplicates(subset=["_nom_norm"], keep="first")
            .drop(columns=["_nom_norm"])
            .reset_index(drop=True))

    # -- Passe 3 : fuzzy leger (nom contenu dans l'autre) ---------------------
    names   = df["Account Name"].str.upper().str.strip().tolist()
    to_drop = set()
    for i in range(min(len(names), 200)):
        if i in to_drop: continue
        for j in range(i+1, min(i+15, len(names))):
            if j in to_drop: continue
            a, b = names[i], names[j]
            short, long = (a,b) if len(a) <= len(b) else (b,a)
            if len(short) >= 5 and short in long:
                nb_i = df.iloc[i]["Nb Etablissements"] or 0
                nb_j = df.iloc[j]["Nb Etablissements"] or 0
                to_drop.add(j if nb_i >= nb_j else i)
    if to_drop:
        df = df.drop(index=list(to_drop)).reset_index(drop=True)

    df = df.sort_values("Nb Etablissements", ascending=False).reset_index(drop=True)
    return df.head(max_results)

# ==================================================================
# 5. SCORING MCKINSEY FIT / TIMING
# ==================================================================

def _get_nb_stores(row):
    """Recupere le nb de magasins depuis les colonnes disponibles."""
    for col in ["No. of Stores","Nb Etablissements"]:
        v = row.get(col)
        try:
            if not is_empty(v): return int(float(v))
        except: pass
    return 0

def _get_ca_m(row):
    """Tente d'extraire le CA en millions depuis la colonne Annual Revenue."""
    ca_raw = str(row.get("Annual Revenue","") or "")
    if is_empty(ca_raw): return None
    # Nettoyer : supprimer espaces, lettres, garder chiffres et separateurs
    cleaned = re.sub(r"[^\d.,]", "", ca_raw.replace(" ",""))
    try:
        ca_num = float(cleaned.replace(",","."))
        # Si le chiffre est tres grand (en euros), convertir en millions
        if ca_num > 100_000:
            ca_num = ca_num / 1_000_000
        return ca_num
    except:
        return None

def _assign_segment(nb_stores, ca_m):
    """Attribue le segment officiel Cegid (S/M/L/XL) selon les regles du document."""
    for seg, rules in CEGID_SEGMENTS.items():
        if nb_stores >= rules["stores_min"] and nb_stores <= rules["stores_max"]:
            return seg
        if ca_m and ca_m >= rules["ca_min_m"] and ca_m <= rules["ca_max_m"]:
            return seg
    if nb_stores >= 500 or (ca_m and ca_m >= 500):
        return "XL"
    return None  # Hors cible (<5 magasins ET CA inconnu)

def _score_product_fit(row, nb_stores, ca_m, naf, lbl, sect, pays, segment):
    """
    Calcule le score FIT pour chaque produit Cegid selon les regles officielles.
    Retourne dict {produit: score_fit, ...}
    """
    scores = {}

    # -- Cegid Retail Y2 -------------------------------------------------------
    fit_y2 = 0
    # Secteur prioritaire Y2
    NAF_Y2_PREFIXES = ["4771","4772","4777","4775","4759","4741","4719","4778","4751","4711","4779","9319","5510","9102","9001"]
    if any(naf.startswith(p) for p in NAF_Y2_PREFIXES):
        fit_y2 += 25
    elif any(k in lbl or k in sect for k in SECTORS_Y2_PRIORITY):
        fit_y2 += 20
    elif any(k in lbl or k in sect for k in SECTORS_Y2_SECONDARY):
        fit_y2 += 10
    # Taille minimale Y2 : 5 magasins
    if nb_stores >= 500:    fit_y2 += 25
    elif nb_stores >= 100:  fit_y2 += 20
    elif nb_stores >= 20:   fit_y2 += 15
    elif nb_stores >= 5:    fit_y2 += 8
    else:                   fit_y2 -= 10  # Hors cible
    # Geographie Y2
    if any(g.lower() in pays.lower() for g in ["france","belgique","suisse","luxembourg"]):
        fit_y2 += 15
    elif any(g.lower() in pays.lower() for g in ["uk","united kingdom","allemagne","espagne","italie","ireland"]):
        fit_y2 += 10
    elif any(g.lower() in pays.lower() for g in ["saudi","emirates","china","japan","singapore"]):
        fit_y2 += 5
    scores["Cegid Retail Y2"] = max(0, fit_y2)

    # -- Cegid Orli ------------------------------------------------------------
    fit_orli = 0
    NAF_ORLI_PREFIXES = ["141","142","143","151","152","2042","3213","3230","4641","4642","4645"]
    if any(naf.replace(".","").startswith(p) for p in NAF_ORLI_PREFIXES):
        fit_orli += 35  # NAF Orli prioritaire
    elif any(k in lbl or k in sect for k in ["fabrication","confection","manufacture"]):
        fit_orli += 20
    # CA > 3M pour Orli
    if ca_m and ca_m >= 50:    fit_orli += 20
    elif ca_m and ca_m >= 10:  fit_orli += 15
    elif ca_m and ca_m >= 3:   fit_orli += 8
    elif ca_m:                  fit_orli -= 5  # CA trop faible
    # Geographie Orli : zones francophones uniquement
    if any(g.lower() in pays.lower() for g in ["france","belgique","suisse","luxembourg","monaco","andorre"]):
        fit_orli += 15
    elif any(g.lower() in pays.lower() for g in ["maroc","tunisie"]):
        fit_orli += 8
    else:
        fit_orli -= 10  # Hors zone francophone
    scores["Cegid Orli"] = max(0, fit_orli)

    # -- Cegid Store Excellence ------------------------------------------------
    fit_se = 0
    # Tous secteurs retail physiques - mais seuil 20 magasins
    if nb_stores >= 500:    fit_se += 30
    elif nb_stores >= 100:  fit_se += 25
    elif nb_stores >= 20:   fit_se += 20
    elif nb_stores >= 10:   fit_se += 5
    else:                   fit_se -= 15  # Hors cible (min 20 magasins)
    # Secteurs prioritaires Store Excellence
    SE_SECTORS = ["fashion","luxury","ladieswear","footwear","beauty","sportswear","accessories","lingerie","stations services"]
    if any(k in lbl or k in sect for k in SE_SECTORS):
        fit_se += 20
    elif any(naf.startswith(p) for p in ["4771","4772","4775","4777"]):
        fit_se += 15
    # Geographie SE : Europe Nord + France/Belgique/Suisse
    SE_GEO = ["france","belgique","suisse","luxembourg","uk","united kingdom","ireland","allemagne"]
    if any(g.lower() in pays.lower() for g in SE_GEO):
        fit_se += 15
    else:
        fit_se -= 10
    scores["Cegid Store Excellence"] = max(0, fit_se)

    return scores


def compute_score(row):
    """
    Scoring calibre sur le document officiel Cegid 'Definition d'un prospect'.

    Structure du score :
    - FIT Y2 (0-65) + FIT Orli (0-65) + FIT Store Excellence (0-65)
    - Score principal = meilleur FIT produit
    - TIMING (0-35) : qualite lead + dirigeant identifie + segmentation

    Produit recommande = celui avec le meilleur FIT score.
    """
    det = []

    # Recuperer les donnees cles
    naf   = str(row.get("Industry Code","") or "").replace(".","")
    lbl   = str(row.get("Industry Label","") or "").lower()
    sect  = str(row.get("Retail Sector","") or "").lower()
    pays  = str(row.get("Billing Country","") or "France").lower()
    nb    = _get_nb_stores(row)
    ca_m  = _get_ca_m(row)

    # Segment officiel Cegid
    segment = _assign_segment(nb, ca_m)
    det.append("Segment Cegid: {}".format(segment or "Hors cible (<5 magasins)"))

    # Scores FIT par produit
    fit_scores = _score_product_fit(row, nb, ca_m, naf, lbl, sect, pays, segment)
    best_product = max(fit_scores, key=fit_scores.get)
    best_fit     = fit_scores[best_product]
    det.append("Meilleur FIT: {} (score {})".format(best_product, best_fit))
    for prod, sc in fit_scores.items():
        det.append("  {} FIT: {}".format(prod, sc))

    # -- TIMING (35 pts) -------------------------------------------------------
    timing = 0

    # Taille reseau -> urgence (un grand reseau = plus de magasins a equiper = deal plus large)
    if   nb >= 500: timing += 15; det.append("Reseau XL 500+ -> deal majeur +15")
    elif nb >= 100: timing += 12; det.append("Reseau L 100-499 -> deal important +12")
    elif nb >= 20:  timing += 8;  det.append("Reseau M 20-99 +8")
    elif nb >= 5:   timing += 4;  det.append("Reseau S 5-19 +4")
    else:           det.append("Reseau <5 -> hors cible +0")

    # Qualite des donnees disponibles
    filled = sum(1 for c in ["National ID","Industry Code","Adresse Siege",
                              "Effectifs","Annual Revenue","Dirigeant"]
                 if not is_empty(row.get(c)))
    timing += min(10, filled * 2)
    det.append("Qualite lead {}/6 champs +{}".format(filled, min(10, filled*2)))

    # Dirigeant identifie -> contact direct possible
    if not is_empty(row.get("Dirigeant")):
        timing += 10; det.append("Dirigeant identifie +10 (contact direct possible)")
    elif not is_empty(row.get("Annual Revenue")):
        timing += 5;  det.append("CA connu +5")

    # Score final
    total   = min(100, best_fit + timing)
    grade   = "A" if total >= 75 else ("B" if total >= 55 else ("C" if total >= 35 else "D"))
    prio    = {"A":"Priorite 1","B":"Priorite 2","C":"Priorite 3","D":"Hors scope"}[grade]

    # Persona recommande selon le produit et le segment
    personas_dict = PERSONAS.get(best_product, {})
    persona = personas_dict.get(segment, personas_dict.get("all", ["Direction Informatique"]))
    persona_str = " / ".join(persona[:3])

    return {
        "Score Total":           total,
        "Score FIT":             best_fit,
        "Score TIMING":          timing,
        "Grade":                 grade,
        "Priorite":              prio,
        "Produit Recommande":    best_product,
        "Segment Cegid":         segment or "Hors cible",
        "Score Y2":              fit_scores["Cegid Retail Y2"],
        "Score Orli":            fit_scores["Cegid Orli"],
        "Score Store Excellence":fit_scores["Cegid Store Excellence"],
        "Persona Cible":         persona_str,
        "Detail Score":          " | ".join(det),
    }

def normalize_name_dedup(name):
    """Normalise un nom pour la deduplication (utilise dans score_df)."""
    if not name: return ""
    n = str(name).upper().strip()
    for suffix in [" SAS"," SA"," SARL"," SNC"," SASU"," SCM"," SCI",
                   " GIE"," FRANCE"," BOUTIQUES"," STORES"," SHOP"," RETAIL"," GROUP"," GROUPE"]:
        n = n.replace(suffix, "")
    SKIP_WORDS = {"LES","LE","LA","L","DE","DU","DES","ET","THE","NEW",
                  "LTD","INC","STE","CIE","ETS","SOC"}
    words = [w for w in n.strip().split() if w and len(w) >= 2 and w not in SKIP_WORDS]
    return " ".join(words[:2]).strip()

def score_df(df):
    # Deduplication avant scoring (filiales avec noms similaires)
    df = df.copy()
    df["_nom_norm"] = df["Account Name"].apply(normalize_name_dedup)
    nb_col = "Nb Etablissements" if "Nb Etablissements" in df.columns else df.columns[0]
    df[nb_col] = pd.to_numeric(df[nb_col], errors="coerce").fillna(0)
    df = (df.sort_values(nb_col, ascending=False)
            .drop_duplicates(subset=["_nom_norm"], keep="first")
            .drop(columns=["_nom_norm"])
            .reset_index(drop=True))
    scores = pd.DataFrame(df.apply(compute_score, axis=1).tolist())
    result = pd.concat([df.reset_index(drop=True), scores], axis=1)
    return result.sort_values("Score Total", ascending=False).reset_index(drop=True)

# ==================================================================
# 6. EXPORT EXCEL
# ==================================================================

def to_excel(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Leads")
        ws = w.sheets["Leads"]
        from openpyxl.styles import PatternFill, Font, Alignment
        from openpyxl.utils import get_column_letter
        hf = PatternFill(start_color="003082", end_color="003082", fill_type="solid")
        for ci, cell in enumerate(ws[1], 1):
            cell.fill = hf
            cell.font = Font(color="FFFFFF", bold=True, size=10)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.column_dimensions[get_column_letter(ci)].width = min(max(len(str(cell.value or ""))+4, 12), 40)
        ws.freeze_panes = "A2"
        alt = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
        for ri in range(2, ws.max_row+1, 2):
            for ci in range(1, ws.max_column+1):
                ws.cell(row=ri, column=ci).fill = alt
    return out.getvalue()

# ==================================================================
# 7. SESSION STATE
# ==================================================================

if "df_prospects" not in st.session_state: st.session_state.df_prospects = None
if "df_scored"    not in st.session_state: st.session_state.df_scored    = None

# ==================================================================
# 8. SIDEBAR
# ==================================================================

with st.sidebar:
    st.markdown("## Cegid Retail")
    st.markdown("**Lead Enricher v2.0**")
    st.markdown("---")
    page = st.radio("Navigation", [
        "Enrichissement Dataset",
        "Prospection From Scratch",
        "Scoring & Top 100",
        "Analyse Business",
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**Statut des cles API**")
    st.markdown("{} Pappers {}".format("OK" if PAPPERS_KEY else "KO", "(active)" if PAPPERS_KEY else "(absente)"))
    st.markdown("{} Google Maps {}".format("OK" if GMAPS_KEY else "KO", "(active)" if GMAPS_KEY else "(absente)"))
    st.markdown("{} SerpApi {}".format("OK" if SERPAPI_KEY else "KO", "(active)" if SERPAPI_KEY else "(optionnel)"))
    st.markdown("---")
    st.markdown("**Sources**")
    st.markdown("""
- API Sirene (INSEE) - gratuit, illimite
- OpenStreetMap Overpass - gratuit, sans cle
- Scraping store locator - gratuit
- Pappers API - 1 000 req/mois gratuit
- Google Maps Places - optionnel
    """)

# ==================================================================
# PAGE 1 - ENRICHISSEMENT DATASET
# ==================================================================

def _get_store_col(df):
    """Priorite : No. of Stores > Nb Etablissements (proxy moins precis)."""
    if "No. of Stores" in df.columns and pd.to_numeric(df["No. of Stores"], errors="coerce").notna().sum() > 0:
        return "No. of Stores"
    if "Nb Etablissements" in df.columns:
        return "Nb Etablissements"
    return None


try:
    if "Enrichissement Dataset" in page:
        st.markdown("""<div class="main-header">
            <h1>Cegid Retail - <span class="accent">Enrichissement</span></h1>
            <p>Completion automatique de votre base _ Chaque action est tracee et expliquee</p>
        </div>""", unsafe_allow_html=True)

        if not PAPPERS_KEY:
            _on_cloud = ON_CLOUD
            if ON_CLOUD:
                _msg = "Cle Pappers absente -> CA et dirigeants non recuperes. Ajoutez <b>PAPPERS_API_KEY</b> dans <b>Settings -> Secrets</b> (menu Manage app en bas a droite)."
            else:
                _msg = "Cle Pappers absente -> CA et dirigeants non recuperes. Ajoutez <code>PAPPERS_API_KEY=votre_cle</code> dans le fichier <code>.env</code>."
            st.markdown('<div class="warn-box">{}</div>'.format(_msg), unsafe_allow_html=True)
        if not GMAPS_KEY and not SERPAPI_KEY:
            st.markdown('<div class="warn-box">Aucune cle Maps -> le nb de magasins physiques ne sera pas recupere automatiquement. Le nombre d\'etablissements Sirene sera utilise comme proxy.</div>', unsafe_allow_html=True)

        uploaded = st.file_uploader("Deposez votre fichier Excel ou CSV", type=["xlsx","xls","csv"])

        if uploaded:
            try:
                df_in = pd.read_csv(uploaded, sep=None, engine="python") if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
            except Exception as e:
                st.error("Erreur chargement : {}".format(e)); st.stop()

            c1,c2,c3,c4 = st.columns(4)
            pct_av = (1 - df_in.isna().mean().mean()) * 100
            with c1: st.markdown('<div class="metric-card"><div class="label">Lignes total</div><div class="value">{:,}</div></div>'.format(len(df_in)), unsafe_allow_html=True)
            with c2: st.markdown('<div class="metric-card"><div class="label">Completude</div><div class="value">{:.0f}%</div></div>'.format(pct_av), unsafe_allow_html=True)
            with c3: st.markdown('<div class="metric-card"><div class="label">Lignes a enrichir</div><div class="value">{:,}</div></div>'.format(df_in.isna().any(axis=1).sum()), unsafe_allow_html=True)
            with c4: st.markdown('<div class="metric-card"><div class="label">Colonnes incompletes</div><div class="value">{}</div></div>'.format((df_in.isna().sum()>0).sum()), unsafe_allow_html=True)

            st.markdown('<div class="section-title">Apercu du fichier</div>', unsafe_allow_html=True)
            st.dataframe(df_in.head(8), use_container_width=True, height=230)

            max_rows = st.number_input("Nb max de lignes a enrichir", 1, len(df_in), min(20, len(df_in)))

            if st.button("Lancer l'enrichissement", use_container_width=True, key="btn_enrich"):
                # Fix : convertir toutes les colonnes en object (string) avant enrichissement
                # pour eviter TypeError quand on assigne un SIREN string dans une colonne float64
                # Forcer object dtype sur chaque colonne individuellement
            df_out = df_in.copy()
            for _col in df_out.columns:
                try:
                    df_out[_col] = df_out[_col].where(df_out[_col].isna(), df_out[_col].astype(str))
                except Exception:
                    df_out[_col] = df_out[_col].astype(object)
                to_enrich = df_out[df_in.isna().any(axis=1)].head(max_rows)
                progress  = st.progress(0)
                status    = st.empty()
                log_area  = st.empty()
                all_logs  = []
                n         = len(to_enrich)
                enriched_rows = []  # Collecter les lignes enrichies

                for i, (idx, row) in enumerate(to_enrich.iterrows()):
                    name = str(row.get("Account Name","") or "")[:45]
                    status.markdown("**Enrichissement** `{}` ({}/{})".format(name, i+1, n))
                    progress.progress((i+1)/n)

                    try:
                        enriched, logs = enrich_row(row)
                        enriched_rows.append((idx, enriched))
                        # Mise a jour colonne par colonne
                        # Tout convertir en string pour eviter TypeError float64
                        for col, val in enriched.items():
                            # Convertir en string sauf None/NaN
                            if val is None or (isinstance(val, float) and val != val):
                                safe_val = None
                            else:
                                safe_val = str(val)
                            try:
                                if col in df_out.columns:
                                    df_out.at[idx, col] = safe_val
                                else:
                                    # Nouvelle colonne : creer en object dtype
                                    df_out[col] = df_out[col].astype(object) if col in df_out.columns else None
                                    df_out.at[idx, col] = safe_val
                            except Exception:
                                pass  # Ignorer les colonnes non assignables
                    except Exception as e:
                        logs = {"Sirene": "Erreur: {}".format(str(e)[:40]),
                                "Pappers": "Non appele", "Magasins": "Non appele"}

                    log_line = "[{:03d}/{}] {:<40} | S: {} | P: {} | M: {}".format(
                        i+1, n, name,
                        logs["Sirene"][:45],
                        logs["Pappers"][:45],
                        logs["Magasins"][:45],
                    )
                    all_logs.append(log_line)
                    log_area.markdown(
                        '<div class="log-box">' + "<br>".join(all_logs[-10:]) + "</div>",
                        unsafe_allow_html=True)
                    # Delai reduit : 0.5s suffisant, les API prennent deja du temps
                    time.sleep(0.5)

                status.markdown("**Enrichissement termine !**")
                progress.progress(1.0)
                pct_ap = (1 - df_out.replace("None", None).isnull().mean().mean()) * 100

                c1,c2,c3 = st.columns(3)
                c1.metric("Completude avant", "{:.1f}%".format(pct_av))
                c2.metric("Completude apres", "{:.1f}%".format(pct_ap), delta="+{:.1f}%".format(pct_ap-pct_av))
                c3.metric("Lignes traitees", n)

                # Nettoyer les "None" string avant affichage
                df_display = df_out.replace("None", "").replace("nan", "")
                st.markdown('<div class="section-title">Resultats enrichis</div>', unsafe_allow_html=True)
                st.dataframe(df_display, use_container_width=True, height=380)
                st.session_state.df_prospects = df_display

                st.download_button("Telecharger le fichier enrichi (.xlsx)",
                    data=to_excel(df_display),
                    file_name="leads_enrichis_{}.xlsx".format(datetime.now().strftime("%Y%m%d_%H%M")),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
        else:
            st.markdown("""<div style="text-align:center;padding:3rem;background:#f8fafc;border-radius:12px;border:2px dashed #cbd5e1;margin-top:1rem">
                <div style="font-size:2.5rem">_</div>
                <h3 style="color:#64748b;font-weight:600">Deposez votre fichier ici</h3>
                <p style="color:#94a3b8">Excel (.xlsx, .xls) ou CSV acceptes</p>
            </div>""", unsafe_allow_html=True)

    # ==================================================================
    # PAGE 2 - PROSPECTION FROM SCRATCH
    # ==================================================================

    elif "Prospection From Scratch" in page:
        st.markdown("""<div class="main-header">
            <h1>Cegid Retail - <span class="accent">Prospection</span></h1>
            <p>Generation d'une liste de prospects retail France depuis zero</p>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Criteres de recherche</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2,2,1])
        with col1:
            naf_sel = st.multiselect("Codes NAF (secteurs retail)", list(NAF_RETAIL.keys()),
                default=["4771Z","4772A","4777Z","4775Z","4778A"],
                format_func=lambda x: "{} - {}".format(x, NAF_RETAIL[x]))
        with col2:
            region_sel = st.selectbox("Region", ["Toutes les regions"] + REGIONS_FR, index=7)
        with col3:
            max_res  = st.number_input("Nb max", 5, 500, 100)
            min_etab = st.number_input("Nb min etab.", 1, 50, 5,
                                        help="5+ etablissements = enseigne avec reseau de magasins actif")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Tester la connexion API", use_container_width=True, key="btn_test_api"):
                with st.spinner("Test..."):
                    try:
                        resp = requests.get("https://recherche-entreprises.api.gouv.fr/search",
                                            params={"q":"decathlon","per_page":1}, headers=HEADERS, timeout=8)
                        if resp.status_code == 200:
                            d = resp.json()
                            st.success("API Sirene OK - {:,} resultats disponibles dans la base".format(d.get("total_results",0)))
                        else:
                            st.error("API HTTP {} - verifie ta connexion".format(resp.status_code))
                    except Exception as e:
                        st.error("Connexion impossible: {}".format(e))

        if not naf_sel:
            st.warning("Selectionnez au moins un code NAF.")
        else:
            with col_btn2:
                launch = st.button("Lancer la prospection", use_container_width=True, key="btn_prospect")

            if launch:
                with st.spinner("Recherche en cours..."):
                    df_p = prospect_by_naf(naf_sel, region_sel, min_etab, max_res)
                if df_p.empty:
                    st.error("Aucun resultat. Reduisez le filtre Nb min etablissements a 1 ou 2.")
                else:
                    st.session_state.df_prospects = df_p
                    st.session_state.df_scored    = None

            # Afficher depuis session_state : persiste apres navigation entre pages
            if st.session_state.df_prospects is not None:
                df_p = st.session_state.df_prospects
                c1,c2,c3,c4 = st.columns(4)
                with c1: st.markdown('<div class="metric-card"><div class="label">Prospects</div><div class="value">{:,}</div></div>'.format(len(df_p)), unsafe_allow_html=True)
                with c2: st.markdown('<div class="metric-card"><div class="label">Nb etab. median</div><div class="value">{:.0f}</div></div>'.format(pd.to_numeric(df_p["Nb Etablissements"],errors="coerce").median()), unsafe_allow_html=True)
                with c3: st.markdown('<div class="metric-card"><div class="label">Villes</div><div class="value">{}</div></div>'.format(df_p["Ville"].nunique()), unsafe_allow_html=True)
                with c4: st.markdown('<div class="metric-card"><div class="label">Regions</div><div class="value">{}</div></div>'.format(df_p["Region"].nunique()), unsafe_allow_html=True)

                st.markdown('<div class="section-title">Liste des prospects</div>', unsafe_allow_html=True)
                st.dataframe(df_p.sort_values("Nb Etablissements", ascending=False), use_container_width=True, height=400)

                col_dl, col_rst = st.columns([3,1])
                with col_dl:
                    st.download_button("Telecharger {:,} prospects (.xlsx)".format(len(df_p)),
                        data=to_excel(df_p),
                        file_name="prospects_{}.xlsx".format(datetime.now().strftime("%Y%m%d")),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
                with col_rst:
                    if st.button("Effacer", use_container_width=True, key="btn_effacer"):
                        st.session_state.df_prospects = None
                        st.session_state.df_scored    = None
                        st.rerun()
                st.markdown('<div class="info-box">Resultats conserves apres navigation. Cliquez <b>Effacer</b> pour lancer une nouvelle recherche.</div>', unsafe_allow_html=True)

    # ==================================================================
    # PAGE 3 - SCORING & TOP 100
    # ==================================================================

    elif "Scoring & Top 100" in page:
        st.markdown("""<div class="main-header">
            <h1>Cegid Retail - <span class="accent">Scoring & Top 100</span></h1>
            <p>Priorisation des prospects _ Framework McKinsey Fit / Timing</p>
        </div>""", unsafe_allow_html=True)

        with st.expander("Methodologie de scoring (cliquez pour voir)", expanded=False):
            st.markdown("""
    **Score total sur 100 pts = FIT (60 pts) + TIMING (40 pts)**

    | Dimension | Critere | Max |
    |-----------|---------|-----|
    | FIT | Secteur NAF retail cible Cegid (habillement, luxe, beaute, sport...) | 20 pts |
    | FIT | Taille reseau (nb etablissements declares Sirene) | 20 pts |
    | FIT | Taille financiere (effectifs Sirene + CA Pappers) | 10 pts |
    | FIT | Geographie France prioritaire | 10 pts |
    | TIMING | Volume activite (nb etablissements comme proxy urgence) | 20 pts |
    | TIMING | Qualite du lead (nb champs remplis sur 6 cles) | 10 pts |
    | TIMING | Dirigeant identifie / CA connu | 10 pts |

    **Grades :** A (>=75) Priorite 1 - B (>=55) Priorite 2 - C (>=35) Priorite 3 - D (<35) Hors scope
            """)

        source = st.radio("Source des donnees", ["Prospection (Page 2)","Uploader un fichier"], horizontal=True)
        df_to_score = None
        if source == "Prospection (Page 2)":
            if st.session_state.df_prospects is not None:
                df_to_score = st.session_state.df_prospects
                st.success("{:,} prospects charges depuis la page Prospection.".format(len(df_to_score)))
            else:
                st.warning("Lancez d'abord une prospection (Page 2) ou uploadez un fichier.")
        else:
            up = st.file_uploader("Uploadez votre fichier", type=["xlsx","xls","csv"])
            if up:
                df_to_score = pd.read_csv(up, sep=None, engine="python") if up.name.endswith(".csv") else pd.read_excel(up)
                st.success("{:,} lignes chargees.".format(len(df_to_score)))

        if df_to_score is not None and not df_to_score.empty:
            top_n = st.slider("Taille du Top", 10, 200, 100)
            if st.button("Calculer le scoring", use_container_width=True, key="btn_scoring"):
                with st.spinner("Calcul du scoring..."):
                    df_s = score_df(df_to_score)
                    st.session_state.df_scored = df_s

            if st.session_state.df_scored is not None:
                df_s  = st.session_state.df_scored
                df_top = df_s.head(top_n)
                n_a = (df_s["Grade"]=="A").sum()
                n_b = (df_s["Grade"]=="B").sum()
                n_c = (df_s["Grade"]=="C").sum()
                n_d = (df_s["Grade"]=="D").sum()

                c1,c2,c3,c4,c5 = st.columns(5)
                with c1: st.markdown('<div class="metric-card"><div class="label">Grade A - Priorite 1</div><div class="value" style="color:#166534">{}</div></div>'.format(n_a), unsafe_allow_html=True)
                with c2: st.markdown('<div class="metric-card"><div class="label">Grade B - Priorite 2</div><div class="value" style="color:#1e40af">{}</div></div>'.format(n_b), unsafe_allow_html=True)
                with c3: st.markdown('<div class="metric-card"><div class="label">Grade C - Priorite 3</div><div class="value" style="color:#92400e">{}</div></div>'.format(n_c), unsafe_allow_html=True)
                with c4: st.markdown('<div class="metric-card"><div class="label">Hors scope</div><div class="value" style="color:#991b1b">{}</div></div>'.format(n_d), unsafe_allow_html=True)
                with c5: st.markdown('<div class="metric-card"><div class="label">Score moyen</div><div class="value">{:.0f}/100</div></div>'.format(df_s["Score Total"].mean()), unsafe_allow_html=True)

                # Repartition par produit recommande
                if "Produit Recommande" in df_s.columns:
                    st.markdown('<div class="section-title">Repartition par produit Cegid recommande</div>', unsafe_allow_html=True)
                    cp1, cp2 = st.columns(2)
                    with cp1:
                        prod_counts = df_s["Produit Recommande"].value_counts()
                        st.bar_chart(prod_counts, color="#003082")
                        st.caption("Nb de prospects par produit Cegid recommande")
                    with cp2:
                        seg_counts = df_s["Segment Cegid"].value_counts().reindex(["S","M","L","XL","Hors cible"], fill_value=0)
                        st.bar_chart(seg_counts, color="#FF6B35")
                        st.caption("Repartition par segment officiel Cegid (S/M/L/XL)")

                # Distribution
                st.markdown('<div class="section-title">Distribution des scores</div>', unsafe_allow_html=True)
                cg1, cg2 = st.columns(2)
                with cg1:
                    st.bar_chart(df_s["Grade"].value_counts().reindex(["A","B","C","D"],fill_value=0), color="#003082")
                    st.caption("Nombre de prospects par grade")
                with cg2:
                    score_bins = pd.cut(df_s["Score Total"], bins=[0,20,35,55,75,100],
                                        labels=["0-20","20-35","35-55","55-75","75-100"])
                    st.bar_chart(score_bins.value_counts().sort_index(), color="#FF6B35")
                    st.caption("Repartition des scores par tranche")

                # Top N
                st.markdown('<div class="section-title">Top {} - comptes a contacter en priorite</div>'.format(top_n), unsafe_allow_html=True)
                disp_cols = [c for c in [
                             "Account Name","Ville","Region","Industry Label",
                             "Nb Etablissements","Effectifs","Annual Revenue","Dirigeant",
                             "Score Total","Grade","Priorite",
                             "Produit Recommande","Segment Cegid","Persona Cible",
                             "Score Y2","Score Orli","Score Store Excellence",
                             "Score FIT","Score TIMING","Detail Score"]
                            if c in df_top.columns]
                st.dataframe(df_top[disp_cols], use_container_width=True, height=430)

                cd1, cd2 = st.columns(2)
                with cd1:
                    st.download_button("Telecharger le Top {} (.xlsx)".format(top_n),
                        data=to_excel(df_top),
                        file_name="top{}_cegid_{}.xlsx".format(top_n, datetime.now().strftime("%Y%m%d")),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
                with cd2:
                    st.download_button("Telecharger tous les prospects scores (.xlsx)",
                        data=to_excel(df_s),
                        file_name="prospects_scores_{}.xlsx".format(datetime.now().strftime("%Y%m%d")),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)

    # ==================================================================
    # PAGE 4 - ANALYSE BUSINESS
    # ==================================================================

    elif "Analyse Business" in page:
        st.markdown("""<div class="main-header">
            <h1>Cegid Retail - <span class="accent">Analyse Business</span></h1>
            <p>Insights strategiques sur le marche adressable _ Mode consultant McKinsey</p>
        </div>""", unsafe_allow_html=True)

        # Priorite : df_scored (score) > df_prospects (brut)
        # Ne pas utiliser "or" avec des DataFrames pandas -> ValueError
        if st.session_state.df_scored is not None:
            df_ana = st.session_state.df_scored
        elif st.session_state.df_prospects is not None:
            df_ana = st.session_state.df_prospects
        else:
            df_ana = None
        if df_ana is None:
            up = st.file_uploader("Uploadez votre fichier de prospects (score ou non)", type=["xlsx","xls","csv"])
            if up:
                df_ana = pd.read_csv(up, sep=None, engine="python") if up.name.endswith(".csv") else pd.read_excel(up)
            else:
                st.markdown("""<div class="info-box">
                Lancez d'abord une <strong>Prospection (Page 2)</strong> puis un <strong>Scoring (Page 3)</strong>,
                ou uploadez un fichier Excel ici.
                </div>""", unsafe_allow_html=True)

        if df_ana is not None and not df_ana.empty:
            # KPIs globaux
            st.markdown('<div class="section-title">Marche adressable - vue d\'ensemble</div>', unsafe_allow_html=True)
            _store_col = _get_store_col(df_ana)
            _store_series = pd.to_numeric(df_ana[_store_col], errors="coerce") if _store_col else pd.Series(dtype=float)
            c1,c2,c3,c4,c5 = st.columns(5)
            with c1: st.markdown('<div class="metric-card"><div class="label">Prospects total</div><div class="value">{:,}</div></div>'.format(len(df_ana)), unsafe_allow_html=True)
            with c2: st.markdown('<div class="metric-card"><div class="label">Total magasins</div><div class="value">{:,}</div></div>'.format(int(_store_series.sum()) if not _store_series.empty else 0), unsafe_allow_html=True)
            with c3: st.markdown('<div class="metric-card"><div class="label">Mediane reseau</div><div class="value">{:.0f}</div></div>'.format(_store_series.median() if not _store_series.empty else 0), unsafe_allow_html=True)
            region_col = "Region" if "Region" in df_ana.columns else "Billing Country"
            with c4: st.markdown('<div class="metric-card"><div class="label">Regions couvertes</div><div class="value">{}</div></div>'.format(df_ana[region_col].nunique() if region_col in df_ana.columns else "N/A"), unsafe_allow_html=True)
            with c5:
                if "Grade" in df_ana.columns:
                    prio = df_ana["Grade"].isin(["A","B"]).sum()
                    st.markdown('<div class="metric-card"><div class="label">Leads prioritaires A+B</div><div class="value">{}</div></div>'.format(prio), unsafe_allow_html=True)

            # Analyse par secteur
            st.markdown('<div class="section-title">Repartition par secteur retail (NAF)</div>', unsafe_allow_html=True)
            if "Industry Label" in df_ana.columns:
                _has_etab = "Nb Etablissements" in df_ana.columns
                _agg_dict = {"nb_prospects": ("Account Name","count")}
                if _has_etab:
                    df_ana["Nb Etablissements"] = pd.to_numeric(df_ana["Nb Etablissements"], errors="coerce")
                    _agg_dict["moy_etab"] = ("Nb Etablissements","mean")
                sect = (df_ana.groupby("Industry Label")
                        .agg(**_agg_dict)
                        .sort_values("nb_prospects", ascending=False).head(10).reset_index())
                if _has_etab:
                    sect["moy_etab"] = sect["moy_etab"].round(1)
                    sect.columns = ["Secteur","Nb Prospects","Moy. Etab."]
                else:
                    sect.columns = ["Secteur","Nb Prospects"]
                    sect["Moy. Etab."] = "N/A"
                cs1, cs2 = st.columns([3,2])
                with cs1:
                    st.bar_chart(sect.set_index("Secteur")["Nb Prospects"], color="#003082")
                    st.caption("Nombre de prospects par secteur (Top 10)")
                with cs2:
                    st.dataframe(sect, use_container_width=True, height=300)

            # Analyse geographique
            st.markdown('<div class="section-title">Repartition geographique</div>', unsafe_allow_html=True)
            reg_col = "Region" if "Region" in df_ana.columns else ("Billing Country" if "Billing Country" in df_ana.columns else None)
            if reg_col:
                df_geo = df_ana[df_ana[reg_col].notna() & (df_ana[reg_col] != "")]
                geo = (df_geo.groupby(reg_col)
                       .agg(nb=("Account Name","count"))
                       .sort_values("nb", ascending=False).reset_index())
                geo.columns = [reg_col, "Nb Prospects"]
                geo["Total Etab."] = "N/A"
                if "Nb Etablissements" in df_ana.columns:
                    etab_geo = (df_geo.groupby(reg_col)["Nb Etablissements"]
                               .apply(lambda x: pd.to_numeric(x, errors="coerce").sum())
                               .reset_index())
                    etab_geo.columns = [reg_col, "Total Etab."]
                    geo = geo.merge(etab_geo, on=reg_col, how="left")
                geo = geo.rename(columns={reg_col: "Region"})
                cg1, cg2 = st.columns([3,2])
                with cg1:
                    st.bar_chart(geo.set_index("Region")["Nb Prospects"], color="#FF6B35")
                    st.caption("Prospects par region")
                with cg2:
                    st.dataframe(geo, use_container_width=True, height=300)

            # Segmentation taille
            st.markdown('<div class="section-title">Segmentation par taille de reseau</div>', unsafe_allow_html=True)
            if "Nb Etablissements" in df_ana.columns:
                nb_s = pd.to_numeric(df_ana["Nb Etablissements"], errors="coerce").dropna()
                segs = pd.cut(nb_s, bins=[0,4,9,19,49,99,float("inf")],
                              labels=["Micro 1-4","Petite enseigne 5-9","Moyenne enseigne 10-19",
                                      "Grande enseigne 20-49","Tres grande 50-99","Top account 100+"])
                seg_c = segs.value_counts().sort_index()
                ct1, ct2 = st.columns([2,1])
                with ct1:
                    st.bar_chart(seg_c, color="#003082")
                    st.caption("Nb de prospects par segment (base scoring Cegid : cible primaire = 10+ etab.)")
                with ct2:
                    df_seg = seg_c.reset_index()
                    df_seg.columns = ["Segment","Nb Prospects"]
                    df_seg["% du total"] = (df_seg["Nb Prospects"] / df_seg["Nb Prospects"].sum() * 100).round(1).astype(str) + "%"
                    st.dataframe(df_seg, use_container_width=True)

            # Scoring summary + recommandations McKinsey
            if "Grade" in df_ana.columns:
                st.markdown('<div class="section-title">Synthese scoring & recommandations strategiques</div>', unsafe_allow_html=True)
                _grade_agg = {"nb": ("Account Name","count")}
                if "Score Total" in df_ana.columns:
                    _grade_agg["score_moy"] = ("Score Total","mean")
                if "Nb Etablissements" in df_ana.columns:
                    df_ana["Nb Etablissements"] = pd.to_numeric(df_ana["Nb Etablissements"], errors="coerce")
                    _grade_agg["etab_moy"] = ("Nb Etablissements","mean")
                grade_s = df_ana.groupby("Grade").agg(**_grade_agg).round(1).reset_index()
                grade_s.columns = ["Grade"] + [c for c in ["Nb Prospects","Score Moyen","Etab. Moyen"][:len(_grade_agg)]]
                st.dataframe(grade_s, use_container_width=True)

                n_a = (df_ana["Grade"]=="A").sum() if "Grade" in df_ana.columns else 0
                n_b = (df_ana["Grade"]=="B").sum() if "Grade" in df_ana.columns else 0
                top_sect = "N/A"
                top_reg  = "N/A"
                if n_a > 0 and "Grade" in df_ana.columns:
                    df_a = df_ana[df_ana["Grade"]=="A"]
                    if "Industry Label" in df_ana.columns:
                        vc = df_a["Industry Label"].value_counts()
                        if len(vc): top_sect = vc.index[0]
                    if reg_col and reg_col in df_ana.columns:
                        vc2 = df_a[reg_col].value_counts()
                        if len(vc2): top_reg = vc2.index[0]

                score_moyen_a = df_ana[df_ana["Grade"]=="A"]["Score Total"].mean() if (n_a > 0 and "Score Total" in df_ana.columns) else 0
                _sc4 = _get_store_col(df_ana)
            stores_moyen_a = pd.to_numeric(df_ana[df_ana["Grade"]=="A"][_sc4], errors="coerce").mean() if (n_a > 0 and _sc4) else 0

                # Calculer repartition par produit
            prod_a = df_ana[df_ana["Grade"]=="A"]["Produit Recommande"].value_counts().to_dict() if "Produit Recommande" in df_ana.columns else {}
            seg_m_l_xl = df_ana["Segment Cegid"].isin(["M","L","XL"]).sum() if "Segment Cegid" in df_ana.columns else 0

            st.markdown("""
    <div class="info-box">
    <strong>Insights strategiques - recommandations McKinsey</strong><br><br>

    <b>Marche adressable prioritaire :</b> {n_a} comptes Grade A (Priorite 1) et {n_b} Grade B (Priorite 2),
    soit {total} comptes a traiter en priorite.<br><br>

    <b>Segmentation selon les regles officielles Cegid :</b><br>
    - Segment S (5-19 magasins) -> Cegid Retail Y2, interlocuteur : Directeur General<br>
    - Segment M (20-99 magasins) -> Y2 + Store Excellence, interlocuteur : DSI + Direction Retail<br>
    - Segment L/XL (100+ magasins) -> Y2 + Store Excellence, interlocuteur : DSI + CTO + VP Retail<br><br>

    <b>Profil type Grade A :</b> score moyen {score:.0f}/100, reseau moyen {etab:.0f} etablissements.<br><br>

    <b>Secteur dominant Grade A :</b> {sect} - concentrer les kits de prospection sur ce secteur.<br>

    <b>Region prioritaire :</b> {reg} - fort potentiel, a couvrir en priorite.<br><br>

    <b>Recommandation :</b> Prioriser les comptes M/L/XL (20+ magasins) qui representent
    le meilleur ratio effort/ARR pour Cegid. Les comptes S (5-19 magasins) sont qualifies
    mais necessite un cycle de vente plus court avec acces direct au DG.
    </div>""".format(
                    n_a=n_a, n_b=n_b, total=n_a+n_b,
                    score=score_moyen_a, etab=stores_moyen_a,
                    sect=top_sect, reg=top_reg,
            ), unsafe_allow_html=True)

            # Export
            st.markdown('<div class="section-title">Export du rapport</div>', unsafe_allow_html=True)
            st.download_button("Telecharger le rapport complet (.xlsx)",
                data=to_excel(df_ana),
                file_name="analyse_business_cegid_{}.xlsx".format(datetime.now().strftime("%Y%m%d")),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)

except Exception as _page_err:
    st.error("Erreur inattendue — rechargez la page (F5). Detail: {}".format(str(_page_err)[:200]))
    st.info("Si le probleme persiste, utilisez le bouton Effacer dans la page Prospection.")
