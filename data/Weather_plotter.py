import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Import our custom modules
from data_collection.frost import FrostAPI
st.set_page_config(
    layout="wide",
    page_title="Væranalyse"
)

st.title("Vær App")
st.markdown("dette er en app som bruker historisk værdata til å predikere vær")

@st.cache_resource
def hent_api():
    return FrostAPI()
API = hent_api()


st.sidebar.header("Konfigurasjoner")
st.sidebar.markdown("Vi bruker data fra OSLO")

API.params["sources"] = "SN17850" #koden for oslo

#setter datoer

vanlig_slutt_dato = datetime.now()
vanlig_start_dato = vanlig_slutt_dato - timedelta(days=365) # setter 1 år mellom start å sluttdato

start_dato = st.sidebar.date_input(
    "Fra dato", vanlig_start_dato, max_value=vanlig_start_dato #setter at du må ha et års mellomrom
)

slutt_dato = st.sidebar.date_input(
    "Til dato", vanlig_slutt_dato, max_value= vanlig_slutt_dato
)

prediksjons_dager = st.sidebar.slider(
    "Antall dager du vil predikere",min_value=1, max_value=30, value=7
)

def hent_data_tid(start_dato, slutt_dato):
    try:
        with st.spinner("Henter data..."):
            data = API.hent_data_for_periode(start_dato.strftime('%Y-%m-%d'), slutt_dato.strftime('%Y-%m-%d'), intervall="M")
        
        if data.empty:
            st.error("Fant ikke data")
            return None
        else:
            return data
    except:
        st.error("Fikk ikke til å hente data")
        return None



    

