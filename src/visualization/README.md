# plot_frost 

Funksjonen init brukes først til å fjerne dupliserte indekser og sparer datasettet. Her bruker vi data.index.duplicates() for å flagge duplikatene, og beholder kun den første forekomsten.

Videre bruker vi histogram som henter en kolonne fra self.data. Den plotter en rød striplet linje for gjennomsnitt, og en grønn linje for median. Om det er ingen data så returnerer den None. Dette skjer for alle plottefunksjonene

plot_box_plot velger alle numeriske kolonner og plotter en pandas boxplot.

plot_correlation_matrix beregner en korrealasjonsmatrise for numeriske kolonner. Vi bruker blant annet sns.heatmap med varme -og kalde farger. Vi har også tallverdier i hver celle, med mellomrom mellom de ulike cellene. 

plot_pair_analysis tar inn fire numeriske kolonner for bedre oversiktlighet og plotter en scatterplot med bruk av sns.pairplot. 

plot_timeseries er en interkativ tidsserie det vi bruker en rangeslider for å kunne enkelt se innenfor et bestemt tidsrom. I tillegg har vi med hover og zoom slik at leser for en god interaktiv opplevelse på den sentrale grafen.

plot_timeseries_with_statistics kombinerer seabirn med glidende gjennomsnitt som skal sikre at vi får en jevn graf i tillegg til standardavvik gitt som skyggeområdet. 

# plot_predictive 

Første funksjonen oppretter PredictiveAnalysis-objekt. Bruker funksjonene fra PredictiveAnalysis og får laget en prediksjon på testsettet. 

plot_predictive_analysis henter reelle og predikerte verdier med get.result, og plotter den i samme figur med plt.plot. 

plot_forecast tegner den historisek dataen, fut_idx lager en x-akse for fremtidige punkter. Tegner prognosen som punkter og en striplet linje. 

Begge metodene bruker matplotlib til å tegne, pynte, lagre og vise figurer. 

