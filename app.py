import streamlit as st
import src.data as data # Mikon tekemä data.py
import src.charts as vis  # Sinun tekemä charts.py

# -------------------------------------------------------------
# 1. Sivun perusasetukset
# -------------------------------------------------------------
st.set_page_config(
    page_title="OMXH25 Analyysi",
    page_icon="📈",
    layout="wide"
)

st.title("📈 OMXH25 Osakeanalysaattori")
st.caption("Suomalaisten pörssiyhtiöiden kurssikehitys, tunnusluvut ja tulokset")
st.divider()

# -------------------------------------------------------------
# 2. Datan lataus Mikon funktioilla (välimuistissa)
# -------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_data():
    price_df = data.get_price_data(data.companies)
    info_df = data.get_info_data(data.companies)
    keyfigures_df = data.get_keyfigures_data(data.companies)
    quarters_df = data.get_quarterly_stmt(data.companies)
    return price_df, info_df, keyfigures_df, quarters_df

with st.spinner("Ladataan markkinadataa..."):
    df_price, df_info, df_keyfigures, df_quarters = load_data()

# -------------------------------------------------------------
# 3. Sivupalkin valinnat
# -------------------------------------------------------------
st.sidebar.header("⚙️ Valinnat")

selected_companies = st.sidebar.multiselect(
    "Valitse seurattavat yhtiöt:",
    options=list(data.companies.keys()),
    default=["Nokia", "Fortum", "Sampo"]
)

if not selected_companies:
    st.warning("⚠️ Valitse vähintään yksi yhtiö sivupalkista nähdäksesi tiedot.")
    st.stop()

# -------------------------------------------------------------
# 4. Päänäkymä: Taulukko & Kuvaaja
# -------------------------------------------------------------
# Osakkeiden vertailutaulukko
st.subheader("📋 Yhtiöiden yleiskatsaus")
table_df = vis.create_comparison_table(df_price, df_keyfigures, df_info, selected_companies)
st.dataframe(table_df, use_container_width=True, hide_index=True)

st.divider()

# Kurssihistorian viivagraafi
st.subheader("📉 Kurssikehitys")
price_fig = vis.plot_price_history(df_price, selected_companies)
st.plotly_chart(price_fig, use_container_width=True)

st.divider()

# -------------------------------------------------------------
# 5. Yhtiökohtainen osio
# -------------------------------------------------------------
st.subheader("🔍 Yhtiökohtainen tarkastelu")

selected_single = st.selectbox(
    "Valitse yhtiö syvempää tarkastelua varten:",
    options=selected_companies
)

if selected_single:
    # Metriikat ja avainluvut
    vis.render_company_kpis(selected_single, df_price, df_keyfigures)
    
    st.write("---")
    
    # Kvartaalitulokset
    st.markdown(f"#### 📑 Kvartaalitulokset: {selected_single}")
    vis.render_quarterly_analysis(selected_single, df_quarters)