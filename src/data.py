import yfinance as yf 
import pandas as pd
import datetime

#Yhtiöt
COMPANIES = {
    "Nokia": {"ticker": "NOKIA.HE"},
    "Nordea": {"ticker": "NDA-FI.HE"},
    "Sampo": {"ticker": "SAMPO.HE"},
    "Kone": {"ticker": "KNEBV.HE"},
    "UPM-Kymmene": {"ticker": "UPM.HE"},
    "Neste": {"ticker": "NESTE.HE"},
    "Stora Enso R": {"ticker": "STERV.HE"},
    "Fortum": {"ticker": "FORTUM.HE"},
    "Metso": {"ticker": "METSO.HE"},
    "Wärtsilä": {"ticker": "WRT1V.HE"},
    "Outokumpu": {"ticker": "OUT1V.HE"},
    "Kesko B": {"ticker": "KESKOB.HE"},
    "Elisa": {"ticker": "ELISA.HE"},
    "Valmet": {"ticker": "VALMT.HE"},
    "Orion B": {"ticker": "ORNBV.HE"},
    "Konecranes": {"ticker": "KCR.HE"},
    "Kemira": {"ticker": "KEMIRA.HE"},
    "Huhtamäki": {"ticker": "HUH1V.HE"},
    "TietoEVRY": {"ticker": "TIETO.HE"},
    "SSAB B": {"ticker": "SSABBH.HE"},
    "Hiab" : {"ticker": "HIAB.HE"},
    "Lumo-Kodit": {"ticker": "LUMO.HE"},
    "Mandatum": {"ticker": "MANTA.HE"},
    "Nokian Renkaat" : {"ticker": "TYRES.HE"},
    "QT Group" : {"ticker": "QTCOM.HE"}
}

#Toimialojen suomennokset
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

start_date = "2024-01-01"
end_date = datetime.datetime.now().date()

#Haetaan kurssikehitys
def get_price_data(companies, start=start_date, end=end_date):
    all_data = []
    
    for name, info in companies.items():
        ticker = info["ticker"]
        stock = yf.Ticker(ticker)
        data = stock.history(start=start, end=end)
        total_shares = stock.info.get("sharesOutstanding")
        
        data.reset_index(level=0, inplace=True)
        data["Yritys"] = name
        data["Date"] = data["Date"].dt.tz_localize(None)
        data["Osakelkm"] = total_shares
        data["Marketcap"] = total_shares * data["Close"] / 1000000
        all_data.append(data)
        
    return pd.concat(all_data, ignore_index=True)

#Haetaan sektorit
def get_info_data(companies):
    all_data = []
    
    for name, info in companies.items():
        ticker = info["ticker"]
        stock = yf.Ticker(ticker)
        data_sector = stock.info.get("sector")
        sector = SECTOR_TRANSLATIONS.get(data_sector, data_sector)
        
        all_data.append({
            "Yritys": name,
            "Sektori": sector
        })
    
    return pd.DataFrame(all_data)

# Ladataan P/E (Trailing, Forward), Market Cap, P/B, PS(Trailing 12months) , EPS (Current year, Trailing, Forward), MA50, MA200, Osionko %
def get_keyfigures_data(companies):
    all_data = []
    
    for name, info in companies.items():
        ticker = info["ticker"]
        stock = yf.Ticker(ticker)
        trailingpe = stock.info.get("trailingPE")
        forwardpe = stock.info.get("forwardPE")
        marketcap = stock.info.get("marketCap")
        avg50 = stock.info.get("fiftyDayAverage")
        avg200 = stock.info.get("twoHundredDayAverage")
        pb = stock.info.get("priceToBook")
        trailingeps = stock.info.get("trailingEps")
        forwardeps = stock.info.get("forwardEps")
        epscurrent = stock.info.get("epsCurrentYear")
        trailingps = stock.info.get("priceToSalesTrailing12Months")
        trailing_yield = stock.info.get("trailingAnnualDividendYield") or stock.info.get("dividendYield")
        
        all_data.append({
            "Yritys": name,
            "Trailing P/E": trailingpe,
            "Forward P/E": forwardpe,
            "Marketcap": marketcap / 1000000,
            "MA50": avg50,
            "MA200": avg200,
            "P/B": pb,
            "EPS Current year": epscurrent,
            "Trailing EPS": trailingeps,
            "Forward EPS": forwardeps,
            "Trailing P/S": trailingps,
            "Osinko % (Trailing)": trailing_yield
        })
    
    return pd.DataFrame(all_data)

