async function send() {
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