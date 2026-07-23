/* ════════════════════════════════════════════════════════════
   MEDIGUIDE AI v3.0 — Chat / AI Doctor Engine
   chat.js
════════════════════════════════════════════════════════════ */

// ─── Welcome Message ───────────────────────────────────────
function getWelcomeMessageHTML() {
  return `
  <div class="msg bot animate-slideup">
    <div class="msg-avatar bot-avatar">🩺</div>
    <div>
      <div class="msg-bubble">
        <strong>Namaste! 🙏 I am MediGuide AI — your rural health companion.</strong><br><br>
        Describe what you are feeling in simple words. You can say things like:<br>
        <em>"Mujhe bukhar hai aur sir dard hai"</em> (Hindi) or<br>
        <em>"Nanage jwara ide mattu tale novu ide"</em> (Kannada) or<br>
        <em>"I have fever and headache since 2 days"</em> (English)<br><br>
        I will check your symptoms using <strong>AI + ML</strong> and guide you on:
        <strong>home remedies</strong>, medicines, and whether you need a doctor! 😊
        <div class="sym-icon-row" style="margin-top:12px">
          <div class="sym-icon">🤒</div>
          <div class="sym-icon">🤕</div>
          <div class="sym-icon">🤢</div>
          <div class="sym-icon">💔</div>
          <div class="sym-icon">🤧</div>
        </div>
      </div>
    </div>
  </div>`;
}

// ─── Quick-Send from Sidebar / Conditions ──────────────────
function quickSend(text) {
  showTab('chatPanel', document.querySelector('.nav-btn[data-panel="chatPanel"]'));
  const input = document.getElementById('chatInput');
  if (input) {
    input.value = text;
    sendMessage();
  }
}

function startSymptomChat(text) {
  quickSend(text);
}

// ─── Send Message ──────────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text  = (input.value || '').trim();
  if (!text || isSending) return;

  isSending = true;
  input.value = '';
  input.style.height = 'auto';
  document.getElementById('sendBtn').disabled = true;

  // Append user bubble
  appendUserBubble(text);

  // Scroll to bottom
  scrollChatToBottom();

  // Show typing indicator
  const typingId = showTyping();

  try {
    const payload = {
      message:              text,
      email:                currentUser?.email || '',
      name:                 currentUser?.name  || '',
      history:              conversationHistory,
      bmi_severity_adjust:  currentSeverityAdjust || 0
    };

    const data = backendOnline
      ? await apiCall('/predict', 'POST', payload)
      : buildLocalFallback(text);

    removeTyping(typingId);
    renderBotResponse(data, text);

    // Update conversation history
    conversationHistory.push({ role: 'user', content: text });
    conversationHistory.push({ role: 'assistant', content: data.simple_explanation || '' });
    if (conversationHistory.length > 20) conversationHistory = conversationHistory.slice(-20);

    // Update session stats
    sessionChecks++;
    sessionHistory.unshift({
      date:        new Date().toLocaleDateString('en-IN'),
      symptoms:    data.matched_symptoms?.join(', ') || text.slice(0, 60),
      triage:      data.triage_level,
      risk:        data.risk_score
    });
    updateDashStats(data);

    // Handle blood bank alert
    if (data.blood_bank_alert) showBloodBankBanner(data.blood_bank_alert);
    if (data.triage_level === 'EMERGENCY') showEmergencyOverlay();

  } catch (err) {
    removeTyping(typingId);
    appendBotBubble('⚠️ Could not connect to the server. Please check if the backend is running. Meanwhile, use the <strong>Home Remedies</strong> tab for guidance.');
    console.error('[Chat error]', err);
  } finally {
    isSending = false;
    document.getElementById('sendBtn').disabled = false;
    scrollChatToBottom();
  }
}

