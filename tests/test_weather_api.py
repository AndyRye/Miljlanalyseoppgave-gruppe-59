import unittest
import sys, os
import requests 


#Legger til en sti til mappen "data" som inneholder weatherapi.py"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))

from weatherapi import WeatherAPI, WeatherStatistics

class TestWeatherAPI(unittest.TestCase):

    def setUp(self):
        self.api = WeatherAPI()
        self.api.fetch()
        self.df = self.api.get_week_view()

    def test_data_is_fetched(self):
        self.assertIsNotNone(self.api.data)
        self.assertIn("properties", self.api.data, "'properties' mangler i JSON-data")


    def test_dataframe_not_empty(self):
        self.assertFalse(self.df.empty, "DataFrame fra get_week_view er tom")
        

    def test_tempertatur_range(self):
        temps = self.df["Temperatur (C)"]
        self.assertTrue(temps.between(-50, 50).all(), "Temperatur er utenfor realistisk område")      

    def statistics_output(self):
        stats = WeatherStatistics(self.df)
        basic_stats = stats.calculate_basic_stats()
        self.assertIn("Temperatur (C)", basic_stats.column, "Temperaturer mangler i statistikken")
        self.assertIn("Gjennomsnitt", basic_stats.column, "Gjennomsnitt mangler i statistikken")


if __name__ == '__main__':
    unittest.main()







