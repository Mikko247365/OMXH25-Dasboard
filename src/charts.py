import streamlit as st
import pandas as pd
import plotly.express as px
from src.data import normalize_price_data

# =============================================================
# 1. YHTIÖKOHTAINEN OSIO (Valikko + Kurssi + KPI:t + Kvartaalit)
# =============================================================
def render_single_company_section(
    df_prices,
    df_keyfigures,
    df_quarters,
    df_info,
    company_list,
    start_date=None,
    end_date=None
):
    st.header("🏢 Yhtiökohtainen analyysi")

    selected_company = st.selectbox(
        "Valitse yhtiö tarkasteltavaksi:",
        options=company_list,
        index=0,
        key="charts_single_company_select"
    )

    st.subheader(f"📈 {selected_company} – Osakekurssi ja kehitys")

    fig = plot_price_history(df_prices, selected_company, start_date, end_date)

    if fig:
        st.plotly_chart(fig, use_container_width=True, key=f"single_chart_{selected_company}")
    else:
        st.warning("Kurssidataa ei voitu esittää valitulle yhtiölle.")

    st.divider()

    df_prices_filtered = filter_by_date(df_prices, start_date, end_date)
    # Välitetään funktiolle sekä koko data että suodatettu data
    render_company_kpis(selected_company, df_prices, df_keyfigures, df_prices_filtered)

    st.divider()

    st.subheader(f"📅 {selected_company} | Kvartaalitulokset")
    render_quarterly_analysis(selected_company, df_quarters)

    return selected_company

# =============================================================
# 2. YHTIÖVERTAILUOSIO (Monivalinta + Vertailukaavio + Taulukko)
# =============================================================
def render_company_comparison_section(
    df_prices,
    df_keyfigures,
    df_info,
    company_list,
    start_date=None,
    end_date=None
):
    st.header("📊 Yhtiövertailu")

    selected_companies = st.multiselect(
        "Valitse vertailtavat yhtiöt:",
        options=company_list,
        default=company_list[:4] if len(company_list) >= 4 else company_list,
        key="charts_multi_company_select"
    )

    if not selected_companies:
        st.info("Valitse vähintään yksi yhtiö vertailua varten.")
        return

    # Valintapainike normalisoinnille
    use_normalization = False
    if len(selected_companies) > 0:
        view_mode = st.radio(
            "Valitse vertailutapa:",
            options=["Eurohinta (€)", "Normalisoitu (Alku = 100)"],
            horizontal=True,
            key="comparison_view_mode"
        )
        use_normalization = (view_mode == "Normalisoitu (Alku = 100)")

    fig_multi = plot_price_history(df_prices, selected_companies, start_date, end_date, normalize=use_normalization)

    if fig_multi:
        st.plotly_chart(fig_multi, use_container_width=True, key="comparison_chart")

    st.divider()

    table_df, latest_date_str, first_date_str = create_comparison_table(
        df_price=df_prices,
        df_keyfigures=df_keyfigures,
        df_info=df_info,
        selected_companies=selected_companies,
        start_date=start_date,
        end_date=end_date
    )

    if first_date_str and latest_date_str:
        st.subheader(f"📋 Vertailutaulukko | Valittu aikaväli: {first_date_str} – {latest_date_str}")
    else:
        st.subheader("📋 Vertailutaulukko")

    if not table_df.empty:
        col_names = table_df.columns.tolist()
        viimeisin_col_key = next((c for c in col_names if "Viimeisin" in c), "Viimeisin (€)")
        marketcap_col_key = next((c for c in col_names if "Markkina-arvo" in c), "Markkina-arvo (mrd €)")

        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Yhtiö": st.column_config.TextColumn("Yhtiö", alignment="left"),
                "Toimiala": st.column_config.TextColumn("Toimiala", alignment="left"),
                viimeisin_col_key: st.column_config.NumberColumn(viimeisin_col_key, format="%.2f €", alignment="right"),
                "Ylin (€)": st.column_config.NumberColumn("Ylin (€)", format="%.2f €", alignment="right"),
                "Alin (€)": st.column_config.NumberColumn("Alin (€)", format="%.2f €", alignment="right"),
                "Tuotto (€)": st.column_config.NumberColumn("Tuotto (€)", format="%+.2f €", alignment="right"),
                "Muutos %": st.column_config.NumberColumn("Muutos %", format="%+.2f %%", alignment="right"),
                marketcap_col_key: st.column_config.NumberColumn(marketcap_col_key, format="%.2f mrd €", alignment="right"),
            }
        )
    else:
        st.warning("Ei tietoja valituille yhtiöille annetulla aikavälillä.")

