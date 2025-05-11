import requests
import pandas as pd
import json
from datetime import datetime
from requests.auth import HTTPBasicAuth
import numpy as np
import matplotlib.pyplot as plt 
from scipy.stats import zscore
from scipy import stats  
from ipywidgets import interact
import plotly.graph_objects as go
import os 
import webbrowser
import seaborn as sns

class FrostAPI:
    def __init__(self):
        self.client_id = "0933ff3e-f805-41e8-a90f-d13658c62567"
        self.client_secret = "06e27da9-90dd-4eec-aeb9-ca90fd6ef805"
        self.endpoint = 'https://frost.met.no/observations/v0.jsonld'
        self.params = {
            
            "sources": 'SN18700,SN90450,SN50539,SN69100', 
            "elements": ','.join([
                "air_temperature","cloud_area_fraction","wind_speed"
            ]),
            "timeresolutions": 'PT1H',
            "referencetime": ''
        }
    
    def handle_missing_data(self, df):
    
        if df.empty:
            return df
        
    
        df_filled = df.copy()
    
        
        for station in df_filled['stasjon'].unique():
            station_data = df_filled[df_filled['stasjon'] == station]
        
            
            for col in ['temperatur', 'skydekke', 'vind']:
                if col in station_data.columns:
                    # First try forward fill
                    station_data[col] = station_data[col].ffill()
                    # Then try backward fill for any remaining NaNs
                    station_data[col] = station_data[col].bfill()
                
            
            df_filled.loc[df_filled['stasjon'] == station] = station_data
    
        return df_filled
    
    def hent_elementverdi(self, observations, element_id):
        for o in observations:
            if o["elementId"] == element_id:
                return o["value"]
        return None

    def hent_data(self, start, slutt):
        self.params["referencetime"] = f"{start}/{slutt}"
        r = requests.get(self.endpoint, params=self.params,
                         auth=(self.client_id, ""))
        r.raise_for_status()
        rows = {}
        for item in r.json().get("data", []):
            k = (item["referenceTime"], item["sourceId"])
            rows.setdefault(k, {"tidspunkt": item["referenceTime"],
                                "stasjon": item["sourceId"],
                                "temperatur": None,
                                "skydekke": None,
                                "vind": None})
            for o in item["observations"]:
                eid = o["elementId"]
                if eid == "air_temperature":
                    rows[k]["temperatur"] = o["value"]
                elif eid == "cloud_area_fraction":
                    rows[k]["skydekke"] = o["value"]
                elif eid == "wind_speed":
                    rows[k]["vind"] = o["value"]

        df = pd.DataFrame(rows.values()).set_index(
                 pd.to_datetime(pd.Series([r["tidspunkt"] for r in rows.values()])))
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
                next_date = current_date + pd.DateOffset(months=1)
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

            full_df = full_df.reset_index()

            if "tidspunkt" in full_df.columns:
                full_df = full_df.drop(columns=["tidspunkt"])

            full_df = full_df.rename(columns={"index": "tidspunkt"})

            full_df = full_df.drop_duplicates(subset=["tidspunkt", "stasjon"], keep="first")

            full_df["tidspunkt"] = pd.to_datetime(full_df["tidspunkt"])
            full_df = full_df.set_index("tidspunkt").sort_index()

            full_df = self.handle_missing_data(full_df)
            return full_df
        else:
            return pd.DataFrame()
        
