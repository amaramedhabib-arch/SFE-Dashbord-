import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io

st.set_page_config(
    page_title="SFE Dashboard — AbbVie",
    page_icon="icon_512.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PALETTE ───────────────────────────────────────────────────────────────────
CB  = "#003087"   # AbbVie bleu foncé
CL  = "#0066cc"   # AbbVie bleu clair
CG  = "#22c55e"   # Vert lisible
CA  = "#f59e0b"   # Ambre
CR  = "#f43f5e"   # Rouge vif
CP  = "#a78bfa"   # Violet clair
C5  = [CL, "#38bdf8", CG, CA, CP]
FILL5 = ["rgba(0,102,204,0.1)","rgba(56,189,248,0.1)","rgba(34,197,94,0.1)","rgba(245,158,11,0.1)","rgba(167,139,250,0.1)"]

# Thème Plotly de base
PT_BASE = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#cbd5e1", size=12),
    margin=dict(l=16, r=16, t=48, b=16)
)

# Thème pour graphiques simples (1 axe)
def pt(height=300, show_legend=True):
    d = dict(**PT_BASE, height=height,
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", color="#94a3b8", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", color="#94a3b8", tickfont=dict(size=11)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1", size=11),
                    orientation="h", y=1.08, x=0) if show_legend else dict(visible=False)
    )
    return d

# Thème pour graphiques à DOUBLE axe Y (pas de clé yaxis dans la base)
def pt_dual(height=360):
    return dict(**PT_BASE, height=height, barmode="group",
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", color="#94a3b8", tickfont=dict(size=10), tickangle=-35),
        yaxis =dict(title=dict(text="Nb Calls",     font=dict(color=CG, size=12)), color=CG,
                    gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color=CG, size=11)),
        yaxis2=dict(title=dict(text="Évolution CA %", font=dict(color=CP, size=12)), color=CP,
                    overlaying="y", side="right", gridcolor="rgba(0,0,0,0)", tickfont=dict(color=CP, size=11),
                    zeroline=True, zerolinecolor="rgba(255,255,255,0.2)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1", size=12),
                    orientation="h", y=-0.18)
    )

