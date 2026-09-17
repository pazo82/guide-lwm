#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
genera.py — costruisce il manuale HTML «Magazzino LwM» dai .md di sorgenti/.

Regola d'oro: i .md sono l'originale, gli HTML sono un prodotto.
Ogni correzione si fa in sorgenti/ e si rigenera. Nessuno modifica un .html a mano.

Uso:   python3 genera.py
"""

import html as htmllib
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import date

RADICE = os.path.dirname(os.path.abspath(__file__))
SORGENTI = os.path.join(RADICE, "sorgenti")
IMG = os.path.join(RADICE, "assets", "img")

# ---------------------------------------------------------------- dati fissi

# numero, file sorgente, titolo, blocco, riga "a cosa serve" (brief 10 §4)
GUIDE = [
    (0, "guida_0_come_funziona_il_sistema.md", "Come funziona il sistema", "A",
     "I quattro componenti e chi fa cosa, i tre automatismi, le regole di fondo, la routine di lavoro."),
    (1, "guida_1_la_mappa_di_grist.md", "La mappa di Grist", "A",
     "Le tabelle e le pagine, cosa presidia ciascuna, quali campi contano e chi li scrive."),
    (2, "guida_2_gli_automatismi.md", "Gli automatismi (Make)", "A",
     "I tre scenari: quando partono, cosa scrivono, cosa non fanno, quali mail possono arrivare."),
    (3, "guida_3_ordini.md", "Ordini", "B",
     "Ordini aperti e magazzino, inserimento a mano, annullare invece che cancellare, kit e movimenti fra magazzini."),
    (4, "guida_4_resi_rimborsi.md", "Resi e rimborsi", "B",
     "La regola della spunta «Rifornisci i prodotti rimborsati», le due uscite di un reso, i casi delicati."),
    (5, "guida_5_catalogo_articoli_kit.md", "Catalogo, articoli e kit", "B",
     "Le regole del catalogo, aliquota e regime, articoli nuovi, kit e ricette."),
    (6, "guida_6_giacenze_inventario.md", "Giacenze e inventario", "B",
     "Leggere le giacenze, caricare merce, contare il magazzino, diagnosi quando i conti non tornano."),
    (7, "guida_7_report_fiscali.md", "Report fiscali", "B",
     "Cosa contengono i due report, chi entra e chi esce, la procedura di export, la checklist di chiusura."),
    (8, "guida_8_muoversi_in_grist.md", "Muoversi in Grist", "C",
     "Filtri, ordinamenti, ricerca, colonne, export; il temporaneo e il salvato; cosa non toccare mai."),
    (9, "guida_9_manutenzione_problemi.md", "Manutenzione e problemi", "C",
     "Il calendario dei controlli, sintomo → causa → azione, i rimedi ai guai già fatti, cosa segnalare."),
]

SCHEDA = ("scheda_a4_riferimento_rapido.md", "Scheda di riferimento rapido")

BLOCCHI = [
    ("A", "Capire", "Si leggono una volta, all'inizio."),
    ("B", "Fare", "Si consultano all'occorrenza."),
    ("C", "Cavarsela da sola", "Quando qualcosa non torna."),
]

# Allegato B del brief 11: (guida, numero screenshot) -> nome file
SCREENSHOT = {
    (0, 1): "g0-01-barra-pagine.png",
    (0, 2): "g0-02-ordini-aperti-magazzino.png",
    (0, 3): "g0-03-resi-attesa-rientro.png",
    (0, 4): "g0-04-mail-avviso.png",
    (0, 5): "g0-05-vista-vuota.png",
    (1, 1): "g1-01-dati-grezzi.png",
    (1, 2): "g1-02-articoli-colonne.png",
    (1, 4): "g1-04-ordini-tre-tipi.png",
    (1, 5): "g1-05-giacenze-filtri.png",
    (1, 3): "g1-03-inserimento-ordini.png",
    (2, 1): "g2-01-make-tre-scenari.png",
    (2, 2): "g2-02-mail-articoli-creati.png",
    (2, 3): "g2-03-cronologia-esecuzioni.png",
    (3, 1): "g3-01-ordini-aperti-tipi.png",
    (3, 2): "g3-02-maschera-prodotti.png",
    (3, 3): "g3-03-maschera-fattura.png",
    (3, 4): "g3-04-woo-stato-annullato.png",
    (4, 1): "g4-01-woo-finestra-rimborso.png",
    (4, 2): "g4-02-resi-kit-da-esplodere.png",
    (4, 3): "g4-03-resi-attesa-caselle.png",
    (5, 1): "g5-01-prodotti-due-lingue.png",
    (5, 2): "g5-02-articoli-famiglia-tshirt.png",
    (5, 3): "g5-03-articolo-da-verificare.png",
    (5, 4): "g5-04-bundle-ricetta.png",
    (5, 5): "g5-05-giacenze-filtro-kit.png",
    (6, 1): "g6-01-giacenze-venduto-x.png",
    (6, 2): "g6-02-maschera-approvvigionamento.png",
    (6, 3): "g6-03-approvvigionamenti-alert.png",
    (6, 4): "g6-04-giacenze-tshirt-nc.png",
    (6, 5): "g6-05-movimenti-articolo.png",
    (7, 1): "g7-01-report-corrispettivi.png",
    (7, 2): "g7-02-report-art74.png",
    (7, 3): "g7-03-scarica-xlsx.png",
    (7, 4): "g7-04-esporta-documento.png",
    (8, 1): "g8-01-quattro-zone.png",
    (8, 2): "g8-02-sort-and-filter.png",
    (8, 3): "g8-03-giacenze-menu-filtri.png",
    (8, 4): "g8-04-etichetta-id-colonna.png",
    (8, 5): "g8-05-menu-canale-edit.png",
    (9, 1): "g9-01-storia-documento.png",
    (9, 2): "g9-02-mail-scenario-disattivato.png",
    (9, 3): "g9-03-make-scenario-spento.png",
}

LARGHEZZA_MAX_FIGURA = 90  # caratteri: oltre, la figura scorre

# frasi in cui un colore di Grist è semantica e merita il campione (brief 11 §3.1)
COLORI = [
    (r"(?:intestazion[ei]|colonn[ae]|casell[ae]|cell[ae]|sfondo|band[ae])\s+"
     r"(arancion[ei]|grigi[oae]|viol[ae](?:\s+chiar[oa])?|azzurr[oaei])", None),
]

# ---------------------------------------------------------------- diagnostica

class Rapporto:
    def __init__(self):
        self.link_rotti = []
        self.img_mancanti = []
        self.figure_larghe = []
        self.img_piccole = []
        self.senza_didascalia = []
        self.marcatori = 0
        self.sezioni = 0

RAP = Rapporto()
ANCORE = {}          # numero guida -> set di sezioni esistenti
LINK_RICHIESTI = []  # (guida sorgente, guida destinazione, sezione)

# ---------------------------------------------------------------- utilità

def esc(t):
    return htmllib.escape(t, quote=False)

def slug(t):
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^\w\s-]", "", t.lower())
    return re.sub(r"[\s_]+", "-", t).strip("-")[:60]

def senza_tag(t):
    return re.sub(r"<[^>]*>", "", t)

def normalizza(t):
    """minuscolo e senza accenti: per l'indice di ricerca"""
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))