api = FrostAPI()
df_periode = api.hent_data_for_periode("2023-01-01", "2024-01-07")

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
        median = round(float(np.median(self.data[kolonne])), 2)
        std_avvik = round(float(np.std(self.data[kolonne])), 2)
        min_verdi = round(float(np.min(self.data[kolonne])), 2)
        max_verdi = round(float(np.max(self.data[kolonne])), 2)
        skjevhet = round(float(stats.skew(self.data[kolonne].dropna())), 2)
        kurtose = round(float(stats.kurtosis(self.data[kolonne].dropna())), 2)

        return {
            "gjennomsnitt": gjennomsnitt,
            "median": median, 
            "standard avvik": std_avvik,
            "minimum": min_verdi,
            "maksimum": max_verdi,
            "skjevhet": skjevhet,
            "kurtose": kurtose

        }   
    
    def beregn_alle_statistikker(self):
        numeriske_kolonner = self.data.select_dtypes(include=['float64', 'int64']).columns

        stats_df = pd.DataFrame(index=['Gjennomsnitt', 'Median', 'Standardavvik', 'Min', 'Max', 'Skjevhet', 'Kurtose'])

        for kolonne in numeriske_kolonner:
            stats = self.beregn_statistikk(kolonne)
            stats_df[kolonne] = [
                stats["gjennomsnitt"],
                stats["median"],
                stats["standard avvik"],
                stats["minimum"],
                stats["maksimum"],
                stats["skjevhet"],
                stats["kurtose"],
            ]
        
        return stats_df
    
    
    def undersok_sammenheng(self, kolonne1, kolonne2):
        
        korrealasjon  = self.data[[kolonne1, kolonne2]].corr().iloc[0, 1]
        return round(korrealasjon, 2)
    
    def analyser_korrelasjon(self):

        numeriske_kolonner = self.data.select_dtypes(include=['float64', 'int64']).columns
        korrelasjon_matrise = self.data[numeriske_kolonner].corr()
        return korrelasjon_matrise
    
    def test_normalfordeling(self, kolonne):

        shapiro_test = stats.shapiro(self.data[kolonne].dropna())
        return {
            'statistikk': shapiro_test[0],
            'p-verdi': shapiro_test[1],
            'er_normalfordelt': shapiro_test[1] > 0.05
        }
    

    def fjern_uteliggere(self, kolonne, z_score_threshold=3):
        
        while True: 
            z_scores = np.abs(zscore(self.data[kolonne]))
            ny_data = self.data[z_scores < z_score_threshold]

            if len(ny_data) == len(self.data):
                break
            self.data = ny_data
        
        return self.data
    
    def haanterer_skjevhet(self, kolonne):

        originale_data = self.data[kolonne]
        skjevhet = originale_data.skew()

        if skjevhet > 1 and originale_data.min() >= 0:
            #En Logaritmisk transformasjon for positiv skjevhet
            transformerte_data = np.log1p(originale_data)
            return{
                'original': originale_data,
                'transformert': transformerte_data,
                'transformasjonstype': 'Log',
                'original_skjevhet': skjevhet,
                'transformert_skjevhet': transformerte_data.skew()
            }
        elif skjevhet < -1:
            #En eksponensiell transformasjon for negativ skjevhet
            transformerte_data = np.exp(originale_data/ originale_data.max())
            return{
                'original': originale_data,
                'transformert': transformerte_data,
                'transformasjonstype': 'Eksponensiell',
                'original_skjevhet': skjevhet,
                'transformert_skjevhet': transformerte_data.skew()
            }
        else:
            #Ingen transformasjon nødvendig
            return{
                'original': originale_data,
                'transformert': originale_data,
                'transformasjonstype': 'Ingen',
                'original_skjevhet': skjevhet,
                'transformert_skjevhet': skjevhet
            }

    def plot_histogram(self,kolonne, filnavn="Visualisering.png"):

        if not self.data.empty:
            plt.figure(figsize=(8, 6))
            sns.histplot(self.data[kolonne], kde=True, color='skyblue', edgecolor='black')
            plt.axvline(self.data[kolonne].mean(), color='red',linestyle='--', label=f'Gjennomsnitt:{self.data[kolonne].mean():.2f}')
            plt.axvline(self.data[kolonne].median(), color='green',linestyle='-.', label=f'Median:{self.data[kolonne].median():.2f}')

            plt.title(f"Histogram for {kolonne}")
            plt.xlabel(kolonne)
            plt.ylabel("Frekvens")
            plt.legend()
            plt.tight_layout()
            plt.savefig(filnavn)
            plt.close()
            print(f"Histogram lagret som {filnavn}")
        else:
            print("ingen data tilgjenlig for plotting")

    def plot_box_plot(self, filnavn="Boxplot.png"): #Identifiserer utliggere

        if not self.data.empty:
            numeriske_kolonner = self.data.select_dtypes(include=['float64', 'int64']).columns

            plt.figure(figsize=(12, 8))
            self.data[numeriske_kolonner].boxplot()
            plt.title('Boxplot av Værvariabler')
            plt.ylabel('Verdi')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(filnavn)
            plt.close()
            print(f'Box plot lagret som {filnavn}')
        else:
            print('Ingen data tilgjenglig for plotting')

    def plot_korrelasjonsmatrise(self, filnavn= "Korrelasjonsmatrise.png"):

        if not self.data.empty:
            numeriske_kolonner = self.data.select_dtypes(include=['float64', 'int64']).columns
            korrelasjon_matrise = self.data[numeriske_kolonner].corr()

            plt.figure(figsize=(10, 8))
            sns.heatmap(korrelasjon_matrise, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
            plt.title('Korrelasjonsmatrise av Værvariabler')
            plt.tight_layout()
            plt.savefig(filnavn)
            plt.close()
            print(f"Korrelasjonsmatrise lagret som {filnavn}")
        else:
            print("Ingen data tilgjenglig for plotting")

    def plot_par_analyse(self, filnavn="Paranalyse.png"):

        if not self.data.empty:
            numeriske_kolonner = self.data.select_dtypes(include=['float64', 'int64']).columns

            if len(numeriske_kolonner) > 4:
                numeriske_kolonner = numeriske_kolonner[:4]

            pair_grid = sns.pairplot(self.data[numeriske_kolonner], height=2.5, diag_kind='kde')
            pair_grid.fig.suptitle('Parvise relasjoner mellom værvariablene', y=1.02)
            plt.tight_layout()
            plt.savefig(filnavn)
            plt.close()
            print(f'Paranalyse lagret som {filnavn}')
        else:
            print("Ingen data tilgjenglig for plotting")
    




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


    def plot_tidsserie_med_statistikk(self, kolonne, filnavn="Tidsserie_med_statistikk.png"):

        if not self.data.empty:
            fig, ax = plt.subplots(figsize=(12, 6))

            sns.lineplot(x=self.data.index, y=self.data[kolonne], label='Fanktiske verdier', ax=ax)

            if len(self.data) > 3:
                rolling_mean = self.data[kolonne].rolling(window=3, min_periods=1).mean()
                rolling_std = self.data[kolonne].rolling(window=3, min_periods=1).std()

                ax.plot(self.data.index, rolling_mean, 'r--', label='Glidende gjennomsnitt (3 punkter)')
                ax.fill_between(self.data.index, rolling_mean - rolling_std, rolling_mean + rolling_std, color='r', alpha=0.2, label='±1 standardavvik')

                ax.set_title(f'Tidsserie av {kolonne} med statistiske mål')
                ax.set_xlabel('Tid')
                ax.set_ylabel(kolonne)
                ax.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(filnavn)
                plt.close()
                print(f'tidsserie med statistikk lagret som {filnavn}')
            else:
                print("Ingen data tilgjengelig for plotting")

    def sammenlign_med_yr(self, frost_data, yr_data, kolonne, filnavn="Sammenligning.png"):

        if frost_data.empty or yr_data.empty:
            print("Ingen data tilgjengelig for sammenligning")
            return
        
        if kolonne not in frost_data.columns or kolonne not in yr_data.columns:
            print(f"Kolonnen '{kolonne}' finnes ikke i begge datasett")
            return
        
        if not isinstance(frost_data.index, pd.DatetimeIndex):
            frost_data = frost_data.reset_index()
            frost_data["tidspunkt"] = pd.to_datetime(frost_data["tidspunkt"])
            frost_data.set_index('tidspunkt', inplace=True)

        if not isinstance(yr_data.index, pd.DatetimeIndex):
            yr_data['Tid'] = pd.to_datetime(yr_data['Tid'])
            yr_data.set_index('Tid', inplace=True)

        #Tilpasser kolonnene for sammenligning
        frost_kolonne = kolonne
        yr_kolonne= kolonne
        if kolonne == "temperatur" and "Temperatur (C)" in yr_data.columns:
            yr_kolonne = "Temperatur (C)"
            
        elif kolonne == "vind" and "Vindhastighet (m/s)" in yr_data.columns:
            yr_kolonne = "Vindhastighet (m/s)"
        
        plt.figure(figsize=(12,6))
        plt.plot(frost_data.index, frost_data[frost_kolonne], 'b-', label='Frost(historisk)')
        plt.plot(yr_data.index, yr_data[yr_kolonne], 'r-', label='Yr (prognose)')

        plt.title(f'Sammenlining av {kolonne} -Historisk vs Prognose')
        plt.xlabel('Tid')
        plt.ylabel(kolonne)
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(filnavn)
        plt.close()
        print(f"Sammenligning lagret som {filnavn}")

        frost_stats = {
            "Gjennomsnitt": round(float(np.mean(frost_data[frost_kolonne])), 2),
            "Median": round(float(np.median(frost_data[frost_kolonne])), 2),
            "Std_avvik": round(float(np.std(frost_data[frost_kolonne])), 2)
        }

        yr_stats = {
            "Gjennomsnitt": round(float(np.mean(yr_data[yr_kolonne])), 2),
            "Median": round(float(np.median(yr_data[yr_kolonne])), 2),
            "Std_avvik": round(float(np.std(yr_data[yr_kolonne])), 2)
        }

        print(f"\nStatistikk for {kolonne}:")
        print(f"Frost (Historisk): Gjennomsnitt={frost_stats['Gjennomsnitt']}, Median={frost_stats['Median']}, Std.avvik={frost_stats['Std_avvik']}")
        print(f"Yr (Prognose): Gjennomsnitt={yr_stats['Gjennomsnitt']}, Median={yr_stats['Median']}, Std.avvik={yr_stats['Std_avvik']}")

        return {
            "frost": frost_stats,
            "yr": yr_stats
        }

api = FrostAPI()
df_periode = api.hent_data_for_periode("2023-01-01", "2023-02-01")

if not df_periode.empty:
    print(df_periode.head())
    print(df_periode.describe())
    
    
    analyzer = DataAnalyse(df_periode)
    
  
    print("\nStatistical measures:")
    stats = analyzer.beregn_alle_statistikker()
    print(stats)
    
   
    print("\nCorrelation analysis:")
    corr = analyzer.analyser_korrelasjon()
    print(corr)
    
   
    analyzer.plot_histogram("temperatur")
    analyzer.plot_box_plot()
    analyzer.plot_korrelasjonsmatrise()  # Make sure to fix the typo in this method
    analyzer.plot_tidserie("temperatur")
    analyzer.plot_tidsserie_med_statistikk("temperatur")
else:
    print("Ingen data funnet")


print("DataAnalyse class defined successfully")
test_data = pd.DataFrame({'temperatur': [1, 2, 3]})
test_analyzer = DataAnalyse(test_data)
print("DataAnalyse object created successfully")









