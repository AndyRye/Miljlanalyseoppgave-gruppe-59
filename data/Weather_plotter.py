import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_collection.frost import FrostAPI
from src.visualization.plotting_frost_api import DataPlotting
from src.analysis.data_analysis import DataAnalyse




st.set_page_config(
    layout="wide",
    page_title="Væranalyse"
)

st.title("Vær App")
st.markdown("dette er en app som bruker historisk værdata til å predikere vær")

@st.cache_resource
def fetch_api():
    return FrostAPI()
API = fetch_api()


st.sidebar.header("Konfigurasjoner")
st.sidebar.markdown("Vi bruker data fra OSLO")

API.params["sources"] = 'SN18700,SN90450,SN50539,SN69100'

#setter datoer

initial_end_date = datetime.now()
initial_start_date= initial_end_date - timedelta(days=365) # setter 1 år mellom start å sluttdato

start_date = st.sidebar.date_input(
    "Fra dato", initial_start_date, max_value=initial_start_date #setter at du må ha et års mellomrom
)

end_date = st.sidebar.date_input(
    "Til dato", initial_end_date, max_value= initial_end_date
)

prediksjons_dager = st.sidebar.slider(
    "Antall dager du vil predikere",min_value=1, max_value=30, value=7
)

def fetch_data_time(start_date, end_date):

    with st.spinner("Henter data..."):
        try:
            data = API.fetch_data_for_periode(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), intervall="M")
        
            if data.empty:
                st.error("Fant ikke data")
                return None
            else:
                return data
        except:
            st.error("Fikk ikke til å hente data")
            return None
        

def plot_historical_data(df):
    if df is None or df.empty:
        st.error("Fant ikke data")
        return
    analyzer = DataPlotting(df)
    sub_tabs = st.tabs(["Temperatur grafer", "Vind grafer", "Skydekke grafer"])

    for column, tab in zip(["temperatur", "vind", "skydekke"], sub_tabs):
        with tab:
            st.subheader(f"{column.capitalize()} Histogram")
            fig_1 = analyzer.plot_histogram(column)
            st.pyplot(fig_1)

            st.subheader(f"{column.capitalize()} Tidsserie")
            fig_2 = analyzer.plot_timeseries(column)
            st.plotly_chart(fig_2)

            st.subheader(f"{column.capitalize()} Tidsserie med statistikk")
            fig_3 = analyzer.plot_timeseries_with_statistics(column)
            st.pyplot(fig_3)

def plot_predictive_data(df):
    if df is None or df.empty:
        st.error("Fant ikke data")
        return
    analyzer = DataPlotting(df)
    
    for column in ["temperatur", "vind", "skydekke"]:
        with st.expander(f"{column.capitalize()} grafer"):

            st.subheader(f"{column.capitalize()} Histogram")
            fig_1 = analyzer.plot_histogram(column)
            st.pyplot(fig_1)

            st.subheader(f"{column.capitalize()} Tidsserie")
            fig_2 = analyzer.plot_timeseries(column)
            st.plotly_chart(fig_2)

            st.subheader(f"{column.capitalize()} Tidsserie med statistikk")
            fig_3 = analyzer.plot_timeseries_with_statistics(column)
            st.pyplot(fig_3)

if st.sidebar.button("vis data"):
    data = fetch_data_time(start_date, end_date)
    main_tab = st.tabs(["Historisk data", "Prediksjon"])
    with main_tab[0]:
        st.subheader("Historisk data")
        plot_historical_data(data)
    with main_tab[1]:
        st.subheader("Prediksjons data")
        plot_predictive_data(data)
