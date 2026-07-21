import plotly.express as px
import pandas as pd
import streamlit as st

# Kaikkien toimialojen suomennokset
SECTOR_TRANSLATIONS = {
    "Technology": "Teknologia",
    "Financial Services": "Rahoituspalvelut",
    "Industrials": "Teollisuustuotteet ja -palvelut",
    "Consumer Defensive": "Päivittäistavarat",
    "Consumer Cyclical": "Kestokulutustavarat",
    "Basic Materials": "Perusteollisuus & Materiaalit",
    "Energy": "Energia",
    "Utilities": "Yhdyskuntatekniikka & Hyödykkeet",
    "Healthcare": "Terveydenhuolto",
    "Real Estate": "Kiinteistöala",
    "Communication Services": "Viestintäpalvelut"
}

# -------------------------------------------------------------
# 1. Osakkeen hinnan kehitys (Viivagraafi)
# -------------------------------------------------------------
def plot_price_history(df_price, selected_companies):
    filtered_df = df_price[df_price["Yritys"].isin(selected_companies)].copy()
    date_col = "Date" if "Date" in filtered_df.columns else filtered_df.columns[0]
    
    fig = px.line(
        filtered_df,
        x=date_col,
        y="Close",
        color="Yritys",
        title="Osakkeen päätöskurssin kehitys (€)"
    )
    
    fig.update_layout(
        xaxis_title="Päivämäärä",
        yaxis_title="Päätöskurssi (€)",
        hovermode="x unified",
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

# -------------------------------------------------------------
# 2. Valittujen yhtiöiden yleiskatsaustaulukko
# -------------------------------------------------------------
def create_comparison_table(df_price, df_keyfigures, df_info, selected_companies):
    comparison_list = []
    
    for company in selected_companies:
        p_data = df_price[df_price["Yritys"] == company]
        kf_data = df_keyfigures[df_keyfigures["Yritys"] == company]
        inf_data = df_info[df_info["Yritys"] == company]
        
        if p_data.empty:
            continue
            
        start_price = float(p_data["Close"].iloc[0])
        end_price = float(p_data["Close"].iloc[-1])
        high_price = float(p_data["Close"].max())
        low_price = float(p_data["Close"].min())
        change_pct = ((end_price - start_price) / start_price) * 100
        
        mcap = kf_data["Marketcap"].values[0] if not kf_data.empty else None
        raw_sector = inf_data["Sektori"].values[0] if not inf_data.empty else "Ei tietoa"
        sector_fi = SECTOR_TRANSLATIONS.get(raw_sector, raw_sector)
        
        comparison_list.append({
            "Yhtiö": company,
            "Toimiala": sector_fi,
            "Viimeisin (€)": round(end_price, 2),
            "Ylin (€)": round(high_price, 2),
            "Alin (€)": round(low_price, 2),
            "Kehitys (%)": round(change_pct, 2),
            "Markkina-arvo": mcap  # Näytetään Mikon raakadata sellaisenaan
        })
        
    return pd.DataFrame(comparison_list)

# -------------------------------------------------------------
# 3. Yhtiökohtaiset Avainmetriikat (KPIs)
# -------------------------------------------------------------
def render_company_kpis(company_name, df_price, df_keyfigures):
    p_data = df_price[df_price["Yritys"] == company_name]
    kf_data = df_keyfigures[df_keyfigures["Yritys"] == company_name]
    
    if p_data.empty or kf_data.empty:
        st.warning("Tietoja ei löytynyt valitulle yhtiölle.")
        return

    start_p = float(p_data["Close"].iloc[0])
    end_p = float(p_data["Close"].iloc[-1])
    price_change = end_p - start_p
    return_pct = ((end_p - start_p) / start_p) * 100
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aloitushinta", f"{start_p:.2f} €")
    c2.metric("Viimeisin hinta", f"{end_p:.2f} €")
    c3.metric("Tuotto ajanjaksolla", f"{price_change:+.2f} €", delta=f"{return_pct:.2f} %")
    
    mcap = kf_data["Marketcap"].values[0]
    c4.metric("Markkina-arvo", f"{mcap}" if pd.notnull(mcap) else "-")
    
    st.write("---")
    
    pe = kf_data["Trailing P/E"].values[0]
    ps = kf_data["Trailing PS"].values[0]
    ma50 = kf_data["MA50"].values[0]
    ma200 = kf_data["MA200"].values[0]
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("P/E (Trailing)", f"{pe:.2f}" if pd.notnull(pe) else "-")
    k2.metric("P/S (Trailing)", f"{ps:.2f}" if pd.notnull(ps) else "-")
    k3.metric("MA50 (50pv KA)", f"{ma50:.2f} €" if pd.notnull(ma50) else "-")
    k4.metric("MA200 (200pv KA)", f"{ma200:.2f} €" if pd.notnull(ma200) else "-")

# -------------------------------------------------------------
# 4. Kvartaalitulokset (Alkuperäisillä luvuilla)
# -------------------------------------------------------------
def render_quarterly_analysis(company_name, df_quarters):
    company_q = df_quarters[df_quarters["Yritys"] == company_name].copy()
    
    if company_q.empty:
        st.info("Kvartaalituloksia ei löytynyt tälle yhtiölle.")
        return

    company_q["Kvartaali"] = pd.to_datetime(company_q["Neljännes"]).dt.to_period("Q").astype(str)
    company_q = company_q.sort_values(by="Neljännes", ascending=True)
    
    # Käytetään Mikon sarakkeita sellaisenaan ilman jakolaskuja
    display_df = pd.DataFrame({"Kvartaali": company_q["Kvartaali"]})
    
    for col in ["Liikevaihto", "Nettotulos", "EPS"]:
        if col in company_q.columns:
            display_df[col] = company_q[col]
        
    metric_choice = st.radio(
        "Valitse näytettävä mittari kuvaajalle:",
        [c for c in display_df.columns if c != "Kvartaali"],
        horizontal=True
    )
    
    if metric_choice:
        fig = px.bar(
            display_df,
            x="Kvartaali",
            y=metric_choice,
            title=f"{company_name} - {metric_choice}",
            color=metric_choice,
            color_continuous_scale="Viridis"
        )
        fig.update_layout(xaxis_type="category")
        st.plotly_chart(fig, use_container_width=True)
        
    st.dataframe(display_df, use_container_width=True, hide_index=True)