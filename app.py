import streamlit as st
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="Job Dashboard", layout="wide")

# CSS dashboard
st.markdown("""
<style>

.stApp {
background-color:#0B1F33;
color:white;
}

[data-testid="stSidebar"]{
background-color:#081521;
}

label {
color:white !important;
font-size:16px !important;
font-weight:bold;
}

/* bouton actualiser */
div.stButton > button {
background-color:#1f4e79;
color:white;
border-radius:8px;
font-weight:bold;
border:none;
padding:10px 20px;
}

</style>
""", unsafe_allow_html=True)

# charger données
df = pd.read_csv("data.csv")

# nettoyage ville
df["ville"] = df["ville"].astype(str)
df["ville"] = df["ville"].str.split(",").str[0].str.strip()

# corriger pays
def fix_city(v):
    v=v.lower()
    if "côte" in v:
        return "Abidjan"
    if "benin" in v or "bénin" in v:
        return "Cotonou"
    return v.capitalize()

df["ville"]=df["ville"].apply(fix_city)

# SIDEBAR FILTRES
st.sidebar.markdown("<h2 style='color:white;'>🔎 FILTRES</h2>", unsafe_allow_html=True)

ville = st.sidebar.multiselect(
    "Choisir la ville :",
    df["ville"].unique(),
    default=df["ville"].unique()
)

df = df[df["ville"].isin(ville)]

# TITRE ENCADRÉ
st.markdown("""
<div style="
background:#12263A;
padding:25px;
border-radius:10px;
text-align:center;
margin-bottom:20px;
">
<h1 style="color:white;">Dashboard des Offres d'Emploi en Côte d'Ivoire</h1>
<p style="color:#bcd0e5;">
Analyse du marché de l'emploi basée sur les offres collectées
</p>
</div>
""", unsafe_allow_html=True)

# BOUTON ACTUALISER
if st.button("🔄 Actualiser les données"):
    st.rerun()

# KPI animés
c1,c2,c3,c4 = st.columns(4)

def animated_kpi(title, value):

    placeholder = st.empty()

    for i in range(value+1):

        placeholder.markdown(f"""
        <div style="
        background:#12263A;
        padding:25px;
        border-radius:12px;
        text-align:center;
        box-shadow:0px 6px 20px rgba(0,0,0,0.6);
        ">
        <h3 style="color:white;">{title}</h3>
        <h1 style="color:#4ea8ff;">{i}</h1>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(0.02)

with c1:
    animated_kpi("Total Offres", len(df))

with c2:
    animated_kpi("Entreprises", df["entreprise"].nunique())

with c3:
    animated_kpi("Postes", df["poste"].nunique())

with c4:
    animated_kpi("Villes", df["ville"].nunique())

# GRAPHIQUES
g1,g2,g3 = st.columns(3)

with g1:
    st.subheader("Offres par ville")
    st.line_chart(df["ville"].value_counts())

with g2:
    st.subheader("Top entreprises")
    st.bar_chart(df["entreprise"].value_counts().head(10))

with g3:
    st.subheader("Répartition des villes")
    st.bar_chart(df["ville"].value_counts())

# CAMEMBERT
st.subheader("Camembert des villes")

fig = px.pie(
    df,
    names="ville",
    title="Répartition des offres par ville"
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# CARTE INTERACTIVE
# =============================

st.subheader("Carte des offres d'emploi")

coords = {
    "Abidjan": {"lat": 5.359952, "lon": -4.008256},
    "Cotonou": {"lat": 6.370293, "lon": 2.391236},
    "Bouafle": {"lat": 6.991944, "lon": -5.744722}
}

map_data = df.groupby("ville").size().reset_index(name="offres")

map_data["lat"] = map_data["ville"].map(lambda x: coords.get(x, {}).get("lat"))
map_data["lon"] = map_data["ville"].map(lambda x: coords.get(x, {}).get("lon"))

fig_map = px.scatter_mapbox(
    map_data,
    lat="lat",
    lon="lon",
    size="offres",
    hover_name="ville",
    size_max=40,
    zoom=5
)

fig_map.update_layout(mapbox_style="open-street-map")

st.plotly_chart(fig_map, use_container_width=True)

# =============================
# HEATMAP METIERS
# =============================

st.subheader("Carte de chaleur des métiers les plus demandés")

top_jobs = df["poste"].value_counts().head(15).reset_index()
top_jobs.columns = ["poste", "offres"]

fig_heat = px.density_heatmap(
    top_jobs,
    x="poste",
    y="offres",
    z="offres",
    color_continuous_scale="Blues"
)

st.plotly_chart(fig_heat, use_container_width=True)

# =============================
# EVOLUTION OFFRES
# =============================

st.subheader("Evolution des offres par ville")

evolution = df.groupby("ville").size().reset_index(name="offres")

fig_evo = px.line(
    evolution,
    x="ville",
    y="offres",
    markers=True
)

st.plotly_chart(fig_evo, use_container_width=True)

# TABLEAU
st.subheader("Données")
st.dataframe(df)

# =============================
# TELECHARGER CSV
# =============================

st.subheader("Télécharger les données")

csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Télécharger les données CSV",
    data=csv,
    file_name="offres_emploi.csv",
    mime="text/csv"
)