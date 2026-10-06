/* JOBPREP_DA flashcards: study-guide and interview-mock Q&A. Click/Space to flip, ←/→ to move. */
(function () {
  "use strict";
  var app = document.getElementById("fc-app");
  if (!app) return;
  var KEY = "jobprep-flashcards-v1";
  var known = {};
  try { known = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { known = {}; }
  var all = [], deck = [], i = 0, flipped = false;

  function h(tag, cls, html) { var n = document.createElement(tag); if (cls) n.className = cls; if (html !== undefined) n.innerHTML = html; return n; }
  function saveKnown() { try { localStorage.setItem(KEY, JSON.stringify(known)); } catch (e) { /* ignore */ } }

  var controls = h("div", "fc-controls");
  var chapter = h("select"); chapter.setAttribute("aria-label", "Filter by chapter");
  var search = h("input"); search.type = "search"; search.placeholder = "Search questions or answers";
  search.setAttribute("aria-label", "Search flashcards");
  var hideKnown = h("label", null, '<input type="checkbox"> hide cards I know');
  var shuffleBtn = h("button", "md-button", "🔀 Shuffle");
  var resetBtn = h("button", "md-button", "Reset known");
  resetBtn.setAttribute("aria-label", "Reset all marked-known flashcards");
  controls.appendChild(chapter); controls.appendChild(search); controls.appendChild(shuffleBtn); controls.appendChild(hideKnown); controls.appendChild(resetBtn);
  var card = h("div", "fc-card"); card.setAttribute("tabindex", "0"); card.setAttribute("role", "button");
  var meta = h("div", "fc-meta"); meta.setAttribute("aria-live", "polite");
  var nav = h("div", "fc-controls");
  var prev = h("button", "md-button", "← Prev"), flip = h("button", "md-button md-button--primary", "Flip"),
      gotIt = h("button", "md-button", "✓ I know this"), nxt = h("button", "md-button", "Next →");
  [prev, flip, gotIt, nxt].forEach(function (b) { nav.appendChild(b); });
  var wrap = h("div", "fc-wrap"); [controls, card, meta, nav].forEach(function (n) { wrap.appendChild(n); });
  app.innerHTML = ""; app.appendChild(wrap);

  function rebuild() {
    var ch = chapter.value, hk = hideKnown.querySelector("input").checked;
    var query = search.value.trim().toLocaleLowerCase();
    deck = all.filter(function (c) {
      var text = (c.question + " " + c.answer_html.replace(/<[^>]*>/g, " ") + " " + c.chapter).toLocaleLowerCase();
      return (ch === "all" || c.chapter === ch) && !(hk && known[c.id]) && (!query || text.indexOf(query) !== -1);
    });
    i = 0; render();
  }
  function render() {
    if (!deck.length) {
      card.setAttribute("aria-disabled", "true");
      card.innerHTML = '<div class="fc-text">No matching cards. Clear the search, choose another chapter, or adjust “hide cards I know”.</div>';
      meta.textContent = "0 matching cards"; return;
    }
    var c = deck[i];
    card.setAttribute("aria-disabled", "false");
    card.setAttribute("aria-pressed", String(flipped));
    card.setAttribute("aria-label", (flipped ? "Answer for: " : "Reveal answer for: ") + c.question);
    card.className = "fc-card" + (flipped ? " fc-back" : "");
    card.innerHTML = '<div class="fc-side">' + (flipped ? "Answer" : "Question") + " · " + c.chapter + '</div><div class="fc-text">' +
      (flipped ? c.answer_html : c.question) + "</div>";
    var nKnown = all.filter(function (x) { return known[x.id]; }).length;
    meta.innerHTML = "<span>Card " + (i + 1) + " / " + deck.length + "</span><span>" + nKnown + " / " + all.length + " marked known" +
      (known[c.id] ? " · ✓ this one" : "") + "</span>";
  }
  function go(d) { if (!deck.length) return; i = (i + d + deck.length) % deck.length; flipped = false; render(); }
  function doFlip() { if (!deck.length) return; flipped = !flipped; render(); }

  card.addEventListener("click", doFlip);
  card.addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); doFlip(); }
  });
  flip.addEventListener("click", doFlip);
  prev.addEventListener("click", function () { go(-1); });
  nxt.addEventListener("click", function () { go(1); });
  gotIt.addEventListener("click", function () {
    if (!deck.length) return; var id = deck[i].id; known[id] = !known[id]; saveKnown();
    if (hideKnown.querySelector("input").checked) rebuild(); else render();
  });
  resetBtn.addEventListener("click", function () {
    if (!Object.keys(known).some(function (id) { return known[id]; })) return;
    if (window.confirm("Reset all marked-known flashcards?")) {
      known = {}; saveKnown(); rebuild();
    }
  });
  shuffleBtn.addEventListener("click", function () {
    for (var k = deck.length - 1; k > 0; k--) { var j = Math.floor(Math.random() * (k + 1)); var t = deck[k]; deck[k] = deck[j]; deck[j] = t; }
    i = 0; flipped = false; render();
  });
  chapter.addEventListener("change", rebuild);
  search.addEventListener("input", rebuild);
  hideKnown.querySelector("input").addEventListener("change", rebuild);
  document.addEventListener("keydown", function (e) {
    if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT" || e.target.tagName === "TEXTAREA") return;
    if (e.key === "ArrowRight") go(1); else if (e.key === "ArrowLeft") go(-1);
    else if (e.key === " " && document.activeElement === card) { e.preventDefault(); doFlip(); }
  });

  fetch(app.getAttribute("data-src")).then(function (r) { return r.json(); }).then(function (cards) {
    all = cards;
    var chapters = ["all"].concat(Array.from(new Set(cards.map(function (c) { return c.chapter; }))));
    chapters.forEach(function (c) {
      var o = document.createElement("option"); o.value = c;
      o.textContent = c === "all" ? "All chapters (" + cards.length + " cards)" : c; chapter.appendChild(o);
    });
    rebuild();
  }).catch(function (err) { card.textContent = "Could not load cards: " + err.message; });
})();
