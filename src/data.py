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

def get_price_data(companies, start=start_date, end=end_date):
    all_data = {}
    
    for name, info in companies.items():
        ticker = info["ticker"]
        stock = yf.Ticker(ticker)
        data = stock.history(start=start, end=end)
        
        all_data[name] = data
        
    return all_data

#Haetaan infodata
def get_info_data(companies, start=start_date, end=end_date):
    pass


if __name__ == "__main__":
    data = get_price_data(companies)
    print(data["QT Group"].head())