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




class FrostAPI:
    def __init__(self):
        self.client_id = "0933ff3e-f805-41e8-a90f-d13658c62567"
        self.client_secret = "06e27da9-90dd-4eec-aeb9-ca90fd6ef805"
        self.endpoint = 'https://frost.met.no/observations/v0.jsonld'
        self.params = {
            
            "sources": 'SN18700,SN90450,SN50539,SN69100,SN99840', 
            
            "elements": [
                'air_temperature',
                'cloud_area_fraction', 
                'wind_speed',
                'relative_humidity',
                'air_pressure_at_sea_level',
                'precipitation_amount'
            ], 
            "referencetime": ""
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
         
            full_df = self.handle_missing_data(full_df)
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


