# Brief — Conversione HTML delle guide operative

> Redatto il 14/09/2026 · Documento di riferimento per le sessioni di produzione degli HTML

Questo documento sta al `10_brief_guide_operative.md` come un capitolato sta a un progetto: il `10` dice **cosa** raccontano le guide e a chi, questo dice **come** diventano un manuale navigabile. Vale per i dieci HTML delle guide, per la scheda di riferimento rapido e per la pagina indice.

Il principio che regge tutto il resto, e da cui discendono metà delle regole qui sotto:

> **I `.md` sono l'originale. Gli HTML sono un prodotto.** Ogni correzione si fa nel `.md` e si rigenera. Nessuno modifica un HTML a mano, mai, nemmeno per una virgola: la modifica sparirebbe alla prima rigenerazione, e nell'intervallo il manuale direbbe due cose diverse in due formati.

---

## 1. Le decisioni prese

| # | Decisione | Presa il |
|---|---|---|
| H1 | Cartella con CSS e JS condivisi, un file HTML per guida — non il file unico previsto dal `10` §12 | 14/09/2026 |
| H2 | Il testo HTML è **identico** al `.md`. Il «taglio più snello» del `10` §12 si ottiene collassando i box *Perché funziona così*, non tagliando testo | 14/09/2026 |
| H3 | Gli HTML si producono con uno **script di generazione**, non a mano | 14/09/2026 |
| H4 | La pagina indice ha una **ricerca** su tutto il testo del manuale | 14/09/2026 |
| H5 | Destinazione: **GitHub Pages** più una copia su Google Drive. Il pacchetto deve funzionare identico anche aperto da cartella locale | 14/09/2026 |
| H6 | Colore d'accento: **verde profondo** | 14/09/2026 |
| H7 | Screenshot con dati reali, **salvo i campi che identificano un cliente**, che vanno mascherati — vedi §8.3. È l'unico punto in cui la risposta della sessione del 14/09 è stata corretta, e il motivo sta lì | 14/09/2026 |

---

## 2. L'architettura del pacchetto

```
manuale/
├── .nojekyll
├── index.html
├── guida-0.html … guida-9.html
├── scheda.html
└── assets/
    ├── stile.css
    ├── manuale.js
    ├── ricerca.js          ← indice di ricerca, generato
    └── img/
        ├── g0-01-barra-pagine.png
        ├── …
        └── registro-immagini.md
```

**Dodici pagine HTML, un foglio di stile, due script.** Nient'altro.

### 2.1 Vincoli di costruzione

Sono vincoli e non preferenze: ognuno corrisponde a un posto dove il manuale dovrà girare.

- **Nessuna dipendenza esterna.** Niente font Google, niente CDN, niente librerie. Il manuale si apre in aereo, dentro una rete aziendale che blocca i domini esterni, e fra dieci anni quando quel CDN non esisterà più.
- **Percorsi solo relativi.** Su GitHub Pages un sito di progetto vive sotto `/nome-repo/`, quindi un percorso che comincia con `/` punta fuori dal sito e non trova niente. `assets/stile.css` funziona ovunque, `/assets/stile.css` funziona solo in locale.
- **Nomi di file minuscoli, senza spazi né accenti.** I server di GitHub Pages distinguono maiuscole e minuscole; il computer di casa no. Un `Giacenze.png` linkato come `giacenze.png` funziona in prova e si rompe in pubblicazione.
- **Script classici, non moduli.** Un `<script type="module">` viene bloccato dalle regole di origine quando la pagina è aperta da `file://`. Stessa ragione per cui l'indice di ricerca è un `.js` che assegna una variabile e non un `.json` letto con `fetch`: da cartella locale il `fetch` fallisce e la ricerca smette di funzionare proprio nella copia che si usa senza rete.
- **File `.nojekyll` vuoto nella radice.** GitHub Pages passa di default i contenuti attraverso Jekyll, che ignora file e cartelle il cui nome comincia con un trattino basso e può riscrivere cose che non vogliamo riscritte. Il `.nojekyll` disattiva tutto il meccanismo e pubblica i file così come sono.

### 2.2 Le due destinazioni, e cosa sanno fare

**GitHub Pages** è la sede di lettura: indirizzo stabile, aggiornamento con un `push`, e la cliente apre un link invece di gestire una cartella.

**Google Drive** non è una seconda sede di lettura. Drive non esegue HTML: apre l'anteprima di un file `.html` come testo, non come pagina. Su Drive va quindi messo **l'archivio `.zip` dell'intero pacchetto**, come copia di sicurezza e come via d'uscita se l'accesso a GitHub dovesse mancare. Scaricato e scompattato, funziona identico grazie ai vincoli del §2.1.

