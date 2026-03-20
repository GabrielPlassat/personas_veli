"""
Optimiseur de véhicule intermédiaire — données mobilité EMP 2019 réelles
"""
import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Optimiseur véhicule intermédiaire",page_icon="🎯",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>.block-container{padding-top:2rem;padding-bottom:2rem}.card{background:white;border:1px solid #e2e8f0;border-radius:12px;padding:16px 20px}.lcard{background:#f8fafc;border-left:4px solid #2563eb;border-radius:6px;padding:10px 14px;margin:5px 0;font-size:13px}.ok{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:10px 14px;margin:4px 0}.ko{background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:10px 14px;margin:4px 0}</style>""",unsafe_allow_html=True)

CUMUL_AUTO={
    "periurbain_solo":    {10:0.544,20:0.702,30:0.781,40:0.825,50:0.854,60:0.883,80:0.928,100:0.943,120:0.960,150:0.969},
    "periurbain_famille": {10:0.346,20:0.538,30:0.635,40:0.750,50:0.788,60:0.808,80:0.885,100:0.904,120:0.962,150:1.000},
    "rural_navetteur":    {10:0.210,20:0.347,30:0.492,40:0.596,50:0.679,60:0.762,80:0.850,100:0.896,120:0.943,150:0.959},
    "rural_famille":      {10:0.286,20:0.449,30:0.469,40:0.551,50:0.673,60:0.776,80:0.837,100:0.898,120:0.918,150:0.939},
    "rural_longue_dist":  {10:0.184,20:0.305,30:0.418,40:0.539,50:0.631,60:0.667,80:0.794,100:0.844,120:0.872,150:0.894},
}

PROFILES=[
    {"id":"periurbain_solo",    "nom":"Périurbain · solo",    "icon":"🚶",  "desc":"Personne seule, grande couronne, trajets courts domicile-travail",         "pct":0.15,"vit_min":45,"places":1,"km_med":10,"auto_p50":9, "auto_p75":23, "auto_p90":69, "co2_jour":1800},
    {"id":"periurbain_famille", "nom":"Périurbain · famille", "icon":"👨‍👩‍👧","desc":"Famille avec enfants, grande couronne, école + courses + travail",          "pct":0.25,"vit_min":45,"places":3,"km_med":21,"auto_p50":17,"auto_p75":39, "auto_p90":86, "co2_jour":3200},
    {"id":"rural_navetteur",    "nom":"Rural · navetteur",    "icon":"🌾",  "desc":"Ouvrier/employé rural, routes nationales et départementales, trajets longs","pct":0.28,"vit_min":90,"places":2,"km_med":33,"auto_p50":32,"auto_p75":59, "auto_p90":101,"co2_jour":5000},
    {"id":"rural_famille",      "nom":"Rural · famille",      "icon":"🏡",  "desc":"Famille rurale, enfants, combinaison trajets travail + école",              "pct":0.20,"vit_min":90,"places":3,"km_med":40,"auto_p50":34,"auto_p75":57, "auto_p90":97, "co2_jour":5400},
    {"id":"rural_longue_dist",  "nom":"Rural · longue dist.", "icon":"🛣️", "desc":"Zone isolée, trajets > 40 km aller, forte dépendance automobile",           "pct":0.12,"vit_min":90,"places":1,"km_med":40,"auto_p50":34,"auto_p75":80, "auto_p90":153,"co2_jour":4800},
]

N_CIBLE=1_950_000; N_DATASET=6_000_000

AFFORD={2000:0.97,3000:0.92,4000:0.86,5000:0.78,6000:0.68,7000:0.58,8000:0.49,9000:0.41,10000:0.34,11000:0.27,12000:0.22,13000:0.17,14000:0.13,15000:0.10,18000:0.06,22000:0.03,99999:0.00}

