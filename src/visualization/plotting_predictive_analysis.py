import sys
import os
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analysis.predictive_analysis import PredictiveAnalysis
from visualization.plotting_predictive_analysis import PlottingPredictiveAnalysis

class PlottingPredictiveAnalysis:

    def __init__(self):
        self.analysis = PredictiveAnalysis()
        self.analysis.fetch_and_prepare_data()
        self.analysis.split_data()
        self.analysis.train_model()
        self.analysis.predict()
    
    def plot_predictive_analysis(self):
        y_test, y_pred = self.analysis.get_result()
        plt.plot(y_test.values, label = "Actual")
        plt.plot(y_pred, label = "Predicted")
        plt.title("Predicted Vs Actual Temperature")
        plt.xlabel("Time")
        plt.ylabel("Temperature")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.savefig("prediction_vs_real.png")
        plt.show()
    
    def plot_forecast(self, history: pd.Series, forecast: list):
        plt.figure(figsize=(10,4))
        plt.plot(history.values, label="History")
        fut_idx = range(len( history),len(history) + len(forecast))
        plt.plot(fut_idx, forecast, 'o--', label="Forecast")
        plt.title("Historical and Forecasted Temperature")
        plt.xlabel("Time Step")
        plt.ylabel("Temperature")
        plt.legend()
        plt.grid(True)
        plt.savefig("prediction_vs_real2.png")
        plt.tight_layout()
        plt.show()

if __name__=="__main__":
    pa = PredictiveAnalysis()
    pa.fetch_and_prepare_data()
    pa.split_data()
    pa.train_model()
    pa.predict()

    print("Eval:", pa.evaluate_model())

    plotter = PlottingPredictiveAnalysis()
    plotter.plot_predictive_analysis()

    history = pa.df["temperature"].iloc[-20:]
    future = pa.forecast(hours = 5)
    plotter.plot_forecast(history, future)