### 2.3 Il problema della visibilità, e come si chiude

Va detto in chiaro perché è il punto in cui questo progetto può fare un danno vero.

**Un sito GitHub Pages è pubblico anche quando il repository è privato.** Sui piani Free, Pro e Team non esiste alcun modo di limitarne l'accesso: la restrizione ai soli utenti del repository esiste solo su GitHub Enterprise Cloud. Repository privato significa che nessuno vede il codice sorgente; il sito pubblicato resta raggiungibile da chiunque abbia l'indirizzo, e indicizzabile.

Il manuale contiene 43 screenshot di un gestionale dove **la vista *Ordini Aperti* mostra nome, cognome, indirizzo di spedizione completo ed email dei clienti**, e la maschera di inserimento mostra anche partita IVA e codice fiscale. Pubblicarli su un sito aperto significa diffondere dati personali di terzi senza alcuna base per farlo, e non è un rischio teorico: è precisamente ciò che accadrebbe al primo `push`.

Da qui la decisione H7 e la procedura del §8.3. Le contromisure ausiliarie — `<meta name="robots" content="noindex">` su tutte le pagine e un `robots.txt` che scoraggia i motori — si applicano comunque, ma **non sono una soluzione**: riducono la probabilità che qualcuno arrivi, non l'esposizione. La soluzione è che quei dati non entrino nelle immagini.

---

## 3. Il sistema visivo

### 3.1 Il colore, che qui è documentazione

Il `10` §6 stabilisce che in Grist il colore è semantica: arancione per un presidio, viola chiaro per un campo dei resi, azzurro per la spedizione, **grigio per un campo da non toccare**. Se il manuale usa quegli stessi colori per decorarsi, sporca il codice esattamente dove la cliente deve leggerlo pulito.

**Regola: la grafica del manuale non usa arancione, viola, azzurro né grigio in funzione decorativa.** Palette:

| Ruolo | Valore | Dove |
|---|---|---|
| Accento | `#14532d` verde profondo | link, titoli di sezione, menu attivo, filetti |
| Accento chiaro | `#dcfce7` | sfondi tenui, riga attiva del menu |
| Inchiostro | `#1c1917` | testo |
| Inchiostro tenue | `#57534e` | didascalie, metadati, note |
| Carta | `#fffdf8` | fondo pagina |
| Carta ombra | `#f5f2ea` | fondo dei riquadri neutri |
| Richiamo *Attenzione* | `#b45309` su `#fffbeb` | **unica** eccezione all'arancione: è un bordo di riquadro, mai un'intestazione di colonna, e vive in un contesto in cui non si può confondere con Grist |
| Annotazione screenshot | `#e5007e` magenta | solo dentro le immagini, vedi §8.4 |

I colori di Grist compaiono **citati**, non usati: quando il testo dice «la colonna arancione», accanto alla parola sta un campioncino quadrato del colore vero. Diventa documentazione di un codice, non stile.

### 3.2 Tipografia e misura

- Font di sistema, senza grazie per il testo e monospaziato per `` `codice` ``, figure ASCII e nomi di colonna.
- Corpo **17px**, interlinea **1.65**.
- **Colonna di lettura 760px.** Non è una scelta estetica: la figura ASCII più larga della serie misura 90 caratteri, che a 13px monospaziati stanno in 700px. A 720px comincerebbero a scorrere orizzontalmente le figure della guida 5 e della 0.
- Titoli di sezione con il numero in evidenza e leggermente staccato: «§7» è la moneta dei rimandi e deve trovarsi con l'occhio, scorrendo.
- Un solo peso oltre al normale. Il testo delle guide usa già molto grassetto come strumento di scansione, e aggiungere una terza gradazione lo annacqua.

### 3.3 La stampa

Un foglio di stile di stampa è obbligatorio, non un extra: la scheda di riferimento rapido nasce per stare su una scrivania e non su uno schermo.

- Menu, barra di navigazione e pulsanti spariscono; la colonna si allarga.
- **Tutti i `<details>` si aprono.** Un manuale stampato con i box collassati perde 23 riquadri.
- Gli indirizzi dei link non vengono stampati fra parentesi: in un documento pieno di rimandi interni produrrebbe rumore illeggibile.
- `scheda.html` ha in più un layout a due pagine A4, fronte e retro, con interruzione forzata fra i due blocchi.
- Interruzioni di pagina evitate dentro un riquadro, una tabella o una figura.

### 3.4 Cosa non si fa

