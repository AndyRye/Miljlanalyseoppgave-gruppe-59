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
    "User-Agent" : "MyWeatherApp/1.0(tvmoen@stud.ntnu.no)"
}

# En funksjon som skjekker om data mangler
def if_missing_data(weather_data):
    if all(entry[1] is not None and entry[2] is not None for entry in weather_data):
        print("Mangler ingen data for vindhastighet eller temperatur")


try:
    #Vi henter data fra vår API
    response = requests.get(url, params = params,  headers = headers)

    #Vi skjekker for HTTP-feil (400, 500...)
    response.raise_for_status()
    
    #Vi konverterer vår respons til JSON
    data = response.json()

    #Nå skjekker vi om de forventede nøklene finnes i JSON-dataene
    if "properties" not in data or "timeseries" not in data["properties"]:
        raise KeyError("NB JSON-struktur er ikke som forventet!")
    
    #Henter de første fem tidspunktene
    timeseries = data["properties"]["timeseries"][:5]

    weather_data = []
    for entry in timeseries:
        try:
            time = entry.get("time", "Mangler tid")
            details = entry.get("data", {}).get("instant", {}).get("details",{})

            temp = details.get("air_temperature")
            wind_speed = details.get("wind_speed")

            #Her skjekker vi om det mangler noe data
            if temp is None or wind_speed is None:
                print(f"NB Mangler data for {time}: Temperature={temp}, Vindhastighet={wind_speed}")

            #Vi legger til data i listen
            weather_data.append([time, temp, wind_speed])

        except KeyError as e:
            print(f"NB Feil ved parsing av JSON for {time}: {e}")
        
    #Skjekker om noen verdier mangler
    if_missing_data(weather_data)

    #Vi oppretter DataFrame
    df = pd.DataFrame(weather_data, columns =["Tid","Temperatur (C)", "Vindhastighet (m/s)"])

    #Rensing av dataen

    #Fjerner rader med manglende verdier
    df.dropna(inplace = True)

    #Fjerner urealistiske temperaturer 
    df = df[df["Temperatur (C)"].between(-50,50)]
    
    #Fjerner duplikater
    df.drop_duplicates(subset = ["Tid"], keep = "first", inplace = True)

    #Printer renset data
    print("\n Renset Værdata")
    print(df)

except requests.exceptions.RequestException as e:
    print(f"NB! Feil ved henting av API-data {e}")
except (KeyError, ValueError, TypeError) as e:
    print(f"NB! JSON-feil: {e}")


    



        

   


