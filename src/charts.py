
import streamlit as st
import pandas as pd
import plotly.express as px

# =============================================================
# 1. YHTIÖKOHTAINEN OSIO (Valikko + Kurssi + KPI:t + Kvartaalit)
# =============================================================
def render_single_company_section(
    df_prices, df_keyfigures, df_quarters, df_info, company_list,
    start_date, end_date
):
    # Suodata hinnat aikavälin mukaan
    df_prices = filter_by_date(df_prices, start_date, end_date)
    
# Kokoaa yhteen paikkaan yhtiövalinnan, kurssikuvaajan, tunnuslukukortit 
# ja kvartaalianalyysin.
    
    st.header("🏢 Yhtiökohtainen analyysi")

    # Yhtiövalinta komponenttina suoraan tässä funktiossa
    selected_company = st.selectbox(
        "Valitse yhtiö tarkasteltavaksi:",
        options=company_list,
        index=0,
        key="charts_single_company_select"
    )

    st.subheader(f"📈 {selected_company} – Osakekurssi ja kehitys")

    # Kurssikaavio
    fig = plot_price_history(df_prices, selected_company)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Kurssidataa ei voitu esittää valitulle yhtiölle.")

    st.divider()

    # Tunnuslukukortit
    st.subheader(f"📊 {selected_company} – Avaintunnusluvut")
    render_company_kpis(selected_company, df_prices, df_keyfigures)

    st.divider()

    # Kvartaalitilastot Kvarttaalidata.csv:stä
    st.subheader(f"📅 {selected_company} – Kvartaalitulokset")
    render_quarterly_analysis(selected_company, df_quarters)

    return selected_company


# =============================================================
# 2. YHTIÖVERTAILUOSIO (Monivalinta + Vertailukaavio + Taulukko)
# =============================================================
def render_company_comparison_section(
    df_prices, df_keyfigures, df_info, company_list,
    start_date, end_date
):

    # Suodata hinnat aikavälin mukaan
    df_prices = filter_by_date(df_prices, start_date, end_date)

    st.header("📊 Yhtiövertailu")

    
    # Kokoaa yhteen paikkaan useamman yhtiön valinnan, vertailukaavion 
    # ja järjestettävän vertailutaulukon.
    
    # Monivalintakomponentti yhtiöille
    selected_companies = st.multiselect(
        "Valitse vertailtavat yhtiöt:",
        options=company_list,
        default=company_list[:4] if len(company_list) >= 4 else company_list,
        key="charts_multi_company_select"
    )

    if not selected_companies:
        st.info("Valitse vähintään yksi yhtiö vertailua varten.")
        return

    # Monen yhtiön vertailukaavio
    fig_multi = plot_price_history(df_prices, selected_companies)
    if fig_multi:
        st.plotly_chart(fig_multi, use_container_width=True)

    st.divider()

    # Järjestettävä vertailutaulukko
    st.subheader("📋 Vertailutaulukko")
    
    col_sort, _ = st.columns([2, 2])
    with col_sort:
        sort_col = st.selectbox(
            "Järjestä taulukko sarakkeen mukaan:",
            options=["Muutos %", "Tuotto (€)", "Viimeisin (€)", "Markkina-arvo"],
            index=0,
            key="charts_sort_select"
        )

    table_df = create_comparison_table(
        df_price=df_prices,
        df_keyfigures=df_keyfigures,
        df_info=df_info,
        selected_companies=selected_companies,
        sort_by=sort_col,
        ascending=False
    )

    st.dataframe(table_df, use_container_width=True, hide_index=True)


# =============================================================
# APUFUNKTIOT (Kuvaajat, Taulukot, KPI-kortit)
# =============================================================
def filter_by_date(df, start_date, end_date):
    df_filtered = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ].copy()
    return df_filtered