- **Niente tema scuro.** Quarantatré screenshot chiari dentro una pagina scura stanno peggio di una pagina chiara.
- Niente animazioni oltre l'apertura dei box.
- Niente icone decorative. Le tre emoji che il `.md` usa — ⚠️ 💡 📷 — diventano il segno grafico dei tre componenti e bastano.

---

## 4. Anatomia di una pagina guida

Dall'alto:

1. **Barra di navigazione** sottile: indice · scheda · guida precedente · guida successiva · «Espandi tutto» · «Stampa».
2. **Menu laterale** fisso a sinistra, con le undici voci raggruppate nei tre blocchi *Capire / Fare / Cavarsela da sola* e la guida corrente evidenziata. Sotto i 900px di larghezza diventa un pulsante che apre un pannello.
3. **Testata**: numero e titolo della guida, e sotto il riquadro della versione già presente nel `.md`.
4. **Sommario** generato dalle sezioni numerate, con i numeri visibili. Sta in cima, non fluttua.
5. **Il corpo**, nell'ordine del `.md`, invariato.
6. **Piè di pagina**: data di versione della guida, data di generazione del pacchetto, e la riga sul confine dell'autonomia con il riferimento del consulente.

Sul corpo l'unico intervento di layout è che **i titoli di sezione riportano il numero** e sono ancore cliccabili: clic sul titolo, l'indirizzo della sezione finisce nella barra e si può incollare in una mail.

---

## 5. La pagina indice

Non è un elenco di link. Nell'ordine:

1. **Titolo e una riga su cos'è** questo manuale, di chi è il sistema, a quale versione corrisponde.
2. **Ricerca**, in evidenza. È la prima cosa sotto il titolo perché è il modo in cui il manuale verrà usato nell'80% dei casi: non «leggo la guida 4», ma «dove sta quella spunta del rimborso».
3. **Come si usa**, quattro righe: le guide del blocco A si leggono una volta, quelle del blocco B si consultano, la 8 e la 9 servono quando qualcosa non torna. E il percorso per la prima volta: **0 → 1 → 2**.
4. **I tre blocchi in schede**, ognuna con numero, titolo e la riga «a cosa serve» già scritta nel `10` §4.
5. **La scheda di riferimento rapido in evidenza**, con il pulsante di stampa accanto: è l'unico pezzo del manuale pensato per vivere fuori dallo schermo.
6. **Il confine dell'autonomia** in tre righe — cosa è ordinario e cosa si segnala — con il riferimento del consulente. Oggi quella risposta è sparsa in nove guide, e la domanda «questo posso farlo io?» si fa prima di aprirne una.

### 5.1 La ricerca

Indice costruito in fase di generazione, salvato come `assets/ricerca.js`, che assegna un oggetto a una variabile globale. Una voce per **sezione**, non per guida: il risultato deve portare a `guida-6.html#s7`, non alla cima della guida 6.

Ogni voce porta guida, numero e titolo di sezione, e il testo ripulito da marcatura. Il risultato mostra il titolo della guida, il titolo della sezione e una riga di contesto attorno alla corrispondenza. Ricerca senza distinzione di accenti e maiuscole, perché nessuno scriverà «perché» con l'accento giusto mentre cerca in fretta.

Peso stimato: circa 300 KB non compressi, una quarantina serviti compressi. Accettabile.

---

## 6. Mappatura `.md` → HTML

La tabella completa sta nell'**Allegato A**. Qui i tre punti che decidono più degli altri.

**I box *Attenzione* sono sempre aperti.** Sono 56 e sono il motivo per cui questo manuale esiste: descrivono errori che non producono alcun messaggio. Un errore costoso non si mette dietro un clic.

**I box *Perché funziona così* sono chiusi.** Sono 20 e sono il «taglio più snello» previsto dal `10` §12, ottenuto senza mantenere due testi. Sul rischio che nasconderli sottragga contenuto alla ricerca del browser: **con Safari 26.2 tutti i browser principali aprono automaticamente un `<details>` chiuso quando la ricerca nella pagina trova una corrispondenza al suo interno**, ed è ormai il comportamento predefinito. Su versioni precedenti Firefox e Safari saltavano il contenuto chiuso. La contromisura è il pulsante **«Espandi tutto»** in testa a ogni guida, che serve anche per la stampa e per chi preferisce leggere disteso. La ricerca del §5.1 indicizza comunque il testo dei box, chiusi o aperti.

**Le tabelle non si ristrutturano.** Su schermo stretto scorrono orizzontalmente dentro il loro contenitore, e basta. La tentazione è spaccarle in schede impilate: applicata alle tabelle di questa serie — la matrice dei quattro percorsi del reso, i sette stati per tre domande della guida 3, i tre tipi di menu della guida 8 — distrugge proprio la cosa che le rende utili, cioè il confronto per colonna. Una matrice che scorre è leggibile; una matrice srotolata in elenco non è più una matrice.

