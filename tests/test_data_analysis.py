"""
Unit test for the DataAnalysis class in the FrostAPI
Tests statistical calculations, normality test, outliers and skewness adjustments.
"""

import numpy as np
import sys
import os
import unittest
import pandas as pd
from scipy import stats

#Add the project's root directory to the path to allow importing from src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis.data_analysis import DataAnalysis

class TestDataAnalysis(unittest.TestCase):
    def setUp(self):
        #Create datasett with an outlier
        data = pd.DataFrame( {
            "temperature": [1, 2, 3, 4, 100],
            "wind": [5, 6, 7, 8, 9]
        })
        self.analyse = DataAnalysis(data)

    def test_calculate_statistics_keys_exist(self):
        #Check that all expected statistical keys are present
        stats = self.analyse.calculate_statistics("temperature")
        expected_keys = {"mean", "median", "std_dev", "minimum", "maximum", "skewness", "kurtosis"}
        self.assertTrue(expected_keys.issubset(stats.keys()))

    def test_calculate_statsitics_values_are_floats(self):
        #Check that all statistical values are a float datatype
        stats = self.analyse.calculate_statistics("temperature")
        for value in stats.values():
            self.assertIsInstance(value, float)

    def test_calculate_all_statistics_shape(self):
        #Check that the returned DataFrame has correct shape and expected columns
        all_stats = self.analyse.caluclate_all_statistics()
        self.assertEqual(all_stats.shape[0], 7)
        self.assertIn("temperature", all_stats.columns)
        self.assertIn("wind", all_stats.columns)

    def test_normality_output(self):
        #Makes sure that the normality test output conatains required keys and correct data types
        result = self.analyse.test_normality("temperature")
        self.assertIn("statistics", result)
        self.assertIn("p-value", result)
        self.assertIn("is_normally_distributed", result)
        self.assertIn(type(result["is_normally_distributed"]), [bool, np.bool_])

    def test_remove_outliers_reduces_length(self):
        #Verifies that removing outliers reduces the number of data points
        before = len(self.analyse.data)
        self.analyse.remove_outliers("temperature", z_score_threshold = 1)
        after = len(self.analyse.data)
        self.assertLess(after, before)
        self.assertNotIn(100, self.analyse.data["temperature"].values)

    def test_handle_skewness_keys_exist(self):
        #Ensure skewness handling returns the expected result keys
        result = self.analyse.handle_skewness("temperature")
        self.assertIn("original_skewness", result)
        self.assertIn("transformed_skewness", result)
        
        orig_skew = result["original_skewness"]
        trans_skew = result["transformed_skewness"]

        self.assertLessEqual(abs(trans_skew), abs(orig_skew))

if __name__ == "__main__":
    unittest.main()

    

