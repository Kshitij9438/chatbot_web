const inputEl = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const messagesEl = document.getElementById("messages");

function appendMessage(text, cls) {
  const div = document.createElement("div");
  div.className = `msg ${cls}`;
  div.innerText = text;

  // timestamp
  const ts = document.createElement("span");
  ts.className = "timestamp";
  ts.innerText = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit"
  });
  div.appendChild(ts);

  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

sendBtn.addEventListener("click", async () => {
  const msg = inputEl.value.trim();
  if (!msg) return;
  appendMessage(msg, "user-msg");
  inputEl.value = "";

  try {
    const res = await fetch("/chatbot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: msg })
    });
    const data = await res.json();
    if (data.reply) {
      appendMessage(data.reply, "bot-msg");
    } else {
      appendMessage("Error: " + (data.error || "Unknown"), "bot-msg");
    }
  } catch (err) {
    appendMessage("Network error", "bot-msg");
  }
});

// allow Enter to send
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendBtn.click();
});
