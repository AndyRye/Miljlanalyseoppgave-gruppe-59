import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore, stats
import plotly.graph_objects as go
import os
import webbrowser
from data.fFrost import FrostAPI


api = FrostAPI()
df_frost = api.hent_data_for_periode("2023-01-01","2023-01-31", intervall ="W")

if not df_frost.empty:
    print("Hentet frost data:")
    print(df_frost.head())
    print(df_frost.describe())

    analyse = DataAnalyse(df_frost)

    temp_stats = analyse.beregn_statistikk("temperatur")
    print("\nStatistikk for temperatur:")
    print(temp_stats)

    alle_stats = analyse.beregn_alle_statistikker()
    print("\nStatistikk for alle kolonner:")
    print(alle_stats)

    korrelasjon = analyse.undersøk_sammenheng("temperatur", "skydekke")
    print(f"\nKorrelasjon mellom temperatur og skydekke {korrelasjon}")

    renset_data = analyse.fjern_uteliggere("temperatur")
    print(f"\nAntall datapunkter etter fjerning av uteliggere: {len(renset_data)}")

    normalitetstest = analyse.test_normalfordeling("temperatur")
    print("\nNormalitetstest for temperatur")
    print(f"p-verdi: {normalitetstest['p-verdi']:.4f}")
    print(f"Er dataene normalfordelt? {'Ja' if normalitetstest['er_normalfordelt'] else 'Nei'}")

    skjevhetsresultat = analyse.håndter_skjevhet("vind")
    print("\nHåndtering av skjevhet for vindhastighet:")
    print(f"Original skjevhet: {skjevhetsresultat['original_skjevhet']:.4f}")
    print(f"Transformert skjevhet: {skjevhetsresultat['transformert_skjevhet']:.4f}")
    print(f"Transformasjonstype: {skjevhetsresultat['transformasjonstype']}")

    analyse.plot_histogram("temperatur", filnavn="Temperatur_Histogram.png")
    analyse.plot_box_plot(filnavn="Værvariabler_Boxplot.png")
    analyse.plot_korrelasjonsmatrise(filnavn="Korrelasjon_Værvariabler.png")
    analyse.plot_par_analyse(filnavn="Paranalyse_Værvariabler.png")
    analyse.plot_tidserie("temperatur", filnavn="Temperatur_Tidsserie.html")
    analyse.plot_tidsserie_med_statistikk("temperatur", filnavn="Temperatur_Tidsserie_Statistikk.png")

    try:
        weather_api = WeatherAPI()
        df_yr = weather_api.get_week_view()

        if not df_yr.empty:
            analyse.sammenlign_med_yr(df_frost, df_yr, "temperatur", filnavn="Temperatur_Sammenligning.png")
    except Exception as e:
        print(f"Kunne ikke sammenligne med YR data {e}")
else:
    print("Ingen data hentet fra Frost API")