# =============================================================
# APUFUNKTIOT (Kuvaajat, Taulukot, KPI-kortit)
# =============================================================
def filter_by_date(df, start_date, end_date):
    if df is None or df.empty or "Date" not in df.columns:
        return df

    if start_date is None or end_date is None:
        return df

    df_filtered = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ].copy()
    return df_filtered

def plot_price_history(df_price, selected_companies, start_date=None, end_date=None, normalize=False):
    if isinstance(selected_companies, str):
        selected_companies = [selected_companies]

    if df_price is None or df_price.empty or "Close" not in df_price.columns:
        return None

    df = df_price[df_price["Yritys"].isin(selected_companies)].copy()
    if df.empty:
        return None

    df = df.sort_values("Date")

    # --- 1. YKSI YHTIÖ VALITTUNA ---
    if len(selected_companies) == 1:
        df["MA50"] = df["Close"].rolling(window=50, min_periods=1).mean()
        df["MA200"] = df["Close"].rolling(window=200, min_periods=1).mean()

        df = filter_by_date(df, start_date, end_date)

        color_map = {
            "Sulkemishinta": "#00E5FF",
            "MA 50": "#FF9F0A",
            "MA 200": "#FF453A"
        }

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
        
        fig.update_traces(patch={"line": {"width": 2.5}}, selector={"name": "Sulkemishinta"})
        fig.update_traces(patch={"line": {"width": 1.5}}, selector={"name": "MA 50"})
        fig.update_traces(patch={"line": {"width": 1.5}}, selector={"name": "MA 200"})

    # --- 2. USEAMPI YHTIÖ VALITTUNA ---
    else:
        df = filter_by_date(df, start_date, end_date)

        if normalize:
            df = normalize_price_data(df, base_value=100)
            y_column = "Normalized"
            title_text = "Osakkeiden suhteellinen tuottokehitys (indeksoitu 100)"
            yaxis_label = "Kehitys (Alku = 100)"
            base_line = 100
        else:
            y_column = "Close"
            title_text = "Osakkeiden kurssivertailu (€)"
            yaxis_label = "Hinta (€)"
            base_line = None

        fig = px.line(
            df,
            x="Date",
            y=y_column,
            color="Yritys",
            title=title_text,
            labels={y_column: yaxis_label, "Yritys": "Yhtiö"}
        )

        fig.update_layout(yaxis_title=yaxis_label)

        if base_line is not None:
            fig.add_hline(y=base_line, line_dash="dash", line_color="gray", opacity=0.7)

    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Päivämäärä",
        legend_title="Tiedot",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def render_company_kpis(company_name, df_price_all, df_keyfigures, df_price_filtered=None):
    # 1. Alempi otsikko ja markkina-arvo: käytetään AINA koko datajoukon tuoreinta riviä
    price_full = df_price_all[df_price_all["Yritys"] == company_name].sort_values("Date") if df_price_all is not None else pd.DataFrame()
    
    if price_full.empty:
        st.warning(f"Ei hintadataa yhtiölle {company_name}.")
        return

    valid_price_full = price_full.dropna(subset=["Close"])
    if valid_price_full.empty:
        return

    absolute_latest = valid_price_full.iloc[-1]
    latest_close = absolute_latest["Close"]
    absolute_latest_date = absolute_latest["Date"]
    latest_date_str = absolute_latest_date.strftime("%d.%m.%Y") if hasattr(absolute_latest_date, "strftime") else str(absolute_latest_date)

    if "Marketcap" in absolute_latest and pd.notna(absolute_latest["Marketcap"]):
        marketcap = absolute_latest["Marketcap"]
    elif "Marketcap" in valid_price_full.columns and not valid_price_full["Marketcap"].dropna().empty:
        marketcap = valid_price_full["Marketcap"].dropna().iloc[-1]
    else:
        key_temp = df_keyfigures[df_keyfigures["Yritys"] == company_name] if df_keyfigures is not None else pd.DataFrame()
        marketcap = key_temp["Marketcap"].iloc[0] if not key_temp.empty and "Marketcap" in key_temp.columns else None

    # 2. Ylempi otsikko ja kortit: elävät valitun aikavälin mukaan (df_price_filtered)
    df_use = df_price_filtered if df_price_filtered is not None and not df_price_filtered.empty else price_full
    price_filtered = df_use[df_use["Yritys"] == company_name].sort_values("Date")
    valid_price_df = price_filtered.dropna(subset=["Close"])

    if valid_price_df.empty:
        valid_price_df = valid_price_full

    first = valid_price_df["Close"].iloc[0]
    highest = valid_price_df["Close"].max()
    lowest = valid_price_df["Close"].min()

    first_date = valid_price_df["Date"].iloc[0]
    filtered_latest_date = valid_price_df["Date"].iloc[-1]

    first_date_str = first_date.strftime("%d.%m.%Y") if hasattr(first_date, "strftime") else str(first_date)
    filtered_latest_date_str = filtered_latest_date.strftime("%d.%m.%Y") if hasattr(filtered_latest_date, "strftime") else str(filtered_latest_date)

    price_change_eur = valid_price_df["Close"].iloc[-1] - first
    change_pct = ((valid_price_df["Close"].iloc[-1] - first) / first) * 100

    key = df_keyfigures[df_keyfigures["Yritys"] == company_name] if df_keyfigures is not None else pd.DataFrame()

    pe = key["Trailing P/E"].iloc[0] if "Trailing P/E" in key.columns and not key.empty else None
    pb = key["P/B"].iloc[0] if "P/B" in key.columns and not key.empty else None
    ps = key["Trailing P/S"].iloc[0] if "Trailing P/S" in key.columns and not key.empty else None

    div_col = None
    for c in ["Osinko % (Trailing)", "Osinko-%", "Dividend Yield"]:
        if key is not None and c in key.columns:
            div_col = c
            break

    div_yield = key[div_col].iloc[0] if div_col and not key.empty else None
    eps = key["Trailing EPS"].iloc[0] if "Trailing EPS" in key.columns and not key.empty else None

    # --- UI ---
    st.subheader(f"📈 Kurssiyhteenveto | Valittu aikaväli: {first_date_str} – {filtered_latest_date_str}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ylin kurssi", f"{highest:.2f} €")
    c2.metric("Alin kurssi", f"{lowest:.2f} €")
    c3.metric("Muutos valitulla aikavälillä", f"{price_change_eur:+.2f} €", delta=f"{change_pct:.2f} %")

    st.write("")
    
    # Alempi otsikko lukittuna tuoreimmalla päivällä ja päätöskurssilla
    st.subheader(f"📊 Tunnusluvut | Päätöskurssi {latest_close:.2f} € ({latest_date_str})")
    
    k1, k2, k3 = st.columns(3)
    k1.metric("P/E (Trailing)", "-" if pd.isna(pe) else f"{pe:.2f}")
    k2.metric("P/S (Trailing)", "-" if pd.isna(ps) else f"{ps:.2f}")
    k3.metric("P/B", "-" if pd.isna(pb) else f"{pb:.2f}")

    st.write("")

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
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        title="",
        xaxis_title="Kvarttaali",
        yaxis_title=f"{metric} ({'€' if metric == 'EPS' else 'M€'})",
        template="plotly_white",
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=10, b=20)
    )

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px; margin-bottom: 10px;">
            <h3 style="margin: 0; font-size: 1.3rem;">{company_name} – {metric} kvartaaleittain</h3>
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="
                    width: 250px;
                    height: 14px;
                    background: linear-gradient(to right, #e0f2fe, #0284c7, #030712);
                    border-radius: 4px;
                "></div>
                <span style="font-size: 0.82rem; color: #6b7280; font-family: monospace;">
                    Vaaleampi = alempi tulos, tummempi = suurempi tulos
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
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

def create_comparison_table(
    df_price, 
    df_keyfigures, 
    df_info, 
    selected_companies, 
    start_date=None, 
    end_date=None
):
    rows = []
    if isinstance(selected_companies, str):
        selected_companies = [selected_companies]

    global_latest_date = None
    global_first_date = None

    for company in selected_companies:
        prices = df_price[df_price["Yritys"] == company] if df_price is not None else pd.DataFrame()

        if start_date is not None and end_date is not None and not prices.empty:
            prices = filter_by_date(prices, start_date, end_date)

        prices = prices.sort_values("Date") if not prices.empty else pd.DataFrame()

        if prices.empty:
            continue

        valid_prices = prices.dropna(subset=["Close"])
        if valid_prices.empty:
            continue

        valid_close = valid_prices["Close"]
        start_price = valid_close.iloc[0]
        end_price = valid_close.iloc[-1]

        high = valid_close.max()
        low = valid_close.min()

        first_date = valid_prices["Date"].iloc[0]
        latest_date = valid_prices["Date"].iloc[-1]

        if global_first_date is None or first_date < global_first_date:
            global_first_date = first_date
        if global_latest_date is None or latest_date > global_latest_date:
            global_latest_date = latest_date

        price_change_eur = end_price - start_price
        change_pct = ((end_price - start_price) / start_price) * 100

        info = df_info[df_info["Yritys"] == company] if df_info is not None and not df_info.empty else pd.DataFrame()
        kf = df_keyfigures[df_keyfigures["Yritys"] == company] if df_keyfigures is not None and not df_keyfigures.empty else pd.DataFrame()

        sector = "-"
        if not info.empty and "Sektori" in info.columns:
            sector = info.iloc[0]["Sektori"]

        marketcap = None
        if "Marketcap" in prices.columns and not prices["Marketcap"].dropna().empty:
            marketcap = prices["Marketcap"].dropna().iloc[-1]
        elif not kf.empty and "Marketcap" in kf.columns:
            marketcap = kf.iloc[0]["Marketcap"]

        # Skaalataan suoraan miljardeiksi, jotta luku pysyy pienenä (esim. 58.76) ja lajittelu toimii
        if pd.notnull(marketcap):
            marketcap_val = float(marketcap) / 1000 if float(marketcap) >= 1000 else float(marketcap)
        else:
            marketcap_val = None

        rows.append({
            "Yhtiö": company,
            "Toimiala": sector,
            "Viimeisin (€)": end_price,
            "Ylin (€)": high,
            "Alin (€)": low,
            "Tuotto (€)": price_change_eur,
            "Muutos %": change_pct,
            "Markkina-arvo": marketcap_val
        })

    first_date_str = global_first_date.strftime("%d.%m.%Y") if global_first_date and hasattr(global_first_date, "strftime") else ""
    latest_date_str = global_latest_date.strftime("%d.%m.%Y") if global_latest_date and hasattr(global_latest_date, "strftime") else ""

    # Lyhyet otsikot taulukkoon
    viimeisin_col_title = "Viimeisin (€)"
    marketcap_col_title = "Markkina-arvo (mrd €)"

    table = pd.DataFrame(rows)

    if not table.empty:
        table = table.rename(columns={
            "Viimeisin (€)": viimeisin_col_title,
            "Markkina-arvo": marketcap_col_title
        })

    return table, latest_date_str, first_date_str