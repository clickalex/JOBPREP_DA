// Lightweight DOM smoke test for the browser flashcard controls (no jsdom/npm dependency).
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

class Element {
  constructor(tag) {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.attributes = {};
    this.listeners = {};
    this.value = "";
    this.className = "";
    this._html = "";
    this._text = "";
  }
  set innerHTML(value) {
    this._html = String(value);
    this._text = this._html.replace(/<[^>]*>/g, " ");
    if (this.tagName === "DIV" && value === "") this.children = [];
    if (this.tagName === "LABEL" && this._html.includes('type="checkbox"')) {
      this.checkbox = new Element("input");
      this.checkbox.type = "checkbox";
      this.checkbox.checked = false;
    }
  }
  get innerHTML() { return this._html; }
  set textContent(value) { this._text = String(value); this._html = this._text; }
  get textContent() { return this._text; }
  appendChild(child) {
    this.children.push(child);
    if (this.tagName === "SELECT" && this.children.length === 1) this.value = child.value;
    return child;
  }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  getAttribute(name) { return this.attributes[name] || null; }
  addEventListener(name, fn) { (this.listeners[name] ||= []).push(fn); }
  dispatch(name, event = {}) {
    event.target ||= this;
    event.preventDefault ||= function () {};
    (this.listeners[name] || []).forEach((fn) => fn(event));
  }
  querySelector(selector) { return selector === "input" ? this.checkbox : null; }
  click() { this.dispatch("click"); }
}

class Document {
  constructor() {
    this.app = new Element("div");
    this.app.setAttribute("data-src", "flashcards.json");
    this.activeElement = null;
    this.listeners = {};
  }
  getElementById(id) { return id === "fc-app" ? this.app : null; }
  createElement(tag) { return new Element(tag); }
  addEventListener(name, fn) { (this.listeners[name] ||= []).push(fn); }
  dispatch(name, event = {}) { (this.listeners[name] || []).forEach((fn) => fn(event)); }
}

async function main() {
  const document = new Document();
  const storage = new Map();
  const cards = [
    { id: "sql-1", chapter: "SQL", question: "What is a window function?", answer_html: "<p>It computes across related rows.</p>" },
    { id: "interview-1", chapter: "Interview Q&A", question: "How do you handle a missed deadline?", answer_html: "<p>Communicate early and agree a revised scope.</p>" },
    ...Array.from({ length: 28 }, (_, i) => ({ id: "sql-extra-" + i, chapter: "SQL", question: "Practice item " + i, answer_html: "<p>Example response " + i + "</p>" })),
  ];
  const localStorage = {
    getItem: (key) => storage.get(key) || null,
    setItem: (key, value) => storage.set(key, value),
  };
  let confirmAnswer = false;
  const window = { confirm: (message) => { assert.equal(message, "Reset all marked-known flashcards?"); return confirmAnswer; } };
  const fetch = async () => ({ json: async () => cards });
  const source = fs.readFileSync("website/assets/flashcards/flashcards.js", "utf8");
  vm.runInNewContext(source, { document, localStorage, window, fetch, Array, JSON, Math, String });
  await new Promise((resolve) => setImmediate(resolve));

  const [wrap] = document.app.children;
  const [controls, card, answerArea, meta, nav] = wrap.children;
  const [chapter, sessionSize, search, shuffle, hideKnown, typeFirst, reset] = controls.children;
  const [answerInput, answerStatus] = answerArea.children;
  const [prev, flip, know, next] = nav.children;
  assert.match(meta.innerHTML, /Card 1 \/ 30/);
  assert.equal(chapter.value, "all");
  assert.equal(sessionSize.value, "all");
  sessionSize.value = "10";
  sessionSize.dispatch("change");
  assert.match(meta.innerHTML, /Card 1 \/ 10/);

  search.value = "missed deadline";
  search.dispatch("input");
  assert.match(meta.innerHTML, /Card 1 \/ 1/);
  assert.match(card.innerHTML, /How do you handle a missed deadline/);

  search.value = "not a real question";
  search.dispatch("input");
  assert.equal(meta.textContent, "0 matching cards");
  assert.equal(card.getAttribute("aria-disabled"), "true");

  search.value = "";
  search.dispatch("input");
  chapter.value = "Interview Q&A";
  chapter.dispatch("change");
  card.dispatch("keydown", { key: "Enter" });
  assert.equal(card.getAttribute("aria-pressed"), "true");
  assert.match(card.innerHTML, /Communicate early/);
  card.dispatch("keydown", { key: "Enter" });
  assert.equal(card.getAttribute("aria-pressed"), "false");

  know.click();
  assert.match(meta.innerHTML, /1 \/ 30 marked known/);
  chapter.value = "all";
  chapter.dispatch("change");
  search.value = "computes across"; // search also matches answer text
  search.dispatch("input");
  hideKnown.checkbox.checked = true;
  hideKnown.checkbox.dispatch("change");
  assert.match(meta.innerHTML, /Card 1 \/ 1/);
  assert.match(card.innerHTML, /What is a window function/);

  reset.click(); // confirmation is cancelled; progress remains
  assert.match(meta.innerHTML, /1 \/ 30 marked known/);
  confirmAnswer = true;
  reset.click();
  assert.equal(storage.get("jobprep-flashcards-v1"), "{}");
  assert.match(meta.innerHTML, /Card 1 \/ 1/);
  assert.match(meta.innerHTML, /0 \/ 30 marked known/);

  typeFirst.checkbox.checked = true;
  typeFirst.checkbox.dispatch("change");
  assert.equal(answerArea.hidden, false);
  assert.equal(flip.textContent, "Reveal answer");
  flip.click();
  assert.equal(card.getAttribute("aria-pressed"), "false");
  assert.match(answerStatus.textContent, /Try typing a short answer first/);
  answerInput.value = "Explain the idea in my own words";
  answerInput.dispatch("input");
  flip.click();
  assert.equal(card.getAttribute("aria-pressed"), "true");
  assert.equal(answerArea.hidden, true);
  assert.match(card.innerHTML, /It computes across related rows/);

  // Keep references alive so lint-like checks catch accidentally disconnected controls.
  assert.ok(prev && next && flip && shuffle && reset && sessionSize);
  console.log("flashcards: search, sessions, active recall, empty state, keyboard flip, hide-known, and reset passed");
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
