import streamlit as st
import pandas as pd
import plotly.express as px


# -------------------------------------------------------------
# 1. Kurssikehitys
# -------------------------------------------------------------
def plot_price_history(df_price, selected_companies):
    df = df_price[df_price["Yritys"].isin(selected_companies)].copy()

    fig = px.line(
        df,
        x="Date",
        y="Close",
        color="Yritys",
        title="Osakkeiden kurssikehitys valitulla aikavälillä"
    )

    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Päivämäärä",
        yaxis_title="Kurssi (€)",
        legend_title="Yhtiö",
        template="plotly_white"
    )

    return fig


# -------------------------------------------------------------
# 2. Yhtiöiden vertailutaulukko (Lajittelumahdollisuus mukana)
# -------------------------------------------------------------
def create_comparison_table(
    df_price,
    df_keyfigures,
    df_info,
    selected_companies,
    sort_by="Muutos %",
    ascending=False
):
    rows = []

    for company in selected_companies:
        prices = df_price[
            df_price["Yritys"] == company
        ].sort_values("Date")

        valid_prices = prices["Close"].dropna()
        if prices.empty:
            continue

        info = df_info[df_info["Yritys"] == company]
        kf = df_keyfigures[df_keyfigures["Yritys"] == company]

        start_price = valid_prices.iloc[0]
        end_price = valid_prices.iloc[-1]

        high = valid_prices.max()
        low = valid_prices.min()

        price_change_eur = end_price - start_price
        change_pct = ((end_price - start_price) / start_price) * 100

        sector = "-"
        if not info.empty:
            sector = info.iloc[0]["Sektori"]

        marketcap = None
        if not kf.empty:
            marketcap = kf.iloc[0]["Marketcap"]

        if pd.notnull(marketcap):
            if marketcap >= 1000:
                marketcap_text = f"{marketcap/1000:.2f} mrd €"
            else:
                marketcap_text = f"{marketcap:.0f} M€"
        else:
            marketcap_text = "-"

        rows.append({
            "Yhtiö": company,
            "Toimiala": sector,
            "Viimeisin (€)": round(end_price, 2),
            "Ylin (€)": round(high, 2),
            "Alin (€)": round(low, 2),
            "Tuotto (€)": round(price_change_eur, 2),
            "Muutos %": round(change_pct, 2),
            "Markkina-arvo": marketcap_text,
            "_raw_mcap": marketcap if pd.notnull(marketcap) else 0  # Piilotettu kenttä lajittelua varten
        })

    table = pd.DataFrame(rows)

    if not table.empty:
        # Lajittelu vaatimuksen 4e mukaisesti
        if sort_by == "Markkina-arvo":
            table = table.sort_values("_raw_mcap", ascending=ascending)
        elif sort_by in table.columns:
            table = table.sort_values(sort_by, ascending=ascending)
        
        # Poistetaan tekninen apusarake ennen näyttämistä
        table = table.drop(columns=["_raw_mcap"])

    return table


# -------------------------------------------------------------
# 3. Yhtiökohtaiset tunnusluvut (Osinko-% mukana)
# -------------------------------------------------------------
def render_company_kpis(company_name, df_price, df_keyfigures):
    price = (
        df_price[df_price["Yritys"] == company_name]
        .sort_values("Date")
        .copy()
    )

    key = df_keyfigures[df_keyfigures["Yritys"] == company_name]

    if price.empty or key.empty:
        st.warning("Tietoja ei löytynyt.")
        return

    latest = price["Close"].dropna().iloc[-1]
    first = price["Close"].dropna().iloc[0]

    highest = price["Close"].max()
    lowest = price["Close"].min()

    price_change_eur = latest - first
    change_pct = ((latest - first) / first) * 100

    pe = key["Trailing P/E"].iloc[0] if "Trailing P/E" in key.columns else None
    pb = key["P/B"].iloc[0] if "P/B" in key.columns else None
    ps = key["Trailing P/S"].iloc[0] if "Trailing P/S" in key.columns else None
    div_yield = key["Dividend Yield"].iloc[0] if "Dividend Yield" in key.columns else None

    ma50 = key["MA50"].iloc[0] if "MA50" in key.columns else None
    ma200 = key["MA200"].iloc[0] if "MA200" in key.columns else None
    marketcap = key["Marketcap"].iloc[0] if "Marketcap" in key.columns else None
    eps = key["Trailing EPS"].iloc[0] if "Trailing EPS" in key.columns else None

    # Ensimmäinen rivi: Kurssimuutokset
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Viimeisin kurssi", f"{latest:.2f} €")
    c2.metric("Ylin kurssi", f"{highest:.2f} €")
    c3.metric("Alin kurssi", f"{lowest:.2f} €")
    c4.metric("Tuotto valitulla aikavälillä", f"{price_change_eur:+.2f} €", delta=f"{change_pct:.2f} %")

    st.divider()

    # Toinen rivi: Valuaatiot ja Osinko-% (Vaatimus 6a, 6b, 6c)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("P/E", "-" if pd.isna(pe) else f"{pe:.2f}")
    k2.metric("P/S", "-" if pd.isna(ps) else f"{ps:.2f}")
    
    # Osinko-% muotoilu (YFinance antaa desimaalina esim. 0.045 -> 4.5 %)
    if pd.notna(div_yield):
        div_text = f"{div_yield * 100:.2f} %" if div_yield < 1 else f"{div_yield:.2f} %"
    else:
        div_text = "-"
    k3.metric("Osinko %", div_text)

    if pd.notna(marketcap):
        if marketcap >= 1000:
            marketcap_text = f"{marketcap/1000:.2f} mrd €"
        else:
            marketcap_text = f"{marketcap:.0f} M€"
    else:
        marketcap_text = "-"
    k4.metric("Markkina-arvo", marketcap_text)

    st.divider()

    # Kolmas rivi: Muut tunnusluvut
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("P/B", "-" if pd.isna(pb) else f"{pb:.2f}")
    m2.metric("MA50", "-" if pd.isna(ma50) else f"{ma50:.2f} €")
    m3.metric("MA200", "-" if pd.isna(ma200) else f"{ma200:.2f} €")
    m4.metric("EPS", "-" if pd.isna(eps) else f"{eps:.2f}")


# -------------------------------------------------------------
# 4. Kvartaalitulokset
# -------------------------------------------------------------
def render_quarterly_analysis(company_name, df_quarters):
    company = df_quarters[df_quarters["Yritys"] == company_name].copy()

    if company.empty:
        st.info("Kvartaalituloksia ei löytynyt.")
        return

    if "Pvm" in company.columns:
        company = company.sort_values("Pvm", ascending=True)
    else:
        company = company.sort_values("Kvarttaali", ascending=True)

    metric = st.radio(
        "Valitse tarkasteltava tunnusluku",
        ["Liikevaihto", "Nettotulos", "EPS"],
        horizontal=True,
        key="quarter_metric"
    )

    fig = px.bar(
        company,
        x="Kvarttaali",
        y=metric,
        color=metric,
        text_auto=".2s",
        title=f"{company_name} – {metric}",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        xaxis_title="Kvartaali",
        yaxis_title=metric,
        template="plotly_white",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Kvartaalitiedot")

    display = company[
        ["Kvarttaali", "Liikevaihto", "Nettotulos", "EPS"]
    ].copy()

    display["Liikevaihto"] = display["Liikevaihto"].round(1)
    display["Nettotulos"] = display["Nettotulos"].round(1)
    display["EPS"] = display["EPS"].round(2)

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )