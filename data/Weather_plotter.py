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
from src.visualization.plotting_predictive_analysis import PlottingPredictiveAnalysis
from src.analysis.predictive_analysis import PredictiveAnalysis
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

prediction_days = st.sidebar.slider(
    "Antall dager du vil predikere",min_value=1, max_value=30, value=7
)

if "show_data" not in st.session_state:
    st.session_state["show_data"] = False

if "prev_start" not in st.session_state or "prev_end" not in st.session_state:
    st.session_state["prev_start"] = start_date
    st.session_state["prev_end"] = end_date

if start_date != st.session_state["prev_start"] or end_date != st.session_state["prev_end"]:
    st.session_state["show_data"] = False

@st.cache_data
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
                st.info("Histogrammet viser hvor ofte en verdi forekommer i datasettet, dette kan være nyttig for å se om dataen er normalfordelt")

            st.subheader(f"{column_dict[column]} Tidsserie")
            fig_2 = analyzer.plot_timeseries(column, column_dict[column])
            if fig_2 is not None:
                st.plotly_chart(fig_2, use_container_width=True)
                st.info("Tidsserien viser hvordan dataen endrer seg over tid, dette kan være nyttig for å se trender og mønstre i dataene")

            st.subheader(f"{column_dict[column]} Tidserie med statistikk")
            fig_3 = analyzer.plot_timeseries_with_statistics(column, column_dict[column])
            if fig_3 is not None:
                st.plotly_chart(fig_3)
                st.info("Tidsserien med statistikk viser hvordan dataene endrer seg over tid, med glidende gjennomsnitt og standardavvik")




def plot_predictive_data(df, days_to_predict):
    if df is None or df.empty:
        st.error("Fant ikke data")
        return
    
    plotter = PlottingPredictiveAnalysis()
    prediction = plotter.analysis


    fig_1 = plotter.plot_predictive_analysis()
    if fig_1 is not None:
        st.plotly_chart(fig_1, use_container_width=True)

    history = df["temperature"].iloc[-20:]
    forecast = prediction.forecast(days=days_to_predict)

    fig_2 = plotter.plot_forecast(history, forecast)
    if fig_2 is not None:
        st.plotly_chart(fig_2, use_container_width=True)

    metrics = prediction.evaluate_model()
    st.json(metrics)


if st.sidebar.button("vis data"):
    st.session_state["show_data"] = True
    st.session_state["prev_start"]=start_date
    st.session_state["prev_end"]=end_date


if st.session_state.get("show_data", False):
    raw_historical_data = fetch_data_time(start_date, end_date)
    results = clean_data(raw_historical_data)
    historical_data = results["cleaned_data"]
    outliers = results["outliers"]
    transformations = results["transformations"]
    statistics = results["statistics"]
    correlation = results["correlation"]


    main_tab = st.tabs(["Historisk data", "Prediksjon"])
    with main_tab[0]:
        st.subheader("Historisk data")
        plot_historical_data(historical_data)
        st.markdown("""
                <hr style="border: 2px solid #bbb; margin: 45px 0;">
                """, unsafe_allow_html=True)

        sub_tabs_hist = st.tabs(["Rådata", "Renset data", "Uteliggere", "Transformasjoner"])
        with sub_tabs_hist[0]:
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

        with sub_tabs_hist[1]:
            st.subheader("last ned renset data")
            csv = historical_data.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Last ned renset data",
                data=csv,
                file_name="cleaned_historical_weather_data.csv",
                mime="text/csv"
            )
            st.write(historical_data)

        with sub_tabs_hist[2]:
            st.subheader("last ned uteliggere")
            csv = outliers.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Last ned uteliggere",
                data=csv,
                file_name="outliers.csv",
                mime="text/csv"
            )
            st.write(outliers)
        with sub_tabs_hist[3]:
            st.subheader("last ned transformasjoner")
            csv = transformations.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Last ned transformasjoner",
                data=csv,
                file_name="transformations.csv",
                mime="text/csv"
            )
            st.write(transformations)


    with main_tab[1]:
        st.subheader("Prediksjon")
        plot_predictive_data(historical_data, prediction_days)
        sub_tabs_pred = st.tabs(["Korrelasjon", "Statistikk"])
        st.markdown("""
                <hr style="border: 2px solid #bbb; margin: 45px 0;">
                """, unsafe_allow_html=True)
        with sub_tabs_pred[0]:
            st.subheader("Korrelasjon")
            fig = px.imshow(correlation, text_auto=True)
            st.plotly_chart(fig, use_container_width=True)
            csv = correlation.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Last ned korrelasjon",
                data=csv,
                file_name="correlation.csv",
                mime="text/csv"
            )
            st.write(correlation)
        with sub_tabs_pred[1]:
            st.subheader("Statistikk")

            data_analyzer = DataPlotting(historical_data)
            fig_1 = data_analyzer.plot_pair_analysis()
            fig_2 = data_analyzer.plot_box_plot()
            st.plotly_chart(fig_1)
            st.plotly_chart(fig_2)

            csv = statistics.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Last ned statistikk",
                data=csv,
                file_name="statistics.csv",
                mime="text/csv"
            )
            st.write(statistics)

