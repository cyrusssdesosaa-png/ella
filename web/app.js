/* ============================================================
   E.L.L.A. — FRIDAY-style assistant UI
   All existing /api/* endpoints preserved.
   ============================================================ */

/* ---- Constants ---- */
const COLORS = {
  Router: "#22c58b", Wiki: "#e8e8e8", Concepts: "#e7b928",
  Suites: "#8e63d9", Skills: "#4a7fe0", Tools: "#e0559a",
  Worlds: "#f5a524", Notes: "#2fbf8f", Files: "#8b8f98",
};
const GREETINGS = [
  "Morning, Cyrus. What are we doing?",
  "Hey Cyrus. Ready when you are.",
  "Good to see you. What's the plan?",
  "Afternoon, Cyrus. Need anything?",
  "Evening, Cyrus. What's on your mind?",
];

/* ---- State ---- */
let brain = { mode: "local", model: "qwen2.5:7b" };
let conversationMode = false;
let currentView = "home";
let chatHistory = [];
let rec = null;
let currentAudio = null;
let ttsAnalyser = null;
let ttsDataArray = null;
let ambientEnabled = true;
let reducedMotion = false;

/* ---- Graph state ---- */
let nodes = [];
let links = [];
let focus = -1;
let hidden = new Set();
let tick = 0;

/* ---- DOM refs ---- */
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);
const API_TOKEN = document.querySelector('meta[name="ella-request-token"]')?.content || "";

const orbCanvas = $("#orb");
const octx = orbCanvas.getContext("2d");
const ambientCanvas = $("#ambientGraph");
const actx = ambientCanvas.getContext("2d");
const brainCanvas = $("#brainGraph");
const bctx = brainCanvas.getContext("2d");
const chatMessages = $("#chatMessages");
const chatInput = $("#chatInput");
const liveCaption = $("#liveCaption");
const stateLabel = $("#stateLabel");
const brainLabel = $("#brainLabel");
const clockEl = $("#clock");
const toastEl = $("#toast");

/* ============================================================
   API helpers (unchanged)
   ============================================================ */
async function api(path, options) {
  if (!API_TOKEN || API_TOKEN === "__ELLA_REQUEST_TOKEN__") {
    throw new Error("Ella authorization is unavailable. Reload the panel from the local server.");
  }
  const headers = new Headers((options && options.headers) || {});
  headers.set("X-Ella-Request-Token", API_TOKEN);
  const res = await fetch(path, { ...(options || {}), headers });
  let data = {};
  try { data = await res.json(); } catch (_) {}
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}
function post(path, body) {
  return api(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
}

/* ============================================================
   Clock
   ============================================================ */
function updateClock() {
  const now = new Date();
  const h = now.getHours();
  const m = String(now.getMinutes()).padStart(2, "0");
  const ampm = h >= 12 ? "PM" : "AM";
  const h12 = h % 12 || 12;
  clockEl.textContent = `${h12}:${m} ${ampm}`;
}
updateClock();
setInterval(updateClock, 30000);

/* ============================================================
   View switching
   ============================================================ */
function switchView(name) {
  currentView = name;
  $$(".view").forEach((v) => v.classList.remove("active"));
  const view = $(`#${name}View`);
  if (view) view.classList.add("active");
  $$(".rail-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.view === name);
  });
  if (name === "brain") requestAnimationFrame(() => resizeBrainCanvas());
}
$$(".rail-btn").forEach((btn) => {
  btn.addEventListener("click", () => switchView(btn.dataset.view));
});
$("#gearBtn").addEventListener("click", () => switchView("settings"));

/* ============================================================
   Chat panel toggle
   ============================================================ */
let chatCollapsed = false;
$("#chatToggle").addEventListener("click", () => {
  chatCollapsed = !chatCollapsed;
  $("#chatPanel").classList.toggle("collapsed", chatCollapsed);
  $("#chatToggle").textContent = chatCollapsed ? "▶" : "◀";
});

/* ============================================================
   Chat messages
   ============================================================ */
function addMessage(role, text, tag, tokens) {
  const time = new Date().toLocaleTimeString("en-PH", { hour: "2-digit", minute: "2-digit", hour12: true });
  chatHistory.push({ role, text, time, tag });

  const div = document.createElement("div");
  div.className = role === "user" ? "msg msg-user" : "msg msg-ella";

  const body = document.createElement("div");
  body.className = "msg-body";
  body.textContent = text;
  div.appendChild(body);

  const meta = document.createElement("div");
  meta.className = "msg-meta";
  const timeEl = document.createElement("span");
  timeEl.textContent = time;
  meta.appendChild(timeEl);
  if (tag) {
    const tagEl = document.createElement("span");
    tagEl.className = "msg-tag";
    tagEl.textContent = tag;
    meta.appendChild(tagEl);
  }
  if (tokens) {
    const tokenEl = document.createElement("span");
    tokenEl.className = "msg-tag";
    tokenEl.textContent = `${fmtTok(tokens)} tok`;
    meta.appendChild(tokenEl);
  }
  const copyBtn = document.createElement("button");
  copyBtn.className = "msg-copy";
  copyBtn.textContent = "Copy";
  copyBtn.onclick = () => {
    navigator.clipboard.writeText(text).then(() => { copyBtn.textContent = "Copied!"; setTimeout(() => copyBtn.textContent = "Copy", 1500); });
  };
  meta.appendChild(copyBtn);
  div.appendChild(meta);

  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  if (role === "ella") showQuickChips();
}

function showQuickChips() {
  const chips = ["Good morning", "What time is it?", "Check in", "Backup"];
  $("#quickChips").innerHTML = chips.map((c) =>
    `<button class="chip" type="button">${c}</button>`
  ).join("");
  $$("#quickChips .chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      chatInput.value = btn.textContent;
      $("#inputForm").requestSubmit();
    });
  });
}

/* ============================================================
   Live caption — word-by-word typing
   ============================================================ */
let captionTimer = null;
function typeCaption(text) {
  if (captionTimer) clearInterval(captionTimer);
  liveCaption.textContent = "";
  const words = text.split(" ");
  let i = 0;
  captionTimer = setInterval(() => {
    if (i >= words.length) { clearInterval(captionTimer); captionTimer = null; return; }
    liveCaption.textContent += (i > 0 ? " " : "") + words[i];
    i++;
  }, 60);
}

/* ============================================================
   Toast
   ============================================================ */
function showToast(msg, duration) {
  toastEl.textContent = msg;
  toastEl.classList.remove("hidden");
  setTimeout(() => toastEl.classList.add("hidden"), duration || 4000);
}

/* ============================================================
   Mode / status
   ============================================================ */
let mode = "online";
function setStatus(next) {
  mode = next;
  document.body.dataset.mode = next;
  const labels = { online: "Online", thinking: "Thinking", listening: "Listening", transcribing: "Transcribing", speaking: "Speaking" };
  stateLabel.textContent = labels[next] || next;

  if (next === "speaking") {
    $("#stopBtn").classList.remove("hidden");
  } else {
    $("#stopBtn").classList.add("hidden");
  }
}

function friendly(message) {
  if (/10061|refused|ollama/i.test(message || "")) {
    return "Ollama isn't running. Start it with \"ollama serve\", then ask again.";
  }
  return message;
}

/* ============================================================
   Brain pill
   ============================================================ */
function paintBrain() {
  const label = `${brain.mode.toUpperCase()} · ${brain.model}`;
  brainLabel.textContent = label;
  $(".brain-dot").style.background = brain.mode === "local" ? "var(--green)" : "var(--cyan)";
}
$("#brainPill").addEventListener("click", async () => {
  const next = brain.mode === "local" ? "cloud" : "local";
  try {
    const data = await post("/api/brain", { mode: next });
    brain = data.brain;
    paintBrain();
  } catch (e) { showToast("Couldn't switch brain: " + e.message); }
});