# ---------------------------------------------------------------- inline

RE_CODICE = re.compile(r"`([^`]+)`")
RE_FORTE = re.compile(r"\*\*(.+?)\*\*(?!\*)", re.S)
RE_CORSIVO = re.compile(r"(?<![\*\w])\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)")
RE_GUIDA = re.compile(r"\b([Gg]uid[ae])\s+(\d)\b")
RE_SEZ = re.compile(r"^\s*(?:\*\*)?\s*(?:,\s*sezion[ei]\s*(\d+)|§\s*(\d+))")
RE_MARCATORE = re.compile(r"non ancora verificat[oi] sul campo")
RE_SCHEDA = re.compile(r"\b([Ss]cheda\s+A4)\b")


def inline(t, guida_corrente=None, con_link=True):
    """testo markdown inline -> HTML"""
    codici = []

    def salva(m):
        codici.append(m.group(1))
        return "\x00%d\x00" % (len(codici) - 1)

    t = RE_CODICE.sub(salva, t)
    t = esc(t)
    t = RE_FORTE.sub(lambda m: "<strong>%s</strong>" % m.group(1), t)
    t = RE_CORSIVO.sub(lambda m: "<em>%s</em>" % m.group(1), t)

    if con_link:
        t = collega_guide(t, guida_corrente)
    t = marca_non_verificato(t)
    t = campioni_colore(t)

    for i, c in enumerate(codici):
        t = t.replace("\x00%d\x00" % i, "<code>%s</code>" % esc(c))
    return t


def collega_guide(t, guida_corrente):
    """«guida 4 §5», «guida 9, sezione 2», «guida 3» -> link.
    Si linka il solo testo «guida N»: la sezione finisce nell'indirizzo.
    Così il link non attraversa mai un tag <strong> aperto."""
    out, pos = [], 0
    for m in RE_GUIDA.finditer(t):
        n = int(m.group(2))
        coda = senza_tag(t[m.end():m.end() + 40])
        ms = RE_SEZ.match(coda)
        sez = None
        if ms:
            sez = int(ms.group(1) or ms.group(2))
        href = "guida-%d.html" % n
        if sez:
            href += "#s%d" % sez
        LINK_RICHIESTI.append((guida_corrente, n, sez))
        out.append(t[pos:m.start()])
        out.append('<a href="%s">%s %d</a>' % (href, m.group(1), n))
        pos = m.end()
    out.append(t[pos:])
    t = "".join(out)
    # la scheda, citata per nome
    if guida_corrente != "scheda":
        t = RE_SCHEDA.sub(lambda m: '<a href="scheda.html">%s</a>' % m.group(1), t)
    return t


def marca_non_verificato(t):
    def sostituisci(m):
        RAP.marcatori += 1
        return ('<span class="marcatore"><a href="guida-9.html#s9" '
                'title="elenco completo nella guida 9 §9">%s</a></span>' % m.group(0))
    # il marcatore vive dentro un <em>: si evidenzia l'intero corsivo che lo contiene
    return re.sub(r"<em>[^<]*non ancora verificat[oi] sul campo[^<]*</em>", sostituisci, t)


def campioni_colore(t):
    def sostituisci(m):
        colore = m.group(1)
        cls = ("arancione" if colore.startswith("arancion") else
               "grigio" if colore.startswith("grigi") else
               "viola" if colore.startswith("viol") else "azzurro")
        return '<span class="campione campione-%s" aria-hidden="true"></span>%s' % (cls, m.group(0))
    for pat, _ in COLORI:
        t = re.sub(pat, sostituisci, t)
    return t

# ---------------------------------------------------------------- blocchi

def rendi(linee, guida, livello_base=3):
    """converte un elenco di righe markdown in HTML"""
    out = []
    i = 0
    figura_in_attesa = None

    while i < len(linee):
        r = linee[i]
        s = r.strip()

        if not s:
            i += 1
            continue

        # blocco preformattato
        if s.startswith("```"):
            i += 1
            corpo = []
            while i < len(linee) and not linee[i].strip().startswith("```"):
                corpo.append(linee[i])
                i += 1
            i += 1
            largh = max([len(x) for x in corpo] or [0])
            if figura_in_attesa:
                if largh > LARGHEZZA_MAX_FIGURA:
                    RAP.figure_larghe.append((guida, figura_in_attesa, largh))
                out.append(
                    '<figure class="figura">\n<figcaption>%s</figcaption>\n'
                    '<pre>%s</pre>\n</figure>' % (figura_in_attesa, esc("\n".join(corpo))))
                figura_in_attesa = None
            else:
                out.append("<pre>%s</pre>" % esc("\n".join(corpo)))
            continue

        # separatore
        if re.match(r"^-{3,}$", s):
            out.append('<hr>')
            i += 1
            continue

        # intestazioni
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            liv, testo = len(m.group(1)), m.group(2)
            mf = re.match(r"^Figura\s+(\d+)\s*—\s*(.*)$", testo)
            if mf:
                figura_in_attesa = "Figura %s — %s" % (mf.group(1), inline(mf.group(2), guida))
                i += 1
                continue
            id_attr = ' id="%s"' % slug(testo)
            out.append("<h%d%s>%s</h%d>" % (min(liv + 1, 6), id_attr,
                                            inline(testo, guida), min(liv + 1, 6)))
            i += 1
            continue

        # citazione / riquadro
        if s.startswith(">"):
            blocco = []
            while i < len(linee) and linee[i].strip().startswith(">"):
                blocco.append(re.sub(r"^\s*>\s?", "", linee[i]))
                i += 1
            out.append(riquadro(blocco, guida))
            continue

        # tabella
        if s.startswith("|"):
            tab = []
            while i < len(linee) and linee[i].strip().startswith("|"):
                tab.append(linee[i].strip())
                i += 1
            out.append(tabella(tab, guida))
            continue

        # elenco numerato
        if re.match(r"^\d+\.\s", s):
            voci, i = raccogli_elenco(linee, i, r"^\d+\.\s+(.*)$")
            out.append("<ol>%s</ol>" % "".join(
                "<li>%s</li>" % rendi_voce(v, guida) for v in voci))
            continue

        # elenco puntato
        if re.match(r"^[-*]\s", s):
            voci, i = raccogli_elenco(linee, i, r"^[-*]\s+(.*)$")
            out.append("<ul>%s</ul>" % "".join(
                "<li>%s</li>" % rendi_voce(v, guida) for v in voci))
            continue

        # paragrafo
        par = [s]
        i += 1
        while i < len(linee):
            n = linee[i].strip()
            if (not n or n.startswith(("#", ">", "|", "```")) or
                    re.match(r"^([-*]\s|\d+\.\s|-{3,}$)", n)):
                break
            par.append(n)
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(par), guida))

    return "\n".join(out)


def raccogli_elenco(linee, i, pattern):
    """raccoglie le voci di un elenco, comprese le righe rientrate che le continuano"""
    voci = []
    while i < len(linee):
        r = linee[i]
        m = re.match(pattern, r.strip())
        if m and not r.startswith("   "):
            voci.append([m.group(1)])
            i += 1
        elif r.startswith("  ") and r.strip() and voci:
            voci[-1].append(r)
            i += 1
        else:
            break
    return voci, i