# Haetaan neljänneksien tulokset, Liikevaihto, EPS, Nettotulos
def get_quarterly_stmt(companies):
    all_data = []
    
    for name, info in companies.items():
        ticker = info["ticker"]
        stock = yf.Ticker(ticker)
        stmt = stock.quarterly_income_stmt
        
        for quarter in stmt.columns:
            q_num = ((quarter.month - 1) // 3) + 1
            formated_q = f"{quarter.year}Q{q_num}"
            all_data.append({
                "Yritys": name,
                "Kvarttaali": formated_q,
                "Liikevaihto": stmt.loc["Total Revenue", quarter] / 1000000 if "Total Revenue" in stmt.index else None,
                "Nettotulos": stmt.loc["Net Income", quarter] / 1000000 if "Net Income" in stmt.index else None,
                "EPS": stmt.loc["Basic EPS", quarter] if "Basic EPS" in stmt.index else None
            })
            
    return pd.DataFrame(all_data)

#Käytetään tätä funktioita visualisoinneissa. Tämä hakee CSV tiedostosta dataframeen tarvittavat asiat
def quarterly_data(path="Kvarttaalidata.csv"):
    df = pd.read_csv(path)
    
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
        
    return df

#Haetaan vuosittaiset tulokset
def get_income_stmt(companies):
    all_data = []
    
    for name, info in companies.items():
        ticker = info["ticker"]
        stock = yf.Ticker(ticker)
        stmt = stock.income_stmt
        
        for yearly in stmt.columns:
            year_formated = yearly.year
            all_data.append({
                "Yritys": name,
                "Vuosi": year_formated,
                "Liikevaihto": stmt.loc["Total Revenue", yearly] / 1000000 if "Total Revenue" in stmt.index else None,
                "Nettotulos": stmt.loc["Net Income", yearly]  / 1000000 if "Net Income" in stmt.index else None,
                "EPS": stmt.loc["Basic EPS", yearly] if "Basic EPS" in stmt.index else None
            })
            
    return pd.DataFrame(all_data)

##### TÄSTÄ ETEENPÄIN FUNKTIOT PÄIVITTÄÄ TUOTA KVARTTAALLIDATA CSV:TÄ. KÄYTETÄÄN MANUAALISESTI!
def find_new_quarters(existing_df, new_df):
    existing_keys = set(zip(existing_df["Yritys"], existing_df["Kvarttaali"]))
    new_rows = new_df[
        ~new_df[["Yritys", "Kvarttaali"]].apply(tuple, axis=1).isin(existing_keys)
    ].copy()

    return new_rows

def update_quarterly_csv(companies, path="Kvarttaalidata.csv"):
    existing_df = quarterly_data(path)
    fetched_df = get_quarterly_stmt(companies)

    new_rows = find_new_quarters(existing_df, fetched_df)

    if new_rows.empty:
        print("Ei uusia kvarttaaleja.")
        return existing_df

    updated_df = pd.concat([existing_df, new_rows], ignore_index=True)
    updated_df = updated_df.sort_values(["Yritys", "Kvarttaali"]).reset_index(drop=True)
    updated_df.to_csv(path, index=False)

    print(f"Lisättiin {len(new_rows)} uutta riviä CSV:hen.")
    return updated_df

if __name__ == "__main__":
    updated_quarters = update_quarterly_csv(COMPANIES, "Kvarttaalidata.csv")
    print(updated_quarters.tail())
    