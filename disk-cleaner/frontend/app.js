const scanButton = document.getElementById("scan-btn");
const resultsBody = document.getElementById("results-body");
const totalSpace = document.getElementById("total-space");
const deleteButton = document.getElementById("delete-btn");
const deleteMode = document.getElementById("delete-mode");
const statusText = document.getElementById("status");
const providerText = document.getElementById("provider");
const chatHistory = document.getElementById("chat-history");
const chatMessage = document.getElementById("chat-message");
const chatSend = document.getElementById("chat-send");

let scanResults = [];

const formatBytes = (value) => {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = value;
  let index = 0;
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024;
    index += 1;
  }
  return `${size.toFixed(1)} ${units[index]}`;
};

const updateTotals = () => {
  const selected = scanResults.filter((item) => item.selected);
  const total = selected.reduce((sum, item) => sum + item.size_bytes, 0);
  totalSpace.textContent = `Space to free: ${formatBytes(total)}`;
};

const renderResults = () => {
  resultsBody.innerHTML = "";
  scanResults.forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "table-row";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = item.selected;
    checkbox.addEventListener("change", () => {
      item.selected = checkbox.checked;
      updateTotals();
    });

    const title = document.createElement("div");
    title.innerHTML = `<strong>${item.name}</strong><br/><small>${item.path}</small>`;

    const size = document.createElement("div");
    size.textContent = item.size_human;

    const safety = document.createElement("div");
    safety.innerHTML = `<span class="badge">${item.category_label}</span><br/><small>${item.safety_score}/100</small>`;

    const details = document.createElement("div");
    const extra = [item.explanation, item.age_summary, item.backup_dates]
      .filter(Boolean)
      .join(" ");
    details.innerHTML = `<small>${extra}</small>`;

    const ask = document.createElement("button");
    ask.className = "secondary";
    ask.textContent = "?";
    ask.addEventListener("click", () => {
      sendChat(`Tell me about ${item.name} at ${item.path}.`);
    });

    row.appendChild(checkbox);
    row.appendChild(title);
    row.appendChild(size);
    row.appendChild(safety);
    row.appendChild(details);
    row.appendChild(ask);

    resultsBody.appendChild(row);
  });
  updateTotals();
};

const scan = async () => {
  statusText.textContent = "Scanning...";
  const response = await fetch("/api/scan", { method: "POST" });
  const data = await response.json();
  scanResults = data.items.map((item) => ({ ...item, selected: false }));
  providerText.textContent = `Provider: ${data.provider}`;
  renderResults();
  statusText.textContent = `Found ${scanResults.length} items.`;
};

const deleteSelected = async () => {
  const targets = scanResults.filter((item) => item.selected).map((item) => item.path);
  if (!targets.length) {
    statusText.textContent = "Select at least one item.";
    return;
  }
  if (deleteMode.value === "permanent") {
    const confirmed = window.confirm("Permanently delete selected items? This cannot be undone.");
    if (!confirmed) {
      return;
    }
  }
  statusText.textContent = "Deleting...";
  await fetch("/api/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: deleteMode.value, paths: targets }),
  });
  statusText.textContent = "Delete completed.";
  scanResults = scanResults.filter((item) => !item.selected);
  renderResults();
};

const addChatMessage = (role, content) => {
  const bubble = document.createElement("div");
  bubble.className = `chat-message ${role}`;
  bubble.textContent = content;
  chatHistory.appendChild(bubble);
  chatHistory.scrollTop = chatHistory.scrollHeight;
};

const sendChat = async (message) => {
  if (!message.trim()) return;
  addChatMessage("user", message);
  chatMessage.value = "";
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages: [{ role: "user", content: message }],
      context: {
        items: scanResults.map((item) => ({
          name: item.name,
          path: item.path,
          size_human: item.size_human,
          safety_score: item.safety_score,
          category: item.category_label,
        })),
      },
    }),
  });
  const data = await response.json();
  addChatMessage("bot", data.response || "No response.");
};

scanButton.addEventListener("click", scan);
deleteButton.addEventListener("click", deleteSelected);
chatSend.addEventListener("click", () => sendChat(chatMessage.value));
