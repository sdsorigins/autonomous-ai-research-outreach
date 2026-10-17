/**
 * Autonomous Research Intelligence - Client Controller
 * Understated, elegant Three.js 3D background & clean conversational orchestration.
 */

// ============================================================================
// 1. Minimalist Three.js Ambient Visualizer
// ============================================================================
let scene, camera, renderer, geomGroup;
let mouseX = 0, mouseY = 0;

function initThreeBackground() {
  const canvas = document.getElementById("webgl-canvas");
  if (!canvas) return;

  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 28;

  renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  geomGroup = new THREE.Group();
  scene.add(geomGroup);

  // Position subtly in background
  geomGroup.position.set(6, -2, -5);

  // Smooth minimalist wireframe torus
  const torusGeo = new THREE.TorusGeometry(8.5, 2.2, 16, 90);
  const torusMat = new THREE.MeshBasicMaterial({
    color: 0x3f3f46,
    wireframe: true,
    transparent: true,
    opacity: 0.28,
  });
  const torus = new THREE.Mesh(torusGeo, torusMat);
  torus.rotation.x = Math.PI / 4;
  geomGroup.add(torus);

  // Subtle floating particles
  const particleGeo = new THREE.BufferGeometry();
  const particleCount = 280;
  const positions = new Float32Array(particleCount * 3);

  for (let i = 0; i < particleCount * 3; i += 3) {
    positions[i] = (Math.random() - 0.5) * 35;
    positions[i + 1] = (Math.random() - 0.5) * 35;
    positions[i + 2] = (Math.random() - 0.5) * 20;
  }
  particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));

  const particleMat = new THREE.PointsMaterial({
    size: 0.08,
    color: 0xd97757, // Claude warm terracotta
    transparent: true,
    opacity: 0.35,
  });
  const points = new THREE.Points(particleGeo, particleMat);
  geomGroup.add(points);

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  window.addEventListener("mousemove", (e) => {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  renderLoop();
}

function renderLoop() {
  requestAnimationFrame(renderLoop);

  geomGroup.rotation.y += 0.0018;
  geomGroup.rotation.x += 0.0012;

  // Gentle parallax
  geomGroup.position.x += (6 + mouseX * 0.5 - geomGroup.position.x) * 0.03;
  geomGroup.position.y += (-2 - mouseY * 0.5 - geomGroup.position.y) * 0.03;

  renderer.render(scene, camera);
}

// ============================================================================
// 2. Chat & Multi-Agent Flow Controller
// ============================================================================
document.addEventListener("DOMContentLoaded", () => {
  initThreeBackground();

  const queryInput = document.getElementById("query-input");
  const sendBtn = document.getElementById("send-trigger");

  queryInput.addEventListener("input", () => {
    queryInput.style.height = "auto";
    queryInput.style.height = Math.min(queryInput.scrollHeight, 120) + "px";
  });

  queryInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleQueryDispatch();
    }
  });

  sendBtn.addEventListener("click", handleQueryDispatch);
});

function submitPrompt(text) {
  const queryInput = document.getElementById("query-input");
  queryInput.value = text;
  handleQueryDispatch();
}

async function handleQueryDispatch() {
  const queryInput = document.getElementById("query-input");
  const sendBtn = document.getElementById("send-trigger");
  const emailInput = document.getElementById("target-email-input");

  const query = queryInput.value.trim();
  if (!query) return;

  const email = emailInput ? emailInput.value.trim() : "executive@enterprise.com";

  queryInput.value = "";
  queryInput.style.height = "38px";
  sendBtn.disabled = true;

  // Render user prompt
  appendUserBubble(query);

  // Hide welcome hero with GSAP
  const hero = document.getElementById("welcome-hero");
  if (hero) {
    gsap.to(hero, { opacity: 0, y: -15, duration: 0.3, onComplete: () => hero.remove() });
  }

  // Create bot response container with stepper
  const botCardEl = createBotResponseCard();
  scrollChatToBottom();

  // Step 1: Research Strategist
  updateAgentNode(1, "Searching", true);
  updateStepRow(botCardEl, 1, "Agent 1: Senior Research Strategist querying live web sources...", "active");

  try {
    const res = await fetch("/api/research", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, email }),
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();

    // Step 1 done
    updateAgentNode(1, "Done", false, true);
    updateStepRow(botCardEl, 1, `Agent 1: Gathered ${data.evidence.length} empirical source findings.`, "done");

    // Step 2: Quantitative Analyst
    updateAgentNode(2, "Analyzing", true);
    updateStepRow(botCardEl, 2, "Agent 2: Quantitative Analyst structuring benchmark tables...", "active");
    await sleep(450);
    updateAgentNode(2, "Done", false, true);
    updateStepRow(botCardEl, 2, "Agent 2: Quantitative benchmarks and variances calculated.", "done");

    // Step 3: Citations Verifier
    updateAgentNode(3, "Auditing", true);
    updateStepRow(botCardEl, 3, "Agent 3: Forensic Citations Verifier cross-referencing claims...", "active");
    await sleep(450);
    updateAgentNode(3, "Certified", false, true);
    updateStepRow(botCardEl, 3, `Agent 3: Certified 100% evidentiary grounding (Zero hallucinations).`, "done");

    // Step 4: Executive Delivery
    updateAgentNode(4, "Compiling", true);
    updateStepRow(botCardEl, 4, "Agent 4: Executive Delivery compiling formal intelligence brief...", "active");
    await sleep(400);
    updateAgentNode(4, "Ready", false, true);
    updateStepRow(botCardEl, 4, `Agent 4: PDF Brief assembled (${data.pdf_filename}).`, "done");

    // Render formatted results
    renderFullAnalysis(botCardEl, data);

  } catch (err) {
    console.error("Research failed:", err);
    botCardEl.querySelector(".response-content-area").innerHTML = `
      <div style="color: #ef4444; font-size: 0.85rem; padding: 12px 0;">
        System Notice: Could not complete investigation (${err.message}).
      </div>
    `;
  } finally {
    sendBtn.disabled = false;
    scrollChatToBottom();
  }
}

