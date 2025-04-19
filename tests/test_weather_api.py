import unittest
import sys, os
import requests 


#Legger til en sti til mappen "data" som inneholder weatherapi.py"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))

from weatherapi import WeatherAPI
from weatherapi import WeatherDataProcessor

class APItestWeather(unittest.TestCase):

    def setUp(self):
        self.api = WeatherAPI()

    def test_init(self):
        #Bruker assertEqual for å sjekke at url, parametere og headers stemmer
        self.assertEqual(self.url, "https://api.met.no/weatherapi/locationforecast/2.0/compact")
        self.assertEqual(self.params, {"lat" : 59.9139, "lon" : 10.7522 })
        self.assertEqual(self.headers, {"User-Agent" : "MyWeatherApp/1.0(tvmoen@stud.ntnu.no)"})
        self.assertIsNone(self.data)

    
    def testfetch(self):
        #Henter feile koordinater og sjekke om det raiser en requests.exceptions.RequestException
        self.params = {"lat" : 57.9139, "lon" : 10.7522 }

        with self.assertRaises(requests.exceptions.RequestException):
            self.api.fetch()

    def test_get_week_view(self):
        self.data = None
        self.get_week_view() 
        self.assertIsNotNone(self.data)

    def test_get_month_view(self):
        self.data = None
        self.get_month_view()
        self.assertIsNotNone(self.data)

class WeatherDataProcessor(unittest.TestCase):

    def test_init2(self):
        test_data = {"relative_humidity": 75.5, "air_temperature": -2.5}
        client = WeatherAPI(test_data)
        self.assertEqual(self.data, test_data)


if __name__ == '__main__':
    unittest.main()