def plot_price_history(df_price, selected_companies):
   #Piirtää Plotly-viivakaavion valituille osakkeille.
    if isinstance(selected_companies, str):
        selected_companies = [selected_companies]

    if df_price is None or df_price.empty or "Close" not in df_price.columns:
        return None

    df = df_price[df_price["Yritys"].isin(selected_companies)].copy()
    if df.empty:
        return None

    fig = px.line(
        df,
        x="Date",
        y="Close",
        color="Yritys",
        title="Osakkeiden kurssikehitys"
    )

    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Päivämäärä",
        yaxis_title="Kurssi (€)",
        legend_title="Yhtiö",
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def render_company_kpis(company_name, df_price, df_keyfigures):
    #Esittää valitun yhtiön tunnusluvut Streamlit metric -kortteina.
    price = df_price[df_price["Yritys"] == company_name].sort_values("Date") if df_price is not None else pd.DataFrame()
    key = df_keyfigures[df_keyfigures["Yritys"] == company_name] if df_keyfigures is not None else pd.DataFrame()

    if price.empty:
        st.warning(f"Ei hintadataa yhtiölle {company_name}.")
        return

    valid_close = price["Close"].dropna()
    if valid_close.empty:
        return

    latest = valid_close.iloc[-1]
    first = valid_close.iloc[0]
    highest = valid_close.max()
    lowest = valid_close.min()

    price_change_eur = latest - first
    change_pct = ((latest - first) / first) * 100

    pe = key["Trailing P/E"].iloc[0] if "Trailing P/E" in key.columns and not key.empty else None
    pb = key["P/B"].iloc[0] if "P/B" in key.columns and not key.empty else None
    ps = key["Trailing P/S"].iloc[0] if "Trailing P/S" in key.columns and not key.empty else None
    
    div_col = None
    for c in ["Osinko % (Trailing)", "Osinko-%", "Dividend Yield"]:
        if key is not None and c in key.columns:
            div_col = c
            break
    div_yield = key[div_col].iloc[0] if div_col and not key.empty else None

    ma50 = key["MA50"].iloc[0] if "MA50" in key.columns and not key.empty else None
    ma200 = key["MA200"].iloc[0] if "MA200" in key.columns and not key.empty else None
    marketcap = key["Marketcap"].iloc[0] if "Marketcap" in key.columns and not key.empty else None
    eps = key["Trailing EPS"].iloc[0] if "Trailing EPS" in key.columns and not key.empty else None

    st.markdown("##### 📈 Kurssiyhteenveto")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Viimeisin kurssi", f"{latest:.2f} €")
    c2.metric("Ylin kurssi", f"{highest:.2f} €")
    c3.metric("Alin kurssi", f"{lowest:.2f} €")
    c4.metric("Tuotto valitulla aikavälillä", f"{price_change_eur:+.2f} €", delta=f"{change_pct:.2f} %")

    st.write("")

    st.markdown("##### 📊 Valuaatio & Osinko")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("P/E (Trailing)", "-" if pd.isna(pe) else f"{pe:.2f}")
    k2.metric("P/S (Trailing)", "-" if pd.isna(ps) else f"{ps:.2f}")
    
    if pd.notna(div_yield):
        div_text = f"{div_yield * 100:.2f} %" if div_yield < 1 else f"{div_yield:.2f} %"
    else:
        div_text = "-"
    k3.metric("Osinko %", div_text)

    if pd.notna(marketcap):
        marketcap_text = f"{marketcap/1000:.2f} mrd €" if marketcap >= 1000 else f"{marketcap:.0f} M€"
    else:
        marketcap_text = "-"
    k4.metric("Markkina-arvo", marketcap_text)

    st.write("")

    st.markdown("##### 🔍 Muut tunnusluvut")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("P/B", "-" if pd.isna(pb) else f"{pb:.2f}")
    m2.metric("MA50", "-" if pd.isna(ma50) else f"{ma50:.2f} €")
    m3.metric("MA200", "-" if pd.isna(ma200) else f"{ma200:.2f} €")
    m4.metric("EPS (Trailing)", "-" if pd.isna(eps) else f"{eps:.2f} €")


