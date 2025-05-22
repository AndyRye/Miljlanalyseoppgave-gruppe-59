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

import webbrowser
import seaborn as sns

from src.data_collection import FrostAPI
from src.analysis import DataAnalysis


class DataPlotting: 

    def __init__(self, data):
        #Removes duplicated indexes
        data = data[~data.index.duplicated(keep='first')]
        self.data = data

    def plot_histogram(self, column, title):
        if self.data.empty or column not in self.data.columns:
            return None
        titles = ["Temperatur (C)", "Vind (m/s)", "Skydekke (%)"]
        for i in range(len(titles)):
            if title in titles[i]:
                if i == 2:
                    values = self.data[column].dropna()*10
                else:
                    values = self.data[column].dropna()
                mean_val = values.mean()
                median_val = values.median()

                fig = go.Figure()

                fig.add_trace(go.Histogram(
                    x=values,
                    nbinsx=30,
                    name=column,
                    marker_color='skyblue',
                    opacity=0.75
                ))


                fig.add_vline( x=mean_val, line=dict(color='red', dash='dash'))
                fig.add_vline(x=median_val, line=dict(color='green', dash='dot'))

                fig.add_annotation(
                    x=0,
                    y=1.05,
                    yref='paper',
                    xref='paper',
                    text=f'Gjennomsnitt: {mean_val:.2f}',
                    font =dict(color='red'),
                    showarrow=False
                    
                )
                fig.add_annotation(
                    x=1,
                    y=1.05,
                    yref='paper',
                    xref='paper',
                    text=f'Median: {median_val:.2f}',
                    font =dict(color='green'),
                    showarrow=False
                )
                
                fig.update_layout(
                    title=f'Interaktivt histogram for {title}',
                    xaxis_title=titles[i],
                    yaxis_title='Frekvens',
                    bargap=0.05,
                    template='plotly_white'
                )

                return fig

    def plot_box_plot(self):
        if not self.data.empty:
            import plotly.express as px
            import pandas as pd

            # Henter numeriske kolonner
            numerical_data = self.data.select_dtypes(include=['float64', 'int64'])

            # Konverterer til "long format" for Plotly
            melted_df = numerical_data.reset_index().melt(id_vars=numerical_data.index.name or 'index', 
                                                        var_name='Variabel', value_name='Verdi')

            fig = px.box(
                melted_df,
                x='Variabel',
                y='Verdi',
                title='Boxplot av Værvariabler',
                points='all',  # Vis datapunkter også
                template='plotly_white'
            )

            fig.update_layout(
                xaxis_title='Variabel',
                yaxis_title='Verdi',
                xaxis_tickangle=-45,
                height=600
            )

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
            import plotly.express as px

            numerical_columns = self.data.select_dtypes(include=['float64', 'int64']).columns
            if len(numerical_columns) > 4:
                numerical_columns = numerical_columns[:4]  # Begrens for tydelig visning

            fig = px.scatter_matrix(
                self.data,
                dimensions=numerical_columns,
                title='Parvise relasjoner mellom værvariablene',
                height=700,
                width=700,
                labels={col: col.capitalize() for col in numerical_columns}
            )

            fig.update_traces(diagonal_visible=True, marker=dict(size=5, opacity=0.6))
            fig.update_layout(
                template='plotly_white',
                dragmode='select'
            )

            return fig
        return None



    def plot_timeseries(self, column, title_name):
        titles = ["Temperatur (C)", "Vind (m/s)", "Skydekke (%)"]
        if not self.data.empty and column in self.data.columns:
            for i in range(len(titles)):
                if title_name in titles[i]:
                    if i == 2:
                        values = self.data[column].dropna()*10
                    else:
                        values = self.data[column].dropna()
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=self.data.index, 
                        y=values, 
                        mode='lines+markers', 
                        name=column,
                        line=dict(color='orange')
                    ))
                    fig.update_layout(
                        title=f'Interaktiv Tidsserie for {title_name}',
                        xaxis_title='Tid', 
                        yaxis_title=titles[i], 
                        xaxis=dict(rangeslider=dict(visible=True)), 
                        template='plotly_white'
                    )
                    return fig
        return None


    def plot_timeseries_with_statistics(self, column, title):
        if not self.data.empty and column in self.data.columns:
            import plotly.graph_objects as go

            values = self.data[column].dropna()
            rolling_mean = values.rolling(window=3, min_periods=1).mean()
            rolling_std = values.rolling(window=3, min_periods=1).std()

            fig = go.Figure()

            # Faktiske verdier
            fig.add_trace(go.Scatter(
                x=self.data.index,
                y=values,
                mode='lines+markers',
                name='Faktiske verdier',
                line=dict(color='blue')
            ))

            # Glidende gjennomsnitt
            fig.add_trace(go.Scatter(
                x=self.data.index,
                y=rolling_mean,
                mode='lines',
                name='Glidende gjennomsnitt (3 punkter)',
                line=dict(color='red', dash='dash')
            ))

            # ±1 standardavvik som område
            fig.add_trace(go.Scatter(
                x=self.data.index.tolist() + self.data.index[::-1].tolist(),
                y=(rolling_mean + rolling_std).tolist() + (rolling_mean - rolling_std)[::-1].tolist(),
                fill='toself',
                fillcolor='rgba(255, 0, 0, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                name='±1 standardavvik'
            ))

            fig.update_layout(
                title=f'Tidsserie av {title} med statistiske mål',
                xaxis_title='Tid',
                yaxis_title=title.capitalize(),
                template='plotly_white',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(rangeslider=dict(visible=True))
            )

            return fig
        return None
    


















