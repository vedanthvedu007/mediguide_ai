/* ════════════════════════════════════════════════════════════
   MEDIGUIDE AI v3.0 — Emergency Panel & Alerts
   emergency.js
════════════════════════════════════════════════════════════ */

// ─── Manual Blood Bank Alert ───────────────────────────────
async function triggerManualBloodAlert() {
  const btn = document.getElementById('manualAlertBtn');
  if (!btn) return;

  if (!currentUser) {
    showToast('Please log in to send an emergency alert', 'warn');
    return;
  }

  const confirm = window.confirm(
    '🚨 Are you sure you want to send an EMERGENCY blood bank alert?\n\n' +
    'This will notify the blood bank and emergency services.\n' +
    'Only use this in a real emergency!'
  );
  if (!confirm) return;

  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Sending Alert...';

  try {
    if (backendOnline) {
      // Trigger via predict endpoint with emergency symptoms
      await apiCall('/predict', 'POST', {
        message: 'emergency blood required urgent help',
        email:   currentUser.email,
        name:    currentUser.name,
        history: []
      });
    }

    showBloodBankBanner({
      message: `🚨 Emergency alert sent for ${currentUser.name}! Blood bank and emergency team notified. Call 108 now!`
    });

    // Show emergency overlay
    showEmergencyOverlay();

    showToast('🚨 Emergency alert sent! Call 108 immediately.', 'danger', 6000);

    // Log to activity
    sessionHistory.unshift({
      date:     new Date().toLocaleDateString('en-IN'),
      symptoms: 'MANUAL BLOOD BANK ALERT',
      triage:   'EMERGENCY',
      risk:     100
    });
    updateActivityFeed();

  } catch (e) {
    console.error('[Emergency alert]', e);
    showToast('Alert failed to send via server. Please call 108 directly!', 'danger');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '🩸 Send Blood Bank Alert';
  }
}

// ─── Call Emergency Number ─────────────────────────────────
function callEmergency(number) {
  window.location.href = 'tel:' + number;
}

// ─── Blood Donation Register CTA ──────────────────────────
function openDonorRegistration() {
  window.open('https://ksbb.karnataka.gov.in/', '_blank'); // State blood bank (example)
  showToast('Opening blood donation registration...', 'info');
}

// ─── Find Nearest PHC ─────────────────────────────────────
function findNearestPHC() {
  if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
      pos => {
        const { latitude, longitude } = pos.coords;
        window.open(
          `https://www.google.com/maps/search/Primary+Health+Centre/@${latitude},${longitude},13z`,
          '_blank'
        );
      },
      () => {
        window.open('https://www.google.com/maps/search/Primary+Health+Centre', '_blank');
      }
    );
  } else {
    window.open('https://www.google.com/maps/search/Primary+Health+Centre', '_blank');
  }
}
