import unittest
from datetime import datetime 
import sys, os
import numpy as np
 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))
print(sys.path)

from frostapi import FrostAPI, DataAnalyse 

class TestDataAnalyseWithRealAPI(unittest.TestCase):

    def setUp(self):
        self.api = FrostAPI()
        self.df = self.api.hent_data("2023-01-01", "2023-01-07")

        #sjekker at data er blitt hentet
        if self.df.empty:
            raise ValueError("Ingen data hentet fra frostAPItesten.")
        self.analyse = DataAnalyse(self.df)

    def test_beregn_statistikk_temperatur(self):
        stats = self.analyse.beregn_statistikk("temperatur")

        print("Statistikk:", stats)

        #sjekker at alle verdier er en float og at de er innenfor forventet intervall
        self.assertIsInstance(stats["gjennomsnitt"], float)
        self.assertIsInstance(stats["median"], float)
        self.assertIsInstance(stats["standard avvik"], float)

        self.assertGreater(stats["gjennomsnitt"], -50)
        self.assertLess(stats["gjennomsnitt"], 50)

    """ def test_fjern_uteliggere_temperatur(self):
        før_rader = len(self.analyse.data)
        print("Antall rader før fjerning:", før_rader)

        self.analyse.fjern_uteliggere("temperatur", z_score_threshold=2)
        etter_rader = len(self.analyse.data)
        print("Antall rader etter fjerning:", etter_rader)

        self.assertLessEqual(etter_rader, før_rader)

        z_score =  abs((self.analyse.data["temperatur"] - self.analyse.data["temperatur"].mean()) / 
                    self.analyse.data["temperatur"].std())
        self.assertTrue((z_score <= 2).all(), "Noen uteliggere er fortsatt igjen")"""

    def test_fjern_uteliggere_temperatur(self):
        før_rader = len(self.analyse.data)
        print("Antall rader før fjerning:", før_rader)

        self.analyse.fjern_uteliggere("temperatur", z_score_threshold=2)
        etter_rader = len(self.analyse.data)
        print("Antall rader etter fjerning:", etter_rader)

        self.assertLessEqual(etter_rader, før_rader)

        # ⚠️ Her må vi bruke Z-score beregnet på det filtrerte datasettet
        temperaturverdier = self.analyse.data["temperatur"]
        z_scores = np.abs((temperaturverdier - temperaturverdier.mean()) / temperaturverdier.std())

        print("Maksimal z-score etter fjerning:", z_scores.max())  # Debug

        self.assertTrue((z_scores <= 2).all(), "Noen uteliggere er fortsatt igjen")

    
if __name__ == "__main__":
    unittest.main()
