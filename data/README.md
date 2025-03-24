Gruppe 59; Amund, Anders, Tom-Vegar

Vi har valgt å skrive koden vår i en python fil (FilNavn.py) isteden for å jobbe sammen i Jupyter Notebook filer for å unngå merge conflicts. Dette gjør det lettere og mer effektivt for oss å sammarbeide som en gruppe. Vi skal så klart oppsumere koden senere i sluttfasen av mappeprojektet i en og samme jupyter notebook fil

Vi valgte å hente data gjennom Yr sin API. Dette er fordi vi ser på yr som en trygg og realistisk værmeldningsnettside å hente data fra. For programering i python er CSV filer ofte ett godt valg, men med tanke på plottingen i den neste delen av oppgaven, og ønsket om å minimere risiko for feil, valgte vi å hente data som en JSON fil ettersom at JSON-data allerede er strukturert data som gjør det lett for oss å finne feil og mangler. Som gjør det lettere for oss i oppgaven om rensing og databehanldig.

Vi vurderte å bruke Open weather forecast, men vi ønsket ikke å logge inn med bankkort og andre identifikasjoner, selv om det mest sansynelig er trygt, var det også en grunn til å velge Yr. Personlig id sikkerhet. Vi henter fra yr tiden, vindhastgheten og temperaturene

Det viktigste ved databehandlingen er å passe på at man ikke får urealistiske dataer. Derfor har vi begrenset temperaturen til å være mellom -50 og 50. Vi ønsker heller ikke å bare fjerne dataradene som mangler. Eksempel hvis det blåser gjevnt gjennom daten med 10 m/s, men vi mangler data kl 11. så er det dumt å fjerne dataen og sette lik 0. Dermed ønsler vi å finne en gjennomsnittstemp før og etter for å gi en mer realistisk værdata. Her ønsker vi å bruke Pandas SQL


sammelign med api med andre, jo kulere jo fete jo bedre. Lag en værapp, sammenlig og lag en intensjonertrjgoijoi toijt@ itij@åøijoøet@ åæoiqi4pi



# Tittel





## Undertittel

### mini tittel

**bold**

*italic*

> denen er ekstra tydlig

1. nummer 1
2. nummer 2
3. nummer 3

- point 1
- point 2
- point 3

- [x] done
- [ ] undone

`dette er kodeblock`