---

## 7. Rimandi, ancore e numerazione

I `.md` contengono circa **170 rimandi incrociati** nelle due forme «guida 9, sezione 6» e «guida 5 §3». Diventano link, e li risolve lo script.

**Convenzione di ancora: la sezione numero N di una guida ha `id="sN"`.** Ricostruibile dal testo senza tabelle di conversione: `guida-4.html#s5`. Le sottosezioni (`###`) prendono un identificativo derivato dal titolo, e sono ancore ma non destinazioni di rimandi.

Ne discende un vincolo che vale la pena scrivere in grassetto, perché ha la stessa forma di metà delle avvertenze contenute nelle guide:

> **La numerazione delle sezioni è diventata un'interfaccia pubblica.** Rinumerare una sezione in un `.md` rompe in silenzio i link che la citano dalle altre otto guide e dalla scheda. È lo stesso tipo di rottura di una colonna rinominata in Grist: nessun errore, nessun segnale, e un rimando che porta nel posto sbagliato. Se una sezione va aggiunta in mezzo, si rinumera **e** si rigenera, e il controllo dei link morti del §9.3 dice cosa è rimasto indietro.

I rimandi alle immagini restano **per nome e non per numero** quando attraversano una guida, come già stabilito dal `10` §11.

---

## 8. Gli screenshot — procedura standard

Sono 43, elencati nell'**Allegato B**. La procedura è scritta per essere eseguita in sessioni brevi, un gruppo di immagini per volta, senza dover rileggere il resto del brief.

### 8.1 Il flusso, in breve

1. Apri l'Allegato B e prendi la riga dell'immagine da catturare: contiene già **dove va**, **cosa deve mostrare** e **come si chiamerà**.
2. Cattura seguendo il §8.2.
3. Se la riga è segnata **`DP`**, maschera i dati personali — §8.3.
4. Annota, se serve — §8.4.
5. Salva con il nome dell'Allegato B in `assets/img/`.
6. Segna la data nel registro e rigenera.

Non serve toccare l'HTML: la `<figure>` esiste già, con il nome file corretto, dal momento in cui la guida è stata generata la prima volta.

### 8.2 Cattura

- **Finestra del browser a 1440px, zoom al 100%**, tema chiaro. La larghezza fissa serve a che le colonne di Grist cadano sempre negli stessi punti: immagini catturate a larghezze diverse sembrano schermate di programmi diversi.
- **Cattura dell'area**, non dello schermo intero. Niente barra del browser, barra delle applicazioni, segnalibri, ora e notifiche. Eccezione: quando il punto è proprio dove si trova un comando del browser.
- **Inquadratura stretta su ciò che la didascalia nomina.** Metà di questi screenshot devono mostrare una singola cella, un menu o un pannello. Una pagina intera di Grist ridotta a 760px non si legge, e il lettore non sa dove guardare.
- **Sempre a 2×, senza eccezioni.** Il manuale rende ogni immagine a **metà dei suoi pixel**: un PNG largo 1520 occupa 760 e resta nitido su qualsiasi schermo, e un ritaglio stretto largo 690 occupa 345 invece di essere gonfiato a tutta colonna. Ne discende che una cattura a 1× non è «un po' meno bella»: esce **grande la metà del dovuto**. Il rapporto di generazione segnala le immagini sotto i 640 px.
- **Il riferimento sono i pixel voluti, non i pixel della schermata.** Un pannello che sullo schermo è largo 230 px, catturato a rapporto 2, produce un PNG da 460: reso a metà tornerebbe a 230, cioè minuscolo dentro una colonna da 760. Per i ritagli stretti si alza il rapporto a **3**, che porta lo stesso pannello a 690 px e lo rende a 345: grande una volta e mezzo il vero, e perfettamente nitido. Regola pratica: **rapporto 2 sulle tabelle, rapporto 3 su pannelli, menu e finestre.**
- **Zoom del browser al 100%, tranne sulle tabelle larghe.** *Giacenze*, *Giacenze T-Shirt* e i due report non stanno in 1440 px a zoom pieno: lì si scende all'**80%**, che a densità doppia resta perfettamente leggibile. Lo zoom usato va annotato nel registro, perché serve a rifare l'immagine uguale la volta dopo.
- **Tagliare le righe in eccesso.** Una tabella di Grist catturata per intero arriva a trenta righe: rese a metà pixel diventano righe da otto pixel, cioè un grigio. **Otto o dieci righe** sono il massimo utile, scelte in modo che dentro ci sia la cosa che la didascalia nomina.
- **Partire da una riga intera.** Se la cattura comincia a metà di una riga, la prima cosa che il lettore vede è un troncone: si scorre di mezza riga prima di scattare.
- **PNG**, ottimizzato dopo il salvataggio. Tetto **300 KB** per file. Se un'immagine sfora, quasi sempre vuol dire che l'inquadratura è troppo larga: si taglia meglio invece di comprimere di più.

