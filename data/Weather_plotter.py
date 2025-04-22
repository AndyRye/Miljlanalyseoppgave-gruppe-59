import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Import our custom modules
from frost import FrostAPI
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



    



def plot(self, kolonne, filnavn="Interaktiv.html"):
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




