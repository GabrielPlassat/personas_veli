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
    .block-container { padding-top: 2.5rem; padding-bottom: 1rem; }
    .stSidebar { background-color: #0f172a; }
    .persona-header { background: #f8fafc; border-radius: 10px; padding: 14px 18px; border: 1px solid #e2e8f0; margin-bottom: 12px; }
    .vehicle-card { background: white; border-radius: 10px; padding: 14px 18px; border: 1px solid #e2e8f0; margin-bottom: 8px; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .tag-ok  { background: #dcfce7; color: #15803d; padding: 2px 7px; border-radius: 4px; font-size: 11px; display: inline-block; margin: 2px; }
    .tag-ko  { background: #fee2e2; color: #b91c1c; padding: 2px 7px; border-radius: 4px; font-size: 11px; display: inline-block; margin: 2px; }
    .tag-neu { background: #f1f5f9; color: #475569; padding: 2px 7px; border-radius: 4px; font-size: 11px; display: inline-block; margin: 2px; }
    .reaction-box { background: #f8fafc; border-left: 3px solid #a5b4fc; border-radius: 6px; padding: 10px 14px; margin-top: 8px; font-size: 13px; color: #334155; }
    .score-label { font-size: 11px; color: #94a3b8; margin-bottom: 2px; }
    div[data-testid="stSidebarContent"] { background-color: #0f172a; }
    div[data-testid="stSidebarContent"] * { color: #e2e8f0 !important; }
    div[data-testid="stSidebarContent"] .stRadio label { color: #cbd5e1 !important; font-size: 13px !important; }
    div[data-testid="stSidebarContent"] h1,
    div[data-testid="stSidebarContent"] h2,
    div[data-testid="stSidebarContent"] h3,
    div[data-testid="stSidebarContent"] p,
    div[data-testid="stSidebarContent"] strong { color: #f1f5f9 !important; }
    div[data-testid="stSidebarContent"] hr { border-color: #334155 !important; }
</style>
""", unsafe_allow_html=True)

# ─── DONNÉES PERSONAS (enrichies — source NVIDIA Nemotron-Personas-France) ────
PERSONAS = [
    {"id":1,  "avatar":"👷‍♀️", "prenom":"Epse Janiak",        "age":39, "commune":"Bruay-la-Buissière", "dep":"62",  "urbanite":"periurbain", "budget":9000,
     "profil":"Ouvrière maintenance",        "resume":"Bassin minier, 2 enfants, budget serré.",
     "culture":"Patrimoine minier du Nord, art flamand, musées locaux",
     "sport":"Marche nordique, poterie sportive, randonnée famille",
     "travel":"Vacances en famille en Bretagne, tourisme régional Nord",
     "skills":"Maintenance industrielle, électricité basse tension, diagnostic pannes",
     "hobbies":"Poterie, jardinage, bénévolat association scolaire",
     "besoins":["trajets domicile travail","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants"]},

    {"id":2,  "avatar":"👩‍💼", "prenom":"Nathalie Guillanton", "age":57, "commune":"Donges",             "dep":"44",  "urbanite":"periurbain", "budget":11000,
     "profil":"Assistante administrative",    "resume":"PME logistique, balades, sensible CO₂.",
     "culture":"Musées des Pays de la Loire, expositions contemporaines, livres d'histoire",
     "sport":"Marche nordique, natation, balades nature",
     "travel":"Voyages culturels en Europe, tourisme de patrimoine, Loire à vélo",
     "skills":"Bureautique avancée, gestion documentaire, organisation",
     "hobbies":"Aquarelle, lecture, jardinage, sorties culturelles",
     "besoins":["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire"]},

    {"id":3,  "avatar":"🔧",  "prenom":"Olivier Carpentier",  "age":43, "commune":"Coise (Rhône)",      "dep":"69",  "urbanite":"rural",      "budget":10000,
     "profil":"Ouvrier métallurgie",          "resume":"Village Beaujolais, routes campagne, pêcheur.",
     "culture":"Patrimoine Beaujolais, fêtes du vin, culture ouvrière",
     "sport":"Pêche en rivière, VTT sur chemins ruraux, randonnée",
     "travel":"Camping Ardèche, circuits Bourgogne, tourisme local",
     "skills":"Soudure MIG/TIG, mécanique auto et moto, bricolage polyvalent, électricité",
     "hobbies":"Réparation d'objets, jardinage potager, mécanique vélo, pêche",
     "besoins":["trajets domicile travail","Faire ses courses","se rendre sur les sites d'activités sportives"]},

    {"id":4,  "avatar":"🛒",  "prenom":"Pauline Poree",       "age":27, "commune":"Saint-Égrève",       "dep":"38",  "urbanite":"periurbain", "budget":8000,
     "profil":"Employée commerce",            "resume":"Banlieue grenobloise, randonneuse, budget limité.",
     "culture":"Scène culturelle grenobloise, cinéma indépendant, street art",
     "sport":"Randonnée en Chartreuse, yoga, escalade en salle",
     "travel":"Week-ends découverte Alpes, Vercors, camping sauvage",
     "skills":"Vente, relation client, informatique bureautique",
     "hobbies":"Cuisine végétarienne, jeux de société, photographie nature",
     "besoins":["trajets domicile travail","Faire ses courses","se rendre sur les sites d'activités sportives"]},

    {"id":5,  "avatar":"🧑",  "prenom":"Ludovic Renard",      "age":26, "commune":"Corbère (66)",       "dep":"66",  "urbanite":"rural",      "budget":8000,
     "profil":"Employé supermarché",          "resume":"Village catalan, pétanque, tourisme montagne.",
     "culture":"Culture catalane, sardane, festivals Pyrénées-Orientales",
     "sport":"Randonnée dans les Albères, pétanque, VTT occasionnel",
     "travel":"Tourisme local catalan, Espagne voisine, mer Méditerranée",
     "skills":"Commerce polyvalent, encaissement, logistique rayon",
     "hobbies":"BD franco-belge, pétanque, cuisine catalane",
     "besoins":["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]},

    {"id":6,  "avatar":"👴",  "prenom":"Daniel Turpin",       "age":70, "commune":"Quincieux (Rhône)",  "dep":"69",  "urbanite":"periurbain", "budget":9000,
     "profil":"Retraité actif",               "resume":"Plus de navettes, cherche plaisir et praticité.",
     "culture":"Patrimoine lyonnais, musées Gallo-romains, brocantes",
     "sport":"Pêche en Saône, marche, vélo de loisir sur voies vertes",
     "travel":"Tourisme Bourgogne, Provence, voyages fluviaux",
     "skills":"Bricolage tous corps d'état, jardinage maraîcher, repair café bénévole",
     "hobbies":"Jardinage potager, repair café, pêche, brocantes",
     "besoins":["Faire ses courses","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]},

    {"id":7,  "avatar":"📦",  "prenom":"Hanaé Hamzaoui",      "age":56, "commune":"Argenteuil",         "dep":"95",  "urbanite":"urbain",     "budget":13000,
     "profil":"Technicienne logistique",      "resume":"Zone urbaine dense, trajets courts, confort.",
     "culture":"Culture franco-algérienne, musiques du Maghreb, cinéma arabe",
     "sport":"Marche active, fitness en salle, natation",
     "travel":"Voyages en Algérie famille, tourisme culturel Europe",
     "skills":"Gestion de flux logistiques, ERP, organisation entrepôt",
     "hobbies":"Cuisine maghrébine, décoration intérieure, couture",
     "besoins":["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire"]},

    {"id":8,  "avatar":"⚓",  "prenom":"Romain Botherel",     "age":33, "commune":"Mons-en-Barœul",     "dep":"59",  "urbanite":"urbain",     "budget":3500,
     "profil":"Manutentionnaire intérimaire", "resume":"Budget RSA très serré, banlieue Lille.",
     "culture":"Culture ouvrière du Nord, supporter LOSC, musique électro",
     "sport":"Football en loisir, promenades bord de Deûle, vélo urbain",
     "travel":"Peu de voyages, sorties locales Lille métropole",
     "skills":"Manutention, conduite chariot, force physique",
     "hobbies":"Football, jeux vidéo, promenades vélo bords de Deûle",
     "besoins":["Faire ses courses","se rendre sur les sites d'activités sportives"]},

    {"id":9,  "avatar":"📋",  "prenom":"Corinne Monneret",    "age":59, "commune":"Orly",               "dep":"94",  "urbanite":"urbain",     "budget":11000,
     "profil":"Assistante de gestion",        "resume":"Banlieue parisienne, seule, praticité avant tout.",
     "culture":"Culture francilienne, musées Paris, patrimoine Val-de-Marne",
     "sport":"Salsa en club, marche urbaine, natation",
     "travel":"Vacances Martinique, balades IDF, week-ends Normandie",
     "skills":"Comptabilité, bureautique Office, gestion fournisseurs",
     "hobbies":"Salsa, karaoké, balades, cuisine créole",
     "besoins":["trajets domicile travail","Faire ses courses"]},

    {"id":10, "avatar":"⚙️",  "prenom":"Mehmet Kancel",       "age":31, "commune":"Chambéry",           "dep":"73",  "urbanite":"periurbain", "budget":12000,
     "profil":"Technicien maintenance",       "resume":"Alpes, enfants, technique apprécié, sportif.",
     "culture":"Culture franco-turque, musiques d'Anatolie, fêtes alpines",
     "sport":"Randonnée alpine, ski de fond, vélo de montagne VTT",
     "travel":"Turquie en famille, tourisme alpin Savoie, Italie du Nord",
     "skills":"Maintenance industrielle, électronique, hydraulique, mécanique moto",
     "hobbies":"Mécanique moto et vélo, bricolage électronique, ski",
     "besoins":["trajets domicile travail","Faire ses courses","se rendre sur les sites d'activités sportives","Transport scolaire et périscolaire avec plusieurs enfants"]},

    {"id":11, "avatar":"🥛",  "prenom":"Audrey Poitiers",     "age":44, "commune":"Périgueux",          "dep":"24",  "urbanite":"periurbain", "budget":7000,
     "profil":"Ouvrière laiterie",            "resume":"Mère célibataire, budget très contraint, yoga.",
     "culture":"Patrimoine Périgord, préhistoire, gastronomie du Sud-Ouest",
     "sport":"Yoga, marche en forêt, baignade Dordogne",
     "travel":"Vacances Périgord noir, tourisme local, pas de grands voyages",
     "skills":"Agroalimentaire, rigueur hygiène, conduite ligne de production",
     "hobbies":"Aquarelle, jardinage, lecture, sorties musée avec enfants",
     "besoins":["trajets domicile travail","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants"]},

    {"id":12, "avatar":"🏔️", "prenom":"Paul Coubrun",         "age":61, "commune":"Val-Cenis",          "dep":"73",  "urbanite":"montagne",   "budget":11000,
     "profil":"Employé mairie alpine",        "resume":"Routes de montagne, lacets, proche retraite.",
     "culture":"Culture savoyarde, patrimoine fortifié Maurienne, musique de montagne",
     "sport":"Ski alpin et de fond, randonnée montagne, VTT électrique",
     "travel":"Tourisme alpin Italie, Savoie, balades transfrontalières vélo",
     "skills":"Administration publique, photographie, connaissance du terrain alpin",
     "hobbies":"Photographie paysages, VTT, ski, randonnée Grand Arc",
     "besoins":["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]},

    {"id":13, "avatar":"🥖",  "prenom":"Fabienne Assoun",     "age":57, "commune":"Niffer (68)",        "dep":"68",  "urbanite":"rural",      "budget":16000,
     "profil":"Boulangère artisane",          "resume":"Alsace, village rural, budget professionnel artisan.",
     "culture":"Culture alsacienne, marchés de Noël, gastronomie du Rhin",
     "sport":"Vélo sur la Véloroute du Rhin, marche en forêt Noire, natation",
     "travel":"Tourisme alsacien et rhénan, véloroute Rhin-Rhône, Allemagne proche",
     "skills":"Boulangerie-pâtisserie artisanale, gestion TPE, réparation équipements four",
     "hobbies":"Vélo sur voies vertes, cuisine alsacienne, jardinage aromatique",
     "besoins":["pour artisans","Faire ses courses","trajets domicile travail"]},

    {"id":14, "avatar":"🏗️", "prenom":"Antoine Zawada",       "age":35, "commune":"Paris 10e",          "dep":"75",  "urbanite":"urbain",     "budget":8000,
     "profil":"Technicien HLM",               "resume":"Paris dense, Canal St-Martin, 25 km/h suffit.",
     "culture":"Culture polonaise, Paris multiculturel, street art canal St-Martin",
     "sport":"Vélo urbain quotidien Canal St-Martin, natation, foot avec enfants",
     "travel":"Pologne en famille, vélo île-de-France, bord de Seine",
     "skills":"Plomberie, électricité bâtiment, serrurerie, multimédia, bricolage tous corps",
     "hobbies":"Vélo, bricolage et personnalisation objets, sorties famille Paris",
     "besoins":["trajets domicile travail","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants"]},

    {"id":15, "avatar":"🌺",  "prenom":"Louis Proust",         "age":55, "commune":"Saint-Paul (Réunion)","dep":"974","urbanite":"ile",        "budget":15000,
     "profil":"Chargé de mission mairie",     "resume":"Routes sinueuses île, orchidées, Grand Bénare.",
     "culture":"Culture créole réunionnaise, maloya, patrimoine Réunion",
     "sport":"Randonnée Grand Bénare, VTT sur pistes volcaniques, surf côtier",
     "travel":"Tour de la Réunion à vélo, océan Indien, Madagascar",
     "skills":"Gestion de projet, botanique tropicale, connaissance terrain insulaire",
     "hobbies":"Orchidées et botanique, randonnée volcanique, VTT, plongée",
     "besoins":["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]},
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

# ── Actif/Passif : valeur réelle issue du champ Airtable "Véhicule Actif ou Passif" ──
# Actif  = pédalage obligatoire (VAE, certains L6e…)
# Passif = pas de pédalage (quadricycle, 2-roues motorisé…)
ACTIF_PASSIF = {
    "CIRCLE": "Passif",
    "CamiGO": "Actif",
    "Sorean": "Actif",
    "Pelican Train": "Actif",
    "Ouicycle": "Actif",
    "Urbaner VIVALDI": "Actif",
    "Urbaner BOXOO": "Actif",
    "Urbaner PROMENER": "Actif",
    "T-ZER 45": "Passif",
    "T-ZER 90": "Passif",
    "Supercycle": "Actif",
    "CYGUS": "Actif",
    "Maillon Cargo": "Actif",
    "Maillon Daily": "Actif",
    "Nocar": "Actif",
    "VeMoo": "Actif",
    "BOB": "Actif",
    "La bagnole": "Passif",
    "Ulive": "Passif",
    "VUF XXL MAX POLY": "Actif",
    "VUF XXL TAXI": "Actif",
    "DUAL": "Passif",
    "MIDIPILE": "Actif",
    "KOZI": "Actif",
    "KOLI": "Actif",
    "KUBI": "Actif",
    "KARI": "Actif",
    "Weez Lite": "Passif",
    "Arsène": "Passif",
    "Woodybus": "Actif",
    "ACT3.1 VAE": "Actif",
    "ACT3.6 RANDO": "Actif",
    "e-roe 25 Cargo": "Actif",
    "e-roe 25 Passenger": "Actif",
    "e-roe 45 Passenger": "Passif",
    "e-roe 45 Cargo": "Passif",
    "MS TRACKER": "Passif",
    "X-Bikium Utility": "Actif",
    "PelicanTrain": "Actif",
    "moskitOS": "Actif",
    "KIWEE": "Passif",
    "Baker-Prax": "Actif",
    "Cargo Cycles du Midi": "Actif",
    "AEMOTION L5e": "Passif",
    "BigTetu": "Actif",
    "La Fourmi": "Actif",
    "DRAKKAR NoBox L": "Actif",
    "KETCH CLEEN": "Actif",
    "KETCH STAND": "Actif",
    "KETCH DELIVERY": "Actif",
    "KETCH NOBOX": "Actif",
    "CLIPPER FOOD": "Actif",
    "CLIPPER NOBOX": "Actif",
    "DRAKKAR CARGO L": "Actif",
    "DRAKKAR GREEN L": "Actif",
    "DRAKKAR FLAT L": "Actif",
    "DRAKKAR NoBox S": "Actif",
    "DRAKKAR CARGO S": "Actif",
    "DRAKKAR GREEN S": "Actif",
    "DRAKKAR FLAT S": "Actif",
}

def is_actif(v):  return ACTIF_PASSIF.get(v["nom"], "Actif") == "Actif"
def is_passif(v): return ACTIF_PASSIF.get(v["nom"], "Actif") == "Passif"

URBANITE_LABELS = {"urbain":"🏙️ Urbain","periurbain":"🏘️ Périurbain",
                   "rural":"🌾 Rural","montagne":"🏔️ Montagne","ile":"🌊 Île"}

# Mots-clés pour détection d'affinité profil ─────────────────────────────────
KW_VELO    = ["vélo","vtt","cyclisme","bikepacking","véloroute","cycle","biking"]
KW_TRAVEL  = ["tourisme","voyage","découverte","road trip","tour de","balade","randonn"]
KW_BRICO   = ["bricolage","mécanique","réparation","soudure","électricité","plomberie",
              "électronique","maintenance","repair","diy","entretien","moto"]

def _match(text, keywords):
    t = text.lower()
    return any(k in t for k in keywords)

def affinity_score(persona, vehicle):
    """Bonus 0-20 pts basé sur culture/sport/travel/skills/hobbies du persona."""
    sport  = persona.get("sport","")
    travel = persona.get("travel","")
    skills = persona.get("skills","")
    hobbies= persona.get("hobbies","")
    profil_text = f"{sport} {skills} {hobbies}"

    bonus = 0
    flags = []

    # +8 pts : pratique du vélo/VTT → affinité naturelle avec véhicule actif (VAE)
    if _match(sport + " " + hobbies, KW_VELO) and is_actif(vehicle):
        bonus += 8
        flags.append("🚴 Cycliste → VAE adapté")

    # +4 pts : goût du voyage/tourisme → vehicle avec usage Tourisme
    if _match(travel + " " + sport, KW_TRAVEL) and "Tourisme Découverte d'un territoire" in vehicle["usages"]:
        bonus += 4
        flags.append("🗺️ Voyageur → usage Tourisme")

    # +8 pts : bricolage/mécanique → VAE simple à entretenir soi-même
    if _match(profil_text, KW_BRICO) and is_actif(vehicle):
        bonus += 8
        flags.append("🔧 Bricoleur → entretien autonome possible")

    return min(bonus, 20), flags  # plafond à 20 pts

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

    # Affinité profil (0-20 pts bonus — sport vélo, travel, bricolage)
    a, flags = affinity_score(persona, vehicle)

    return {"b":b, "s":s, "u":u, "a":a, "affinity_flags":flags,
            "base":b+s+u, "total":b+s+u+a,
            "covered":covered, "uncovered":uncovered}

def badge_info(total):
    # seuils sur 120 (base 100 + bonus affinité 20)
    if total >= 100: return "🟢 Excellent",  "#dcfce7", "#14532d"
    if total >= 82:  return "🔵 Bon match",  "#dbeafe", "#1e3a8a"
    if total >= 58:  return "🟡 Partiel",    "#fef3c7", "#78350f"
    if total >= 34:  return "🟠 Faible",     "#ffedd5", "#7c2d12"
    return               "🔴 Non adapté",    "#fee2e2", "#7f1d1d"

def bar_color(total):
    if total >= 100: return "#16a34a"
    if total >= 82:  return "#2563eb"
    if total >= 58:  return "#d97706"
    if total >= 34:  return "#ea580c"
    return "#dc2626"

# ─── INIT SESSION STATE ───────────────────────────────────────────────────────
if "reactions" not in st.session_state:
    st.session_state.reactions = {}

# ─── SIDEBAR : sélection persona + chargement CSV Colab ──────────────────────
import pandas as pd

def _score_to_color(val, vmin=20, vmax=85):
    """Retourne une couleur de fond CSS sans matplotlib (rouge→jaune→vert)."""
    try: v = float(val)
    except: return "background-color: #f1f5f9; color: #475569"
    t = max(0.0, min(1.0, (v - vmin) / (vmax - vmin)))
    if t < 0.5:
        r, g = 220, int(220 * t * 2)
        b = 50
    else:
        r, g = int(220 * (1 - t) * 2), 160
        b = 50
    lum = 0.299*r + 0.587*g + 0.114*b
    txt = "#1a1a1a" if lum > 140 else "#f9fafb"
    return f"background-color: rgb({r},{g},{b}); color: {txt}"

def style_pivot(df):
    """Applique _score_to_color cellule par cellule — pas besoin de matplotlib."""
    styled = pd.DataFrame("", index=df.index, columns=df.columns)
    for r in df.index:
        for c in df.columns:
            styled.loc[r, c] = _score_to_color(df.loc[r, c])
    return styled

if "personas_source" not in st.session_state:
    st.session_state.personas_source = "builtin"
if "personas_csv" not in st.session_state:
    st.session_state.personas_csv = []

with st.sidebar:
    st.markdown("## 🚲 Simulateur Vélis")
    st.divider()

    # ── Chargement CSV Colab ──────────────────────────────────────────────────
    with st.expander("📥 Charger des personas depuis Colab", expanded=False):
        st.caption("Uploade le CSV exporté depuis le notebook Colab pour remplacer les 15 personas.")
        uploaded = st.file_uploader("CSV personas (export Colab)", type="csv", key="csv_upload")
        if uploaded is not None:
            try:
                df_up = pd.read_csv(uploaded, encoding="utf-8-sig")
                required_cols = {"prenom","age","commune","urbanite","budget","besoins"}
                if not required_cols.issubset(set(df_up.columns)):
                    st.error(f"Colonnes manquantes : {required_cols - set(df_up.columns)}")
                else:
                    personas_loaded = []
                    for i, row_up in df_up.iterrows():
                        besoins_raw = str(row_up.get("besoins",""))
                        besoins_list = [b.strip() for b in besoins_raw.split("|") if b.strip()]
                        personas_loaded.append({
                            "id":       i + 100,
                            "avatar":   str(row_up.get("avatar","👤")),
                            "prenom":   str(row_up.get("prenom",""))[:40],
                            "age":      int(row_up.get("age", 40)),
                            "commune":  str(row_up.get("commune","")),
                            "dep":      str(row_up.get("departement", row_up.get("dep",""))),
                            "urbanite": str(row_up.get("urbanite","periurbain")),
                            "budget":   int(row_up.get("budget", 9000)),
                            "profil":   str(row_up.get("profil", row_up.get("occupation",""))),
                            "resume":   str(row_up.get("resume",""))[:200],
                            "culture":  str(row_up.get("culture","")),
                            "sport":    str(row_up.get("sport","")),
                            "travel":   str(row_up.get("travel","")),
                            "skills":   str(row_up.get("skills","")),
                            "hobbies":  str(row_up.get("hobbies","")),
                            "besoins":  besoins_list,
                        })
                    st.session_state.personas_csv = personas_loaded
                    st.session_state.personas_source = "csv"
                    st.success(f"✅ {len(personas_loaded)} personas chargés !")
            except Exception as e:
                st.error(f"Erreur lecture CSV : {e}")

        if st.session_state.personas_source == "csv" and st.session_state.personas_csv:
            if st.button("↩️ Revenir aux 15 personas par défaut"):
                st.session_state.personas_source = "builtin"
                st.rerun()

    st.divider()

    # ── Sélection active des personas ─────────────────────────────────────────
    active_personas = (st.session_state.personas_csv
                       if st.session_state.personas_source == "csv" and st.session_state.personas_csv
                       else PERSONAS)

    nb_p = len(active_personas)
    source_label = f"CSV Colab ({nb_p})" if st.session_state.personas_source == "csv" else f"15 personas intégrés"
    st.caption(f"Source : {source_label}")

    persona_labels = [
        f"{p['avatar']}  {p['prenom']}  ·  {p['age']} ans\n{p['commune']}"
        for p in active_personas
    ]
    selected_idx = st.radio(
        "Choisir un persona", range(len(active_personas)),
        format_func=lambda i: persona_labels[i], label_visibility="collapsed"
    )
    persona = active_personas[selected_idx]

# ─── ONGLETS ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔍 Simulateur personas", "📊 Analyse constructeurs × territoires", "🎯 Optimiseur véhicule"])

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — Simulateur personas × véhicules
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
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

        with st.expander("🔍 Profil détaillé — culture, sport, voyages, compétences"):
            dc1, dc2 = st.columns(2)
            with dc1:
                st.markdown(f"**🎭 Culture**  \n{persona.get('culture','—')}")
                st.markdown(f"**🏃 Sport**  \n{persona.get('sport','—')}")
                st.markdown(f"**✈️ Voyages**  \n{persona.get('travel','—')}")
            with dc2:
                st.markdown(f"**🔧 Compétences**  \n{persona.get('skills','—')}")
                st.markdown(f"**🎯 Hobbies**  \n{persona.get('hobbies','—')}")
            has_velo   = _match(persona.get("sport","")+" "+persona.get("hobbies",""), KW_VELO)
            has_travel = _match(persona.get("travel","")+" "+persona.get("sport",""),   KW_TRAVEL)
            has_brico  = _match(persona.get("skills","")+" "+persona.get("hobbies",""), KW_BRICO)
            indi = []
            if has_velo:   indi.append("🚴 Pratique le vélo → **bonus +8 pts** sur les VAE")
            if has_travel: indi.append("🗺️ Aime voyager → **bonus +4 pts** si usage Tourisme")
            if has_brico:  indi.append("🔧 Bricoleur/mécano → **bonus +8 pts** entretien autonome VAE")
            if indi:
                st.divider()
                st.markdown("**Affinités détectées (bonus scoring)**")
                for ind in indi:
                    st.markdown(f"- {ind}")

    budget = st.slider(
        f"💰 Budget d'achat  *(défaut persona : {persona['budget']:,} €)*",
        min_value=1000, max_value=40000, step=500, value=persona["budget"], format="%d €"
    )

    aide_pct = st.slider(
        "🏛️ Aides publiques (subventions, bonus écologique, aides locales…)",
        min_value=0, max_value=20, step=1, value=0, format="%d %%",
        key="aide_pct",
        help="Réduit le prix net de chaque véhicule. Exemple : 10% sur un véhicule à 10 000 € → prix net 9 000 €"
    )
    if aide_pct > 0:
        st.caption(
            f"💡 Avec {aide_pct} % d'aides : un véhicule à **10 000 €** revient à "
            f"**{10000*(1-aide_pct/100):,.0f} €** · à **20 000 €** → "
            f"**{20000*(1-aide_pct/100):,.0f} €**"
        )
    st.divider()

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filtre_vitesse = st.selectbox("🚀 Vitesse maxi", ["Tous","≤ 25 km/h","≤ 45 km/h","≤ 90 km/h"])
    with fc2:
        filtre_mode = st.selectbox("🚴 Motorisation", ["Tous","Actif (avec pédalage)","Passif (sans pédalage)"],
                                   help="Actif = pédalage obligatoire | Passif = sans pédalage")
    with fc3:
        filtre_fin = st.selectbox("💳 Financement", ["Tous","Prix connu (achat)","Location disponible"])

    def apply_filters(v):
        if filtre_vitesse == "≤ 25 km/h"  and v["vitesse"] > 25:  return False
        if filtre_vitesse == "≤ 45 km/h"  and v["vitesse"] > 45:  return False
        if filtre_vitesse == "≤ 90 km/h"  and v["vitesse"] > 90:  return False
        if filtre_mode == "Actif (avec pédalage)"  and not is_actif(v):  return False
        if filtre_mode == "Passif (sans pédalage)" and not is_passif(v): return False
        if filtre_fin  == "Prix connu (achat)"    and v["prix"] is None: return False
        if filtre_fin  == "Location disponible"   and v["loc"]  is None: return False
        return True

    scored = []
    for v in VEHICLES:
        if not apply_filters(v): continue
        prix_net = round(v["prix"] * (1 - aide_pct / 100)) if v["prix"] is not None else None
        sc = compute_score(persona, {**v, "prix": prix_net}, budget)
        scored.append({**v, "prix_net": prix_net, **sc})
    scored.sort(key=lambda x: x["total"], reverse=True)

    nb_excellent = sum(1 for v in scored if v["total"] >= 100)
    nb_bon       = sum(1 for v in scored if 82 <= v["total"] < 100)
    nb_partiel   = sum(1 for v in scored if 58 <= v["total"] < 82)

    with col_stats:
        st.caption("Scores sur les véhicules filtrés")
        m1, m2, m3 = st.columns(3)
        m1.metric("🟢 Excellent (≥100)", nb_excellent)
        m2.metric("🔵 Bon match (≥82)",  nb_bon)
        m3.metric("🟡 Partiel (≥58)",    nb_partiel)

    st.markdown(f"**{len(scored)} véhicules** · score = Budget(30) + Territoire(40) + Usages(30) + Affinité(+20 max) = **/120**")
    st.divider()

    if not scored:
        st.warning("Aucun véhicule ne correspond à ces filtres.")
    else:
        for i, v in enumerate(scored):
            label, bg, txt = badge_info(v["total"])
            color     = bar_color(v["total"])
            prix_str  = f"{v['prix']:,} € HT" if v["prix"] is not None else "sur devis"
            loc_str   = f"· loc. {v['loc']} €/mois" if v["loc"] else ""
            cats_str  = " / ".join(v["cat"])
            ap_val    = ACTIF_PASSIF.get(v["nom"], "?")
            ap_badge  = "🚴 Actif" if ap_val == "Actif" else "🛞 Passif"
            ap_bg     = "#dcfce7" if ap_val == "Actif" else "#e0e7ff"
            ap_txt    = "#15803d" if ap_val == "Actif" else "#3730a3"

            prix_brut = v["prix"]
            prix_net  = v["prix_net"]   # None si sur devis
            economie  = round(prix_brut * aide_pct / 100) if prix_brut and aide_pct > 0 else 0

            prix_ok   = prix_net is not None and prix_net <= budget
            prix_high = prix_net is not None and prix_net > budget

            # Affichage prix : barré si aide > 0
            if prix_brut is None:
                prix_str = "sur devis"
            elif aide_pct > 0:
                prix_str = (
                    f"<span style='text-decoration:line-through;color:#94a3b8;font-size:11px'>"
                    f"{prix_brut:,} €</span> "
                    f"<b>{prix_net:,} € net</b> "
                    f"<span style='color:#16a34a;font-size:11px'>(-{economie:,} €)</span>"
                )
            else:
                prix_str = f"{prix_brut:,} € HT"

            with st.container(border=True):
                c1, c2 = st.columns([1, 7])
                with c1:
                    st.markdown(
                        f"<div style='text-align:center'>"
                        f"<div style='font-size:11px;color:#94a3b8'>#{i+1}</div>"
                        f"<div style='font-size:32px;font-weight:700;color:{color}'>{v['total']}</div>"
                        f"<div style='font-size:9px;color:#94a3b8'>/120</div>"
                        f"<span style='background:{bg};color:{txt};padding:2px 6px;border-radius:4px;font-size:10px;font-weight:600'>{label}</span>"
                        f"</div>", unsafe_allow_html=True)
                with c2:
                    prix_color = "#15803d" if prix_ok else ("#b91c1c" if prix_high else "#854d0e")
                    prix_bg2   = "#dcfce7" if prix_ok else ("#fee2e2" if prix_high else "#fef9c3")
                    prix_html  = (
                        f"<span style='background:{prix_bg2};color:{prix_color};"
                        f"padding:2px 8px;border-radius:4px;font-size:12px'>{prix_str}</span>"
                    )
                    st.markdown(
                        f"**{v['nom']}** &nbsp;<span style='color:#94a3b8;font-size:13px'>{v['fab']}</span> &nbsp;"
                        f"<span class='tag-neu'>{cats_str}</span> &nbsp;"
                        f"<span style='background:{ap_bg};color:{ap_txt};padding:1px 7px;border-radius:4px;font-size:11px;font-weight:600'>{ap_badge}</span> &nbsp;"
                        f"<span class='tag-neu'>{v['vitesse']} km/h</span> &nbsp;"
                        + prix_html
                        + (f" &nbsp;<span style='background:#ede9fe;color:#5b21b6;padding:2px 7px;border-radius:4px;font-size:11px'>{loc_str.strip()}</span>" if loc_str else ""),
                        unsafe_allow_html=True)

                    bc1, bc2, bc3, bc4 = st.columns(4)
                    bc1.progress(v["b"]/30, text=f"💰 Budget : {v['b']}/30")
                    bc2.progress(v["s"]/40, text=f"🗺️ Territoire : {v['s']}/40")
                    bc3.progress(v["u"]/30, text=f"🎯 Usages : {v['u']}/30")
                    bc4.progress(v["a"]/20, text=f"✨ Affinité : +{v['a']}/20")

                    if v["affinity_flags"]:
                        st.markdown(" &nbsp;".join([
                            f"<span style='background:#fdf4ff;color:#7e22ce;padding:2px 8px;border-radius:4px;font-size:11px'>{f}</span>"
                            for f in v["affinity_flags"]]), unsafe_allow_html=True)

                    tags_html = (
                        " ".join([f"<span class='tag-ok'>✓ {b}</span>" for b in v["covered"]]) + " " +
                        " ".join([f"<span class='tag-ko'>✗ {b}</span>" for b in v["uncovered"]]))
                    st.markdown(tags_html, unsafe_allow_html=True)

                    key = f"{persona['id']}-{v['id']}-{budget}-{aide_pct}"
                    if key in st.session_state.reactions:
                        st.markdown(
                            f"<div class='reaction-box'>"
                            f"<div style='font-size:10px;color:#6366f1;font-weight:600;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.05em'>"
                            f"Réaction de {persona['prenom'].split()[0]}</div>"
                            f"{st.session_state.reactions[key]}</div>",
                            unsafe_allow_html=True)
                    else:
                        if st.button(f"✦ Simuler la réaction de {persona['prenom'].split()[0]}", key=f"btn_{key}"):
                            with st.spinner("Génération en cours…"):
                                affinity_ctx = (f"\nAffinités détectées : {', '.join(v['affinity_flags'])}."
                                                if v["affinity_flags"] else "")
                                prix_prompt = (
                                    f"{prix_brut:,} € HT, soit {prix_net:,} € net après {aide_pct} % d'aides publiques ({economie:,} € d'économie)"
                                    if prix_brut and aide_pct > 0
                                    else (f"{prix_brut:,} € HT" if prix_brut else "prix sur devis")
                                )
                                prompt = (
                                    f"Tu es {persona['prenom']}, {persona['age']} ans, {persona['profil']}, "
                                    f"habitant {persona['commune']} ({persona['dep']}). {persona['resume']}\n"
                                    f"Culture : {persona.get('culture','')}. Sport : {persona.get('sport','')}. "
                                    f"Voyages : {persona.get('travel','')}. Compétences : {persona.get('skills','')}. "
                                    f"Hobbies : {persona.get('hobbies','')}.\n"
                                    f"Budget : {budget:,}€. Besoins : {', '.join(persona['besoins'])}. "
                                    f"Territoire : {URBANITE_LABELS[persona['urbanite']]}.{affinity_ctx}\n\n"
                                    f"Tu découvres le \"{v['nom']}\" ({v['fab']}) — {v['vitesse']} km/h, "
                                    f"{ap_val.lower()} ({'avec pédalage' if ap_val=='Actif' else 'sans pédalage'}), "
                                    f"{prix_prompt}{(' · location '+str(v['loc'])+'€/mois') if v['loc'] else ''}.\n\n"
                                    f"En 2-3 phrases à la 1ère personne, réaction sincère. "
                                    f"Intègre ton profil (sport, bricolage, voyages si pertinent). "
                                    f"Concret sur le territoire, le prix net, et l'usage quotidien."
                                )
                                try:
                                    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                                    message = client.messages.create(
                                        model="claude-sonnet-4-20250514", max_tokens=350,
                                        messages=[{"role":"user","content":prompt}])
                                    st.session_state.reactions[key] = message.content[0].text
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erreur API : {e}")

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — Analyse inverse : quels constructeurs pour quels territoires ?
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Quelle opportunité marché pour chaque constructeur ?")
    st.caption(
        "30 archétypes représentatifs (5 territoires × 3 tranches d'âge × 2 profils sportif/standard) "
        "sont scorés sur les 60 véhicules. Les résultats montrent les segments où chaque constructeur a "
        "le plus de chances de convaincre."
    )

    # ── Définition des 30 archétypes ─────────────────────────────────────────
    ARCH_CONFIG = [
        # (urbanite, age_label, age_mid, budget, besoins)
        ("urbain",     "18-35", 26, 6500,  ["trajets domicile travail","Faire ses courses","se rendre sur les sites d'activités sportives"]),
        ("urbain",     "35-55", 44, 10000, ["trajets domicile travail","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants"]),
        ("urbain",     "55+",   63, 9000,  ["Faire ses courses","Tourisme Découverte d'un territoire"]),
        ("periurbain", "18-35", 27, 7500,  ["trajets domicile travail","Faire ses courses","se rendre sur les sites d'activités sportives"]),
        ("periurbain", "35-55", 44, 11000, ["trajets domicile travail","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants"]),
        ("periurbain", "55+",   63, 10000, ["Faire ses courses","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]),
        ("rural",      "18-35", 26, 7000,  ["trajets domicile travail","Faire ses courses","Tourisme Découverte d'un territoire"]),
        ("rural",      "35-55", 44, 10500, ["trajets domicile travail","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants"]),
        ("rural",      "55+",   63, 9500,  ["Faire ses courses","Tourisme Découverte d'un territoire"]),
        ("montagne",   "18-35", 26, 9000,  ["trajets domicile travail","se rendre sur les sites d'activités sportives","Tourisme Découverte d'un territoire"]),
        ("montagne",   "35-55", 44, 12000, ["trajets domicile travail","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants"]),
        ("montagne",   "55+",   63, 11000, ["Faire ses courses","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]),
        ("ile",        "18-35", 26, 10000, ["trajets domicile travail","se rendre sur les sites d'activités sportives","Tourisme Découverte d'un territoire"]),
        ("ile",        "35-55", 44, 14000, ["trajets domicile travail","Faire ses courses","Transport scolaire et périscolaire avec plusieurs enfants"]),
        ("ile",        "55+",   63, 13000, ["Faire ses courses","Tourisme Découverte d'un territoire","se rendre sur les sites d'activités sportives"]),
    ]

    ARCHETYPES = []
    for urbanite, age_label, age_mid, budget_arch, besoins_arch in ARCH_CONFIG:
        for sport_label, sport_txt, hobbies_txt, skills_txt in [
            ("Sportif",  "vélo vtt randonnée cyclisme", "vélo bricolage mécanique", "mécanique bricolage électricité"),
            ("Standard", "", "", ""),
        ]:
            ARCHETYPES.append({
                "segment":  f"{age_label} · {sport_label}",
                "urbanite": urbanite,
                "age":      age_mid,
                "budget":   budget_arch,
                "sport":    sport_txt,
                "hobbies":  hobbies_txt,
                "skills":   skills_txt,
                "travel":   "tourisme voyage découverte" if urbanite in ["ile","montagne","rural"] else "",
                "besoins":  besoins_arch,
            })

    # ── Score de tous les véhicules × tous les archétypes ────────────────────
    rows = []
    for v in VEHICLES:
        for arch in ARCHETYPES:
            sc = compute_score(arch, v, arch["budget"])
            terr_label = URBANITE_LABELS[arch["urbanite"]].split()[1]  # ex. "Urbain"
            rows.append({
                "Véhicule":     v["nom"],
                "Constructeur": v["fab"],
                "Actif/Passif": ACTIF_PASSIF.get(v["nom"], "?"),
                "Territoire":   terr_label,
                "Segment":      arch["segment"],
                "Score base":   sc["base"],   # /100
                "Score total":  sc["total"],  # /120
            })
    df_all = pd.DataFrame(rows)

    # ── VUE 1 : Heatmap constructeurs × territoires ───────────────────────────
    st.divider()
    st.markdown("#### 🗺️ Carte des opportunités — score moyen /100 par territoire")
    st.caption("Score base uniquement (budget 30 + territoire 40 + usages 30), moyenné sur tous les archétypes du territoire.")

    pivot = (df_all.groupby(["Constructeur","Territoire"])["Score base"]
             .mean().round(1).unstack("Territoire"))

    # Réordonner les colonnes territoire
    terr_order = ["Urbain","Périurbain","Rural","Montagne","Île"]
    pivot = pivot.reindex(columns=[c for c in terr_order if c in pivot.columns])

    # Garder constructeurs avec au moins 1 score ≥ 55 (filtrer les très faibles)
    pivot = pivot[pivot.max(axis=1) >= 40].sort_values(
        pivot.columns.tolist(), ascending=False)

    st.dataframe(
        pivot.style
            .apply(style_pivot, axis=None)
            .format("{:.0f}"),
        use_container_width=True, height=min(50 + len(pivot)*35, 600)
    )

    # ── VUE 2 : Top véhicules par territoire ──────────────────────────────────
    st.divider()
    st.markdown("#### 🏆 Top 5 véhicules par territoire")
    st.caption("Moyenne sur tous les archétypes du territoire, score base /100.")

    terr_cols = st.columns(len(terr_order))
    for col_t, terr in zip(terr_cols, terr_order):
        if terr not in df_all["Territoire"].values:
            continue
        top = (df_all[df_all["Territoire"]==terr]
               .groupby(["Véhicule","Constructeur","Actif/Passif"])["Score base"]
               .mean().round(0).reset_index()
               .sort_values("Score base", ascending=False).head(5))
        with col_t:
            st.markdown(f"**{terr}**")
            for _, row_v in top.iterrows():
                ap_icon = "🚴" if row_v["Actif/Passif"]=="Actif" else "🛞"
                score_v = int(row_v["Score base"])
                color_v = "#16a34a" if score_v>=70 else "#2563eb" if score_v>=55 else "#d97706"
                st.markdown(
                    f"<div style='margin:3px 0;padding:5px 8px;background:#f8fafc;border-radius:6px;"
                    f"border-left:3px solid {color_v};font-size:12px'>"
                    f"<b style='color:{color_v}'>{score_v}</b> {ap_icon} {row_v['Véhicule']}"
                    f"<br><span style='color:#94a3b8;font-size:10px'>{row_v['Constructeur']}</span></div>",
                    unsafe_allow_html=True)

    # ── VUE 3 : Analyse par constructeur ─────────────────────────────────────
    st.divider()
    st.markdown("#### 🏭 Analyse détaillée par constructeur")

    constructeurs = sorted(df_all["Constructeur"].unique())
    sel_fab = st.selectbox("Choisir un constructeur", constructeurs, key="sel_fab")

    df_fab = df_all[df_all["Constructeur"] == sel_fab]
    vehicles_fab = df_fab["Véhicule"].unique().tolist()

    fa1, fa2, fa3, fa4 = st.columns(4)
    fa1.metric("Véhicules", len(vehicles_fab))
    fa2.metric("Score moy. global", f"{df_fab['Score base'].mean():.0f}/100")
    fa3.metric("Meilleur territoire",
               df_fab.groupby("Territoire")["Score base"].mean().idxmax())
    fa4.metric("Meilleur segment",
               df_fab.groupby("Segment")["Score base"].mean().idxmax())

    # Scores par territoire × segment (heatmap constructeur)
    pivot_fab = (df_fab.groupby(["Territoire","Segment"])["Score base"]
                 .mean().round(0).astype(int).unstack("Segment"))
    pivot_fab = pivot_fab.reindex([t for t in terr_order if t in pivot_fab.index])

    st.markdown(f"**Scores de {sel_fab} par territoire × segment d'âge/profil**")
    st.dataframe(
        pivot_fab.style
            .apply(style_pivot, axis=None)
            .format("{:.0f}"),
        use_container_width=True
    )

    # Segments porteurs (score ≥ 65)
    best_segs = (df_fab.groupby(["Territoire","Segment"])["Score base"]
                 .mean().round(0).reset_index()
                 .query("`Score base` >= 65")
                 .sort_values("Score base", ascending=False))
    if not best_segs.empty:
        st.markdown(f"**Segments porteurs (score ≥ 65/100) pour {sel_fab} :**")
        seg_parts = []
        for _, rs in best_segs.iterrows():
            seg_parts.append(
                f"<span style='background:#dcfce7;color:#14532d;padding:3px 9px;"
                f"border-radius:4px;font-size:12px;margin:2px;display:inline-block'>"
                f"✓ {rs['Territoire']} · {rs['Segment']} — {int(rs['Score base'])}/100</span>"
            )
        st.markdown(" ".join(seg_parts), unsafe_allow_html=True)
    else:
        st.info(f"Aucun segment avec score ≥ 65 pour {sel_fab}. Ce constructeur est positionné sur des usages très spécifiques (pro/utilitaire).")

    # Tableau des véhicules du constructeur avec meilleurs segments
    st.markdown(f"**Détail des {len(vehicles_fab)} véhicule(s) de {sel_fab}**")
    for vnom in vehicles_fab:
        df_v = df_fab[df_fab["Véhicule"]==vnom]
        best_t = df_v.groupby("Territoire")["Score base"].mean().idxmax()
        best_s = int(df_v.groupby("Territoire")["Score base"].mean().max())
        avg_s  = int(df_v["Score base"].mean())
        ap     = ACTIF_PASSIF.get(vnom, "?")
        ap_icon = "🚴" if ap=="Actif" else "🛞"
        v_data = next((v for v in VEHICLES if v["nom"]==vnom), {})
        prix_s = f"{v_data['prix']:,} €" if v_data.get("prix") else "sur devis"
        color_s = "#16a34a" if avg_s>=70 else "#2563eb" if avg_s>=55 else "#d97706"
        st.markdown(
            f"<div style='padding:8px 12px;margin:4px 0;background:#f8fafc;border-radius:8px;"
            f"border-left:3px solid {color_s}'>"
            f"<b>{ap_icon} {vnom}</b> &nbsp;"
            f"<span style='color:#94a3b8;font-size:12px'>{'/'.join(v_data.get('cat',[]))} · {v_data.get('vitesse','?')} km/h · {prix_s}</span><br>"
            f"<span style='font-size:12px'>Score moyen : <b style='color:{color_s}'>{avg_s}/100</b> · "
            f"Meilleur territoire : <b>{best_t} ({best_s}/100)</b></span></div>",
            unsafe_allow_html=True)

    # ── Meilleurs & pires personas réels ─────────────────────────────────────
    st.divider()
    st.markdown(f"#### 👤 Meilleurs et pires personas pour {sel_fab}")
    st.caption("Score moyen sur tous les véhicules du constructeur, calculé sur les 15 personas intégrés.")

    # Calculer le score moyen de chaque persona sur tous les véhicules du constructeur
    vehicles_du_fab = [v for v in VEHICLES if v["fab"] == sel_fab]
    persona_scores = []
    for p in PERSONAS:
        scores_p = []
        details_p = []
        for v in vehicles_du_fab:
            sc = compute_score(p, v, p["budget"])
            scores_p.append(sc["total"])
            # Collecter les signaux pour expliquer le fit
            details_p.append({
                "vehicule": v["nom"],
                "total": sc["total"],
                "b": sc["b"], "s": sc["s"], "u": sc["u"], "a": sc["a"],
                "covered": sc["covered"], "uncovered": sc["uncovered"],
                "affinity_flags": sc["affinity_flags"],
            })
        avg_total = round(sum(scores_p) / len(scores_p)) if scores_p else 0
        best_v    = max(details_p, key=lambda x: x["total"]) if details_p else {}

        # Construire l'explication du fit
        fit_reasons = []
        # Budget
        budget_scores = [d["b"] for d in details_p]
        avg_b = round(sum(budget_scores)/len(budget_scores)) if budget_scores else 0
        if avg_b >= 22:   fit_reasons.append(f"💰 Budget OK ({p['budget']:,} €)")
        elif avg_b <= 6:  fit_reasons.append(f"💸 Trop cher vs budget {p['budget']:,} €")
        # Territoire
        terr_scores = [d["s"] for d in details_p]
        avg_s2 = round(sum(terr_scores)/len(terr_scores)) if terr_scores else 0
        if avg_s2 >= 35:  fit_reasons.append(f"🗺️ Territoire idéal ({URBANITE_LABELS[p['urbanite']]})")
        elif avg_s2 <= 8: fit_reasons.append(f"🚧 Territoire défavorable ({URBANITE_LABELS[p['urbanite']]})")
        # Usages
        usage_scores = [d["u"] for d in details_p]
        avg_u2 = round(sum(usage_scores)/len(usage_scores)) if usage_scores else 0
        if avg_u2 >= 22:  fit_reasons.append(f"🎯 Usages bien couverts")
        elif avg_u2 <= 8: fit_reasons.append(f"❌ Usages peu couverts")
        # Affinité
        any_affinity = any(d["affinity_flags"] for d in details_p)
        if any_affinity:  fit_reasons.append(f"✨ Affinité sport/bricolage détectée")

        persona_scores.append({
            "persona": p,
            "avg": avg_total,
            "best_v": best_v,
            "fit_reasons": fit_reasons,
            "avg_b": avg_b, "avg_s": avg_s2, "avg_u": avg_u2,
        })

    persona_scores.sort(key=lambda x: x["avg"], reverse=True)
    top5  = persona_scores[:5]
    flop5 = persona_scores[-5:][::-1]  # du pire au moins pire

    def render_persona_fit(items, is_top):
        for rank, item in enumerate(items, 1):
            p      = item["persona"]
            avg    = item["avg"]
            bv     = item["best_v"]
            color  = "#16a34a" if avg >= 82 else "#2563eb" if avg >= 58 else "#d97706" if avg >= 34 else "#dc2626"
            bg     = "#f0fdf4" if avg >= 82 else "#eff6ff" if avg >= 58 else "#fffbeb" if avg >= 34 else "#fef2f2"
            medal  = ["🥇","🥈","🥉","4️⃣","5️⃣"][rank-1] if is_top else ["💀","😞","😕","😐","🤔"][rank-1]
            best_vnom = bv.get("vehicule","—")
            best_vscore = bv.get("total", 0)

            reasons_html = " ".join([
                f"<span style='background:#f1f5f9;color:#334155;padding:2px 7px;"
                f"border-radius:4px;font-size:11px'>{r}</span>"
                for r in item["fit_reasons"]
            ])

            st.markdown(
                f"<div style='padding:10px 14px;margin:5px 0;background:{bg};"
                f"border-radius:10px;border-left:4px solid {color}'>"
                f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>"
                f"<span style='font-size:20px'>{medal}</span>"
                f"<span style='font-size:22px'>{p['avatar']}</span>"
                f"<div>"
                f"<b style='color:{color};font-size:15px'>{p['prenom']}</b> &nbsp;"
                f"<span style='color:#64748b;font-size:12px'>{p['age']} ans · {p['profil']} · "
                f"{URBANITE_LABELS[p['urbanite']].split()[1]}</span>"
                f"</div>"
                f"<span style='margin-left:auto;font-size:22px;font-weight:700;color:{color}'>"
                f"{avg}<span style='font-size:11px;color:#94a3b8'>/120</span></span>"
                f"</div>"
                f"<div style='font-size:11px;color:#64748b;margin-bottom:5px'>"
                f"Meilleur véhicule : <b>{best_vnom}</b> ({best_vscore}/120)"
                f"</div>"
                f"{reasons_html}"
                f"</div>",
                unsafe_allow_html=True)

    col_top, col_flop = st.columns(2)
    with col_top:
        st.markdown("**🏆 Top 5 — meilleurs fits**")
        render_persona_fit(top5, is_top=True)
    with col_flop:
        st.markdown("**⚠️ Flop 5 — moins bons fits**")
        render_persona_fit(flop5, is_top=False)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — Optimiseur véhicule intermédiaire (reverse engineering EMP 2019)
# ══════════════════════════════════════════════════════════════════════════════

# ── Données et fonctions de l'optimiseur (scope global pour tab3) ────────────
# Valeurs par défaut (EMP 2019 + CGDD/INSEE) — remplacées si JSON Nemotron uploadé
_CUMUL_AUTO_DEFAULT={
    "periurbain_solo":    {10:0.544,20:0.702,30:0.781,40:0.825,50:0.854,60:0.883,80:0.928,100:0.943,120:0.960,150:0.969},
    "periurbain_famille": {10:0.346,20:0.538,30:0.635,40:0.750,50:0.788,60:0.808,80:0.885,100:0.904,120:0.962,150:1.000},
    "rural_navetteur":    {10:0.210,20:0.347,30:0.492,40:0.596,50:0.679,60:0.762,80:0.850,100:0.896,120:0.943,150:0.959},
    "rural_famille":      {10:0.286,20:0.449,30:0.469,40:0.551,50:0.673,60:0.776,80:0.837,100:0.898,120:0.918,150:0.939},
    "rural_longue_dist":  {10:0.184,20:0.305,30:0.418,40:0.539,50:0.631,60:0.667,80:0.794,100:0.844,120:0.872,150:0.894},
}

# ── Accessibilité budget PAR PROFIL (CGDD/INSEE 2022, calibré sur CSP dominants) ──
_AFFORD_PROFILES_DEFAULT={
    "periurbain_solo":    {2000:0.95,3000:0.87,4000:0.76,5000:0.64,6000:0.53,7000:0.42,8000:0.33,9000:0.25,10000:0.19,12000:0.12,15000:0.06,18000:0.03,99999:0.0},   # inactifs + employés
    "periurbain_famille": {2000:0.96,3000:0.90,4000:0.82,5000:0.72,6000:0.62,7000:0.52,8000:0.43,9000:0.35,10000:0.28,12000:0.18,15000:0.09,18000:0.04,99999:0.0},   # employés + ouvriers
    "rural_navetteur":    {2000:0.96,3000:0.89,4000:0.81,5000:0.70,6000:0.59,7000:0.49,8000:0.40,9000:0.32,10000:0.25,12000:0.15,15000:0.07,18000:0.03,99999:0.0},   # ouvriers dominant
    "rural_famille":      {2000:0.96,3000:0.89,4000:0.80,5000:0.69,6000:0.58,7000:0.48,8000:0.39,9000:0.31,10000:0.24,12000:0.14,15000:0.07,18000:0.03,99999:0.0},   # ouvriers + employés
    "rural_longue_dist":  {2000:0.97,3000:0.93,4000:0.87,5000:0.79,6000:0.70,7000:0.61,8000:0.53,9000:0.45,10000:0.37,12000:0.25,15000:0.13,18000:0.07,99999:0.0},   # intermédiaires + agriculteurs
}
# Les distributions actives (remplacées dynamiquement par l'upload Nemotron)
CUMUL_AUTO = _CUMUL_AUTO_DEFAULT.copy()
AFFORD_PROFILES = _AFFORD_PROFILES_DEFAULT.copy()
# Courbe globale utilisée dans les tableaux de synthèse (moyenne pondérée)
AFFORD_GLOBAL={2000:0.97,3000:0.92,4000:0.86,5000:0.78,6000:0.68,7000:0.58,8000:0.49,9000:0.41,10000:0.34,11000:0.27,12000:0.22,13000:0.17,14000:0.13,15000:0.10,18000:0.06,22000:0.03,99999:0.00}

PROFILES=[
    {"id":"periurbain_solo",    "nom":"Périurbain · solo",    "icon":"🚶",  "desc":"Personne seule, grande couronne, trajets courts domicile-travail",          "pct":0.15,"vit_min":45,"places":1,"auto_p75":23, "co2_jour":1800},
    {"id":"periurbain_famille", "nom":"Périurbain · famille", "icon":"👨‍👩‍👧","desc":"Famille avec enfants, grande couronne, école + courses + travail",           "pct":0.25,"vit_min":45,"places":3,"auto_p75":39, "co2_jour":3200},
    {"id":"rural_navetteur",    "nom":"Rural · navetteur",    "icon":"🌾",  "desc":"Ouvrier/employé rural, routes nationales et départementales, trajets longs", "pct":0.28,"vit_min":90,"places":2,"auto_p75":59, "co2_jour":5000},
    {"id":"rural_famille",      "nom":"Rural · famille",      "icon":"🏡",  "desc":"Famille rurale, enfants, combinaison trajets travail + école",               "pct":0.20,"vit_min":90,"places":3,"auto_p75":57, "co2_jour":5400},
    {"id":"rural_longue_dist",  "nom":"Rural · longue dist.", "icon":"🛣️", "desc":"Zone isolée, trajets > 40 km aller, forte dépendance automobile",            "pct":0.12,"vit_min":90,"places":1,"auto_p75":80, "co2_jour":4800},
]

N_CIBLE=1_950_000; N_DATASET=6_000_000
BASE_CHASSIS={25:2600,45:3500,90:5200,110:6400,999:8000}
BATT=40; SEATS={1:0,2:650,3:1500,4:2700}; MARGIN=1.30
SPEED_KEYS=[25,45,90,110,999]; AUTO_KEYS=[10,20,30,40,50,60,80,100,120]; SEATS_KEYS=[1,2,3,4]
SPEED_LABELS={25:"VAE/L1e  ≤25 km/h",45:"L6e  ≤45 km/h",90:"L7e  ≤90 km/h",110:"L8e hyp.  ≤110 km/h",999:"M1  sans limite"}
SEATS_LABELS={1:"1 adulte",2:"2 adultes",3:"1 adulte + 2 enfants",4:"4 adultes"}

def interp(d,v):
    keys=sorted(d.keys())
    if v<=keys[0]: return d[keys[0]]
    if v>=keys[-1]: return d[keys[-1]]
    for i in range(len(keys)-1):
        k0,k1=keys[i],keys[i+1]
        if k0<=v<=k1: return d[k0]+(v-k0)/(k1-k0)*(d[k1]-d[k0])
    return 0.0

def prix_brut(auto,vit,pl):
    return round((BASE_CHASSIS[vit]+BATT*auto+SEATS[pl])*MARGIN/100)*100

def reach(auto,vit,pl,prix_net):
    """
    Personas atteints = Σ profil × N_cible × P(autonomie couverte) × P(vitesse ok)
                         × P(places ok) × P(peut financer)
    Chaque probabilité est issue de distributions réelles EMP 2019 / CGDD 2022.
    """
    total=0; details=[]
    for p in PROFILES:
        p_auto=interp(CUMUL_AUTO[p["id"]],auto)
        p_vit=1.0 if vit>=p["vit_min"] else 0.0
        p_pl=1.0 if pl>=p["places"] else 0.0
        # ✅ FIX : chaque profil a sa propre courbe d'accessibilité budgétaire
        p_afford=interp(AFFORD_PROFILES[p["id"]],prix_net)
        contrib=p["pct"]*N_CIBLE*p_auto*p_vit*p_pl*p_afford
        total+=contrib
        fails=[]
        if p_vit==0: fails.append(f"vitesse {vit} km/h < {p['vit_min']} requis")
        if p_pl==0:  fails.append(f"{pl} place(s) < {p['places']} requises")
        details.append({"profil":p["nom"],"icon":p["icon"],"desc":p["desc"],"pct_pop":p["pct"],
                        "auto_p75":p["auto_p75"],"ok":p_vit>0 and p_pl>0,
                        "p_auto":p_auto,"p_afford":p_afford,
                        "contrib_n":round(contrib),"contrib_pct":contrib/N_CIBLE*100,"fails":fails})
    return round(total),details

def optimize(aide):
    best=None
    for vit in SPEED_KEYS:
        for pl in SEATS_KEYS:
            for auto in AUTO_KEYS:
                pb=prix_brut(auto,vit,pl); pn=round(pb*(1-aide/100))
                r,_=reach(auto,vit,pl,pn); eff=r/max(pn,1)
                if best is None or eff>best["eff"]:
                    best={"auto":auto,"vit":vit,"pl":pl,"pb":pb,"pn":pn,"r":r,"eff":eff}
    return best

with tab3:
    # ── Sidebar onglet 3 ─────────────────────────────────────────────────────
    with st.sidebar:
        st.divider()
        st.markdown("### 🎯 Optimiseur")
        st.markdown("**🏛️ Aides publiques**")
        st.caption("S'applique à tous les véhicules. Recalcul en temps réel.")
        aide3 = st.slider("Niveau d'aide", min_value=0, max_value=20, step=1, value=0,
                          format="%d %%", key="aide_optimiseur",
                          help="Réduit le prix net. Chaque % débloque de nouveaux segments ruraux.")
        st.markdown(
            f"5 k€ → **{round(5000*(1-aide3/100)):,} €** · "
            f"8 k€ → **{round(8000*(1-aide3/100)):,} €** · "
            f"12 k€ → **{round(12000*(1-aide3/100)):,} €**"
        )
        st.divider()
        st.markdown("**📥 Distributions Nemotron (optionnel)**")
        st.caption("Remplace les estimations EMP/CGDD par les vraies distributions Nemotron. Généré par `personas_mobilite_500k.ipynb`.")
        uploaded_json = st.file_uploader("distributions_nemotron.json", type=["json"], key="nemotron_json",
                                         help="Fichier JSON généré à l'étape 9d du notebook Colab")
        if uploaded_json is not None:
            try:
                import json as _json
                data = _json.load(uploaded_json)
                required_profiles = {"periurbain_solo","periurbain_famille","rural_navetteur","rural_famille","rural_longue_dist"}
                if "CUMUL_AUTO" in data and "AFFORD_PROFILES" in data:
                    CUMUL_AUTO.update({pid:{int(k):v for k,v in d.items()} for pid,d in data["CUMUL_AUTO"].items() if pid in required_profiles})
                    AFFORD_PROFILES.update({pid:{int(k):v for k,v in d.items()} for pid,d in data["AFFORD_PROFILES"].items() if pid in required_profiles})
                    st.success(f"✅ Nemotron chargé · {data.get('n_cible_nemotron',N_CIBLE):,} personas")
                else:
                    st.error("❌ Clés manquantes : CUMUL_AUTO + AFFORD_PROFILES")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
        else:
            st.info("Estimations EMP 2019 / CGDD actives", icon="ℹ️")

    aide = aide3  # alias

    # ── Titre et explication ──────────────────────────────────────────────────
    st.markdown("## 🎯 Optimiseur — 5 types de véhicules pour couvrir tous les territoires")

    with st.expander("📖 Comment ce modèle fonctionne — cliquez pour comprendre", expanded=False):
        st.markdown("""
### Ce que fait ce modèle

Au lieu de chercher UN véhicule universel, ce modèle **optimise 5 types de véhicules distincts** en parallèle,
chacun ciblant des cas d'usage différents. Pour chaque type, autonomie et nombre de places sont optimisés
pour maximiser le rapport personas atteints ÷ prix net.

### Les 5 types de véhicules

| Type | Catégorie | Vitesse | Pédalage | Profils cibles |
|---|---|---|---|---|
| 🚴 VAE cargo | VAE/L1e | ≤ 25 km/h | Actif | Cyclistes urbains, courses courtes |
| 🚲 L6e Actif | L6e | ≤ 45 km/h | Actif | Périurbain, axes secondaires |
| 🚗 L6e Passif | L6e | ≤ 45 km/h | Passif | Périurbain, seniors, sans permis |
| 🚙 L7e Passif | L7e | ≤ 90 km/h | Passif | Rural, routes nationales |
| 🛣️ L8e (hyp.) | L8e | ≤ 110 km/h | Passif | Rural isolé, voies rapides |

### Calcul du coût public des aides

Le curseur d'aides permet de simuler le coût budgétaire total selon :
- Le % d'aide appliqué (→ montant € par véhicule)
- Un taux de pénétration du marché (% de la population cible qui achète)
- Le cumul sur tous les véhicules aidés

### ⚠️ Source des données

**Distributions mobilité** : micro-données EMP 2019 (SDES/INSEE) — réelles.  
**Courbes budgétaires** : calibration CGDD/INSEE 2022 par CSP — estimées.  
**Populations** : estimations sur Nemotron 6M. Uploader `distributions_nemotron.json` pour les vraies valeurs.
""")

    st.caption(
        f"Population cible estimée : **{N_CIBLE:,} personas** · faibles revenus Q1+Q2 · rural + périurbain · "
        f"Aide active : **{aide} %**"
    )
    st.divider()

    # ── Définition des 5 types de véhicules ─────────────────────────────────────
    VEHICLE_TYPES_T3 = [
        {"id":"vae_cargo",  "label":"VAE cargo",  "icon":"🚴", "vit":25,  "actif":True,  "cat":"VAE/L1e",          "color":"#16a34a",
         "desc":"Vélo cargo électrique — courses, école, livraison en ville et périurbain proche",
         "vit_label":"≤ 25 km/h","usage":"Trajets courts, pratique sportive, alternatives à la voiture en zone dense"},
        {"id":"l6e_actif",  "label":"L6e Actif",  "icon":"🚲", "vit":45,  "actif":True,  "cat":"L6e actif",        "color":"#2563eb",
         "desc":"Tricycle/quadricycle léger avec pédalage — axes secondaires périurbains",
         "vit_label":"≤ 45 km/h","usage":"Navette domicile-travail, courses, transport scolaire périurbain"},
        {"id":"l6e_passif", "label":"L6e Passif", "icon":"🚗", "vit":45,  "actif":False, "cat":"L6e passif",       "color":"#7c3aed",
         "desc":"Voiturette sans permis — accessibilité seniors, pas de permis requis",
         "vit_label":"≤ 45 km/h","usage":"Autonomie mobilité seniors, zones périurbaines, pas d'effort physique"},
        {"id":"l7e_passif", "label":"L7e Passif", "icon":"🚙", "vit":90,  "actif":False, "cat":"L7e passif",       "color":"#d97706",
         "desc":"Quadricycle lourd — routes nationales et départementales, usage rural complet",
         "vit_label":"≤ 90 km/h","usage":"Remplacement voiture en rural, longues distances, famille"},
        {"id":"l8e_hyp",    "label":"L8e (hyp.)", "icon":"🛣️","vit":110, "actif":False, "cat":"L8e hypothétique", "color":"#dc2626",
         "desc":"Nouvelle catégorie hypothétique — voies rapides, zones très isolées",
         "vit_label":"≤ 110 km/h","usage":"Zones rurales isolées, voies rapides, remplacement complet voiture thermique"},
    ]

    # Profil "cycliste" spécifique au VAE (vit_min=25)
    PROFILES_T3 = [
        {"id":"periurbain_cycliste","nom":"Périurbain · cycliste","icon":"🚴","desc":"Déjà cycliste ou prêt à adopter VAE, trajets ≤15 km","pct":0.08,"vit_min":25,"places":1,"auto_p75":15,"co2_jour":800},
        {"id":"periurbain_solo",    "nom":"Périurbain · solo",    "icon":"🚶","desc":"Personne seule, grande couronne, trajets courts",        "pct":0.12,"vit_min":45,"places":1,"auto_p75":23,"co2_jour":1800},
        {"id":"periurbain_famille", "nom":"Périurbain · famille", "icon":"👨‍👩‍👧","desc":"Famille avec enfants, grande couronne, école+courses",   "pct":0.25,"vit_min":45,"places":3,"auto_p75":39,"co2_jour":3200},
        {"id":"rural_navetteur",    "nom":"Rural · navetteur",    "icon":"🌾","desc":"Ouvrier/employé rural, routes nationales, trajets longs","pct":0.28,"vit_min":90,"places":2,"auto_p75":59,"co2_jour":5000},
        {"id":"rural_famille",      "nom":"Rural · famille",      "icon":"🏡","desc":"Famille rurale, enfants, combinaison travail+école",     "pct":0.20,"vit_min":90,"places":3,"auto_p75":57,"co2_jour":5400},
        {"id":"rural_longue_dist",  "nom":"Rural · longue dist.", "icon":"🛣️","desc":"Zone isolée, trajets > 40 km aller",                   "pct":0.07,"vit_min":90,"places":1,"auto_p75":80,"co2_jour":4800},
    ]
    # Distribution autonomie pour le profil cycliste (similaire périurbain_solo)
    CUMUL_AUTO_CYCLISTE = {10:0.60,20:0.78,30:0.88,40:0.93,50:0.96,60:0.97,80:0.98,100:0.99,120:1.0,150:1.0}
    AFFORD_CYCLISTE     = {2000:0.96,3000:0.91,4000:0.84,5000:0.74,6000:0.62,7000:0.49,8000:0.37,9000:0.27,10000:0.20,12000:0.11,15000:0.05,18000:0.02,99999:0.0}

    def cumul_auto_t3(pid, km):
        # Priorité : JSON Nemotron uploadé > hardcoded (pour le profil cycliste aussi)
        if pid in CUMUL_AUTO:
            return interp(CUMUL_AUTO[pid], km)
        if pid == "periurbain_cycliste":
            return interp(CUMUL_AUTO_CYCLISTE, km)
        return interp(CUMUL_AUTO.get(pid, CUMUL_AUTO["periurbain_solo"]), km)

    def afford_t3(pid, prix_net):
        if pid in AFFORD_PROFILES:
            return interp(AFFORD_PROFILES[pid], prix_net)
        if pid == "periurbain_cycliste":
            return interp(AFFORD_CYCLISTE, prix_net)
        return interp(AFFORD_PROFILES.get(pid, AFFORD_PROFILES["periurbain_solo"]), prix_net)

    def reach_t3(auto, vit, pl, prix_net):
        total = 0; details = []
        for p in PROFILES_T3:
            p_auto   = cumul_auto_t3(p["id"], auto)
            p_vit    = 1.0 if vit >= p["vit_min"] else 0.0
            p_pl     = 1.0 if pl  >= p["places"]  else 0.0
            p_afford = afford_t3(p["id"], prix_net)
            contrib  = p["pct"] * N_CIBLE * p_auto * p_vit * p_pl * p_afford
            total   += contrib
            fails = []
            if p_vit == 0: fails.append(f"{vit} km/h < {p['vit_min']} requis")
            if p_pl  == 0: fails.append(f"{pl} pl < {p['places']} requises")
            details.append({
                "profil":p["nom"],"icon":p["icon"],"desc":p["desc"],"pct_pop":p["pct"],
                "ok":p_vit>0 and p_pl>0,"p_auto":p_auto,"p_afford":p_afford,
                "contrib_n":round(contrib),"contrib_pct":contrib/N_CIBLE*100,"fails":fails
            })
        return round(total), details

    def optimize_type(vit, aide_pct):
        best = None
        for pl in [1,2,3,4]:
            for auto in [10,20,30,40,50,60,80,100,120]:
                pb2 = prix_brut(auto, vit, pl)
                pn2 = round(pb2 * (1 - aide_pct/100))
                r, _ = reach_t3(auto, vit, pl, pn2)
                eff = r / max(pn2, 1)
                if best is None or eff > best["eff"]:
                    best = {"auto":auto,"pl":pl,"pb":pb2,"pn":pn2,"r":r,"eff":eff}
        return best

    # Calcul des 5 optimums
    results_t3 = []
    for vt in VEHICLE_TYPES_T3:
        opt_vt  = optimize_type(vt["vit"], aide)
        opt_vt0 = optimize_type(vt["vit"], 0)
        r0_vt, _ = reach_t3(opt_vt0["auto"], vt["vit"], opt_vt0["pl"], opt_vt0["pn"])
        r_vt, dets_vt = reach_t3(opt_vt["auto"], vt["vit"], opt_vt["pl"], opt_vt["pn"])
        results_t3.append({**vt, "opt":opt_vt, "r":r_vt, "r0":r0_vt, "dets":dets_vt,
                           "gain":r_vt-r0_vt, "pct":r_vt/N_CIBLE*100})

    # ── VUE SYNTHÉTIQUE : les 5 véhicules en une ligne ────────────────────────
    st.markdown("### 🚗 Les 5 types de véhicules — comparaison à la loupe")
    st.caption(f"Pour chaque type, autonomie et places sont optimisés librement. Aide active : {aide} %.")

    cols5 = st.columns(5)
    for col, res in zip(cols5, results_t3):
        o = res["opt"]
        auto_spec = round(o["auto"] * 1.20)
        gain_html = (f"<div style='font-size:11px;color:#16a34a'>▲+{res['gain']:,} vs 0%</div>"
                     if res["gain"] > 0 else "")
        ap_badge  = ("🚴 Actif" if res["actif"] else "🛞 Passif")
        ap_bg     = "#f0fdf4" if res["actif"] else "#ede9fe"
        ap_txt    = "#14532d" if res["actif"] else "#4c1d95"
        col.markdown(
            f"<div style='background:white;border:2px solid {res['color']};border-radius:12px;"
            f"padding:12px 10px;text-align:center;height:100%'>"
            f"<div style='font-size:28px'>{res['icon']}</div>"
            f"<div style='font-size:13px;font-weight:700;color:{res['color']};margin:4px 0'>{res['label']}</div>"
            f"<div style='font-size:10px;color:#64748b;margin-bottom:6px'>{res['cat']} · {res['vit_label']}</div>"
            f"<div style='background:{ap_bg};color:{ap_txt};border-radius:8px;padding:2px 0;font-size:10px;font-weight:600;margin-bottom:6px'>{ap_badge}</div>"
            f"<div style='font-size:11px;color:#64748b;margin-bottom:4px'>🔋 {o['auto']} km réels<br><span style='color:#94a3b8'>spec. {auto_spec} km (+20%)</span></div>"
            f"<div style='font-size:11px;color:#64748b;margin-bottom:4px'>💺 {SEATS_LABELS[o['pl']]}</div>"
            f"<div style='font-size:12px;font-weight:700;color:#0f172a;margin-bottom:2px'>{o['pn']:,} € net</div>"
            f"<div style='font-size:10px;color:#94a3b8'>brut {o['pb']:,} €</div>"
            f"<div style='font-size:15px;font-weight:800;color:{res['color']};margin-top:6px'>{res['r']:,}</div>"
            f"<div style='font-size:10px;color:#64748b'>{res['pct']:.1f} % cibles</div>"
            f"{gain_html}"
            f"</div>",
            unsafe_allow_html=True)

    # ── BARRE CUMULATIVE ──────────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("### 📊 Couverture cumulée — qui est adressé par chaque type ?")
    st.caption(
        "Chaque profil peut être couvert par plusieurs types de véhicules. "
        "La barre montre la fraction de la population cible adressée par chaque type, "
        "empilées par profil. Les zones de recouvrement sont normales : un persona a le choix.")

    # Pour chaque profil, quel(s) véhicule(s) le couvrent et à quel score ?
    for prof in PROFILES_T3:
        pid   = prof["id"]
        p_pct = prof["pct"]
        p_n   = round(p_pct * N_CIBLE)
        contribs = []
        for res in results_t3:
            o = res["opt"]
            vit_ok = o["opt"]["vit"] if False else res["vit"]  # always use res["vit"]
            p_vit  = 1.0 if vit_ok >= prof["vit_min"] else 0.0
            p_pl   = 1.0 if o["pl"] >= prof["places"] else 0.0
            if p_vit > 0 and p_pl > 0:
                p_auto   = cumul_auto_t3(pid, o["auto"])
                p_afford = afford_t3(pid, o["pn"])
                score    = p_auto * p_afford * 100
                contribs.append((res["label"], res["color"], round(score, 1)))

        # Build stacked bar
        bar_parts = "".join(
            f"<div style='flex:{score};background:{color};height:100%;min-width:2px' title='{label}: {score:.0f}%'></div>"
            for label, color, score in contribs
        ) if contribs else "<div style='flex:1;background:#e2e8f0;height:100%'></div>"

        best_v = max(contribs, key=lambda x:x[2])[0] if contribs else "—"
        covered = len(contribs)

        st.markdown(
            f"<div style='display:flex;align-items:center;gap:10px;margin:5px 0'>"
            f"<span style='font-size:18px'>{prof['icon']}</span>"
            f"<div style='width:160px;font-size:12px;line-height:1.2'><b>{prof['nom']}</b><br>"
            f"<span style='color:#94a3b8;font-size:10px'>{p_n:,} personas · {p_pct*100:.0f}%</span></div>"
            f"<div style='flex:1;height:20px;background:#f1f5f9;border-radius:4px;overflow:hidden;display:flex'>"
            f"{bar_parts}</div>"
            f"<span style='font-size:11px;color:#64748b;width:100px;text-align:right'>{covered} type(s) · top: {best_v}</span>"
            f"</div>",
            unsafe_allow_html=True)

    # Légende couleurs
    legend = " &nbsp;".join(
        f"<span style='background:{res['color']};color:white;padding:2px 8px;border-radius:4px;font-size:11px'>{res['icon']} {res['label']}</span>"
        for res in results_t3)
    st.markdown(legend, unsafe_allow_html=True)

    st.divider()

    # ── DÉTAIL PAR VÉHICULE ───────────────────────────────────────────────────
    st.markdown("### 🔍 Détail — profils servis par chaque type de véhicule")
    st.caption("Cliquez sur un onglet pour voir quels profils sont couverts et à quel niveau.")

    tabs_vt = st.tabs([f"{res['icon']} {res['label']}" for res in results_t3])
    for tab_vt, res in zip(tabs_vt, results_t3):
        with tab_vt:
            o = res["opt"]
            auto_spec = round(o["auto"]*1.20)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Autonomie minimale", f"{o['auto']} km", f"spec. {auto_spec} km (+20%)")
            c2.metric("Prix net", f"{o['pn']:,} €", f"brut {o['pb']:,} €")
            c3.metric("Personas atteints", f"{res['r']:,}", f"{res['pct']:.1f}% cibles")
            c4.metric("Gain vs 0% aides", f"+{res['gain']:,}" if res['gain']>0 else "—")

            st.caption(f"_{res['desc']}_ · {res['usage']}")

            for d in res["dets"]:
                if d["ok"]:
                    w_auto  = d["p_auto"] * 100
                    w_af    = d["p_afford"] * 100
                    c_a     = "#16a34a" if w_auto>=70 else "#2563eb" if w_auto>=40 else "#d97706"
                    c_f     = "#16a34a" if w_af>=50   else "#2563eb" if w_af>=25   else "#d97706"
                    st.markdown(
                        f"<div style='background:#f8fafc;border-left:3px solid {res['color']};"
                        f"border-radius:6px;padding:8px 12px;margin:4px 0'>"
                        f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>"
                        f"<span style='font-size:18px'>{d['icon']}</span>"
                        f"<b>{d['profil']}</b> &nbsp;"
                        f"<span style='font-size:11px;color:#64748b'>{d['desc']} · {d['pct_pop']*100:.0f}%</span>"
                        f"<span style='margin-left:auto;font-size:12px;font-weight:700;color:{res['color']}'>"
                        f"+{d['contrib_n']:,} personas ({d['contrib_pct']:.1f}%)</span></div>"
                        f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:6px'>"
                        f"<div><div style='font-size:10px;color:#64748b'>🔋 Autonomie couverte (P75={d['auto_p75']} km)</div>"
                        f"<div style='background:#e2e8f0;border-radius:3px;height:10px;overflow:hidden'>"
                        f"<div style='width:{w_auto:.0f}%;background:{c_a};height:100%'></div></div>"
                        f"<span style='font-size:10px;color:{c_a}'>{w_auto:.0f}% couverts</span></div>"
                        f"<div><div style='font-size:10px;color:#64748b'>💰 Accessibilité budget</div>"
                        f"<div style='background:#e2e8f0;border-radius:3px;height:10px;overflow:hidden'>"
                        f"<div style='width:{w_af:.0f}%;background:{c_f};height:100%'></div></div>"
                        f"<span style='font-size:10px;color:{c_f}'>{w_af:.0f}% peuvent financer {o['pn']:,}€</span></div>"
                        f"</div></div>",
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<div style='background:#fef2f2;border-left:3px solid #fca5a5;border-radius:6px;"
                        f"padding:6px 12px;margin:3px 0;font-size:12px;color:#b91c1c'>"
                        f"{d['icon']} <b>{d['profil']}</b> — ❌ {' · '.join(d['fails'])}</div>",
                        unsafe_allow_html=True)

    st.divider()

    # ── COÛT PUBLIC DES AIDES ─────────────────────────────────────────────────
    st.markdown("### 💶 Coût public des aides — simulation budgétaire")
    st.markdown("""
> **Comment lire ce tableau ?**  
> Pour chaque type de véhicule, le coût public total = montant de l'aide par véhicule × nombre de véhicules vendus.  
> Le **taux de pénétration** (curseur ci-dessous) représente la fraction de la population cible atteinte  
> qui passe réellement à l'achat. 1 % est conservateur (adoption précoce), 5 % est ambitieux (marché mature).  
> Le **total multi-véhicules** est la somme sur les 5 types — une même personne peut en théorie n'acheter qu'un seul véhicule.
""")

    taux_penetration = st.slider(
        "Taux de pénétration du marché (%)",
        min_value=1, max_value=10, value=2, step=1, format="%d %%",
        key="taux_penet",
        help="% de la population cible atteinte qui achète effectivement le véhicule."
    )

    if aide > 0:
        st.markdown(f"**À {aide} % d'aides — taux de pénétration {taux_penetration} % :**")
        rows_cost = []
        total_veh_all = 0; total_cout_all = 0; total_co2_all = 0
        for res in results_t3:
            o         = res["opt"]
            aide_euro = o["pb"] - o["pn"]          # montant aide par véhicule
            nb_veh    = round(res["r"] * taux_penetration / 100)
            cout_m    = nb_veh * aide_euro / 1e6   # M€
            # CO₂ économisé : personas × co2 moyen journalier × 250j/an
            co2_jour_moy = sum(p["co2_jour"]*p["pct"] for p in PROFILES_T3
                               if any(d["profil"]==p["nom"] and d["ok"] for d in res["dets"]))
            co2_kt    = res["r"] * taux_penetration/100 * co2_jour_moy * 250 / 1e9  # ktCO₂/an
            total_veh_all  += nb_veh
            total_cout_all += nb_veh * aide_euro
            total_co2_all  += res["r"] * taux_penetration/100 * co2_jour_moy * 250

            rows_cost.append({
                "Type":             f"{res['icon']} {res['label']}",
                "Catégorie":        res["cat"],
                "Prix brut":        f"{o['pb']:,} €",
                "Aide/véhicule":    f"{aide_euro:,} €",
                "Pop. cible":       f"{res['r']:,}",
                "Nb véhicules":     f"{nb_veh:,}",
                "Coût public":      f"{cout_m:.1f} M€",
                "CO₂ économisé/an": f"{co2_kt:.2f} ktCO₂",
            })

        st.dataframe(pd.DataFrame(rows_cost).set_index("Type"), use_container_width=True)

        # Totaux
        total_cout_m = total_cout_all / 1e6
        total_co2_kt = total_co2_all / 1e9
        cout_co2 = total_cout_all / max(total_co2_all/1000, 1)  # €/tCO₂

        t1, t2, t3m, t4 = st.columns(4)
        t1.metric("💶 Coût public total", f"{total_cout_m:.0f} M€", f"{total_veh_all:,} véhicules")
        t2.metric("🌍 CO₂ économisé/an", f"{total_co2_kt:.1f} ktCO₂", "vs voiture thermique EMP 2019")
        t3m.metric("📊 Coût/tCO₂ évité", f"{cout_co2:,.0f} €/tCO₂", "efficacité climatique")
        t4.metric("🚗 Véhicules aidés", f"{total_veh_all:,}", f"sur {sum(r['r'] for r in results_t3):,} personas cibles")

        st.caption(
            f"Hypothèses : aide {aide} % · taux de pénétration {taux_penetration} % · "
            f"250 jours d'utilisation/an · CO₂ actuel estimé EMP 2019 · "
            f"Les totaux multi-véhicules peuvent sur-compter si un persona achète plusieurs types.")
    else:
        st.info("💡 Montez le curseur d'aide (sidebar) à au moins 1 % pour calculer le coût public.", icon="ℹ️")

    st.divider()

    # ── TABLEAU RÉCAPITULATIF ──────────────────────────────────────────────────
    st.markdown("### 📋 Récapitulatif — cahiers des charges par type de véhicule")
    for res in results_t3:
        o = res["opt"]
        auto_spec = round(o["auto"]*1.20)
        n_ok = sum(1 for d in res["dets"] if d["ok"])
        st.markdown(
            f"<div style='background:white;border:1px solid #e2e8f0;border-left:5px solid {res['color']};"
            f"border-radius:10px;padding:12px 16px;margin:6px 0;display:flex;align-items:center;gap:16px'>"
            f"<span style='font-size:32px'>{res['icon']}</span>"
            f"<div style='flex:1'>"
            f"<b style='color:{res['color']}'>{res['label']}</b> &nbsp;"
            f"<span style='font-size:11px;color:#94a3b8'>{res['cat']} · {'Actif (pédalage)' if res['actif'] else 'Passif (moteur seul)'}</span><br>"
            f"<span style='font-size:12px;color:#475569'>{res['desc']}</span>"
            f"</div>"
            f"<div style='text-align:center;padding:0 12px;border-left:1px solid #e2e8f0'>"
            f"<div style='font-size:10px;color:#94a3b8'>Autonomie min.</div>"
            f"<div style='font-size:16px;font-weight:700'>{o['auto']} km</div>"
            f"<div style='font-size:10px;color:#94a3b8'>spec. {auto_spec} km</div>"
            f"</div>"
            f"<div style='text-align:center;padding:0 12px;border-left:1px solid #e2e8f0'>"
            f"<div style='font-size:10px;color:#94a3b8'>Places</div>"
            f"<div style='font-size:14px;font-weight:700'>{SEATS_LABELS[o['pl']]}</div>"
            f"</div>"
            f"<div style='text-align:center;padding:0 12px;border-left:1px solid #e2e8f0'>"
            f"<div style='font-size:10px;color:#94a3b8'>Prix net cible</div>"
            f"<div style='font-size:16px;font-weight:700;color:{res['color']}'>{o['pn']:,} €</div>"
            f"<div style='font-size:10px;color:#94a3b8'>brut {o['pb']:,} €</div>"
            f"</div>"
            f"<div style='text-align:center;padding:0 12px;border-left:1px solid #e2e8f0'>"
            f"<div style='font-size:10px;color:#94a3b8'>Personas</div>"
            f"<div style='font-size:16px;font-weight:700;color:{res['color']}'>{res['r']:,}</div>"
            f"<div style='font-size:10px;color:#94a3b8'>{res['pct']:.1f}% · {n_ok}/6 profils</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True)
