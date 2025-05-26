"""
Unit tests for plotting
"""
import sys
import os
import unittest
import pandas as pd
import plotly.graph_objects as go


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.visualization.plot_predictive import PlottingPredictiveAnalysis

class TestPlotPredictive(unittest.TestCase):

    def setUp(self):
        #Lager objekt om inneholder plottefunksjoner
        self.plotter = PlottingPredictiveAnalysis()

    def test_plot_predictive_analysis(self):
        #Tester at det returneres en go.Figure, at den inneholder 2 dataserier og at navnene på serien er "Faktisk" og "Predikert"
        fig = self.plotter.plot_predictive_analysis()
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 2)
        self.assertEqual(fig.data[0].name, "Faktisk")
        self.assertEqual(fig.data[1].name, "Predikert")

    def test_plot_forecast(self):
        # Bruker egen data til testing. Sjekker at det er 2 dataserier og at navnene på serien er riktige
        history = pd.Series([1, 2, 3])
        forecast = [4, 5, 6]

        fig = self.plotter.plot_forecast(history, forecast)
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 2)
        self.assertEqual(fig.data[0].name, "Historikk")
        self.assertEqual(fig.data[1].name, "Prognose")
        self.assertEqual(list(fig.data[1].y), forecast)

if __name__ == "__main__":
    unittest.main()








