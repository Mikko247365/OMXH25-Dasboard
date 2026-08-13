import streamlit as st
import src.data as data
import src.charts as vis

st.set_page_config(
    page_title="OMXH25 Visualisoinnit",
    page_icon="📈",
    layout="wide"
)

st.title("📈 OMXH25 Osakedashboard (Visualisointiosio)")

# -------------------------------------------------------------
# Datan lataus
# -------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_data():
    prices = data.get_price_data(data.COMPANIES)
    info = data.get_info_data(data.COMPANIES)
    keyfigures = data.get_keyfigures_data(data.COMPANIES)
    
    try:
        quarters = data.quarterly_data("Kvarttaalidata.csv")
    except Exception:
        quarters = data.get_quarterly_stmt(data.COMPANIES)
        
    return prices, info, keyfigures, quarters

with st.spinner("Ladataan markkinadataa..."):
    df_prices, df_info, df_keyfigures, df_quarters = load_data()

company_list = list(data.COMPANIES.keys())

# -------------------------------------------------------------
# Kutsutaan suoraan valmiita kokonaisuuksia charts.py-tiedostosta
# -------------------------------------------------------------
tab1, tab2 = st.tabs(["🏢 Yhtiökohtainen tarkastelu", "📊 Yhtiövertailu"])

with tab1:
    # Sisältää yhtiövalikon + kurssikaavion + KPI-kortit + kvartaalit
    vis.render_single_company_section(
        df_prices=df_prices,
        df_keyfigures=df_keyfigures,
        df_quarters=df_quarters,
        df_info=df_info,
        company_list=company_list
    )

with tab2:
    # Sisältää monivalinnan + vertailukaavion + vertailutaulukon
    vis.render_company_comparison_section(
        df_prices=df_prices,
        df_keyfigures=df_keyfigures,
        df_info=df_info,
        company_list=company_list
    )