/* ============================================================
   TTS with Web Audio amplitude
   ============================================================ */
function cleanForTTS(text) {
  return text.replace(/```[\s\S]*?```/g, " code block ")
    .replace(/[*_~`#>|]/g, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/\s+/g, " ").trim();
}

async function speak(text) {
  if (!text) { setStatus("online"); return; }
  setStatus("speaking");
  try {
    const res = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Ella-Request-Token": API_TOKEN },
      body: JSON.stringify({ text: cleanForTTS(text).slice(0, 800) }),
    });
    const ct = res.headers.get("content-type") || "";
    if (!res.ok) {
      let data = {};
      try { data = await res.json(); } catch (_) {}
      showToast(data.error || "Speech synthesis is unavailable.");
      setStatus("online");
      return;
    }
    if (ct.includes("audio")) {
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      currentAudio = audio;

      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioCtx.createMediaElementSource(audio);
      ttsAnalyser = audioCtx.createAnalyser();
      ttsAnalyser.fftSize = 256;
      ttsDataArray = new Uint8Array(ttsAnalyser.frequencyBinCount);
      source.connect(ttsAnalyser);
      ttsAnalyser.connect(audioCtx.destination);

      audio.onended = () => {
        setStatus("online");
        URL.revokeObjectURL(url);
        currentAudio = null;
        ttsAnalyser = null;
        audioCtx.close();
        if (conversationMode) setTimeout(startListening, 300);
      };
      audio.onerror = () => {
        setStatus("online");
        URL.revokeObjectURL(url);
        currentAudio = null;
        ttsAnalyser = null;
        audioCtx.close();
      };
      audio.play();
    } else {
      setStatus("online");
    }
  } catch (_) {
    setStatus("online");
  }
}

function getTTSAmplitude() {
  if (!ttsAnalyser || !ttsDataArray) return 0;
  ttsAnalyser.getByteFrequencyData(ttsDataArray);
  let sum = 0;
  for (let i = 0; i < ttsDataArray.length; i++) sum += ttsDataArray[i];
  return sum / ttsDataArray.length / 255;
}

/* ============================================================
   STT — mic recording
   ============================================================ */
let micLevel = 0;
function say(text) {
  liveCaption.textContent = text;
}

async function sendAudio(blob) {
  setStatus("transcribing");
  say("Transcribing…");
  try {
    const res = await fetch("/api/stt", {
      method: "POST",
      headers: { "Content-Type": blob.type || "audio/webm", "X-Ella-Request-Token": API_TOKEN },
      body: blob,
    });
    const data = await res.json();
    if (!data.ok) { say(data.error || "Couldn't understand that."); setStatus("online"); return; }
    chatInput.value = data.text;
    $("#inputForm").requestSubmit();
  } catch (error) {
    say("Speech-to-text failed: " + error.message);
    setStatus("online");
  }
}

async function startListening() {
  const micBtn = $("#micBtn");
  if (!navigator.mediaDevices || !window.MediaRecorder) { showToast("This browser can't record audio."); return; }
  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
  } catch (error) {
    if (error.name === "NotAllowedError") showToast("Mic blocked. Click the lock icon to allow.");
    else if (error.name === "NotFoundError") showToast("No microphone found.");
    else showToast("Mic error: " + error.message);
    return;
  }
  if (currentAudio) { currentAudio.pause(); currentAudio.src = ""; currentAudio = null; }

  const type = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg", "audio/mp4"].find((t) => MediaRecorder.isTypeSupported(t)) || "";
  const recorder = new MediaRecorder(stream, type ? { mimeType: type } : undefined);
  const chunks = [];
  const audioCtx = new AudioContext();
  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 1024;
  audioCtx.createMediaStreamSource(stream).connect(analyser);
  const buf = new Uint8Array(analyser.fftSize);
  let heard = false, quietSince = performance.now(), started = performance.now(), peak = 0;

  const timer = setInterval(() => {
    analyser.getByteTimeDomainData(buf);
    let sum = 0;
    for (const v of buf) sum += (v - 128) * (v - 128);
    const level = Math.sqrt(sum / buf.length);
    micLevel = Math.min(1, level / 40);
    peak = Math.max(peak, level);
    const now = performance.now();
    if (level > 6) { heard = true; quietSince = now; }
    if ((heard && now - quietSince > 1400) || now - started > 15000 || (!heard && now - started > 6000)) stop();
  }, 100);

  function stop() { if (recorder.state !== "inactive") recorder.stop(); }

  recorder.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
  recorder.onstop = () => {
    clearInterval(timer);
    stream.getTracks().forEach((t) => t.stop());
    audioCtx.close();
    micBtn.classList.remove("on");
    micLevel = 0;
    rec = null;
    if (!heard) { say("I didn't hear anything. Check the mic."); setStatus("online"); return; }
    sendAudio(new Blob(chunks, { type: recorder.mimeType || "audio/webm" }));
  };

  rec = { stop };
  recorder.start(250);
  micBtn.classList.add("on");
  setStatus("listening");
  say("Listening… speak now.");
}

/* ============================================================
   Input handling
   ============================================================ */
let mainSending = false;

$("#inputForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (mainSending) return;
  const text = chatInput.value.trim();
  const image = pendingMainImage;

  if (!text && !image) return;
  mainSending = true;
  chatInput.value = "";

  if (image) {
    pendingMainImage = null;
    const preview = $("#pastePreview");
    if (preview) preview.classList.add("hidden");
    addImageMessage(image, "screenshot.png");
  }
  if (text) addMessage("user", text);

  setStatus("thinking");
  liveCaption.textContent = "";
  try {
    const body = { text: text || "What do you see in this image?" };
    if (image) body.image = image;
    const data = await post("/api/ask", body);
    const reply = data.ok === false ? friendly(data.error) : (data.text || data.error || "No reply.");
    const tag = brain.mode === "local" ? (image ? "moondream" : brain.model) : "cloud";
    addMessage("ella", reply, tag, data.usage && data.usage.completion);
    if (data.usage_summary) paintUsage(data.usage_summary);
    typeCaption(reply);
    if (data.ok !== false) speak(reply);
    else setStatus("online");
  } catch (error) {
    const msg = friendly(error.message);
    addMessage("ella", msg, "error");
    typeCaption(msg);
    setStatus("online");
  } finally {
    mainSending = false;
  }
});

function addImageMessage(dataUrl, filename) {
  const div = document.createElement("div");
  div.className = "msg msg-user";
  const img = document.createElement("img");
  img.src = dataUrl;
  img.style.cssText = "max-width:220px;max-height:180px;border-radius:8px;display:block;margin-bottom:4px;";
  div.appendChild(img);
  const meta = document.createElement("div");
  meta.className = "msg-meta";
  const time = new Date().toLocaleTimeString("en-PH", { hour: "2-digit", minute: "2-digit", hour12: true });
  const timeEl = document.createElement("span");
  timeEl.textContent = time;
  const filenameEl = document.createElement("span");
  filenameEl.className = "file-label";
  filenameEl.textContent = filename;
  meta.append(timeEl, filenameEl);
  div.appendChild(meta);
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/* ---- Clipboard paste image (main chat) ---- */
let pendingMainImage = null;
const MAX_IMAGE_FILE_BYTES = 12 * 1024 * 1024;
const ALLOWED_IMAGE_TYPES = new Set(["image/png", "image/jpeg", "image/webp"]);

function validImageFile(file) {
  return !!file && ALLOWED_IMAGE_TYPES.has(file.type.toLowerCase()) && file.size > 0 && file.size <= MAX_IMAGE_FILE_BYTES;
}

function validImageDataUrl(value) {
  return typeof value === "string" && value.length <= 16 * 1024 * 1024 + 128
    && /^data:image\/(?:png|jpeg|webp);base64,[A-Za-z0-9+/]*={0,2}$/i.test(value);
}

document.addEventListener("paste", (e) => {
  const items = (e.clipboardData || {}).items;
  if (!items) return;

  for (const item of items) {
    if (item.type.startsWith("image/")) {
      e.preventDefault();
      const file = item.getAsFile();
      if (!validImageFile(file)) { showToast("Use a PNG, JPEG, or WebP image up to 12 MiB."); return; }
      const reader = new FileReader();
      reader.onload = () => {
        if (!validImageDataUrl(reader.result)) { showToast("That image format or size is not supported."); return; }
        const el = document.activeElement;
        const projWin = el?.closest(".proj-win") || el?.closest(".proj-win-input");
        if (projWin) {
          const inputArea = projWin.querySelector(".proj-win-input") || projWin.closest(".proj-win")?.querySelector(".proj-win-input");
          if (inputArea) {
            handleProjectPaste(inputArea, reader.result);
            return;
          }
        }
        pendingMainImage = reader.result;
        showPastePreview(reader.result);
      };
      reader.readAsDataURL(file);
      return;
    }
  }
});

function showPastePreview(dataUrl) {
  let preview = $("#pastePreview");
  if (!preview) {
    preview = document.createElement("div");
    preview.id = "pastePreview";
    const img = document.createElement("img");
    const remove = document.createElement("button");
    remove.className = "paste-remove";
    remove.type = "button";
    remove.title = "Remove";
    remove.textContent = "✕";
    preview.append(img, remove);
    $("#inputForm").parentElement.insertBefore(preview, $("#inputForm"));
    preview.querySelector(".paste-remove").addEventListener("click", () => {
      pendingMainImage = null;
      preview.classList.add("hidden");
    });
  }
  preview.querySelector("img").src = dataUrl;
  preview.classList.remove("hidden");
}

function handleProjectPaste(inputArea, dataUrl) {
  const win = inputArea.closest(".proj-win");
  if (!win) return;
  const pid = Object.keys(openProjectWindows).find(k => openProjectWindows[k].el === win);
  if (!pid) return;
  const state = openProjectWindows[pid];
  const proj = state.proj;
  const chatEl = win.querySelector(".proj-win-chat");
  const inputEl = inputArea.querySelector("input[type=text]");

  /* show inline preview before sending */
  let existing = inputArea.querySelector(".pw-paste-preview");
  if (existing) existing.remove();
  const preview = document.createElement("div");
  preview.className = "pw-paste-preview";
  const img = document.createElement("img");
  img.src = dataUrl;
  img.style.cssText = "max-width:120px;max-height:80px;border-radius:6px;";
  const remove = document.createElement("button");
  remove.className = "pw-paste-x";
  remove.type = "button";
  remove.title = "Remove";
  remove.textContent = "✕";
  preview.append(img, remove);
  inputArea.insertBefore(preview, inputArea.firstChild);
  preview.querySelector(".pw-paste-x").addEventListener("click", () => { preview.remove(); state._pendingImg = null; });
  state._pendingImg = dataUrl;

  /* auto-send if there's text, otherwise wait for Enter */
  const existingText = inputEl.value.trim();
  if (existingText) {
    sendProjectImage(pid, existingText);
    inputEl.value = "";
  }
}

function sendProjectImage(pid, caption) {
  const state = openProjectWindows[pid];
  if (!state || !state._pendingImg) return;
  const img = state._pendingImg;
  state._pendingImg = null;
  const proj = state.proj;
  const win = state.el;
  const chatEl = win.querySelector(".proj-win-chat");
  const preview = win.querySelector(".pw-paste-preview");
  if (preview) preview.remove();

  addProjectImg(chatEl, "user", "screenshot.png", img, proj);
  const dots = addThinkingDot(chatEl, proj);
  post("/api/ask", { text: caption || "What do you see in this image?", project: pid, image: img })
    .then((data) => {
      dots.remove();
      const reply = data.ok === false ? (data.error || "Error") : (data.text || "No reply.");
      addProjectMsg(chatEl, "ella", reply, proj, data.usage && data.usage.completion);
      if (data.usage_summary) paintUsage(data.usage_summary);
    })
    .catch((e) => { dots.remove(); addProjectMsg(chatEl, "ella", "Error: " + e.message, proj); });
}

$("#micBtn").addEventListener("click", () => { if (rec) rec.stop(); else startListening(); });

$("#stopBtn").addEventListener("click", () => {
  if (currentAudio) { currentAudio.pause(); currentAudio.src = ""; currentAudio = null; }
  setStatus("online");
  liveCaption.textContent = "";
});

/* ============================================================
   Keyboard shortcuts
   ============================================================ */
function isTypingInInput() {
  const el = document.activeElement;
  if (!el) return false;
  return el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.isContentEditable;
}

document.addEventListener("keydown", (e) => {
  if (e.key === " " && !isTypingInInput() && !e.ctrlKey && !e.altKey) {
    e.preventDefault();
    if (rec) rec.stop(); else startListening();
  }
  if (e.key === "Escape") {
    if (!$("#projLauncher").classList.contains("hidden")) {
      $("#projLauncher").classList.add("hidden");
      return;
    }
    if (currentAudio) { currentAudio.pause(); currentAudio.src = ""; currentAudio = null; }
    if (rec) rec.stop();
    setStatus("online");
    liveCaption.textContent = "";
  }
  if (e.ctrlKey && e.key === "k") {
    e.preventDefault();
    const activeWin = document.querySelector(".proj-win:not(.hidden):last-child");
    if (activeWin) activeWin.querySelector(".proj-win-input input")?.focus();
    else chatInput.focus();
  }
  if (e.ctrlKey && e.key === "n") {
    e.preventDefault();
    chatHistory = [];
    chatMessages.innerHTML = "";
    liveCaption.textContent = "";
  }
});

/* ============================================================
   Settings
   ============================================================ */
$("#ambientToggle").addEventListener("change", (e) => { ambientEnabled = e.target.checked; });
$("#reducedMotion").addEventListener("change", (e) => {
  reducedMotion = e.target.checked;
  document.body.classList.toggle("reduced-motion", reducedMotion);
});
$("#convoToggle").addEventListener("change", (e) => { conversationMode = e.target.checked; });

/* ============================================================
   ORB drawing (center stage, 320px)
   ============================================================ */
function drawOrb() {
  const w = orbCanvas.width;
  const h = orbCanvas.height;
  const c = w / 2;
  const scale = w / 320;

  octx.setTransform(scale, 0, 0, scale, 0, 0);
  octx.clearRect(0, 0, 320, 320);

  const cx = 160;
  const live = mode === "speaking" || mode === "thinking" || mode === "listening" || mode === "transcribing";
  const col = mode === "speaking" ? "#2bff9a" : mode === "thinking" ? "#ffb020" : "#22e5ff";

  octx.lineCap = "round";

  /* tick marks */
  for (let i = 0; i < 72; i++) {
    const angle = (i / 72) * Math.PI * 2;
    octx.strokeStyle = "rgba(120,200,220,.2)";
    octx.lineWidth = 1;
    octx.beginPath();
    const inner = 138;
    const outer = i % 6 ? 143 : 148;
    octx.moveTo(cx + Math.cos(angle) * inner, cx + Math.sin(angle) * inner);
    octx.lineTo(cx + Math.cos(angle) * outer, cx + Math.sin(angle) * outer);
    octx.stroke();
  }

  /* scanline overlay (subtle) */
  octx.strokeStyle = "rgba(200,230,240,.03)";
  octx.lineWidth = 0.5;
  for (let y = 0; y < 320; y += 4) {
    octx.beginPath();
    octx.moveTo(0, y);
    octx.lineTo(320, y);
    octx.stroke();
  }

  /* main arcs */
  octx.shadowColor = col;
  octx.shadowBlur = 16;
  octx.strokeStyle = col;
  octx.lineWidth = 5;
  const speed = mode === "thinking" ? 0.8 : 0.25;
  for (let k = 0; k < 6; k++) {
    const start = tick * speed + k * 1.047;
    octx.beginPath();
    octx.arc(cx, cx, 126, start, start + 0.55);
    octx.stroke();
  }

  /* amber accent arc */
  octx.strokeStyle = "#ffb020";
  octx.shadowColor = "#ffb020";
  octx.lineWidth = 4;
  const orangePos = mode === "speaking" ? tick * 0.4 : -1.3;
  octx.beginPath();
  octx.arc(cx, cx, 110, orangePos, orangePos + 1.2);
  octx.stroke();

  octx.shadowBlur = 0;

  /* dashed inner ring */
  octx.setLineDash([2, 6]);
  octx.strokeStyle = "rgba(200,230,240,.35)";
  octx.lineWidth = 1.5;
  octx.beginPath();
  octx.arc(cx, cx, 88, -tick * 0.5, -tick * 0.5 + Math.PI * 2);
  octx.stroke();
  octx.setLineDash([]);

  /* core glow */
  let amplitude = 0;
  if (mode === "speaking") amplitude = getTTSAmplitude();
  else if (mode === "listening") amplitude = micLevel;

  const baseR = 50;
  const pulseR = baseR + (live ? amplitude * 20 + Math.sin(tick * 6) * 3 : Math.sin(tick * 1.5) * 2);
  const glow = octx.createRadialGradient(cx, cx, 0, cx, cx, pulseR);
  const coreColor = mode === "speaking" ? "rgba(43,255,154,.45)"
    : mode === "thinking" ? "rgba(255,176,32,.25)"
    : mode === "listening" ? `rgba(34,229,255,${0.15 + amplitude * 0.3})`
    : "rgba(34,229,255,.12)";
  glow.addColorStop(0, coreColor);
  glow.addColorStop(1, "rgba(5,8,13,.9)");
  octx.fillStyle = glow;
  octx.beginPath();
  octx.arc(cx, cx, pulseR, 0, Math.PI * 2);
  octx.fill();

  octx.strokeStyle = col;
  octx.lineWidth = 2;
  octx.shadowBlur = live ? 24 : 8;
  octx.shadowColor = col;
  octx.stroke();
  octx.shadowBlur = 0;

  /* label */
  octx.fillStyle = "#e8f6ff";
  octx.font = "bold 16px 'Rajdhani', Consolas, monospace";
  octx.textAlign = "center";
  octx.textBaseline = "middle";
  octx.fillText("E.L.L.A.", cx, cx);
}

/* ============================================================
   Brain graph layout + drawing
   ============================================================ */
function layoutGraph(notes) {
  const folders = [];
  notes.forEach((n) => { if (!folders.includes(n.folder)) folders.push(n.folder); });
  nodes = [];
  links = [];
  const center = 0;
  nodes.push({ x: 0.5, y: 0.5, r: 8, color: COLORS.Concepts, name: "Vault", real: true, phase: 0 });

  folders.forEach((folder, i) => {
    const angle = (i / Math.max(folders.length, 1)) * Math.PI * 2;
    const hub = nodes.length;
    const cat = (notes.find((n) => n.folder === folder) || {}).category;
    nodes.push({
      x: 0.5 + Math.cos(angle) * 0.28,
      y: 0.5 + Math.sin(angle) * 0.28,
      r: 6, color: COLORS[cat] || COLORS.Notes,
      name: folder, real: true, phase: i, category: cat,
    });
    links.push([center, hub]);

    const children = notes.filter((n) => n.folder === folder);
    children.forEach((note, ci) => {
      const spread = (ci / Math.max(children.length, 1)) * Math.PI * 2;
      nodes.push({
        x: nodes[hub].x + Math.cos(spread) * 0.08,
        y: nodes[hub].y + Math.sin(spread) * 0.07,
        r: 3.2, color: COLORS[note.category] || COLORS.Notes,
        name: note.name, real: true, phase: ci,
        category: note.category, folder: folder,
      });
      links.push([hub, nodes.length - 1]);
    });
  });

  /* stats for brain view */
  const counts = {};
  notes.forEach((n) => { counts[n.category] = (counts[n.category] || 0) + 1; });
  const catHtml = Object.keys(COLORS).map((name) => {
    const c = counts[name] || 0;
    return `<button class="cat-btn" data-cat="${name}"><span class="cat-dot" style="background:${COLORS[name]}"></span>${name}<span class="cat-count">${c}</span></button>`;
  }).join("");
  $("#brainCats").innerHTML = catHtml;
  $$("#brainCats .cat-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const name = btn.dataset.cat;
      if (hidden.has(name)) hidden.delete(name);
      else hidden.add(name);
      btn.style.opacity = hidden.has(name) ? "0.35" : "1";
    });
  });

  const hubs = folders.map((f) => ({
    folder: f,
    count: notes.filter((n) => n.folder === f).length,
    color: COLORS[(notes.find((n) => n.folder === f) || {}).category] || COLORS.Notes,
  })).sort((a, b) => b.count - a.count).slice(0, 8);
  $("#hubList").innerHTML = hubs.map((h) =>
    `<div class="hub-row"><span class="hub-dot" style="background:${safeProjectColor(h.color)}"></span>${escapeHtml(h.folder)}<span class="hub-count">${h.count}</span></div>`
  ).join("");
}

function graphPoint(node, w, h) {
  const repel = Number($("#repel").value) / 100;
  const reach = Number($("#link").value) / 100;
  const ox = (node.x - 0.5) * reach * 1.4;
  const oy = (node.y - 0.5) * reach * 1.4;
  return [
    w * (0.5 + ox) + Math.sin(tick * 0.5 + node.phase) * (2 + repel * 8),
    h * (0.5 + oy) + Math.cos(tick * 0.4 + node.phase) * (2 + repel * 8),
  ];
}

function nodeVisible(node) {
  return !node.category || !hidden.has(node.category);
}

function drawGraph(ctx, w, h, isAmbient) {
  const spots = nodes.map((n) => graphPoint(n, w, h));
  const neighbor = new Set();
  if (!isAmbient && focus >= 0) {
    neighbor.add(focus);
    links.forEach(([a, b]) => {
      if (a === focus) neighbor.add(b);
      if (b === focus) neighbor.add(a);
    });
  }

  ctx.lineWidth = isAmbient ? 0.4 : 0.6;
  links.forEach(([a, b]) => {
    if (!nodeVisible(nodes[a]) || !nodeVisible(nodes[b])) return;
    const hot = isAmbient || focus < 0 || (neighbor.has(a) && neighbor.has(b));
    ctx.strokeStyle = isAmbient
      ? "rgba(47,224,176,0.15)"
      : hot ? "rgba(47,224,176,0.28)" : "rgba(47,224,176,0.05)";
    ctx.beginPath();
    ctx.moveTo(spots[a][0], spots[a][1]);
    ctx.lineTo(spots[b][0], spots[b][1]);
    ctx.stroke();
  });

  nodes.forEach((node, i) => {
    if (!nodeVisible(node)) return;
    if (isAmbient && !node.real) return;
    const hot = isAmbient || focus < 0 || neighbor.has(i);
    ctx.beginPath();
    ctx.arc(spots[i][0], spots[i][1], isAmbient ? node.r * 0.7 : node.r, 0, Math.PI * 2);
    ctx.fillStyle = node.color;
    ctx.globalAlpha = isAmbient ? 0.3 : (hot ? 0.95 : 0.12);
    ctx.fill();
    ctx.globalAlpha = 1;

    if (!isAmbient && node.real && node.r > 4 && hot) {
      ctx.fillStyle = "#d6dbe3";
      ctx.font = "12px Inter, Segoe UI, sans-serif";
      ctx.fillText(node.name, spots[i][0] + 10, spots[i][1] - 8);
    }
  });
}

/* ============================================================
   Brain view interaction
   ============================================================ */
if (brainCanvas) {
  brainCanvas.addEventListener("click", async (e) => {
    const rect = brainCanvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const w = brainCanvas.width;
    const h = brainCanvas.height;
    const spots = nodes.map((n) => graphPoint(n, w, h));
    let hit = -1;
    spots.forEach((s, i) => {
      if (!nodes[i].real || !nodeVisible(nodes[i])) return;
      const dx = mx - s[0];
      const dy = my - s[1];
      if (dx * dx + dy * dy < 200) hit = i;
    });
    focus = hit;
    if (hit >= 0 && nodes[hit].name && nodes[hit].name !== "Vault") {
      const q = nodes[hit].folder ? nodes[hit].name : nodes[hit].name.replace(/^\d+\s*-\s*/, "");
      try {
        const note = await api("/api/note?q=" + encodeURIComponent(q));
        const text = note.text || (note.matches || []).join(", ") || "No note found.";
        $("#biTitle").textContent = nodes[hit].name;
        $("#biBody").textContent = text.slice(0, 1200);
      } catch (_) {}
    }
  });
}

$("#bcToggle").addEventListener("click", () => {
  $("#bcDrawer").classList.toggle("collapsed");
  $("#bcToggle").textContent = $("#bcDrawer").classList.contains("collapsed") ? "Controls ▸" : "Controls ▾";
});
$("#fitBtn").addEventListener("click", () => {
  focus = -1;
  hidden.clear();
  $$("#brainCats .cat-btn").forEach((b) => b.style.opacity = "1");
});

/* ============================================================
   Canvas resize
   ============================================================ */
function resizeAmbient() {
  const home = $("#homeView");
  if (!home) return;
  ambientCanvas.width = home.clientWidth;
  ambientCanvas.height = home.clientHeight;
}
function resizeBrainCanvas() {
  const bv = $("#brainView");
  if (!bv) return;
  brainCanvas.width = bv.clientWidth;
  brainCanvas.height = bv.clientHeight;
}
window.addEventListener("resize", () => {
  resizeAmbient();
  if (currentView === "brain") resizeBrainCanvas();
});
resizeAmbient();

/* ============================================================
   Main render loop
   ============================================================ */
function render() {
  tick += 0.016;

  drawOrb();

  if (currentView === "home" && ambientEnabled && nodes.length) {
    actx.clearRect(0, 0, ambientCanvas.width, ambientCanvas.height);
    drawGraph(actx, ambientCanvas.width, ambientCanvas.height, true);
  }

  if (currentView === "brain" && nodes.length) {
    bctx.fillStyle = "#05080d";
    bctx.fillRect(0, 0, brainCanvas.width, brainCanvas.height);
    drawGraph(bctx, brainCanvas.width, brainCanvas.height, false);
  }

  requestAnimationFrame(render);
}

/* ============================================================
   Greeting
   ============================================================ */
function greet() {
  const key = "ella_greeted_" + new Date().toDateString();
  if (sessionStorage.getItem(key)) return;
  sessionStorage.setItem(key, "1");
  const h = new Date().getHours();
  let greeting;
  if (h < 12) greeting = GREETINGS[0];
  else if (h < 17) greeting = GREETINGS[3];
  else greeting = GREETINGS[4];
  setTimeout(() => {
    addMessage("ella", greeting, brain.model);
    typeCaption(greeting);
    speak(greeting);
  }, 1200);
}

/* ============================================================
   Status dots
   ============================================================ */
let panelState = {};

function fmtTok(n) {
  n = Number(n) || 0;
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "m";
  if (n >= 1000) return (n / 1000).toFixed(n >= 10000 ? 0 : 1) + "k";
  return String(n);
}
function tokLevel(pct) {
  if (pct >= 90) return "hot";
  if (pct >= 70) return "warm";
  return "ok";
}
function escapeHtml(s) {
  return String(s || "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);
}
function safeProjectColor(value) {
  return /^#[0-9a-f]{6}$/i.test(String(value || "")) ? value : "#4a7fe0";
}
function shortTime(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleTimeString("en-PH", { hour: "2-digit", minute: "2-digit", hour12: true });
}

function paintUsage(u) {
  if (!u) return;
  panelState.usage = u;
  const totals = u.totals || {};
  const last = u.last || {};
  const ctx = u.ctx_limit || 4096;
  const used = Number(u.ctx_used != null ? u.ctx_used : last.prompt) || 0;
  const pct = ctx ? Math.min(100, Math.round((used / ctx) * 100)) : 0;
  const level = tokLevel(pct);
  const session = (totals.prompt || 0) + (totals.completion || 0);
  const label = $("#tokenLabel");
  if (label) label.textContent = `${fmtTok(used)} / ${fmtTok(ctx)}`;
  const fill = $("#tokenFill");
  if (fill) { fill.style.width = pct + "%"; fill.dataset.level = level; }
  const set = (id, val) => { const el = $(id); if (el) el.textContent = val; };
  set("#hudPrompt", fmtTok(totals.prompt));
  set("#hudReply", fmtTok(totals.completion));
  set("#hudSession", fmtTok(session));
  set("#hudSpeed", last.tps ? `${last.tps}/s` : "—");
  set("#hudCalls", `${totals.calls || 0} calls`);
  set("#chatTokens", `${fmtTok(session)} tok`);
  const readout = $("#ctxReadout");
  if (readout) readout.textContent = `${used.toLocaleString()} / ${ctx.toLocaleString()}`;
  const ctxFill = $("#ctxFill");
  if (ctxFill) { ctxFill.style.width = pct + "%"; ctxFill.dataset.level = level; }
}

function renderActivity() {
  const el = $("#activityList");
  if (!el) return;
  const rows = panelState.activity || [];
  el.innerHTML = rows.length ? rows.map((row) => `
    <div class="activity-row">
      <span class="activity-kind">${escapeHtml(row.kind || "note")}</span>
      <span class="activity-main">${escapeHtml(row.text || "")}</span>
      <span>${shortTime(row.at)}</span>
    </div>`).join("") : `<div class="empty-note">No activity yet.</div>`;
}

function renderHealth() {
  const u = panelState.usage || {};
  const totals = u.totals || {};
  const last = u.last || {};
  const quota = u.quota || {};
  const stats = $("#healthStats");
  if (stats) {
    const session = (totals.prompt || 0) + (totals.completion || 0);
    const callsCount = Number(totals.calls) || 0;
    const tokensPerSecond = Number(last.tps);
    const cards = [
      ["Prompt", fmtTok(totals.prompt), "tokens in"],
      ["Reply", fmtTok(totals.completion), "tokens out"],
      ["Session", fmtTok(session), `${callsCount} calls · $0.00`],
      ["Speed", Number.isFinite(tokensPerSecond) && tokensPerSecond > 0 ? `${tokensPerSecond}/s` : "—", last.provider || "waiting"],
    ];
    stats.innerHTML = cards.map(([k, v, s]) =>
      `<div class="stat-card"><span>${escapeHtml(k)}</span><strong>${escapeHtml(v)}</strong><em>${escapeHtml(s)}</em></div>`
    ).join("");
  }
  const calls = $("#healthCalls");
  if (calls) {
    const rows = u.calls || [];
    let html = rows.length ? rows.map((c) => `
      <div class="call-row">
        <span>${shortTime(c.at)}</span>
        <span class="call-main">${escapeHtml(c.provider || "model")} · ${escapeHtml(c.kind || "chat")}</span>
        <span>${fmtTok(c.prompt)} → ${fmtTok(c.completion)}</span>
      </div>`).join("") : `<div class="empty-note">No calls logged yet. Send a message and the ledger fills in.</div>`;
    if (quota.remaining != null && quota.remaining !== "") {
      html += `<div class="call-row"><span class="call-main">Rate limit left · ${escapeHtml(quota.provider || "cloud")}</span><span>${escapeHtml(quota.remaining)}</span></div>`;
    }
    calls.innerHTML = html;
  }
  const local = $("#healthLocal");
  if (local) {
    const names = panelState.local_models || [];
    const active = (panelState.brain || brain || {}).model;
    local.innerHTML = names.length ? names.map((n) => `
      <div class="model-chip"><span class="call-main">${escapeHtml(n)}</span>${n === active ? '<span class="on">ACTIVE</span>' : ""}</div>
    `).join("") : `<div class="empty-note">Ollama has no models listed.</div>`;
  }
  const free = $("#healthFree");
  if (free) {
    const models = panelState.free_models || [];
    free.innerHTML = models.length ? models.map((m) => `
      <div class="model-chip"><span class="call-main" title="${escapeHtml(m.id)}">${escapeHtml(m.name || m.id)}</span></div>
    `).join("") : `<div class="empty-note">Free cloud list is empty.</div>`;
  }
}

function applyState(state) {
  panelState = state || {};
  if (state.brain) { brain = state.brain; paintBrain(); }
  if (state.usage) paintUsage(state.usage);
  updateStatusDots(state);
  if (currentView === "health") renderHealth();
  if (currentView === "inbox") renderActivity();
  if (currentView === "tasks") renderDashboard();
}

async function refreshPanel() {
  try { applyState(await api("/api/state")); } catch (_) {}
}

function updateStatusDots(state) {
  const dots = $$("#statusDots .sdot");
  const setup = state.setup || [];
  const ollamaOk = setup.find((s) => s.name === "model");
  if (ollamaOk) dots[0].className = "sdot " + (ollamaOk.ok ? "green" : "red");
  dots[1].className = "sdot green";
  dots[2].className = "sdot green";
}

/* ============================================================
   Boot
   ============================================================ */
async function boot() {
  try {
    const [map, state] = await Promise.all([api("/api/graph"), api("/api/state"), loadProjects()]);
    applyState(state);
    layoutGraph(map.notes || []);
    resizeAmbient();
    resizeBrainCanvas();
    render();
    showQuickChips();
    greet();
    restoreProjects();
  } catch (e) {
    showToast("Couldn't connect to Ella server: " + e.message, 8000);
    render();
  }
}

/* ============================================================
   PROJECT BOTS
   ============================================================ */
let projectConfigs = [];
let openProjectWindows = {};
let minimizedProjects = new Set();
let projectZIndex = 201;

async function loadProjects() {
  try {
    const data = await post("/api/projects", { action: "list" });
    projectConfigs = data.projects || [];
  } catch (_) { projectConfigs = []; }
}

function toggleLauncher() {
  const el = $("#projLauncher");
  el.classList.toggle("hidden");
  if (!el.classList.contains("hidden")) renderLauncher();
}
$("#projBtn").addEventListener("click", toggleLauncher);
$("#projOverlay").addEventListener("click", () => $("#projLauncher").classList.add("hidden"));

function renderLauncher() {
  const grid = $("#projGrid");
  grid.innerHTML = projectConfigs.map((p) => {
    const color = safeProjectColor(p.color);
    const linkCount = (p.links || []).length;
    const badge = linkCount ? `<span class="proj-card-links" title="${linkCount} linked resources">📎${linkCount}</span>` : "";
    return `
    <div class="proj-card" data-pid="${escapeHtml(p.id)}" style="border-color: ${color}22;">
      <span class="proj-card-icon">${escapeHtml(p.icon || "📁")}</span>
      <span class="proj-card-name">${escapeHtml(p.name)}</span>
      <div class="proj-card-foot">
        <span class="proj-card-status" style="background: ${color};"></span>
        ${badge}
      </div>
    </div>`;
  }).join("") + `
    <div class="proj-card proj-card-add" id="projAddCard">
      <span class="proj-card-icon">+</span>
      <span class="proj-card-name" style="color: var(--text-dim);">Add project</span>
    </div>
  `;
  $$("#projGrid .proj-card[data-pid]").forEach((card) => {
    card.addEventListener("click", () => {
      const pid = card.dataset.pid;
      openProjectWindow(pid);
      $("#projLauncher").classList.add("hidden");
    });
  });
}

async function openProjectWindow(pid) {
  if (openProjectWindows[pid]) {
    const win = openProjectWindows[pid].el;
    win.classList.remove("hidden");
    win.style.zIndex = ++projectZIndex;
    minimizedProjects.delete(pid);
    renderMiniChips();
    return;
  }

  const proj = projectConfigs.find((p) => p.id === pid);
  if (!proj) return;
  const color = safeProjectColor(proj.color);

  let session;
  try {
    const data = await post("/api/projects", { action: "session", project_id: pid });
    session = data.session || { messages: [] };
  } catch (_) { session = { messages: [] }; }

  let saved = null;
  try { saved = JSON.parse(localStorage.getItem("projWinPos_" + pid) || "null"); } catch (_) {}
  const storedNumber = (value, fallback, min, max) => {
    const number = Number(value);
    return Number.isFinite(number) ? Math.min(max, Math.max(min, number)) : fallback;
  };
  const x = storedNumber(saved?.x, 200 + Object.keys(openProjectWindows).length * 30, -window.innerWidth, window.innerWidth);
  const y = storedNumber(saved?.y, 100 + Object.keys(openProjectWindows).length * 20, 0, window.innerHeight);
  const w = storedNumber(saved?.w, 440, 280, Math.max(280, window.innerWidth));
  const h = storedNumber(saved?.h, 480, 300, Math.max(300, window.innerHeight));

  const customActions = (proj.actions || []).slice(0, 4);
  const actionsHtml = customActions.length
    ? customActions.map((a, i) => `<button class="proj-action" data-idx="${i}">${escapeHtml(a.label)}</button>`).join("")
    : `<button class="proj-action" data-act="status">Status</button><button class="proj-action" data-act="continue">Continue</button><button class="proj-action" data-act="tasks">Tasks</button>`;

  const linksArr = proj.links || [];
  const linksHtml = linksArr.map((lnk, i) => `
    <div class="pw-link-row" data-li="${i}">
      <span class="pw-link-label" title="${escapeHtml(lnk.url)}">${escapeHtml(lnk.label || lnk.url || "Link")}</span>
      <button class="pw-link-open" title="Open">↗</button>
      <button class="pw-link-del" title="Remove">✕</button>
    </div>`).join("");

  const win = document.createElement("div");
  win.className = "proj-win";
  win.style.cssText = `left:${x}px;top:${y}px;width:${w}px;height:${h}px;z-index:${++projectZIndex};`;
  win.innerHTML = `
    <div class="proj-win-header">
      <span class="proj-win-icon">${escapeHtml(proj.icon || "📁")}</span>
      <span class="proj-win-name">${escapeHtml(proj.name)}</span>
      <span class="proj-win-dot" style="background:${color};box-shadow:0 0 4px ${color};"></span>
      <button class="proj-win-btn pw-links-toggle" title="Links" style="font-size:12px;">📎</button>
      <button class="proj-win-btn pw-clear" title="Clear chat">🗑</button>
      <button class="proj-win-btn pw-min" title="Minimize">─</button>
      <button class="proj-win-btn pw-close" title="Close">✕</button>
    </div>
    <div class="pw-links-panel hidden">
      <div class="pw-links-list">${linksHtml}</div>
      <div class="pw-link-add">
        <input type="text" class="pw-link-add-label" placeholder="Label" autocomplete="off">
        <input type="text" class="pw-link-add-url" placeholder="URL or path" autocomplete="off">
        <button class="pw-link-add-btn" title="Add link">+</button>
      </div>
    </div>
    <div class="proj-win-actions">${actionsHtml}</div>
    <div class="proj-win-chat"></div>
    <div class="proj-win-input">
      <input type="text" placeholder="Ask ${escapeHtml(proj.name)}..." autocomplete="off">
      <input type="file" class="pw-file-input" accept="image/png,image/jpeg,image/webp" style="display:none">
      <button class="attach-btn pw-attach" title="Attach image">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
      </button>
      <button class="proj-win-send">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
      </button>
    </div>
  `;

  $("#projWindows").appendChild(win);

  const chatEl = win.querySelector(".proj-win-chat");
  const inputEl = win.querySelector(".proj-win-input input");
  const state = { el: win, proj, unread: 0 };
  openProjectWindows[pid] = state;

  (session.messages || []).forEach((m) => {
    addProjectMsg(chatEl, m.role, m.text, proj);
  });

  makeDraggable(win, win.querySelector(".proj-win-header"), pid);

  win.querySelector(".pw-min").addEventListener("click", () => {
    win.classList.add("hidden");
    minimizedProjects.add(pid);
    renderMiniChips();
    saveWinPos(pid, win);
  });

  win.querySelector(".pw-close").addEventListener("click", () => {
    saveWinPos(pid, win);
    win.remove();
    delete openProjectWindows[pid];
    minimizedProjects.delete(pid);
    renderMiniChips();
  });

  let projSending = false;
  const sendMsg = async () => {
    if (projSending) return;
    const text = inputEl.value.trim();
    const hasImage = !!state._pendingImg;

    if (!text && !hasImage) return;

    /* if there's a pending pasted image, send it with the text */
    if (hasImage) {
      projSending = true;
      inputEl.value = "";
      sendProjectImage(pid, text || "What do you see in this image?");
      projSending = false;
      return;
    }

    projSending = true;
    inputEl.value = "";
    addProjectMsg(chatEl, "user", text, proj);
    const dots = addThinkingDot(chatEl, proj);
    try {
      const data = await post("/api/ask", { text, project: pid });
      dots.remove();
      const reply = data.ok === false ? (data.error || "Error") : (data.text || "No reply.");
      addProjectMsg(chatEl, "ella", reply, proj, data.usage && data.usage.completion);
      if (data.usage_summary) paintUsage(data.usage_summary);
      if (win.classList.contains("hidden")) {
        state.unread++;
        renderMiniChips();
      }
    } catch (e) {
      dots.remove();
      addProjectMsg(chatEl, "ella", "Error: " + e.message, proj);
    } finally {
      projSending = false;
    }
  };

  inputEl.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); sendMsg(); } });
  win.querySelector(".proj-win-send").addEventListener("click", sendMsg);

  const fileInput = win.querySelector(".pw-file-input");
  win.querySelector(".pw-attach").addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) return;
    if (!validImageFile(file)) { showToast("Use a PNG, JPEG, or WebP image up to 12 MiB."); fileInput.value = ""; return; }
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result;
      if (!validImageDataUrl(base64)) { showToast("That image format or size is not supported."); return; }
      addProjectImg(chatEl, "user", file.name, base64, proj);
      const caption = inputEl.value.trim() || "What do you see in this image?";
      inputEl.value = "";
      const dots = addThinkingDot(chatEl, proj);
      post("/api/ask", { text: caption, project: pid, image: base64 })
        .then((data) => {
          dots.remove();
          const reply = data.ok === false ? (data.error || "Error") : (data.text || "No reply.");
          addProjectMsg(chatEl, "ella", reply, proj, data.usage && data.usage.completion);
          if (data.usage_summary) paintUsage(data.usage_summary);
        })
        .catch((e) => { dots.remove(); addProjectMsg(chatEl, "ella", "Error: " + e.message, proj); });
    };
    reader.readAsDataURL(file);
    fileInput.value = "";
  });

  win.querySelectorAll(".proj-action").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = btn.dataset.idx;
      const act = btn.dataset.act;
      if (idx !== undefined && customActions[idx]) {
        inputEl.value = customActions[idx].prompt;
        sendMsg();
      } else if (act === "status") { inputEl.value = "Give me a quick status update on this project."; sendMsg(); }
      else if (act === "continue") { inputEl.value = "Continue where we left off."; sendMsg(); }
      else if (act === "tasks") { inputEl.value = "What are the open tasks for this project?"; sendMsg(); }
    });
  });

  /* --- Links panel --- */
  const linksToggle = win.querySelector(".pw-links-toggle");
  const linksPanel = win.querySelector(".pw-links-panel");
  linksToggle.addEventListener("click", () => linksPanel.classList.toggle("hidden"));

  function refreshLinks() {
    const list = win.querySelector(".pw-links-list");
    const currentLinks = proj.links || [];
    list.innerHTML = currentLinks.map((lnk, i) => `
      <div class="pw-link-row" data-li="${i}">
        <span class="pw-link-label" title="${escapeHtml(lnk.url)}">${escapeHtml(lnk.label || lnk.url || "Link")}</span>
        <button class="pw-link-open" title="Open">↗</button>
        <button class="pw-link-del" title="Remove">✕</button>
      </div>`).join("");
    bindLinkEvents();
  }

  function bindLinkEvents() {
    win.querySelectorAll(".pw-link-open").forEach(btn => {
      btn.addEventListener("click", () => {
        const idx = parseInt(btn.closest(".pw-link-row").dataset.li);
        const lnk = (proj.links || [])[idx];
        if (lnk && lnk.url) {
          let target;
          try { target = new URL(lnk.url); } catch (_) { target = null; }
          if (target && ["http:", "https:"].includes(target.protocol)) {
            window.open(target.href, "_blank", "noopener,noreferrer");
          } else inputEl.value = `Open ${lnk.url}`;
        }
      });
    });
    win.querySelectorAll(".pw-link-del").forEach(btn => {
      btn.addEventListener("click", async () => {
        const idx = parseInt(btn.closest(".pw-link-row").dataset.li);
        proj.links.splice(idx, 1);
        await post("/api/projects", { action: "update", project_id: pid, updates: { links: proj.links } });
        refreshLinks();
      });
    });
  }
  bindLinkEvents();

  async function addLink() {
    const labelIn = win.querySelector(".pw-link-add-label");
    const urlIn = win.querySelector(".pw-link-add-url");
    const label = labelIn.value.trim();
    const url = urlIn.value.trim();
    if (!url) return;
    if (!proj.links) proj.links = [];
    proj.links.push({ label: label || url, url });
    await post("/api/projects", { action: "update", project_id: pid, updates: { links: proj.links } });
    labelIn.value = "";
    urlIn.value = "";
    refreshLinks();
  }
  win.querySelector(".pw-link-add-btn").addEventListener("click", addLink);
  win.querySelector(".pw-link-add-url").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); addLink(); } });
  win.querySelector(".pw-link-add-label").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); win.querySelector(".pw-link-add-url").focus(); } });

  /* --- Clear chat --- */
  win.querySelector(".pw-clear").addEventListener("click", async () => {
    if (!confirm(`Clear all chat history for ${proj.name}?`)) return;
    const chatArea = win.querySelector(".proj-win-chat");
    chatArea.innerHTML = "";
    await post("/api/projects", { action: "clear_session", project_id: pid });
  });

  win.addEventListener("mousedown", () => { win.style.zIndex = ++projectZIndex; });
}

function addProjectMsg(chatEl, role, text, proj, tokens) {
  const div = document.createElement("div");
  div.className = role === "user" ? "msg msg-user" : "msg msg-ella";
  const body = document.createElement("div");
  body.className = "msg-body";
  body.textContent = text;
  div.appendChild(body);
  const meta = document.createElement("div");
  meta.className = "msg-meta";
  const time = new Date().toLocaleTimeString("en-PH", { hour: "2-digit", minute: "2-digit", hour12: true });
  const timeEl = document.createElement("span");
  timeEl.textContent = time;
  meta.appendChild(timeEl);
  if (role === "ella") {
    const tag = document.createElement("span");
    const color = safeProjectColor(proj.color);
    tag.className = "msg-tag";
    tag.style.background = `${color}22`;
    tag.style.color = color;
    tag.textContent = proj.name;
    meta.appendChild(tag);
  }
  if (tokens) {
    const tokenEl = document.createElement("span");
    tokenEl.className = "msg-tag";
    tokenEl.textContent = `${fmtTok(tokens)} tok`;
    meta.appendChild(tokenEl);
  }
  if (role === "ella") {
    const copyBtn = document.createElement("button");
    copyBtn.className = "msg-copy";
    copyBtn.textContent = "Copy";
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(text).then(() => { copyBtn.textContent = "Copied!"; setTimeout(() => copyBtn.textContent = "Copy", 1500); });
    };
    meta.appendChild(copyBtn);
  }
  div.appendChild(meta);
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
  return div;
}

function addProjectImg(chatEl, role, filename, dataUrl, proj) {
  const div = document.createElement("div");
  div.className = "msg msg-user";
  const img = document.createElement("img");
  img.src = dataUrl;
  img.style.cssText = "max-width:200px;max-height:160px;border-radius:8px;display:block;margin-bottom:4px;";
  div.appendChild(img);
  const meta = document.createElement("div");
  meta.className = "msg-meta";
  const time = new Date().toLocaleTimeString("en-PH", { hour: "2-digit", minute: "2-digit", hour12: true });
  const timeEl = document.createElement("span");
  timeEl.textContent = time;
  const filenameEl = document.createElement("span");
  filenameEl.className = "file-label";
  filenameEl.textContent = filename;
  meta.append(timeEl, filenameEl);
  div.appendChild(meta);
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function addThinkingDot(chatEl, proj) {
  const div = document.createElement("div");
  div.className = "msg msg-ella proj-thinking";
  const body = document.createElement("div");
  body.className = "msg-body";
  const dots = document.createElement("span");
  dots.className = "thinking-dots";
  dots.style.color = safeProjectColor(proj.color);
  dots.textContent = "● ● ●";
  body.appendChild(dots);
  div.appendChild(body);
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
  return div;
}

function makeDraggable(win, handle, pid) {
  let startX, startY, origX, origY;
  handle.addEventListener("mousedown", (e) => {
    if (e.target.closest(".proj-win-btn")) return;
    e.preventDefault();
    startX = e.clientX;
    startY = e.clientY;
    origX = win.offsetLeft;
    origY = win.offsetTop;
    const move = (ev) => {
      let nx = origX + ev.clientX - startX;
      let ny = origY + ev.clientY - startY;
      nx = Math.max(-win.offsetWidth + 80, Math.min(window.innerWidth - 80, nx));
      ny = Math.max(0, Math.min(window.innerHeight - 40, ny));
      win.style.left = nx + "px";
      win.style.top = ny + "px";
    };
    const up = () => {
      document.removeEventListener("mousemove", move);
      document.removeEventListener("mouseup", up);
      saveWinPos(pid, win);
    };
    document.addEventListener("mousemove", move);
    document.addEventListener("mouseup", up);
  });
}

function saveWinPos(pid, win) {
  localStorage.setItem("projWinPos_" + pid, JSON.stringify({
    x: win.offsetLeft, y: win.offsetTop,
    w: win.offsetWidth, h: win.offsetHeight,
  }));
}

function renderMiniChips() {
  const el = $("#miniChips");
  el.innerHTML = "";
  minimizedProjects.forEach((pid) => {
    const proj = projectConfigs.find((p) => p.id === pid);
    if (!proj) return;
    const state = openProjectWindows[pid];
    const chip = document.createElement("div");
    chip.className = "mini-chip";
    const icon = document.createElement("span");
    icon.className = "mini-chip-icon";
    icon.textContent = proj.icon || "📁";
    const name = document.createElement("span");
    name.textContent = proj.name;
    const badge = document.createElement("span");
    badge.className = "mini-chip-badge";
    badge.textContent = state?.unread || "";
    chip.append(icon, name, badge);
    chip.addEventListener("click", () => {
      minimizedProjects.delete(pid);
      if (state) { state.el.classList.remove("hidden"); state.el.style.zIndex = ++projectZIndex; state.unread = 0; }
      renderMiniChips();
    });
    el.appendChild(chip);
  });
}

/* restore open windows from last session */
function restoreProjects() {
  const saved = localStorage.getItem("ella_open_projects");
  if (!saved) return;
  try {
    const data = JSON.parse(saved);
    if (Array.isArray(data)) {
      data.forEach((pid) => openProjectWindow(pid));
    } else {
      for (const [pid, info] of Object.entries(data)) {
        openProjectWindow(pid).then(() => {
          if (info.minimized && openProjectWindows[pid]) {
            openProjectWindows[pid].el.classList.add("hidden");
            minimizedProjects.add(pid);
            renderMiniChips();
          }
        });
      }
    }
  } catch (_) {}
}

/* save open project IDs and their state before unload */
window.addEventListener("beforeunload", () => {
  const state = {};
  for (const pid of Object.keys(openProjectWindows)) {
    state[pid] = { minimized: minimizedProjects.has(pid) };
  }
  localStorage.setItem("ella_open_projects", JSON.stringify(state));
});

/* ============================================================
   PROJECT DASHBOARD (Tasks view)
   ============================================================ */
function renderDashboard() {
  const container = $("#dashboardGrid");
  if (!container) return;
  const q = ($("#dashFilter") && $("#dashFilter").value || "").trim().toLowerCase();
  const list = projectConfigs.filter((p) => !q || (p.name || "").toLowerCase().includes(q) || (p.id || "").includes(q));
  container.innerHTML = list.map(p => {
    const color = safeProjectColor(p.color);
    const linkCount = (p.links || []).length;
    const isOpen = !!openProjectWindows[p.id];
    const isMin = minimizedProjects.has(p.id);
    const statusText = isOpen ? (isMin ? "Minimized" : "Open") : "Closed";
    const statusClass = isOpen ? (isMin ? "dash-min" : "dash-open") : "dash-closed";
    return `
      <div class="dash-card" data-pid="${escapeHtml(p.id)}" data-name="${escapeHtml((p.name || "").toLowerCase())}" style="--accent:${color}">
        <div class="dash-card-top">
          <span class="dash-card-icon">${escapeHtml(p.icon || "📁")}</span>
          <div class="dash-card-info">
            <span class="dash-card-name">${escapeHtml(p.name)}</span>
            <span class="dash-card-status ${statusClass}">${statusText}</span>
          </div>
          <span class="dash-card-dot" style="background:${color};box-shadow:0 0 6px ${color};"></span>
        </div>
        <div class="dash-card-meta">
          ${linkCount ? `<span class="dash-meta-item">📎 ${linkCount} link${linkCount > 1 ? "s" : ""}</span>` : ""}
          ${p.path ? `<span class="dash-meta-item" title="${escapeHtml(p.path)}">📂 ${escapeHtml(p.path.split("\\").pop())}</span>` : ""}
        </div>
        <div class="dash-card-actions">
          <button class="dash-open-btn" data-pid="${escapeHtml(p.id)}">Open</button>
        </div>
      </div>`;
  }).join("");

  container.querySelectorAll(".dash-open-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      openProjectWindow(btn.dataset.pid);
    });
  });
  container.querySelectorAll(".dash-card").forEach(card => {
    card.addEventListener("click", () => openProjectWindow(card.dataset.pid));
  });
}

const dashFilter = $("#dashFilter");
if (dashFilter) dashFilter.addEventListener("input", () => renderDashboard());
$("#tokenPill").addEventListener("click", () => switchView("health"));

/* re-render panels when their view opens */
const origSwitchView = switchView;
switchView = function(name) {
  origSwitchView(name);
  if (name === "tasks" || name === "health" || name === "inbox") refreshPanel();
};

boot();
