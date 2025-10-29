// Config
const API_ENDPOINT = "http://127.0.0.1:8000/predict";
const MIN_SELECTION_CHARS = 10;

// Inject enhanced tooltip styles once
(function ensureStyles() {
  if (document.getElementById("phish-detector-tooltip-style")) return;
  const style = document.createElement("style");
  style.id = "phish-detector-tooltip-style";
  style.textContent = `
    .phish-detector-tooltip {
      position: fixed;
      z-index: 2147483647;
      background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
      color: #ffffff;
      padding: 16px 20px;
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.1);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      font-size: 14px;
      line-height: 1.5;
      max-width: 320px;
      pointer-events: none;
      backdrop-filter: blur(10px);
      animation: phishDetectorSlideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      border: 1px solid rgba(255,255,255,0.15);
    }
    
    @keyframes phishDetectorSlideIn {
      from {
        opacity: 0;
        transform: translateY(-8px) scale(0.95);
      }
      to {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }
    
    .phish-detector-tooltip .header {
      display: flex;
      align-items: center;
      margin-bottom: 8px;
      font-weight: 600;
      font-size: 15px;
    }
    
    .phish-detector-tooltip .icon {
      width: 20px;
      height: 20px;
      margin-right: 8px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: bold;
    }
    
    .phish-detector-tooltip .content {
      margin-bottom: 8px;
    }
    
    .phish-detector-tooltip .probability {
      font-size: 13px;
      opacity: 0.9;
      font-weight: 500;
    }
    
    .phish-detector-tooltip .progress-bar {
      width: 100%;
      height: 4px;
      background: rgba(255,255,255,0.2);
      border-radius: 2px;
      margin-top: 8px;
      overflow: hidden;
    }
    
    .phish-detector-tooltip .progress-fill {
      height: 100%;
      border-radius: 2px;
      transition: width 0.6s ease-out;
    }
    
    .phish-detector-tooltip .footer {
      margin-top: 8px;
      font-size: 12px;
      opacity: 0.7;
      font-style: italic;
    }
    
    /* Phishing variant */
    .phish-detector-tooltip.phishing {
      background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
      border-color: rgba(255,255,255,0.2);
    }
    
    .phish-detector-tooltip.phishing .icon {
      background: rgba(255,255,255,0.2);
      color: #ffffff;
    }
    
    .phish-detector-tooltip.phishing .progress-fill {
      background: linear-gradient(90deg, #fca5a5 0%, #ffffff 100%);
    }
    
    /* Safe variant */
    .phish-detector-tooltip.safe {
      background: linear-gradient(135deg, #059669 0%, #047857 100%);
      border-color: rgba(255,255,255,0.2);
    }
    
    .phish-detector-tooltip.safe .icon {
      background: rgba(255,255,255,0.2);
      color: #ffffff;
    }
    
    .phish-detector-tooltip.safe .progress-fill {
      background: linear-gradient(90deg, #86efac 0%, #ffffff 100%);
    }
    
    /* Warning variant */
    .phish-detector-tooltip.warning {
      background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
      border-color: rgba(255,255,255,0.2);
    }
    
    .phish-detector-tooltip.warning .icon {
      background: rgba(255,255,255,0.2);
      color: #ffffff;
    }
    
    .phish-detector-tooltip.warning .progress-fill {
      background: linear-gradient(90deg, #fde68a 0%, #ffffff 100%);
    }
    
    /* Error variant */
    .phish-detector-tooltip.error {
      background: linear-gradient(135deg, #7c2d12 0%, #991b1b 100%);
      border-color: rgba(255,255,255,0.2);
    }
    
    .phish-detector-tooltip.error .icon {
      background: rgba(255,255,255,0.2);
      color: #ffffff;
    }
  `;
  document.documentElement.appendChild(style);
})();

let tooltipEl;
function removeTooltip() {
  if (tooltipEl && tooltipEl.parentNode) {
    tooltipEl.style.animation = "phishDetectorSlideOut 0.2s ease-in forwards";
    setTimeout(() => {
      if (tooltipEl && tooltipEl.parentNode) {
        tooltipEl.parentNode.removeChild(tooltipEl);
      }
      tooltipEl = null;
    }, 200);
  }
}

