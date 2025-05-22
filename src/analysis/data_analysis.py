import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import zscore
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class DataAnalyse:
    
    def __init__(self, data):
        self.data = data

    def calculate_statistics(self, kolonne):
        mean = round(float(np.mean(self.data[kolonne])), 2)
        median = round(float(np.median(self.data[kolonne])), 2)
        std_dev = round(float(np.std(self.data[kolonne])), 2)
        min_value = round(float(np.min(self.data[kolonne])), 2)
        max_value = round(float(np.max(self.data[kolonne])), 2)
        skewness = round(float(stats.skew(self.data[kolonne].dropna())), 2)
        kurtosis = round(float(stats.kurtosis(self.data[kolonne].dropna())), 2)

        return {
            "mean": mean,
            "median": median, 
            "std_dev": std_dev,
            "minimum": min_value,
            "maximum": max_value,
            "skewness": skewness,
            "kurtosis": kurtosis

        }   
    
    def calculate_all_statistics(self):

        numerical_columns = self.data.select_dtypes(include=['float64', 'int64']).columns

        stats_df = pd.DataFrame(index=['mean', 'median', 'std_dev', 'minimum', 'maximum', 'skewness', 'kurtosis'])

        for kolonne in numerical_columns:
            stats = self.calculate_statistics(kolonne)
            stats_df[kolonne] = [
                stats["mean"],
                stats["median"],
                stats["std_dev"],
                stats["minimum"],
                stats["maximum"],
                stats["skewness"],
                stats["kurtosis"],
            ]
        
        return stats_df
    
    
    def evaluate_correlation(self, kolonne1, kolonne2):
        
        correlation  = self.data[[kolonne1, kolonne2]].corr().iloc[0, 1]
        return round(correlation, 2)
    
    def analyse_correlation(self):

        numerical_columns = self.data.select_dtypes(include=['float64', 'int64']).columns
        korrelasjon_matrise = self.data[numerical_columns].corr()
        return korrelasjon_matrise
    
    def test_normality(self, kolonne):

        shapiro_test = stats.shapiro(self.data[kolonne].dropna())
        return {
            'statistics': shapiro_test[0],
            'p-value': shapiro_test[1],
            'is_normally_distributed': shapiro_test[1] > 0.05
        }
    

    def remove_outliers(self, kolonne, z_score_threshold=3):
        outliers = pd.DataFrame()
        while True: 
            if self.data[kolonne].dropna().nunique() <=2:
                continue
            z_scores = np.abs(zscore(self.data[kolonne], nan_policy='omit'))
            ny_data = self.data[z_scores < z_score_threshold]
            new_outliers = self.data[z_scores >= z_score_threshold]

            outliers = pd.concat([outliers, new_outliers])

            if len(ny_data) == len(self.data):
                break
            self.data = ny_data
        
        return self.data, outliers
    
    def handle_skewness(self, kolonne):

        originale_data = self.data[kolonne]
        skewness = originale_data.skew()

        if skewness > 0.5 and originale_data.min() >= 0:
            #En Logaritmisk transformasjon for positiv skewness
            transformed_data = np.log1p(originale_data)
            return{
                'original': originale_data,
                'transformed': transformed_data,
                'transformation_type': 'Log',
                'original_skewness': skewness,
                'transformed_skewness': transformed_data.skew()
            }
        elif skewness < -0.5 and originale_data.min() >= 0:
            #En eksponensiell transformasjon for negativ skewness
            transformed_data = np.exp(originale_data/ originale_data.max())
            return{
                'original': originale_data,
                'transformed': transformed_data,
                'transformation_type': 'Eksponensiell',
                'original_skewness': skewness,
                'transformed_skewness': transformed_data.skew()
            }
        else:
            #Ingen transformasjon nødvendig
            return{
                'original': originale_data,
                'transformed': originale_data,
                'transformation_type': 'Ingen',
                'original_skewness': skewness,
                'transformed_skewness': skewness
            }