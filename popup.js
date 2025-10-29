const API_ENDPOINT = "http://127.0.0.1:8000/predict";
const statusEl = document.getElementById("status");
const btn = document.getElementById("analyze");

async function getSelectionInPage(tabId) {
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      const text = String(window.getSelection()?.toString() || "").trim();
      return text;
    }
  });
  return result || "";
}

async function analyzeText(text) {
  const resp = await fetch(API_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

btn.addEventListener("click", async () => {
  btn.disabled = true;
  statusEl.className = "result muted";
  statusEl.textContent = "Analyzing...";

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) throw new Error("No active tab");
    const selectedText = await getSelectionInPage(tab.id);
    if (!selectedText || selectedText.length < 10) {
      statusEl.className = "result muted";
      statusEl.textContent = "Select at least 10 characters on the page.";
      btn.disabled = false;
      return;
    }

    const data = await analyzeText(selectedText);
    const label = Number(data.label) === 1 ? 1 : 0;
    const prob = typeof data.phishing_probability === "number" ? data.phishing_probability : 0;

    if (label === 1) {
      statusEl.className = "result warn";
      statusEl.textContent = `Phishing detected! Probability: ${(prob * 100).toFixed(1)}%`;
    } else {
      statusEl.className = "result ok";
      statusEl.textContent = `Likely safe. Probability: ${(prob * 100).toFixed(1)}%`;
    }
  } catch (e) {
    statusEl.className = "result warn";
    statusEl.textContent = "Could not analyze (network/API error).";
  } finally {
    btn.disabled = false;
  }
});