// ─── Render Bot Response ───────────────────────────────────
function renderBotResponse(data, userText) {
  const level       = data.triage_level || 'HOME_CARE';
  const riskScore   = data.risk_score   || 0;
  const riskLevel   = data.risk_level   || 'LOW';
  const explanation = data.simple_explanation || 'Here is your health assessment.';
  const tips        = data.home_care_tips  || [];
  const warnings    = data.warning_signs   || [];
  const followUp    = data.follow_up       || '';
  const followOpts  = data.followup_options|| [];
  const icons       = data.symptom_icons   || ['🩺'];
  const reason      = data.triage_reason   || '';

  // Triage colors
  const triageConfig = {
    EMERGENCY:   { cls: 'triage-emergency', icon: '🚨', label: 'EMERGENCY — Call 108 Now!' },
    CLINIC_VISIT:{ cls: 'triage-clinic',    icon: '🏥', label: 'CLINIC VISIT Recommended' },
    HOME_CARE:   { cls: 'triage-home',      icon: '🏠', label: 'HOME CARE — Rest & Monitor' }
  };
  const tc = triageConfig[level] || triageConfig.HOME_CARE;

  // Risk bar color — derived from triage level to stay consistent
  const riskColor = level === 'EMERGENCY' ? 'high' : level === 'CLINIC_VISIT' ? 'med' : 'low';

  // Build symptom icons
  const iconsHTML = icons.slice(0,5).map(ic => `<div class="sym-icon">${ic}</div>`).join('');

  // Build tips list
  const tipsHTML = tips.slice(0,8).map(t =>
    `<li>${t}</li>`
  ).join('');

  // Build warnings
  const warningsHTML = warnings.map(w =>
    `<li style="color:var(--warn);font-weight:600">⚠️ ${w}</li>`
  ).join('');

  // Build follow-up buttons
  const followBtns = followOpts.map(opt =>
    `<button class="followup-btn" onclick="quickSend('${opt.replace(/'/g,"&#39;")}')">${opt}</button>`
  ).join('');

  const html = `
  <div class="msg bot animate-slideup">
    <div class="msg-avatar bot-avatar">🩺</div>
    <div style="flex:1;min-width:0">
      <div class="msg-bubble">
        <p>${explanation}</p>
        ${iconsHTML ? `<div class="sym-icon-row">${iconsHTML}</div>` : ''}
      </div>

      <div class="triage-card">
        <div class="triage-header ${tc.cls}">
          ${tc.icon} ${tc.label}
        </div>
        <div class="triage-body">
          ${reason ? `<div class="triage-reason">${reason}</div>` : ''}

          <div class="risk-meter">
            <div class="risk-meter-label">
              <span>Risk Level: <strong>${riskLevel}</strong></span>
              <span>${riskScore}/100</span>
            </div>
            <div class="risk-bar">
              <div class="risk-fill ${riskColor}" style="width:${riskScore}%"></div>
            </div>
          </div>

          ${tipsHTML ? `
          <div class="remedy-section" style="margin-top:14px">
            <div class="remedy-title">🌿 ${level === 'EMERGENCY' ? 'Emergency Steps' : 'Home Care & Remedies'}</div>
            <ul class="remedy-list">${tipsHTML}</ul>
          </div>` : ''}

          ${warningsHTML ? `
          <div class="remedy-section" style="margin-top:10px;background:var(--warn-bg);border-color:var(--warn-border)">
            <div class="remedy-title" style="color:var(--warn)">⚠️ Warning Signs — Seek Help If You Notice:</div>
            <ul class="remedy-list">${warningsHTML}</ul>
          </div>` : ''}

          ${followUp ? `<p style="font-size:13px;color:var(--text2);margin-top:12px;font-style:italic">💬 ${followUp}</p>` : ''}
          ${followBtns ? `<div class="followup-wrap">${followBtns}</div>` : ''}
        </div>
      </div>
    </div>
  </div>`;

  const msgs = document.getElementById('chatMessages');
  if (msgs) {
    msgs.insertAdjacentHTML('beforeend', html);
    scrollChatToBottom();
  }
}

// ─── Helper: Append User Bubble ───────────────────────────
function appendUserBubble(text) {
  const initial = currentUser?.name?.charAt(0).toUpperCase() || 'U';
  const html = `
  <div class="msg user animate-slideup">
    <div class="msg-avatar user-avatar-chat">${initial}</div>
    <div class="msg-bubble">${escapeHtml(text)}</div>
  </div>`;
  document.getElementById('chatMessages').insertAdjacentHTML('beforeend', html);
}

function appendBotBubble(html) {
  const markup = `
  <div class="msg bot animate-slideup">
    <div class="msg-avatar bot-avatar">🩺</div>
    <div class="msg-bubble">${html}</div>
  </div>`;
  document.getElementById('chatMessages').insertAdjacentHTML('beforeend', markup);
}

// ─── Typing Indicator ─────────────────────────────────────
let _typingCounter = 0;
function showTyping() {
  const id = 'typing_' + (++_typingCounter);
  const html = `
  <div class="msg bot" id="${id}">
    <div class="msg-avatar bot-avatar">🩺</div>
    <div class="typing-row">
      <div class="typing-dots"><span></span><span></span><span></span></div>
      <span style="font-size:12px;color:var(--text3);margin-left:4px">Analysing symptoms...</span>
    </div>
  </div>`;
  document.getElementById('chatMessages').insertAdjacentHTML('beforeend', html);
  scrollChatToBottom();
  return id;
}
function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ─── Scroll Chat ─────────────────────────────────────────
function scrollChatToBottom() {
  const el = document.getElementById('chatMessages');
  if (el) el.scrollTop = el.scrollHeight;
}