### 8.3 Dati personali — le immagini `DP`

Undici delle 43 immagini inquadrano campi che identificano una persona. Nell'Allegato B sono marcate **`DP`**. Due gruppi:

- **Dati di clienti** — nome, cognome, email, indirizzo di spedizione, partita IVA, codice fiscale. Sono le immagini di *Ordini Aperti*, della pagina *Ordini*, della maschera *Inserimento Ordini*, di *Resi senza righe* e delle schermate di WooCommerce.
- **Dati interni** — indirizzi di posta di Letizia, Virginia e Paolo nelle intestazioni delle mail e nella storia del documento Grist.

**Come si maschera:** banda piena del colore del testo sopra i valori, **non sfocatura**. Una sfocatura leggera su testo piccolo è reversibile con mezzi banali, e una pixellatura non è molto meglio. La banda è definitiva e, per di più, si legge come «qui c'è un dato che non ti serve» invece che come un difetto dell'immagine.

Cosa si maschera: **i valori, non le intestazioni.** La colonna deve restare riconoscibile — serve a far capire dove si è — mentre il contenuto delle celle sparisce. Su *Ordini Aperti*, in concreto: restano visibili numero d'ordine, data, tipo, stato, totale, fattura, magazzino; spariscono email, nome, cognome e le sette colonne della spedizione.

Il numero d'ordine **non si maschera**: è un identificativo interno, serve alla didascalia, e le guide chiedono esplicitamente alla cliente di citarlo nelle segnalazioni.

### 8.4 Annotazioni

- **Un solo colore, il magenta `#e5007e`.** Scelto perché non è nessuno dei quattro colori semantici di Grist: un riquadro arancione disegnato sopra uno screenshot verrebbe letto come un'intestazione di presidio.
- Rettangolo dal bordo di **3px**, angoli vivi, nessuna ombra.
- Quando la didascalia indica più punti, **pallini numerati ①②③** in magenta, e la didascalia li richiama nell'ordine.
- **Nessun testo dentro l'immagine.** Il testo sta nella didascalia: un testo cotto dentro un PNG non si corregge senza rifare l'immagine, non si trova con la ricerca e non si legge con uno strumento di lettura assistita.
- Frecce solo dove un rettangolo non basta, cioè quasi mai.

### 8.5 Come l'immagine entra nella pagina

Lo script genera per ogni segnaposto 📷 una figura completa: immagine, didascalia numerata, testo alternativo uguale alla didascalia.

**Se il file non esiste, al suo posto compare un riquadro tratteggiato con dentro la didascalia** e la scritta «immagine da catturare», invece dell'icona di immagine rotta. Due conseguenze pratiche: gli HTML si possono pubblicare e leggere **prima** che le 43 catture siano finite, e quelle mancanti si vedono scorrendo la pagina invece di doverle rintracciare in una lista.

**Clic sull'immagine, ingrandimento a schermo intero.** Serve davvero: una tabella di Grist resa a 760px si intuisce ma non si legge, e senza ingrandimento saremmo costretti a inquadrature così strette da perdere il contesto.

### 8.6 Il registro

`assets/img/registro-immagini.md`, una riga per immagine: nome file, guida e sezione, cosa mostra, pagina Grist o WooCommerce ritratta, marcatore `DP`, data della cattura.

Serve a una cosa sola, ma importante: **quando una pagina di Grist cambia, sapere in dieci secondi quali immagini sono da rifare.** È lo stesso ruolo dello snapshot `09` per le formule, e la ragione è la stessa — un'immagine vecchia non dà errore, mostra semplicemente qualcosa che non esiste più.

L'Allegato B è la versione iniziale del registro, con le date da riempire.

### 8.7 Quando un'immagine invecchia

Tre eventi obbligano a rifare uno screenshot: una colonna che cambia etichetta o colore, una vista a cui si aggiungono o tolgono colonne o filtri, un aggiornamento di Grist o WooCommerce che cambia l'aspetto dei menu. Al verificarsi di uno dei tre si interroga il registro sulla pagina interessata e si rifanno le righe che escono.

