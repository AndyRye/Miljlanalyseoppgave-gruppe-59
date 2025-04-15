import pandas as pd
import json
import requests
import matplotlib.pyplot as plt
import datetime
import numpy as np
import seaborn as sns
from scipy import stats


class WeatherAPI:
    def __init__(self):
        #Url lenka til YR sin API
        self.url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

        #koordinater til Oslo
        self.params = {"lat" : 59.9139, "lon" : 10.7522 }


        #Yr krever å vite hvem som bruker API-en deres, logger inn med min
        self.headers = {"User-Agent" : "MyWeatherApp/1.0(tvmoen@stud.ntnu.no)"}
        self.data = None

    #fetcher data fra apier
    def fetch(self):
        try:
             #Vi henter data fra vår API
            response = requests.get(self.url, params = self.params, headers = self.headers)

            #Vi skjekker for HTTP-feil (400, 500...)
            response.raise_for_status() 

            #Vi konverterer vår respons til JSON
            self.data = response.json()

            #pretty print i terminal
            print(json.dumps(self.data, indent=2)) #HVOR SKAL DENNE

            self.validate()#HVA SKJER HER

        except requests.exceptions.RequestException as e:
            print(f"NB! Feil ved henting av API-data: {e}")

    def validate(self):

        #Nå skjekker vi om de forventede nøkklene finnes i JSON-dataene
        if "properties" not in self.data or "timeseries" not in self.data["properties"]:
            raise KeyError("NB JSON-struktur er ikke som forventet!")
        

    def get_week_view(self):
        if self.data is None:
            self.fetch()
        return WeatherDataProcessor(self.data).process()

    def get_month_view(self):
        if self.data is None:
            self.fetch()
        return WeatherDataProcessor(self.data).process()

class WeatherDataProcessor:
    def __init__(self, data):
        self.data = data

    def process(self):

        #V henter de første 24 timene
        timeseries = self.data["properties"]["timeseries"][:24]
        weather_data = []

        for entry in timeseries:
            try:

                time = entry.get("time", "Mangler tid")
                details = entry.get("data", {}).get("instant", {}).get("details", {})

                temp = details.get("air_temperature")
                wind_speed = details.get("wind_speed")
                humidity = details.get("relative_humidity")
                pressure = details.get("air_pressure_at_sea_level")
                cloud_cover = details.get("cloud_area_fraction")

                #Skjekker hvis det mangler data
                if temp is None or wind_speed is None:
                    print(f"NB! Mangler data for {time}: Temperature = {temp}, Vindhastighet = {wind_speed}")

                #Vi legger til data i listen
                weather_data.append([time, temp, wind_speed, humidity, pressure, cloud_cover])

            except KeyError as e:
                print(f"NB! Feil ved parsing av JSON for {time}: {e}")
            
        return WeatherDataCleaner(weather_data).clean()


    
class WeatherDataCleaner:
    def __init__(self, weather_data):
        self.weather_data = weather_data
    
    def clean(self):
        #Vi oppretter DataFrame
        df = pd.DataFrame(self.weather_data, columns = ["Tid", "Temperatur (C)", "Vindhastighet (m/s)", "Luftfuktighet(%)", "Lufttrykk(hPa)", "Skydekke(%)"])

        #Fjerner rader med manglende verdier
        df.dropna(inplace = True)

        df["Tid"] = pd.to_datetime(df["Tid"])

        #Fjerner urealistiske temperaturer 
        df = df[df["Temperatur (C)"].between(-50, 50)]

        #Fjerner duplikater
        df.drop_duplicates(subset = ["Tid"], keep = "first", inplace = True)

        return df