def render_quarterly_analysis(company_name, df_quarters):
    #Esittää kvartaalitulokset Kvarttaalidata.csv:stä.
    if df_quarters is None or df_quarters.empty:
        st.info("Kvartaalidataa ei ole ladattu.")
        return

    company = df_quarters[df_quarters["Yritys"] == company_name].copy()
    if company.empty:
        st.info(f"Yhtiölle {company_name} ei löytynyt kvartaalituloksia.")
        return

    if "Kvarttaali" in company.columns:
        company = company.sort_values("Kvarttaali", ascending=True)

    metric = st.radio(
        "Valitse tarkasteltava tunnusluku:",
        ["Liikevaihto", "Nettotulos", "EPS"],
        horizontal=True,
        key=f"quarter_metric_{company_name}"
    )

    if metric not in company.columns:
        st.error(f"Saraketta {metric} ei löydy kvartaalidatasta.")
        return

    fig = px.bar(
        company,
        x="Kvarttaali",
        y=metric,
        color=metric,
        text_auto=".2f",
        title=f"{company_name} – {metric} kvartaaleittain",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        xaxis_title="Kvarttaali",
        yaxis_title=f"{metric} ({'€' if metric == 'EPS' else 'M€'})",
        template="plotly_white",
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    cols_to_show = [c for c in ["Kvarttaali", "Liikevaihto", "Nettotulos", "EPS"] if c in company.columns]
    display = company[cols_to_show].copy()

    if "Liikevaihto" in display.columns:
        display["Liikevaihto"] = display["Liikevaihto"].apply(lambda x: f"{x:.1f} M€" if pd.notnull(x) else "-")
    if "Nettotulos" in display.columns:
        display["Nettotulos"] = display["Nettotulos"].apply(lambda x: f"{x:.1f} M€" if pd.notnull(x) else "-")
    if "EPS" in display.columns:
        display["EPS"] = display["EPS"].apply(lambda x: f"{x:.2f} €" if pd.notnull(x) else "-")

    st.dataframe(display, use_container_width=True, hide_index=True)


def create_comparison_table(df_price, df_keyfigures, df_info, selected_companies, sort_by="Muutos %", ascending=False):
   #Laskee ja muodostaa yhtiöiden vertailutaulukon.
    rows = []
    if isinstance(selected_companies, str):
        selected_companies = [selected_companies]

    for company in selected_companies:
        prices = df_price[df_price["Yritys"] == company].sort_values("Date") if df_price is not None else pd.DataFrame()
        if prices.empty:
            continue

        valid_prices = prices["Close"].dropna()
        if valid_prices.empty:
            continue

        info = df_info[df_info["Yritys"] == company] if df_info is not None and not df_info.empty else pd.DataFrame()
        kf = df_keyfigures[df_keyfigures["Yritys"] == company] if df_keyfigures is not None and not df_keyfigures.empty else pd.DataFrame()

        start_price = valid_prices.iloc[0]
        end_price = valid_prices.iloc[-1]

        high = valid_prices.max()
        low = valid_prices.min()

        price_change_eur = end_price - start_price
        change_pct = ((end_price - start_price) / start_price) * 100

        sector = "-"
        if not info.empty and "Sektori" in info.columns:
            sector = info.iloc[0]["Sektori"]

        marketcap = None
        if not kf.empty and "Marketcap" in kf.columns:
            marketcap = kf.iloc[0]["Marketcap"]

        if pd.notnull(marketcap):
            marketcap_text = f"{marketcap/1000:.2f} mrd €" if marketcap >= 1000 else f"{marketcap:.0f} M€"
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
            "_raw_mcap": marketcap if pd.notnull(marketcap) else 0
        })

    table = pd.DataFrame(rows)
    if not table.empty:
        if sort_by == "Markkina-arvo":
            table = table.sort_values("_raw_mcap", ascending=ascending)
        elif sort_by in table.columns:
            table = table.sort_values(sort_by, ascending=ascending)
        table = table.drop(columns=["_raw_mcap"])

    return table
