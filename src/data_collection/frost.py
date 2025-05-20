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
import numpy as np

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
        
            
            for col in ['temperature', 'cloud_area_fraction', 'wind_speed']:
                if col in station_data.columns:
                    # First try forward fill
                    station_data.loc[:, col] = station_data[col].ffill()
                    # Then try backward fill for any remaining NaNs
                    station_data.loc[:, col] = station_data[col].bfill()
                
            
            df_filled.loc[df_filled['stasjon'] == station] = station_data
    
        return df_filled
    
    def fetch_elementvalue(self, observations, element_id):
        for o in observations:
            if o["elementId"] == element_id:
                return o["value"]
        return None

    def fetch_data(self, start, slutt):
        self.params["referencetime"] = f"{start}/{slutt}"
        r = requests.get(self.endpoint, params=self.params,
                         auth=(self.client_id, ""))
        r.raise_for_status()
        rows = {}
        for item in r.json().get("data", []):
            k = (item["referenceTime"], item["sourceId"])
            rows.setdefault(k, {"tidspunkt": item["referenceTime"],
                                "stasjon": item["sourceId"],
                                "temperature": None,
                                "cloud_area_fraction": None,
                                "wind_speed": None})
            for o in item["observations"]:
                eid = o["elementId"]
                if eid == "air_temperature":
                    rows[k]["temperatur"] = o["value"]
                elif eid == "cloud_area_fraction":
                    rows[k]["cloud_area_fraction"] = o["value"]
                elif eid == "wind_speed":
                    rows[k]["wind_speed"] = o["value"]

        df = pd.DataFrame(rows.values()).set_index(
                 pd.to_datetime(pd.Series([r["tidspunkt"] for r in rows.values()])))
        return df
    
    def fetch_data_for_periode(self, start_dato, sluttdato, intervall="W"):
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
            df = self.fetch_data(current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'))
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
df_periode = api.fetch_data_for_periode("2023-01-01", "2024-01-07")

if not df_periode.empty:
    print(df_periode.head())
    print(df_periode.describe())
else:
    print("Ingen data funnet")
