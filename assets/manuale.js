
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
