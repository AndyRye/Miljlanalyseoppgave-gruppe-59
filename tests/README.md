## Testing

# Enhetsstester for DataAnalyse

Vi har to tester for statistikkberegning. Statistikkberegning er en viktig del av vår kode, og for at denne skal gi logiske resultat bruker vi tester som sjekker at ingenting mangler fra "resultat", og at rounding er korrekt. Ved å sette inn uteligger i pandas DataFramen kunne vi også teste at koden håndterer urealistiske tall uten å krasje. 

Vi bruker remove_outliers metoden som skal forkaste rekker med unormalt høye z-scores. Dette er en sentral del av koden og gjør det mulig for oss å plott nøyaktige analyser. 

Vi har også valgt å teste skjevhetshåndeteringen; handle_skewness finjusterer formen uten å kaste bort observasjoner. 

Denne tilnærimgen gir både renslighet og justerer skjevhet, noe som er avgjørende for pålitlige, robuste analyser og prediksjoner. 

# Enhetsstester for FrostAPI

Her tester vi at enkelte sentrale funksjoner i FrostAPI fungerer. Vi har valgt å bruke mock for denne unittesten. Dette gjør det mulig å lage falske svarobjekter, i steden for at vi for å kalle frost APIen. Vi kan også enklere kontrollere hvilke data som skal brukes i testingen.  

Videre har vi testet at fetch_elementvalue fungerer som den skal slik at elementId henter korrekt og at metoden kan returnerer None når ID ikke finnes.

Videre tester vi at periodisk henting fungerer, og at ett ugyldig intervall vil kaste en ValueError. Dette er viktig at metoden validerer inputen som blir gitt og gir en klar feilmelding hvis brukeren ber om et ukjent intervall. 

# Enhetsstester for PredictiveAnalysis

Klassen starter med konstruere en DataFrame, og tester at split_data deler X og y i forventede former - både på antall rader og kolonner. Etter trening til predict alltid levere en prediksjon. Vi sjekker lengden på prediksjonsliten opp mot y_test for å avdekke eventuelle avvik.

Videre bruker vi forecast metoden til å bygge videre på predict, som itererer for flere steg fram i tid. Testen verifiserer at den returnerer riktig antall flyttall samt sjekke at alle talene er riktig datatype

# Enhetstester for DataPlotting

Bruker setUp() for å lage ett data sett som brukes i testing. 

test_histogram_returns_figure() sjekker at plot_histogram() returnerer en gydlig plotly til streamlit applikasjonen. 

test_box_plot_not_none() sjekker at plot_box_plot() plotter en box plot når det finnes tilgjenglig data for plotting. 

# Enhetstester for PlottingPredictiveAnalysis

Lager et testobjekt som brukes til videre testing. 

test_plot_predictive_analysis() sjekker at serienavnene er riktig. 

test_plot_forecast() sjekker at serianvnenn stemmer samt sjekekr at forecast verdiene plottes riktig. 

# Oppsummering 

Alle testene er blitt kjørt og fått OK status. Dermed er vi sikre på at sentrale deler av koden kjører og fungerer som ønsket. For å kjøre testene skriver man python -m unittest tests/"testen_man_vil_kjøre.py"



