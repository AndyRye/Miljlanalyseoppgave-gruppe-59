import requests
import pandas as pd
import json
from datetime import datetime
from requests.auth import HTTPBasicAuth
import numpy as np
import matplotlib.pyplot as plt 
from scipy.stats import zscore
from scipy import stats  # Added missing import
from ipywidgets import interact
import plotly.graph_objects as go
import os 
import webbrowser
import seaborn as sns
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_collection.frost import FrostAPI
from src.analysis.data_analysis import DataAnalyse

class DataPlotting: 

    def __init__(self, data):
        self.data = data

    def plot_histogram(self,kolonne, filnavn="Visualisering.png"):

        if not self.data.empty:
            plt.figure(figsize=(8, 6))
            sns.histplot(self.data[kolonne], kde=True, color='skyblue', edgecolor='black')
            plt.axvline(self.data[kolonne].mean(), color='red',linestyle='--', label=f'mean:{self.data[kolonne].mean():.2f}')
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
            numerical_columns = self.data.select_dtypes(include=['float64', 'int64']).columns

            plt.figure(figsize=(12, 8))
            self.data[numerical_columns].boxplot()
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
            numerical_columns = self.data.select_dtypes(include=['float64', 'int64']).columns
            korrelasjon_matrise = self.data[numerical_columns].corr()

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
            numerical_columns = self.data.select_dtypes(include=['float64', 'int64']).columns

            if len(numerical_columns) > 4:
                numerical_columns = numerical_columns[:4]

            pair_grid = sns.pairplot(self.data[numerical_columns], height=2.5, diag_kind='kde')
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

                ax.plot(self.data.index, rolling_mean, 'r--', label='Glidende mean (3 punkter)')
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
        if kolonne == "temperature" and "temperature (C)" in yr_data.columns:
            yr_kolonne = "temperature (C)"
            
        elif kolonne == "wind_speed" and "Windspeed (m/s)" in yr_data.columns:
            yr_kolonne = "Windspeed (m/s)"
        
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
            "mean": round(float(np.mean(frost_data[frost_kolonne])), 2),
            "Median": round(float(np.median(frost_data[frost_kolonne])), 2),
            "std_dev": round(float(np.std(frost_data[frost_kolonne])), 2)
        }

        yr_stats = {
            "mean": round(float(np.mean(yr_data[yr_kolonne])), 2),
            "Median": round(float(np.median(yr_data[yr_kolonne])), 2),
            "std_dev": round(float(np.std(yr_data[yr_kolonne])), 2)
        }

        print(f"\nStatistikk for {kolonne}:")
        print(f"Frost (Historisk): mean={frost_stats['mean']}, Median={frost_stats['Median']}, Std.avvik={frost_stats['std_dev']}")
        print(f"Yr (Prognose): mean={yr_stats['mean']}, Median={yr_stats['Median']}, Std.avvik={yr_stats['std_dev']}")

        return {
            "frost": frost_stats,
            "yr": yr_stats
        }

api = FrostAPI()
df_periode = api.fetch_data_for_periode("2023-01-01", "2023-02-01")

if not df_periode.empty:
    print(df_periode.head())
    print(df_periode.describe())
    
    
    analyzer = DataAnalyse(df_periode)
    
  
    print("\nStatistical measures:")
    stats = analyzer.beregn_alle_statistikker()
    print(stats)
    
   
    print("\nCorrelation analysis:")
    corr = analyzer.analyse_correlastion()
    print(corr)
    
   
    analyzer.plot_histogram("temperature")
    analyzer.plot_box_plot()
    analyzer.plot_korrelasjonsmatrise()  # Make sure to fix the typo in this method
    analyzer.plot_tidserie("temperature")
    analyzer.plot_tidsserie_med_statistikk("temperature")
else:
    print("Ingen data funnet")


print("DataAnalyse class defined successfully")
test_data = pd.DataFrame({'temperature': [1, 2, 3]})
test_analyzer = DataAnalyse(test_data)
print("DataAnalyse object created successfully")


















