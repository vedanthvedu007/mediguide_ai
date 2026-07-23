/* ════════════════════════════════════════════════════════════
   MEDIGUIDE AI v3.0 — Report Generation & History
   report.js
════════════════════════════════════════════════════════════ */

// ─── Load History from Backend ─────────────────────────────
async function loadHistory(email) {
  if (!email || !backendOnline) return;
  try {
    const rows = await apiCall('/history/' + encodeURIComponent(email));
    if (!rows || !rows.length) return;

    // Merge backend history into sessionHistory
    const existing = new Set(sessionHistory.map(h => h.date + h.symptoms));
    rows.forEach(r => {
      const key = r.date + r.symptoms;
      if (!existing.has(key)) {
        sessionHistory.push({ date: r.date, symptoms: r.symptoms, triage: r.triage_level, risk: r.risk });
        existing.add(key);
      }
    });

    sessionChecks = Math.max(sessionChecks, rows.length);
    const checks = document.getElementById('statChecks');
    if (checks) checks.textContent = sessionChecks;

    updateActivityFeed();
    renderReportHistory();
  } catch (e) {
    console.warn('[History load]', e);
  }
}

// ─── Update Activity Feed (Home Panel) ─────────────────────
function updateActivityFeed() {
  const list = document.getElementById('activityList');
  if (!list) return;

  if (!sessionHistory.length) {
    list.innerHTML = `
      <div class="activity-item">
        <div class="activity-dot dot-safe">💚</div>
        <div class="activity-info">
          <div class="activity-title">No checks yet</div>
          <div class="activity-sub">Start a symptom check to see history here</div>
        </div>
      </div>`;
    return;
  }

  const dotMap  = { EMERGENCY: 'dot-danger', CLINIC_VISIT: 'dot-warn', HOME_CARE: 'dot-safe' };
  const iconMap = { EMERGENCY: '🚨', CLINIC_VISIT: '🏥', HOME_CARE: '💚' };
  const tagMap  = { EMERGENCY: 'badge-danger', CLINIC_VISIT: 'badge-warn', HOME_CARE: 'badge-safe' };
  const labelMap= { EMERGENCY: 'Emergency', CLINIC_VISIT: 'Clinic Visit', HOME_CARE: 'Home Care' };

  list.innerHTML = sessionHistory.slice(0, 8).map(h => `
    <div class="activity-item">
      <div class="activity-dot ${dotMap[h.triage] || 'dot-safe'}">${iconMap[h.triage] || '💚'}</div>
      <div class="activity-info">
        <div class="activity-title">${h.symptoms || 'Symptom Check'}</div>
        <div class="activity-sub">${h.date} · Risk: ${h.risk || 0}/100</div>
      </div>
      <span class="badge ${tagMap[h.triage] || 'badge-safe'}">${labelMap[h.triage] || 'Home Care'}</span>
    </div>
  `).join('');
}

// ─── Render Report History Table ───────────────────────────
function renderReportHistory() {
  const tbody = document.getElementById('reportHistoryBody');
  if (!tbody) return;

  if (!sessionHistory.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4" style="text-align:center;color:var(--text3);padding:24px">
          No symptom checks yet. Use AI Doctor to check symptoms.
        </td>
      </tr>`;
    return;
  }

  const badgeMap = { EMERGENCY: 'badge-danger', CLINIC_VISIT: 'badge-warn', HOME_CARE: 'badge-safe' };
  const labelMap = { EMERGENCY: 'Emergency', CLINIC_VISIT: 'Clinic Visit', HOME_CARE: 'Home Care' };

  tbody.innerHTML = sessionHistory.slice(0, 15).map(h => `
    <tr>
      <td>${h.date}</td>
      <td style="max-width:280px;overflow:hidden;text-overflow:ellipsis">${h.symptoms || '—'}</td>
      <td><span class="badge ${badgeMap[h.triage] || 'badge-safe'}">${labelMap[h.triage] || 'Home Care'}</span></td>
      <td><strong>${h.risk || 0}</strong>/100</td>
    </tr>
  `).join('');
}

// ─── Refresh Report Panel ──────────────────────────────────
function refreshReport() {
  if (!currentUser) return;
  renderReportHistory();

  // Update BMI in report
  if (currentBMI) {
    const rptBMI    = document.getElementById('rptBMI');
    const rptBMICat = document.getElementById('rptBMICat');
    if (rptBMI) rptBMI.textContent       = currentBMI.toFixed(1);
    if (rptBMICat) rptBMICat.textContent = currentBMICategory;
  }

  // Update HR estimate based on age
  const age = currentUser.age || currentAge;
  const hrEl = document.getElementById('rptHR');
  if (hrEl) hrEl.textContent = `${Math.round(60 + (age * 0.1))} bpm (est.)`;

  document.getElementById('rptFooterDate').textContent =
    new Date().toLocaleDateString('en-IN', { weekday:'long', year:'numeric', month:'long', day:'numeric' });
}

// ─── Print Report ──────────────────────────────────────────
function printReport() {
  refreshReport();
  setTimeout(() => window.print(), 200);
}

// ─── Feedback Submit ───────────────────────────────────────
async function submitFeedback() {
  const btn = document.getElementById('feedbackBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }

  try {
    const like    = document.getElementById('fbLike')?.value    || '';
    const improve = document.getElementById('fbImprove')?.value || '';
    const recommend = document.getElementById('fbRecommend')?.value || '';

    if (backendOnline) {
      await apiCall('/feedback', 'POST', {
        email:     currentUser?.email || 'anonymous',
        rating:    userRating,
        liked:     like,
        improve:   improve,
        recommend: recommend
      });
    }

    // Show success
    document.getElementById('feedbackFormDiv').classList.add('hidden');
    document.getElementById('feedbackSuccess').classList.remove('hidden');

    showToast('Thank you for your feedback! 💚', 'success');
  } catch (e) {
    console.warn('[Feedback]', e);
    // Still show success on frontend
    document.getElementById('feedbackFormDiv').classList.add('hidden');
    document.getElementById('feedbackSuccess').classList.remove('hidden');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Submit Feedback ✓'; }
  }
}

// ─── Star Rating ───────────────────────────────────────────
function setRating(n) {
  userRating = n;
  document.querySelectorAll('.star').forEach((el, i) => {
    el.textContent = i < n ? '⭐' : '☆';
    el.classList.toggle('selected', i < n);
  });
}
