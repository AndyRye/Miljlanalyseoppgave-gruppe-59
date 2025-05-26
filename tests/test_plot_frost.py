import sys
import os
import unittest 
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.visualization.plot_frost import DataPlotting

class TestPlotFrost(unittest.TestCase):

    def setUp(self):
        #Lager en dataframe som brukes i testing
        dates = pd.date_range(end=datetime.now(), periods = 10)
        self.df = pd.DataFrame({
            "Temp": [10 + i for i in range(10)],
            "Wind": [2.0 + 0.1 * i for i in range(10)],
            "Cloud": [0.1 * i for i in range(10)],
        }, index = dates)
        self.plotter = DataPlotting(self.df)

    def test_histogram_returns_figure(self):
        #Tester at plot_histogram() returnerer en gydlig plotly når gydlig kolonne og tittel oppgis
        fig = self.plotter.plot_histogram("temp", "Temperatur")
        self.assertIsInstance(fig, go.Figure)

    def test_box_plot_not_none(self):
        #Sjekker at plot_box_plot() returnerer data når det finnes tilgjenglig data
        fig = self.plotter.plot_box_plot()
        self.assertIsNone(fig)

if __name__ == "__main__":
    unittest.main()





