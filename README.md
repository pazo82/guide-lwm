# guide-lwm — Manuale operativo «Magazzino LwM»

Manuale HTML per la gestione di magazzino, ordini e report fiscali fra WooCommerce, Grist e Make.
Pubblicato su GitHub Pages: `https://pazo82.github.io/guide-lwm/`

## La regola che conta

> **I `.md` in `sorgenti/` sono l'originale. Gli `.html` sono un prodotto.**
> Ogni correzione si fa nel `.md` e si rigenera. Nessuno modifica un `.html` a mano: la modifica
> sparirebbe alla rigenerazione successiva, e nell'intervallo il manuale direbbe due cose diverse.

## Come si rigenera

```
python3 genera.py
```

Riscrive le dodici pagine, il foglio di stile, gli script e l'indice di ricerca, e stampa il
rapporto di generazione: link interni non risolti, screenshot mancanti, figure troppo larghe,
marcatori «non ancora verificato sul campo». Le prime tre voci devono essere a zero prima di
pubblicare.

Nessuna dipendenza: serve solo Python 3.

Per una copia autoportante di una pagina, con stile e script incorporati (utile per mandarla a
qualcuno senza la cartella):

```
python3 genera.py --anteprima guida-0.html
```

## Struttura

```
sorgenti/          i .md — l'originale, qui si corregge
genera.py          il convertitore
index.html         pagina indice, con la ricerca
guida-0..9.html    le dieci guide
scheda.html        la scheda di riferimento rapido (pensata per la stampa)
assets/stile.css   foglio di stile, generato
assets/manuale.js  menu, riquadri, lente, ricerca — generato
assets/ricerca.js  indice di ricerca, generato
assets/img/        gli screenshot, più registro-immagini.md
.nojekyll          disattiva Jekyll su GitHub Pages
robots.txt         scoraggia l'indicizzazione
```

I file generati sono versionati apposta: GitHub Pages pubblica quello che trova nel ramo, senza
costruire niente.

## Prima di ogni pubblicazione

1. `python3 genera.py` senza segnalazioni sulle prime tre voci del rapporto.
2. **Nessuna immagine con dati personali non mascherati** in `assets/img/` — guardarle, una per una.
   Le righe marcate `DP` nel registro sono quelle da controllare. Un'immagine pubblicata per
   errore resta nella cronologia di git anche dopo essere stata rimossa.
3. `git add -A && git commit && git push` sul ramo pubblicato.

## Convenzioni

Stanno nel brief di progetto `11_brief_html.md`: struttura, palette, riquadri, procedura degli
screenshot, ancore e rimandi. Il brief `10_brief_guide_operative.md` contiene invece le
convenzioni di contenuto e di registro delle guide.
