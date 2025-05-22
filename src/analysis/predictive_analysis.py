import sys
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_collection.frost import FrostAPI

class PredictiveAnalysis:   

    def __init__(self, start="2023-01-01", end="2024-01-07", station="SN18700:0"):
        #Defining variables and parameters that will be used
        self.api = FrostAPI()
        self.start = start
        self.end = end
        self.station = station
        self.df = None
        self.model = None 
        self.X_train, self.X_test = None, None
        self.y_train, self.y_test = None, None
        self.y_pred = None

    
    def fetch_and_prepare_data(self):
        df_periode = self.api.fetch_data_for_periode(self.start, self.end)
            
        df = df_periode.copy()
        #Makes a coloumn that represents the values from the previous hour
        df["temp_prev"] = df["temperature"].shift(1) 
        df["cloud_prev"] = df["cloud_area_fraction"].shift(1)
        df["wind_prev"] = df["wind_speed"].shift(1)

        print("Raw df_periode rows:", len(df_periode))
        print("Unique stations:", df_periode["stasjon"].unique())

        #Removes the row that contains the NaN 
        df = df.dropna()

        self.df = df
        return df
    
    def split_data(self, test_size = 0.2):

        X = self.df[["temp_prev", "cloud_prev", "wind_prev"]] #Values from the last hour
        y = self.df["temperature"] #Goalvariable 

        #Calculates how many rows to be used for training and testing
        split_index = int(len(X) * (1 - test_size))

        self.X_train, self.X_test = X.iloc[:split_index], X.iloc[split_index:]
        self.y_train, self.y_test = y.iloc[:split_index], y.iloc[split_index:]

    def train_model(self):
        #Creates an empty model to predict correlation in change between X_train and y_train
        self.model = LinearRegression()
        self.model.fit(self.X_train, self.y_train)

    def predict(self):
        self.y_pred = self.model.predict(self.X_test)
        return self.y_pred
    
    def evaluate_model(self):
        #Return evaluation metrics from the predictive model
        mae = mean_absolute_error(self.y_test, self.y_pred)
        rmse = np.sqrt(mean_squared_error(self.y_test, self.y_pred))
        r2 = r2_score(self.y_test, self.y_pred)

        return {"MAE" : round(mae, 2),
                "RMSE": round(rmse, 2),
                "r2": round(r2, 2)
                }
    
    def get_result(self):
        return self.y_test, self.y_pred
    
    def forecast(self, days):
        #Returns a list with predictions 
        last = self.df.iloc[-1].copy()
        preds =[]
        
        for _ in range(days):
            inp = pd.DataFrame({
                "temp_prev": [last["temperature"]],
                "cloud_prev": [last["cloud_area_fraction"]],
                "wind_prev": [last["wind_speed"]]
            })
            next_temp = self.model.predict(inp)[0]
            preds.append(next_temp)
            #Updates "last" with the next prediction
            last["temperature"] = next_temp
        
        return preds
