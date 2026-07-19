import yfinance as yf 
import pandas as pd
import datetime

companies = {
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

start_date = "2024-01-01"
end_date = datetime.datetime.now().date()

#Haetaan kurssikehitys
def get_price_data(companies, start=start_date, end=end_date):
    all_data = []
    
    for name, info in companies.items():
        ticker = info["ticker"]
        stock = yf.Ticker(ticker)
        data = stock.history(start=start, end=end)
        
        data.reset_index(level=0, inplace=True)
        data["Yritys"] = name
        all_data.append(data)
        
    return pd.concat(all_data, ignore_index=True)

#Haetaan infodata
def get_info_data(companies):
    all_data = []
    
    for name, info in companies.items():
        ticker = info["ticker"]
        stock = yf.Ticker(ticker)
        data = stock.info.get("sector")
        
        all_data.append({
            "Yritys": name,
            "Sektori": data
        })
    
    return pd.DataFrame(all_data)

# Ladataan P/E (Trailing, Forward), Market Cap, P/B, PS(Trailing 12months) , EPS (Current year, Trailing, Forward), MA50, MA200
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
        
        all_data.append({
            "Yritys": name,
            "Trailing P/E": trailingpe,
            "Forward PE": forwardpe,
            "Marketcap": marketcap,
            "MA50": avg50,
            "MA200": avg200,
            "P/B": pb,
            "EPS Current year": epscurrent,
            "Trailing EPS": trailingeps,
            "Forward EPS": forwardeps,
            "Trailing PS": trailingps
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
            all_data.append({
                "Yritys": name,
                "Neljännes": quarter,
                "Liikevaihto": stmt.loc["Total Revenue", quarter] if "Total Revenue" in stmt.index else None,
                "Nettotulos": stmt.loc["Net Income", quarter] if "Net Income" in stmt.index else None,
                "EPS": stmt.loc["Basic EPS", quarter] if "Basic EPS" in stmt.index else None
            })
            
    return pd.DataFrame(all_data)

#Haetaan vuosittaiset tulokset
def get_income_stmt(companies):
    all_data = []
    
    for name, info in companies.items():
        ticker = info["ticker"]
        stock = yf.Ticker(ticker)
        stmt = stock.income_stmt
        
        for year in stmt.columns:
            all_data.append({
                "Yritys": name,
                "Vuosi": year,
                "Liikevaihto": stmt.loc["Total Revenue", year] if "Total Revenue" in stmt.index else None,
                "Nettotulos": stmt.loc["Net Income", year] if "Net Income" in stmt.index else None,
                "EPS": stmt.loc["Basic EPS", year] if "Basic EPS" in stmt.index else None
            })
            
    return pd.DataFrame(all_data)

if __name__ == "__main__":
    price = get_price_data(companies)
    info = get_info_data(companies)
    keyfigures = get_keyfigures_data(companies)
    quarters = get_quarterly_stmt(companies)
    yearly = get_income_stmt(companies)
    
    ticker = yf.Ticker("QTCOM.HE")
    
    df = pd.DataFrame([ticker.info])
    # print(ticker.quarterly_income_stmt)
    
    print(yearly)