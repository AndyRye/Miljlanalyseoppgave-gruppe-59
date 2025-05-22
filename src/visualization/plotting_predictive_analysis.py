import sys
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analysis.predictive_analysis import PredictiveAnalysis


class PlottingPredictiveAnalysis:

    def __init__(self):
        self.analysis = PredictiveAnalysis()
        self.analysis.fetch_and_prepare_data()
        self.analysis.split_data()
        self.analysis.train_model()
        self.analysis.predict()
    
    def plot_predictive_analysis(self):
        y_test, y_pred = self.analysis.get_result()

        fig = go.Figure()
        fig.add_trace(go.Scatter(y=y_test.values, mode='lines', name='Faktisk'))
        fig.add_trace(go.Scatter(y=y_pred, mode='lines', name='Predikert'))

        fig.update_layout(
            title="Faktisk vs Predikert temperatur",
            xaxis_title="Tidssteg",
            yaxis_title="Temperatur",
            legend=dict(x=0, y=1),
            template="plotly_white"
        )

        return fig
    
    def plot_forecast(self, history: pd.Series, forecast: list):
        fut_idx = list(range(len(history), len(history) + len(forecast)))

        fig = go.Figure()
        fig.add_trace(go.Scatter(y=history.values, mode='lines', name='Historikk'))
        fig.add_trace(go.Scatter(x=fut_idx, y=forecast, mode='lines+markers', name='Prognose'))

        fig.update_layout(
            title="Historiske verdier + prognose",
            xaxis_title="Tidssteg",
            yaxis_title="Temperatur",
            template="plotly_white"
        )

        return fig

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