// ─── Local Fallback (no backend) ─────────────────────────
function buildLocalFallback(text) {
  const t = text.toLowerCase();
  let triage = 'HOME_CARE', riskScore = 15, riskLevel = 'LOW';

  const emergencyKw = ['chest pain', 'breathing', 'unconscious', 'blood', 'stroke', 'can\'t breathe', 'heart'];
  const clinicKw    = ['fever', 'vomit', 'diarrhea', 'diarrhoea', 'high fever', 'severe'];

  if (emergencyKw.some(k => t.includes(k))) {
    triage = 'EMERGENCY'; riskScore = 85; riskLevel = 'HIGH';
  } else if (clinicKw.some(k => t.includes(k))) {
    triage = 'CLINIC_VISIT'; riskScore = 55; riskLevel = 'MEDIUM';
  }

  const tips = triage === 'EMERGENCY'
    ? ['🚨 CALL 108 (Ambulance) IMMEDIATELY', '🪑 Keep patient seated or lying on side', '📞 Stay on the line with 108 operator']
    : triage === 'CLINIC_VISIT'
    ? ['💊 Take Paracetamol 500mg for fever/pain', '💧 Drink 8–10 glasses of water daily', '🌿 Ginger tea with honey helps immunity', '🛌 Rest well — allow your body to recover']
    : ['🛌 Rest well — 7–8 hours of sleep helps recovery', '💧 Drink plenty of water and eat light food', '🌿 Tulsi tea or ginger water boosts immunity', '🌡️ Monitor your symptoms over the next 24 hours'];

  return {
    simple_explanation: triage === 'EMERGENCY'
      ? '🚨 Your symptoms suggest an emergency. Please call 108 immediately!'
      : triage === 'CLINIC_VISIT'
      ? '⚠️ Your symptoms need a doctor\'s attention soon. Please visit a clinic.'
      : '😊 Your symptoms appear mild. You can manage at home with rest and remedies.',
    symptom_icons:  ['🩺'],
    triage_level:   triage,
    triage_reason:  'Assessment based on symptom keywords (backend offline)',
    risk_score:     riskScore,
    risk_level:     riskLevel,
    matched_symptoms: [],
    home_care_tips: tips,
    warning_signs:  ['Symptoms worsen suddenly', 'High fever above 103°F', 'Cannot eat or drink'],
    follow_up:      'Are you experiencing any other symptoms?',
    followup_options: ['Fever', 'Pain', 'Difficulty breathing', 'No other symptoms'],
    blood_bank_alert: triage === 'EMERGENCY' ? { message: 'Emergency detected — please call 108!' } : null
  };
}

// ─── Update Dashboard Stats ────────────────────────────────
function updateDashStats(data) {
  const checks = document.getElementById('statChecks');
  if (checks) checks.textContent = sessionChecks;

  const riskEl = document.getElementById('statRisk');
  if (riskEl) {
    const scoreVal = data.risk_score !== undefined ? data.risk_score : 15;
    riskEl.textContent = `${scoreVal}%`;
  }

  const statusEl = document.getElementById('statStatus');
  if (statusEl) {
    const statusMap = { EMERGENCY: 'Alert 🚨', CLINIC_VISIT: 'Caution 🏥', HOME_CARE: 'Good 🏠' };
    statusEl.textContent = statusMap[data.triage_level] || 'Good 🏠';
  }

  updateActivityFeed();
}

// ─── Blood Bank Banner ─────────────────────────────────────
function showBloodBankBanner(alert) {
  const bbb = document.getElementById('bloodBankBanner');
  if (!bbb) return;
  const info = document.getElementById('bbAlertInfo');
  const contact = alert.blood_bank_contact || '';
  const baseMsg = alert.message || 'Emergency team notified. Call 108!';
  const contactLine = contact ? ` Blood bank contact: ${contact}` : '';
  if (info) info.textContent = baseMsg + contactLine;
  bbb.classList.remove('hidden');
}

// ─── Emergency Overlay ─────────────────────────────────────
function showEmergencyOverlay() {
  const eo = document.getElementById('emergencyOverlay');
  if (eo) eo.classList.remove('hidden');
}
function dismissEmergencyOverlay() {
  const eo = document.getElementById('emergencyOverlay');
  if (eo) eo.classList.add('hidden');
}

// ─── Utility ──────────────────────────────────────────────
function escapeHtml(str) {
  return str
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}

// ─── Auto-resize textarea ─────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const chatInput = document.getElementById('chatInput');
  if (chatInput) {
    chatInput.addEventListener('input', () => {
      chatInput.style.height = 'auto';
      chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });
    chatInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }
});
