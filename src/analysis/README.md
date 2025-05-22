# PredictiveAnalysis

PredictiveAnalysis klassen er en tidsserie-regresjon av temperatur som baserer seg på time forskøvet værvariabel fra frostAPI. Initialiseringsfunksjonen setter opp API klienten, tidsrom og stasjonene som bruker i analysen. 

fetch_and_prepare_data() henter dag-data i det ønskede tidsrommet. Her lager vi tre nye kolonner: temperatur, skydekke og vind fra forrige dag. Fjerner alle rader som er NaN, det vil alltid være den første raden, grunnet shift(1). Her bruker vi df.dropna(). Til slutt returneres den rensede DataFramen under self.df

split.data(test_size) deler self.df i X og y. X er her de tre "prev" kolonnene og y fungerer som en målvariabel for temperatur. Bruker indeksering basert på test_size for å konstruere X_train, X_test, y_train og y_test. 

train_model() starter en linær regresjon og trener (.fit) for X -og y_train. 

predict() kjører modellen på X_test og lagrer den resulterende prediksjonen i self.y_pred. 

evaluate_model() evaluerer pålitligheten til y_test. Her bruker vi MAE, RMSE og R2:

MAE: Ser på gjennomsnittet av de avvikene mellom verdier på X_test og y_pred i grader. 

RMSE: Ser på hvor mye avvikene påvirker feilet. 
R2: Sier hvor god modellen er til å forklare variasjoner i temperatur.
Disse verdiene vil bli returnert ti grader. (skriv noe om verdiene vi fikk)

# DataAnalysis 

Denne klassen starter med å ta inn en pandas.DataFrame og lagrer den i self.data. Dette gir alle funksjoner et felles datasett å jobbe på. 

calculate_statistics(self, kolonne) bruker til å beregne mål for en enkelt kolonne. Vi henter gjennomsnitt, median, standardavvik, minimum, maksimum, skjevhet og kurtose med hjelp av numpy biblioteket sine innebygde kommandoer. Til slutt returneres variablene i en ordbok.

calculate_all_statistics(self) finner numeriske kolonner i self.data. Kaller på calculate_statistics på alle kolonnene og setter resulterende ordbok inn i en ny DataFrame, med en rad og en kolonne per input. 

evaluate_correlation(self, kolonne1, kolonne2) beregner korrelasjoner mellom to numeriske kolonner i DataFrame.corr(). Deretter runder vi av resultatet til to desimaler og returnerer det. 

analyse_correlatin(self) henter alle numeriske kolonner i datasettet. Kjører corr() for å få hele korrelasjonsmatrisen som en DataFrame. 

test_normality(self, kolonne) tester på kolonnen med hjelp av stats.shapiro og p-value. Dette sjekker at en variabel er normalfordelt.

remove_outliers(self, kolonne, z_score_treshold=1) beregner z-score for hver verdi i kolonnen. Z-score måler hvor pålitlig verdiene i kolonnen er. Hvis en verdi blir designert med en z_score over den satte grensen vil den fjernes fra kolonnen. Dette gjentas frem til det ikke finnes flere rader. Da vil datasettet være renset for uteliggere. Det rensede datasettet blir returnert. 

handle_skewness målet opprinnelig skjevhet (skewness()) på kolonnen. Dersom skjevheten større eller lik 0 - brueker np.log1, hvis skjevheten <-1 brukes np.exp(). Dataen forblir uendret hvis ingen av disse stemmer. Deretter returneres en ordbok med, serien før og etter transformasjonen. Denne brukes hvis vi får en veldgi skjev fordeling uten å miste rader - viktig for å oppfylle kravene til normalfordeling eller varians i videre analyser. 