Il nome del file **non cambia** quando l'immagine viene rifatta. Si sovrascrive: così il testo e il registro restano validi, e la cronologia del repository conserva comunque la versione precedente.

---

## 9. Lo script di generazione

### 9.1 Cosa fa

Un convertitore su misura, in Python, dentro il repository. Legge gli undici `.md` e produce i dodici HTML più il foglio di stile, gli script e l'indice di ricerca. In particolare:

- applica la mappatura dell'Allegato A;
- numera le sezioni e genera ancore e sommari;
- risolve i circa 170 rimandi incrociati nelle due forme;
- costruisce le figure degli screenshot, con il segnaposto per quelle mancanti;
- costruisce l'indice di ricerca;
- genera la pagina indice dalle testate delle guide e dalle righe «a cosa serve» del `10` §4;
- **riporta a schermo un rapporto**: link interni non risolti, screenshot mancanti, figure ASCII oltre la larghezza massima, sezioni fuori numerazione.

Non è un convertitore markdown generico. La sintassi dei `.md` è regolare — tre tipi di riquadro, figure sempre introdotte da `### Figura N`, screenshot sempre da `> 📷 **Screenshot N**` — e uno strumento su misura di trecento righe fa esattamente quello che serve senza portarsi dietro una dipendenza da aggiornare.

### 9.2 Come si usa

`python3 genera.py`, dalla radice del repository. Rigenera tutto: non esiste una generazione parziale, perché l'indice di ricerca e la risoluzione dei rimandi guardano tutte le guide insieme. Nessuna dipendenza da installare.

`python3 genera.py --anteprima guida-0.html` produce in più una copia autoportante di una pagina, con stile e script incorporati: serve per mostrare una guida a qualcuno senza mandargli la cartella, e non è un formato di consegna, perché le immagini restano esterne.

### 9.3 Il rapporto di generazione

Ogni esecuzione stampa quattro conteggi, ed è il collaudo automatico che sostituisce la lettura a campione:

1. **Link interni non risolti** — un rimando a una guida o a una sezione che non esiste. Deve essere **zero**.
2. **Screenshot mancanti** — normale durante la produzione, deve essere zero alla consegna.
3. **Figure oltre 90 caratteri** — deve essere zero, altrimenti quella figura scorre.
4. **Marcatori «non ancora verificato sul campo»** — non è un errore, è un numero da confrontare con l'elenco della guida 9 §9. Quando i due divergono, uno dei due è indietro.

---

## 10. Collaudo e pubblicazione

### 10.1 Checklist per guida

Da eseguire una volta per guida, la prima volta che viene generata:

- il rapporto del §9.3 non segnala niente su quella guida;
- le figure ASCII non scorrono a 760px;
- i box *Attenzione* sono tutti aperti, i *Perché* tutti chiusi;
- gli screenshot presenti hanno la didascalia giusta e quelli assenti mostrano il segnaposto;
- l'anteprima di stampa produce un documento sensato;
- la pagina si apre correttamente con doppio clic, senza rete.

### 10.2 Prima del primo `push` pubblico

Tre controlli, e sono quelli che non si possono rifare dopo:

1. **Nessuna immagine `DP` non mascherata** nella cartella. Da verificare guardandole, una per una, non fidandosi del registro.
2. `robots.txt` e `<meta name="robots" content="noindex">` presenti — contromisura ausiliaria, non sostitutiva del punto 1.
3. `.nojekyll` presente, percorsi relativi, nomi minuscoli.

Vale la pena aggiungere una cosa, che è una proprietà sgradevole di git: **un'immagine con dati personali pubblicata per errore e poi rimossa resta nella cronologia del repository.** Toglierla davvero richiede una riscrittura della cronologia. È il motivo per cui il controllo 1 va fatto prima e non dopo.

---

## 11. Punti aperti

- **Ordine degli screenshot nella guida 1.** Il numero 5 compare nel testo prima del 3 e del 4. Non è un errore di rimando — le didascalie sono coerenti — ma la numerazione non segue l'ordine di lettura, e alla consegna sembrerà una svista. Da rinumerare nel `.md`, oppure da lasciare consapevolmente: sono tre righe da spostare.
- **La scheda A4 risulta scritta** (14/09, `scheda_a4_riferimento_rapido.md`) mentre il `10` §13 la dà ancora da fare. Da allineare il `10`.
- **Il `10` §12 va aggiornato** con le decisioni H1 e H2: prevede un file unico e un testo ridotto, entrambi superati.
- **La conversione Word** resta da impostare e riuserà lo stesso convertitore con un secondo formato di uscita. Da affrontare quando gli HTML sono chiusi, non prima.
- ~~Il nome del repository~~ — *chiuso il 14/09/2026:* `pazo82/guide-lwm`, indirizzo `https://pazo82.github.io/guide-lwm/`.