// Add slide out animation
(function addSlideOutAnimation() {
  if (document.getElementById("phish-detector-slideout-style")) return;
  const style = document.createElement("style");
  style.id = "phish-detector-slideout-style";
  style.textContent = `
    @keyframes phishDetectorSlideOut {
      from {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
      to {
        opacity: 0;
        transform: translateY(-8px) scale(0.95);
      }
    }
  `;
  document.documentElement.appendChild(style);
})();

function showTooltipAt(x, y, state) {
  removeTooltip();
  tooltipEl = document.createElement("div");
  tooltipEl.className = `phish-detector-tooltip ${state.variant}`;
  
  const probability = Math.round(state.probability * 100);
  const progressWidth = `${probability}%`;
  
  tooltipEl.innerHTML = `
    <div class="header">
      <div class="icon">${state.icon}</div>
      <div>${state.title}</div>
    </div>
    <div class="content">${state.message}</div>
    <div class="probability">Confidence: ${probability}%</div>
    <div class="progress-bar">
      <div class="progress-fill" style="width: ${progressWidth}"></div>
    </div>
    <div class="footer">${state.footer}</div>
  `;
  
  document.documentElement.appendChild(tooltipEl);

  // Position within viewport bounds
  const padding = 16;
  const rect = tooltipEl.getBoundingClientRect();
  let left = x + 16;
  let top = y + 16;
  
  if (left + rect.width + padding > window.innerWidth) {
    left = x - rect.width - 16;
  }
  if (top + rect.height + padding > window.innerHeight) {
    top = y - rect.height - 16;
  }
  
  tooltipEl.style.left = `${Math.max(8, left)}px`;
  tooltipEl.style.top = `${Math.max(8, top)}px`;

  // Auto-hide after delay
  setTimeout(removeTooltip, state.duration || 5000);
}

// Get selected text and selection bounding box
function getSelectionInfo() {
  const sel = window.getSelection();
  if (!sel || sel.isCollapsed) return { text: "", rect: null };
  const text = String(sel.toString()).trim();
  if (!text) return { text: "", rect: null };
  let range;
  try {
    range = sel.getRangeAt(0).cloneRange();
  } catch {
    return { text: "", rect: null };
  }
  const rect = range.getBoundingClientRect();
  return { text, rect };
}

// Debounce helper
let debounceTimer;
function debounce(fn, wait = 350) {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(fn, wait);
}

// Send to API and show enhanced tooltip
async function analyzeSelectionAtPoint(clientX, clientY, text) {
  try {
    const resp = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    const label = Number(data.label) === 1 ? 1 : 0;
    const prob = typeof data.phishing_probability === "number" ? data.phishing_probability : 0;

    let state;
    if (label === 1) {
      state = {
        variant: "phishing",
        icon: "⚠",
        title: "Phishing Detected",
        message: "This content appears to be malicious or suspicious.",
        probability: prob,
        footer: "Do not click links or provide personal information.",
        duration: 6000
      };
    } else {
      state = {
        variant: "safe",
        icon: "✓",
        title: "Content Appears Safe",
        message: "No phishing indicators detected in this text.",
        probability: 1 - prob,
        footer: "Always verify suspicious requests independently.",
        duration: 4000
      };
    }
    
    showTooltipAt(clientX, clientY, state);
  } catch (e) {
    const state = {
      variant: "error",
      icon: "!",
      title: "Analysis Failed",
      message: "Unable to analyze this content.",
      probability: 0,
      footer: "Check your connection and try again.",
      duration: 3000
    };
    showTooltipAt(clientX, clientY, state);
  }
}

// Listen for text selection mouseup
document.addEventListener("mouseup", (ev) => {
  debounce(() => {
    const { text, rect } = getSelectionInfo();
    if (!text || text.length < MIN_SELECTION_CHARS) return;
    const x = rect ? rect.left + rect.width / 2 : ev.clientX;
    const y = rect ? rect.top : ev.clientY;
    analyzeSelectionAtPoint(x, y, text);
  }, 250);
});

// Clean up tooltip on scroll, escape, or click
document.addEventListener("scroll", removeTooltip, { passive: true, capture: true });
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") removeTooltip();
});
document.addEventListener("click", (e) => {
  if (tooltipEl && !tooltipEl.contains(e.target)) {
    removeTooltip();
  }
});