BASE_CHASSIS={25:2600,45:3500,90:5200,110:6400,999:8000}
BATT_COST_KM=40; SEATS_COST={1:0,2:650,3:1500,4:2700}; MARGIN=1.30
SPEED_KEYS=[25,45,90,110,999]; AUTO_KEYS=[10,20,30,40,50,60,80,100,120]; SEATS_KEYS=[1,2,3,4]
SPEED_LABELS={25:"VAE/L1e  ≤25 km/h",45:"L6e  ≤45 km/h",90:"L7e  ≤90 km/h",110:"L8e hyp.  ≤110 km/h",999:"M1  sans limite"}
SEATS_LABELS={1:"1 adulte",2:"2 adultes",3:"1 adulte+2 enfants",4:"4 adultes"}

def interp(d,v):
    keys=sorted(d.keys())
    if v<=keys[0]: return d[keys[0]]
    if v>=keys[-1]: return d[keys[-1]]
    for i in range(len(keys)-1):
        k0,k1=keys[i],keys[i+1]
        if k0<=v<=k1:
            t=(v-k0)/(k1-k0); return d[k0]+t*(d[k1]-d[k0])
    return 0.0

def prix_brut(auto,vit,pl):
    return round((BASE_CHASSIS[vit]+BATT_COST_KM*auto+SEATS_COST[pl])*MARGIN/100)*100