class WeatherStatistics:

    def __init__(self, df):
        self.df = df

    def calculate_basic_stats(self):

        """
        Beregner grunnleggende statistiske mål som gjennomsnitt, median, standardavvik for alle numeriske kolonner i datasettet vårt
        """

        numeric_columns = self.df.select_dtypes(include= ['float64', 'int64']).columns

        stats_df = pd.DataFrame(index= ['Gjennomsnitt', 'Median','Standardavvik', 'Min','Max','Skjevhet', 'Kurtose'])

        for col in numeric_columns:
            stats_df[col] = [
                self.df[col].mean(),
                self.df[col].median(),
                self.df[col].std(),
                self.df[col].min(),
                self.df[col].max(),
                self.df[col].skew(),
                self.df[col].kurt()
            ]

        return stats_df
    
    def analyze_correlation(self):
        #Vi analyserer korrelasjon mellom ulike værparametere

        numeric_df = self.df.select_dtypes(include=['float64', 'int64'])

        corr_matrix = numeric_df.corr()
        return corr_matrix
    
    def test_normality(self, column):
        #Her har vi valgt å teste om en kolonne følger normalfordeling ved hjelp av en Shapiro- Wilk test som er svært gunstig for små til middels store datasett

        shapiro_test = stats.shapiro(self.df[column].dropna())
        return {
            'statistikk': shapiro_test[0],
            'p-verdi':shapiro_test[1],
            'Er normalfordelt': shapiro_test[1] > 0.05
        }
    
    def handle_skewness(self, column):
        #håndterer skjevheter i data ved å transformere dem, returnerer orginal og transformert data

        original_data = self.df[column]
        skewness = original_data.skew()

        if skewness > 1 and original_data.min() >= 0:

            transformed_data = np.log1p(original_data)
            return{
                'Original': original_data,
                'Transformert': transformed_data,
                'Transformasjonstype': 'Log',
                'Original skjevhet': skewness,
                'Transformert skjevhet': transformed_data.skew()
            }
        
        elif skewness < -1:
            transformed_data = np.exp(original_data /original_data.max())
            return{'Original': original_data,
                'Transformert': transformed_data,
                'Transformasjonstype': 'Eksponensiell',
                'Original skjevhet': skewness,
                'Transformert skjevhet': transformed_data.skew()
            }
        
        else:
            return{
                'Original': original_data,
                'Transformert': original_data,
                'Transformasjonstype': 'Ingen',
                'Original skjevhet': skewness,
                'Transformert skjevhet': skewness
            }
        

