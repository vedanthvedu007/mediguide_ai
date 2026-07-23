/* ════════════════════════════════════════════════════════════
   MEDIGUIDE AI v3.0 — Main App Initialization & Navigation
   app.js
════════════════════════════════════════════════════════════ */

// ─── Tab Navigation ────────────────────────────────────────
function showTab(panelId, clickedBtn) {
  // Hide all panels
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  // Remove active from all nav buttons
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

  // Show the target panel
  const panel = document.getElementById(panelId);
  if (panel) panel.classList.add('active');

  // Mark the button active
  if (clickedBtn) clickedBtn.classList.add('active');
  else {
    // Find the nav btn for this panel
    const btn = document.querySelector(`.nav-btn[data-panel="${panelId}"]`);
    if (btn) btn.classList.add('active');
  }

  // Panel-specific init
  if (panelId === 'remediesPanel') initRemedies();
  if (panelId === 'reportPanel')   refreshReport();
  if (panelId === 'bmiPanel')      initBMI();
}

// ─── Settings Modal ────────────────────────────────────────
function openSettings() {
  document.getElementById('settingsModal').classList.remove('hidden');
  const urlInput = document.getElementById('settingsUrl');
  if (urlInput) urlInput.value = BACKEND_URL !== window.location.origin ? BACKEND_URL : '';
}
function closeSettings() {
  document.getElementById('settingsModal').classList.add('hidden');
}

async function saveSettings() {
  const urlInput = document.getElementById('settingsUrl');
  const rawUrl   = (urlInput?.value || '').trim().replace(/\/$/, '');
  BACKEND_URL    = rawUrl || window.location.origin;
  closeSettings();
  await checkBackend();
  showToast('Settings saved', 'success');
}

// ─── Backend Check ─────────────────────────────────────────
async function checkBackend() {
  const dot    = document.getElementById('backendDot');
  const badge  = document.getElementById('backendBadge');
  const statBE = document.getElementById('statBackend');

  try {
    const data = await Promise.race([
      apiCall('/'),
      new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 3000))
    ]);

    backendOnline = true;
    if (dot)    { dot.className = 'status-dot online'; }
    if (badge)  { badge.innerHTML = '<span class="status-dot online"></span> Backend Online'; }
    if (statBE) { statBE.textContent = 'Online'; }

    console.log(`[MediGuide] Backend connected — ML: ${data.ml_available}, AI: ${data.ai_enabled}`);

  } catch (e) {
    backendOnline = false;
    if (dot)    { dot.className = 'status-dot offline'; }
    if (badge)  { badge.innerHTML = '<span class="status-dot offline"></span> Backend Offline'; }
    if (statBE) { statBE.textContent = 'Offline'; }
    console.warn('[MediGuide] Backend offline — using local fallback');
  }
}

// ─── Ticker Init ───────────────────────────────────────────
function initTicker() {
  const inner = document.getElementById('tickerInner');
  if (!inner) return;
  // Duplicate items for seamless scroll
  const items = HEALTH_TICKERS.map(t => `<span class="ticker-item">⚕️ ${t}</span>`).join('');
  inner.innerHTML = items + items; // duplicate for infinite loop
}

// ─── Tips Filter ───────────────────────────────────────────
function filterTips(cat) {
  document.querySelectorAll('.filter-chip[data-tipcat]').forEach(el => {
    el.classList.toggle('active', el.dataset.tipcat === cat);
  });

  document.querySelectorAll('.tip-card').forEach(card => {
    if (cat === 'all' || card.dataset.cat === cat) {
      card.style.display = '';
    } else {
      card.style.display = 'none';
    }
  });
}

// ─── App Init ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Check backend status
  checkBackend();

  // Auto-check every 60 seconds
  setInterval(checkBackend, 60000);

  // Init chat welcome message
  const msgs = document.getElementById('chatMessages');
  if (msgs && !msgs.innerHTML.trim()) {
    msgs.innerHTML = getWelcomeMessageHTML();
  }

  // Init ticker
  initTicker();

  // Set today's date in report
  const today = new Date().toLocaleDateString('en-IN', { day:'numeric', month:'long', year:'numeric' });
  const rptDate = document.getElementById('rptDate');
  if (rptDate) rptDate.textContent = today;

  // Default tab button data-panel sync
  document.querySelectorAll('.nav-btn[data-panel]').forEach(btn => {
    btn.addEventListener('click', () => showTab(btn.dataset.panel, btn));
  });

  // Home panel: set stat backend
  const statBE = document.getElementById('statBackend');
  if (statBE) statBE.textContent = '—';

  // Keyboard: Escape closes overlays
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      closeSettings();
      dismissEmergencyOverlay();
    }
  });

  // Blood bank dismiss
  const dismissBtn = document.getElementById('dismissBanner');
  if (dismissBtn) {
    dismissBtn.addEventListener('click', () => {
      document.getElementById('bloodBankBanner').classList.add('hidden');
    });
  }

  console.log(`%c🩺 MediGuide AI v${APP_VERSION} — Bringing healthcare to every village`,
    'color:#0d6b5e;font-weight:bold;font-size:14px');
});

// ─── Body Map Hotspot Data-Region attribute support ─────────
document.addEventListener('click', e => {
  const hotspot = e.target.closest('.hotspot');
  if (hotspot && hotspot.dataset.region) {
    selectRegion(hotspot.dataset.region);
  }
});
