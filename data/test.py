import pandas as pd
import json

import requests

#Url lenka til YR sin API
url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

#koordinater til Oslo

params = {
    "lat" : 59.9139, #bredde
    "lon" : 10.7522 #lengde
}


#Yr krever å vite hvem som bruker API-en deres, logger inn med min
headers = {
    "User-Agent" : "MyWeatherApp/1.0 (tvmoen@stud.ntnu.no)"
}

#Vi henter data fra vår API
response = requests.get(url, params = params,  headers = headers)

# vi skjekker om forespørselen er vellykket

if response.status_code == 200:
    data = response.json()



    print(json.dumps(data, indent=2))

    timeseries = data["properties"]["timeseries"][:5]

    weather_data = []
    for entry in timeseries:
        time = entry["time"]
        temp = entry["data"]["instant"]["details"]["air_temperature"]
        wind_speed = entry["data"]["instant"]["details"]["wind_speed"]
        weather_data.append([time, temp, wind_speed])

    with open(r"C:\Users\amund\OneDrive\Skrivebord\Anvendt programering\Miljlanalyseoppgave-gruppe-59\data\data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        

    #oppretter en dataframe vha pandas
    df = pd.DataFrame(weather_data, columns=["Tid", "Temperatur (C)", "Vindhastighet (m/s)"])

    print(df)

else:
    print(f"Feil oppstod ved henting av data: {response.status_code}")