class Weather_Plotting:
    def __init__(self, weather_data):

        if isinstance(weather_data, list):
            self.df = WeatherDataCleaner(weather_data).clean()
        elif isinstance(weather_data, pd.DataFrame):
            self.df = weather_data
        else:
            raise ValueError("Ikke kompatibelt Dataformat")
        
        #sjekker at dataen som kommer inn i klassen minst har kolonnene ["Tid", "Temperatur (C)", "Vindhastighet (m/s)"]

        expeted_colum = ["Tid", "Temperatur (C)", "Vindhastighet (m/s)"]
        if not all(col in self.df.columns for col in expeted_colum):
            raise ValueError(f"Datasettet mangler påkrevde kolonner, forventet:{expeted_colum}")
    
    def Plott_Temperatur(self):
        fig, ax1 = plt.subplots(figsize=(7,5))
        sns.lineplot(x = "Tid",  y = "Temperatur (C)", hue = "Temperatur (C)", palette = "coolwarm", data = self.df, ax = ax1)
        ax1.set_xlabel("tid")
        ax1.set_ylabel("Temperatur")
        ax1.set_title("Temperatur Over Tid")
        ax1.grid(True)
        plt.show()

    def Scatterplott_Temperatur(self):
        fig, ax2 = plt.subplots(figsize=(7,5))
        
        sns.scatterplot(x = "Tid", y= "Temperatur (C)", hue = "Temperatur (C)", palette = "magma", data= self.df, ax = ax2)
        ax2.set_xlabel("tid")
        ax2.set_ylabel("Temperatur")
        ax2.set_title("Temperatur Over Tid")
        plt.show()

    def Plott_Vindhastighet(self):
        fig, ax3 = plt.subplots(figsize=(7,5))

        ax3.plot(self.df["Tid"], self.df["Vindhastighet (m/s)"], color = "blue")
        ax3.set_title("Vindhastighet")
        ax3.set_xlabel("Tid")
        ax3.set_ylabel("vindhastighet")
        ax3.legend(["Vindhastighet"])
        plt.show()

    def Plott_Statistisk_Fordeling(self, kolonne):
        #Plotter histogram med kurvetilpasning for å vise datafordeling
        plt.figure(figsize=(10, 6))
    
        sns.histplot(self.df[kolonne], kde=True, color="steelblue")

        plt.axvline(self.df[kolonne].mean(), color='red', linestyle='--', label=f'Gjennomsnitt: {self.df[kolonne].mean():.2f}')
        plt.axvline(self.df[kolonne].median(), color='green', linestyle='-.', label=f'Median: {self.df[kolonne].median():.2f}')

        plt.title(f'Statistisk fordeling av {kolonne}')
        plt.xlabel(kolonne)
        plt.ylabel('Frekvens')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def Plott_Box_plot(self):
        #lager box plott for å identifisere utligger
        numeric_cols = self.df.select_dtypes(include=['float64','int64']).columns

        plt.figure(figsize=(12, 8))
        self.df[numeric_cols].boxplot()
        plt.title('Box Plot av Værvariabler')
        plt.ylabel('Verdi')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def Plott_Korrelasjonsmatrise(self):
        #Visualiserer korrelasjon mellom alle numeriske varibaler

        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        corr_matrix = self.df[numeric_cols].corr()

        plt.figure(figsize=(10,8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='2f', linewidths=0.5)
        plt.title('Korrelasjonsmatrise av Værvariabler')
        plt.tight_layout()
        plt.show()

    def Plott_Par_Analyse(self):
        #Lager parvise plot for å vise forholdene mellom varibalene@

        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns

        if len(numeric_cols) > 4:
            numeric_cols = numeric_cols[:4]

        sns.pairplot(self.df[numeric_cols], height=2.5, diag_kind='kde')
        plt.suptitle('Parvise relasjoner mellom Værvariabler', y=1.02)
        plt.tight_layout()
        plt.show()

    def Plott_Tidsserie_Med_Statistikk(self, kolonne):
        #Her plotter vi en tidsserie med glidende gjennomsnitt og konfidensintervall
        fig, ax = plt.subplots(figsize=(12, 6))

        sns.lineplot(x='Tid', y=kolonne, data=self.df, label='Faktiske verdier', ax=ax)

        if len(self.df) > 3:
            rolling_mean = self.df[kolonne].rolling(window=3, min_periods=1).mean()
            rolling_std = self.df[kolonne].rolling(window= 3, min_periods=1).std()

            ax.plot(self.df['Tid'], rolling_mean, 'r--', label='Glidende gjennomsnitt( 3 punkter)')
            ax.fill_between(self.df['Tid'],
                            rolling_mean -rolling_std,
                            rolling_mean + rolling_std,
                            color='r', alpha=0.2, label='±1 Standardavvik')
            
            ax.set_title(f'Tidsserie av {kolonne} med statistiske mål')
            ax.set_xlabel('Tid')
            ax.set_ylabel(kolonne)
            ax.legend()
            plt.xticks(rotation= 45)
            plt.tight_layout()
            plt.show()

if __name__ == "__main__":
    weather_api = WeatherAPI()
    df = weather_api.get_week_view()
    print("\nRenset Værdata")
    print(df)

    stats = WeatherStatistics(df)
    basic_stats = stats.calculate_basic_stats()
    print("\n Grunnleggende statistikk:")
    print(basic_stats)

    correlation = stats.analyze_correlation()
    print("\n Korrelasjonsmatrise:")
    print(correlation)

    #Tester normalfordelingen
    try:
        normality_temp = stats.test_normality("Temperatur (C)")
        print("\n Normalitetstest for temperatur:")
        print(normality_temp)
    except Exception as e:
        print(f"kunne ikke utføre normalitetstest: {e}")

    try:
        skewness_result = stats.handle_skewness("Vindhastighet (m/s)")
        print("n\ Håndtering av skjevhet for vindhastighet:")
        print(f" Original skjevhet: {skewness_result['Original skjevhet']:.4f}")
        print(f"Transformert skjevhet: {skewness_result['Transformert skjevhet']:.4f}")
        print(f"Transformasjonstype: {skewness_result['Transformasjonstype']}")
    except Exception as e:
        print(f"Kunne ikke håndtere skjevhet: {e}")

    plotter = Weather_Plotting(df)

    #standard
    plotter.Plott_Temperatur()
    plotter.Plott_Vindhastighet()

    #Avansert
    plotter.Plott_Statistisk_Fordeling("Temperatur (C)")
    plotter.Plott_Box_plot()
    plotter.Plott_Korrelasjonsmatrise()
    plotter.Plott_Par_Analyse()
    plotter.Plott_Tidsserie_Med_Statistikk("Temperatur (C)")






        


        




