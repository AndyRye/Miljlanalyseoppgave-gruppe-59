Gruppe 59; Amund, Anders, Tom-Vegar

# Væranalyse
dette er en interaktiv Streamlit-applikasjon som henter bearbeider, analyserer og predikerer data som er hentet fra Frost API (Oslo MET)
appen inkluderer statistikk, Maskinlæring, visualisering og analyse av rådataen som er hentet fra Oslo MET


## Krav for kjøring
- Python 3.8 + 
- internett tilkobling 
- requirements.txt installert


## Hvordan kjøre koden
#### For å åpne Vær appen må du kjøre:
- streamlit run data\main_app.py

i rot-terminalen
#### Klone repoet:
- git clone https://github.com/AndyRye/Miljlanalyseoppgave-gruppe-59

#### Laste ned requirements.txt
- pip install -r requirements.txt



## Hvordan funker Appen?
App-GUIen satt opp i to hoveddeler, en sidebar og en hoveddel

#### Sidebar
Her kan du velge kondigurasjoner:
- Datointervallet du vil hente historisk data fra
- Antall dager du vil predikere

#### Hoveddel
hoveddelen er delt opp i to Main tabs:
Historisk data og Prediktiv data
1. Historik data
Historisk data har 3 underdelinger:
- Temperatur
- Vind
- Skydekke
i hver av disse vises grafer som her plottet ved hjelp av klasser

det er også nedlastningsknapper for:
- Rådata
- Renset data
- Uteliggere
- Transformasjoner

2. Prediktiv data
her bruker vi PredictiveAnalysis og PlottingPredictiveAnalysis til å vise treningsdataen og prediksjon
vi viser evaluerings-metri



## Plotting

### Plotting av historisk data

- Funksjonen init brukes først til å fjerne dupliserte indekser og sparer datasettet. Her bruker vi data.index.duplicates() for å flagge duplikatene, og beholder kun den første forekomsten.

- Videre bruker vi histogram som henter en kolonne fra self.data. Den plotter en rød striplet linje for gjennomsnitt, og en grønn linje for median. Om det er ingen data så returnerer den None. Dette skjer for alle plottefunksjonene

- plot_box_plot velger alle numeriske kolonner og plotter en pandas boxplot.

- plot_correlation_matrix beregner en korrealasjonsmatrise for numeriske kolonner. Vi bruker blant annet sns.heatmap med varme -og kalde farger. Vi har også tallverdier i hver celle, med mellomrom mellom de ulike cellene. 

- plot_pair_analysis tar inn fire numeriske kolonner for bedre oversiktlighet og plotter en scatterplot med bruk av plotly. 

- plot_timeseries er en interkativ tidsserie det vi bruker en rangeslider for å kunne enkelt se innenfor et bestemt tidsrom. I tillegg har vi med hover og zoom slik at leser for en god interaktiv opplevelse på den sentrale grafen.

- plot_timeseries_with_statistics har et glidende gjennomsnitt som skal sikre at vi får en jevn graf i tillegg til standardavvik gitt som skyggeområdet. 

### Plotting av prediskjoner

- Første funksjonen oppretter PredictiveAnalysis-objekt. Bruker funksjonene fra PredictiveAnalysis og får laget en prediksjon på testsettet. 

- plot_predictive_analysis henter reelle og predikerte verdier med get.result, og plotter den i samme figur med plotly. 

- plot_forecast tegner den historisek dataen, fut_idx lager en x-akse for fremtidige punkter. Tegner prognosen som punkter og en striplet linje. 

- Begge metodene bruker plotly til å tegne, pynte, lagre og vise interaktive figurer. 


## Prediktiv Analyse

- PredictiveAnalysis klassen er en tidsserie-regresjon av temperatur som baserer seg på time forskøvet værvariabel fra frostAPI. Initialiseringsfunksjonen setter opp API klienten, tidsrom og stasjonene som bruker i analysen. 

- fetch_and_prepare_data() henter dag-data i det ønskede tidsrommet. Her lager vi tre nye kolonner: temperatur, skydekke og vind fra forrige dag. Fjerner alle rader som er NaN, det vil alltid være den første raden, grunnet shift(1). Her bruker vi df.dropna(). Til slutt returneres den rensede DataFramen under self.df

- split.data(test_size) deler self.df i X og y. X er her de tre "prev" kolonnene og y fungerer som en målvariabel for temperatur. Bruker indeksering basert på test_size for å konstruere X_train, X_test, y_train og y_test. 

- train_model() starter en linær regresjon og trener (.fit) for X -og y_train. 

- predict() kjører modellen på X_test og lagrer den resulterende prediksjonen i self.y_pred. 

- evaluate_model() evaluerer pålitligheten til y_test. Her bruker vi MAE, RMSE og R2:

- MAE: Ser på gjennomsnittet av de avvikene mellom verdier på X_test og y_pred i grader. 

- RMSE: Ser på hvor mye avvikene påvirker feilet. 
R2: Sier hvor god modellen er til å forklare variasjoner i temperatur.
Disse verdiene vil bli returnert ti grader. (skriv noe om verdiene vi fikk)

## DataAnalysis 

