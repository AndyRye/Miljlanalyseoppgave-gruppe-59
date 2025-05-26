Gruppe 59; Amund, Anders, Tom-Vegar

# Væranalyse
dette er en interaktiv Streamlit-applikasjon som henter bearbeider, analyserer og predikerer data som er hentet fra Frost API (Oslo MET)
appen inkluderer statistikk, Maskinlæring, visualisering og analyse av rådataen som er hentet fra Oslo MET


## Krav for kjøring
- Python 3.8 + 
- internett tilkobling 
- requirements.txt installert


## Hvordan kjøre koden
For å åpne Vær appen må du kjøre:
        streamlit run data\main_app.py
i rot-terminalen

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


