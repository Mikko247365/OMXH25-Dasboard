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
    
    st.header("🏢 Yhtiökohtainen analyysi")

    # Yhtiövalinta komponenttina suoraan tässä funktiossa
    selected_company = st.selectbox(
        "Valitse yhtiö tarkasteltavaksi:",
        options=company_list,
        index=0,
        key="charts_single_company_select"
    )

    st.subheader(f"📈 {selected_company} – Osakekurssi ja kehitys")

    # Kurssikaavio (sisältää liukuvat keskiarvot MA50 ja MA200)
    fig = plot_price_history(df_prices, selected_company)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Kurssidataa ei voitu esittää valitulle yhtiölle.")

    st.divider()

    # Tunnuslukukortit
    render_company_kpis(selected_company, df_prices, df_keyfigures)

    st.divider()

    # Kvartaalitilastot Kvarttaalidata.csv:stä
    st.subheader(f"📅 {selected_company} | Kvartaalitulokset")
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
    if df is None or df.empty or "Date" not in df.columns:
        return df

    df_filtered = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ].copy()
    return df_filtered


def plot_price_history(df_price, selected_companies):
    if isinstance(selected_companies, str):
        selected_companies = [selected_companies]

    if df_price is None or df_price.empty or "Close" not in df_price.columns:
        return None

    df = df_price[df_price["Yritys"].isin(selected_companies)].copy()
    if df.empty:
        return None

    df = df.sort_values("Date")

    # Jos kyseessä on yksittäinen yhtiö, lasketaan liukuvat keskiarvot (MA)
    if len(selected_companies) == 1:
        df["MA50"] = df["Close"].rolling(window=50).mean()
        df["MA200"] = df["Close"].rolling(window=200).mean()

        # Määritetään omat selkeät värit käyrille
        color_map = {
            "Sulkemishinta": "#00E5FF",  # Kirkas Cyan / Neon Sininen (Pääkäyrä)
            "MA 50": "#FF9F0A",          # Warm Orange (Lyhyt KA)
            "MA 200": "#FF453A"          # Bright Red (Pitkä KA)
        }

        # Nimetään sarakkeet uudelleen suoraan ennen kuvaajan luontia
        df_plot = df.rename(columns={
            "Close": "Sulkemishinta",
            "MA50": "MA 50",
            "MA200": "MA 200"
        })

        fig = px.line(
            df_plot,
            x="Date",
            y=["Sulkemishinta", "MA 50", "MA 200"],
            title=f"{selected_companies[0]} – Osakekurssi ja liukuvat keskiarvot",
            labels={"value": "Hinta (€)", "variable": "Käyrä"},
            color_discrete_map=color_map
        )
        
        # Säädetään pääkurssin viivasta hieman paksumpi
        fig.update_traces(patch={"line": {"width": 2.5}}, selector={"name": "Sulkemishinta"})
        fig.update_traces(patch={"line": {"width": 1.5}}, selector={"name": "MA 50"})
        fig.update_traces(patch={"line": {"width": 1.5}}, selector={"name": "MA 200"})

    else:
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
        legend_title="Tiedot",
        template="plotly_dark",  # Vaihdetaan pohja tummalle teemalle sopivaksi
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def render_company_kpis(company_name, df_price, df_keyfigures):
    # Esittää valitun yhtiön kurssiyhteenvedon ja tunnusluvut Streamlit metric -kortteina.
    price = df_price[df_price["Yritys"] == company_name].sort_values("Date") if df_price is not None else pd.DataFrame()
    key = df_keyfigures[df_keyfigures["Yritys"] == company_name] if df_keyfigures is not None else pd.DataFrame()

    if price.empty:
        st.warning(f"Ei hintadataa yhtiölle {company_name}.")
        return

    valid_price_df = price.dropna(subset=["Close"])
    if valid_price_df.empty:
        return

    valid_close = valid_price_df["Close"]
    latest = valid_close.iloc[-1]
    first = valid_close.iloc[0]
    highest = valid_close.max()
    lowest = valid_close.min()

    # Haetaan aikavälin aloitus- ja lopetuspäivämäärät
    first_date = valid_price_df["Date"].iloc[0]
    latest_date = valid_price_df["Date"].iloc[-1]
    
    first_date_str = first_date.strftime("%d.%m.%Y") if hasattr(first_date, "strftime") else str(first_date)
    latest_date_str = latest_date.strftime("%d.%m.%Y") if hasattr(latest_date, "strftime") else str(latest_date)

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

    marketcap = key["Marketcap"].iloc[0] if "Marketcap" in key.columns and not key.empty else None
    eps = key["Trailing EPS"].iloc[0] if "Trailing EPS" in key.columns and not key.empty else None

    # 1. Kurssiyhteenveto (valittu aikaväli suluissa otsikossa)
    st.subheader(f"📈 Kurssiyhteenveto | Valittu aikaväli: {first_date_str} – {latest_date_str}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Ylin kurssi", f"{highest:.2f} €")
    c2.metric("Alin kurssi", f"{lowest:.2f} €")
    c3.metric("Muutos valitulla aikavälillä", f"{price_change_eur:+.2f} €", delta=f"{change_pct:.2f} %")

    st.write("")

    # 2. Tunnusluvut (tuorein valittu päivämäärä ja kurssi suluissa otsikossa)
    st.subheader(f"📊 Tunnusluvut | Päätöskurssi {latest:.2f} € ({latest_date_str} )")
    
    # Rivi 1: Valuaatiokertoimet (3 laatikkoa)
    k1, k2, k3 = st.columns(3)
    k1.metric("P/E (Trailing)", "-" if pd.isna(pe) else f"{pe:.2f}")
    k2.metric("P/S (Trailing)", "-" if pd.isna(ps) else f"{ps:.2f}")
    k3.metric("P/B", "-" if pd.isna(pb) else f"{pb:.2f}")

    st.write("")

    # Rivi 2: Muut tunnusluvut ja Osinko (3 laatikkoa)
    m1, m2, m3 = st.columns(3)
    m1.metric("EPS (Trailing)", "-" if pd.isna(eps) else f"{eps:.2f} €")
    
    if pd.notna(div_yield):
        div_text = f"{div_yield * 100:.2f} %" if div_yield < 1 else f"{div_yield:.2f} %"
    else:
        div_text = "-"
    m2.metric("Osinko %", div_text)

    if pd.notna(marketcap):
        marketcap_text = f"{marketcap/1000:.2f} mrd €" if marketcap >= 1000 else f"{marketcap:.0f} M€"
    else:
        marketcap_text = "-"
    m3.metric("Markkina-arvo", marketcap_text)


def render_quarterly_analysis(company_name, df_quarters):
    # Esittää kvartaalitulokset Kvarttaalidata.csv:stä.
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
    # Laskee ja muodostaa yhtiöiden vertailutaulukon.
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