---

## Allegato A — Mappatura `.md` → HTML

| Elemento nel `.md` | Resa | Note |
|---|---|---|
| `# Guida N — Titolo` | testata della pagina | anche `<title>` e voce del menu |
| `> **Versione del …**` subito sotto | riquadro neutro in testata | |
| `## N. Titolo` | titolo di sezione, `id="sN"` | numero in evidenza, ancora cliccabile, voce del sommario |
| `### Titolo` | sottotitolo, identificativo dal titolo | non entra nel sommario |
| `### Figura N — Titolo` + blocco ``` | figura con `<pre>` | didascalia sopra; scorrimento solo sotto 760px |
| `> ⚠️ **Attenzione — …**` | riquadro d'allarme | **sempre aperto**, bordo ambra, icona |
| `> 💡 **Perché funziona così**` | `<details>` | **chiuso**; si apre da solo con la ricerca del browser, e con «Espandi tutto» |
| `> 📷 **Screenshot N — …**` | figura con immagine e didascalia | segnaposto tratteggiato se il file manca; clic per ingrandire |
| `>` semplice | riquadro neutro | usato per i riquadri di nota |
| `` `testo` `` | `<code>` | nomi di colonne, tabelle e valori |
| `«Testo»` | corsivo leggero | etichette a schermo, caporali conservati |
| `*Pagina*` | corsivo | nomi di pagine e viste di Grist |
| `**testo**` | grassetto | invariato, è strumento di scansione |
| Tabelle | tabella con contenitore a scorrimento | **mai** ristrutturate in schede |
| «guida N §M» / «guida N, sezione M» | link a `guida-N.html#sM` | resa visiva uniforme |
| «guida N» senza sezione | link alla guida | |
| «scheda» / «scheda A4» | link a `scheda.html` | |
| *comportamento atteso, non ancora verificato sul campo* | etichetta inline uniforme | con link alla guida 9 §9 |
| `---` | separatore leggero | |

## Allegato B — Registro degli screenshot

`DP` = contiene dati personali, da mascherare secondo il §8.3. `DP-i` = dati interni (indirizzi di posta nostri).

