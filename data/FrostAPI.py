import requests
import pandas as pd
import json
from datetime import datetime
from requests.auth import HTTPBasicAuth
import numpy as np
import matplotlib.pyplot as plt 
from scipy.stats import zscore
from ipywidgets import interact

class frostAPI:
    def __init__(self):
        self.client_id = "0933ff3e-f805-41e8-a90f-d13658c62567"
        self.client_secret = "06e27da9-90dd-4eec-aeb9-ca90fd6ef805"
        self.endpoint = 'https://frost.met.no/observations/v0.jsonld'
        self.params = {
            "sources" : 'SN18700,SN90450', 
            "elements" : 'air_temperature, pm10, pm2.5', 
            "referencetime" : ""
           }
        
    def hent_data(self, startdato, sluttdato):

        self.params["referencetime"] = f"{startdato}/{sluttdato}"

        response = requests.get( 
            self.endpoint,
            params = self.params,
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
        )
        
        if response.status_code != 200:
            raise Exception(f"Feil med forespørsel: {response.status_code} \n {response.text}")
        
        data = response.json().get("data", [])

        lst = []
        for obs in data:
            lst.append({
                "tidspunkt": obs["referenceTime"],
                "stasjon": obs["sourceId"],
                "temperatur": obs["observations"][0]["value"],
                "pm10": obs["observations"][1]["value"] if len(obs["observations"]) > 1 else None, 
                "pm2_5": obs["observations"][2]["value"] if len(obs["observations"]) > 2 else None
            })

        df = pd.DataFrame(lst)

        if not df.empty:
            df["tidspunkt"] = pd.to_datetime(df["tidspunkt"])
            df.set_index("tidspunkt", inplace=True)

        return df
    
    def hent_data_for_periode(self, start_dato, sluttdato, intervall="W"):
        start_date = pd.to_datetime(start_dato)
        end_date = pd.to_datetime(sluttdato)

        current_date = start_date
        all_data  = []

        while current_date < end_date:
            if intervall == "W":
                next_date = current_date + pd.DateOffset(weeks=1)
            elif intervall == "M":
                next_date = current_date + pd.DateOffset(month=1)
            else:
                raise ValueError("Ugyldig. Bruk 'W' for ukentlig eller 'M' for måndelig")
            
            if next_date > end_date:
                next_date = end_date

            print(f"Henter data fra {current_date.strftime('%Y-%m-%d')} til {next_date.strftime('%Y-%m-%d')}")
            df = self.hent_data(current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'))
            all_data.append(df)
            current_date = next_date
        
        if all_data:
            full_df = pd.concat(all_data)
            return full_df
        else:
            return pd.DataFrame()
        
api = weatherAPI()
df_periode = api.hent_data_for_periode("2020-01-01", "2024-12-31")

if not df_periode.empty:
    print(df_periode.head())
    print(df_periode.describe())
else:
    print("Ingen data funnet")


class DataAnalyse:
    def __init__(self, data):
        self.data = data

    def beregn_statistikk(self, kolonne):
        gjennomsnitt = round(float(np.mean(self.data[kolonne])), 2)
        median = round(float(np.median(self.data[kolonne])),2)
        std_avvik = round(float(np.std(self.data[kolonne])),2)

        return {
            "gjennomsnitt": gjennomsnitt,
            "median": median, 
            "standard avvik": std_avvik
        }
    
    def undersok_sammenheng(self, kolonne1, kolonne2):
        korrealasjon  = self.data[[kolonne1, kolonne2]].corr()
        return korrealasjon
    
    def fjern_uteliggere(self, kolonne, z_score_threshold=3):
        z_scores = np.abs(zscore(self.data[kolonne]))
        self.data = self.data[z_scores < z_score_threshold]

    def plot_histogram(self,kolonne, filnavn="Visualisering.png"):
        if not self.data.empty:
            plt.figure(figsize=(8, 6))
            plt.hist(self.data[kolonne], bins=20, color='skyblue', edgecolor='black')
            plt.title(f"Histogram for {kolonne}")
            plt.xlabel(kolonne)
            plt.ylabel("Frekvens")
            plt.tight_layout()
            plt.savefig(filnavn)
            plt.close()
            print(f"Histogram lagret som {filnavn}")
        else:
            print("ingen data tilgjenlig for plotting")

    def plot_tidserie(self, kolonne, filnavn="tidserie_plot.png"):
        if not self.data.empty:
            plt.figure(figsize=(10, 6))
            plt.plot(self.data.index, self.data[kolonne], color = "darkorange")
            plt.title(f"Tidsserie for {kolonne}")
            plt.xlabel("Tid")
            plt.xticks(rotation=45)
            plt.ylabel(kolonne)
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(filnavn)
            plt.close()
        else:
            print("Ingen data tilgjenlig for plotting")


    
analyse = DataAnalyse(df_periode) 

statistikk = analyse.beregn_statistikk("temperatur")
print("Statistikk", statistikk)

analyse.fjern_uteliggere("temperatur")
analyse.plot_histogram("temperatur", filnavn="Visualisering.png")
analyse.plot_tidserie("temperatur", filnavn="tidserie_plot.png")


