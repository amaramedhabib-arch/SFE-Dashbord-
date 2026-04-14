import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# ============================================================
#  CONFIG
# ============================================================
st.set_page_config(
    page_title="SFE Dashboard — AbbVie",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

ADMIN_PASSWORD = "admin2025"
USER_PASSWORD  = "team2025"

ABBVIE_BLUE  = "#003087"
ABBVIE_LIGHT = "#0066cc"
GREEN  = "#10b981"
AMBER  = "#f59e0b"
RED    = "#ef4444"

# ============================================================
#  CSS
# ============================================================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0a0e1a; }
[data-testid="stSidebar"] { background: #0d1221; border-right: 1px solid rgba(255,255,255,0.07); }
[data-testid="stSidebar"] * { color: #e8eaf0 !important; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
h1, h2, h3 { color: #f0f0f5 !important; }
p, label, div { color: #d1d5db; }
.metric-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 20px;
    border-top: 2px solid #003087;
}
.metric-label { font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 6px; }
.metric-value { font-size: 28px; font-weight: 700; color: #fff; }
.metric-sub { font-size: 12px; color: #9ca3af; margin-top: 4px; }
.section-header {
    font-size: 12px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .1em; color: #6b7280;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding-bottom: 8px; margin-bottom: 16px; margin-top: 8px;
}
.tag-potential { background: rgba(245,158,11,0.15); color: #f59e0b; padding: 2px 8px; border-radius: 8px; font-size: 11px; font-weight: 600; }
.tag-performer { background: rgba(16,185,129,0.15); color: #10b981; padding: 2px 8px; border-radius: 8px; font-size: 11px; font-weight: 600; }
[data-testid="stSelectbox"] > div { background: #151b2e !important; border-color: rgba(255,255,255,0.1) !important; }
div[data-testid="stFileUploader"] { background: #111827; border-radius: 12px; border: 1px dashed rgba(0,48,135,0.4); padding: 1rem; }
</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#9ca3af', size=11),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#6b7280'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', color='#6b7280'),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#9ca3af')),
    margin=dict(l=10, r=10, t=30, b=10)
)

# ============================================================
#  AUTH
# ============================================================
def login_screen():
    st.markdown("""
    <div style="text-align:center;padding:3rem 0 1rem">
      <div style="font-size:11px;letter-spacing:.3em;color:#003087;text-transform:uppercase;margin-bottom:1rem">AbbVie</div>
      <h1 style="font-size:2.2rem;font-weight:700;color:#fff;margin-bottom:.5rem">SFE Dashboard</h1>
      <p style="color:#6b7280;font-size:14px">Territoire FA-99 · Analyse Calls × Ventes</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1.2,1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        role = st.selectbox("Rôle", ["Sélectionner...", "Admin", "User"])
        pwd  = st.text_input("Mot de passe", type="password")
        if st.button("Connexion", use_container_width=True):
            if role == "Admin" and pwd == ADMIN_PASSWORD:
                st.session_state.role = "admin"
                st.rerun()
            elif role == "User" and pwd == USER_PASSWORD:
                st.session_state.role = "user"
                st.rerun()
            elif role == "Sélectionner...":
                st.warning("Sélectionne un rôle.")
            else:
                st.error("Mot de passe incorrect.")

# ============================================================
#  LOAD DATA
# ============================================================
@st.cache_data
def load_excel(file_bytes):
    xl = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
    db = xl.get('DB', xl[list(xl.keys())[0]])
    calls = xl.get('Calls', xl[list(xl.keys())[1]] if len(xl) > 1 else None)

    db['Month-Year'] = db['Month-Year'].astype(str)
    db['Quarter-Year'] = db['Quarter-Year'].astype(str)
    db['Year'] = db['Year'].astype(int)

    if calls is not None:
        calls['Call: Created Date'] = pd.to_datetime(calls['Call: Created Date'], errors='coerce')
        calls['Month-Year'] = calls['Call: Created Date'].dt.strftime('%b-%Y')
        calls['Quarter-Year'] = 'Q' + calls['Call: Created Date'].dt.quarter.astype(str) + '-' + calls['Call: Created Date'].dt.year.astype(str)
        calls['Year'] = calls['Call: Created Date'].dt.year.astype('Int64')

    return db, calls

def get_data():
    if 'data' in st.session_state:
        return st.session_state.data
    return None, None

# ============================================================
#  SIDEBAR
# ============================================================
def sidebar(db, calls):
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 8px">
          <div style="font-size:10px;letter-spacing:.2em;color:#003087;text-transform:uppercase">AbbVie · FA-99</div>
          <div style="font-size:16px;font-weight:700;color:#fff;margin-top:4px">SFE Dashboard</div>
          <div style="font-size:11px;color:#6b7280;margin-top:2px">Connecté : {'Admin' if st.session_state.role=='admin' else 'User'}</div>
        </div>
        <hr style="border-color:rgba(255,255,255,0.06);margin:12px 0">
        """, unsafe_allow_html=True)

        st.markdown("**Filtres**")
        years = ["Toutes"] + sorted(db['Year'].unique().tolist(), reverse=True)
        year = st.selectbox("Année", years)

        quarters = ["Tous"] + sorted(db['Quarter-Year'].unique().tolist())
        quarter = st.selectbox("Trimestre", quarters)

        products = ["Tous"] + sorted(db['Product Group'].unique().tolist())
        product = st.selectbox("Produit", products)

        segs = ["Tous"] + sorted(db['Acc Level 2 Segment'].unique().tolist())
        seg = st.selectbox("Segment", segs)

        st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:12px 0'>", unsafe_allow_html=True)
        if st.button("Déconnexion", use_container_width=True):
            for k in ['role','data']: st.session_state.pop(k, None)
            st.rerun()

    return year, quarter, product, seg

# ============================================================
#  FILTER
# ============================================================
def apply_filters(db, calls, year, quarter, product, seg):
    dbf = db.copy()
    if year != "Toutes": dbf = dbf[dbf['Year'] == int(year)]
    if quarter != "Tous": dbf = dbf[dbf['Quarter-Year'] == quarter]
    if product != "Tous": dbf = dbf[dbf['Product Group'] == product]
    if seg != "Tous": dbf = dbf[dbf['Acc Level 2 Segment'] == seg]

    cf = calls.copy() if calls is not None else pd.DataFrame()
    if len(cf) > 0:
        if year != "Toutes": cf = cf[cf['Year'] == int(year)]
        if quarter != "Tous": cf = cf[cf['Quarter-Year'] == quarter]

    return dbf, cf

# ============================================================
#  KPIs
# ============================================================
def render_kpis(dbf, cf):
    total_sales = dbf['Net Sales'].sum()
    total_calls = len(cf)
    roi = total_sales / total_calls if total_calls > 0 else 0
    top_prod = dbf.groupby('Product Group')['Net Sales'].sum().idxmax() if len(dbf) > 0 else "—"
    top_prod_sales = dbf.groupby('Product Group')['Net Sales'].sum().max() if len(dbf) > 0 else 0

    def fmt(v):
        if v >= 1_000_000: return f"{v/1_000_000:.1f}M€"
        if v >= 1_000: return f"{v/1_000:.0f}K€"
        return f"{v:.0f}€"

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub in [
        (c1, "Net Sales total", fmt(total_sales), f"{len(dbf)} transactions"),
        (c2, "Calls réalisés", str(total_calls), f"{cf['Customer Name'].nunique() if len(cf)>0 else 0} clients contactés"),
        (c3, "ROI par call", fmt(roi), "Net Sales / Call"),
        (c4, "Top produit", top_prod, fmt(top_prod_sales))
    ]:
        col.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{val}</div>
          <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

# ============================================================
#  CHARTS
# ============================================================
def render_sales(dbf):
    st.markdown('<div class="section-header">Analyse des ventes</div>', unsafe_allow_html=True)

    # Monthly sales by product
    months_order = sorted(dbf['Month-Year'].unique(), key=lambda x: pd.to_datetime(x, format='%b-%Y', errors='coerce'))
    monthly = dbf.groupby(['Month-Year','Product Group'])['Net Sales'].sum().reset_index()
    colors = [ABBVIE_BLUE, ABBVIE_LIGHT, '#4db8ff', '#10b981', '#f59e0b']
    fig1 = go.Figure()
    for i, prod in enumerate(sorted(dbf['Product Group'].unique())):
        sub = monthly[monthly['Product Group']==prod]
        sub = sub.set_index('Month-Year').reindex(months_order).fillna(0).reset_index()
        fig1.add_trace(go.Scatter(
            x=sub['Month-Year'], y=sub['Net Sales'], name=prod,
            mode='lines+markers', line=dict(color=colors[i%len(colors)], width=2),
            fill='tozeroy', fillcolor=colors[i%len(colors)].replace('#','rgba(').replace(')',',0.05)') if len(colors[i%len(colors)]) > 4 else 'rgba(0,48,135,0.05)'
        ))
    fig1.update_layout(title="Évolution mensuelle — Net Sales par produit", **PLOTLY_THEME, height=280)
    st.plotly_chart(fig1, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        seg_data = dbf.groupby('Acc Level 2 Segment')['Net Sales'].sum().reset_index().sort_values('Net Sales', ascending=True)
        fig2 = px.bar(seg_data, x='Net Sales', y='Acc Level 2 Segment', orientation='h',
                      color='Net Sales', color_continuous_scale=['#001a4d','#0066cc'],
                      title="Ventes par segment (Acc Level 2)")
        fig2.update_layout(**PLOTLY_THEME, height=260, showlegend=False)
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        top_c = dbf.groupby('Customer Name')['Net Sales'].sum().nlargest(10).reset_index().sort_values('Net Sales')
        fig3 = px.bar(top_c, x='Net Sales', y='Customer Name', orientation='h',
                      title="Top 10 clients — Net Sales",
                      color_discrete_sequence=[ABBVIE_LIGHT])
        fig3.update_layout(**PLOTLY_THEME, height=260, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

def render_calls(cf):
    st.markdown('<div class="section-header">Analyse des calls</div>', unsafe_allow_html=True)
    if len(cf) == 0:
        st.info("Aucun call dans la période sélectionnée.")
        return

    c1, c2 = st.columns([2,1])
    with c1:
        months_order = sorted(cf['Month-Year'].dropna().unique(), key=lambda x: pd.to_datetime(x, format='%b-%Y', errors='coerce'))
        monthly_c = cf.groupby(['Month-Year','Call Type']).size().reset_index(name='Calls')
        colors_c = [GREEN, AMBER, RED, '#8b5cf6']
        fig4 = go.Figure()
        for i, ct in enumerate(cf['Call Type'].dropna().unique()):
            sub = monthly_c[monthly_c['Call Type']==ct].set_index('Month-Year').reindex(months_order).fillna(0).reset_index()
            fig4.add_trace(go.Scatter(
                x=sub['Month-Year'], y=sub['Calls'], name=ct,
                mode='lines+markers', line=dict(color=colors_c[i%len(colors_c)], width=2)
            ))
        fig4.update_layout(title="Évolution mensuelle — Calls par type", **PLOTLY_THEME, height=250)
        st.plotly_chart(fig4, use_container_width=True)

    with c2:
        status_d = cf['Status'].value_counts().reset_index()
        status_d.columns = ['Status','Count']
        fig5 = px.pie(status_d, values='Count', names='Status', title="Répartition par statut",
                      color_discrete_sequence=[ABBVIE_BLUE, GREEN, AMBER])
        fig5.update_layout(**PLOTLY_THEME, height=250)
        fig5.update_traces(textfont_color='white')
        st.plotly_chart(fig5, use_container_width=True)

    top_cc = cf.groupby('Customer Name').size().nlargest(20).reset_index(name='Calls').sort_values('Calls')
    fig6 = px.bar(top_cc, x='Calls', y='Customer Name', orientation='h',
                  title="Fréquence calls par client (Top 20)",
                  color_discrete_sequence=[GREEN])
    fig6.update_layout(**PLOTLY_THEME, height=300, showlegend=False)
    st.plotly_chart(fig6, use_container_width=True)

def render_correlation(dbf, cf):
    st.markdown('<div class="section-header">Corrélation Calls × Ventes</div>', unsafe_allow_html=True)
    if len(cf) == 0:
        st.info("Pas de données calls pour la corrélation.")
        return

    sales_by_c = dbf.groupby('Customer Name')['Net Sales'].sum()
    calls_by_c = cf.groupby('Customer Name').size()
    common = set(sales_by_c.index) & set(calls_by_c.index)

    if not common:
        st.info("Aucun client commun entre les deux datasets pour la période sélectionnée.")
        return

    corr_df = pd.DataFrame({
        'Client': list(common),
        'Calls': [int(calls_by_c[c]) for c in common],
        'Net Sales': [round(float(sales_by_c[c]),2) for c in common]
    })
    corr_df['ROI / Call'] = (corr_df['Net Sales'] / corr_df['Calls']).round(0)

    med_sales = corr_df['Net Sales'].median()
    med_calls = corr_df['Calls'].median()

    def classify(row):
        if row['Calls'] >= med_calls and row['Net Sales'] < med_sales: return '⚡ Fort potentiel'
        if row['Calls'] <= med_calls and row['Net Sales'] >= med_sales: return '🏆 Performer'
        return '—'

    corr_df['Profil'] = corr_df.apply(classify, axis=1)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        color_map = {'⚡ Fort potentiel': AMBER, '🏆 Performer': GREEN, '—': '#60a5fa'}
        fig7 = px.scatter(corr_df, x='Calls', y='Net Sales', color='Profil',
                          hover_name='Client', hover_data={'ROI / Call': True},
                          title="Scatter — Calls vs Net Sales par client",
                          color_discrete_map=color_map)
        fig7.update_traces(marker=dict(size=10, opacity=0.85))
        fig7.update_layout(**PLOTLY_THEME, height=320)
        st.plotly_chart(fig7, use_container_width=True)

    with c2:
        st.markdown("**Insights automatiques**")
        pot = corr_df[corr_df['Profil']=='⚡ Fort potentiel'].nlargest(5,'Calls')[['Client','Calls','Net Sales']]
        per = corr_df[corr_df['Profil']=='🏆 Performer'].nlargest(5,'Net Sales')[['Client','Calls','Net Sales']]

        if len(pot) > 0:
            st.markdown('<div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);border-radius:8px;padding:12px;margin-bottom:10px">', unsafe_allow_html=True)
            st.markdown('<span class="tag-potential">⚡ Fort potentiel — beaucoup de calls, peu de ventes</span>', unsafe_allow_html=True)
            for _, r in pot.iterrows():
                st.markdown(f'<div style="font-size:12px;padding:4px 0;color:#d1d5db">{r["Client"]} — {r["Calls"]} calls · {r["Net Sales"]/1000:.0f}K€</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if len(per) > 0:
            st.markdown('<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:8px;padding:12px">', unsafe_allow_html=True)
            st.markdown('<span class="tag-performer">🏆 Performers — ventes élevées, calls modérés</span>', unsafe_allow_html=True)
            for _, r in per.iterrows():
                st.markdown(f'<div style="font-size:12px;padding:4px 0;color:#d1d5db">{r["Client"]} — {r["Net Sales"]/1000:.0f}K€ · {r["Calls"]} calls</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("**Tableau de corrélation complet**")
    display_df = corr_df.sort_values('Net Sales', ascending=False).reset_index(drop=True)
    display_df['Net Sales'] = display_df['Net Sales'].apply(lambda x: f"{x/1000:.1f}K€")
    display_df['ROI / Call'] = display_df['ROI / Call'].apply(lambda x: f"{x:.0f}€")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ============================================================
#  ADMIN PANEL
# ============================================================
def admin_panel():
    st.markdown("## Panneau Admin — Mise à jour des données")
    st.markdown("---")

    uploaded = st.file_uploader(
        "Dépose ton fichier Excel Salesforce ici",
        type=['xlsx','xls'],
        help="Le fichier doit contenir les feuilles 'DB' (ventes) et 'Calls' (activité terrain)"
    )

    if uploaded:
        try:
            db, calls = load_excel(uploaded.read())
            st.session_state.data = (db, calls)
            st.success(f"Données chargées — {len(db)} lignes ventes · {len(calls) if calls is not None else 0} calls")
            st.markdown(f"""
            | Feuille | Lignes | Colonnes |
            |---|---|---|
            | DB (ventes) | {len(db)} | {len(db.columns)} |
            | Calls | {len(calls) if calls is not None else 0} | {len(calls.columns) if calls is not None else 0} |
            """)
            if st.button("Aller au dashboard →", use_container_width=True):
                st.session_state.view = 'dashboard'
                st.rerun()
        except Exception as e:
            st.error(f"Erreur lors du chargement : {e}")
    else:
        db, calls = get_data()
        if db is not None:
            st.info(f"Données actuelles : {len(db)} lignes ventes · {len(calls) if calls is not None else 0} calls")
            if st.button("Voir le dashboard avec les données actuelles →", use_container_width=True):
                st.session_state.view = 'dashboard'
                st.rerun()
        else:
            st.warning("Aucune donnée chargée. Dépose ton fichier Excel pour commencer.")

# ============================================================
#  MAIN
# ============================================================
def main():
    if 'role' not in st.session_state:
        login_screen()
        return

    if 'view' not in st.session_state:
        st.session_state.view = 'admin' if st.session_state.role == 'admin' else 'dashboard'

    db, calls = get_data()

    # Admin → upload d'abord si pas de data
    if st.session_state.role == 'admin' and (db is None or st.session_state.view == 'admin'):
        with st.sidebar:
            st.markdown('<div style="padding:16px 0 8px"><div style="font-size:16px;font-weight:700;color:#fff">SFE Dashboard</div><div style="font-size:11px;color:#6b7280">Admin</div></div>', unsafe_allow_html=True)
            if db is not None:
                if st.button("Dashboard", use_container_width=True):
                    st.session_state.view = 'dashboard'
                    st.rerun()
            if st.button("Déconnexion", use_container_width=True):
                for k in ['role','data','view']: st.session_state.pop(k, None)
                st.rerun()
        admin_panel()
        return

    if db is None:
        st.error("Aucune donnée disponible. Contacte l'admin pour charger les données.")
        if st.button("Déconnexion"):
            for k in ['role','data','view']: st.session_state.pop(k, None)
            st.rerun()
        return

    # Dashboard
    year, quarter, product, seg = sidebar(db, calls if calls is not None else pd.DataFrame())
    dbf, cf = apply_filters(db, calls if calls is not None else pd.DataFrame(), year, quarter, product, seg)

    # Header
    col_h1, col_h2 = st.columns([3,1])
    with col_h1:
        st.markdown(f'<h1 style="font-size:1.6rem;font-weight:700;color:#fff;margin-bottom:4px">SFE Analytics — AbbVie</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#6b7280;font-size:13px">Territoire FA-99 · Corrélation Calls × Ventes · {year if year!="Toutes" else "2023–2025"}</p>', unsafe_allow_html=True)
    with col_h2:
        if st.session_state.role == 'admin':
            if st.button("Mettre à jour les données", use_container_width=True):
                st.session_state.view = 'admin'
                st.rerun()

    st.markdown("---")
    render_kpis(dbf, cf)
    st.markdown("<br>", unsafe_allow_html=True)
    render_sales(dbf)
    st.markdown("<br>", unsafe_allow_html=True)
    render_calls(cf)
    st.markdown("<br>", unsafe_allow_html=True)
    render_correlation(dbf, cf)

if __name__ == '__main__':
    main()
