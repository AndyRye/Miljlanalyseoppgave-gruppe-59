"""
Unit test for the FrostAPI
"""
import numpy as np
import sys
import os
import unittest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))

from data.frost import DataAnalysis

class TestDataAnalysis(unittest.TestCase):
    def setUp(self):
        data = pd.DataFrame( {
            "temperatur": [1, 2, 3, 4, 100],
            "vind": [5, 6, 7, 8, 9]
        })
        self.analyse = DataAnalysis(data)

    def test_fetch

