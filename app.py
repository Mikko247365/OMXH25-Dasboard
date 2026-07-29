import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="OMXH25 Dashboard", layout="wide")
st.title("OMXH25 Dashboard")

# --- OMXH25-yhtiöt: nimi UI:ssa, ticker taustalla ---
companies = {
    "Nokia": "NOKIA.HE",
    "Kone": "KNEBV.HE",
    "UPM": "UPM.HE",
    "Fortum": "FORTUM.HE",
    "Neste": "NESTE.HE",
    "Sampo": "SAMPO.HE",
    "Elisa": "ELISA.HE",
    "Kesko": "KESKOB.HE",
    "Orion": "ORNBV.HE",
    "Stora Enso": "STEAV.HE",
    "Metso": "METSO.HE",
    "Valmet": "VALMT.HE",
    "Wärtsilä": "WRT1V.HE",
    "Huhtamäki": "HUH1V.HE",
    "YIT": "YIT.HE",
    "Outokumpu": "OUT1V.HE",
    "Fiskars": "FSKRS.HE",
    "Terveystalo": "TTALO.HE",
    "Cargotec": "CGCBV.HE",
    "Kojamo": "KOJAMO.HE",
    "Revenio": "REG1V.HE",
    "Sanoma": "SAA1V.HE",
    "Verkkokauppa": "VERK.HE",
    "Harvia": "HARVIA.HE",
    "Olvi": "OLVAS.HE"
}

# --- Valintakomponentit ---
st.sidebar.header("Valinnat")

selected_name = st.sidebar.selectbox(
    "Valitse yhtiö",
    list(companies.keys())
)

selected_ticker = companies[selected_name]

period = st.sidebar.selectbox(
    "Aikaväli",
    ["1y", "3y", "5y"]
)

# --- Datan lataus ---
ticker = yf.Ticker(selected_ticker)
df = ticker.history(period=period)

# --- Kurssikehityksen graafi (VK32-parannettu) ---
def create_price_chart(df, company, period):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        line=dict(color="#1f77b4", width=2),
        hovertemplate="Päivä: %{x}<br>Kurssi: %{y:.2f} €<extra></extra>"
    ))

    fig.update_layout(
        title=f"{company} kurssikehitys ({period})",
        xaxis_title="Päivämäärä",
        yaxis_title="Kurssi (€)",
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig

# --- Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Kurssikehitys")
    st.plotly_chart(create_price_chart(df, selected_name, period), use_container_width=True)

with col2:
    st.subheader("Perustiedot")

    info = ticker.info

    st.markdown("""
    <div style="padding: 15px; background-color: #f5f5f5; border-radius: 8px; border: 1px solid #e0e0e0;">
        <h4 style="margin-bottom: 10px;">Yhtiön perustiedot</h4>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    **Yhtiö:** {info.get('longName', 'N/A')}  
    **Toimiala:** {info.get('industry', 'N/A')}  
    **Sektori:** {info.get('sector', 'N/A')}  
    **Kotimaa:** {info.get('country', 'N/A')}  
    **Verkkosivu:** {info.get('website', 'N/A')}
    """)

st.subheader("Kvartaalitulokset")
st.write("Kvartaalidata lisätään myöhemmin, kun data.py sisältää kvartaaliluvut.")

st.subheader("Tunnusluvut")
st.write("Tunnuslukujen laskenta lisätään myöhemmin (P/E, EPS, liikevaihto, kvartaalimuutokset).")