def rendi_voce(parti, guida):
    """una voce di elenco: prima riga inline, eventuali righe rientrate come sotto-elenco"""
    testo = inline(parti[0], guida)
    resto = [p for p in parti[1:] if p.strip()]
    if resto:
        sotto = [re.sub(r"^\s+", "", x) for x in resto]
        if all(re.match(r"^[-*]\s", x) for x in sotto):
            testo += "<ul>%s</ul>" % "".join(
                "<li>%s</li>" % inline(re.sub(r"^[-*]\s+", "", x), guida) for x in sotto)
        else:
            testo += " " + inline(" ".join(sotto), guida)
    return testo


def tabella(righe, guida):
    def celle(r):
        r = r.strip().strip("|")
        return [c.strip() for c in r.split("|")]

    testa = celle(righe[0])
    corpo = righe[2:] if len(righe) > 1 and re.match(r"^\|[\s:|-]+\|?$", righe[1]) else righe[1:]
    h = "".join("<th>%s</th>" % inline(c, guida) for c in testa)
    b = []
    for r in corpo:
        cs = celle(r)
        b.append("<tr>%s</tr>" % "".join(
            "<td>%s</td>" % cella_tabella(c, guida) for c in cs))
    return ('<div class="tabella"><table>\n<thead><tr>%s</tr></thead>\n'
            '<tbody>%s</tbody>\n</table></div>' % (h, "".join(b)))


RE_CELLA_RIMANDO = re.compile(r"^(\d)\s*§(\d+)((?:\s*,\s*§\d+)*)$")


def cella_tabella(c, guida):
    """nella scheda la colonna «Guida» contiene rimandi nudi: «3 §4, §5»"""
    m = RE_CELLA_RIMANDO.match(c.strip())
    if m:
        n = int(m.group(1))
        LINK_RICHIESTI.append((guida, n, int(m.group(2))))
        pezzi = ['<a href="guida-%d.html#s%s">%s §%s</a>' % (n, m.group(2), n, m.group(2))]
        for s in re.findall(r"§(\d+)", m.group(3)):
            LINK_RICHIESTI.append((guida, n, int(s)))
            pezzi.append('<a href="guida-%d.html#s%s">§%s</a>' % (n, s, s))
        return ", ".join(pezzi)
    return inline(c, guida)


def riquadro(linee, guida):
    """i tre tipi di riquadro del brief 10 §5, più il riquadro neutro"""
    testa = linee[0].strip() if linee else ""

    # screenshot
    m = re.match(r"^📷\s*\*\*Screenshot\s+(\d+)\*\*\s*—\s*(.*)$", testa)
    if m:
        return screenshot(int(m.group(1)), m.group(2), guida, linee[1:])

    # attenzione
    m = re.match(r"^⚠️?\s*\*\*(.+?)\*\*\s*(.*)$", testa)
    if m:
        coda = [m.group(2)] if m.group(2).strip() else []
        corpo = rendi(coda + linee[1:], guida)
        return ('<aside class="box box-attenzione">\n<p class="box-titolo">%s</p>\n%s\n</aside>'
                % (inline(m.group(1), guida), corpo))

    # perché funziona così
    m = re.match(r"^💡\s*\*\*(.+?)\*\*\s*(.*)$", testa)
    if m:
        coda = [m.group(2)] if m.group(2).strip() else []
        corpo = rendi(coda + linee[1:], guida)
        return ('<details class="box box-perche">\n<summary>%s</summary>\n<div class="box-corpo">%s</div>\n</details>'
                % (inline(m.group(1), guida), corpo))

    # riquadro neutro
    return '<aside class="box box-nota">\n%s\n</aside>' % rendi(linee, guida)


