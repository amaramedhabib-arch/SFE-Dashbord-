import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io

st.set_page_config(page_title="SFE Dashboard — AbbVie", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

ADMIN_PASSWORD = "admin2025"
USER_PASSWORD  = "team2025"
CB = "#003087"; CL = "#0066cc"; CG = "#10b981"; CA = "#f59e0b"; CR = "#ef4444"; CP = "#8b5cf6"
C5 = [CB, CL, "#4db8ff", CG, CA]
FILL5 = ["rgba(0,48,135,0.08)","rgba(0,102,204,0.08)","rgba(77,184,255,0.08)","rgba(16,185,129,0.08)","rgba(249,158,11,0.08)"]

PT = dict(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
          font=dict(color='#9ca3af',size=11),
          xaxis=dict(gridcolor='rgba(255,255,255,0.05)',color='#6b7280'),
          yaxis=dict(gridcolor='rgba(255,255,255,0.06)',color='#6b7280'),
          legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(color='#9ca3af')),
          margin=dict(l=10,r=10,t=40,b=10))

st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:#0a0e1a}
[data-testid="stSidebar"]{background:#0d1221;border-right:1px solid rgba(255,255,255,0.07)}
[data-testid="stSidebar"] *{color:#e8eaf0!important}
.main .block-container{padding-top:1.5rem;padding-bottom:2rem}
h1,h2,h3{color:#f0f0f5!important}
.mc{background:#111827;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:16px;border-top:2px solid #003087;margin-bottom:4px}
.ml{font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}
.mv{font-size:26px;font-weight:700;color:#fff;line-height:1.1}
.ms{font-size:12px;color:#9ca3af;margin-top:3px}
.sh{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#6b7280;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:8px;margin:16px 0 14px}
stTabs [data-baseweb="tab-list"]{background:#0d1221;border-bottom:1px solid rgba(255,255,255,0.08)}
[data-baseweb="tab"]{color:#6b7280!important;font-size:13px!important}
[aria-selected="true"]{color:#fff!important;border-bottom:2px solid #003087!important}
div[data-testid="stFileUploader"]{background:#111827;border-radius:12px;border:1px dashed rgba(0,48,135,0.4);padding:1rem}
</style>""", unsafe_allow_html=True)

def fmtk(v):
    if v>=1e6: return f"{v/1e6:.1f}M€"
    if v>=1e3: return f"{v/1e3:.0f}K€"
    return f"{v:.0f}€"

def fmtp(v): return f"{v:+.1f}%"

def sort_months(lst):
    return sorted(lst, key=lambda x: pd.to_datetime("01 "+x, format="%d %b-%Y", errors="coerce"))

def kpi(col, label, val, sub=""):
    col.markdown(f'<div class="mc"><div class="ml">{label}</div><div class="mv">{val}</div><div class="ms">{sub}</div></div>', unsafe_allow_html=True)

# ── AUTH ──────────────────────────────────────────────────────────────────────
def login():
    st.markdown("""<div style="text-align:center;padding:3rem 0 1rem">
    <div style="font-size:11px;letter-spacing:.3em;color:#003087;text-transform:uppercase;margin-bottom:1rem">AbbVie</div>
    <h1 style="font-size:2.2rem;font-weight:700;color:#fff;margin-bottom:.5rem">SFE Dashboard</h1>
    <p style="color:#6b7280;font-size:14px">Territoire FA-99 · Performance Commerciale</p></div>""", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1.2,1])
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        role = st.selectbox("Rôle", ["Sélectionner...","Admin","User"])
        pwd  = st.text_input("Mot de passe", type="password")
        if st.button("Connexion", use_container_width=True):
            if role=="Admin" and pwd==ADMIN_PASSWORD: st.session_state.role="admin"; st.rerun()
            elif role=="User" and pwd==USER_PASSWORD: st.session_state.role="user"; st.rerun()
            elif role=="Sélectionner...": st.warning("Sélectionne un rôle.")
            else: st.error("Mot de passe incorrect.")

# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load(b):
    xl = pd.read_excel(io.BytesIO(b), sheet_name=None)
    db = xl.get("DB", list(xl.values())[0])
    calls = xl.get("Calls", list(xl.values())[1] if len(xl)>1 else pd.DataFrame())
    db["Month-Year"]   = db["Month-Year"].astype(str)
    db["Quarter-Year"] = db["Quarter-Year"].astype(str)
    db["Year"]         = db["Year"].astype(int)
    if len(calls):
        calls["Call: Created Date"] = pd.to_datetime(calls["Call: Created Date"], errors="coerce")
        calls["Month-Year"]   = calls["Call: Created Date"].dt.strftime("%b-%Y")
        calls["Quarter-Year"] = "Q"+calls["Call: Created Date"].dt.quarter.astype(str)+"-"+calls["Call: Created Date"].dt.year.astype(str)
        calls["Year"] = calls["Call: Created Date"].dt.year.astype("Int64")
    return db, calls

# ── ADMIN ─────────────────────────────────────────────────────────────────────
def admin_panel():
    with st.sidebar:
        st.markdown('<div style="padding:16px 0 8px"><div style="font-size:16px;font-weight:700;color:#fff">SFE Dashboard</div><div style="font-size:11px;color:#6b7280">Admin</div></div>', unsafe_allow_html=True)
        if "data" in st.session_state:
            if st.button("Voir le dashboard", use_container_width=True): st.session_state.view="dash"; st.rerun()
        if st.button("Déconnexion", use_container_width=True):
            for k in ["role","data","view"]: st.session_state.pop(k,None)
            st.rerun()
    st.markdown("## Mise à jour des données")
    up = st.file_uploader("Dépose le fichier Excel Salesforce", type=["xlsx","xls"])
    if up:
        try:
            db, calls = load(up.read())
            st.session_state.data = (db, calls)
            st.success(f"Chargé — {len(db)} lignes ventes · {len(calls)} calls")
            if st.button("Accéder au dashboard →", use_container_width=True): st.session_state.view="dash"; st.rerun()
        except Exception as e: st.error(f"Erreur : {e}")
    elif "data" in st.session_state:
        db, _ = st.session_state.data
        st.info(f"Données actuelles : {len(db)} lignes")
        if st.button("Voir le dashboard →", use_container_width=True): st.session_state.view="dash"; st.rerun()

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
def sidebar_filters(db, calls):
    with st.sidebar:
        role_lbl = "Admin" if st.session_state.role=="admin" else "User"
        st.markdown(f'<div style="padding:12px 0 6px"><div style="font-size:15px;font-weight:700;color:#fff">SFE Dashboard</div><div style="font-size:11px;color:#6b7280">FA-99 · {role_lbl}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        years    = ["Toutes"] + sorted(db["Year"].unique().tolist(), reverse=True)
        quarters = ["Tous"]   + sorted(db["Quarter-Year"].unique().tolist())
        months   = ["Tous"]   + sort_months(db["Month-Year"].unique().tolist())
        products = ["Tous"]   + sorted(db["Product Group"].unique().tolist())
        packs    = ["Tous"]   + sorted(db["Product Pack"].unique().tolist())
        segs     = ["Tous"]   + sorted(db["Acc Level 2 Segment"].unique().tolist())
        cities   = ["Toutes"] + sorted(db["Ship To - City"].dropna().unique().tolist())
        st.markdown("**Filtres**")
        fy  = st.selectbox("Année",     years)
        fq  = st.selectbox("Trimestre", quarters)
        fm  = st.selectbox("Mois",      months)
        fp  = st.selectbox("Produit",   products)
        fpp = st.selectbox("Déclinaison", packs)
        fs  = st.selectbox("Segment",   segs)
        fc  = st.selectbox("Secteur",   cities)
        st.markdown("---")
        call_months  = ["Tous"] + sort_months(calls["Month-Year"].dropna().unique().tolist()) if len(calls) else ["Tous"]
        call_statuses= ["Tous"] + sorted(calls["Status"].dropna().unique().tolist()) if len(calls) else ["Tous"]
        st.markdown("**Filtres activité**")
        fcm = st.selectbox("Mois (calls)", call_months)
        fcs = st.selectbox("Statut",       call_statuses)
        st.markdown("---")
        if st.session_state.role=="admin":
            if st.button("Mettre à jour les données", use_container_width=True): st.session_state.view="admin"; st.rerun()
        if st.button("Déconnexion", use_container_width=True):
            for k in ["role","data","view"]: st.session_state.pop(k,None)
            st.rerun()
    return fy, fq, fm, fp, fpp, fs, fc, fcm, fcs

def filt_db(db, fy, fq, fm, fp, fpp, fs, fc):
    d = db.copy()
    if fy!="Toutes":  d=d[d["Year"]==int(fy)]
    if fq!="Tous":    d=d[d["Quarter-Year"]==fq]
    if fm!="Tous":    d=d[d["Month-Year"]==fm]
    if fp!="Tous":    d=d[d["Product Group"]==fp]
    if fpp!="Tous":   d=d[d["Product Pack"]==fpp]
    if fs!="Tous":    d=d[d["Acc Level 2 Segment"]==fs]
    if fc!="Toutes":  d=d[d["Ship To - City"]==fc]
    return d

def filt_calls(calls, fcm, fcs):
    if not len(calls): return calls
    c=calls.copy()
    if fcm!="Tous": c=c[c["Month-Year"]==fcm]
    if fcs!="Tous": c=c[c["Status"]==fcs]
    return c

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — VENTES
# ══════════════════════════════════════════════════════════════════════════════
def tab_ventes(db, dbf):
    total_ca   = dbf["Net Sales"].sum()
    total_qty  = dbf["Quantity"].sum()
    top_prod   = dbf.groupby("Product Group")["Net Sales"].sum().idxmax() if len(dbf) else "—"
    top_prod_v = dbf.groupby("Product Group")["Net Sales"].sum().max() if len(dbf) else 0

    # MoM
    all_months = sort_months(db["Month-Year"].unique().tolist())
    mom_pct = None
    if len(all_months)>=2:
        last_m  = all_months[-1]
        prev_m  = all_months[-2]
        s_last  = db[db["Month-Year"]==last_m]["Net Sales"].sum()
        s_prev  = db[db["Month-Year"]==prev_m]["Net Sales"].sum()
        if s_prev>0: mom_pct = (s_last-s_prev)/s_prev*100

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1,"CA Total", fmtk(total_ca), f"{len(dbf)} transactions")
    kpi(c2,"Unités vendues", f"{int(total_qty):,}", "Quantité totale")
    kpi(c3,"Top produit", top_prod, fmtk(top_prod_v))
    kpi(c4,"Croissance MoM", fmtp(mom_pct) if mom_pct is not None else "—",
        f"{all_months[-1] if all_months else ''} vs {all_months[-2] if len(all_months)>=2 else ''}")

    st.markdown('<div class="sh">Évolution mensuelle</div>', unsafe_allow_html=True)

    months_o = sort_months(dbf["Month-Year"].unique().tolist())
    prods    = sorted(dbf["Product Group"].unique())

    # G1 — Net Sales
    fig1 = go.Figure()
    for i,p in enumerate(prods):
        sub = dbf[dbf["Product Group"]==p].groupby("Month-Year")["Net Sales"].sum()
        sub = sub.reindex(months_o).fillna(0)
        fig1.add_trace(go.Scatter(x=sub.index, y=sub.values, name=p,
            mode="lines+markers", line=dict(color=C5[i%len(C5)],width=2),
            fill="tozeroy", fillcolor=FILL5[i%len(FILL5)]))
    fig1.update_layout(title="Net Sales par produit", **PT, height=260)
    st.plotly_chart(fig1, use_container_width=True)

    # G2 — Quantity
    fig2 = go.Figure()
    for i,p in enumerate(prods):
        sub = dbf[dbf["Product Group"]==p].groupby("Month-Year")["Quantity"].sum()
        sub = sub.reindex(months_o).fillna(0)
        fig2.add_trace(go.Scatter(x=sub.index, y=sub.values, name=p,
            mode="lines+markers", line=dict(color=C5[i%len(C5)],width=2,dash="dot"),
            fill="tozeroy", fillcolor=FILL5[i%len(FILL5)]))
    fig2.update_layout(title="Quantités vendues par produit", **PT, height=240)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="sh">Répartitions & Classements</div>', unsafe_allow_html=True)
    r1,r2 = st.columns(2)

    # G3 — Segment
    with r1:
        seg_d = dbf.groupby("Acc Level 2 Segment")["Net Sales"].sum().reset_index().sort_values("Net Sales",ascending=True)
        fig3 = px.bar(seg_d, x="Net Sales", y="Acc Level 2 Segment", orientation="h",
                      title="Net Sales par segment (Acc Level 2)",
                      color="Net Sales", color_continuous_scale=["#001a4d","#0066cc"])
        fig3.update_layout(**PT, height=260, showlegend=False)
        fig3.update_coloraxes(showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    # G4 — Top 20 clients
    with r2:
        top20 = dbf.groupby("Customer Name")["Net Sales"].sum().nlargest(20).reset_index().sort_values("Net Sales")
        fig4 = px.bar(top20, x="Net Sales", y="Customer Name", orientation="h",
                      title="Top 20 clients — Net Sales", color_discrete_sequence=[CL])
        fig4.update_layout(**PT, height=260, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    # G5 — Bubble chart quadrants (dernier mois)
    st.markdown('<div class="sh">Analyse positionnelle produits — dernier mois</div>', unsafe_allow_html=True)
    all_m_db = sort_months(db["Month-Year"].unique().tolist())
    if len(all_m_db)>=2:
        last_m = all_m_db[-1]; prev_m = all_m_db[-2]
        last_d = db[db["Month-Year"]==last_m].groupby("Product Group")["Net Sales"].sum()
        prev_d = db[db["Month-Year"]==prev_m].groupby("Product Group")["Net Sales"].sum()
        total_last = last_d.sum()
        bubble_df = []
        for p in last_d.index:
            s_l = last_d.get(p,0); s_p = prev_d.get(p,0)
            evol = (s_l-s_p)/s_p*100 if s_p>0 else 0
            part = s_l/total_last*100 if total_last>0 else 0
            bubble_df.append({"Produit":p,"Evol%":round(evol,1),"Part%":round(part,1),"Sales":s_l})
        bdf = pd.DataFrame(bubble_df)
        mean_evol = bdf["Evol%"].mean()
        bdf["EcartMoyenne"] = bdf["Evol%"] - mean_evol

        def quadrant(row):
            if row["Evol%"]>=0 and row["EcartMoyenne"]>=0: return "⭐ Croissance > moyenne"
            if row["Evol%"]<0  and row["EcartMoyenne"]>=0: return "📉 Décroissance > moyenne"
            if row["Evol%"]>=0 and row["EcartMoyenne"]<0:  return "⚠️ Croissance < moyenne"
            return "🔴 Décroissance < moyenne"

        bdf["Quadrant"] = bdf.apply(quadrant, axis=1)
        cmap = {"⭐ Croissance > moyenne":CG,"📉 Décroissance > moyenne":CA,
                "⚠️ Croissance < moyenne":CL,"🔴 Décroissance < moyenne":CR}

        fig5 = px.scatter(bdf, x="Evol%", y="EcartMoyenne", size="Part%", color="Quadrant",
                          text="Produit", hover_data={"Sales":True,"Part%":True},
                          title=f"Positionnement produits — {last_m} (taille = part CA)",
                          color_discrete_map=cmap, size_max=60)
        fig5.add_vline(x=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        fig5.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        fig5.update_traces(textposition="top center", textfont=dict(color="#fff",size=11))
        fig5.update_layout(**PT, height=380,
            annotations=[
                dict(x=max(bdf["Evol%"])*0.85, y=max(bdf["EcartMoyenne"])*0.85, text="⭐ Croissance forte", showarrow=False, font=dict(color=CG,size=10)),
                dict(x=min(bdf["Evol%"])*0.85, y=max(bdf["EcartMoyenne"])*0.85, text="📉 Résistant", showarrow=False, font=dict(color=CA,size=10)),
                dict(x=max(bdf["Evol%"])*0.85, y=min(bdf["EcartMoyenne"])*0.85, text="⚠️ Sous moyenne", showarrow=False, font=dict(color=CL,size=10)),
                dict(x=min(bdf["Evol%"])*0.85, y=min(bdf["EcartMoyenne"])*0.85, text="🔴 En difficulté", showarrow=False, font=dict(color=CR,size=10)),
            ])
        st.plotly_chart(fig5, use_container_width=True)

    # G6 — Par ville
    st.markdown('<div class="sh">Répartition par secteur</div>', unsafe_allow_html=True)
    city_d = dbf.groupby("Ship To - City")["Net Sales"].sum().nlargest(20).reset_index().sort_values("Net Sales")
    fig6 = px.bar(city_d, x="Net Sales", y="Ship To - City", orientation="h",
                  title="Net Sales par secteur (Top 20 villes)", color_discrete_sequence=[CP])
    fig6.update_layout(**PT, height=340, showlegend=False)
    st.plotly_chart(fig6, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — ACTIVITÉ
# ══════════════════════════════════════════════════════════════════════════════
def tab_activite(db, cf):
    if not len(cf):
        st.info("Aucune donnée d'activité disponible."); return

    nb_calls = len(cf)
    nb_clients_calls = cf["Customer Name"].nunique()
    nb_clients_db    = db["Customer Name"].nunique()
    couverture = round(nb_clients_calls/nb_clients_db*100,1) if nb_clients_db>0 else 0

    # Produit le plus mentionné
    all_prods = pd.concat([
        cf["Detailed Products 1"].dropna(),
        cf["Detailed Products 2"].dropna(),
        cf["Detailed Products 3"].dropna()
    ])
    top_prod_call = all_prods.value_counts().idxmax() if len(all_prods) else "—"

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1,"Calls réalisés", str(nb_calls), f"{nb_clients_calls} clients contactés")
    kpi(c2,"Taux de couverture", f"{couverture}%", f"{nb_clients_calls}/{nb_clients_db} clients")
    kpi(c3,"Produit le plus présenté", top_prod_call, "Mentions cumulées")
    dur_known = cf["Duration"].dropna()
    kpi(c4,"Durée totale", f"{int(dur_known.sum())}min" if len(dur_known) else "N/D",
        f"Moy. {dur_known.mean():.0f} min/call" if len(dur_known) else "Non renseigné")

    st.markdown('<div class="sh">Évolution & Répartitions</div>', unsafe_allow_html=True)

    # G7 — Evolution mensuelle calls
    months_c = sort_months(cf["Month-Year"].dropna().unique().tolist())
    call_types = sorted(cf["Call Type"].dropna().unique())
    fig7 = go.Figure()
    cc = [CG, CA, CR, CP]
    for i,ct in enumerate(call_types):
        sub = cf[cf["Call Type"]==ct].groupby("Month-Year").size().reindex(months_c).fillna(0)
        fig7.add_trace(go.Scatter(x=sub.index, y=sub.values, name=ct,
            mode="lines+markers", line=dict(color=cc[i%len(cc)],width=2)))
    fig7.update_layout(title="Évolution mensuelle des calls par type", **PT, height=240)
    st.plotly_chart(fig7, use_container_width=True)

    r1,r2,r3 = st.columns(3)

    # G5 — Call Type donut
    with r1:
        ct_d = cf["Call Type"].value_counts().reset_index()
        ct_d.columns=["Type","Count"]
        fig_ct = px.pie(ct_d, values="Count", names="Type", hole=.55,
                        title="Répartition par type de call",
                        color_discrete_sequence=[CB,CG,CA])
        fig_ct.update_layout(**PT, height=260)
        fig_ct.update_traces(textfont_color="white")
        st.plotly_chart(fig_ct, use_container_width=True)

    # G1 — Segment donut (via jointure avec DB)
    with r2:
        seg_calls = cf.merge(db[["Customer Name","Acc Level 2 Segment"]].drop_duplicates(),
                             on="Customer Name", how="left")
        seg_d = seg_calls["Acc Level 2 Segment"].fillna("Non segmenté").value_counts().reset_index()
        seg_d.columns=["Segment","Count"]
        fig_sg = px.pie(seg_d, values="Count", names="Segment", hole=.55,
                        title="Répartition calls par segment",
                        color_discrete_sequence=[CB,CL,"#4db8ff",CG,CA,CR,CP,"#6b7280"])
        fig_sg.update_layout(**PT, height=260)
        fig_sg.update_traces(textfont_color="white")
        st.plotly_chart(fig_sg, use_container_width=True)

    # Statut donut
    with r3:
        st_d = cf["Status"].value_counts().reset_index()
        st_d.columns=["Status","Count"]
        fig_st = px.pie(st_d, values="Count", names="Status", hole=.55,
                        title="Répartition par statut",
                        color_discrete_sequence=[CB,CG])
        fig_st.update_layout(**PT, height=260)
        fig_st.update_traces(textfont_color="white")
        st.plotly_chart(fig_st, use_container_width=True)

    st.markdown('<div class="sh">Classements clients & Produits</div>', unsafe_allow_html=True)
    r4,r5 = st.columns(2)

    # G2 — Top 20 clients par calls
    with r4:
        top20c = cf.groupby("Customer Name").size().nlargest(20).reset_index()
        top20c.columns=["Client","Calls"]
        top20c = top20c.sort_values("Calls")
        fig_t20 = px.bar(top20c, x="Calls", y="Client", orientation="h",
                         title="Top 20 clients — Nombre de calls",
                         color_discrete_sequence=[CG])
        fig_t20.update_layout(**PT, height=340, showlegend=False)
        st.plotly_chart(fig_t20, use_container_width=True)

    # G6 — Produits mentionnés
    with r5:
        prod_all = pd.concat([cf["Detailed Products 1"].dropna(),
                              cf["Detailed Products 2"].dropna(),
                              cf["Detailed Products 3"].dropna()])
        prod_d = prod_all.value_counts().reset_index()
        prod_d.columns=["Produit","Mentions"]
        prod_d = prod_d.sort_values("Mentions")
        fig_pr = px.bar(prod_d, x="Mentions", y="Produit", orientation="h",
                        title="Produits mentionnés lors des calls",
                        color_discrete_sequence=[CA])
        fig_pr.update_layout(**PT, height=340, showlegend=False)
        st.plotly_chart(fig_pr, use_container_width=True)

    st.markdown('<div class="sh">Segmentation Top 20 & Répartition régionale</div>', unsafe_allow_html=True)
    r6,r7 = st.columns(2)

    # G3 — Segmentation top 20
    with r6:
        top20_names = cf.groupby("Customer Name").size().nlargest(20).index
        top20_seg = seg_calls[seg_calls["Customer Name"].isin(top20_names)]
        seg20_d = top20_seg["Acc Level 2 Segment"].fillna("Non segmenté").value_counts().reset_index()
        seg20_d.columns=["Segment","Count"]
        fig_s20 = px.bar(seg20_d, x="Segment", y="Count",
                         title="Segmentation des Top 20 clients (par calls)",
                         color="Segment",
                         color_discrete_sequence=[CB,CL,"#4db8ff",CG,CA,CR,CP,"#6b7280"])
        fig_s20.update_layout(**PT, height=260, showlegend=False)
        st.plotly_chart(fig_s20, use_container_width=True)

    # G4 — Région
    with r7:
        region_calls = cf.merge(db[["Customer Name","Ship To - City"]].drop_duplicates(),
                                on="Customer Name", how="left")
        reg_d = region_calls["Ship To - City"].value_counts().nlargest(15).reset_index()
        reg_d.columns=["Ville","Calls"]
        reg_d = reg_d.sort_values("Calls")
        fig_rg = px.bar(reg_d, x="Calls", y="Ville", orientation="h",
                        title="Répartition calls par région (Top 15)",
                        color_discrete_sequence=[CP])
        fig_rg.update_layout(**PT, height=260, showlegend=False)
        st.plotly_chart(fig_rg, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — CORRÉLATION
# ══════════════════════════════════════════════════════════════════════════════
def tab_correlation(dbf, cf):
    if not len(cf):
        st.info("Aucune donnée d'activité disponible pour la corrélation."); return

    sales_c  = dbf.groupby("Customer Name")["Net Sales"].sum()
    calls_c  = cf.groupby("Customer Name").size()
    common   = sorted(set(sales_c.index) & set(calls_c.index))

    if not common:
        st.info("Aucun client commun entre les deux sources de données."); return

    cdf = pd.DataFrame({
        "Client": common,
        "Calls":  [int(calls_c[c]) for c in common],
        "Net Sales": [float(sales_c[c]) for c in common]
    })
    cdf["ROI"] = (cdf["Net Sales"]/cdf["Calls"]).round(0)

    # ROI global et par dimensions
    roi_global = dbf["Net Sales"].sum()/len(cf) if len(cf)>0 else 0

    seg_roi = dbf.merge(cf[["Customer Name"]].drop_duplicates(), on="Customer Name", how="inner")
    seg_roi_d = seg_roi.groupby("Acc Level 2 Segment").agg(sales=("Net Sales","sum")).reset_index()
    seg_calls_d = cf.merge(dbf[["Customer Name","Acc Level 2 Segment"]].drop_duplicates(), on="Customer Name", how="left")
    seg_calls_cnt = seg_calls_d.groupby("Acc Level 2 Segment").size().reset_index(name="calls")
    seg_merged = seg_roi_d.merge(seg_calls_cnt, on="Acc Level 2 Segment")
    seg_merged["roi"] = (seg_merged["sales"]/seg_merged["calls"]).round(0)
    best_seg = seg_merged.nlargest(1,"roi").iloc[0] if len(seg_merged) else None

    type_calls = cf.groupby("Call Type").size().reset_index(name="calls")
    type_sales_df = cf.merge(dbf[["Customer Name","Net Sales"]], on="Customer Name", how="left")
    type_sales = type_sales_df.groupby("Call Type")["Net Sales"].sum().reset_index()
    type_merged = type_calls.merge(type_sales, on="Call Type")
    type_merged["roi"] = (type_merged["Net Sales"]/type_merged["calls"]).round(0)
    best_type = type_merged.nlargest(1,"roi").iloc[0] if len(type_merged) else None

    # Coefficient de corrélation
    corr_val = round(np.corrcoef(cdf["Calls"], cdf["Net Sales"])[0,1], 2) if len(cdf)>2 else None

    c1,c2,c3,c4,c5 = st.columns(5)
    kpi(c1,"ROI global", fmtk(roi_global), "Net Sales / Call")
    kpi(c2,"Meilleur segment", best_seg["Acc Level 2 Segment"] if best_seg is not None else "—",
        fmtk(best_seg["roi"]) if best_seg is not None else "")
    kpi(c3,"Meilleur type call", best_type["Call Type"] if best_type is not None else "—",
        fmtk(best_type["roi"]) if best_type is not None else "")
    kpi(c4,"Corrélation calls×ventes",
        f"r = {corr_val}" if corr_val is not None else "—",
        "Forte" if corr_val and abs(corr_val)>0.6 else "Modérée" if corr_val and abs(corr_val)>0.3 else "Faible")
    kpi(c5,"Clients analysés", str(len(common)), f"{len(cdf[cdf['ROI']>roi_global])} au-dessus ROI moyen")

    # G1 — Histogramme double axe par segment
    st.markdown('<div class="sh">Impact pression de visite sur les ventes</div>', unsafe_allow_html=True)
    segs_available = sorted(dbf["Acc Level 2 Segment"].unique())
    seg_sel = st.selectbox("Sélectionner le segment", segs_available)

    seg_clients = dbf[dbf["Acc Level 2 Segment"]==seg_sel]["Customer Name"].unique()
    seg_calls_clients = cf[cf["Customer Name"].isin(seg_clients)]

    db_all_months = sorted(dbf["Month-Year"].unique(), key=lambda x: pd.to_datetime("01 "+x, format="%d %b-%Y", errors="coerce"))
    if len(db_all_months)>=2:
        last_m = db_all_months[-1]; prev_m = db_all_months[-2]
        last_s = dbf[(dbf["Acc Level 2 Segment"]==seg_sel)&(dbf["Month-Year"]==last_m)].groupby("Customer Name")["Net Sales"].sum()
        prev_s = dbf[(dbf["Acc Level 2 Segment"]==seg_sel)&(dbf["Month-Year"]==prev_m)].groupby("Customer Name")["Net Sales"].sum()
        calls_by_c = seg_calls_clients.groupby("Customer Name").size()

        hist_clients = sorted(set(last_s.index)|set(prev_s.index))
        hist_data = []
        for c in hist_clients:
            s_l=last_s.get(c,0); s_p=prev_s.get(c,0)
            evol=(s_l-s_p)/s_p*100 if s_p>0 else 0
            hist_data.append({"Client":c,"Calls":int(calls_by_c.get(c,0)),"Evol%":round(evol,1)})
        hdf = pd.DataFrame(hist_data)

        if len(hdf):
            fig_h = go.Figure()
            fig_h.add_trace(go.Bar(x=hdf["Client"], y=hdf["Calls"], name="Nb Calls",
                yaxis="y1", marker_color=CG, opacity=0.85))
            fig_h.add_trace(go.Bar(x=hdf["Client"], y=hdf["Evol%"], name="Évolution CA %",
                yaxis="y2", marker_color=CP, opacity=0.85))
            fig_h.update_layout(
                title=f"Segment {seg_sel} — Impact de la pression de visite sur les ventes",
                **PT, height=360, barmode="group",
                yaxis=dict(title="Nb Calls", color=CG, gridcolor="rgba(255,255,255,0.04)"),
                yaxis2=dict(title="Évolution CA %", overlaying="y", side="right", color=CP, gridcolor="rgba(0,0,0,0)"),
                legend=dict(orientation="h", y=-0.15)
            )
            st.plotly_chart(fig_h, use_container_width=True)

    # G2 — Scatter
    st.markdown('<div class="sh">Corrélation Calls × Ventes par client</div>', unsafe_allow_html=True)
    med_s = cdf["Net Sales"].median(); med_c = cdf["Calls"].median()

    def classify(row):
        if row["Calls"]>=med_c and row["Net Sales"]<med_s:  return "Fort potentiel"
        if row["Calls"]<=med_c and row["Net Sales"]>=med_s: return "Top performer"
        return "Standard"

    cdf["Profil"] = cdf.apply(classify, axis=1)
    cmap = {"Fort potentiel":CA,"Top performer":CG,"Standard":"#60a5fa"}

    r1,r2 = st.columns([1.3,1])
    with r1:
        fig_sc = px.scatter(cdf, x="Calls", y="Net Sales", color="Profil",
                            hover_name="Client", hover_data={"ROI":True},
                            color_discrete_map=cmap, title="Scatter — Calls vs Net Sales par client")
        fig_sc.update_traces(marker=dict(size=10,opacity=0.85))
        fig_sc.update_layout(**PT, height=340)
        st.plotly_chart(fig_sc, use_container_width=True)

    with r2:
        st.markdown("<br>", unsafe_allow_html=True)
        pot = cdf[cdf["Profil"]=="Fort potentiel"].nlargest(5,"Calls")[["Client","Calls","Net Sales"]]
        per = cdf[cdf["Profil"]=="Top performer"].nlargest(5,"Net Sales")[["Client","Calls","Net Sales"]]

        if len(pot):
            st.markdown(f'<div style="background:rgba(249,158,11,0.08);border:1px solid rgba(249,158,11,0.2);border-radius:8px;padding:12px;margin-bottom:10px">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:11px;font-weight:700;color:{CA};margin-bottom:8px">FORT POTENTIEL — calls élevés, ventes faibles</div>', unsafe_allow_html=True)
            for _,row in pot.iterrows():
                st.markdown(f'<div style="font-size:12px;color:#d1d5db;padding:3px 0">{row["Client"]} — {row["Calls"]} calls · {fmtk(row["Net Sales"])}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if len(per):
            st.markdown(f'<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:8px;padding:12px">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:11px;font-weight:700;color:{CG};margin-bottom:8px">TOP PERFORMERS — ventes élevées, calls modérés</div>', unsafe_allow_html=True)
            for _,row in per.iterrows():
                st.markdown(f'<div style="font-size:12px;color:#d1d5db;padding:3px 0">{row["Client"]} — {fmtk(row["Net Sales"])} · {row["Calls"]} calls</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # G3 — Tableau corrélation
    st.markdown('<div class="sh">Tableau de corrélation complet</div>', unsafe_allow_html=True)
    disp = cdf.sort_values("Net Sales",ascending=False).reset_index(drop=True)
    disp["Net Sales"] = disp["Net Sales"].apply(lambda x: f"{x/1000:.1f}K€")
    disp["ROI"] = disp["ROI"].apply(lambda x: f"{x:.0f}€")
    disp = disp.rename(columns={"ROI":"ROI / Call"})
    st.dataframe(disp, use_container_width=True, hide_index=True)

    # G4 — Matrice ROI heatmap
    st.markdown('<div class="sh">Matrice ROI — Segment × Type de call</div>', unsafe_allow_html=True)
    matrix_df = cf.merge(dbf[["Customer Name","Acc Level 2 Segment","Net Sales"]], on="Customer Name", how="left")
    if "Call Type" in matrix_df.columns and "Acc Level 2 Segment" in matrix_df.columns:
        calls_mx = matrix_df.groupby(["Acc Level 2 Segment","Call Type"]).size().reset_index(name="Calls")
        sales_mx = matrix_df.groupby(["Acc Level 2 Segment","Call Type"])["Net Sales"].sum().reset_index()
        mx = calls_mx.merge(sales_mx, on=["Acc Level 2 Segment","Call Type"])
        mx["ROI"] = (mx["Net Sales"]/mx["Calls"]).round(0)
        pivot = mx.pivot(index="Acc Level 2 Segment", columns="Call Type", values="ROI").fillna(0)

        fig_hm = go.Figure(data=go.Heatmap(
            z=pivot.values, x=list(pivot.columns), y=list(pivot.index),
            colorscale=[[0,CR],[0.5,CA],[1,CG]],
            text=[[f"{int(v)}€" for v in row] for row in pivot.values],
            texttemplate="%{text}", textfont=dict(color="white",size=12)
        ))
        fig_hm.update_layout(title="ROI Net Sales/Call par Segment × Type de call",
                             **PT, height=300)
        st.plotly_chart(fig_hm, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    if "role" not in st.session_state: login(); return
    if "view" not in st.session_state: st.session_state.view = "admin" if st.session_state.role=="admin" else "dash"

    if "data" not in st.session_state or st.session_state.view=="admin":
        admin_panel(); return

    db, calls = st.session_state.data
    fy,fq,fm,fp,fpp,fs,fc,fcm,fcs = sidebar_filters(db, calls)
    dbf = filt_db(db, fy, fq, fm, fp, fpp, fs, fc)
    cf  = filt_calls(calls, fcm, fcs)

    st.markdown(f'<h1 style="font-size:1.5rem;font-weight:700;color:#fff;margin-bottom:2px">SFE Dashboard — AbbVie</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#6b7280;font-size:12px;margin-bottom:16px">Territoire FA-99 · Performance Commerciale · {fy if fy!="Toutes" else "2023–2025"}</p>', unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["📈  Analyse des ventes", "📞  Analyse de l'activité", "🔗  Corrélation Calls × Ventes"])

    with t1: tab_ventes(db, dbf)
    with t2: tab_activite(db, cf)
    with t3: tab_correlation(dbf, cf)

if __name__ == "__main__":
    main()
