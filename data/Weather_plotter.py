import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
from google import genai
from dotenv import load_dotenv


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_collection.frost import FrostAPI
from src.visualization.plotting_frost_api import DataPlotting
from src.analysis.data_analysis import DataAnalyse



st.set_page_config(
    layout="wide",
    page_title="Væranalyse"
)

st.title("Væranalyse")


@st.cache_resource
def fetch_api():
    api = FrostAPI()
    return api
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
        st.error("Fant ikke data 1")
        return
    analyzer = DataPlotting(df)
    sub_tabs = st.tabs(["Temperatur grafer", "Vind grafer", "Skydekke grafer"])
    column_dict = {
        "temperature": "Temperatur",
        "wind_speed": "Vind",
        "cloud_area_fraction": "Skydekke"
    }

    for column, tab in zip(column_dict.keys(), sub_tabs):
        with tab:
            st.subheader(f"{column_dict[column]} Histogram")
            fig_1 = analyzer.plot_histogram(column, column_dict[column])
            if fig_1 is not None:
                st.plotly_chart(fig_1, use_container_width=True)
                st.markdown("Histogrammet viser hvor ofte en verdi forekommer i datasettet, dette kan være nyttig for å se om dataen er normalfordelt")

            st.subheader(f"{column_dict[column]} Tidsserie")
            fig_2 = analyzer.plot_timeseries(column, column_dict[column])
            if fig_2 is not None:
                st.plotly_chart(fig_2, use_container_width=True)
                st.markdown("Tidsserien viser hvordan dataen endrer seg over tid, dette kan være nyttig for å se trender og mønstre i dataene")

            st.subheader(f"{column_dict[column]} Tidserie med statistikk")
            fig_3 = analyzer.plot_timeseries_with_statistics(column, column_dict[column])
            if fig_3 is not None:
                st.pyplot(fig_3)
                st.markdown("Tidsserien med statistikk viser hvordan dataene endrer seg over tid, med glidende gjennomsnitt og standardavvik")


def plot_predictive_data(df):
    if df is None or df.empty:
        st.error("Fant ikke data")
        return
    analyzer = DataPlotting(df)
    
    for column in ["temperature", "vind", "skydekke"]:
        with st.expander(f"{column.capitalize()} grafer"):

            st.subheader(f"{column.capitalize()} Histogram")
            fig_1 = analyzer.plot_histogram(column)
            st.plotly_chart(fig_1, use_container_width=True)

            st.subheader(f"{column.capitalize()} Tidsserie")
            fig_2 = analyzer.plot_timeseries(column)
            st.plotly_chart(fig_2, use_container_width=True)

            st.subheader(f"{column.capitalize()} Tidsserie med statistikk")
            fig_3 = analyzer.plot_timeseries_with_statistics(column)
            st.pyplot(fig_3)

        
def clean_data(df, z_score_threshold=3):
    data_analyzer = DataAnalyse(df)
    all_outliers = pd.DataFrame()
    transformed_columns = {}
    for column in df.select_dtypes(include=['float64', 'int64']).columns:

        cleaned_data, outliers = data_analyzer.remove_outliers(column, z_score_threshold)
        all_outliers = pd.concat([all_outliers, outliers])
        data_analyzer.data = cleaned_data

        skew_result = data_analyzer.handle_skewness(column)
        transformed_columns[column] = {
            "transformasjonstype": skew_result["transformation_type"],
            "opprinnelig_skewness": round(skew_result["original_skewness"], 2),
            "transformert_skewness": round(skew_result["transformed_skewness"], 2)
        }
    statistics = data_analyzer.calculate_all_statistics()
    correlation = data_analyzer.analyse_correlation()

    return {
        "cleaned_data": data_analyzer.data,
        "outliers": all_outliers,
        "transformations": pd.DataFrame.from_dict(transformed_columns, orient="index"),
        "statistics": statistics,
        "correlation": correlation
    }

if st.sidebar.button("vis data"):
    raw_historical_data = fetch_data_time(start_date, end_date)
    results = clean_data(raw_historical_data)
    historical_data = results["cleaned_data"]
    outliers = results["outliers"]
    transformations = results["transformations"]
    statistics = results["statistics"]
    correlation = results["correlation"]

    st.write(historical_data)


    main_tab = st.tabs(["Historisk data", "Prediksjon"])
    with main_tab[0]:
        st.subheader("Historisk data")
        plot_historical_data(historical_data)
    with main_tab[1]:
        st.subheader("Prediksjon")
    
    st.markdown("____________________________________________________________")

    sub_tabs = st.tabs(["Rådata", "Renset data", "Uteliggere", "Transformasjoner"])
    with sub_tabs[0]:
        if raw_historical_data is not None and not raw_historical_data.empty:
            st.subheader("last ned rådata")
            csv = raw_historical_data.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Last ned rådata",
                data=csv,
                file_name="raw_historical_weather_data.csv",
                mime="text/csv"
            )
            st.write(raw_historical_data)

    with sub_tabs[1]:
        st.subheader("last ned renset data")
        csv = historical_data.reset_index().to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Last ned renset data",
            data=csv,
            file_name="cleaned_historical_weather_data.csv",
            mime="text/csv"
        )
        st.write(historical_data)

    with sub_tabs[2]:
        st.subheader("last ned uteliggere")
        csv = outliers.reset_index().to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Last ned uteliggere",
            data=csv,
            file_name="outliers.csv",
            mime="text/csv"
        )
        st.write(outliers)
    with sub_tabs[3]:
        st.subheader("last ned transformasjoner")
        csv = transformations.reset_index().to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Last ned transformasjoner",
            data=csv,
            file_name="transformations.csv",
            mime="text/csv"
        )
        st.write(transformations)
