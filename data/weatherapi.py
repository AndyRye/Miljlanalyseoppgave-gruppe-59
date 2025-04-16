import pandas as pd
import json
import requests
import matplotlib.pyplot as plt
import datetime

import seaborn as sns

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

                #Skjekker hvis det mangler data
                if temp is None or wind_speed is None:
                    print(f"NB! Mangler data for {time}: Temperature = {temp}, Vindhastighet = {wind_speed}")

                #Vi legger til data i listen
                weather_data.append([time, temp, wind_speed])

            except KeyError as e:
                print(f"NB! Feil ved parsing av JSON for {time}: {e}")
            
        return WeatherDataCleaner(weather_data).clean()


    
class WeatherDataCleaner:
    def __init__(self, weather_data):
        self.weather_data = weather_data
    
    def clean(self):
        #Vi oppretter DataFrame
        df = pd.DataFrame(self.weather_data, columns = ["Tid", "Temperatur (C)", "Vindhastighet (m/s)"])

        #Fjerner rader med manglende verdier
        df.dropna(inplace = True)

        #Fjerner urealistiske temperaturer 
        df = df[df["Temperatur (C)"].between(-50, 50)]

        #Fjerner duplikater
        df.drop_duplicates(subset = ["Tid"], keep = "first", inplace = True)

        return df

if __name__ == "__main__":
    weather_api = WeatherAPI()
    df = weather_api.get_week_view()
    print("\nRenset Værdata")
    print(df)



class Weather_Plotting:
    def __init__(self, weather_data):

        #henter ut værdataen å forsikrer at den er i pandas dataframe format

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
        
        #konverterer Tid til Datetime
        self.df["Tid"] = pd.to_datetime(self.df["Tid"]) 


    def Plott_Temperatur(self):
        fig, ax1 = plt.subplots(figsize=(7,5))
        sns.lineplot(x = "Tid",  y = "Temperatur (C)", color = "blue", data = self.df, ax = ax1)
        ax1.set_xlabel("tid")
        ax1.set_ylabel("Temperatur")
        ax1.set_title("Temperatur Over Tid")
        ax1.grid(True)
        plt.xticks(rotation = 30)
        plt.show()

    def Scatterplott_Temperatur(self):
        fig, ax2 = plt.subplots(figsize=(7,5))
        
        sns.scatterplot(x = "Tid", y= "Temperatur (C)", hue = "Temperatur (C)", palette = "coolwarm", data=self.df, ax = ax2)
        ax2.set_xlabel("tid")
        ax2.set_ylabel("Temperatur")
        ax2.set_title("Temperatur Over Tid")
        plt.xticks(rotation = 30)
        plt.show()

    def Plott_Vindhastighet(self):
        fig, ax3 = plt.subplots(figsize=(7,5))

        ax3.plot(self.df["Tid"], self.df["Vindhastighet (m/s)"], color = "blue")
        ax3.set_title("Vindhastighet")
        ax3.set_xlabel("Tid")
        ax3.set_ylabel("vindhastighet")
        ax3.legend(["Vindhastighet"])
        plt.xticks(rotation = 30)
        plt.show()
    def Plott_samtidig(self):
        fig, (ax1, ax2, ax3)= plt.subplots(3, 1, figsize=(15,10))

        sns.lineplot(x = "Tid",  y = "Temperatur (C)", color = "blue", data = self.df, ax = ax1)
        ax1.set_xlabel("tid")
        ax1.set_ylabel("Temperatur")
        ax1.set_title("Temperatur Over Tid")
        ax1.grid(True)
        plt.xticks(rotation = 30)
        

        sns.scatterplot(x = "Tid", y= "Temperatur (C)", hue = "Temperatur (C)", palette = "coolwarm", data=self.df, ax = ax2)
        ax2.set_xlabel("tid")
        ax2.set_ylabel("Temperatur")
        ax2.set_title("Temperatur Over Tid")
        plt.xticks(rotation = 30)
        

        ax3.plot(self.df["Tid"], self.df["Vindhastighet (m/s)"], color = "blue")
        ax3.set_title("Vindhastighet")
        ax3.set_xlabel("Tid")
        ax3.set_ylabel("vindhastighet")
        ax3.legend(["Vindhastighet"])
        plt.xticks(rotation = 30)
        plt.show()







        


        




