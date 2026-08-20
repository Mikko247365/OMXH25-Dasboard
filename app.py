import streamlit as st
import src.data as data
import src.charts as vis
import datetime

st.set_page_config(
    page_title="OMXH25 Visualisoinnit",
    page_icon="📈",
    layout="wide"
)

# -------------------------------------------------------------
# Teema-asetukset (UI v2)
# -------------------------------------------------------------
st.markdown("""
<style>

/* Yleinen fontti */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Otsikot */
h1, h2, h3, h4 {
    font-weight: 600;
}

/* KPI-korttien reunat ja padding */
div[data-testid="stMetric"] {
    padding: 20px !important;
    border-radius: 10px !important;
    border: 1px solid #ddd !important;
}

/* Divider spacing */
hr {
    margin-top: 30px;
    margin-bottom: 30px;
}

/* Taulukot */
.dataframe {
    border-radius: 8px;
    overflow: hidden;
}

/* Tabien otsikot */
.stTabs [role="tab"] {
    font-size: 16px;
    padding: 10px 20px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Hero-otsikko
# -------------------------------------------------------------
st.markdown("""
<div style="padding: 20px 0 10px 0;">
    <h1 style="margin-bottom: 0;">📈 OMXH25 Osakedashboard</h1>
    <p style="color: #666; font-size: 18px; margin-top: 5px;">
        Yhtiökohtaiset analyysit, vertailut ja kvartaalitulokset yhdellä silmäyksellä.
    </p>
</div>
""", unsafe_allow_html=True)

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
# UI spacing ennen tabien luontia
# -------------------------------------------------------------
st.write("")
st.write("")


MIN_DATE = datetime.date(2024, 1, 1)
TODAY = datetime.date.today()


# -------------------------------------------------------------
# Valinta: Päivämäärä vs Kvartaali
# -------------------------------------------------------------
mode = st.radio(
    "Valitse tarkastelutapa",
    ["Päivämäärä", "Kvartaali"],
    horizontal=True
)

st.subheader("📅 Valitse aikaväli kurssikehitykselle")

# -------------------------------------------------------------
# Päivämäärävalinta (näkyy vain jos valittu)
# -------------------------------------------------------------
 
if mode == "Päivämäärä":
    start_date = st.date_input(
        "Alkupäivä",
        value=TODAY,
        min_value=MIN_DATE,
        max_value=TODAY
    )

    end_date = st.date_input(
        "Loppupäivä",
        value=TODAY,
        min_value=MIN_DATE,
        max_value=TODAY
    )
    # -------------------------------------------------------------
# Kvartaali-valinta (näkyy vain jos valittu)
# -------------------------------------------------------------
if mode == "Kvartaali":
    kvartaalit = sorted(df_quarters["Kvarttaali"].unique())

    selected_quarter = st.selectbox(
        "Valitse kvartaali",
        kvartaalit
    )


    # Muutetaan kvartaalivalinta päivämääriksi
    year = int(selected_quarter[:4])
    q = int(selected_quarter[-1])

    quarter_start = {
        1: datetime.date(year, 1, 1),
        2: datetime.date(year, 4, 1),
        3: datetime.date(year, 7, 1),
        4: datetime.date(year, 10, 1)
    }[q]

    quarter_end = {
        1: datetime.date(year, 3, 31),
        2: datetime.date(year, 6, 30),
        3: datetime.date(year, 9, 30),
        4: datetime.date(year, 12, 31)
    }[q]

    start_date = quarter_start
    end_date = quarter_end


# -------------------------------------------------------------
# UI v1 — kaksi tabia
# -------------------------------------------------------------
tab1, tab2 = st.tabs(["🏢 Yhtiökohtainen tarkastelu", "📊 Yhtiövertailu"])

with tab1:
    vis.render_single_company_section(
        df_prices=df_prices,
        df_keyfigures=df_keyfigures,
        df_quarters=df_quarters,
        df_info=df_info,
        company_list=company_list,
        start_date=start_date,
        end_date=end_date
    )

with tab2:
    vis.render_company_comparison_section(
        df_prices=df_prices,
        df_keyfigures=df_keyfigures,
        df_info=df_info,
        company_list=company_list,
        start_date=start_date,
        end_date=end_date
    )