ADMIN_PASSWORD = "admin2025"
USER_PASSWORD  = "team2025"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #080c18; }
[data-testid="stSidebar"] {
    background: #0d1221;
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stSelectbox label { color: #94a3b8 !important; font-size: 12px !important; }
.main .block-container { padding-top: 1.25rem; padding-bottom: 2rem; max-width: 1400px; }

/* Onglets */
[data-baseweb="tab-list"] {
    background: #0d1221 !important;
    border-bottom: 1px solid rgba(255,255,255,0.1) !important;
    gap: 4px;
    padding: 0 4px;
}
[data-baseweb="tab"] {
    color: #64748b !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    border-radius: 6px 6px 0 0 !important;
}
[aria-selected="true"] {
    color: #f1f5f9 !important;
    background: rgba(0,102,204,0.15) !important;
    border-bottom: 2px solid #0066cc !important;
}
[data-baseweb="tab"]:hover { color: #cbd5e1 !important; background: rgba(255,255,255,0.04) !important; }
[data-baseweb="tab-panel"] { padding-top: 20px !important; }

/* KPI cards */
.kc {
    background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
    border: 1px solid rgba(255,255,255,0.09);
    border-top: 2px solid #0066cc;
    border-radius: 10px;
    padding: 16px 18px;
}
.kl { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: .1em; margin-bottom: 8px; font-weight: 600; }
.kv { font-size: 28px; font-weight: 700; color: #f1f5f9; line-height: 1.1; }
.ks { font-size: 12px; color: #94a3b8; margin-top: 5px; }

/* Section headers */
.sh {
    font-size: 13px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .08em; color: #94a3b8;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding-bottom: 10px; margin: 24px 0 16px;
    display: flex; align-items: center; gap: 8px;
}
.sh::before { content: ''; display: inline-block; width: 3px; height: 14px; background: #0066cc; border-radius: 2px; }

/* Titles */
h1 { color: #f1f5f9 !important; font-size: 1.6rem !important; }
h2, h3 { color: #e2e8f0 !important; }

/* Chart cards */
.chart-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 4px;
}

/* File uploader */
div[data-testid="stFileUploader"] {
    background: #111827;
    border-radius: 10px;
    border: 1.5px dashed rgba(0,102,204,0.5);
    padding: 1.5rem;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* Badges */
.badge-green { background: rgba(34,197,94,0.15); color: #4ade80; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-amber { background: rgba(245,158,11,0.15); color: #fbbf24; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-red   { background: rgba(244,63,94,0.15);  color: #fb7185; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── UTILS ─────────────────────────────────────────────────────────────────────
def fmtk(v):
    if v >= 1e6: return f"{v/1e6:.1f}M€"
    if v >= 1e3: return f"{v/1e3:.0f}K€"
    return f"{v:.0f}€"

def fmtp(v): return f"{v:+.1f}%"

def sort_months(lst):
    return sorted(set(lst), key=lambda x: pd.to_datetime("01 " + x, format="%d %b-%Y", errors="coerce"))

def kpi(col, label, val, sub=""):
    col.markdown(
        f'<div class="kc"><div class="kl">{label}</div>'
        f'<div class="kv">{val}</div><div class="ks">{sub}</div></div>',
        unsafe_allow_html=True
    )

def section(title):
    st.markdown(f'<div class="sh">{title}</div>', unsafe_allow_html=True)

# ── AUTH ──────────────────────────────────────────────────────────────────────
def login():
    st.markdown("""
    <div style="text-align:center;padding:4rem 0 2rem">
      <div style="font-size:10px;letter-spacing:.4em;color:#0066cc;text-transform:uppercase;margin-bottom:1.5rem;font-weight:700">AbbVie</div>
      <h1 style="font-size:2.4rem;font-weight:700;color:#f1f5f9;margin-bottom:.5rem">SFE Dashboard</h1>
      <p style="color:#64748b;font-size:15px">Territoire FA-99 · Performance Commerciale 2023–2025</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.1, 1])
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        role = st.selectbox("Rôle", ["Sélectionner...", "Admin", "User"])
        pwd  = st.text_input("Mot de passe", type="password")
        if st.button("Connexion", use_container_width=True):
            if role == "Admin" and pwd == ADMIN_PASSWORD:
                st.session_state.role = "admin"; st.rerun()
            elif role == "User" and pwd == USER_PASSWORD:
                st.session_state.role = "user"; st.rerun()
            elif role == "Sélectionner...":
                st.warning("Sélectionne un rôle.")
            else:
                st.error("Mot de passe incorrect.")

# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load(b):
    xl    = pd.read_excel(io.BytesIO(b), sheet_name=None)
    db    = xl.get("DB",    list(xl.values())[0])
    calls = xl.get("Calls", list(xl.values())[1] if len(xl) > 1 else pd.DataFrame())
    db["Month-Year"]   = db["Month-Year"].astype(str)
    db["Quarter-Year"] = db["Quarter-Year"].astype(str)
    db["Year"]         = db["Year"].astype(int)
    if len(calls):
        calls["Call: Created Date"] = pd.to_datetime(calls["Call: Created Date"], errors="coerce")
        calls["Month-Year"]   = calls["Call: Created Date"].dt.strftime("%b-%Y")
        calls["Quarter-Year"] = "Q" + calls["Call: Created Date"].dt.quarter.astype(str) + "-" + calls["Call: Created Date"].dt.year.astype(str)
        calls["Year"]         = calls["Call: Created Date"].dt.year.astype("Int64")
    return db, calls

# ── ADMIN ─────────────────────────────────────────────────────────────────────
def admin_panel():
    with st.sidebar:
        st.markdown('<div style="padding:16px 0 8px"><div style="font-size:16px;font-weight:700;color:#f1f5f9">SFE Dashboard</div><div style="font-size:11px;color:#64748b">Administration</div></div>', unsafe_allow_html=True)
        if "data" in st.session_state:
            if st.button("Voir le dashboard", use_container_width=True):
                st.session_state.view = "dash"; st.rerun()
        if st.button("Déconnexion", use_container_width=True):
            for k in ["role", "data", "view"]: st.session_state.pop(k, None)
            st.rerun()
    st.markdown("## Mise à jour des données")
    up = st.file_uploader("Dépose le fichier Excel Salesforce", type=["xlsx", "xls"])
    if up:
        try:
            db, calls = load(up.read())
            st.session_state.data = (db, calls)
            st.success(f"Chargé — {len(db)} lignes ventes · {len(calls)} calls")
            if st.button("Accéder au dashboard →", use_container_width=True):
                st.session_state.view = "dash"; st.rerun()
        except Exception as e:
            st.error(f"Erreur : {e}")
    elif "data" in st.session_state:
        db, _ = st.session_state.data
        st.info(f"Données actuelles : {len(db)} lignes")
        if st.button("Voir le dashboard →", use_container_width=True):
            st.session_state.view = "dash"; st.rerun()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def sidebar_filters(db, calls):
    with st.sidebar:
        role_lbl = "Admin" if st.session_state.role == "admin" else "User"
        st.markdown(
            f'<div style="padding:12px 0 6px">'
            f'<div style="font-size:15px;font-weight:700;color:#f1f5f9">SFE Dashboard</div>'
            f'<div style="font-size:11px;color:#64748b">FA-99 · {role_lbl}</div></div>',
            unsafe_allow_html=True
        )
        st.markdown("---")
        years    = ["Toutes"] + sorted(db["Year"].unique().tolist(), reverse=True)
        quarters = ["Tous"]   + sorted(db["Quarter-Year"].unique().tolist())
        months   = ["Tous"]   + sort_months(db["Month-Year"].unique().tolist())
        products = ["Tous"]   + sorted(db["Product Group"].unique().tolist())
        packs    = ["Tous"]   + sorted(db["Product Pack"].unique().tolist())
        segs     = ["Tous"]   + sorted(db["Acc Level 2 Segment"].unique().tolist())
        cities   = ["Toutes"] + sorted(db["Ship To - City"].dropna().unique().tolist())

        st.markdown("""
        <div style="background:rgba(0,102,204,0.12);border-left:3px solid #0066cc;
                    border-radius:0 6px 6px 0;padding:8px 10px;margin-bottom:10px">
          <span style="font-size:11px;font-weight:700;color:#60a5fa;
                       text-transform:uppercase;letter-spacing:.1em">📊 Filtres ventes</span>
        </div>""", unsafe_allow_html=True)
        fy  = st.selectbox("Année",       years)
        fq  = st.selectbox("Trimestre",   quarters)
        fm  = st.selectbox("Mois",        months)
        fp  = st.selectbox("Produit",     products)
        fpp = st.selectbox("Déclinaison", packs)
        fs  = st.selectbox("Segment",     segs)
        fc  = st.selectbox("Secteur",     cities)

        # Badge filtres actifs
        actifs = sum([fy!="Toutes", fq!="Tous", fm!="Tous", fp!="Tous", fpp!="Tous", fs!="Tous", fc!="Toutes"])
        if actifs > 0:
            st.markdown(f'<div style="background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.3);border-radius:6px;padding:6px 10px;margin:6px 0;font-size:11px;color:#fbbf24;font-weight:600">⚡ {actifs} filtre(s) actif(s)</div>', unsafe_allow_html=True)

        st.markdown("---")
        if len(calls):
            call_months   = ["Tous"] + sort_months(calls["Month-Year"].dropna().unique().tolist())
            call_statuses = ["Tous"] + sorted(calls["Status"].dropna().unique().tolist())
        else:
            call_months = call_statuses = ["Tous"]

        st.markdown("""
        <div style="background:rgba(34,197,94,0.1);border-left:3px solid #22c55e;
                    border-radius:0 6px 6px 0;padding:8px 10px;margin-bottom:10px">
          <span style="font-size:11px;font-weight:700;color:#4ade80;
                       text-transform:uppercase;letter-spacing:.1em">📞 Filtres activité</span>
        </div>""", unsafe_allow_html=True)
        fcm = st.selectbox("Mois (calls)", call_months)
        fcs = st.selectbox("Statut",       call_statuses)
        st.markdown("---")
        if st.session_state.role == "admin":
            if st.button("Mettre à jour les données", use_container_width=True):
                st.session_state.view = "admin"; st.rerun()
        if st.button("Déconnexion", use_container_width=True):
            for k in ["role", "data", "view"]: st.session_state.pop(k, None)
            st.rerun()
    return fy, fq, fm, fp, fpp, fs, fc, fcm, fcs

def filt_db(db, fy, fq, fm, fp, fpp, fs, fc):
    d = db.copy()
    if fy  != "Toutes": d = d[d["Year"] == int(fy)]
    if fq  != "Tous":   d = d[d["Quarter-Year"] == fq]
    if fm  != "Tous":   d = d[d["Month-Year"] == fm]
    if fp  != "Tous":   d = d[d["Product Group"] == fp]
    if fpp != "Tous":   d = d[d["Product Pack"] == fpp]
    if fs  != "Tous":   d = d[d["Acc Level 2 Segment"] == fs]
    if fc  != "Toutes": d = d[d["Ship To - City"] == fc]
    return d

def filt_calls(calls, fcm, fcs):
    if not len(calls): return calls
    c = calls.copy()
    if fcm != "Tous": c = c[c["Month-Year"] == fcm]
    if fcs != "Tous": c = c[c["Status"] == fcs]
    return c

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — VENTES
# ══════════════════════════════════════════════════════════════════════════════
def tab_ventes(db, dbf):
    total_ca  = dbf["Net Sales"].sum()
    total_qty = int(dbf["Quantity"].sum())
    by_prod   = dbf.groupby("Product Group")["Net Sales"].sum()
    top_prod  = by_prod.idxmax() if len(by_prod) else "—"
    top_prod_v = by_prod.max() if len(by_prod) else 0

    # MoM sur données non filtrées
    all_m = sort_months(db["Month-Year"].unique().tolist())
    mom_pct = None
    if len(all_m) >= 2:
        s_l = db[db["Month-Year"] == all_m[-1]]["Net Sales"].sum()
        s_p = db[db["Month-Year"] == all_m[-2]]["Net Sales"].sum()
        if s_p > 0: mom_pct = (s_l - s_p) / s_p * 100

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "CA Total",        fmtk(total_ca),  f"{len(dbf):,} transactions")
    kpi(c2, "Unités vendues",  f"{total_qty:,}", "Quantité totale")
    kpi(c3, "Top produit",     top_prod,         fmtk(top_prod_v))
    kpi(c4, "Croissance MoM",
        fmtp(mom_pct) if mom_pct is not None else "—",
        f"{all_m[-1]} vs {all_m[-2]}" if len(all_m) >= 2 else "")

    section("Évolution mensuelle des ventes")
    months_o = sort_months(dbf["Month-Year"].unique().tolist())
    prods    = sorted(dbf["Product Group"].unique())

    # G1 — Net Sales par produit
    fig1 = go.Figure()
    for i, p in enumerate(prods):
        sub = dbf[dbf["Product Group"] == p].groupby("Month-Year")["Net Sales"].sum().reindex(months_o).fillna(0)
        fig1.add_trace(go.Scatter(
            x=sub.index, y=sub.values, name=p,
            mode="lines+markers",
            line=dict(color=C5[i % len(C5)], width=2.5),
            marker=dict(size=6),
            fill="tozeroy", fillcolor=FILL5[i % len(FILL5)]
        ))
    fig1.update_layout(title="<b>Net Sales par produit</b>", **pt(280))
    st.plotly_chart(fig1, use_container_width=True)

    # G2 — Quantités par produit
    fig2 = go.Figure()
    for i, p in enumerate(prods):
        sub = dbf[dbf["Product Group"] == p].groupby("Month-Year")["Quantity"].sum().reindex(months_o).fillna(0)
        fig2.add_trace(go.Scatter(
            x=sub.index, y=sub.values, name=p,
            mode="lines+markers",
            line=dict(color=C5[i % len(C5)], width=2.5, dash="dot"),
            marker=dict(size=6),
        ))
    fig2.update_layout(title="<b>Quantités vendues par produit</b>", **pt(240))
    st.plotly_chart(fig2, use_container_width=True)

    section("Répartitions & Classements")
    r1, r2 = st.columns(2)

    with r1:
        seg_d = dbf.groupby("Acc Level 2 Segment")["Net Sales"].sum().reset_index().sort_values("Net Sales", ascending=True)
        fig3 = px.bar(seg_d, x="Net Sales", y="Acc Level 2 Segment", orientation="h",
                      title="<b>Net Sales par segment</b>",
                      color="Net Sales", color_continuous_scale=["#1e3a5f", CL])
        fig3.update_layout(**pt(280, show_legend=False))
        fig3.update_coloraxes(showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    with r2:
        top20 = dbf.groupby("Customer Name")["Net Sales"].sum().nlargest(20).reset_index().sort_values("Net Sales")
        fig4 = px.bar(top20, x="Net Sales", y="Customer Name", orientation="h",
                      title="<b>Top 20 clients — Net Sales</b>",
                      color_discrete_sequence=[CL])
        fig4.update_layout(**pt(280, show_legend=False))
        st.plotly_chart(fig4, use_container_width=True)

    # G5 — Bubble chart quadrants (dernier mois, données non filtrées)
    section(f"Positionnement produits — dernier mois ({all_m[-1] if all_m else ''})")
    if len(all_m) >= 2:
        last_d = db[db["Month-Year"] == all_m[-1]].groupby("Product Group")["Net Sales"].sum()
        prev_d = db[db["Month-Year"] == all_m[-2]].groupby("Product Group")["Net Sales"].sum()
        total_last = last_d.sum()
        bdf = []
        for p in last_d.index:
            s_l = last_d.get(p, 0); s_p = prev_d.get(p, 0)
            evol = (s_l - s_p) / s_p * 100 if s_p > 0 else 0
            part = s_l / total_last * 100 if total_last > 0 else 0
            bdf.append({"Produit": p, "Evol%": round(evol, 1), "Part%": round(part, 1), "Sales": s_l})
        bdf = pd.DataFrame(bdf)
        mean_evol = bdf["Evol%"].mean()
        bdf["EcartMoyenne"] = (bdf["Evol%"] - mean_evol).round(1)

        def quad(r):
            if r["Evol%"] >= 0 and r["EcartMoyenne"] >= 0: return "⭐ Croissance > moyenne"
            if r["Evol%"] <  0 and r["EcartMoyenne"] >= 0: return "📉 Décroissance > moyenne"
            if r["Evol%"] >= 0 and r["EcartMoyenne"] <  0: return "⚠️ Croissance < moyenne"
            return "🔴 Décroissance < moyenne"

        bdf["Quadrant"] = bdf.apply(quad, axis=1)
        cmap = {"⭐ Croissance > moyenne": CG, "📉 Décroissance > moyenne": CA,
                "⚠️ Croissance < moyenne": CL, "🔴 Décroissance < moyenne": CR}

        fig5 = px.scatter(bdf, x="Evol%", y="EcartMoyenne", size="Part%", color="Quadrant",
                          text="Produit", hover_data={"Sales": True, "Part%": True},
                          title=f"<b>Positionnement produits — {all_m[-1]} (taille bulle = part CA)</b>",
                          color_discrete_map=cmap, size_max=70)
        fig5.add_vline(x=0, line_dash="dot", line_color="rgba(255,255,255,0.25)", line_width=1.5)
        fig5.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.25)", line_width=1.5)
        fig5.update_traces(textposition="top center", textfont=dict(color="#fff", size=12, family="Arial Black"))

        x_max = bdf["Evol%"].abs().max() * 0.9
        y_max = bdf["EcartMoyenne"].abs().max() * 0.8

        fig5.update_layout(**pt(400),
            annotations=[
                dict(x= x_max, y= y_max, text="⭐ Croissance forte", showarrow=False, font=dict(color=CG,  size=11), bgcolor="rgba(34,197,94,0.1)",  borderpad=4),
                dict(x=-x_max, y= y_max, text="📉 Résistant",        showarrow=False, font=dict(color=CA,  size=11), bgcolor="rgba(245,158,11,0.1)", borderpad=4),
                dict(x= x_max, y=-y_max, text="⚠️ Sous moyenne",     showarrow=False, font=dict(color=CL,  size=11), bgcolor="rgba(0,102,204,0.1)",  borderpad=4),
                dict(x=-x_max, y=-y_max, text="🔴 En difficulté",    showarrow=False, font=dict(color=CR,  size=11), bgcolor="rgba(244,63,94,0.1)",  borderpad=4),
            ])
        st.plotly_chart(fig5, use_container_width=True)

    # G6 — Par ville
    section("Répartition par secteur géographique")
    city_d = dbf.groupby("Ship To - City")["Net Sales"].sum().nlargest(20).reset_index().sort_values("Net Sales")
    fig6 = px.bar(city_d, x="Net Sales", y="Ship To - City", orientation="h",
                  title="<b>Net Sales par secteur — Top 20 villes</b>",
                  color_discrete_sequence=[CP])
    fig6.update_layout(**pt(360, show_legend=False))
    st.plotly_chart(fig6, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — ACTIVITÉ
# ══════════════════════════════════════════════════════════════════════════════
def tab_activite(db, cf):
    if not len(cf):
        st.info("Aucune donnée d'activité disponible."); return

    nb_calls         = len(cf)
    nb_clients_calls = cf["Customer Name"].nunique()
    nb_clients_db    = db["Customer Name"].nunique()
    couverture       = round(nb_clients_calls / nb_clients_db * 100, 1) if nb_clients_db > 0 else 0

    prods_all = pd.concat([cf["Detailed Products 1"].dropna(),
                            cf["Detailed Products 2"].dropna(),
                            cf["Detailed Products 3"].dropna()])
    top_prod_call = prods_all.value_counts().idxmax() if len(prods_all) else "—"
    dur_known     = cf["Duration"].dropna()

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Calls réalisés",          str(nb_calls),           f"{nb_clients_calls} clients contactés")
    kpi(c2, "Taux de couverture",       f"{couverture}%",        f"{nb_clients_calls}/{nb_clients_db} clients")
    kpi(c3, "Produit le plus présenté", top_prod_call,           "Mentions cumulées")
    kpi(c4, "Durée totale",
        f"{int(dur_known.sum())} min" if len(dur_known) else "N/D",
        f"Moy. {dur_known.mean():.0f} min/call" if len(dur_known) else "Non renseigné")

    section("Évolution mensuelle de l'activité")
    months_c   = sort_months(cf["Month-Year"].dropna().unique().tolist())
    call_types = sorted(cf["Call Type"].dropna().unique())
    cc = [CG, CA, CR, CP, CL]

    fig7 = go.Figure()
    for i, ct in enumerate(call_types):
        sub = cf[cf["Call Type"] == ct].groupby("Month-Year").size().reindex(months_c).fillna(0)
        fig7.add_trace(go.Scatter(
            x=sub.index, y=sub.values, name=ct,
            mode="lines+markers",
            line=dict(color=cc[i % len(cc)], width=2.5),
            marker=dict(size=7)
        ))
    fig7.update_layout(title="<b>Évolution mensuelle des calls par type</b>", **pt(260))
    st.plotly_chart(fig7, use_container_width=True)

    section("Répartitions")
    r1, r2, r3 = st.columns(3)

    with r1:
        ct_d = cf["Call Type"].value_counts().reset_index()
        ct_d.columns = ["Type", "Count"]
        fig_ct = px.pie(ct_d, values="Count", names="Type", hole=0.55,
                        title="<b>Type de call</b>",
                        color_discrete_sequence=[CL, CG, CA])
        fig_ct.update_layout(**PT_BASE, height=260,
                             legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1", size=11)))
        fig_ct.update_traces(textfont=dict(color="white", size=12))
        st.plotly_chart(fig_ct, use_container_width=True)

    with r2:
        seg_calls = cf.merge(db[["Customer Name", "Acc Level 2 Segment"]].drop_duplicates(), on="Customer Name", how="left")
        seg_d     = seg_calls["Acc Level 2 Segment"].fillna("Non segmenté").value_counts().reset_index()
        seg_d.columns = ["Segment", "Count"]
        fig_sg = px.pie(seg_d, values="Count", names="Segment", hole=0.55,
                        title="<b>Calls par segment</b>",
                        color_discrete_sequence=[CB, CL, "#38bdf8", CG, CA, CR, CP, "#94a3b8"])
        fig_sg.update_layout(**PT_BASE, height=260,
                             legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1", size=11)))
        fig_sg.update_traces(textfont=dict(color="white", size=12))
        st.plotly_chart(fig_sg, use_container_width=True)

    with r3:
        st_d = cf["Status"].value_counts().reset_index()
        st_d.columns = ["Status", "Count"]
        fig_st = px.pie(st_d, values="Count", names="Status", hole=0.55,
                        title="<b>Statut des calls</b>",
                        color_discrete_sequence=[CL, CG])
        fig_st.update_layout(**PT_BASE, height=260,
                             legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1", size=11)))
        fig_st.update_traces(textfont=dict(color="white", size=12))
        st.plotly_chart(fig_st, use_container_width=True)

    section("Classements clients & Produits")
    r4, r5 = st.columns(2)

    with r4:
        top20c = cf.groupby("Customer Name").size().nlargest(20).reset_index()
        top20c.columns = ["Client", "Calls"]
        top20c = top20c.sort_values("Calls")
        fig_t20 = px.bar(top20c, x="Calls", y="Client", orientation="h",
                         title="<b>Top 20 clients — Nombre de calls</b>",
                         color_discrete_sequence=[CG])
        fig_t20.update_layout(**pt(360, show_legend=False))
        st.plotly_chart(fig_t20, use_container_width=True)

    with r5:
        prod_d = prods_all.value_counts().reset_index()
        prod_d.columns = ["Produit", "Mentions"]
        prod_d = prod_d.sort_values("Mentions")
        fig_pr = px.bar(prod_d, x="Mentions", y="Produit", orientation="h",
                        title="<b>Produits mentionnés lors des calls</b>",
                        color_discrete_sequence=[CA])
        fig_pr.update_layout(**pt(360, show_legend=False))
        st.plotly_chart(fig_pr, use_container_width=True)

    section("Segmentation Top 20 & Répartition régionale")
    r6, r7 = st.columns(2)

    with r6:
        top20_names = cf.groupby("Customer Name").size().nlargest(20).index
        top20_seg   = seg_calls[seg_calls["Customer Name"].isin(top20_names)]
        seg20_d     = top20_seg["Acc Level 2 Segment"].fillna("Non segmenté").value_counts().reset_index()
        seg20_d.columns = ["Segment", "Count"]
        fig_s20 = px.bar(seg20_d, x="Segment", y="Count",
                         title="<b>Segmentation des Top 20 clients (par calls)</b>",
                         color="Segment",
                         color_discrete_sequence=[CB, CL, "#38bdf8", CG, CA, CR, CP, "#94a3b8"])
        fig_s20.update_layout(**pt(260, show_legend=False))
        st.plotly_chart(fig_s20, use_container_width=True)

    with r7:
        region_calls = cf.merge(db[["Customer Name", "Ship To - City"]].drop_duplicates(), on="Customer Name", how="left")
        reg_d        = region_calls["Ship To - City"].value_counts().nlargest(15).reset_index()
        reg_d.columns = ["Ville", "Calls"]
        reg_d = reg_d.sort_values("Calls")
        fig_rg = px.bar(reg_d, x="Calls", y="Ville", orientation="h",
                        title="<b>Répartition calls par région — Top 15</b>",
                        color_discrete_sequence=[CP])
        fig_rg.update_layout(**pt(260, show_legend=False))
        st.plotly_chart(fig_rg, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — CORRÉLATION
# ══════════════════════════════════════════════════════════════════════════════
def tab_correlation(dbf, cf):
    if not len(cf):
        st.info("Aucune donnée d'activité disponible."); return

    sales_c = dbf.groupby("Customer Name")["Net Sales"].sum()
    calls_c = cf.groupby("Customer Name").size()
    common  = sorted(set(sales_c.index) & set(calls_c.index))

    if not common:
        st.info("Aucun client commun entre les deux sources de données."); return

    cdf = pd.DataFrame({
        "Client":    common,
        "Calls":     [int(calls_c[c]) for c in common],
        "Net Sales": [float(sales_c[c]) for c in common]
    })
    cdf["ROI"] = (cdf["Net Sales"] / cdf["Calls"]).round(0)

    roi_global = dbf["Net Sales"].sum() / len(cf) if len(cf) > 0 else 0

    # ROI par segment
    seg_joined  = cf.merge(dbf[["Customer Name", "Acc Level 2 Segment", "Net Sales"]].drop_duplicates("Customer Name"),
                            on="Customer Name", how="left")
    seg_r = seg_joined.groupby("Acc Level 2 Segment").agg(sales=("Net Sales","sum"), calls=("Customer Name","count")).reset_index()
    seg_r["roi"] = (seg_r["sales"] / seg_r["calls"]).round(0)
    best_seg = seg_r.nlargest(1, "roi").iloc[0] if len(seg_r) else None

    # ROI par type de call
    type_r = cf.copy()
    type_r = type_r.merge(dbf[["Customer Name","Net Sales"]].groupby("Customer Name").sum().reset_index(), on="Customer Name", how="left")
    type_rx = type_r.groupby("Call Type").agg(calls=("Customer Name","count"), sales=("Net Sales","sum")).reset_index()
    type_rx["roi"] = (type_rx["sales"] / type_rx["calls"]).round(0)
    best_type = type_rx.nlargest(1, "roi").iloc[0] if len(type_rx) else None

    corr_val = round(float(np.corrcoef(cdf["Calls"], cdf["Net Sales"])[0, 1]), 2) if len(cdf) > 2 else None

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "ROI global",             fmtk(roi_global), "Net Sales / Call")
    kpi(c2, "Meilleur segment",
        best_seg["Acc Level 2 Segment"] if best_seg is not None else "—",
        fmtk(best_seg["roi"]) if best_seg is not None else "")
    kpi(c3, "Meilleur type call",
        best_type["Call Type"] if best_type is not None else "—",
        fmtk(best_type["roi"]) if best_type is not None else "")
    kpi(c4, "Corrélation calls×ventes",
        f"r = {corr_val}" if corr_val is not None else "—",
        "Forte" if corr_val and abs(corr_val) > 0.6 else
        "Modérée" if corr_val and abs(corr_val) > 0.3 else "Faible")
    kpi(c5, "Clients analysés", str(len(common)),
        f"{len(cdf[cdf['ROI'] > roi_global])} au-dessus ROI moyen")

    # G1 — Histogramme double axe par segment (utilise pt_dual, PAS **PT)
    section("Impact de la pression de visite sur les ventes")
    segs_available = sorted(dbf["Acc Level 2 Segment"].unique())
    seg_sel = st.selectbox("Sélectionner le segment", segs_available)

    all_m_db = sort_months(dbf["Month-Year"].unique().tolist())
    if len(all_m_db) >= 2:
        last_m = all_m_db[-1]; prev_m = all_m_db[-2]
        seg_clients      = dbf[dbf["Acc Level 2 Segment"] == seg_sel]["Customer Name"].unique()
        seg_calls_clients = cf[cf["Customer Name"].isin(seg_clients)]

        last_s = dbf[(dbf["Acc Level 2 Segment"] == seg_sel) & (dbf["Month-Year"] == last_m)].groupby("Customer Name")["Net Sales"].sum()
        prev_s = dbf[(dbf["Acc Level 2 Segment"] == seg_sel) & (dbf["Month-Year"] == prev_m)].groupby("Customer Name")["Net Sales"].sum()
        calls_by_c = seg_calls_clients.groupby("Customer Name").size()

        hist_data = []
        for c in sorted(set(last_s.index) | set(prev_s.index)):
            s_l = last_s.get(c, 0); s_p = prev_s.get(c, 0)
            evol = (s_l - s_p) / s_p * 100 if s_p > 0 else 0
            hist_data.append({"Client": c, "Calls": int(calls_by_c.get(c, 0)), "Evol%": round(evol, 1)})
        hdf = pd.DataFrame(hist_data)

        if len(hdf):
            fig_h = go.Figure()
            fig_h.add_trace(go.Bar(
                x=hdf["Client"], y=hdf["Calls"], name="Nb Calls",
                yaxis="y1", marker_color=CG, opacity=0.9
            ))
            fig_h.add_trace(go.Bar(
                x=hdf["Client"], y=hdf["Evol%"], name="Évolution CA %",
                yaxis="y2", marker_color=CP, opacity=0.9
            ))
            # Utilise pt_dual() qui ne contient PAS de clé yaxis en doublon
            fig_h.update_layout(
                title=f"<b>Segment {seg_sel} — Impact de la pression de visite sur les ventes</b>",
                **pt_dual(380)
            )
            st.plotly_chart(fig_h, use_container_width=True)
    else:
        st.info("Pas assez de mois pour calculer l'évolution.")

    # G2 — Scatter
    section("Corrélation Calls × Ventes par client")
    med_s = cdf["Net Sales"].median(); med_c = cdf["Calls"].median()

    def classify(row):
        if row["Calls"] >= med_c and row["Net Sales"] < med_s:  return "Fort potentiel"
        if row["Calls"] <= med_c and row["Net Sales"] >= med_s: return "Top performer"
        return "Standard"

    cdf["Profil"] = cdf.apply(classify, axis=1)
    cmap = {"Fort potentiel": CA, "Top performer": CG, "Standard": "#60a5fa"}

    r1, r2 = st.columns([1.3, 1])
    with r1:
        fig_sc = px.scatter(
            cdf, x="Calls", y="Net Sales", color="Profil",
            hover_name="Client", hover_data={"ROI": True},
            color_discrete_map=cmap,
            title="<b>Scatter — Calls vs Net Sales par client</b>"
        )
        fig_sc.update_traces(marker=dict(size=11, opacity=0.85))
        fig_sc.update_layout(**pt(360))
        st.plotly_chart(fig_sc, use_container_width=True)

    with r2:
        st.markdown("<br>", unsafe_allow_html=True)
        pot = cdf[cdf["Profil"] == "Fort potentiel"].nlargest(5, "Calls")
        per = cdf[cdf["Profil"] == "Top performer"].nlargest(5, "Net Sales")

        if len(pot):
            items = "".join([
                f'<div style="font-size:12px;color:#e2e8f0;padding:5px 0;'
                f'border-bottom:1px solid rgba(255,255,255,0.06)">'
                f'{row["Client"]}<span style="float:right;color:#fbbf24;font-weight:600">'
                f'{row["Calls"]} calls · {fmtk(row["Net Sales"])}</span></div>'
                for _, row in pot.iterrows()
            ])
            st.markdown(
                f'<div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);'
                f'border-radius:8px;padding:14px;margin-bottom:12px;overflow:hidden">'
                f'<div style="font-size:11px;font-weight:700;color:{CA};margin-bottom:10px;'
                f'text-transform:uppercase;letter-spacing:.06em;white-space:nowrap;'
                f'overflow:hidden;text-overflow:ellipsis">⚡ Fort potentiel</div>'
                f'<div style="font-size:11px;color:#94a3b8;margin-bottom:8px">Calls élevés · Ventes faibles</div>'
                f'{items}</div>',
                unsafe_allow_html=True
            )

        if len(per):
            items = "".join([
                f'<div style="font-size:12px;color:#e2e8f0;padding:5px 0;'
                f'border-bottom:1px solid rgba(255,255,255,0.06)">'
                f'{row["Client"]}<span style="float:right;color:#4ade80;font-weight:600">'
                f'{fmtk(row["Net Sales"])} · {row["Calls"]} calls</span></div>'
                for _, row in per.iterrows()
            ])
            st.markdown(
                f'<div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.25);'
                f'border-radius:8px;padding:14px;overflow:hidden">'
                f'<div style="font-size:11px;font-weight:700;color:{CG};margin-bottom:10px;'
                f'text-transform:uppercase;letter-spacing:.06em;white-space:nowrap;'
                f'overflow:hidden;text-overflow:ellipsis">🏆 Top performers</div>'
                f'<div style="font-size:11px;color:#94a3b8;margin-bottom:8px">Ventes élevées · Calls modérés</div>'
                f'{items}</div>',
                unsafe_allow_html=True
            )

    # G3 — Tableau corrélation
    section("Tableau de corrélation complet")
    disp = cdf.sort_values("Net Sales", ascending=False).reset_index(drop=True).copy()
    disp_export = disp.copy()
    disp["Net Sales"] = disp["Net Sales"].apply(lambda x: f"{x/1000:.1f}K€")
    disp["ROI"]       = disp["ROI"].apply(lambda x: f"{x:.0f}€")
    disp = disp.rename(columns={"ROI": "ROI / Call"})

    ce1, ce2 = st.columns([3, 1])
    with ce2:
        csv = disp_export.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Exporter CSV", csv, "correlation_sfe.csv", "text/csv", use_container_width=True)
    st.dataframe(disp, use_container_width=True, hide_index=True)

    # G4 — Matrice ROI heatmap
    section("Matrice ROI — Segment × Type de call")
    mx_df = cf.merge(
        dbf[["Customer Name", "Acc Level 2 Segment", "Net Sales"]],
        on="Customer Name", how="left"
    )
    if "Call Type" in mx_df.columns and "Acc Level 2 Segment" in mx_df.columns:
        calls_mx = mx_df.groupby(["Acc Level 2 Segment", "Call Type"]).size().reset_index(name="Calls")
        sales_mx = mx_df.groupby(["Acc Level 2 Segment", "Call Type"])["Net Sales"].sum().reset_index()
        mx = calls_mx.merge(sales_mx, on=["Acc Level 2 Segment", "Call Type"])
        mx["ROI"] = (mx["Net Sales"] / mx["Calls"]).round(0)
        pivot = mx.pivot(index="Acc Level 2 Segment", columns="Call Type", values="ROI").fillna(0)

        fig_hm = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=list(pivot.index),
            colorscale=[[0, CR], [0.5, CA], [1, CG]],
            text=[[f"{int(v)}€" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            textfont=dict(color="white", size=13)
        ))
        fig_hm.update_layout(
            title="<b>ROI Net Sales / Call par Segment × Type de call</b>",
            **PT_BASE, height=320,
            xaxis=dict(color="#94a3b8", tickfont=dict(size=12, color="#e2e8f0")),
            yaxis=dict(color="#94a3b8", tickfont=dict(size=12, color="#e2e8f0"))
        )
        st.plotly_chart(fig_hm, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    if "role" not in st.session_state:
        login(); return

    if "view" not in st.session_state:
        st.session_state.view = "admin" if st.session_state.role == "admin" else "dash"

    if "data" not in st.session_state or st.session_state.view == "admin":
        admin_panel(); return

    db, calls = st.session_state.data
    fy, fq, fm, fp, fpp, fs, fc, fcm, fcs = sidebar_filters(db, calls)
    dbf = filt_db(db, fy, fq, fm, fp, fpp, fs, fc)
    cf  = filt_calls(calls, fcm, fcs)

    period = fy if fy != "Toutes" else "2023–2025"
    st.markdown(
        f'<h1 style="font-size:1.6rem;font-weight:700;color:#f1f5f9;margin-bottom:2px">SFE Dashboard — AbbVie</h1>'
        f'<p style="color:#64748b;font-size:13px;margin-bottom:18px">Territoire FA-99 · Performance Commerciale · {period}</p>',
        unsafe_allow_html=True
    )

    t1, t2, t3 = st.tabs([
        "📈   Analyse des ventes",
        "📞   Analyse de l'activité",
        "🔗   Corrélation Calls × Ventes"
    ])

    with t1: tab_ventes(db, dbf)
    with t2: tab_activite(db, cf)
    with t3: tab_correlation(dbf, cf)

if __name__ == "__main__":
    main()
