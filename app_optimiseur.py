import streamlit as st
import json
import pandas as pd

st.set_page_config(
    page_title="Optimiseur Véhicule Intermédiaire",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .metric-card { background:white;border:1px solid #e2e8f0;border-radius:10px;padding:14px 18px;text-align:center }
    .spec-card   { background:#f8fafc;border-left:4px solid #2563eb;border-radius:6px;padding:10px 14px;margin:5px 0;font-size:13px }
    .prof-ok  { background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:10px 14px;margin:5px 0 }
    .prof-ko  { background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:10px 14px;margin:5px 0 }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DONNÉES — 5 profils archétypaux (faibles revenus, rural + périurbain)
# ═══════════════════════════════════════════════════════════════════════════════
# afford[prix] = P(ce profil peut financer le prix) — décroissant avec le prix
PROFILES = [
    {"name":"Périurbain · solo",    "pct":0.15, "icon":"🚶",
     "desc":"Personne seule, banlieue éloignée, trajets courts à moyens",
     "auto_min":20, "speed_min":45, "seats_min":1,
     "afford":{2000:0.95,4000:0.82,5000:0.73,7000:0.56,9000:0.40,12000:0.24,16000:0.10,99999:0.0}},
    {"name":"Périurbain · famille", "pct":0.25, "icon":"👨‍👩‍👧",
     "desc":"Famille avec enfants, grande couronne, école + courses",
     "auto_min":30, "speed_min":45, "seats_min":3,
     "afford":{2000:0.90,4000:0.76,6000:0.62,8000:0.48,10000:0.35,14000:0.18,20000:0.07,99999:0.0}},
    {"name":"Rural · navetteur",    "pct":0.28, "icon":"🌾",
     "desc":"Employé/ouvrier, village, routes nationales, 2 adultes",
     "auto_min":50, "speed_min":90, "seats_min":2,
     "afford":{2000:0.93,4000:0.79,6000:0.64,8000:0.48,10000:0.34,13000:0.18,18000:0.07,99999:0.0}},
    {"name":"Rural · famille",      "pct":0.20, "icon":"🏡",
     "desc":"Famille rurale, enfants, longues distances, budget contraint",
     "auto_min":50, "speed_min":90, "seats_min":3,
     "afford":{3000:0.90,5000:0.74,7000:0.58,9000:0.43,12000:0.26,16000:0.12,22000:0.04,99999:0.0}},
    {"name":"Rural · longue dist.", "pct":0.12, "icon":"🛣️",
     "desc":"Zone isolée, trajets > 40 km aller, forte contrainte de vitesse",
     "auto_min":80, "speed_min":90, "seats_min":1,
     "afford":{2000:0.94,4000:0.80,6000:0.64,8000:0.48,10000:0.32,13000:0.16,18000:0.06,99999:0.0}},
]

VEHICLES_VELIS = [
    {"nom":"moskitOS",            "fab":"moskitOS",           "cat":"VAE",   "vitesse":100,"prix":1200, "places":1,"autonomie":30},
    {"nom":"La Fourmi",           "fab":"AirNAM",             "cat":"VAE",   "vitesse":25, "prix":3625, "places":1,"autonomie":50},
    {"nom":"Cargo Cycles du Midi","fab":"Cycles du Midi",     "cat":"VAE",   "vitesse":25, "prix":4200, "places":1,"autonomie":50},
    {"nom":"Urbaner PROMENER",    "fab":"HPR SOLUTIONS",      "cat":"VAE",   "vitesse":25, "prix":5400, "places":2,"autonomie":50},
    {"nom":"T-ZER 45",            "fab":"MOBILOW",            "cat":"L2e",   "vitesse":45, "prix":8000, "places":1,"autonomie":80},
    {"nom":"e-roe 45 Passenger",  "fab":"E-ROE",              "cat":"L6eBP", "vitesse":45, "prix":9800, "places":3,"autonomie":80},
    {"nom":"Sorean",              "fab":"QBX",                "cat":"L6eBP", "vitesse":45, "prix":11990,"places":2,"autonomie":80},
    {"nom":"ACT3.6 RANDO",        "fab":"Acticycle",          "cat":"L6eBP", "vitesse":45, "prix":12000,"places":2,"autonomie":80},
    {"nom":"T-ZER 90",            "fab":"MOBILOW",            "cat":"L5e",   "vitesse":90, "prix":12500,"places":1,"autonomie":100},
    {"nom":"La bagnole",          "fab":"KILOW",              "cat":"L7e",   "vitesse":80, "prix":13000,"places":4,"autonomie":120},
    {"nom":"MS TRACKER",          "fab":"MOBISLOW",           "cat":"L7e",   "vitesse":80, "prix":13000,"places":2,"autonomie":120},
    {"nom":"Arsène",              "fab":"Arsène",             "cat":"L7eC",  "vitesse":80, "prix":13300,"places":2,"autonomie":130},
    {"nom":"Weez Lite",           "fab":"Eon Motors",         "cat":"L7e",   "vitesse":90, "prix":14200,"places":2,"autonomie":150},
    {"nom":"Ulive",               "fab":"Avatar Mobilité",    "cat":"L7e",   "vitesse":90, "prix":15000,"places":2,"autonomie":140},
    {"nom":"DUAL",                "fab":"AEMOTION",           "cat":"L5e",   "vitesse":115,"prix":19000,"places":1,"autonomie":120},
]

BASE_CHASSIS = {25:2800, 45:3800, 90:5500, 110:6500, 999:8000}
SEATS_EXTRA  = {1:0, 2:700, 3:1600, 4:2800}
MARGIN       = 1.28
SPEED_KEYS   = [25, 45, 90, 110, 999]
AUTO_KEYS    = [20, 30, 40, 50, 60, 80, 100]
SEATS_KEYS   = [1, 2, 3, 4]
SPEED_LABELS = {25:"VAE/L1e (≤25 km/h)", 45:"L6e (≤45 km/h)",
                90:"L7e (≤90 km/h)", 110:"L8e hyp. (≤110 km/h)", 999:"M1 (sans limite)"}
SEATS_LABELS = {1:"1 adulte", 2:"2 adultes", 3:"1 adulte + 2 enfants", 4:"4 adultes"}
N_CIBLE   = 1_950_000
N_DATASET = 6_000_000

# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def interp(d, v):
    keys = sorted(d.keys())
    if v <= keys[0]:  return d[keys[0]]
    if v >= keys[-1]: return d[keys[-1]]
    for i in range(len(keys)-1):
        k0, k1 = keys[i], keys[i+1]
        if k0 <= v <= k1:
            t = (v-k0)/(k1-k0)
            return d[k0] + t*(d[k1]-d[k0])
    return 0.0

def estimate_price(auto, vit, pl):
    return round((BASE_CHASSIS[vit] + 42*auto + SEATS_EXTRA[pl]) * MARGIN / 100) * 100

def reach(auto, vit, pl, pn):
    total = 0
    details = []
    for p in PROFILES:
        ok = auto>=p["auto_min"] and vit>=p["speed_min"] and pl>=p["seats_min"]
        if ok:
            pa = interp(p["afford"], pn)
            contrib = p["pct"] * N_CIBLE * pa
            total += contrib
            fails = []
        else:
            pa, contrib = 0.0, 0.0
            fails = []
            if auto < p["auto_min"]:  fails.append(f"autonomie {auto}<{p['auto_min']} km")
            if vit  < p["speed_min"]: fails.append(f"vitesse {vit}<{p['speed_min']} km/h")
            if pl   < p["seats_min"]: fails.append(f"{pl} place(s) < {p['seats_min']} requises")
        details.append({"profil":p["name"],"icon":p["icon"],"desc":p["desc"],
                        "pct_pop":p["pct"],"ok":ok,"pa":pa,
                        "contrib_n":round(contrib),"contrib_pct":contrib/N_CIBLE*100,"fails":fails})
    return round(total), details

def optimize(aide):
    best = None
    for vit in SPEED_KEYS:
        for pl in SEATS_KEYS:
            for auto in AUTO_KEYS:
                pb = estimate_price(auto, vit, pl)
                pn = round(pb*(1-aide/100))
                r, _ = reach(auto, vit, pl, pn)
                eff = r / max(pn, 1)
                if best is None or eff > best["eff"]:
                    best = {"auto":auto,"vit":vit,"pl":pl,"pb":pb,"pn":pn,"r":r,"eff":eff}
    return best

def velis_proximity(o_auto, o_vit, o_pl, o_pn):
    res = []
    for v in VEHICLES_VELIS:
        s_a = 100 if v["autonomie"]>=o_auto else v["autonomie"]/o_auto*60
        s_v = (100-max(0,(v["vitesse"]-o_vit)/20) if v["vitesse"]>=o_vit
               else v["vitesse"]/o_vit*40)
        s_p = 100 if v["places"]>=o_pl else v["places"]/o_pl*50
        diff_p = abs(v["prix"]-o_pn)/max(o_pn,1)
        s_p2 = max(0, 100-diff_p*60)
        prox = round((s_a+s_v+s_p+s_p2)/4)
        res.append({**v, "prox":prox,
                    "ok_a":v["autonomie"]>=o_auto,
                    "ok_v":v["vitesse"]>=o_vit,
                    "ok_p":v["places"]>=o_pl})
    return sorted(res, key=lambda x: x["prox"], reverse=True)[:8]

# ═══════════════════════════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("## 🎯 Optimiseur de véhicule intermédiaire")
st.markdown(
    "**Reverse engineering** : quel est le véhicule électrique à concevoir "
    "pour toucher le maximum de personas à faibles revenus en milieu rural et périurbain, à coût minimal ?"
)
st.caption(
    f"Base : **{N_CIBLE:,} personas cibles** ({N_CIBLE/N_DATASET*100:.0f} % du dataset Nemotron 6M) — "
    f"5 profils archétypaux · Tout le reste est calculé automatiquement."
)
st.divider()

# ── CURSEUR UNIQUE ────────────────────────────────────────────────────────────
col_sl, col_hint = st.columns([3, 1])
with col_sl:
    aide_pct = st.slider(
        "🏛️  Aides publiques — bonus écologique · subventions territoriales · aides ADEME…",
        min_value=0, max_value=20, step=1, value=0, format="%d %%",
        help="Chaque point de % réduit le prix net et déverrouille de nouveaux profils."
    )
with col_hint:
    if aide_pct > 0:
        st.markdown(
            f"<div style='background:#eff6ff;border-radius:8px;padding:10px 14px;"
            f"margin-top:6px;font-size:12px'>"
            f"<b>Exemples de réduction</b><br>"
            f"6 000 € → <b>{round(6000*(1-aide_pct/100)):,} €</b><br>"
            f"10 000 € → <b>{round(10000*(1-aide_pct/100)):,} €</b><br>"
            f"14 000 € → <b>{round(14000*(1-aide_pct/100)):,} €</b>"
            f"</div>", unsafe_allow_html=True)

# ── CALCUL ────────────────────────────────────────────────────────────────────
opt   = optimize(aide_pct)
r_tot, dets = reach(opt["auto"], opt["vit"], opt["pl"], opt["pn"])
opt0  = optimize(0)
r0, _ = reach(opt0["auto"], opt0["vit"], opt0["pl"], opt0["pn"])
gain  = r_tot - r0
color_r = "#16a34a" if r_tot/N_CIBLE>=0.30 else "#2563eb" if r_tot/N_CIBLE>=0.18 else "#d97706"

# ── SPÉCIFICATIONS OPTIMALES ──────────────────────────────────────────────────
st.markdown("### 🏆 Spécifications optimales calculées")

cols = st.columns(5)
items = [
    ("Autonomie",         f"{opt['auto']} km",                                    "batterie LFP dimensionnée au besoin médian"),
    ("Catégorie vitesse", SPEED_LABELS[opt["vit"]].split("(")[0].strip(),         SPEED_LABELS[opt["vit"]]),
    ("Configuration",     SEATS_LABELS[opt["pl"]],                                "configuration familiale couverte"),
    ("Prix net cible",    f"{opt['pn']:,} €",                                     f"brut {opt['pb']:,} € — aide {aide_pct} %"),
    ("Personas atteints", f"{r_tot:,}",                                           f"{r_tot/N_CIBLE*100:.1f} % des cibles"),
]
for col, (title, value, sub) in zip(cols, items):
    fs = "18px" if len(value) > 10 else "26px"
    col.markdown(
        f"<div class='metric-card'>"
        f"<div style='font-size:10px;color:#94a3b8;margin-bottom:4px'>{title}</div>"
        f"<div style='font-size:{fs};font-weight:700;color:#0f172a;line-height:1.2'>{value}</div>"
        f"<div style='font-size:10px;color:#64748b;margin-top:4px'>{sub}</div>"
        f"</div>", unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# Barre de reach globale
bar_w = min(r_tot/N_CIBLE*100*3, 100)
gain_span = (f"&nbsp;<span style='font-size:12px;background:#dcfce7;color:#14532d;"
             f"padding:1px 10px;border-radius:12px'>+{gain:,} personas vs 0 % aides</span>"
             if gain > 0 else "")
st.markdown(
    f"<div style='background:#f1f5f9;border-radius:8px;overflow:hidden;height:36px'>"
    f"<div style='width:{bar_w:.1f}%;background:{color_r};height:100%;display:flex;"
    f"align-items:center;padding:0 16px;font-size:13px;font-weight:700;color:white;white-space:nowrap'>"
    f"{r_tot:,} personas · {r_tot/N_CIBLE*100:.1f} % de la population cible"
    f"{gain_span}</div></div>", unsafe_allow_html=True)

# ── PROFILS SERVIS ────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 👥 Détail par profil archétypal")

for d in dets:
    if d["ok"]:
        w = d["pa"] * 100
        c = "#16a34a" if w >= 50 else "#2563eb" if w >= 30 else "#d97706"
        st.markdown(
            f"<div class='prof-ok'>"
            f"<div style='display:flex;align-items:center;gap:10px;margin-bottom:6px'>"
            f"<span style='font-size:22px'>{d['icon']}</span>"
            f"<div><b>{d['profil']}</b> &nbsp;"
            f"<span style='color:#64748b;font-size:11px'>{d['desc']} · {d['pct_pop']*100:.0f} % de la cible</span></div>"
            f"<span style='margin-left:auto;font-weight:700;color:{c};white-space:nowrap'>"
            f"+{d['contrib_n']:,} personas ({d['contrib_pct']:.1f} %)</span></div>"
            f"<div style='background:#d1fae5;border-radius:4px;height:12px;overflow:hidden;margin-bottom:3px'>"
            f"<div style='width:{w:.0f}%;background:{c};height:100%'></div></div>"
            f"<div style='font-size:11px;color:#64748b'>"
            f"{w:.0f} % de ce profil peuvent financer {opt['pn']:,} € net</div>"
            f"</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div class='prof-ko'>"
            f"<span style='font-size:20px'>{d['icon']}</span> &nbsp;"
            f"<b>{d['profil']}</b> &nbsp;"
            f"<span style='color:#64748b;font-size:11px'>{d['desc']}</span><br>"
            f"<span style='color:#b91c1c;font-size:11px'>❌ {' · '.join(d['fails'])}</span>"
            f"</div>", unsafe_allow_html=True)

# ── TABLEAU DE DÉVERROUILLAGE ─────────────────────────────────────────────────
st.divider()
st.markdown("### 🔓 Profils déverrouillés à chaque niveau d'aide")
st.caption("L'optimum change de catégorie quand les aides permettent d'atteindre un seuil de prix critique.")

prev_ok = set()
unlock_rows = []
for ap in range(0, 21, 5):
    o2 = optimize(ap)
    r2, dts2 = reach(o2["auto"], o2["vit"], o2["pl"], o2["pn"])
    curr_ok = {d["profil"] for d in dts2 if d["ok"] and d["pa"] >= 0.20}
    nouveaux = curr_ok - prev_ok
    prev_ok = curr_ok.copy()
    unlock_rows.append({
        "Aide": f"{ap} %",
        "Optimum calculé": (f"{o2['auto']} km · "
                            f"{SPEED_LABELS[o2['vit']].split('(')[0].strip()} · "
                            f"{SEATS_LABELS[o2['pl']]}"),
        "Prix net": f"{o2['pn']:,} €",
        "Personas atteints": f"{r2:,}",
        "% cibles": f"{r2/N_CIBLE*100:.1f} %",
        "Nouveaux profils": (", ".join(nouveaux) if nouveaux else "—"),
    })

st.dataframe(pd.DataFrame(unlock_rows).set_index("Aide"), use_container_width=True)

# ── SENSIBILITÉ ───────────────────────────────────────────────────────────────
st.divider()
st.markdown(f"### 📊 Sensibilité — impact de chaque dimension (aide fixée à {aide_pct} %)")

tab_a, tab_v, tab_p = st.tabs(["🔋 Autonomie", "🚀 Vitesse", "💺 Places"])

for tab, vary, vals, fixed in [
    (tab_a, "auto",  AUTO_KEYS,  {"vit":opt["vit"],"pl":opt["pl"]}),
    (tab_v, "vit",   SPEED_KEYS, {"auto":opt["auto"],"pl":opt["pl"]}),
    (tab_p, "pl",    SEATS_KEYS, {"auto":opt["auto"],"vit":opt["vit"]}),
]:
    with tab:
        rows = []
        for val in vals:
            a = val if vary=="auto" else fixed["auto"]
            v = val if vary=="vit"  else fixed["vit"]
            p = val if vary=="pl"   else fixed["pl"]
            pb = estimate_price(a,v,p)
            pn = round(pb*(1-aide_pct/100))
            r2, dts2 = reach(a,v,p,pn)
            ok_n = sum(1 for d in dts2 if d["ok"])
            label = (f"{val} km"                           if vary=="auto"
                     else SPEED_LABELS.get(val,"?").split("(")[0].strip() if vary=="vit"
                     else SEATS_LABELS[val])
            rows.append({
                ("Autonomie" if vary=="auto" else "Catégorie" if vary=="vit" else "Configuration"): label,
                "Prix brut": f"{pb:,} €",
                "Prix net":  f"{pn:,} €",
                "Profils couverts": f"{ok_n}/5",
                "Personas atteints": f"{r2:,}",
                "% cibles": f"{r2/N_CIBLE*100:.1f} %",
                "Efficacité": f"{r2/max(pn,1):.2f}",
            })
        key = list(rows[0].keys())[0]
        st.dataframe(pd.DataFrame(rows).set_index(key), use_container_width=True)

# ── VÉHICULES VÉLIS PROCHES ───────────────────────────────────────────────────
st.divider()
st.markdown("### 🚲 Véhicules Vélis les plus proches du cahier des charges")
st.caption(
    f"Spec optimal : {opt['auto']} km · {SPEED_LABELS[opt['vit']]} · "
    f"{SEATS_LABELS[opt['pl']]} · prix net cible {opt['pn']:,} €"
)

matches = velis_proximity(opt["auto"], opt["vit"], opt["pl"], opt["pn"])
gap = all(m["prox"] < 65 for m in matches)

for m in matches:
    prox = m["prox"]
    c  = "#16a34a" if prox>=75 else "#2563eb" if prox>=60 else "#d97706" if prox>=45 else "#94a3b8"
    bg = "#f0fdf4" if prox>=75 else "#eff6ff" if prox>=60 else "#fffbeb" if prox>=45 else "#f8fafc"
    pn_v = round(m["prix"]*(1-aide_pct/100))
    prix_txt = f"{pn_v:,} € net (brut {m['prix']:,} €)"
    chks = (f"{'✅' if m['ok_a'] else '⚠️'} {m['autonomie']} km &nbsp;&nbsp;"
            f"{'✅' if m['ok_v'] else '⚠️'} {m['vitesse']} km/h &nbsp;&nbsp;"
            f"{'✅' if m['ok_p'] else '⚠️'} {m['places']} place(s)")
    st.markdown(
        f"<div style='background:{bg};border-left:4px solid {c};border-radius:10px;"
        f"padding:12px 16px;margin:5px 0'>"
        f"<div style='display:flex;align-items:center;gap:10px'>"
        f"<span style='font-size:24px;font-weight:800;color:{c}'>{prox}</span>"
        f"<span style='font-size:10px;color:{c};font-weight:600'>/100</span>"
        f"<div><b>{m['nom']}</b> &nbsp;"
        f"<span style='color:#94a3b8;font-size:12px'>{m['fab']} · {m['cat']}</span></div>"
        f"<span style='margin-left:auto;font-size:13px;font-weight:700;color:{c}'>{prix_txt}</span>"
        f"</div>"
        f"<div style='font-size:12px;color:#475569;margin-top:5px'>{chks}</div>"
        f"</div>", unsafe_allow_html=True)

if gap:
    st.markdown(
        "<div style='margin-top:14px;padding:14px 18px;background:#fef3c7;border-radius:10px;"
        "border-left:4px solid #f59e0b'>"
        "<b>⚡ Opportunité de marché non adressée</b><br>"
        "<span style='font-size:13px;color:#78350f'>"
        "Aucun véhicule Vélis actuel ne dépasse 65/100 de proximité avec ce cahier des charges. "
        "Ce segment reste sous-équipé. Un constructeur qui conçoit un véhicule aux specs "
        "ci-dessus à ce prix accèderait à un marché de plusieurs centaines de milliers de foyers."
        "</span></div>", unsafe_allow_html=True)

# ── SYNTHÈSE ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 📋 Cahier des charges synthétique")
batt_min = round(opt["auto"]*0.15, 1)
batt_max = round(opt["auto"]*0.22, 1)
st.markdown(
    f"<div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:20px 24px'>"
    f"<div class='spec-card'>🔋 <b>Autonomie :</b> {opt['auto']} km · "
    f"Batterie estimée {batt_min}-{batt_max} kWh (LFP 2025) · "
    f"Couvre {sum(1 for d in dets if d['ok'])}/5 profils</div>"
    f"<div class='spec-card'>🚀 <b>Homologation :</b> {SPEED_LABELS[opt['vit']]} · "
    + ("Accès routes nationales/départementales indispensable en zone rurale."
       if opt["vit"] >= 90 else "Adapté aux axes périurbains et routes secondaires.")
    + "</div>"
    f"<div class='spec-card'>💺 <b>Habitabilité :</b> {SEATS_LABELS[opt['pl']]} · "
    f"Couvre {sum(p['pct'] for p in PROFILES if p['seats_min']<=opt['pl'])*100:.0f} % des besoins familiaux cibles</div>"
    f"<div class='spec-card'>💰 <b>Prix cible :</b> {opt['pb']:,} € HT brut → "
    f"<b>{opt['pn']:,} € net</b> après {aide_pct} % d'aides</div>"
    f"<div class='spec-card'>👥 <b>Potentiel :</b> <b style='color:{color_r}'>{r_tot:,} personas</b> "
    f"({r_tot/N_CIBLE*100:.1f} % des cibles)"
    + (f" · +{gain:,} grâce aux aides" if gain > 0 else "")
    + "</div></div>", unsafe_allow_html=True)