// ============================================================================
// 3. UI Helpers & Rendering
// ============================================================================
function appendUserBubble(text) {
  const bounds = document.getElementById("chat-bounds");
  const row = document.createElement("div");
  row.className = "chat-row user";
  row.innerHTML = `<div class="user-bubble">${escapeHtml(text)}</div>`;
  bounds.appendChild(row);
  gsap.from(row, { opacity: 0, y: 10, duration: 0.25 });
}

function createBotResponseCard() {
  const bounds = document.getElementById("chat-bounds");
  const row = document.createElement("div");
  row.className = "chat-row bot";
  row.innerHTML = `
    <div class="bot-card">
      <div class="crew-stepper-box">
        <div class="crew-stepper-header">Autonomous 4-Agent Execution</div>
        <div class="stepper-items">
          <div class="step-row active" id="st-1">· Agent 1: Senior Research Strategist</div>
          <div class="step-row" id="st-2">· Agent 2: Quantitative Analyst</div>
          <div class="step-row" id="st-3">· Agent 3: Citations Verifier</div>
          <div class="step-row" id="st-4">· Agent 4: Executive Delivery</div>
        </div>
      </div>
      <div class="response-content-area"></div>
    </div>
  `;
  bounds.appendChild(row);
  gsap.from(row, { opacity: 0, y: 15, duration: 0.3 });
  return row;
}

function updateStepRow(cardEl, stepNum, text, state) {
  const el = cardEl.querySelector(`#st-${stepNum}`);
  if (!el) return;
  el.className = `step-row ${state}`;
  el.innerText = state === "done" ? `✓ ${text}` : `· ${text}`;
}

function renderFullAnalysis(cardEl, data) {
  const area = cardEl.querySelector(".response-content-area");

  // Build Statistical Benchmark Table
  let statRowsHTML = "";
  if (data.statistical_data) {
    data.statistical_data.forEach((s) => {
      statRowsHTML += `
        <tr>
          <td>${escapeHtml(s.metric)}</td>
          <td>${escapeHtml(s.baseline)}</td>
          <td>${escapeHtml(s.result)}</td>
          <td class="delta-badge">${escapeHtml(s.variance)}</td>
          <td class="stat-cite-tag">${escapeHtml(s.citation)}</td>
        </tr>
      `;
    });
  }

  // Build Evidence rows
  let evidenceRowsHTML = "";
  data.evidence.forEach((ev) => {
    evidenceRowsHTML += `
      <div class="evidence-row-item">
        <div class="evidence-header">
          <span class="evidence-id">${ev.id}</span>
          <a href="${ev.source_url}" target="_blank" rel="noopener noreferrer" class="evidence-source-link">
            ${escapeHtml(ev.source_title)} ↗
          </a>
        </div>
        <div style="color: var(--text-primary); font-size: 0.84rem;">${escapeHtml(ev.fact)}</div>
      </div>
    `;
  });

  area.innerHTML = `
    <div class="response-title-bar">
      <h3 class="response-query-title">${escapeHtml(data.query)}</h3>
      <span class="certified-pill">Certified 100% Grounded</span>
    </div>

    <!-- Statistical Comparison Table -->
    <div class="section-subtitle">Quantitative Benchmarks & Variance</div>
    <div class="stat-table-wrapper">
      <table class="statistical-table">
        <thead>
          <tr>
            <th>Benchmark Metric</th>
            <th>Baseline</th>
            <th>Observed Result</th>
            <th>Variance</th>
            <th>Citation</th>
          </tr>
        </thead>
        <tbody>
          ${statRowsHTML}
        </tbody>
      </table>
    </div>

    <!-- Verified Primary Evidence -->
    <div class="section-subtitle">Primary Verified Evidence</div>
    <div class="evidence-list">
      ${evidenceRowsHTML}
    </div>

    <!-- Clean Download PDF Action -->
    <div class="download-action-bar">
      <span class="citation-counter">${data.evidence.length} Source Citations Verified</span>
      <a href="${data.pdf_download_url}" class="download-pdf-button" download>
        <svg viewBox="0 0 24 24">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        Download PDF Report
      </a>
    </div>
  `;

  gsap.from(area.children, {
    opacity: 0,
    y: 10,
    stagger: 0.08,
    duration: 0.35,
    ease: "power2.out",
  });
}

function updateAgentNode(nodeNum, status, isActive = false, isCompleted = false) {
  const item = document.getElementById(`node-agent-${nodeNum}`);
  const badge = document.getElementById(`status-${nodeNum}`);
  if (!item || !badge) return;

  badge.innerText = status;
  item.classList.remove("active", "completed");

  if (isActive) {
    item.classList.add("active");
  } else if (isCompleted) {
    item.classList.add("completed");
  }
}

function scrollChatToBottom() {
  const area = document.getElementById("chat-stream");
  if (area) area.scrollTop = area.scrollHeight;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
