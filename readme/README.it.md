README.it.md

Questo progetto è stato preparato per apprendere le API chatgpt, iptv-org e tmdb. I codici sono stati scritti interamente da chatgpt, quindi non so cosa manca, cosa è di troppo o cosa non va. Non so se posso prendere accordi in merito alle tue richieste in futuro. Nel file m3utostrm.py finale, tutte le spiegazioni, le istruzioni e le impostazioni sono in inglese. Tuttavia, nelle vecchie versioni nella cartella "old_versions", c'è scritto turco, che è la mia lingua. Mi spiace se questo sarà un problema per chi volesse utilizzare versioni precedenti.

Utilizza Python per scansionare il contenuto dei file ".m3u" scaricati dai fornitori di servizi IPTV e creare file ".strm" per film e programmi TV. Crea inoltre file ".nfo" utilizzando l'API TMDB e organizza le trasmissioni TV in file ".m3u" con l'API IPTVORG.

L'applicazione segue il seguente percorso per eseguire queste operazioni:
1) Installare le librerie Python da utilizzare se non sono installate,

2) Scarica il file ".m3u" con le informazioni del provider IPTV fornite dall'utente, nominandolo in base alla data e all'ora di esecuzione dell'applicazione,

3) Se non sono presenti altri file ".m3u" nella cartella in cui si trova il file ".m3u" scaricato, lo salverà anche come file "tobeprocess.m3u",

4) Se sono presenti altri file ".m3u" nella cartella in cui si trova il file ".m3u" scaricato, trova quello più recente esaminando i loro nomi,

5) Salva le linee URL che non si trovano nel file '.m3u' più recente che trova, ma si trovano nel file '.m3u' appena scaricato, come file 'tobeprocess.m3u',

6) Tiene traccia del numero rimanente di transazioni contando gli URL nel file "tobeprocess.m3u",

7) Crea cartelle "movies" per film, cartelle "serie" per serie TV e cartelle "porn" per contenuti porno per salvare file ".strm" e ".nfo",

8) Modifica i nomi delle trasmissioni dei canali IPTV con il modello del suffisso nel codice,

9) Crea file ".strm" nella cartella "porn" per "url" la cui denominazione è adatta per la denominazione porno,

10) Utilizzando la chiave API Tmdb, separa i restanti 'url' in film e serie TV,

11) Crea una cartella con un proprio nome per ogni film all'interno della cartella 'movies', e crea un file '.strm' in cui è scritto l''url' del film e un file '.nfo' contenente le informazioni prese dal sito tmdb,

12) Crea una cartella con un proprio nome per ogni serie all'interno della cartella 'series', questa cartella crea anche una cartella per le stagioni e crea un file '.strm' in cui è scritto l''url' della serie ed un ' file .nfo' contenente le informazioni ottenute dal sito tmdb,

13) Crea un nuovo file denominato "updated_channels.m3u" per le trasmissioni dei canali iptv nel file ".m3u" scaricato e ne modifica il contenuto con l'API iptv-org,


Miglioramenti pianificati da apportare;
- Opzione per scaricare il file '.m3u' o elaborare il file esistente,
