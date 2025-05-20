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
        data = data[~data.index.duplicated(keep='first')]
        self.data = data

    def plot_histogram(self, kolonne):
        if not self.data.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(self.data[kolonne], kde=True, color='skyblue', edgecolor='black', ax=ax)
            ax.axvline(self.data[kolonne].mean(), color='red', linestyle='--', label=f'Gjennomsnitt: {self.data[kolonne].mean():.2f}')
            ax.axvline(self.data[kolonne].median(), color='green', linestyle='-.', label=f'Median: {self.data[kolonne].median():.2f}')
            ax.set_title(f"Histogram for {kolonne}")
            ax.set_xlabel(kolonne)
            ax.set_ylabel("Frekvens")
            ax.legend()
            plt.tight_layout()
            return fig
        return None

    def plot_box_plot(self):
        if not self.data.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            self.data.select_dtypes(include=['float64', 'int64']).boxplot(ax=ax)
            ax.set_title('Boxplot av Værvariabler')
            ax.set_ylabel('Verdi')
            plt.xticks(rotation=45)
            plt.tight_layout()
            return fig
        return None

    def plot_correlation_matrix(self):
        if not self.data.empty:
            fig, ax = plt.subplots(figsize=(10, 8))
            correlation_matrix = self.data.select_dtypes(include=['float64', 'int64']).corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, ax=ax)
            ax.set_title('Korrelasjonsmatrise av Værvariabler')
            plt.tight_layout()
            return fig
        return None


    def plot_pair_analysis(self):
        if not self.data.empty:
            numerical_columns = self.data.select_dtypes(include=['float64', 'int64']).columns
            if len(numerical_columns) > 4:
                numerical_columns = numerical_columns[:4]
            pair_grid = sns.pairplot(self.data[numerical_columns], height=2.5, diag_kind='kde')
            pair_grid.fig.suptitle('Parvise relasjoner mellom værvariablene', y=1.02)
            plt.tight_layout()
            return pair_grid.fig
        return None



    def plot_timeseries(self, column):
        if not self.data.empty and column in self.data.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=self.data.index, 
                y=self.data[column], 
                mode='lines+markers', 
                name=column, 
                line=dict(color='orange')
            ))
            fig.update_layout(
                title=f'Interaktiv Tidsserie for {column}',
                xaxis_title='Tid', 
                yaxis_title=column, 
                xaxis=dict(rangeslider=dict(visible=True)), 
                template='plotly_white'
            )
            return fig
        return None


    def plot_timeseries_with_statistics(self, column):
        if not self.data.empty and column in self.data.columns:
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.lineplot(x=self.data.index, y=self.data[column], label='Faktiske verdier', ax=ax)
            if len(self.data) > 3:
                rolling_mean = self.data[column].rolling(window=3, min_periods=1).mean()
                rolling_std = self.data[column].rolling(window=3, min_periods=1).std()
                ax.plot(self.data.index, rolling_mean, 'r--', label='Glidende gjennomsnitt (3 punkter)')
                ax.fill_between(self.data.index, rolling_mean - rolling_std, rolling_mean + rolling_std, color='r', alpha=0.2, label='±1 standardavvik')
            ax.set_title(f'Tidsserie av {column} med statistiske mål')
            ax.set_xlabel('Tid')
            ax.set_ylabel(column)
            ax.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            return fig
        return None

    def compare_with_yr(self, frost_data, yr_data, column, filename="Comparison.png"):

        if frost_data.empty or yr_data.empty:
            print("Ingen data tilgjengelig for sammenligning")
            return

        if column not in frost_data.columns or column not in yr_data.columns:
            print(f"Kolonnen '{column}' finnes ikke i begge datasett")
            return

        if not isinstance(frost_data.index, pd.DatetimeIndex):
            frost_data = frost_data.reset_index()
            frost_data["tidspunkt"] = pd.to_datetime(frost_data["tidspunkt"])
            frost_data.set_index('tidspunkt', inplace=True)

        if not isinstance(yr_data.index, pd.DatetimeIndex):
            yr_data['Tid'] = pd.to_datetime(yr_data['Tid'])
            yr_data.set_index('Tid', inplace=True)

        #Tilpasser kolonnene for sammenligning
        frost_column = column
        yr_column = column
        if column == "temperature" and "temperature (C)" in yr_data.columns:
            yr_column = "temperature (C)"

        elif column == "wind_speed" and "Windspeed (m/s)" in yr_data.columns:
            yr_column = "Windspeed (m/s)"

        plt.figure(figsize=(12,6))
        plt.plot(frost_data.index, frost_data[frost_column], 'b-', label='Frost(historisk)')
        plt.plot(yr_data.index, yr_data[yr_column], 'r-', label='Yr (prognose)')

        plt.title(f'Sammenlining av {column} -Historisk vs Prognose')
        plt.xlabel('Tid')
        plt.ylabel(column)
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        print(f"Sammenligning lagret som {filename}")

        frost_stats = {
            "mean": round(float(np.mean(frost_data[frost_column])), 2),
            "Median": round(float(np.median(frost_data[frost_column])), 2),
            "std_dev": round(float(np.std(frost_data[frost_column])), 2)
        }

        yr_stats = {
            "mean": round(float(np.mean(yr_data[yr_column])), 2),
            "Median": round(float(np.median(yr_data[yr_column])), 2),
            "std_dev": round(float(np.std(yr_data[yr_column])), 2)
        }

        print(f"\nStatistikk for {column}:")
        print(f"Frost (Historisk): mean={frost_stats['mean']}, Median={frost_stats['Median']}, Std.avvik={frost_stats['std_dev']}")
        print(f"Yr (Prognose): mean={yr_stats['mean']}, Median={yr_stats['Median']}, Std.avvik={yr_stats['std_dev']}")

        return {
            "frost": frost_stats,
            "yr": yr_stats
        }
if __name__ == "__main__":
    api = FrostAPI()
    df_periode = api.fetch_data_for_periode("2023-01-01", "2023-02-01")

    if not df_periode.empty:
        print(df_periode.head())
        print(df_periode.describe())


        analyzer = DataAnalyse(df_periode)

        print("\nStatistical measures:")
        stats = analyzer.calculate_all_statistics()
        print(stats)

        print("\nCorrelation analysis:")
        corr = analyzer.analyse_correlation()
        print(corr)


        analyzer.plot_histogram("temperatur")
        analyzer.plot_box_plot()
        analyzer.plot_correlation_matrix()
        analyzer.plot_time_series("temperatur")
        analyzer.plot_time_series_with_statistics("temperatur")
    else:
        print("Ingen data funnet")


print("DataAnalyse class defined successfully")
test_data = pd.DataFrame({'temperature': [1, 2, 3]})
test_analyzer = DataAnalyse(test_data)
print("DataAnalyse object created successfully")


