def larghezza_png(percorso):
    """larghezza in pixel di un PNG, letta dall'intestazione (niente dipendenze)"""
    try:
        with open(percorso, "rb") as f:
            testa = f.read(24)
        if testa[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        return int.from_bytes(testa[16:20], "big")
    except OSError:
        return None


RE_DIDASCALIA = re.compile(r"^\*Didascalia:\*\s*«?(.+?)»?\s*$")


def screenshot(n, cosa_mostra, guida, coda=()):
    """La riga «Screenshot N — ...» descrive cosa catturare: e' una specifica per chi
    scatta, e finisce nel testo alternativo. La riga «Didascalia:» che la segue e' la
    frase rivolta a chi legge, e diventa la didascalia visibile."""
    nome = SCREENSHOT.get((guida, n))
    visibile = None
    for r in coda:
        md = RE_DIDASCALIA.match(r.strip())
        if md:
            visibile = md.group(1)
            break
    if visibile is None:
        RAP.senza_didascalia.append((guida, n))
        visibile = cosa_mostra
    testo = inline(visibile, guida)
    piano = senza_tag(inline(cosa_mostra, guida))
    if not nome:
        RAP.img_mancanti.append((guida, n, "(nome non in Allegato B)"))
        nome = "g%s-%02d-da-definire.png" % (guida, n)
    percorso = os.path.join(IMG, nome)
    if os.path.exists(percorso):
        # ogni immagine e' catturata a 2x e resa a meta' dei suoi pixel: cosi' non viene
        # mai ingrandita, e una cattura a 1x si riconosce subito perche' esce piccola
        larg = larghezza_png(percorso)
        stile = ' style="width:%dpx"' % (larg // 2) if larg else ""
        if larg and larg < 2 * 320:
            RAP.img_piccole.append((guida, n, nome, larg))
        corpo = ('<a class="ingrandisci" href="assets/img/%s">'
                 '<img src="assets/img/%s" alt="%s" loading="lazy"%s></a>'
                 % (nome, nome, esc(piano), stile))
    else:
        RAP.img_mancanti.append((guida, n, nome))
        corpo = ('<div class="segnaposto"><span class="segnaposto-etichetta">'
                 'immagine da catturare</span><span class="segnaposto-file">%s</span></div>' % esc(nome))
    return ('<figure class="screenshot">\n%s\n'
            '<figcaption><span class="numero">Screenshot %d</span> %s</figcaption>\n</figure>'
            % (corpo, n, testo))

# ---------------------------------------------------------------- pagine

def leggi(nome):
    with open(os.path.join(SORGENTI, nome), encoding="utf-8") as f:
        return f.read().split("\n")


def costruisci_guida(numero, file_md, titolo):
    linee = leggi(file_md)

    # h1 e riquadro della versione
    h1 = linee[0].lstrip("# ").strip()
    versione = ""
    resto_da = 1
    for j in range(1, min(6, len(linee))):
        if linee[j].strip().startswith(">"):
            versione = re.sub(r"^\s*>\s?", "", linee[j]).strip()
            resto_da = j + 1
            break
    corpo_linee = linee[resto_da:]

    # sommario e ancore
    sezioni = []
    for r in corpo_linee:
        m = re.match(r"^##\s+(\d+)\.\s+(.*)$", r.strip())
        if m:
            sezioni.append((int(m.group(1)), m.group(2)))
    ANCORE[numero] = {n for n, _ in sezioni}
    RAP.sezioni += len(sezioni)

    # corpo, con i titoli di sezione riscritti con l'ancora
    html_corpo = []
    buffer = []
    testo_sezione = {}
    corrente = None
    for r in corpo_linee:
        m = re.match(r"^##\s+(\d+)\.\s+(.*)$", r.strip())
        if m:
            if buffer:
                html_corpo.append(rendi(buffer, numero))
                if corrente:
                    testo_sezione[corrente] = "\n".join(buffer)
            buffer = []
            corrente = int(m.group(1))
            html_corpo.append(
                '<h2 id="s%s"><a class="ancora" href="#s%s">§%s</a> %s</h2>'
                % (corrente, corrente, corrente, inline(m.group(2), numero)))
        else:
            buffer.append(r)
    if buffer:
        html_corpo.append(rendi(buffer, numero))
        if corrente:
            testo_sezione[corrente] = "\n".join(buffer)

    sommario = "".join(
        '<li><a href="#s%d"><span class="n">%d</span>%s</a></li>' % (n, n, esc(t))
        for n, t in sezioni)

    contenuto = """
<header class="testata">
  <p class="occhiello">Guida %d</p>
  <h1>%s</h1>
  %s
</header>
<nav class="sommario" aria-label="Sezioni della guida">
  <p class="sommario-titolo">In questa guida</p>
  <ol class="sommario-voci">%s</ol>
</nav>
<div class="corpo">
%s
</div>
""" % (numero, esc(titolo),
       '<p class="versione">%s</p>' % inline(versione, numero) if versione else "",
       sommario, "\n".join(html_corpo))

    scrivi_pagina("guida-%d.html" % numero,
                  "Guida %d — %s" % (numero, titolo),
                  contenuto, attiva=numero)

    # voci per l'indice di ricerca
    voci = []
    for n, t in sezioni:
        grezzo = testo_sezione.get(n, "")
        grezzo = re.sub(r"[#>*`|\-]+", " ", grezzo)
        grezzo = re.sub(r"\s+", " ", grezzo).strip()
        voci.append({
            "g": "Guida %d — %s" % (numero, titolo),
            "u": "guida-%d.html#s%d" % (numero, n),
            "s": "§%d. %s" % (n, t),
            "t": grezzo,
            "n": normalizza(t + " " + grezzo),
        })
    return voci


def costruisci_scheda():
    linee = leggi(SCHEDA[0])
    h1 = linee[0].lstrip("# ").strip()
    versione = ""
    resto_da = 1
    for j in range(1, 6):
        if linee[j].strip().startswith(">"):
            versione = re.sub(r"^\s*>\s?", "", linee[j]).strip()
            resto_da = j + 1
            break
    corpo = linee[resto_da:]

    out, buffer = [], []
    for r in corpo:
        m = re.match(r"^#\s+(FRONTE|RETRO)\s*$", r.strip())
        if m:
            if buffer:
                out.append(rendi(buffer, "scheda"))
            buffer = []
            out.append('<h2 class="faccia" id="%s">%s</h2>' % (m.group(1).lower(), m.group(1)))
            continue
        m = re.match(r"^##\s+(\d+)\s*·\s*(.*)$", r.strip())
        if m:
            if buffer:
                out.append(rendi(buffer, "scheda"))
            buffer = []
            out.append('<h3 id="p%s"><span class="ancora">%s</span> %s</h3>'
                       % (m.group(1), m.group(1), inline(m.group(2), "scheda")))
            continue
        buffer.append(r)
    if buffer:
        out.append(rendi(buffer, "scheda"))

    contenuto = """
<header class="testata">
  <p class="occhiello">Scheda</p>
  <h1>%s</h1>
  %s
  <p class="azioni"><button type="button" class="bottone" onclick="window.print()">Stampa la scheda</button></p>
</header>
<div class="corpo scheda">
%s
</div>
""" % (esc(h1), '<p class="versione">%s</p>' % inline(versione, "scheda") if versione else "",
       "\n".join(out))

    scrivi_pagina("scheda.html", SCHEDA[1], contenuto, attiva="scheda")
    testo = " ".join(re.sub(r"[#>*`|\-]+", " ", x) for x in corpo)
    return [{
        "g": "Scheda di riferimento rapido",
        "u": "scheda.html",
        "s": "Scheda di riferimento rapido",
        "t": re.sub(r"\s+", " ", testo),
        "n": normalizza(re.sub(r"\s+", " ", testo)),
    }]


def costruisci_indice():
    schede = []
    for codice, nome_blocco, sottotitolo in BLOCCHI:
        voci = []
        for n, _f, tit, blk, riga in GUIDE:
            if blk != codice:
                continue
            voci.append(
                '<a class="carta" href="guida-%d.html">'
                '<span class="carta-n">%d</span>'
                '<span class="carta-testo"><strong>%s</strong><span>%s</span></span></a>'
                % (n, n, esc(tit), esc(riga)))
        schede.append(
            '<section class="blocco"><h2>%s</h2><p class="blocco-sottotitolo">%s</p>'
            '<div class="carte">%s</div></section>' % (esc(nome_blocco), esc(sottotitolo), "".join(voci)))

    contenuto = """
<header class="testata testata-indice">
  <p class="occhiello">Sistema «Magazzino LwM»</p>
  <h1>Manuale operativo</h1>
  <p class="sottotitolo">Come si gestiscono magazzino, ordini e report fiscali fra WooCommerce, Grist e Make.</p>
</header>

<div class="ricerca-zona">
  <label class="ricerca-etichetta" for="q">Cerca in tutto il manuale</label>
  <input type="search" id="q" placeholder="per esempio: rifornisci i prodotti rimborsati" autocomplete="off">
  <div id="risultati" class="risultati" hidden></div>
</div>

<section class="come-si-usa">
  <h2>Come si usa</h2>
  <p>Le <strong>tre guide del blocco «Capire»</strong> si leggono una volta, all'inizio: spiegano com'è fatto il sistema e con quale lessico se ne parla. Quelle del blocco <strong>«Fare»</strong> non si leggono, si consultano: si apre quella dell'attività che si sta svolgendo. Le ultime due servono quando qualcosa non torna.</p>
  <p>Se è la prima volta, il percorso è <a href="guida-0.html">0</a> → <a href="guida-1.html">1</a> → <a href="guida-2.html">2</a>.</p>
</section>

%s

<section class="blocco blocco-scheda">
  <h2>Da tenere sulla scrivania</h2>
  <a class="carta carta-scheda" href="scheda.html">
    <span class="carta-n">A4</span>
    <span class="carta-testo"><strong>Scheda di riferimento rapido</strong>
    <span>Quando guardare, cosa non fare, dove andare. Due facciate, pensate per essere stampate.</span></span>
  </a>
</section>

<section class="confine">
  <h2>Fin dove si arriva da sole</h2>
  <p><strong>Ordinario:</strong> i controlli periodici, riavviare uno scenario fermo, rinnovare l'autorizzazione della posta, correggere dati, creare articoli e kit, registrare carichi e movimenti, gestire filtri, ordinamenti e colonne.</p>
  <p><strong>Da segnalare a Paolo:</strong> le formule, i moduli di Make, i collegamenti fra i due sistemi, il cambio di uno SKU esistente e qualsiasi cosa nuova da costruire. Cosa allegare a una segnalazione sta nella <a href="guida-9.html#s11">guida 9 §11</a>.</p>
</section>
""" % "\n".join(schede)

    scrivi_pagina("index.html", "Manuale operativo", contenuto, attiva="indice", indice=True)


def menu(attiva):
    righe = ['<a class="menu-voce menu-indice%s" href="index.html">Indice</a>'
             % (" attiva" if attiva == "indice" else "")]
    for codice, nome_blocco, _ in BLOCCHI:
        righe.append('<p class="menu-blocco">%s</p>' % esc(nome_blocco))
        for n, _f, tit, blk, _r in GUIDE:
            if blk != codice:
                continue
            righe.append('<a class="menu-voce%s" href="guida-%d.html">'
                         '<span class="menu-n">%d</span>%s</a>'
                         % (" attiva" if attiva == n else "", n, n, esc(tit)))
    righe.append('<p class="menu-blocco">Riferimento</p>')
    righe.append('<a class="menu-voce%s" href="scheda.html">'
                 '<span class="menu-n">A4</span>Scheda rapida</a>'
                 % (" attiva" if attiva == "scheda" else ""))
    return "\n".join(righe)


def scrivi_pagina(nome_file, titolo, contenuto, attiva, indice=False):
    prec = succ = ""
    if isinstance(attiva, int):
        if attiva > 0:
            prec = '<a href="guida-%d.html">‹ Guida %d</a>' % (attiva - 1, attiva - 1)
        if attiva < 9:
            succ = '<a href="guida-%d.html">Guida %d ›</a>' % (attiva + 1, attiva + 1)
    strumenti = ""
    if isinstance(attiva, int):
        strumenti = ('<button type="button" class="bottone-piatto" id="espandi">Espandi tutto</button>'
                     '<button type="button" class="bottone-piatto" onclick="window.print()">Stampa</button>')

    pagina = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>%(titolo)s · Magazzino LwM</title>
<link rel="stylesheet" href="assets/stile.css">
</head>
<body%(classe_body)s>
<a class="salta" href="#principale">Vai al contenuto</a>

<button type="button" class="apri-menu" id="apri-menu" aria-label="Apri il menu delle guide">☰ Guide</button>

<nav class="menu" id="menu" aria-label="Le guide">
  <p class="menu-titolo">Magazzino LwM</p>
  %(menu)s
</nav>

<div class="colonna">
  <div class="barra">
    <div class="barra-nav">%(prec)s %(succ)s</div>
    <div class="barra-strumenti">%(strumenti)s</div>
  </div>
  <main id="principale">
%(contenuto)s
  </main>
  <footer class="pie">
    <p>Manuale del sistema «Magazzino LwM» · generato il %(data)s</p>
    <p>Per i casi che non stanno nelle guide, e per qualsiasi cosa nuova da costruire, si scrive a Paolo: cosa allegare sta nella <a href="guida-9.html#s11">guida 9 §11</a>.</p>
  </footer>
</div>

<div class="lente" id="lente" hidden><img src="" alt=""></div>
%(ricerca)s
<script src="assets/manuale.js"></script>
</body>
</html>
""" % {
        "titolo": esc(titolo),
        "classe_body": ' class="pagina-indice"' if indice else "",
        "menu": menu(attiva),
        "prec": prec,
        "succ": succ,
        "strumenti": strumenti,
        "contenuto": contenuto,
        "data": date.today().strftime("%d/%m/%Y"),
        "ricerca": '<script src="assets/ricerca.js"></script>' if indice else "",
    }
    with open(os.path.join(RADICE, nome_file), "w", encoding="utf-8") as f:
        f.write(pagina)

# ---------------------------------------------------------------- risorse

def scrivi_risorse(voci_ricerca):
    os.makedirs(os.path.join(RADICE, "assets"), exist_ok=True)
    os.makedirs(IMG, exist_ok=True)
    with open(os.path.join(RADICE, "assets", "stile.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    with open(os.path.join(RADICE, "assets", "manuale.js"), "w", encoding="utf-8") as f:
        f.write(JS)
    with open(os.path.join(RADICE, "assets", "ricerca.js"), "w", encoding="utf-8") as f:
        f.write("window.INDICE_MANUALE = " + json.dumps(voci_ricerca, ensure_ascii=False) + ";\n")
    with open(os.path.join(RADICE, ".nojekyll"), "w") as f:
        f.write("")
    with open(os.path.join(RADICE, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nDisallow: /\n")

# ---------------------------------------------------------------- rapporto

def stampa_rapporto():
    print("\n" + "=" * 64)
    print("RAPPORTO DI GENERAZIONE — %s" % date.today().strftime("%d/%m/%Y"))
    print("=" * 64)
    print("Pagine prodotte      : %d guide + scheda + indice" % len(GUIDE))
    print("Sezioni numerate     : %d" % RAP.sezioni)

    rotti = []
    for sorgente, dest, sez in LINK_RICHIESTI:
        if dest not in ANCORE:
            rotti.append("guida %s → guida %s (guida inesistente)" % (sorgente, dest))
        elif sez and sez not in ANCORE[dest]:
            rotti.append("guida %s → guida %s §%s (sezione inesistente)" % (sorgente, dest, sez))
    rotti = sorted(set(rotti))

    print("Rimandi risolti      : %d" % len(LINK_RICHIESTI))
    print("1. Link non risolti  : %d %s" % (len(rotti), "" if not rotti else "← DA CORREGGERE"))
    for r in rotti:
        print("     · " + r)

    mancanti = sorted(set(RAP.img_mancanti))
    print("2. Screenshot mancanti: %d su %d" % (len(mancanti), len(SCREENSHOT)))

    print("3. Figure oltre %d car.: %d %s" % (
        LARGHEZZA_MAX_FIGURA, len(RAP.figure_larghe), "" if not RAP.figure_larghe else "← SCORRERANNO"))
    for g, cap, w in RAP.figure_larghe:
        print("     · guida %s — %s (%d caratteri)" % (g, senza_tag(cap), w))

    piccole = sorted(set(RAP.img_piccole))
    print("4. Immagini che si renderanno sotto i 320 px: %d %s" % (
        len(piccole), "" if not piccole else "← ritagli stretti, oppure catture a 1x: verificare"))
    for g, n, nome, w in piccole:
        print("     · %s (%d px)" % (nome, w))

    manca = sorted(set(RAP.senza_didascalia))
    print("5. Screenshot senza riga «Didascalia»: %d" % len(manca))
    for g, n in manca:
        print("     · guida %s, screenshot %s" % (g, n))

    print("6. Marcatori «non verificato»: %d  (da confrontare con l'elenco della guida 9 §9)"
          % RAP.marcatori)
    print("=" * 64 + "\n")
    return 1 if rotti or RAP.figure_larghe else 0

# ---------------------------------------------------------------- CSS e JS

CSS = r"""
/* Manuale «Magazzino LwM» — generato da genera.py, non modificare a mano */
:root{
  --accento:#14532d; --accento-chiaro:#dcfce7; --accento-medio:#166534;
  --inchiostro:#1c1917; --inchiostro-tenue:#57534e; --inchiostro-lieve:#78716c;
  --carta:#fffdf8; --carta-ombra:#f5f2ea; --filetto:#e7e2d6;
  --allarme:#b45309; --allarme-fondo:#fffbeb; --allarme-bordo:#fcd34d;
  --grist-arancione:#f6a35c; --grist-grigio:#c9c9c9; --grist-viola:#cdb7e8; --grist-azzurro:#a8d4ef;
  --colonna:760px;
  --testo:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--carta);color:var(--inchiostro);
  font-family:var(--testo);font-size:17px;line-height:1.65}
a{color:var(--accento);text-underline-offset:2px}
a:hover{color:var(--accento-medio)}
.salta{position:absolute;left:-9999px}
.salta:focus{left:1rem;top:1rem;background:var(--accento);color:#fff;padding:.5rem 1rem;z-index:50}

/* ---- menu laterale ---- */
.menu{position:fixed;top:0;left:0;bottom:0;width:250px;overflow-y:auto;
  background:var(--carta-ombra);border-right:1px solid var(--filetto);padding:1.4rem 0 2rem}
.menu-titolo{margin:0 1.2rem 1rem;font-size:.78rem;letter-spacing:.09em;text-transform:uppercase;
  color:var(--inchiostro-lieve)}
.menu-blocco{margin:1.3rem 1.2rem .35rem;font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;
  color:var(--inchiostro-lieve)}
.menu-voce{display:flex;gap:.6rem;align-items:baseline;padding:.42rem 1.2rem;
  color:var(--inchiostro);text-decoration:none;font-size:.92rem;line-height:1.35;
  border-left:3px solid transparent}
.menu-voce:hover{background:#efeade}
.menu-voce.attiva{background:var(--accento-chiaro);border-left-color:var(--accento);
  color:var(--accento);font-weight:600}
.menu-n{flex:0 0 1.5rem;font-variant-numeric:tabular-nums;color:var(--inchiostro-lieve);font-size:.85rem}
.menu-voce.attiva .menu-n{color:var(--accento)}
.menu-indice{margin-bottom:.4rem;font-weight:600}
.apri-menu{display:none}

/* ---- colonna ---- */
.colonna{margin-left:250px;padding:0 2.5rem 4rem;max-width:calc(var(--colonna) + 5rem)}
main{max-width:var(--colonna)}
.barra{display:flex;justify-content:space-between;align-items:center;gap:1rem;
  padding:.9rem 0;border-bottom:1px solid var(--filetto);margin-bottom:2.2rem;
  font-size:.85rem;flex-wrap:wrap}
.barra-nav a{margin-right:1rem;text-decoration:none;color:var(--inchiostro-tenue)}
.barra-nav a:hover{color:var(--accento)}
.bottone-piatto{background:none;border:1px solid var(--filetto);border-radius:4px;
  padding:.3rem .7rem;font:inherit;font-size:.82rem;color:var(--inchiostro-tenue);cursor:pointer}
.bottone-piatto:hover{border-color:var(--accento);color:var(--accento)}
.bottone{background:var(--accento);color:#fff;border:0;border-radius:5px;
  padding:.55rem 1.1rem;font:inherit;font-size:.9rem;cursor:pointer}

/* ---- testata ---- */
.testata{margin-bottom:2rem}
.occhiello{margin:0;font-size:.8rem;letter-spacing:.1em;text-transform:uppercase;color:var(--accento)}
.testata h1{margin:.2rem 0 .6rem;font-size:2.05rem;line-height:1.18;letter-spacing:-.015em}
.versione{margin:0;padding:.7rem .95rem;background:var(--carta-ombra);border-left:3px solid var(--filetto);
  font-size:.88rem;color:var(--inchiostro-tenue)}
.sottotitolo{margin:.3rem 0 0;font-size:1.05rem;color:var(--inchiostro-tenue)}

/* ---- sommario ---- */
.sommario{margin:0 0 2.6rem;padding:1.1rem 1.3rem;border:1px solid var(--filetto);border-radius:6px}
.sommario-titolo{margin:0 0 .6rem;font-size:.76rem;letter-spacing:.09em;text-transform:uppercase;
  color:var(--inchiostro-lieve)}
.sommario-voci{list-style:none;margin:0;padding:0;columns:2;column-gap:2rem}
.sommario-voci li{break-inside:avoid;margin:.16rem 0}
.sommario-voci a{display:flex;gap:.55rem;text-decoration:none;color:var(--inchiostro);font-size:.9rem}
.sommario-voci a:hover{color:var(--accento)}
.sommario-voci .n{flex:0 0 1.3rem;text-align:right;color:var(--inchiostro-lieve);
  font-variant-numeric:tabular-nums}

/* ---- testo ---- */
h2{margin:3rem 0 .9rem;font-size:1.42rem;line-height:1.25;letter-spacing:-.01em;
  padding-top:.7rem;border-top:2px solid var(--accento-chiaro)}
h3{margin:2rem 0 .6rem;font-size:1.1rem}
h4{margin:1.5rem 0 .4rem;font-size:1rem}
.ancora{text-decoration:none;color:var(--accento);font-variant-numeric:tabular-nums;
  font-size:.85em;margin-right:.15em}
p{margin:0 0 1.05rem}
ul,ol{margin:0 0 1.15rem;padding-left:1.3rem}
li{margin:.3rem 0}
li>ul,li>ol{margin:.35rem 0 .1rem}
strong{font-weight:650}
code{font-family:var(--mono);font-size:.87em;background:var(--carta-ombra);
  padding:.09em .34em;border-radius:3px;word-break:break-word}
hr{border:0;border-top:1px solid var(--filetto);margin:2.4rem 0}

/* ---- campioni di colore di Grist ---- */
.campione{display:inline-block;width:.72em;height:.72em;border-radius:2px;
  margin-right:.3em;vertical-align:baseline;border:1px solid rgba(0,0,0,.2)}
.campione-arancione{background:var(--grist-arancione)}
.campione-grigio{background:var(--grist-grigio)}
.campione-viola{background:var(--grist-viola)}
.campione-azzurro{background:var(--grist-azzurro)}

/* ---- marcatore ---- */
.marcatore a{color:var(--inchiostro-tenue);text-decoration:underline dotted;
  text-decoration-thickness:1px}
.marcatore{background:var(--carta-ombra);border-radius:3px;padding:.05em .3em}

/* ---- riquadri ---- */
.box{margin:1.6rem 0;border-radius:6px}
.box p:last-child{margin-bottom:0}
.box-attenzione{background:var(--allarme-fondo);border:1px solid var(--allarme-bordo);
  border-left:4px solid var(--allarme);padding:1rem 1.15rem}
.box-attenzione .box-titolo{color:var(--allarme);font-weight:650;margin-bottom:.55rem}
.box-attenzione .box-titolo::before{content:"⚠ ";}
.box-nota{background:var(--carta-ombra);border-left:3px solid var(--filetto);padding:.9rem 1.15rem}
.box-perche{border:1px solid var(--filetto);background:#fff}
.box-perche summary{cursor:pointer;padding:.7rem 1.1rem;font-weight:600;color:var(--accento);
  list-style:none;display:flex;gap:.5rem;align-items:baseline}
.box-perche summary::-webkit-details-marker{display:none}
.box-perche summary::before{content:"›";display:inline-block;transition:transform .15s;
  font-size:1.2em;line-height:1}
.box-perche[open] summary::before{transform:rotate(90deg)}
.box-perche summary:hover{background:var(--accento-chiaro)}
.box-corpo{padding:0 1.1rem 1rem;border-top:1px solid var(--filetto)}
.box-corpo>:first-child{margin-top:.9rem}

/* ---- figure ---- */
.figura{margin:1.9rem 0;border:1px solid var(--filetto);border-radius:6px;overflow:hidden}
.figura figcaption{background:var(--carta-ombra);padding:.6rem .95rem;font-size:.86rem;
  font-weight:600;color:var(--inchiostro-tenue);border-bottom:1px solid var(--filetto)}
.figura pre{margin:0;padding:1rem .95rem;overflow-x:auto}
pre{font-family:var(--mono);font-size:13px;line-height:1.42;overflow-x:auto;
  background:#fff;margin:1.5rem 0}

/* ---- screenshot ---- */
.screenshot{margin:1.9rem 0}
.screenshot img{display:block;max-width:100%;height:auto;border:1px solid var(--filetto);border-radius:5px}
.ingrandisci{display:block;cursor:zoom-in}
.screenshot figcaption{margin-top:.55rem;font-size:.86rem;color:var(--inchiostro-tenue);line-height:1.5}
.screenshot .numero{font-weight:650;color:var(--accento);margin-right:.3em}
.segnaposto{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.4rem;
  min-height:140px;border:2px dashed var(--filetto);border-radius:5px;background:var(--carta-ombra);
  padding:1.4rem}
.segnaposto-etichetta{font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;
  color:var(--inchiostro-lieve)}
.segnaposto-file{font-family:var(--mono);font-size:.8rem;color:var(--inchiostro-tenue)}

/* ---- tabelle ---- */
.tabella{overflow-x:auto;margin:1.6rem 0;border:1px solid var(--filetto);border-radius:6px}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{padding:.55rem .75rem;text-align:left;vertical-align:top;border-bottom:1px solid var(--filetto)}
th{background:var(--carta-ombra);font-weight:650;font-size:.84rem;white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:#faf8f2}

/* ---- lente ---- */
/* [hidden] deve vincere su qualsiasi display di classe: senza questa riga
   un pannello nascosto resta visibile (è successo con la lente) */
[hidden]{display:none!important}
.lente{position:fixed;inset:0;background:rgba(28,25,23,.92);display:flex;align-items:center;
  justify-content:center;padding:2rem;z-index:80;cursor:zoom-out}
.lente img{max-width:100%;max-height:100%;box-shadow:0 6px 40px rgba(0,0,0,.5)}

/* ---- piè di pagina ---- */
.pie{margin-top:4rem;padding-top:1.2rem;border-top:1px solid var(--filetto);
  font-size:.83rem;color:var(--inchiostro-lieve);max-width:var(--colonna)}
.pie p{margin:.25rem 0}

/* ---- indice ---- */
.pagina-indice .testata-indice h1{font-size:2.4rem}
.ricerca-zona{margin:2.2rem 0 2.6rem;position:relative}
.ricerca-etichetta{display:block;font-size:.76rem;letter-spacing:.09em;text-transform:uppercase;
  color:var(--inchiostro-lieve);margin-bottom:.45rem}
#q{width:100%;padding:.8rem 1rem;font:inherit;font-size:1rem;border:2px solid var(--filetto);
  border-radius:6px;background:#fff}
#q:focus{outline:none;border-color:var(--accento)}
.risultati{margin-top:.6rem;border:1px solid var(--filetto);border-radius:6px;background:#fff;
  max-height:420px;overflow-y:auto}
.risultato{display:block;padding:.7rem .95rem;border-bottom:1px solid var(--filetto);
  text-decoration:none;color:var(--inchiostro)}
.risultato:last-child{border-bottom:0}
.risultato:hover{background:var(--accento-chiaro)}
.risultato-guida{font-size:.74rem;letter-spacing:.06em;text-transform:uppercase;color:var(--accento)}
.risultato-sez{font-weight:600;display:block;margin:.1rem 0}
.risultato-ctx{font-size:.85rem;color:var(--inchiostro-tenue);display:block}
.risultato-ctx mark{background:var(--accento-chiaro);color:inherit;padding:0 .1em}
.niente{padding:.9rem .95rem;color:var(--inchiostro-tenue);font-size:.9rem}
.blocco{margin:2.6rem 0}
.blocco h2{border-top:0;padding-top:0;margin-bottom:.15rem;font-size:1.28rem}
.blocco-sottotitolo{color:var(--inchiostro-tenue);font-size:.92rem;margin:0 0 1rem}
.carte{display:grid;gap:.6rem}
.carta{display:flex;gap:1rem;align-items:flex-start;padding:.9rem 1rem;border:1px solid var(--filetto);
  border-radius:7px;text-decoration:none;color:var(--inchiostro);background:#fff}
.carta:hover{border-color:var(--accento);background:var(--accento-chiaro)}
.carta-n{flex:0 0 2rem;font-size:1.25rem;font-weight:650;color:var(--accento);
  font-variant-numeric:tabular-nums;line-height:1.3}
.carta-testo strong{display:block;margin-bottom:.1rem}
.carta-testo span{font-size:.9rem;color:var(--inchiostro-tenue);line-height:1.45}
.carta-scheda{border-style:dashed}
.come-si-usa,.confine{margin:2.4rem 0;padding:1.1rem 1.3rem;background:var(--carta-ombra);border-radius:7px}
.come-si-usa h2,.confine h2{margin:0 0 .6rem;border-top:0;padding-top:0;font-size:1.1rem}
.come-si-usa p:last-child,.confine p:last-child{margin-bottom:0}

/* ---- scheda ---- */
.faccia{border-top:0;letter-spacing:.12em;font-size:.9rem;color:var(--accento);
  padding-top:0;margin-top:2.6rem}
.corpo.scheda h3{border-top:1px solid var(--filetto);padding-top:1rem}
.corpo.scheda .ancora{display:inline-block;width:1.5rem;height:1.5rem;line-height:1.5rem;
  text-align:center;border-radius:50%;background:var(--accento);color:#fff;font-size:.8rem;
  margin-right:.35rem}

/* ---- schermi stretti ---- */
@media (max-width:980px){
  .menu{transform:translateX(-100%);transition:transform .2s;z-index:60;box-shadow:0 0 30px rgba(0,0,0,.15)}
  .menu.aperto{transform:none}
  .colonna{margin-left:0;padding:0 1.1rem 3rem;max-width:none}
  .apri-menu{display:block;position:sticky;top:0;z-index:55;width:100%;padding:.7rem 1.1rem;
    background:var(--carta-ombra);border:0;border-bottom:1px solid var(--filetto);
    font:inherit;font-size:.9rem;text-align:left;cursor:pointer;color:var(--inchiostro)}
  .sommario-voci{columns:1}
  .testata h1{font-size:1.7rem}
  body{font-size:16px}
}

/* ---- stampa ---- */
@media print{
  .menu,.barra,.apri-menu,.salta,.lente,.ricerca-zona,.azioni{display:none!important}
  .colonna{margin:0;padding:0;max-width:none}
  body{font-size:10.5pt;background:#fff;color:#000}
  main{max-width:none}
  a{color:#000;text-decoration:none}
  .box-perche{border:1px solid #bbb}
  .box-perche summary{color:#000}
  .box-corpo{display:block!important}
  .box,.figura,.screenshot,.tabella,table,tr{break-inside:avoid}
  h2,h3{break-after:avoid}
  .sommario{break-after:avoid}
  .pie{font-size:8pt}
  .corpo.scheda #retro{break-before:page}
  .segnaposto{min-height:70px}
}
"""

JS = r"""
/* Manuale «Magazzino LwM» — generato da genera.py */
(function () {
  "use strict";

  // menu su schermo stretto
  var apri = document.getElementById("apri-menu"),
      menu = document.getElementById("menu");
  if (apri && menu) {
    apri.addEventListener("click", function () { menu.classList.toggle("aperto"); });
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) menu.classList.remove("aperto");
    });
  }

  // espandi tutto
  var bottone = document.getElementById("espandi");
  if (bottone) {
    bottone.addEventListener("click", function () {
      var box = document.querySelectorAll("details.box-perche");
      var apriTutto = bottone.dataset.stato !== "aperto";
      for (var i = 0; i < box.length; i++) box[i].open = apriTutto;
      bottone.dataset.stato = apriTutto ? "aperto" : "chiuso";
      bottone.textContent = apriTutto ? "Richiudi tutto" : "Espandi tutto";
    });
  }

  // apre i riquadri quando si arriva da un link a un'ancora interna
  function apriContenitore(el) {
    var d = el && el.closest ? el.closest("details") : null;
    while (d) { d.open = true; d = d.parentElement.closest("details"); }
  }
  if (location.hash) {
    var bersaglio = document.querySelector(location.hash);
    if (bersaglio) { apriContenitore(bersaglio); bersaglio.scrollIntoView(); }
  }

  // stampa: tutto aperto, poi si richiude com'era
  var richiudi = [];
  window.addEventListener("beforeprint", function () {
    richiudi = [];
    var box = document.querySelectorAll("details");
    for (var i = 0; i < box.length; i++) if (!box[i].open) { box[i].open = true; richiudi.push(box[i]); }
  });
  window.addEventListener("afterprint", function () {
    for (var i = 0; i < richiudi.length; i++) richiudi[i].open = false;
  });

  // lente sugli screenshot
  var lente = document.getElementById("lente");
  if (lente) {
    var img = lente.querySelector("img");
    document.addEventListener("click", function (e) {
      var a = e.target.closest ? e.target.closest("a.ingrandisci") : null;
      if (a) {
        e.preventDefault();
        img.src = a.getAttribute("href");
        img.alt = a.querySelector("img") ? a.querySelector("img").alt : "";
        lente.hidden = false;
      } else if (!lente.hidden && e.target.closest("#lente")) {
        lente.hidden = true; img.src = "";
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !lente.hidden) { lente.hidden = true; img.src = ""; }
    });
  }

  // ricerca (solo sull'indice)
  var campo = document.getElementById("q"),
      cassetto = document.getElementById("risultati");
  if (!campo || !window.INDICE_MANUALE) return;

  function normalizza(s) {
    return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }
  function proteggi(s) {
    return s.replace(/[&<>]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c];
    });
  }

  var attesa;
  campo.addEventListener("input", function () {
    clearTimeout(attesa);
    attesa = setTimeout(cerca, 120);
  });

  function cerca() {
    var q = normalizza(campo.value.trim());
    if (q.length < 2) { cassetto.hidden = true; cassetto.innerHTML = ""; return; }
    var parole = q.split(/\s+/), trovati = [];

    for (var i = 0; i < window.INDICE_MANUALE.length; i++) {
      var v = window.INDICE_MANUALE[i], punti = 0, tutte = true;
      for (var p = 0; p < parole.length; p++) {
        var pos = v.n.indexOf(parole[p]);
        if (pos === -1) { tutte = false; break; }
        var freq = v.n.split(parole[p]).length - 1;
        punti += Math.min(freq, 6) + (normalizza(v.s).indexOf(parole[p]) !== -1 ? 20 : 0);
      }
      if (tutte) trovati.push({ v: v, punti: punti, pos: v.n.indexOf(parole[0]) });
    }
    trovati.sort(function (a, b) { return b.punti - a.punti; });
    trovati = trovati.slice(0, 12);

    if (!trovati.length) {
      cassetto.innerHTML = '<p class="niente">Nessun risultato. Prova con una parola sola, ' +
        'o con il nome della pagina di Grist.</p>';
      cassetto.hidden = false;
      return;
    }

    var html = "";
    for (var k = 0; k < trovati.length; k++) {
      var v = trovati[k].v, t = v.t, low = normalizza(t), at = low.indexOf(parole[0]);
      var da = Math.max(0, at - 60), ctx = t.slice(da, da + 190);
      if (da > 0) ctx = "…" + ctx;
      ctx = proteggi(ctx);
      var re = new RegExp("(" + parole[0].replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
      ctx = ctx.replace(re, "<mark>$1</mark>");
      html += '<a class="risultato" href="' + v.u + '">' +
        '<span class="risultato-guida">' + proteggi(v.g) + "</span>" +
        '<span class="risultato-sez">' + proteggi(v.s) + "</span>" +
        '<span class="risultato-ctx">' + ctx + "</span></a>";
    }
    cassetto.innerHTML = html;
    cassetto.hidden = false;
  }
})();
"""

# ---------------------------------------------------------------- avvio

def anteprima(nome_file):
    """copia autoportante di una pagina, con stile e script incorporati.
    Serve solo per far vedere il risultato a chi non ha la cartella: non è un formato
    di consegna, perché le immagini restano esterne."""
    with open(os.path.join(RADICE, nome_file), encoding="utf-8") as f:
        t = f.read()
    t = t.replace('<link rel="stylesheet" href="assets/stile.css">',
                  "<style>%s</style>" % CSS)
    t = t.replace('<script src="assets/manuale.js"></script>',
                  "<script>%s</script>" % JS)
    t = re.sub(r'<script src="assets/ricerca\.js"></script>', "", t)
    fuori = os.path.join(RADICE, "_anteprime")
    os.makedirs(fuori, exist_ok=True)
    uscita = os.path.join(fuori, "anteprima-" + nome_file)
    with open(uscita, "w", encoding="utf-8") as f:
        f.write(t)
    print("Anteprima autoportante: %s" % os.path.basename(uscita))


def main():
    if not os.path.isdir(SORGENTI):
        print("Manca la cartella sorgenti/", file=sys.stderr)
        return 2
    voci = []
    for numero, file_md, titolo, _blocco, _riga in GUIDE:
        voci += costruisci_guida(numero, file_md, titolo)
    voci += costruisci_scheda()
    costruisci_indice()
    scrivi_risorse(voci)
    esito = stampa_rapporto()
    if "--anteprima" in sys.argv:
        i = sys.argv.index("--anteprima")
        pagine = sys.argv[i + 1:] or ["guida-0.html"]
        for p in pagine:
            anteprima(p)
    return esito


if __name__ == "__main__":
    sys.exit(main())
