"""
Unit test for the FrostAPI
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime 
import sys
import os
import json 
from datetime import datetime
import requests 

 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_collection.frost import FrostAPI

class TestFrostAPI(unittest.TestCase):
    #Lager en liste av ordbøker til testing
    def setUp(self):
        self.api = FrostAPI()
        self.sample_observations = [
            {"elementId": "air_temperature", "value": 3.2},
            {"elementId": "wind_speed", "value": 5.1}
        ]


    def test_fetch_elementvalue(self):
        #Tester at fetch_elementvalue() korrekt hente verdier fra en liste
        
        self.assertEqual(self.api.fetch_elementvalue(self.sample_observations, "air_temperature"), 3.2)
        self.assertIsNone(self.api.fetch_elementvalue(self.sample_observations, "cloud_area_fraction"))


    @patch("requests.get")
    def test_fetch_data(self, mock_get):
        #Tester at fetch_data() returnerer ett data sett med riktig antall kolonner og verdier
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "referenceTime": "2023-01-01T00:00:00Z",
                    "sourceId": "SN18700",
                    "observations": self.sample_observations
                }
            ]
        }
        mock_get.return_value = mock_response
        df = self.api.fetch_data("2023-01-01", "2023-01-02")
        self.assertFalse(df.empty)
        self.assertIn("temperature", df.columns)
        self.assertEqual(df.iloc[0]["temperature"], 3.2)

    @patch("requests.get") 
    def test_data_fetch_empty(self, mock_get):
        #Tester at fetch_data() returnerer et tomt datasett når frostAPI svarer med ingen data

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        df = self.api.fetch_data("2023-01-01", "2023-01-02")
        self.assertTrue(df.empty)

    def test_fetch_data_for_periode_invalid_intervall(self):
        #Tester at det returneres en ValueError ved ugydlig input

        with self.assertRaises(ValueError):
            self.api.fetch_data_for_periode("2023-01-01", "2023-01-03", intervall="X")
    
if __name__ == "__main__":
    unittest.main()
