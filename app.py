import streamlit as st
import anthropic

# ─── CONFIG PAGE ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulateur Vélis × Personas",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS CUSTOM ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stSidebar { background-color: #0f172a; }
    .persona-header { background: #f8fafc; border-radius: 10px; padding: 14px 18px; border: 1px solid #e2e8f0; margin-bottom: 12px; }
    .vehicle-card { background: white; border-radius: 10px; padding: 14px 18px; border: 1px solid #e2e8f0; margin-bottom: 8px; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .tag-ok  { background: #dcfce7; color: #15803d; padding: 2px 7px; border-radius: 4px; font-size: 11px; display: inline-block; margin: 2px; }
    .tag-ko  { background: #fee2e2; color: #b91c1c; padding: 2px 7px; border-radius: 4px; font-size: 11px; display: inline-block; margin: 2px; }
    .tag-neu { background: #f1f5f9; color: #475569; padding: 2px 7px; border-radius: 4px; font-size: 11px; display: inline-block; margin: 2px; }
    .reaction-box { background: #f8fafc; border-left: 3px solid #a5b4fc; border-radius: 6px; padding: 10px 14px; margin-top: 8px; font-size: 13px; color: #334155; }
    .score-label { font-size: 11px; color: #94a3b8; margin-bottom: 2px; }
    div[data-testid="stSidebarContent"] { background-color: #0f172a; color: white; }
</style>
""", unsafe_allow_html=True)

# ─── DONNÉES PERSONAS ─────────────────────────────────────────────────────────
PERSONAS = [
    {"id":1,  "avatar":"👷‍♀️", "prenom":"Epse Janiak",        "age":39, "commune":"Bruay-la-Buissière", "dep":"62",  "urbanite":"periurbain", "budget":9000,  "profil":"Ouvrière maintenance",       "resume":"Bassin minier, 2 enfants, budget serré.",             "besoins":["trajets domicile travail","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants"]},
    {"id":2,  "avatar":"👩‍💼", "prenom":"Nathalie Guillanton", "age":57, "commune":"Donges",             "dep":"44",  "urbanite":"periurbain", "budget":11000, "profil":"Assistante administrative",   "resume":"PME logistique, balades, sensible CO₂.",              "besoins":["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire"]},
    {"id":3,  "avatar":"🔧",  "prenom":"Olivier Carpentier",  "age":43, "commune":"Coise (Rhône)",      "dep":"69",  "urbanite":"rural",      "budget":10000, "profil":"Ouvrier métallurgie",         "resume":"Village Beaujolais, routes campagne, pêcheur.",       "besoins":["trajets domicile travail","Faire ses courses","se rendre sur les sites d'activités sportives"]},
    {"id":4,  "avatar":"🛒",  "prenom":"Pauline Poree",       "age":27, "commune":"Saint-Égrève",       "dep":"38",  "urbanite":"periurbain", "budget":8000,  "profil":"Employée commerce",           "resume":"Banlieue grenobloise, randonneuse, budget limité.",   "besoins":["trajets domicile travail","Faire ses courses","se rendre sur les sites d'activités sportives"]},
    {"id":5,  "avatar":"🧑",  "prenom":"Ludovic Renard",      "age":26, "commune":"Corbère (66)",       "dep":"66",  "urbanite":"rural",      "budget":8000,  "profil":"Employé supermarché",         "resume":"Village catalan, pétanque, tourisme montagne.",       "besoins":["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]},
    {"id":6,  "avatar":"👴",  "prenom":"Daniel Turpin",       "age":70, "commune":"Quincieux (Rhône)",  "dep":"69",  "urbanite":"periurbain", "budget":9000,  "profil":"Retraité actif",              "resume":"Plus de navettes, cherche plaisir et praticité.",     "besoins":["Faire ses courses","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]},
    {"id":7,  "avatar":"📦",  "prenom":"Hanaé Hamzaoui",      "age":56, "commune":"Argenteuil",         "dep":"95",  "urbanite":"urbain",     "budget":13000, "profil":"Technicienne logistique",     "resume":"Zone urbaine dense, trajets courts, confort.",        "besoins":["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire"]},
    {"id":8,  "avatar":"⚓",  "prenom":"Romain Botherel",     "age":33, "commune":"Mons-en-Barœul",     "dep":"59",  "urbanite":"urbain",     "budget":3500,  "profil":"Manutentionnaire intérimaire","resume":"Budget RSA très serré, banlieue Lille.",              "besoins":["Faire ses courses","se rendre sur les sites d'activités sportives"]},
    {"id":9,  "avatar":"📋",  "prenom":"Corinne Monneret",    "age":59, "commune":"Orly",               "dep":"94",  "urbanite":"urbain",     "budget":11000, "profil":"Assistante de gestion",       "resume":"Banlieue parisienne, seule, praticité avant tout.",   "besoins":["trajets domicile travail","Faire ses courses"]},
    {"id":10, "avatar":"⚙️",  "prenom":"Mehmet Kancel",       "age":31, "commune":"Chambéry",           "dep":"73",  "urbanite":"periurbain", "budget":12000, "profil":"Technicien maintenance",      "resume":"Alpes, enfants, technique apprécié, sportif.",        "besoins":["trajets domicile travail","Faire ses courses","se rendre sur les sites d'activités sportives","Transport scolaire et périscolaire avec plusieurs enfants"]},
    {"id":11, "avatar":"🥛",  "prenom":"Audrey Poitiers",     "age":44, "commune":"Périgueux",          "dep":"24",  "urbanite":"periurbain", "budget":7000,  "profil":"Ouvrière laiterie",           "resume":"Mère célibataire, budget très contraint, yoga.",      "besoins":["trajets domicile travail","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants"]},
    {"id":12, "avatar":"🏔️", "prenom":"Paul Coubrun",         "age":61, "commune":"Val-Cenis",          "dep":"73",  "urbanite":"montagne",   "budget":11000, "profil":"Employé mairie alpine",       "resume":"Routes de montagne, lacets, proche retraite.",        "besoins":["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]},
    {"id":13, "avatar":"🥖",  "prenom":"Fabienne Assoun",     "age":57, "commune":"Niffer (68)",        "dep":"68",  "urbanite":"rural",      "budget":16000, "profil":"Boulangère artisane",         "resume":"Alsace, village rural, budget professionnel artisan.","besoins":["pour artisans","Faire ses courses","trajets domicile travail"]},
    {"id":14, "avatar":"🏗️", "prenom":"Antoine Zawada",       "age":35, "commune":"Paris 10e",          "dep":"75",  "urbanite":"urbain",     "budget":8000,  "profil":"Technicien HLM",              "resume":"Paris dense, Canal St-Martin, 25 km/h suffit.",      "besoins":["trajets domicile travail","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants"]},
    {"id":15, "avatar":"🌺",  "prenom":"Louis Proust",         "age":55, "commune":"Saint-Paul (Réunion)","dep":"974","urbanite":"ile",        "budget":15000, "profil":"Chargé de mission mairie",    "resume":"Routes sinueuses île, orchidées, Grand Bénare.",      "besoins":["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]},
]

# ─── DONNÉES VÉHICULES ────────────────────────────────────────────────────────
VEHICLES = [
    {"id":"circle",         "nom":"CIRCLE",             "fab":"CIRCLE-MOBILITY",        "cat":["L7e"],           "vitesse":90,  "prix":None,   "loc":350,  "usages":["Tourisme Découverte d'un territoire","Véhicule En libre service","Faire ses courses","trajets domicile travail","véhicules municipaux"]},
    {"id":"sorean",         "nom":"Sorean",             "fab":"QBX",                    "cat":["L6eBP"],         "vitesse":45,  "prix":11990,  "loc":None, "usages":["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire"]},
    {"id":"camigo",         "nom":"CamiGO",             "fab":"CAMINADE",               "cat":["VAE"],           "vitesse":25,  "prix":11000,  "loc":390,  "usages":["distribuer courrier et colis","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","véhicules municipaux","pour commerçants et stands mobiles"]},
    {"id":"pelican1",       "nom":"Pelican Train",      "fab":"Pelican",                "cat":["VAE"],           "vitesse":25,  "prix":2990,   "loc":190,  "usages":["distribuer courrier et colis","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","se rendre sur les sites d'activités sportives","véhicules municipaux"]},
    {"id":"ouicycle",       "nom":"Ouicycle",           "fab":"France Quadricycle",     "cat":["VAE","L1eA"],    "vitesse":25,  "prix":36000,  "loc":None, "usages":["Tourisme Découverte d'un territoire","Transport scolaire et périscolaire avec plusieurs enfants","véhicules municipaux"]},
    {"id":"vivaldi",        "nom":"Urbaner VIVALDI",    "fab":"HPR SOLUTIONS",          "cat":["VAE"],           "vitesse":25,  "prix":8600,   "loc":None, "usages":["Faire ses courses","distribuer courrier et colis","trajets domicile travail","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]},
    {"id":"boxoo",          "nom":"Urbaner BOXOO",      "fab":"HPR SOLUTIONS",          "cat":["VAE"],           "vitesse":25,  "prix":11500,  "loc":None, "usages":["distribuer courrier et colis","pour opérateur de maintenance et entretien","pour artisans","véhicules municipaux"]},
    {"id":"promener",       "nom":"Urbaner PROMENER",   "fab":"HPR SOLUTIONS",          "cat":["VAE"],           "vitesse":25,  "prix":5400,   "loc":None, "usages":["Tourisme Découverte d'un territoire","Faire ses courses","se rendre sur les sites d'activités sportives","trajets domicile travail"]},
    {"id":"tzer45",         "nom":"T-ZER 45",           "fab":"MOBILOW",                "cat":["L2e"],           "vitesse":45,  "prix":8000,   "loc":None, "usages":["Tourisme Découverte d'un territoire","Véhicule En libre service","Faire ses courses","se rendre sur les sites d'activités sportives","trajets domicile travail"]},
    {"id":"supercycle",     "nom":"Supercycle",         "fab":"Supercycle",             "cat":["VAE"],           "vitesse":25,  "prix":9084,   "loc":None, "usages":["Tourisme Découverte d'un territoire","Faire ses courses","se rendre sur les sites d'activités sportives","trajets domicile travail"]},
    {"id":"cygus",          "nom":"CYGUS",              "fab":"ERKA INDUSTRIES",        "cat":["VAE"],           "vitesse":25,  "prix":None,   "loc":None, "usages":["véhicules municipaux","pour commerçants et stands mobiles","pour artisans","pour opérateur de maintenance et entretien","distribuer courrier et colis"]},
    {"id":"tzer90",         "nom":"T-ZER 90",           "fab":"MOBILOW",                "cat":["L5e"],           "vitesse":90,  "prix":12500,  "loc":None, "usages":["Tourisme Découverte d'un territoire","Véhicule En libre service","Faire ses courses","se rendre sur les sites d'activités sportives","trajets domicile travail"]},
    {"id":"maillon-cargo",  "nom":"Maillon Cargo",      "fab":"Maillon Mobility",       "cat":["VAE"],           "vitesse":25,  "prix":9000,   "loc":None, "usages":["distribuer courrier et colis","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","pour secteur agricole","se rendre sur les sites d'activités sportives","surveillance incendie","véhicules municipaux"]},
    {"id":"maillon-daily",  "nom":"Maillon Daily",      "fab":"Maillon Mobility",       "cat":["VAE"],           "vitesse":25,  "prix":9000,   "loc":None, "usages":["Tourisme Découverte d'un territoire","Véhicule En libre service","Faire ses courses","véhicules municipaux","trajets domicile travail","se rendre sur les sites d'activités sportives"]},
    {"id":"nocar",          "nom":"Nocar",              "fab":"Helio2",                 "cat":["VAE"],           "vitesse":25,  "prix":17900,  "loc":None, "usages":["Tourisme Découverte d'un territoire","Faire ses courses","véhicules municipaux","trajets domicile travail"]},
    {"id":"vemoo",          "nom":"VeMoo",              "fab":"VeMoo SAS",              "cat":["VAE"],           "vitesse":25,  "prix":10000,  "loc":None, "usages":["Tourisme Découverte d'un territoire","Faire ses courses","pour artisans","se rendre sur les sites d'activités sportives","trajets domicile travail"]},
    {"id":"bob",            "nom":"BOB",                "fab":"Sanka Cycle",            "cat":["VAE"],           "vitesse":25,  "prix":12000,  "loc":None, "usages":["trajets domicile travail","Faire ses courses","se rendre sur les sites d'activités sportives","véhicules municipaux"]},
    {"id":"bagnole",        "nom":"La bagnole",         "fab":"KILOW",                  "cat":["L6eB","L7e"],    "vitesse":80,  "prix":13000,  "loc":None, "usages":["distribuer courrier et colis","Tourisme Découverte d'un territoire","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","pour secteur agricole","Transport scolaire et périscolaire avec plusieurs enfants","se rendre sur les sites d'activités sportives","surveillance incendie","trajets domicile travail","véhicules municipaux"]},
    {"id":"ulive",          "nom":"Ulive",              "fab":"Avatar Mobilité",        "cat":["L7e","L7eC"],    "vitesse":90,  "prix":15000,  "loc":None, "usages":["distribuer courrier et colis","Tourisme Découverte d'un territoire","Véhicule En libre service","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","se rendre sur les sites d'activités sportives","trajets domicile travail","véhicules municipaux","pour secteur agricole"]},
    {"id":"vuf-poly",       "nom":"VUF XXL MAX POLY",   "fab":"VUF BIKES",              "cat":["VAE"],           "vitesse":25,  "prix":7500,   "loc":None, "usages":["distribuer courrier et colis","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","pour secteur agricole","surveillance incendie","véhicules municipaux"]},
    {"id":"vuf-taxi",       "nom":"VUF XXL TAXI",       "fab":"VUF BIKES",              "cat":["VAE"],           "vitesse":25,  "prix":7500,   "loc":None, "usages":["Tourisme Découverte d'un territoire","véhicules municipaux","se rendre sur les sites d'activités sportives"]},
    {"id":"dual",           "nom":"DUAL",               "fab":"AEMOTION",               "cat":["L5e"],           "vitesse":115, "prix":19000,  "loc":None, "usages":["Faire ses courses","pour opérateur de maintenance et entretien","trajets domicile travail","véhicules municipaux"]},
    {"id":"midipile",       "nom":"MIDIPILE",           "fab":"MIDIPILE",               "cat":["L6eBU"],         "vitesse":45,  "prix":15500,  "loc":None, "usages":["distribuer courrier et colis","Tourisme Découverte d'un territoire","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","se rendre sur les sites d'activités sportives","surveillance incendie","trajets domicile travail","véhicules municipaux"]},
    {"id":"kozi",           "nom":"KOZI",               "fab":"Karbikes",               "cat":["VAE"],           "vitesse":25,  "prix":10625,  "loc":None, "usages":["Tourisme Découverte d'un territoire","Véhicule En libre service","Faire ses courses","se rendre sur les sites d'activités sportives","Transport scolaire et périscolaire avec plusieurs enfants","trajets domicile travail"]},
    {"id":"koli",           "nom":"KOLI",               "fab":"Karbikes",               "cat":["VAE"],           "vitesse":25,  "prix":12150,  "loc":None, "usages":["distribuer courrier et colis","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","se rendre sur les sites d'activités sportives"]},
    {"id":"kubi",           "nom":"KUBI",               "fab":"Karbikes",               "cat":["VAE"],           "vitesse":25,  "prix":10800,  "loc":None, "usages":["distribuer courrier et colis","Faire ses courses","pour opérateur de maintenance et entretien","véhicules municipaux","pour artisans"]},
    {"id":"kari",           "nom":"KARI",               "fab":"Karbikes",               "cat":["VAE"],           "vitesse":25,  "prix":11050,  "loc":None, "usages":["pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","véhicules municipaux"]},
    {"id":"weez",           "nom":"Weez Lite",          "fab":"Eon Motors",             "cat":["L7e"],           "vitesse":90,  "prix":14200,  "loc":None, "usages":["distribuer courrier et colis","Tourisme Découverte d'un territoire","Véhicule En libre service","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","se rendre sur les sites d'activités sportives","surveillance incendie","trajets domicile travail","véhicules municipaux"]},
    {"id":"arsene",         "nom":"Arsène",             "fab":"Arsène",                 "cat":["L7eC"],          "vitesse":80,  "prix":13300,  "loc":None, "usages":["Faire ses courses","pour artisans","se rendre sur les sites d'activités sportives","trajets domicile travail","véhicules municipaux","Tourisme Découverte d'un territoire"]},
    {"id":"woodybus",       "nom":"Woodybus",           "fab":"Humbird",                "cat":["VAE"],           "vitesse":25,  "prix":19990,  "loc":None, "usages":["Transport scolaire et périscolaire avec plusieurs enfants","se rendre sur les sites d'activités sportives","véhicules municipaux","trajets domicile travail","Tourisme Découverte d'un territoire"]},
    {"id":"act31",          "nom":"ACT3.1 VAE",         "fab":"Acticycle",              "cat":["VAE"],           "vitesse":25,  "prix":9917,   "loc":None, "usages":["distribuer courrier et colis","Tourisme Découverte d'un territoire","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","se rendre sur les sites d'activités sportives","trajets domicile travail","véhicules municipaux"]},
    {"id":"act36",          "nom":"ACT3.6 RANDO",       "fab":"Acticycle",              "cat":["L6eBP"],         "vitesse":45,  "prix":12000,  "loc":None, "usages":["distribuer courrier et colis","Tourisme Découverte d'un territoire","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","trajets domicile travail","véhicules municipaux"]},
    {"id":"eroe25c",        "nom":"e-roe 25 Cargo",     "fab":"E-ROE",                  "cat":["VAE"],           "vitesse":25,  "prix":9400,   "loc":None, "usages":["distribuer courrier et colis","Véhicule En libre service","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","se rendre sur les sites d'activités sportives","surveillance incendie","véhicules municipaux"]},
    {"id":"eroe25p",        "nom":"e-roe 25 Passenger", "fab":"E-ROE",                  "cat":["VAE"],           "vitesse":25,  "prix":9400,   "loc":None, "usages":["Tourisme Découverte d'un territoire","Véhicule En libre service","Faire ses courses","se rendre sur les sites d'activités sportives","Transport scolaire et périscolaire avec plusieurs enfants","trajets domicile travail","véhicules municipaux"]},
    {"id":"eroe45p",        "nom":"e-roe 45 Passenger", "fab":"E-ROE",                  "cat":["L6eB","L6eBP"],  "vitesse":45,  "prix":9800,   "loc":None, "usages":["Tourisme Découverte d'un territoire","Véhicule En libre service","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants","se rendre sur les sites d'activités sportives","trajets domicile travail","véhicules municipaux"]},
    {"id":"eroe45c",        "nom":"e-roe 45 Cargo",     "fab":"E-ROE",                  "cat":["L6eB","L6eBU"],  "vitesse":45,  "prix":9800,   "loc":None, "usages":["distribuer courrier et colis","Véhicule En libre service","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","surveillance incendie","véhicules municipaux"]},
    {"id":"mstracker",      "nom":"MS TRACKER",         "fab":"MOBISLOW",               "cat":["L7e","L7eC","L6eB"],"vitesse":80,"prix":13000,  "loc":None, "usages":["distribuer courrier et colis","Tourisme Découverte d'un territoire","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","pour secteur agricole","se rendre sur les sites d'activités sportives","surveillance incendie","trajets domicile travail","véhicules municipaux"]},
    {"id":"xbikium",        "nom":"X-Bikium Utility",   "fab":"X-Bikium",               "cat":["VAE"],           "vitesse":25,  "prix":5990,   "loc":None, "usages":["distribuer courrier et colis","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","véhicules municipaux"]},
    {"id":"pelican2",       "nom":"PelicanTrain",       "fab":"Pelican Cycles",         "cat":["VAE"],           "vitesse":25,  "prix":7490,   "loc":None, "usages":["distribuer courrier et colis","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","véhicules municipaux"]},
    {"id":"moskitos",       "nom":"moskitOS",           "fab":"moskitOS",               "cat":["VAE"],           "vitesse":100, "prix":1200,   "loc":None, "usages":["Tourisme Découverte d'un territoire","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","se rendre sur les sites d'activités sportives","trajets domicile travail"]},
    {"id":"kiwee",          "nom":"KIWEE",              "fab":"METACAR MOBILITY SYSTEMS","cat":["L6eB","L6eBP"],  "vitesse":45,  "prix":20000,  "loc":None, "usages":["Tourisme Découverte d'un territoire","Véhicule En libre service","Faire ses courses","pour opérateur de maintenance et entretien","trajets domicile travail","véhicules municipaux"]},
    {"id":"baker",          "nom":"Baker-Prax",         "fab":"PRAX",                   "cat":["VAE"],           "vitesse":25,  "prix":11600,  "loc":None, "usages":["distribuer courrier et colis","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","pour secteur agricole","surveillance incendie","véhicules municipaux","trajets domicile travail"]},
    {"id":"cyclesmidi",     "nom":"Cargo Cycles du Midi","fab":"Cycles du Midi",        "cat":["VAE"],           "vitesse":25,  "prix":4200,   "loc":None, "usages":["Tourisme Découverte d'un territoire","Faire ses courses","pour artisans","pour commerçants et stands mobiles","trajets domicile travail","Véhicule En libre service","distribuer courrier et colis"]},
    {"id":"aemotion2",      "nom":"AEMOTION L5e",       "fab":"AEMOTION",               "cat":["L5e"],           "vitesse":115, "prix":None,   "loc":None, "usages":["pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","trajets domicile travail","véhicules municipaux"]},
    {"id":"bigtetu",        "nom":"BigTetu",            "fab":"BigTetu Cargo Bikes",    "cat":["VAE","L1eA"],    "vitesse":25,  "prix":6209,   "loc":None, "usages":["distribuer courrier et colis","Véhicule En libre service","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","se rendre sur les sites d'activités sportives","surveillance incendie","véhicules municipaux"]},
    {"id":"fourmi",         "nom":"La Fourmi",          "fab":"AirNAM",                 "cat":["VAE"],           "vitesse":25,  "prix":3625,   "loc":None, "usages":["Tourisme Découverte d'un territoire","Faire ses courses","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","se rendre sur les sites d'activités sportives"]},
    {"id":"drakkar-nobox-l","nom":"DRAKKAR NoBox L",    "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":8990,   "loc":None, "usages":["pour opérateur de maintenance et entretien","distribuer courrier et colis"]},
    {"id":"ketch-cleen",    "nom":"KETCH CLEEN",        "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":7549,   "loc":None, "usages":["pour opérateur de maintenance et entretien","véhicules municipaux"]},
    {"id":"ketch-stand",    "nom":"KETCH STAND",        "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":10888,  "loc":None, "usages":["pour commerçants et stands mobiles","véhicules municipaux"]},
    {"id":"ketch-delivery", "nom":"KETCH DELIVERY",     "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":9199,   "loc":None, "usages":["distribuer courrier et colis","pour artisans","véhicules municipaux","se rendre sur les sites d'activités sportives","pour commerçants et stands mobiles","Faire ses courses"]},
    {"id":"ketch-nobox",    "nom":"KETCH NOBOX",        "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":6499,   "loc":None, "usages":["pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","véhicules municipaux","distribuer courrier et colis"]},
    {"id":"clipper-food",   "nom":"CLIPPER FOOD",       "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":13999,  "loc":None, "usages":["pour commerçants et stands mobiles"]},
    {"id":"clipper-nobox",  "nom":"CLIPPER NOBOX",      "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":6999,   "loc":None, "usages":["distribuer courrier et colis","pour opérateur de maintenance et entretien","pour artisans","pour commerçants et stands mobiles","véhicules municipaux"]},
    {"id":"drakkar-cargo-l","nom":"DRAKKAR CARGO L",    "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":20999,  "loc":None, "usages":["distribuer courrier et colis","Faire ses courses","pour artisans","pour commerçants et stands mobiles","véhicules municipaux"]},
    {"id":"drakkar-green-l","nom":"DRAKKAR GREEN L",    "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":18999,  "loc":None, "usages":["pour artisans","pour secteur agricole","véhicules municipaux","pour opérateur de maintenance et entretien"]},
    {"id":"drakkar-flat-l", "nom":"DRAKKAR FLAT L",     "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":16599,  "loc":None, "usages":["pour opérateur de maintenance et entretien","pour artisans","véhicules municipaux"]},
    {"id":"drakkar-nobox-s","nom":"DRAKKAR NoBox S",    "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":12999,  "loc":None, "usages":["pour opérateur de maintenance et entretien","véhicules municipaux"]},
    {"id":"drakkar-cargo-s","nom":"DRAKKAR CARGO S",    "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":18999,  "loc":None, "usages":["pour opérateur de maintenance et entretien","véhicules municipaux","distribuer courrier et colis"]},
    {"id":"drakkar-green-s","nom":"DRAKKAR GREEN S",    "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":16999,  "loc":None, "usages":["pour opérateur de maintenance et entretien","pour artisans","pour secteur agricole","véhicules municipaux"]},
    {"id":"drakkar-flat-s", "nom":"DRAKKAR FLAT S",     "fab":"BLUEMOOOV",              "cat":["VAE"],           "vitesse":25,  "prix":14999,  "loc":None, "usages":["pour opérateur de maintenance et entretien","pour artisans","véhicules municipaux","pour secteur agricole"]},
]

USAGE_ACTIF = {"Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives",
               "Faire ses courses","trajets domicile travail",
               "Transport scolaire et périscolaire avec plusieurs enfants","Véhicule En libre service"}
USAGE_PRO   = {"distribuer courrier et colis","pour opérateur de maintenance et entretien",
               "pour artisans","pour commerçants et stands mobiles",
               "pour secteur agricole","surveillance incendie","véhicules municipaux"}

URBANITE_LABELS = {"urbain":"🏙️ Urbain","periurbain":"🏘️ Périurbain",
                   "rural":"🌾 Rural","montagne":"🏔️ Montagne","ile":"🌊 Île"}

# ─── ALGO DE SCORING ──────────────────────────────────────────────────────────
def speed_score(urbanite, vitesse):
    table = {
        "urbain":     {25:40, 45:35, 999:28},
        "periurbain": {25:8,  45:38, 999:40},
        "rural":      {25:0,  45:22, 999:40},
        "montagne":   {25:0,  45:15, 999:40},
        "ile":        {25:8,  45:28, 999:40},
    }
    row = table.get(urbanite, {25:15, 45:25, 999:30})
    if vitesse <= 25: return row[25]
    if vitesse <= 45: return row[45]
    return row[999]

def compute_score(persona, vehicle, budget):
    # Budget (30 pts)
    if vehicle["prix"] is None:
        b = 12
    else:
        r = vehicle["prix"] / budget
        b = 30 if r<=1 else 22 if r<=1.25 else 14 if r<=1.5 else 6 if r<=2 else 0

    # Territoire (40 pts)
    s = speed_score(persona["urbanite"], vehicle["vitesse"])

    # Usages (30 pts)
    covered   = [x for x in persona["besoins"] if x in vehicle["usages"]]
    uncovered = [x for x in persona["besoins"] if x not in vehicle["usages"]]
    u = round((len(covered) / len(persona["besoins"])) * 30) if persona["besoins"] else 15

    return {"b":b, "s":s, "u":u, "total":b+s+u, "covered":covered, "uncovered":uncovered}

def badge_info(total):
    if total >= 85: return "🟢 Excellent",  "#dcfce7", "#14532d"
    if total >= 68: return "🔵 Bon match",  "#dbeafe", "#1e3a8a"
    if total >= 48: return "🟡 Partiel",    "#fef3c7", "#78350f"
    if total >= 28: return "🟠 Faible",     "#ffedd5", "#7c2d12"
    return              "🔴 Non adapté",    "#fee2e2", "#7f1d1d"

def bar_color(total):
    if total >= 85: return "#16a34a"
    if total >= 68: return "#2563eb"
    if total >= 48: return "#d97706"
    if total >= 28: return "#ea580c"
    return "#dc2626"

# ─── INIT SESSION STATE ───────────────────────────────────────────────────────
if "reactions" not in st.session_state:
    st.session_state.reactions = {}

# ─── SIDEBAR : sélection persona ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚲 Simulateur Vélis")
    st.markdown("**15 Personas** · NVIDIA Nemotron-FR")
    st.divider()
    persona_labels = [f"{p['avatar']} {p['prenom']} · {p['age']}a · {p['commune']}" for p in PERSONAS]
    selected_idx   = st.radio("Choisir un persona", range(len(PERSONAS)),
                              format_func=lambda i: persona_labels[i], label_visibility="collapsed")
    persona = PERSONAS[selected_idx]

# ─── HEADER : infos persona + curseur budget ─────────────────────────────────
col_avatar, col_info, col_stats = st.columns([1, 5, 2])

with col_avatar:
    st.markdown(f"<div style='font-size:64px;line-height:1;margin-top:10px'>{persona['avatar']}</div>",
                unsafe_allow_html=True)

with col_info:
    st.markdown(f"### {persona['prenom']} — {persona['age']} ans")
    st.markdown(f"*{persona['profil']}* · {persona['commune']} ({persona['dep']}) · {URBANITE_LABELS[persona['urbanite']]}")
    st.caption(persona["resume"])
    besoins_html = " ".join([f"<span class='tag-neu'>{b}</span>" for b in persona["besoins"]])
    st.markdown(besoins_html, unsafe_allow_html=True)

budget = st.slider(
    f"💰 Budget d'achat  *(défaut persona : {persona['budget']:,} €)*",
    min_value=1000, max_value=40000, step=500, value=persona["budget"],
    format="%d €"
)

st.divider()

# ─── FILTRES ─────────────────────────────────────────────────────────────────
fc1, fc2, fc3 = st.columns(3)
with fc1:
    filtre_vitesse = st.selectbox("🚀 Vitesse maxi", ["Tous","≤ 25 km/h","≤ 45 km/h","≤ 90 km/h"])
with fc2:
    filtre_mode = st.selectbox("🎯 Usage", ["Tous","Actif / Perso","Pro / Utilitaire"])
with fc3:
    filtre_fin = st.selectbox("💳 Financement", ["Tous","Prix connu (achat)","Location disponible"])

# ─── FILTRAGE + SCORING ───────────────────────────────────────────────────────
def apply_filters(v):
    if filtre_vitesse == "≤ 25 km/h"  and v["vitesse"] > 25:  return False
    if filtre_vitesse == "≤ 45 km/h"  and v["vitesse"] > 45:  return False
    if filtre_vitesse == "≤ 90 km/h"  and v["vitesse"] > 90:  return False
    if filtre_mode   == "Actif / Perso"    and not any(u in USAGE_ACTIF for u in v["usages"]): return False
    if filtre_mode   == "Pro / Utilitaire" and not any(u in USAGE_PRO   for u in v["usages"]): return False
    if filtre_fin    == "Prix connu (achat)"   and v["prix"] is None: return False
    if filtre_fin    == "Location disponible"  and v["loc"]  is None: return False
    return True

scored = []
for v in VEHICLES:
    if not apply_filters(v):
        continue
    sc = compute_score(persona, v, budget)
    scored.append({**v, **sc})

scored.sort(key=lambda x: x["total"], reverse=True)

# Compteurs
nb_excellent = sum(1 for v in scored if v["total"] >= 85)
nb_bon       = sum(1 for v in scored if 68 <= v["total"] < 85)
nb_partiel   = sum(1 for v in scored if 48 <= v["total"] < 68)

with col_stats:
    m1, m2, m3 = st.columns(3)
    m1.metric("🟢 Excellent", nb_excellent)
    m2.metric("🔵 Bon match", nb_bon)
    m3.metric("🟡 Partiel",   nb_partiel)

st.markdown(f"**{len(scored)} véhicules** correspondent aux filtres · score = Budget(30) + Territoire(40) + Usages(30)")
st.divider()

# ─── AFFICHAGE VÉHICULES ─────────────────────────────────────────────────────
if not scored:
    st.warning("Aucun véhicule ne correspond à ces filtres. Essaie d'en assouplir certains.")
else:
    for i, v in enumerate(scored):
        label, bg, txt = badge_info(v["total"])
        color = bar_color(v["total"])
        prix_str  = f"{v['prix']:,} € HT" if v["prix"] is not None else "sur devis"
        loc_str   = f"· loc. {v['loc']} €/mois" if v["loc"] else ""
        cats_str  = " / ".join(v["cat"])

        prix_ok   = v["prix"] is not None and v["prix"] <= budget
        prix_high = v["prix"] is not None and v["prix"] > budget

        with st.container(border=True):
            c1, c2 = st.columns([1, 7])
            with c1:
                st.markdown(f"<div style='text-align:center'>"
                            f"<div style='font-size:11px;color:#94a3b8'>#{i+1}</div>"
                            f"<div style='font-size:32px;font-weight:700;color:{color}'>{v['total']}</div>"
                            f"<div style='font-size:9px;color:#94a3b8'>/100</div>"
                            f"<span style='background:{bg};color:{txt};padding:2px 6px;border-radius:4px;font-size:10px;font-weight:600'>{label}</span>"
                            f"</div>", unsafe_allow_html=True)
            with c2:
                # Nom + badges inline
                prix_color = "#15803d" if prix_ok else ("#b91c1c" if prix_high else "#854d0e")
                prix_bg    = "#dcfce7" if prix_ok else ("#fee2e2" if prix_high else "#fef9c3")
                st.markdown(
                    f"**{v['nom']}** &nbsp; <span style='color:#94a3b8;font-size:13px'>{v['fab']}</span> &nbsp;"
                    f"<span class='tag-neu'>{cats_str}</span> &nbsp;"
                    f"<span class='tag-neu'>{v['vitesse']} km/h</span> &nbsp;"
                    f"<span style='background:{prix_bg};color:{prix_color};padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600'>{prix_str}</span>"
                    + (f" &nbsp;<span style='background:#ede9fe;color:#5b21b6;padding:2px 7px;border-radius:4px;font-size:11px'>{loc_str.strip()}</span>" if loc_str else ""),
                    unsafe_allow_html=True
                )

                # Barres de progression
                bc1, bc2, bc3 = st.columns(3)
                bc1.progress(v["b"]/30, text=f"💰 Budget : {v['b']}/30")
                bc2.progress(v["s"]/40, text=f"🗺️ Territoire : {v['s']}/40")
                bc3.progress(v["u"]/30, text=f"🎯 Usages : {v['u']}/30")

                # Tags usages
                tags_html = (
                    " ".join([f"<span class='tag-ok'>✓ {b}</span>" for b in v["covered"]]) + " " +
                    " ".join([f"<span class='tag-ko'>✗ {b}</span>" for b in v["uncovered"]])
                )
                st.markdown(tags_html, unsafe_allow_html=True)

                # Bouton réaction IA
                key = f"{persona['id']}-{v['id']}"
                if key in st.session_state.reactions:
                    st.markdown(
                        f"<div class='reaction-box'>"
                        f"<div style='font-size:10px;color:#6366f1;font-weight:600;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.05em'>"
                        f"Réaction de {persona['prenom'].split()[0]}</div>"
                        f"{st.session_state.reactions[key]}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    if st.button(f"✦ Simuler la réaction de {persona['prenom'].split()[0]}", key=f"btn_{key}"):
                        with st.spinner("Génération en cours…"):
                            prompt = (
                                f"Tu es {persona['prenom']}, {persona['age']} ans, {persona['profil']}, "
                                f"habitant {persona['commune']} ({persona['dep']}). {persona['resume']} "
                                f"Budget mobilité : {budget:,}€. Besoins : {', '.join(persona['besoins'])}. "
                                f"Territoire : {URBANITE_LABELS[persona['urbanite']]}.\n\n"
                                f"Tu découvres le \"{v['nom']}\" ({v['fab']}) — {v['vitesse']} km/h, "
                                f"{prix_str}{(' · location '+str(v['loc'])+'€/mois') if v['loc'] else ''}.\n\n"
                                f"En 2-3 phrases à la 1ère personne, donne ta réaction sincère sur ce véhicule. "
                                f"Sois concret sur le territoire, le prix, et l'usage quotidien."
                            )
                            try:
                                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                                message = client.messages.create(
                                    model="claude-sonnet-4-20250514",
                                    max_tokens=300,
                                    messages=[{"role":"user","content":prompt}]
                                )
                                st.session_state.reactions[key] = message.content[0].text
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erreur API : {e}")
