"""
Unit test for the FrostAPI
"""
import numpy as np
import sys
import os
import unittest
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))

from data.frost import DataAnalysis

class TestDataAnalysis(unittest.TestCase):
    def setUp(self):
        data = pd.DataFrame( {
            "temperatur": [1, 2, 3, 4, 100],
            "vind": [5, 6, 7, 8, 9]
        })
        self.analyse = DataAnalysis(data)

    def test_calculate_statistics(self):
        stats = self.analyse.calculate_satistics("temperatur")
        self.assertIn("gjennomsnitt", stats)
        self.assertIsInstance(stats["gjennosnitt"], float)

    def test_check_correlation(self):
        correlation = self.analyse.check_correlation("temperatur", "vind")
        self.assertTrue(-1 <= correlation <= 1)
        




    def test_remove_outliers(self):

        