| File | Sede | Cosa mostra | | Data |
|---|---|---|---|---|
| `g0-01-barra-pagine.png` | 0 §7 | La barra laterale di Grist con l'elenco completo delle pagine | | |
| `g0-02-ordini-aperti-magazzino.png` | 0 §7 | *Ordini Aperti*, menu del magazzino aperto su un ordine, un'altra casella arancione visibile | **DP** | |
| `g0-03-resi-attesa-rientro.png` | 0 §7 | *Resi in attesa di rientro*, le due caselle affiancate sulla stessa riga | | |
| `g0-04-mail-avviso.png` | 0 §7 | Una mail di avviso come arriva in casella | **DP-i** | |
| `g0-05-vista-vuota.png` | 0 §7 | Una vista di presidio vuota, es. *Resi di kit da esplodere* | | |
| `g1-01-dati-grezzi.png` | 1 §2 | *Dati grezzi* con l'elenco delle otto tabelle | | |
| `g1-02-articoli-colonne.png` | 1 §3 | *Articoli*: intestazioni colorate, colonne grigie, almeno una riga con «da verificare» acceso | | |
| `g1-03-ordini-tre-tipi.png` | 1 §5 | *Ordini* con tre righe di tipo diverso: Ordine, Reso, Approvvigionamento | **DP** | |
| `g1-04-giacenze-filtri.png` | 1 §5 | Barra dei filtri di *Giacenze*, filtri di comodo in vista e menu aperto | | |
| `g1-05-inserimento-ordini.png` | 1 §5 | *Inserimento Ordini*, i quattro riquadri con un ordine aperto | **DP** | |
| `g2-01-make-tre-scenari.png` | 2 §2 | Schermata iniziale di Make, tre scenari con gli interruttori accesi | | |
| `g2-02-mail-articoli-creati.png` | 2 §6 | La mail «Nuovi articoli creati in Grist automaticamente» con l'elenco | **DP-i** | |
| `g2-03-cronologia-esecuzioni.png` | 2 §8 | Cronologia di uno scenario con esecuzioni riuscite | | |
| `g3-01-ordini-aperti-tipi.png` | 3 §3 | *Ordini Aperti*: colonna del tipo, righe di stato diverso, due caselle magazzino arancioni | **DP** | |
| `g3-02-maschera-prodotti.png` | 3 §6 | Riquadro **PRODOTTI** con una riga in compilazione | | |
| `g3-03-maschera-fattura.png` | 3 §6 | Riquadro **VALORE ORDINE e FATTURA** a inserimento finito, campo fattura in evidenza | **DP** | |
| `g3-04-woo-stato-annullato.png` | 3 §11 | Menu degli stati di un ordine su WooCommerce, `Annullato` in evidenza | **DP** | |
| `g4-01-woo-finestra-rimborso.png` | 4 §3 | Finestra del rimborso su WooCommerce: importo, motivo, casella «Rifornisci i prodotti rimborsati:» | **DP** | |
| `g4-02-resi-kit-da-esplodere.png` | 4 §5 | *Resi di kit da esplodere* con una riga e l'avviso nella colonna arancione | | |
| `g4-03-resi-attesa-caselle.png` | 4 §5 | *Resi in attesa di rientro*, due o tre righe, le due caselle visibili | | |
| `g5-01-prodotti-due-lingue.png` | 5 §3 | *Prodotti*: le due righe, italiana e inglese, dello stesso SKU | | |
| `g5-02-articoli-famiglia-tshirt.png` | 5 §5 | *Articoli* filtrata su una famiglia di magliette: genitore e varianti | | |
| `g5-03-articolo-da-verificare.png` | 5 §8 | *Articoli*, articolo creato dal sistema: «da verificare» acceso, aliquota e listino vuoti | | |
| `g5-04-bundle-ricetta.png` | 5 §10 | *Bundle* filtrata su un kit: tre righe con componenti e quantità | | |
| `g5-05-giacenze-filtro-kit.png` | 5 §10 | *Giacenze* con il filtro dei kit: si vedono i componenti, il kit no | | |
| `g6-01-giacenze-venduto-x.png` | 6 §3 | *Giacenze* con almeno una riga a `venduto_X` diverso da zero | | |
| `g6-02-maschera-approvvigionamento.png` | 6 §5 | Maschera con un approvvigionamento compilato e una riga a quantità negativa | | |
| `g6-03-approvvigionamenti-alert.png` | 6 §5 | *Approvvigionamenti*: una riga pulita e una con avviso | | |
| `g6-04-giacenze-tshirt-nc.png` | 6 §8 | *Giacenze T-Shirt* con la colonna `N.C.` che mostra un numero | | |
| `g6-05-movimenti-articolo.png` | 6 §9 | *Movimenti di un articolo* su uno SKU, con `valido_per_giacenze` acceso e spento | | |
| `g7-01-report-corrispettivi.png` | 7 §4 | *REPORT Corrispettivi*, filtro del trimestre in barra, un giorno in cui `22%` è la somma delle due colonne | | |
| `g7-02-report-art74.png` | 7 §5 | *REPORT Art. 74* su un trimestre pieno, con alcuni mesi a zero visibili | | |
| `g7-03-scarica-xlsx.png` | 7 §7 | Menu a tre puntini aperto, voce «Scarica come XLSX» leggibile | | |
| `g7-04-esporta-documento.png` | 7 §7 | Menu di condivisione aperto sull'esportazione del documento intero | | |
| `g8-01-quattro-zone.png` | 8 §2 | Una pagina qualsiasi con le quattro zone evidenziate | ①②③④ | |
| `g8-02-sort-and-filter.png` | 8 §3 | Barra dei filtri con «Sort and filter» accesa in verde e il menu sui due comandi | | |
| `g8-03-giacenze-menu-filtri.png` | 8 §5 | Menu dei filtri di *Giacenze* aperto, con i filtri che non compaiono in barra | | |
| `g8-04-etichetta-id-colonna.png` | 8 §9 | Sezione «ETICHETTA E ID DELLA COLONNA», inquadratura stretta sui due campi e sulla catena | | |
| `g8-05-menu-canale-edit.png` | 8 §10 | Elenco delle scelte del canale aperto con «Edit», con il campo per aggiungere una voce | | |
| `g9-01-storia-documento.png` | 9 §3 | «Storia documento», scheda «Attività», modifiche recenti e due utenti diversi | **DP-i** | |
| `g9-02-mail-scenario-disattivato.png` | 9 §5 | La mail di Make che comunica la disattivazione di uno scenario | **DP-i** | |
| `g9-03-make-scenario-spento.png` | 9 §5 | Make con uno dei tre scenari spento, interruttore grigio accanto ai due accesi | | |
| `g9-04-esecuzioni-incomplete.png` | 9 §5 | Sezione delle esecuzioni incomplete con una riga in attesa | | |