def reach(auto,vit,pl,prix_net):
    total=0; details=[]
    for p in PROFILES:
        p_auto=interp(CUMUL_AUTO[p["id"]],auto)
        p_vit=1.0 if vit>=p["vit_min"] else 0.0
        p_pl=1.0 if pl>=p["places"] else 0.0
        p_afford=interp(AFFORD,prix_net)
        contrib=p["pct"]*N_CIBLE*p_auto*p_vit*p_pl*p_afford
        total+=contrib
        fails=[]
        if p_vit==0: fails.append(f"vitesse {vit} km/h < {p['vit_min']} requis")
        if p_pl==0:  fails.append(f"{pl} place(s) < {p['places']} requises")
        details.append({"profil":p["nom"],"icon":p["icon"],"desc":p["desc"],"pct_pop":p["pct"],
                        "auto_p75":p["auto_p75"],"ok":p_vit>0 and p_pl>0,
                        "p_auto":p_auto,"p_vit":p_vit,"p_pl":p_pl,"p_afford":p_afford,
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

st.markdown("## 🎯 Optimiseur — Véhicule intermédiaire pour les territoires ruraux")
st.markdown("Quel est le véhicule électrique à concevoir pour toucher le **maximum de personas à faibles revenus en milieu rural et périurbain**, à coût minimal ?\n\nLes besoins de mobilité proviennent des **micro-données EMP 2019** (SDES/INSEE) — 45 000 déplacements individuels réels. Le reste est calculé automatiquement.")
st.caption(f"Population cible : **{N_CIBLE:,} personas** ({N_CIBLE/N_DATASET*100:.0f} % du dataset Nemotron 6M) · faibles revenus Q1+Q2 · rural + périurbain · France métropolitaine")
st.divider()

col_sl,col_expl=st.columns([3,1])
with col_sl:
    aide=st.slider("🏛️  Aides publiques — bonus écologique · subventions locales · aides ADEME…",min_value=0,max_value=20,step=1,value=0,format="%d %%",help="Réduit le prix net. Chaque point de % débloque de nouveaux segments.")
with col_expl:
    if aide>0:
        st.markdown(f"<div style='background:#eff6ff;border-radius:8px;padding:10px 14px;margin-top:8px;font-size:12px'><b>{aide} % d'aides :</b><br>5 000 € → <b>{round(5000*(1-aide/100)):,} €</b><br>8 000 € → <b>{round(8000*(1-aide/100)):,} €</b><br>12 000 € → <b>{round(12000*(1-aide/100)):,} €</b></div>",unsafe_allow_html=True)

opt=optimize(aide); r_tot,dets=reach(opt["auto"],opt["vit"],opt["pl"],opt["pn"])
opt0=optimize(0); r0,_=reach(opt0["auto"],opt0["vit"],opt0["pl"],opt0["pn"]); gain=r_tot-r0
color_r="#16a34a" if r_tot/N_CIBLE>=0.25 else "#2563eb" if r_tot/N_CIBLE>=0.15 else "#d97706"

st.markdown("### 🏆 Spécifications optimales calculées")
cols=st.columns(5)
items=[
    ("🔋 Autonomie",f"{opt['auto']} km",f"Batterie ~{round(opt['auto']*0.15,1)}-{round(opt['auto']*0.20,1)} kWh (LFP 2025)"),
    ("🚀 Catégorie",SPEED_LABELS[opt["vit"]].split("  ")[0].strip(),SPEED_LABELS[opt["vit"]].split("  ")[-1].strip()),
    ("💺 Habitabilité",SEATS_LABELS[opt["pl"]],"configuration familiale"),
    ("💰 Prix net cible",f"{opt['pn']:,} €",f"Brut {opt['pb']:,} € · après {aide} % d'aides"),
    ("👥 Personas atteints",f"{r_tot:,}",f"{r_tot/N_CIBLE*100:.1f} % des {N_CIBLE/1e6:.1f}M cibles"),
]
for col,(title,value,sub) in zip(cols,items):
    fs="18px" if len(value)>8 else "24px"
    col.markdown(f"<div class='card' style='text-align:center'><div style='font-size:11px;color:#94a3b8;margin-bottom:6px'>{title}</div><div style='font-size:{fs};font-weight:700;color:#0f172a;line-height:1.2'>{value}</div><div style='font-size:10px;color:#64748b;margin-top:4px'>{sub}</div></div>",unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
bar_w=min(r_tot/N_CIBLE*100*3.5,100)
gain_badge=(f"&nbsp;<span style='font-size:12px;background:#dcfce7;color:#14532d;padding:2px 10px;border-radius:12px'>+{gain:,} personas grâce aux aides</span>" if gain>0 else "")
st.markdown(f"<div style='background:#f1f5f9;border-radius:8px;overflow:hidden;height:36px'><div style='width:{bar_w:.1f}%;background:{color_r};height:100%;display:flex;align-items:center;padding:0 16px;font-size:13px;font-weight:700;color:white;white-space:nowrap'>{r_tot:,} personas · {r_tot/N_CIBLE*100:.1f} % de la population cible{gain_badge}</div></div>",unsafe_allow_html=True)

st.divider()
st.markdown("### 👥 Détail par profil archétypal — données mobilité EMP 2019 réelles")
st.caption("La couverture autonomie est calculée à partir des distributions réelles de trajet (EMP 2019, déplacements semaine, Q1+Q2, rural+périurbain).")

for d in dets:
    if d["ok"]:
        w_auto=d["p_auto"]*100; w_afford=d["p_afford"]*100
        c_auto="#16a34a" if w_auto>=70 else "#2563eb" if w_auto>=40 else "#d97706"
        c_afford="#16a34a" if w_afford>=50 else "#2563eb" if w_afford>=25 else "#d97706"
        st.markdown(
            f"<div class='ok'><div style='display:flex;align-items:center;gap:10px;margin-bottom:8px'>"
            f"<span style='font-size:22px'>{d['icon']}</span>"
            f"<div><b>{d['profil']}</b> &nbsp;<span style='color:#64748b;font-size:11px'>{d['desc']} · {d['pct_pop']*100:.0f} % de la cible</span></div>"
            f"<span style='margin-left:auto;font-weight:700;color:{color_r};white-space:nowrap'>+{d['contrib_n']:,} personas ({d['contrib_pct']:.1f} %)</span></div>"
            f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>"
            f"<div><div style='font-size:11px;color:#64748b;margin-bottom:2px'>🔋 Autonomie couverte (EMP 2019) · P75 besoin = {d['auto_p75']} km</div>"
            f"<div style='background:#e2e8f0;border-radius:4px;height:14px;overflow:hidden'><div style='width:{w_auto:.0f}%;background:{c_auto};height:100%'></div></div>"
            f"<div style='font-size:11px;color:{c_auto};margin-top:2px'>{w_auto:.0f} % de ce profil ont leur trajet couvert par {opt['auto']} km d'autonomie</div></div>"
            f"<div><div style='font-size:11px;color:#64748b;margin-bottom:2px'>💰 Accessibilité budget (CGDD/INSEE)</div>"
            f"<div style='background:#e2e8f0;border-radius:4px;height:14px;overflow:hidden'><div style='width:{w_afford:.0f}%;background:{c_afford};height:100%'></div></div>"
            f"<div style='font-size:11px;color:{c_afford};margin-top:2px'>{w_afford:.0f} % peuvent financer {opt['pn']:,} € net</div></div>"
            f"</div></div>",unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ko'><span style='font-size:20px'>{d['icon']}</span> &nbsp;<b>{d['profil']}</b> &nbsp;<span style='color:#64748b;font-size:11px'>{d['desc']}</span><br><span style='color:#b91c1c;font-size:11px'>❌ Specs insuffisantes : {' · '.join(d['fails'])}</span></div>",unsafe_allow_html=True)

st.divider()
st.markdown("### 🔓 Seuils critiques — quand les aides déverrouillent de nouveaux profils")
rows=[]; prev_set=set(); prev_vit=None
for ap in range(0,21,2):
    o2=optimize(ap); r2,d2=reach(o2["auto"],o2["vit"],o2["pl"],o2["pn"])
    curr_ok={d["profil"] for d in d2 if d["ok"]}
    nouveaux=curr_ok-prev_set; changed=prev_vit is not None and o2["vit"]!=prev_vit
    rows.append({"Aide":f"{ap} %","Autonomie":f"{o2['auto']} km","Catégorie":SPEED_LABELS[o2["vit"]].split("  ")[0].strip(),"Places":SEATS_LABELS[o2["pl"]],"Prix net":f"{o2['pn']:,} €","Personas":f"{r2:,}","% cibles":f"{r2/N_CIBLE*100:.1f} %","Changement":("🆕 "+", ".join(nouveaux) if nouveaux else ("🔼 Catégorie ↑" if changed else "—"))})
    prev_set=curr_ok.copy(); prev_vit=o2["vit"]
st.dataframe(pd.DataFrame(rows).set_index("Aide"),use_container_width=True)

st.divider()
st.markdown(f"### 📊 Sensibilité — chaque dimension à l'aide fixée à {aide} %")
tab_a,tab_v,tab_p=st.tabs(["🔋 Autonomie","🚀 Vitesse / catégorie","💺 Nombre de places"])
for tab,vary,vals in [(tab_a,"auto",AUTO_KEYS),(tab_v,"vit",SPEED_KEYS),(tab_p,"pl",SEATS_KEYS)]:
    with tab:
        rows2=[]
        for val in vals:
            a2=val if vary=="auto" else opt["auto"]; v2=val if vary=="vit" else opt["vit"]; p2=val if vary=="pl" else opt["pl"]
            pb2=prix_brut(a2,v2,p2); pn2=round(pb2*(1-aide/100)); r2,d2=reach(a2,v2,p2,pn2)
            ok_n=sum(1 for d in d2 if d["ok"]); p_af=interp(AFFORD,pn2)
            label=(f"{val} km" if vary=="auto" else SPEED_LABELS.get(val,"").split("  ")[0].strip() if vary=="vit" else SEATS_LABELS[val])
            kc="Autonomie" if vary=="auto" else "Catégorie" if vary=="vit" else "Configuration"
            rows2.append({kc:label,"Prix brut":f"{pb2:,} €","Prix net":f"{pn2:,} €","% financent":f"{p_af*100:.0f} %","Profils":f"{ok_n}/5","Personas":f"{r2:,}","% cibles":f"{r2/N_CIBLE*100:.1f} %","Efficacité":f"{r2/max(pn2,1):.1f}"})
        st.dataframe(pd.DataFrame(rows2).set_index(list(rows2[0].keys())[0]),use_container_width=True)

st.divider()
st.markdown("### 📈 Courbe Pareto — aides publiques → personas atteints")
pareto=[]; r_ref=reach(optimize(0)["auto"],optimize(0)["vit"],optimize(0)["pl"],optimize(0)["pn"])[0]
for ap in range(0,21,1):
    o2=optimize(ap); r2,_=reach(o2["auto"],o2["vit"],o2["pl"],o2["pn"]); pareto.append((ap,r2,o2))
max_r=max(x[1] for x in pareto)
for ap,r2,o2 in pareto:
    w=r2/max_r*100; c="#16a34a" if w>=75 else "#2563eb" if w>=45 else "#d97706" if w>=20 else "#dc2626"
    gv=r2-r_ref; gs=f"+{gv:,}" if gv>0 else "—"
    st.markdown(f"<div style='display:flex;align-items:center;gap:8px;margin:2px 0'><span style='width:34px;font-size:12px;color:#64748b;text-align:right'>{ap} %</span><div style='flex:1;background:#f1f5f9;border-radius:3px;height:20px'><div style='width:{w:.1f}%;background:{c};height:100%;border-radius:3px'></div></div><span style='font-size:12px;font-weight:600;color:{c};width:80px'>{r2:,}</span><span style='font-size:11px;color:#94a3b8;width:50px'>{r2/N_CIBLE*100:.1f} %</span><span style='font-size:10px;color:#64748b;width:160px'>{o2['auto']} km · {SPEED_LABELS[o2['vit']].split()[0]}</span><span style='font-size:10px;color:#16a34a;width:60px'>{gs}</span></div>",unsafe_allow_html=True)

st.divider()
st.markdown("### 📋 Cahier des charges synthétique")
n_ok=sum(1 for d in dets if d["ok"])
co2_t=sum(p["co2_jour"]*p["pct"] for p in PROFILES if any(d["profil"]==p["nom"] and d["ok"] for d in dets))
st.markdown(
    f"<div class='card'>"
    f"<div class='lcard'>🔋 <b>Autonomie :</b> {opt['auto']} km — batterie {round(opt['auto']*0.15,1)}-{round(opt['auto']*0.20,1)} kWh (LFP 2025) — couvre {n_ok}/5 profils</div>"
    f"<div class='lcard'>🚀 <b>Homologation :</b> {SPEED_LABELS[opt['vit']]} — "
    +("accès routes nationales et départementales, indispensable en rural." if opt["vit"]>=90 else "adapté aux axes secondaires périurbains.")
    +"</div>"
    f"<div class='lcard'>💺 <b>Habitabilité :</b> {SEATS_LABELS[opt['pl']]} — "
    f"couvre {sum(p['pct'] for p in PROFILES if p['places']<=opt['pl'])*100:.0f} % des configurations familiales cibles</div>"
    f"<div class='lcard'>💰 <b>Prix cible :</b> {opt['pb']:,} € HT brut → <b>{opt['pn']:,} € net</b> après {aide} % d'aides — {interp(AFFORD,opt['pn'])*100:.0f} % de la cible peut financer</div>"
    f"<div class='lcard'>👥 <b>Potentiel :</b> <b style='color:{color_r}'>{r_tot:,} personas</b> ({r_tot/N_CIBLE*100:.1f} % des cibles)"
    +(f" · +{gain:,} grâce aux {aide} % d'aides" if gain>0 else "")+"</div>"
    f"<div class='lcard'>🌍 <b>Impact CO₂ :</b> si ce segment bascule vers l'électrique : ~{round(r_tot*co2_t/1e9,1)} ktCO₂/jour économisés (vs thermique actuel EMP 2019)</div>"
    f"<div style='margin-top:10px;font-size:11px;color:#94a3b8'>Sources mobilité : EMP 2019 SDES/INSEE — micro-données Q1+Q2 DENSITECOM 2-3-4 · Budget : CGDD 2022 «Ménages modestes et mobilité» · Prix : modèle cost-driven LFP 2025 marge 30 %</div>"
    f"</div>",unsafe_allow_html=True)
