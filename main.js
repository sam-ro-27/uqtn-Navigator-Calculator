(() => {
  "use strict";
  const KEY = "krimoxous_state_v1";
  const LOG = "krimoxous_state_history_v1";
  const PHI = 1.618033988749895;
  const $ = id => document.getElementById(id);
  const now = () => Date.now();
  const defaults = () => ({ env: 0.2, emo: 0.2, ment: 0.2, phys: 0.2, res: 0.2, task_type: "general", session: null });
  let state = loadState();
  let recognition = null;
  let listening = false;
  let projectRegistry = null;

  function saveState() {
    localStorage.setItem(KEY, JSON.stringify(state));
    return "State saved locally.";
  }

  function loadState() {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || defaults();
    } catch {
      return defaults();
    }
  }

  function getLog() {
    try {
      return JSON.parse(localStorage.getItem(LOG)) || [];
    } catch {
      return [];
    }
  }

  function log() {
    const d = calc();
    const a = getLog();
    a.push({ timestamp: now(), ...d });
    localStorage.setItem(LOG, JSON.stringify(a.slice(-1000)));
  }

  function calc() {
    const agency = state.env + state.emo + state.ment + state.phys;
    const base = agency / Math.max(state.res, 0.01);
    const branches = { base, phiMultiply: base * PHI, phiDivide: base / PHI };
    const label = base >= 1 ? "Hyper-Resonant" : "Entropic";
    return { ...state, agency, mer: base, branches, label };
  }

  function advice(d) {
    if (d.mer < 0.7) return "Take a 10-15 minute break and reduce cognitive load.";
    if (d.mer < 1) return "Use light work or planning tasks.";
    if (d.mer <= 1.3) return "Use focused deep work.";
    return "Use high-intensity deep work, but monitor resistance and plan a micro-break soon.";
  }

  // NOTE: this file is a legacy standalone script. Confirm index.html does
  // not also load this via <script src> alongside its own inline script,
  // since running both would create two independent state engines writing
  // to the same-shaped but separately-keyed localStorage data.
})();