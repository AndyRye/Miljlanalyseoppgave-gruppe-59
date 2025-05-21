import sys
import os
import pandas as pd
import numpy as np
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis.predictive_analysis import PredictiveAnalysis

class test_predictive_analysis(unittest.TestCase):
    
    def data_frame(self):
        #Creates a small data frame for further testing
        self.times = pd.date_range("2023-01-01", periods = 6, freq = "h")
        df = pd.DataFrame({
            "temperature": [10, 12, 14, 16, 18, 20],
            "cloud_area_fraction": [0, 0, 0, 0, 0, 0],
            "wind_speed": [1, 1, 1, 1, 1, 1],
        }, index = self.times)
        df["temp_prev"] = df["temperature"].shift(1) 
        df["cloud_prev"] = df["cloud_area_fraction"].shift(1)
        df["wind_prev"] = df["wind_speed"].shift(1)
        return df.dropna()
    
    def setUp(self):
        self.pa = PredictiveAnalysis()
        self.pa.df = self.data_frame()
        self.pa.split_data(test_size = 0.5)
        self.pa.train_model()

    def test_split_data_shapes(self):
        self.assertEqual(self.pa.X_train.shape, (2, 3))
        self.assertEqual(self.pa.X_test.shape, (3, 3))
        self.assertEqual(len(self.pa.y_train), 2)
        self.assertEqual(len(self.pa.y_test), 3)

    def test_predict_length(self):
        preds = self.pa.predict()
        #Should be one prediction per y_test row
        self.assertEqual(len(preds), len(self.pa.y_test))

    def test_evaluate_returns_proper_keys(self):
        #Predicts 4 times ahead 
        future = self.pa.forecast(hours = 4)
        self.assertIsInstance(future, list)
        self.assertEqual(len(future), 4)
        #Itierates thru future and tests that its float
        for val in future:
            self.assertIsInstance(val, float)

if __name__ == "__main__":
    unittest.main()



    
    

