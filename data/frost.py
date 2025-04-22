import requests
import pandas as pd
import json
from datetime import datetime
from requests.auth import HTTPBasicAuth
import numpy as np
import matplotlib.pyplot as plt 
from scipy.stats import zscore
from ipywidgets import interact
import plotly.graph_objects as go
import os 
import webbrowser

class FrostAPI:
    def __init__(self):
        self.client_id = "0933ff3e-f805-41e8-a90f-d13658c62567"
        self.client_secret = "06e27da9-90dd-4eec-aeb9-ca90fd6ef805"
        self.endpoint = 'https://frost.met.no/observations/v0.jsonld'
        self.params = {
            "sources" : 'SN18700,SN90450', 
            "elements" : ['air_temperature','cloud_area_fraction', 'wind_speed'], 
            "referencetime" : ""
           }
    
    def hent_elementverdi(self, observations, element_id):
        for o in observations:
            if o["elementId"] == element_id:
                return o["value"]
        return None

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
                "temperatur": self.hent_elementverdi(obs["observations"], "air_temperature"),
                "skydekke": self.hent_elementverdi(obs["observations"], "cloud_area_fraction"),
                "vind": self.hent_elementverdi(obs["observations"], "wind_speed")
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
        
api = FrostAPI()
df_periode = api.hent_data_for_periode("2023-01-01", "2023-01-07")

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
        while True: 
            z_scores = np.abs(zscore(self.data[kolonne]))
            ny_data = self.data[z_scores < z_score_threshold]

            if len(ny_data) == len(self.data):
                break
            self.data = ny_data

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


    def plot_tidserie(self, kolonne, filnavn="Interaktiv.html"):
        print("Antall rader i data:", len(self.data))
        print("Kolonner:", self.data.columns)

        if not self.data.empty:
            try:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=self.data.index, 
                    y=self.data[kolonne], 
                    mode='lines+markers', 
                    name=kolonne, 
                    line=dict(color='orange')
                ))
                fig.update_layout(
                    title=f'Interaktiv Tidsserie for {kolonne}',
                    xaxis_title='Tid', 
                    yaxis_title=kolonne, 
                    xaxis=dict(rangeslider=dict(visible=True)), 
                    template='plotly_white'
                )
                fig.write_html(filnavn)
                print(f"Interaktiv plott lagret som: {filnavn}")

                print("Lagringsmappe:", os.getcwd())

                webbrowser.open(filnavn)
            except Exception as e:
                print(f"Feil ved plotting: {e}")
        else:
            print(" Ingen data tilgjengelig for interaktiv plott")


        


    
analyse = DataAnalyse(df_periode) 

statistikk = analyse.beregn_statistikk("temperatur")
print("Statistikk", statistikk)

analyse.fjern_uteliggere("temperatur")
analyse.plot_histogram("temperatur", filnavn = "Visualisering.png")
analyse.plot_tidserie("temperatur", filnavn = "Interaktiv.html")











