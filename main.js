(() => {
  "use strict";

  const KEY = "zetari_state_v1";
  const LOG = "aion_state_log";
  const PHI = 1.618033988749895;

  const $ = id => document.getElementById(id);
  const now = () => Date.now();

  const defaults = () => ({
    env: 0.2,
    emo: 0.2,
    ment: 0.2,
    phys: 0.2,
    res: 0.2,
    task_type: "general",
    session: null
  });

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
    const branches = {
      base,
      phiMultiply: base * PHI,
      phiDivide: base / PHI
    };
    const label = base >= 1 ? "Hyper-Resonant" : "Entropic";
    return { ...state, agency, mer: base, branches, label };
  }

  function advice(d) {
    if (d.mer < 0.7) return "Take a 10–15 minute break and reduce cognitive load.";
    if (d.mer < 1) return "Use light work or planning tasks.";
    if (d.mer <= 1.3) return "Use focused deep work.";
    return "Use high-intensity deep work, but monitor resistance and plan a micro-break soon.";
  }

  function render() {
    const d = calc();

    $("state").innerHTML = [
      `<div class=card><small>Virtual state vector</small><b>(${d.env.toFixed(3)}, ${d.emo.toFixed(3)}, ${d.ment.toFixed(3)}, ${d.phys.toFixed(3)})</b></div>`,
      `<div class=card><small>Resistance</small><b>${d.res.toFixed(3)}</b></div>`,
      `<div class=card><small>MER base</small><b>${d.branches.base.toFixed(4)}</b></div>`,
      `<div class=card><small>MER × φ</small><b>${d.branches.phiMultiply.toFixed(4)}</b></div>`,
      `<div class=card><small>MER ÷ φ</small><b>${d.branches.phiDivide.toFixed(4)}</b></div>`
    ].join("");

    $("status").innerHTML =
      `Agency: <b>${d.agency.toFixed(4)}</b><br>` +
      `State: <b>${d.label}</b><br><br>` +
      `Navigator recommendation:<br>${advice(d)}`;

    const recent = getLog().slice(-8).reverse();
    $("timeline").innerHTML =
      `<b>Recent timeline</b><br>${
        recent.length
          ? recent.map(x =>
              `${new Date(x.timestamp).toLocaleTimeString()} — MER ${x.mer.toFixed(2)} — ${x.label}`
            ).join("<br>")
          : "No history yet."
      }`;
  }

  function add(text, who) {
    const e = document.createElement("div");
    e.className = `msg ${who}`;
    e.textContent = text;
    $("messages").appendChild(e);
    $("messages").scrollTop = $("messages").scrollHeight;
  }

  function interpret(text) {
    const t = text.toLowerCase();

    const hit = arr => arr.some(x => t.includes(x));

    const pos = {
      env: ["quiet", "comfortable", "safe"],
      emo: ["calm", "happy", "confident", "motivated", "good mood"],
      ment: ["focused", "clear", "creative", "ready"],
      phys: ["rested", "energetic", "strong", "awake"]
    };

    const neg = {
      env: ["noisy", "crowded", "chaotic", "uncomfortable"],
      emo: ["sad", "angry", "mad", "anxious", "worried", "stressed", "upset", "frustrated"],
      ment: ["confused", "distracted", "brain fog", "can't focus", "cannot focus", "blocked"],
      phys: ["tired", "exhausted", "sleepy", "sick", "pain", "weak"]
    };

    for (const k of Object.keys(pos)) {
      if (hit(pos[k])) state[k] += 0.08;
      if (hit(neg[k])) state[k] -= 0.08;
    }

    if (hit(["break", "rest", "pause"])) state.res -= 0.08;
    if (hit(["deadline", "pressure", "hard", "struggle"])) state.res += 0.08;

    for (const k of ["env", "emo", "ment", "phys"]) {
      state[k] = Math.max(0, Math.min(1, state[k]));
    }

    state.res = Math.max(0.01, Math.min(1, state.res));

    const tags = ["coding", "study", "writing", "physics", "weather", "planning"];
    state.task_type = tags.find(x => t.includes(x)) || state.task_type;

    log();
    render();
  }

  function sessionStart(minutes) {
    state.session = {
      start: now(),
      planned: minutes || null,
      task_type: state.task_type
    };
    saveState();
    render();

    if (minutes) {
      return `Work block planned for ${minutes} minutes. End time: ${new Date(now() + minutes * 60000).toLocaleTimeString()}.`;
    }
    return `Session started at ${new Date().toLocaleTimeString()}.`;
  }

  function summary() {
    const d = calc();
    const a = getLog().filter(x => state.session && x.timestamp >= state.session.start);
    const avg = a.length ? a.reduce((s, x) => s + x.mer, 0) / a.length : d.mer;

    return `Session summary
Task: ${state.task_type}
Samples: ${a.length}
Average MER: ${avg.toFixed(4)}
Current state: ${d.label}
Recommendation: ${advice(d)}`;
  }

  function command(raw) {
    const t = raw.toLowerCase().trim();
    const m = t.match(/plan block\s+(\d+)\s*minutes?/);

    if (m) return sessionStart(Number(m[1]));
    if (t.includes("start session")) return sessionStart();

    if (t.includes("end session")) {
      const r = summary();
      state.session = null;
      saveState();
      render();
      return r + "\nSession ended.";
    }

    if (t.includes("summary")) return summary();
    if (t.includes("save")) return saveState();

    if (t.includes("reset")) {
      state = defaults();
      localStorage.removeItem(LOG);
      saveState();
      render();
      return "State and history reset.";
    }

    if (t.includes("help")) {
      return "Commands: status report, start session, plan block N minutes, summary, end session, save state, reset state.";
    }

    if (t.includes("status")) {
      render();
      return summary();
    }

    interpret(raw);
    return `Message interpreted for ${state.task_type}.\n${summary()}`;
  }

 async function send() {
  alert("send() fired");
  const i = $("input");
  const t = i.value.trim();
  if (!t) return;
    add(t, "user");
    i.value = "";

    const lower = t.toLowerCase().trim();
    const localOnly =
      lower.includes("start session") ||
      lower.includes("end session") ||
      lower.includes("summary") ||
      lower.includes("save") ||
      lower.includes("reset") ||
      lower.includes("status") ||
      lower.includes("plan block") ||
      lower.includes("help");

    if (localOnly) {
      const r = command(t);
      add(r, "bot");
      return;
    }

    interpret(t);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt: t })
      });

      const data = await response.json();
      add(data.response || "No response returned.", "bot");
    } catch (err) {
      add("Backend connection failed: " + err.message, "bot");
    }
  }

  async function loadProjectRegistry() {
    try {
      const response = await fetch("project.json");
      if (!response.ok) {
        throw new Error(`Registry request failed: ${response.status}`);
      }

      projectRegistry = await response.json();
      console.log("UQTN project registry loaded:", projectRegistry);
    } catch (error) {
      console.warn("Project registry unavailable:", error);
    }
  }

  $("send").onclick = send;

  $("input").onkeydown = e => {
    if (e.key === "Enter") send();
  };

  document.querySelectorAll("[data-cmd]").forEach(b => {
    b.onclick = () => {
      add(b.dataset.cmd, "user");
      add(command(b.dataset.cmd), "bot");
    };
  });

  $("speak").onclick = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SR) {
      add("Voice input is unavailable in this browser.", "bot");
      return;
    }

    if (!recognition) {
      recognition = new SR();
      recognition.lang = "en-US";

      recognition.onresult = async e => {
        const t = e.results[0][0].transcript;
        $("input").value = t;
        await send();
      };

      recognition.onend = () => {
        listening = false;
        $("speak").textContent = "🎤 Speak";
      };
    }

    if (listening) {
      recognition.stop();
    } else {
      listening = true;
      $("speak").textContent = "🎙️ Listening...";
      recognition.start();
    }
  };

  render();
  add("Navigator ready. Describe how you feel or what you are working on to start a session.", "bot");
  loadProjectRegistry();

  // if ("serviceWorker" in navigator) {
//   navigator.serviceWorker.register("sw.js").catch(console.warn);
// }
})();