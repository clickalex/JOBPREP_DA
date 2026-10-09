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
  var sessionSize = h("select"); sessionSize.setAttribute("aria-label", "Session size");
  [["all", "All matching cards"], ["10", "10-card session"], ["25", "25-card session"]].forEach(function (item) {
    var option = h("option", null, item[1]); option.value = item[0]; sessionSize.appendChild(option);
  });
  var search = h("input"); search.type = "search"; search.placeholder = "Search questions or answers";
  search.setAttribute("aria-label", "Search flashcards");
  var hideKnown = h("label", null, '<input type="checkbox"> hide cards I know');
  var typeFirst = h("label", null, '<input type="checkbox"> type answer first');
  var shuffleBtn = h("button", "md-button", "🔀 Shuffle");
  var resetBtn = h("button", "md-button", "Reset known");
  resetBtn.setAttribute("aria-label", "Reset all marked-known flashcards");
  controls.appendChild(chapter); controls.appendChild(sessionSize); controls.appendChild(search);
  controls.appendChild(shuffleBtn); controls.appendChild(hideKnown); controls.appendChild(typeFirst); controls.appendChild(resetBtn);
  var card = h("div", "fc-card"); card.setAttribute("tabindex", "0"); card.setAttribute("role", "button");
  var answerArea = h("div", "fc-recall"); answerArea.hidden = true;
  var answerInput = h("textarea", "fc-recall-input"); answerInput.rows = 3;
  answerInput.placeholder = "Type a short answer before revealing the model answer…";
  answerInput.setAttribute("aria-label", "Your answer before revealing the model answer");
  var answerStatus = h("div", "fc-recall-status"); answerStatus.setAttribute("role", "status"); answerStatus.setAttribute("aria-live", "polite");
  answerArea.appendChild(answerInput); answerArea.appendChild(answerStatus);
  var meta = h("div", "fc-meta"); meta.setAttribute("aria-live", "polite");
  var nav = h("div", "fc-controls");
  var prev = h("button", "md-button", "← Prev"), flip = h("button", "md-button md-button--primary", "Flip"),
      gotIt = h("button", "md-button", "✓ I know this"), nxt = h("button", "md-button", "Next →");
  [prev, flip, gotIt, nxt].forEach(function (b) { nav.appendChild(b); });
  var wrap = h("div", "fc-wrap"); [controls, card, answerArea, meta, nav].forEach(function (n) { wrap.appendChild(n); });
  app.innerHTML = ""; app.appendChild(wrap);

  function rebuild() {
    var ch = chapter.value, hk = hideKnown.querySelector("input").checked;
    var query = search.value.trim().toLocaleLowerCase();
    deck = all.filter(function (c) {
      var text = (c.question + " " + c.answer_html.replace(/<[^>]*>/g, " ") + " " + c.chapter).toLocaleLowerCase();
      return (ch === "all" || c.chapter === ch) && !(hk && known[c.id]) && (!query || text.indexOf(query) !== -1);
    });
    for (var k = deck.length - 1; k > 0; k--) {
      var j = Math.floor(Math.random() * (k + 1)), t = deck[k]; deck[k] = deck[j]; deck[j] = t;
    }
    var limit = parseInt(sessionSize.value, 10);
    if (limit > 0 && deck.length > limit) deck = deck.slice(0, limit);
    i = 0; flipped = false; answerInput.value = ""; answerStatus.textContent = ""; render();
  }
  function render() {
    if (!deck.length) {
      card.setAttribute("aria-disabled", "true"); answerArea.hidden = true;
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
    answerArea.hidden = !(typeFirst.querySelector("input").checked && !flipped);
    flip.textContent = flipped ? "Show question" : (typeFirst.querySelector("input").checked ? "Reveal answer" : "Flip");
    var nKnown = all.filter(function (x) { return known[x.id]; }).length;
    meta.innerHTML = "<span>Card " + (i + 1) + " / " + deck.length + "</span><span>" + nKnown + " / " + all.length + " marked known" +
      (known[c.id] ? " · ✓ this one" : "") + "</span>";
  }
  function go(d) {
    if (!deck.length) return;
    i = (i + d + deck.length) % deck.length; flipped = false;
    answerInput.value = ""; answerStatus.textContent = ""; render();
  }
  function doFlip() {
    if (!deck.length) return;
    if (!flipped && typeFirst.querySelector("input").checked && !answerInput.value.trim()) {
      answerStatus.textContent = "Try typing a short answer first, then reveal the model answer.";
      return;
    }
    answerStatus.textContent = ""; flipped = !flipped; render();
  }

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
  shuffleBtn.addEventListener("click", rebuild); // deal a fresh randomized sample for the current filters
  chapter.addEventListener("change", rebuild);
  sessionSize.addEventListener("change", rebuild);
  search.addEventListener("input", rebuild);
  hideKnown.querySelector("input").addEventListener("change", rebuild);
  typeFirst.querySelector("input").addEventListener("change", function () {
    answerInput.value = ""; answerStatus.textContent = ""; render();
  });
  answerInput.addEventListener("input", function () { answerStatus.textContent = ""; });
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