- Denne klassen starter med å ta inn en pandas.DataFrame og lagrer den i self.data. Dette gir alle funksjoner et felles datasett å jobbe på. 

- calculate_statistics(self, kolonne) bruker til å beregne mål for en enkelt kolonne. Vi henter gjennomsnitt, median, standardavvik, minimum, maksimum, skjevhet og kurtose med hjelp av numpy biblioteket sine innebygde kommandoer. Til slutt returneres variablene i en ordbok.

- calculate_all_statistics(self) finner numeriske kolonner i self.data. Kaller på calculate_statistics på alle kolonnene og setter resulterende ordbok inn i en ny DataFrame, med en rad og en kolonne per input. 

- evaluate_correlation(self, kolonne1, kolonne2) beregner korrelasjoner mellom to numeriske kolonner i DataFrame.corr(). Deretter runder vi av resultatet til to desimaler og returnerer det. 

- analyse_correlatin(self) henter alle numeriske kolonner i datasettet. Kjører corr() for å få hele korrelasjonsmatrisen som en DataFrame. 

- test_normality(self, kolonne) tester på kolonnen med hjelp av stats.shapiro og p-value. Dette sjekker at en variabel er normalfordelt.

- remove_outliers(self, kolonne, z_score_treshold=1) beregner z-score for hver verdi i kolonnen. Z-score måler hvor pålitlig verdiene i kolonnen er. Hvis en verdi blir designert med en z_score over den satte grensen vil den fjernes fra kolonnen. Dette gjentas frem til det ikke finnes flere rader. Da vil datasettet være renset for uteliggere. Det rensede datasettet blir returnert. 

- handle_skewness målet opprinnelig skjevhet (skewness()) på kolonnen. Dersom skjevheten større eller lik 0 - brueker np.log1, hvis skjevheten <-1 brukes np.exp(). Dataen forblir uendret hvis ingen av disse stemmer. Deretter returneres en ordbok med, serien før og etter transformasjonen. Denne brukes hvis vi får en veldgi skjev fordeling uten å miste rader - viktig for å oppfylle kravene til normalfordeling eller varians i videre analyser. 


## Testing

### Enhetsstester for DataAnalyse

- Vi har to tester for statistikkberegning. Statistikkberegning er en viktig del av vår kode, og for at denne skal gi logiske resultat bruker vi tester som sjekker at ingenting mangler fra "resultat", og at rounding er korrekt. Ved å sette inn uteligger i pandas DataFramen kunne vi også teste at koden håndterer urealistiske tall uten å krasje. 

- Vi bruker remove_outliers metoden som skal forkaste rekker med unormalt høye z-scores. Dette er en sentral del av koden og gjør det mulig for oss å plott nøyaktige analyser. 

- Vi har også valgt å teste skjevhetshåndeteringen; handle_skewness finjusterer formen uten å kaste bort observasjoner. 

- Denne tilnærimgen gir både renslighet og justerer skjevhet, noe som er avgjørende for pålitlige, robuste analyser og prediksjoner. 

### Enhetsstester for FrostAPI

- Her tester vi at enkelte sentrale funksjoner i FrostAPI fungerer. Vi har valgt å bruke mock for denne unittesten. Dette gjør det mulig å lage falske svarobjekter, i steden for at vi for å kalle frost APIen. Vi kan også enklere kontrollere hvilke data som skal brukes i testingen.  

- Videre har vi testet at fetch_elementvalue fungerer som den skal slik at elementId henter korrekt og at metoden kan returnerer None når ID ikke finnes.

- Videre tester vi at periodisk henting fungerer, og at ett ugyldig intervall vil kaste en ValueError. Dette er viktig at metoden validerer inputen som blir gitt og gir en klar feilmelding hvis brukeren ber om et ukjent intervall. 

### Enhetsstester for PredictiveAnalysis

- Klassen starter med konstruere en DataFrame, og tester at split_data deler X og y i forventede former - både på antall rader og kolonner. Etter trening til predict alltid levere en prediksjon. Vi sjekker lengden på prediksjonsliten opp mot y_test for å avdekke eventuelle avvik.

- Videre bruker vi forecast metoden til å bygge videre på predict, som itererer for flere steg fram i tid. Testen verifiserer at den returnerer riktig antall flyttall samt sjekke at alle talene er riktig datatype

### Enhetstester for DataPlotting

- Bruker setUp() for å lage ett data sett som brukes i testing. 

- test_histogram_returns_figure() sjekker at plot_histogram() returnerer en gydlig plotly til streamlit applikasjonen. 

- test_box_plot_not_none() sjekker at plot_box_plot() plotter en box plot når det finnes tilgjenglig data for plotting. 

### Enhetstester for PlottingPredictiveAnalysis

- Lager et testobjekt som brukes til videre testing. 

- test_plot_predictive_analysis() sjekker at serienavnene er riktig. 

- test_plot_forecast() sjekker at serianvnenn stemmer samt sjekekr at forecast verdiene plottes riktig. 

### Oppsummering 

- Alle testene er blitt kjørt og fått OK status. Dermed er vi sikre på at sentrale deler av koden kjører og fungerer som ønsket. For å kjøre testene skriver man python -m unittest tests/"testen_man_vil_kjøre.py"