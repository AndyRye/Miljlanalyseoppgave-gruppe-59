from weatherapi import WeatherAPI, Weather_Plotting

def hent_data():
    API = WeatherAPI()
    return API.get_month_view()

def interaktiv_plotting():
    df = hent_data()