"""


class Weather_Plotting:
    def __init__(self, weather_data):

        if isinstance(weather_data, list):
            self.df = WeatherDataCleaner(weather_data).clean()
        elif isinstance(weather_data, pd.DataFrame):
            self.df = weather_data
        else:
            raise ValueError("Ikke kompatibelt Dataformat")
        
        #sjekker at dataen som kommer inn i klassen minst har kolonnene ["Tid", "Temperatur (C)", "Vindhastighet (m/s)"]

        expeted_colum = ["Tid", "Temperatur (C)", "Vindhastighet (m/s)"]
        if not all(col in self.df.columns for col in expeted_colum):
            raise ValueError(f"Datasettet mangler påkrevde kolonner, forventet:{expeted_colum}")
        
        #konverterer Tid til Datetime
        self.df["Tid"] = pd.to_datetime(self.df["Tid"]) 


    def Plott_Temperatur(self):
        fig, ax1 = plt.subplots(figsize=(7,5))
        sns.lineplot(x = "Tid",  y = "Temperatur (C)", color = "blue", data = self.df, ax = ax1)
        ax1.set_xlabel("tid")
        ax1.set_ylabel("Temperatur")
        ax1.set_title("Temperatur Over Tid")
        ax1.grid(True)
        plt.xticks(rotation = 30)
        plt.show()

    def Scatterplott_Temperatur(self):
        fig, ax2 = plt.subplots(figsize=(7,5))
        
        sns.scatterplot(x = "Tid", y= "Temperatur (C)", hue = "Temperatur (C)", palette = "coolwarm", data=self.df, ax = ax2)
        ax2.set_xlabel("tid")
        ax2.set_ylabel("Temperatur")
        ax2.set_title("Temperatur Over Tid")
        plt.xticks(rotation = 30)
        plt.show()

    def Plott_Vindhastighet(self):
        fig, ax3 = plt.subplots(figsize=(7,5))

        ax3.plot(self.df["Tid"], self.df["Vindhastighet (m/s)"], color = "blue")
        ax3.set_title("Vindhastighet")
        ax3.set_xlabel("Tid")
        ax3.set_ylabel("vindhastighet")
        ax3.legend(["Vindhastighet"])
        plt.xticks(rotation = 30)
        plt.show()
    def Plott_samtidig(self):
        fig, (ax1, ax2, ax3)= plt.subplots(3, 1, figsize=(15,10))

        sns.lineplot(x = "Tid",  y = "Temperatur (C)", color = "blue", data = self.df, ax = ax1)
        ax1.set_xlabel("tid")
        ax1.set_ylabel("Temperatur")
        ax1.set_title("Temperatur Over Tid")
        ax1.grid(True)
        plt.xticks(rotation = 30)
        

        sns.scatterplot(x = "Tid", y= "Temperatur (C)", hue = "Temperatur (C)", palette = "coolwarm", data=self.df, ax = ax2)
        ax2.set_xlabel("tid")
        ax2.set_ylabel("Temperatur")
        ax2.set_title("Temperatur Over Tid")
        plt.xticks(rotation = 30)
        

        ax3.plot(self.df["Tid"], self.df["Vindhastighet (m/s)"], color = "blue")
        ax3.set_title("Vindhastighet")
        ax3.set_xlabel("Tid")
        ax3.set_ylabel("vindhastighet")
        ax3.legend(["Vindhastighet"])
        plt.xticks(rotation = 30)
        plt.show()

    def Plott_Statistisk_Fordeling(self, kolonne):
        #Plotter histogram med kurvetilpasning for å vise datafordeling
        plt.figure(figsize=(10, 6))
    
        sns.histplot(self.df[kolonne], kde=True, color="steelblue")

        plt.axvline(self.df[kolonne].mean(), color='red', linestyle='--', label=f'Gjennomsnitt: {self.df[kolonne].mean():.2f}')
        plt.axvline(self.df[kolonne].median(), color='green', linestyle='-.', label=f'Median: {self.df[kolonne].median():.2f}')

        plt.title(f'Statistisk fordeling av {kolonne}')
        plt.xlabel(kolonne)
        plt.ylabel('Frekvens')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def Plott_Box_plot(self):
        #lager box plott for å identifisere utligger
        numeric_cols = self.df.select_dtypes(include=['float64','int64']).columns

        plt.figure(figsize=(12, 8))
        self.df[numeric_cols].boxplot()
        plt.title('Box Plot av Værvariabler')
        plt.ylabel('Verdi')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def Plott_Korrelasjonsmatrise(self):
        #Visualiserer korrelasjon mellom alle numeriske varibaler

        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        corr_matrix = self.df[numeric_cols].corr()

        plt.figure(figsize=(10,8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='2f', linewidths=0.5)
        plt.title('Korrelasjonsmatrise av Værvariabler')
        plt.tight_layout()
        plt.show()

    def Plott_Par_Analyse(self):
        #Lager parvise plot for å vise forholdene mellom varibalene@

        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns

        if len(numeric_cols) > 4:
            numeric_cols = numeric_cols[:4]

        sns.pairplot(self.df[numeric_cols], height=2.5, diag_kind='kde')
        plt.suptitle('Parvise relasjoner mellom Værvariabler', y=1.02)
        plt.tight_layout()
        plt.show()

    def Plott_Tidsserie_Med_Statistikk(self, kolonne):
        #Her plotter vi en tidsserie med glidende gjennomsnitt og konfidensintervall
        fig, ax = plt.subplots(figsize=(12, 6))

        sns.lineplot(x='Tid', y=kolonne, data=self.df, label='Faktiske verdier', ax=ax)

        if len(self.df) > 3:
            rolling_mean = self.df[kolonne].rolling(window=3, min_periods=1).mean()
            rolling_std = self.df[kolonne].rolling(window= 3, min_periods=1).std()

            ax.plot(self.df['Tid'], rolling_mean, 'r--', label='Glidende gjennomsnitt( 3 punkter)')
            ax.fill_between(self.df['Tid'],
                            rolling_mean -rolling_std,
                            rolling_mean + rolling_std,
                            color='r', alpha=0.2, label='±1 Standardavvik')
            
            ax.set_title(f'Tidsserie av {kolonne} med statistiske mål')
            ax.set_xlabel('Tid')
            ax.set_ylabel(kolonne)
            ax.legend()
            plt.xticks(rotation= 45)
            plt.tight_layout()
            plt.show()"""

