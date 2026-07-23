/* ════════════════════════════════════════════════════════════
   MEDIGUIDE AI v3.0 — Authentication (Login / Register / Logout)
   auth.js
════════════════════════════════════════════════════════════ */

function showLogin() {
  document.getElementById('loginForm').classList.remove('hidden');
  document.getElementById('registerForm').classList.add('hidden');
  document.getElementById('loginError').classList.add('hidden');
}

function showRegister() {
  document.getElementById('loginForm').classList.add('hidden');
  document.getElementById('registerForm').classList.remove('hidden');
  document.getElementById('registerError').classList.add('hidden');
  document.getElementById('registerSuccess').classList.add('hidden');
}

// ─── Login ─────────────────────────────────────────────────
async function doLogin() {
  const email    = document.getElementById('loginEmail').value.trim().toLowerCase();
  const password = document.getElementById('loginPass').value;
  const errEl    = document.getElementById('loginError');
  const btn      = document.getElementById('loginBtn');

  errEl.classList.add('hidden');

  if (!email || !password) {
    errEl.textContent = '❌ Please enter both email and password.';
    errEl.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Signing in...';

  try {
    // Demo mode fallback (works without backend)
    if (email === DEMO.email && password === DEMO.pass) {
      onLoginSuccess({ name: DEMO.name, email: DEMO.email, age: DEMO.age });
      return;
    }

    if (backendOnline) {
      const data = await apiCall('/login', 'POST', { email, password });
      if (data.status === 'success') {
        onLoginSuccess({ name: data.name, email: data.email, age: data.age });
      } else {
        throw new Error('Invalid credentials');
      }
    } else {
      // Not online — only demo allowed
      errEl.textContent = '❌ Backend not connected. Use demo credentials: demo@mediguide.ai / health123';
      errEl.classList.remove('hidden');
    }
  } catch (e) {
    errEl.textContent = '❌ Invalid email or password. Try the demo credentials above.';
    errEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Sign In →';
  }
}

// ─── Register ──────────────────────────────────────────────
async function doRegister() {
  const name     = document.getElementById('regName').value.trim();
  const age      = parseInt(document.getElementById('regAge').value) || null;
  const email    = document.getElementById('regEmail').value.trim().toLowerCase();
  const password = document.getElementById('regPass').value;
  const errEl    = document.getElementById('registerError');
  const sucEl    = document.getElementById('registerSuccess');
  const btn      = document.getElementById('registerBtn');

  errEl.classList.add('hidden');
  sucEl.classList.add('hidden');

  if (!name || !email || password.length < 6) {
    errEl.textContent = '❌ Please fill all fields. Password must be at least 6 characters.';
    errEl.classList.remove('hidden');
    return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errEl.textContent = '❌ Please enter a valid email address.';
    errEl.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Creating account...';

  try {
    if (!backendOnline) {
      errEl.textContent = '❌ Backend not connected. Cannot register without backend.';
      errEl.classList.remove('hidden');
      return;
    }

    const data = await apiCall('/register', 'POST', { name, email, password, age });

    if (data.status === 'success') {
      sucEl.textContent = '✅ Account created! Signing you in...';
      sucEl.classList.remove('hidden');
      setTimeout(() => onLoginSuccess({ name, email, age }), 1200);
    } else if (data.status === 'exists') {
      errEl.textContent = '❌ This email is already registered. Please sign in instead.';
      errEl.classList.remove('hidden');
    } else {
      errEl.textContent = '❌ Invalid input. Please check your details.';
      errEl.classList.remove('hidden');
    }
  } catch (e) {
    errEl.textContent = '❌ Registration failed. Please try again.';
    errEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create Account →';
  }
}

// ─── On Login Success ──────────────────────────────────────
function onLoginSuccess(user) {
  currentUser = user;

  // Update UI elements
  const initial = user.name.charAt(0).toUpperCase();

  document.getElementById('topUserName').textContent = user.name.split(' ')[0];
  document.getElementById('topUserAvatar').textContent = initial;
  document.getElementById('welcomeName').textContent = user.name.split(' ')[0];

  // Profile panel
  document.getElementById('profileAvatar').textContent   = initial;
  document.getElementById('profileName').textContent     = user.name;
  document.getElementById('profileEmail').textContent    = user.email;
  document.getElementById('piName').textContent          = user.name;
  document.getElementById('piAge').textContent           = user.age ? user.age + ' years' : '—';

  // Report panel
  document.getElementById('rptName').textContent         = user.name;
  document.getElementById('rptEmail').textContent        = user.email;
  document.getElementById('rptAge').textContent          = user.age || '—';
  document.getElementById('rptDate').textContent         = new Date().toLocaleDateString('en-IN', { day:'numeric', month:'long', year:'numeric' });
  document.getElementById('rptFooterDate').textContent   = new Date().toLocaleDateString('en-IN', { weekday:'long', year:'numeric', month:'long', day:'numeric' });

  // Switch screens
  document.getElementById('loginScreen').classList.remove('active');
  document.getElementById('dashScreen').classList.add('active');

  // Load history from backend if online
  if (backendOnline && user.email) {
    loadHistory(user.email);
  }

  showToast(`Welcome back, ${user.name.split(' ')[0]}! 👋`, 'success');
}

// ─── Logout ───────────────────────────────────────────────
function doLogout() {
  currentUser           = null;
  conversationHistory   = [];
  sessionHistory        = [];
  sessionChecks         = 0;
  currentBMI            = null;

  // Reset chat
  const msgs = document.getElementById('chatMessages');
  if (msgs) msgs.innerHTML = getWelcomeMessageHTML();

  // Reset form fields
  document.getElementById('loginEmail').value = '';
  document.getElementById('loginPass').value  = '';

  // Switch screens
  document.getElementById('dashScreen').classList.remove('active');
  document.getElementById('loginScreen').classList.add('active');
  showLogin();

  // Hide alerts
  const bbb = document.getElementById('bloodBankBanner');
  if (bbb) bbb.classList.add('hidden');
  const eo = document.getElementById('emergencyOverlay');
  if (eo) eo.classList.add('hidden');
}

// ─── Keyboard shortcuts ────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    const loginForm = document.getElementById('loginForm');
    const regForm   = document.getElementById('registerForm');
    if (loginForm && !loginForm.classList.contains('hidden')) {
      const ae = document.activeElement;
      if (ae && (ae.id === 'loginEmail' || ae.id === 'loginPass')) doLogin();
    }
  }
});
